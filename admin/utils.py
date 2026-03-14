import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import StrEnum
from itertools import chain
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

from admin import PROJECT_ROOT

EMPTY_STR = object()
"""Sentinel object to represent an empty string."""


class Environment(StrEnum):
    LOCAL = 'local'
    """Run in local machine, no Docker."""

    DEV = 'dev'
    """Run in Docker in local machine."""

    STAGING = 'staging'
    """Run in Docker in AWS (staging)."""

    PROD = 'prod'
    """Run in Docker in AWS (prod)."""


class OS(StrEnum):
    """Operating System."""

    Linux = 'linux'
    MacOS = 'mac'
    Windows = 'win'


class LogLevel(StrEnum):
    """Enum for typer options."""

    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    # TRACE = 'TRACE'


class NoHighlightRichHandler(RichHandler):
    """Custom RichHandler that completely disables highlighting."""

    def render_message(self, record, message):
        """Override to disable auto-highlighting while keeping markup."""
        from rich.text import Text

        # Process markup but don't apply highlighting
        if self.markup:
            return Text.from_markup(message)
        return Text(message)


@dataclass
class StripOutput:
    strip_ansi: bool = True
    normal_strip: bool = True
    extra_chars: str | None = None

    def strip(self, text: str) -> str:
        if self.strip_ansi:
            text = strip_ansi(text)
        if self.normal_strip:
            text = text.strip()
        if self.extra_chars:
            text = text.strip(self.extra_chars)

        return text


EnvironmentAnnotation = Annotated[
    Environment | None,
    typer.Argument(help='Environment to use.', show_default=False),
]

LogLevelAnnotation = Annotated[
    LogLevel,
    typer.Option(
        help='Log level.',
        show_default=True,
        case_sensitive=True,
        show_choices=True,
    ),
]

DryAnnotation = Annotated[
    bool,
    typer.Option(
        help='Show the command that would be run without running it.',
        show_default=False,
    ),
]


def read_env_file_from_path(env_path: Path) -> dict[str, str]:
    """
    Read a `.env` file. Minimal parser, no dependencies.
    Does not update environment.

    Rules:

    - Ignores blank lines and comments.
    - Supports `export KEY=VALUE`.
    - Strips surrounding single/double quotes.
    """
    if not env_path.exists():
        raise FileNotFoundError(f'Env file not found: {env_path}')

    env = {}
    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        if line.startswith('export '):
            line = line.removeprefix('export ').lstrip()

        key, sep, value = line.partition('=')
        if not sep:
            continue

        key = key.strip()
        value = value.strip()
        if (value.startswith("'") and value.endswith("'")) or (
            value.startswith('"') and value.endswith('"')
        ):
            value = value[1:-1]

        env[key] = value

    return env


def get_env_file_path(environment: Environment) -> Path:
    return PROJECT_ROOT / f'.env.{environment.value}'


def read_env_file(environment: Environment) -> dict[str, str]:
    return read_env_file_from_path(get_env_file_path(environment))


# Another version, using `python-dotenv`
# from dotenv import dotenv_values
# def load_env_file(env_file: Path) -> dict[str, str | None]:
#     """Load environment variables from the specified .env file."""
#     if not env_file.exists():
#         logger.error(f'Environment file not found: {env_file}')
#         raise typer.Exit(1)
#
#     env_vars = dotenv_values(env_file)
#     logger.info(f'Loaded environment from: {env_file}')
#     return env_vars


def select_environment(
    environment: Environment | None = None,
    set_env: bool = True,
    **select_enum_kwargs,
) -> Environment:
    """
    Select an environment and load its `.env` file into `os.environ`.

    This project used to rely on `python-dotenv` for this. We keep the behavior (populate
    `os.environ`) without depending on `python-dotenv`.
    """

    from textual_searchable_selectionlist.options import SelectionStrategy
    from textual_searchable_selectionlist.select import select_enum

    if environment:
        env = Environment(environment)
    else:
        try:
            selected = select_enum(
                Environment,
                selection_strategy=SelectionStrategy.ONE,
                title='Environment',
                select_by='value',
                **select_enum_kwargs,
            )
        except Exception as e:
            logger.error(f'Error selecting environment: {type(e).__name__}: {e}')
            raise typer.Exit(1)

        if not selected:
            logger.error('No environment selected.')
            raise typer.Exit(1)

        env = selected[0]

    if set_env:
        logger.debug(f'Setting environment [b]{env.value}[/b]')
        env_values = read_env_file(env)
        os.environ.update(env_values)
    else:
        logger.debug(f'Selected environment [b]{env.value}[/b]')

    return env


