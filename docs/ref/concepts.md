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

* Salt extensions were introduced in [February 2016](https://github.com/saltstack/salt/pull/31218) and released in Salt 2016.9.
* A major improvement was added in November 2020 and released in [Salt 3003](https://github.com/saltstack/salt/pull/58943). You can watch the [Salt Extension Overview](https://www.youtube.com/watch?v=hhomJkwxK3Q) video for more details.
* In July 2022, Tom Hatch submitted a [SEP](https://github.com/saltstack/salt-enhancement-proposals/blob/24660626d9fe26953cd4581be0804ddfd0ceeb90/extention-migration.md) to migrate lots of built-in modules to extensions.
* In October 2023, a [project board](https://github.com/orgs/salt-extensions/projects/5/views/1) was created to track the migration process
* After the Broadcom event, the push really came to shove, and it was said that there [won't be any deprecation period](https://www.youtube.com/watch?v=CubGR8rTy3Y&t=245s).
* In January 2024, the [list of modules to be extracted](https://github.com/saltstack/great-module-migration) was opened for comments. Take your time to read it.
* The modules are being migrated into the [salt-extensions](https://github.com/salt-extensions) community org.
* In February 2024, the [great module purge PR](https://github.com/saltstack/salt/pull/65971) was created.
* In April 2024, the great module purge PR was merged, making 3008 the target release.

The main reasons for such a drastic change are:

1. Reduce the amount of effort required to maintain Salt.
2. Bulk deprecate modules that are no longer used, maintained, or relevant.
3. Release modules independent of Salt versions – decoupling the extension module release cycle from Salt allows for more up-to-date plugins and better backporting. For extensions that are pure Python, only a single artifact will need to be released, rather than dozens per release.
4. Release platform specific versions of Salt that are smaller and more efficient.
5. Speed up PR merges and reviews through faster tests and a smaller core code base.

The modules are split into three categories:

1. Core modules - will be kept inside the main Salt codebase, and development will be tied to the Salt release cycle.
2. Supported modules (extended core) - will be moved to their own repositories within the SaltStack Github organization where they can be maintained separately from the Salt codebase.
3. Community modules - will be deprecated from the Salt Core codebase and community members will be able to continue independent maintainership if they are interested. The community modules can be hosted either in the community run Salt Extensions Github organization, or in individual or corporate source control systems.

In conclusion, this migration represents a shift in how Salt is maintained and developed. It opens the door for users and organizations to have a direct impact on the tools they rely on. If you use any of the modules categorized as community modules, their future depends on people like you. By becoming a maintainer or contributor, you can ensure that the modules you depend on continue to thrive and evolve.

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

(copier-template-ref)=
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
