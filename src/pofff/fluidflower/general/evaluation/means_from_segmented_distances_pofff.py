#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/evaluation/means_from_segmented_distances.py
# pylint: disable=R0912,R0913,R0914,R0915,R0917,C0103

"""
Generate the Wasserstein distance plots.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

font = {"family": "normal", "weight": "normal", "size": 12}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "monospace",
        "legend.columnspacing": 1.5,
        "legend.handlelength": 1.0,
    }
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "-satmin",
    "--minimumsaturation",
    type=float,
    default=1e-2,
    help="The minimum saturation above which gaseous CO2 is considered for the segmentation.",
)
parser.add_argument(
    "-conmin",
    "--minimumconcentration",
    type=float,
    default=1e-1,
    help="The minimum concentration above which CO2 is considered to be dissolved in the "
    "liquid phase for the segmentation.",
)
parser.add_argument(
    "-a",
    "--add",
    default="1",
    help="Add the result to the plots ('1' by default).",
)
cmdargs = vars(parser.parse_args())
add = cmdargs["add"] == "1"
groups = [
    "Austin",
    "CSIRO",
    "Delft-DARSim",
    "Delft-DARTS",
    "Heriot-Watt",
    "LANL",
    "Melbourne",
    "Stanford",
    "Stuttgart",
    "MIT_M1",
    "CSSR",
]
colors = [
    "C0",
    "C1",
    "C2",
    "C3",
    "C4",
    "C6",
    "C7",
    "C8",
    "C9",
    (0.9, 0.9, 0.9),
    "#14b825",
]

if add:
    groups += ["YOURS"]
    colors += ["#FF1493"]
    marker = "X"

nBaseGroups = 9
marker_mit = "o"
includeLANL = True
numGroups = len(groups)
numExps = 5
numGroupsPlusExps = numGroups + numExps


distances = np.loadtxt(
    f"segmented_distances_satmin-{cmdargs['minimumsaturation']}_conmin-"
    f"{cmdargs['minimumconcentration']}.csv",
    delimiter=",",
)

fig, axs = plt.subplots(2, 3, figsize=(9, 6))

# The calculated distances have the unit of normalized mass times meter.
# Multiply by 8.5, the injected mass of CO2 in g, and 100, to convert to g.cm.
A = 850 * distances[:numGroupsPlusExps, :numGroupsPlusExps]

# set LANL distances to zero
if includeLANL:
    A[5, :] = 0
    A[:, 5] = 0

meanA_exp = np.mean(A[numGroups:, :], axis=0)
# take correct avg due to missing LANL data, exclude MIT_M1 and CSSR
meanA_fore = np.mean(A[:nBaseGroups, :], axis=0) * nBaseGroups / (nBaseGroups - 1)

axs[0][0].scatter(
    meanA_exp[1], meanA_fore[1], s=96, c=colors[1], label=groups[1], zorder=5
)
axs[0][0].scatter(
    meanA_exp[9],
    meanA_fore[9],
    s=72,
    color=colors[9],
    marker=marker_mit,
    label=groups[9],
    edgecolors="k",
    zorder=5,
)
axs[0][0].scatter(
    meanA_exp[10],
    meanA_fore[10],
    s=400,
    marker="*",
    label=groups[10],
    edgecolors="k",
    c=colors[10],
    zorder=5,
)
if add:
    axs[0][0].scatter(
        meanA_exp[11],
        meanA_fore[11],
        s=100,
        c=colors[11],
        marker=marker,
        label=groups[11],
        edgecolors="k",
        zorder=5,
    )
axs[0][0].scatter(
    meanA_exp[numGroups],
    meanA_fore[numGroups],
    s=96,
    c="k",
    marker="d",
    label=r"\textrm{exp. run 1}",
    zorder=5,
)
axs[0][0].scatter(
    meanA_exp[numGroups + 1],
    meanA_fore[numGroups + 1],
    s=96,
    c="k",
    marker="^",
    label=r"\textrm{exp. run 2}",
    zorder=5,
)
axs[0][0].scatter(
    meanA_exp[numGroups + 2],
    meanA_fore[numGroups + 2],
    s=96,
    c="k",
    marker=">",
    label=r"\textrm{exp. run 3}",
    zorder=5,
)
axs[0][0].scatter(
    meanA_exp[numGroups + 3],
    meanA_fore[numGroups + 3],
    s=96,
    c="k",
    marker="v",
    label=r"\textrm{exp. run 4}",
    zorder=5,
)
axs[0][0].scatter(
    meanA_exp[numGroups + 4],
    meanA_fore[numGroups + 4],
    s=96,
    c="k",
    marker="<",
    label=r"\textrm{exp. run 5}",
    zorder=5,
)
axs[0][0].set_title(r"\textrm{\textbf{24 h}}")
axs[0][0].set_xlim((0, 320))
axs[0][0].set_ylim((40, 270))
axs[0][0].grid(color=(0.9, 0.9, 0.9), linestyle="-", linewidth=0.5, zorder=0)


for k, hour, ki, kj in zip(range(1, 5), [48, 72, 96, 120], [0, 0, 1, 1], [1, 2, 0, 1]):
    A = (
        850
        * distances[
            k * numGroupsPlusExps : (k + 1) * numGroupsPlusExps,
            k * numGroupsPlusExps : (k + 1) * numGroupsPlusExps,
        ]
    )
    # set LANL distances to zero
    if includeLANL:
        A[5, :] = 0
        A[:, 5] = 0

    meanA_exp = np.mean(A[numGroups:, :], axis=0)
    if hour > 48:
        meanA_fore = (
            np.mean(A[:nBaseGroups, :], axis=0) * nBaseGroups / (nBaseGroups - 2)
        )  # take correct avg due to missing LANL and HW data
    else:
        meanA_fore = (
            np.mean(A[:nBaseGroups, :], axis=0) * nBaseGroups / (nBaseGroups - 1)
        )  # take correct avg due to missing LANL data

    axs[ki][kj].scatter(meanA_exp[1], meanA_fore[1], s=96, c=colors[1], zorder=5)
    axs[ki][kj].scatter(
        meanA_exp[9],
        meanA_fore[9],
        s=72,
        color=colors[9],
        marker=marker_mit,
        edgecolors="k",
        zorder=5,
    )
    axs[ki][kj].scatter(
        meanA_exp[10],
        meanA_fore[10],
        s=400,
        marker="*",
        edgecolors="k",
        c=colors[10],
        zorder=5,
    )
    if add:
        axs[ki][kj].scatter(
            meanA_exp[11],
            meanA_fore[11],
            s=100,
            marker=marker,
            edgecolors="k",
            c=colors[11],
            zorder=5,
        )
    axs[ki][kj].scatter(
        meanA_exp[numGroups], meanA_fore[numGroups], s=96, c="k", marker="d", zorder=5
    )
    axs[ki][kj].scatter(
        meanA_exp[numGroups + 1],
        meanA_fore[numGroups + 1],
        s=96,
        c="k",
        marker="^",
        zorder=5,
    )
    axs[ki][kj].scatter(
        meanA_exp[numGroups + 2],
        meanA_fore[numGroups + 2],
        s=96,
        c="k",
        marker=">",
        zorder=5,
    )
    axs[ki][kj].scatter(
        meanA_exp[numGroups + 3],
        meanA_fore[numGroups + 3],
        s=96,
        c="k",
        marker="v",
        zorder=5,
    )
    axs[ki][kj].scatter(
        meanA_exp[numGroups + 4],
        meanA_fore[numGroups + 4],
        s=96,
        c="k",
        marker="<",
        zorder=5,
    )
    if hour == 48:
        axs[ki][kj].set_title(r"\textrm{\textbf{48 h}}")
    if hour == 72:
        axs[ki][kj].set_title(r"\textrm{\textbf{72 h}}")
    if hour == 96:
        axs[ki][kj].set_title(r"\textrm{\textbf{96 h}}")
    if hour == 120:
        axs[ki][kj].set_title(r"\textrm{\textbf{120 h}}")
    axs[ki][kj].set_xlim((0, 320))
    axs[ki][kj].set_ylim((40, 270))
    axs[ki][kj].grid(color=(0.9, 0.9, 0.9), linestyle="-", linewidth=0.5, zorder=0)

axs[0][0].tick_params(
    axis="x", which="both", bottom=False, top=False, labelbottom=False
)
axs[0][1].tick_params(
    axis="x", which="both", bottom=False, top=False, labelbottom=False
)
axs[0][1].tick_params(axis="y", which="both", left=False, right=False, labelleft=False)
axs[0][2].tick_params(
    axis="y", which="both", left=False, right=True, labelleft=False, labelright=True
)
axs[1][1].tick_params(
    axis="y", which="both", left=False, right=True, labelleft=False, labelright=True
)
axs[1][2].set_axis_off()
axs[1][0].set_xlabel(r"\textrm{dist. to experiments [gr.cm]}")
axs[1][1].set_xlabel(r"\textrm{dist. to experiments [gr.cm]}")
axs[0][2].set_xlabel(r"\textrm{dist. to experiments [gr.cm]}")
axs[0][0].set_ylabel(r"\textrm{dist. to forecasts [gr.cm]}")
axs[1][0].set_ylabel(r"\textrm{dist. to forecasts [gr.cm]}")

fig.legend(loc="lower right", bbox_to_anchor=(1.0, 0.05), ncol=2)

fig.savefig(
    f"means_segmented_snapshots_satmin-{cmdargs['minimumsaturation']}_conmin-"
    f"{cmdargs['minimumconcentration']}.png",
    bbox_inches="tight",
)

for k, hour, ki, kj in zip(
    range(0, 5), [24, 48, 72, 96, 120], [0, 0, 0, 1, 1], [0, 1, 2, 0, 1]
):
    # axs[ki][kj].set_xlim((0, 120))
    axs[ki][kj].set_xlim((0, 80))
    axs[ki][kj].set_xticks([0, 20, 40, 60, 80])
    axs[ki][kj].set_ylim((70, 180))
    axs[ki][kj].grid(color=(0.9, 0.9, 0.9), linestyle="-", linewidth=0.5, zorder=0)

fig.savefig(
    f"zoom_means_segmented_snapshots_satmin-{cmdargs['minimumsaturation']}_conmin-"
    f"{cmdargs['minimumconcentration']}.png",
    bbox_inches="tight",
)
