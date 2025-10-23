# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0912,R0915

"""Main script for pofff"""

import os
import argparse
from pofff.utils.inputvalues import process_input
from pofff.utils.runs import flow, data, benchmark, everest, ert
from pofff.utils.writefile import opm_files
from pofff.utils.mapproperties import grid, positions


def pofff():
    """Main function for the pofff executable"""
    cmdargs = load_parser()
    file = cmdargs["input"].strip()  # Name of the input file
    dic = {"fol": os.path.abspath(cmdargs["output"])}  # Name for the output folder
    dic["figures"] = cmdargs["figures"].strip()  # Which figures to generate
    dic["experiment"] = cmdargs["experiment"].strip()  # Experiment to history match
    dic["mode"] = cmdargs["mode"].strip()  # Parts of the workflow to run
    dic["path"] = os.path.dirname(__file__)[:-5]  # Path to the pofff folder
    dic["times"] = cmdargs["times"]  # Temporal resolution to write the dense data
    dic["latex"] = int(cmdargs["latex"])  # LaTeX formatting
    dic["mcon"] = cmdargs["minimumconcentration"]  # Con threshold for segmentation
    dic["msat"] = cmdargs["minimumsaturation"]  # Sat threshold for segmentation
    dic["use"] = cmdargs["use"]  # Use precopmpued WD matrix?

    if not os.path.exists(f"{dic['fol']}"):  # Make the output folders
        os.system(f"mkdir {dic['fol']}")

    dic["location"] = dic["path"] + "/fluidflower/cssr/conmin"
    dic["location"] += "5e-2" if float(dic["mcon"]) == 5e-2 else "1e-1"

    if dic["mode"] != "fair":
        dic["add"] = "1"
        process_input(dic, file)  # Process the input file

        dic["deck"] = dic["jobs"] = dic["fol"]
        if dic["mode"] in ["ert", "everest"]:
            for name in ["deck", "jobs"]:
                dic[name] += f"/{name}"
                if not os.path.exists(f"{dic['fol']}/{name}"):
                    os.system(f"mkdir {dic['fol']}/{name}")
        os.chdir(f"{dic['fol']}")
        if dic["mode"] not in ["none", "data"]:
            print("\nGenerating the input files, please wait.")
            grid(dic)  # Initialize the grid
            positions(dic)  # Get the sand and source positions
            opm_files(dic)  # Write used opm related files
    else:
        os.chdir(f"{dic['fol']}")
        dic["add"] = "0"
        dic["figures"] = "all"
        dic["times"] = "24,48,72,96,120"
        dic["experiment"] = "run2"
    if dic["mode"] == "single":
        print("\nRunning the simulation, please wait.")
        flow(dic)
        print("\nGenerating the data, please wait.")
        data(dic)
        print(f"\nThe results have been written to {dic['fol']}")
    elif dic["mode"] == "data":
        print("\nGenerating the data, please wait.")
        data(dic)
        print(f"\nThe results have been written to {dic['fol']}")
    elif dic["mode"] == "everest":
        os.system(f"cp -a {dic['path']}/jobs/. {dic['fol']}/jobs/.")
        print("\nRunning everest, please wait.")
        everest(dic)
        print(f"\nThe results have been written to {dic['fol']}")
    elif dic["mode"] == "ert":
        os.system(f"cp -a {dic['path']}/jobs/. {dic['fol']}/jobs/.")
        print("\nRunning ert, please wait.")
        ert(dic)
        print(f"\nThe results have been written to {dic['fol']}")

    if dic["figures"] in ["all", "basic"]:
        if os.path.exists(f"{dic['fol']}/figures/best_simulation"):
            os.chdir(f"{dic['fol']}/figures/best_simulation")
        else:
            os.chdir(f"{dic['fol']}")
        print("\nGenerating the benchmark files, please wait.")
        benchmark(dic)
        print(f"\nThe results have been written to {dic['fol']}")


def load_parser():
    """Argument options"""
    parser = argparse.ArgumentParser(
        description="pofff, a Python tool for history matching the "
        "FluidFlower images using OPM Flow, ERT, and everest.",
    )
    parser.add_argument(
        "-i",
        "--input",
        default="input.toml",
        help="The base name of the input file ('input.toml' by default).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="The base name of the output folder ('output' by default).",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="single",
        help="Run a 'single' simulation, 'data', 'everest', 'ert', 'fair', or "
        "'none' (i.e., useful to generate the benchmark figures) ('single' by "
        "default).",
    )
    parser.add_argument(
        "-t",
        "--times",
        default="0.25",
        help="Times in hours separated by commas to evaluate the metrics "
        "('0.25' by default).",
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
        "-e",
        "--experiment",
        default="C2",
        help="Experimental data to history match, valid options are C1 to C5 "
        "('C2' by default).",
    )
    parser.add_argument(
        "-l",
        "--latex",
        default=1,
        help="Set to 0 to not use LaTeX formatting ('1' by default).",
    )
    parser.add_argument(
        "-s",
        "--minimumsaturation",
        default="1e-2",
        help="The minimum saturation above which gaseous CO2 is considered for "
        "the segmentation ('1e-2' by default).",
    )
    parser.add_argument(
        "-c",
        "--minimumconcentration",
        default="1e-1",
        help="The minimum concentration above which CO2 is considered to be "
        "dissolved for the segmentation ('1e-1' by default).",
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


def main():
    """Main function"""
    pofff()
