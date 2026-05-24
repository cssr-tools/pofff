#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

${imports_block}

def bcprop():
    """Evaluation of the boundary condition."""
${monotonic_block}
${coef_block}
    with open(${bcprop_path}, "w", encoding="utf8") as file:
        file.write("BCPROP\n")
${bc_line}
        file.write("/\n")
${thickness_block}

if __name__ == "__main__":
    bcprop()
