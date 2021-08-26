__package__ = 'cli'

import typer

from . import palette
from . import theme

app = typer.Typer()
app.add_typer(palette.app, name='palette')
app.add_typer(theme.app, name='theme')

if __name__ == '__main__':
    app()
