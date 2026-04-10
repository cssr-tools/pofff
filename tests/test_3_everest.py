# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the everest functionality via the configuration file"""

from pathlib import Path
import subprocess


def test_everest(tmp_path, monkeypatch):
    """See examples/everest.toml"""
    repo_root = Path(__file__).parents[1]
    config = repo_root / "examples" / "everest.toml"
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        ["pofff", "-i", str(config), "-o", "everest", "-m", "everest"],
        check=True,
    )
    assert (tmp_path / "everest" / "figures" / "details.png").is_file()
    assert (
        tmp_path / "everest" / "figures" / "best_simulation" / "spatial_map_0.25h.csv"
    ).is_file()
