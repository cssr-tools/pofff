#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Check if the parameters are monotonic
"""

import json

with open("parameters.json", "r", encoding="utf8") as file:
    coef = json.load(file)
nomonotonic = False
% for name in ["SWI", "SNI", "PEN", "NKRW", "NKRN", "NPE"]:
<% name0, i0, = "", -1 %>\
% for i in range(1,8):
% if f"{name}{i}" in dic["hm"]:
% if i0 == -1:
<% name0, i0, = name, i %>\
% else:
if coef['${name0}${i0}'] < coef['${name}${i}']:
    nomonotonic = True
<% name0, i0, = name, i %>\
% endif
% endif
% endfor
% endfor
% for name in ["PERM", "PERMX", "PERMZ", "DISPERC"]:
<% name0, i0, = "", -1 %>\
% for i in reversed(range(1,8)):
% if f"{name}{i}" in dic["hm"]:
% if i0 == -1:
<% name0, i0, = name, i %>\
% else:
if coef['${name0}${i0}'] < coef['${name}${i}']:
    nomonotonic = True
<% name0, i0, = name, i %>\
% endif
% endif
% endfor
% endfor
if nomonotonic:
    with open("NOMONOTONIC", "w", encoding="utf8") as file:
        file.write("True")