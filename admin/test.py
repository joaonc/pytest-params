#!python
"""
Test tasks.
"""

import typer

from admin.utils import DryAnnotation, run

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


@app.command(name='unit')
def test_unit(dry: DryAnnotation = False):
    """
    Run unit tests.

    Temporarily installs the ``pytest-params`` package in editable mode.
    """
    run('uv', 'pip', 'install', '--editable', '.', dry=dry)
    run('uv', 'run', 'pytest', dry=dry)
    run('uv', 'pip', 'uninstall', 'pytest-params', dry=dry)


if __name__ == '__main__':
    app()
