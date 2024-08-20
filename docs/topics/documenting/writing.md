# Writing documentation
Your project's documentation sources are found in `docs`.

## Markup language

### `docs/*`
You can write dedicated docs pages in both [MyST](https://myst-parser.readthedocs.io/en/stable/syntax/typography.html), a superset of Markdown,
and [RST](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html).

Yes, even in a mix.

### Docstrings
Docstrings in modules on the other hand must be written in RST.

## Cross-references
### Entities
It's possible to cross-reference specific entities, which can improve the documentation's usability a lot.

#### Modules
Link to a complete module.

Works for all modules that are present in the virtual environment, which includes Salt core ones.

:::{tab} MyST
```md
{py:mod}`foo <saltext.foo.modules.foo_mod>`
```
:::
:::{tab} RST
```rst
:py:mod:`foo <saltext.foo.modules.foo_mod>`
```
:::

#### Functions
Link to a specific function in a module.

Works for all modules that are present in the virtual environment, which includes Salt core ones.

:::{tab} MyST
```md
{py:func}`foo.bar <saltext.foo.modules.foo_mod.bar>`
```
:::
:::{tab} RST
```rst
:py:func:`foo.bar <saltext.foo.modules.foo_mod.bar>`
```
:::

#### Salt master configuration value
Link to the documentation of a Salt master configuration value.

:::{tab} MyST
```md
{conf_master}`ssh_minion_opts`
```
:::

:::{tab} RST
```rst
:conf_master:`ssh_minion_opts`
```
:::

#### Salt minion configuration value
Link to the documentation of a Salt minion configuration value.

:::{tab} MyST
```md
{conf_minion}`order_masters`
```
:::

:::{tab} RST
```rst
:conf_minion:`order_masters`
```
:::

### Arbitrary anchors
You can define arbitrary anchors and reference them later in the same document or from a different document.

:::{tab} MyST
```md
(my-custom-target)=
# Something

...

Later in the file, or in another one:

Please refer to [Something](my-custom-target)
```
:::
:::{tab} RST
```rst
.. _my-custom-target:
Something
=========

...

Later in the file, or in another one:

Please refer to :ref:`Something <my-custom-target>`
```
:::
