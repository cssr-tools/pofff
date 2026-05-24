# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Main entry script for pofff."""

import os
import shutil
import argparse
from pathlib import Path

from pofff.config.config import CliConfig, PofffConfig
from pofff.utils.inputvalues import load_toml, build_config, postprocess_config
from pofff.utils.runs import flow, data, benchmark, everest, ert, postprocess
from pofff.utils.writefile import write_files
from pofff.utils.mapproperties import grid_and_properties


def main() -> None:
    """Main pofff execution routine."""
    args = parse_args()
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


def parse_args():
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
    return parser.parse_known_args()[0]
