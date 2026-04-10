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

def bcprop():
    """Evaluation of the boundary condition."""
% if dic.get("monotonic"):
    if os.path.exists("NOMONOTONIC"):
        sys.exit()
% endif
    <%
    everert = dic.get("everert", False)
    popsize = dic.get("popsize", False)
    hm = dic.get("hm", {})
    para = dic.get("para", {})
    pressure = dic["pressure"]
    fol = dic.get("fol", ".")
    %>
% if everert:
    with open("para.json", "r", encoding="utf8") as f:
        coef = json.load(f)
    bcprop_path = "BCPROP.INC"
% else:
    bcprop_path = os.path.join('${fol}', "BCPROP.INC")
% endif
    with open(bcprop_path, "w", encoding="utf8") as file:
        file.write("BCPROP\n")
<%
val = None
if everert and "pen1" in hm:
    if popsize:
        lo = hm["pen1"][1]
        hi = hm["pen1"][2]
        scale = hm["pen1"][3]
        val = f"({pressure}+{lo}+coef['pen1']*({hi}-{lo})/(1.0*{scale}))"
    else:
        val = f"({pressure}+coef['pen1'])"
else:
    val = f"({pressure}+{para['pen1']})"
%>\
        file.write(f"1 DIRICHLET WATER 1* {${val}/1.e5} /\n")
        file.write("/\n")
% if everert and "thicknessmult" in hm:
    with open("THICKNESSMULT.INC", "w", encoding="utf8") as file:
%   for name in ["PV", "X", "X-", "Z", "Z-"]:
        file.write("MULT${name}\n")
<%
if popsize:
    lo = hm["thicknessmult"][1]
    hi = hm["thicknessmult"][2]
    scale = hm["thicknessmult"][3]
    mult_val = f"{lo}+coef['thicknessmult']*({hi}-{lo})/(1.0*{scale})"
else:
    mult_val = "coef['thicknessmult']"
%>\
        file.write(f"${dic['nxz'][0]*dic['nxz'][1]}*{${mult_val}} /\n")
%   endfor
% endif


if __name__ == "__main__":
    bcprop()
