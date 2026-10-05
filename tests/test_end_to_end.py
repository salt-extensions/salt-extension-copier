import shutil
import textwrap

import pytest
from plumbum import ProcessExecutionError
from plumbum import local

from tests.helpers.pre_commit import check_pre_commit_rerun
from tests.helpers.pre_commit import parse_pre_commit

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


def _commit_with_pre_commit(git, venv, max_retry=3, message="initial commit"):
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


@pytest.mark.parametrize(
    "source_url,typing_,no_saltext_namespace",
    (
        # namespace parametrization also helps with races in the pre-commit lint hook
        pytest.param(  # different defaults, especially require_autorelease_app
            "non_org", False, True, id="non_org_no_typing_no_ns"
        ),
        pytest.param("org", True, False, id="org_typing_ns"),
    ),
    indirect=True,
)
def test_first_commit_works(project, project_venv, git):
    """
    Ensure the generated project can be committed after generation
    with pre-commit hooks active.
    It should take at most three tries.
    """
    with local.cwd(project.project_dir):
        _commit_with_pre_commit(git, project_venv, max_retry=3)


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
        res = project_venv.run_module("nox", "-e", "tests-3", check=False)
        if res.returncode != 0:  # pragma: no cover
            # The caches might include a corrupt Salt wheel.
            # Evict it and retry once with a fresh session venv.
            project_venv.rm_cached("salt")
            shutil.rmtree(project.project_dir / ".nox", ignore_errors=True)
            res = project_venv.run_module("nox", "-e", "tests-3", check=False)
    assert res.returncode == 0


def _add_package_resource(project_dir):
    """
    Add a package-shaped resource type with a loader overlay directory,
    which requires special treatment in autodocs generation.
    Returns the import path of the resource type package.
    """
    rtype_dir = next((project_dir / "src").rglob("resources")) / "cluster"
    (rtype_dir / "modules").mkdir(parents=True)
    (rtype_dir / "__init__.py").write_text(textwrap.dedent('''\
            """
            Cluster resource type connection module.
            """
            __virtualname__ = "cluster"


            def init(opts):
                """
                Set up the cluster connection.
                """
            '''))
    (rtype_dir / "modules" / "__init__.py").touch()
    (rtype_dir / "modules" / "pod.py").write_text(textwrap.dedent('''\
            """
            Pod management for cluster resources.
            """


            def list_pods():
                """
                List the pods.

                CLI Example:

                .. code-block:: bash

                    salt 'cluster:prod' pod.list_pods
                """
                return []
            '''))
    return ".".join(rtype_dir.relative_to(project_dir / "src").parts)


@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
def test_docs_build_works(project, project_venv, git):
    rtype_import_path = _add_package_resource(project.project_dir)
    with local.cwd(project.project_dir):
        git("init")  # autodocs are not generated for untracked modules
        git("add", "--intent-to-add", ".")
        for check in (False, True):
            project_venv.run(
                project_venv.venv_python,
                str(project.project_dir / ".pre-commit-hooks" / "make-autodocs.py"),
                check=check,
            )
        ref_dir = project.project_dir / "docs" / "ref" / "resources"
        assert (ref_dir / f"{rtype_import_path}.rst").exists()
        assert (ref_dir / f"{rtype_import_path}.modules.pod.rst").exists()
        res = project_venv.run_module("nox", "-e", "docs", check=False)
    assert res.returncode == 0
