import os
import sys

from task_helpers.pythonpath import project_tools

with project_tools():
    from helpers import prompt
    from helpers.copier import finish_task
    from helpers.git import ensure_git
    from helpers.pre_commit import run_pre_commit
    from helpers.venv import ensure_project_venv

# Globs for files that should not be regenerated during updates if deleted.
# This functionality can be removed once _copier_conf.operation is available.
SKIP_IF_EXISTS_BOILERPLATE = (
    "src/**/*_mod.py",
    "tests/**/test_*.py",
)


if __name__ == "__main__":
    try:
        ctx = sys.argv[1]
    except IndexError:
        finish_task("Missing invocation context", False, True)
    if ctx == "init":
        init = True
    elif ctx == "migrate":
        init = False
    else:
        finish_task(f"Unknown invocation context: {ctx}", False, True)

    if os.environ.get("SKIP_INIT_MIGRATE", "0") == "1":
        finish_task(
            f"Skipping post-copy {'initialization' if init else 'migration'}, SKIP_INIT_MIGRATE is set",
            True,
        )
    try:
        prompt.ensure_utf8()
        ensure_git()
        venv = ensure_project_venv()
        if not run_pre_commit(venv):
            finish_task(
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
        finish_task(
            f"Failed {'initializing' if init else 'migrating'} environment: {err}",
            False,
            extra=f"No worries, just follow the manual steps documented here: {docs}",
        )
    finish_task(f"Successfully {'initialized' if init else 'migrated'} environment", True)
