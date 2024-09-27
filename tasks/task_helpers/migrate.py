import os

from packaging.version import Version

from .pythonpath import project_tools

with project_tools():
    from helpers.copier import dump_answers
    from helpers.copier import load_answers


VERSION_FROM = Version(os.environ["VERSION_PEP440_FROM"])
VERSION_TO = Version(os.environ["VERSION_PEP440_TO"])
HEAD_UPDATE = bool(VERSION_TO.post)
STAGE = os.environ["STAGE"]


MIGRATIONS = []


class Migration:
    def __init__(self, func):
        self.func = func

    def __call__(self, answers):
        return self.func(answers)


class VarMigration(Migration):
    def __init__(self, func, varname):
        super().__init__(func)
        self.varname = varname

    def __call__(self, answers):
        if self.varname not in answers:
            return
        if (new_val := self.func(answers[self.varname])) is not None:
            if new_val is ...:
                answers.pop(self.varname)
            else:
                answers[self.varname] = new_val
        return answers


def migration(trigger, stage="after"):
    def wrapper(func):
        if STAGE != stage:
            return func
        trigger_version = Version(trigger)
        if VERSION_FROM >= trigger_version:
            return func
        # When updating with --vcs-ref=HEAD, run defined migrations independent of VERSION_TO.
        # Otherwise, VERSION_TO should be at least the version trigger
        if not (HEAD_UPDATE or trigger_version <= VERSION_TO):
            return func

        if not isinstance(func, Migration):
            func = Migration(func)
        global MIGRATIONS
        MIGRATIONS.append((trigger_version, func))
        return func

    return wrapper


def var_migration(trigger, varname):
    def wrapper(func):
        return migration(trigger, "before")(VarMigration(func, varname))

    return wrapper


def run_migrations():
    if not MIGRATIONS:
        return
    answers = load_answers()
    for _, func in sorted(MIGRATIONS):
        func(answers)
    dump_answers(answers)
