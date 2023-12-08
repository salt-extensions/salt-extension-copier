# Create Salt Extensions

A [Copier](https://github.com/copier-org/copier) template that initializes a project structure for developing [Salt](https://github.com/saltstack/salt) extension modules.

The template files themselves are based on the official [create-salt-extension](https://github.com/saltstack/salt-extension) tool, with several updates [submitted as a PR](https://github.com/saltstack/salt-extension/pull/42). This template provides the necessary scaffolding to render them via Copier ([which does not require ugly hacks for this like Cookiecutter+Cruft](https://github.com/lkubb/salt-extension-cookiecutter/)).

I would like to keep this mostly in sync/slightly ahead of upstream.

## Why
With the amount of extensions that could be created in the future, I think it is relevant to ensure they have a frictionless way of keeping the necessary boilerplate up to date. I have used this method before for my numerous formulae via `cruft` and am quite happy.

## How

![Preview](./docs/rec.svg)

### Prerequisites
At least [Copier](https://copier.readthedocs.io/en/latest/) version `9.1.0` is required (for [multiselect functionality](https://github.com/copier-org/copier/pull/1386)). It is generally recommended to install it via `pipx`:

```bash
pipx install copier
```

Furthermore, since this template provides some Jinja extensions, you need to ensure [copier-templates-extensions](https://github.com/copier-org/copier-templates-extensions) is present in the `copier` virtual environment:

```bash
pipx inject copier copier-templates-extensions
```

Note that `copier` has to be invoked with the `--trust` flag because of the included Python code that runs during template rendering. Please verify for yourself that it does not do anything nasty.

### Creation
Now, creating an extension project is as simple as running:

```bash
copier copy --trust https://github.com/lkubb/salt-extension-copier saltext-example
```

You are then presented with several questions, after which the project skeleton should be available. It additionally contains a `.copier-answers.yml` file with the inputs you gave and the commit ref of the template repository that was used when creating it. You should commit it together with the project.

### First commit
For specifics, please see the rendered `README.md` instructions. The following describes the general workflow with notes:

Inside your project directory, initialize a git repository:

```bash
git init
```

Ensure you create a virtual environment for your extension and source it:

```bash
python -m venv venv --prompt 'saltext-example'
source venv/bin/activate
```

Then, install the project inside the created environment in editable mode. This needs to be run inside a git repository, so ensure you have initialized it at this point:

```bash
python -m pip install -e '.[tests,dev,docs]'  # zsh requires the quotes
```

Ensure the pre-commit hook is installed:

```bash
pre-commit install
```

Then, you are ready to commit:

```bash
git add . && git commit -m "Initial commit"
```

Note that the pre-commit hooks might modify or create some files, which makes it fail. Just re-execute the command and all should be set.

### Updating
Future boilerplate updates can be as simple as:

```bash
copier update --trust --skip-answered
```

In case you want to update your answers to the questions as well as update:

```bash
copier update --trust
```

To just change your answers without updating, you need to specify the git ref found in your `.copier_answers.yml`:

```bash
copier update --trust --vcs-ref=$ref
```

Note that manually changing the inputs in the file is [strongly discouraged](https://copier.readthedocs.io/en/latest/updating/#never-change-the-answers-file-manually) by Copier.

### Migration from official tool
Existing projects can be migrated to this template by simply running the creation command over a clone of the existing repository. You should specify the `0.0.2` tag as a reference at the moment since this template diverges from the latest official release (`0.24.0`) after that.

```bash
git clone https://github.com/salt-extensions/saltext-example
copier copy --trust --vcs-ref=0.0.2 https://github.com/lkubb/salt-extension-copier saltext-example
```

You are then presented with the same questions as during initialization. `copier` asks about conflict resolutions and afterwards creates `.copier-answers.yml`. There have likely been several modifications to the boilerplate since the extension was generated, so this can require some attention and could even reintroduce older dependencies. In the next step, you should thus update the project to a more recent version.

## Differences vs the official tool
The latest version of this template differs from the latest `salt-extension 0.24.0` in the following ways:
* Updated dependencies, pre-commit hooks and workflow actions
* Salt and Python versions are parametrized all over the template
* Dropped support for Python 3.5/3.6 completely
* Contains functional tests skeleton, `(master|minion)_opts` fixtures for unit tests and optionally fixtures for `salt-ssh` tests
* Removes pinning of test/docs/lint requirements ([related issue](https://github.com/saltstack/salt-extension/issues/41)) and the corresponding files
* Transitions to using `pyproject.toml` instead of `setup.cfg`

## References
* The official tool is found here: https://github.com/saltstack/salt-extension
* The `salt-extensions` organization: https://github.com/salt-extensions
* `copier` docs: https://copier.readthedocs.io/en/latest/
* An overview of modular systems in Salt: https://docs.saltproject.io/en/latest/topics/development/modules/index.html
* The Salt-specific `pytest` docs: https://pytest-salt-factories.readthedocs.io/en/latest/
