# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912,R0913,R0914,R0915,R0917,C0302

"""Load, validate, and normalize pofff configuration values.

This module combines command-line settings with TOML input, validates common
simulation variables and workflow-specific ERT or Everest options, extracts
facies and history-matching definitions, and populates derived runtime settings.
Validation reports accepted values through the shared terminal helpers."""

import ast
import math
import tomllib
from pathlib import Path
from typing import Any

import numpy as np

from pofff.config.config import CliConfig, PofffConfig
from pofff.utils.terminal import (
    cli_correct_value,
    cli_error_value,
    cli_warning_value,
    pofff_error,
    pofff_warning,
)

FACIES_KEYS = {
    "poro",
    "perm",
    "permx",
    "permy",
    "permz",
    "disperc",
    "swi",
    "sni",
    "pen",
    "nkrw",
    "nkrn",
    "npe",
    "thre",
    "npnt",
}


def load_toml(filename: str, mode: str) -> dict:
    """Load and validate a TOML configuration file.

    Parameters
    ----------
    filename : str
        Path to the input file.
    mode : str
        Selected pofff execution mode.

    Returns
    -------
    dict
        Validated and normalized TOML configuration values.

    Raises
    ------
    SystemExit
        If the TOML configuration is invalid."""
    with open(filename, "rb") as f:
        toml = tomllib.load(f)
    return _validate_toml(toml, mode)


def postprocess_config(cfg: PofffConfig, toml: dict) -> None:
    """Enrich configuration with derived values and runtime flags.

    The function converts diffusion to m²/day and populates derived grid,
    history-matching, and workflow flags on ``cfg``.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    toml : dict
        Validated TOML values used to populate the runtime configuration."""
    cfg.para.update(
        {
            "permx7": 0,
            "permz7": 0,
            "poro7": 0,
            "disperc7": 0,
            "swi7": 0,
            "sni7": 0,
            "pen7": 0,
            "nkrw7": 2,
            "nkrn7": 2,
            "npe7": 2,
            "thre7": 5e-2,
            "npnt7": 2,
        }
    )
    cfg.nxz = [int(np.sum(cfg.x)), int(np.sum(cfg.z))]
    cfg.diffusion = 86400 * np.array(cfg.diffusion)  # Convert to m²/day
    cfg.data = cfg.fol.name.upper()
    process_tuning(cfg)
    cfg.hascellmaps = (
        cfg.x != [140]
        or cfg.z != [7, 5, 5, 5, 5, 5, 5, 8, 10, 9, 5]
        or cfg.grid != "corner-point"
    )
    cfg.everert = cfg.cores is not None and cfg.mode != "single"
    if cfg.everert:
        for i in range(1, 8):
            for name in FACIES_KEYS:
                key = f"{name}{i}"
                if key in toml:
                    cfg.hm[key] = toml[key]
        if "thicknessmult" in toml:
            cfg.hm["thicknessmult"] = toml["thicknessmult"]


def process_tuning(cfg: PofffConfig) -> None:
    """Enable tuning and normalize injection specifications if requested.

    Injection rows with TUNING text are expanded in place and ``cfg.tuning`` is enabled.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state."""
    for token in cfg.flow.split():
        if "--enable-tuning" not in token:
            continue
        if token[16:] not in {"true", "True", "1"}:
            continue
        cfg.tuning = True
        for i, inj in enumerate(cfg.inj):
            if len(inj) != 5:
                continue
            parts = inj[-1].split("/")
            cfg.inj[i] = [
                *inj[:-1],
                parts[0].strip(),
                *(p.strip() for p in parts[1:]),
            ]


def extract_facies(data: dict) -> dict:
    """Extract definitions and remove them from the main config dict.

    Parameters
    ----------
    data : dict
        Configuration dictionary modified while extracting definitions.

    Returns
    -------
    dict
        Facies tables removed from the input dictionary."""
    facies = {k: data.pop(k) for k in list(data) if k.startswith("facie")}
    for i in range(1, 8):
        for name in FACIES_KEYS:
            data.pop(f"{name}{i}", None)
    data.pop("thicknessmult", None)
    return facies


def build_config(
    *,
    pofff_path: Path,
    cli: CliConfig,
    toml: dict,
) -> PofffConfig:
    """Build and return a fully initialized PofffConfig object.

    Parameters
    ----------
    pofff_path : Path
        Package root containing templates, geology, jobs, and benchmark data.
    cli : CliConfig
        Cli used by this operation.
    toml : dict
        Validated TOML values used to populate the runtime configuration.

    Returns
    -------
    PofffConfig
        Runtime configuration populated from CLI and TOML values."""
    facies = extract_facies(toml)
    cfg = PofffConfig(
        path=pofff_path,
        fol=cli.fol,
        deck=cli.deck,
        jobs=cli.jobs,
        experiment=cli.experiment,
        times=cli.times,
        msat=cli.msat,
        mcon=cli.mcon,
        mode=cli.mode,
        figures=cli.figures,
        location=cli.location,
        use=cli.use,
        **toml,
    )
    for values in facies.values():
        cfg.para.update(values)
    return cfg


