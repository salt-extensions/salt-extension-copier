import fnmatch
import os
import re
import sys
from pathlib import Path

import questionary
from plumbum import TEE
from plumbum import local
from plumbum.commands.processes import CommandNotFound
from plumbum.commands.processes import ProcessExecutionError

PRE_COMMIT_TEST_REGEX = re.compile(
    r"^(?P<test>[^\n]+?)\.{4,}.*(?P<resolution>Failed|Passed|Skipped)$"
)

NON_IDEMPOTENT_HOOKS = (
    "trim trailing whitespace",
    "mixed line ending",
    "fix end of files",
    "Remove Python Import Header Comments",
    "Check rST doc files exist for modules/states",
    "Salt extensions docstrings auto-fixes",
    "Rewrite the test suite",
    "Rewrite Code to be Py3.",
    "isort",
    "black",
    "blacken-docs",
)


RECOMMENDED_PYVER = "3.10"

VENV_DIRS = (
    ".venv",
    "venv",
    ".env",
    "env",
)

SKIP_IF_EXISTS_BOILERPLATE = (
    "src/**/*_mod.py",
    "tests/**/test_*.py",
)


git = local["git"]

try:
    uv = local["uv"]
except CommandNotFound:
    uv = None


answers = Path(".copier-answers.yml")


def _discover_project_name():
    if not answers.exists():
        raise RuntimeError("Not in copier template, missing answers file")
    for line in answers.read_text().splitlines():
        if line.startswith("project_name"):
            return line.split(":", maxsplit=1)[1].strip()
    raise RuntimeError("Failed discovering project name")


def status(msg):
    questionary.print(f"\n    → {msg}", style="bold fg:darkgreen")


def warn(header, message=None):
    questionary.print(f"\n{header}", style="bold bg:darkred")
    if message:
        questionary.print(message)


def parse_pre_commit(data):
    passing = []
    failing = {}
    cur = None
    for line in data.splitlines():
        if match := PRE_COMMIT_TEST_REGEX.match(line):
            cur = None
            if match.group("resolution") != "Failed":
                passing.append(match.group("test"))
                continue
            cur = match.group("test")
            failing[cur] = []
            continue
        try:
            failing[cur].append(line)
        except KeyError:
            # in case the parsing logic fails, let's not crash everything
            continue
    return passing, {test: "\n".join(output).strip() for test, output in failing.items()}


def check_pre_commit_rerun(data):
    """
    Check if we can expect failing hooks to turn green during a rerun.
    """
    _, failing = parse_pre_commit(data)
    for hook in failing:
        if hook.startswith(NON_IDEMPOTENT_HOOKS):
            return True
    return False


def _get_venv():
    try:
        return _discover_venv()
    except RuntimeError:
        return Path(VENV_DIRS[0]).resolve()


def _discover_venv():
    for name in VENV_DIRS:
        if (found := Path(name)).is_dir() and (found / "pyvenv.cfg").exists():
            return found.resolve()
    raise RuntimeError("No venv found")


def _ensure_venv():
    try:
        venv = _discover_venv()
        status(f"Found existing virtual environment at {venv}")
    except RuntimeError:
        venv = Path(VENV_DIRS[0]).resolve()
        status(f"Creating virtual environment at {venv}")
        if uv is not None:
            status("Found `uv`. Creating venv")
            uv(
                "venv",
                "--python",
                RECOMMENDED_PYVER,
                f"--prompt=saltext-{_discover_project_name()}",
            )
            status("Installing pip into venv")
            # Ensure there's still a `pip` inside the venv for compatibility
            uv("pip", "install", "pip")
        else:
            status("Did not find `uv`. Falling back to `venv`")
            try:
                python = local[f"python{RECOMMENDED_PYVER}"]
            except CommandNotFound:
                python = local["python3"]
                version = python("--version").split(" ")[1]
                if not version.startswith(RECOMMENDED_PYVER):
                    raise RuntimeError(
                        f"No `python{RECOMMENDED_PYVER}` executable found in $PATH, exiting"
                    )
            _run(python, "-m", "venv", VENV_DIRS[0], f"--prompt=saltext-{_discover_project_name()}")
    status("Installing project and dependencies")
    if uv is not None:
        _run_in_venv(venv, uv, "pip", "install", "-qe", ".[dev,tests,docs]")
    else:
        _run_in_venv(venv, "pip", "install", "-qe", ".[dev,tests,docs]")
    status("Installing pre-commit hooks")
    _run_in_venv(venv, "pre-commit", "install", "--install-hooks")
    return venv


