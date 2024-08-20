# Extraction of Salt core modules
TODO - ref https://github.com/salt-extensions/extension_migration

## Gotchas and considerations
### Unit test module imports

Unit tests import the modules directly. After migration, these imports
need to be adjusted, otherwise the tests will run against the modules found in Salt,
but still pass (or fail once they are removed in a future release). Example:

:::{tab} old
```python
from salt.modules import vault
```
:::

:::{tab} correct
```python
from saltext.vault.modules import vault
```
:::

### Unit test `tests.support` imports

Many unit tests in the Salt code base use an indirect import for `unittest.mock`.
Ensure you update them.

:::{tab} old
```python
from tests.support.mock import MagicMock, Mock, patch
```
:::

:::{tab} correct
```python
from unittest.mock import MagicMock, Mock, patch
```
:::

### Library dependencies

Some modules have library dependencies. Since they were included in Salt core,
which cannot possibly be shipped with every dependency,
they needed to account for the library not being present.
They typically use the following stanza to avoid a crash during import:

```python
HAS_LIBS = False

try:
    import foo
    HAS_LIBS = True
except ImportError:
    pass

__virtualname__ = "foobar"


def __virtual__():
    if HAS_LIBS:
        return __virtualname__
    return False, "Missing 'foo' library"
```

If the dependencies are all hard dependencies, you should declare them as such in your Saltext's
`pyproject.toml` (in `dependencies`) and remove the conditional loading:

```python
import foo

__virtualname__ = "foobar"


def __virtual__():
    return __virtualname__
```

Other modules can work with several, interchangeable libraries. For this case, you should at least
declare a dependency on one of the choices in your `optional-dependencies` for `tests`
in order to make the tests run.

### `__utils__`

Some Salt core modules access their utilities via the `__utils__` dunder instead of direct imports,
which ensures that the called utility function has access to Salt's global dunders.

This does not work in Salt extensions. If this is the case for your extracted set of modules,
you need to adjust the `utils` to not rely on the dunders, e.g. by passing in the required
references:

:::{tab} old

```python
# ------- salt.modules.foo ---------------
def get(entity):
    return __utils__["foo.query"](entity)
```

```python
# ------- salt.utils.foo -----------------
def query(entity):
    base_url = __opts__.get("foo_base_url", "https://foo.bar")
    profile = __salt__["config.option"]("foo_profile")
    return __utils__["http.query"](base_url, data=profile)
```
:::

:::{tab} correct
```python
# ------- saltext.foo.modules.foo -------
from saltext.foo.utils import foo


def get(entity):
    base_url = __opts__.get("foo_base_url", "https://foo.bar")
    return foo.query(base_url, entity, __salt__["config.option"])
```
```python
# ------- saltext.foo.utils.foo -------
import salt.utils.http


def query(base_url, entity, config_option):
    profile = config_option("foo_profile")
    return salt.utils.http.query(base_url, data=profile)
```
:::

### Pre-pytest tests

Not all Salt core tests have been converted to Pytest. You might need to convert them
in order to keep them running.

### Migrated tests in `tests/pytest`

All tests in Salt core that were migrated to Pytest are found in `tests/pytests`.
After a migration, this directory is replicated to the Saltext project, but
Salt extension projects assume that all tests are Pytest-based and found in `tests` directly.
To ensure everything works as expected, you should remove the `pytest` part
of the path by moving the tests one level up.

### Docs

Salt core modules are documented inline. You should consider extracting general parts of the
inline documentation into a separate topic inside the `docs/topics` directory.
