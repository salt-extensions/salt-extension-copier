(building-target)=
# Building your Saltext

## Prerequisites

Ensure your Python environment has the `build` package installed:

```bash
python -m pip install build
```

:::{important}
Your project must be tracked by Git. Make sure you have initialized your repository.
:::

## Building

Building your Salt extension's wheel is easy:

```bash
python -m build --outdir dist/
```

The installable wheel file (`.whl`) can be found in the `dist` directory. You can install it with `salt-pip`/`pip`, provided you don't rename the file.

For broader distribution, consider [publishing](publishing) your extension to a package index like PyPI.
