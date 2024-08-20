# Updating your Saltext

Using Copier, you have the means to ensure your Salt extension's repository always follows the latest best practices. Updating fetches the latest template release, renders it using the saved answers as defaults and applies your customizations on top of it.

## Manual update

Manual updates allow you to

* update answers to existing questions
* provide custom answers to new questions
* resolve merge conflicts when a file you customized has changed in the template

### Workflow

1. Ensure you are in your project's root directory, then run:
    ```bash
    git switch main && git switch -c copier-update
    copier update --trust
    ```
2. You can review all your previous answers. If the update introduces new questions, you need to answer them now.
3. Check the repository status for merge conflicts and resolve them:
    ```bash
    git status
    ```
4. Currently, there is an issue where default boilerplate files are regenerated if they were deleted (a subset of `ls src/**/*_mod.py tests/**/test_*.py`). Remove the unwanted files again. This will be fixed soon, but depends on a new Copier release.
5. Once you have reviewed the proposed changes, stage them:
    ```bash
    git add .
    ```
6. Run pre-commit against the whole repository and ensure it is happy:
    ```bash
    pre-commit run -a
    ```
7. Once pre-commit passes, commit and submit the update in a PR:
   ```bash
   git add . && git commit -m "Update to Copier template 0.3.7" && git push
   ```

#### Skip reviewing answers

If you don't want to review existing answers, invoke Copier via:

```bash
copier update --trust --skip-answered
```

#### Always use defaults

If you don't want to answer new questions, you can request to always use the defaults by passing `--defaults`. The following command is thus non-interactive:

```bash
copier update --trust --skip-answered --defaults
```

#### Update to a specific version

You can request Copier to update to a specific template version by passing it as `vcs-ref`:

```bash
copier update --trust --skip-answered --vcs-ref=0.3.7
```

## Automatic update

[Renovate](https://docs.renovatebot.com/) supports updating Copier templates. If your repository is hosted inside the `salt-extensions` GitHub organization, you will receive automated pull requests with template updates in the future. Ensure you review them carefully before merging.

:::{important}
This is not yet implemented since there is an issue in Copier that needs to be addressed.
:::
