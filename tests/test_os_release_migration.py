"""
Unit tests for the `*_releases` answer migration logic.
"""

import pytest

from tasks.task_helpers.os_releases import default_releases
from tasks.task_helpers.os_releases import migrate_release_answer


@pytest.mark.parametrize(
    "answer,available,old_default,new_default,expected",
    (
        # The previous default was selected and has changed -> follow it
        (["15", "14"], ["16", "15"], ["15", "14"], ["16", "15"], ["16", "15"]),
        # Selection order should not matter for default detection
        (["14", "15"], ["16", "15"], ["15", "14"], ["16", "15"], ["16", "15"]),
        # The previous default was selected and is unchanged -> keep
        (["15", "14"], ["15", "14"], ["15", "14"], ["15", "14"], None),
        # A custom selection of offered releases -> keep
        (["14"], ["16", "15", "14"], ["15"], ["16"], None),
        # A custom selection containing an unsupported release -> drop it
        (["15", "13"], ["16", "15"], ["15", "14"], ["16"], ["15"]),
        # No selected release is offered anymore -> reset the answer
        (["13"], ["16", "15"], ["15", "14"], ["16"], ...),
        # Unknown previous default (e.g. shallow template clone) -> only
        # drop unsupported releases
        (["15", "14"], ["15"], None, ["15"], ["15"]),
        (["15"], ["16", "15"], None, ["16"], None),
    ),
)
def test_migrate_release_answer(answer, available, old_default, new_default, expected):
    assert migrate_release_answer(answer, available, old_default, new_default) == expected


@pytest.mark.parametrize(
    "path,expected",
    (
        (("FreeBSD",), ["15.2", "14.5"]),
        (("Linux", "distros", "Ubuntu"), ["24.04"]),
    ),
)
def test_default_releases(path, expected):
    os_support = {
        "Linux": {
            "distros": {
                "Ubuntu": {"runner": "github", "available": ["26.04", "24.04"]},
            },
        },
        "FreeBSD": {
            "vm": {"releases": ["15.2", "14.5"], "available": ["15.2", "15.1", "14.5", "14.4"]}
        },
    }
    assert default_releases(os_support, {"ubuntu": "24.04"}, path) == expected
