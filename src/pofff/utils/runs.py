# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Utility functions for running simulations, processing data,
and generating benchmark plots."""

import subprocess
from collections.abc import Sequence
from pathlib import Path

from pofff.config.config import PofffConfig
from pofff.visualization.benchmark import run_benchmark
from pofff.visualization.error_table import run_error_table
from pofff.visualization.everert import run_everert
from pofff.visualization.maps import run_maps


def _run(cmd: Sequence[str]) -> None:
    """Execute a command and abort if it fails."""
    subprocess.run(cmd, check=True)


def flow(cfg: PofffConfig) -> None:
    """Run the OPM Flow simulator with configured options."""
    _run(
        cfg.flow.split(" ")
        + [f"--output-dir={cfg.fol}", str(Path(cfg.fol) / f"{cfg.data}.DATA")]
    )


def data(cfg: PofffConfig) -> None:
    """Generate benchmark time-series and spatial data."""
    _run(
        [
            "python",
            str(cfg.path / "jobs" / "data.py"),
            "-m",
            str(Path(cfg.deck) / "cellmap.npy"),
            "-t",
            cfg.times,
        ]
    )

    _run(
        [
            "python",
            str(cfg.path / "jobs" / "metric.py"),
            "-e",
            cfg.experiment,
            "-p",
            str(cfg.path),
            "-t",
            cfg.times,
            "-s",
            cfg.msat,
            "-c",
            cfg.mcon,
        ]
    )


def benchmark(cfg: PofffConfig) -> None:
    """Generate benchmark figures and comparisons."""
    args = [
        "-e",
        cfg.experiment,
        "-t",
        cfg.times,
        "-p",
        str(cfg.path),
        "-s",
        cfg.msat,
        "-c",
        cfg.mcon,
        "-l",
        "." if cfg.mode != "fair" else cfg.location,
    ]
    run_maps(args)

    if cfg.mode != "fair":
        _run(
            [
                "python",
                str(cfg.path / "visualization" / "sparse_values.py"),
            ]
        )

    args = [
        "-f",
        cfg.figures,
        "-p",
        str(cfg.path),
        "-s",
        cfg.msat,
        "-t",
        cfg.times,
        "-c",
        cfg.mcon,
        "-l",
        cfg.location,
        "-a",
        str(int(cfg.mode != "fair")),
        "-u",
        cfg.use,
    ]
    run_benchmark(args)

    if cfg.figures == "all":
        if cfg.times != "24,48,72,96,120":
            print(
                "The error table requires a 120-hour simulation.\n"
                "Please run with -t '24,48,72,96,120' "
                f"(current: -t {cfg.times})."
            )
        else:
            args = [
                "-p",
                str(cfg.path),
                "-s",
                cfg.msat,
                "-c",
                cfg.mcon,
                "-l",
                cfg.location,
                "-a",
                str(int(cfg.mode != "fair")),
            ]
            run_error_table(args)


def everest() -> None:
    """Run Everest optimization and skip interactive prompts."""
    _run(["everest", "run", "everest.yml", "--skip-prompt"])


def ert(cfg: PofffConfig) -> None:
    """Run ERT with configured arguments."""
    _run(["ert", *(cfg.ertargs or "").split(), "ert.txt"])


def postprocess(cfg: PofffConfig) -> None:
    """Postprocess ERT and Everest simulation results."""
    args = [
        "-e",
        str(cfg.path),
        "-s",
        cfg.msat,
        "-c",
        cfg.mcon,
        "-r",
        cfg.experiment,
        "-t",
        cfg.times,
        "-m",
        str(Path(cfg.deck) / "cellmap.npy"),
    ]
    run_everert(args)
