#!/usr/bin/env python3
# Modified from https://github.com/fluidflower/general/blob/main/evaluation/emd.py and
# https://github.com/fluidflower/general/blob/main/evaluation/calculate_segmented_emds.py

"""
Plot spatial results and compute Wasserstein (EMD) distances
between simulated and experimental segmentations.
"""

import argparse
import os
import sys
import numpy as np
import ot
from PIL import Image

# ============================================================
# Wasserstein / EMD
# ============================================================


def calculate_emd(file_1, file_2):
    """
    Compute Wasserstein distance between two images.
    Reproduces the original numerical behavior exactly.
    """

    # --- Load and resize first image ---
    im1 = Image.open(file_1).convert("L")
    im1 = im1.resize((140, 60), Image.Resampling.LANCZOS)

    # NOTE: reshape order is intentional
    n_x, n_z = im1.size
    a_1 = np.array(im1.get_flattened_data()).reshape(n_x, n_z)

    # --- Load and resize second image ---
    im2 = Image.open(file_2).convert("L")
    im2 = im2.resize(im1.size, Image.Resampling.LANCZOS)
    b_1 = np.array(im2.get_flattened_data()).reshape(n_x, n_z)

    # Save resized image to ensure reproducibility
    im2.save(file_2)

    # Normalize mass distributions
    a_1 = a_1 / np.sum(a_1)
    b_1 = b_1 / np.sum(b_1)

    # Flatten using Fortran order
    a_flat = a_1.flatten(order="F")
    b_flat = b_1.flatten(order="F")

    # --- Cell center coordinates (fixed definition) ---
    cc_x = np.zeros((n_x, n_z), dtype=float).flatten("F")
    cc_y = np.zeros((n_x, n_z), dtype=float).flatten("F")

    cc_x, cc_y = np.meshgrid(np.arange(n_x), np.arange(n_z), indexing="ij")

    cc_x_flat = cc_x.flatten("F") / n_x * 2.8 + 5e-3 * 280 / n_x
    cc_y_flat = cc_y.flatten("F") / n_z * 1.2 + 5e-3 * 120 / n_z

    # Pairwise Euclidean cost matrix
    cost = ot.dist(
        np.vstack((cc_x_flat, cc_y_flat)).T,
        np.vstack((cc_x_flat, cc_y_flat)).T,
        metric="euclidean",
    )

    # Compute EMD with fixed iteration limit
    return ot.emd2(
        a_flat,
        b_flat,
        cost,
        numItermax=500000,
    )


# ============================================================
# Segmentation
# ============================================================


def generate_segment_map(
    file_name,
    xlim,
    zlim,
    satmin,
    conmin,
):
    """
    Convert continuous saturation and concentration fields
    into a discrete segmentation map.
    """

    # Define structured grid
    dic = {"xcord": np.arange(xlim[0], xlim[1] + 5.0e-3, 1.0e-2)}
    dic["zcord"] = np.arange(zlim[0], zlim[1] + 5.0e-3, 1.0e-2)
    dic["n_x"] = dic["xcord"].size - 1
    dic["n_z"] = dic["zcord"].size - 1

    # Detect optional CSV header
    skip_header = 0
    with open(file_name, "r", encoding="utf8") as file:
        if not file.readline()[0].isnumeric():
            skip_header = 1

    saturation = np.zeros([dic["n_z"], dic["n_x"]])
    concentration = np.zeros([dic["n_z"], dic["n_x"]])

    csv_data = np.genfromtxt(file_name, delimiter=",", skip_header=skip_header)

    # Populate grids row-wise
    for i in np.arange(0, dic["n_z"]):
        saturation[i, :] = csv_data[i * dic["n_x"] : (i + 1) * dic["n_x"], 2]
        concentration[i, :] = csv_data[i * dic["n_x"] : (i + 1) * dic["n_x"], 3]

    # Target segmentation map
    segmentmap = np.zeros((120, 280), dtype=int)
    in0 = 119

    # Assign phase labels
    for i in np.arange(0, dic["n_z"]):
        for j in np.arange(0, dic["n_x"]):
            if saturation[i, j] > satmin:
                segmentmap[in0 - i, j] = 2
            elif concentration[i, j] > conmin:
                segmentmap[in0 - i, j] = 1

    return segmentmap


# ============================================================
# Image creation + EMD bridge
# ============================================================


def before_emd(model_result, experimental_data, indx):
    """
    Create PNG images from segmentation maps and compute EMD.
    PNG round-trip is required to preserve original behavior.
    """

    # --- Model image ---
    mod_image = Image.new("L", (280, 120))
    mod_pixels = mod_image.load()

    for i in range(mod_image.size[0]):
        for j in range(mod_image.size[1]):
            if model_result[j, i] == 1:
                mod_pixels[i, j] = 128
            elif model_result[j, i] == 2:
                mod_pixels[i, j] = 255
            else:
                mod_pixels[i, j] = 0

    mod_image.save(f"mod_{indx}.png")

    # --- Experimental image ---
    exp_image = Image.new("L", (280, 120))
    exp_pixels = exp_image.load()

    for i in range(exp_image.size[0]):
        for j in range(exp_image.size[1]):
            if experimental_data[j, i] == 1:
                exp_pixels[i, j] = 128
            elif experimental_data[j, i] == 2:
                exp_pixels[i, j] = 255
            else:
                exp_pixels[i, j] = 0

    exp_image.save(f"exp_{indx}.png")

    return calculate_emd(f"mod_{indx}.png", f"exp_{indx}.png")


# ============================================================
# Main
# ============================================================


def main():
    """
    Segment maps at requested times and compute total EMD score.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Segment maps at requested times and compute total EMD score.",
    )
    parser.add_argument("-s", "--minimumsaturation", default="1e-2")
    parser.add_argument("-c", "--minimumconcentration", default="1e-1")
    parser.add_argument("-e", "--experiment", default="run2")
    parser.add_argument("-t", "--times", default="24,48,72,96,120")
    parser.add_argument("-p", "--path", default=".")

    # Early termination for non-monotonic runs
    if os.path.exists("NOMONOTONIC"):
        with open("func", "w", encoding="utf8") as file:
            file.write("-1")
        sys.exit()

    args = vars(parser.parse_args())
    times = [row.strip() for row in args["times"].split(",")]

    everest = 0.0
    nobs = len(times)

    # Write per-time Wasserstein distances
    with open("sim_metrics_0.txt", "w", encoding="utf8") as file:
        for time in times:
            file_i = f"spatial_map_{time}h.csv"

            model_result = generate_segment_map(
                file_i,
                [0.0, 2.8],
                [0.0, 1.2],
                float(args["minimumsaturation"]),
                float(args["minimumconcentration"]),
            )

            # Convert hours to seconds (zero-padded)
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
                * before_emd(
                    model_result,
                    experimental_data,
                    time,
                )
            )

            file.write(f"{dist}\n")
            everest += dist

    # Write final normalized objective value
    with open("func", "w", encoding="utf8") as file:
        file.write(f"{-everest/(8.5*100*nobs)}")


if __name__ == "__main__":
    main()
