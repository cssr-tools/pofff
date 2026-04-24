# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0913, R0914, R0917, E1102

"""
Utility functions for grid generation and spatial indexing
in geological FluidFlower-style models.
"""

import csv
import shutil
from pathlib import Path
import numpy as np
from shapely.geometry import Point, Polygon
from alive_progress import alive_bar

from pofff.utils.writefile import create_corner_point_grid

# =============================================================================
# GRID DISPATCH
# =============================================================================


def grid_and_properties(cfg):
    """
    Dispatch grid generation and spatial property assignment
    based on the selected grid type.
    """
    polygons, points = getpolygons(cfg)

    # Corner-point grid handling
    if cfg.grid == "corner-point":
        xyz, xcoord, zcoord = corner(cfg, points)
        positions(cfg, polygons, xyz=xyz, xcoord=xcoord, zcoord=zcoord)
        return

    dims = np.asarray(cfg.dims, float)

    # Cartesian grid
    if cfg.grid == "cartesian":
        xvert = np.linspace(0, dims[0], cfg.nxz[0] + 1)
        zvert = np.linspace(0, dims[2], cfg.nxz[1] + 1)

    # Tensor grid
    else:

        def tensor(parts, dim):
            """Construct non-uniform grid edges from part sizes."""
            return np.concatenate(
                [
                    np.linspace(
                        i * dim / len(parts),
                        (i + 1) * dim / len(parts),
                        n + 1,
                        endpoint=True,
                    )[:-1]
                    for i, n in enumerate(parts)
                ]
                + [np.array([dim])]
            )

        xvert = tensor(cfg.x, dims[0])
        zvert = tensor(cfg.z, dims[2])
        cfg.nxz = [len(xvert) - 1, len(zvert) - 1]

    # Cell centers
    xcent = 0.5 * (xvert[:-1] + xvert[1:])
    zcent = 0.5 * (zvert[:-1] + zvert[1:])

    # Cell sizes
    setattr(cfg, "dx", xvert[1:] - xvert[:-1])
    setattr(cfg, "dz", zvert[1:] - zvert[:-1])

    positions(cfg, polygons, xcent=xcent, zcent=zcent)

    # Tensor grid expansion (OPM-compatible)
    if cfg.grid == "tensor":
        cfg.dx = list(map(str, xvert[1:] - xvert[:-1]))
        dz = list(map(str, zvert[1:] - zvert[:-1]))

        cfg.dz = [dz[0]] * cfg.nxz[0]
        for i in range(cfg.nxz[1] - 1):
            cfg.dx.extend(cfg.dx[-cfg.nxz[0] :])
            cfg.dz.extend([dz[i + 1]] * cfg.nxz[0])


# =============================================================================
# CORNER-POINT GEOMETRY
# =============================================================================


def corner(cfg, points):
    """
    Build corner-point grid coordinates and compute cell centroids.
    """
    horizonts = get_lines(cfg, points)

    # Horizontal grid lines in x
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

    xcoord, zcoord = [], []

    # Interpolate z-coordinates along horizons
    for x in xvert:
        for layer in horizonts:
            xs = np.array([p[0] for p in layer])
            zs = np.array([p[1] for p in layer])
            i = np.argmin(np.abs(xs - x))

            if xs[i] < x:
                z = zs[i] + (zs[i + 1] - zs[i]) / (xs[i + 1] - xs[i]) * (x - xs[i])
            else:
                z = zs[i - 1] + (zs[i] - zs[i - 1]) / (xs[i] - xs[i - 1]) * (
                    x - xs[i - 1]
                )

            xcoord.append(x)
            zcoord.append(z)

    xcoord, zcoord = np.asarray(xcoord), np.asarray(zcoord)

    stride = len(cfg.z) + 1
    cfg.nxz[0] = len(xcoord) // stride - 1
    cfg.nxz[1] = stride - 1

    # Vertical refinement
    xcoord, zcoord, cfg.nxz[0], cfg.nxz[1] = refinement_z(
        xcoord, zcoord, cfg.nxz[1], cfg.z
    )

    # Compute cell centroids
    xyz = np.zeros((cfg.nxz[0] * cfg.nxz[1], 3))
    stride = cfg.nxz[1] + 1
    idx = 0

    for k in range(cfg.nxz[1]):
        for i in range(cfg.nxz[0]):
            n = i * stride + k
            m = (i + 1) * stride + k

            x = np.array([xcoord[n], xcoord[m], xcoord[m + 1], xcoord[n + 1]])
            z = np.array([zcoord[n], zcoord[m], zcoord[m + 1], zcoord[n + 1]])

            a = x * np.roll(z, -1) - np.roll(x, -1) * z
            area = 0.5 * np.sum(a)

            if abs(area) > 1e-12:
                cx = np.sum((x + np.roll(x, -1)) * a) / (6 * area)
                cz = np.sum((z + np.roll(z, -1)) * a) / (6 * area)
            else:
                # Fallback for degenerate cells
                cx, cz = np.mean(x), np.mean(z)

            xyz[idx] = [cx, 0.0, cz]
            idx += 1

    return xyz, xcoord, zcoord


