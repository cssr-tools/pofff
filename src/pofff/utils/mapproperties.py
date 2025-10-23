# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0302, R0912, R0914, R0915, E1102

"""
Utiliy function for the grid and locations in the geological models.
"""

import os
import csv
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon
from alive_progress import alive_bar
from pofff.utils.writefile import create_corner_point_grid


def grid(dic):
    """
    Handle the different grid types (Cartesian, tensor, and corner-point grids)

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    getpolygons(dic)
    if dic["grid"] == "corner-point":
        corner(dic)
    elif dic["grid"] == "cartesian":
        dic["dsize"] = [1.0 * dic["dims"][i] / dic["noCells"][i] for i in range(3)]
        for i, name in enumerate(["xmx", "ymy", "zmz"]):
            dic[f"{name}"] = np.linspace(0, dic["dims"][i], dic["noCells"][i] + 1)
    else:
        for i, (name, arr) in enumerate(zip(["xmx", "ymy", "zmz"], ["x", "y", "z"])):
            dic[f"{name}"] = [0.0]
            for j, num in enumerate(dic[f"{arr}"]):
                for k in range(num):
                    dic[f"{name}"].append(
                        (j + (k + 1.0) / num) * dic["dims"][i] / len(dic[f"{arr}"])
                    )
            dic[f"{name}"] = np.array(dic[f"{name}"])
            dic["noCells"][i] = len(dic[f"{name}"]) - 1
    if dic["grid"] != "corner-point":
        for name, size in zip(["xmx", "ymy", "zmz"], ["dx", "dy", "dz"]):
            dic[f"{name}_center"] = (dic[f"{name}"][1:] + dic[f"{name}"][:-1]) / 2.0
            dic[f"{size}"] = dic[f"{name}"][1:] - dic[f"{name}"][:-1]


def structured_handling_fluidflower(dic):
    """
    Locate the geological positions in the tensor/cartesian grid for fluidflower

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    sensor1, sensor2 = [], []
    with alive_bar(dic["noCells"][0] * dic["noCells"][2]) as bar_animation:
        for k in range(dic["noCells"][2]):
            for i in range(dic["noCells"][0]):
                bar_animation()
                n = -1
                for ind in range(len(dic["polygons"])):
                    if dic["polygons"][ind].contains(
                        Point(dic["xmx_center"][i], dic["zmz_center"][k])
                    ):
                        n = dic["facies"][ind]
                        break
                sensor1.append(
                    (dic["xmx_center"][i] - dic["sensors"][0][0]) ** 2
                    + (dic["zmz_center"][k] + dic["sensors"][0][2] - dic["dims"][2])
                    ** 2
                )
                sensor2.append(
                    (dic["xmx_center"][i] - dic["sensors"][1][0]) ** 2
                    + (dic["zmz_center"][k] + dic["sensors"][1][2] - dic["dims"][2])
                    ** 2
                )
                dic["fluxnum"].append(str(n))
                boxes(
                    dic,
                    dic["xmx_center"][i],
                    dic["zmz_center"][k],
                    dic["fluxnum"][-1],
                )
                if "multpv" in dic:
                    indx = pd.Series(
                        abs(
                            (dic["refxthickness"] - dic["xmx_center"][i]) ** 2
                            + (
                                dic["refzthickness"]
                                - dic["dims"][2]
                                + dic["zmz_center"][k]
                            )
                            ** 2
                        )
                    ).argmin()
                    dic["multpv"].append(str(dic["multThickness"][indx]))
                if "cellmaps" in dic:
                    dic["simxcent"].append(dic["xmx_center"][i])
                    dic["simzcent"].append(dic["dims"][2] - dic["zmz_center"][k])
    dic["pop1"] = pd.Series(sensor1).argmin()
    dic["pop2"] = pd.Series(sensor2).argmin()
    dic["fipnum"][dic["pop1"]] = "8"
    dic["fipnum"][dic["pop2"]] = "9"
    sensors(dic)
    wells(dic)


