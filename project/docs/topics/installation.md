# Installation

Generally, extensions need to be installed into the same Python environment Salt uses.

:::{tab} State
```yaml
Install Salt {{ project_name | capitalize}} extension:
  pip.installed:
    - name: {{ project_name_full }}
```
:::

:::{tab} Onedir installation
```bash
salt-pip install {{ project_name_full }}
```
:::

:::{tab} Regular installation
```bash
pip install {{ project_name_full }}
```
:::

:::{important}
Currently, there is [an issue][issue-second-saltext] where the installation of a Saltext fails silently
if the environment already has another one installed. You can workaround this by
removing all Saltexts and reinstalling them in one transaction.
:::

:::{hint}
Saltexts are not distributed automatically via the fileserver like custom modules, they need to be installed
on each node you want them to be available on.
:::

[issue-second-saltext]: https://github.com/saltstack/salt/issues/65433
