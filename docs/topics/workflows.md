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
If your repository is not hosted within the `salt-extensions` organization, you need
to ensure the project can be published to PyPI. You can either setup legacy API tokens
or configure a [Trusted Publisher][trusted-publishers] on PyPI.

#### Trusted Publisher
To configure a Trusted Publisher, head over to PyPI and login. Click on your user name
in the top right corner, then `Your projects`. In the left menu, select `Publishing`.
Scroll down until you see `Add a new pending publisher`. Select `GitHub` (should be selected by default).
Specify a PyPI project name, the name of the GitHub organization/user account that owns the repository
and the repository name. As `Workflow name`, fill in `deploy-package-action.yml`.

Repeat the above steps for `test.pypi.org`.

:::{note}
Reusable workflows, as employed in generated projects, are [not fully supported][trusted-publishing-issue]
as a Trusted Publisher at the moment. Specifically, [attestations] cannot be uploaded.
:::

#### Legacy API token
Alternatively, you can add the following secrets:

`PYPI_API_TOKEN`
:   An [API token for PyPI](https://pypi.org/help/#apitoken) for [releasing your Saltext](publishing-target).

`TEST_PYPI_API_TOKEN`
:   An [API token for TestPyPI](https://test.pypi.org/help/#apitoken) for testing the [release of your Saltext](publishing-target).

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


[trusted-publishing-issue]: https://github.com/pypi/warehouse/issues/11096
[attestations]: https://docs.pypi.org/attestations/producing-attestations/
[trusted-publishers]: https://docs.pypi.org/trusted-publishers/
