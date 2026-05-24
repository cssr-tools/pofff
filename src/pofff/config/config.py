#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Central configuration models for pofff.

Defines structured configuration objects used across the codebase:
- CliConfig: raw CLI inputs
- PofffConfig: unified runtime and TOML-based configuration
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Iterable, Sequence, Tuple, Optional, Union
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
    x: List[int] = field(default_factory=list)
    z: List[int] = field(default_factory=list)
    temperature: List[float] = field(default_factory=lambda: [20, 20])
    pressure: float = 0.0
    diffusion: np.ndarray = field(default_factory=lambda: np.array([1e-9, 2e-8]))
    sources: List[List[float]] = field(default_factory=lambda: [[0, 0], [0, 0]])
    inj: List[List[Any]] = field(default_factory=lambda: [[]])
    krw: str = "(max(0, (sw - swi) / (1 - swi))) ** nkrw"
    krn: str = "(max(0, (1 - sw - sni) / (1 - sni))) ** nkrn"
    cap: str = "pen * ((sw-swi) / (1-swi)) ** (-(1.0 / npen))"

    # ------------------------------------------------------------------
    # TOML configuration (ERT / everest runtime)
    # ------------------------------------------------------------------
    cores: Optional[int] = None
    maxtime: Optional[float] = None
    delete: Optional[bool] = None

    # ------------------------------------------------------------------
    # TOML configuration (ERT)
    # ------------------------------------------------------------------
    ertargs: Optional[str] = None
    ensembles: Optional[int] = None
    enkf_alpha: Optional[float] = None
    errors: Optional[np.ndarray] = None
    random_seed: Optional[int] = None  # Used by scipy differential evolution

    # ------------------------------------------------------------------
    # TOML configuration (everest)
    # ------------------------------------------------------------------
    min_realizations_success: Optional[int] = None
    max_function_evaluations: Optional[int] = None
    max_batch_num: Optional[int] = None

    # ------------------------------------------------------------------
    # TOML differential evolution parameters (via everest)
    # ------------------------------------------------------------------
    args: Optional[Tuple[Any, ...]] = None
    strategy: Optional[str] = None
    maxiter: Optional[int] = None
    popsize: Optional[int] = None
    tol: Optional[float] = None
    mutation: Optional[Union[float, Tuple[float, float]]] = None
    recombination: Optional[float] = None
    rng: Optional[Any] = None
    callback: Optional[Callable] = None
    disp: Optional[bool] = None
    polish: Optional[bool] = None
    init: Optional[str] = None
    atol: Optional[float] = None
    updating: Optional[str] = None
    workers: Optional[int] = None
    constraints: Optional[Iterable[Any]] = None
    x0: Optional[Sequence[float]] = None
    integrality: Optional[Sequence[bool]] = None
    vectorized: Optional[bool] = None

    # ------------------------------------------------------------------
    # OPM input arrays
    # ------------------------------------------------------------------
    facies: list[int] = field(default_factory=list)
    fluxnum: list[str] = field(default_factory=list)
    fipnum: list[str] = field(default_factory=list)
    porv: list[str] = field(default_factory=list)
    multpv: list[str] = field(default_factory=list)
    dx: Optional[list] = field(default_factory=list)
    dz: Optional[list] = field(default_factory=list)

    # ------------------------------------------------------------------
    # FluidFlower geometry and observation setup
    # ------------------------------------------------------------------
    dims: List[float] = field(default_factory=lambda: [2.8, 0.019, 1.2])
    sensors: List[List[float]] = field(default_factory=lambda: [[1.5, 0.5], [1.7, 1.1]])
    sensor_ik: List[List[int]] = field(default_factory=lambda: [[0, 0], [0, 0]])
    source_ik: List[List[int]] = field(default_factory=lambda: [[0, 0], [0, 0]])
    boxa: List[List[float]] = field(default_factory=lambda: [[1.1, 0.0], [2.8, 0.6]])
    boxb: List[List[float]] = field(default_factory=lambda: [[0.0, 0.6], [1.1, 1.2]])
    boxc: List[List[float]] = field(default_factory=lambda: [[1.1, 0.1], [2.6, 0.4]])

    # ------------------------------------------------------------------
    # Miscellaneous runtime flags and metadata
    # ------------------------------------------------------------------
    hm: Dict[str, Any] = field(default_factory=dict)
    monotonic: bool = False
    hascellmaps: bool = False
    everert: bool = False
    tuning: bool = False
    para: Dict[str, Any] = field(default_factory=dict)
    nxz: List[int] = field(default_factory=lambda: [0, 0])
    data: Optional[str] = None
