#!/usr/bin/env python3
# Modified from https://github.com/fluidflower/general/blob/main/evaluation/emd.py and
# https://github.com/fluidflower/general/blob/main/evaluation/calculate_segmented_emds.py

"""Calculate segmented FluidFlower Wasserstein-distance metrics.

The job converts simulated saturation and dissolved-CO2 fields into benchmark
segmentation classes, compares them with experimental segmentations using Earth
Mover's Distance, and writes per-observation metrics and the Everest objective."""

import argparse
import os
import sys

import numpy as np
import ot
from numpy.typing import NDArray
from PIL import Image


def _calculate_wasserstein_distance(file_1: str, file_2: str) -> float:
    """Calculate the Earth Mover's Distance between two segmented images.

    Both images are converted to grayscale, resized to 140 by 60 pixels, normalized,
    and compared on the physical FluidFlower domain.

    Parameters
    ----------
    file_1 : str
        Path to the first segmented PNG image.
    file_2 : str
        Path to the second segmented PNG image, resized in place.

    Returns
    -------
    float
        Wasserstein distance in physical x-z coordinates."""

    im1 = Image.open(file_1).convert("L")
    im1 = im1.resize((140, 60), Image.Resampling.LANCZOS)

    n_x, n_z = im1.size
    a_1 = np.array(im1.get_flattened_data()).reshape(n_x, n_z)

    im2 = Image.open(file_2).convert("L")
    im2 = im2.resize(im1.size, Image.Resampling.LANCZOS)
    b_1 = np.array(im2.get_flattened_data()).reshape(n_x, n_z)

    im2.save(file_2)

    a_1 = a_1 / np.sum(a_1)
    b_1 = b_1 / np.sum(b_1)

    a_flat = a_1.flatten(order="F")
    b_flat = b_1.flatten(order="F")

    cc_x, cc_y = np.meshgrid(np.arange(n_x), np.arange(n_z), indexing="ij")

    cc_x_flat = cc_x.flatten("F") / n_x * 2.8 + 5e-3 * 280 / n_x
    cc_y_flat = cc_y.flatten("F") / n_z * 1.2 + 5e-3 * 120 / n_z

    cost = ot.dist(
        np.vstack((cc_x_flat, cc_y_flat)).T,
        np.vstack((cc_x_flat, cc_y_flat)).T,
        metric="euclidean",
    )

    return ot.emd2(
        a_flat,
        b_flat,
        cost,
        numItermax=500000,
    )


def _segment_spatial_map(
    file_name: str,
    xlim: tuple[float, float],
    zlim: tuple[float, float],
    satmin: float,
    conmin: float,
) -> NDArray[np.int64]:
    """Convert saturation and concentration fields to benchmark classes.

    Parameters
    ----------
    file_name : str
        Spatial-map CSV containing x, z, saturation, and concentration columns.
    xlim : tuple[float, float]
        Minimum and maximum x coordinates, in metres.
    zlim : tuple[float, float]
        Minimum and maximum z coordinates, in metres.
    satmin : float
        Minimum gas saturation for class 2.
    conmin : float
        Minimum dissolved-CO2 concentration for class 1.

    Returns
    -------
    NDArray[np.int64]
        Segmentation on the 120 by 280 benchmark reporting grid."""

    n_x = np.arange(xlim[0], xlim[1] + 5.0e-3, 1.0e-2).size - 1
    n_z = np.arange(zlim[0], zlim[1] + 5.0e-3, 1.0e-2).size - 1

    tmp = 0
    with open(file_name, "r", encoding="utf8") as file:
        if not file.readline()[0].isnumeric():
            tmp = 1

    saturation = np.zeros([n_z, n_x])
    concentration = np.zeros([n_z, n_x])

    csv_data = np.genfromtxt(file_name, delimiter=",", skip_header=tmp)

    for i in np.arange(0, n_z):
        saturation[i, :] = csv_data[i * n_x : (i + 1) * n_x, 2]
        concentration[i, :] = csv_data[i * n_x : (i + 1) * n_x, 3]

    segmentmap = np.zeros((120, 280), dtype=int)
    tmp = 119

    for i in np.arange(0, n_z):
        for j in np.arange(0, n_x):
            if saturation[i, j] > satmin:
                segmentmap[tmp - i, j] = 2
            elif concentration[i, j] > conmin:
                segmentmap[tmp - i, j] = 1

    return segmentmap


