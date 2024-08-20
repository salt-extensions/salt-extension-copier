# Keeping a changelog

Your Saltext project includes scaffolding for keeping a changelog via [towncrier](https://towncrier.readthedocs.io/en/stable/).

This changelog is rendered as part of the documentation.

## Procedure
Each time there is a user-facing change to your project, the patch should contain a corresponding news fragment.

1. There should be an issue in the bug tracker that describes the context of the change.
2. Before merging a PR, ensure there is an added news fragment in the `changelog` directory describing the change.
3. Its file name should follow `<issue_number>.<resolution>.md`, where `resolution` is one of the following actions:

    * `fixed`
    * `added`
    * `changed`
    * `removed`
    * `deprecated`
    * `security`

4. Its file contents are interpreted as Markdown.

## Example

A PR fixes an ungraceful crash when the `foo.bar` configuration value is missing.
The author can create the news fragment as follows:

```bash
echo "Fixed a crash when 'foo.bar' is missing from the configuration" > changelog/23.fixed.md
```

This file should be submitted as part of the PR.
