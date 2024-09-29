import os
import typer

from .foobar import foobar

app = typer.Typer()

app.command()(foobar)
