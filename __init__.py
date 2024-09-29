import importlib
import os
import typer
from typing import Dict, Any, Optional
import rich


def load_commands(app: typer.Typer, directory: str) -> None:

    for root, dirs, files in os.walk(directory):
        if "__init__.py" in files:
            rel_path = os.path.relpath(root, directory)
            module_path = rel_path.replace(os.path.sep, ".")

            if module_path == ".":
                continue

            module = importlib.import_module(f"commands.{module_path}")

            if hasattr(module, "app") and isinstance(module.app, typer.Typer):
                group_name = module_path.split(".")[-1]
                for item_name in os.listdir(root):
                    if item_name.endswith(".py") and item_name != "__init__.py":
                        command_module = importlib.import_module(
                            f"commands.{module_path}.{item_name[:-3]}"
                        )

                group_app = module.app
                app.add_typer(group_app, name=group_name, no_args_is_help=True)


app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=lambda value: typer.echo("1.0.0") if value else None,
        is_eager=True,
        help="Show the version and exit.",
    ),
):
    """
    My CLI application
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def create_cli() -> typer.Typer:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    commands_dir = os.path.join(current_dir, "commands")
    load_commands(app, commands_dir)
    return app


cli = create_cli()

if __name__ == "__main__":
    cli()
