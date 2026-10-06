#!/usr/bin/env python3
"""
Update the prek CI container pins after a container (re)build.

Rewrites the line following each ``# prek-ci-container`` marker:

  * ``.github/workflows/pre-commit-action.yml``: the ``image:`` pin of
    this repo's own pre-commit job (full Python version tag).
  * ``data/versions.yaml``: the ``prek_container`` pin rendered into
    generated projects (minor Python version tag).

The Python version is read from ``containers/prek.Dockerfile``; the
image digest must be passed as the only argument. Intended to be run by
the ``build-prek-container`` workflow, which submits the result as a PR.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGE = "ghcr.io/salt-extensions/prek-ci"
MARKER = "# prek-ci-container"


def read_python_version():
    dockerfile = REPO_ROOT / "containers" / "prek.Dockerfile"
    match = re.search(r"^ARG PYTHON_VERSION=(\S+)$", dockerfile.read_text(), flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Failed to parse PYTHON_VERSION from {dockerfile}")
    return match.group(1)


def replace_after_marker(path, replacement):
    lines = path.read_text().splitlines()
    marker_indices = [i for i, line in enumerate(lines) if line.strip() == MARKER]
    if len(marker_indices) != 1:
        raise RuntimeError(
            f"Expected exactly one {MARKER!r} line in {path}, found {len(marker_indices)}"
        )
    pin_index = marker_indices[0] + 1
    if pin_index >= len(lines):
        raise RuntimeError(f"No line follows {MARKER!r} in {path}")
    indent = lines[marker_indices[0]][: -len(MARKER)]
    lines[pin_index] = indent + replacement
    path.write_text("\n".join(lines) + "\n")


def main():
    try:
        digest = sys.argv[1]
    except IndexError:
        sys.exit(f"usage: {sys.argv[0]} <image digest>")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        sys.exit(f"Invalid image digest: {digest!r}")

    version = read_python_version()
    replace_after_marker(
        REPO_ROOT / ".github" / "workflows" / "pre-commit-action.yml",
        f"image: {IMAGE}:{version}@{digest}",
    )
    replace_after_marker(
        REPO_ROOT / "data" / "versions.yaml",
        f"prek_container: '{IMAGE}:{version}@{digest}'",
    )


if __name__ == "__main__":
    main()
