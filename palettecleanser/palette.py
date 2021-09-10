from __future__ import annotations

import yaml
import numpy as np
import os

from tabulate import tabulate
from PIL import Image
from dataclasses import dataclass
from functools import reduce
from typing import Optional, Callable

from . import config

### EXCEPTIONS ###
class MalformedHexError(Exception):
    pass

class PaletteNotFoundError(Exception):
    pass

### CLASSES ###
@dataclass
class Color:
    '''
    represents an rgb color

    Attributes
    ----------
    red : int
        red component
    green : int
        green component
    blue : int
        blue component

    Methods
    -------
    distance(color)
        computes distance to another Color
    closest(colors)
        finds the most similar element out of a list of colors
    tone(percent, lighten)
        lightens/darkens current object by specified percent
    spectrum(color, n)
        generates a spectrum from the current object to given color with n increments
    hex()
        calculates hex code
    '''
    red: int
    green: int
    blue: int

    def distance(self, color: Color) -> float:
        '''computes distance to another Color

        uses distance formula between two 3D points for computation

        Parameters
        ----------
        color : Color
            color to compute distance to

        Returns
        -------
        float
            the computed distance
        '''
        return ((self.red - color.red)**2 + (self.green - color.green)**2 + (self.blue - color.blue)**2)**.5

    def closest(self, colors: list[Color]) -> int:
        '''out of a list of colors, finds the one that is most similar to the current object

        "most similar" is defined by distance on a 3D coordinate plane (where
        the coordinates are the red, green, and blue components of the color)

        Parameters
        ----------
        colors : list[Color]
            list of Colors to compare to the current object

        Returns
        -------
        int
            index of Color in list that is most similar to the current object
        '''
        return np.argmin([self.distance(color) for color in colors])

    def tone(self, percent: float, lighten: bool) -> Color:
        '''lightens/darkens current Color object by specified percent

        Parameters
        ----------
        percent : float
            amount to lighten/darken by (percent=5 means 5%)
        lighten : bool
            lightens color if True, darkens if False

        Returns
        -------
        Color
            toned color
        '''
        rgb = tuple(int(((255 if lighten else 0) - coordinate) * (percent / 100)) + coordinate for coordinate in vars(self).values())
        return Color(*rgb)

    def spectrum(self, color: Color, n: int) -> list[Color]:
        '''generates a spectrum (list of Colors) from current object to provided color with n increments

        Parameters
        ----------
        color : Color
            other endpoint of spectrum
        n : int
            number of elements in the generated spectrum

        Returns
        -------
        list[Color]
            a spectrum of Colors of length n spanning the current object to the Color object provided
        '''
        # equations for the 3D line that self and color lie on
        r = lambda t: round(self.red + (color.red - self.red) * t)
        g = lambda t: round(self.green + (color.green - self.green) * t)
        b = lambda t: round(self.blue + (color.blue - self.blue) * t)

        return [Color(r(t), g(t), b(t)) for t in np.linspace(0, 1, n)]

    def __str__(self) -> str:
        '''calculates hex code

        Returns
        -------
        str
            hex code formatted as "#RRGGBB"
        '''
        return '#' + '%0.2x' * 3 % (self.red, self.green, self.blue)

    def show(self):
        '''hex code where the background color is that represented by the current object'''
        start = ';'.join(['\x1b[48', '2', str(self.red), str(self.green), str(self.blue) + 'm'])
        end = '\x1b[0m'
        return start + str(self) + end

