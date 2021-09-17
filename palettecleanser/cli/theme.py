from .. import theme
from .. import template
from .. import config
from .. import palette as pal
from typing import Optional, Any
from PIL import Image, UnidentifiedImageError

import typer
import subprocess
import sys
import os
import jinja2 as j2

app = typer.Typer(help=f'''manages your themes

saved themes can be found and manually edited at {config.themes_dir}''')


@app.command()
def show(name: str = typer.Argument(..., help='name of saved theme')):
    '''prints theme'''
    try:
        print(theme.from_config(name))
    except theme.ThemeNotFoundError:
        print(f"couldn't find '{name}' in saved themes", file=sys.stderr)
        print(f"check that '{name}.yml' exists in '{config.themes_dir}'", file=sys.stderr)
        raise typer.Exit(1)

@app.command()
def ls():
    '''lists saved themes'''
    for theme_file in os.listdir(config.themes_dir):
        print(os.path.splitext(theme_file)[0])


# TODO: add some sort of loading/processing text
# TODO: exception handling for template errors
@app.command(help=f'''evaluates jinja2 in managed templates and
saves them to their respective paths under {os.environ['HOME']}

if --template option is passed, only evaluates that specific template ''')
def deploy(
        name: str = typer.Argument(..., help='name of saved theme'),
        path: Optional[str] = typer.Option(None, '--template', metavar='PATH', help='path to configuration file relative to $HOME')
):
    try:
        t = theme.from_config(name)
    except theme.ThemeNotFoundError:
        print(f"couldn't find '{name}' in saved themes", file=sys.stderr)
        print(f"check that '{name}.yml' exists in '{config.themes_dir}'", file=sys.stderr)
        raise typer.Exit(1)

    try:
        if path:
            template.TemplateFile(path).template(t)
        else:
            template.template_managed(t)
    except j2.exceptions.TemplateNotFound:
        print(f"couldn't find '{path}' in saved templates", file=sys.stderr)
        print(f"check that '{config.themes_dir}/{path}.j2' exists", file=sys.stderr)


@app.command(help=f'''creates theme from a list of palettes, name, image path, and additional settings
and saves to {config.themes_dir} where it can be manually edited later''')
def create(
        palettes: list[str] = typer.Argument(..., help='space-delimited list of names of saved palettes'),
        name: str = typer.Option(..., metavar='NAME', help='name of theme'),
        image_path: str = typer.Option(..., metavar='PATH', help='path to background image'),
        setting: Optional[list[str]] = typer.Option(None, metavar='KEY=VALUE', help='additional settings to initialize new theme with')
):
    try:
        t = theme.Theme(name, palettes, image_path, {k: v for k, v in [single_setting.split('=') for single_setting in setting]})
        print(t)
    except pal.PaletteNotFoundError as e:
        print(e, file=sys.stderr)
        print(f"check that it exists in '{config.palettes_dir}'", file=sys.stderr)
        raise typer.Exit(1)

    t.save()
    print(f'"{name}" saved to {config.themes_dir}/{name}.yml')


def generate_from_image(
        image_path: str,
        name: str,
        settings: Optional[dict[str, Any]] = None,
        quantize_number: int = 64,
        algorithm: str = 'from_ordered_colors_match',
        **algorithm_parameters
):
    '''generates theme from image

    see palettecleanser.theme.from_image for more details
    '''
    if not settings:
        settings = {}

    try:
        with Image.open(image_path) as img:
            t = theme.from_image(img, name, settings, quantize_number, pal.generation_algorithms[algorithm], **algorithm_parameters)
    except FileNotFoundError:
        print(f"No such file or directory: '{image_path}'", file=sys.stderr)
        raise typer.Exit(1)
    except UnidentifiedImageError:
        print(f"'{image_path}' is not an image", file=sys.stderr)
        raise typer.Exit(1)

    print(t)
    t.save()


# TODO: --help type flag for available algorithms
@app.command(help=f'''generates a theme and saves to
{config.themes_dir} where it can be manually edited later''')
def generate(
        from_image: str = typer.Option('', metavar='PATH', help='generate theme from image at the specified path'),
        name: str = typer.Option(..., metavar='NAME', help=f'name of theme'),
        setting: Optional[list[str]] = typer.Option(None, metavar='KEY=VALUE', help='additional settings to initialize new theme with'),
        quantize_number: int = typer.Option(64, metavar='QUANTIZE_NUMBER', help='if generating from image, specifies the number of colors to quantize the image to and thus select colors from; --from-image option must be passed'),
        algorithm: str = typer.Option('from_ordered_colors_match', metavar='ALGORITHM', help='if generating from image, specifies thealgorithm to use for converting a list of colors to a palette;  --from-image option must be passed'),
        algorithm_parameter: Optional[list[str]] = typer.Option(None, metavar='KEY=VALUE', help='if generating from image, specifies keyword arguments which algorithm accepts in addition to a list of colors and name of palette; --algorithm option must be passed')
):
    if from_image:
        generate_from_image(
            from_image,
            name,
            {k: v for k, v in [single_setting.split('=') for single_setting in setting]},
            quantize_number,
            algorithm,
            **{k: v for k, v in [param.split('=') for param in algorithm_parameter]}
        )


@app.command()
def remove(name: str = typer.Argument(..., help='name of theme to remove from configuration')):
    '''removes a saved theme from configuration'''
    try:
        os.remove(os.path.join(config.themes_dir, f'{name}.yml'))
    except FileNotFoundError:
        print(f"couldn't find '{name}' in saved themes", file=sys.stderr)
        print(f"check that '{name}.yml' exists in '{config.themes_dir}'", file=sys.stderr)
        raise typer.Exit(1)

    print(f'"{name}" successfully removed from saved themes')


@app.command()
def edit(name: str = typer.Argument(..., help='name of theme to edit')):
    '''edit theme with $EDITOR'''
    try:
        editor = os.environ['EDITOR']
    except KeyError:
        editor = input('"$EDITOR" environment variable is not defined; please enter the text editor you would like to use: ')

    subprocess.run([editor, os.path.join(config.themes_dir, f'{name}.yml')])
