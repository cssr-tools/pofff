#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

${imports_block}

import numpy as np

def krwe(sw, swi, nkrw):
    return ${krw_expr}

def krne(sw, sni, nkrn):
    return ${krn_expr}

def pcwce(sw, swi, pen, npen):
    return 0 if pen == 0 else ${cap_expr} / 1e5


def satufunc():
${monotonic_block}
${coef_block}
    safu = [[0.0 for _ in range(8)] for _ in range(7)]
${safu_block}
    with open(${tables_path}, "w", encoding="utf8") as file:
        file.write("SGFN\n")
        for j, para_row in enumerate(safu):
            if j > 0 and safu[j - 1] == para_row:
                file.write("/\n")
                continue
            sco2 = np.linspace(para_row[1], 1, int(para_row[7]))
            if sco2[0] > 0:
                file.write(f"{0}".rjust(12) + f"{0}".rjust(13) + f" {0}\n")
            for sc in sco2:
                krn_val = max(0, krne(1 - sc, para_row[1], para_row[4]))
                file.write(
                    (f"{sc:E}" if sc not in (0, 1) else f"{int(sc)}".rjust(12))
                    + (f" {krn_val:E}" if krn_val not in (0, 1) else f"{int(krn_val)}".rjust(13))
                    + f" {0}\n"
                )
            file.write("/\n")
        file.write("SWFN\n")
        for j, para_row in enumerate(safu):
            if j > 0 and safu[j - 1] == para_row:
                file.write("/\n")
                continue
            swatc = np.linspace(para_row[0], 1, int(para_row[7]))
            for sw in swatc:
                pc_val = pcwce(sw, para_row[0] - para_row[6], para_row[2], para_row[5])
                if sw <= para_row[0]:
                    krw_val = 0
                else:
                    krw_val = max(0, krwe(sw, para_row[0], para_row[3]))
                file.write(
                    (f"{sw:E}" if sw not in (0, 1) else f"{int(sw)}".rjust(12))
                    + (f" {krw_val:E}" if krw_val not in (0, 1) else f"{int(krw_val)}".rjust(13))
                    + (f" {pc_val:E}\n" if pc_val != 0 else f" 0\n")
                )
            file.write("/\n")


if __name__ == "__main__":
    satufunc()