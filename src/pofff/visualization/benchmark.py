#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Generate FluidFlower benchmark figures and comparisons.

The module configures plotting and dispatches the maintained comparison scripts
for time series, sparse values, segmented Wasserstein distances, and mean
distance summaries."""

import argparse
import shutil
import subprocess
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

from pofff.utils.terminal import cli_correct_value, pofff_error, pofff_info


def run_benchmark(argv=None):
    """Configure and generate benchmark comparison figures.

    Parameters
    ----------
    argv : object, optional
        Arguments to parse instead of the process command line."""
    cfg = _parse_arguments(argv)

    cfg["s"] = cfg["minimumsaturation"]
    cfg["c"] = cfg["minimumconcentration"]
    cfg["p"] = Path(cfg["path"]) / "fluidflower"
    cfg["u"] = bool(int(cfg["use"]))
    cfg["f"] = cfg["figures"].strip()

    matplotlib.rc("font", family="monospace", weight="normal", size=14)

    plt.rcParams.update(
        {
            "text.usetex": shutil.which("latex") is not None,
            "legend.columnspacing": 0.9,
            "legend.handlelength": 3.5,
            "legend.fontsize": 14,
            "lines.linewidth": 4,
            "axes.titlesize": 14,
            "axes.grid": False,
            "figure.figsize": (16, 8),
        }
    )

    _generate_benchmark_comparisons(cfg)


def run(cmd):
    """Execute external command with logging.

    Parameters
    ----------
    cmd : object
        Command and arguments to execute without a shell."""
    pofff_info(f"running {' '.join(map(str, cmd))}")
    subprocess.run(cmd, check=True)


def _generate_benchmark_comparisons(cfg):
    """Run the maintained benchmark comparison scripts.

    Parameters
    ----------
    cfg : object
        Shared pofff configuration and derived runtime state."""

    run(
        [
            "python3",
            cfg["p"] / "general/evaluation/compare_time_series_pofff.py",
            "-p",
            str(cfg["p"]) + "/",
            "-l",
            cfg["location"],
            "-a",
            cfg["add"],
        ]
    )

    if Path("sparse_data.csv").exists():
        run(
            [
                "python3",
                cfg["p"] / "general/evaluation/compare_sparse_data_pofff.py",
                "-p",
                str(cfg["p"]) + "/",
                "-l",
                cfg["location"],
                "-a",
                cfg["add"],
            ]
        )

    if cfg["f"] == "all":
        if cfg["times"] != "24,48,72,96,120":
            pofff_error(
                "Wasserstein distance figures require "
                f"{cli_correct_value('-t 24,48,72,96,120')}."
            )

        if float(cfg["s"]) == 0.01 and float(cfg["c"]) in (0.05, 0.1) and cfg["u"]:
            run(
                [
                    "python3",
                    cfg["p"]
                    / "general/evaluation/calculate_segmented_emds_simplified_pofff.py",
                    "-p",
                    str(cfg["p"]) + "/",
                    "-satmin",
                    cfg["s"],
                    "-conmin",
                    cfg["c"],
                    "-l",
                    cfg["location"],
                    "-a",
                    cfg["add"],
                ]
            )
        else:
            run(
                [
                    "python3",
                    cfg["p"] / "general/evaluation/calculate_segmented_emds_pofff.py",
                    "-p",
                    str(cfg["p"]) + "/",
                    "-satmin",
                    cfg["s"],
                    "-conmin",
                    cfg["c"],
                    "-l",
                    cfg["location"],
                    "-a",
                    cfg["add"],
                ]
            )

        run(
            [
                "python3",
                cfg["p"] / "general/evaluation/means_from_segmented_distances_pofff.py",
                "-satmin",
                cfg["s"],
                "-conmin",
                cfg["c"],
                "-a",
                cfg["add"],
            ]
        )


def _parse_arguments(argv):
    """Define and parse command-line arguments.

    Parameters
    ----------
    argv : object
        Arguments to parse instead of the process command line."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Manage the generation of _generate_benchmark_comparisons figures.",
    )

    parser.add_argument("-c", "--minimumconcentration", default=0.1)
    parser.add_argument("-s", "--minimumsaturation", default=0.01)
    parser.add_argument("-p", "--path", default="./")
    parser.add_argument("-t", "--times", default="24,48,72,96,120")
    parser.add_argument("-f", "--figures", default="basic")
    parser.add_argument("-l", "--location", default=".")
    parser.add_argument("-a", "--add", default="1")
    parser.add_argument(
        "-u",
        "--use",
        default="1",
        help="Use precomputed Wasserstein distances (1=yes, 0=no)",
    )

    return vars(parser.parse_args(argv))


if __name__ == "__main__":
    run_benchmark()
