#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Check if the parameters are monotonic"""

import json

with open("parameters.json", "r", encoding="utf8") as file:
    coef = json.load(file)

nomonotonic = False

# Increasing order parameters
${increasing_block}

# Decreasing order parameters
${decreasing_block}

if nomonotonic:
    with open("NOMONOTONIC", "w", encoding="utf8") as file:
        file.write("True")
