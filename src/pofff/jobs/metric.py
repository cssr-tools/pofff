#!/usr/bin/env python3
# Modified from https://github.com/fluidflower/general/blob/main/evaluation/emd.py and
# https://github.com/fluidflower/general/blob/main/evaluation/calculate_segmented_emds.py

"""
Script to plot the results
"""

import argparse
import os
import sys
import numpy as np
import ot
from PIL import Image


def calculate_emd(file_1, file_2):
    """Compute the Wasserstein distance"""
    # Define problem size
    # NOTE: ot has severe memory restrictions - cv2 has much more mild restrictions
    # Furthermore, computing the exact EMD has O(n**3) complexity and can therefore be
    # quite slow.

    # Define distributions
    im1 = Image.open(file_1).convert("L")
    im1 = im1.resize((140, 60), Image.Resampling.LANCZOS)
    n_x, n_z = im1.size
    a_1 = np.array(im1.getdata()).reshape(n_x, n_z)

    im2 = Image.open(file_2).convert("L")
    im2 = im2.resize(im1.size, Image.Resampling.LANCZOS)
    b_1 = np.array(im2.getdata()).reshape(n_x, n_z)
    im2.save(file_2)

    # Make a and b 'true' distributions
    # NOTE: cv2 will internally convert a and b to distributions (summing
    # up to 1), while ot is not.
    # Furthermore, it requires a and b to be compatible, i.e., that their
    # sums are equal. While cv2 does not, it is however also not clear
    # how to interpret the result for non-compatible signals.
    a_1 = a_1 / np.sum(a_1)
    b_1 = b_1 / np.sum(b_1)

    # Determine EMD using ot
    # OT takes 1d arrays as inputs
    a_flat = a_1.flatten(order="F")
    b_flat = b_1.flatten(order="F")

    # Cell centers of all cells - x and y coordinates.
    cc_x = np.zeros((n_x, n_z), dtype=float).flatten("F")
    cc_y = np.zeros((n_x, n_z), dtype=float).flatten("F")

    cc_x, cc_y = np.meshgrid(np.arange(n_x), np.arange(n_z), indexing="ij")

    cc_x_flat = cc_x.flatten("F") / n_x * 2.8 + 5e-3 * 280 / n_x
    cc_y_flat = cc_y.flatten("F") / n_z * 1.2 + 5e-3 * 120 / n_z

    # Distance matrix
    # NOTE the definition of this distance matrix is memory consuming and
    # does not allow for too large distributions.

    return ot.emd2(
        a_flat,
        b_flat,
        ot.dist(
            np.vstack((cc_x_flat, cc_y_flat)).T,
            np.vstack((cc_x_flat, cc_y_flat)).T,
            metric="euclidean",
        ),
        numItermax=500000,
    )


def generate_segment_map(
    file_name,
    xlim,
    zlim,
    satmin,
    conmin,
):
    """Use the thresholds for the segmentation"""
    dic = {"xcord": np.arange(xlim[0], xlim[1] + 5.0e-3, 1.0e-2)}
    dic["zcord"] = np.arange(zlim[0], zlim[1] + 5.0e-3, 1.0e-2)
    dic["n_x"] = dic["xcord"].size - 1
    dic["n_z"] = dic["zcord"].size - 1

    skip_header = 0
    with open(file_name, "r", encoding="utf8") as file:
        if not (file.readline()[0]).isnumeric():
            skip_header = 1

    saturation = np.zeros([dic["n_z"], dic["n_x"]])
    concentration = np.zeros([dic["n_z"], dic["n_x"]])
    csv_data = np.genfromtxt(file_name, delimiter=",", skip_header=skip_header)
    for i in np.arange(0, dic["n_z"]):
        saturation[i, :] = csv_data[i * dic["n_x"] : (i + 1) * dic["n_x"], 2]
        concentration[i, :] = csv_data[i * dic["n_x"] : (i + 1) * dic["n_x"], 3]
    segmentmap = np.zeros((120, 280), dtype=int)
    in0 = 119

    # Start from the fourth row as the first three are not contained in the experimental data
    for i in np.arange(0, dic["n_z"]):
        # For the same reason, exclude the first and last three columns
        for j in np.arange(0, dic["n_x"] - 0):
            # The first row of the segment map corresponds to the top of the domain
            if saturation[i, j] > satmin:
                segmentmap[in0 + 0 - i, j - 0] = 2
            elif concentration[i, j] > conmin:
                segmentmap[in0 + 0 - i, j - 0] = 1

    return segmentmap