def get_os() -> OS:
    """
    Similar to ``sys.platform`` and ``platform.system()``, but less ambiguous by returning an Enum
    instead of a string.

    Doesn't make granular distinctions of linux variants, OS versions, etc.
    """
    if sys.platform == 'darwin':
        return OS.MacOS
    if sys.platform == 'win32':
        return OS.Windows
    return OS.Linux


def run(
    *args,
    dry: bool = False,
    extra_env: dict[str, str] | None = None,
    strip_output: StripOutput | None = StripOutput(),
    **kwargs,
) -> subprocess.CompletedProcess | None:
    """
    Run a CLI command synchronously (i.e., wait for the command to finish) and return the result.

    This function is a wrapper around ``subprocess.run(...)``.

    If you need access to the output, add the ``capture_output=True`` argument and do
    ``.stdout`` to get the output as a string.

    Notes:

    * Args are converted to strings using ``str(...)``.
    * Empty strings and ``None`` are removed from the command.
      If you want to explicitly include an empty string, use ``EMPTY_STR`` instead.
    * ``stdout`` and ``stderr`` will be stripped of ANSI escape sequences by default.
    """
    final_args: list[str] = []
    for arg in args:
        if arg in ['', None]:
            continue
        if arg == EMPTY_STR:
            final_args.append('')
        else:
            final_args.append(str(arg))
    logger.info(' '.join(f'"{a}"' if (not a or ' ' in a) else a for a in final_args))

    if dry:
        return None

    defaults = dict(
        cwd=PROJECT_ROOT,
        capture_output=False,
        text=True,
        check=True,
        env=os.environ.copy() | (extra_env or {}),
    )
    final_kwargs = defaults | kwargs

    try:
        result = subprocess.run(final_args, **final_kwargs)  # type: ignore
    except subprocess.CalledProcessError as e:
        msg = str(e)
        if e.stdout:
            msg += f'\nSTDOUT:\n{e.stdout}'
        if e.stderr:
            msg += f'\nSTDERR:\n{e.stderr}'
        logger.error(msg)
        raise typer.Exit(1)

    if final_kwargs.get('capture_output') and strip_output:
        result.stdout = strip_output.strip(result.stdout)
        result.stderr = strip_output.strip(result.stderr)

    return result  # type: ignore


def run_async(*args, dry: bool = False, **kwargs) -> subprocess.Popen | None:
    """
    Starts the process and continues code execution.

    Use the following checks::

        process.poll()              # Returns None if still running, else return code
        process.wait()              # Wait for completion (blocking)
        process.terminate()         # Send SIGTERM (graceful)
        process.kill()              # Send SIGKILL (force)
        process.returncode          # Access return code after completion

    See ``subprocess.Popen(...)`` for more details.
    """
    logger.info(' '.join(map(str, args)))

    if dry:
        return None

    defaults = dict(
        cwd=PROJECT_ROOT,
    )

    try:
        return subprocess.Popen(args, **(defaults | kwargs))
    except subprocess.CalledProcessError as e:
        logger.error(e)
        raise typer.Exit(1)


def is_package_installed(package_name: str) -> bool:
    """Check if a Python package is installed."""
    import importlib.util

    if importlib.util.find_spec(package_name) is not None:
        return True

    try:
        import importlib.metadata as metadata

        metadata.version(package_name)
        return True
    except Exception:  # noqa
        return False


def install_package(
    package: str,
    package_install: str | None = None,
    exit_if_install: bool = True,
    dry: bool = False,
):
    """
    Install a Python package if not already installed.

    :param package: Name of the package to check/install.
    :param package_install: Name of the package to install, if different from the name to check.
    :param exit_if_install: Exit the program if the package is installed and `dry` is False.
    :param dry: Show the command that would be run without running it.
    """
    if is_package_installed(package):
        logger.debug(f'Package `{package}` is already installed.')
        return

    run(sys.executable, '-m', 'pip', 'install', package_install or package, dry=dry)

    if exit_if_install and not dry:
        logger.info(f'Package `{package}` installed successfully.\nRe-run the command.')
        raise typer.Exit(1)


def multiple_parameters(parameter: str, *options) -> list[str]:
    return list(chain.from_iterable(zip([parameter] * len(options), map(str, options))))


def strip_ansi(text: str) -> str:
    return Text.from_ansi(text).plain


def get_logger(name: str | None = 'typer-invoke', level=logging.DEBUG) -> logging.Logger:
    """Set up logging configuration with Rich handler and custom formatting."""

    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    _logger.handlers.clear()

    console = Console(markup=True)

    handler = NoHighlightRichHandler(
        level=level,
        console=console,
        show_time=False,
        show_level=True,
        show_path=False,
        markup=True,
        rich_tracebacks=False,
    )

    formatter = logging.Formatter(fmt='%(message)s', datefmt='[%X]')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.propagate = False

    return _logger


def set_log_level(level: LogLevel):
    logger.setLevel(level.value)


logger = get_logger()
