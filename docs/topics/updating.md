(update-target)=
# Updating your Saltext

Copier allows you to keep your Salt extension repository up to date with the latest best practices. Updating fetches the latest template release, uses your saved answers as defaults, and applies your customizations.

## Manual update

Manual updates let you:

* Update answers to existing questions
* Provide answers to new questions
* Resolve merge conflicts when customized files change in the template

### Workflow

1. Ensure you are in your project's root directory and run:
    ```bash
    git switch main && git switch -c copier-update
    copier update --trust
    ```
2. Review your previous answers and provide answers to any new questions.
3. Check for and resolve any merge conflicts:
    ```bash
    git status
    ```
4. Remove any unwanted regenerated boilerplate files (a subset of `ls src/**/*_mod.py tests/**/test_*.py`).[^skip-if-exists-issue]
5. Review, then stage the changes:
    ```bash
    git status
    git diff
    git add .
    ```
6. Run `pre-commit` on the entire repository and ensure it passes:
    ```bash
    pre-commit run -a
    ```
7. Commit and submit the update via a PR:
   ```bash
   git add . && git commit -m "Update to Copier template 0.3.7" && git push
   ```

[^skip-if-exists-issue]: Currently, there is an issue where default boilerplate files are regenerated if they were deleted. This will be fixed soon, but depends on a new Copier release.

#### Skip reviewing answers

To skip reviewing existing answers:

```bash
copier update --trust --skip-answered
```

#### Always use default answers

To skip new questions and use defaults:

```bash
copier update --trust --skip-answered --defaults
```

:::{hint}
This command is non-interactive.
:::

(vcs-ref-target)=
#### Update to a specific version

To update to a specific template version:

```bash
copier update --trust --skip-answered --vcs-ref=0.3.7
```

## Automatic update

[RenovateBot](https://docs.renovatebot.com/) supports updating Copier templates. If your repository is hosted within the `salt-extensions` GitHub organization, automated PRs for template updates will be provided in the future. Review these carefully before merging.

:::{important}
This feature is not yet implemented due to an outstanding issue in Copier.
:::
