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

:::{hint}
Works for all packages whose docs are registered in the `docs/conf.py`
`intersphinx_mapping`. This specifically includes Salt core by default.
:::

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

:::{hint}
Works for all packages whose docs are registered in the `docs/conf.py`
`intersphinx_mapping`. This specifically includes Salt core by default.
:::

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
You can define arbitrary anchors and reference them later in the same document or from a different one.

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

## Admonitions

It's often helpful to add a related note to some topic using admonitions.

:::{hint}
They look like this.
:::

:::{tab} MyST

    :::{important}
    Ensure you understand the usage of admonitions.
    :::
:::

:::{tab} RST
```rst
.. important::
    Ensure you understand the usage of admonitions.
```
:::

Commonly used admonitions are:

* `important`
* `hint`
* `note`
* `warning`
* `attention`
* `tip`

## Tabs

It's also possible to use tabs like we have been doing here. As you can see, all tabs with the same titles are triggered in concert.

The syntax is as follows:

:::{tab} MyST

    :::{tab} MyST
    ... is a supserset of Markdown.
    :::

    :::{tab} RST
    ... is not a supserset of Markdown.
    :::
:::
:::{tab} RST
```rst
.. tab:: MyST
    ... is a supserset of Markdown.

.. tab:: RST
    ... is not a supserset of Markdown.
```
:::