def corner_point_handling_fluidflower(dic):
    """
    Locate the geological positions in the corner-point grid for the fluidflower

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    well1, well2, sensor1, sensor2 = [], [], [], []
    dic["wellijk"] = [[] for _ in range(len(dic["sources"]))]
    with alive_bar(dic["no_cells"]) as bar_animation:
        for i in range(dic["no_cells"]):
            bar_animation()
            i_x = int(i % dic["noCells"][0])
            k_z = int(np.floor(i / dic["noCells"][0]))
            n = -1
            for ind in range(len(dic["polygons"])):
                if dic["polygons"][ind].contains(
                    Point(dic["xyz"][i][0], dic["xyz"][i][2])
                ):
                    n = dic["facies"][ind]
                    break
            well1.append(
                (dic["sources"][0][0] - dic["xyz"][i][0]) ** 2
                + (dic["sources"][0][2] - dic["xyz"][i][2]) ** 2
            )
            well2.append(
                (dic["sources"][1][0] - dic["xyz"][i][0]) ** 2
                + (dic["sources"][1][2] - dic["xyz"][i][2]) ** 2
            )
            sensor1.append(
                (dic["xyz"][i][0] - dic["sensors"][0][0]) ** 2
                + (dic["xyz"][i][2] + dic["sensors"][0][2] - dic["dims"][2]) ** 2
            )
            sensor2.append(
                (dic["xyz"][i][0] - dic["sensors"][1][0]) ** 2
                + (dic["xyz"][i][2] + dic["sensors"][1][2] - dic["dims"][2]) ** 2
            )
            dic["fluxnum"].append(str(n))
            boxes(dic, dic["xyz"][i][0], dic["xyz"][i][2], dic["fluxnum"][-1])
            if "multpv" in dic:
                indx = pd.Series(
                    abs(
                        (dic["refxthickness"] - dic["xyz"][i][0]) ** 2
                        + (dic["refzthickness"] - dic["dims"][2] + dic["xyz"][i][2])
                        ** 2
                    )
                ).argmin()
                dic["multpv"].append(str(dic["multThickness"][indx]))
            if "cellmaps" in dic:
                dic["simxcent"].append(dic["xyz"][i][0])
                dic["simzcent"].append(dic["dims"][2] - dic["xyz"][i][2])
    dic["pop1"] = pd.Series(sensor1).argmin()
    dic["pop2"] = pd.Series(sensor2).argmin()
    dic["fipnum"][dic["pop1"]] = "8"
    dic["fipnum"][dic["pop2"]] = "9"
    idwell1 = pd.Series(well1).argmin()
    idwell2 = pd.Series(well2).argmin()
    i_x = int(idwell1 % dic["noCells"][0])
    k_z = int(np.floor(idwell1 / dic["noCells"][0]))
    well1ijk = [i_x, 0, k_z]
    i_x = int(idwell2 % dic["noCells"][0])
    k_z = int(np.floor(idwell2 / dic["noCells"][0]))
    well2ijk = [i_x, 0, k_z]
    i_x = int(dic["pop1"] % dic["noCells"][0])
    k_z = int(np.floor(dic["pop1"] / dic["noCells"][0]))
    dic["sensorijk"][0] = [i_x, 0, k_z]
    i_x = int(dic["pop2"] % dic["noCells"][0])
    k_z = int(np.floor(dic["pop2"] / dic["noCells"][0]))
    dic["sensorijk"][1] = [i_x, 0, k_z]
    dic["wellijk"][0] = [well1ijk[0] + 1, 1, well1ijk[2] + 1]
    dic["wellijk"][1] = [well2ijk[0] + 1, 1, well2ijk[2] + 1]


def boxes(dic, x_c, z_c, fluxnum):
    """
    Find the global indices for the different boxes for the report data

    Args:
        dic (dict): Global dictionary\n
        x_c (float): x-position of the cell center\n
        z_c (float): z-position of the cell center\n
        fluxnum (int): Number of the facie in the cell

    Returns:
        dic (dict): Modified global dictionary

    """
    if (
        (dic["dims"][2] - z_c >= dic["boxb"][0][2])
        & (dic["dims"][2] - z_c <= dic["boxb"][1][2])
        & (x_c >= dic["boxb"][0][0])
        & (x_c <= dic["boxb"][1][0])
    ):
        check_facie1(dic, fluxnum, "6", "3")
    elif (
        (dic["dims"][2] - z_c >= dic["boxc"][0][2])
        & (dic["dims"][2] - z_c <= dic["boxc"][1][2])
        & (x_c >= dic["boxc"][0][0])
        & (x_c <= dic["boxc"][1][0])
    ):
        check_facie1(dic, fluxnum, "12", "4")
    elif (
        (dic["dims"][2] - z_c >= dic["boxa"][0][2])
        & (dic["dims"][2] - z_c <= dic["boxa"][1][2])
        & (x_c >= dic["boxa"][0][0])
        & (x_c <= dic["boxa"][1][0])
    ):
        check_facie1(dic, fluxnum, "5", "2")
    elif fluxnum == "1":
        dic["fipnum"].append("7")
    else:
        dic["fipnum"].append("1")


def check_facie1(dic, fluxnum, numa, numb):
    """
    Handle the overlaping with facie 1

    Args:
        dic (dict): Global dictionary\n
        fluxnum (int): Number of the facie in the cell\n
        numa (int): Fipnum to assign to the cell if it overlaps with Facie 1\n
        numb (int): Fipnum to assign to the cell otherwise.

    Returns:
        dic (dict): Modified global dictionary

    """
    if fluxnum == "1":
        dic["fipnum"].append(numa)
    else:
        dic["fipnum"].append(numb)


def positions(dic):
    """
    Function to locate sand and well positions

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["sensorijk"] = [[] for _ in range(len(dic["sensors"]))]
    for names in ["fluxnum", "fipnum", "porv"]:
        dic[f"{names}"] = []
    if dic["grid"] == "corner-point":
        corner_point_handling_fluidflower(dic)
    else:
        structured_handling_fluidflower(dic)
    if "cellmaps" in dic:
        get_cellmaps(dic)
    else:
        os.system(f"cp {dic['path']}/geology/cellmap.npy {dic['deck']}/")


