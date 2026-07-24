# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Central configuration models for pofff.

Defines structured configuration objects used across the codebase:
- CliConfig: raw CLI inputs
- PofffConfig: unified runtime and TOML-based configuration
"""

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(slots=True)
class CliConfig:
    """
    Container for command-line arguments before normalization.
    """

    fol: Path
    deck: Path
    jobs: Path
    experiment: str
    times: str
    msat: str
    mcon: str
    mode: str
    figures: str
    location: str
    use: str


@dataclass(slots=True)
class PofffConfig:
    """
    Central configuration object for pofff.

    Combines CLI options, TOML inputs, and derived runtime settings.
    """

    # ------------------------------------------------------------------
    # CLI configuration (normalized)
    # ------------------------------------------------------------------
    path: Path
    fol: Path = Path("output")
    deck: Path = Path("output")
    jobs: Path = Path("output")
    experiment: str = "run2"
    times: str = "0.25"
    msat: str = "1e-2"
    mcon: str = "1e-1"
    mode: str = "single"
    figures: str = "basic"
    location: str = ""
    use: str = "1"

    # ------------------------------------------------------------------
    # TOML configuration (simulation setup)
    # ------------------------------------------------------------------
    flow: str = "flow"
    grid: str = "corner-point"
    thickness: str = "final"
    mult_thickness: float = 1.0
    x: list[int] = field(default_factory=list)
    z: list[int] = field(default_factory=list)
    temperature: list[float] = field(default_factory=lambda: [20, 20])
    pressure: float = 0.0
    diffusion: np.ndarray = field(default_factory=lambda: np.array([1e-9, 2e-8]))
    sources: list[list[float]] = field(default_factory=lambda: [[0, 0], [0, 0]])
    inj: list[list[Any]] = field(default_factory=lambda: [[]])
    krw: str = "(max(0, (sw - swi) / (1 - swi))) ** nkrw"
    krn: str = "(max(0, (1 - sw - sni) / (1 - sni))) ** nkrn"
    cap: str = "pen * ((sw-swi) / (1-swi)) ** (-(1.0 / npen))"

    # ------------------------------------------------------------------
    # TOML configuration (ERT / everest runtime)
    # ------------------------------------------------------------------
    cores: int | None = None
    maxtime: float | None = None
    delete: bool | None = None

    # ------------------------------------------------------------------
    # TOML configuration (ERT)
    # ------------------------------------------------------------------
    ertargs: str | None = None
    ensembles: int | None = None
    enkf_alpha: float | None = None
    errors: np.ndarray | None = None
    random_seed: int | None = None  # Used by scipy differential evolution

    # ------------------------------------------------------------------
    # TOML configuration (everest)
    # ------------------------------------------------------------------
    min_realizations_success: int | None = None
    max_function_evaluations: int | None = None
    max_batch_num: int | None = None

    # ------------------------------------------------------------------
    # TOML differential evolution parameters (via everest)
    # ------------------------------------------------------------------
    args: tuple[Any, ...] | None = None
    strategy: str | None = None
    maxiter: int | None = None
    popsize: int | None = None
    tol: float | None = None
    mutation: float | tuple[float, float] | None = None
    recombination: float | None = None
    rng: Any | None = None
    callback: Callable | None = None
    disp: bool | None = None
    polish: bool | None = None
    init: str | None = None
    atol: float | None = None
    updating: str | None = None
    workers: int | None = None
    constraints: Iterable[Any] | None = None
    x0: Sequence[float] | None = None
    integrality: Sequence[bool] | None = None
    vectorized: bool | None = None

    # ------------------------------------------------------------------
    # OPM input arrays
    # ------------------------------------------------------------------
    facies: list[int] = field(default_factory=list)
    fluxnum: list[str] = field(default_factory=list)
    fipnum: list[str] = field(default_factory=list)
    porv: list[str] = field(default_factory=list)
    multpv: list[str] = field(default_factory=list)
    dx: list | None = field(default_factory=list)
    dz: list | None = field(default_factory=list)

    # ------------------------------------------------------------------
    # FluidFlower geometry and observation setup
    # ------------------------------------------------------------------
    dims: list[float] = field(default_factory=lambda: [2.8, 0.019, 1.2])
    sensors: list[list[float]] = field(default_factory=lambda: [[1.5, 0.5], [1.7, 1.1]])
    sensor_ik: list[list[int]] = field(default_factory=lambda: [[0, 0], [0, 0]])
    source_ik: list[list[int]] = field(default_factory=lambda: [[0, 0], [0, 0]])
    boxa: list[list[float]] = field(default_factory=lambda: [[1.1, 0.0], [2.8, 0.6]])
    boxb: list[list[float]] = field(default_factory=lambda: [[0.0, 0.6], [1.1, 1.2]])
    boxc: list[list[float]] = field(default_factory=lambda: [[1.1, 0.1], [2.6, 0.4]])

    # ------------------------------------------------------------------
    # Miscellaneous runtime flags and metadata
    # ------------------------------------------------------------------
    hm: dict[str, Any] = field(default_factory=dict)
    monotonic: bool = False
    hascellmaps: bool = False
    everert: bool = False
    tuning: bool = False
    para: dict[str, Any] = field(default_factory=dict)
    nxz: list[int] = field(default_factory=lambda: [0, 0])
    data: str | None = None
