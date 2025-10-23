# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1702

"""
Utiliy functions to set the requiried input values by pofff.
"""

import tomllib
import numpy as np


def process_input(dic, in_file):
    """
    Process the configuration file

    Args:
        dic (dict): Global dictionary\n
        in_file (str): Name of the input text file

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["monotonic"] = False
    dic["popsize"] = 15
    dic["experiment"] = "run" + dic["experiment"][-1]
    with open(in_file, "rb") as file:
        dic.update(tomllib.load(file))
    dic["PARA"] = {}
    for i in range(1, 7):
        dic["PARA"].update(dic[f"facie{i}"])
        del dic[f"facie{i}"]
    dic["PARA"].update(
        {
            "PERMX7": 0,
            "PERMZ7": 0,
            "PORO7": 0,
            "DISPERC7": 0,
            "SWI7": 0,
            "SNI7": 0,
            "PEN7": 0,
            "NKRW7": 2,
            "NKRN7": 2,
            "NPE7": 2,
            "THRE7": 5e-2,
            "NPNT7": 2,
        }
    )
    dic["dims"] = [2.8, 0.019, 1.2]
    dic["sensors"] = [[1.5, 0.005, 0.5], [1.7, 0.005, 1.1]]
    dic["boxa"] = [[1.1, 0.0, 0.0], [2.8, 0.01, 0.6]]
    dic["boxb"] = [[0.0, 0.0, 0.6], [1.1, 0.01, 1.2]]
    dic["boxc"] = [[1.1, 0.0, 0.1], [2.6, 0.01, 0.4]]
    dic["noCells"] = [sum(dic["x"]), 1, sum(dic["z"])]
    dic["diffusion"] = np.array(dic["diffusion"]) * 86400  # To [m^2/day]
    dic["noSands"] = 7
    dic["y"] = [1]
    dic["sources"][0][-1] = dic["dims"][2] - dic["sources"][0][-1]
    dic["sources"][1][-1] = dic["dims"][2] - dic["sources"][1][-1]
    dic["data"] = dic["fol"].split("/")[-1].upper()
    handle_thickness_map(dic)
    dic["tuning"] = False
    for value in dic["flow"].split():
        if "--enable-tuning" in value:
            if value[16:] in ["true", "True", "1"]:
                dic["tuning"] = True
                for i, inj in enumerate(dic["inj"]):
                    if len(inj) == 5:
                        tmp = inj[-1].split("/")
                        dic["inj"][i][-1] = tmp[0].strip()
                        if len(tmp) > 1:
                            for val in tmp[1:]:
                                dic["inj"][i].append(val.strip())
    if (
        dic["x"] != [140]
        or dic["z"] != [7, 5, 5, 5, 5, 5, 5, 8, 10, 9, 5]
        or dic["grid"] != "corner-point"
    ):
        dic["cellmaps"] = []
        dic["simxcent"] = []
        dic["simzcent"] = []
        refx = np.arange(0, 2.8 + 5.0e-3, 1.0e-2)
        refz = np.arange(0, 1.2 + 5.0e-3, 1.0e-2)
        refx = 0.5 * (refx[1:] + refx[:-1])
        refz = 0.5 * (refz[1:] + refz[:-1])
        dic["refxgrid"] = np.zeros(280 * 120)
        dic["refzgrid"] = np.zeros(280 * 120)
        ind = 0
        for zcen in refz:
            for xcen in refx:
                dic["refxgrid"][ind] = xcen
                dic["refzgrid"][ind] = zcen
                ind += 1


def handle_thickness_map(dic):
    """
    Set the thickness map (y size)

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    if dic["thickness"] == "final":
        dic["multpv"] = []
        thickness = np.load(f"{dic['path']}/geology/final_thickness.npy")
        dic["dims"][1] = thickness.min()
        dic["multThickness"] = (
            dic["mult_thickness"] * thickness.reshape(-1) / thickness.min()
        )
        dic["refx"] = np.arange(0, 2.8 + 5.0e-3, 1.0e-2)
        dic["refzd"] = 1.5 - np.arange(0, 1.5 + 5.0e-3, 1.0e-2)
        dic["refxcent"] = 0.5 * (dic["refx"][1:] + dic["refx"][:-1])
        dic["refzdcent"] = 0.5 * (dic["refzd"][1:] + dic["refzd"][:-1])
        dic["refxthickness"], dic["refzthickness"] = [], []
        for k in dic["refzdcent"]:
            for i in dic["refxcent"]:
                dic["refxthickness"].append(i)
                dic["refzthickness"].append(k)
        dic["refxthickness"] = np.array(dic["refxthickness"])
        dic["refzthickness"] = np.array(dic["refzthickness"])
    elif dic["thickness"] == "initial":
        dic["multpv"] = []
        thickness = np.genfromtxt(
            f"{dic['path']}/geology/initial_thickness.csv",
            delimiter=",",
            skip_header=0,
        )
        dic["refxthickness"] = thickness[:, 0] - 0.03
        dic["refzthickness"] = 1.34 - thickness[:, 2]
        dic["dims"][1] = thickness[:, 1].min()
        dic["multThickness"] = (
            dic["mult_thickness"] * thickness[:, 1].reshape(-1) / thickness[:, 1].min()
        )
    else:
        dic["dims"][1] = float(dic["thickness"])
