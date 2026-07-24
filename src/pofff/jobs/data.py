#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2023-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Write benchmark time-series and spatial (dense) data from OPM simulations."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from opm.io.ecl import EclFile as OpmFile
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import ERst as OpmRestart
from opm.io.ecl import ESmry as OpmSummary
from scipy.interpolate import interp1d

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


@dataclass
class SimulationContext:
    """Simulation-wide state, file handles, and grid information."""

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

    @property
    def nxz(self) -> NDArray:
        """Alias for resolution to preserve original naming."""
        return self.resolution


@dataclass
class SparseResults:
    """Container for sparse (time-series) benchmark quantities."""

    ctx: SimulationContext
    times_data: NDArray = field(init=False)
    fipnum: NDArray = field(init=False)
    dx: NDArray = field(init=False)
    dz: NDArray = field(init=False)
    pop1: NDArray = field(init=False)
    pop2: NDArray = field(init=False)
    moba: NDArray = field(init=False)
    imma: NDArray = field(init=False)
    dissa: NDArray = field(init=False)
    seala: NDArray = field(init=False)
    mobb: NDArray = field(init=False)
    immb: NDArray = field(init=False)
    dissb: NDArray = field(init=False)
    sealb: NDArray = field(init=False)
    sealt: NDArray = field(init=False)
    m_c_series: list[float] = field(default_factory=list)
    m_c: NDArray | None = None

    def __post_init__(self) -> None:
        assert self.ctx.ini
        assert self.ctx.times
        self.times_data = np.arange(
            0.0, self.ctx.times[-1] + self.ctx.sparse_t, self.ctx.sparse_t
        )
        self.fipnum = np.asarray(self.ctx.ini["FIPNUM"])
        self.dx = np.asarray(self.ctx.ini["DX"])
        self.dz = np.asarray(self.ctx.ini["DZ"])


