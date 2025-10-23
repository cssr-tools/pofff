#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/evaluation/calculate_segmented_emds.py
# pylint: disable=R0912,R0913,R0914,R0915,R0917,C0103

"""
Script to calculate Wasserstein distances between segmented data.
"""

import os
import os.path
import argparse
import numpy as np
from PIL import Image
import pofff.fluidflower.general.visualization.generate_segmented_images as seg
from pofff.fluidflower.general.evaluation import emd


def calculateEMD(modelResult, experimentalData):
    """Calculate Wasserstein distance"""
    modImage = Image.new("L", (280, 120))
    modPixels = modImage.load()
    for i in range(0, modImage.size[0]):
        for j in range(0, modImage.size[1]):
            if modelResult[j, i] == 1:
                modPixels[i, j] = 128
            elif modelResult[j, i] == 2:
                modPixels[i, j] = 255
            else:
                modPixels[i, j] = 0

    modImage.save("mod0.png")

    expImage = Image.new("L", (280, 120))
    expPixels = expImage.load()
    for i in range(0, expImage.size[0]):
        for j in range(0, expImage.size[1]):
            if experimentalData[j, i] == 1:
                expPixels[i, j] = 128
            elif experimentalData[j, i] == 2:
                expPixels[i, j] = 255
            else:
                expPixels[i, j] = 0

    expImage.save("exp0.png")

    return emd.calculateEMD("mod0.png", "exp0.png")


def calculate_segmented_emds():
    """Calculate the segmented Wasserstein distances"""
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
        default="1",
        help="Add the result to the plots ('1' by default).",
    )

    cmdargs = vars(parser.parse_args())
    add = cmdargs["add"] == "1"
    path = cmdargs["path"]

    baseFileNames = [
        f"{path}austin/spatial_maps/spatial_map_",
        f"{path}csiro/spatial_map_",
        f"{path}delft/delft-DARSim/spatial_map_",
        f"{path}delft/delft-DARTS/spatial_map_",
        f"{path}heriot-watt/spatial_map_",
        f"{path}lanl/spatial_map_",
        f"{path}melbourne/spatial_map_",
        f"{path}stanford/spatial_maps/spatial_map_",
        f"{path}stuttgart/spatial_map_",
        f"{path}mit/spatial_map_",
        cmdargs["location"] + "/spatial_map_",
    ]
    if add:
        baseFileNames += ["spatial_map_"]
        distances = np.load(
            f"{os.path.dirname(__file__)}/precomputed/distances_satmin-"
            f"{cmdargs['minimumsaturation']}_conmin-{cmdargs['minimumconcentration']}.npy"
        )
    else:
        distances = np.load(
            f"{os.path.dirname(__file__)}/precomputed/groups_11_distances_satmin-"
            f"{cmdargs['minimumsaturation']}_conmin-{cmdargs['minimumconcentration']}.npy"
        )

    timesteps = [24, 48, 72, 96, 120]
    numGroups = len(baseFileNames)
    numExps = 5  # number of experiments
    numGroupsPlusExps = numGroups + numExps

    for hourI in timesteps:
        for hourJ in [hourI]:  # [24, 48, 72, 96, 120]:
            if hourJ < hourI:
                continue

            for i, baseFileNameI in zip(range(numGroups), baseFileNames):
                fileNameI = baseFileNameI + str(hourI) + "h.csv"
                if not os.path.exists(fileNameI):
                    continue

                if "watt" in fileNameI:
                    modelResultI = seg.generateSegmentMap(
                        fileNameI,
                        0.03,
                        2.83,
                        0.03,
                        1.23,
                        cmdargs["minimumsaturation"],
                        cmdargs["minimumconcentration"],
                    )
                elif i == numGroups - 1 or (add and i == numGroups - 2):
                    modelResultI = seg.generateSegmentMap(
                        fileNameI,
                        0.0,
                        2.8,
                        0.0,
                        1.2,
                        cmdargs["minimumsaturation"],
                        cmdargs["minimumconcentration"],
                    )
                else:
                    modelResultI = seg.generateSegmentMap(
                        fileNameI,
                        0.0,
                        2.86,
                        0.0,
                        1.23,
                        cmdargs["minimumsaturation"],
                        cmdargs["minimumconcentration"],
                    )
                row = int((hourI / 24 - 1) * numGroupsPlusExps + i)

                for j, baseFileNameJ in zip(range(numGroups), baseFileNames):
                    if j <= i and hourJ == hourI:
                        continue
                    if j < numGroups - 1:
                        continue
                    fileNameJ = baseFileNameJ + str(hourJ) + "h.csv"
                    modelResultJ = seg.generateSegmentMap(
                        fileNameJ,
                        0.0,
                        2.8,
                        0.0,
                        1.2,
                        cmdargs["minimumsaturation"],
                        cmdargs["minimumconcentration"],
                    )

                    col = int((hourJ / 24 - 1) * numGroupsPlusExps + j)
                    distances[row][col] = calculateEMD(modelResultI, modelResultJ)

                    print(
                        f"{hourI}, {hourJ}, {i}, {j} -> ({row}, {col}): {distances[row][col]}"
                    )

                    os.system("rm mod0.png exp0.png")

                if i < numGroups - 1:
                    continue
                for j in range(numGroups, numGroups + numExps):
                    if j <= i and hourJ == hourI:
                        continue

                    fileNameJ = (
                        f"{path}experiment/benchmarkdata/spatial_maps/run"
                        + str(j - numGroups + 1)
                        + "/segmentation_"
                        + str(hourJ)
                        + "h.csv"
                    )
                    experimentalDataJ = np.loadtxt(
                        fileNameJ, dtype="int", delimiter=","
                    )
                    # skip the first 30 rows as they are not contained in the modeling results
                    experimentalDataJ = experimentalDataJ[30:, :]

                    col = int((hourJ / 24 - 1) * numGroupsPlusExps + j)
                    distances[row][col] = calculateEMD(modelResultI, experimentalDataJ)

                    print(
                        f"{hourI}, {hourJ}, {i}, {j} -> ({row}, {col}): {distances[row][col]}"
                    )

                    os.system("rm mod0.png exp0.png")

    distances = distances + distances.T - np.diag(distances.diagonal())

    np.savetxt(
        f"segmented_distances_satmin-{cmdargs['minimumsaturation']}_conmin-"
        f"{cmdargs['minimumconcentration']}.csv",
        distances,
        delimiter=",",
    )


if __name__ == "__main__":
    calculate_segmented_emds()
