#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

import os
import json
import sys

def bcprop():
    """
    Evaluation of the boundary condition
    """
% if dic['monotonic']:
    if os.path.exists("NOMONOTONIC"):
        sys.exit()
% endif
% if dic["mode"] in ["ert", "everest"]:
    with open("para.json", "r", encoding="utf8") as file:
        coef = json.load(file)
    with open("BCPROP.INC", "w", encoding="utf8") as file:
% else:
    with open("${dic['fol']}/BCPROP.INC", "w", encoding="utf8") as file:
% endif
        file.write("BCPROP\n")
% if "PEN1" in dic.keys():
% if dic["mode"] == "everest":
        file.write(f"1 DIRICHLET WATER 1* {(${dic['pressure']}+${dic["PEN1"][1]}+coef['PEN1']*(${dic["PEN1"][2]}-${dic["PEN1"][1]})/(1.0*${dic["PEN1"][3]}))/1.E5} /\n")
% else:
        file.write(f"1 DIRICHLET WATER 1* {(${dic['pressure']}+coef['PEN1'])/1.E5} /\n")
% endif
% else:
        file.write(f"1 DIRICHLET WATER 1* ${(dic['pressure']+dic["PARA"]["PEN1"])/1.E5} /\n")
% endif
        file.write("/\n")
% if "THICKNESSMULT" in dic.keys() and dic["mode"] in ["ert", "everest"]:
    with open("THICKNESSMULT.INC", "w", encoding="utf8") as file:
% for name in ["PV", "X", "X-", "Z", "Z-"]:
        file.write("MULT${name}\n")
% if dic["mode"] == "everest":
        file.write(f"${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*{${dic["THICKNESSMULT"][1]}+coef['THICKNESSMULT']*(${dic["THICKNESSMULT"][2]}-${dic["THICKNESSMULT"][1]})/(1.0*${dic["THICKNESSMULT"][3]})} /\n")
% else:
        file.write(f"${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*{coef['THICKNESSMULT']} /\n")
% endif
% endfor
% endif

if __name__ == "__main__":
    bcprop()