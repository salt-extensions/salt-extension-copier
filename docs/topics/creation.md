(creation-target)=
# Creation

With Copier, creating a Salt extension project structure is easy:

```bash
copier copy --trust https://github.com/salt-extensions/salt-extension-copier my-awesome-new-saltext
```

You are then asked a set of questions that will shape the final project structure.
They will be remembered for future updates in `.copier-answers.yml`.

:::{important}

Copier needs to be invoked with the `--trust` flag in order to enable
custom Jinja extensions required for template rendering (and, when updating, migrations).
Effectively, this runs unsandboxed commands defined in the template on your host,
so ensure you trust it!

* [Jinja extensions][jinja-exts]
* [tasks and migrations][tasks-migrations]
:::

(first-steps-target)=
## First steps

Many operations in your Salt extension project require to be run inside an initialized Git repository
and a Python virtual environment with your project installed. Some `pre-commit` hooks might also
create important files.

The following steps are therefore necessary to finish your project generation:

### Initialize the repository
```bash
git init -b main
```

:::{important}
Some automations might assume your default branch is called `main`. Please ensure
this assumption holds.
:::

(dev-setup-target)=
### Initialize the Python virtual environment
```bash
python -m venv venv
source venv/bin/activate
python -m pip install -e '.[tests,dev,docs]'
```

This creates a venv and installs relevant dependencies, including `nox` and `pre-commit`.

### Install `pre-commit` hook
```bash
python -m pre_commit install
```

This ensures `pre-commit` runs before each commit. It autoformats and lints your code and ensures the presence of some necessary documentation files. If you want to skip the checks during a commit for some reason, invoke Git like this: `git commit --no-verify`.

### First commit
```bash
git add .
git commit -m "Initial extension layout"
```

When `pre-commit` modifies or creates some files, the commit is aborted. Just stage the changes again and retry committing.

[jinja-exts]: https://github.com/salt-extensions/salt-extension-copier/blob/main/jinja_extensions/saltext.py
[tasks-migrations]: https://github.com/salt-extensions/salt-extension-copier/blob/main/copier.yml
