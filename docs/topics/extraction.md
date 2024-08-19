# Extraction of Salt core modules
TODO - ref https://github.com/salt-extensions/extension_migration

## Gotchas
### Unit test imports

Unit tests import the modules directly. After migration, these imports
need to be adjusted, otherwise the tests will run against the modules found in Salt, but still pass (or fail once they are removed). Example:

```python
# Old import
from salt.modules import vault

# Correct
from saltext.vault.modules import vault
```
