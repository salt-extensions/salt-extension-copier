# Installation

To render the template, you only need a functional [Copier][copier-docs] installation.

## Copier

It’s recommended to install Copier globally using either [uv][uv-docs] or [pipx][pipx-docs]:

:::{tab} uv


```bash
uv tool install --python 3.10 --with copier-templates-extensions 'copier>=9.3,<9.5'
```
:::

:::{tab} pipx

```bash
pipx install 'copier>=9.3,<9.5' && \
 pipx inject copier copier-templates-extensions
```
:::

:::{tab} pip

Alternatively, you can install Copier with `pip`, preferably inside a virtual environment:

```bash
python -m pip install 'copier>=9.3,<9.5' copier-templates-extensions
```
:::

:::{note}
The `copier` virtual environment should be based on the Python version (MAJOR.MINOR) [listed here](https://github.com/saltstack/salt/blob/master/cicd/shared-gh-workflows-context.yml), at the time of writing Python 3.10. Other versions - especially higher ones - should work, but the template's CI tests only verify the mentioned version.
:::

:::{important}
This template includes custom Jinja extensions, so ensure that [copier-templates-extensions][copier-templates-extensions] is installed in the same environment as `copier`. The example commands above handle this.
:::

[copier-docs]: https://copier.readthedocs.io/en/stable/
[copier-multiselect-pr]: https://github.com/copier-org/copier/pull/1386
[copier-templates-extensions]: https://github.com/copier-org/copier-templates-extensions
[pipx-docs]: https://pipx.pypa.io/stable/
[uv-docs]: https://docs.astral.sh/uv/
