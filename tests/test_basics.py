import platform

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


@pytest.mark.parametrize("salt_version", ("3006.5",), indirect=True)
@pytest.mark.parametrize("max_salt_version", ("3007.0",), indirect=True)
def test_copy_works_with_salt_minor_version(copie, answers):
    res = copie.copy(extra_answers=answers)
    _assert_worked(res)


@pytest.mark.parametrize("skip_init_migrate", (False,), indirect=True)
def test_project_init_works(copie, answers, capfd):
    res = copie.copy(extra_answers=answers)
    _assert_worked(res)
    # ensure the environment initialization did not fail
    # (it does not cause an exit code > 0 since it's optional)
    assert "Failed initializing environment" not in capfd.readouterr().err
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
    # ensure extra dev tools can be installed by passing --extras
    black_path = proj / ".venv/bin/black"
    if platform.system() == "Windows":
        black_path = proj / ".venv/Scripts/black.exe"
    assert not black_path.exists()
    with local.cwd(proj):
        local["python"]("tools/initialize.py", "--extras")
    assert black_path.exists()


@pytest.mark.parametrize("skip_init_migrate", (False,), indirect=True)
@pytest.mark.parametrize("project", ("0.7.2",), indirect=True)
def test_project_migration_works(copie, project, project_venv, request, capfd):
    """
    Ensure the generated project can be updated as expected
    and the virtualenv is reinstalled after with new requirements.

    Because of several breaking changes in Copier and a bug in
    version 0.6.0 venv Python selection, we cannot test this
    reliably with versions below 0.7.2, which has been hotfixed
    to work with Copier 9.7+.
    """

    def _check_version(expected):
        out = project_venv.run_module("nox", "--version")
        curr = out.stderr.strip()
        assert (curr == "2023.4.22") is expected

    # This is the tagged version of actions/setup-python in version 0.7.2
    indicator = "42375524e23c412d93fb67b49958b491fce71c38"
    docs_action = project.project_dir / ".github" / "workflows" / "docs-action.yml"
    assert indicator in docs_action.read_text()
    # delete boilerplate, should not be regenerated after update
    # also, all of this makes pylint fail
    boilerplate = [
        next(project.project_dir.glob(ptrn))
        for ptrn in (
            "src/**/sdb/*_mod.py",
            "tests/unit/sdb/test_*.py",
            "tests/unit/fileserver/test_*.py",
        )
    ]
    for bpl in boilerplate:
        bpl.unlink()
    # downgrade nox below minimum version
    project_venv.install("nox==2023.4.22")
    _check_version(True)
    request.getfixturevalue("project_committed")
    # TODO: When there is 0.7.4 or similar, remove vcs_ref again.
    # This is needed because 0.7.3 and 0.7.2 point to different branches
    # because of a hotfix, so Copier thinks we're upgrading to 0.7.1-postsomething
    # when not specifying a specific tag.
    res = copie.update(project, vcs_ref="0.7.3")
    _assert_worked(res)
    # ensure the environment migration did not fail
    # (it does not cause an exit code > 0 since it's optional)
    assert "Failed migrating environment" not in capfd.readouterr().err
    # ensure the upgrade worked
    assert indicator not in docs_action.read_text()
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
    assert not (new_file := project.project_dir / "CODE-OF-CONDUCT.md").exists()
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


def test_first_commit_works(project):
    """
    Ensure the generated project can be committed after generation
    with pre-commit hooks active.
    It should take at most three tries.
    """
    with ProjectVenv(project.project_dir) as venv, local.cwd(project.project_dir):
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
    with local.cwd(project.project_dir):
        # Force re-build of Salt in case pip cache includes corrupt wheel
        project_venv.run_module("pip", "cache", "remove", "salt")
        res = project_venv.run_module("nox", "-e", "tests-3", check=False)
    assert res.returncode == 0


@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
def test_docs_build_works(project, project_venv):
    with ProjectVenv(project.project_dir) as venv, local.cwd(project.project_dir):
        for check in (False, True):
            venv.run(
                venv.venv_python,
                str(project.project_dir / ".pre-commit-hooks" / "make-autodocs.py"),
                check=check,
            )
        res = project_venv.run_module("nox", "-e", "docs", check=False)
    assert res.returncode == 0
