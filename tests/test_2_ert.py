# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the ert functionality via the configuration file"""

from pathlib import Path
import subprocess


def test_ert(tmp_path, monkeypatch):
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
    assert (base / "best_simulation" / "spatial_map_0.25h.csv").is_file()
