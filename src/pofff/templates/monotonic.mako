#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Check if the parameters are monotonic
"""

import json

with open("parameters.json", "r", encoding="utf8") as file:
    coef = json.load(file)

nomonotonic = False

# Increasing order parameters
% for name in ["swi", "sni", "pen", "nkrw", "nkrn", "npe"]:
<% name0, i0 = "", -1 %>\
%   for i in range(1, 8):
%       if f"{name}{i}" in dic["hm"]:
%           if i0 == -1:
<%                 name0, i0 = name, i %>\
%           else:
if coef['${name0}${i0}'] < coef['${name}${i}']:
    nomonotonic = True
<%                 name0, i0 = name, i %>\
%           endif
%       endif
%   endfor
% endfor

# Decreasing order parameters
% for name in ["perm", "permx", "permz", "disperc"]:
<% name0, i0 = "", -1 %>\
%   for i in reversed(range(1, 8)):
%       if f"{name}{i}" in dic["hm"]:
%           if i0 == -1:
<%                 name0, i0 = name, i %>\
%           else:
if coef['${name0}${i0}'] < coef['${name}${i}']:
    nomonotonic = True
<%                 name0, i0 = name, i %>\
%           endif
%       endif
%   endfor
% endfor

if nomonotonic:
    with open("NOMONOTONIC", "w", encoding="utf8") as file:
        file.write("True")
