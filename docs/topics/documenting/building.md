(build-docs-target)=
# Building documentation

:::{important}
Ensure you have already installed `nox`. If you followed the [first steps](first-steps-target), you should be fine.
:::

## Prerequisites
On some systems (MacOS, WSL, some Linux distributions) building the docs requires the `enchant` library to be installed on your system.

:::{tab} Linux/WSL
```bash
sudo apt-get install -y enchant
```
:::
:::{tab} MacOS
```bash
brew install -y enchant
```

:::{important}
On Apple Silicon, you might need to ensure your environment points to the correct library location:

```bash
export PYENCHANT_LIBRARY_PATH=/opt/homebrew/lib/libenchant-2.2.dylib
```
:::

## Build once
If you just want to build your documentation:

```bash
nox -e docs
```

You can find the rendered docs in `docs/_build/html`.

## Live preview
While developing, it can help to have an automatically reloading preview of the rendered documentation.
The following command renders the current documentation, starts an HTTP server, opens your default browser
and watches the repository for changes.

```bash
nox -e docs-dev
```

:::{note}
If you're building the documentation on a remote system, you need to override the
host the HTTP server is listening to since it defaults to `localhost`:

```bash
nox -e docs-dev -- --host=1.2.3.4
```
:::
