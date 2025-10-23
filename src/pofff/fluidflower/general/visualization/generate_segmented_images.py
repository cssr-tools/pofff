#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/visualization/generate_segmented_images.py
# pylint: disable=R0912,R0913,R0914,R0915,R0917,C0103

"""
Script to overlay a modeling spatial map with contour
lines based on the experimental data.
"""

import argparse
import numpy as np
from PIL import Image


def generateImages(
    modelResult, experimentalData, outFileName, satmin, conmin, onlyModCont=False
):
    "Generate images"
    modImage = Image.new("RGBA", (280, 120))
    modPixels = modImage.load()
    for i in range(0, modImage.size[0]):
        for j in range(0, modImage.size[1]):
            if modelResult[j, i] == 1:
                modPixels[i, j] = (0, 255, 0)
            elif modelResult[j, i] == 2:
                modPixels[i, j] = (255, 0, 0)
            else:
                modPixels[i, j] = (0, 0, 0)

    modContImage = modImage.copy()
    modContPixels = modContImage.load()
    modImage = modImage.resize((560, 240))
    if not onlyModCont:
        modImage.save(f"{outFileName}_mod_satmin-{satmin}_conmin-{conmin}.png")

    expImage = Image.new("RGBA", (280, 120))
    expPixels = expImage.load()
    for i in range(0, expImage.size[0]):
        for j in range(0, expImage.size[1]):
            if experimentalData[j, i] == 1:
                expPixels[i, j] = (0, 255, 0)
            elif experimentalData[j, i] == 2:
                expPixels[i, j] = (255, 0, 0)
            else:
                expPixels[i, j] = (0, 0, 0)

    expContImage = expImage.copy()
    expContPixels = expContImage.load()
    expImage = expImage.resize((560, 240))
    if not onlyModCont:
        expImage.save(f"{outFileName}_exp.png")

    for i in range(1, expContImage.size[0] - 1):
        for j in range(1, expContImage.size[1] - 1):
            if modelResult[j, i] == 1 and any(
                val == 0
                for val in [
                    modelResult[j - 1, i],
                    modelResult[j + 1, i],
                    modelResult[j, i - 1],
                    modelResult[j, i + 1],
                ]
            ):
                expContPixels[i - 1, j - 1] = (255, 255, 0)
                expContPixels[i - 1, j] = (255, 255, 0)
                expContPixels[i - 1, j + 1] = (255, 255, 0)
                expContPixels[i, j - 1] = (255, 255, 0)
                expContPixels[i, j] = (255, 255, 0)
                expContPixels[i, j + 1] = (255, 255, 0)
                expContPixels[i + 1, j - 1] = (255, 255, 0)
                expContPixels[i + 1, j] = (255, 255, 0)
                expContPixels[i + 1, j + 1] = (255, 255, 0)
            elif modelResult[j, i] == 2 and any(
                val < 2
                for val in [
                    modelResult[j - 1, i],
                    modelResult[j + 1, i],
                    modelResult[j, i - 1],
                    modelResult[j, i + 1],
                ]
            ):
                expContPixels[i - 1, j - 1] = (0, 0, 255)
                expContPixels[i - 1, j] = (0, 0, 255)
                expContPixels[i - 1, j + 1] = (0, 0, 255)
                expContPixels[i, j - 1] = (0, 0, 255)
                expContPixels[i, j] = (0, 0, 255)
                expContPixels[i, j + 1] = (0, 0, 255)
                expContPixels[i + 1, j - 1] = (0, 0, 255)
                expContPixels[i + 1, j] = (0, 0, 255)
                expContPixels[i + 1, j + 1] = (0, 0, 255)
            elif experimentalData[j, i] == 1:
                expContPixels[i, j] = (138, 254, 190)
            elif experimentalData[j, i] == 2:
                expContPixels[i, j] = (249, 107, 107)

    expContImage = expContImage.resize((560, 240))
    if not onlyModCont:
        expContImage.save(f"{outFileName}_exp_cont_satmin-{satmin}_conmin-{conmin}.png")

    for i in range(1, modContImage.size[0] - 1):
        for j in range(1, modContImage.size[1] - 1):
            if experimentalData[j, i] == 1 and any(
                val == 0
                for val in [
                    experimentalData[j - 1, i],
                    experimentalData[j + 1, i],
                    experimentalData[j, i - 1],
                    experimentalData[j, i + 1],
                ]
            ):
                modContPixels[i - 1, j - 1] = (255, 255, 0)
                modContPixels[i - 1, j] = (255, 255, 0)
                modContPixels[i - 1, j + 1] = (255, 255, 0)
                modContPixels[i, j - 1] = (255, 255, 0)
                modContPixels[i, j] = (255, 255, 0)
                modContPixels[i, j + 1] = (255, 255, 0)
                modContPixels[i + 1, j - 1] = (255, 255, 0)
                modContPixels[i + 1, j] = (255, 255, 0)
                modContPixels[i + 1, j + 1] = (255, 255, 0)
            elif experimentalData[j, i] == 2 and any(
                val < 2
                for val in [
                    experimentalData[j - 1, i],
                    experimentalData[j + 1, i],
                    experimentalData[j, i - 1],
                    experimentalData[j, i + 1],
                ]
            ):
                modContPixels[i - 1, j - 1] = (0, 0, 255)
                modContPixels[i - 1, j] = (0, 0, 255)
                modContPixels[i - 1, j + 1] = (0, 0, 255)
                modContPixels[i, j - 1] = (0, 0, 255)
                modContPixels[i, j] = (0, 0, 255)
                modContPixels[i, j + 1] = (0, 0, 255)
                modContPixels[i + 1, j - 1] = (0, 0, 255)
                modContPixels[i + 1, j] = (0, 0, 255)
                modContPixels[i + 1, j + 1] = (0, 0, 255)
            elif modelResult[j, i] == 1:
                modContPixels[i, j] = (138, 254, 190)
            elif modelResult[j, i] == 2:
                modContPixels[i, j] = (249, 107, 107)

    modContImage = modContImage.resize((560, 240))
    modContImage.save(f"{outFileName}_mod_cont_satmin-{satmin}_conmin-{conmin}.png")


