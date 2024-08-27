(writing-docs-target)=
# Writing documentation

Your project's documentation is located in the {path}`docs` directory.

## Markup language

### `docs/*`
You can write dedicated documentation pages using either [MyST](https://myst-parser.readthedocs.io/en/stable/syntax/typography.html) (a Markdown superset) or [reStructuredText (rST)](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html). Mixing files of different formats is allowed.

### Docstrings
Docstrings in your modules must be written in rST.

## Tagging changes between versions

Document any user-facing changes between releases using the `versionadded`, `versionchanged`, `deprecated`, or `versionremoved` directives.

:::{tab} MyST
    changed_arg
    :   Has been doing something for a long time.

        :::{versionchanged} 1.1.0
        Does it a little differently now.
        :::

    new_arg
    :   Does something new.

        :::{versionadded} 1.1.0
        :::
:::

:::{tab} rST
```rst
changed_arg
    Has been doing something for a long time.

    ..versionchanged:: 1.1.0
        Does it a little differently now.

new_arg
    Does something new.

    .. versionadded:: 1.1.0
```
:::

:::{tab} Preview
changed_arg
:   Has been doing something for a long time.

    :::{versionchanged} 1.1.0
    Does it a little differently now.
    :::

new_arg
:   Does something new.

    :::{versionadded} 1.1.0
    :::
:::

## Cross-references

### Entities
Improve documentation usability by cross-referencing entities. Some highlights:

#### Modules
Link to a complete module.

:::{tab} MyST
```md
{py:mod}`foo <saltext.foo.modules.foo_mod>`
```
:::

:::{tab} rST
```rst
:py:mod:`foo <saltext.foo.modules.foo_mod>`
```
:::

:::{hint}
Works for all packages registered in the `docs/conf.py`
`intersphinx_mapping`. This specifically includes Salt core by default.
:::

#### Functions
Link to a specific function within a module.

:::{tab} MyST
```md
{py:func}`foo.bar <saltext.foo.modules.foo_mod.bar>`
```
:::

:::{tab} rST
```rst
:py:func:`foo.bar <saltext.foo.modules.foo_mod.bar>`
```
:::

:::{hint}
Works for all packages registered in the `docs/conf.py`
`intersphinx_mapping`. This specifically includes Salt core by default.
:::

#### Salt master configuration
Link to the documentation of a Salt master configuration value.

:::{tab} MyST
```md
{conf_master}`ssh_minion_opts`
```
:::

:::{tab} rST
```rst
:conf_master:`ssh_minion_opts`
```
:::

#### Salt minion configuration
Link to the documentation of a Salt minion configuration value.

:::{tab} MyST
```md
{conf_minion}`order_masters`
```
:::

:::{tab} rST
```rst
:conf_minion:`order_masters`
```
:::

### Arbitrary anchors
Define and reference custom anchors within the same or different documents.

:::{tab} MyST
```md
(my-custom-target)=
# Something

...

Later in the file, or in another one:

Please refer to [Something](my-custom-target)
```
:::

:::{tab} rST
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

Use admonitions to add notes or emphasize important information.

:::{tab} MyST

    :::{important}
    Ensure you understand the usage of admonitions.
    :::
:::

:::{tab} rST
```rst
.. important::
    Ensure you understand the usage of admonitions.
```
:::

:::{tab} Preview
:::{important}
Ensure you understand the usage of admonitions.
:::

Common admonitions include:

* `important`
* `hint`
* `note`
* `warning`
* `attention`
* `tip`

## Tabs

You can use tabs to organize content, as shown here. Tabs with the same titles will synchronize.

:::{tab} MyST

    :::{tab} MyST
    ... is a supserset of Markdown.
    :::

    :::{tab} rST
    ... is not a supserset of Markdown.
    :::
:::

:::{tab} rST
```rst
.. tab:: MyST
    ... is a supserset of Markdown.

.. tab:: RST
    ... is not a supserset of Markdown.
```
:::
