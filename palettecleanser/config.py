import os
import yaml
from typing import Any

try:
    config_root = os.environ['XDG_CONFIG_HOME']
except KeyError:
    config_root = os.path.join(os.environ['HOME'], '.config')

config_dir = os.path.join(config_root, 'palette-cleanser')
palettes_dir = os.path.join(config_dir, 'palettes')
themes_dir = os.path.join(config_dir, 'themes')
templates_dir = os.path.join(config_dir, 'templates')

def get_config_settings() -> dict[str, Any]:
    ''' load config settings from $XDG_CONFIG_HOME/palette-cleanser/config.yml '''
    with open(os.path.join(config_dir, 'config.yml')) as config_settings:
        return yaml.load(config_settings, Loader=yaml.Loader)
