import pytest
from plumbum import ProcessExecutionError
from plumbum import local

from tests.helpers.copier_hlp import load_copier_yaml
from tests.helpers.venv import ProjectVenv

COPIER_CONF = load_copier_yaml()

pytestmark = [
    pytest.mark.usefixtures(
        "author",
        "author_email",
        "project_name",
        "no_saltext_namespace",
        "source_url",
    ),
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


@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
@pytest.mark.parametrize("project", ("0.0.2",), indirect=True)
@pytest.mark.parametrize("source_url", ("org", "non_org", "non_github"), indirect=True)
def test_update_from_002_works(copie, project):
    assert not (new_file := project / "CODE-OF-CONDUCT.md").exists()
    res = copie.update(project)
    _assert_worked(res)
    assert new_file.exists()


def test_first_commit_works(copie, answers):
    """
    Ensure the generated project can be committed after generation
    with pre-commit hooks active.
    It should take at most three tries.
    """
    res = copie.copy(extra_answers=answers)

    assert res.exit_code == 0
    assert res.exception is None
    assert res.project_dir.is_dir()

    with ProjectVenv(res.project_dir) as venv, local.cwd(res.project_dir):
        git = local["git"]["-c", "commit.gpgsign=false"]
        venv.run("pre-commit", "install")
        retry_count = 1
        saved_err = None

        while retry_count <= 3:
            try:
                git("add", ".")
                git("commit", "-m", "initial commit")
                break
            except ProcessExecutionError as err:
                retry_count += 1
                saved_err = err
        else:
            raise saved_err


@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
@pytest.mark.parametrize(
    "answers",
    (
        {
            "loaders": COPIER_CONF["loaders"]["choices"],
            "test_containers": True,
        },
    ),
    indirect=True,
)
def test_testsuite_works(project, project_venv):
    with local.cwd(project):
        res = project_venv.run(
            str(project_venv.venv_python), "-m", "nox", "-e", "tests-3", check=False
        )
    assert res.returncode == 0
