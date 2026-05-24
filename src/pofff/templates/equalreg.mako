#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

${imports_block}

def equalreg():
    """Evaluation of model parameters."""
${monotonic_block}
${coef_block}
    with open(${output_path}, "w", encoding="utf8") as file:
        file.write("EQUALREG\n")
${body_block}
        file.write("/\n")

if __name__ == "__main__":
    equalreg()
