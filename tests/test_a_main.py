# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the configuration files"""

import shutil
from pathlib import Path

import numpy as np
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid

from pofff.core.pofff import main

EPS = 1e-6


def test_a_main(tmp_path, monkeypatch):
    """See examples/input.toml"""
    repo_root = Path(__file__).parents[1]
    input_config = repo_root / "examples" / "input.toml"
    shutil.copy(input_config, tmp_path / "input.toml")
    monkeypatch.chdir(tmp_path)
    main()
    for name in [
        "compare_all_time_series.png",
        "map_0.25h.png",
        "mod_0.25.png",
        "exp_0.25.png",
    ]:
        assert (tmp_path / "output" / name).is_file()

    name = tmp_path / "output" / "OUTPUT.DATA"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    content = "".join(lines)
    assert "TUNING" in content
    assert "DISPERC" in content
    assert content.count("INCLUDE") == 11

    name = tmp_path / "output" / "TABLES.INC"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert len(lines) == 1225

    name = tmp_path / "output" / "spatial_map_0.25h.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 33600
    assert sum(float(line.split(",")[2]) for line in lines if line.strip()) > 0
    assert sum(float(line.split(",")[3]) for line in lines if line.strip()) > 0

    name = tmp_path / "output" / "time_series.csv"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()[1:]
    assert len(lines) == 2
    assert sum(float(line.split(",")[5]) for line in lines if line.strip()) > 0

    name = tmp_path / "output" / "func"
    with open(name, "r", encoding="utf8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    assert float(lines[0]) < 0

    egrid = OpmGrid(f"{tmp_path}/output/OUTPUT.EGRID")
    nx, _, nz = egrid.dimension
    assert nx == 140 and nz == 69
    init = OpmFile(f"{tmp_path}/output/OUTPUT.INIT")
    assert abs(np.sum(np.array(init["PORV"])) - 0.03100875) < EPS
    assert abs(min(init["DZ"]) - 4.7e-05) < EPS
    assert abs(max(init["DZ"]) - 0.031141) < EPS
    assert abs(min(init["PERMX"]) - 5e04) < EPS
    assert abs(max(init["PERMX"]) - 3e06) < EPS
    assert abs(max(init["TRANX"]) - 1117.8423) < EPS
    assert abs(np.sum(np.array(init["TRANX"])) - 2.12548e06) < EPS
    assert abs(np.sum(np.array(init["TRANZ"])) - 3.283e06) < EPS
    assert abs(max(init["TRANZ"]) - 101768.33) < EPS
    assert np.sum(np.array(init["SATNUM"])) - 34575 == 0
    assert np.sum(np.array(init["FIPNUM"])) - 28418 == 0
