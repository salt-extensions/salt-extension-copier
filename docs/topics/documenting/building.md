(build-docs-target)=
# Building documentation

:::{important}
Ensure {tool}`nox` is installed. If you executed the [first steps](first-steps-target) in some way, you should be all set.
:::

## Build once

To build your documentation once:

```bash
nox -e docs
# or: make docs
```

The rendered documentation will be located in `docs/_build/html`.

## Live preview
For continuous development, you can start a live preview that automatically reloads when changes are made:

```bash
nox -e docs-dev
# or: make docs-dev
```

This command builds the documentation, starts an HTTP server, opens your default browser, and watches for changes.

:::{note}
If building on a remote system, override the default `localhost` host with:

```bash
nox -e docs-dev -- --host=1.2.3.4
```
:::
