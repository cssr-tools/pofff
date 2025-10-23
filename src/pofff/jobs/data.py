#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0302, R0912, R0914, R0801, R0915, E1102, C0325

"""
Script to write the benchmark data
"""

import argparse
import os
import sys
from io import StringIO
from scipy.interpolate import interp1d
import numpy as np
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import ERst as OpmRestart
from opm.io.ecl import ESmry as OpmSummary

GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108
SECONDS_IN_YEAR = 31536000
KMOL_TO_KG = 1e3 * 0.044


def main():
    """Postprocessing to generate the benchmark data"""
    parser = argparse.ArgumentParser(description="Main script to process the data")
    parser.add_argument(
        "-r",
        "--resolution",
        default="280,1,120",
        help="Number of x, y, and z elements to write the data ('10,1,5' by default).",
    )
    parser.add_argument(
        "-t",
        "--time",
        default="24,48,72,96,120",
        help="If one number, time step for the spatial maps in [h] ('24' by default); "
        "otherwise, times separated by commas.",
    )
    parser.add_argument(
        "-m",
        "--maps",
        default="/Users/dmar/Github/pofff/src/pofff/geology/cellmap.npy",
        help="Path to the cell maps",
    )
    if os.path.exists("NOMONOTONIC"):
        sys.exit()
    cmdargs = vars(parser.parse_known_args()[0])
    dig = {"where": "./"}
    dig["flowf"] = "."
    dig["maps"] = cmdargs["maps"]
    dig["nxyz"] = np.genfromtxt(
        StringIO(cmdargs["resolution"]), delimiter=",", dtype=int
    )
    for file in os.listdir(dig["flowf"]):
        if os.path.splitext(file)[1] == ".UNRST":
            dig["sim"] = os.path.abspath(dig["flowf"] + f"/{os.path.splitext(file)[0]}")
            break
    dig["dense_t"] = (
        np.genfromtxt(StringIO(cmdargs["time"]), delimiter=",", dtype=float) * 3600
    )
    dig["sparse_t"] = 1.0 * 600
    dig["dims"] = [2.8, 1.0, 1.2]
    dig["nocellsr"] = dig["nxyz"][0] * dig["nxyz"][2]
    dig["noxzr"] = dig["nxyz"][0] * dig["nxyz"][2]
    dig["time_initial"], dig["times"] = 0, []
    read_opm(dig)
    sparse_data(dig)
    if isinstance(dig["dense_t"], float):
        dig["dense_t"] = [
            i * dig["dense_t"]
            for i in range(1, int(np.floor((dig["times"][-1]) / dig["dense_t"])) + 1)
        ]
    dense_data(dig)


def sparse_data(dig):
    """
    Generate the sparse data within the benchmark format

    Args:
        dig (dict): Global dictionary

    Returns:
        None

    """
    dil = {
        "times_data": np.linspace(
            0, dig["times"][-1], round(dig["times"][-1] / dig["sparse_t"]) + 1
        )
    }
    dil["fipnum"] = list(dig["init"]["FIPNUM"])
    for name in ["dx", "dy", "dz"]:
        dil[f"{name}"] = np.array(dig["init"][name.upper()])
    dil["names"] = [
        "pop1",
        "pop2",
        "moba",
        "imma",
        "dissa",
        "seala",
        "mobb",
        "immb",
        "dissb",
        "sealb",
        "sealt",
    ]
    for ent in dil["names"]:
        dil[ent] = 0.0
    dil["m_c"] = []
    dil["fip_diss_a"] = [2, 4, 5, 8]
    dil["fip_seal_a"] = [5, 8]
    dil["fip_diss_b"] = [3, 6]
    dil["fip_seal_b"] = [6]
    create_from_summary(dig, dil)
    compute_m_c(dig, dil)
    write_sparse_data(dig, dil)


