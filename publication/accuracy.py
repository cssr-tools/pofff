# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Table C5 in the pofff paper"""

import os
from opm.io.ecl import ESmry as OpmSummary
from mako.template import Template

cnv_tolerances = ["1e-2", "1e-3"]
cnv_tolerances_relaxed = ["1", "1e-3"]
cases = ["relax", "tight"]
CO2 = 3e-7 * 8100 + 2 * 3e-7 * 10200  # mass injection rates times injection periods

os.system("mkdir accuracy")
text = "Case                         Accuracy (%)  Wall time (s)\n"
mytemplate = Template(filename="appendixc.mako")
for case, cnv, cnv_relaxed in zip(cases, cnv_tolerances, cnv_tolerances_relaxed):
    var = {"cores": 1, "random_seed": 7, "cnv": cnv, "cnv_relaxed": cnv_relaxed}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{case}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"pofff -i {case}.toml -o {case} -m single -t 24,48,72,96,120 -f none")
    tcpu = OpmSummary(f"{case}/{case.upper()}.SMSPEC")["TCPU"][-1]
    fgmip = OpmSummary(f"{case}/{case.upper()}.SMSPEC")["FGMIP"][-1]
    text += f"{case} CNV solver tolerance   "
    text += f"{100*(1.0-(abs(fgmip-CO2)/CO2)):.5f}"
    text += f"          {tcpu:.2f}\n"

with open(
    "accuracy/accuracy-time-trade-offs.txt",
    "w",
    encoding="utf8",
) as file:
    file.write(text)
