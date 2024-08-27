# Concepts

This section outlines key concepts related to Salt extensions.

(saltext-ref)=
## Salt extension

Salt extensions are `pip`-installable Python packages that hook into Salt's module
loading system. They function similarly to custom modules found in `salt://_modules`, `salt://_states` etc., but with additional benefits like a dedicated testing framework and versioned releases. However, they must be installed on each node individually.

(great-migration-ref)=
## Great module migration

The Salt Project team has embarked on a significant transformation known as the "Great Module Migration." This initiative involves moving many modules, which were previously part of the core Salt distribution, into separate extensions. While this shift promises to streamline Salt’s core, it also means that many modules will no longer be maintained directly by the Salt team. Instead, their future now depends on community contributors.

### Timeline and Key Events

- **February 2016**: Salt extensions [were introduced](https://github.com/saltstack/salt/pull/31218) with the release of Salt 2016.9.
- **November 2020**: A [major update](https://github.com/saltstack/salt/pull/58943) to Salt extensions was released in Salt 3003. [Watch the Salt Extension Overview](https://www.youtube.com/watch?v=hhomJkwxK3Q) video for more details.
- **July 2022**: Tom Hatch submitted a [SEP](https://github.com/saltstack/salt-enhancement-proposals/blob/24660626d9fe26953cd4581be0804ddfd0ceeb90/extention-migration.md) to migrate numerous built-in modules to extensions.
- **October 2023**: A [project board](https://github.com/orgs/salt-extensions/projects/5/views/1) was created to track the migration process.
- **December 2023**: The Broadcom event forced an immediate shift in strategy, leading to the announcement that there [won't be any deprecation period](https://www.youtube.com/watch?v=CubGR8rTy3Y&t=245s) for [community-designated](community-modules-target) modules.
- **January 2024**: A [list of modules to be extracted](https://github.com/saltstack/great-module-migration) was opened for public comment. Take your time to review it. The modules are being migrated into the [salt-extensions](https://github.com/salt-extensions) community org.
- **February 2024**: The [Great Module Purge PR](https://github.com/saltstack/salt/pull/65971) was created.
- **April 2024**: The Great Module Purge PR was merged, making 3008 the target release.

### Why This Change?

This drastic change is driven by several key goals:

1. **Streamline Maintenance**: Reducing the core Salt codebase makes it easier to maintain and improve.
2. **Deprecate Obsolete Modules**: Modules that are no longer relevant or maintained are bulk-deprecated.
3. **Decoupled Releases**: Separating modules from the core Salt release cycle allows for faster updates and better backporting. For extensions that are pure Python, only a single artifact will need to be released, rather than dozens per release.
4. **Efficient Salt Distributions**: Release platform-specific versions of Salt that are smaller and more efficient.
5. **Faster Development**: With fewer modules in the core, testing and review times will decrease, accelerating development.

### Categories of Modules

The migration splits modules into three categories:

1. **Core modules**: These will remain within the Salt codebase and follow the Salt release cycle.
2. **Supported modules (extended core)**: These modules will move to their own repositories within the `saltstack` GitHub organization, where they can be maintained separately.
(community-modules-target)=
3. **Community Modules**: These will be removed from the Salt Core codebase. Community members can take over their maintenance, either in the community-run Salt Extensions GitHub organization or in their own repositories.

### Why You Should Get Involved

In conclusion, this migration represents a shift in how Salt is maintained and developed. It opens the door for users and organizations to have a direct impact on the tools they rely on. If you use any of the modules categorized as community modules, their future depends on people like you. By becoming a maintainer or contributor, you can ensure that the modules you depend on continue to thrive and evolve.

(gh-org-ref)=
## GitHub organization

The [salt-extensions GitHub organization][saltext-org] was established to offer a community-driven, centralized hub for discovering, creating and maintaining Salt extensions. This organization aims to simplify the development and release process for both new extensions and modules extracted from Salt core starting with the `3008` release.

Do you care about a set of modules that will be removed from Salt core?
Do you want to publish awesome new Salt functionality?
[Getting involved](org-involve-target) is easy!

(copier-template-ref)=
## Copier template

The `salt-extension-copier` template simplifies the creation and maintenance of Salt extensions. Based on user inputs, it generates a custom boilerplate for anyone to develop new Salt functionality and allows for automated updates when new template versions are released.

Very important: You don't need to publish within the organization to use it – it works for individual projects too!


[saltext-org]: https://github.com/salt-extensions
