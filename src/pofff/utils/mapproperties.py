# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0913, R0914, R0917, E1102

"""Generate FluidFlower grids and assign spatial model properties.

The module builds Cartesian, tensor, and corner-point grids; reads geological
points, horizons, and facies polygons; applies thickness maps; locates sensors
and injection sources; classifies reporting boxes; and writes mappings from the
simulation grid to the benchmark reporting grid."""

import csv
import shutil
import sys
from contextlib import nullcontext
from pathlib import Path
from typing import Any

import numpy as np
from alive_progress import alive_bar
from numpy.typing import NDArray
from shapely.geometry import Point, Polygon

from pofff.config.config import PofffConfig
from pofff.utils.writefile import create_corner_point_grid


def grid_and_properties(cfg: PofffConfig) -> None:
    """Generate the selected grid and assign spatial model properties.

    The function updates grid dimensions, generated OPM arrays, sensor and source
    indices, and the benchmark cell map on ``cfg``.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state."""
    polygons, points = _read_geological_polygons(cfg)
    if cfg.grid == "corner-point":
        xyz, xcoord, zcoord = _build_corner_point_coordinates(cfg, points)
        _assign_spatial_properties(cfg, polygons, xyz=xyz, xcoord=xcoord, zcoord=zcoord)
        return
    dims = np.asarray(cfg.dims, float)
    if cfg.grid == "cartesian":
        xvert = np.linspace(0, dims[0], cfg.nxz[0] + 1)
        zvert = np.linspace(0, dims[2], cfg.nxz[1] + 1)
    else:
        xvert = _tensor(cfg.x, dims[0])
        zvert = _tensor(cfg.z, dims[2])
        cfg.nxz = [len(xvert) - 1, len(zvert) - 1]
    xcent = 0.5 * (xvert[:-1] + xvert[1:])
    zcent = 0.5 * (zvert[:-1] + zvert[1:])
    cfg.dx = list(xvert[1:] - xvert[:-1])
    cfg.dz = list(zvert[1:] - zvert[:-1])
    _assign_spatial_properties(cfg, polygons, xcent=xcent, zcent=zcent)
    if cfg.grid == "tensor":
        cfg.dx = list(map(str, xvert[1:] - xvert[:-1]))
        dz = list(map(str, zvert[1:] - zvert[:-1]))
        cfg.dz = [dz[0]] * cfg.nxz[0]
        for i in range(cfg.nxz[1] - 1):
            cfg.dx.extend(cfg.dx[-cfg.nxz[0] :])
            cfg.dz.extend([dz[i + 1]] * cfg.nxz[0])


def _tensor(parts: list[int], dimension: float) -> NDArray[np.float64]:
    """Construct tensor-grid edges from per-region refinement counts.

    Divide the physical dimension into equally sized regions, then subdivide
    each region according to its corresponding refinement count.

    Parameters
    ----------
    parts : list[int]
        Positive numbers of cells assigned to consecutive equal-sized regions.
    dimension : float
        Total physical length of the grid axis, in metres.

    Returns
    -------
    NDArray[np.float64]
        Ordered grid-edge coordinates from zero through ``dimension``, in
        metres.
    """
    return np.concatenate(
        [
            np.linspace(
                index * dimension / len(parts),
                (index + 1) * dimension / len(parts),
                cells + 1,
                endpoint=True,
            )[:-1]
            for index, cells in enumerate(parts)
        ]
        + [np.array([dimension], dtype=np.float64)]
    )


