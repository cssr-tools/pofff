# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test FAIR data generation mode for benchmark visualization outputs."""

import subprocess

EPS = 2e-2


def test_i_fair(tmp_path, monkeypatch):
    """Towards FAIR data https://www.nature.com/articles/sdata201618"""
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [
            "pofff",
            "-m",
            "fair",
            "-c",
            "5e-2",
            "-o",
            "appendix",
        ],
        check=True,
    )
    base = tmp_path / "appendix"
    assert (
        base / "zoom_means_segmented_snapshots_satmin-0.01_conmin-0.05.png"
    ).is_file()
    name = base / "error_table_satmin-0.01_conmin-0.05.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert len(lines) == 23
    values = lines[2].split(",")
    assert abs(float(values[8]) - 18.32) < EPS
    values = lines[13].split(",")
    assert abs(float(values[7]) - 31.61) < EPS
    assert abs(float(values[8]) - 28.32) < EPS
