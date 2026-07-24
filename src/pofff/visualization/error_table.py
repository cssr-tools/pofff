#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/evaluation/compare_sparse_data.py
# pylint: disable=R0914,R0915,C0103

"""Quantify errors between simulation results and experimental data
and summarize them in a comparison table."""

import argparse
import os

import numpy as np

NUM_EXPERIMENTS = 5  # Number of experimental realizations
NUM_MEASURABLES = 13  # Number of reported sparse quantities
SCALING = 1e3  # Unit scaling for mass values
DISTANCE_SCALE = 850.0  # Scaling factor for Wasserstein distances
LANL_INDEX = 5  # Index of LANL (excluded in distance stats)


def parse_arguments(argv):
    """Parse command-line arguments controlling paths and thresholds."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="This script compares the data "
        "as published in the pofff paper error tables.",
    )
    parser.add_argument(
        "-p", "--path", default="../..", help="Path to the third-party folder."
    )
    parser.add_argument(
        "-satmin",
        "--minimumsaturation",
        type=float,
        default=1e-2,
        help="Minimum saturation threshold for gaseous CO2 segmentation.",
    )
    parser.add_argument(
        "-conmin",
        "--minimumconcentration",
        type=float,
        default=1e-1,
        help="Minimum concentration threshold for dissolved CO2 segmentation.",
    )
    parser.add_argument(
        "-l",
        "--location",
        default=".",
        help="Location of the simulation CSV files.",
    )
    parser.add_argument(
        "-a", "--add", default="1", help="Whether to add the local result to plots."
    )

    return vars(parser.parse_known_args(argv)[0])


def load_sparse_csv(filename):
    """Load a sparse CSV file, automatically handling optional headers."""
    skip_header = 0
    with open(filename, "r", encoding="utf8") as f:
        # Detect header line by first character
        if not f.readline()[0].isnumeric():
            skip_header = 1

    return np.genfromtxt(
        filename,
        delimiter=",",
        skip_header=skip_header,
        skip_footer=0,
    )


def run_error_table(argv=None):
    """Compute error metrics and Wasserstein distances
    and write a formatted comparison table to disk."""
    cmdargs = parse_arguments(argv)

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
        where = os.path.abspath(".").split("/")
        if where[-1] == "best_simulation" and where[-2] == "figures":
            groups += [where[-3]]
        else:
            groups += [where[-1]]
        fileNames += ["sparse_data.csv"]

    numGroups = len(groups)
    numGroupsPlusExps = numGroups + NUM_EXPERIMENTS

    means = np.zeros((NUM_MEASURABLES, numGroups))
    stddevs = np.zeros((NUM_MEASURABLES, numGroups))

    for i, fileName in zip(range(numGroups), fileNames):
        print(f"Processing {fileName}.")
        data = load_sparse_csv(fileName)
        means[:, i] = data[:, 2]
        stddevs[:, i] = data[:, 5]

    distances = np.loadtxt(
        f"segmented_distances_satmin-{cmdargs['minimumsaturation']}_"
        f"conmin-{cmdargs['minimumconcentration']}.csv",
        delimiter=",",
    )

    distTable = [0.0] * numGroups
    distExp = [0.0] * (NUM_EXPERIMENTS * NUM_EXPERIMENTS)

    for k in range(NUM_EXPERIMENTS):
        A = (
            DISTANCE_SCALE
            * distances[
                k * numGroupsPlusExps : (k + 1) * numGroupsPlusExps,
                k * numGroupsPlusExps : (k + 1) * numGroupsPlusExps,
            ]
        )

        A[LANL_INDEX, :] = np.nan
        A[:, LANL_INDEX] = np.nan

        meanA_exp = np.mean(A[numGroups:, :], axis=0)

        for i in range(numGroups):
            distTable[i] += meanA_exp[i] / NUM_EXPERIMENTS

        for i in range(NUM_EXPERIMENTS):
            distExp[NUM_EXPERIMENTS * k + i] = meanA_exp[numGroups + i]

    expName = f"{path}experiment/benchmarkdata/sparse_data/sparse_data.csv"
    expData = np.genfromtxt(expName, delimiter=",", skip_header=1)

    expTable = [
        [np.mean(expData[2][1:6]), np.std(expData[2][1:6])],
        [SCALING * np.mean(expData[3][1:6]), SCALING * np.std(expData[3][1:6])],
        [SCALING * np.mean(expData[5][1:6]), SCALING * np.std(expData[5][1:6])],
        [SCALING * np.mean(expData[6][1:6]), SCALING * np.std(expData[6][1:6])],
        [SCALING * np.mean(expData[9][1:6]), SCALING * np.std(expData[9][1:6])],
        [SCALING * np.mean(expData[13][1:6]), SCALING * np.std(expData[13][1:6])],
    ]

    text = ""
    text += "Parameter\t, 1 (s)\t\t, 2a (g), 2c (g), 2d (g), 3c (g), 5 (g) ,  "
    text += "error, WD (g cm), Metric\n"
    text += "Group    \t, mean \t  \t, mean \t, mean \t, mean \t, mean \t, "
    text += "mean \t,   mean,      mean,    sum\n"
    text += (
        f"Experiment\t, {expTable[0][0]:.2E}\t, {expTable[1][0]:.2f}\t, "
        f"{expTable[2][0]:.2f}\t, {expTable[3][0]:.2f}\t, {expTable[4][0]:.2f}\t, "
        f"{expTable[5][0]:.2f}\t,    nan,     {np.mean(distExp):.2f},    nan\n"
    )

    error, w_d, metric = [], [], []

    for i, name in enumerate(groups):
        tab = ""
        if len(name) < 12:
            tab += "\t"
            if len(name) < 7:
                tab += "\t"

        errors = [
            100.0 * abs(means[2, i] - expTable[0][0]) / expTable[0][0],
            100.0 * abs(SCALING * means[3, i] - expTable[1][0]) / expTable[1][0],
            100.0 * abs(SCALING * means[5, i] - expTable[2][0]) / expTable[2][0],
            100.0 * abs(SCALING * means[6, i] - expTable[3][0]) / expTable[3][0],
            100.0 * abs(SCALING * means[9, i] - expTable[4][0]) / expTable[4][0],
            100.0 * abs(SCALING * means[12, i] - expTable[5][0]) / expTable[5][0],
        ]

        err = (
            f"{np.mean(errors):.0E}"
            if name.upper() == "LANL"
            else f"{np.mean(errors):.2f}"
        )

        was = f"{distTable[i]:.2f}"
        tot = f"{np.mean(errors) + distTable[i]:.2f}"

        text += (
            f"{name.upper()}{tab}, {means[2,i]:.2E}\t, {SCALING*means[3,i]:.2f}\t, "
            f"{SCALING*means[5,i]:.2f}\t, {SCALING*means[6,i]:.2f}\t, "
            f"{SCALING*means[9,i]:.2f}\t, {SCALING*means[12,i]:.2f}  , "
            f"{' '*(6-len(err))}{err}, "
            f"{' '*(9-len(was))}{was}, "
            f"{' '*(6-len(tot))}{tot}\n"
        )

        error.append(np.mean(errors))
        w_d.append(distTable[i])
        metric.append(np.mean(errors) + distTable[i])

    text += "\nLower to larger error:\n"
    text += ", ".join(groups[i].upper() for i in np.argsort(error)) + "\n"

    text += "Lower to larger Wasserstein distance:\n"
    text += ", ".join(groups[i].upper() for i in np.argsort(w_d)) + "\n"

    text += "Lower to larger sum of both quantities:\n"
    text += ", ".join(groups[i].upper() for i in np.argsort(metric)) + "\n\n"

    text += (
        "Thresholds for the segmentation of simulation results: "
        f"satmin = {cmdargs['minimumsaturation']} and "
        f"conmin = {cmdargs['minimumconcentration']}\n"
    )

    with open(
        f"error_table_satmin-{cmdargs['minimumsaturation']}_"
        f"conmin-{cmdargs['minimumconcentration']}.csv",
        "w",
        encoding="utf8",
    ) as file:
        file.write(text)


if __name__ == "__main__":
    run_error_table()
