# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912

"""Command-line entry point and top-level workflow coordination for pofff.

pofff supports connected workflows for FluidFlower history matching:

* File generation creates OPM Flow, ERT, and Everest input.
* Single execution runs OPM Flow and generates benchmark data.
* History matching runs ERT ensemble studies or Everest optimization.
* Postprocessing creates benchmark maps, metrics, and comparison figures.

This module parses and validates CLI arguments, builds the shared configuration,
prepares output folders, dispatches the selected workflows, and reports results.
Grid construction, file writing, execution, and visualization are implemented in
the utility and visualization modules."""

import argparse
import math
import os
import shutil
from pathlib import Path

from pofff.config.config import CliConfig, PofffConfig
from pofff.utils.inputvalues import build_config, load_toml, postprocess_config
from pofff.utils.mapproperties import grid_and_properties
from pofff.utils.runs import benchmark, data, ert, everest, flow, postprocess
from pofff.utils.terminal import (
    cli_correct_value,
    cli_error_value,
    pofff_error,
    pofff_info,
    pofff_success,
    pofff_tip,
)
from pofff.utils.writefile import write_files


def main(argv: list[str] | None = None) -> None:
    """Main pofff execution routine.

    The selected file-generation, simulation, data, history-matching, and
    plotting stages are executed in dependency order.

    Parameters
    ----------
    argv : list[str] | None, optional
        Arguments to parse instead of the process command line."""
    args = _parse_arguments(argv)
    _validate_arguments(args)
    pofff_path = Path(__file__).resolve().parents[1]

    cli = _build_cli_config(args, pofff_path=pofff_path)

    if cli.figures == "none" and cli.mode == "none":
        pofff_info("nothing to do because -m none and -f none were selected.")
        return

    cli.fol.mkdir(parents=True, exist_ok=True)

    if cli.mode == "fair":
        cfg = build_config(pofff_path=pofff_path, cli=cli, toml={})
        cfg.path = pofff_path
        cfg.figures = "all"
        cfg.times = "24,48,72,96,120"
        cfg.experiment = "run2"

    elif cli.mode == "none":
        cfg = build_config(pofff_path=pofff_path, cli=cli, toml={})
        _prepare_simulation(cfg)

    else:
        toml = load_toml(args.input, args.mode)
        cfg = build_config(pofff_path=pofff_path, cli=cli, toml=toml.copy())
        postprocess_config(cfg, toml)
        _prepare_simulation(cfg)

    _run_simulation_steps(cfg)

    if cfg.figures in {"basic", "all"} and cfg.mode != "files":
        _generate_figures(cfg)

    msg = (
        "The files have been written to"
        if cfg.mode == "files"
        else "The results have been written to"
    )
    pofff_success(f"{msg.lower()} ", str(cfg.fol), [])


def _build_cli_config(args: argparse.Namespace, *, pofff_path: Path) -> CliConfig:
    """Build normalized CLI configuration object.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command-line arguments.
    pofff_path : Path
        Package root containing templates, geology, jobs, and benchmark data.

    Returns
    -------
    CliConfig
        Normalized command-line configuration."""
    output = Path(args.output).absolute()

    location = (
        pofff_path
        / "fluidflower"
        / "cssr"
        / f"conmin{'5e-2' if float(args.minimumconcentration) == 5e-2 else '1e-1'}"
    )

    return CliConfig(
        fol=output,
        deck=output,
        jobs=output,
        experiment=f"run{args.experiment[-1]}",
        times=args.times,
        msat=args.minimumsaturation,
        mcon=args.minimumconcentration,
        mode=args.mode,
        figures=args.figures,
        location=str(location),
        use=args.use,
    )


def _prepare_simulation(cfg: PofffConfig) -> None:
    """Prepare directories and generate all input files.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state."""
    if cfg.mode == "none":
        cfg.deck = cfg.deck / "deck"
        cfg.jobs = cfg.jobs / "jobs"
    elif cfg.mode in {"files", "ert", "everest", "data"} and cfg.everert:
        cfg.deck = cfg.deck / "deck"
        cfg.jobs = cfg.jobs / "jobs"
        for sub in ("deck", "jobs"):
            (cfg.fol / sub).mkdir(parents=True, exist_ok=True)

    if cfg.mode in ["everest", "ert"] or (cfg.everert and cfg.mode == "files"):
        _prepare_jobs_folder(cfg)

    if cfg.mode not in {"data", "none"}:
        pofff_info("generating the input files, please wait...")
        grid_and_properties(cfg)
        write_files(cfg)


def _prepare_jobs_folder(cfg: PofffConfig) -> None:
    """Copy job scripts into output/jobs and make them executable.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state."""
    src = cfg.path / "jobs"
    dst = cfg.fol / "jobs"
    shutil.copytree(src, dst, dirs_exist_ok=True)

    for script in ("data", "delete", "metric"):
        script_path = dst / f"{script}.py"
        if script_path.exists():
            script_path.chmod(0o755)


def _run_simulation_steps(cfg: PofffConfig) -> None:
    """Run the selected execution mode.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state."""
    os.chdir(cfg.fol)

    if cfg.mode == "single":
        pofff_info("running the simulation, please wait...")
        flow(cfg)
        pofff_info("generating the data, please wait...")
        data(cfg)
    elif cfg.mode == "data":
        data(cfg)
    elif cfg.mode == "ert":
        ert(cfg)
    elif cfg.mode == "everest":
        everest()
    elif cfg.mode in {"files", "fair", "none"}:
        pass
    else:
        pofff_error(f"unknown mode {cli_error_value(f'-m {cfg.mode}')}.")


