# SPDX-FileCopyrightText: 2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Format command-line messages for pofff.

ANSI colors are applied when supported by the selected stream. The module
provides consistent formatting for invalid, accepted, deprecated, and
informational values, plus fatal errors, warnings, tips, progress messages, and
generated-file reports."""

import os
import sys
from typing import NoReturn

ANSI_BOLD_RED = "1;31"
ANSI_BOLD_YELLOW = "1;33"
ANSI_BOLD_GREEN = "1;32"
ANSI_BOLD_BLUE = "1;34"
ANSI_BOLD_MAGENTA = "1;35"
ANSI_YELLOW = "1;33"
ANSI_GREEN = "1;32"
ANSI_CYAN = "36"
ANSI_RED = "31"
ANSI_BLUE = "1;34"


def _supports_color(stream: object = sys.stderr) -> bool:
    """Check whether an output stream supports ANSI colors.

    Parameters
    ----------
    stream : object, optional
        Output stream used to determine ANSI-color support.

    Returns
    -------
    bool
        Whether ANSI color output is enabled for the stream."""
    return (
        hasattr(stream, "isatty")
        and stream.isatty()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM") != "dumb"
    )


def _colorize(
    text: str,
    code: str,
    stream: object = sys.stderr,
) -> str:
    """Wrap text in an ANSI color sequence when supported.

    Parameters
    ----------
    text : str
        Text to format.
    code : str
        ANSI Select Graphic Rendition code.
    stream : object, optional
        Output stream used to determine ANSI-color support.

    Returns
    -------
    str
        Colored text, or unchanged text when colors are disabled."""
    if not _supports_color(stream):
        return text
    return f"\033[{code}m{text}\033[0m"


def cli_warning_value(value: str) -> str:
    """Format a deprecated CLI option or value.

    Parameters
    ----------
    value : str
        Value to inspect or format.

    Returns
    -------
    str
        Quoted value colored as a warning when supported."""
    return _colorize(repr(value), ANSI_YELLOW)


def cli_correct_value(value: str) -> str:
    """Format a correct CLI option or value.

    Parameters
    ----------
    value : str
        Value to inspect or format.

    Returns
    -------
    str
        Quoted value colored as a valid alternative when supported."""
    return _colorize(repr(value), ANSI_GREEN)


def cli_error_value(value: str) -> str:
    """Format an invalid CLI option or value.

    Parameters
    ----------
    value : str
        Value to inspect or format.

    Returns
    -------
    str
        Quoted value colored as invalid when supported."""
    return _colorize(repr(value), ANSI_RED)


def cli_info_value(value: str) -> str:
    """Format an informational CLI option or value.

    Parameters
    ----------
    value : str
        Value to inspect or format.

    Returns
    -------
    str
        Quoted value colored as information when supported."""
    return _colorize(repr(value), ANSI_BLUE)


def pofff_error(message: str) -> NoReturn:
    """Raise a fatal command-line error.

    Parameters
    ----------
    message : str
        Human-readable message to display or append.

    Raises
    ------
    SystemExit
        Always raised with the formatted error message."""
    label = _colorize("error", ANSI_BOLD_RED)
    raise SystemExit(f"{pofff_name()}: {label}: {message}")


def pofff_warning(message: str) -> None:
    """Display a non-fatal command-line warning.

    Parameters
    ----------
    message : str
        Human-readable message to display or append."""
    label = _colorize("warning", ANSI_BOLD_YELLOW)
    print(f"{pofff_name()}: {label}: {message}", file=sys.stderr)


def pofff_info(message: str) -> None:
    """Display an informational command-line message.

    Parameters
    ----------
    message : str
        Human-readable message to display or append."""
    label = _colorize("info", ANSI_BOLD_BLUE, sys.stdout)
    print(f"{pofff_name()}: {label}: {message}")


def pofff_tip(message: str) -> None:
    """Display a command-line suggestion.

    Parameters
    ----------
    message : str
        Human-readable message to display or append."""
    label = _colorize("tip", ANSI_BOLD_MAGENTA, sys.stdout)
    print(f"{pofff_name(sys.stdout)}: {label}: {message}")


def pofff_success(msg: str, output_dir: str, filenames: list[str]) -> None:
    """Display the generated output location and filenames.

    Parameters
    ----------
    msg : str
        Optional success text printed before the output location.
    output_dir : str
        Directory containing the generated files.
    filenames : list[str]
        Generated filenames to report."""
    label = _colorize("success", ANSI_BOLD_GREEN, sys.stdout)
    if not filenames:
        print(f"{pofff_name()}: {label}: {msg}{output_dir}")
    elif len(filenames) == 1:
        print(f"{pofff_name()}: {label}: {msg}{output_dir}/{filenames[0]}")
    elif len(filenames) <= 5:
        print(f"{pofff_name()}: {label}{msg}")
        print(f"            Output directory: {output_dir}")
        print(f"            Files ({len(filenames)}): {', '.join(filenames)}")
    else:
        print(f"{pofff_name()}: {label}{msg}")
        print(f"            Output directory: {output_dir}")
        print(f"            Files ({len(filenames)}):")
        for filename in filenames:
            print(f"              - {filename}")


def pofff_name(stream: object = sys.stderr) -> str:
    """Format the pofff program name.

    Parameters
    ----------
    stream : object, optional
        Output stream used to determine ANSI-color support.

    Returns
    -------
    str
        Formatted program name."""
    characters = [("pofff", "1")]
    return "".join(
        _colorize(character, color, stream) for character, color in characters
    )