# =============================================================================
# STRUCTURED POSITION HANDLING
# =============================================================================


def handle_thickness_map(cfg):
    """
    Load and normalize thickness map and corresponding multipliers.
    """
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


def structured_handling_fluidflower(cfg, xcent, zcent, polygons):
    """
    Assign facies, boxes, sensors, and wells on structured grids.
    """
    nx, nz = cfg.nxz
    x = np.tile(xcent, nz)
    z = np.repeat(zcent, nx)
    ztop = cfg.dims[2] - z

    flux = np.full(len(x), -1)

    if cfg.thickness in {"initial", "final"}:
        cfg.dims[1], xth, zth, mult = handle_thickness_map(cfg)
    else:
        cfg.dims[1] = float(cfg.thickness)

    with alive_bar(len(x)) as bar_animation:
        for i, (xi, zi) in enumerate(zip(x, z)):
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
    cfg.fipnum = classify_boxes(cfg, x, ztop, cfg.fluxnum)

    s1, s2 = sensors_structured(cfg, xcent, zcent)
    cfg.fipnum[s1], cfg.fipnum[s2] = "8", "9"

    wells_structured(cfg, xcent, zcent)

    if cfg.hascellmaps:
        get_cellmaps(cfg, x.tolist(), ztop.tolist())
    else:
        shutil.copy(cfg.path / "geology/cellmap.npy", cfg.deck)


# =============================================================================
# CORNER-POINT POSITION HANDLING
# =============================================================================


def corner_point_handling_fluidflower(cfg, xyz, polygons, xcoord, zcoord):
    """
    Assign facies, boxes, sensors, and wells for corner-point grids.
    """
    x = xyz[:, 0]
    ztop = cfg.dims[2] - xyz[:, 2]

    if cfg.thickness in {"initial", "final"}:
        cfg.dims[1], xth, zth, mult = handle_thickness_map(cfg)
    else:
        cfg.dims[1] = float(cfg.thickness)

    flux = np.full(len(x), -1)

    with alive_bar(len(x)) as bar_animation:
        for i, (xi, zi) in enumerate(zip(x, ztop)):
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
    cfg.fipnum = classify_boxes(cfg, x, ztop, cfg.fluxnum)

    s1, s2 = sensors_corner_point(cfg, x, ztop)
    cfg.fipnum[s1], cfg.fipnum[s2] = "8", "9"

    wells_corner_point(cfg, x, ztop)

    if cfg.hascellmaps:
        get_cellmaps(cfg, x.tolist(), ztop.tolist())
    else:
        shutil.copy(cfg.path / "geology/cellmap.npy", cfg.deck)

    create_corner_point_grid(cfg, xcoord, zcoord)


# =============================================================================
# DISPATCHER
# =============================================================================


def positions(
    cfg, polygons, xcent=None, zcent=None, xyz=None, xcoord=None, zcoord=None
):
    """
    Dispatch spatial indexing for either grid type.
    """
    if cfg.grid == "corner-point":
        corner_point_handling_fluidflower(cfg, xyz, polygons, xcoord, zcoord)
    else:
        structured_handling_fluidflower(cfg, xcent, zcent, polygons)


# =============================================================================
# SENSOR AND WELL HELPERS
# =============================================================================


def sensors_structured(cfg, xcent, zcent):
    """
    Determine structured-grid sensor indices.
    """
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


def wells_structured(cfg, xcent, zcent):
    """
    Determine structured-grid well indices.
    """
    for i, w in enumerate(cfg.sources):
        cfg.source_ik[i] = [
            int(np.argmin(np.abs(xcent - w[0]))) + 1,
            int(np.argmin(np.abs(cfg.dims[2] - w[1] - zcent))) + 1,
        ]


