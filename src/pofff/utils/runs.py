# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Execute simulation, data, history-matching, and plotting workflows.

The functions run OPM Flow and the maintained data scripts, launch ERT or
Everest, postprocess ensemble results, and coordinate benchmark maps, sparse
values, Wasserstein comparisons, and error tables."""

import subprocess
from collections.abc import Sequence
from pathlib import Path

from pofff.config.config import PofffConfig
from pofff.utils.terminal import cli_correct_value, cli_error_value, pofff_error
from pofff.visualization.benchmark import run_benchmark
from pofff.visualization.error_table import run_error_table
from pofff.visualization.everert import run_everert
from pofff.visualization.maps import run_maps
from pofff.visualization.sparse_values import main as sparse_values


def _run(cmd: Sequence[str]) -> None:
    """Execute a command and abort if it fails.

    Parameters
    ----------
    cmd : Sequence[str]
        Command and arguments to execute without a shell.

    Raises
    ------
    subprocess.CalledProcessError
        If the command exits with a nonzero status."""
    subprocess.run(cmd, check=True)


def flow(cfg: PofffConfig) -> None:
    """Run the OPM Flow simulator with configured options.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.

    Raises
    ------
    subprocess.CalledProcessError
        If OPM Flow exits with a nonzero status."""
    _run(
        cfg.flow.split(" ")
        + [f"--output-dir={cfg.fol}", str(Path(cfg.fol) / f"{cfg.data}.DATA")]
    )


def data(cfg: PofffConfig) -> None:
    """Generate benchmark time-series and spatial data.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.

    Raises
    ------
    subprocess.CalledProcessError
        If a data or metric script exits with a nonzero status."""
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
    """Generate benchmark figures and comparisons.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state."""
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

    sparse_values(timeseries_file=f"{cfg.location}/time_series.csv")

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
            pofff_error(
                "the error table requires a 120-hour simulation, no "
                f"{cli_error_value(f'-t {cfg.times}')} but "
                f"{cli_correct_value('-t 24,48,72,96,120')}."
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
    """Run Everest optimization and skip interactive prompts.

    Raises
    ------
    subprocess.CalledProcessError
        If Everest exits with a nonzero status."""
    _run(["everest", "run", "everest.yml", "--skip-prompt"])


def ert(cfg: PofffConfig) -> None:
    """Run ERT with configured arguments.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.

    Raises
    ------
    subprocess.CalledProcessError
        If ERT exits with a nonzero status."""
    _run(["ert", *(cfg.ertargs or "").split(), "ert.txt"])


def postprocess(cfg: PofffConfig) -> None:
    """Postprocess ERT and Everest simulation results.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state."""
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
