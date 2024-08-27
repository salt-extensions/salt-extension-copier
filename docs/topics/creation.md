(creation-target)=
# Creation

With Copier, creating a Salt extension project is easy:

```bash
copier copy --trust https://github.com/salt-extensions/salt-extension-copier my-awesome-new-saltext
```

You are then prompted with questions to configure your project structure. These answers are saved in {path}`.copier-answers.yml` for future [updates](update-target).

:::{important}

Copier needs to be invoked with the `--trust` flag in order to enable
custom Jinja extensions (always) and migrations (during updates).
This effectively runs unsandboxed commands on your host,
so ensure you trust the template source!

* [Jinja extensions][jinja-exts]
* [tasks and migrations][tasks-migrations]
:::

## Important considerations

### Organization vs single
Decide early whether to [submit your project](submitting-target) to the [`salt-extensions` GitHub organization](gh-org-ref) or host it in your [own repository](required-secrets-target). This is determined by the `source_url` you provide.

### GitHub vs other Git host (non-org)
If hosting the repository outside the organization, you can choose your provider freely. Note that the [default workflows](workflows-target) only work on GitHub though.

(first-steps-target)=
## First steps

To finalize your project setup, ensure you initialize the Git repository and Python virtual environment and install and run the `pre-commit` hooks.

### Initialize the repository
```bash
git init -b main
```

:::{important}
Some automations assume your default branch is `main`. Ensure this is the case.
:::

(dev-setup-target)=
### Initialize the Python virtual environment
```bash
python -m venv venv
source venv/bin/activate
python -m pip install -e '.[tests,dev,docs]'
```

This creates a virtual environment and installs relevant dependencies, including `nox` and `pre-commit`.

### Install the `pre-commit` hook
```bash
python -m pre_commit install --install-hooks
```

This ensures `pre-commit` runs before each commit. It autoformats and lints your code and ensures the presence of necessary documentation files. To skip these checks temporarily, use `git commit --no-verify`.

### First commit
```bash
git add .
git commit -m "Initial extension layout"
```

In case `pre-commit` modifies or creates files, the commit is aborted. Stage the changes and try again.

[jinja-exts]: https://github.com/salt-extensions/salt-extension-copier/blob/main/jinja_extensions/saltext.py
[tasks-migrations]: https://github.com/salt-extensions/salt-extension-copier/blob/main/copier.yml
