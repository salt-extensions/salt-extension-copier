# Project layout
This section provides an overview of the key paths in your Salt extension project.

:::{path} .copier-answers.yml
:::
## `.copier-answers.yml`
Stores Copier-specific data, including answers to [template questions](questions-target), the template's source URI, and the last version the project was updated to.

**Do not edit manually.** To change your answers, use `copier update --trust`. To avoid updating the template version, [pass the current version in `vcs-ref`](vcs-ref-target).

:::{path} .envrc.example
:::
## `.envrc.example`
Example {tool}`direnv` configuration. Copy to `.envrc` to automate [dev env setup](automatic-init-target) and venv activation on shell entry.

:::{path} .pre-commit-config.yaml
:::
## `.pre-commit-config.yaml`
Configures the project's {tool}`pre-commit` hooks: autoformatting, linting and docs generation.

:::{path} .pre-commit-hooks
:::
## `.pre-commit-hooks`
Project-local hook scripts, generating module docs and checking CLI examples.

:::{path} CHANGELOG.md
:::
## `CHANGELOG.md`
Contains the project’s changelog. Update this file using [towncrier](changelog-build-target) instead of manually.

:::{path} Makefile
:::
## `Makefile`
Convenience targets for common development tasks, e.g. `make dev` (create/synchronize the dev venv), `make tests`, `make docs`, `make changelog` and `make clean`.

:::{path} README.md
:::
## `README.md`
Provides a brief project overview and developer information. Includes a note about user documentation and, if {question}`docs_url` was set, a link to the hosted documentation.

:::{path} noxfile.py
:::
## `noxfile.py`
Defines {tool}`nox` sessions for [running tests](run-tests-target), [building documentation](build-docs-target), and linting code.

:::{path} pyproject.toml
:::
## `pyproject.toml`
Holds project metadata, package dependencies and configuration for tools used in the project's lifecycle.

:::{path} .github
:::
## `.github`
Contains GitHub-related configurations and workflows. This directory is only present if your {question}`source_url` is on GitHub.

:::{path} .github/workflows
:::
### `.github/workflows`
Houses GitHub Actions [workflows](workflows-target). Besides the entry points described below, it contains reusable `*-action.yml` building blocks they delegate to.

:::{path} .github/workflows/ci.yml
:::
#### `.github/workflows/ci.yml`
A meta-workflow that triggers other workflows related to testing and building.

:::{path} .github/workflows/clear-caches.yml
:::
#### `.github/workflows/clear-caches.yml`
Purges the repository's GitHub Actions caches, either all of them or a single key. Triggered via manual dispatch.

:::{path} .github/workflows/deploy-package-action.yml
:::
#### `.github/workflows/deploy-package-action.yml`
A minimal standalone workflow publishing the built packages to Test PyPI and PyPI. Triggered when the release pipeline in {path}`tag.yml <.github/workflows/tag.yml>` – or, {question}`without the autorelease app <require_autorelease_app>`, {path}`tag-auto.yml <.github/workflows/tag-auto.yml>` – has concluded. Needs to be entered as the workflow when configuring [Trusted Publishers](trusted-publisher-target). Subsequent release steps run in {path}`finalize-release-action.yml <.github/workflows/finalize-release-action.yml>`, outside the publishing trust boundary.

:::{path} .github/workflows/finalize-release-action.yml
:::
#### `.github/workflows/finalize-release-action.yml`
Finalizes a release after {path}`deploy-package-action.yml <.github/workflows/deploy-package-action.yml>` has published the packages: creates the GitHub release and deploys the documentation if configured. Kept separate to keep the Trusted Publisher workflow minimal.

:::{path} .github/workflows/pr.yml
:::
#### `.github/workflows/pr.yml`
Handles Pull Requests. Delegates to workflows in {path}`ci.yml <.github/workflows/ci.yml>`.

