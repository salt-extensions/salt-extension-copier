# Create Salt Extensions

A [Copier](https://github.com/copier-org/copier) template that initializes a project structure for developing [Salt](https://github.com/saltstack/salt) extension modules.

The template files themselves are currently sourced almost verbatim from the official [create-salt-extension](https://github.com/saltstack/salt-extension) tool. This template provides the necessary scaffolding to render them via Copier ([which does not require ugly hacks for this like Cookiecutter+Cruft](https://github.com/lkubb/salt-extension-cookiecutter/)).

I would like to keep this mostly in sync/slightly ahead of upstream.

## Why
With the amount of extensions that could be created in the future, I think it is relevant to ensure they have a frictionless way of keeping the necessary boilerplate up to date. I have used this method before for my numerous formulae via `cruft` and have been quite happy.

## How
### Prerequisites
You will currently need the latest code of [Copier](https://copier.readthedocs.io/en/latest/), which is still unreleased (for [multiselect functionality](https://github.com/copier-org/copier/pull/1386)). It is generally recommended to install it via `pipx`:

```bash
pipx install git+https://github.com/copier-org/copier
```

Furthermore, since this template provides some Jinja extensions, you will need to ensure [copier-templates-extensions](https://github.com/copier-org/copier-templates-extensions) is present in the `copier` virtual environment:

```bash
pipx inject copier copier-templates-extensions
```

Note that `copier` will have to be invoked with the `--trust` flag because of the included Python code that will run during template rendering. Please verify for yourself that it does not do anything nasty.

### Creation
Now, creating an extension project is as simple as running:

```bash
copier copy --trust https://github.com/lkubb/salt-extension-copier saltext-example
```

You will be presented with several questions, after which the project skeleton should be available. It will additionally contain a `.copier-answers.yml` file with the inputs you gave and the commit ref of the template repository that was used when creating it. You should commit it together with the project.

### First Commit
For specifics, please follow the rendered `README.md` instructions. The following describes the general workflow with notes:

Inside your project directory, initialize a git repository:

```bash
git init
```

Ensure you create a virtual environment for your extension and source it:

```bash
python -m venv venv --prompt 'saltext-example'
source venv/bin/activate
```

Then, install the project inside the created environment in editable mode. This is required for `pre-commit` to work later (and needs to be run inside a git repository, so ensure you have initialized it at this point):

```bash
python -m pip install -e '.[tests,dev,docs]'  # zsh requires the quotes
```

Ensure the pre-commit hook is installed:

```bash
pre-commit install
```

At least on some macOS systems, you will need to ensure the pre-commit lint hooks do not attempt to install requirements, otherwise you will receive errors like `error: could not create 'build/bdist.macosx-13.6-arm64/wheel/saltext': Permission denied` and similar ones:

```bash
export SKIP_REQUIREMENTS_INSTALL=1
```

Then, you are ready to commit:

```bash
git add . && git commit -m "Initial commit"
```

Note that the pre-commit hooks might modify or create some files, which will make it fail. Just re-execute the command and all should be set.

### Updating
Future boilerplate updates can be as simple as:

```bash
copier update --trust --skip-answered
```

In case you want to update your answers to the questions as well as update:

```bash
copier update --trust
```

To just change your answers without updating, you will need to specify the commit hash found in your `.copier_answers.yml`:

```bash
copier update --trust --vcs-ref=$ref
```

Note that manually changing the inputs in the file is [strongly discouraged](https://copier.readthedocs.io/en/latest/updating/#never-change-the-answers-file-manually) by Copier.

## References
* The official tool is found here: https://github.com/saltstack/salt-extension
* The `salt-extensions` organization: https://github.com/salt-extensions
* `copier` docs: https://copier.readthedocs.io/en/latest/
* An overview of modular systems in Salt: https://docs.saltproject.io/en/latest/topics/development/modules/index.html
* The Salt-specific `pytest` docs: https://pytest-salt-factories.readthedocs.io/en/latest/