def _build_corner_point_coordinates(
    cfg: PofffConfig,
    points: list[list[float]],
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Build refined corner-point coordinates and cell centroids.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    points : list[list[float]]
        Geological points represented by x and z coordinates in metres.

    Returns
    -------
    tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]
        Cell centroids followed by refined corner x and z coordinates."""
    horizonts = _read_horizon_lines(cfg, points)
    xvert = np.concatenate(
        [
            np.linspace(
                i * cfg.dims[0] / len(cfg.x),
                (i + 1) * cfg.dims[0] / len(cfg.x),
                n + 1,
                endpoint=True,
            )[:-1]
            for i, n in enumerate(cfg.x)
        ]
        + [np.array([cfg.dims[0]])]
    )
    xcoor, zcoor = [], []
    for x in xvert:
        for layer in horizonts:
            xs = np.array([p[0] for p in layer])
            zs = np.array([p[1] for p in layer])
            i = np.argmin(np.abs(xs - x))
            if i == 0:
                z = zs[0] + (zs[1] - zs[0]) / (xs[1] - xs[0]) * (x - xs[0])
            elif i == len(xs) - 1:
                z = zs[i - 1] + (zs[i] - zs[i - 1]) / (xs[i] - xs[i - 1]) * (
                    x - xs[i - 1]
                )
            elif xs[i] < x:
                z = zs[i] + (zs[i + 1] - zs[i]) / (xs[i + 1] - xs[i]) * (x - xs[i])
            else:
                z = zs[i - 1] + (zs[i] - zs[i - 1]) / (xs[i] - xs[i - 1]) * (
                    x - xs[i - 1]
                )
            xcoor.append(x)
            zcoor.append(z)
    xcoord, zcoord = np.asarray(xcoor), np.asarray(zcoor)

    stride = len(cfg.z) + 1
    cfg.nxz[0] = len(xcoord) // stride - 1
    cfg.nxz[1] = stride - 1

    xcoord, zcoord, cfg.nxz[0], cfg.nxz[1] = _refine_vertical_coordinates(
        xcoord, zcoord, cfg.nxz[1], np.array(cfg.z)
    )

    xyz = np.zeros((cfg.nxz[0] * cfg.nxz[1], 3))
    stride = cfg.nxz[1] + 1
    idx = 0

    for k in range(cfg.nxz[1]):
        for o in range(cfg.nxz[0]):
            n = o * stride + k
            m = (o + 1) * stride + k

            x = np.array([xcoord[n], xcoord[m], xcoord[m + 1], xcoord[n + 1]])
            z = np.array([zcoord[n], zcoord[m], zcoord[m + 1], zcoord[n + 1]])

            a = x * np.roll(z, -1) - np.roll(x, -1) * z
            area = 0.5 * np.sum(a)

            if abs(area) > 1e-12:
                cx = np.sum((x + np.roll(x, -1)) * a) / (6 * area)
                cz = np.sum((z + np.roll(z, -1)) * a) / (6 * area)
            else:
                cx, cz = np.mean(x), np.mean(z)

            xyz[idx] = [cx, 0.0, cz]
            idx += 1

    return xyz, xcoord, zcoord


def _load_thickness_map(cfg: PofffConfig) -> tuple[float, NDArray, NDArray, NDArray]:
    """Load the selected FluidFlower thickness map and multipliers.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.

    Returns
    -------
    tuple[float, NDArray, NDArray, NDArray]
        Minimum thickness, map x and z coordinates, and normalized multipliers."""
    geology = cfg.path / "geology"

    if cfg.thickness == "final":
        thickness = np.load(geology / "final_thickness.npy")
        ydim = float(np.min(thickness))
        mult = cfg.mult_thickness * thickness.reshape(-1) / np.min(thickness)

        refx = np.arange(0, 2.8 + 5.0e-3, 1.0e-2)
        refz = 1.5 - np.arange(0, 1.5 + 5.0e-3, 1.0e-2)
        refx = 0.5 * (refx[1:] + refx[:-1])
        refz = 0.5 * (refz[1:] + refz[:-1])
        x, z = np.meshgrid(refx, refz, indexing="xy")

        return ydim, x.ravel(), z.ravel(), mult

    thickness = np.genfromtxt(geology / "initial_thickness.csv", delimiter=",")
    return (
        float(np.min(thickness[:, 1])),
        thickness[:, 0] - 0.03,
        1.34 - thickness[:, 2],
        cfg.mult_thickness * thickness[:, 1] / np.min(thickness[:, 1]),
    )


def _assign_structured_grid_properties(
    cfg: PofffConfig,
    xcent: NDArray[np.float64],
    zcent: NDArray[np.float64],
    polygons: list[Polygon],
) -> None:
    """Assign properties and feature indices on a structured grid.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    xcent : NDArray[np.float64]
        Cell-centre x coordinates in metres.
    zcent : NDArray[np.float64]
        Cell-centre z coordinates in metres.
    polygons : list[Polygon]
        FluidFlower facies polygons in model coordinates."""
    nx, nz = cfg.nxz
    x = np.tile(xcent, nz)
    z = np.repeat(zcent, nx)
    ztop = cfg.dims[2] - z

    flux = np.full(len(x), -1)

    if cfg.thickness in {"initial", "final"}:
        cfg.dims[1], xth, zth, mult = _load_thickness_map(cfg)
    else:
        cfg.dims[1] = float(cfg.thickness)
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(len(x), bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for i, (xi, zi) in enumerate(zip(x, z)):
            if show_progress:
                bar_animation()
            pt = Point(xi, zi)
            for j, poly in enumerate(polygons):
                if poly.contains(pt):
                    flux[i] = cfg.facies[j]
                    break

            if cfg.thickness in {"initial", "final"}:
                idx = np.argmin((xth - xi) ** 2 + (zth - (cfg.dims[2] - zi)) ** 2)
                cfg.multpv.append(str(mult[idx]))

    cfg.fluxnum = flux.astype(str).tolist()
    cfg.fipnum = _classify_reporting_boxes(cfg, x, ztop, cfg.fluxnum)

    s1, s2 = _locate_structured_sensors(cfg, xcent, zcent)
    cfg.fipnum[s1], cfg.fipnum[s2] = "8", "9"

    _locate_structured_sources(cfg, xcent, zcent)

    if cfg.hascellmaps:
        _write_cell_map(cfg, x.tolist(), ztop.tolist())
    else:
        shutil.copy(cfg.path / "geology/cellmap.npy", cfg.deck)


def _assign_corner_point_properties(
    cfg: PofffConfig,
    xyz: NDArray[np.float64],
    polygons: list[Polygon],
    xcoord: NDArray[np.float64],
    zcoord: NDArray[np.float64],
) -> None:
    """Assign properties and feature indices on a corner-point grid.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    xyz : NDArray[np.float64]
        Cell-centroid coordinates with columns x, y, and z.
    polygons : list[Polygon]
        FluidFlower facies polygons in model coordinates.
    xcoord : NDArray[np.float64]
        Corner-point x coordinates arranged by pillar and vertical interface.
    zcoord : NDArray[np.float64]
        Corner-point z coordinates arranged by pillar and vertical interface."""
    x = xyz[:, 0]
    ztop = cfg.dims[2] - xyz[:, 2]

    if cfg.thickness in {"initial", "final"}:
        cfg.dims[1], xth, zth, mult = _load_thickness_map(cfg)
    else:
        cfg.dims[1] = float(cfg.thickness)

    flux = np.full(len(x), -1)
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(len(x), bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for i, (xi, zi) in enumerate(zip(x, ztop)):
            if show_progress:
                bar_animation()
            pt = Point(xi, cfg.dims[2] - zi)
            for j, poly in enumerate(polygons):
                if poly.contains(pt):
                    flux[i] = cfg.facies[j]
                    break

            if cfg.thickness in {"initial", "final"}:
                idx = np.argmin((xth - xi) ** 2 + (zth - zi) ** 2)
                cfg.multpv.append(str(mult[idx]))

    cfg.fluxnum = flux.astype(str).tolist()
    cfg.fipnum = _classify_reporting_boxes(cfg, x, ztop, cfg.fluxnum)

    s1, s2 = _locate_corner_point_sensors(cfg, x, ztop)
    cfg.fipnum[s1], cfg.fipnum[s2] = "8", "9"

    _locate_corner_point_sources(cfg, x, ztop)

    if cfg.hascellmaps:
        _write_cell_map(cfg, x.tolist(), ztop.tolist())
    else:
        shutil.copy(cfg.path / "geology/cellmap.npy", cfg.deck)

    create_corner_point_grid(cfg, xcoord, zcoord)


def _assign_spatial_properties(
    cfg: PofffConfig,
    polygons: list[Polygon],
    xcent: NDArray[np.float64] | None = None,
    zcent: NDArray[np.float64] | None = None,
    xyz: NDArray[np.float64] | None = None,
    xcoord: NDArray[np.float64] | None = None,
    zcoord: NDArray[np.float64] | None = None,
) -> None:
    """Dispatch property assignment for the selected grid representation.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    polygons : list[Polygon]
        FluidFlower facies polygons in model coordinates.
    xcent : NDArray[np.float64] | None, optional
        Cell-centre x coordinates in metres.
    zcent : NDArray[np.float64] | None, optional
        Cell-centre z coordinates in metres.
    xyz : NDArray[np.float64] | None, optional
        Cell-centroid coordinates with columns x, y, and z.
    xcoord : NDArray[np.float64] | None, optional
        Corner-point x coordinates arranged by pillar and vertical interface.
    zcoord : NDArray[np.float64] | None, optional
        Corner-point z coordinates arranged by pillar and vertical interface."""
    if cfg.grid == "corner-point":
        assert xyz is not None
        assert xcoord is not None
        assert zcoord is not None
        _assign_corner_point_properties(cfg, xyz, polygons, xcoord, zcoord)
    else:
        assert xcent is not None
        assert zcent is not None
        _assign_structured_grid_properties(cfg, xcent, zcent, polygons)


def _locate_structured_sensors(
    cfg: PofffConfig, xcent: NDArray[np.float64], zcent: NDArray[np.float64]
) -> tuple[int, int]:
    """Locate both observation sensors on a structured grid.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    xcent : NDArray[np.float64]
        Cell-centre x coordinates in metres.
    zcent : NDArray[np.float64]
        Cell-centre z coordinates in metres.

    Returns
    -------
    tuple[int, int]
        Global zero-based indices of the two sensor cells."""
    sx1, sz1 = cfg.sensors[0]
    sx2, sz2 = cfg.sensors[1]
    dimz = cfg.dims[2]

    d1, d2 = [], []

    for k in range(cfg.nxz[1]):
        for i in range(cfg.nxz[0]):
            d1.append((xcent[i] - sx1) ** 2 + (zcent[k] + sz1 - dimz) ** 2)
            d2.append((xcent[i] - sx2) ** 2 + (zcent[k] + sz2 - dimz) ** 2)

    i1, i2 = int(np.argmin(d1)), int(np.argmin(d2))

    for j, s in enumerate(cfg.sensors):
        cfg.sensor_ik[j] = [
            int(np.argmin(np.abs(xcent - s[0]))),
            int(np.argmin(np.abs(dimz - s[1] - zcent))),
        ]

    return i1, i2


def _locate_structured_sources(
    cfg: PofffConfig, xcent: NDArray[np.float64], zcent: NDArray[np.float64]
) -> None:
    """Locate both injection sources on a structured grid.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    xcent : NDArray[np.float64]
        Cell-centre x coordinates in metres.
    zcent : NDArray[np.float64]
        Cell-centre z coordinates in metres."""
    for i, w in enumerate(cfg.sources):
        cfg.source_ik[i] = [
            int(np.argmin(np.abs(xcent - w[0]))) + 1,
            int(np.argmin(np.abs(cfg.dims[2] - w[1] - zcent))) + 1,
        ]


def _locate_corner_point_sensors(
    cfg: PofffConfig, x: NDArray[np.float64], ztop: NDArray[np.float64]
) -> tuple[int, int]:
    """Locate both observation sensors on a corner-point grid.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    x : NDArray[np.float64]
        Cell or plotting x coordinates in metres.
    ztop : NDArray[np.float64]
        Cell-centre depth coordinates measured from the model top.

    Returns
    -------
    tuple[int, int]
        Global zero-based indices of the two sensor cells."""
    coords = np.column_stack((x, ztop))
    sensors = np.array(cfg.sensors)
    d = ((coords[:, None] - sensors) ** 2).sum(axis=2)

    s1, s2 = int(np.argmin(d[:, 0])), int(np.argmin(d[:, 1]))
    nx = cfg.nxz[0]

    cfg.sensor_ik[0] = [s1 % nx, s1 // nx]
    cfg.sensor_ik[1] = [s2 % nx, s2 // nx]

    return s1, s2


def _locate_corner_point_sources(
    cfg: PofffConfig, x: NDArray[np.float64], ztop: NDArray[np.float64]
) -> None:
    """Locate both injection sources on a corner-point grid.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    x : NDArray[np.float64]
        Cell or plotting x coordinates in metres.
    ztop : NDArray[np.float64]
        Cell-centre depth coordinates measured from the model top."""
    coords = np.column_stack((x, ztop))
    wells = np.array(cfg.sources)
    d = ((coords[:, None] - wells) ** 2).sum(axis=2)

    for i in range(2):
        idx = np.argmin(d[:, i])
        cfg.source_ik[i] = [
            int(idx % cfg.nxz[0] + 1),
            int(idx // cfg.nxz[0] + 1),
        ]


def _assign_box_region(
    bounds: list[list[float]],
    sand_region: str,
    other_region: str,
    x: NDArray[np.float64],
    z: NDArray[np.float64],
    fluxnum: NDArray[Any],
    fipnum: NDArray[Any],
) -> None:
    """Assign FIPNUM values inside one benchmark reporting box.

    Cells belonging to facies 1 receive ``sand_region``. All other cells
    inside the box receive ``other_region``. The ``fipnum`` array is modified
    in place.

    Parameters
    ----------
    bounds : list[list[float]]
        Lower-left and upper-right box corners as
        ``[[xmin, zmin], [xmax, zmax]]`` in metres.
    sand_region : str
        FIPNUM assigned to cells in facies 1.
    other_region : str
        FIPNUM assigned to all other facies inside the box.
    x : NDArray[np.float64]
        Cell-centre x coordinates in global cell order, in metres.
    z : NDArray[np.float64]
        Cell-centre z coordinates in global cell order, in metres.
    fluxnum : list[str]
        Facies identifiers in global cell order.
    fipnum : list[str]
        FIPNUM values in global cell order, modified in place.
    """
    inside = (
        (x >= bounds[0][0])
        & (x <= bounds[1][0])
        & (z >= bounds[0][1])
        & (z <= bounds[1][1])
    )
    unassigned = inside & (fipnum == "1")
    fipnum[unassigned & (fluxnum == "1")] = sand_region
    fipnum[unassigned & (fluxnum != "1")] = other_region


def _classify_reporting_boxes(
    cfg: PofffConfig,
    x: NDArray[np.float64],
    z: NDArray[np.float64],
    flux: list[str],
) -> list[str]:
    """Assign benchmark reporting-region FIPNUM values.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    x : NDArray[np.float64]
        Cell or plotting x coordinates in metres.
    z : NDArray[np.float64]
        Cell or plotting z coordinates in metres.
    flux : list[str]
        Facies identifiers in global cell order.

    Returns
    -------
    list[str]
        FIPNUM values in global cell order."""
    x, z, flux0 = map(np.asarray, (x, z, flux))
    fip = np.full(len(x), "1", dtype=object)

    _assign_box_region(cfg.boxb, "6", "3", x, z, flux0, fip)
    _assign_box_region(cfg.boxc, "12", "4", x, z, flux0, fip)
    _assign_box_region(cfg.boxa, "5", "2", x, z, flux0, fip)

    fip[(flux0 == "1") & (fip == "1")] = "7"
    return fip.tolist()


def _write_cell_map(
    cfg: PofffConfig, simxcent: NDArray[np.float64], simzcent: NDArray[np.float64]
) -> None:
    """Map benchmark reporting cells to their nearest simulation cells.

    The mapping is written as ``cellmap.npy`` below ``cfg.deck``.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    simxcent : NDArray[np.float64]
        Simulation-cell x coordinates in global cell order.
    simzcent : NDArray[np.float64]
        Simulation-cell z coordinates in global cell order."""
    refx = np.arange(0, 2.8 + 5.0e-3, 1.0e-2)
    refz = np.arange(0, 1.2 + 5.0e-3, 1.0e-2)
    refx = 0.5 * (refx[1:] + refx[:-1])
    refz = 0.5 * (refz[1:] + refz[:-1])

    x, z = np.meshgrid(refx, refz, indexing="xy")
    ref = np.column_stack((x.ravel(), z.ravel()))
    sim = np.column_stack((simxcent, simzcent))

    d = np.abs(sim[:, None] - ref).sum(axis=2)
    np.save(Path(cfg.deck) / "cellmap.npy", np.argmin(d, axis=0))


def _read_horizon_lines(
    cfg: PofffConfig, points: list[list[float]]
) -> list[list[list[float]]]:
    """Read and order geological horizon polylines.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.
    points : list[list[float]]
        Geological points represented by x and z coordinates in metres.

    Returns
    -------
    list[list[list[float]]]
        Geological horizons ordered from bottom to top."""
    horizonts: list[list[list[float]]] = []
    with open(cfg.path / "geology/horizonts.geo", encoding="utf8") as file:
        for r in csv.reader(file, delimiter=" "):
            if r[0].startswith("Line"):
                if not horizonts[-1]:
                    horizonts[-1].append(points[int(r[2][1:-1]) - 1])
                horizonts[-1].append(points[int(r[3][:-2]) - 1])
            if len(r) > 1 and r[1] == "Horizont":
                horizonts.append([])
    return horizonts[::-1]


def _read_geological_polygons(
    cfg: PofffConfig,
) -> tuple[list[Polygon], list[list[float]]]:
    """Read geological points, line connectivity, and facies polygons.

    Parameters
    ----------
    cfg : PofffConfig
        Shared pofff configuration and derived runtime state.

    Returns
    -------
    tuple[list[Polygon], list[list[float]]]
        Facies polygons and the geological point coordinates."""
    polygons, points, lines, curves, facie = [], [], [], [], 0
    h_ref, l_ref = 1.5 / 1490, 2.8 / 2594

    with open(cfg.path / "geology/points.geo", encoding="utf8") as file:
        for r in csv.reader(file, delimiter=" "):
            if r[0].startswith("Point"):
                points.append(
                    [l_ref * float(r[2][1:-1]), cfg.dims[2] - h_ref * float(r[3][:-1])]
                )

    with open(cfg.path / "geology/lines.geo", encoding="utf8") as file:
        for r in csv.reader(file, delimiter=" "):
            if r[0].startswith("Line"):
                lines.append([int(r[2][1:-1]), int(r[3][:-2])])

    with open(cfg.path / "geology/polygons.geo", encoding="utf8") as file:
        for r in csv.reader(file, delimiter=" "):
            if r[0] == "Curve":
                cfg.facies.append(facie)
                curve = []
                for t in r[3:]:
                    t = t.strip(",;{}")
                    if t:
                        curve.append(int(t))
                curves.append(curve)
            if len(r) > 1 and r[1] in {"Sand", "Water"}:
                facie += 1

    for c in curves:
        poly = []
        for lid in c:
            idx = 0 if lid < 0 else 1
            poly.append(points[lines[abs(lid) - 1][idx] - 1])
        poly.append(poly[0])
        polygons.append(Polygon(poly))

    return polygons, points


def _refine_vertical_coordinates(
    xci: NDArray[np.float64],
    zci: NDArray[np.float64],
    ncz: int,
    znr: NDArray[np.float64],
) -> tuple[NDArray[np.float64], NDArray[np.float64], int, int]:
    """Subdivide geological layers by their vertical refinement factors.

    Parameters
    ----------
    xci : NDArray[np.float64]
        Unrefined corner-point x coordinates.
    zci : NDArray[np.float64]
        Unrefined corner-point z coordinates.
    ncz : int
        Number of unrefined vertical cells.
    znr : NDArray[np.float64]
        Vertical refinement factor for each geological layer.

    Returns
    -------
    tuple[NDArray[np.float64], NDArray[np.float64], int, int]
        Refined x and z coordinates and the new x and z cell counts."""
    stride = ncz + 1
    ncols = len(xci) // stride

    xcr, zcr = [], []

    for j in range(ncols):
        b = j * stride
        xcr.append(xci[b])
        zcr.append(zci[b])
        for i in range(ncz):
            w = np.arange(1.0 / znr[i], 1.0 + 1.0 / znr[i], 1.0 / znr[i])
            xcr.extend(xci[b + i] + (xci[b + i + 1] - xci[b + i]) * w)
            zcr.extend(zci[b + i] + (zci[b + i + 1] - zci[b + i]) * w)

    ncx_new = ncols - 1
    ncz_new = np.where(zcr == zcr[-1])[0][0]

    return np.asarray(xcr), np.asarray(zcr), ncx_new, ncz_new
