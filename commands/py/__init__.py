import os
import typer

from .copy_context import copy_context
from .paste_llm import paste_llm

app = typer.Typer()

app.command()(copy_context)
app.command()(paste_llm)