def before_emd(model_result, experimental_data, indx):
    """Segment the results"""
    mod_image = Image.new("L", (280, 120))
    mod_pixels = mod_image.load()
    for i in range(0, mod_image.size[0]):
        for j in range(0, mod_image.size[1]):
            if model_result[j, i] == 1:
                mod_pixels[i, j] = 128
            elif model_result[j, i] == 2:
                mod_pixels[i, j] = 255
            else:
                mod_pixels[i, j] = 0
    mod_image.save(f"mod_{indx}.png")

    exp_image = Image.new("L", (280, 120))
    exp_pixels = exp_image.load()
    for i in range(0, exp_image.size[0]):
        for j in range(0, exp_image.size[1]):
            if experimental_data[j, i] == 1:
                exp_pixels[i, j] = 128
            elif experimental_data[j, i] == 2:
                exp_pixels[i, j] = 255
            else:
                exp_pixels[i, j] = 0

    exp_image.save(f"exp_{indx}.png")

    return calculate_emd(f"mod_{indx}.png", f"exp_{indx}.png")


def main():
    """Script to evaluate the Wasserstein distance"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--minimumsaturation",
        default="1e-2",
        help="The minimum saturation above which gaseous CO2 is considered for the segmentation.",
    )
    parser.add_argument(
        "-c",
        "--minimumconcentration",
        default="1e-1",
        help="The min conc above which CO2 is considered to be dissolved for the segmentation.",
    )
    parser.add_argument(
        "-e",
        "--experiment",
        default="run2",
        help="Experimental data to history match, valid options are run1 to run5 "
        "('run2' by default).",
    )
    parser.add_argument(
        "-t",
        "--times",
        default="24,48,72,96,120",
        help="Times for the images in [h].",
    )
    parser.add_argument(
        "-p", "--path", default=".", help="Path to the fluidflower data."
    )
    if os.path.exists("NOMONOTONIC"):
        with open("func", "w", encoding="utf8") as file:
            file.write("-1")
        sys.exit()
    cmdargs = vars(parser.parse_args())
    times = [row.strip() for row in cmdargs["times"].split(",")]
    everest = 0.0
    nobs = len(times)
    with open("sim_metrics_0.txt", "w", encoding="utf8") as file:
        for time in times:
            file_i = f"spatial_map_{time}h.csv"
            model_result_i = generate_segment_map(
                file_i,
                [0.0, 2.8],
                [0.0, 1.2],
                float(cmdargs["minimumsaturation"]),
                float(cmdargs["minimumconcentration"]),
            )
            name = f"{int(float(time)*3600)}"
            zeros = 6 - len(name)
            for _ in range(zeros):
                name = "0" + name
            filename = (
                f"{cmdargs['path']}/fluidflower/experiment/benchmarkdata/"
                + f"spatial_maps/{cmdargs['experiment']}/segmentation_"
                + name
                + "s.csv"
            )
            experimental_data_j = np.loadtxt(filename, dtype="int", delimiter=",")
            # skip the first 30 rows as they are not contained in the modeling results
            experimental_data_j = experimental_data_j[30:, :]
            # The calculated distances have the unit of normalized mass times meter.
            # Multiply by 8.5, the injected mass of CO2 in g, and 100, to convert to g.cm.
            dist = (
                8.5
                * 100
                * before_emd(
                    model_result_i,
                    experimental_data_j,
                    time,
                )
            )
            file.write(f"{dist}\n")
            everest += dist
    with open("func", "w", encoding="utf8") as file:
        file.write(f"{-everest/(8.5*100*nobs)}")


if __name__ == "__main__":
    main()
