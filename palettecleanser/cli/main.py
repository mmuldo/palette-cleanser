import typer

from . import palette
from . import theme
from . import template

app = typer.Typer(help='abstracts color scheming from desktop configuration')
app.add_typer(palette.app, name='palette')
app.add_typer(theme.app, name='theme')
app.add_typer(template.app, name='template')
