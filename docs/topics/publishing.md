(publishing-target)=
# Publishing your Saltext

:::{important}
This guide assumes your repository is hosted on GitHub.

There are currently no included workflows for other Git hosting providers or CI systems.
:::

Once your Salt extension is ready, you can submit it to PyPI.

## 0: Prerequisites

* Your project is hosted on GitHub.
* It is either in the `salt-extensions` organization or you have set up the [required secrets](required-secrets-target).
* You have commit rights to the repository.
* You have added a git remote `upstream` to your local repository, pointing to the official repository via **SSH**.
* You have followed the [first steps](first-steps-target) to setup your repository and virtual environment.
* You have activated your virtual environment.

Ensure your `main` branch is up to date:

```bash
git switch main && git fetch upstream && git rebase upstream/main
```

(changelog-build-target)=
## 1: Build the changelog

Create and switch to a new branch:

```bash
git switch -c release/100
```

You have been [keeping a changelog](documenting/changelog) with `towncrier`, now is the time to compile it.

```bash
towncrier build --yes --version v1.0.0
```

This command combines all news fragments into {path}`CHANGELOG.md` and clears them. Commit the change.

## 2: Submit the changelog

Submit this commit as a PR and merge it into the default branch on `upstream`.

:::{tip}
Squash-merging this PR results in a cleaner tag target.
:::

## 3: Tag a release

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

## 4: Push the tag

Push the new tag upstream to trigger the publishing workflow:

```bash
git push upstream v1.0.0
```

## 5: Check the result

If CI passes, a new release should be available on both PyPI and your GitHub repository.
