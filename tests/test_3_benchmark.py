# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the single functionality and plotting for the benchmark"""

import os
import pathlib
import subprocess

testpth: pathlib.Path = pathlib.Path(__file__).parent
mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]


def test_benchmark():
    """See examples/single.toml"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    os.chdir(f"{testpth}/output")
    confi = f"{mainpth}/examples/single.toml"
    subprocess.run(
        ["pofff", "-i", confi, "-o", "benchmark", "-t", "24,48,72", "-e", "C1"],
        check=True,
    )
    assert os.path.exists(
        f"{testpth}/output/benchmark/compare_all_time_series.png"
    ), "Issue with the test_3_benchmark.py"
    assert os.path.exists(
        f"{testpth}/output/benchmark/compare_all_sparse.png"
    ), "Issue with the test_3_benchmark.py"
