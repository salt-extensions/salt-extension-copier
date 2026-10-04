(envvars-target)=
# Environment variables

The following environment variables are respected by the tooling in generated projects.

## Project generation and updates

:::{envvar} SKIP_INIT_MIGRATE
When `1`, skips the [automatic initialization/migration](automatic-init-target) during `copier copy`/`copier update`.
:::

## Development environment

:::{envvar} VENV_SYSTEM_SITE_PACKAGES
When `1`, the development virtual environment and the {tool}`nox` session venvs [inherit system-wide packages](system-site-packages-target), easing development of OS-specific extensions. Implies a `venv` + `pip` fallback since {tool}`uv` does not consider inherited packages.
:::

:::{envvar} TOOLS_SILENT
When set, suppresses status output of the bundled {path}`developer tools <tools>`.
:::

:::{envvar} SKIP
Comma-separated list of {tool}`pre-commit` [hook IDs to skip](https://pre-commit.com/#temporarily-disabling-hooks). Useful on [platforms lacking prebuilt hook binaries](hook-install-target), e.g. FreeBSD.
:::

## `nox` sessions

:::{envvar} SKIP_REQUIREMENTS_INSTALL
When `1`, skips dependency installation in `nox` sessions, [speeding up repeated runs](run-tests-target).
:::

:::{envvar} EXTRA_REQUIREMENTS_INSTALL
Whitespace-separated list of extra requirements to install into the session venv, e.g. a debugger.
:::

:::{envvar} SALT_REQUIREMENT
Overrides the Salt requirement in `test`/`docs` sessions. Defaults to the project's minimum Salt version. The special value `salt==master` installs Salt from the git `master` branch, release branch values like `salt==3007.x` from the corresponding upstream git branch.
:::

:::{envvar} COVERAGE_REQUIREMENT
Overrides the pinned `coverage` requirement.
:::

:::{envvar} PYLINT_REPORT
Path to additionally write the `lint` sessions' output to.
:::

:::{envvar} PYENCHANT_LIBRARY_PATH
Path to the `enchant` library required by the docs spellcheck. Autodiscovered on most platforms, including Apple Silicon Homebrew installs.
:::

## Detected

* `CI`, `JENKINS_URL`, `DRONE` – indicate a CI context: `nox` sessions install dependencies verbosely, test daemons receive longer start timeouts and rootless Podman autodetection is disabled.
* `XDG_RUNTIME_DIR` – used to locate the rootless Podman socket for container tests.
