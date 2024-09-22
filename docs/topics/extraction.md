# Extraction of Salt core modules

## Scripted example

A tool named [saltext-migrate](https://github.com/salt-extensions/salt-extension-migrate) was created based on the [manual example](manual-extraction-example) below. It removes many obstacles in the extraction process. Let’s use the same example module (`stalekey`).

### 1. Install `saltext-migrate` and `git-filter-repo`

:::{tab} pipx
```bash
pipx install git-filter-repo
pipx install git+https://github.com/salt-extensions/salt-extension-migrate
```
:::
:::{tab} pip
```bash
pip install git-filter-repo git+https://github.com/salt-extensions/salt-extension-migrate
```

If you want to install using `pip`, consider creating a virtual environment beforehand.
:::

### 2. Run the tool

:::{important}
Run the tool inside a dedicated directory serving as the working directory for all your Salt extension migrations. This avoids accidental data loss and speeds up repeated migrations.
:::

```bash
mkdir migrated-saltexts && cd migrated-saltexts
saltext-migrate stalekey
```

The tool will:

1. [Ensure Salt is cloned and the history analysis is available](clone-analyze-target)
2. Filter for paths containing `stalekey` and ask for approval
3. [Filter the history into a separate branch](filter-branch-target), renaming paths as needed
4. Auto-[cleanup the history](clean-history-target), as far as possible non-interactively
5. [Run copier](populate-repo-target) with sane defaults and remove the project starter boilerplate
6. [Create a virtual environment](migration-venv-target) for your project
7. [Apply rewrites](migration-clean-up-target) (with fixes and improvements versus `salt-rewrite`)
8. Install and run pre-commit
9. Provide an overview of issues to fix and next steps

(manual-extraction-example)=
## A manual module extraction example

Below are some rough steps to extract an existing set of modules into an extension while preserving the Git history. Let's use the `stalekey` engine as an example.

### 1. Install the Git history filtering tool

:::{tab} pipx
```shell
pipx install git-filter-repo
```
:::
:::{tab} pip
```shell
pip install git-filter-repo
```

If you want to install using `pip`, consider creating a virtual environment beforehand.
:::

(clone-analyze-target)=
### 2. Clone the Salt repo and analyze its history

```shell
mkdir workdir && cd workdir
git clone https://github.com/saltstack/salt --single-branch
cd salt
git filter-repo --analyze
tree .git/filter-repo/analysis/
grep stalekey .git/filter-repo/analysis/path-{all,deleted}-sizes.txt | \
    awk '{print $NF}' | sort | uniq | \
    grep -vE '^(.github|doc/ref|debian/|doc/locale|salt/([^/]+/)?__init__.py|tests/(pytests/)?(unit|functional|integration)/conftest.py)'
```

The main objective of this step is to find all relevant files (modules, utils, automated tests, fixtures, documentation). For the `stalekey` engine, they are:

* `salt/engines/stalekey.py` - the engine itself
* `tests/unit/engines/test_stalekey.py` - old style unit tests (historic path, no longer exists in HEAD)
* `tests/pytests/unit/engines/test_stalekey.py` - new-style unit tests using pytest

(filter-branch-target)=
### 3. Filter the history into a separate branch

```shell
git checkout -b filter-source
git filter-repo \
    --path salt/engines/stalekey.py \
    --path-rename salt/engines/stalekey.py:src/saltext/stalekey/engines/stalekey.py \
    --path tests/pytests/unit/engines/test_stalekey.py \
    --path-rename tests/pytests/unit/engines/test_stalekey.py:tests/unit/engines/test_stalekey.py \
    --path tests/unit/engines/test_stalekey.py \
    --refs refs/heads/filter-source --force
```

The `--path-rename` option moves the files into the directory structure used by Salt extensions.

(clean-history-target)=
### 4. Clean up the history

```shell
git log --name-only
git rebase -i --empty=drop --root --committer-date-is-author-date
```

The purpose of this step is to drop commits that don’t touch the extracted files plus the last commit that removes them. Merge commits are deleted automatically during the rebase.

While reviewing the Git log, please note the major contributors (in order to add them as code authors later).

(populate-repo-target)=
### 5. Populate the extension repo

Answer the Copier questions, choosing the `engine` module type only, and specify yourself as the author:

```shell
cd ..
mkdir saltext-stalekey && cd saltext-stalekey
git init --initial-branch=main
copier copy --trust https://github.com/salt-extensions/salt-extension-copier ./
```

Remove unwanted boilerplate files:

```shell
rm -f tests/**/test_*.py src/**/*_mod.py
```

Merge the history:

```shell
git remote add repo-source ../salt
git fetch repo-source
git merge repo-source/filter-source
git remote rm repo-source
git tag | xargs git tag -d
```

(migration-venv-target)=
### 6. Create a virtualenv and activate it

:::{important}
Creating a virtualenv is usually not necessary anymore since Copier takes care of it now. You still need to ensure you're inside the virtual environment from here on.
:::

To create the virtualenv, it is recommended to use the same Python version (MAJOR.MINOR) as the one [listed here](https://github.com/saltstack/salt/blob/master/cicd/shared-gh-workflows-context.yml).

```shell
python3.10 -m venv .venv --prompt saltext-stalekey
source venv/bin/activate
```

Please ensure you're inside your virtual environment from here on.

(migration-clean-up-target)=
### 7. Clean up and test

Run the automatic fixups:

```shell
pip install git+https://github.com/saltstack/salt-rewrite
SALTEXT_NAME=stalekey salt-rewrite -F fix_saltext .
```

:::{important}
You may need to re-rewrite some imports, as `salt-rewrite` assumes the project is named `saltext.saltext_stalekey` rather than `saltext.stalekey`.
:::

```shell
pip install -e ".[dev,tests,docs]"
pre-commit install --install-hooks
pre-commit run -a  # ensure it is happy
git status
git add .
git commit -m 'Add extension layout'
```

Add the main authors to {path}`pyproject.toml`:

```shell
vi pyproject.toml
git add pyproject.toml
git commit -m 'Add authors'
```

Try [running the test suite](run-tests-target) and [building the docs](build-docs-target) locally until both pass, then commit and push it to run the full test suite on GitHub.

## Basic fixes (automated)
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

### Migrated tests in `tests/pytest`

The generated Salt extension project does not account for a `tests/pytests` subdirectory. Its contents need to be moved to the top-level `tests` directory.

## Issues needing manual fixing
(utils-dunder-into-saltext-utils)=
### `__utils__` into Salt extension utils

Some Salt core modules access their utilities via the `__utils__` dunder instead of direct imports,
which ensures that the called utility function has access to Salt's global dunders.

Accessing a Salt extension's `utils` this way does not work. If this is the case for your extracted set of modules,
you need to adjust the `utils` to not rely on the dunders, e.g. by passing in the required
references:

:::{tab} old

```{code-block} python
:caption: salt/modules/foo.py

def get(entity):
    return __utils__["foo.query"](entity)
```

```{code-block} python
:caption: salt/utils/foo.py

def query(entity):
    base_url = __opts__.get("foo_base_url", "https://foo.bar")
    profile = __salt__["config.option"]("foo_profile")
    return __utils__["http.query"](base_url, data=profile)
```
:::

:::{tab} correct
```{code-block} python
:caption: saltext/foo/modules/foo.py

from saltext.foo.utils import foo


def get(entity):
    base_url = __opts__.get("foo_base_url", "https://foo.bar")
    return foo.query(base_url, entity, __salt__["config.option"])
```
```{code-block} python
:caption: saltext/foo/utils/foo.py

import salt.utils.http


def query(base_url, entity, config_option):
    profile = config_option("foo_profile")
    return salt.utils.http.query(base_url, data=profile)
```
:::

(utils-dunder-from-saltext-utils)=
### `__utils__` from Salt extension utils
Some modules in `salt.utils` still expect to be accessed via `__utils__`. While this works for modules loaded through the Salt loader (e.g., those using any {question}`loaders`), it fails if your Salt extension’s utils are calling these modules directly.

Here are some options to address this:

* Remove the dependency on the core module or call it from the modules calling the utils directly
* Migrate the dependency into your Salt extension repository and modify it locally as described [here](utils-dunder-into-saltext-utils)
* Submit a PR to Salt core with the necessary changes to eliminate the code duplication in the long term.

(utils-dunder-into-salt-utils)=
### `__utils__` from other Salt extension modules
If any other Saltext module relies on a Salt core utility that requires being called via `__utils__`, it will still work. However, you should consider creating a PR to remove this dependency, as [`__utils__` is scheduled for deprecation](https://github.com/saltstack/salt/issues/62191).

(pre-pytest-tests)=
### Pre-pytest tests

Salt core contains both Pytest-based and legacy tests, but Salt extension projects only support `pytest`. To keep legacy tests running, you may need to convert them. If you prefer to skip this task for now, you can:

- Exclude the corresponding files from `pylint`
- Skip the legacy tests entirely

```python
# pylint: disable-all
import pytest

pytest.skip(reason="Old non-pytest tests", allow_module_level=True)
```

## Considerations

(library-dependencies)=
### Library dependencies

Some modules have library dependencies. Since Salt core cannot include every possible dependency, these modules often include a safeguard to handle missing libraries or library alternatives. They typically use the following pattern:

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

If all the dependencies are hard dependencies, declare them in the `dependencies` section of your Saltext's {path}`pyproject.toml` and remove the conditional import logic:

```python
import foo

__virtualname__ = "foobar"


def __virtual__():
    return __virtualname__
```

For modules that can work with multiple interchangeable libraries, declare at least one of them in the `optional-dependencies` section for `tests` in your {path}`pyproject.toml` to ensure the tests can run.

(dedicated-docs)=
### Dedicated docs

Salt core modules often include inline documentation. Consider extracting the general parts of this inline documentation into separate topics within the {path}`docs/topics` directory.
