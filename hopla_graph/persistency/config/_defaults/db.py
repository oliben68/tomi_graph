import os
import yaml

_current_dir = os.path.dirname(os.path.realpath(__file__))
_yaml_file = os.path.join(_current_dir, os.path.splitext(__file__)[0] + ".yml")


DB_CONFIG = {}

if os.path.isfile(_yaml_file):
    with open(_yaml_file, "r") as db_config:
        DB_CONFIG = yaml.load(db_config)
