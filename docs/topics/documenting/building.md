(build-docs-target)=
# Building documentation

:::{important}
Ensure `nox` is installed. If you followed the [first steps](first-steps-target), you should be all set.
:::

## Prerequisites

On some systems (macOS, WSL, and certain Linux distributions), you must install the `enchant` library to build the documentation.

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

To build your documentation once:

```bash
nox -e docs
```

The rendered documentation will be located in `docs/_build/html`.

## Live preview
For continuous development, you can start a live preview that automatically reloads when changes are made:

```bash
nox -e docs-dev
```

This command builds the documentation, starts an HTTP server, opens your default browser, and watches for changes.

:::{note}
If building on a remote system, override the default `localhost` host with:

```bash
nox -e docs-dev -- --host=1.2.3.4
```
:::
