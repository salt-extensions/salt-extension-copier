import pytest


@pytest.fixture(scope="module")
def grains(loaders):
    return loaders.grains
