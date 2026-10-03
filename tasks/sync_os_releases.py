#!/usr/bin/env -S uv run --no-project --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "ruamel.yaml>=0.18,<0.19",
# ]
# ///
"""
Sync the OS releases offered by the ``*_releases`` questions.

For each OS/distribution tested in CI, this script updates in
``data/os_support.yaml``:

  * ``available``: all releases that are both still supported upstream
    (according to https://endoflife.date) and offered in CI. For
    VM-based platforms, this means the respective vmactions action
    offers it (a ``<release>.conf`` exists in the action repo's
    ``conf`` directory); for Ubuntu, a GitHub-hosted runner image
    exists (https://github.com/actions/runner-images).
  * ``releases``: the default selection, the newest ``default_count``
    entries of ``available``, split across available majors.
    Not synced for Ubuntu, whose default follows the Renovate-managed
    runner version in ``data/versions.yaml`` instead.

Intended to be run by the scheduled ``sync-os-releases`` workflow, which
submits the result as a PR. Pass ``--check`` to exit with status 2
instead of writing changes (for manual verification).
"""

import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ruamel.yaml import YAML  # pylint: disable=import-error
from ruamel.yaml.scalarstring import DoubleQuotedScalarString  # pylint: disable=import-error

OS_SUPPORT_FILE = Path(__file__).parent.parent / "data" / "os_support.yaml"


@dataclass(frozen=True)
class SyncSpec:
    """
    Describes how to sync a single OS/distribution.
    """

    # Product slug on https://endoflife.date
    eol_product: str
    # The vmactions repository is named f"{vm_repo}-vm".
    # If unset, the releases offered as GitHub-hosted runner images
    # are discovered instead.
    vm_repo: str | None = None
    # Only consider major.minor release cycles (e.g. FreeBSD lists both
    # stable branches like "14" and point release cycles like "14.3")
    exclude_majors: bool = False
    # How many of the newest available releases to test by default.
    # If unset, the default selection (`releases`) is not synced.
    default_count: int | None = 1


# Keys are the OS/distro names used in data/os_support.yaml.
# Each entry containing a `vm` or `runner` key must be listed here.
SYNC_SPECS = {
    # Ubuntu's default release follows the Renovate-managed runner
    # version in data/versions.yaml instead.
    "Ubuntu": SyncSpec(eol_product="ubuntu", default_count=None),
    "Debian": SyncSpec(eol_product="debian", vm_repo="debian"),
    "Alpine": SyncSpec(eol_product="alpine", vm_repo="alpine"),
    "AlmaLinux": SyncSpec(eol_product="almalinux", vm_repo="almalinux"),
    "Rocky Linux": SyncSpec(eol_product="rocky-linux", vm_repo="rockylinux"),
    "FreeBSD": SyncSpec(
        eol_product="freebsd", vm_repo="freebsd", exclude_majors=True, default_count=2
    ),
    "OpenBSD": SyncSpec(eol_product="openbsd", vm_repo="openbsd"),
}


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def fetch_supported_cycles(spec):
    """
    List currently supported release cycles, newest first.
    """
    today = date.today().isoformat()
    cycles = []
    for entry in _get(f"https://endoflife.date/api/{spec.eol_product}.json"):
        cycle = str(entry["cycle"])
        if spec.exclude_majors and "." not in cycle:
            continue
        released = entry.get("releaseDate")
        if not released or released > today:
            continue
        eol = entry.get("eol")
        # `eol` is either a date string or a boolean (true meaning EOL,
        # false meaning no EOL date announced yet).
        if eol is True or (isinstance(eol, str) and eol <= today):
            continue
        cycles.append(cycle)
    return sorted(cycles, key=lambda c: tuple(map(int, c.split("."))), reverse=True)


def _get_github(url):
    headers = {"Accept": "application/vnd.github+json"}
    if token := (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")):
        headers["Authorization"] = f"Bearer {token}"
    return _get(url, headers=headers)


def fetch_offered_releases(spec):
    """
    List the x86_64 releases offered in CI, either by the OS' vmactions
    action or as GitHub-hosted runner images (Ubuntu).
    """
    releases = set()
    if spec.vm_repo is None:
        images = _get_github(
            "https://api.github.com/repos/actions/runner-images/contents/images/ubuntu"
        )
        for entry in images:
            # x86_64 image docs are named e.g. `Ubuntu2404-Readme.md`.
            if match := re.fullmatch(r"Ubuntu(\d{2})(\d{2})-Readme\.md", entry["name"]):
                releases.add(".".join(match.groups()))
        return releases
    conf = _get_github(f"https://api.github.com/repos/vmactions/{spec.vm_repo}-vm/contents/conf")
    for entry in conf:
        name = entry["name"]
        # Arch-specific variants carry a suffix, e.g. `13-aarch64.conf`.
        if name == "default.release.conf" or not name.endswith(".conf") or "-" in name:
            continue
        releases.add(name.removesuffix(".conf"))
    return releases


def select_default_releases(available, count):
    """
    Select the default releases from the available ones (sorted newest
    first): the newest cycle of each release train first (newest train
    first), then older cycles.
    """
    trains = {}
    for cycle in available:
        trains.setdefault(cycle.split(".")[0], []).append(cycle)
    picks = []
    for rank in range(max(map(len, trains.values()))):
        picks.extend(cycles[rank] for cycles in trains.values() if rank < len(cycles))
    return picks[:count]


def sync_entry(name, entry_data):
    """
    Sync a single OS/distribution mapping in place. Returns a
    description of the changes, if any.
    """
    spec = SYNC_SPECS.get(name)
    if spec is None:
        raise RuntimeError(
            f"Missing sync configuration for '{name}'. Please add it to SYNC_SPECS "
            f"in {Path(__file__).name}."
        )
    supported = fetch_supported_cycles(spec)
    offered = fetch_offered_releases(spec)
    # A release cycle is available if CI offers it exactly or offers a
    # point release of it ("15" matches "15.1.conf").
    available = [
        cycle
        for cycle in supported
        if cycle in offered or any(rel.startswith(f"{cycle}.") for rel in offered)
    ]
    if not available:
        raise RuntimeError(
            f"No available releases found for '{name}'. "
            f"Supported: {supported}, offered in CI: {sorted(offered)}"
        )
    updates = [("available", available)]
    if spec.default_count is not None:
        updates.append(("releases", select_default_releases(available, spec.default_count)))
    changes = []
    for key, new in updates:
        if list(entry_data.get(key, ())) != new:
            changes.append(f"{key}: {list(entry_data.get(key, ()))} -> {new}")
            entry_data[key] = [DoubleQuotedScalarString(rel) for rel in new]
    return changes


def main():
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    data = yaml.load(OS_SUPPORT_FILE)

    candidates = dict(data) | dict(data.get("Linux", {}).get("distros", {}))
    entries = {
        name: meta.get("vm", meta)
        for name, meta in candidates.items()
        if "vm" in meta or "runner" in meta
    }
    changed = False
    for name, vm_data in entries.items():
        for change in sync_entry(name, vm_data):
            changed = True
            print(f"{name}: {change}")

    if not changed:
        print("All OS releases are up to date.")
        return 0
    if "--check" in sys.argv[1:]:
        return 2
    yaml.dump(data, OS_SUPPORT_FILE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
