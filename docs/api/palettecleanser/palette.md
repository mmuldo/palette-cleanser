Module palettecleanser.palette
==============================

Functions
---------

    
`from_config(name: str) ‑> palettecleanser.palette.Palette`
:   pulls existing palette from config
    
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

    
`from_hex(hexcode: str) ‑> palettecleanser.palette.Color`
:   generates Color from hexcode
    
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

    
`from_hexes(hexcodes: list[str], name: str = None) ‑> palettecleanser.palette.Palette`
:   generates Palette from a list of hexcodes
    
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

    
`from_image(image_path: str, name: Optional[str] = None, light: bool = False, backend: str = 'wal', saturate_percent: Optional[float] = None) ‑> palettecleanser.palette.Palette`
:   constructs Palette object from an image (.jpg/.png file) using the provided pywal backend
    
    Parameters
    ----------
    image_path : str
        path to image file
    name : str, optional
        name of palette (default is None)
    light : bool, optional
        True to generate a light color palette, False to generate a dark color
        palette (default is False)
    backend : str, optional
        pywal backend generation algorithm to use (see more at
        https://github.com/dylanaraps/pywal/tree/master/pywal/backends) (default is 'wal')
    saturate_percent : float, optional
        amount to saturate colors by (saturate_percent=5 means 5%) (default is None)
    
    Returns
    -------
    Palette
        color palette based off of provided image

Classes
-------

`Color(red: int, green: int, blue: int)`
:   represents an rgb color
    
    Attributes
    ----------
    red : int
        red component
    green : int
        green component
    blue : int
        blue component

    ### Class variables

    `blue: int`
    :

    `green: int`
    :

    `red: int`
    :

    ### Methods

    `closest(self, colors: list[Color]) ‑> int`
    :   out of a list of colors, finds the one that is most similar to the current object
        
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

    `distance(self, color: Color) ‑> float`
    :   computes distance to another Color
        
        uses distance formula between two 3D points for computation
        
        Parameters
        ----------
        color : Color
            color to compute distance to
        
        Returns
        -------
        float
            the computed distance

    `show(self)`
    :   hex code where the background color is that represented by the current object

    `spectrum(self, color: Color, n: int) ‑> list`
    :   generates a spectrum (list of Colors) from current object to provided color with n increments
        
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

    `tone(self, percent: float, lighten: bool) ‑> palettecleanser.palette.Color`
    :   lightens/darkens current Color object by specified percent
        
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

`MalformedHexError(*args, **kwargs)`
:   thrown when a hexcode is not of the form #rrggbb

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`Palette(colors: list[Color], name: Optional[str] = None)`
:   represents a palette of rgb colors
    
    Attributes
    ----------
    colors : list[Color]
        base colors of palette
    name : str, optional
        name of palette (default is None)

    ### Class variables

    `colors: list`
    :

    `name: Optional[str]`
    :

    ### Methods

    `save(self)`
    :   saves Palette to yml file at $XDG_CONFIG_HOME/palette-cleanser/palettes/
        
        defaults to ~/.config/palette-cleanser/palettes/

    `table(self) ‑> dict[str, list[Colors]]`
    :   converts palette to data that can be tabulated
        
        Returns
        -------
        dict[str, list[Colors]]
            single column where the header is the name of the palatte and the data are the colors

    `tone(self, percent: float, lighten: bool, name: str = None) ‑> palettecleanser.palette.Palette`
    :   lightens/darkens every color in palette by specified percent
        
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

`PaletteNotFoundError(*args, **kwargs)`
:   thrown when a palette is not found in palette-cleanser configuration

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException