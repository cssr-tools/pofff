#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to generate the sparse values.
"""

import sys
import numpy as np


def postprocessing():
    """Compute the quantities in boxes A, B, and C"""
    dic = {"t": 259200}
    values = np.genfromtxt(
        "time_series.csv",
        delimiter=",",
        skip_header=1,
    )
    if values[-1][0] < dic["t"]:
        print(
            "The box quantities in the benchmark figures required at least to simulate "
            f"for 72 hours (the simulation is only {values[-1][0]/3600:.2f} h)"
        )
        sys.exit()
    i_d = [val[0] for val in values].index(float(3 * 86400))
    dic["sparse1a"] = max(val[1] for val in values)
    dic["sparse1b"] = max(val[2] for val in values)
    dic["sparse2"] = values[np.array([val[3] for val in values]).argmax()][0]
    dic["sparse3a"] = values[i_d][3]
    dic["sparse3c"] = values[i_d][5]
    dic["sparse3d"] = values[i_d][6]
    dic["sparse4c"] = values[i_d][9]
    dic["sparse5"] = 0
    for i, val in enumerate(val[11] for val in values):
        if val >= 1.65:
            dic["sparse5"] = values[i][0]
            break
    dic["sparse6"] = values[-1][6]
    with open("sparse_data.csv", "w", encoding="utf8") as file:
        file.write(
            f"dx,p10_mean,p50_mean,p90_mean,p10_dev,p50_dev,p90_dev\n"
            f"1a,0,{dic['sparse1a']},0,0,0,0\n"
            f"1b,0,{dic['sparse1b']},0,0,0,0\n"
            f"2,0,{dic['sparse2']},0,0,0,0\n"
            f"3a,0,{dic['sparse3a']},0,0,0,0\n"
            f"3b,0,0,0,0,0,0\n"
            f"3c,0,{dic['sparse3c']},0,0,0,0\n"
            f"3d,0,{dic['sparse3d']},0,0,0,0\n"
            f"4a,0,0,0,0,0,0\n"
            f"4b,0,0,0,0,0,0\n"
            f"4c,0,{dic['sparse4c']},0,0,0,0\n"
            f"4d,0,0,0,0,0,0\n"
            f"5,0,{dic['sparse5']},0,0,0,0\n"
            f"6,0,{dic['sparse6']},0,0,0,0\n"
        )


if __name__ == "__main__":
    postprocessing()
