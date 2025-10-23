# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0801

"""Test the everest functionality via the configuration file"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_everest():
    """See examples/everest.toml"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    os.chdir(f"{testpth}/output")
    confi = f"{mainpth}/examples/everest.toml"
    subprocess.run(["pofff", "-i", confi, "-o", "everest", "-m", "everest"], check=True)
    assert os.path.exists(
        f"{testpth}/output/everest/figures/details.png"
    ), "Issue with the test_1_everest.py"
    assert os.path.exists(
        f"{testpth}/output/everest/figures/best_simulation/spatial_map_0.25h.csv"
    ), "Issue with the test_1_everest.py"