def generateSegmentMap(fileName, xmin, xmax, ymin, ymax, satmin, conmin):
    "Generate segmented map"
    xSpace = np.arange(xmin, xmax + 5.0e-3, 1.0e-2)
    ySpace = np.arange(ymin, ymax + 5.0e-3, 1.0e-2)
    nX = xSpace.size - 1
    nY = ySpace.size - 1

    skip_header = 0
    with open(fileName, "r", encoding="utf8") as file:
        if not (file.readline()[0]).isnumeric():
            skip_header = 1

    saturation = np.zeros([nY, nX])
    concentration = np.zeros([nY, nX])
    csvData = np.genfromtxt(fileName, delimiter=",", skip_header=skip_header)
    for i in np.arange(0, nY):
        saturation[i, :] = csvData[i * nX : (i + 1) * nX, 2]
        concentration[i, :] = csvData[i * nX : (i + 1) * nX, 3]

    segmentMap = np.zeros((120, 280), dtype=int)

    if not ((nX == 286 and nY == 123) or (nX == 280 and nY == 120)):
        print("Warning: wrong dimensions. Return 0 segment map.")
        return segmentMap

    offset = 0
    if nX == 286:
        offset = 3

    # Start from the fourth row as the first three are not contained in the experimental data
    for i in np.arange(offset, nY):
        # For the same reason, exclude the first and last three columns
        for j in np.arange(offset, nX - offset):
            # The first row of the segment map corresponds to the top of the domain
            if saturation[i, j] > satmin:
                segmentMap[119 + offset - i, j - offset] = 2
            elif concentration[i, j] > conmin:
                segmentMap[119 + offset - i, j - offset] = 1

    return segmentMap


def generateSegmentedImages():
    """Overlay a modeling spatial map with contour lines based on the experimental data"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--modelresult",
        help="The csv file containing a spatial map as required by the benchmark description.",
    )
    parser.add_argument(
        "-e",
        "--experimentaldata",
        help="The csv file containing the segment information from the experiment. Expected "
        "to correspond to a 150x280 array.",
    )
    parser.add_argument(
        "-o", "--outbasefilename", help="The base name of the output image files."
    )
    parser.add_argument(
        "-xmin",
        "--xmin",
        type=float,
        default=0.0,
        help="The minimum x value of the domain. Defaults to 0.0.",
    )
    parser.add_argument(
        "-xmax",
        "--xmax",
        type=float,
        default=2.86,
        help="The maximum x value of the domain. Defaults to 2.86.",
    )
    parser.add_argument(
        "-ymin",
        "--ymin",
        type=float,
        default=0.0,
        help="The minimum y value of the domain. Defaults to 0.0.",
    )
    parser.add_argument(
        "-ymax",
        "--ymax",
        type=float,
        default=1.23,
        help="The maximum y value of the domain. Defaults to 1.23.",
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

    cmdArgs = vars(parser.parse_args())

    modelResult = generateSegmentMap(
        cmdArgs["modelresult"],
        cmdArgs["xmin"],
        cmdArgs["xmax"],
        cmdArgs["ymin"],
        cmdArgs["ymax"],
        cmdArgs["minimumsaturation"],
        cmdArgs["minimumconcentration"],
    )

    experimentalData = np.loadtxt(
        cmdArgs["experimentaldata"], dtype="int", delimiter=","
    )
    # skip the first 30 rows as they are not contained in the modeling results
    experimentalData = experimentalData[30:, :]

    generateImages(
        modelResult,
        experimentalData,
        cmdArgs["outbasefilename"],
        cmdArgs["minimumsaturation"],
        cmdArgs["minimumconcentration"],
    )


if __name__ == "__main__":
    generateSegmentedImages()
