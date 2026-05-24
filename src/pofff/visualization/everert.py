#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Postprocess Everest (ERT) ensemble and optimization studies.
Generates diagnostics, plots, and extracts best simulations."""

from __future__ import annotations

import argparse
import csv
import math
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


@dataclass
class Config:
    """Runtime configuration and paths."""

    path: Path
    times: str
    jobs: List[str]
    external: Path
    run: str
    maps: Path
    min_saturation: float
    min_concentration: float


@dataclass
class EnsembleState:
    """Holds ensemble simulations and diagnostics."""

    observations: np.ndarray
    n_e: int
    n_i: int
    no_obs: int
    no_para: int
    simulations: List[List[list]] = field(default_factory=list)
    sim_ens: List[List[float]] = field(default_factory=list)
    miss_ens: List[List[float]] = field(default_factory=list)
    par_dis: List[List[float]] = field(default_factory=list)
    idrealisation: List[List[int]] = field(default_factory=list)
    num_ens: List[int] = field(default_factory=list)
    cumulative: List[List[List[float]]] = field(default_factory=list)
    para_file: Path | None = None
    para_names: List[str] = field(default_factory=list)


@dataclass
class OptimizationState:
    """Tracks optimization progress and outcomes."""

    optimization: List[float] = field(default_factory=list)
    optimal_value: float = -np.inf
    ind_batch: int = 0
    ind_sim: int = 0
    tot_eval: int = 0
    s: List[List[int]] = field(default_factory=lambda: [[], [], []])
    x: List[int] = field(default_factory=lambda: [0, 0, 0])


def run(cmd: List[str]) -> None:
    """Execute external command and abort on failure."""
    subprocess.run(cmd, check=True)


def ensure_dir(path: Path):
    """Create directory if missing."""
    path.mkdir(parents=True, exist_ok=True)


def save_figure(fig, path: Path, dpi=300):
    """Save figure and release memory."""
    fig.savefig(path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)


def copy_tree_contents(src: Path, dst: Path):
    """Copy contents of src into dst (cp -r src/. dst/)."""
    ensure_dir(dst)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def parse_args(argv) -> Config:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Visualization of optimization studies using Everest (ERT)",
    )
    parser.add_argument("-p", "--path", default=".")
    parser.add_argument("-t", "--times", default="24")
    parser.add_argument("-j", "--jobs", default="equalreg,bcprop,satufunc,flow")
    parser.add_argument("-e", "--external", default="/home/ThirdParty")
    parser.add_argument("-r", "--run", default="run2")
    parser.add_argument("-s", "--minimumsaturation", default="1e-2")
    parser.add_argument("-c", "--minimumconcentration", default="1e-1")
    parser.add_argument("-m", "--maps", default="cellmap.npy")

    a = vars(parser.parse_known_args(argv)[0])

    return Config(
        path=Path(a["path"]).resolve(),
        times=a["times"],
        jobs=[j.strip() for j in a["jobs"].split(",")],
        external=Path(a["external"]),
        run=a["run"],
        maps=Path(a["maps"]),
        min_saturation=float(a["minimumsaturation"]),
        min_concentration=float(a["minimumconcentration"]),
    )


def setup_matplotlib():
    """Apply consistent matplotlib styling."""
    matplotlib.rc("font", family="monospace", size=14)
    plt.rcParams.update(
        {
            "text.usetex": shutil.which("latex") is not None,
            "axes.grid": True,
            "figure.figsize": (16, 8),
        }
    )
    return matplotlib.colormaps["tab20"]


def initialize_ensemble(cfg: Config) -> EnsembleState:
    """Initialize ensemble from simulation folders."""
    obs = np.genfromtxt(cfg.path / "deck/obs.txt")
    no_obs = 1 if obs.ndim == 1 else len(obs)

    sim_root = cfg.path / "output/simulations"
    n_e = len(list(sim_root.iterdir()))
    n_i = max(len(list((sim_root / f"realisation-{i}").iterdir())) for i in range(n_e))

    return EnsembleState(
        observations=obs,
        n_e=n_e,
        n_i=n_i,
        no_obs=no_obs,
        no_para=0,
        simulations=[[] for _ in range(n_i)],
        sim_ens=[[] for _ in range(n_i)],
        miss_ens=[[] for _ in range(n_i)],
        par_dis=[[] for _ in range(n_i)],
        idrealisation=[[] for _ in range(n_i)],
        num_ens=[0 for _ in range(n_i)],
        cumulative=[[[] for _ in range(no_obs)] for _ in range(n_i)],
    )


def read_realisation(cfg: Config, state: EnsembleState, i: int, j: int):
    """Read one realization and update ensemble statistics."""
    base = cfg.path / f"output/simulations/realisation-{j}/iter-{i}"
    if not (base / "OK").exists():
        return

    state.num_ens[i] += 1
    state.idrealisation[i].append(j)

    sim = np.atleast_1d(np.genfromtxt(base / "sim_metrics_0.txt")).astype(float)
    state.simulations[i].append(sim.tolist())

    obs = state.observations

    if obs.ndim == 1:
        miss = ((sim[0] - obs[0]) / obs[1]) ** 2
        state.cumulative[i][0].append(sim[0])
        sim_sum = sim[0]
        n = 1
    else:
        miss = np.sum(((sim - obs[:, 0]) / obs[:, 1]) ** 2)
        for k, v in enumerate(sim):
            state.cumulative[i][k].append(v)
        sim_sum = np.sum(sim)
        n = len(sim)

    state.miss_ens[i].append(miss / (2 * n))
    state.sim_ens[i].append(sim_sum)

    para = base / "parameters.txt"
    if para.exists():
        state.para_file = para
        data = np.atleast_2d(np.genfromtxt(para))
        state.no_para = data.ndim
        for row in data:
            state.par_dis[i].append(row[1])


def plot_simulation_ensemble(cfg: Config, state: EnsembleState, tab20):
    """Plot initial and final ensemble simulations."""
    fig, ax = plt.subplots()

    x = range(1, state.no_obs + 1)
    marker = "o" if state.observations.ndim == 1 else ""

    for vals in state.simulations[0][:-1]:
        ax.plot(x, vals, color=tab20.colors[0], lw=0.5, marker=marker)

    ax.plot(
        x,
        state.simulations[0][-1],
        color=tab20.colors[0],
        lw=0.5,
        marker=marker,
        label="Initial ensemble",
    )

    if state.n_i > 1:
        for vals in state.simulations[-1][:-1]:
            ax.plot(x, vals, color=tab20.colors[2], lw=0.5, marker=marker)

        ax.plot(
            x,
            state.simulations[-1][-1],
            color=tab20.colors[2],
            lw=0.5,
            marker=marker,
            label="Final ensemble",
        )

    obs = state.observations
    if obs.ndim == 1:
        ax.errorbar(1, obs[0], yerr=obs[1], fmt="o", color="gray", label="Observation")
    else:
        for i, (v, e) in enumerate(obs[:-1]):
            ax.errorbar(i + 1, v, yerr=e, fmt="o", color="gray")
        ax.errorbar(
            state.no_obs,
            obs[-1][0],
            yerr=obs[-1][1],
            fmt="o",
            color="gray",
            label="Observation",
        )

    ax.set_xlabel(r"Obsservable [\#]")
    ax.set_ylabel("Wasserstein distance [gr cm]")
    ax.set_ylim(bottom=0)
    ax.set_xticks(x)
    ax.legend()

    save_figure(fig, cfg.path / "figures/simulationensemble.png")


def plot_misfit(cfg: Config, state: EnsembleState):
    """Plot ensemble misfit per iteration."""
    fig, ax = plt.subplots()
    ax.boxplot(state.miss_ens)
    ax.set_xlabel(r"Iteration [\#]")
    ax.set_ylabel("Misfit [-]")
    ax.set_title(
        r"$O_{i,j}=\frac{1}{2N_{obs}}\sum_n^{N_{obs}}((d^{n}_{i,j}-d^{n})/\sigma_n)^2$"
    )
    save_figure(fig, cfg.path / "figures/dist_mismatch.png")


def plot_parameter_distributions(cfg: Config, state: EnsembleState):
    """Boxplots of parameter distributions."""
    if not state.para_file:
        return

    with open(state.para_file, encoding="utf8") as f:
        state.para_names = [row[0] for row in csv.reader(f, delimiter=" ")]

    n_params = len(state.para_names)
    rows = math.ceil(n_params / 3)
    fig = plt.figure(figsize=(25, n_params))

    for k in range(n_params):
        ax = fig.add_subplot(rows, 3, k + 1)
        ini_dist = state.par_dis[0][k::n_params]

        if state.n_i > 1:
            fin_dist = state.par_dis[-1][k::n_params]
            ax.boxplot([ini_dist, fin_dist], tick_labels=["Initial", "Final"])
            ax.set_title(
                f"Box plot of initial and final {state.para_names[k].lower()} parameter"
            )
        else:
            ax.boxplot([ini_dist], tick_labels=["Initial"])
            ax.set_title(f"Box plot of initial {state.para_names[k]} parameter")

    save_figure(fig, cfg.path / "figures/parameterdistributions.png")


def extract_best_simulation(cfg: Config, state: EnsembleState):
    """Extract best-fitting ensemble realization."""
    sims = np.array(state.simulations[-1])
    obs = state.observations

    if obs.ndim == 1:
        diff = np.abs(sims[:, 0] - obs[0])
    else:
        diff = np.sum(np.abs(sims - obs[:, 0]), axis=1)

    idx = int(np.argmin(diff))
    best_id = state.idrealisation[-1][idx]

    src = cfg.path / f"output/simulations/realisation-{best_id}/iter-{state.n_i - 1}"
    dst = cfg.path / "figures/best_simulation"
    copy_tree_contents(src, dst)

    old_cwd = Path.cwd()
    os.chdir(dst)
    try:
        run(["python3", str(cfg.path / "jobs/copyd.py")])
        for job in cfg.jobs:
            run(["python3", str(cfg.path / f"jobs/{job}.py")])
        run(
            [
                "python3",
                str(cfg.path / "jobs/data.py"),
                "-t",
                cfg.times,
                "-m",
                str(cfg.maps),
            ]
        )
        run(
            [
                "python3",
                str(cfg.path / "jobs/metric.py"),
                "-t",
                cfg.times,
                "-e",
                cfg.run,
                "-p",
                str(cfg.external),
                "-s",
                str(cfg.min_saturation),
                "-c",
                str(cfg.min_concentration),
            ]
        )
    finally:
        os.chdir(old_cwd)

    print(
        f"Best: {cfg.path}/output/simulations/"
        f"realisation-{best_id}/iter-{state.n_i - 1}"
    )

    best_vals = state.simulations[-1][idx]
    print(f"Values: {list(best_vals) if state.n_i > 1 else best_vals}")


def process_optimization(cfg: Config) -> OptimizationState:
    """Process Everest optimization results."""
    root = cfg.path / "everest_output/sim_output"
    opt = OptimizationState()

    improved = -np.inf
    where = []

    batches = sorted(root.iterdir(), key=lambda p: int(p.name.split("_")[1]))

    for batch in batches:
        batch_index = int(batch.name.split("_")[1])
        evals = sorted(
            (batch / "realization_0").iterdir(),
            key=lambda p: int(p.name.split("_")[1]),
        )

        for ev in evals:
            fval = np.genfromtxt(ev / "func")
            opt.tot_eval += 1

            if np.isnan(fval):
                opt.x[1] += 1
            elif fval == -1:
                opt.x[2] += 1
            else:
                opt.x[0] += 1
                if fval > improved:
                    improved = float(fval)
                    where.append((batch_index, int(ev.name.split("_")[1])))

        opt.optimization.append(improved)

        for i in range(3):
            opt.s[i].append(opt.x[i])
            opt.x[i] = 0

    idx = int(np.nanargmax(opt.optimization))
    opt.optimal_value = opt.optimization[idx]
    opt.ind_batch, opt.ind_sim = where[idx]

    return opt


def plot_optimization(cfg: Config, opt: OptimizationState):
    """Plot optimization progress."""
    fig, ax = plt.subplots()

    scale = 8.5 * 100
    values = [-v * scale for v in opt.optimization]
    steps = range(1, len(values) + 1)

    if len(values) > 1:
        ax.step(steps, values, lw=5, color="b")
    else:
        ax.plot(1, values[0], marker="*", ms=20, color="k")

    ax.set_title("Optimization results")
    ax.set_xlabel(r"Iteration [\#]")
    ax.set_ylabel("Wasserstein distance [gr cm]")

    if len(values) < 20:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        ax.set_xticks(np.linspace(0, len(values) + 1, 11))

    save_figure(fig, cfg.path / "figures/optimization_results.png")


def extract_optimal_solution(cfg: Config, opt: OptimizationState):
    """Extract and postprocess optimal optimization result."""
    dst = cfg.path / "figures/best_simulation"
    ensure_dir(dst)

    src = (
        cfg.path
        / "everest_output/sim_output"
        / f"batch_{opt.ind_batch}"
        / "realization_0"
        / f"evaluation_{opt.ind_sim}"
        / "para.json"
    )

    shutil.copy2(src, dst / "para.json")

    old_cwd = Path.cwd()
    os.chdir(dst)
    try:
        run(["python3", str(cfg.path / "jobs/copyd.py")])
        for job in cfg.jobs:
            run(["python3", str(cfg.path / f"jobs/{job}.py")])
        run(
            [
                "python3",
                str(cfg.path / "jobs/data.py"),
                "-t",
                cfg.times,
                "-m",
                str(cfg.maps),
            ]
        )
        run(
            [
                "python3",
                str(cfg.path / "jobs/metric.py"),
                "-t",
                cfg.times,
                "-e",
                cfg.run,
                "-p",
                str(cfg.external),
                "-s",
                str(cfg.min_saturation),
                "-c",
                str(cfg.min_concentration),
            ]
        )
        run(["python3", str(cfg.path / "jobs/scale.py")])
    finally:
        os.chdir(old_cwd)

    print(
        f"Best: {cfg.path}/everest_output/sim_output/"
        f"batch_{opt.ind_batch}/realization_0/"
        f"evaluation_{opt.ind_sim}"
    )


def plot_observable_distribution(cfg: Config, state: EnsembleState):
    """Plot observable sum distributions."""
    fig, ax = plt.subplots()
    ax.boxplot(
        [state.sim_ens[i] for i in range(state.n_i)],
        positions=list(range(state.n_i)),
    )
    ax.set_xlabel(r"Iteration [\#]")
    ax.set_ylabel("Wasserstein distance [gr cm]")
    ax.set_title(r"$\sum_n^{N_{obs}} d^n_{i,j}$")
    ax.set_xticks(range(state.n_i))

    save_figure(fig, cfg.path / "figures/dist_observable.png")


def plot_hm_mismatch(cfg: Config, state: EnsembleState):
    """Plot ensemble-mean misfit per iteration."""
    fig, ax = plt.subplots()

    for i in range(state.n_i):
        if not state.miss_ens[i]:
            continue
        mean_misfit = np.sum(state.miss_ens[i]) / len(state.miss_ens[i])
        ax.plot(i, mean_misfit, marker="o", label=rf"$N_{{ens}}={state.num_ens[i]}$")

    ax.set_title(
        r"$O_i=\frac{1}{N_{ens}}\sum_{j=1}^{N_{ens}} O_{i,j}$, \#"
        + f"HM parameters: {state.no_para}"
    )
    ax.set_xlabel(r"Iteration [\#]")
    ax.set_ylabel("Misfit [-]")
    ax.set_xticks(range(state.n_i))
    ax.legend()

    save_figure(fig, cfg.path / "figures/hm_mismatch.png")


def plot_cumulative_misfit(cfg: Config, state: EnsembleState, tab20):
    """Plot cumulative misfit contributions per observation."""
    for i in range(state.n_i):
        if not state.cumulative[i] or not state.cumulative[i][0]:
            continue

        fig, ax = plt.subplots()

        allw = np.zeros(len(state.cumulative[i][0]))
        for j in range(state.no_obs):
            allw += np.array(state.cumulative[i][j])

        indc = np.argsort(allw)
        allw_sorted = np.sort(allw)

        ax.axhline(
            y=allw_sorted.mean() / state.no_obs,
            color="black",
            ls="--",
            lw=1,
            label=f"Total average {allw_sorted.mean() / state.no_obs:.2f}",
        )

        ax.bar(range(1, len(allw_sorted) + 1), allw_sorted, color=tab20.colors[0])

        remainder = allw_sorted.copy()
        for j in range(state.no_obs - 1):
            vals = np.array([state.cumulative[i][j][r] for r in indc])
            remainder -= vals
            ax.bar(
                range(1, len(remainder) + 1),
                remainder,
                color=tab20.colors[j + 1],
                label=f"obs-{j+1}",
            )

        ax.set_title(f"Realization (iter-{i})")
        ax.set_xlabel(r"Realisation [\#]")
        ax.set_ylabel("Cumulative misfit [-]")
        ax.legend()

        save_figure(fig, cfg.path / f"figures/cumulative_misfit_ite-{i}.png")


def plot_optimization_details(cfg: Config, opt: OptimizationState):
    """Plot optimization success statistics."""
    colors = ["g", "r", "k"]
    names = [
        f"Succeeded (no={sum(opt.s[0])})",
        f"Failed (no={sum(opt.s[1])})",
        f"Nonmonotonic (no={sum(opt.s[2])})",
    ]

    fig, ax = plt.subplots()

    n_steps = len(opt.s[0])
    x = np.arange(1, n_steps + 1)

    total = np.array(opt.s[0]) + np.array(opt.s[1]) + np.array(opt.s[2])
    ax.bar(x, total, color=colors[0], label=names[0])

    remainder = total.copy()
    for i in range(2):
        remainder -= np.array(opt.s[i])
        if i == 0 and sum(opt.s[1]) == 0:
            continue
        ax.bar(x, remainder, color=colors[i + 1], label=names[i + 1])

    ax.set_title(f"Details on failed and succeeded simulations (Total={opt.tot_eval})")
    ax.set_xlabel(r"Iteration [\#]")
    ax.set_ylabel(r"Occurrence [\#]")

    if n_steps < 20:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    else:
        ax.set_xticks(np.linspace(1, n_steps, 11))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax.legend()
    save_figure(fig, cfg.path / "figures/details.png", dpi=900)


def run_everert(argv=None):
    """Entry point."""
    cfg = parse_args(argv)
    tab20 = setup_matplotlib()

    ensure_dir(cfg.path / "figures")

    if (cfg.path / "everest_output").exists():
        opt = process_optimization(cfg)
        plot_optimization(cfg, opt)
        plot_optimization_details(cfg, opt)
        extract_optimal_solution(cfg, opt)
    else:
        state = initialize_ensemble(cfg)
        for j in range(state.n_e):
            for i in range(state.n_i):
                read_realisation(cfg, state, i, j)

        plot_simulation_ensemble(cfg, state, tab20)
        plot_hm_mismatch(cfg, state)
        plot_misfit(cfg, state)
        plot_observable_distribution(cfg, state)
        plot_parameter_distributions(cfg, state)
        plot_cumulative_misfit(cfg, state, tab20)
        extract_best_simulation(cfg, state)


if __name__ == "__main__":
    run_everert()
