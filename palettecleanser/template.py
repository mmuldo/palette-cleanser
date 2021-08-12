import jinja2 as j2
import yaml
import os
import shutil

from palette import Palette

templated_signature = '@palette-cleanser'

try:
    configs_root = os.environ['XDG_CONFIG_HOME']
except KeyError:
    configs_root = os.environ['HOME'] +  '/.config'
templates_dir = '/'.join([configs_root, 'palette-cleanser', 'templates'])
settings = '/'.join([configs_root, 'palette-cleanser', 'config.yaml'])

env = j2.Environment(loader=j2.FileSystemLoader(templates_dir))


def generate_signature(file_extension: str) -> str:
    start, end = {
        '.yml': ('#', '')
    }[file_extension]

    return start + templated_signature + end + '\n'

def is_templated(path: str) -> bool:
    try:
        with open('/'.join([configs_root, path]), 'r') as f:
            return templated_signature in f.readline()
    except FileNotFoundError:
        return True

def template_file(path: str, palette: Palette):
    template = env.get_template(path)
    output = template.render(vars(palette))

    if not is_templated(path):
        shutil.move('/'.join([configs_root, path]), '/'.join([configs_root, path + '.backup']))

    with open('/'.join([configs_root, path]), 'w') as out_file:
        out_file.write(generate_signature(os.path.splitext(path)) + output)


def template_managed_files(palette: Palette):
    for path in settings['managed_files']:
        template_file(path, palette)
