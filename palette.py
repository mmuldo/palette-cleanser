import numpy as np
from PIL import Image

### GLOBAL VARS ###
base_colors = {
    'black':    (0,     0,      0),
    'red':      (255,   0,      0),
    'green':    (0,     255,    0),
    'yellow':   (255,   255,    0),
    'blue':     (0,     0,      255),
    'purple':   (255,   0,      255),
    'cyan':     (0,     255,    255),
    'white':    (255,   255,    255),
}


### UTILITY FUNCTIONS ###
def show(red, green, blue):
    '''
    prints background for text in the specified rgb color

    Args:
        red (int): red component, 0 to 255
        green (int): green component, 0 to 255
        blue (int): blue component, 0 to 255

    Returns:
        str -> str: a function who's input is the text to print
            and who's output is a string that when printed has a
            background with the specified rgb color
    '''
    start = ';'.join(['\x1b[48', '2', str(red), str(green), str(blue) + 'm'])
    end = '\x1b[0m'
    return lambda text: start + text + end

def distance(x, y):
    '''
    computes distance between two 3D points

    Args:
        x (float tuple): first point with 3 coordinates
        y (float tuple): second point with 3 coordinates

    Returns:
        float: distance between x and y
    '''
    return ((x[0] - y[0])**2 + (x[1] - y[1])**2 + (x[2] - y[2])** 2)**.5

def closest(colors, base_color):
    '''
    finds the element out of a list of colors that is "closest"
    to base_color. "closest" is defined by distance on a 3D coordinate
    plane (where the coordinates are the red, green, and blue components
    of the color).

    Args:
        colors (int tuple list): list of rgb colors
        base_color (int tuple): rgb color to compare to

    Returns:
        int: index of rgb color in list that is "closest" to the base color
    '''
    return np.argmin([distance(color, base_color) for color in colors])


### CLASSES ###
class Palette:
    '''
    represents a palette of rgb colors

    Params:
        colors (int tuple list): list of indexed (r, g, b) colors
        background (int tuple): (r, g, b) background for the palette
        foreground (int tuple): (r, g, b) foreground for the palette
    '''
    def __init__(self, colors, background, foreground):
        self.colors = colors
        self.background = background
        self.foreground = foreground

    def __str__(self):
        colors = '\n'.join([show(*color)('color' + str(index)) for index, color in enumerate(self.colors)])

        return '\n'.join([colors, show(*self.background)('background'), show(*self.foreground)('foreground')])


### FUNCTIONS ###
def from_image(img, quantize_number=64):
    '''
    constructs Palette object from an image (.jpg/.png file)

    Args:
        img (Image): from .jpg/.png file
        quantize_number (int, optional): number of colors to quantize the image to
            and thus select colors from (default is 64)

    Returns:
        Palette: color palette of 8 colors, a background color, and a foreground color
    '''
    colors = [rgb for rgb, _ in img.quantize(colors=quantize_number, method=Image.MAXCOVERAGE).palette.colors.items()]

    color0 = colors.pop(closest(colors, base_colors['black']))
    background = colors.pop(closest(colors, base_colors['black']))
    foreground = colors.pop(closest(colors, base_colors['white']))

    return Palette([color0] + [colors.pop(closest(colors, rgb)) for name, rgb in base_colors.items() if name != 'black'], background, foreground)