@dataclass
class Palette:
    '''
    represents a palette of rgb colors

    Attributes
    ----------
    colors : list[Color]
        base colors of palette
    name : str, optional
        name of palette (default is None)

    Methods
    -------
    tone(percent, lighten, name=None)
        lightens/darkens every color in palette by specified percent
    save()
        saves palette to local palette-cleanser configuration
    table()
        converts palette to data that can be tabulated
    '''
    colors: list[Color]
    name: Optional[str] = None

    def tone(self, percent: float, lighten: bool, name: str = None) -> Palette:
        '''lightens/darkens every color in palette by specified percent

        Parameters
        ----------
        percent : float
            amount to lighten/darken by (percent=5 means 5%)
        lighten : bool
            lightens colors if True, darkens if False
        name : str, optional
            name of the new palette (default is None)

        Returns
        -------
        Palette
            toned palette
        '''
        return Palette([color.tone(percent, lighten) for color in self.colors], name)

    def save(self):
        '''saves Palette to yml file at $XDG_CONFIG_HOME/palette-cleanser/palettes/

        defaults to ~/.config/palette-cleanser/palettes/
        '''
        while not self.name:
            self.name = input("must define palette's name in order to save: ")

        if not os.path.exists(config.palettes_dir):
            os.makedirs(config.palettes_dir)

        path = os.path.join(config.palettes_dir, f'{self.name}.yml')

        if os.path.exists(path) and input(f'a palette for {self.name} already exists; overwrite? [y/N] ') not in ['y', 'Y', 'yes' 'Yes']:
            return

        with open(path, 'w') as f:
            yaml.dump(self, f)


    def table(self) -> dict[str, list[Colors]]:
        '''converts palette to data that can be tabulated

        Returns
        -------
        dict[str, list[Colors]]
            single column where the header is the name of the palatte and the data are the colors
        '''
        return {self.name: [color.show() for color in self.colors]}

    def __str__(self):
        return tabulate(self.table(), headers='keys')


### GLOBAL VARS AND OBJECTS ###
ansi_normal_palette = Palette(
    [
        Color(0,     0,      0),    # black
        Color(170,   0,      0),    # red
        Color(0,     170,    0),    # green
        Color(170,   170,    0),    # yellow
        Color(0,     0,      170),  # blue
        Color(170,   0,      170),  # purple
        Color(0,     170,    170),  # cyan
        Color(170,   170,    170)   # white
    ],
    'ansi-normal'
)

axarva_palette = Palette(
    [
        Color(33,   33,     33),    # black
        Color(240,  113,    120),   # red
        Color(195,  232,    141),   # green
        Color(255,  203,    107),   # yellow
        Color(130,  170,    255),   # blue
        Color(199,  146,    234),   # purple
        Color(137,  221,    255),   # cyan
        Color(238,  255,    255),   # white
    ],
    'axarva'
)



### FUNCTIONS ###
def from_hex(hexcode: str) -> Color:
    '''generates Color from hexcode

    Parameters
    ----------
    hexcode : str
        of the form "#RRGGBB"

    Returns
    -------
    Color
        Color object to represent hexcode

    Raises
    ------
    MalformedHexError
        if provided hexcode is not of the form "#RRGGBB"
    '''
    if hexcode[0] == "#":
        hexcode = hexcode[1:]

    try:
        rgb = tuple(int(hexcode[i:i+2], 16) for i in range(0, len(hexcode), 2))
        return Color(*rgb)
    except:
        raise MalformedHexError(f'#{hexcode} is a malformed hexcode; must be of the form #RRGGBB')

def from_hexes(hexcodes: list[str], name: str = None) -> Palette:
    '''generates Palette from a list of hexcodes

    Parameters
    ----------
    hexcodes : list[str]
        of the form "#RRGGBB"
    name : str
        name of Palette (default is None)

    Returns
    -------
    Palette
        Palette object to where each color represents one of the provided hexcodes

    Raises
    ------
    MalformedHexError
        if one of the provided hexcodes is not of the form "#RRGGBB"
    '''
    return Palette([from_hex(hexcode) for hexcode in hexcodes], name)


