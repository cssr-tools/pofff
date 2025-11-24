# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Table C3 and Figure C4 in the pofff paper"""

import os
import shutil
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from opm.io.ecl import ESmry as OpmSummary
from mako.template import Template

ncores = [64, 32, 16, 8, 4, 2, 1]

total_times = []
mytemplate = Template(filename="appendixc.mako")
os.system("mkdir accuracy")
for cores in ncores:
    var = {"cores": cores, "random_seed": 7, "cnv": 1e-2, "cnv_relaxed": 1}
    filledtemplate = mytemplate.render(**var)
    with open(
        "appendixc.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    start_time = time.perf_counter()
    os.system("pofff -i appendixc.toml -o appendixc -m files -t 24,48,72,96,120")
    end_time = time.perf_counter()
    preprocessing = end_time - start_time
    os.chdir("appendixc")
    start_time = time.perf_counter()
    os.system("everest run everest.yml")
    end_time = time.perf_counter()
    optimization = end_time - start_time
    os.chdir("..")
    start_time = time.perf_counter()
    os.system("pofff -i appendixc.toml -o appendixc -m none -t 24,48,72,96,120")
    end_time = time.perf_counter()
    postprocessing = end_time - start_time
    total_times.append(preprocessing + optimization + postprocessing)
    nruns, times, root = 0, [], "appendixc/everest_output/sim_output"
    for n in range(len(os.listdir(root))):
        for m in range(len(os.listdir(f"{root}/batch_{n}/realization_0"))):
            if os.path.exists(f"{root}/batch_{n}/realization_0/evaluation_{m}/OK"):
                times.append(
                    OpmSummary(
                        f"{root}/batch_{n}/realization_0/evaluation_{m}/APPENDIXC.SMSPEC"
                    )["TCPU"][-1]
                )
                nruns += 1
    q1, median, q3 = (
        np.percentile(times, 25),
        np.median(times),
        np.percentile(times, 75),
    )
    iqr = q3 - q1

    text = f"\nProfiling the workflow time in seconds using {cores} cores\n"
    text += f"Preprocessing: {preprocessing:.2f}\n"
    # This only makes sense when running with one core, which corresponds to the values in Table C3
    text += f"OPM Flow: {np.sum(times):.2f}\n"
    text += f"Optimization: {optimization - np.sum(times):.2f}\n"
    text += f"Postprocessing: {postprocessing:.2f}\n"
    text += f"Sum: {total_times[-1]:.2f}\n"
    text += f"\nProfiling the simulation time of {nruns} OPM Flow runs in seconds\n"
    text += f"Median: {median:.2f}\n"
    text += f"First Quartile (Q1): {q1:.2f}\n"
    text += f"Third Quartile (Q3): {q3:.2f}\n"
    text += f"Interquartile Range (IQR): {iqr:.2f}\n"
    text += f"Median ± IQR: {median:.2f} ± {iqr:.2f}"
    with open(
        f"profiling/profiling_ncpu_{cores}.txt",
        "w",
        encoding="utf8",
    ) as file:
        file.write(text)
    os.system("rm -rf appendixc appendixc.toml")

font = {"family": "normal", "weight": "normal", "size": 24}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": shutil.which("latex") != "None",
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
axis.plot(ncores, total_times, color="k", ls="--")
axis.set_ylabel("Wall time [s]")
axis.set_xlabel("Number of cores")
axis.set_xticks(ncores[::-1])
axis.set_yticks(total_times[::-1])
axis.set_ylim(1500, 30000)
fig.savefig("profiling/figurec4.png")
