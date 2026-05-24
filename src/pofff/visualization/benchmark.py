#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Generate benchmark-format figures and comparisons."""

import argparse
import shutil
import sys
import subprocess
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt


def run_benchmark(argv=None):
    """Main entry point for generating benchmark figures."""
    cfg = load_parser(argv)

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

    benchmark(cfg)


def benchmark(cfg):
    """Run figure generation and benchmark comparisons."""

    def run(cmd):
        """Execute external command with logging."""
        print("Running:", " ".join(map(str, cmd)))
        subprocess.run(cmd, check=True)

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
            print(
                "ERROR: Wasserstein distance figures require times "
                "'24,48,72,96,120'."
            )
            sys.exit(1)

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


def load_parser(argv):
    """Define and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Manage the generation of benchmark figures.",
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

    return vars(parser.parse_known_args(argv)[0])


if __name__ == "__main__":
    run_benchmark()