def _run(cmd, *args) -> tuple[int, str, str]:
    """
    Run commands that don't need stdin, but whose output should be piped
    to stdout (usually because they are long-running).
    """
    final_cmd = cmd[args]
    return final_cmd & TEE


def _run_pre_commit(venv):
    def _run_pre_commit_loop(retries_left):
        for path in _list_untracked():
            # Ensure pre-commit runs on all paths.
            # We don't want to git add . because this removes merge conflicts
            git("add", "--intent-to-add", str(path))
        try:
            _run_in_venv(venv, "pre-commit", "run", "--all-files", force_non_interactive=True)
        except ProcessExecutionError as err:
            if retries_left > 0 and check_pre_commit_rerun(err.stdout):
                return _run_pre_commit_loop(retries_left - 1)
            raise

    status("Running pre-commit hooks against all files. This can take a minute, please be patient")

    try:
        _run_pre_commit_loop(2)
        return True
    except ProcessExecutionError as err:
        _, failing = parse_pre_commit(err.stdout)
        if failing:
            msg = f"Please fix all ({len(failing)}) failing hooks"
        else:
            msg = f"Output: {err.stderr or err.stdout}"
        warn(f"Pre-commit is failing. {msg}")
        for i, failing_hook in enumerate(failing):
            warn(f"✗ Failing hook ({i + 1}): {failing_hook}", failing[failing_hook])
    return False


def _run_in_venv(venv, command, *args, force_non_interactive=False):
    venv_bin_dir = (venv / "bin").resolve()
    if isinstance(command, (str, Path)):
        command = venv_bin_dir / command
        try:
            cmd = local[venv_bin_dir / command]
        except CommandNotFound:
            # Maybe we just want to run something within a venv, like uv
            cmd = local[command]
    else:
        cmd = command
    with local.env(PATH=f"{venv_bin_dir}:{local.env['PATH']}", VIRTUAL_ENV=str(venv_bin_dir)):
        if force_non_interactive:
            return cmd[args].run()
        else:
            return _run(cmd, *args)


def _ensure_git():
    if Path(".git").is_dir():
        return
    git("init", "--initial-branch", "main")


def _list_untracked():
    for path in git("ls-files", "-z", "-o", "--exclude-standard").split("\x00"):
        if path:
            yield path


def remove_untracked_unwanted():
    """
    Fix Copier regenerating paths listed in skip_if_exists on updates until
    _copier_conf.operation is merged.
    """
    for path in _list_untracked():
        if any(fnmatch.fnmatch(path, ptrn) for ptrn in SKIP_IF_EXISTS_BOILERPLATE):
            Path(path).unlink()


def finish(msg, success, err_exit=False, extra=None):
    """
    Print final conclusion.

    We usually want to exit with 0 because failing here should not
    prevent an update, it's only a nice-to-have.
    """
    print("\n")
    if success is None:
        questionary.print(f"\n    ✓ {msg}", style="bold fg:ansiyellow bg:darkgreen")
        success = True
    elif success:
        questionary.print(f"\n    ✓ {msg}", style="bold bg:darkgreen")
    else:
        warn(f"    ✗ {msg}", extra)
    raise SystemExit(int(not success and err_exit))


if __name__ == "__main__":
    try:
        ctx = sys.argv[1]
    except IndexError:
        finish("Missing invocation context", False, True)
    if ctx == "init":
        init = True
    elif ctx == "migrate":
        init = False
    else:
        finish(f"Unknown invocation context: {ctx}", False, True)
    if os.environ.get("SKIP_INIT_MIGRATE", "0") == "1":
        finish(
            f"Skipping post-copy {'initialization' if init else 'migration'}, SKIP_INIT_MIGRATE is set",
            True,
        )
    try:
        _ensure_git()
        if not init:
            remove_untracked_unwanted()
        venv = _ensure_venv()
        if not _run_pre_commit(venv):
            finish(
                f"Successfully {'initialized' if init else 'migrated'} environment, "
                "but you need to fix the failing pre-commit hooks manually",
                None,
            )
    except Exception as err:  # pylint: disable=broad-except
        docs = (
            "https://salt-extensions.github.io/salt-extension-copier/topics/creation.html#first-steps"
            if init
            else "https://salt-extensions.github.io/salt-extension-copier/topics/updating.html#workflow"
        )
        finish(
            f"Failed {'initializing' if init else 'migrating'} environment: {err}",
            False,
            extra=f"No worries, just follow the manual steps documented here: {docs}",
        )
    finish(f"Successfully {'initialized' if init else 'migrated'} environment", True)
