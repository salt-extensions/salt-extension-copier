import os

from packaging.version import Version

from .copier import load_copier_conf
from .pythonpath import project_tools

with project_tools():
    from helpers.copier import dump_answers
    from helpers.copier import load_answers
    from helpers.prompt import status


VERSION_FROM = Version(os.environ["VERSION_PEP440_FROM"])
VERSION_TO = Version(os.environ["VERSION_PEP440_TO"])
HEAD_UPDATE = bool(VERSION_TO.post)
STAGE = os.environ["STAGE"]


MIGRATIONS = []
COPIER_CONF = load_copier_conf()


def run_migrations():
    """
    Run registered migrations valid for this update.
    """
    if not MIGRATIONS:
        return None
    answers = load_answers()
    if STAGE == "before":
        return _run_migrations_before(answers)
    return _run_migrations_after(answers)


def _run_migrations_before(answers):
    """
    Run `before` migrations and dump the new answers.
    """
    for _, func in sorted(MIGRATIONS):
        ret = func(answers)
        if ret is not None:
            answers = ret
    dump_answers(answers)


def _run_migrations_after(answers):
    """
    Run `after` migrations.
    Answers can only be updated in the `before` stage.
    """
    for _, func in sorted(MIGRATIONS):
        func(answers.copy())


def migration(trigger, stage="after", desc=None, after=None):
    """
    Decorator for declaring a general migration.

    Decorated functions receive the complete answers dict as the sole parameter.

    trigger
        Version that triggers the migration when crossed during an update.
        Set this to `None` to always trigger the migration.

    stage
        Stage in which the migration should run, either `before` or `after`.
        Defaults to `after`.
        Set this to `None` to run the migration in both stages.

    desc
        A description that is printed when running the migration.
        Defaults to the decorated function's name with underscores
        replaced by spaces.

    Examples:

        # Triggered when updating from a version below 1.0.0 to at least 1.0.0
        @migration("1.0.0")
        def migrate_some_stuff_100(answers):
            ...

        # Answers can only be changed in the `before` stage
        @migration("1.0.0", stage="before")
        def migrate_some_stuff_100(answers):
            if answers["answer_a"] != "foo":
                answers["answer_b"] = "bar"

        # This runs during all updates and in both stages
        @migration(None, stage=None)
        def do_some_voodoo(_):
            ...
    """

    def wrapper(func):
        if stage is not None and STAGE != stage:
            return func
        if trigger is not None:
            trigger_version = Version(trigger)
            if VERSION_FROM >= trigger_version:
                return func
            # When updating with --vcs-ref=HEAD, run defined migrations independent of VERSION_TO.
            # Otherwise, VERSION_TO should be at least the version trigger
            if not (HEAD_UPDATE or trigger_version <= VERSION_TO):
                return func
        else:
            # Run version-independent migrations last
            trigger_version = Version("9999")

        # Other decorators delegate to this one, only create a general
        # migration if it's not already another subtype
        if not isinstance(func, Migration):
            nonlocal desc
            if desc is None:
                desc = func.__name__.replace("_", " ")
            elif not desc:
                desc = None
            func = Migration(func, desc=desc)
        global MIGRATIONS
        MIGRATIONS.append((trigger_version, func))
        return func

    return wrapper


def var_migration(trigger, varname, after=None):
    """
    Decorator for declaring an answer migration, e.g. when raising
    a minimum version or changing an answer's type.

    Checks if the answer is defined in the answers file, if so
    runs the decorated function with its value as the sole parameter.

    If the function returns an Ellipsis (...), resets the answer.
    If the function returns a value other than None, updates the answer.

    trigger
        Version that triggers the migration when crossed during an update.

    varname
        The name of the answer that should be migrated.

    Example:

        @var_migration("1.0.0", "foo")
        def migrate_foo_100(val):
            if val < 4:
                return 4
    """

    def wrapper(func):
        return migration(trigger, "before")(VarMigration(func, varname, after=after))

    return wrapper


def raise_minimum_version(trigger, varname, minimum):
    """
    Register a migration to increase the value of an answer representing
    a version to a minimum value.

    Examples:

        raise_minimum_version("1.0.0", "python", 3.8)
        raise_minimum_version("1.0.0", "python", "3.8")
    """

    def _raise_minimum(var):
        if Version(str(var)) < Version(str(minimum)):
            return type(var)(minimum)

    return var_migration(trigger, varname)(_raise_minimum)


def sync_minimum_version(trigger, varname):
    """
    Register a migration to increase the value of an answer representing
    a version to a minimum value, determined by its default answer.
    """
    default = COPIER_CONF[varname]["default"]
    return raise_minimum_version(trigger, varname, default)


class Migration:
    def __init__(self, func, desc=None, after=None):
        self.func = func
        self.desc = desc
        after = after or []
        if not isinstance(after, list):
            after = [after]
        self.after = after

    def __call__(self, answers):
        if self.desc is not None:
            status(f"Running migration: {self.desc}")
        return self.func(answers)

    def __lt__(self, other):
        """
        Ensure we can sort the list of migrations, even if there
        are multiple migrations for a single version.

        This also allows explicit ordering of migrations of the
        same version (or those without one).
        """
        if not isinstance(other, Migration):
            raise TypeError(f"Cannot compare Migration to {other!r}")
        return any(migration is self for migration in other.after)


class VarMigration(Migration):
    def __init__(self, func, varname, after=None):
        super().__init__(func, after=after)
        self.varname = varname

    def __call__(self, answers):
        if self.varname not in answers:
            return
        if (new_val := self.func(answers[self.varname])) is not None:
            if new_val is ...:
                status(f"Answer migration: Resetting {self.varname}")
                answers.pop(self.varname)
            else:
                status(
                    f"Answer migration: Updating {self.varname} from "
                    f"{answers[self.varname]!r} to {new_val!r}"
                )
                answers[self.varname] = new_val
        return answers