def sensors_corner_point(cfg, x, ztop):
    """
    Determine corner-point sensor indices.
    """
    coords = np.column_stack((x, ztop))
    sensors = np.array(cfg.sensors)
    d = ((coords[:, None] - sensors) ** 2).sum(axis=2)

    s1, s2 = int(np.argmin(d[:, 0])), int(np.argmin(d[:, 1]))
    nx = cfg.nxz[0]

    cfg.sensor_ik[0] = [s1 % nx, s1 // nx]
    cfg.sensor_ik[1] = [s2 % nx, s2 // nx]

    return s1, s2


def wells_corner_point(cfg, x, ztop):
    """
    Determine corner-point well indices.
    """
    coords = np.column_stack((x, ztop))
    wells = np.array(cfg.sources)
    d = ((coords[:, None] - wells) ** 2).sum(axis=2)

    for i in range(2):
        idx = np.argmin(d[:, i])
        cfg.source_ik[i] = [idx % cfg.nxz[0] + 1, idx // cfg.nxz[0] + 1]


# =============================================================================
# UTILITIES
# =============================================================================


def classify_boxes(cfg, x, z, flux):
    """
    Assign box-specific FIP numbers based on spatial regions.
    """
    x, z, flux = map(np.asarray, (x, z, flux))
    fip = np.full(len(x), "1", dtype=object)

    def box(b, a, b2):
        m = (x >= b[0][0]) & (x <= b[1][0]) & (z >= b[0][1]) & (z <= b[1][1])
        sel = m & (fip == "1")
        fip[sel & (flux == "1")] = a
        fip[sel & (flux != "1")] = b2

    # Priority order preserved
    box(cfg.boxb, "6", "3")
    box(cfg.boxc, "12", "4")
    box(cfg.boxa, "5", "2")

    fip[(flux == "1") & (fip == "1")] = "7"
    return fip.tolist()


def get_cellmaps(cfg, simxcent, simzcent):
    """
    Construct mapping from structured grid to reference grid.
    """
    refx = np.arange(0, 2.8 + 5.0e-3, 1.0e-2)
    refz = np.arange(0, 1.2 + 5.0e-3, 1.0e-2)
    refx = 0.5 * (refx[1:] + refx[:-1])
    refz = 0.5 * (refz[1:] + refz[:-1])

    x, z = np.meshgrid(refx, refz, indexing="xy")
    ref = np.column_stack((x.ravel(), z.ravel()))
    sim = np.column_stack((simxcent, simzcent))

    d = np.abs(sim[:, None] - ref).sum(axis=2)
    np.save(Path(cfg.deck) / "cellmap.npy", np.argmin(d, axis=0))


# =============================================================================
# GEOMETRY INPUT
# =============================================================================


def get_lines(cfg, points):
    """
    Read geological horizon lines.
    """
    horizonts = []
    with open(cfg.path / "geology/horizonts.geo", encoding="utf8") as file:
        for r in csv.reader(file, delimiter=" "):
            if r[0].startswith("Line"):
                if not horizonts[-1]:
                    horizonts[-1].append(points[int(r[2][1:-1]) - 1])
                horizonts[-1].append(points[int(r[3][:-2]) - 1])
            if len(r) > 1 and r[1] == "Horizont":
                horizonts.append([])
    return horizonts[::-1]


def getpolygons(cfg):
    """
    Read geological polygons and facies definitions.
    """
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


def refinement_z(xci, zci, ncz, znr):
    """
    Refine grid vertically according to znr refinement factors.
    """
    xci, zci = np.asarray(xci), np.asarray(zci)
    stride = ncz + 1
    ncols = len(xci) // stride

    xcr, zcr = [], []

    for j in range(ncols):
        b = j * stride
        xcr.append(xci[b])
        zcr.append(zci[b])
        for i in range(ncz):
            w = np.linspace(1 / znr[i], 1, znr[i])
            xcr.extend(xci[b + i] + (xci[b + i + 1] - xci[b + i]) * w)
            zcr.extend(zci[b + i] + (zci[b + i + 1] - zci[b + i]) * w)

    xcr, zcr = np.asarray(xcr), np.asarray(zcr)
    ncx_new = ncols - 1
    ncz_new = np.where(zcr == zcr[-1])[0][0]

    return xcr.tolist(), zcr.tolist(), ncx_new, ncz_new
