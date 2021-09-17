from .. import config
from .. import template

import typer
import sys
import os
import subprocess

app = typer.Typer(help=f'''manages your templates

saved themes can be found and manually edited at {config.templates_dir}''')

@app.command(help=f'''creates a template based on a current configuration file

the generated template is comprised of default settings (required just to get the given
application working), the settings from the current configuration file, and
overwrite settings (mostly template expressions for the given application's
color schemes); in other words, the current configuration file will take
precedence over the default settings and the overwrite settings will take
precedence over the current configuration file.''')
def create(path: str = typer.Argument(..., help='path to configuration file relative to $HOME')):
    template.TemplateFile(path).create()
    print(f'"{config.templates_dir}/{path}.j2" template successfully created')


@app.command(help=f''' removes a template from palette-cleanser configuration

this will not remove the actual config file that exists under $HOME, just
the template file from {config.templates_dir}
''')
def remove(path: str = typer.Argument(..., help='path to configuration file relative to $HOME')):
    try:
        os.remove(os.path.join(config.templates_dir, f'{path}.j2'))
    except FileNotFoundError:
        print(f"couldn't find '{path}' in saved templates", file=sys.stderr)
        print(f"check that '{config.templates_dir}/{path}.j2' exists", file=sys.stderr)
        raise typer.Exit(1)

    print(f'"{path}" successfully removed from saved templates')


@app.command()
def edit(path: str = typer.Argument(..., help='path to configuration file relative to $HOME')):
    '''edit template with $EDITOR'''
    try:
        editor = os.environ['EDITOR']
    except KeyError:
        editor = input('"$EDITOR" environment variable is not defined; please enter the text editor you would like to use: ')

    subprocess.run([editor, os.path.join(config.templates_dir, f'{path}.j2')])
