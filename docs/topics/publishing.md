(publishing-target)=
# Publishing your Saltext

:::{important}
This guide assumes your repository is hosted on GitHub.

There are currently no included workflows for other Git hosting providers or CI systems.
:::

Once your Salt extension is ready, you can submit it to PyPI.

Ensure you meet the following prerequisites:

* Your project is hosted on GitHub.
* It is either in the `salt-extensions` organization or you have set up the [required secrets](required-secrets-target) and [permissions](actions-pr-permission-target).
* You have commit rights to the repository.

(release-automated-target)=
## Automated
Generated projects include a workflow that automatically detects the next version bump based on [news fragments](changelog-target) in {path}`changelog`, builds the changelog and submits a PR with these changes. Once you are ready to release a new version, simply merge this PR, which creates a new git tag and triggers the release workflow.

:::{important}
Before merging, ensure the PR is based on the current default branch HEAD.
:::

:::{hint}
To force a custom version or manually trigger an update to the release PR (e.g. to adjust the release date), go to `Actions` > `Prepare Release PR` > `Run workflow`.
:::

:::{note}
The generated PR is only created automatically if there is at least one news fragment to render. You can still trigger a manual run as described above.
:::

(release-manual-target)=
## Manual
### 0: Prerequisites

* You have added a git remote `upstream` to your local repository, pointing to the official repository via **SSH**.
* You have executed the [first steps](first-steps-target) to setup your repository and virtual environment in some way.
* You have activated your virtual environment.

Ensure your `main` branch is up to date:

```bash
git switch main && git fetch upstream && git rebase upstream/main
```

(changelog-build-target)=
### 1: Build the changelog

Create and switch to a new branch:

```bash
git switch -c release/100
```

You have been [keeping a changelog](documenting/changelog) with `towncrier`, now is the time to compile it.

```bash
towncrier build --yes --version v1.0.0
```

This command combines all news fragments into {path}`CHANGELOG.md` and clears them. Commit the change.

### 2: Submit the changelog

Submit this commit as a PR and merge it into the default branch on `upstream`.

:::{tip}
Squash-merging this PR results in a cleaner tag target.
:::

### 3: Tag a release

Ensure your `main` branch is up to date (again):

```bash
git switch main && git fetch upstream && git rebase upstream/main
```

Create a new tag named after the version:

```bash
git tag v1.0.0
```

:::{important}
The tag must start with `v` for the default publishing workflows to work correctly.
:::

### 4: Push the tag

Push the new tag upstream to trigger the publishing workflow:

```bash
git push upstream v1.0.0
```

### 5: Check the result

If CI passes, a new release should be available on both PyPI and your GitHub repository.
