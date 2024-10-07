from pathlib import Path

import copier.template
import yaml

TEMPLATE_ROOT = (Path(__file__).parent.parent.parent).resolve()


def load_copier_conf():
    """
    Load the complete Copier configuration.
    """
    return copier.template.load_template_config(TEMPLATE_ROOT / "copier.yml")


def load_data_yaml(name):
    """
    Load a file in the template root `data` directory.
    """
    file = (TEMPLATE_ROOT / "data" / name).with_suffix(".yaml")
    if not file.exists():
        raise OSError(f"The file '{file}' does not exist")
    with open(file, encoding="utf-8") as f:
        return yaml.safe_load(f)
