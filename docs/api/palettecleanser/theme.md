Module palettecleanser.theme
============================

Functions
---------

    
`from_config(name: str) ‑> palettecleanser.theme.Theme`
:   pulls existing theme from config
    
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

    
`from_image(image_path: str, name: str, settings: Optional[dict] = None, light: bool = False, backend: str = 'wal', saturate_percent: Optional[float] = None) ‑> palettecleanser.theme.Theme`
:   generates a theme from an image
    
    The generated theme consists of three palettes: a palette generated from
    provided image, a darker version of this palette, and a lighter version of
    this palette. The image provided is used as the associated image for the theme.
    
    Parameters
    ----------
    image_path : str
        path image with which to generate the palettes for the theme; it also
        serves as the associated image for the theme
    name : str
        name of theme
    settings : dict[str, Any], optional
        additional settings to initialize new theme with (default is {})
    light : bool, optional
        True to generate a light color theme, False to generate a dark color
        theme (default is False)
    backend : str, optional
        pywal backend generation algorithm to use (see more at
        https://github.com/dylanaraps/pywal/tree/master/pywal/backends) (default is 'wal')
    saturate_percent : float, optional
        amount to saturate colors by (saturate_percent=5 means 5%) (default is None)
    
    Returns
    -------
    Theme
        new theme based off of provided image

Classes
-------

`Theme(name: str, palettes: list, image_path: str, settings: dict = {})`
:   represents a configuration theme
    
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

    ### Class variables

    `image_path: str`
    :

    `name: str`
    :

    `palettes: list`
    :

    `settings: dict`
    :

    ### Methods

    `export(self) ‑> dict`
    :   converts theme to dictionary
        
        Returns
        -------
        dict[str, Any]
            dictionary representation of theme

    `get_palettes(self) ‑> list`
    :   gets the actual palette objects
        
        Returns
        -------
        list[pal.Palette]
            list of Palettes associated with names in palettes attribute

    `save(self)`
    :   saves Theme to yml file at $XDG_CONFIG_HOME/palette-cleanser/themes/
        
        defaults to ~/.config/palette-cleanser/themes/

    `table(self) ‑> dict`
    :   converts palette to data that can be tabulated
        
        Returns
        -------
        dict[str, list[palette.Color]]
            set of columns where the headers are names of palattes and cells are colors

`ThemeNotFoundError(*args, **kwargs)`
:   thrown when theme is not found in palette-cleanser configuration

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException