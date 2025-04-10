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
def project_committed(project):
    with local.cwd(project.project_dir):
        git = local["git"][
            "-c", "commit.gpgsign=false", "-c", "user.name=foobar", "-c", "user.email=foo@b.ar"
        ]
        git("init")
        git("add", ".")
        git("commit", "-m", "initial commit")
    return project


@pytest.fixture
def project_venv(project):
    with ProjectVenv(project.project_dir) as venv:
        yield venv


def pytest_make_parametrize_id(config, val, argname):  # pylint: disable=unused-argument
    if argname == "no_saltext_namespace":
        return f"{'no_' if val else ''}ns"
    if argname == "skip_init_migrate":
        return f"{'no_' if val else ''}init"
