# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the functionality of the data generation"""

from pathlib import Path
import shutil

from pofff.jobs.data import main

EPS = 1e-6
TIME_SERIES = [
    1.200e03,
    1.11764e05,
    1.05885e05,
    0.000e00,
    0.000e00,
    3.417e-07,
    6.784e-10,
    0.000e00,
    0.000e00,
    3.923e-23,
    3.848e-23,
    1.424e-05,
    7.016e-07,
]


def test_c_data(tmp_path, monkeypatch):
    """Check spatial_map_*h.csv and time_series.csv"""
    repo_root = Path(__file__).parents[1]
    where = repo_root / "tests" / "flows"
    for i in ["EGRID", "INIT", "SMSPEC", "UNRST", "UNSMRY"]:
        data = where / f"OUTPUT.{i}"
        shutil.copy(data, tmp_path / f"OUTPUT.{i}")
    cellmap = repo_root / "src" / "pofff" / "geology" / "cellmap.npy"
    shutil.copy(cellmap, tmp_path / "cellmap.npy")
    monkeypatch.chdir(tmp_path)
    main(["-t", "0.25"])

    name = tmp_path / "spatial_map_0.25h.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 33600
    satu = sum(float(line.split(",")[2]) for line in lines if line.strip())
    assert abs(satu - 16.51) < EPS
    conc = sum(float(line.split(",")[3]) for line in lines if line.strip())
    assert abs(conc - 258.328) < EPS

    name = tmp_path / "time_series.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 2
    values = lines[-1].split(",")
    for value, ref in zip(values, TIME_SERIES):
        assert abs(float(value) - ref) < EPS
