#!python
"""
Linting and static type checking.
"""

from typing import Annotated

import typer

from admin.utils import DryAnnotation, logger, run

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


@app.command(name='ruff')
def lint_ruff(
    path: Annotated[str, typer.Argument(help='Path to directory or file to lint.')] = '.',
    dry: DryAnnotation = False,
):
    run('ruff', 'format', path, dry=dry)
    run('ruff', 'check', '--fix', path, dry=dry)


@app.command(name='mypy')
def lint_mypy(path='.', dry: DryAnnotation = False):
    run('mypy', path, dry=dry)


@app.command(name='all')
def lint_all(dry: DryAnnotation = False):
    """
    Run all linters.

    Config for each of the tools is in ``pyproject.toml``.
    """
    lint_ruff(dry=dry)
    lint_mypy(dry=dry)

    logger.info('Done')


if __name__ == '__main__':
    app()
