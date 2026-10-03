import pytest
import yaml

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


OS_CLASSIFIERS = {
    "Linux": "Operating System :: POSIX :: Linux",
    "macOS": "Operating System :: MacOS",
    "Windows": "Operating System :: Microsoft :: Windows",
    "FreeBSD": "Operating System :: POSIX :: BSD :: FreeBSD",
    "OpenBSD": "Operating System :: POSIX :: BSD :: OpenBSD",
}


@pytest.mark.parametrize(
    "answers,os_support",
    (
        ({}, ("Linux", "macOS", "Windows")),
        (
            {"os_support": ["FreeBSD", "OpenBSD"]},
            ("FreeBSD", "OpenBSD"),
        ),
    ),
    indirect=("answers",),
    ids=("default", "platform_specific"),
)
def test_pyproject_os_classifiers(copie, answers, os_support):
    res = copie.copy(extra_answers=answers)
    assert_worked(res)
    pyproject = (res.project_dir / "pyproject.toml").read_text()
    for os_name, classifier in OS_CLASSIFIERS.items():
        if os_name in os_support:
            assert f'"{classifier}",' in pyproject
        else:
            assert classifier not in pyproject


@pytest.mark.parametrize(
    "os_support",
    (
        None,
        ["Linux", "FreeBSD", "OpenBSD"],
        ["Linux"],
    ),
    indirect=(True),
    ids=("default", "vm_platforms", "linux-only"),
)
def test_test_workflow_os_jobs(project, os_support):
    workflow = project.project_dir / ".github" / "workflows" / "test-action.yml"
    jobs = yaml.safe_load(workflow.read_text())["jobs"]
    # The default Linux test distribution is Ubuntu, rendered as the `Linux` job
    expected = set(os_support)
    assert set(jobs) == expected
    if "Linux" in expected:
        ubuntu = jobs["Linux"]
        assert ubuntu["runs-on"] == "ubuntu-${{ matrix.osrelease }}"
        includes = ubuntu["strategy"]["matrix"]["include"]
        assert includes
        assert all({"salt-version", "python-version", "osrelease"} <= set(e) for e in includes)
    for os_name in set(os_support) & {"FreeBSD", "OpenBSD"}:
        steps = jobs[os_name]["steps"]
        start_vm = next(step for step in steps if step.get("name") == "Start VM")
        assert start_vm["uses"].startswith(f"vmactions/{os_name.lower()}-vm@")
        assert start_vm["with"]["cache-after-prepare"] is True
        assert "nox" in start_vm["with"]["prepare"]
        assert "{nox_version}" not in start_vm["with"]["prepare"]
        in_vm_steps = [
            step for step in steps if step.get("name") in ("Install Test Requirements", "Test")
        ]
        assert len(in_vm_steps) == 2
        assert all(step["shell"] == f"{os_name.lower()} {{0}}" for step in in_vm_steps)
        assert any("coverage-project.xml" in str(step) for step in steps)
        assert jobs[os_name]["strategy"]["matrix"]["osrelease"]
        # BSD tests run against the OS-packaged Salt release
        assert jobs[os_name]["env"]["VENV_SYSTEM_SITE_PACKAGES"] == "1"


@pytest.mark.parametrize(
    "answers",
    (
        {
            "linux_test_distros": ["Debian", "Alpine", "AlmaLinux", "Rocky Linux"],
            "debian_releases": ["13", "12"],
        },
    ),
    indirect=True,
)
def test_test_workflow_distro_jobs(project):
    workflow = project.project_dir / ".github" / "workflows" / "test-action.yml"
    jobs = yaml.safe_load(workflow.read_text())["jobs"]
    # Deselecting Ubuntu should not render the native runner job
    assert set(jobs) == {"Debian", "Alpine", "AlmaLinux", "Rocky-Linux", "Windows", "macOS"}
    for job_id, slug in (
        ("Debian", "debian"),
        ("Alpine", "alpine"),
        ("AlmaLinux", "almalinux"),
        ("Rocky-Linux", "rockylinux"),
    ):
        job = jobs[job_id]
        start_vm = next(step for step in job["steps"] if step.get("name") == "Start VM")
        assert start_vm["uses"].startswith(f"vmactions/{slug}-vm@")
        assert start_vm["with"]["custom-shell-name"] == slug
        prepare = start_vm["with"]["prepare"]
        # The tool version placeholders are substituted with the pins
        # from data/versions.yaml
        assert "nox==" in prepare
        assert "{nox_version}" not in prepare
        assert "{uv_version}" not in prepare
        in_vm_steps = [
            step
            for step in job["steps"]
            if step.get("name") in ("Install Test Requirements", "Test")
        ]
        assert len(in_vm_steps) == 2
        assert all(step["shell"] == f"{slug} {{0}}" for step in in_vm_steps)
        if job_id == "Alpine":
            # Alpine tests run against the OS-packaged Salt release, like the BSDs
            assert job["env"] == {"VENV_SYSTEM_SITE_PACKAGES": "1"}
            assert start_vm["with"]["envs"] == "SKIP_REQUIREMENTS_INSTALL VENV_SYSTEM_SITE_PACKAGES"
            assert job["strategy"]["matrix"]["osrelease"]
            assert "salt" in prepare
            assert all("tests-3 " in step["run"] for step in in_vm_steps)
        else:
            # Other distro VM jobs run the parametrized Salt/Python matrix
            assert job["env"] == {"SALT_REQUIREMENT": "salt==${{ matrix.salt-version }}"}
            includes = job["strategy"]["matrix"]["include"]
            assert includes
            assert all({"salt-version", "python-version", "osrelease"} <= set(e) for e in includes)
            assert start_vm["with"]["envs"] == "SKIP_REQUIREMENTS_INSTALL SALT_REQUIREMENT"
            assert "uv==" in prepare
            assert all("tests-${{ matrix.python-version }}" in step["run"] for step in in_vm_steps)
    assert {e["osrelease"] for e in jobs["Debian"]["strategy"]["matrix"]["include"]} == {
        "13",
        "12",
    }


@pytest.mark.parametrize("answers", ({"ubuntu_releases": ["24.04", "22.04"]},), indirect=True)
def test_test_workflow_ubuntu_releases(project):
    workflow = project.project_dir / ".github" / "workflows" / "test-action.yml"
    jobs = yaml.safe_load(workflow.read_text())["jobs"]
    includes = jobs["Linux"]["strategy"]["matrix"]["include"]
    assert {entry["osrelease"] for entry in includes} == {"24.04", "22.04"}


@pytest.mark.usefixtures("project_committed")
@pytest.mark.parametrize("no_saltext_namespace", (False, True), indirect=True)
@pytest.mark.parametrize("project", ("0.0.2",), indirect=True)
@pytest.mark.parametrize("source_url", ("org", "non_org", "non_github"), indirect=True)
# The following deprecations are fixed in the current template,
# but are still triggered when rendering the old version.
@pytest.mark.filterwarnings(
    "ignore:Returning a dict from the `hook` method:DeprecationWarning",
    "ignore:`copier-templates-extensions` is renamed:DeprecationWarning",
    r'ignore:"\\-" is an invalid escape sequence:DeprecationWarning',
)
def test_update_from_002_works(copie, project):
    assert not (new_file := project.project_dir / "CODE-OF-CONDUCT.md").exists()
    res = copie.update(project)
    assert_worked(res)
    assert new_file.exists()
