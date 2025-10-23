#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/evaluation/compare_sparse_data.py
# pylint: disable=R0912,R0914,R0915,C0103


"""
Script to quantify the errors between simulation and experiments into a table.
"""

import argparse
import numpy as np


def error_table():
    """Compare errors"""

    parser = argparse.ArgumentParser(
        description="This script compares the data "
        "as published in the pofff paper error tables."
    )
    parser.add_argument(
        "-p", "--path", default="../..", help="Path to the third-party folder."
    )
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
    cmdargs = vars(parser.parse_known_args()[0])
    path = cmdargs["path"] + "/fluidflower/"
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

    if cmdargs["add"] == "1":
        groups += ["YOURS"]
        fileNames += ["sparse_data.csv"]

    numGroups = len(groups)
    numExps = 5
    includeLANL = True
    numGroupsPlusExps = numGroups + numExps
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
    distances = np.loadtxt(
        f"segmented_distances_satmin-{cmdargs['minimumsaturation']}_conmin"
        f"-{cmdargs['minimumconcentration']}.csv",
        delimiter=",",
    )
    distTable = [0.0] * numGroups
    distExp = [0.0] * (numExps * 5)
    for k in range(5):
        A = (
            850
            * distances[
                k * numGroupsPlusExps : (k + 1) * numGroupsPlusExps,
                k * numGroupsPlusExps : (k + 1) * numGroupsPlusExps,
            ]
        )
        # set LANL distances to nan
        if includeLANL:
            A[5, :] = np.nan
            A[:, 5] = np.nan
        meanA_exp = np.mean(A[numGroups:, :], axis=0)
        for i in range(numGroups):
            distTable[i] += meanA_exp[i] / 5.0
        for i in range(5):
            distExp[5 * k + i] = meanA_exp[numGroups + i]
    expName = f"{path}experiment/benchmarkdata/sparse_data/sparse_data.csv"
    expData = np.genfromtxt(expName, delimiter=",", skip_header=1, skip_footer=0)
    expTable = [
        [np.mean(expData[2][1:6]), np.std(expData[2][1:6])],
        [1e3 * np.mean(expData[3][1:6]), 1e3 * np.std(expData[3][1:6])],
        [1e3 * np.mean(expData[5][1:6]), 1e3 * np.std(expData[5][1:6])],
        [1e3 * np.mean(expData[6][1:6]), 1e3 * np.std(expData[6][1:6])],
        [1e3 * np.mean(expData[9][1:6]), 1e3 * np.std(expData[9][1:6])],
        [1e3 * np.mean(expData[13][1:6]), 1e3 * np.std(expData[13][1:6])],
    ]
    text = ""
    text += "Parameter\t, 1 (s)\t\t, 2a (g), 2c (g), 2d (g), 3c (g), 5 (g) ,  "
    text += "error, WD (g cm), Metric\n"
    text += "Group    \t, mean \t  \t, mean \t, mean \t, mean \t, mean \t, "
    text += "mean \t,   mean,      mean,    sum\n"
    text += f"Experiment\t, {expTable[0][0]:.2E}\t, {expTable[1][0]:.2f}\t, "
    text += f"{expTable[2][0]:.2f}\t, {expTable[3][0]:.2f}\t, {expTable[4][0]:.2f}\t, "
    text += f"{expTable[5][0]:.2f}\t,    nan,     {np.mean(distExp):.2f},    nan\n"
    error = []
    w_d = []
    metric = []
    for i, name in enumerate(groups):
        tab = ""
        tab1 = "  "
        if len(name) < 12:
            tab += "\t"
            if len(name) < 7:
                tab += "\t"
        errors = [
            100.0 * abs(means[2, i] - expTable[0][0]) / expTable[0][0],
            100.0 * abs(1e3 * means[3, i] - expTable[1][0]) / expTable[1][0],
            100.0 * abs(1e3 * means[5, i] - expTable[2][0]) / expTable[2][0],
            100.0 * abs(1e3 * means[6, i] - expTable[3][0]) / expTable[3][0],
            100.0 * abs(1e3 * means[9, i] - expTable[4][0]) / expTable[4][0],
            100.0 * abs(1e3 * means[12, i] - expTable[5][0]) / expTable[5][0],
        ]
        err = (
            f"{np.mean(errors):.0E}"
            if name.upper() == "LANL"
            else f"{np.mean(errors):.2f}"
        )
        was = f"{distTable[i]:.2f}"
        tot = f"{np.mean(errors)+distTable[i]:.2f}"
        text += f"{name.upper()}{tab}, {means[2,i]:.2E}\t, {1e3*means[3,i]:.2f}\t, "
        text += (
            f"{1e3*means[5,i]:.2f}\t, {1e3*means[6,i]:.2f}\t, {1e3*means[9,i]:.2f}\t, "
        )
        text += f"{1e3*means[12,i]:.2f}{tab1}, "
        text += f"{''.join([' ' for _ in range(6-len(str(err)))])}{err}, "
        text += f"{''.join([' ' for _ in range(9-len(str(was)))])}{was}, "
        text += f"{''.join([' ' for _ in range(6-len(str(tot)))])}{tot}\n"
        tab = ""
        error.append(np.mean(errors))
        w_d.append(distTable[i])
        metric.append(np.mean(errors) + distTable[i])
    text += "\n"
    text += "Lower to larger error:\n"
    ind = np.argsort(error)
    for n, i in enumerate(ind):
        if n == 0:
            text += f"{groups[i].upper()}"
        else:
            text += f", {groups[i].upper()}"
    text += "\n"
    text += "Lower to larger Wasserstein distance:\n"
    ind = np.argsort(w_d)
    for n, i in enumerate(ind):
        if n == 0:
            text += f"{groups[i].upper()}"
        else:
            text += f", {groups[i].upper()}"
    text += "\n"
    text += "Lower to larger sum of both quantities:\n"
    ind = np.argsort(metric)
    for n, i in enumerate(ind):
        if n == 0:
            text += f"{groups[i].upper()}"
        else:
            text += f", {groups[i].upper()}"
    text += "\n"
    text += "\n"
    text += "Thresholds for the segmentation of simulation results: satmin = "
    text += f"{cmdargs['minimumsaturation']} and conmin = {cmdargs['minimumconcentration']}\n"
    with open(
        f"error_table_satmin-{cmdargs['minimumsaturation']}_conmin-"
        f"{cmdargs['minimumconcentration']}.csv",
        "w",
        encoding="utf8",
    ) as file:
        file.write(text)


if __name__ == "__main__":
    error_table()
