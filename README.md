# Create & Maintain Salt Extensions

A [Copier](https://github.com/copier-org/copier) template that initializes a project structure for developing [Salt](https://github.com/saltstack/salt) [extension modules][saltext-def].

## Why
For individual extension creators, this template allows to [quickly get started with developing][saltext-creation], [testing][saltext-testing] and [releasing][saltext-release] new Salt functionality.

For extension maintainers and the [`salt-extensions` organization][gh-org-ref], it ensures that there is a frictionless way of keeping the necessary boilerplate [up to date][saltext-update].

## How

For comprehensive instructions on all aspects of Salt extension development with this template, please refer to the [user documentation][docs].

![Preview](./docs/rec.svg)

### Migration from the [deprecated tool][create-salt-extension]
Existing projects can be migrated to this template by simply running the [creation commands][saltext-creation] on top of a repo clone. Ensure you additionally pass `--vcs-ref=0.0.2` to Copier since this template diverges from the last official release (`0.24.0`) after that.

```bash
git clone https://github.com/salt-extensions/saltext-example
copier copy --trust --vcs-ref=0.0.2 https://github.com/salt-extensions/salt-extension-copier saltext-example
```

During this process, Copier asks about conflict resolutions. There have likely been several modifications to the boilerplate since the extension was generated, so this can require some attention and could even reintroduce older dependencies. Afterwards, you should [update the project][saltext-update] to the latest template version.

## References
* [User documentation][docs] for this template
* An overview of [modular systems in Salt][salt-modules]
* [Salt-specific `pytest` docs][pytest-salt-factories]
* [`salt-extensions` organization][gh-org]
* [Copier docs][copier-docs]

[docs]: https://salt-extensions.github.io/salt-extension-copier/
[saltext-def]: https://salt-extensions.github.io/salt-extension-copier/ref/concepts.html#saltext-ref
[saltext-creation]: https://salt-extensions.github.io/salt-extension-copier/topics/creation.html
[saltext-testing]: https://salt-extensions.github.io/salt-extension-copier/topics/testing/writing.html
[saltext-release]: https://salt-extensions.github.io/salt-extension-copier/topics/publishing.html
[gh-org-ref]: https://salt-extensions.github.io/salt-extension-copier/ref/concepts.html#gh-org-ref
[saltext-update]: https://salt-extensions.github.io/salt-extension-copier/topics/updating.html
[create-salt-extension]: https://github.com/saltstack/salt-extension
[copier-docs]: https://copier.readthedocs.io/en/stable/
[salt-modules]: https://docs.saltproject.io/en/latest/topics/development/modules/index.html
[pytest-salt-factories]: https://pytest-salt-factories.readthedocs.io/en/latest/
[gh-org]: https://github.com/salt-extensions/
