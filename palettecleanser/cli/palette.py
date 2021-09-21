from .. import palette as pal
from .. import config
from typing import Optional, Any

import typer
import subprocess
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
    try:
        p = pal.Palette([pal.from_hex(color) for color in colors], name)
    except pal.MalformedHexError as e:
        print(e, file=sys.stderr)
        raise typer.Exit(1)

    print(p)

    if name:
        p.save()
        print(f'"{name}" saved to {config.palettes_dir}/{name}.yml')



def generate_from_image(
        image_path: str,
        name: Optional[str] = None,
        light: bool = False,
        backend: str = 'wal',
        saturate_percent: Optional[float] = None
):
    '''generates palette from image

    see palettecleanser.palette.from_image for more details
    '''
    try:
        p = pal.from_image(image_path, name, light, backend, saturate_percent)
    except:
        print(f"'{image_path}' either couldn't be found or isn't an image", file=sys.stderr)
        raise typer.Exit(1)

    print(p)
    if name:
        p.save()
        print(f'"{name}" saved to {config.palettes_dir}/{name}.yml')


# TODO: --help type flag for available algorithms
@app.command(help=f'''generates a palette

if --name option is passed, saves palette to {config.palettes_dir}
where it can be manually edited later''')
def generate(
        from_image: str = typer.Option('', metavar='PATH', help='generate palette from image at the specified path'),
        name: Optional[str] = typer.Option(None, metavar='NAME', help=f'saves the palette to "{config.palettes_dir}" with specified name'),
        light: bool = typer.Option(False, help='generate a light color palette'),
        backend: str = typer.Option('wal', metavar='BACKEND', help='pywal backend to use for image-to-palette algorithm; --from-image must be passed'),
        saturate_percent: Optional[float] = typer.Option(None, metavar='PERCENTAGE', help=f'amount to saturate colors by (5 means 5%)')
):
    if from_image:
        generate_from_image(
            from_image,
            name,
            light,
            backend,
            saturate_percent
        )



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


@app.command()
def edit(name: str = typer.Argument(..., help='name of palette to edit')):
    '''edit palette with $EDITOR'''
    try:
        editor = os.environ['EDITOR']
    except KeyError:
        editor = input('"$EDITOR" environment variable is not defined; please enter the text editor you would like to use: ')

    subprocess.run([editor, os.path.join(config.palettes_dir, f'{name}.yml')])
