# pylint: disable=missing-module-docstring,import-error,protected-access,missing-function-docstring
import datetime
import json
import os
import pathlib
import shutil
import sys
import tempfile

import nox
from nox.virtualenv import VirtualEnv

# Nox options
#  Reuse existing virtualenvs
nox.options.reuse_existing_virtualenvs = True
#  Don't fail on missing interpreters
nox.options.error_on_missing_interpreters = False

# Be verbose when running under a CI context
CI_RUN = (
    os.environ.get("JENKINS_URL") or os.environ.get("CI") or os.environ.get("DRONE") is not None
)
PIP_INSTALL_SILENT = CI_RUN is False
SKIP_REQUIREMENTS_INSTALL = os.environ.get("SKIP_REQUIREMENTS_INSTALL", "0") == "1"
EXTRA_REQUIREMENTS_INSTALL = os.environ.get("EXTRA_REQUIREMENTS_INSTALL")

COVERAGE_REQUIREMENT = os.environ.get("COVERAGE_REQUIREMENT") or "coverage==7.5.1"

# Prevent Python from writing bytecode
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Global Path Definitions
REPO_ROOT = pathlib.Path(__file__).resolve().parent
# Change current directory to REPO_ROOT
os.chdir(str(REPO_ROOT))

ARTIFACTS_DIR = REPO_ROOT / "artifacts"
# Make sure the artifacts directory exists
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
CUR_TIME = datetime.datetime.now().strftime("%Y%m%d%H%M%S.%f")
RUNTESTS_LOGFILE = ARTIFACTS_DIR / f"runtests-{CUR_TIME}.log"
COVERAGE_REPORT_DB = REPO_ROOT / ".coverage"
COVERAGE_REPORT_TESTS = ARTIFACTS_DIR.relative_to(REPO_ROOT) / "coverage-tests"


DEV_REQUIREMENTS = ("pylint",)

DOCS_REQUIREMENTS = (
    "sphinx",
    "sphinxcontrib-spelling",
    "sphinx-copybutton",
    "myst_parser",
    "furo",
    "sphinx-inline-tabs",
    "towncrier==22.12.0",
    "sphinxcontrib-towncrier",
    "sphinx_tippy",
)

DOCSAUTO_REQUIREMENTS = ("sphinx-autobuild",)

TESTS_REQUIREMENTS = (
    "copier>=9.1",
    "copier-templates-extensions",
    "plumbum",
    "pytest",
    "pytest-copie",
    "pyyaml",
    "virtualenv",
)


def _install_requirements(
    session,
    *passed_requirements,
):
    if SKIP_REQUIREMENTS_INSTALL is False:
        install_command = ["--progress-bar=off"]
        install_command += passed_requirements
        if EXTRA_REQUIREMENTS_INSTALL:
            session.log(
                "Installing the following extra requirements because the "
                "EXTRA_REQUIREMENTS_INSTALL environment variable was set: "
                "EXTRA_REQUIREMENTS_INSTALL='%s'",
                EXTRA_REQUIREMENTS_INSTALL,
            )
            install_command += [req.strip() for req in EXTRA_REQUIREMENTS_INSTALL.split()]
        session.install(*install_command, silent=PIP_INSTALL_SILENT)


