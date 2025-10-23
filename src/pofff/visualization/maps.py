#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/visualization/generate_segmented_images.py
# pylint: disable=R0913, R0914, R0917

"""
Script to overlay a modeling spatial map with contour
lines based on the experimental data.
"""

import argparse
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors

font = {"family": "normal", "weight": "normal", "size": 12}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": 1,
        "font.family": "monospace",
        "legend.columnspacing": 0.9,
        "legend.handlelength": 3.5,
        "legend.fontsize": 12,
        "lines.linewidth": 4,
        "axes.titlesize": 12,
        "axes.grid": False,
        "figure.figsize": (10, 5),
    }
)


def pngs(simulations, experiment, x, z, points, lines, t):
    """
    Create a png from the segmented data with sand interfaces

    Args:
        simulations (array): Segmented simulated results\n
        experiment (array): Segmented experimental results\n
        x (array): mesh grid\n
        z (array): mesh grid\n
        points (list): Locations of the sand interface vertices\n
        lines (list): Connections between points\n
        t (float): Value in hours for the spatial map

    Returns:
        None

    """
    cmap = colors.ListedColormap(
        ["#ffffff", "#f8a98c", "#faf7a1", "#df3a0c", "#B1B106"]
    )
    for i in range(1, len(experiment[0]) - 1):
        for j in range(1, len(experiment) - 1):
            if experiment[j, i] == 1 and any(
                val == 0
                for val in [
                    experiment[j - 1, i],
                    experiment[j + 1, i],
                    experiment[j, i - 1],
                    experiment[j, i + 1],
                ]
            ):
                simulations[j, i] = 3
            elif experiment[j, i] == 2 and any(
                val < 2
                for val in [
                    experiment[j - 1, i],
                    experiment[j + 1, i],
                    experiment[j, i - 1],
                    experiment[j, i + 1],
                ]
            ):
                simulations[j, i] = 4
    plt.pcolormesh(x, z, np.flip(simulations, axis=0), cmap=cmap)
    for line in lines:
        plt.plot(
            [points[line[0]][0], points[line[1]][0]],
            [points[line[0]][1], points[line[1]][1]],
            "k",
            lw=0.25,
        )
    # plt.colorbar()
    plt.ylim([0, 1.2])
    plt.xticks([])
    plt.yticks([])
    plt.savefig(f"map_{t}h.png")


def segment(file, satmin, conmin):
    """
    From continuous values to discrete for the gas and dissolevd co2

    Args:
        file (str): Name of the csv file with the spatial values\n
        satmin (float): Threshold for the gas saturation\n
        conmin (float): Threshold for the dissolved co2

    Returns:
        None

    """
    xspace = np.arange(0, 2.8 + 5.0e-3, 1.0e-2)
    zspace = np.arange(0, 1.2 + 5.0e-3, 1.0e-2)
    x, z = np.meshgrid(xspace, zspace)
    nx = xspace.size - 1
    nz = zspace.size - 1

    skip_header = 0
    with open(file, "r", encoding="utf8") as text:
        if not (text.readline()[0]).isnumeric():
            skip_header = 1

    saturation = np.zeros([nz, nx])
    concentration = np.zeros([nz, nx])
    values = np.genfromtxt(file, delimiter=",", skip_header=skip_header)
    for i in np.arange(0, nz):
        saturation[i, :] = values[i * nx : (i + 1) * nx, 2]
        concentration[i, :] = values[i * nx : (i + 1) * nx, 3]

    segmented = np.zeros((120, 280), dtype=int)

    offset = 0
    if nx == 286:
        offset = 3

    # Start from the fourth row as the first three are not contained in the experimental data
    for i in np.arange(offset, nz):
        # For the same reason, exclude the first and last three columns
        for j in np.arange(offset, nx - offset):
            # The first row of the segment map corresponds to the top of the domain
            if saturation[i, j] > satmin:
                segmented[119 + offset - i, j - offset] = 2
            elif concentration[i, j] > conmin:
                segmented[119 + offset - i, j - offset] = 1

    return segmented, x, z


def maps():
    """Overlay a modeling spatial map with contour lines based on the experimental data"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--experiment",
        default="run2",
        help="Experimental data to history match, valid options are run1 to run5 "
        "('run2' by default).",
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
        "-t",
        "--times",
        default="24,48,72,96,120",
        help="The times to generate the spatial maps.",
    )
    parser.add_argument(
        "-l",
        "--location",
        default=".",
        help="Location for the csv simulation data ('.' by default).",
    )
    parser.add_argument("-p", "--path", default=".", help="Path to the geometry data.")

    cmdargs = vars(parser.parse_args())
    for i in cmdargs["times"].split(","):
        simulations, x, z = segment(
            f"{cmdargs['location'].strip()}/spatial_map_{i}h.csv",
            cmdargs["minimumsaturation"],
            cmdargs["minimumconcentration"],
        )
        name = f"{int(float(i)*3600)}"
        zeros = 6 - len(name)
        for _ in range(zeros):
            name = "0" + name
        experiment = np.loadtxt(
            f"{cmdargs['path']}/fluidflower/experiment/benchmarkdata/spatial_maps/"
            + f"{cmdargs['experiment']}/segmentation_{name}s.csv",
            dtype="int",
            delimiter=",",
        )
        # skip the first 30 rows as they are not contained in the modeling results
        experiment = experiment[30:, :]
        points, lines = load_points(cmdargs["path"])
        pngs(
            simulations,
            experiment,
            x,
            z,
            points,
            lines,
            i,
        )


def load_points(path):
    """
    Get the contours for the sand interfaces

    Args:
        file (str): Name of the csv file with the spatial values

    Returns:
        None

    """
    points = []
    lines = []
    h_ref = 1.5 / 1490
    l_ref = 2.8 / 2594
    with open(
        f"{path}/geology/points.geo",
        "r",
        encoding="utf8",
    ) as file:
        for val in csv.reader(file, delimiter=" "):
            if val[0][:5] == "Point":
                points.append(
                    [
                        l_ref * float(val[2][1:-1]),
                        h_ref * float(val[3][:-1]),
                    ]
                )
    with open(
        f"{path}/geology/lines.geo",
        "r",
        encoding="utf8",
    ) as file:
        for row in csv.reader(file, delimiter=" "):
            if row[0] == "//" and not points or len(row) < 2:
                continue
            if row[0][:4] == "Line":
                lines.append([int(row[2][1:-1]) - 1, int(row[3][:-2]) - 1])
    return points, lines


if __name__ == "__main__":
    maps()
