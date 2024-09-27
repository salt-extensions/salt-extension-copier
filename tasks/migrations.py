from packaging.version import Version
from task_helpers.migrate import run_migrations
from task_helpers.migrate import var_migration


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


@var_migration("0.3.0", "python_requires")
def migrate_030_python_requires(val):
    """
    Raise minimum Python version to 3.8.
    """
    if Version(val) < Version("3.8"):
        return "3.8"


if __name__ == "__main__":
    run_migrations()
