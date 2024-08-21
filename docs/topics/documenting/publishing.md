(docs-publish-target)=
# Publishing documentation

If your {question}`source_url` is on GitHub and you have selected `org` or
`enhanced` {question}`workflows`, you have the option to automatically deploy
your rendered documentation to your repository's GitHub Pages site.

This behavior is influenced by {question}`deploy_docs`.

(docs-publish-setup-target)=
## Setup
If you have enabled {question}`deploy_docs` in your Copier template, you need
to ensure the workflow is allowed to publish to your GitHub Pages site.

1. On GitHub, go to your repository and click on `Settings`.
2. Click on `Pages`.
3. Look for `Build and deployment source`.
4. Ensure `GitHub Actions` is selected.

Once a `tag` event or a `push` event (only if you selected {question}`deploy_docs` == `rolling`)
happens, the built documentation is automatically pushed to your GitHub pages site.

## Further steps
### Docs URL in metadata
Ensure {question}`docs_url` points to your GitHub Pages site.

This is included in the project's PyPI metadata and ensures the {path}`README.md`
contains a link to the user documentation.

### Repository website
Consider selecting your GitHub pages site as your project's website on GitHub.

1. On GitHub, go to your repository and click on the top right settings wheel
   (not the `Settings` button in the nav bar)
2. Under `Website`, select `Use your GitHub Pages website`.