:::{path} .github/workflows/prepare-release-action.yml
:::
#### `.github/workflows/prepare-release-action.yml`
Creates/updates the [autorelease PR](release-automated-target). Called by {path}`push.yml <.github/workflows/push.yml>`, can also be dispatched manually (`Prepare Release PR`) to force a custom version or refresh the PR.

:::{path} .github/workflows/push.yml
:::
#### `.github/workflows/push.yml`
Handles pushes to the `main` branch. Includes workflows from {path}`ci.yml <.github/workflows/ci.yml>`, creates the [autorelease PR](release-automated-target) and can publish documentation.

:::{path} .github/workflows/tag-auto.yml
:::
#### `.github/workflows/tag-auto.yml`
Triggered by merging the [autorelease PR](release-automated-target). Validates the release and pushes the version tag. With the [autorelease app](optional-secrets-target) configured, the tag is pushed using the app's token, handing the release off to {path}`tag.yml <.github/workflows/tag.yml>`. Otherwise, this workflow runs the release pipeline itself as an alternative entry point.

:::{path} .github/workflows/tag.yml
:::
#### `.github/workflows/tag.yml`
Triggered by [tag pushes](publishing-target) for tags beginning with `v`, including those pushed by {path}`tag-auto.yml <.github/workflows/tag-auto.yml>` with the autorelease app's token. Includes workflows from {path}`ci.yml <.github/workflows/ci.yml>`. {path}`Separate workflows <.github/workflows/deploy-package-action.yml>` publish the built packages and finalize the release.

:::{path} changelog
:::
## `changelog`
Directory containing [news fragments](news-fragment-target) for {tool}`towncrier`. Also includes the default version-specific changelog template in `changelog/.template.jinja`.

:::{path} docs
:::
## `docs`
Root directory for documentation-related files.

:::{path} docs/conf.py
:::
### `docs/conf.py`
Contains Sphinx configuration and plugins.

:::{path} docs/index.rst
:::
### `docs/index.rst`
Homepage for the documentation, (indirectly) linking to all other documentation files.

:::{hint}
If your project includes a `utils` directory, manually add the corresponding documentation here (not handled by the Copier template or the pre-commit hook).
:::

:::{path} docs/ref
:::
### `docs/ref`
Directory containing autogenerated module documentation. Typically does not require manual updates, but can be used for custom documents, like a configuration reference.

:::{path} docs/topics
:::
### `docs/topics`
Intended to hold high-level guides related to your Salt extension, such as `Configuration`. By default, includes an `Installation` guide.

:::{path} src
:::
## `src`
Root directory for your Salt extension's package.

:::{path} utils/_types.py
:::
### `src/<package>/utils/_types.py`
Static typing helpers, only generated when {question}`typing` is enabled: type aliases for common Salt objects and typed loader dunders for importing inside `typing.TYPE_CHECKING` blocks.

:::{path} tests
:::
## `tests`
Root directory for Pytest-based test modules.

:::{path} tests/conftest.py
:::
### `tests/conftest.py`
Provides default fixtures and basic test setup.

:::{path} tests/functional
:::
### `tests/functional`
Contains functional tests.

:::{path} tests/functional/conftest.py
:::
#### `tests/functional/conftest.py`
Provides default fixtures for functional tests.

:::{path} tests/integration
:::
### `tests/integration`
Contains integration tests.

:::{path} tests/integration/conftest.py
:::
#### `tests/integration/conftest.py`
Provides default fixtures for integration tests.

:::{path} tests/unit
:::
### `tests/unit`
Contains unit tests.

:::{path} tests/unit/conftest.py
:::
#### `tests/unit/conftest.py`
Provides default fixtures for unit tests.

:::{path} tools
:::
## `tools`
Development automation scripts.

:::{path} tools/initialize.py
:::
### `tools/initialize.py`
Creates/synchronizes the development environment ([first steps](first-steps-target)). Invoked via `make dev`, `.envrc` or directly.

:::{path} tools/version.py
:::
### `tools/version.py`
Infers the project version from the changelog and pending news fragments. Used by the release workflows.