def from_ordered_colors_match(
        colors: list[Colors],
        name: Optional[str] = None,
        base_palette: Palette = axarva_palette
) -> Palette:
    '''generates palette from list of colors in decreasing order of amount

    the algorithm works by iterating through the provided list of colors and,
    for each color, assigning it to the position that the most similar color in
    the base palette occupies; e.g. if #000000 (black) occupies the 0th position
    in the base palette and the current color being examined is most silimar to
    #000000 then the current color will occupy the 0th position in the generated
    palette

    Parameters
    ----------
    colors : list[Colors]
        list of colors ordered from most frequently appeared to least frequenty appeared
    name : str, optional
        name to give to palette (default is None)
    base_palette : Palette, optional
        Palette to base the new palette off of (default is axarva_palette, see https://github.com/Axarva/dotfiles-2.0/blob/main/config/alacritty.yml)

    Returns
    -------
    Palette
        color palette with len(base_palette.colors) number of colors
    '''
    indices, base_colors = list(range(len(base_palette.colors))), base_palette.colors.copy()

    palette_colors = [None for _ in range(len(base_palette.colors))]

    for color in colors:
        if not base_colors:
            break

        i = color.closest(base_colors)
        j, _ = indices.pop(i), base_colors.pop(i)

        palette_colors[j] = color

    return Palette(palette_colors, name)

def from_ordered_colors_find(
        colors: list[Colors],
        name: Optional[str] = None,
        base_palette: Palette = axarva_palette
) -> Palette:
    '''generates palette from list of colors in decreasing order of amount

    the algorithm works by iterating through the colors of the base palette and,
    for each base color, finding the most similar color in the provided list of
    colors and assigning it to the position that the current base color occupies
    in the base palette; e.g. if #000000 (black) occupies the 0th position
    in the base palette, the color most similar to #000000 in the provided list
    of colors will occupy the 0th position in the generated palette

    Parameters
    ----------
    colors : list[Colors]
        list of colors ordered from most frequently appeared to least frequenty appeared
    base_palette : Palette, optional
        Palette to base the new palette off of (default is axarva_palette, see https://github.com/Axarva/dotfiles-2.0/blob/main/config/alacritty.yml)
    name : str, optional
        name to give to palette (default is None)

    Returns
    -------
    Palette
        color palette with len(base_palette.colors) number of colors
    '''
    base_colors = base_palette.colors.copy()

    return Palette([colors.pop(base_color.closest(colors)) for base_color in base_colors], name)

generation_algorithms = {
    'from_ordered_colors_match': from_ordered_colors_match,
    'from_ordered_colors_find': from_ordered_colors_find
}


def from_image(
        img: Image,
        name: Optional[str] = None,
        quantize_number: int = 64,
        algorithm=from_ordered_colors_match,
        **algorithm_parameters
) -> Palette:
    '''constructs Palette object from an image (.jpg/.png file) using the provided algorithm

    Parameters
    ----------
    img : Image
        from .jpg/.png file
    name : str, optional
        name of palette (default is None)
    quantize_number : int, optional
        number of colors to quantize the image to and thus select colors from (default is 64)
    algorithm : (list[Colors], **params) -> Palette
        algorithm to use for converting a list of colors to a palette
    **algorithm_parameters
        keyword arguments which algorithm accepts in addition to a list of colors and name of palette

    Returns
    -------
    Palette
        color palette based off of provided image
    '''
    colors = [Color(*rgb) for rgb, _ in img.quantize(colors=quantize_number, method=Image.MAXCOVERAGE).palette.colors.items()]

    return algorithm(colors, name, **algorithm_parameters)


def from_config(name: str) -> Palette:
    '''pulls existing palette from config

    Parameters
    ----------
    name : str
        name of palette

    Returns
    -------
    Palette
        the palette as it exists in config

    Raises
    ------
    PaletteNotFoundError
        if the palette doesn't exist
    '''
    try:
        with open(os.path.join(config.palettes_dir, f'{name}.yml')) as f:
            return yaml.load(f, Loader=yaml.Loader)
    except FileNotFoundError:
        raise PaletteNotFoundError(f'{name} palette doesn\'t exist')
