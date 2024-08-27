# Keeping a changelog

Your Saltext project uses [towncrier](https://towncrier.readthedocs.io/en/stable/) to manage and render its {path}`CHANGELOG.md` file, which is included in the rendered documentation as well.

:::{hint}
If you selected {question}`deploy_docs` == `rolling`, the changelog will display upcoming changes from the `main` branch alongside [crystallized changes from previous releases](changelog-build-target).
:::

(news-fragment-target)=
## Procedure

For every user-facing change, ensure your patch includes a corresponding news fragment:

1. Ensure there is an issue in the bug tracker that describes the context of the change.
2. Before merging a PR, ensure a news fragment describing the change is added to the `changelog` directory.
3. Its file name should follow `<issue_number>.<resolution>.md`, where `resolution` is one of the following:

    * `fixed`
    * `added`
    * `changed`
    * `removed`
    * `deprecated`
    * `security`

4. The file contents should be written in Markdown.

## Example

Suppose a PR fixes a crash when the `foo.bar` configuration value is missing. The news fragment can be created as follows:

```bash
echo "Fixed a crash when 'foo.bar' is missing from the configuration" > changelog/23.fixed.md
```

Include this file in the PR.

## Building the changelog

Before tagging a release, the individual `changelog/*.md` files need to be compiled into the actual changelog. Refer to [Building the changelog](changelog-build-target) for instructions on how to do this.
