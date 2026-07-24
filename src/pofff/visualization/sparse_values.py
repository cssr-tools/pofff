#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Generate sparse benchmark values from a time series CSV."""

import sys
from pathlib import Path

import numpy as np

SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400
REQUIRED_TIME = 3 * SECONDS_PER_DAY  # 72 hours total


def main(
    timeseries_file: str = "time_series.csv",
    output_file: str = "sparse_data.csv",
) -> None:
    """Read a time series CSV, extract benchmark values,
    and write them in sparse CSV format."""

    if not Path(timeseries_file).exists():
        print(f"ERROR: File not found: {timeseries_file}")
        sys.exit(1)

    values = np.genfromtxt(timeseries_file, delimiter=",", skip_header=1)

    if values.ndim != 2 or values.shape[0] == 0:
        print("ERROR: time_series.csv contains no valid data")
        sys.exit(1)

    time = values[:, 0]

    if time[-1] < REQUIRED_TIME:
        sim_hours = time[-1] / SECONDS_PER_HOUR
        print(
            "The box quantities in the benchmark figures require at least "
            f"72 hours of simulation (current simulation: {sim_hours:.2f} h)"
        )
        sys.exit(0)

    try:
        idx_72h = np.where(time == REQUIRED_TIME)[0][0]
    except IndexError:
        print("ERROR: No data point exactly at 72 hours (259200 s)")
        sys.exit(1)

    sparse = {}

    sparse["sparse1a"] = np.max(values[:, 1])
    sparse["sparse1b"] = np.max(values[:, 2])
    sparse["sparse2"] = time[np.argmax(values[:, 3])]
    sparse["sparse3a"] = values[idx_72h, 3]
    sparse["sparse3c"] = values[idx_72h, 5]
    sparse["sparse3d"] = values[idx_72h, 6]
    sparse["sparse4c"] = values[idx_72h, 9]
    mask = values[:, 11] >= 1.65
    sparse["sparse5"] = time[mask][0] if np.any(mask) else 0.0
    sparse["sparse6"] = values[-1, 6]

    with open(output_file, "w", encoding="utf8") as f:
        f.write("dx,p10_mean,p50_mean,p90_mean,p10_dev,p50_dev,p90_dev\n")
        f.write(f"1a,0,{sparse['sparse1a']},0,0,0,0\n")
        f.write(f"1b,0,{sparse['sparse1b']},0,0,0,0\n")
        f.write(f"2,0,{sparse['sparse2']},0,0,0,0\n")
        f.write(f"3a,0,{sparse['sparse3a']},0,0,0,0\n")
        f.write("3b,0,0,0,0,0,0\n")
        f.write(f"3c,0,{sparse['sparse3c']},0,0,0,0\n")
        f.write(f"3d,0,{sparse['sparse3d']},0,0,0,0\n")
        f.write("4a,0,0,0,0,0,0\n")
        f.write("4b,0,0,0,0,0,0\n")
        f.write(f"4c,0,{sparse['sparse4c']},0,0,0,0\n")
        f.write("4d,0,0,0,0,0,0\n")
        f.write(f"5,0,{sparse['sparse5']},0,0,0,0\n")
        f.write(f"6,0,{sparse['sparse6']},0,0,0,0\n")


if __name__ == "__main__":
    main()
