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

```bash
git init
python -m venv venv
source venv/bin/activate
python -m pip install -e '.[tests,dev,docs]'
pre-commit install
git add .
git commit -m "Initial extension layout"  # Can fail, just add the changes and repeat
```

## Important considerations
TODO

### Organization or individual

[jinja-exts]: https://github.com/salt-extensions/salt-extension-copier/blob/main/jinja_extensions/saltext.py
[tasks-migrations]: https://github.com/salt-extensions/salt-extension-copier/blob/main/copier.yml
