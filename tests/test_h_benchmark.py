# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the single functionality and plotting for the benchmark"""

from pathlib import Path
import subprocess


def test_h_benchmark(tmp_path, monkeypatch):
    """See examples/single.toml"""
    repo_root = Path(__file__).parents[1]
    config = repo_root / "examples" / "single.toml"
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [
            "pofff",
            "-i",
            str(config),
            "-o",
            "benchmark",
            "-t",
            "24,48,72",
            "-e",
            "C1",
        ],
        check=True,
    )
    assert (tmp_path / "benchmark" / "compare_all_time_series.png").is_file()
    assert (tmp_path / "benchmark" / "compare_all_sparse.png").is_file()
