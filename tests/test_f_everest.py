# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the everest functionality via the configuration file"""

import subprocess
from pathlib import Path


def test_f_everest(tmp_path, monkeypatch):
    """See examples/everest.toml"""
    repo_root = Path(__file__).parents[1]
    config = repo_root / "examples" / "everest.toml"
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        ["pofff", "-i", str(config), "-o", "everest", "-m", "everest"],
        check=True,
    )
    base = tmp_path / "everest" / "figures"
    assert (base / "details.png").is_file()
    assert (base / "optimization_results.png").is_file()

    name = base / "best_simulation" / "spatial_map_0.25h.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 33600
    assert sum(float(line.split(",")[2]) for line in lines if line.strip()) > 0
    assert sum(float(line.split(",")[3]) for line in lines if line.strip()) > 0

    name = base / "best_simulation" / "time_series.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 2
    assert sum(float(line.split(",")[5]) for line in lines if line.strip()) > 0

    name = base / "best_simulation" / "para.json"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert len(lines) == 5

    name = base / "best_simulation" / "func"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    assert float(lines[0]) < 0

    name = tmp_path / "everest" / "everest.yml"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    names = [
        "scale",
        "monotonic",
        "copyd",
        "equalreg",
        "satufunc",
        "bcprop",
        "flow",
        "data",
        "metric",
        "delete",
    ]
    for name in names:
        assert f"- {name}" in content

    name = tmp_path / "everest" / "jobs" / "bcprop.py"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    pattern = "(104900+1000+coef['pen1']*(2000-1000)/(1.0*10))/1.e5"
    assert pattern in content
    assert content.count("0.9+coef['thicknessmult']*(1.1-0.9)/(1.0*50)") == 5

    name = tmp_path / "everest" / "jobs" / "equalreg.py"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    pattern = "1000000.0+coef['perm5']*(3000000.0-1000000.0)/(1.0*10)"
    assert "".join(lines).count(pattern) == 3

    name = tmp_path / "everest" / "jobs" / "satufunc.py"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert "1000+coef['pen1']*(2000-1000)/(1.0*10)" in "".join(lines)
