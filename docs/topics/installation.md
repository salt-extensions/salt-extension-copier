# Installation

To render the template, you only need a functional [Copier][copier-docs] installation.

## Copier

:::{tab} pipx

It’s recommended to install Copier globally using [pipx][pipx-docs]:

```bash
pipx install 'copier>=9.3' && \
 pipx inject copier copier-templates-extensions
```
:::

:::{tab} pip

Alternatively, you can install Copier with `pip`, preferably inside a virtual environment:

```bash
python -m pip install 'copier>=9.3' copier-templates-extensions
```
:::

:::{important}
This template includes custom Jinja extensions, so ensure that [copier-templates-extensions][copier-templates-extensions] is installed in the same environment as `copier`. The example commands above handle this.
:::

[copier-docs]: https://copier.readthedocs.io/en/stable/
[copier-multiselect-pr]: https://github.com/copier-org/copier/pull/1386
[copier-templates-extensions]: https://github.com/copier-org/copier-templates-extensions
[pipx-docs]: https://pipx.pypa.io/stable/
