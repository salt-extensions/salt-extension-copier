import pytest

from tests.helpers import assert_worked

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


@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
@pytest.mark.parametrize("source_url", ("org", "non_org", "non_github"), indirect=True)
def test_copy_works(copie, answers):
    res = copie.copy(extra_answers=answers)
    assert_worked(res)


@pytest.mark.parametrize("salt_version", ("3006.5",), indirect=True)
@pytest.mark.parametrize("max_salt_version", ("3007.0",), indirect=True)
def test_copy_works_with_salt_minor_version(copie, answers):
    res = copie.copy(extra_answers=answers)
    assert_worked(res)


@pytest.mark.usefixtures("project_committed")
@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
@pytest.mark.parametrize("project", ("0.0.2",), indirect=True)
@pytest.mark.parametrize("source_url", ("org", "non_org", "non_github"), indirect=True)
def test_update_from_002_works(copie, project):
    assert not (new_file := project.project_dir / "CODE-OF-CONDUCT.md").exists()
    res = copie.update(project)
    assert_worked(res)
    assert new_file.exists()
