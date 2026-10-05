(creation-target)=
# Creation

:::{note}
If you are migrating existing modules out of Salt core, follow the [extraction guide](extraction-target) instead. The automation takes care of project creation.
:::

With Copier, creating a Salt extension project is easy:

```bash
copier copy --trust https://github.com/salt-extensions/salt-extension-copier my-awesome-new-saltext
```

You are then prompted with questions to configure your project structure. These answers are saved in {path}`.copier-answers.yml` for future [updates](update-target).

:::{important}

Copier needs to be invoked with the [`--trust` flag][trust-flag] in order to enable
custom Jinja extensions (always) and migrations (during updates).
This effectively runs unsandboxed commands on your host,
so ensure you trust the template source!

* [Jinja extensions][jinja-exts]
* [tasks and migrations][tasks-migrations]
:::

## Important considerations

### Organization vs single
Decide early whether to [submit your project](submitting-target) to the [`salt-extensions` GitHub organization](gh-org-ref) or host it in your [own repository](required-secrets-target). This is determined by the {question}`source_url` you provide.

### GitHub vs other Git host (non-org)
If hosting the repository outside the organization, you can choose your provider freely. Note that the [default workflows](workflows-target) only work on GitHub though.

(first-steps-target)=
## First steps
Before hacking away on your new Salt extension, you need to initialize a Git repository and set up a development environment.

Contributors to existing Salt extension projects need to do the latter after cloning.

(automatic-init-target)=
### Automatic
:::{versionadded} 0.4.0
:::

This process is automated completely in the following cases:

* For maintainers: When creating/updating a project via Copier, unless {envvar}`SKIP_INIT_MIGRATE=1 <SKIP_INIT_MIGRATE>` was set in the environment ([repo initialization](repo-init-target) + [dev env setup](dev-setup-target) + [pre-commit hook installation](hook-install-target) + running pre-commit).
* For all developers: If you have a working {tool}`direnv` installation, you can copy the included {path}`.envrc.example` to `.envrc` and allow it to run. This takes care of the [dev env setup](dev-setup-target) and [pre-commit hook installation](hook-install-target) as well as activating the virtual environment. To keep shell entry fast, the example passes `--skip-install`, meaning the project is only installed when the virtual environment is freshly created — run `make dev` to synchronize it after dependency changes. Without `direnv`, you can also run `make dev` (see the included {path}`Makefile` for all targets) to create/update the development environment. Remember to activate it via `source .venv/bin/activate` afterwards.

:::{important}
The automation either requires {tool}`uv`, which provisions the requested Python version automatically, or the Python version chosen in {question}`venv_python` to be available on your system.
:::

:::{hint}
Without {tool}`direnv` or {tool}`make`, you can still call the {path}`automation script <tools/initialize.py>` manually after entering the project root directory:

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
To create the virtualenv, use the Python version you chose in {question}`venv_python`. Its default follows the latest supported Salt onedir release ([listed here](https://github.com/saltstack/salt/blob/master/cicd/shared-gh-workflows-context.yml)). The example below assumes 3.14, substitute your answer.
:::

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[tests,dev,docs]'
```

This creates a virtual environment and installs relevant dependencies, including {tool}`nox` and {tool}`prek` (or {tool}`pre-commit` on platforms without prebuilt `prek` binaries).

(system-site-packages-target)=
### Inheriting system-wide packages
Some extensions, especially OS-specific ones, depend on packages that are only available system-wide (e.g. installed via FreeBSD ports). In this case, set {envvar}`VENV_SYSTEM_SITE_PACKAGES=1 <VENV_SYSTEM_SITE_PACKAGES>` in your environment (e.g. via `.envrc` or your shell profile). Both the development virtual environment and the [`nox` session venvs](run-tests-target) are then created with `--system-site-packages`, based on your system Python, and requirements that are already satisfied system-wide (such as a system-packaged Salt) are not reinstalled.

Since {tool}`uv` [does not consider inherited packages during installs](https://github.com/astral-sh/uv/issues/4466), the tooling automatically falls back to `venv` and `pip` in this mode.

:::{note}
When toggling this setting, the development virtual environment is recreated automatically on the next `make dev`, but existing `nox` session venvs are not. Remove them via `make clean` (or `rm -rf .nox`).
:::

(hook-install-target)=
### Install the `pre-commit` hook
```bash
prek install --install-hooks
```

If {tool}`prek` is unavailable on your platform, substitute `python -m pre_commit` for `prek`.

This ensures the hooks run before each commit. They autoformat and lint your code and ensure the presence of necessary documentation files, as configured in {path}`.pre-commit-config.yaml`. To skip these checks temporarily, use `git commit --no-verify`.

:::{note}
Some hooks may fail to install or run on certain platforms. For example, this can affect {tool}`actionlint` (which is compiled locally — the hook manager provisions the required [Go](https://go.dev/) toolchain automatically, but only on platforms with [official Go binaries](https://go.dev/dl/)) and {tool}`ty` (which relies on prebuilt binaries of both {tool}`uv` and itself and is only generated when {question}`typing` is enabled; on platforms without `uv` wheels, the hook falls back to a locally installed `uv`, e.g. from your system package manager). In this case, skip the affected hooks persistently by setting [`SKIP`](https://pre-commit.com/#temporarily-disabling-hooks) in your environment (e.g. via `.envrc` or your shell profile):

```bash
export SKIP=actionlint,ty
```

Skipped hooks are neither run nor installed during commits. Note that the `--install-hooks` flag in the command above prepares environments for all hooks regardless of `SKIP`, so drop it when relying on this — missing environments are then installed on first use. The [automation](automatic-init-target) accounts for this automatically. The skipped hooks still run in CI, which executes on supported platforms.
:::

## First commit
```bash
git add .
git commit -m "Initial extension layout"
```

In case the hooks modify or create files, the commit is aborted. Stage the changes and try again.

[jinja-exts]: https://github.com/salt-extensions/salt-extension-copier/blob/main/jinja_extensions/saltext.py
[tasks-migrations]: https://github.com/salt-extensions/salt-extension-copier/blob/main/copier.yml
[trust-flag]: https://copier.readthedocs.io/en/stable/configuring/#unsafe
