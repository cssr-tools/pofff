# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Configuration and runtime settings shared across pofff workflows.

The data classes combine raw command-line selections, validated TOML input,
FluidFlower geometry, OPM deck arrays, history-matching options, and values
derived while grids, simulations, and benchmark products are created.
``PofffConfig`` is mutable because paths, cell indices, properties, and runtime
flags are populated progressively."""

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(slots=True)
class CliConfig:
    """Store command-line values before TOML normalization.

    Attributes
    ----------
    fol
        Base output directory.
    deck
        Directory used for generated OPM deck files.
    jobs
        Directory used for generated ERT and Everest job scripts.
    experiment
        FluidFlower experimental realization, normalized as ``run1`` through ``run5``.
    times
        Comma-separated benchmark evaluation times in hours.
    msat
        Minimum gas-saturation threshold used for segmentation.
    mcon
        Minimum dissolved-CO2 concentration threshold used for segmentation.
    mode
        Selected simulation, file-generation, history-matching, or FAIR workflow.
    figures
        Figure mode: ``all``, ``basic``, or ``none``.
    location
        Directory containing comparison or precomputed benchmark data.
    use
        Whether precomputed Wasserstein distances may be used."""

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
    """Store TOML input, CLI options, and derived pofff runtime state.

    TOML-backed attributes retain the spelling used by existing configuration files.
    Derived arrays, grid dimensions, feature indices, paths, and history-matching
    flags are populated while input is normalized and model files are generated.

    Attributes
    ----------
    path
        Package root containing geology, templates, jobs, and benchmark resources.
    fol, deck, jobs
        Base output, generated deck, and generated job-script directories.
    experiment, times, msat, mcon
        Experimental realization, evaluation times [h], and segmentation thresholds.
    mode, figures, location, use
        Workflow, figure selection, comparison-data location, and reuse selection.
    flow
        OPM Flow command and command-line options.
    grid
        Grid representation: ``cartesian``, ``tensor``, or ``corner-point``.
    thickness
        ``initial`` or ``final`` thickness map, or a positive physical thickness [m].
    mult_thickness
        Positive multiplier applied to the selected thickness map.
    x, z
        Horizontal and vertical refinement counts.
    temperature
        Initial and boundary temperatures used by the deck.
    pressure
        Positive reference pressure used for initialization and boundary properties.
    diffusion
        Two molecular diffusion coefficients, converted from m²/s to m²/day.
    sources
        Two injection-source coordinates as ``[x, z]`` rows [m].
    inj
        Injection rows containing times, rates, and optional TUNING text.
    krw, krn, cap
        Python expressions used to generate saturation-function tables.
    cores, maxtime, delete
        Shared ERT/Everest resources, run timeout, and cleanup selection.
    ertargs, ensembles, enkf_alpha, errors, random_seed
        ERT command options, ensemble controls, observation errors, and random seed.
    min_realizations_success, max_function_evaluations, max_batch_num
        Shared success requirement and Everest evaluation limits.
    strategy, maxiter, popsize, tol, mutation, recombination
        Differential-evolution strategy and convergence settings.
    rng, callback, disp, polish, init, atol, updating, workers
        Additional differential-evolution options passed to Everest.
    constraints, x0, integrality, vectorized
        Optional differential-evolution constraints and evaluation controls.
    facies, fluxnum, fipnum, porv, multpv, dx, dz
        Generated facies, region, pore-volume, and grid-size arrays for OPM input.
    dims
        FluidFlower dimensions in x, y, and z order [m].
    sensors, sensor_ik
        Sensor coordinates [m] and zero-based grid indices.
    source_ik
        One-based grid indices of the two injection sources.
    boxa, boxb, boxc
        Opposite ``[x, z]`` corners of the benchmark reporting boxes [m].
    hm, para
        History-matching definitions and fixed facies properties.
    monotonic, hascellmaps, everert, tuning
        Derived workflow and file-generation flags.
    nxz
        Numbers of simulation cells in x and z order.
    data
        Uppercase OPM deck base name derived from the output directory."""

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
