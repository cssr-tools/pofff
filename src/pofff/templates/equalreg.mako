#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

% if dic.get("monotonic"):
import sys
%   if dic.get("everert"):
import os
%   endif
% endif
% if dic.get("everert"):
import json
% else:
import os
% endif

def equalreg():
    """Evaluation of model parameters."""
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
    output_path = "EQUALREG.INC"
% else:
    output_path = os.path.join('${fol}', "EQUALREG.INC")
% endif
    with open(output_path, "w", encoding="utf8") as file:
        file.write("EQUALREG\n")
<%
    names = [
        ("poro", "poro"),
        ("permx", "permx"),
        ("permy", "permx"),
        ("permz", "permz"),
        ("disperc", "disperc"),
    ]
%>\
% for i in range(1, 8):
%   for name, key in names:
<%
val = None
hm_key = f"{name}{i}"
perm_key = f"perm{i}"

if everert:
    if hm_key in hm:
        if popsize:
            lo = hm[hm_key][1]
            hi = hm[hm_key][2]
            scale = hm[hm_key][3]
            val = f"{lo}+coef['{hm_key}']*({hi}-{lo})/(1.0*{scale})"
        else:
            val = f"coef['{hm_key}']"

    elif name in ("permx", "permy", "permz") and perm_key in hm:
        if popsize:
            lo = hm[perm_key][1]
            hi = hm[perm_key][2]
            scale = hm[perm_key][3]
            val = f"{lo}+coef['{perm_key}']*({hi}-{lo})/(1.0*{scale})"
        else:
            val = f"coef['{perm_key}']"

if val is None:
    val = para[f"{key}{i}"]
%>\
        file.write(f"${name.upper()} {${val}} ${i} F /\n")
%   endfor
% endfor
        file.write("/\n")


if __name__ == "__main__":
    equalreg()