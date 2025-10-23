# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0801

"""Test the configuration files"""

import os
import pathlib
from pofff.core.pofff import main

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_main():
    """See examples/input.toml"""
    confi = f"{mainpth}/examples/input.toml"
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
        os.system(f"mkdir {testpth}/output/main")
        os.system(f"cp {confi} {testpth}/output/main/input.toml")
    elif not os.path.exists(f"{testpth}/output/main"):
        os.system(f"mkdir {testpth}/output/main")
        os.system(f"cp {confi} {testpth}/output/main/input.toml")
    elif not os.path.isfile(f"{testpth}/output/main/input.toml"):
        os.system(f"cp {confi} {testpth}/output/main/input.toml")
    os.chdir(f"{testpth}/output/main")
    main()
    assert os.path.exists(
        f"{testpth}/output/main/output/sim_metrics_0.txt"
    ), "Issue with the test_0_main.py"
    assert os.path.exists(
        f"{testpth}/output/main/output/map_0.25h.png"
    ), "Issue with the test_0_main.py"
    assert os.path.exists(
        f"{testpth}/output/main/output/time_series.csv"
    ), "Issue with the test_0_main.py"
