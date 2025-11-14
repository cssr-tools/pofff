# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Table C4 in the pofff paper"""

import os
from mako.template import Template

mytemplate = Template(filename="appendixc.mako")
for case, random_seed in zip(["base", "random_seed"], [7, 11]):
    var = {"cores": 64, "random_seed": random_seed, "cnv": 1e-2, "cnv_relaxed": 1}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{case}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"pofff -i {case}.toml -o {case} -m everest -t 24,48,72,96,120 -f all")
