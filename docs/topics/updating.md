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
4. Review, then stage the changes:
    ```bash
    git status
    git diff
    git add .
    ```
5. Run `pre-commit` on the entire repository and ensure it passes:
    ```bash
    pre-commit run -a
    ```
6. Commit and submit the update via a PR:
   ```bash
   git add . && git commit -m "Update to Copier template 0.4.2" && git push
   ```

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
copier update --trust --skip-answered --vcs-ref=0.4.2
```

## Automatic update

[RenovateBot](https://docs.renovatebot.com/) supports updating Copier templates. If your repository is hosted within the  [`salt-extensions` organization](gh-org-ref), you will receive automated PRs for template updates. Review these carefully before merging and ensure CI is passing since Renovate will submit merge conflicts - it adds a PR comment warning about them though.

:::{hint}
When an update introduces a new Copier template question, the automated PR uses the default value. If you want to use a custom one, just perform a manual update.
:::
