import os
import typer

from .copy_context import copy_context, copy_import
from .paste_llm import paste_llm

app = typer.Typer()

app.command()(copy_context)
app.command()(copy_import)
app.command()(paste_llm)