def get_cellmaps(dic):
    """
    Write the mapping between simulation and reporting grid

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    cellmaps = []
    print("\nMapping simulation to reporting grid, please wait.")
    with alive_bar(len(dic["refxgrid"])) as bar_animation:
        for xcen, zcen in zip(dic["refxgrid"], dic["refzgrid"]):
            bar_animation()
            cellmaps.append(
                np.argmin(
                    np.abs(dic["simxcent"] - xcen) + np.abs(dic["simzcent"] - zcen)
                )
            )
    np.save(f"{dic['deck']}/cellmap", cellmaps)


def sensors(dic):
    """
    Find the i,j,k sensor indices

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    for j, _ in enumerate(dic["sensors"]):
        for sensor_coord, axis in zip(dic["sensors"][j], ["xmx", "ymy", "zmz"]):
            if axis == "zmz":
                dic["sensorijk"][j].append(
                    pd.Series(
                        abs(dic["dims"][2] - sensor_coord - dic[f"{axis}_center"])
                    ).argmin()
                )
            else:
                dic["sensorijk"][j].append(
                    pd.Series(abs(sensor_coord - dic[f"{axis}_center"])).argmin()
                )


def wells(dic):
    """
    Function to find the wells/sources index

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["wellijk"] = [[] for _ in range(len(dic["sources"]))]
    for j, _ in enumerate(dic["sources"]):
        for well_coord, axis in zip(dic["sources"][j], ["xmx", "ymy", "zmz"]):
            dic["wellijk"][j].append(
                pd.Series(abs(well_coord - dic[f"{axis}_center"])).argmin() + 1
            )


def getpolygons(dic):
    """
    Function to create the polygons from the benchmark geo file

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    dic["points"] = []
    lines = []
    curves = []
    dic["polygons"] = []
    dic["facies"] = []
    facie = 0
    h_ref = 1.5 / 1490
    l_ref = 2.8 / 2594
    dic["ztopbot"] = dic["dims"][2] - 0.644
    dic["zmidbot"] = dic["dims"][2] - 0.265
    with open(
        f"{dic['path']}/geology/points.geo",
        "r",
        encoding="utf8",
    ) as file:
        for row in csv.reader(file, delimiter=" "):
            if row[0][:5] == "Point":
                dic["points"].append(
                    [
                        l_ref * float(row[2][1:-1]),
                        dic["dims"][2] - h_ref * float(row[3][:-1]),
                    ]
                )
    with open(
        f"{dic['path']}/geology/lines.geo",
        "r",
        encoding="utf8",
    ) as file:
        for row in csv.reader(file, delimiter=" "):
            if row[0][:4] == "Line":
                lines.append([int(row[2][1:-1]), int(row[3][:-2])])
    with open(
        f"{dic['path']}/geology/polygons.geo",
        "r",
        encoding="utf8",
    ) as file:
        for row in csv.reader(file, delimiter=" "):
            if row[0] == "Curve":
                dic["facies"].append(facie)
                tmp = []
                tmp.append(int(row[3][1:-1]))
                for col in row[4:-1]:
                    tmp.append(int(col[:-1]))
                tmp.append(int(row[-1][:-2]))
                curves.append(tmp)
            if len(row) > 1:
                if row[1] in ["Sand", "Water"]:
                    facie += 1
    for curve in curves:
        tmp = []
        tmp.append(
            [
                dic["points"][lines[curve[0] - 1][0] - 1][0],
                dic["points"][lines[curve[0] - 1][0] - 1][1],
            ]
        )
        tmp.append(
            [
                dic["points"][lines[curve[0] - 1][1] - 1][0],
                dic["points"][lines[curve[0] - 1][1] - 1][1],
            ]
        )
        for line in curve[1:]:
            if line < 0:
                tmp.append(
                    [
                        dic["points"][lines[abs(line) - 1][0] - 1][0],
                        dic["points"][lines[abs(line) - 1][0] - 1][1],
                    ]
                )
            else:
                tmp.append(
                    [
                        dic["points"][lines[line - 1][1] - 1][0],
                        dic["points"][lines[line - 1][1] - 1][1],
                    ]
                )
        tmp.append(tmp[0])
        dic["polygons"].append(Polygon(tmp))


