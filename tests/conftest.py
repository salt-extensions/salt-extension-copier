import os
from itertools import islice

import pytest
from plumbum import local

from tests.helpers.copier_hlp import load_copier_yaml
from tests.helpers.venv import ProjectVenv


@pytest.fixture(scope="session")
def copier_yaml():
    return load_copier_yaml()


@pytest.fixture
def project_name(request):
    return getattr(request, "param", "copiertest")


@pytest.fixture
def author(request):
    return getattr(request, "param", "Foo Bar")


@pytest.fixture
def author_email(request):
    return getattr(request, "param", "foo@b.ar")


@pytest.fixture
def loaders(copier_yaml, request):
    return getattr(request, "param", copier_yaml["loaders"]["choices"])


@pytest.fixture(params=(False,))
def no_saltext_namespace(request):
    return request.param


@pytest.fixture
def salt_version(copier_yaml, request):
    return getattr(request, "param", copier_yaml["salt_version"]["default"])


@pytest.fixture
def max_salt_version(copier_yaml, request):
    return getattr(request, "param", copier_yaml["max_salt_version"]["default"])


@pytest.fixture
def venv_python(request):
    return getattr(request, "param", None)


@pytest.fixture(params=("org",))
def source_url(project_name, request):
    if not request.param:
        return None
    if request.param == "org":
        return f"https://github.com/salt-extensions/saltext-{project_name}"
    if request.param == "non_org":
        return f"https://github.com/foo/{project_name}"
    if request.param == "non_github":
        return f"https://gitlab.com/foo/bar/{project_name}"
    raise ValueError(f"Invalid parameter for source_url: '{request.param}'")


@pytest.fixture
def workflows(source_url, request):
    # Dropped in release 0.5.0, but still needed for upgrade tests
    default = "org" if "github.com/salt-extensions/" in source_url else "enhanced"
    return getattr(request, "param", default)


@pytest.fixture(params=((),))
def answers(
    author,
    author_email,
    loaders,
    max_salt_version,
    no_saltext_namespace,
    salt_version,
    project_name,
    venv_python,
    workflows,
    request,
):
    defaults = {
        "project_name": project_name,
        "author": author,
        "author_email": author_email,
        "loaders": loaders,
        "no_saltext_namespace": no_saltext_namespace,
        "salt_version": salt_version,
        "max_salt_version": max_salt_version,
        "workflows": workflows,
    }
    if venv_python is not None:
        defaults["venv_python"] = venv_python
    defaults.update(request.param)
    return {k: v for k, v in defaults.items() if v is not None}


@pytest.fixture(params=(True,))
def skip_init_migrate(request):
    # Copier uses plumbum as well, which is already initialized.
    # Overriding via os.environ thus has no effect.
    with local.env(SKIP_INIT_MIGRATE=str(int(request.param))):
        yield bool(request.param)


@pytest.fixture
def project(answers, request, copie, skip_init_migrate):  # pylint: disable=unused-argument
    vcs_ref = getattr(request, "param", "HEAD")
    res = copie.copy(extra_answers=answers, vcs_ref=vcs_ref)

    assert res.exit_code == 0
    assert res.exception is None
    assert res.project_dir.is_dir()

    yield res


@pytest.fixture
def git():
    return local["git"][
        "-c", "commit.gpgsign=false", "-c", "user.name=foobar", "-c", "user.email=foo@b.ar"
    ]


@pytest.fixture
def project_committed(project, git):
    with local.cwd(project.project_dir):
        git("init")
        git("add", ".")
        git("commit", "-m", "initial commit", "--no-verify")
    return project


@pytest.fixture
def project_venv(project):
    with ProjectVenv(project.project_dir) as venv:
        yield venv


# Rough relative test costs. xdist distributes tests in collection order,
# so sorting the heaviest ones first gets them started early, minimizing
# the chance of a single straggler dominating the suite's wall clock time.
# The `worksteal` scheduler rebalances whatever this ordering cannot foresee.
TEST_WEIGHTS = {
    "test_project_migration_works": 100,
    "test_testsuite_works": 90,
    "test_docs_build_works": 80,
    "test_first_commit_works": 70,
    "test_project_init_works": 60,
    "test_update_from_002_works": 50,
}


def pytest_collection_modifyitems(items):
    items.sort(
        key=lambda item: TEST_WEIGHTS.get(getattr(item, "originalname", item.name), 0),
        reverse=True,
    )
    # The `worksteal` scheduler initially distributes the collection to the
    # workers evenly as contiguous chunks, so consecutive heavy tests would
    # start on the same worker and only run in parallel once stolen by an
    # idle one. Reorder the collection so each worker's initial chunk begins
    # with one of the heaviest tests, ensuring they all start immediately.
    workers = int(os.environ.get("PYTEST_XDIST_WORKER_COUNT", "0"))
    if workers < 2 or len(items) <= workers:
        return
    heads = items[:workers]
    rest = iter(items[workers:])
    reordered = []
    remaining = len(items)
    for i, head in enumerate(heads):
        # Mirrors the scheduler's initial chunk size calculation
        chunksize = remaining // (workers - i)
        remaining -= chunksize
        reordered.append(head)
        reordered.extend(islice(rest, chunksize - 1))
    items[:] = reordered


def pytest_make_parametrize_id(config, val, argname):  # pylint: disable=unused-argument
    if argname == "no_saltext_namespace":
        return f"{'no_' if val else ''}ns"
    if argname == "skip_init_migrate":
        return f"{'no_' if val else ''}init"
