from datetime import datetime

import yaml
from copier_templates_extensions import ContextHook
from jinja2.ext import Extension


class Year(ContextHook):
    """
    Provide the current year
    """

    def hook(self, context):
        return {"copyright_year": datetime.now().year}


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
