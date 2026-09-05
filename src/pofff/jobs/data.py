#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0914

"""Generate FluidFlower benchmark data from OPM Flow results.

The job locates the current simulation, reads restart, grid, initialization, and
summary files through the OPM Python bindings, calculates sparse benchmark time
series, maps saturation and dissolved CO2 to the reporting grid, and writes CSV
files at the requested evaluation times."""

import argparse
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import ERst as OpmRestart
from opm.io.ecl import ESmry as OpmSummary
from scipy.interpolate import interp1d

from pofff.utils.terminal import cli_error_value, pofff_error

SECONDS_IN_DAY = 86400.0
GAS_DEN_REF = 1.86843
WAT_DEN_REF = 998.108
KMOL_TO_KG = 44.0
FIP_BOXC = (4, 12, 17, 18)
FIP_DISS_A = (2, 4, 5, 8)
FIP_SEAL_A = (5, 8)
FIP_DISS_B = (3, 6)
FIP_SEAL_B = (6,)

ArrayLike = float | NDArray


@dataclass(slots=True)
class SimulationContext:
    """Store simulation files, time grids, and OPM grid metadata.

    The object is initialized from command-line selections. OPM handles, report
    times, active-cell indices, pore volumes, and grid dimensions are populated
    after the current simulation base name is located.

    Attributes
    ----------
    resolution
        Numbers of benchmark reporting cells in x and z order.
    dense_t
        Requested dense-output times in seconds.
    maps
        Path to the NumPy mapping from reporting cells to simulation cells.
    where
        Directory containing simulation files and receiving generated CSV data.
    sparse_t
        Uniform sparse-output interval in seconds.
    dims
        FluidFlower dimensions in x, y, and z order, in metres.
    sim
        Simulation base path without an OPM file extension.
    unrst
        Open OPM restart result, or ``None`` before results are loaded.
    ini
        Open OPM initialization result, or ``None`` before results are loaded.
    egrid
        Open OPM grid result, or ``None`` before results are loaded.
    smspec
        Open OPM summary result, or ``None`` before results are loaded.
    times
        Restart times relative to the start of CO2 injection, in seconds.
    times_summary
        Summary times relative to the start of CO2 injection, in seconds.
    time_initial
        Absolute simulator time at the start of CO2 injection, in seconds.
    porv
        Pore volumes in global cell order.
    actind
        Global indices of cells with positive pore volume.
    gxyz
        Simulation-grid dimensions in x, y, and z order.
    norst
        Number of restart report steps."""

    resolution: NDArray
    dense_t: NDArray
    maps: Path
    where: Path = Path(".")
    sparse_t: float = 600.0
    dims: NDArray = field(default_factory=lambda: np.array([2.8, 1.0, 1.2]))
    sim: Path | None = None
    unrst: OpmRestart | None = None
    ini: OpmFile | None = None
    egrid: OpmGrid | None = None
    smspec: OpmSummary | None = None
    times: list[float] = field(default_factory=list)
    times_summary: NDArray | None = None
    time_initial: float = 0.0
    porv: NDArray | None = None
    actind: NDArray | None = None
    gxyz: tuple[int, int, int] | None = None
    norst: int | None = None


