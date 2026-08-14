# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912

"""Main entry script for pofff."""

import argparse
import math
import os
import shutil
from pathlib import Path

from pofff.config.config import CliConfig, PofffConfig
from pofff.utils.inputvalues import build_config, load_toml, postprocess_config
from pofff.utils.mapproperties import grid_and_properties
from pofff.utils.runs import benchmark, data, ert, everest, flow, postprocess
from pofff.utils.writefile import write_files


def main(argv: list[str] | None = None) -> None:
    """Main pofff execution routine."""
    args = parse_args(argv)
    check_cmdargs(args)
    pofff_path = Path(__file__).resolve().parents[1]

    cli = cli_config(args, pofff_path=pofff_path)

    if cli.figures == "none" and cli.mode == "none":
        print("Nothing to do since -m none -f none")
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
        prepare_simulation(cfg)

    else:
        toml = load_toml(args.input)
        cfg = build_config(pofff_path=pofff_path, cli=cli, toml=toml.copy())
        postprocess_config(cfg, toml)
        prepare_simulation(cfg)

    run_simulation_steps(cfg)

    if cfg.figures in {"basic", "all"} and cfg.mode != "files":
        generate_figures(cfg)

    msg = (
        "The files have been written to"
        if cfg.mode == "files"
        else "The results have been written to"
    )
    print(f"\n{msg} {cfg.fol}")


def cli_config(args: argparse.Namespace, *, pofff_path: Path) -> CliConfig:
    """Build normalized CLI configuration object."""
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


def prepare_simulation(cfg: PofffConfig) -> None:
    """Prepare directories and generate all input files."""
    if cfg.mode == "none":
        cfg.deck = cfg.deck / "deck"
        cfg.jobs = cfg.jobs / "jobs"
    elif cfg.mode in {"files", "ert", "everest", "data"} and cfg.everert:
        cfg.deck = cfg.deck / "deck"
        cfg.jobs = cfg.jobs / "jobs"
        for sub in ("deck", "jobs"):
            (cfg.fol / sub).mkdir(parents=True, exist_ok=True)

    if cfg.mode in ["everest", "ert"] or (cfg.everert and cfg.mode == "files"):
        prepare_jobs_folder(cfg)

    if cfg.mode not in {"data", "none"}:
        print("\nGenerating the input files, please wait.")
        grid_and_properties(cfg)
        write_files(cfg)


def prepare_jobs_folder(cfg: PofffConfig) -> None:
    """Copy job scripts into output/jobs and make them executable."""
    src = cfg.path / "jobs"
    dst = cfg.fol / "jobs"
    shutil.copytree(src, dst, dirs_exist_ok=True)

    for script in ("data", "delete", "metric"):
        script_path = dst / f"{script}.py"
        if script_path.exists():
            script_path.chmod(0o755)


def run_simulation_steps(cfg: PofffConfig) -> None:
    """Run the selected execution mode."""
    os.chdir(cfg.fol)

    if cfg.mode == "single":
        print("\nRunning the simulation, please wait.")
        flow(cfg)
        print("\nGenerating the data, please wait.")
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
        raise SystemExit(f"Unknown -m {cfg.mode}")


def generate_figures(cfg: PofffConfig) -> None:
    """Generate benchmark plots and comparison figures."""
    if shutil.which("latex") is None:
        print(
            "\nLaTeX is recommended for high-quality figures.\n"
            "See the pofff documentation for installation instructions."
        )
    if (cfg.fol / "jobs").exists():
        postprocess(cfg)

    figures_dir = cfg.fol / "figures" / "best_simulation"
    if figures_dir.exists():
        os.chdir(figures_dir)
    else:
        os.chdir(cfg.fol)

    print("\nGenerating the benchmark files, please wait.")
    benchmark(cfg)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Define and parse command-line arguments."""
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


def check_cmdargs(cmdargs: argparse.Namespace) -> None:
    """Validate command-line arguments and incompatible operations.

    The checks cover input and output paths, evaluation times, saturation and
    concentration thresholds, options ignored by specialized workflows, and
    combinations that do not result in any operation.

    Parameters
    ----------
    cmdargs
        Parsed arguments returned by :func:`parse_args`.

    Raises
    ------
    SystemExit
        If an argument is invalid or an incompatible combination is requested.
    """
    if not cmdargs.output:
        print("\nInvalid value for '-o', the output directory cannot be empty.\n")
        raise SystemExit(1)
    mode = cmdargs.mode
    if mode not in {"fair", "none"}:
        if not cmdargs.input:
            print("\nInvalid value for '-i', the input file cannot be empty.\n")
            raise SystemExit(1)
        if not cmdargs.input.lower().endswith(".toml"):
            print(
                f"\nInvalid extension for input file '-i {cmdargs.input}', "
                "the valid extension is .toml.\n"
            )
            raise SystemExit(1)
    times = cmdargs.times
    try:
        time_values = [float(value.strip()) for value in times.split(",")]
    except ValueError:
        time_values = []
    if not time_values or any(
        not math.isfinite(value) or value <= 0 for value in time_values
    ):
        print(
            f"\nInvalid value '-t {times}', expected positive finite numbers "
            "separated by commas, e.g., '-t 24,48,72'.\n"
        )
        raise SystemExit(1)
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
        print(
            f"\nInvalid value '-s {minimum_saturation}', expected a finite "
            "number between 0 and 1.\n"
        )
        raise SystemExit(1)
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
        print(
            f"\nInvalid value '-c {minimum_concentration}', valid values are "
            "'5e-2' and '1e-1'.\n"
        )
        raise SystemExit(1)
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
            print(
                "\nInvalid option for '-m fair'; this workflow uses its own "
                "input data, figure mode, evaluation times, and experiment. "
                f"Invalid options: {', '.join(invalid_options)}.\n"
            )
            raise SystemExit(1)
    if mode == "files" and cmdargs.figures == "all":
        print(
            "\nInvalid combination, '-f all' cannot be used with '-m files' "
            "because this mode only generates input files. Use '-f none' or "
            "omit the '-f' option.\n"
        )
        raise SystemExit(1)