@nox.session
def tests(session):
    _install_requirements(session, COVERAGE_REQUIREMENT, *TESTS_REQUIREMENTS)

    env = {
        # The full path to the .coverage data file. Makes sure we always write
        # them to the same directory
        "COVERAGE_FILE": str(COVERAGE_REPORT_DB),
        # Instruct sub processes to also run under coverage
        # "COVERAGE_PROCESS_START": str(REPO_ROOT / ".coveragerc"),
    }

    session.run("coverage", "erase")
    args = [
        "--rootdir",
        str(REPO_ROOT),
        f"--log-file={RUNTESTS_LOGFILE.relative_to(REPO_ROOT)}",
        "--log-file-level=debug",
        "--showlocals",
        "-ra",
        "-vv",
    ]
    if session._runner.global_config.forcecolor:
        args.append("--color=yes")
    if not session.posargs:
        args.append("tests/")
    else:
        for arg in session.posargs:
            if arg.startswith("--color") and args[0].startswith("--color"):
                args.pop(0)
            args.append(arg)
        for arg in session.posargs:
            if arg.startswith("-"):
                continue
            if arg.startswith(f"tests{os.sep}"):
                break
            try:
                pathlib.Path(arg).resolve().relative_to(REPO_ROOT / "tests")
                break
            except ValueError:
                continue
        else:
            args.append("tests/")
    try:
        session.run("coverage", "run", "-m", "pytest", *args, env=env)
    finally:
        try:
            session.run("coverage", "report", "--show-missing", "--include=tests/*")
        finally:
            # Move the coverage DB to artifacts/coverage in order for it to be archived by CI
            if COVERAGE_REPORT_DB.exists():
                shutil.move(str(COVERAGE_REPORT_DB), str(ARTIFACTS_DIR / COVERAGE_REPORT_DB.name))


class Tee:
    """
    Python class to mimic linux tee behaviour
    """

    def __init__(self, first, second):
        self._first = first
        self._second = second

    def write(self, buf):
        wrote = self._first.write(buf)
        self._first.flush()
        self._second.write(buf)
        self._second.flush()
        return wrote

    def fileno(self):
        return self._first.fileno()


def _lint(session, rcfile, flags, paths, tee_output=True):
    _install_requirements(
        session,
        *DEV_REQUIREMENTS,
        *TESTS_REQUIREMENTS,
    )

    if tee_output:
        session.run("pylint", "--version")
        pylint_report_path = os.environ.get("PYLINT_REPORT")

    cmd_args = ["pylint", f"--rcfile={rcfile}"] + list(flags) + list(paths)

    python_path_env_var = os.environ.get("PYTHONPATH") or None
    if python_path_env_var is None:
        python_path_env_var = REPO_ROOT
    else:
        python_path_entries = python_path_env_var.split(os.pathsep)
        if REPO_ROOT in python_path_entries:
            python_path_entries.remove(REPO_ROOT)
        python_path_entries.insert(0, REPO_ROOT)
        python_path_env_var = os.pathsep.join(python_path_entries)

    env = {
        # The updated python path so that the tests are importable
        "PYTHONPATH": python_path_env_var,
        "PYTHONUNBUFFERED": "1",
    }

    cmd_kwargs = {"env": env}

    if tee_output:
        stdout = tempfile.TemporaryFile(mode="w+b")
        cmd_kwargs["stdout"] = Tee(stdout, sys.__stdout__)

    try:
        session.run(*cmd_args, **cmd_kwargs)
    finally:
        if tee_output:
            stdout.seek(0)
            contents = stdout.read()
            if contents:
                contents = contents.decode("utf-8")
                sys.stdout.write(contents)
                sys.stdout.flush()
                if pylint_report_path:
                    # Write report
                    with open(pylint_report_path, "w", encoding="utf-8") as wfh:
                        wfh.write(contents)
                    session.log("Report file written to %r", pylint_report_path)
            stdout.close()


def _lint_pre_commit(session, rcfile, flags, paths):
    if "VIRTUAL_ENV" not in os.environ:
        session.error(
            "This should be running from within a virtualenv and "
            "'VIRTUAL_ENV' was not found as an environment variable."
        )
    if "pre-commit" not in os.environ["VIRTUAL_ENV"]:
        session.error(
            "This should be running from within a pre-commit virtualenv and "
            f"'VIRTUAL_ENV'({os.environ['VIRTUAL_ENV']}) does not appear to be a pre-commit virtualenv."
        )

    # Let's patch nox to make it run inside the pre-commit virtualenv
    session._runner.venv = VirtualEnv(
        os.environ["VIRTUAL_ENV"],
        interpreter=session._runner.func.python,
        reuse_existing=True,
        venv=True,
    )
    _lint(session, rcfile, flags, paths, tee_output=False)


@nox.session(python="3")
def lint(session):
    """
    Run PyLint against the code and the test suite. Set PYLINT_REPORT to a path to capture output.
    """
    session.notify("lint-tests")