@dataclass(slots=True)
class SparseResults:
    """Store sparse FluidFlower quantities before writing the time series.

    The state is initialized by :func:`_initialize_sparse_results` with the uniform
    time grid, region identifiers, and cell dimensions. Pressure, mobile, immobile,
    dissolved, seal, and migration quantities are then populated from OPM summary
    and restart results and interpolated to ``times_data``.

    Attributes
    ----------
    ctx
        Shared simulation context and OPM file handles.
    times_data
        Uniform sparse-output times in seconds.
    fipnum
        FIPNUM values in global cell order.
    dx, dz
        Cell dimensions in x and z order, in metres.
    pop1, pop2
        Pressure time series at the two observation points, in pascals.
    moba, imma, dissa, seala
        Mobile, immobile, dissolved, and seal CO2 masses in box A, in kilograms.
    mobb, immb, dissb, sealb
        Mobile, immobile, dissolved, and seal CO2 masses in box B, in kilograms.
    sealt
        Total CO2 mass in the seal regions, in kilograms.
    m_c_series
        Mass-center migration values calculated at restart times.
    m_c
        Mass-center migration values interpolated to ``times_data``, in metres."""

    ctx: SimulationContext
    times_data: NDArray = field(default_factory=lambda: np.empty(0))
    fipnum: NDArray = field(default_factory=lambda: np.empty(0))
    dx: NDArray = field(default_factory=lambda: np.empty(0))
    dz: NDArray = field(default_factory=lambda: np.empty(0))
    pop1: NDArray = field(default_factory=lambda: np.empty(0))
    pop2: NDArray = field(default_factory=lambda: np.empty(0))
    moba: NDArray = field(default_factory=lambda: np.empty(0))
    imma: NDArray = field(default_factory=lambda: np.empty(0))
    dissa: NDArray = field(default_factory=lambda: np.empty(0))
    seala: NDArray = field(default_factory=lambda: np.empty(0))
    mobb: NDArray = field(default_factory=lambda: np.empty(0))
    immb: NDArray = field(default_factory=lambda: np.empty(0))
    dissb: NDArray = field(default_factory=lambda: np.empty(0))
    sealb: NDArray = field(default_factory=lambda: np.empty(0))
    sealt: NDArray = field(default_factory=lambda: np.empty(0))
    m_c_series: list[float] = field(default_factory=list)
    m_c: NDArray | None = None


