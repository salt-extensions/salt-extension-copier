# Workflows

Your Salt extension repository comes with several workflows out of the box
(if {question}`source_url` is on GitHub).

:::{note}
The workflows used inside the `salt-extensions` organization (`org`) are equivalent
to the `enhanced` ones.
:::

## Repository setup
### Required settings (all)
When publishing documentation to GitHub Pages, ensure you have
[set up your repository to allow deployments from GitHub Actions](docs-publish-setup-target).

(required-secrets-target)=
### Required secrets (non-org)
If you don't host your repository inside the `salt-extensions` organization,
you need to add some required secrets.

`PYPI_API_TOKEN`
:   An [API token for PyPI](https://pypi.org/help/#apitoken) to use when [releasing your Saltext](publishing-target).

`TEST_PYPI_API_TOKEN`
:   An [API token for TestPyPI](https://test.pypi.org/help/#apitoken) to use when [releasing your Saltext](publishing-target).

:::{important}
In the near future, the workflows are scheduled to migrate to [Trusted Publishing](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/).

These secrets will become obsolete at that point.
:::

## Important artifacts
After a workflow run has finished, several artifacts will be available for download.
You can find them on the action summary page by scrolling down.

### `runtests-*.log`
Contains all log artifacts generated during a specific test run.
Useful when debugging failing tests in CI.

### `html-docs`
The built HTML docs. They are also available when triggered by a Pull Request,
hence this is handy for previewing proposed documentation updates.

## Workflows call stack
1. {path}`.github/workflows/pr.yml` or {path}`.github/workflows/tag.yml` is triggered
2. {path}`.github/workflows/ci.yml` (or its equivalent centralized workflow) is called as the singular entry point to CI
3. Depending on the event and inputs, several workflows doing the actual jobs are called.
