#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to delete large files
"""

import os
import sys

if os.path.exists("NOMONOTONIC"):
    sys.exit()

for suff in [
    "INC",
    "EGRID",
    "DBG",
    "PRT",
    "SMSPEC",
    "UNRST",
    "UNSMRY",
    "INIT",
    "csv",
    "DATA",
]:
    for filename in os.listdir("."):
        if filename.endswith(suff):
            os.system(f"rm -rf *.{suff}")
            break