@nox.session(name="lint-tests")
def lint_tests(session):
    """
    Run PyLint against the test suite. Set PYLINT_REPORT to a path to capture output.
    """
    flags = [
        "--disable=I,redefined-outer-name,missing-function-docstring,no-member,missing-module-docstring"
    ]
    if session.posargs:
        paths = session.posargs
    else:
        paths = ["tests/"]
    _lint(session, ".pylintrc", flags, paths)


@nox.session(name="lint-tests-pre-commit")
def lint_tests_pre_commit(session):
    """
    Run PyLint against the test suite. Set PYLINT_REPORT to a path to capture output.
    """
    flags = [
        "--disable=I,redefined-outer-name,missing-function-docstring,no-member,missing-module-docstring",
    ]
    if session.posargs:
        paths = session.posargs
    else:
        paths = ["tests/"]
    _lint_pre_commit(session, ".pylintrc", flags, paths)


@nox.session
def docs(session):
    """
    Build Docs
    """
    _install_requirements(
        session,
        *DOCS_REQUIREMENTS,
    )
    os.chdir("docs/")
    session.run("make", "clean", external=True)
    session.run("make", "linkcheck", "SPHINXOPTS=-W", external=True)
    session.run("make", "html", "SPHINXOPTS=-W", external=True)
    os.chdir(str(REPO_ROOT))


@nox.session(name="docs-html")
@nox.parametrize("clean", [False, True])
@nox.parametrize("include_api_docs", [False, True])
def docs_html(session, clean, include_api_docs):
    """
    Build Sphinx HTML Documentation

    TODO: Add option for `make linkcheck` and `make coverage`
          calls via Sphinx. Ran into problems with two when
          using Furo theme and latest Sphinx.
    """
    _install_requirements(
        session,
        *DOCS_REQUIREMENTS,
    )
    build_dir = pathlib.Path("docs", "_build", "html")
    sphinxopts = "-Wn"
    if clean:
        sphinxopts += "E"
    args = [sphinxopts, "--keep-going", "docs", str(build_dir)]
    session.run("sphinx-build", *args, external=True)


@nox.session(name="docs-dev")
def docs_dev(session) -> None:
    """
    Build and serve the Sphinx HTML documentation, with live reloading on file changes, via sphinx-autobuild.

    Note: Only use this in INTERACTIVE DEVELOPMENT MODE. This SHOULD NOT be called
        in CI/CD pipelines, as it will hang.
    """
    _install_requirements(
        session,
        *DOCS_REQUIREMENTS,
        *DOCSAUTO_REQUIREMENTS,
    )

    build_dir = pathlib.Path("docs", "_build", "html")

    # Allow specifying sphinx-autobuild options, like --host.
    args = ["--watch", "."] + session.posargs
    if not any(arg.startswith("--host") for arg in args):
        # If the user is overriding the host to something other than localhost,
        # it's likely they are rendering on a remote/headless system and don't
        # want the browser to open.
        args.append("--open-browser")
    args += ["docs", str(build_dir)]

    if build_dir.exists():
        shutil.rmtree(build_dir)

    session.run("sphinx-autobuild", *args)


@nox.session(name="docs-crosslink-info")
def docs_crosslink_info(session):
    """
    Report intersphinx cross links information
    """
    _install_requirements(
        session,
        install_extras=["docs"],
    )
    os.chdir("docs/")
    intersphinx_mapping = json.loads(
        session.run(
            "python",
            "-c",
            "import json; import conf; print(json.dumps(conf.intersphinx_mapping))",
            silent=True,
            log=False,
        )
    )
    intersphinx_mapping_list = ", ".join(list(intersphinx_mapping))
    try:
        mapping_entry = intersphinx_mapping[session.posargs[0]]
    except IndexError:
        session.error(
            f"You need to pass at least one argument whose value must be one of: {intersphinx_mapping_list}"
        )
    except KeyError:
        session.error(f"Only acceptable values for first argument are: {intersphinx_mapping_list}")
    session.run(
        "python", "-m", "sphinx.ext.intersphinx", mapping_entry[0].rstrip("/") + "/objects.inv"
    )
    os.chdir(str(REPO_ROOT))
