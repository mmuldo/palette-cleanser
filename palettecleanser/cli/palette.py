from .. import palette as pal
from .. import config
from typing import Optional, Any
from PIL import Image, UnidentifiedImageError

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
        quantize_number: int = 64,
        algorithm: str = 'from_ordered_colors_match',
        **algorithm_parameters
):
    '''generates palette from image

    see palettecleanser.palette.from_image for more details
    '''
    try:
        with Image.open(image_path) as img:
            p = pal.from_image(img, name, quantize_number, pal.generation_algorithms[algorithm], **algorithm_parameters)
    except FileNotFoundError:
        print(f"No such file or directory: '{image_path}'", file=sys.stderr)
        raise typer.Exit(1)
    except UnidentifiedImageError:
        print(f"'{image_path}' is not an image", file=sys.stderr)
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
        quantize_number: int = typer.Option(64, metavar='QUANTIZE_NUMBER', help='if generating from image, specifies the number of colors to quantize the image to and thus select colors from; --from-image option must be passed'),
        algorithm: str = typer.Option('from_ordered_colors_match', metavar='ALGORITHM', help='if generating from image, specifies thealgorithm to use for converting a list of colors to a palette;  --from-image option must be passed'),
        algorithm_parameter: Optional[list[str]] = typer.Option(None, metavar='KEY=VALUE', help='if generating from image, specifies keyword arguments which algorithm accepts in addition to a list of colors and name of palette; --algorithm option must be passed')
):
    if from_image:
        generate_from_image(
            from_image,
            name,
            quantize_number,
            algorithm,
            **{k: v for k, v in [param.split('=') for param in algorithm_parameter]}
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
