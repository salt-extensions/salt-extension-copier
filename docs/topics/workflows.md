(workflows-target)=
# Workflows

Your Salt extension repository includes several workflows out of the box if your {question}`source_url` is on GitHub.

## Provided functions

The workflows currently:

* Ensure the pre-commit hooks pass (run via {tool}`prek`)
* Run the test suite and upload code coverage reports
* Build the documentation
* Build the changelog and submit a PR that triggers a release when merged
* Optionally deploy built documentation to GitHub Pages
* Optionally build and release your project to PyPI
* Cache dependencies between runs (except during releases, which never use caches), purgeable via the {path}`Clear Actions Caches <.github/workflows/clear-caches.yml>` workflow

## Repository setup

### Required settings (all)
#### GitHub Pages
If publishing documentation to GitHub Pages, ensure you have
[set up your repository to allow deployments from GitHub Actions](docs-publish-setup-target).

(actions-release-environment-target)=
#### Release environment

The {path}`package release workflow <.github/workflows/deploy-package-action.yml>` requires a dedicated
environment for package releases to PyPI.

In your repository settings, click on `Environments` > `New environment`, enter `release`
as its name and click `Configure environment`. Under `Deployment branches and tags`,
select `Selected branches and tags`, click `Add deployment branch or tag rule`, select
`Ref type: Branch`, enter `main` and click `Add rule`.

You can configure other restrictions as desired.

(actions-pr-permission-target)=
#### Release automation
Also, ensure GitHub Actions are allowed to create PRs to take advantage of
the release automation. In the organization, this should be enabled by default.

In your repository settings, click on `Actions` > `General`, scroll down
and ensure `Allow GitHub Actions to create and approve pull requests` is checked.

(required-secrets-target)=
### Required secrets (non-org)
If your repository is not hosted within the `salt-extensions` organization, you need
to ensure the project can be published to PyPI. You can either setup legacy API tokens
or configure a [Trusted Publishers](trusted-publisher-target) on PyPI.

(trusted-publisher-target)=
#### Trusted Publisher
To configure a Trusted Publisher, head over to PyPI and login. Click on your user name
in the top right corner, then `Your projects`. In the left menu, select `Publishing`.
Scroll down until you see `Add a new pending publisher`. Select `GitHub` (should be selected by default).
Specify a PyPI project name, the name of the GitHub organization/user account that owns the repository
and the repository name. As `Workflow name`, fill in `deploy-package-action.yml`.
It is recommended to also fill in `release` as the `Environment name`, which ensures publish
tokens are only valid when minted from the protected [release environment](actions-release-environment-target).

Repeat the above steps for `test.pypi.org`, but leave the `Environment name` empty there
since the Test PyPI publishing job does not run in an environment.

#### Legacy API token
Alternatively, you can add the following secrets:

`PYPI_API_TOKEN`
:   An [API token for PyPI](https://pypi.org/help/#apitoken) for [releasing your Saltext](publishing-target).

`TEST_PYPI_API_TOKEN`
:   An [API token for TestPyPI](https://test.pypi.org/help/#apitoken) for testing the [release of your Saltext](publishing-target).

(optional-secrets-target)=
### GitHub App secrets (non-org)
#### Release automation
The release workflows use a dedicated GitHub App:

* CI runs on the autorelease PR. PRs created with the default `GITHUB_TOKEN` do not trigger workflows.
* When the autorelease PR is merged, the release tag is pushed with the app's token,
  meaning all releases are handled uniformly by the tag push workflow.

When {question}`require_autorelease_app` is true (the default for repositories inside
the `salt-extensions` organization, where the app is configured organization-wide),
the workflows require the app and fail without it.
Otherwise, they additionally support falling back to the default `GITHUB_TOKEN`,
at the cost of a more complex release pipeline and no CI runs on the autorelease PR.

To set up an app, follow the steps described [here](https://github.com/peter-evans/create-pull-request#user-content-token) and add the following two secrets:
The app's client ID as `AUTORELEASE_CLID` and the generated private key as `AUTORELEASE_PRIV`.
The app needs read and write permissions for the repository's `Contents` and `Pull requests`.

## Important artifacts

After a workflow run, several artifacts are available for download
on the action summary page (scroll down).

### `runtests-*.log`
Contains logs generated during a specific test run, useful for debugging test failures.

### `html-docs`
The built HTML documentation, also available for preview when triggered by a Pull Request.


[trusted-publishing-issue]: https://github.com/pypi/warehouse/issues/11096
[attestations]: https://docs.pypi.org/attestations/producing-attestations/
[trusted-publishers]: https://docs.pypi.org/trusted-publishers/
