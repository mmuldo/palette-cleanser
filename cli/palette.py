from palettecleanser import palette as pal
from palettecleanser import config
from typing import Optional
from PIL import Image, UnidentifiedImageError

import typer
import sys
import os

app = typer.Typer(help=f'''manages your palettes

saved palettes can be found and manually edited at {config.palettes_dir}''')


@app.command()
def show(name: str = typer.Argument(..., help='name of saved palette')):
    '''prints palette'''
    try:
        print(pal.from_config(name))
    except pal.PaletteNotFoundError:
        print(f"couldn't find '{name}' in saved palettes", file=sys.stderr)
        print(f"check that '{name}.yml' exists in '{config.palettes_dir}'", file=sys.stderr)
        raise typer.Exit(1)


@app.command()
def ls():
    '''lists saved palettes'''
    for palette_file in os.listdir(config.palettes_dir):
        print(os.path.splitext(palette_file)[0])


@app.command(help=f'''creates palette from list of colors

if --name option is passed, saves palette to {config.palettes_dir}
where it can be manually edited later''')
def create(
        colors: list[str] = typer.Argument(..., help='space delimited list of "#rrggbb" formatted colors'),
        name: Optional[str] = typer.Option(None, metavar='NAME', help=f'saves the palette to "{config.palettes_dir}" with specified name')
):
    p = pal.Palette([pal.from_hex(color) for color in colors], name)
    print(p)

    if name:
        p.save()


# TODO: add other arguments for pal.from_image
def generate_from_image(image_path: str, name: Optional[str] = None):
    '''generates palette from image'''
    try:
        with Image.open(image_path) as img:
            p = pal.from_image(img, name)
    except FileNotFoundError:
        print(f"No such file or directory: '{image_path}'", file=sys.stderr)
        raise typer.Exit(1)
    except UnidentifiedImageError:
        print(f"'{image_path}' is not an image", file=sys.stderr)
        raise typer.Exit(1)

    print(p)
    if name:
        p.save()


@app.command(help=f'''generates a palette

if --name option is passed, saves palette to {config.palettes_dir}
where it can be manually edited later''')
def generate(
        from_image: str = typer.Option('', metavar='PATH', help='generate palette from image at the specified path'),
        name: Optional[str] = typer.Option(None, metavar='NAME', help=f'saves the palette to "{config.palettes_dir}" with specified name')
):
    if from_image:
        generate_from_image(from_image, name)


@app.command()
def remove(name: str = typer.Argument(..., help='name of palette to remove from configuration')):
    '''removes a saved palette from configuration'''
    try:
        os.remove(os.path.join(config.palettes_dir, f'{name}.yml'))
    except FileNotFoundError:
        print(f"couldn't find '{name}' in saved palettes", file=sys.stderr)
        print(f"check that '{name}.yml' exists in '{config.palettes_dir}'", file=sys.stderr)
        raise typer.Exit(1)

    print(f'"{name}" successfully removed from saved palettes')
