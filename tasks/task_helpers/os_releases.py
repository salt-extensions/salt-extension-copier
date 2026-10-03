"""
Shared logic regarding the OS releases offered by the ``*_releases``
questions, defined in ``data/os_support.yaml``.
"""

# Maps the `*_releases` questions to the path of the corresponding
# OS/distribution entry in data/os_support.yaml.
RELEASE_QUESTIONS = {
    "ubuntu_releases": ("Linux", "distros", "Ubuntu"),
    "debian_releases": ("Linux", "distros", "Debian"),
    "alpine_releases": ("Linux", "distros", "Alpine"),
    "almalinux_releases": ("Linux", "distros", "AlmaLinux"),
    "rockylinux_releases": ("Linux", "distros", "Rocky Linux"),
    "freebsd_releases": ("FreeBSD",),
    "openbsd_releases": ("OpenBSD",),
}


def release_meta(os_support, path):
    """
    Return the mapping carrying `available` (+ `releases`, unless the
    default is managed elsewhere) for an OS/distribution entry.

    os_support
        The parsed contents of data/os_support.yaml.

    path
        A RELEASE_QUESTIONS value.
    """
    entry = os_support
    for key in path:
        entry = entry[key]
    return entry.get("vm", entry)


def default_releases(os_support, versions, path):
    """
    Return the default release selection for an OS/distribution entry.

    versions
        The parsed contents of data/versions.yaml. Entries without a
        `releases` key (`runner: github`, i.e. Ubuntu) follow the
        Renovate-managed runner version defined there.
    """
    meta = release_meta(os_support, path)
    try:
        return list(meta["releases"])
    except KeyError:
        return [versions["ubuntu"]]


def migrate_release_answer(answer, available, old_default, new_default):
    """
    Adjust a `*_releases` answer to the currently offered releases.

    If the previous default selection was chosen, follow the current
    default. Otherwise, drop releases that are not offered anymore.

    Returns None if the answer should be kept, Ellipsis if it should be
    reset (reproposing the default) or the adjusted answer.

    answer
        The current answer to the `*_releases` question.

    available
        The currently selectable releases.

    old_default
        The default selection of the previous template version, if known.

    new_default
        The current default selection.
    """
    if old_default is not None and set(answer) == set(old_default):
        if set(answer) != set(new_default):
            return list(new_default)
        return None
    filtered = [release for release in answer if release in available]
    if filtered == list(answer):
        return None
    return filtered or ...
