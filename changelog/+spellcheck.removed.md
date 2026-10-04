Removed the vestigial `sphinxcontrib-spelling` Sphinx extension. Its spellcheck builder was never invoked, but loading the extension forced all docs builds to require the `enchant` system library.
