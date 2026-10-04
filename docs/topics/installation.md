# Installation

To render the template, you only need a functional {tool}`copier` installation.

## Copier

It’s recommended to install Copier globally using either {tool}`uv` or [pipx][pipx-docs]:

:::{tab} uv


```bash
uv tool install --python 3.14 --with copier-template-extensions 'copier>=9.6'
```
:::

:::{tab} pipx

```bash
pipx install 'copier>=9.6' && \
 pipx inject copier copier-template-extensions
```
:::

:::{tab} pip

Alternatively, you can install Copier with `pip`, preferably inside a virtual environment:

```bash
python -m pip install 'copier>=9.6' copier-template-extensions
```
:::

:::{note}
The `copier` virtual environment should be based on a recent Python version. Other versions should work, but the template's CI tests currently only verify Python 3.14.
:::

:::{important}
This template includes custom Jinja extensions, so ensure that [copier-template-extensions][copier-template-extensions] is installed in the same environment as `copier`. The example commands above handle this.
:::

[copier-template-extensions]: https://github.com/copier-org/copier-template-extensions
[pipx-docs]: https://pipx.pypa.io/stable/
