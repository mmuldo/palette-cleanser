import os

try:
    config_root = os.environ['XDG_CONFIG_HOME']
except KeyError:
    config_root = os.path.join(os.environ['HOME'], '.config')

config_dir = os.path.join(config_root, 'palette-cleanser')
palettes_dir = os.path.join(config_dir, 'palettes')
themes_dir = os.path.join(config_dir, 'themes')
templates_dir = os.path.join(config_dir, 'templates')
