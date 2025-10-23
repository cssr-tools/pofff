#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/evaluation/compare_sparse_data.py
# pylint: disable=R0912,R0913,R0914,R0915,R0917,C0103

"""Generate the sparse data figure"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib


def visualizeRow(means, stddevs, expData, ax, colors, groups, withlegend):
    """Handle the different groups"""
    median = np.nanpercentile(means[:9], 50)
    dev = np.nanpercentile(stddevs[:9], 50)
    ax.plot([1.0, 2.0], [median, median], linewidth=2, color="xkcd:brown")
    ax.plot(
        [1.5, 1.5],
        [median - dev, median + dev],
        linewidth=1,
        linestyle="dashed",
        color="xkcd:brown",
    )
    ax.plot([1.4, 1.6], [median - dev, median - dev], linewidth=1, color="xkcd:brown")
    ax.plot([1.4, 1.6], [median + dev, median + dev], linewidth=1, color="xkcd:brown")
    if withlegend:
        ax.scatter(1.5, means[1], s=96, c=colors[1], label=groups[1])
        ax.scatter(2.25, means[9], s=100, c="0.5", marker="o", label=groups[9])
        ax.scatter(2.25, means[10], s=400, c="#14b825", marker="*", label=groups[10])
        if len(groups) == 12:
            ax.scatter(
                2.25, means[11], s=100, c="#FF1493", marker="X", label=groups[11]
            )
    else:
        ax.scatter(1.5, means[1], s=96, c=colors[1])
        ax.scatter(2.25, means[9], s=100, c="0.5", marker="o")
        ax.scatter(2.25, means[10], s=400, c="#14b825", marker="*")
        if len(groups) == 12:
            ax.scatter(2.25, means[11], s=100, c="#FF1493", marker="X")

    mean = np.mean(expData[1:6])
    dev = np.std(expData[1:6])

    ax.plot([2.5, 3.5], [mean, mean], linewidth=2, color="k")
    ax.plot(
        [3.0, 3.0], [mean - dev, mean + dev], linewidth=1, linestyle="dashed", color="k"
    )
    ax.plot([2.9, 3.1], [mean - dev, mean - dev], linewidth=1, color="k")
    ax.plot([2.9, 3.1], [mean + dev, mean + dev], linewidth=1, color="k")
    if withlegend:
        ax.scatter(3, expData[1], s=96, c="k", label=r"\textrm{experiment}")
        ax.scatter(3 * np.ones(4), expData[2:6], s=96, c="k")
    else:
        ax.scatter(3 * np.ones(5), expData[1:6], s=96, c="k")


def compareSparseData():
    """Compare sparse data for the FluidFlower benchmark"""

    parser = argparse.ArgumentParser(
        description="This script compares the sparse data "
        "as required by the benchmark description."
    )
    parser.add_argument(
        "-l",
        "--location",
        default=".",
        help="Location for the csv simulation data ('.' by default).",
    )
    parser.add_argument(
        "-a",
        "--add",
        default="1",
        help="Add the result to the plots ('1' by default).",
    )
    parser.add_argument(
        "-p", "--path", default="../..", help="Path to the third-party folder."
    )
    cmdargs = vars(parser.parse_known_args()[0])
    path = cmdargs["path"]
    fileNames = [
        f"{path}austin/sparse_data.csv",
        f"{path}csiro/sparse_data.csv",
        f"{path}delft/delft-DARSim/sparse_data.csv",
        f"{path}delft/delft-DARTS/sparse_data.csv",
        f"{path}heriot-watt/HWU-sparsedata-final.csv",
        f"{path}lanl/sparse_data.csv",
        f"{path}melbourne/sparse_data.csv",
        f"{path}stanford/sparse_data.csv",
        f"{path}stuttgart/sparse_data.csv",
        f"{path}mit/sparse_data.csv",
        cmdargs["location"] + "/sparse_data.csv",
    ]
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
    colors = ["C0", "C1", "C2", "C3", "#9932CC", "#FF1493", "C7", "C8", "C9", "b"]
    ncol = 4
    if cmdargs["add"] == "1":
        fileNames += ["sparse_data.csv"]
        groups += ["YOURS"]
        colors += ["#FF1493"]
        ncol = 5

    font = {"family": "normal", "weight": "normal", "size": 18}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": True,
            "font.family": "monospace",
            "legend.columnspacing": 0.9,
            "legend.handlelength": 1.2,
            "legend.fontsize": 12,
        }
    )

    numGroups = len(groups)
    numMeasurables = 13
    means = np.zeros((numMeasurables, numGroups))
    stddevs = np.zeros((numMeasurables, numGroups))
    for i, fileName in zip(range(numGroups), fileNames):
        print(f"Processing {fileName}.")

        skip_header = 0
        with open(fileName, "r", encoding="utf8") as file:
            if not (file.readline()[0]).isnumeric():
                skip_header = 1

        delimiter = ","
        skip_footer = 0

        csvData = np.genfromtxt(
            fileName,
            delimiter=delimiter,
            skip_header=skip_header,
            skip_footer=skip_footer,
        )
        means[:, i] = csvData[:, 2]
        stddevs[:, i] = csvData[:, 5]

    expName = f"{path}experiment/benchmarkdata/sparse_data/sparse_data.csv"
    expData = np.genfromtxt(expName, delimiter=",", skip_header=1, skip_footer=0)

    figF, axsF = plt.subplots(3, 3, figsize=(18, 12))
    visualizeRow(
        means[0, :] / 1e5,
        stddevs[0, :] / 1e5,
        expData[0, :] / 1e5,
        axsF[0][0],
        colors,
        groups,
        False,
    )
    axsF[0][0].set_ylabel(r"\textrm{\LARGE pressure [bar]}")
    axsF[0][0].set_title(
        r"\textrm{\textbf{\Large 1a: expected max. pressure at sensor 1}}"
    )
    axsF[0][0].set_xticks([])
    visualizeRow(
        means[1, :] / 1e5,
        stddevs[1, :] / 1e5,
        expData[1, :] / 1e5,
        axsF[0][1],
        colors,
        groups,
        True,
    )
    axsF[0][1].set_ylabel(r"\textrm{\LARGE pressure [bar]}")
    axsF[0][1].set_title(
        r"\textrm{\textbf{\Large 1b: expected max. pressure at sensor 2}}"
    )
    axsF[0][1].set_yticks([1.04, 1.05, 1.06, 1.07, 1.08])
    axsF[0][1].set_xticks([])
    visualizeRow(
        means[2, :] / 60 / 60,
        stddevs[2, :] / 60 / 60,
        expData[2, :] / 60 / 60,
        axsF[0][2],
        colors,
        groups,
        False,
    )
    axsF[0][2].set_ylabel(r"\textrm{\LARGE time [h]}")
    axsF[0][2].set_title(
        r"\textrm{\textbf{\Large 2: max. mobile gaseous CO$_2$ in Box A}}"
    )
    axsF[0][2].set_xticks([])
    visualizeRow(
        1e3 * means[3, :],
        1e3 * stddevs[3, :],
        1e3 * expData[3, :],
        axsF[1][0],
        colors,
        groups,
        False,
    )
    axsF[1][0].set_ylabel(r"\textrm{\LARGE mass [g]}")
    axsF[1][0].set_title(r"\textrm{\textbf{\Large 3a: mobile gaseous CO$_2$}}")
    axsF[1][0].set_xticks([])
    visualizeRow(
        1e3 * means[5, :],
        1e3 * stddevs[5, :],
        1e3 * expData[5, :],
        axsF[1][1],
        colors,
        groups,
        False,
    )
    axsF[1][1].set_ylabel(r"\textrm{\LARGE mass [g]}")
    axsF[1][1].set_title(r"\textrm{\textbf{\Large 3c: dissolved CO$_2$}}")
    axsF[1][1].set_xticks([])
    visualizeRow(
        1e3 * means[7, :],
        1e3 * stddevs[7, :],
        1e3 * expData[7, :],
        axsF[1][2],
        colors,
        groups,
        False,
    )
    axsF[1][2].set_ylabel(r"\textrm{\LARGE mass [g]}")
    axsF[1][2].set_title(r"\textrm{\textbf{\Large 4a: mobile gaseous CO$_2$}}")
    axsF[1][2].set_xticks([])
    visualizeRow(
        1e3 * means[9, :],
        1e3 * stddevs[9, :],
        1e3 * expData[9, :],
        axsF[2][0],
        colors,
        groups,
        False,
    )
    axsF[2][0].set_ylabel(r"\textrm{\LARGE mass [g]}")
    axsF[2][0].set_title(r"\textrm{\textbf{\Large 4c: dissolved CO$_2$}}")
    axsF[1][0].set_yticks([0.0, 0.5, 1.0, 1.5])
    axsF[1][1].set_yticks([1.0, 2.0, 3.0, 4.0])
    axsF[1][2].set_ylim((-0.0003, 0.0028))
    axsF[1][2].ticklabel_format(axis="y", style="sci", scilimits=[0, 0])
    axsF[1][2].text(0.6, 2.80e-3, r"$\times 10^{-2}$")
    axsF[1][2].yaxis.offsetText.set_visible(False)
    axsF[2][0].set_yticks([0.0, 0.5, 1.0])
    visualizeRow(
        means[11, :] / 60 / 60,
        stddevs[11, :] / 60 / 60,
        expData[12, :] / 60 / 60,
        axsF[2][1],
        colors,
        groups,
        False,
    )
    axsF[2][1].set_ylabel(r"\textrm{\LARGE time [h]}")
    axsF[2][1].set_title(
        r"\textrm{\textbf{\Large 5: $M(t)$ exceeds 110\% of Box C’s width}}"
    )
    axsF[2][1].set_xticks([1.5, 3.0])
    axsF[2][1].set_xticklabels(
        [r"\textrm{\LARGE modeling}", r"\textrm{\LARGE experiment}"]
    )
    visualizeRow(
        1e3 * means[12, :],
        1e3 * stddevs[12, :],
        1e3 * expData[13, :],
        axsF[2][2],
        colors,
        groups,
        False,
    )
    axsF[2][2].set_ylabel(r"\textrm{\LARGE mass [g]}")
    axsF[2][2].set_title(
        r"\textrm{\textbf{\Large 6: CO$_2$ in seal facies in Box A at 120\,h}}"
    )
    axsF[2][2].set_xticks([1.5, 3.0])
    axsF[2][2].set_xticklabels(
        [r"\textrm{\LARGE modeling}", r"\textrm{\LARGE experiment}"]
    )
    axsF[2][0].set_xticks([1.5, 2.25, 3.0])
    axsF[2][0].set_xticklabels(
        [
            r"\textrm{\LARGE modeling}",
            r"\textrm{\LARGE HM}",
            r"\textrm{\LARGE experiment}",
        ]
    )
    axsF[2][1].set_xticks([1.5, 2.25, 3.0])
    axsF[2][1].set_xticklabels(
        [
            r"\textrm{\LARGE modeling}",
            r"\textrm{\LARGE HM}",
            r"\textrm{\LARGE experiment}",
        ]
    )
    axsF[2][2].set_xticks([1.5, 2.25, 3.0])
    axsF[2][2].set_xticklabels(
        [
            r"\textrm{\LARGE modeling}",
            r"\textrm{\LARGE HM}",
            r"\textrm{\LARGE experiment}",
        ]
    )
    axsF[0][1].legend(loc="upper center", bbox_to_anchor=(0.5, 1.3), ncol=ncol)
    figF.savefig("compare_all_sparse.png", bbox_inches="tight")


if __name__ == "__main__":
    compareSparseData()
