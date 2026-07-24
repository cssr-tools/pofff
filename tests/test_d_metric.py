# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the functionality of the metric evaluations"""

import shutil
from pathlib import Path

from pofff.jobs.metric import main

EPS = 1e-6


def test_d_metric(tmp_path, monkeypatch):
    """Check func and sim_metrics_0.txt"""
    repo_root = Path(__file__).parents[1]
    pofff = repo_root / "src" / "pofff"
    for i in [24, 48, 72, 96, 120]:
        data = pofff / "fluidflower" / "cssr" / "conmin1e-1" / f"spatial_map_{i}h.csv"
        shutil.copy(data, tmp_path / f"spatial_map_{i}h.csv")
    monkeypatch.chdir(tmp_path)
    main(["-p", str(pofff)])

    name = tmp_path / "func"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert float(lines[0]) - (-0.031148980582265527) < EPS

    name = tmp_path / "sim_metrics_0.txt"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert float(lines[0]) - (42.282415132027424) < EPS
    assert float(lines[1]) - (18.40352290510448) < EPS
    assert float(lines[2]) - (20.166760361898472) < EPS
    assert float(lines[3]) - (21.98276098171813) < EPS
    assert float(lines[4]) - (29.547708093879987) < EPS
