import os
import yaml

from . import palette as pal
from . import config

from tabulate import tabulate
from collections import defaultdict
from dataclasses import dataclass
from PIL import Image
from functools import reduce
from typing import Any

### EXCEPTIONS ###
class ThemeNotFoundError(Exception):
    pass

### CLASSES ###
@dataclass
class Theme:
    '''
    represents a configuration theme

    Attributes
    ----------
    name : str
        name of theme
    palettes : list[str]
        list of names of saved palettes
    image_path : str
        path to image that will be associated with the theme (e.g. to serve as the
        background wallpaper for the desktop)
    settings : dict[str, Any], optional
        additional settings accessible to templates under the "settings" dictionary (default is {})

    Methods
    -------
    save()
        saves theme to local palette-cleanser configuration
    '''
    name: str
    palettes: list[str]
    image_path: str
    settings: dict[str, Any]

    def __init__(self, name: str, palettes: list[str], image_path: str, settings: dict[str, Any] = {}):
        self.name = name
        self.palettes = palettes
        self.image_path = image_path
        self.settings = settings

    def save(self):
        '''saves Theme to yml file at $XDG_CONFIG_HOME/palette-cleanser/themes/

        defaults to ~/.config/palette-cleanser/themes/
        '''
        if not os.path.exists(config.themes_dir):
            os.makedirs(config.themes_dir)

        path = os.path.join(config.themes_dir, f'{self.name}.yml')

        if os.path.exists(path) and input(f'a theme for {self.name} already exists; overwrite? [y/N] ') not in ['y', 'Y', 'yes' 'Yes']:
            return

        with open(path, 'w') as f:
            yaml.dump(self, f)

    def table(self) -> dict[str, list[pal.Color]]:
        '''converts palette to data that can be tabulated

        Returns
        -------
        dict[str, list[palette.Color]]
            set of columns where the headers are names of palattes and cells are colors
        '''
        palettes = [pal.from_config(p) for p in self.palettes]
        return {p.name: p.colors for p in palettes}

    def __str__(self):
        return tabulate(self.table(), headers='keys')

### FUNCTIONS ###
def from_image(img: Image,
               name: str,
               settings: dict[str, Any] = {},
               base_palette: pal.Palette = pal.ansi_normal_palette,
               quantize_number: int = 64) -> Theme:
    '''generates a theme from an image

    The generated theme consists of three palettes: a palette generated from
    provided image, a darker version of this palette, and a lighter version of
    this palette. The image provided is used as the associated image for the theme.

    Parameters
    ----------
    img : Image
        image with which to generate the palettes for the theme; it also
        serves as the associated image for the theme
    name : str
        name of theme
    settings : dict[str, Any], optional
        additional settings to initialize new theme with (default is {})
    base_palette : palette.Palette, optional
        Palette to base the new palette off of. The default is palette.ansi_normal_palette (the 8 ansi
        normal colors), so in the default case this function will iterate through each of these colors
        and select the color from the quantized image that is most similar to add to the new palette.
    quantize_number : int, optional
        number of colors to quantize the image to and thus select colors from (default is 64)

    Returns
    -------
    Theme
        new theme based off of provided image
    '''
    main_palette = pal.from_image(img, name, base_palette, quantize_number)
    dark_palette = main_palette.tone(35, False, name + "-dark")
    light_palette = main_palette.tone(35, True, name + "-light")
    for p in [main_palette, dark_palette, light_palette]:
        p.save()

    return Theme(name, [name + tail for tail in ["", "-dark", "-light"]], img.filename, settings)

def from_config(name: str) -> Theme:
    '''pulls existing theme from config

    Parameters
    ----------
    name : str
        name of theme

    Returns
    -------
    Theme
        the theme as it exists in config

    Raises
    ------
    ThemeNotFoundError
        if the theme doesn't exist
    '''
    try:
        with open(os.path.join(config.themes_dir, f'{name}.yml')) as f:
            return yaml.load(f, Loader=yaml.Loader)
    except FileNotFoundError:
        raise ThemeNotFoundError(f'{name} theme doesn\'t exist')
