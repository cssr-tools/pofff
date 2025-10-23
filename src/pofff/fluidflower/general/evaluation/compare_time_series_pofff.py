#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/evaluation/compare_time_series.py
# pylint: disable=R0912,R0913,R0914,R0915,R0917,C0103

"""
Generate the time series figures.
"""

import argparse
from operator import methodcaller
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy import interpolate


def addExpData(fileName, ax, numFields=1, fieldIdx=0):
    """Add experimental data"""
    f = []
    minT = -np.inf
    maxT = np.inf

    data = np.genfromtxt(fileName, delimiter=",", skip_header=1)

    for run in range(5):
        dataRun = data[:, (numFields + 1) * run : (numFields + 1) * (run + 1)]
        dataRun = dataRun[~np.isnan(dataRun).any(axis=1)]

        f.append(interpolate.interp1d(dataRun[:, 0], dataRun[:, fieldIdx + 1]))
        minT = max(minT, dataRun[0, 0])
        maxT = min(maxT, dataRun[-1, 0])

    ls = np.linspace(minT, maxT, num=1000)
    interpolateddata = list(map(methodcaller("__call__", ls), f))
    meanvalues = np.mean(interpolateddata, axis=0)
    std = np.std(interpolateddata, axis=0)

    (e1,) = ax.plot(ls, meanvalues, color="k", linewidth=3, label="experiment")
    e2 = ax.fill_between(ls, meanvalues - std, meanvalues + std, color="gray")
    ax.grid(True, which="both")

    return (e1, e2)