def main(argv=None) -> None:
    """Entry point for benchmark postprocessing."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Benchmark postprocessing",
    )
    parser.add_argument("-r", "--resolution", default="280,120")
    parser.add_argument("-t", "--time", default="24,48,72,96,120")
    parser.add_argument("-m", "--maps", default="cellmap.npy")
    args = vars(parser.parse_known_args(argv)[0])

    if Path("NOMONOTONIC").exists():
        sys.exit(1)

    ctx = SimulationContext(
        resolution=np.fromstring(args["resolution"], sep=",", dtype=int),
        dense_t=np.fromstring(args["time"], sep=",") * 3600.0,
        maps=Path(args["maps"]),
    )

    ctx.sim = find_simulation_base(ctx.where)
    read_opm(ctx)
    sparse_data(ctx)
    dense_data(ctx)


def find_simulation_base(path: Path) -> Path:
    """Locate simulation base name from .UNRST file."""
    for f in path.iterdir():
        if f.suffix == ".UNRST":
            return f.with_suffix("")
    raise FileNotFoundError("No .UNRST file found")


def read_opm(ctx: SimulationContext) -> None:
    """Load OPM restart, grid, and summary data."""
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

    ctx.ini = OpmFile(f"{ctx.sim}.INIT")
    ctx.egrid = OpmGrid(f"{ctx.sim}.EGRID")
    ctx.smspec = OpmSummary(f"{ctx.sim}.SMSPEC")

    ctx.porv = np.asarray(ctx.ini["PORV"])
    ctx.actind = np.flatnonzero(ctx.porv > 0)

    ctx.times_summary = np.r_[0.0, ctx.smspec["TIME"] * SECONDS_IN_DAY]
    ctx.gxyz = tuple(ctx.egrid.dimension)
    ctx.norst = len(ctx.unrst.report_steps)


def sparse_data(ctx: SimulationContext) -> None:
    """Compute and write sparse time-series benchmark data."""
    res = SparseResults(ctx)

    create_from_summary(ctx, res)
    compute_m_c(ctx, res)
    interpolate_sparse(ctx, res)
    write_sparse_data(res)


def create_from_summary(ctx: SimulationContext, res: SparseResults) -> None:
    """Extract sparse quantities from OPM summary vectors."""
    assert ctx.smspec
    smry = ctx.smspec
    smry_keys = smry.keys()

    bwpr = sorted(k for k in smry_keys if k.startswith("BWPR") and "," in k)[:2]

    def initial_pressure(fip: int) -> float:
        assert ctx.unrst
        idx = list(res.fipnum).index(fip)
        p = ctx.unrst["PRESSURE", 0][idx]
        return (p - ctx.unrst["PCGW", 0][idx]) * 1e5

    res.pop1 = np.r_[initial_pressure(8), smry[bwpr[0]] * 1e5]
    res.pop2 = np.r_[initial_pressure(9), smry[bwpr[1]] * 1e5]

    def sum_smry(exprs) -> NDArray:
        return sum(smry[e] for e in exprs) * KMOL_TO_KG

    res.moba = sum_smry(f"RGKDM:{i}" for i in FIP_DISS_A)
    res.imma = sum_smry(f"RGKDI:{i}" for i in FIP_DISS_A)
    res.dissa = sum_smry(f"RWCD:{i}" for i in FIP_DISS_A)

    res.seala = sum_smry(
        f"{k}:{i}" for i in FIP_SEAL_A for k in ("RWCD", "RGKDM", "RGKDI")
    )

    res.mobb = sum_smry(f"RGKDM:{i}" for i in FIP_DISS_B)
    res.immb = sum_smry(f"RGKDI:{i}" for i in FIP_DISS_B)
    res.dissb = sum_smry(f"RWCD:{i}" for i in FIP_DISS_B)

    res.sealb = sum_smry(
        f"{k}:{i}" for i in FIP_SEAL_B for k in ("RWCD", "RGKDM", "RGKDI")
    )

    res.sealt = (
        res.seala
        + res.sealb
        + sum_smry(f"{k}:{i}" for i in (7, 9) for k in ("RWCD", "RGKDM", "RGKDI"))
    )


def compute_m_c(ctx: SimulationContext, res: SparseResults) -> None:
    """Compute mass-center migration metric."""
    assert ctx.unrst
    assert ctx.gxyz
    assert ctx.norst

    boxc = np.array([fip in FIP_BOXC for fip in res.fipnum])
    nx, ny, _ = ctx.gxyz

    boxc_x = np.roll(boxc, 1)
    boxc_z = np.roll(boxc, -nx * ny)

    for t_n in range(1, ctx.norst):
        rss = np.asarray(ctx.unrst["RSW", t_n])
        rssat = np.asarray(ctx.unrst["RSWSAT", t_n])

        xcw = rss / (rss + WAT_DEN_REF / GAS_DEN_REF)
        xcw /= rssat / (rssat + WAT_DEN_REF / GAS_DEN_REF)

        mc = np.sum(
            np.abs(xcw[boxc_x] - xcw[boxc]) * res.dz[boxc]
            + np.abs(xcw[boxc_z] - xcw[boxc]) * res.dx[boxc]
        )
        res.m_c_series.append(mc)


def interpolate_sparse(ctx: SimulationContext, res: SparseResults) -> None:
    """Interpolate sparse quantities onto uniform time grid."""
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


def write_sparse_data(res: SparseResults) -> None:
    """Write sparse time-series values to CSV."""
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


def dense_data(ctx: SimulationContext) -> None:
    """Write spatial maps for selected dense output times."""
    assert ctx.unrst
    assert ctx.porv is not None
    assert ctx.actind is not None

    dx, _, dz = ctx.dims

    refx = 0.5 * (
        np.linspace(0, dx, ctx.nxz[0] + 1)[:-1] + np.linspace(0, dx, ctx.nxz[0] + 1)[1:]
    )
    refz = 0.5 * (
        np.linspace(0, dz, ctx.nxz[1] + 1)[:-1] + np.linspace(0, dz, ctx.nxz[1] + 1)[1:]
    )

    cell_cent = np.load(ctx.maps).astype(int)

    for t in ctx.dense_t:
        if t not in ctx.times:
            continue
        t_n = ctx.times.index(t)

        sgas = np.abs(ctx.unrst["SGAS", t_n])
        rhow = ctx.unrst["WAT_DEN", t_n]
        rsw = ctx.unrst["RSW", t_n]
        xlco2 = rsw / (rsw + WAT_DEN_REF / GAS_DEN_REF)

        s_full = np.zeros(len(ctx.porv))
        c_full = np.zeros(len(ctx.porv))
        s_full[ctx.actind] = sgas
        c_full[ctx.actind] = xlco2 * rhow

        hours = int(t / 3600.0) if t % 3600 == 0 else t / 3600.0
        write_dense_data(ctx, [refx, refz], s_full[cell_cent], c_full[cell_cent], hours)


def write_dense_data(ctx: SimulationContext, refxz, sgas, cco2, hours) -> None:
    """Write single spatial map CSV."""
    nx, nz = ctx.nxz
    lines = ["x,z,saturation,concentration"]

    for k, z in enumerate(refxz[1]):
        for i, x in enumerate(refxz[0]):
            idx = -nx * (nz - k) + i
            lines.append(f"{x:.3f},{z:.3f},{sgas[idx]:.3f},{cco2[idx]:.3f}")

    (ctx.where / f"spatial_map_{hours}h.csv").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
