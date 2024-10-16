"""
Run migrations between template versions during updates.
"""

from packaging.version import Version
from task_helpers.copier import load_data_yaml
from task_helpers.migrate import COPIER_CONF
from task_helpers.migrate import migration
from task_helpers.migrate import run_migrations
from task_helpers.migrate import status
from task_helpers.migrate import sync_minimum_version
from task_helpers.migrate import var_migration

# 0.5.0 migrates all projects to the enhanced workflows, which
# require accurate Salt versions to generate sensible test matrices.
# The default values always represent the extremes, so sync them
# during all updates from now on. This avoids having to create
# separate migrations for future updates.
sync_minimum_version(None, "max_salt_version")
sync_salt_version = sync_minimum_version(None, "salt_version")


@migration(None, "before", desc=False, after=sync_salt_version)
def ensure_minimum_python_requires(answers):
    """
    Ensure the minimum Python version is respected during each update.
    We cannot use sync_minimum_version for this because the default
    value is computed in Jinja. Let's replicate the Jinja here.
    """
    if "python_requires" not in answers:
        return

    salt_python_support = load_data_yaml("salt_python_support")
    selected_salt_version = int(
        float(answers.get("salt_version", COPIER_CONF["salt_version"]["default"]))
    )
    default = ".".join(str(x) for x in salt_python_support[selected_salt_version]["min"])
    current = answers["python_requires"]

    if Version(str(current)) < Version(str(default)):
        new = type(current)(default)
        status(f"Answer migration: Updating python_requires from {current!r} to {new!r}")
        answers["python_requires"] = new
    return answers


@var_migration("0.4.5", "max_salt_version")
def migrate_045_max_salt_version(val):
    """
    Change max_salt_version from int to str.
    """
    if not isinstance(val, str):
        return str(val)


@var_migration("0.3.7", "docs_url")
def migrate_037_docs_url(val):
    """
    If docs_url is empty, reset it to propose the new default.
    """
    if not val:
        return ...


if __name__ == "__main__":
    run_migrations()
