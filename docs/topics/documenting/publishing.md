(docs-publish-target)=
# Publishing documentation

If your {question}`source_url` is on GitHub and you selected either `org` or
`enhanced` {question}`workflows`, you can automatically deploy your documentation to your repository's GitHub Pages site. This deployment is controlled by the {question}`deploy_docs` setting.

(docs-publish-setup-target)=
## Setup

To enable documentation publishing, follow these steps:

1. On GitHub, navigate to your repository and click on `Settings`.
2. Select `Pages`.
3. Under `Build and deployment source`, ensure `GitHub Actions` is selected.

Once configured, your documentation will be automatically published to your GitHub Pages site after a `tag` event or a `push` event (if {question}`deploy_docs` == `rolling`).

## Further steps

### Docs URL in metadata

Ensure the {question}`docs_url` points to your GitHub Pages site. This URL is included in the project's PyPI metadata and ensures that the {path}`README.md` contains a link to the user documentation.

### Repository website

Consider setting your GitHub Pages site as the project's website on GitHub:

1. In your repository, click the settings wheel in the top right corner (not the `Settings` tab in the navigation bar).
2. Under `Website`, select `Use your GitHub Pages website`.
