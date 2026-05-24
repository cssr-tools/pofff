#!/usr/bin/env python3
# Modified from
# https://github.com/fluidflower/general/blob/main/visualization/generate_segmented_images.py
# pylint: disable=R0913, R0914, R0917

"""Overlay simulated spatial maps with experimental contour boundaries."""

import argparse
import shutil
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors

DX = 1.0e-2  # Grid spacing [m]
DOMAIN_X = 2.8  # Domain length in x-direction [m]
DOMAIN_Z = 1.2  # Domain height in z-direction [m]
NX_TARGET = 280  # Target grid size in x
NZ_TARGET = 120  # Target grid size in z


def pngs(simulations, experiment, x, z, points, lines, t):
    """Plot segmented simulation map with experimental contours and geology."""
    cmap = colors.ListedColormap(
        ["#ffffff", "#f8a98c", "#faf7a1", "#df3a0c", "#B1B106"]
    )

    nz, nx = experiment.shape

    for i in range(1, nx - 1):
        for j in range(1, nz - 1):
            if experiment[j, i] == 1 and any(
                experiment[j + dj, i + di] == 0
                for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            ):
                simulations[j, i] = 3
            elif experiment[j, i] == 2 and any(
                experiment[j + dj, i + di] < 2
                for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]
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

    plt.ylim([0, DOMAIN_Z])
    plt.xticks([])
    plt.yticks([])
    plt.savefig(f"map_{t}h.png")
    plt.clf()


def segment(filename, satmin, conmin):
    """Segment saturation and concentration fields into discrete classes."""
    xspace = np.arange(0, DOMAIN_X + 0.5 * DX, DX)
    zspace = np.arange(0, DOMAIN_Z + 0.5 * DX, DX)
    x, z = np.meshgrid(xspace, zspace)

    nx = xspace.size - 1
    nz = zspace.size - 1

    with open(filename, encoding="utf8") as f:
        skip_header = 0 if f.readline()[0].isnumeric() else 1

    values = np.genfromtxt(filename, delimiter=",", skip_header=skip_header)

    saturation = values[:, 2].reshape(nz, nx)
    concentration = values[:, 3].reshape(nz, nx)

    segmented = np.zeros((NZ_TARGET, NX_TARGET), dtype=int)

    offset = 3 if nx == 286 else 0

    i_src = np.arange(offset, nz)
    j_src = np.arange(offset, nx - offset)

    ii, jj = np.meshgrid(i_src, j_src, indexing="ij")

    zi = NZ_TARGET - 1 + offset - ii
    xi = jj - offset

    gas_mask = saturation[ii, jj] > satmin
    dissolved_mask = (concentration[ii, jj] > conmin) & (~gas_mask)

    segmented[zi[gas_mask], xi[gas_mask]] = 2
    segmented[zi[dissolved_mask], xi[dissolved_mask]] = 1

    return segmented, x, z


def load_points(path):
    """Load geological points and line connectivity from .geo files."""
    points = []
    lines = []

    h_ref = 1.5 / 1490
    l_ref = 2.8 / 2594

    with open(f"{path}/geology/points.geo", encoding="utf8") as file:
        for row in csv.reader(file, delimiter=" "):
            if row and row[0].startswith("Point"):
                points.append(
                    [
                        l_ref * float(row[2][1:-1]),
                        h_ref * float(row[3][:-1]),
                    ]
                )

    with open(f"{path}/geology/lines.geo", encoding="utf8") as file:
        for row in csv.reader(file, delimiter=" "):
            if not row or row[0] == "//":
                continue
            if row[0].startswith("Line"):
                lines.append([int(row[2][1:-1]) - 1, int(row[3][:-2]) - 1])

    return points, lines


def run_maps(argv=None):
    """Generate spatial overlay maps for selected times."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Generate spatial overlay maps for selected times.",
    )
    parser.add_argument("-e", "--experiment", default="run2")
    parser.add_argument("-satmin", "--minimumsaturation", type=float, default=1e-2)
    parser.add_argument("-conmin", "--minimumconcentration", type=float, default=1e-1)
    parser.add_argument("-t", "--times", default="24,48,72,96,120")
    parser.add_argument("-l", "--location", default=".")
    parser.add_argument("-p", "--path", default=".")
    args = vars(parser.parse_known_args(argv)[0])

    matplotlib.rc("font", family="normal", weight="normal", size=12)
    plt.rcParams.update(
        {
            "text.usetex": shutil.which("latex") is not None,
            "font.family": "monospace",
            "figure.figsize": (10, 5),
        }
    )

    points, lines = load_points(args["path"])

    for t in args["times"].split(","):
        simulations, x, z = segment(
            f"{args["location"]}/spatial_map_{t}h.csv",
            args["minimumsaturation"],
            args["minimumconcentration"],
        )

        name = str(int(float(t) * 3600)).zfill(6)

        experiment = np.loadtxt(
            f"{args["path"]}/fluidflower/experiment/benchmarkdata/spatial_maps/"
            f"{args["experiment"]}/segmentation_{name}s.csv",
            dtype=int,
            delimiter=",",
        )[30:, :]

        pngs(simulations, experiment, x, z, points, lines, t)


if __name__ == "__main__":
    run_maps()
