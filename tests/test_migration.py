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


@pytest.mark.parametrize("skip_init_migrate", (False,), indirect=True)
@pytest.mark.parametrize("project", ("0.7.2",), indirect=True)
@pytest.mark.parametrize("max_salt_version", ("3007",), indirect=True)
# The following deprecations are fixed in the current template,
# but are still triggered when rendering the old version.
@pytest.mark.filterwarnings(
    "ignore:Returning a dict from the `hook` method:DeprecationWarning",
    "ignore:`copier-templates-extensions` is renamed:DeprecationWarning",
)
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
    assert project_venv.pyver == "3.10"
    # Windows has issues here. For some reason, pre-commit runs make-autodocs.py
    # with the wrong Python version there. This fixture skips pre-commit.
    request.getfixturevalue("project_committed")
    res = copie.update(project)
    assert_worked(res, capfd=capfd)
    # ensure the upgrade worked
    assert indicator not in docs_action.read_text()
    # ensure boilerplate was not recreated
    for bpl in boilerplate:
        assert not bpl.exists()
    # ensure the project was reinstalled
    _check_version(False)
    # ensure the venv was recreated with the correct Python
    assert project_venv.pyver == "3.14"
