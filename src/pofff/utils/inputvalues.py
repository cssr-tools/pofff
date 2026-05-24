# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Utility functions to prepare and normalize input values for pofff."""

import tomllib
from pathlib import Path
import numpy as np

from pofff.config.config import CliConfig, PofffConfig

FACIES_KEYS = {
    "poro",
    "perm",
    "permx",
    "permy",
    "permz",
    "disperc",
    "swi",
    "sni",
    "pen",
    "nkrw",
    "nkrn",
    "npe",
    "thre",
    "npnt",
}


def load_toml(filename: str) -> dict:
    """Load a TOML configuration file and return its content."""
    with open(filename, "rb") as f:
        toml = tomllib.load(f)
    return toml


def postprocess_config(cfg: PofffConfig, toml: dict) -> None:
    """Enrich configuration with derived values and runtime flags."""
    cfg.para.update(
        {
            "permx7": 0,
            "permz7": 0,
            "poro7": 0,
            "disperc7": 0,
            "swi7": 0,
            "sni7": 0,
            "pen7": 0,
            "nkrw7": 2,
            "nkrn7": 2,
            "npe7": 2,
            "thre7": 5e-2,
            "npnt7": 2,
        }
    )

    cfg.nxz = [int(np.sum(cfg.x)), int(np.sum(cfg.z))]
    cfg.diffusion = 86400 * np.array(cfg.diffusion)  # Convert to m²/day
    cfg.data = cfg.fol.name.upper()
    process_tuning(cfg)
    cfg.hascellmaps = (
        cfg.x != [140]
        or cfg.z != [7, 5, 5, 5, 5, 5, 5, 8, 10, 9, 5]
        or cfg.grid != "corner-point"
    )
    cfg.everert = cfg.cores is not None and cfg.mode != "single"
    if cfg.everert:
        for i in range(1, 8):
            for name in FACIES_KEYS:
                key = f"{name}{i}"
                if key in toml:
                    cfg.hm[key] = toml[key]
        if "thicknessmult" in toml:
            cfg.hm["thicknessmult"] = toml["thicknessmult"]


def process_tuning(cfg: PofffConfig) -> None:
    """Enable tuning and normalize injection specifications if requested."""
    for token in cfg.flow.split():
        if "--enable-tuning" not in token:
            continue
        if token[16:] not in {"true", "True", "1"}:
            continue
        cfg.tuning = True
        for i, inj in enumerate(cfg.inj):
            if len(inj) != 5:
                continue
            parts = inj[-1].split("/")
            cfg.inj[i] = [
                *inj[:-1],
                parts[0].strip(),
                *(p.strip() for p in parts[1:]),
            ]


def extract_facies(data: dict) -> dict:
    """Extract definitions and remove them from the main config dict."""
    facies = {k: data.pop(k) for k in list(data) if k.startswith("facie")}
    for i in range(1, 8):
        for name in FACIES_KEYS:
            data.pop(f"{name}{i}", None)
    data.pop("thicknessmult", None)
    return facies


def build_config(
    *,
    pofff_path: Path,
    cli: CliConfig,
    toml: dict,
) -> PofffConfig:
    """Build and return a fully initialized PofffConfig object."""
    facies = extract_facies(toml)
    cfg = PofffConfig(
        path=pofff_path,
        fol=cli.fol,
        deck=cli.deck,
        jobs=cli.jobs,
        experiment=cli.experiment,
        times=cli.times,
        msat=cli.msat,
        mcon=cli.mcon,
        mode=cli.mode,
        figures=cli.figures,
        location=cli.location,
        use=cli.use,
        **toml,
    )
    for values in facies.values():
        cfg.para.update(values)
    return cfg
