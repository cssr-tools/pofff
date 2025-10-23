# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions for the simulations, data processing, and plotting.
"""
import os
import subprocess


def flow(dic):
    """
    Run OPM Flow

    Args:
        dic (dict): Global dictionary

    Returns:
        None

    """
    os.system(
        f"{dic['flow']} --output-dir={dic['fol']} "
        f"{dic['fol']}/{dic['data']}.DATA & wait\n"
    )


def data(dic):
    """
    Generate the benchmark data

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        None

    """
    prosc = subprocess.run(
        [
            "python",
            f"{dic['path']}/jobs/data.py",
            "-m",
            f"{dic['deck']}/cellmap.npy",
            "-t",
            dic["times"],
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
    prosc = subprocess.run(
        [
            "python",
            f"{dic['path']}/jobs/metric.py",
            "-e",
            dic["experiment"],
            "-p",
            dic["path"],
            "-t",
            dic["times"],
            "-s",
            dic["msat"],
            "-c",
            dic["mcon"],
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")


def benchmark(dic):
    """
    Generate the benchmark figures

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        None

    """
    prosc = subprocess.run(
        [
            "python",
            f"{dic['path']}/visualization/maps.py",
            "-e",
            dic["experiment"],
            "-t",
            dic["times"],
            "-p",
            dic["path"],
            "-s",
            dic["msat"],
            "-c",
            dic["mcon"],
            "-l",
            "." if dic["add"] == "1" else dic["location"],
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
    if dic["add"] == "1":
        prosc = subprocess.run(
            [
                "python",
                f"{dic['path']}/visualization/sparse_values.py",
            ],
            check=True,
        )
        if prosc.returncode != 0:
            raise ValueError(f"Invalid result: { prosc.returncode }")
    prosc = subprocess.run(
        [
            "python",
            f"{dic['path']}/visualization/benchmark.py",
            "-f",
            f"{dic['figures']}",
            "-p",
            dic["path"],
            "-s",
            dic["msat"],
            "-c",
            dic["mcon"],
            "-l",
            dic["location"],
            "-a",
            dic["add"],
            "-u",
            dic["use"],
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
    if dic["figures"] == "all":
        prosc = subprocess.run(
            [
                "python",
                f"{dic['path']}/visualization/error_table.py",
                "-p",
                dic["path"],
                "-s",
                dic["msat"],
                "-c",
                dic["mcon"],
                "-l",
                dic["location"],
                "-a",
                dic["add"],
            ],
            check=True,
        )
        if prosc.returncode != 0:
            raise ValueError(f"Invalid result: { prosc.returncode }")


def everest(dic):
    """
    Run everest and postprocess

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        None

    """
    for name in ["data", "delete", "metric"]:
        os.system(f"chmod u+x {dic['jobs']}/{name}.py")
    os.system("everest run everest.yml")
    postprocess(dic)


def ert(dic):
    """
    Run ert and postprocess

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        None

    """
    for name in ["data", "delete", "metric"]:
        os.system(f"chmod u+x {dic['jobs']}/{name}.py")
    os.system(f"ert {dic['ertargs']} ert.txt")
    postprocess(dic)


def postprocess(dic):
    """
    Postprocess ert and everest

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        None

    """
    prosc = subprocess.run(
        [
            "python",
            f"{dic['path']}/visualization/everert.py",
            "-e",
            f"{dic['path']}/fluidflower",
            "-t",
            dic["times"],
            "-m",
            f"{dic['deck']}/cellmap.npy",
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
