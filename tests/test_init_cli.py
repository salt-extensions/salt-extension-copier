import platform
import sys

import pytest
from plumbum import local

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
def test_project_init_works(copie, answers, capfd, git):
    res = copie.copy(extra_answers=answers)
    assert_worked(res)
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


def _ensure_project_venv(**kwargs):
    """
    Run ``ensure_project_venv`` with the test Python in a subprocess.
    Must be called with the generated project as cwd. Pins ``pyver`` to
    the running interpreter by default since the configured `venv_python`
    is not guaranteed to be available on the test host.
    """
    kwargs.setdefault("pyver", f"{sys.version_info[0]}.{sys.version_info[1]}")
    kwargs_repr = ", ".join(f"{key}={val!r}" for key, val in kwargs.items())
    local[sys.executable](
        "-c",
        "import sys; "
        "sys.path.insert(0, 'tools'); "
        "from helpers.venv import ensure_project_venv; "
        f"ensure_project_venv({kwargs_repr})",
    )


def test_venv_system_site_packages_works(project):
    """
    Ensure $VENV_SYSTEM_SITE_PACKAGES=1 causes both the development venv
    and the nox session venvs to inherit system-wide packages and that
    the development venv is recreated when the setting changes.
    uv must be bypassed for such venvs since it ignores inherited packages.
    """

    def read_pyvenv_cfg(venv):
        cfg = {}
        for line in (venv / "pyvenv.cfg").read_text().splitlines():
            key, _, val = line.partition("=")
            cfg[key.strip()] = val.strip()
        return cfg

    with local.cwd(project.project_dir):
        with local.env(VENV_SYSTEM_SITE_PACKAGES="1"):
            _ensure_project_venv(reinstall=False)
        cfg = read_pyvenv_cfg(project.project_dir / ".venv")
        assert cfg["include-system-site-packages"] == "true"
        # uv pip install ignores inherited packages, so it must not be used
        # for such venvs, even when available. uv-created venvs contain
        # an `uv` key in pyvenv.cfg.
        assert "uv" not in cfg

        # The dev venv should be recreated isolated when the setting is unset
        _ensure_project_venv(reinstall=False)
        cfg = read_pyvenv_cfg(project.project_dir / ".venv")
        assert cfg.get("include-system-site-packages", "false") == "false"

        # nox session venvs should inherit system-wide packages as well.
        # The session itself fails since its requirements are not installed,
        # but the venv is created before that.
        with local.env(VENV_SYSTEM_SITE_PACKAGES="1", SKIP_REQUIREMENTS_INSTALL="1"):
            local[sys.executable]["-m", "nox", "-e", "lint-code"].run(retcode=None)
        session_venvs = list((project.project_dir / ".nox").glob("*/pyvenv.cfg"))
        assert len(session_venvs) == 1
        cfg = read_pyvenv_cfg(session_venvs[0].parent)
        assert cfg["include-system-site-packages"] == "true"


def test_venv_python_env_var_overrides_answer(project):
    """
    Ensure $VENV_PYTHON takes precedence over the committed `venv_python`
    answer when resolving the development venv Python version.
    """
    with local.cwd(project.project_dir):
        with local.env(VENV_PYTHON="3.99"):
            out = local[sys.executable](
                "-c",
                "import sys; "
                "sys.path.insert(0, 'tools'); "
                "from helpers.venv import get_venv_pyver; "
                "print(get_venv_pyver())",
            )
    assert out.strip() == "3.99"


def test_initialize_cli_works(project):
    """
    Ensure ``tools/initialize.py`` rejects unknown arguments and that
    ``reinstall="auto"`` (``--skip-install``) does not reinstall the
    project into an existing venv.
    """
    with local.cwd(project.project_dir):
        # Unknown arguments should be rejected before anything else runs
        retcode, _, stderr = local[sys.executable]["tools/initialize.py", "--bogus"].run(
            retcode=None
        )
        assert retcode == 2
        assert "unrecognized arguments: --bogus" in stderr
        # Create a bare venv, then ensure auto mode skips the installation
        _ensure_project_venv(reinstall=False)
        _ensure_project_venv(reinstall="auto")
        assert not list((project.project_dir / ".venv").rglob("*copiertest*"))


@pytest.mark.usefixtures("project_committed")
@pytest.mark.parametrize("skip_init_migrate", (False,), indirect=True)
@pytest.mark.parametrize("project", ("0.10.0",), indirect=True)
# Need to remove `resource` loader, not supported in 0.10.0
@pytest.mark.parametrize(
    "loaders",
    (
        [
            "auth",
            "beacon",
            "cache",
            "cloud",
            "engine",
            "executor",
            "fileserver",
            "grain",
            "log_handler",
            "matcher",
            "metaproxy",
            "module",
            "netapi",
            "output",
            "pillar",
            "pkgdb",
            "pkgfile",
            "proxy",
            "queue",
            "renderer",
            "returner",
            "roster",
            "runner",
            "sdb",
            "serializer",
            "state",
            "thorium",
            "token",
            "top",
            "wheel",
            "wrapper",
        ],
    ),
    indirect=True,
)
# The following deprecation is fixed in the current template,
# but is still triggered when rendering the old version.
@pytest.mark.filterwarnings(
    "ignore:`copier-templates-extensions` is renamed:DeprecationWarning",
)
def test_init_respects_venv_python(copie, project, project_venv, capfd):
    assert project_venv.pyver == "3.14"
    # update venv_python answer
    res = copie.update(project, {"venv_python": "3.12"})
    assert_worked(res, capfd=capfd)
    assert project_venv.pyver == "3.12"
