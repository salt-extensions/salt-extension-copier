(docs-publish-target)=
# Publishing documentation

If your {question}`source_url` is on GitHub, you can automatically deploy your documentation to your repository's GitHub Pages site. This deployment is controlled by the {question}`deploy_docs` setting.

(docs-publish-setup-target)=
## Setup

To enable documentation publishing, follow these steps:

1. On GitHub, navigate to your repository and click on `Settings`.
2. Select `Pages`.
3. Under `Build and deployment source`, ensure `GitHub Actions` is selected.
4. Select `Environments`.
5. Click on `github-pages`.
6. Under `Deployment branches and tags`, click on `Add deployment branch or tag rule`
7. Ensure `Ref type` is `Branch` (the default).
8. As the `Name pattern`, enter `release/auto` (the branch name used by the [automated release PR](release-automated-target)).
9. Click on `Add rule`.

Once configured, your documentation is automatically published to your GitHub Pages site when [publishing a release](publishing-target) or after pushes to the default branch (if {question}`deploy_docs` == `rolling`).

## Further steps

### Docs URL in metadata

Ensure the {question}`docs_url` points to your GitHub Pages site. This URL is included in the project's PyPI metadata and ensures that the {path}`README.md` contains a link to the user documentation.

### Repository website

Consider setting your GitHub Pages site as the project's website on GitHub:

1. In your repository, click the settings wheel in the top right corner (not the `Settings` tab in the navigation bar).
2. Under `Website`, select `Use your GitHub Pages website`.
