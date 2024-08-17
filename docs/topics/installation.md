# Installation

You only need a functional [Copier][copier-docs] installation to render the template.

## Copier

:::{tab} pipx

It is generally recommended to install it globally via [pipx][pipx-docs]:

```bash
pipx install 'copier>=9.1' && \
 pipx inject copier copier-templates-extensions
```
:::

:::{tab} pip

If you want to use `pip` instead, run the following, preferably inside a virtual environment:

```bash
python -m pip install copier copier-templates-extensions
```
:::

:::{important}
Since this template provides some Jinja extensions, you need to ensure [copier-templates-extensions][copier-templates-extensions] is present in the `copier` virtual environment. The example installation commands above account for this.
:::

[copier-docs]: https://copier.readthedocs.io/en/stable/
[copier-multiselect-pr]: https://github.com/copier-org/copier/pull/1386
[copier-templates-extensions]: https://github.com/copier-org/copier-templates-extensions
[pipx-docs]: https://pipx.pypa.io/stable/
