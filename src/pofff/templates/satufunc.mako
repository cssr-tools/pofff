#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

% if dic.get("monotonic"):
import os
import sys
% endif
% if dic.get("everert"):
import json
% endif
import numpy as np

def krwe(sw, swi, nkrw):
    # Wetting relative permeability
    return ${dic['krw'].strip()}

def krne(sw, sni, nkrn):
    # CO2 relative permeability
    return ${dic['krn'].strip()}

def pcwce(sw, swi, pen, npen):
    # Capillary pressure
    return 0 if pen == 0 else ${dic['cap'].strip()} / 1e5


def satufunc():
% if dic.get("monotonic"):
    if os.path.exists("NOMONOTONIC"):
        sys.exit()
% endif
    <%
    everert = dic.get("everert", False)
    popsize = dic.get("popsize", False)
    hm = dic.get("hm", {})
    para = dic.get("para", {})
    fol = dic.get("fol", ".")
    %>
% if everert:
    with open("para.json", "r", encoding="utf8") as f:
        coef = json.load(f)
% endif
    # Properties: swi, sni, pen, nkrw, nkrn, npen, thr, npoints
    safu = [[0.0 for _ in range(8)] for _ in range(7)]
<%
names = ["swi", "sni", "pen", "nkrw", "nkrn", "npe", "thre", "npnt"]
%>\
% for i in range(1, 8):
<%
row = "["
for j, name in enumerate(names):
    val = None
    key = f"{name}{i}"

    if everert and key in hm:
        if popsize:
            lo = hm[key][1]
            hi = hm[key][2]
            scale = hm[key][3]
            val = f"{lo}+coef['{key}']*({hi}-{lo})/(1.0*{scale})"
        else:
            val = f"coef['{key}']"

    if val is None:
        val = para[key]
    row += f"{val}, "
%>\
    safu[${i-1}] = ${row[:-2]}${"]"}
% endfor
    with open(
% if everert:
        "TABLES.INC",
% else:
        "${fol}/TABLES.INC",
% endif
        "w",
        encoding="utf8",
    ) as file:
        file.write("SGFN\n")
        for j, para_row in enumerate(safu):
            if j > 0 and safu[j - 1] == para_row:
                file.write("/\n")
                continue
            sco2 = np.linspace(para_row[1], 1, int(para_row[7]))
            if sco2[0] > 0:
                file.write(
                    f"{0}".rjust(12)
                    + f"{0}".rjust(13)
                    + f" {0}\n"
                )
            for sc in sco2:
                krn_val = max(0, krne(1 - sc, para_row[1], para_row[4]))
                file.write(
                    (f"{sc:E}" if sc not in (0, 1) else f"{int(sc)}".rjust(12))
                    + (f" {krn_val:E}" if krn_val not in (0, 1) else f"{int(krn_val)}".rjust(13))
                    + f" {0}\n"
                )
            file.write("/\n")
        file.write("SWFN\n")

        for j, para_row in enumerate(safu):
            if j > 0 and safu[j - 1] == para_row:
                file.write("/\n")
                continue
            swatc = np.linspace(para_row[0], 1, int(para_row[7]))
            for sw in swatc:
                pc_val = pcwce(sw, para_row[0] - para_row[6], para_row[2], para_row[5])

                if sw <= para_row[0]:
                    krw_val = 0
                else:
                    krw_val = max(0, krwe(sw, para_row[0], para_row[3]))

                file.write(
                    (f"{sw:E}" if sw not in (0, 1) else f"{int(sw)}".rjust(12))
                    + (f" {krw_val:E}" if krw_val not in (0, 1) else f"{int(krw_val)}".rjust(13))
                    + (f" {pc_val:E}\n" if pc_val != 0 else f" 0\n")
                )
            file.write("/\n")


if __name__ == "__main__":
    satufunc()
