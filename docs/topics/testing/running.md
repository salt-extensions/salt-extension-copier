(run-tests-target)=
# Running the test suite

:::{important}
Ensure {tool}`nox` is installed. If you executed the [first steps](first-steps-target) in some way, you should be ready to go.
:::

## Basic

To run all tests with the {envvar}`selected venv Python <VENV_PYTHON>`:

```bash
nox -e test
# or: make tests
```

## With parameters

You can pass {tool}`pytest` parameters through {tool}`nox` using `--`.

### Only unit tests

```bash
nox -e test -- tests/unit
```

### Rerun last failed tests

```bash
nox -e test -- --lf
```

### Speed up subsequent test runs

```bash
SKIP_REQUIREMENTS_INSTALL=1 nox -e test
```

### Install extra dependencies

Useful if you want to invoke a fancier debugger from the tests:

```bash
EXTRA_REQUIREMENTS_INSTALL="ipdb" PYTHONBREAKPOINT="ipdb.set_trace" nox -e test
```

### Test against a specific Salt version

```bash
SALT_REQUIREMENT="salt~=3006.0" nox -e test
```

:::{tip}
{envvar}`SALT_REQUIREMENT` also understands upstream git refs: `salt==master` installs Salt from the `master` branch, release branch values like `salt==3007.x` from the corresponding release branch. This allows testing against unreleased changes.
:::

### Test against a specific Python version

```bash
nox -e tests-3.12  # or nox --python=3.12 -e tests
```

### Test against system-wide packages

Useful if some dependencies are only available as system packages, e.g. when developing OS-specific extensions:

```bash
VENV_SYSTEM_SITE_PACKAGES=1 nox -e test
```

See [Inheriting system-wide packages](system-site-packages-target) for details. Remember to remove existing session venvs (`make clean` or `rm -rf .nox`) when toggling this setting.
