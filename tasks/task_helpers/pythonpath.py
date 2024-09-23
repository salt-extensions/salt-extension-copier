import sys
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def prepend_path(path):
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        try:
            sys.path.remove(str(path))
        except ValueError:
            pass


@contextmanager
def project_tools():
    tools_path = Path(__file__).parent.parent.parent / "project/tools"
    with prepend_path(tools_path):
        yield
