# Running the test suite

:::{important}
Ensure you have already installed `nox`.
:::

## Basic
If you want to run all tests:

```bash
nox -e tests-3
```

## With parameters
Parameters for `pytest` can be passed through `nox` using `--`.

### Only unit tests

```bash
nox -e tests-3 -- tests/unit
```

### Rerun last failed tests

```bash
nox -e tests-3 -- --lf
```
