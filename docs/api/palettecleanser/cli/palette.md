Module palettecleanser.cli.palette
==================================

Functions
---------

    
`create(colors: list = <typer.models.ArgumentInfo object>, name: Optional[str] = <typer.models.OptionInfo object>)`
:   

    
`edit(name: str = <typer.models.ArgumentInfo object>)`
:   edit palette with $EDITOR

    
`generate(from_image: str = <typer.models.OptionInfo object>, name: Optional[str] = <typer.models.OptionInfo object>, light: bool = <typer.models.OptionInfo object>, backend: str = <typer.models.OptionInfo object>, saturate_percent: Optional[float] = <typer.models.OptionInfo object>)`
:   

    
`generate_from_image(image_path: str, name: Optional[str] = None, light: bool = False, backend: str = 'wal', saturate_percent: Optional[float] = None)`
:   generates palette from image
    
    see palettecleanser.palette.from_image for more details

    
`ls()`
:   lists saved palettes

    
`remove(name: str = <typer.models.ArgumentInfo object>)`
:   removes a saved palette from configuration

    
`show(name: str = <typer.models.ArgumentInfo object>)`
:   prints palette