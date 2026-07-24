# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the ert functionality via the configuration file"""

import subprocess
from pathlib import Path


def test_e_ert(tmp_path, monkeypatch):
    """See examples/ert.toml"""
    repo_root = Path(__file__).parents[1]
    config = repo_root / "examples" / "ert.toml"
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [
            "pofff",
            "-i",
            str(config),
            "-o",
            "ert",
            "-m",
            "ert",
            "-t",
            "0.25,0.5",
        ],
        check=True,
    )
    base = tmp_path / "ert" / "figures"
    assert (base / "hm_mismatch.png").is_file()

    name = base / "best_simulation" / "spatial_map_0.25h.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 33600
    assert sum(float(line.split(",")[2]) for line in lines if line.strip()) > 0
    assert sum(float(line.split(",")[3]) for line in lines if line.strip()) > 0

    name = base / "best_simulation" / "time_series.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 3
    assert sum(float(line.split(",")[5]) for line in lines if line.strip()) > 0

    name = base / "best_simulation" / "parameters.txt"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert len(lines) == 3

    name = base / "best_simulation" / "sim_metrics_0.txt"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert len(lines) == 2
    dist = sum(float(line) for line in lines)
    assert 0 < dist < 360

    name = tmp_path / "ert" / "ert.txt"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    names = [
        "COPYD",
        "EQUALREG",
        "SATUFUNC",
        "BCPROP",
        "FLOW",
        "DATA",
        "METRIC",
        "DELETE",
    ]
    for name in names:
        assert f"./jobs/{name}" in content

    name = tmp_path / "ert" / "jobs" / "bcprop.py"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "(104900+coef['pen1'])/1.e5" in content
    assert content.count("coef['thicknessmult']") == 5

    name = tmp_path / "ert" / "jobs" / "equalreg.py"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert "".join(lines).count("coef['perm5']") == 3

    name = tmp_path / "ert" / "jobs" / "satufunc.py"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert "coef['pen1']" in "".join(lines)
