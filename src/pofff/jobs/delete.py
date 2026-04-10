#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to delete large files
"""

from pathlib import Path
import sys

# Exit early if sentinel file exists
if Path("NOMONOTONIC").exists():
    sys.exit(0)

suffixes = {
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
}

cwd = Path(".")

for path in cwd.iterdir():
    if path.is_file() and path.suffix.lstrip(".") in suffixes:
        path.unlink()
