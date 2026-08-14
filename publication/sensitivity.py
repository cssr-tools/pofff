# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Table 8 in the pofff paper"""

import csv
import subprocess
from pathlib import Path

from mako.template import Template

OUTPUT_DIR = Path("sensitivity")


def get_value(file, row_num=15, col_num=10):
    """Read the WD from error_table_satmin-0.01_conmin-0.1.csv"""
    with open(file, "r", newline="", encoding="utf-8") as ff:
        reader = list(csv.reader(ff))
        return reader[row_num - 1][col_num - 1]


OUTPUT_DIR.mkdir(exist_ok=True)
mytemplate = Template(filename="appendixc.mako")
cases = ["base", "rng"]
values = []
for case, rng in zip(cases, [7, 11]):
    # Modify the number of cores according to your resources
    var = {"cores": 64, "rng": rng, "cnv": 1e-2, "cnv_relaxed": 1}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{case}.toml",
        "w",
        encoding="utf8",
    ) as f:
        f.write(filledtemplate)
    subprocess.run(
        [
            "pofff",
            "-i",
            f"{case}.toml",
            "-o",
            case,
            "-m",
            "everest",
            "-t",
            "24,48,72,96,120",
            "-f",
            "all",
        ],
        check=True,
    )
    csv_file = f"{case}/figures/best_simulation/error_table_satmin-0.01_conmin-0.1.csv"

    values.append(get_value(csv_file))

with open(f"{OUTPUT_DIR!s}/table8.txt", "w", encoding="utf-8") as f:
    f.write("                              Base case     Random seed\n")
    f.write(f"Wasserstein distance [g⋅cm]   {values[0]}   {values[1]}\n")
