# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Table 8 in the pofff paper"""

import subprocess

from mako.template import Template

mytemplate = Template(filename="appendixc.mako")
for case, rng in zip(["base", "rng"], [7, 11]):
    # Modify the number of cores according to your resources
    var = {"cores": 64, "rng": rng, "cnv": 1e-2, "cnv_relaxed": 1}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{case}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
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
