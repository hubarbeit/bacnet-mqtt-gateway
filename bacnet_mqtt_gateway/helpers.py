from pathlib import Path
from ruamel.yaml import YAML, version_info


def get_topic(register, message_type):
    topic = f"{register.device.gateway.discovery_prefix}/{register.component}/{register.device.id}/{register.id}/{message_type}"
    print("topic", topic)
    return topic


def load_yaml_with_includes(filepath):
    yaml = YAML(typ="safe", pure=True)
    yaml.default_flow_style = False

    def my_compose_document(self):
        self.parser.get_event()
        node = self.compose_node(None, None)
        self.parser.get_event()
        # self.anchors = {}    # <<<< commented out
        return node

    yaml.Composer.compose_document = my_compose_document

    # adapted from http://code.activestate.com/recipes/577613-yaml-include-support/
    def yaml_include(loader, node):
        y = loader.loader
        yaml = YAML(typ=y.typ, pure=y.pure)  # same values as including YAML
        yaml.composer.anchors = loader.composer.anchors
        return yaml.load(Path(node.value))

    yaml.Constructor.add_constructor("!include", yaml_include)

    return yaml.load(Path(filepath))
