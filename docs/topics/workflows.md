(workflows-target)=
# Workflows

Your Salt extension repository includes several workflows out of the box if your {question}`source_url` is on GitHub.

## Provided functions

The workflows currently:

* Ensure `pre-commit` checks pass
* Run the test suite and upload code coverage reports
* Build the documentation
* Build the changelog and submit a PR that triggers a release when merged
* Optionally deploy built documentation to GitHub Pages
* Optionally build and release your project to PyPI

## Repository setup

### Required settings (all)
If publishing documentation to GitHub Pages, ensure you have
[set up your repository to allow deployments from GitHub Actions](docs-publish-setup-target).

(required-secrets-target)=
### Required secrets (non-org)
If your repository is not hosted within the `salt-extensions` organization, you need to add the following secrets:

`PYPI_API_TOKEN`
:   An [API token for PyPI](https://pypi.org/help/#apitoken) for [releasing your Saltext](publishing-target).

`TEST_PYPI_API_TOKEN`
:   An [API token for TestPyPI](https://test.pypi.org/help/#apitoken) for testing the [release of your Saltext](publishing-target).

:::{important}
Workflows are expected to migrate to [Trusted Publishing](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) soon, making these secrets obsolete.
:::

## Important artifacts

After a workflow run, several artifacts are available for download
on the action summary page (scroll down).

### `runtests-*.log`
Contains logs generated during a specific test run, useful for debugging test failures.

### `html-docs`
The built HTML documentation, also available for preview when triggered by a Pull Request.

## Workflows call stack
1. {path}`.github/workflows/pr.yml` or {path}`.github/workflows/tag.yml` is triggered
2. {path}`.github/workflows/ci.yml` is called as the main entry point to CI
3. Depending on the event and inputs, select additional workflows perform the necessary tasks.
