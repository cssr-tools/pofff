# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the ert functionality via the configuration file"""

from pathlib import Path
import subprocess


def test_b_grid(tmp_path, monkeypatch):
    """See examples/tensor.toml and examples/cartesian.toml"""
    repo_root = Path(__file__).parents[1]
    monkeypatch.chdir(tmp_path)
    for case in ["cartesian", "tensor"]:
        config = repo_root / "examples" / f"{case}.toml"
        subprocess.run(
            [
                "pofff",
                "-i",
                str(config),
                "-o",
                case,
                "-t",
                "0.25",
            ],
            check=True,
        )
        for name in ["sim_metrics_0.txt", "map_0.25h.png", "time_series.csv"]:
            assert (tmp_path / case / name).is_file()
