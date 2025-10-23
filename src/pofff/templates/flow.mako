#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

import os
import sys
import subprocess

% if dic['monotonic']:
if os.path.exists("NOMONOTONIC"):
    sys.exit()
% endif
try:
% if dic["maxtime"] > 0:
    p = subprocess.run([${str([f'{row}' for row in dic['flow'].split(' ')])[1:-1]}, '${dic['data']}'], timeout=${dic["maxtime"]})
%else:
    p = subprocess.run([${str([f'{row}' for row in dic['flow'].split(' ')])[1:-1]}, '${dic['data']}'])
% endif
except subprocess.TimeoutExpired:
    print('Timeout for flow')
% if dic["delete"]:
    for suff in ["INC", "EGRID", "DBG", "PRT", "SMSPEC", "UNRST", "UNSMRY", "INIT"]:
        os.system(f"rm -rf *.{suff}")
    for pref in ["thickness_eval","metr_eval","safu_eval","poro_eval"]:
        os.system(f"rm -rf {pref}.*")
% endif