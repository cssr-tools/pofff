# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0914

"""
Table 7 and Figure 12 in the pofff paper:
Profiling workflow wall-time and OPM Flow simulation statistics.
"""

import shutil
import subprocess
import time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from mako.template import Template
from opm.io.ecl import ESmry as OpmSummary

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

NCORES = [64, 32, 16, 8, 4, 2, 1]  # Modify according to your resources
TEMPLATE_FILE = "appendixc.mako"

WORKDIR = Path("appendixc")
PROFILING_DIR = Path("profiling")

TIMESTEPS = "24,48,72,96,120"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def run(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a command and fail loudly if it fails."""
    subprocess.run(cmd, check=True, cwd=cwd)


def render_toml(cores: int) -> None:
    """Render appendixc.toml for a given core count."""
    template = Template(filename=TEMPLATE_FILE)
    rendered = template.render(
        cores=cores,
        rng=7,
        cnv=1e-2,
        cnv_relaxed=1,
    )
    Path("appendixc.toml").write_text(rendered, encoding="utf8")


def collect_simulation_times(root: Path) -> list:
    """Collect TCPU times from successful OPM Flow runs."""
    times: list[float] = []

    if (root / "batch_0/realization-0").is_dir():
        realization = "realization-0"
    else:
        realization = "realization_0"

    for batch in sorted(root.iterdir()):
        realization_num = batch / realization
        if not realization_num.exists():
            continue

        for evaluation in sorted(realization_num.iterdir()):
            if (evaluation / "OK").exists():
                summary = OpmSummary(str(evaluation / "APPENDIXC.SMSPEC"))
                times.append(summary["TCPU"][-1])

    return times


# -----------------------------------------------------------------------------
# Main workflow
# -----------------------------------------------------------------------------


def main() -> None:
    """Main entry point for Table 7 and Figure 12 in the pofff paper."""
    PROFILING_DIR.mkdir(exist_ok=True)

    total_times: list[float] = []

    for cores in NCORES:
        render_toml(cores)

        # --- Preprocessing ----------------------------------------------------
        t0 = time.perf_counter()
        run(
            [
                "pofff",
                "-i",
                "appendixc.toml",
                "-o",
                "appendixc",
                "-m",
                "files",
                "-t",
                TIMESTEPS,
            ]
        )
        t1 = time.perf_counter()
        preprocessing = t1 - t0

        # --- Optimization -----------------------------------------------------
        t0 = time.perf_counter()
        run(["everest", "run", "everest.yml", "--skip-prompt"], cwd=WORKDIR)
        t1 = time.perf_counter()
        optimization = t1 - t0

        # --- Postprocessing ---------------------------------------------------
        t0 = time.perf_counter()
        run(
            [
                "pofff",
                "-i",
                "appendixc.toml",
                "-o",
                "appendixc",
                "-m",
                "none",
                "-t",
                TIMESTEPS,
            ]
        )
        t1 = time.perf_counter()
        postprocessing = t1 - t0

        total_time = preprocessing + optimization + postprocessing
        total_times.append(total_time)

        # --- Simulation statistics -------------------------------------------
        sim_root = WORKDIR / "everest_output" / "sim_output"
        times = collect_simulation_times(sim_root)

        nruns = len(times)
        q1, median, q3 = np.percentile(times, [25, 50, 75])
        iqr = q3 - q1

        # --- Profiling report -------------------------------------------------
        text = (
            f"\nProfiling the workflow time in seconds using {cores} cores\n"
            f"Preprocessing: {preprocessing:.2f}\n"
            # Only meaningful for the 1‑core case (Table 7)
            f"OPM Flow: {np.sum(times):.2f}\n"
            f"Optimization: {optimization - np.sum(times):.2f}\n"
            f"Postprocessing: {postprocessing:.2f}\n"
            f"Sum: {total_time:.2f}\n"
            f"\nProfiling the simulation time of {nruns} OPM Flow runs in seconds\n"
            f"Median: {median:.2f}\n"
            f"First Quartile (Q1): {q1:.2f}\n"
            f"Third Quartile (Q3): {q3:.2f}\n"
            f"Interquartile Range (IQR): {iqr:.2f}\n"
            f"Median ± IQR: {median:.2f} ± {iqr:.2f}"
        )

        (PROFILING_DIR / f"profiling_ncpu_{cores}.txt").write_text(
            text, encoding="utf8"
        )

        shutil.rmtree(WORKDIR, ignore_errors=True)
        Path("appendixc.toml").unlink(missing_ok=True)

    # -------------------------------------------------------------------------
    # Plot: Figure 12
    # -------------------------------------------------------------------------

    font = {"family": "normal", "weight": "normal", "size": 24}
    matplotlib.rc("font", **font)

    plt.rcParams.update(
        {
            "text.usetex": shutil.which("latex") is not None,
            "font.family": "monospace",
            "legend.columnspacing": 0.9,
            "legend.handlelength": 3.5,
            "legend.fontsize": font["size"],
            "lines.linewidth": 4,
            "axes.titlesize": font["size"],
            "axes.grid": True,
            "figure.figsize": (12, 20),
        }
    )

    fig, axis = plt.subplots()
    axis.plot(NCORES, total_times, color="k", ls="--")
    axis.set_ylabel("Wall time [s]")
    axis.set_xlabel("Number of cores")
    axis.set_xticks(NCORES[::-1])
    axis.set_yticks(total_times[::-1])
    # axis.set_ylim(1500, 30000)

    fig.savefig(PROFILING_DIR / "figure12.png")


if __name__ == "__main__":
    main()
