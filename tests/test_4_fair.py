# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Generate figures in the main paper in the Appendix"""

import os
import pathlib
import subprocess

mainpth: pathlib.Path = pathlib.Path(__file__).parents[1]
testpth: pathlib.Path = pathlib.Path(__file__).parent


def test_fair():
    """Towards FAIR data https://www.nature.com/articles/sdata201618"""
    if not os.path.exists(f"{testpth}/output"):
        os.system(f"mkdir {testpth}/output")
    os.chdir(f"{testpth}/output")
    subprocess.run(
        ["pofff", "-m", "fair", "-c", "5e-2", "-o", "appendix"],
        check=True,
    )
    where = f"{testpth}/output/appendix/"
    assert os.path.exists(
        f"{where}zoom_means_segmented_snapshots_satmin-0.01_conmin-0.05.png"
    ), "Issue with the test_4_fair.py"
    assert os.path.exists(
        f"{where}error_table_satmin-0.01_conmin-0.05.csv"
    ), "Issue with the test_4_fair.py"
