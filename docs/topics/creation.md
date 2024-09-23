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
Before hacking away on your new Salt extension, you need to initialize a Git repository and set up a development environment.

Contributors to existing Salt extension projects need to do the latter after cloning.

(automatic-init-target)=
### Automatic
This process is automated completely in the following cases:

* For maintainers: When creating/updating a project via Copier, unless `SKIP_INIT_MIGRATE=1` was set in the environment ([repo initialization](repo-init-target) + [dev env setup](dev-setup-target) + [pre-commit hook installation](hook-install-target) + running pre-commit).
* For all developers: When `direnv` is installed and the project's `.envrc` is allowed to run ([dev env setup](dev-setup-target) + [pre-commit hook installation](hook-install-target)).

:::{important}
The automation either requires [`uv`](https://github.com/astral-sh/uv) or the Python version (MAJOR.MINOR) [listed here](https://github.com/saltstack/salt/blob/master/cicd/shared-gh-workflows-context.yml) to be available on your system, at the time of writing Python 3.10.
:::

:::{hint}
Without `direnv`, you can still call the automation script manually after entering the project root directory:

```bash
python3 tools/initialize.py
source .venv/bin/activate
```
:::

### Manual
(repo-init-target)=
### Initialize the repository
```bash
git init -b main
```

:::{important}
Some automations assume your default branch is `main`. Ensure this is the case.
:::

(dev-setup-target)=
### Initialize the Python virtual environment
:::{important}
To create the virtualenv, it is recommended to use the same Python version (MAJOR.MINOR) as the one [listed here](https://github.com/saltstack/salt/blob/master/cicd/shared-gh-workflows-context.yml), at the time of writing Python 3.10.
:::

```bash
python3.10 -m venv .venv
source venv/bin/activate
python -m pip install -e '.[tests,dev,docs]'
```

This creates a virtual environment and installs relevant dependencies, including `nox` and `pre-commit`.

(hook-install-target)=
### Install the `pre-commit` hook
```bash
python -m pre_commit install --install-hooks
```

This ensures `pre-commit` runs before each commit. It autoformats and lints your code and ensures the presence of necessary documentation files. To skip these checks temporarily, use `git commit --no-verify`.

## First commit
```bash
git add .
git commit -m "Initial extension layout"
```

In case `pre-commit` modifies or creates files, the commit is aborted. Stage the changes and try again.

[jinja-exts]: https://github.com/salt-extensions/salt-extension-copier/blob/main/jinja_extensions/saltext.py
[tasks-migrations]: https://github.com/salt-extensions/salt-extension-copier/blob/main/copier.yml
