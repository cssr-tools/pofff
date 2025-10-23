#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to generate figures with the benchmark format.
"""

import argparse
import os
import matplotlib
import matplotlib.pyplot as plt

font = {"family": "normal", "weight": "normal", "size": 14}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "legend.columnspacing": 0.9,
        "font.family": "monospace",
        "legend.handlelength": 3.5,
        "legend.fontsize": 14,
        "lines.linewidth": 4,
        "axes.titlesize": 14,
        "axes.grid": False,
        "figure.figsize": (16, 8),
    }
)


def postprocessing():
    """Main function to generate the benchmark figures"""
    cmdargs = load_parser()
    dic = {"t": cmdargs["times"]}
    dic["s"] = float(cmdargs["minimumsaturation"])
    dic["c"] = float(cmdargs["minimumconcentration"])
    dic["f"] = cmdargs["figures"].strip()
    dic["p"] = cmdargs["path"] + "/fluidflower/"
    dic["l"] = cmdargs["location"]
    dic["a"] = cmdargs["add"]
    dic["u"] = cmdargs["use"] == "1"
    benchmark(dic)


def benchmark(dic):
    """Figures and comaparisons to benchmark data"""
    os.system(
        f"python3 {dic['p']}general/evaluation/compare_time_series_pofff.py"
        + f" -p {dic['p']} -l {dic['l']} -a {dic['a']}"
    )
    os.system(
        f"python3 {dic['p']}general/evaluation/compare_sparse_data_pofff.py"
        + f" -p {dic['p']} -l {dic['l']} -a {dic['a']}"
    )
    if dic["f"] == "all":
        if dic["s"] == 0.01 and dic["c"] in [0.05, 0.1] and dic["u"]:
            os.system(
                f"python3 {dic['p']}general/evaluation/"
                + "calculate_segmented_emds_simplified_pofff.py "
                + f"-p {dic['p']} -satmin {dic['s']} "
                + f"-conmin {dic['c']} -l {dic['l']} -a {dic['a']}"
            )
        else:
            os.system(
                "python3 "
                + f"{dic['p']}general/evaluation/calculate_segmented_emds_pofff.py "
                + f"-p {dic['p']} -satmin {dic['s']} "
                + f"-conmin {dic['c']} -l {dic['l']} -a {dic['a']}"
            )
        os.system(
            "python3 "
            + f"{dic['p']}general/evaluation/means_from_segmented_distances"
            + f"_pofff.py -satmin {dic['s']} -conmin {dic['c']} -a {dic['a']}"
        )


def load_parser():
    """Argument options"""
    parser = argparse.ArgumentParser(
        description="Script to manage the generation of figures with the benchmark "
        " format."
    )
    parser.add_argument(
        "-c",
        "--minimumconcentration",
        default=0.1,
        help="The min conc above which CO2 is considered to be dissolved for the segmentation.",
    )
    parser.add_argument(
        "-s",
        "--minimumsaturation",
        default=0.01,
        help="The minimum saturation above which gaseous CO2 is considered for the segmentation.",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="./",
        help="Path to the fluidflower data.",
    )
    parser.add_argument(
        "-t",
        "--times",
        default="24,48,72,96,120",
        help="Times in hours for the images.",
    )
    parser.add_argument(
        "-f",
        "--figures",
        default="basic",
        help="'all' to generate all benchmark figures, 'basic' to not generate the "
        "Wasserstain distance plot (it is slow), and 'none' for no figures ('basic' "
        "by default).",
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
    parser.add_argument(
        "-u",
        "--use",
        default="1",
        help="Use the precomputed wasserstein distance matrix values for minimum "
        "concentration of 1e-1 and 5e-2 (min sat of 1e-2) to speed up the "
        "computations ('1' by default; set to '0' to compute all).",
    )
    return vars(parser.parse_known_args()[0])


if __name__ == "__main__":
    postprocessing()