def main(argv: list[str] | None = None) -> None:
    """Generate sparse time-series and dense spatial benchmark data.

    Parse reporting-grid settings, locate the OPM simulation, load its results, and
    write the benchmark time-series and spatial-map CSV files.

    Parameters
    ----------
    argv : list[str] | None, optional
        Arguments to parse instead of ``sys.argv[1:]``."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Benchmark postprocessing",
    )
    parser.add_argument("-r", "--resolution", default="280,120")
    parser.add_argument("-t", "--time", default="24,48,72,96,120")
    parser.add_argument("-m", "--maps", default="cellmap.npy")
    args = vars(parser.parse_args(argv))

    if Path("NOMONOTONIC").exists():
        sys.exit(1)

    ctx = SimulationContext(
        resolution=np.fromstring(args["resolution"], sep=",", dtype=int),
        dense_t=np.fromstring(args["time"], sep=",") * 3600.0,
        maps=Path(args["maps"]),
    )

    ctx.sim = _find_simulation_base(ctx.where)
    _read_opm_results(ctx)
    _write_sparse_outputs(ctx)
    _write_dense_outputs(ctx)


def _find_simulation_base(path: Path) -> Path:
    """Locate the simulation base name from an OPM restart file.

    Parameters
    ----------
    path : Path
        Directory to search for a ``.UNRST`` file.

    Returns
    -------
    Path
        Restart-file path without its extension.

    Raises
    ------
    SystemExit
        If the directory contains no ``.UNRST`` result."""
    for f in path.iterdir():
        if f.suffix == ".UNRST":
            return f.with_suffix("")
    pofff_error(
        f"no {cli_error_value('.UNRST')} simulation result was found in "
        f"{cli_error_value(str(path))}."
    )


def _read_opm_results(ctx: SimulationContext) -> None:
    """Load OPM restart, initialization, grid, and summary results.

    Populate OPM handles, injection-relative times, pore volumes, active-cell
    indices, and grid dimensions on ``ctx``.

    Parameters
    ----------
    ctx : SimulationContext
        Mutable simulation context with an initialized simulation base path."""
    assert ctx.sim
    ctx.unrst = OpmRestart(f"{ctx.sim}.UNRST")

    t0: float | None = None
    for i in range(len(ctx.unrst.report_steps)):
        t = SECONDS_IN_DAY * float(ctx.unrst["DOUBHEAD", i][0])

        if t0 is None and np.any(ctx.unrst["RSW", i] > 0):
            t0 = SECONDS_IN_DAY * float(ctx.unrst["DOUBHEAD", i - 1][0])
            ctx.times.append(0.0)

        if t0 is not None:
            ctx.times.append(t - t0)

    ctx.time_initial = t0 or 0.0

    ini = OpmFile(f"{ctx.sim}.INIT")
    egrid = OpmGrid(f"{ctx.sim}.EGRID")
    smspec = OpmSummary(f"{ctx.sim}.SMSPEC")
    ctx.ini = ini
    ctx.egrid = egrid
    ctx.smspec = smspec

    porv = np.asarray(ini["PORV"])
    ctx.porv = porv
    ctx.actind = np.flatnonzero(porv > 0)

    ctx.times_summary = np.r_[0.0, smspec["TIME"] * SECONDS_IN_DAY]
    ctx.gxyz = tuple(egrid.dimension)
    ctx.norst = len(ctx.unrst.report_steps)


def _initialize_sparse_results(ctx: SimulationContext) -> SparseResults:
    """Initialize sparse time coordinates and OPM cell-property arrays.

    Parameters
    ----------
    ctx : SimulationContext
        Loaded simulation context with initialization data and restart times.

    Returns
    -------
    SparseResults
        Sparse state initialized with times, FIPNUM, DX, and DZ arrays.

    Raises
    ------
    SystemExit
        If initialization data or restart times are unavailable."""
    ini = ctx.ini
    if ini is None:
        pofff_error("OPM initialization data are unavailable for sparse processing.")
    if not ctx.times:
        pofff_error("no restart times are available for sparse processing.")
    return SparseResults(
        ctx=ctx,
        times_data=np.arange(0.0, ctx.times[-1] + ctx.sparse_t, ctx.sparse_t),
        fipnum=np.asarray(ini["FIPNUM"]),
        dx=np.asarray(ini["DX"]),
        dz=np.asarray(ini["DZ"]),
    )


def _write_sparse_outputs(ctx: SimulationContext) -> None:
    """Calculate and write the sparse benchmark time series.

    Parameters
    ----------
    ctx : SimulationContext
        Loaded simulation context and OPM results."""
    res = _initialize_sparse_results(ctx)

    _extract_summary_quantities(ctx, res)
    _compute_mass_center_metric(ctx, res)
    _interpolate_sparse_quantities(ctx, res)
    _write_time_series_csv(res)


def _get_initial_water_pressure(
    unrst: OpmRestart,
    fipnum: NDArray,
    region: int,
) -> float:
    """Return the initial water pressure for one FIP region.

    Parameters
    ----------
    unrst : OpmRestart
        Open OPM restart result containing pressure and capillary pressure.
    fipnum : NDArray
        FIPNUM values in global cell order.
    region : int
        FIPNUM identifying the observation-point region.

    Returns
    -------
    float
        Water pressure corrected for capillary pressure, in pascals."""
    index = list(fipnum).index(region)
    pressure = unrst["PRESSURE", 0][index]
    return float((pressure - unrst["PCGW", 0][index]) * 1e5)


def _sum_summary_vectors(
    smry: OpmSummary,
    expressions: Iterable[str],
) -> NDArray:
    """Sum selected OPM summary vectors and convert CO2 to kilograms.

    Parameters
    ----------
    smry : OpmSummary
        Open OPM summary result containing the requested vectors.
    expressions : Iterable[str]
        OPM summary-vector names to add.

    Returns
    -------
    NDArray
        Total mass time series in kilograms."""
    return np.asarray(sum(smry[expression] for expression in expressions)) * KMOL_TO_KG


def _extract_summary_quantities(ctx: SimulationContext, res: SparseResults) -> None:
    """Extract pressures and regional CO2 masses from OPM summary vectors.

    Parameters
    ----------
    ctx : SimulationContext
        Loaded simulation context and OPM summary data.
    res : SparseResults
        Sparse result arrays populated in place.

    Raises
    ------
    SystemExit
        If summary or restart results are unavailable."""
    smry = ctx.smspec
    unrst = ctx.unrst
    if smry is None or unrst is None:
        pofff_error("OPM summary and restart data are required for sparse processing.")
    smry_keys = smry.keys()

    bwpr = sorted(k for k in smry_keys if k.startswith("BWPR") and "," in k)[:2]

    res.pop1 = np.r_[
        _get_initial_water_pressure(unrst, res.fipnum, 8),
        smry[bwpr[0]] * 1e5,
    ]
    res.pop2 = np.r_[
        _get_initial_water_pressure(unrst, res.fipnum, 9),
        smry[bwpr[1]] * 1e5,
    ]

    res.moba = _sum_summary_vectors(smry, (f"RGKDM:{i}" for i in FIP_DISS_A))
    res.imma = _sum_summary_vectors(smry, (f"RGKDI:{i}" for i in FIP_DISS_A))
    res.dissa = _sum_summary_vectors(smry, (f"RWCD:{i}" for i in FIP_DISS_A))

    res.seala = _sum_summary_vectors(
        smry,
        (
            f"{keyword}:{region}"
            for region in FIP_SEAL_A
            for keyword in ("RWCD", "RGKDM", "RGKDI")
        ),
    )

    res.mobb = _sum_summary_vectors(smry, (f"RGKDM:{i}" for i in FIP_DISS_B))
    res.immb = _sum_summary_vectors(smry, (f"RGKDI:{i}" for i in FIP_DISS_B))
    res.dissb = _sum_summary_vectors(smry, (f"RWCD:{i}" for i in FIP_DISS_B))

    res.sealb = _sum_summary_vectors(
        smry,
        (
            f"{keyword}:{region}"
            for region in FIP_SEAL_B
            for keyword in ("RWCD", "RGKDM", "RGKDI")
        ),
    )

    res.sealt = (
        res.seala
        + res.sealb
        + _sum_summary_vectors(
            smry,
            (
                f"{keyword}:{region}"
                for region in (7, 9)
                for keyword in ("RWCD", "RGKDM", "RGKDI")
            ),
        )
    )


def _compute_mass_center_metric(ctx: SimulationContext, res: SparseResults) -> None:
    """Calculate the box-C mass-center migration series.

    Parameters
    ----------
    ctx : SimulationContext
        Loaded simulation context and restart metadata.
    res : SparseResults
        Sparse result state receiving migration values.

    Raises
    ------
    SystemExit
        If restart results or grid metadata are unavailable."""
    unrst = ctx.unrst
    if unrst is None or ctx.gxyz is None or ctx.norst is None:
        pofff_error("OPM restart metadata are required for the mass-center metric.")

    boxc = np.array([fip in FIP_BOXC for fip in res.fipnum])
    nx, ny, _ = ctx.gxyz

    boxc_x = np.roll(boxc, 1)
    boxc_z = np.roll(boxc, -nx * ny)

    for t_n in range(1, ctx.norst):
        rss = np.asarray(unrst["RSW", t_n])
        rssat = np.asarray(unrst["RSWSAT", t_n])

        xcw = rss / (rss + WAT_DEN_REF / GAS_DEN_REF)
        xcw /= rssat / (rssat + WAT_DEN_REF / GAS_DEN_REF)

        mc = np.sum(
            np.abs(xcw[boxc_x] - xcw[boxc]) * res.dz[boxc]
            + np.abs(xcw[boxc_z] - xcw[boxc]) * res.dx[boxc]
        )
        res.m_c_series.append(mc)


def _interpolate_sparse_quantities(ctx: SimulationContext, res: SparseResults) -> None:
    """Interpolate sparse quantities to a uniform time grid.

    Parameters
    ----------
    ctx : SimulationContext
        Simulation and summary time coordinates.
    res : SparseResults
        Sparse quantities replaced by their interpolated arrays."""
    assert ctx.times_summary is not None

    res.m_c = interp1d(
        ctx.times,
        np.r_[0.0, res.m_c_series],
        fill_value="extrapolate",
    )(res.times_data)

    for name in (
        "pop1",
        "pop2",
        "moba",
        "imma",
        "dissa",
        "seala",
        "mobb",
        "immb",
        "dissb",
        "sealb",
        "sealt",
    ):
        data = getattr(res, name)
        x = ctx.times_summary
        y = data if name.startswith("pop") else np.r_[0.0, data]
        setattr(res, name, interp1d(x, y, fill_value="extrapolate")(res.times_data))


def _write_time_series_csv(res: SparseResults) -> None:
    """Write sparse benchmark quantities to ``time_series.csv``.

    Parameters
    ----------
    res : SparseResults
        Interpolated pressure, mass, and migration series."""
    assert res.m_c is not None

    header = (
        "# t [s], p1 [Pa], p2 [Pa], mobA [kg], immA [kg], dissA [kg], "
        "sealA [kg], mobB [kg], immB [kg], dissB [kg], sealB [kg], "
        "MC [m], sealTot [kg]"
    )
    lines = [header]

    for j, t in enumerate(res.times_data[1:]):
        lines.append(
            f"{t:.3e},{res.pop1[j]:.5e},{res.pop2[j]:.5e},"
            f"{res.moba[j]:.3e},{res.imma[j]:.3e},{res.dissa[j]:.3e},"
            f"{res.seala[j]:.3e},{res.mobb[j]:.3e},{res.immb[j]:.3e},"
            f"{res.dissb[j]:.3e},{res.sealb[j]:.3e},"
            f"{res.m_c[j]:.3e},{res.sealt[j]:.3e}"
        )

    Path("time_series.csv").write_text("\n".join(lines), encoding="utf-8")


def _write_dense_outputs(ctx: SimulationContext) -> None:
    """Write spatial maps at the requested dense-output times.

    Map active-cell saturation and dissolved-CO2 concentration to the reporting
    grid and write one CSV file for every requested restart time that is available.

    Parameters
    ----------
    ctx : SimulationContext
        Loaded restart data, reporting-grid resolution, and cell mapping.

    Raises
    ------
    SystemExit
        If restart or initialization data are unavailable."""
    unrst = ctx.unrst
    porv = ctx.porv
    actind = ctx.actind
    if unrst is None or porv is None or actind is None:
        pofff_error(
            "OPM restart and initialization data are required for dense output."
        )

    dx, _, dz = ctx.dims

    refx = 0.5 * (
        np.linspace(0, dx, ctx.resolution[0] + 1)[:-1]
        + np.linspace(0, dx, ctx.resolution[0] + 1)[1:]
    )
    refz = 0.5 * (
        np.linspace(0, dz, ctx.resolution[1] + 1)[:-1]
        + np.linspace(0, dz, ctx.resolution[1] + 1)[1:]
    )

    cell_cent = np.load(ctx.maps).astype(int)

    for t in ctx.dense_t:
        if t not in ctx.times:
            continue
        t_n = ctx.times.index(t)

        sgas = np.abs(unrst["SGAS", t_n])
        rhow = unrst["WAT_DEN", t_n]
        rsw = unrst["RSW", t_n]
        xlco2 = rsw / (rsw + WAT_DEN_REF / GAS_DEN_REF)

        s_full = np.zeros(len(porv))
        c_full = np.zeros(len(porv))
        s_full[actind] = sgas
        c_full[actind] = xlco2 * rhow

        hours = int(t / 3600.0) if t % 3600 == 0 else t / 3600.0
        _write_spatial_map_csv(
            ctx, [refx, refz], s_full[cell_cent], c_full[cell_cent], hours
        )


def _write_spatial_map_csv(
    ctx: SimulationContext,
    refxz: list[NDArray],
    sgas: NDArray,
    cco2: NDArray,
    hours: float,
) -> None:
    """Write one saturation and concentration reporting-grid map.

    Parameters
    ----------
    ctx : SimulationContext
        Output location and reporting-grid resolution.
    refxz : list[NDArray]
        Reporting-cell centre coordinates in x and z order, in metres.
    sgas : NDArray
        Gas saturation in reporting-cell order.
    cco2 : NDArray
        Dissolved-CO2 concentration in reporting-cell order.
    hours : int | float
        Evaluation time in hours used in the output filename."""
    nx, nz = ctx.resolution
    lines = ["x,z,saturation,concentration"]

    for k, z in enumerate(refxz[1]):
        for i, x in enumerate(refxz[0]):
            idx = -nx * (nz - k) + i
            lines.append(f"{x:.3f},{z:.3f},{sgas[idx]:.3f},{cco2[idx]:.3f}")

    (ctx.where / f"spatial_map_{hours}h.csv").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
