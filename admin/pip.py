#!python
"""
Python packages related tasks.
"""

from enum import StrEnum
from typing import Annotated

import typer

from admin import PROJECT_ROOT
from admin.utils import DryAnnotation, logger, run

LOCK_FILE = PROJECT_ROOT / 'uv.lock'

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


class Requirements(StrEnum):
    """
    Requirement groups.
    """

    MAIN = 'requirements'
    DEV = 'requirements-dev'


REQUIREMENTS_TO_GROUP = {
    Requirements.MAIN: None,
    Requirements.DEV: 'dev',
}

RequirementsAnnotation = Annotated[
    list[str] | None,
    typer.Argument(
        help='Requirement group(s) to use. If not set, all groups are used.\nValues can be '
        + ', '.join([f'`{x.name.lower()}`' for x in Requirements]),
        show_default=False,
    ),
]


def _get_requirement(requirements: str | Requirements) -> Requirements:
    if isinstance(requirements, Requirements):
        return requirements
    try:
        return Requirements[requirements.upper()]  # noqa
    except KeyError:
        try:
            return Requirements(requirements.lower())
        except ValueError:
            logger.error(f'`{requirements}` is an unknown requirements group.')
            raise typer.Exit(1)


def _get_requirements(requirements: list[str | Requirements] | None) -> list[Requirements]:
    if requirements is None:
        return list(Requirements)
    return [_get_requirement(req) for req in requirements]


@app.command(name='compile')
def pip_compile(
    requirements: RequirementsAnnotation = None,
    clean: Annotated[
        bool,
        typer.Option(help='Delete the existing `uv.lock` file before generating a new one.'),
    ] = False,
    dry: DryAnnotation = False,
):
    """
    Update lock file.
    """
    _ = _get_requirements(requirements)

    if requirements is not None:
        logger.info(
            'Requirement groups are ignored for lock generation; `uv lock` resolves all groups.'
        )

    if clean and not dry:
        LOCK_FILE.unlink(missing_ok=True)

    run('uv', 'lock', dry=dry)


@app.command(name='sync')
def pip_sync(requirements: RequirementsAnnotation = None, dry: DryAnnotation = False):
    """
    Synchronize environment with lock file.
    """
    selected_requirements = _get_requirements(requirements)

    command = ['uv', 'sync']
    if requirements is None:
        command.append('--all-groups')
    else:
        for req in selected_requirements:
            group = REQUIREMENTS_TO_GROUP[req]
            if group is None:
                command.append('--no-dev')
            else:
                command.extend(['--only-group', group])
    run(*command, dry=dry)


@app.command(name='package')
def pip_package(
    requirements: RequirementsAnnotation,
    package: Annotated[
        list[str], typer.Option('--package', '-p', help='One or more packages to upgrade.')
    ],
    dry: DryAnnotation = False,
):
    """
    Upgrade one or more packages.
    """
    selected_requirements = _get_requirements(requirements)

    for req in selected_requirements:
        group = REQUIREMENTS_TO_GROUP[req]
        group_args = []
        if group:
            group_args = ['--group', group]

        for pkg in package:
            run('uv', 'add', *group_args, '--upgrade-package', pkg, pkg, dry=dry)

    run('uv', 'lock', dry=dry)


@app.command(name='upgrade')
def pip_upgrade(requirements, dry: DryAnnotation = False):
    """
    Try to upgrade all dependencies to their latest versions.

    Equivalent to ``compile`` with ``--clean`` option.

    Use ``package`` to only upgrade individual packages,
    Ex ``pip package dev mypy flake8``.
    """
    _ = _get_requirements(requirements)
    if requirements is not None:
        logger.info(
            'Requirement groups are ignored for full upgrade; use `package` for targeted upgrades.'
        )
    run('uv', 'lock', '--upgrade', dry=dry)


@app.command(name='install')
def pip_install(requirements: RequirementsAnnotation, dry: DryAnnotation = False):
    """
    Install dependencies from lock file.
    """
    pip_sync(requirements=requirements, dry=dry)


if __name__ == '__main__':
    app()
