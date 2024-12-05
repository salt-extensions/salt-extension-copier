(write-tests-target)=
# Writing tests

Familiarity with [pytest](https://docs.pytest.org/en/stable/contents.html) is recommended.

## Overview

This guide offers a quick overview and best practices specific to Salt extension development. For more details, refer to the [pytest-salt-factories documentation](https://pytest-salt-factories.readthedocs.io/en/latest/).

## Test types

There are three main categories of tests:

**Unit**
:   - **Purpose:** Verify low-level or hard-to-reach behavior. Use as a fallback when other test types are too complex to implement.
    - **Approach:** Use patching and mocking to isolate the code under test.
    - **Example applications:** Exception handling, parsing, utility functions

**Functional**
:   - **Purpose:** Validate that functionality works as expected in a realistic, but lightweight environment (no running Salt daemons). Represents the preferred way of testing, if possible.
    - **Approach:** Test modules in a typical environment. Lightweight patching is allowed, but not encouraged.
    - **Example applications:** Execution/State/Runner/SDB module tests

**Integration**
:   - **Purpose:** Ensure functionality that depends on running daemons works correctly in a realistic environment.
    - **Approach:** Run modules using CLI command wrappers, simulating real-world conditions.
    - **Example applications:** Peer publishing, Salt Mine, Salt-SSH (wrapper modules), Reactor

### Unit tests

#### Setup and basics
In your test files, you typically import the modules you want to test directly.

If your module does not reference any Salt-specific global dunders, you can call the function you want to test directly:

```{code-block} python
:emphasize-lines: 1, 5

from saltext.foo.modules import bar


def test_bar_baz():
    res = bar.baz()
    assert res == "worked"
```

However, if your module uses Salt-specific global dunders like `__salt__` or `__opts__`, these dunders won’t be defined yet because the module hasn’t been initialized by the Salt loader. Attempting to call such functions directly would result in a `NameError`.

To resolve this, define a `configure_loader_modules` fixture. This fixture returns a mapping of modules to initialize to dunder content overrides.

The overrides can be empty, which just ensures that the dunders are defined:

```{code-block} python
:emphasize-lines: 2, 8

import pytest
from saltext.foo.modules import bar


@pytest.fixture
def configure_loader_modules():
    return {
        bar: {},
    }
```

If you need the `__salt__` dunder to contain specific keys such as `defaults.merge`, and ensure the `defaults` module is properly initialized by the loader, you can define the fixture as follows:

```{code-block} python
:emphasize-lines: 2-3, 13-21

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

* {py:class}`unittest.mock.Mock`
* {py:class}`unittest.mock.MagicMock`
* {py:func}`unittest.mock.patch`

Please see the {py:mod}`unittest.mock docs <unittest.mock>` for details.

##### Patching
When patching, avoid using the `@patch` decorator [because it can lead to unexpected issues](https://engblog.nextdoor.com/what-your-mocks-do-when-you-aren-t-looking-b278e0d9e201).

Instead, patch inside the test function or a fixture:

```py
from unittest.mock import patch

import pytest
from saltext.foo.modules import bar


@pytest.fixture
def patched_baz():
    with patch("saltext.foo.modules.bar._baz", autospec=True, return_value=True) as baz:
        yield baz


@pytest.mark.usefixtures("patched_baz")
def test_bar_stuff():
    assert bar.stuff() is True


def test_bar_other(patched_baz):
    assert bar.other() == {}
    patched_baz.assert_called_once_with("other")
```

#### Important fixtures

##### `minion_opts`
*Scope*
:   function

*Description*
:   Provides default `__opts__` for unit tests requiring realistic Salt minion opts.

##### `master_opts`
*Scope*
:   function

*Description*
:   Provides default `__opts__` for unit tests requiring realistic Salt master opts.


### Functional tests

#### Setup and basics

Functional tests operate within a familiar Salt environment, so you don't need to import the modules you’re testing. The `loaders` fixture provides access to most Salt module types.

For example, if you're testing an execution module named `foobar`, you can access the initialized module like this:

```{code-block} python
:emphasize-lines: 5, 7

import pytest


@pytest.fixture
def foobar_mod(loaders):
    # This also works with `states`, `runners` etc.
    return loaders.modules.foobar


def test_stuff(foobar_mod):
    res = foobar_mod.baz()
    assert res == "worked"
```

If your module requires specific Salt configurations in `__opts__`, you can define configuration overrides using the `minion_config_overrides` or `master_config_overrides` fixtures. These fixtures are scoped to the module, meaning they apply to all tests in the same file:

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

You can create temporary files using {py:func}`pytest.helpers.temp_file <saltfactories.utils.tempfiles.temp_file>`, preferrably as a context manager:

```{code-block} python
:emphasize-lines: 13

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

In this example, a temporary file is created, used, and cleaned up automatically within the test.

:::{tip}
Temporary files are often created within fixtures, not the tests themselves. This separation of concerns improves code reuse and ensures that the actual tests are concise.
:::

##### Testing state modules

###### Return value assertions

When calling state modules in a functional test, the return value is a wrapper around the standard dictionary return. You should access its properties using the following pattern:

```{code-block} python
:emphasize-lines: 3-5

def test_present_no_changes(states):
    ret = states.my_state.present("foo")
    assert ret.result is True
    assert "as specified" in ret.comment
    assert not ret.changes
```

###### Test mode

State modules can also be called with `test=True` during functional tests:

```{code-block} python
:emphasize-lines: 2

def test_present_create_testmode(states):
    ret = states.my_state.present("foo", test=True)
    assert ret.result is None
    assert "would have created" in ret.comment
    assert ret.changes
```

###### Test mode (parametrized)

A neat pattern to ensure you're testing states with and without test mode is to define a parametrized `testmode` fixture:

```{code-block} python
:emphasize-lines: 1-3,6,7

@pytest.fixture(params=(False, True))
def testmode(request):
    return request.param


def test_present_create(states, testmode):
    ret = states.my_state.present("foo", test=testmode)
    assert ret.result is not False
    assert (ret.result is None) is testmode
    assert ("would have" in ret.comment) is testmode
    assert "created" in ret.comment
    assert ret.changes
```

##### Testing modules in the state compiler context

You can create test `sls` files, {py:func}`state.apply <salt.modules.state.apply_>` (or {py:func}`state.show_sls <salt.modules.state.show_sls>`) them and assert against the {py:class}`return <saltfactories.utils.functional.MultiStateResult>`:

```{code-block} python
import pytest
from textwrap import dedent


@pytest.fixture
def foo_sls(state_tree):
    sls = "test_foo"
    contents = dedent(
        """
        {%- set name = salt["foo.echo"]("wat") %}

        Test foo state:
          foo.bard:
            - name: {{ name }}
        """
    ).strip()

    with pytest.helpers.temp_file(f"{sls}.sls", contents, state_tree):
        yield sls


def test_foo_in_state_compiler(foo_sls, loaders):
    ret = loaders.modules.state.apply(foo_sls)
    assert not ret.failed
    assert "wat" in ret.raw["foo_|-Test foo state_|-wat_|-bard"]["comment"]
```

#### Important fixtures

##### `loaders`
*Scope*
:   function

*Description*
:   An instance of {py:class}`Loaders <saltfactories.utils.functional.Loaders>`, provides access to Salt loaders for several module types via its attributes.

*Example*
:   ```python
    loaders.modules.test.ping()
    ```
##### `modules`
*Scope*
:   function

*Description*
:   Shortcut for `loaders.modules`.

##### `states`
*Scope*
:   function

*Description*
:   Shortcut for `loaders.states`.

##### `state_tree`
*Scope*
:   module

*Description*
:   The {py:class}`Path <pathlib.Path>` to the functional test minion's state directory.

### Integration tests

#### Setup and basics

Integration tests run within a familiar Salt environment, hence you don't need to import the modules you're testing. Instead, you can run your modules using specific fixtures that wrap familiar CLI commands.

These fixtures invoke a subprocess, so their return value is a wrapper around the command's result:

```{code-block} python
:emphasize-lines: 4, 7

def test_stuff(salt_call_cli):
    res = salt_call_cli.run("foobar.baz")
    # Ensure the execution did not error.
    assert res.returncode == 0
    # The actual return value is stored in the `data` attribute.
    # It is automatically hydrated into the appropriate Python type.
    assert res.data == {"worked": True}
```

If your modules require specific Salt configurations, you can override the Salt master or minion configuration in your project's `tests/conftest.py` by defining a fixture named `master_config` or `minion_config`:

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

To test specific modules within the context of the state machinery, you can create a temporary state file in the Salt master's `file_roots`:

```{code-block} python
:emphasize-lines: 14

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
*Scope*
:   function

*Description*
:   Runs `salt-call` commands, typically used in most integration tests.

*Example*
:   ```python
    res = salt_call_cli.run("state.highstate")
    assert res.returncode == 0
    ```

##### `salt_run_cli`
*Scope*
:   function

*Description*
:   Runs `salt-run` commands, often used in runner integration tests or for setting up master fixtures (e.g. syncing the fileserver).

*Example*
:   ```python
    res = salt_run_cli.run("fileserver.update")
    assert res.returncode == 0
    assert res.data is True
    ```

##### `salt_ssh_cli`
*Scope*
:   module

*Description*
:   Runs `salt-ssh` commands, usually for `wrapper` module tests. Available when the extension has enabled `wrapper` {question}`loaders` or {question}`ssh_fixtures`.

*Example*
:   ```python
    res = salt_ssh_cli.run("foobar.baz")
    assert res.returncode == 0
    assert res.data == {"worked": True}
    ```

##### `master`
*Scope*
:   package

*Description*
:   Provides an instance of {py:class}`saltfactories.daemons.master.SaltMaster`. Example uses include inspecting the current master configuration or creating temporary files in the state/pillar tree.

*Example*
:   Temporary state file in `base` env

    ```{parsed-literal}
    with {py:class}`master <saltfactories.daemons.master.SaltMaster>`.{py:class}`state_tree <saltfactories.utils.tempfiles.SaltStateTree>`.{py:class}`base <saltfactories.utils.tempfiles.SaltEnv>`.{py:meth}`temp_file <saltfactories.utils.tempfiles.SaltEnv.temp_file>`("file_name", "contents") as temp_sls:
    ```
:   Temporary pillar file in `prod` env

    ```{parsed-literal}
    with {py:class}`master <saltfactories.daemons.master.SaltMaster>`.{py:class}`pillar_tree <saltfactories.utils.tempfiles.SaltPillarTree>`.{py:class}`prod <saltfactories.utils.tempfiles.SaltEnv>`.{py:meth}`temp_file <saltfactories.utils.tempfiles.SaltEnv.temp_file>`("file_name", "contents") as temp_pillar:
    ```


##### `minion`
*Scope*
:   package

*Description*
:   Provides an instance of {py:class}`saltfactories.daemons.minion.SaltMinion`. Example uses include inspecting the current minion configuration or creating temporary files in the state/pillar tree when `file_client` is set to `local`.

:   Temporary state file in `prod` env

    ```{parsed-literal}
    with {py:class}`minion <saltfactories.daemons.minion.SaltMinion>`.{py:class}`state_tree <saltfactories.utils.tempfiles.SaltStateTree>`.{py:class}`prod <saltfactories.utils.tempfiles.SaltEnv>`.{py:meth}`temp_file <saltfactories.utils.tempfiles.SaltEnv.temp_file>`("file_name", "contents") as temp_sls:
    ```
:   Temporary pillar file in `base` env

    ```{parsed-literal}
    with {py:class}`minion <saltfactories.daemons.minion.SaltMinion>`.{py:class}`pillar_tree <saltfactories.utils.tempfiles.SaltPillarTree>`.{py:class}`base <saltfactories.utils.tempfiles.SaltEnv>`.{py:meth}`temp_file <saltfactories.utils.tempfiles.SaltEnv.temp_file>`("file_name", "contents") as temp_pillar:
    ```