def create_from_summary(dig, dil):
    """
    Use the summary arrays for the sparse data interpolation

    Args:
        dig (dict): Global dictionary\n
        dil (dict): Local dictionary

    Returns:
        dil (dict): Modified local dictionary

    """
    ind, names, i_jk = 0, [], []
    for key in dig["smspec"].keys():
        if key[0 : len("BWPR")] == "BWPR" and "," in key[len("BWPR") + 1 :]:
            names.append(key)
            i_jk.append(
                np.genfromtxt(
                    StringIO(key[len("BWPR") + 1 :]), delimiter=",", dtype=int
                )[0]
            )
            ind += 1
            if ind == 2:
                break
    sort = sorted(range(len(i_jk)), key=i_jk.__getitem__)
    pop1 = dig["unrst"]["PRESSURE", 0][dil["fipnum"].index(8)]
    pop2 = dig["unrst"]["PRESSURE", 0][dil["fipnum"].index(9)]
    if dig["unrst"].count("PCGW", 0):
        pop1 -= dig["unrst"]["PCGW", 0][dil["fipnum"].index(8)]
        pop2 -= dig["unrst"]["PCGW", 0][dil["fipnum"].index(9)]
    dil["pop1"] = [pop1 * 1.0e5] + list(dig["smspec"][names[sort[0]]] * 1.0e5)  # Pa
    dil["pop2"] = [pop2 * 1.0e5] + list(dig["smspec"][names[sort[1]]] * 1.0e5)  # Pa
    for i in dil["fip_diss_a"]:
        dil["moba"] += dig["smspec"][f"RGKDM:{i}"] * KMOL_TO_KG
        dil["imma"] += dig["smspec"][f"RGKDI:{i}"] * KMOL_TO_KG
        dil["dissa"] += dig["smspec"][f"RWCD:{i}"] * KMOL_TO_KG
    for i in dil["fip_seal_a"]:
        dil["seala"] += (
            dig["smspec"][f"RWCD:{i}"]
            + dig["smspec"][f"RGKDM:{i}"]
            + dig["smspec"][f"RGKDI:{i}"]
        ) * KMOL_TO_KG
    for i in dil["fip_diss_b"]:
        dil["mobb"] += dig["smspec"][f"RGKDM:{i}"] * KMOL_TO_KG
        dil["immb"] += dig["smspec"][f"RGKDI:{i}"] * KMOL_TO_KG
        dil["dissb"] += dig["smspec"][f"RWCD:{i}"] * KMOL_TO_KG
    for i in dil["fip_seal_b"]:
        dil["sealb"] += (
            dig["smspec"][f"RWCD:{i}"]
            + dig["smspec"][f"RGKDM:{i}"]
            + dig["smspec"][f"RGKDI:{i}"]
        ) * KMOL_TO_KG
    dil["sealt"] = dil["seala"] + dil["sealb"]
    for name in ["RWCD", "RGKDM", "RGKDI"]:
        dil["sealt"] += (
            dig["smspec"][f"{name}:7"] + dig["smspec"][f"{name}:9"]
        ) * KMOL_TO_KG


def compute_m_c(dig, dil):
    """
    Normalized total variation of the concentration field within Box C

    Args:
        dig (dict): Global dictionary\n
        dil (dict): Local dictionary

    Returns:
        dil (dict): Modified local dictionary

    """
    dil["boxc"] = np.array([fip in (4, 12, 17, 18) for fip in dil["fipnum"]])
    dil["boxc_x"] = np.roll(dil["boxc"], 1)
    dil["boxc_y"] = np.roll(dil["boxc"], -dig["gxyz"][0])
    dil["boxc_z"] = np.roll(dil["boxc"], -dig["gxyz"][0] * dig["gxyz"][1])
    for t_n in range(1, dig["norst"]):
        rss = np.array(dig["unrst"]["RSW", t_n])
        dil["xcw"] = np.divide(rss, rss + WAT_DEN_REF / GAS_DEN_REF)
        rssat = np.array(dig["unrst"]["RSWSAT", t_n])
        x_l_co2_max = np.divide(rssat, rssat + WAT_DEN_REF / GAS_DEN_REF)
        dil["xcw"] = np.divide(dil["xcw"], x_l_co2_max)
        dil["m_c"].append(
            np.sum(
                np.abs(
                    (dil["xcw"][dil["boxc_x"]] - dil["xcw"][dil["boxc"]])
                    * dil["dz"][dil["boxc"]]
                )
                + np.abs(
                    (dil["xcw"][dil["boxc_z"]] - dil["xcw"][dil["boxc"]])
                    * dil["dx"][dil["boxc"]]
                )
            )
        )


