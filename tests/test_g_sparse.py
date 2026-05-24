# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the sparse data generation"""

from pathlib import Path
import shutil

from pofff.visualization.sparse_values import main


def test_g_sparse(tmp_path, monkeypatch):
    """Check sparse_data.csv"""
    repo_root = Path(__file__).parents[1]
    data = (
        repo_root
        / "src"
        / "pofff"
        / "fluidflower"
        / "cssr"
        / "conmin5e-2"
        / "time_series.csv"
    )
    shutil.copy(data, tmp_path / "time_series.csv")
    monkeypatch.chdir(tmp_path)
    main()

    name = tmp_path / "sparse_data.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 13
    assert len(lines[0].split(",")) == 7
    for i in [0, 1, 2, 5, 6, 9, 11, 12]:
        val = float(lines[i].split(",")[2])
        assert val > 0
