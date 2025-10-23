#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

import os
import sys

% if dic['monotonic']:
if os.path.exists("NOMONOTONIC"):
    sys.exit()
% endif
os.system("cp ${dic['deck']}/*.DATA .")
