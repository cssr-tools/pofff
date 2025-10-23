#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

import os
import json
import sys
import numpy as np

def krwe(sw, swi, nkrw):
    # Wetting relative permeability
    return ${dic['krw'].strip()}

def krne(sw, sni, nkrn):
    # CO2 relative permeability
    return ${dic['krn'].strip()}

def pcwce(sw, swi, pen, npen):
    # Capillary pressure
    return 0 if pen==0 else ${dic['cap'].strip()} / 1E5

def satufunc():
% if dic['monotonic']:
    if os.path.exists("NOMONOTONIC"):
        sys.exit()
% endif
% if dic["mode"] in ["ert", "everest"]:
    with open("para.json", "r", encoding="utf8") as file:
       coef = json.load(file)
% endif
    # Properties: swi, sni, pen, nkrw, nkrn, npen, thr, npoints
    safu = [[0.0] * 8 for _ in range(7)]
% for i in range(1,8):
% for j,name in enumerate(["SWI","SNI","PEN","NKRW","NKRN","NPE","THRE","NPNT"]):
% if f"{name}{i}" in dic.keys():
% if dic["mode"] == "everest":
    safu[${i-1}][${j}] = ${dic[f"{name}{i}"][1]}+coef['${name}${i}']*(${dic[f"{name}{i}"][2]}-${dic[f"{name}{i}"][1]})/(1.0*${dic[f"{name}{i}"][3]})
% else:
    safu[${i-1}][${j}] = coef['${name}${i}']
% endif
% else:
    safu[${i-1}][${j}] = ${dic["PARA"][f"{name}{i}"]}
% endif
% endfor
% endfor
    with open(
% if dic["mode"] in ["ert", "everest"]:
        "TABLES.INC",
% else:
        "${dic['fol']}/TABLES.INC",
% endif
        "w",
        encoding="utf8",
    ) as file:
        file.write("SGFN\n")
        for j, para in enumerate(safu):
            if j > 0:
                if safu[j-1] == para:
                    file.write("/\n")
                    continue
            sco2 = np.linspace(para[1], 1, para[7])
            if sco2[0] > 0:
                file.write(f"{0}".rjust(12)
                    + f"{0}".rjust(13)
                    + f" {0}\n")
            for i, value in enumerate(sco2):
                file.write(
                    (f"{value:E}" if value not in [0,1] else f"{int(value)}".rjust(12))
                    + (f" {max(0,krne(1-sco2[i], para[1], para[4])):E}" if max(0,krne(1-sco2[i], para[1], para[4])) not in [0,1] else f"{int(max(0,krne(1-sco2[i], para[1], para[4])))}".rjust(13))
                    + f" {0}\n"
                )
            file.write("/\n")
        file.write("SWFN\n")
        for j, para in enumerate(safu):
            if j > 0:
                if safu[j-1] == para:
                    file.write("/\n")
                    continue
            swatc = np.linspace(para[0], 1, para[7])
            for i, value in enumerate(swatc):
                if value <= para[0]:
                    file.write(
                        (f"{value:E}" if value not in [0,1] else f"{int(value)}".rjust(12))
                        + f"{0}".rjust(13)
                        + (f" {pcwce(value, para[0] - para[6], para[2], para[5]):E}\n" if pcwce(value, para[0] - para[6], para[2], para[5]) != 0 else f" 0\n")
                    )
                else:
                    file.write(
                        (f"{value:E}" if value not in [0,1] else f"{int(value)}".rjust(12))
                        + (f" {max(0,krwe(value, para[0], para[3])):E}" if max(0,krwe(value, para[0], para[3])) not in [0,1] else f"{int(max(0,krwe(value, para[0], para[3])))}".rjust(13))
                        + (f" {pcwce(value, para[0] - para[6], para[2], para[5]):E}\n" if pcwce(value, para[0] - para[6], para[2], para[5]) != 0 else f" 0\n")
                        )
            file.write("/\n")


if __name__ == "__main__":
    satufunc()