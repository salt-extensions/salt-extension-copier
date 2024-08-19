# Writing tests

You should have basic familiarity with [pytest](https://docs.pytest.org/en/stable/contents.html).

## Reference

This guide is intended to provide a quick overview and some best practices
specific to Salt extension development.

For details, refer to the [pytest-salt-factories documentation](https://pytest-salt-factories.readthedocs.io/en/latest/).

## Test types

There are three predefined categories of tests:

Unit
:   Unit tests are intended

    * to verify low-level/hard to reach behavior
    * as a fallback when other test types are too complex to implement

    They rely on patching and mocking to reduce dependencies of the
    code under test.

Functional
:   Functional tests should verify that functionality works as expected
    in a realistic environment and are the preferred way of testing.
    They do not have access to a running Salt master or minion daemon,
    hence they are faster than integration tests.

Integration
:   Integration tests should also verify that functionality works as expected
    in a realistic environment. They are needed when the functionality
    under test depends on a running Salt daemon.

### Unit tests

#### Setup and basics
In your test files, you usually import the modules to test directly.

In the simplest case, if your module does not reference any Salt-specific global dunders,
you can just call the function you want to test:

```python
from saltext.foo.modules import bar


def test_bar_baz():
    res = bar.baz()
    assert res == "worked"
```
If your module uses Salt-specific global dunders like `__salt__` or `__opts__`,
they are not defined yet since the module has not been initialized by the loader.
Calling the functions to test directly would throw a `NameError`.

To fix this, you can define a fixture named `configure_loader_modules`. Its return value
should be a mapping of modules to initialize to dunder content overrides.

The overrides can be empty, which just ensures that the dunders are defined:

```python
import pytest
from saltext.foo.modules import bar


@pytest.fixture
def configure_loader_modules():
    return {
        bar: {},
    }
```

The following code ensures the `__salt__` dunder contains the expected `defaults.merge` key
and that the `defaults` module has been initialized by the loader as well:

```python
import pytest
from salt.modules import defaults
from saltext.foo.modules import bar


@pytest.fixture
def configure_loader_modules():
    opts = {
        "value.for.test": True,
    }

    return {
        bar: {
            "__salt__": {
                "defaults.merge": defaults.merge,
            },
            "__opts__": opts,
        },
        defaults: {
            "__opts__": opts,
        },
    }
```

#### Common patterns
Unit tests usually rely on a subset of the following classes/functions:

* `unittest.mock.Mock`
* `unittest.mock.MagicMock`
* `unittest.mock.patch`

Please see the [unittest.mock docs](https://docs.python.org/3/library/unittest.mock.html) for details.

#### Important fixtures

##### `minion_opts`
Scope
:   function

Description
:   Provides default `__opts__` for use in unit tests which require realistic Salt minion opts.

##### `master_opts`
Scope
:   function

Description
:   Provides default `__opts__` for use in unit tests which require realistic Salt master opts.


### Functional tests
#### Setup and basics

Functional tests run in a familiar Salt environment, hence you do not need to import the modules to test.
The `loaders` fixture provides access to most Salt module types.
For example, if we're testing an execution module named `foobar`, we can access the initialized module like this:

```python
import pytest


@pytest.fixture
def foobar_mod(loaders):
    # this also works with `states`, `runners` etc.
    return loaders.modules.foobar


def test_stuff(foobar_mod):
    res = foobar_mod.baz()
    assert res == "worked"
```

If your module requires some specific Salt configuration in `__opts__`, you can define
configuration overrides via the `(minion|master)_config_overrides` fixtures **per test file** (they are `module`-scoped):

```python
import pytest


@pytest.fixture(scope="module")
def minion_config_overrides():
    return {
        "my_conf": "val",
    }
```

#### Common patterns

##### Creating temporary files

You can create temporary files using `pytest.helpers.temp_file`:

```python
import pytest
from textwrap import dedent


def test_stuff(tmp_path, loaders, minion_opts):
    file_name = "foo"
    file_contents = dedent(
        """
        {{ opts | json }}
        """
    ).strip()

    with pytest.helpers.temp_file(file_name, file_contents, tmp_path) as test_file:
        res = loaders.modules.slsutil.renderer(str(test_file))
        assert res == minion_opts
```

##### Testing state modules

###### Return value assertions
When you call a state module in a functional test, the return value is a wrapper
around the usual dictionary return. You should access its properties like this:

```python
def test_state_module(states):
    ret = states.my_state.present("foo")
    assert ret.result is True
    assert "as specified" in ret.comment
    assert not ret.changes
```

###### Test mode
You can also call state modules with `test=True` in functional tests:

```python
def test_state_module_test(states):
    ret = states.my_state.present("foo", test=True)
    assert ret.result is None
    assert "would have" in ret.comment
    assert ret.changes
```

#### Important fixtures
##### `loaders`
Scope
:   function

Description
:   Allows access to Salt loaders for several module types via its attributes.

##### `modules`
Scope
:   function

Description
:   Shortcut for `loaders.modules`.

##### `states`
Scope
:   function

Description
:   Shortcut for `loaders.states`.


### Integration tests
#### Setup and basics

Integration tests run in a familiar Salt environment, hence you do not need to import the modules to test.
You can run your modules using specific fixtures, which are wrappers around the familiar CLI commands.

Since this invokes a subprocess, the return value is a wrapper around the command's result:

```python
def test_stuff(salt_call_cli):
    res = salt_call_cli.run("foobar.baz")
    # Ensure Salt did not crash.
    assert res.returncode == 0
    # The actual return is stored as the `data` attribute.
    # It is hydrated into a proper Python type.
    assert res.data == {"worked": True}
```

If your modules need specific Salt configuration, you can override Salt master/minion configuration
in your project's `tests/conftest.py`, in a fixture named `(master|minion)_config`:

```python
import pytest


@pytest.fixture(scope="package")
def master_config():
    return {
        "ext_pillar": [
            {"my_pillar": {}},
        ],
    }
```

#### Common patterns

##### Creating temporary state files

Sometimes, you might need to test specific modules via the state compiler.
For this purpose, you can create a temporary state file in your Salt master's file_roots:

```python
from textwrap import dedent


def test_foobar_in_state_apply(salt_call_cli, master):
    sls = "foobar_test"
    file_contents = dedent(
        """
            Test this:
              foobar.present:
                - name: baz
        """
    )

    with master.state_tree.base.temp_file(f"{sls}.sls", file_contents):
        res = salt_call_cli.run("state.apply", sls)
        assert res.returncode == 0
```

#### Important fixtures

##### `salt_call_cli`
Scope
:   function

Description
:   Run `salt-call` commands. This is used for most integration tests.

    Example:

    ```python
    res = salt_call_cli.run("state.highstate")
    assert res.returncode == 0
    ```

##### `salt_run_cli`
Scope
:   function

Description
:   Run `salt-run` commands. This is used in runner integration tests or when
    you need to set up fixtures on the master, e.g. syncing the fileserver.

    Example:

    ```python
    res = salt_run_cli.run("fileserver.update")
    assert res.returncode == 0
    assert res.data is True
    ```

##### `salt_ssh_cli`
Scope
:   module

Description
:   Run `salt-ssh` commands. Usually used for `wrapper` module tests.
    Only available when the Salt extension has selected `wrapper` {question}`loaders`
    or explicitly opted in for {question}`ssh_fixtures`.

    Example:

    ```python
    res = salt_ssh_cli.run("foobar.baz")
    assert res.returncode == 0
    assert res.data == {"worked": True}
    ```
