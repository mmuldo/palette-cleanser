from palettecleanser import theme
from palettecleanser import template
from palettecleanser import config
from typing import Optional
from PIL import Image, UnidentifiedImageError

import typer
import sys
import os

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


# TODO: add support for specific templates
# TODO: add some sort of loading/processing text
@app.command(help=f'''evaluates jinja2 in managed templates and
saves them to their respective paths under {os.environ['HOME']}''')
def deploy(
        name: str = typer.Argument(..., help='name of saved theme')
):
    try:
        t = theme.from_config(name)
    except theme.ThemeNotFoundError:
        print(f"couldn't find '{name}' in saved themes", file=sys.stderr)
        print(f"check that '{name}.yml' exists in '{config.themes_dir}'", file=sys.stderr)
        raise typer.Exit(1)

    template.template_managed(t)


# TODO: add settings argument
@app.command(help=f'''creates theme from a list of palettes, name, image path, and additional settings
and saves to {config.themes_dir} where it can be manually edited later''')
def create(
        palettes: list[str] = typer.Argument(..., help='space-delimited list of names of saved palettes'),
        name: str = typer.Option(..., metavar='NAME', help='name of theme'),
        image_path: str = typer.Option(..., metavar='PATH', help='path to background image'),
):
    t = theme.Theme(name, palettes, image_path)
    print(t)
    t.save()

# TODO: add other arguments for theme.from_image
def generate_from_image(image_path: str, name: str):
    '''generates theme from image'''
    try:
        with Image.open(image_path) as img:
            t = theme.from_image(img, name)
    except FileNotFoundError:
        print(f"No such file or directory: '{image_path}'", file=sys.stderr)
        raise typer.Exit(1)
    except UnidentifiedImageError:
        print(f"'{image_path}' is not an image", file=sys.stderr)
        raise typer.Exit(1)

    print(t)
    t.save()


@app.command(help=f'''generates a theme and saves to
{config.themes_dir} where it can be manually edited later''')
def generate(
        from_image: str = typer.Option('', metavar='PATH', help='generate theme from image at the specified path'),
        name: Optional[str] = typer.Option(None, metavar='NAME', help=f'name of theme')
):
    '''generates a theme'''
    if from_image:
        generate_from_image(from_image, name)


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