def _is_finite_number(value: Any) -> bool:
    """Return whether a value is a finite non-Boolean number.

    Parameters
    ----------
    value : Any
        Value to inspect or format.

    Returns
    -------
    bool
        Whether the value is a finite, non-Boolean number."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _is_integer(value: Any) -> bool:
    """Return whether a value is a non-Boolean integer.

    Parameters
    ----------
    value : Any
        Value to inspect or format.

    Returns
    -------
    bool
        Whether the value is a non-Boolean integer."""
    return isinstance(value, int) and not isinstance(value, bool)


def _add_validation_error(errors: list[str], message: str) -> None:
    """Add a TOML validation error.

    Parameters
    ----------
    errors : list[str]
        Validation messages collected during the current validation pass.
    message : str
        Human-readable message to display or append."""
    errors.append(message)


def _validate_string(cfg_file: dict[str, Any], key: str, errors: list[str]) -> bool:
    """Check that a TOML variable is a non-empty string.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    key : str
        Configuration variable or history-matching parameter name.
    errors : list[str]
        Validation messages collected during the current validation pass.

    Returns
    -------
    bool
        Whether the variable is present and is a non-empty string."""
    if key not in cfg_file:
        return False
    value = cfg_file[key]
    if not isinstance(value, str) or not value.strip():
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has invalid value "
            f"{cli_error_value(str(value))}, expected "
            f"{cli_correct_value('a non-empty string')}.",
        )
        return False
    return True


def _validate_number(
    cfg_file: dict[str, Any],
    key: str,
    errors: list[str],
    minimum: float | None = None,
    maximum: float | None = None,
    strict: bool = False,
    integer: bool = False,
) -> bool:
    """Check that a TOML variable is numeric and in the expected range.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    key : str
        Configuration variable or history-matching parameter name.
    errors : list[str]
        Validation messages collected during the current validation pass.
    minimum : float | None, optional
        Optional lower bound for accepted values.
    maximum : float | None, optional
        Optional upper bound for accepted values.
    strict : bool, optional
        Whether the lower bound is exclusive.
    integer : bool, optional
        Whether accepted entries must be non-Boolean integers.

    Returns
    -------
    bool
        Whether the variable is present and satisfies the numeric constraints."""
    if key not in cfg_file:
        return False
    value = cfg_file[key]
    valid_type = _is_integer(value) if integer else _is_finite_number(value)
    if not valid_type:
        expected = "an integer" if integer else "a finite number"
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has invalid value "
            f"{cli_error_value(str(value))}, expected {cli_correct_value(expected)}.",
        )
        return False
    valid = True
    if minimum is not None and (value <= minimum if strict else value < minimum):
        condition = (
            f"a value greater than {minimum}"
            if strict
            else f"a value greater than or equal to {minimum}"
        )
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has invalid value "
            f"{cli_error_value(str(value))}, expected {cli_correct_value(condition)}.",
        )
        valid = False
    if maximum is not None and value > maximum:
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has invalid value "
            f"{cli_error_value(str(value))}, expected "
            f"{cli_correct_value(f'a value less than or equal to {maximum}')}.",
        )
        valid = False
    return valid


def _validate_array(
    cfg_file: dict[str, Any],
    key: str,
    errors: list[str],
    length: int | None = None,
    integer: bool = False,
    minimum: float | None = None,
    strict: bool = False,
    nonempty: bool = False,
) -> bool:
    """Check the type, length, and numeric values of a TOML array.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    key : str
        Configuration variable or history-matching parameter name.
    errors : list[str]
        Validation messages collected during the current validation pass.
    length : int | None, optional
        Required array length, when specified.
    integer : bool, optional
        Whether accepted entries must be non-Boolean integers.
    minimum : float | None, optional
        Optional lower bound for accepted values.
    strict : bool, optional
        Whether the lower bound is exclusive.
    nonempty : bool, optional
        Whether the array must contain at least one entry.

    Returns
    -------
    bool
        Whether the variable is present and satisfies the array constraints."""
    if key not in cfg_file:
        return False
    value = cfg_file[key]
    if not isinstance(value, list):
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has invalid type "
            f"{cli_error_value(type(value).__name__)}, expected "
            f"{cli_correct_value('an array')}.",
        )
        return False
    if length is not None and len(value) != length:
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has {cli_error_value(str(len(value)))} "
            f"entries, expected {cli_correct_value(str(length))}.",
        )
        return False
    if nonempty and not value:
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} must contain "
            f"{cli_correct_value('at least one entry')}.",
        )
        return False
    valid = True
    for index, entry in enumerate(value):
        correct_type = _is_integer(entry) if integer else _is_finite_number(entry)
        expected = "an integer" if integer else "a finite number"
        if not correct_type:
            _add_validation_error(
                errors,
                f"variable {cli_error_value(f'{key}[{index}]')} has invalid value "
                f"{cli_error_value(str(entry))}, expected "
                f"{cli_correct_value(expected)}.",
            )
            valid = False
            continue
        if minimum is not None and (entry <= minimum if strict else entry < minimum):
            condition = (
                f"a value greater than {minimum}"
                if strict
                else f"a value greater than or equal to {minimum}"
            )
            _add_validation_error(
                errors,
                f"variable {cli_error_value(f'{key}[{index}]')} has invalid value "
                f"{cli_error_value(str(entry))}, expected "
                f"{cli_correct_value(condition)}.",
            )
            valid = False
    return valid


def _validate_matrix(
    cfg_file: dict[str, Any],
    key: str,
    errors: list[str],
    rows: int,
    columns: int,
) -> bool:
    """Check the dimensions and numeric values of a TOML matrix.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    key : str
        Configuration variable or history-matching parameter name.
    errors : list[str]
        Validation messages collected during the current validation pass.
    rows : int
        Required number of matrix rows.
    columns : int
        Required number of entries in each matrix row.

    Returns
    -------
    bool
        Whether the variable is present and has the required numeric shape."""
    if key not in cfg_file:
        return False
    value = cfg_file[key]
    if not isinstance(value, list):
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has invalid type "
            f"{cli_error_value(type(value).__name__)}, expected "
            f"{cli_correct_value('an array of arrays')}.",
        )
        return False
    if len(value) != rows:
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has {cli_error_value(str(len(value)))} "
            f"rows, expected {cli_correct_value(str(rows))}.",
        )
        return False
    valid = True
    for row_index, row in enumerate(value):
        if not isinstance(row, list):
            _add_validation_error(
                errors,
                f"variable {cli_error_value(f'{key}[{row_index}]')} has invalid "
                f"type {cli_error_value(type(row).__name__)}, expected "
                f"{cli_correct_value('an array')}.",
            )
            valid = False
            continue
        if len(row) != columns:
            _add_validation_error(
                errors,
                f"variable {cli_error_value(f'{key}[{row_index}]')} has "
                f"{cli_error_value(str(len(row)))} entries, expected "
                f"{cli_correct_value(str(columns))}.",
            )
            valid = False
            continue
        for column_index, entry in enumerate(row):
            if not _is_finite_number(entry):
                _add_validation_error(
                    errors,
                    f"variable "
                    f"{cli_error_value(f'{key}[{row_index}][{column_index}]')} "
                    f"has invalid value {cli_error_value(str(entry))}, expected "
                    f"{cli_correct_value('a finite number')}.",
                )
                valid = False
    return valid


def _validate_expression(cfg_file: dict[str, Any], key: str, errors: list[str]) -> None:
    """Check that a TOML variable contains a valid Python expression.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    key : str
        Configuration variable or history-matching parameter name.
    errors : list[str]
        Validation messages collected during the current validation pass."""
    if not _validate_string(cfg_file, key, errors):
        return
    try:
        ast.parse(cfg_file[key], mode="eval")
    except SyntaxError as err:
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} contains invalid Python expression "
            f"{cli_error_value(cfg_file[key])}: {err.msg}.",
        )


def _validate_thickness(cfg_file: dict[str, Any], errors: list[str]) -> None:
    """Check the thickness-map selection or numeric thickness.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    errors : list[str]
        Validation messages collected during the current validation pass."""
    if "thickness" not in cfg_file:
        return
    value = cfg_file["thickness"]
    if isinstance(value, str) and value in {"initial", "final"}:
        return
    if _is_finite_number(value) and value > 0:
        return
    _add_validation_error(
        errors,
        f"variable {cli_error_value('thickness')} has invalid value "
        f"{cli_error_value(str(value))}, expected "
        f"{cli_correct_value('initial, final, or a positive finite number')}.",
    )


def _validate_facies(
    cfg_file: dict[str, Any], key: str, index: int, errors: list[str]
) -> None:
    """Check one fixed facies-property definition.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    key : str
        Configuration variable or history-matching parameter name.
    index : int
        One-based facies index.
    errors : list[str]
        Validation messages collected during the current validation pass."""
    if key not in cfg_file:
        return
    facies = cfg_file[key]
    if not isinstance(facies, dict):
        _add_validation_error(
            errors,
            f"variable {cli_error_value(key)} has invalid type "
            f"{cli_error_value(type(facies).__name__)}, expected "
            f"{cli_correct_value('a table of facies properties')}.",
        )
        return
    required_names = {
        "permx",
        "permz",
        "poro",
        "disperc",
        "swi",
        "sni",
        "pen",
        "nkrw",
        "nkrn",
        "npe",
        "thre",
        "npnt",
    }
    required = {f"{name}{index}" for name in required_names}
    allowed = {f"{name}{index}" for name in FACIES_KEYS}
    for name in sorted(required - facies.keys()):
        _add_validation_error(
            errors,
            f"missing required facies property {cli_error_value(name)} in "
            f"{cli_error_value(key)}.",
        )
    for name in sorted(facies.keys() - allowed):
        _add_validation_error(
            errors,
            f"unknown or mismatched facies property {cli_error_value(name)} in "
            f"{cli_error_value(key)}.",
        )
    valid_values: dict[str, float | int] = {}
    for name, value in facies.items():
        base = name.removesuffix(str(index))
        if name not in allowed:
            continue
        if base == "npnt":
            valid = _is_integer(value) and value >= 2
            expected = "an integer greater than or equal to 2"
        elif base in {"poro", "swi", "sni"}:
            valid = _is_finite_number(value) and 0 <= value <= 1
            expected = "a value between 0 and 1"
        elif base in {"nkrw", "nkrn", "npe"}:
            valid = _is_finite_number(value) and value > 0
            expected = "a positive finite number"
        else:
            valid = _is_finite_number(value) and value >= 0
            expected = "a non-negative finite number"
        if not valid:
            _add_validation_error(
                errors,
                f"variable {cli_error_value(name)} has invalid value "
                f"{cli_error_value(str(value))}, expected "
                f"{cli_correct_value(expected)}.",
            )
        else:
            valid_values[base] = value
    if "swi" in valid_values and "sni" in valid_values:
        total = valid_values["swi"] + valid_values["sni"]
        if total > 1:
            _add_validation_error(
                errors,
                f"variables {cli_error_value(f'swi{index}')} and "
                f"{cli_error_value(f'sni{index}')} have a combined value "
                f"{cli_error_value(str(total))}, expected a combined value less "
                f"than or equal to {cli_correct_value('1')}.",
            )


def _validate_injection_schedule(cfg_file: dict[str, Any], errors: list[str]) -> bool:
    """Check injection values and return whether TUNING values are defined.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    errors : list[str]
        Validation messages collected during the current validation pass.

    Returns
    -------
    bool
        Whether at least one injection row defines TUNING values."""
    if "inj" not in cfg_file:
        return False
    inj = cfg_file["inj"]
    if not isinstance(inj, list):
        _add_validation_error(
            errors,
            f"variable {cli_error_value('inj')} has invalid type "
            f"{cli_error_value(type(inj).__name__)}, expected "
            f"{cli_correct_value('an array of injection rows')}.",
        )
        return False
    if not inj:
        _add_validation_error(
            errors,
            f"variable {cli_error_value('inj')} must contain "
            f"{cli_correct_value('at least one injection row')}.",
        )
        return False
    tuning_defined = False
    for row_index, row in enumerate(inj):
        if not isinstance(row, list):
            _add_validation_error(
                errors,
                f"variable {cli_error_value(f'inj[{row_index}]')} has invalid type "
                f"{cli_error_value(type(row).__name__)}, expected "
                f"{cli_correct_value('an array')}.",
            )
            continue
        if len(row) not in {4, 5}:
            _add_validation_error(
                errors,
                f"variable {cli_error_value(f'inj[{row_index}]')} has "
                f"{cli_error_value(str(len(row)))} entries, expected "
                f"{cli_correct_value('4 entries, or 5 with TUNING values')}.",
            )
            continue
        for column_index in range(4):
            value = row[column_index]
            variable = f"inj[{row_index}][{column_index}]"
            if not _is_finite_number(value):
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value(variable)} has invalid value "
                    f"{cli_error_value(str(value))}, expected "
                    f"{cli_correct_value('a finite number')}.",
                )
            elif column_index in {0, 1} and value <= 0:
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value(variable)} has invalid value "
                    f"{cli_error_value(str(value))}, expected "
                    f"{cli_correct_value('a positive value')}.",
                )
            elif column_index in {2, 3} and value < 0:
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value(variable)} has invalid value "
                    f"{cli_error_value(str(value))}, expected "
                    f"{cli_correct_value('a non-negative injection rate')}.",
                )
        if len(row) == 5:
            tuning_defined = True
            if not isinstance(row[4], str) or not row[4].strip():
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value(f'inj[{row_index}][4]')} has "
                    f"invalid value {cli_error_value(str(row[4]))}, expected "
                    f"{cli_correct_value('a non-empty TUNING string')}.",
                )
    return tuning_defined


def _validate_history_parameter(
    cfg_file: dict[str, Any], key: str, workflow: str, errors: list[str]
) -> None:
    """Check an ERT distribution or Everest interval definition.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    key : str
        Configuration variable or history-matching parameter name.
    workflow : str
        Effective simulation, ERT, or Everest workflow.
    errors : list[str]
        Validation messages collected during the current validation pass."""
    value = cfg_file[key]
    if not isinstance(value, list):
        _add_validation_error(
            errors,
            f"history-matching variable {cli_error_value(key)} has invalid type "
            f"{cli_error_value(type(value).__name__)}, expected "
            f"{cli_correct_value('an array')}.",
        )
        return
    if workflow == "ert":
        if len(value) != 3:
            _add_validation_error(
                errors,
                f"history-matching variable {cli_error_value(key)} has "
                f"{cli_error_value(str(len(value)))} entries, expected "
                f"{cli_correct_value('a distribution name and two parameters')}.",
            )
            return
        if not isinstance(value[0], str) or not value[0].strip():
            _add_validation_error(
                errors,
                f"variable {cli_error_value(f'{key}[0]')} has invalid value "
                f"{cli_error_value(str(value[0]))}, expected "
                f"{cli_correct_value('a non-empty distribution name')}.",
            )
        for index in (1, 2):
            if not _is_finite_number(value[index]):
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value(f'{key}[{index}]')} has invalid "
                    f"value {cli_error_value(str(value[index]))}, expected "
                    f"{cli_correct_value('a finite number')}.",
                )
        if (
            isinstance(value[0], str)
            and value[0].lower() == "uniform"
            and all(_is_finite_number(value[index]) for index in (1, 2))
            and value[1] >= value[2]
        ):
            _add_validation_error(
                errors,
                f"history-matching variable {cli_error_value(key)} has invalid "
                f"uniform bounds {cli_error_value(str(value[1:]))}, expected the "
                f"lower bound to be less than {cli_correct_value('the upper bound')}.",
            )
        return
    if len(value) != 4:
        _add_validation_error(
            errors,
            f"history-matching variable {cli_error_value(key)} has "
            f"{cli_error_value(str(len(value)))} entries, expected "
            f"{cli_correct_value('initial, minimum, maximum, and scale values')}.",
        )
        return
    if not all(_is_finite_number(entry) for entry in value):
        for index, entry in enumerate(value):
            if not _is_finite_number(entry):
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value(f'{key}[{index}]')} has invalid "
                    f"value {cli_error_value(str(entry))}, expected "
                    f"{cli_correct_value('a finite number')}.",
                )
        return
    initial, minimum, maximum, scale = value
    if minimum >= maximum:
        _add_validation_error(
            errors,
            f"history-matching variable {cli_error_value(key)} has invalid bounds "
            f"{cli_error_value(str([minimum, maximum]))}, expected the minimum "
            f"to be less than {cli_correct_value('the maximum')}.",
        )
    elif not minimum <= initial <= maximum:
        _add_validation_error(
            errors,
            f"variable {cli_error_value(f'{key}[0]')} has invalid value "
            f"{cli_error_value(str(initial))}, expected a value between "
            f"{cli_correct_value(str(minimum))} and "
            f"{cli_correct_value(str(maximum))}.",
        )
    if not _is_integer(scale) or scale <= 0:
        _add_validation_error(
            errors,
            f"variable {cli_error_value(f'{key}[3]')} has invalid value "
            f"{cli_error_value(str(scale))}, expected "
            f"{cli_correct_value('a positive integer scale')}.",
        )


def _is_tuning_enabled(flow: Any) -> bool:
    """Return whether TUNING is enabled in the Flow command.

    Parameters
    ----------
    flow : Any
        Flow used by this operation.

    Returns
    -------
    bool
        Whether the Flow command explicitly enables TUNING."""
    if not isinstance(flow, str):
        return False
    return any(
        token.lower() in {"--enable-tuning=true", "--enable-tuning=1"}
        for token in flow.split()
    )


def _effective_workflow(cfg_file: dict[str, Any], mode: str) -> str:
    """Return the effective simulation, ERT, or Everest workflow.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    mode : str
        Selected pofff execution mode.

    Returns
    -------
    str
        Effective workflow name used for validation."""
    if mode in {"ert", "everest"}:
        return mode
    if mode == "files" and "cores" in cfg_file:
        return "everest" if "popsize" in cfg_file else "ert"
    return "simulation"


def _warn_and_remove(cfg_file: dict[str, Any], keys: set[str], message: str) -> None:
    """Warn about ineffective variables and remove them.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    keys : set[str]
        Configuration variables to remove when they are ineffective.
    message : str
        Human-readable message to display or append."""
    present = sorted(keys & cfg_file.keys())
    if not present:
        return
    formatted = ", ".join(cli_warning_value(key) for key in present)
    plural = len(present) != 1
    pofff_warning(
        f"variable{'s' if plural else ''} {formatted} "
        f"{'are' if plural else 'is'} only effective for "
        f"{cli_correct_value(message)} and will be ignored."
    )
    for key in present:
        cfg_file.pop(key)


def _validate_toml(cfg_file: dict[str, Any], mode: str) -> dict[str, Any]:
    """Validate and normalize TOML configuration values.

    Parameters
    ----------
    cfg_file : dict[str, Any]
        Cfg file used by this operation.
    mode : str
        Selected pofff execution mode.

    Returns
    -------
    dict[str, Any]
        Validated configuration values suitable for ``PofffConfig``.

    Raises
    ------
    SystemExit
        If one or more configuration values are invalid."""
    if not isinstance(cfg_file, dict):
        pofff_error(
            f"invalid TOML content {cli_error_value(type(cfg_file).__name__)}, "
            f"expected {cli_correct_value('a dictionary of configuration variables')}."
        )
    cfg_file = cfg_file.copy()
    errors: list[str] = []
    common_required = {
        "flow",
        "grid",
        "thickness",
        "mult_thickness",
        "x",
        "z",
        "temperature",
        "pressure",
        "diffusion",
        "sources",
        "inj",
        "krw",
        "krn",
        "cap",
        "facie1",
        "facie2",
        "facie3",
        "facie4",
        "facie5",
        "facie6",
    }
    common_optional = {"cores", "maxtime", "delete", "monotonic"}
    ert_only = {"ertargs", "ensembles", "enkf_alpha", "errors", "random_seed"}
    everest_only = {
        "max_function_evaluations",
        "max_batch_num",
        "strategy",
        "maxiter",
        "popsize",
        "tol",
        "mutation",
        "recombination",
        "rng",
        "callback",
        "disp",
        "polish",
        "init",
        "atol",
        "updating",
        "workers",
        "constraints",
        "x0",
        "integrality",
        "vectorized",
    }
    shared_history = {"min_realizations_success"}
    internal = {
        "path",
        "fol",
        "deck",
        "jobs",
        "experiment",
        "times",
        "msat",
        "mcon",
        "mode",
        "figures",
        "location",
        "use",
        "facies",
        "fluxnum",
        "fipnum",
        "porv",
        "multpv",
        "dx",
        "dz",
        "dims",
        "sensors",
        "sensor_ik",
        "source_ik",
        "boxa",
        "boxb",
        "boxc",
        "hm",
        "hascellmaps",
        "everert",
        "tuning",
        "para",
        "nxz",
        "data",
    }
    history_keys = {
        f"{name}{index}" for name in FACIES_KEYS for index in range(1, 8)
    } | {"thicknessmult"}
    configurable = (
        common_required
        | common_optional
        | ert_only
        | everest_only
        | shared_history
        | history_keys
    )
    internal_values = sorted(internal & cfg_file.keys())
    if internal_values:
        formatted = ", ".join(cli_error_value(key) for key in internal_values)
        plural = len(internal_values) != 1
        pofff_warning(
            f"variable{'s' if plural else ''} {formatted} "
            f"{'are' if plural else 'is'} managed internally and will be ignored."
        )
        for key in internal_values:
            cfg_file.pop(key)
    unknown_values = sorted(cfg_file.keys() - configurable)
    if unknown_values:
        formatted = ", ".join(cli_warning_value(key) for key in unknown_values)
        plural = len(unknown_values) != 1
        pofff_warning(
            f"unknown TOML variable{'s' if plural else ''} {formatted} "
            "will be ignored."
        )
        for key in unknown_values:
            cfg_file.pop(key)
    workflow = _effective_workflow(cfg_file, mode)
    if workflow == "simulation":
        _warn_and_remove(cfg_file, ert_only, "mode = ert")
        _warn_and_remove(cfg_file, everest_only, "mode = everest")
        _warn_and_remove(
            cfg_file,
            common_optional | shared_history,
            "an ERT or Everest workflow",
        )
        present_history = sorted(history_keys & cfg_file.keys())
        if present_history:
            formatted = ", ".join(cli_warning_value(key) for key in present_history)
            plural = len(present_history) != 1
            pofff_warning(
                f"history-matching variable{'s' if plural else ''} {formatted} "
                f"{'are' if plural else 'is'} not effective for "
                f"{cli_warning_value(f'mode = {mode}')} and will be ignored."
            )
            for key in present_history:
                cfg_file.pop(key)
    elif workflow == "ert":
        _warn_and_remove(cfg_file, everest_only, "mode = everest")
    else:
        _warn_and_remove(cfg_file, ert_only, "mode = ert")
    required = set(common_required)
    if workflow in {"ert", "everest"}:
        required |= {"cores", "min_realizations_success"}
    if workflow == "ert":
        required |= {"ertargs", "ensembles", "enkf_alpha", "errors"}
    elif workflow == "everest":
        required |= {"max_function_evaluations", "popsize"}
    for key in sorted(required - cfg_file.keys()):
        _add_validation_error(
            errors,
            f"missing required TOML variable {cli_error_value(key)}.",
        )
    _validate_string(cfg_file, "flow", errors)
    if _validate_string(cfg_file, "grid", errors):
        grid = cfg_file["grid"]
        if grid not in {"cartesian", "tensor", "corner-point"}:
            _add_validation_error(
                errors,
                f"variable {cli_error_value('grid')} has invalid value "
                f"{cli_error_value(grid)}, expected one of "
                f"{cli_correct_value('cartesian, corner-point, tensor')}.",
            )
    else:
        grid = cfg_file.get("grid")
    _validate_thickness(cfg_file, errors)
    _validate_number(cfg_file, "mult_thickness", errors, minimum=0, strict=True)
    refinement_valid = {
        key: _validate_array(
            cfg_file,
            key,
            errors,
            integer=True,
            minimum=0,
            strict=True,
            nonempty=True,
        )
        for key in ("x", "z")
    }
    if grid == "cartesian":
        for key in ("x", "z"):
            value = cfg_file.get(key)
            if refinement_valid[key] and isinstance(value, list) and len(value) != 1:
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value(key)} has "
                    f"{cli_error_value(str(len(value)))} entries, expected "
                    f"{cli_correct_value('one entry for a Cartesian grid')}.",
                )
    elif grid == "corner-point":
        value = cfg_file.get("z")
        if refinement_valid["z"] and isinstance(value, list) and len(value) != 11:
            _add_validation_error(
                errors,
                f"variable {cli_error_value('z')} has "
                f"{cli_error_value(str(len(value)))} entries, expected "
                f"{cli_correct_value('11 entries for a corner-point grid')}.",
            )
    _validate_array(cfg_file, "temperature", errors, length=2)
    _validate_number(cfg_file, "pressure", errors, minimum=0, strict=True)
    _validate_array(cfg_file, "diffusion", errors, length=2, minimum=0)
    sources_valid = _validate_matrix(cfg_file, "sources", errors, 2, 2)
    if sources_valid:
        dims = [2.8, 1.2]
        for source_index, source in enumerate(cfg_file["sources"]):
            for axis, value in enumerate(source):
                if value < 0 or value > dims[axis]:
                    _add_validation_error(
                        errors,
                        f"variable "
                        f"{cli_error_value(f'sources[{source_index}][{axis}]')} has "
                        f"invalid value {cli_error_value(str(value))}, expected a "
                        f"value between {cli_correct_value('0')} and "
                        f"{cli_correct_value(str(dims[axis]))}.",
                    )
    tuning_defined = _validate_injection_schedule(cfg_file, errors)
    for key in ("krw", "krn", "cap"):
        _validate_expression(cfg_file, key, errors)
    for index in range(1, 7):
        _validate_facies(cfg_file, f"facie{index}", index, errors)
    if tuning_defined and not _is_tuning_enabled(cfg_file.get("flow")):
        pofff_warning(
            f"TUNING values are defined in {cli_warning_value('inj')}, but "
            f"{cli_warning_value('--enable-tuning=true')} is not set in "
            f"{cli_correct_value('flow')}. The TUNING values may not be effective."
        )
    if "cores" in cfg_file:
        _validate_number(
            cfg_file, "cores", errors, minimum=0, strict=True, integer=True
        )
    if "maxtime" in cfg_file:
        _validate_number(cfg_file, "maxtime", errors, minimum=0)
    if "delete" in cfg_file and not isinstance(cfg_file["delete"], bool):
        _add_validation_error(
            errors,
            f"variable {cli_error_value('delete')} has invalid value "
            f"{cli_error_value(str(cfg_file['delete']))}, expected "
            f"{cli_correct_value('a Boolean')}.",
        )
    if "monotonic" in cfg_file and not isinstance(cfg_file["monotonic"], bool):
        _add_validation_error(
            errors,
            f"variable {cli_error_value('monotonic')} has invalid value "
            f"{cli_error_value(str(cfg_file['monotonic']))}, expected "
            f"{cli_correct_value('a Boolean')}.",
        )
    if "min_realizations_success" in cfg_file:
        _validate_number(
            cfg_file, "min_realizations_success", errors, minimum=0, integer=True
        )
    present_history = sorted(history_keys & cfg_file.keys())
    if workflow in {"ert", "everest"} and not present_history:
        _add_validation_error(
            errors,
            f"missing {cli_error_value('history-matching variables')}, expected "
            f"{cli_correct_value('at least one facies or thickness parameter')}.",
        )
    for key in present_history:
        _validate_history_parameter(cfg_file, key, workflow, errors)
    if workflow == "ert":
        _validate_string(cfg_file, "ertargs", errors)
        _validate_number(
            cfg_file, "ensembles", errors, minimum=0, strict=True, integer=True
        )
        _validate_number(cfg_file, "enkf_alpha", errors, minimum=0)
        _validate_array(
            cfg_file, "errors", errors, minimum=0, strict=True, nonempty=True
        )
        if "random_seed" in cfg_file:
            _validate_number(cfg_file, "random_seed", errors, minimum=0, integer=True)
    elif workflow == "everest":
        _validate_number(
            cfg_file,
            "max_function_evaluations",
            errors,
            minimum=0,
            strict=True,
            integer=True,
        )
        _validate_number(
            cfg_file, "popsize", errors, minimum=0, strict=True, integer=True
        )
        if "max_batch_num" in cfg_file:
            _validate_number(
                cfg_file,
                "max_batch_num",
                errors,
                minimum=0,
                strict=True,
                integer=True,
            )
        if "rng" in cfg_file:
            _validate_number(cfg_file, "rng", errors, minimum=0, integer=True)
        for key in ("strategy", "init", "updating"):
            if key in cfg_file:
                _validate_string(cfg_file, key, errors)
        if "maxiter" in cfg_file:
            _validate_number(
                cfg_file, "maxiter", errors, minimum=0, strict=True, integer=True
            )
        if "workers" in cfg_file:
            _validate_number(cfg_file, "workers", errors, integer=True)
        for key in ("tol", "atol"):
            if key in cfg_file:
                _validate_number(cfg_file, key, errors, minimum=0)
        if "recombination" in cfg_file:
            _validate_number(cfg_file, "recombination", errors, minimum=0, maximum=1)
        for key in ("disp", "polish", "vectorized"):
            if key in cfg_file and not isinstance(cfg_file[key], bool):
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value(key)} has invalid value "
                    f"{cli_error_value(str(cfg_file[key]))}, expected "
                    f"{cli_correct_value('a Boolean')}.",
                )
        if "mutation" in cfg_file:
            mutation = cfg_file["mutation"]
            if _is_finite_number(mutation):
                if mutation < 0:
                    _add_validation_error(
                        errors,
                        f"variable {cli_error_value('mutation')} has invalid value "
                        f"{cli_error_value(str(mutation))}, expected "
                        f"{cli_correct_value('a non-negative value')}.",
                    )
            elif isinstance(mutation, list) and len(mutation) == 2:
                if not all(_is_finite_number(value) for value in mutation):
                    _add_validation_error(
                        errors,
                        f"variable {cli_error_value('mutation')} has invalid value "
                        f"{cli_error_value(str(mutation))}, expected "
                        f"{cli_correct_value('two finite numbers')}.",
                    )
                elif mutation[0] < 0 or mutation[0] >= mutation[1]:
                    _add_validation_error(
                        errors,
                        f"variable {cli_error_value('mutation')} has invalid range "
                        f"{cli_error_value(str(mutation))}, expected non-negative "
                        f"increasing {cli_correct_value('mutation bounds')}.",
                    )
            else:
                _add_validation_error(
                    errors,
                    f"variable {cli_error_value('mutation')} has invalid value "
                    f"{cli_error_value(str(mutation))}, expected a finite number "
                    f"or {cli_correct_value('an array of two finite numbers')}.",
                )
        unsupported = {"callback", "constraints"} & cfg_file.keys()
        for key in sorted(unsupported):
            _add_validation_error(
                errors,
                f"variable {cli_error_value(key)} cannot be configured through "
                f"{cli_correct_value('TOML')}.",
            )
    if cfg_file.get("monotonic") is True and workflow in {"ert", "everest"}:
        groups = []
        for name in FACIES_KEYS - {"thre", "npnt"}:
            groups.append(
                [
                    f"{name}{index}"
                    for index in range(1, 8)
                    if f"{name}{index}" in cfg_file
                ]
            )
        if not any(len(group) >= 2 for group in groups):
            pofff_warning(
                f"variable {cli_warning_value('monotonic')} is enabled, but the "
                "selected history-matching variables do not define a comparable "
                "facies sequence. The monotonicity constraint may have no effect."
            )
    if errors:
        details = "\n".join(f"  - {error}" for error in errors)
        pofff_error(f"invalid TOML configuration:\n{details}")
    return cfg_file