def _generate_figures(cfg: PofffConfig) -> None:
    """Generate benchmark plots and comparison figures.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state."""
    if shutil.which("latex") is None:
        pofff_tip(
            "LaTeX is recommended for high-quality figures. "
            "See the pofff documentation for installation instructions."
        )
    if (cfg.fol / "jobs").exists():
        postprocess(cfg)

    figures_dir = cfg.fol / "figures" / "best_simulation"
    if figures_dir.exists():
        os.chdir(figures_dir)
    else:
        os.chdir(cfg.fol)

    pofff_info("generating the benchmark files, please wait...")
    benchmark(cfg)


def _parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """Define and parse command-line arguments.

    Parameters
    ----------
    argv : list[str] | None, optional
        Arguments to parse instead of the process command line.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments or the corresponding runtime configuration."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            "pofff, a Python tool for history matching FluidFlower images "
            "using OPM Flow, ERT, and Everest."
        ),
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str.strip,
        default="input.toml",
        help="Input TOML configuration file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str.strip,
        default="output",
        help="Output directory name",
    )
    parser.add_argument(
        "-f",
        "--figures",
        type=str.strip,
        choices=["all", "basic", "none"],
        default="basic",
        help="Figure generation mode: 'all', 'basic', or 'none' "
        "('basic' skips Wasserstein plots)",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str.strip,
        choices=["single", "files", "data", "everest", "ert", "fair", "none"],
        default="single",
        help="Execution mode",
    )
    parser.add_argument(
        "-t",
        "--times",
        type=str.strip,
        default="0.25",
        help="Evaluation times in hours, comma-separated",
    )
    parser.add_argument(
        "-e",
        "--experiment",
        type=str.strip,
        choices=["C1", "C2", "C3", "C4", "C5"],
        default="C2",
        help="Experimental dataset",
    )
    parser.add_argument(
        "-s",
        "--minimumsaturation",
        type=str.strip,
        default="1e-2",
        help="Minimum gas saturation threshold",
    )
    parser.add_argument(
        "-c",
        "--minimumconcentration",
        type=str.strip,
        default="1e-1",
        help="Minimum dissolved CO2 concentration threshold",
    )
    parser.add_argument(
        "-u",
        "--use",
        type=str.strip,
        choices=["0", "1"],
        default="1",
        help="Use precomputed Wasserstein distances if available "
        "(set to '0' to recompute)",
    )
    return parser.parse_args(argv)


def _validate_arguments(cmdargs: argparse.Namespace) -> None:
    """Validate command-line arguments and incompatible operations.

    Parameters
    ----------
    cmdargs : argparse.Namespace
        Parsed command-line arguments.

    Raises
    ------
    SystemExit
        If an argument is invalid or incompatible with the selected workflow."""
    if not cmdargs.output:
        pofff_error(
            f"invalid value {cli_error_value('-o')}, the output directory cannot be empty."
        )
    mode = cmdargs.mode
    if mode not in {"fair", "none"}:
        if not cmdargs.input:
            pofff_error(
                f"invalid value {cli_error_value('-i')}, the input file cannot be empty."
            )
        if not cmdargs.input.lower().endswith(".toml"):
            pofff_error(
                f"invalid extension {cli_error_value(f'-i {cmdargs.input}')}, "
                f"expected {cli_correct_value('.toml')}."
            )
    times = cmdargs.times
    try:
        time_values = [float(value.strip()) for value in times.split(",")]
    except ValueError:
        time_values = []
    if not time_values or any(
        not math.isfinite(value) or value <= 0 for value in time_values
    ):
        pofff_error(
            f"invalid value {cli_error_value(f'-t {times}')}, expected positive "
            f"finite numbers separated by commas, {cli_correct_value('e.g., -t 24,48,72')}."
        )
    minimum_saturation = cmdargs.minimumsaturation
    try:
        minimum_saturation_value = float(minimum_saturation)
    except ValueError:
        minimum_saturation_value = float("nan")
    if (
        not math.isfinite(minimum_saturation_value)
        or minimum_saturation_value < 0
        or minimum_saturation_value > 1
    ):
        pofff_error(
            f"invalid value {cli_error_value(f'-s {minimum_saturation}')}, expected a "
            f"finite number in {cli_correct_value('[0, 1]')}."
        )
    minimum_concentration = cmdargs.minimumconcentration
    try:
        minimum_concentration_value = float(minimum_concentration)
    except ValueError:
        minimum_concentration_value = float("nan")
    valid_concentrations = [5e-2, 1e-1]
    if (
        not math.isfinite(minimum_concentration_value)
        or minimum_concentration_value not in valid_concentrations
    ):
        pofff_error(
            f"invalid value {cli_error_value(f'-c {minimum_concentration}')}, expected "
            f"{cli_correct_value('5e-2')} or {cli_correct_value('1e-1')}."
        )
    if mode == "fair":
        ignored_options = {
            "-i": ("input", "input.toml"),
            "-f": ("figures", "basic"),
            "-t": ("times", "0.25"),
            "-e": ("experiment", "C2"),
        }
        invalid_options = [
            option
            for option, (name, default) in ignored_options.items()
            if getattr(cmdargs, name) != default
        ]
        if invalid_options:
            pofff_error(
                f"invalid combination {cli_error_value('-m fair; ' + ', '.join(invalid_options))}; "
                "the FAIR workflow uses its own input data, figure mode, evaluation "
                "times, and experiment."
            )
    if mode == "files" and cmdargs.figures == "all":
        pofff_error(
            f"invalid combination {cli_error_value('-m files -f all')}; file generation "
            f"does not create figures, use {cli_correct_value('-f none')} or omit -f."
        )
