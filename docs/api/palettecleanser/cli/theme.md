Module palettecleanser.cli.theme
================================

Functions
---------

    
`create(palettes: list = <typer.models.ArgumentInfo object>, name: str = <typer.models.OptionInfo object>, image_path: str = <typer.models.OptionInfo object>, setting: Optional[list] = <typer.models.OptionInfo object>)`
:   

    
`deploy(name: str = <typer.models.ArgumentInfo object>, path: Optional[str] = <typer.models.OptionInfo object>)`
:   

    
`edit(name: str = <typer.models.ArgumentInfo object>)`
:   edit theme with $EDITOR

    
`generate(from_image: str = <typer.models.OptionInfo object>, name: str = <typer.models.OptionInfo object>, setting: Optional[list] = <typer.models.OptionInfo object>, light: bool = <typer.models.OptionInfo object>, backend: str = <typer.models.OptionInfo object>, saturate_percent: Optional[float] = <typer.models.OptionInfo object>)`
:   

    
`generate_from_image(image_path: str, name: str, settings: Optional[dict] = None, light: bool = False, backend: str = 'wal', saturate_percent: Optional[float] = None)`
:   generates theme from image
    
    see palettecleanser.theme.from_image for more details

    
`ls()`
:   lists saved themes

    
`remove(name: str = <typer.models.ArgumentInfo object>)`
:   removes a saved theme from configuration

    
`show(name: str = <typer.models.ArgumentInfo object>)`
:   prints theme