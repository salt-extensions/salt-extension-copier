from collections import ChainMap
from pathlib import Path

import yaml
from pytest_copie.plugin import _add_yaml_include_constructor


def load_copier_yaml(template_dir: Path | None = None) -> ChainMap:
    template_dir = template_dir or Path(".")
    files = template_dir.glob("copier.*")
    try:
        copier_yaml = next(f for f in files if f.suffix in [".yaml", ".yml"])
    except StopIteration as err:
        raise FileNotFoundError("No copier.yaml configuration file found.") from err
    _add_yaml_include_constructor(template_dir)
    return ChainMap(*list(yaml.safe_load_all(copier_yaml.read_text())))