def get_lines(dic):
    """
    Read the points in the z-surface lines

     Args:
        dic (dict): Global dictionary

     Returns:
        horizonts (list): List with the coordinates of the horizonts

    """
    horizonts = []
    with open(
        f"{dic['path']}/geology/horizonts.geo",
        "r",
        encoding="utf8",
    ) as file:
        for row in csv.reader(file, delimiter=" "):
            if row[0][:4] == "Line":
                if not horizonts[-1]:
                    horizonts[-1].append(
                        [
                            dic["points"][int(row[2][1:-1]) - 1][0],
                            dic["points"][int(row[2][1:-1]) - 1][1],
                        ]
                    )
                horizonts[-1].append(
                    [
                        dic["points"][int(row[3][:-2]) - 1][0],
                        dic["points"][int(row[3][:-2]) - 1][1],
                    ]
                )
            if len(row) > 1:
                if row[1] == "Horizont":
                    horizonts.append([])
    return horizonts[::-1]


def corner(dic):
    """
    Create a FludFlower corner-point grid

    Args:
        dic (dict): Global dictionary

    Returns:
        dic (dict): Modified global dictionary

    """
    # Read the geometries
    horizonts = get_lines(dic)
    xcoord, zcoord = [], []
    dic["xmx"] = [0.0]
    for i, n_x in enumerate(dic["x"]):
        for j in range(n_x):
            dic["xmx"].append((i + (j + 1.0) / n_x) * dic["dims"][0] / len(dic["x"]))
    dic["ymy"] = [0.0]
    for i, n_y in enumerate(dic["y"]):
        for j in range(n_y):
            dic["ymy"].append((i + (j + 1.0) / n_y) * dic["dims"][1] / len(dic["y"]))
    dic["noCells"][1] = len(dic["ymy"]) - 1
    for xcor in dic["xmx"]:
        for _, lcor in enumerate(horizonts):
            xcoord.append(xcor)
            idx = pd.Series([abs(ii[0] - xcor) for ii in lcor]).argmin()
            if lcor[idx][0] < xcor:
                zcoord.append(
                    lcor[idx][1]
                    + (
                        (lcor[idx + 1][1] - lcor[idx][1])
                        / (lcor[idx + 1][0] - lcor[idx][0])
                    )
                    * (xcor - lcor[idx][0])
                )
            else:
                zcoord.append(
                    lcor[idx - 1][1]
                    + (
                        (lcor[idx][1] - lcor[idx - 1][1])
                        / (lcor[idx][0] - lcor[idx - 1][0])
                    )
                    * (xcor - lcor[idx - 1][0])
                )
    res = list(filter(lambda i: i == zcoord[-1], zcoord))[0]
    n_z = zcoord.index(res)
    res = list(filter(lambda i: i > 0, xcoord))[0]
    n_x = round(len(xcoord) / xcoord.index(res)) - 1
    dic["noCells"][0], dic["noCells"][2] = n_x, n_z
    # Refine the grid
    xcoord, zcoord, dic["noCells"][0], dic["noCells"][2] = refinement_z(
        xcoord, zcoord, dic["noCells"][0], dic["noCells"][2], dic["z"]
    )
    dic["xmx"] = np.array(dic["xmx"])
    dic["ymy_center"] = 0.5 * (np.array(dic["ymy"])[1:] + np.array(dic["ymy"])[:-1])
    dic["d_y"] = np.array(dic["ymy"])[1:] - np.array(dic["ymy"])[:-1]
    dic["d_x"] = np.array(dic["xmx"])[1:] - np.array(dic["xmx"])[:-1]
    dic["no_cells"] = dic["noCells"][0] * dic["noCells"][2]
    create_corner_point_grid(dic, xcoord, zcoord)
    dic["xyz"] = []
    dic["d_z"] = []
    for k in range(dic["noCells"][2]):
        for i in range(dic["noCells"][0]):
            n = (i * (dic["noCells"][2] + 1)) + k
            m = ((i + 1) * (dic["noCells"][2] + 1)) + k
            poly = Polygon(
                [
                    [xcoord[n], zcoord[n]],
                    [xcoord[m], zcoord[m]],
                    [xcoord[m + 1], zcoord[m + 1]],
                    [xcoord[n + 1], zcoord[n + 1]],
                    [xcoord[n], zcoord[n]],
                ]
            )
            pxz = poly.centroid.wkt
            pxz = list(float(j) for j in pxz[7:-1].split(" "))
            dic["xyz"].append([pxz[0], 0, pxz[1]])
            dic["d_z"].append(poly.area / (xcoord[m] - xcoord[n]))


