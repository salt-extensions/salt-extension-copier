import pytest
from plumbum import ProcessExecutionError
from plumbum import local

from tests.helpers.pre_commit import check_pre_commit_rerun
from tests.helpers.pre_commit import parse_pre_commit
from tests.helpers.venv import ProjectVenv

pytestmark = [
    pytest.mark.usefixtures(
        "author",
        "author_email",
        "project_name",
        "no_saltext_namespace",
        "loaders",
        "salt_version",
        "max_salt_version",
        "source_url",
        "workflows",
        "skip_init_migrate",
    ),
]


git = local["git"][
    "-c", "commit.gpgsign=false", "-c", "user.name=foobar", "-c", "user.email=foo@b.ar"
]


def _assert_worked(result):
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_dir.is_dir()


@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
@pytest.mark.parametrize("source_url", ("org", "non_org", "non_github"), indirect=True)
def test_copy_works(copie, answers):
    res = copie.copy(extra_answers=answers)
    _assert_worked(res)


@pytest.mark.parametrize("workflows", ("basic", "enhanced"), indirect=True)
@pytest.mark.parametrize("salt_version", ("3006.5",), indirect=True)
@pytest.mark.parametrize("max_salt_version", ("3007.0",), indirect=True)
def test_copy_works_with_salt_minor_version(copie, answers):
    res = copie.copy(extra_answers=answers)
    _assert_worked(res)


@pytest.mark.parametrize("skip_init_migrate", (False,), indirect=True)
def test_project_init_works(copie, answers):
    res = copie.copy(extra_answers=answers)
    _assert_worked(res)
    proj = res.project_dir
    # ensure git init worked and the default branch is main
    assert (proj / ".git").is_dir()
    with local.cwd(proj):
        assert "On branch main" in git("status")
    # ensure venv was created
    assert (proj / ".venv").is_dir()
    assert (proj / ".venv" / "pyvenv.cfg").exists()
    # ensure pre-commit ran
    assert (proj / "docs" / "ref" / "beacons" / "index.rst").exists()


@pytest.mark.parametrize("skip_init_migrate", (False,), indirect=True)
@pytest.mark.parametrize("project", ("0.2.0",), indirect=True)
def test_project_migration_works(copie, project, project_venv, request):
    def _check_version(expected):
        curr = project_venv.run_module("pre_commit", "--version").stdout.split()[-1]
        assert (curr == "2.13.0") is expected

    assert not (new_file := project / "CODE-OF-CONDUCT.md").exists()
    # delete boilerplate, should not be regenerated after update
    # also, all of this makes pylint fail
    boilerplate = [
        next(project.glob(ptrn))
        for ptrn in (
            "src/**/sdb/*_mod.py",
            "tests/unit/sdb/test_*.py",
            "tests/unit/fileserver/test_*.py",
        )
    ]
    for bpl in boilerplate:
        bpl.unlink()
    # downgrade pre-commit below required version
    project_venv.install("pre-commit==2.13.0")
    _check_version(True)
    request.getfixturevalue("project_committed")
    res = copie.update(project)
    _assert_worked(res)
    # ensure upgrade worked
    assert new_file.exists()
    # ensure boilerplate was not recreated
    for bpl in boilerplate:
        assert not bpl.exists()
    # ensure the project was reinstalled
    _check_version(False)


@pytest.mark.usefixtures("project_committed")
@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
@pytest.mark.parametrize("project", ("0.0.2",), indirect=True)
@pytest.mark.parametrize("source_url", ("org", "non_org", "non_github"), indirect=True)
def test_update_from_002_works(copie, project):
    assert not (new_file := project / "CODE-OF-CONDUCT.md").exists()
    res = copie.update(project)
    _assert_worked(res)
    assert new_file.exists()


def _commit_with_pre_commit(venv, max_retry=3, message="initial commit"):
    venv.run_module("pre_commit", "install")
    retry_count = 1
    saved_err = None

    while retry_count <= max_retry:
        try:
            git("add", ".")
            git("commit", "-m", message)
            break
        except ProcessExecutionError as err:
            retry_count += 1
            saved_err = err
            if not check_pre_commit_rerun(err.stderr):
                retry_count = max_retry + 1
    else:
        passing, failing = parse_pre_commit(saved_err.stderr)
        msg = f"pre-commit failure\nPassing: {', '.join(passing)}\nFailing: {', '.join(failing)}"
        for hook, out in failing.items():
            msg += f"\n\n{hook}:\n{out}"
        raise AssertionError(msg)


# We need to test both org and enhanced workflows (with actionlint/shellcheck)
@pytest.mark.parametrize("source_url", ("org", "non_org"), indirect=True)
def test_first_commit_works(project):
    """
    Ensure the generated project can be committed after generation
    with pre-commit hooks active.
    It should take at most three tries.
    """
    with ProjectVenv(project) as venv, local.cwd(project):
        _commit_with_pre_commit(venv, max_retry=3)


@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
@pytest.mark.parametrize(
    "answers",
    (
        {
            "test_containers": True,
        },
    ),
    indirect=True,
)
def test_testsuite_works(project, project_venv):
    with local.cwd(project):
        res = project_venv.run_module("nox", "-e", "tests-3", check=False)
    assert res.returncode == 0


@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
def test_docs_build_works(project, project_venv):
    with ProjectVenv(project) as venv, local.cwd(project):
        for check in (False, True):
            venv.run(
                venv.venv_python,
                str(project / ".pre-commit-hooks" / "make-autodocs.py"),
                check=check,
            )
        res = project_venv.run_module("nox", "-e", "docs", check=False)
    assert res.returncode == 0
