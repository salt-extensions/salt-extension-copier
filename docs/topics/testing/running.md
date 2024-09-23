(run-tests-target)=
# Running the test suite

:::{important}
Ensure `nox` is installed. If you executed the [first steps](first-steps-target) in some way, you should be ready to go.
:::

## Basic

To run all tests:

```bash
nox -e tests-3
```

## With parameters

You can pass `pytest` parameters through `nox` using `--`.

### Only unit tests

```bash
nox -e tests-3 -- tests/unit
```

### Rerun last failed tests

```bash
nox -e tests-3 -- --lf
```

### Speed up subsequent test runs

```bash
SKIP_REQUIREMENTS_INSTALL=1 nox -e tests-3
```

### Install extra dependencies

Useful if you want to invoke a fancier debugger from the tests:

```bash
EXTRA_REQUIREMENTS_INSTALL="ipdb" PYTHONBREAKPOINT="ipdb.set_trace" nox -e tests-3
```
