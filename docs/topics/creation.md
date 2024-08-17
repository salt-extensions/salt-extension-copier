# Creation

With Copier, creating a Salt extension project structure is easy:

```bash
copier copy --trust https://github.com/salt-extensions/salt-extension-copier my-awesome-new-saltext
```

You are then asked a set of questions that will shape the final project structure. They will be remembered for future updates in `.copier-answers.yml`.

:::{important}

Copier needs to be invoked with the `--trust` flag in order to enable
custom Jinja extensions required for template rendering (and, when updating, migrations).
Effectively, this runs unsandboxed commands defined in the template on your host,
so ensure you trust it!

* [Jinja extensions][jinja-exts]
* [tasks and migrations][tasks-migrations]
:::

## Important considerations
TODO
### Organization or individual

[jinja-exts]: https://github.com/salt-extensions/salt-extension-copier/blob/main/jinja_extensions/saltext.py
[tasks-migrations]: https://github.com/salt-extensions/salt-extension-copier/blob/main/copier.yml
