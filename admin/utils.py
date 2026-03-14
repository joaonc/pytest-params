import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import StrEnum
from itertools import chain
from typing import Annotated

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

from admin import PROJECT_ROOT

EMPTY_STR = object()
"""Sentinel object to represent an empty string."""


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
        if not arg:
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
