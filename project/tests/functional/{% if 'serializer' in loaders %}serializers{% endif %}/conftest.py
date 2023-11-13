import pytest


@pytest.fixture(scope="module")
def serializers(loaders):
    return loaders.serializers
