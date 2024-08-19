# Building your Saltext

## Prerequisites

In order to build your Salt extension, ensure your current Python has the `build` package installed:

```bash
python -m  pip install build
```

:::{important}
Building requires your project to be tracked by Git. Ensure you have
initialized your repository by now.
:::

## Building

Building your Salt extension's wheel is easy:

```bash
python -m build --outdir dist/
```

Then you can find the installable wheel (`.whl` file extension) inside the `dist` directory. In theory, this file can be installed via `pip`, provided you don't rename it.

You should consider [publishing](publishing) your extension to a package index like PyPI though.
