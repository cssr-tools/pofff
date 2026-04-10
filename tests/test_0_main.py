# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the configuration files"""

from pathlib import Path
import shutil
from pofff.core.pofff import main


def test_main(tmp_path, monkeypatch):
    """See examples/input.toml"""
    repo_root = Path(__file__).parents[1]
    input_config = repo_root / "examples" / "input.toml"
    shutil.copy(input_config, tmp_path / "input.toml")
    monkeypatch.chdir(tmp_path)
    main()
    for name in ["sim_metrics_0.txt", "map_0.25h.png", "time_series.csv"]:
        assert (tmp_path / "output" / name).is_file()