def _prepare_distance_images(
    model_result: NDArray[np.int64],
    experimental_data: NDArray[np.int64],
    indx: int,
) -> float:
    """Write segmentation images and calculate their Wasserstein distance.

    The PNG round trip is retained to preserve the established metric calculation.

    Parameters
    ----------
    model_result : NDArray[np.int64]
        Simulated benchmark classes on the 120 by 280 grid.
    experimental_data : NDArray[np.int64]
        Experimental benchmark classes on the same grid.
    indx : int | str
        Evaluation-time identifier used in temporary filenames.

    Returns
    -------
    float
        Wasserstein distance between the generated images."""

    mod_image = Image.new("L", (280, 120))
    mod_pixels = mod_image.load()
    assert mod_pixels is not None

    for i in range(mod_image.size[0]):
        for j in range(mod_image.size[1]):
            if model_result[j, i] == 1:
                mod_pixels[i, j] = 128
            elif model_result[j, i] == 2:
                mod_pixels[i, j] = 255
            else:
                mod_pixels[i, j] = 0

    mod_image.save(f"mod_{indx}.png")

    exp_image = Image.new("L", (280, 120))
    exp_pixels = exp_image.load()
    assert exp_pixels is not None

    for i in range(exp_image.size[0]):
        for j in range(exp_image.size[1]):
            if experimental_data[j, i] == 1:
                exp_pixels[i, j] = 128
            elif experimental_data[j, i] == 2:
                exp_pixels[i, j] = 255
            else:
                exp_pixels[i, j] = 0

    exp_image.save(f"exp_{indx}.png")

    return _calculate_wasserstein_distance(f"mod_{indx}.png", f"exp_{indx}.png")


def main(argv=None) -> None:
    """Calculate segmented metrics and the Everest objective.

    Parameters
    ----------
    argv : list[str] | None, optional
        Arguments to parse instead of the process command line."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Segment maps at requested times and compute total EMD score.",
    )
    parser.add_argument("-s", "--minimumsaturation", default="1e-2")
    parser.add_argument("-c", "--minimumconcentration", default="1e-1")
    parser.add_argument("-e", "--experiment", default="run2")
    parser.add_argument("-t", "--times", default="24,48,72,96,120")
    parser.add_argument("-p", "--path", default=".")

    if os.path.exists("NOMONOTONIC"):
        with open("func", "w", encoding="utf8") as file:
            file.write("-1")
        sys.exit()

    args = vars(parser.parse_args(argv))
    times = [row.strip() for row in args["times"].split(",")]

    everest = 0.0
    nobs = len(times)

    with open("sim_metrics_0.txt", "w", encoding="utf8") as file:
        for time in times:
            file_i = f"spatial_map_{time}h.csv"

            model_result = _segment_spatial_map(
                file_i,
                (0.0, 2.8),
                (0.0, 1.2),
                float(args["minimumsaturation"]),
                float(args["minimumconcentration"]),
            )

            name = str(int(float(time) * 3600)).zfill(6)

            filename = (
                f"{args['path']}/fluidflower/experiment/benchmarkdata/"
                f"spatial_maps/{args['experiment']}/segmentation_{name}s.csv"
            )

            experimental_data = np.loadtxt(filename, dtype="int", delimiter=",")
            experimental_data = experimental_data[30:, :]

            dist = (
                8.5
                * 100
                * _prepare_distance_images(
                    model_result,
                    experimental_data,
                    time,
                )
            )

            file.write(f"{dist}\n")
            everest += dist

    with open("func", "w", encoding="utf8") as file:
        file.write(f"{-everest/(8.5*100*nobs)}")


if __name__ == "__main__":
    main()
