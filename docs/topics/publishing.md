(publishing-target)=
# Publishing your Saltext

:::{important}
This guide assumes your repository is hosted on GitHub.

There are currently no included workflows for other Git hosting providers or CI systems.
:::

Having done all this work, now it's time to submit your Salt extension to PyPI.

## 0: Prerequisites

* Your project repository is hosted on GitHub.
* Either it is hosted in the `salt-extensions` organization or you have set up all [required secrets](required-secrets-target) for the workflows.
* You have commit rights for the hosted project repository.
* You have added a git remote `upstream` to your local repository, pointing to the official repository of the Saltext via **SSH**.

Ensure your `main` branch is up to date:

```bash
git switch main && git fetch upstream && git rebase upstream/main
```

(changelog-build-target)=
## 1: Building the changelog
First, create and switch to a new branch:

```bash
git switch -c release/100
```

You have [kept a changelog](documenting/changelog), so you certainly want to ensure it's committed before releasing.

If you followed the [first steps](first-steps-target), you should have `towncrier` installed in your project's virtual environment:

```bash
towncrier build --yes --version v1.0.0
```

This command combines all news fragments into a new entry in your `CHANGELOG.md` file and clears them. Commit this change.

## 2: Submitting the changelog

This commit should be submitted as a PR and be merged into the default branch on `upstream`.

:::{tip}
Squash-merging this PR makes the tag target a bit nicer.
:::

## 3: Tagging a release

Ensure your `main` branch is up to date again...

```bash
git switch main && git fetch upstream && git rebase upstream/main
```

and create a new tag named after the version:

```bash
git tag v1.0.0
```

:::{important}
Note that the tag begins with a `v`. This is required for the default publishing workflows to work as expected.
:::

## 4: Pushing the tag

To trigger the publication workflow, push the new tag directly upstream:

```bash
git push upstream v1.0.0
```

## 5: Check result

If CI passes, a new release should now be available on PyPI as well as on your GitHub repository.
