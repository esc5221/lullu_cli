import os
import typer

from .list_all import list_all
from .search import search
from .preview import preview


app = typer.Typer()


app.command()(list_all)
app.command()(search)
app.command()(preview)
