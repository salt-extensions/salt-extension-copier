import copy
import sys
from pathlib import Path

import yaml
from copier_templates_extensions import ContextHook
from jinja2.ext import Extension

SINGULAR_LOADER_DIRS = (
    "auth",
    "cache",
    "fileserver",
    "metaproxy",
    "netapi",
    "output",
    "pillar",
    "pkgdb",
    "proxy",
    "roster",
    "sdb",
    "thorium",
    "wheel",
    "wrapper",
)


class SaltExt(ContextHook):
    """
    Renders some variables for easier templating
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sps = yaml.safe_load(
            (Path(__file__).parent.parent / "data" / "salt_python_support.yaml").read_text()
        )
        self.sps = {
            version: {"min": tuple(defs["min"]), "max": tuple(defs["max"])}
            for version, defs in sps.items()
        }
        self.slp = yaml.safe_load(
            (Path(__file__).parent.parent / "data" / "salt_latest_point.yaml").read_text()
        )

    def hook(self, context):
        if "python_requires" not in context:
            # This happens during pre-copy message rendering
            return {}
        return {
            "python_requires": tuple(int(x) for x in context["python_requires"].split(".")),
            "salt_python_support": copy.deepcopy(self.sps),
            "singular_loader_dirs": SINGULAR_LOADER_DIRS,
            "salt_latest_point": copy.deepcopy(self.slp),
            "copier_python": sys.executable,
        }


def represent_str(dumper, data):
    """
    Represent multiline strings using "|"
    """
    if len(data.splitlines()) > 1:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


class OpinionatedYamlDumper(yaml.SafeDumper):
    """
    Indent lists by two spaces
    """

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow=flow, indentless=False)


OpinionatedYamlDumper.add_representer(str, represent_str)


class YamlDumper(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters["yaml"] = self.dump_yaml

    def dump_yaml(self, data, flow_style=False, indent=0):
        return yaml.dump(
            data,
            Dumper=OpinionatedYamlDumper,
            indent=indent,
            default_flow_style=flow_style,
            canonical=False,
        )
