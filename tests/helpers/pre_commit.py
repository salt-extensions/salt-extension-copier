import re

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