def refinement_z(xci, zci, ncx, ncz, znr):
    """
    Refinement of the grid in the z-dir

    Args:
        xci (list): Floats with the x-coordinates of the cell corners\n
        zci (list): Floats with the z-coordinates of the cell corners\n
        ncx (int): Number of cells in the x-dir\n
        ncz (int): Number of cells in the z-dir\n
        znr (list): Integers with the number of z-refinements per cell

    Returns:
        xcr (list): Floats with the new x-coordinates of the cell corners\n
        zcr (list): Floats with the new z-coordinates of the cell corners\n
        ncx (int): New number of cells in the x-dir\n
        ncz (int): New number of cells in the z-dir

    """
    xcr, zcr = [], []
    for j in range(ncx + 1):
        zcr.append(zci[j * (ncz + 1)])
        xcr.append(xci[j * (ncz + 1)])
        for i in range(ncz):
            for k in range(znr[i]):
                alp = np.arange(1.0 / znr[i], 1.0 + 1.0 / znr[i], 1.0 / znr[i]).tolist()
                zcr.append(
                    zci[j * (ncz + 1) + i]
                    + (zci[j * (ncz + 1) + i + 1] - zci[j * (ncz + 1) + i]) * alp[k]
                )
                xcr.append(
                    xci[j * (ncz + 1) + i]
                    + (xci[j * (ncz + 1) + i + 1] - xci[j * (ncz + 1) + i]) * alp[k]
                )
    res = list(filter(lambda i: i > 0, xcr))[0]
    ncx = round(len(xcr) / xcr.index(res)) - 1
    res = list(filter(lambda i: i == zcr[-1], zcr))[0]
    ncz = zcr.index(res)
    return xcr, zcr, ncx, ncz