def write_sparse_data(dig, dil):
    """
    Write the sparse data

    Args:
        dig (dict): Global dictionary\n
        dil (dict): Local dictionary

    Returns:
        None

    """
    for name in dil["names"] + ["m_c"]:
        if name == "m_c":
            interp = interp1d(
                dig["times"],
                [0.0] + dil[f"{name}"],
                fill_value="extrapolate",
            )
        elif "pop" in name:
            interp = interp1d(
                dig["times_summary"],
                dil[f"{name}"],
                fill_value="extrapolate",
            )
        else:
            interp = interp1d(
                dig["times_summary"],
                [0.0] + list(dil[f"{name}"]),
                fill_value="extrapolate",
            )
        dil[f"{name}"] = interp(dil["times_data"])
    text = [
        "# t [s], p1 [Pa], p2 [Pa], mobA [kg], immA [kg], dissA [kg], sealA [kg], "
        + "<same for B>, MC [m^2], sealTot [kg]"
    ]
    for j, time in enumerate(dil["times_data"][1:]):
        text.append(
            f"{time:.3e},{dil['pop1'][j]:.5e},{dil['pop2'][j]:.5e},"
            f"{dil['moba'][j]:.3e},{dil['imma'][j]:.3e},{dil['dissa'][j]:.3e},"
            f"{dil['seala'][j]:.3e},{dil['mobb'][j]:.3e},{dil['immb'][j]:.3e},"
            f"{dil['dissb'][j]:.3e},{dil['sealb'][j]:.3e},{dil['m_c'][j]:.3e},"
            f"{dil['sealt'][j]:.3e}"
        )
    with open("time_series.csv", "w", encoding="utf8") as file:
        file.write("\n".join(text))


def read_opm(dig):
    """
    Read the simulation files using OPM

    Args:
        dig (dict): Global dictionary

    Returns:
        dig (dict): Modified global dictionary

    """
    dig["unrst"] = OpmRestart(f"{dig['sim']}.UNRST")
    time = []
    for i in range(len(dig["unrst"].report_steps)):
        time.append(float(f"{86400 * dig['unrst']['DOUBHEAD', i][0]:.0f}"))
        if len(dig["times"]) == 0:
            if max(dig["unrst"]["RSW", i]) > 0:
                dig["time_initial"] = 86400 * dig["unrst"]["DOUBHEAD", i - 1][0]
                dig["times"].append(0)
                dig["times"].append(time[-1] - dig["time_initial"])
        else:
            dig["times"].append(time[-1] - dig["time_initial"])
    dig["init"] = OpmFile(f"{dig['sim']}.INIT")
    dig["egrid"] = OpmGrid(f"{dig['sim']}.EGRID")
    dig["smspec"] = OpmSummary(f"{dig['sim']}.SMSPEC")
    dig["norst"] = len(dig["unrst"].report_steps)
    dig["porv"] = np.array(dig["init"]["PORV"])
    dig["actind"] = list(i for i, porv in enumerate(dig["porv"]) if porv > 0)
    dig["porva"] = np.array([porv for porv in dig["porv"] if porv > 0])
    dig["nocellst"], dig["nocellsa"] = (
        len(dig["porv"]),
        dig["egrid"].active_cells,
    )
    dig["times_summary"] = [0.0]
    dig["times_summary"] += list(86400.0 * dig["smspec"]["TIME"])
    dig["gxyz"] = [
        dig["egrid"].dimension[0],
        dig["egrid"].dimension[1],
        dig["egrid"].dimension[2],
    ]
    dig["noxz"] = dig["egrid"].dimension[0] * dig["egrid"].dimension[2]


