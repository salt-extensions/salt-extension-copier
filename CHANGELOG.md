The changelog format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

This project uses [Semantic Versioning](https://semver.org/) - MAJOR.MINOR.PATCH

# Changelog

## 0.4.7 (2024-10-04)


### Fixed

- Fixed codecov uploads in enhanced workflow

## 0.4.6 (2024-10-04)


### Changed

- Reduced maximum Python support of 3007 to 3.10 since 3.11 and 3.12 have issues

## 0.4.5 (2024-09-27)


### Changed

- Allowed specifying a minor version in max_salt_version
- Improved test version matrix generation in enhanced workflow


### Fixed

- Fixed basic workflow tests running against .0 minor releases only
- Fixed project environment initialization crash during first copy. This crash did not result in any issues other than a warning after copy.
- Moved migrations into Python script, making them more platform-agnostic
- Updated salt-rewrite URL in pre-commit config


### Added

- Added `os_support` question when enhanced workflows were selected, influencing the OS the tests are run on

## 0.4.4 (2024-09-25)


### Fixed

- Fixed RenovateBot warning about merge conflicts after update

## 0.4.3 (2024-09-25)


### Changed

- Made pre-commit run on all files in PRs that change lint config
- Made repo automation reset git index after running pre-commit to allow RenovateBot to detect new files correctly

## 0.4.2 (2024-09-24)


### Changed

- Ignored keyword-arg-before-vararg pylint warning by default because `salt.utils.args.get_function_argspec` does not work with this style

## 0.4.1 (2024-09-23)


### Fixed

- Fixed check-merge-conflict pre-commit hook false positive in RST files with specific Saltext name lengths [#52](https://github.com/salt-extensions/salt-extension-copier/issues/52)

## 0.4.0 (2024-09-23)


### Removed

- Removed unnecessary `docs-html` and `gen-api-docs` nox sessions
- Removed unused saltpylint dependency


### Changed

- Changed nox pre-commit hook to local hook, added support for recent nox versions
- Homogenized YAML syntax in `org`/`enhanced` workflows
- Increased default pylint strictness
- Made rolling doc releases the default when `source_url` is in org
- Pinned pylint version used for linting
- Switched nox venv backend to uv, which reduced the time for pre-commit linting and other nox sessions significantly
- Updated pre-commit hook versions
- Updated pylint configuration


### Fixed

- Fixed unwanted regeneration of deleted boilerplate during updates [#41](https://github.com/salt-extensions/salt-extension-copier/issues/41)
- Added Copier template test runs on macOS and Windows and fixed some template issues on Windows
- Ensured pylint lints against the minimum required Python version
- Fixed `deploy-docs` if condition in `enhanced` workflow
- Fixed license classifier usage when non-apache `license` is selected
- Fixed unreleased version in rendered docs changelog with `enhanced` workflow
- Made merge conflict pre-commit hook always run
- Removed duplicate pre-commit hook for merge conflict check


### Added

- Automated most post-copy/update tasks like repo initialization, dev env setup and pre-commit installation and running [#45](https://github.com/salt-extensions/salt-extension-copier/issues/45)
- Added 3006.9 to known point releases
- Added `(master|minion)_config` fixtures to easily allow daemon configuration overrides
- Added `actionlint` with `shellcheck` integration as a pre-commit hook
- Added `relax_pylint` question to suppress some annoying messages, especially with legacy code
- Added a `.envrc` for direnv that runs the new initialization script, ensuring that development environments are present and in sync for all developers
- Added development environment initialization script to generated projects
- Allowed overriding parameters to sphinx-autobuild in `docs-html` nox session

## 0.3.7 (2024-08-05)

Correct meta files, remove install note, better docs URL default

### Changed

- Defaulted docs_url to GH Pages URL when deploying docs
- Removed install note regarding relenv bug


### Fixed

- Fixed new meta files added in 0.3.5


## 0.3.6 (2024-08-05)

Workflow fixes/improvements, more meta files

### Changed

- Synced `enhanced` workflow actions with centralized ones (docs deploy)
- Require tests passing for deploying docs, add docs deploy to pipeline exit status
- Default to `org` workflows if `source_url` is within org

### Fixed

- Fixed `enhanced` workflows
- Removed GitHub Actions workflow creation if `source_url` is not on GitHub

### Added

- Added `deploy_docs` option
- Added more meta files (CODE-OF-CONDUCT, CONTRIBUTING, NOTICE)


## 0.3.5 (2024-07-23)

SSH fixtures fixes

### Changed

- Stopped ignoring host keys in SSH tests

### Fixed

- Fixed test suite crash on Windows when `ssh_fixtures` is selected


## 0.3.4 (2024-07-23)

Workflow deprecation warning fix

### Changed

- Switched from deprecated set-output to environment file in workflows


## 0.3.3 (2024-07-23)

Fix black formatting

### Fixed

- Fixed default black formatting


## 0.3.2 (2024-07-22)

Fix docs build, update dev stuff

### Fixed

- Fixed docs build with importlib-metadata >=8
- Fixed enhanced workflow syntax

### Added

- Added `test_containers` question
- Added 3007.1 to known point releases


## 0.3.1 (2024-05-23)

Provide Python 3.8 migration

### Changed

- Updated actions in workflows
- Updated test requirements

### Fixed

- Provided migration from <0.3.0 regarding `min_python_version` to avoid update crash with `--skip-answered`
- Fixed coverage in `enhanced` workflow

### Added

- Added upload of html-docs artifact to `enhanced` workflow


## 0.3.0 (2024-05-07)

Drop Python 3.7 support, dev updates, default to 3006

### Changed

- Defaulted `min_salt_version` to 3006
- Migrated into `salt-extensions` org
- Dropped Python 3.7 support
- Replaced import reordering tool with isort
- Improved package_name validation
- Updated pre-commit hooks for Python >= 3.8

### Added

- Added crossrefs for `conf_(minion|master)` in docs
- Added 3005.5 to known point releases
- Added 3006.7 to known point releases
- Added 3006.8 to known point releases


## 0.2.9 (2024-02-20)

Correct autodocs path

### Fixed

- Fixed module discovery in autodocs pre-commit hook when `project_name` != `package_name`


## 0.2.8 (2024-02-08)

Suppress localhost linkcheck errs, update data

### Changed

- Suppressed localhost linkcheck errors

### Added

- Added 3006.6 to known point releases
- Added Python 3.12 to 3007 version support


## 0.2.7 (2024-01-06)

Workflow improvements, sync with official tool

### Fixed

- Corrected unit test opts fixture confdir

### Added

- Added enhanced and centralized workflows


## 0.2.6 (2023-12-15)

Minor fixes, support nested utils, add install guide

### Changed

- Minor docs layout changes

### Fixed

- Fixed discovery of nested utils in autodocs hook

### Added

- Added default installation guide


## 0.2.5 (2023-12-13)

Cleanup docs, add changelog to docs, fix CLI scripts

### Changed

- Reduced docs nesting, removed `docs/**/all.rst`

### Fixed

- Fixed local pre-commit hooks paths

### Added

- Added (rolling) changelog to docs


## 0.2.4 (2023-12-11)

Fix typo in README

No significant changes.


## 0.2.3 (2023-12-11)

Community enhancements, changelog

### Changed

- Reworked default README

### Added

- Added towncrier scaffolding
- Added GitHub issue/PR templates


## 0.2.2 (2023-12-10)

pyproject.toml with Salt requirement fixed

### Fixed

- Readded Salt requirement


## 0.2.1 (2023-12-08)

Fix docs build after pyproject migration

### Fixed

- Fixed docs build after switch to pyproject.toml


## 0.2.0 (2023-12-08)

Remove pinning, transition to `pyproject.toml`

### Changed

- Transitioned to `pyproject.toml`


## 0.1.6 (2023-12-08)

Remove pinning

### Changed

- Dropped scaffolding for requirements pinning

### Fixed

- Fixed README instructions


## 0.1.5 (2023-11-15)

Fix autodocs in pre-commit workflow

### Fixed

- Fixed module discovery in autodocs hook


## 0.1.4 (2023-11-15)

More docs build fixes

### Fixed

- Fixed 3.7 pip-compile docs


## 0.1.3 (2023-11-15)

Fix docs build

### Fixed

- Ensured make-autodocs works without saltext namespace
- Fixed intersphinx URL for pytest

### Added

- parametrized docs/all.rst


## 0.1.2 (2023-11-15)

pre-commit pylint fixes

### Fixed

- Fixed pre-commit nox/pylint race condition


## 0.1.1 (2023-11-14)

salt-rewrite 2.3.0 has wrong python_requires

### Fixed

- Fixed pre-commit on Python 3.7 (salt-rewrite 2.3.0 has wrong python_requires)


## 0.1.0 (2023-11-14)

diverged from official salt-extension tool

### Removed

- Dropped support for Python <3.7
- Dropped support for Salt <3003

### Changed

- Defaulted minimum supported version to 3005
- Updated pre-commit hook versions
- Updated workflow action versions
- Added validation for many inputs

### Fixed

- Corrected minimum pytest-salt-factories version
- Corrected reference to requirement files

### Added

- Parametrized versions all over the template
- Added salt-ssh fixtures
- Added functional tests skeleton
- Added `(minion|master)_opts` unit test fixtures


## 0.0.2 (2023-11-14)

in sync w/ salt-extension + pre-commit applied

### Fixed

- Fixed default project pre-commit formatting


## 0.0.1 (2023-11-13)

Initial release based on official salt-extension tool
