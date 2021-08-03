import numpy as np
from PIL import Image

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

def show(red, green, blue):
    start = ';'.join(['\x1b[48', '2', str(red), str(green), str(blue) + 'm'])
    end = '\x1b[0m'
    return lambda text: start + text + end


def distance(x, y):
    return ((x[0] - y[0])**2 + (x[1] - y[1])**2 + (x[2] - y[2])** 2)**.5

def closest(colors, base_color):
    return np.argmin([distance(color, base_color) for color in colors])

def from_image(img, quantize_number=64):
    colors = [rgb for rgb, _ in img.quantize(colors=quantize_number, method=Image.MAXCOVERAGE).palette.colors.items()]

    color0 = colors.pop(closest(colors, base_colors['black']))
    background = colors.pop(closest(colors, base_colors['black']))
    foreground = colors.pop(closest(colors, base_colors['white']))

    return Palette([color0] + [colors.pop(closest(colors, rgb)) for name, rgb in base_colors.items() if name != 'black'], background, foreground)

class Palette():
    def __init__(self, colors, background, foreground):
        self.colors = colors
        self.background = background
        self.foreground = foreground

    def __str__(self):
        colors = '\n'.join([show(*color)('color' + str(index)) for index, color in enumerate(self.colors)])

        return '\n'.join([colors, show(*self.background)('background'), show(*self.foreground)('foreground')])