def compareTimeSeries():
    """Compare time series for the FluidFlower benchmark"""

    parser = argparse.ArgumentParser(
        description="This script compares the time series quantities "
        "as required by the benchmark description."
    )
    parser.add_argument(
        "-p", "--path", default="../..", help="Path to the third-party folder."
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
        default=True,
        help="Add the result to the plots ('True' by default).",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    path = cmdargs["path"]

    fileNames = [
        f"{path}austin/time_series.csv",
        f"{path}csiro/time_series.csv",
        f"{path}delft/delft-DARSim/time_series.csv",
        f"{path}delft/delft-DARTS/time_series.csv",
        f"{path}heriot-watt/HWU-FinalTimeSeries.csv",
        f"{path}lanl/time_series.csv",
        f"{path}melbourne/time_series.csv",
        f"{path}stanford/time_series_final.csv",
        f"{path}stuttgart/time_series.csv",
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
    ]
    colors = ["C0", "C1", "C2", "C3", "#9932CC", "#FF1493", "C7", "C8", "C9"]
    cssrData = np.genfromtxt(
        cmdargs["location"] + "/time_series.csv", delimiter=",", skip_header=1
    )
    mitm1 = np.genfromtxt(f"{path}mit/time_series.csv", delimiter=",", skip_header=1)
    if cmdargs["add"] == "1":
        newData = np.genfromtxt("time_series.csv", delimiter=",", skip_header=1)

    font = {"family": "normal", "weight": "normal", "size": 12}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": True,
            "font.family": "monospace",
            "legend.columnspacing": 1.5,
            "legend.fontsize": 14,
            "legend.handlelength": 1,
        }
    )

    figA, axsA = plt.subplots(2, 3, figsize=(15, 6))

    fMobileA = []
    fDissolvedA = []
    fSealA = []
    fDissolvedB = []
    fMixingC = []
    minT = -np.inf
    maxT = np.inf

    for fileName in fileNames:
        skip_header = 0
        with open(fileName, "r", encoding="utf8") as file:
            if not (file.readline()[0]).isnumeric():
                skip_header = 1

        csvData = np.genfromtxt(fileName, delimiter=",", skip_header=skip_header)

        t = csvData[:, 0] / 3600
        minT = max(minT, t[0])
        maxT = min(maxT, t[-1])

        fMobileA.append(interpolate.interp1d(t, 1e3 * csvData[:, 3]))
        fDissolvedA.append(interpolate.interp1d(t, 1e3 * csvData[:, 5]))
        fSealA.append(interpolate.interp1d(t, 1e3 * csvData[:, 6]))
        fDissolvedB.append(interpolate.interp1d(t, 1e3 * csvData[:, 9]))
        fMixingC.append(interpolate.interp1d(t, csvData[:, 11]))

    ls = np.linspace(minT, maxT, num=1000)

    interpMobileA = list(map(methodcaller("__call__", ls), fMobileA))
    medianMobileA = np.median(interpMobileA, axis=0)
    q1MobileA = np.percentile(interpMobileA, 25, axis=0)
    q3MobileA = np.percentile(interpMobileA, 75, axis=0)
    p2 = axsA[0][0].fill_between(
        ls, q1MobileA, q3MobileA, color="xkcd:pale brown", label="forecast"
    )

    interpDissolvedA = list(map(methodcaller("__call__", ls), fDissolvedA))
    medianDissolvedA = np.median(interpDissolvedA, axis=0)
    q1DissolvedA = np.percentile(interpDissolvedA, 25, axis=0)
    q3DissolvedA = np.percentile(interpDissolvedA, 75, axis=0)
    axsA[0][1].fill_between(ls, q1DissolvedA, q3DissolvedA, color="xkcd:pale brown")

    interpSealA = list(map(methodcaller("__call__", ls), fSealA))
    medianSealA = np.median(interpSealA, axis=0)
    q1SealA = np.percentile(interpSealA, 25, axis=0)
    q3SealA = np.percentile(interpSealA, 75, axis=0)
    axsA[0][2].fill_between(ls, q1SealA, q3SealA, color="xkcd:pale brown")

    interpDissolvedB = list(map(methodcaller("__call__", ls), fDissolvedB))
    medianDissolvedB = np.median(interpDissolvedB, axis=0)
    q1DissolvedB = np.percentile(interpDissolvedB, 25, axis=0)
    q3DissolvedB = np.percentile(interpDissolvedB, 75, axis=0)
    axsA[1][0].fill_between(ls, q1DissolvedB, q3DissolvedB, color="xkcd:pale brown")
    axsA[1][0].fill_between(ls, q1DissolvedB, q3DissolvedB, color="xkcd:pale brown")

    interpMixingC = list(map(methodcaller("__call__", ls), fMixingC))
    medianMixingC = np.median(interpMixingC, axis=0)
    q1MixingC = np.percentile(interpMixingC, 25, axis=0)
    q3MixingC = np.percentile(interpMixingC, 75, axis=0)
    axsA[1][1].fill_between(ls, q1MixingC, q3MixingC, color="xkcd:pale brown")

    axsA[1][0].plot(
        ls, medianDissolvedB, color="xkcd:brown", linewidth=3, label="forecast"
    )
    axsA[1][1].plot(
        ls, medianMixingC, color="xkcd:brown", linewidth=3, label="forecast"
    )

    (e1, e2) = addExpData(
        f"{path}experiment/benchmarkdata/time_series/mobile_box_a.csv", axsA[0][0]
    )
    axsA[0][0].set_xscale("log")
    addExpData(
        f"{path}experiment/benchmarkdata/time_series/dissolved_boxes_a_b.csv",
        axsA[0][1],
        numFields=2,
        fieldIdx=0,
    )
    axsA[0][1].set_xscale("log")
    addExpData(
        f"{path}experiment/benchmarkdata/time_series/dissolved_box_a_seal.csv",
        axsA[0][2],
    )
    axsA[0][2].set_xscale("log")
    addExpData(
        f"{path}experiment/benchmarkdata/time_series/dissolved_boxes_a_b.csv",
        axsA[1][0],
        numFields=2,
        fieldIdx=1,
    )
    axsA[1][0].set_xscale("log")
    addExpData(
        f"{path}experiment/benchmarkdata/time_series/mixing_box_c.csv", axsA[1][1]
    )
    axsA[1][1].set_xscale("log")

    for i, (fileName, group, color) in enumerate(zip(fileNames, groups, colors)):
        if i != 1:
            continue
        print(f"Processing {fileName}.")

        skip_header = 0
        with open(fileName, "r", encoding="utf8") as file:
            if not (file.readline()[0]).isnumeric():
                skip_header = 1

        delimiter = ","

        csvData = np.genfromtxt(fileName, delimiter=delimiter, skip_header=skip_header)
        t = csvData[:, 0] / 3600

        axsA[0, 0].plot(
            t, 1e3 * csvData[:, 3], label=group, color=color, lw=5, ls="dotted"
        )
        axsA[0, 0].plot(
            t, 1e3 * csvData[:, 3], label=group, color=color, lw=5, ls="dotted"
        )
        axsA[0, 0].set_title(r"\textrm{\textbf{\Large Box A: mobile gaseous CO$_2$}}")
        axsA[0, 0].set_ylabel(r"\textrm{\LARGE mass [g]}")
        axsA[0, 0].set_xlim(0.1, 121.0)
        axsA[0, 0].set_ylim(-0.1, 3.0)

        axsA[1, 2].set_axis_off()

        axsA[0][1].plot(
            t, 1e3 * csvData[:, 5], label=group, color=color, lw=5, ls="dotted"
        )
        axsA[0][1].set_title(
            r"\textrm{\textbf{\Large Box A: CO$_2$ dissolved in liquid phase}}"
        )
        axsA[0][1].set_ylabel(r"\textrm{\LARGE mass [g]}")
        axsA[0][1].set_xlim(0.1, 121.0)
        axsA[0][1].set_ylim(-0.01, 5.0)

        axsA[0][2].plot(
            t, 1e3 * csvData[:, 6], label=group, color=color, lw=5, ls="dotted"
        )
        axsA[0][2].set_title(
            r"\textrm{\textbf{\Large Box A: CO$_2$ in the seal facies}}"
        )
        axsA[0][2].set_xlabel(r"\textrm{\LARGE time [h]}")
        axsA[0][2].set_ylabel(r"\textrm{\LARGE mass [g]}")
        axsA[0][2].set_xlim(0.1, 121.0)
        axsA[0][2].set_ylim(-0.01, 1.0)

        axsA[1][0].plot(
            t, 1e3 * csvData[:, 9], label=group, color=color, lw=5, ls="dotted"
        )
        axsA[1][0].set_title(
            r"\textrm{\textbf{\Large Box B: CO$_2$ dissolved in liquid phase}}"
        )
        axsA[1][0].set_xlabel(r"\textrm{\LARGE time [h]}")
        axsA[1][0].set_ylabel(r"\textrm{\LARGE mass [g]}")
        axsA[1][0].set_xlim(3.0, 121.0)
        axsA[1][0].set_ylim(-0.01, 1.5)

        axsA[1][1].plot(t, csvData[:, 11], label=group, color=color, lw=5, ls="dotted")
        axsA[1][1].set_title(r"\textrm{\textbf{\Large Box C: convection}}")
        axsA[1][1].set_xlabel(r"\textrm{\LARGE time [h]}")
        axsA[1][1].set_ylabel(r"\textrm{\LARGE $M$ [m]}")
        axsA[1][1].set_xlim(1.0, 121.0)
    t = mitm1[:, 0] / 3600
    axsA[0, 0].plot(
        t, 1e3 * mitm1[:, 3], label="MIT_M1", color="0.4", lw=5, ls="dashdot"
    )
    axsA[0][1].plot(
        t, 1e3 * mitm1[:, 5], label="MIT_M1", color="0.4", lw=5, ls="dashdot"
    )
    axsA[0][2].plot(
        t, 1e3 * mitm1[:, 6], label="MIT_M1", color="0.4", lw=5, ls="dashdot"
    )
    axsA[1][0].plot(
        t, 1e3 * mitm1[:, 9], label="MIT_M1", color="0.4", lw=5, ls="dashdot"
    )
    axsA[1][1].plot(t, mitm1[:, 11], label="MIT_M1", color="0.4", lw=5, ls="dashdot")
    t = cssrData[:, 0] / 3600
    axsA[0, 0].plot(
        t, 1e3 * cssrData[:, 3], label="CSSR", color="#14b825", lw=5, ls="dashed"
    )
    axsA[0][1].plot(
        t, 1e3 * cssrData[:, 5], label="CSSR", color="#14b825", lw=5, ls="dashed"
    )
    axsA[0][2].plot(
        t, 1e3 * cssrData[:, 6], label="CSSR", color="#14b825", lw=5, ls="dashed"
    )
    axsA[1][0].plot(
        t, 1e3 * cssrData[:, 9], label="CSSR", color="#14b825", lw=5, ls="dashed"
    )
    axsA[1][1].plot(
        t, cssrData[:, 11], label="CSSR", color="#14b825", lw=5, ls="dashed"
    )
    if cmdargs["add"] == "1":
        t = newData[:, 0] / 3600
        axsA[0, 0].plot(t, 1e3 * newData[:, 3], label="YOURS", color="#ff05a8", lw=2)
        axsA[0][1].plot(t, 1e3 * newData[:, 5], label="YOURS", color="#ff05a8", lw=2)
        axsA[0][2].plot(t, 1e3 * newData[:, 6], label="YOURS", color="#ff05a8", lw=2)
        axsA[1][0].plot(t, 1e3 * newData[:, 9], label="YOURS", color="#ff05a8", lw=2)
        axsA[1][1].plot(t, newData[:, 11], label="YOURS", color="#ff05a8", lw=2)
    (p1,) = axsA[0][0].plot(
        ls, medianMobileA, color="xkcd:brown", linewidth=3, label="forecast"
    )
    axsA[0][1].plot(
        ls, medianDissolvedA, color="xkcd:brown", linewidth=3, label="forecast"
    )
    axsA[0][2].plot(ls, medianSealA, color="xkcd:brown", linewidth=3, label="forecast")
    handles, labels = axsA[0][2].get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    del by_label["forecast"]
    by_label["forecast"] = (p2, p1)
    by_label[r"\textrm{forecast}"] = by_label.pop("forecast")
    del by_label["experiment"]
    by_label["experiment"] = (e2, e1)
    by_label[r"\textrm{experiment}"] = by_label.pop("experiment")
    figA.legend(
        by_label.values(),
        by_label.keys(),
        loc="upper left",
        bbox_to_anchor=(0.65, 0.35),
        ncol=2,
        handlelength=3.5,
    )
    axsA[0, 0].set_xticklabels([])
    axsA[0, 1].set_xticklabels([])

    figA.savefig("compare_all_time_series.png", bbox_inches="tight")


if __name__ == "__main__":
    compareTimeSeries()
