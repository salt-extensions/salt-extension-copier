# Concepts

The following describes important concepts around Salt extensions on a high level.

(saltext-ref)=
## Salt extension

Salt extensions are `pip`-installable Python packages that hook into Salt's module
loading system and can thus provide all kinds of modules, much like custom
extension modules in `salt://_modules`, `salt://_states` etc.

In contrast to custom modules, they can be developed inside a dedicated
testing framework similar to the one found in Salt core and have versioned
releases. On a downside, they need to be installed on each node separately.

(great-migration-ref)=
## Great module migration
TODO

(gh-org-ref)=
## GitHub organization

While anyone can create and release a Salt extension, the [salt-extensions GitHub organization][saltext-org]
was created as a community-run umbrella to provide a more centralized and
frictionless experience for both developers and users.

It is intended to both host existing sets of modules extracted from Salt core
from the `3008` release onwards as well as completely new extensions.

Do you care about a set of modules that will be removed from Salt core?
Do you want to publish some awesome new Salt functionality?
Getting involved is easy! Just head over to the `salt-extensions` channel
on the [community Discord][discord-invite] and introduce yourself.

## Copier template

The `salt-extension-copier` template reduces overhead in creating and maintaining
Salt extensions a lot. Based on a set of inputs, it creates an individualized
boilerplate for anyone to develop shiny new Salt functionality.
When new template versions are released, an existing project's boilerplate
can be updated in an automated way.

Very important: You don't need to publish inside the organization to use it!
It can be used for individual projects as well.


[saltext-org]: https://github.com/salt-extensions
[discord-invite]: https://discord.gg/bPah23K7mG