def dense_data(dig):
    """
    Generate the dense data within the benchmark format

    Args:
        dig (dict): Global dictionary

    Returns:
        None

    """
    dil = {"rstno": []}
    for time in dig["dense_t"]:
        dil["rstno"].append(dig["times"].index(time))
    dil["nrstno"] = len(dil["rstno"])
    for i, j, k in zip(["x", "y", "z"], dig["dims"], dig["nxyz"]):
        dil[f"ref{i}vert"] = np.linspace(0, j, k + 1)
        dil[f"ref{i}cent"] = 0.5 * (dil[f"ref{i}vert"][1:] + dil[f"ref{i}vert"][:-1])
    dil["refxgrid"] = np.zeros(dig["nxyz"][0] * dig["nxyz"][2])
    dil["refzgrid"] = np.zeros(dig["nxyz"][0] * dig["nxyz"][2])
    dil["refpoly"] = []
    dil["cell_cent"] = np.load(dig["maps"])
    dig["actindr"] = []
    names = ["sgas", "cco2"]
    for i, t_n in enumerate(dil["rstno"]):
        generate_arrays(dig, dil, names, t_n)
        map_to_report_grid(dil, names)
        if dig["dense_t"][i] % 3600 == 0:
            write_dense_data(dig, dil, int(dig["dense_t"][i] / 3600))
        else:
            write_dense_data(dig, dil, int(dig["dense_t"][i]) / 3600)


def generate_arrays(dig, dil, names, t_n):
    """
    Arrays for the dense data

    Args:
        dig (dict): Global dictionary\n
        dil (dict): Local dictionary\n
        names (list): Strings with the quantities for the spatial maps\n
        t_n (int): Index for the number of restart file

    Returns:
        dil (dict): Modified local dictionary

    """
    for name in names:
        dil[f"{name}_array"] = np.zeros(dig["nocellst"], dtype=float)
        dil[f"{name}_refg"] = np.zeros(dig["nocellsr"], dtype=float)
    sgas = abs(np.array(dig["unrst"]["SGAS", t_n]))
    rhow = np.array(dig["unrst"]["WAT_DEN", t_n])
    rsw = np.array(dig["unrst"]["RSW", t_n])
    xlco2 = np.divide(rsw, rsw + WAT_DEN_REF / GAS_DEN_REF)
    dil["sgas_array"][dig["actind"]] = sgas
    dil["cco2_array"][dig["actind"]] = xlco2 * rhow


def map_to_report_grid(dil, names):
    """
    Map the simulation grid to the reporting grid

    Args:
        dil (dict): Local dictionary\n
        names (list): Strings with the quantities for the spatial maps

    Returns:
        dil (dict): Modified local dictionary

    """
    for i, ind in enumerate(dil["cell_cent"]):
        for name in names:
            dil[f"{name}_refg"][i] = dil[f"{name}_array"][int(ind)]


def write_dense_data(dig, dil, n):
    """
    Map the quantities to the cells

    Args:
        dig (dict): Global dictionary\n
        dil (dict): Local dictionary\n
        n (int): Number of csv file

    Returns:
        None

    """
    text = ["x,z,saturation,concentration"]
    for k, zcord in enumerate(dil["refzcent"]):
        for i, xcord in enumerate(dil["refxcent"]):
            idc = -dig["nxyz"][0] * (dig["nxyz"][2] - k) + i
            text.append(
                f"{xcord:.3f}, {zcord:.3f}, "
                + f"{dil['sgas_refg'][idc]:.3f}, "
                + f"{dil['cco2_refg'][idc]:.3f}"
            )
    with open(f"{dig['where']}/spatial_map_{n}h.csv", "w", encoding="utf8") as file:
        file.write("\n".join(text))


if __name__ == "__main__":
    main()
