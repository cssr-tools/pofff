#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

import os
import json
import sys

def equalreg():
    """
    Evaluation of model parameters
    """
% if dic['monotonic']:
    if os.path.exists("NOMONOTONIC"):
        sys.exit()
% endif
% if dic["mode"] in ["ert", "everest"]:
    with open("para.json", "r", encoding="utf8") as file:
        coef = json.load(file)
    with open("EQUALREG.INC", "w", encoding="utf8") as file:
% else:
    with open("${dic['fol']}/EQUALREG.INC", "w", encoding="utf8") as file:
% endif
        file.write("EQUALREG\n")
% for i in range(1,8):
% for name,key in zip(["PORO", "PERMX", "PERMY", "PERMZ", "DISPERC"],["PORO", "PERMX", "PERMX", "PERMZ", "DISPERC"]):
% if f"{name}{i}" in dic.keys():
% if dic["mode"] == "everest":
        file.write(f"${name} {${dic[f"{name}{i}"][1]}+coef['${name}${i}']*(${dic[f"{name}{i}"][2]}-${dic[f"{name}{i}"][1]})/(1.0*${dic[f"{name}{i}"][3]})} ${i} F /\n")
% else:
        file.write(f"${name} {coef['${name}${i}']} ${i} F /\n")
% endif
% elif name in ["PERMX", "PERMY", "PERMZ"] and f"PERM{i}" in dic.keys():
% if dic["mode"] == "everest":
        file.write(f"${name} {${dic[f"PERM{i}"][1]}+coef['PERM${i}']*(${dic[f"PERM{i}"][2]}-${dic[f"PERM{i}"][1]})/(1.0*${dic[f"PERM{i}"][3]})} ${i} F /\n")
% else:
        file.write(f"${name} {coef['PERM${i}']} ${i} F /\n")
% endif
% else:
        file.write(f"${name} ${dic["PARA"][f"{key}{i}"]} ${i} F /\n")
% endif
% endfor
% endfor
        file.write("/\n")

if __name__ == "__main__":
    equalreg()