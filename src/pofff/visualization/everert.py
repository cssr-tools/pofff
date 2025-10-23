#!/usr/bin/env python
# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Script to postprocess everest and ert studies.
"""

import argparse
import csv
import os
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

font = {"family": "normal", "weight": "normal", "size": 14}
tab20s = matplotlib.colormaps["tab20"]
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "monospace",
        "legend.columnspacing": 0.9,
        "legend.handlelength": 3.5,
        "legend.fontsize": 14,
        "lines.linewidth": 4,
        "axes.titlesize": 14,
        "axes.grid": True,
        "figure.figsize": (16, 8),
    }
)


def figures():
    """Main function to postprocess everest results (differential_evolution)"""
    cmdargs = load_parser()
    dic = {"t": cmdargs["times"]}
    dic["j"] = (cmdargs["jobs"].strip()).split(",")
    dic["p"] = os.path.abspath(cmdargs["path"].strip())
    dic["e"] = cmdargs["external"].strip()
    dic["m"] = cmdargs["maps"].strip()

    # Make the figures folder
    if not os.path.exists("figures"):
        os.system("mkdir figures")

    if os.path.exists("everest_output"):
        plot_optimization_results()
        plt.rcParams.update({"axes.grid": False})
        plot_optimization_details(dic)
        find_optimal(dic)
    else:
        initialize_ert(dic)
        for j in range(dic["n_e"]):
            for i in range(dic["n_i"]):
                read_hm(dic, i, j)
        para_dist(dic)
        make_figures(dic)
        plot_cumulative_misfit(dic)
        find_best(dic)


def find_best(dic):
    """
    Find the closest simulation to the observations
    """
    if dic["observations"].ndim == 1:
        diffo = dic["simulations"][-1] - dic["observations"][0]

    else:
        diffo = np.sum(
            np.array(list(dic["simulations"][-1]))
            - np.array([row[0] for row in dic["observations"]]),
            axis=1,
        )
    eobs = np.where(abs(diffo) == min(abs(diffo)))
    bestid = dic["idrealisation"][-1][eobs[0][0]]
    if not os.path.exists(f"{dic['p']}/figures/best_simulation"):
        os.system(f"mkdir {dic['p']}/figures/best_simulation")
    os.system(
        f"cp -r output/simulations/realisation-{bestid}/iter-{dic['n_i']-1}/. "
        "figures/best_simulation/."
    )
    os.chdir(f"{dic['p']}/figures/best_simulation")
    os.system(f"python3 {dic['p']}/jobs/copyd.py")
    for job in dic["j"]:
        os.system(f"python3 {dic['p']}/jobs/{str(job)}.py")
    os.system(f"python3 {dic['p']}/jobs/data.py -t {dic['t']} -m {dic['m']}")
    os.system(f"python3 {dic['p']}/jobs/metric.py -t {dic['t']} -e {dic['e']}")
    print(
        f"Best: {dic['p']}/output/simulations/realisation-{bestid}/iter-{dic['n_i']-1}"
    )
    if dic["n_i"] > 1:
        print(f"Values: {list(dic['simulations'][-1][eobs[0][0]])}")
    else:
        print(f"Values: {dic['simulations'][0][eobs[0][0]]}")


def plot_cumulative_misfit(dic):
    """
    Plot the cumulative misfit per iteration
    """
    for i in range(dic["n_i"]):
        fig, axis = plt.subplots()
        allw = 0
        for j in range(dic["no_obs"]):
            allw += np.array(dic["cum"][i][j])
        allw = np.array(allw)
        indc = np.argsort(allw)
        allw = np.sort(allw)
        axis.axhline(
            y=allw.mean() / dic["no_obs"],
            color="black",
            ls="--",
            lw=1,
            label=f"Total average {allw.mean()/dic['no_obs']:.2f}",
        )
        axis.bar(
            list(range(len(dic["cum"][i][0]))),
            allw,
            color=tab20s.colors[0],
            label=f"obs-{0}",
        )
        for j in range(dic["no_obs"] - 1):
            allw -= np.array([dic["cum"][i][j][r] for r in indc])
            axis.bar(
                list(range(len(dic["cum"][i][j + 1]))),
                allw,
                color=tab20s.colors[j + 1],
                label=f"obs-{j+1}",
            )
        axis.set_title(f"Realization (iter-{i})")
        axis.set_ylabel("Cumulative misfit")
        axis.legend()
        fig.savefig(
            f"figures/cumulative_misfit_ite-{i}.png",
            bbox_inches="tight",
        )


def make_figures(dic):
    """
    Write the plots
    """
    if dic["observations"].ndim == 1:
        marker = "o"
    else:
        marker = ""
    fig, axis = plt.subplots()
    for values in dic["simulations"][0][:-1]:
        axis.plot(
            range(1, dic["no_obs"] + 1),
            values,
            color=[51 / 255.0, 153 / 255.0, 255 / 255.0],
            lw=0.5,
            marker=marker,
        )
    axis.plot(
        range(1, dic["no_obs"] + 1),
        dic["simulations"][0][-1],
        color=[51 / 255.0, 153 / 255.0, 255 / 255.0],
        lw=0.5,
        marker=marker,
        label="Initial ensemble",
    )
    if dic["n_i"] > 1:
        for values in dic["simulations"][-1][:-1]:
            axis.plot(
                range(1, dic["no_obs"] + 1),
                values,
                color=[0 / 255.0, 204 / 255.0, 0 / 255.0],
                lw=0.5,
                marker=marker,
            )
        axis.plot(
            range(1, dic["no_obs"] + 1),
            dic["simulations"][-1][-1],
            color=[0 / 255.0, 204 / 255.0, 0 / 255.0],
            lw=0.5,
            marker=marker,
            label="Final ensemble",
        )
    if dic["observations"].ndim == 1:
        axis.errorbar(
            1,
            dic["observations"][0],
            yerr=dic["observations"][1],
            fmt="o",
            color=[128 / 255.0, 128 / 255.0, 128 / 255.0],
            ecolor=[128 / 255.0, 128 / 255.0, 128 / 255.0],
            elinewidth=1,
            capsize=0,
            markersize="0.5",
            label="Observation",
        )
    else:
        for i, obs in enumerate(dic["observations"][:-1]):
            axis.errorbar(
                i + 1,
                obs[0],
                yerr=obs[1],
                fmt="o",
                color=[128 / 255.0, 128 / 255.0, 128 / 255.0],
                ecolor=[128 / 255.0, 128 / 255.0, 128 / 255.0],
                elinewidth=1,
                capsize=0,
                markersize="0.5",
            )
        axis.errorbar(
            dic["no_obs"],
            dic["observations"][-1][0],
            yerr=dic["observations"][-1][1],
            fmt="o",
            color=[128 / 255.0, 128 / 255.0, 128 / 255.0],
            ecolor=[128 / 255.0, 128 / 255.0, 128 / 255.0],
            elinewidth=1,
            capsize=0,
            markersize="0.5",
            label="Observation",
        )
    axis.set_ylabel("EMD [gr cm]")
    axis.set_xlabel("No. Obs")
    axis.set_ylim(bottom=0)
    axis.set_xticks(range(1, dic["no_obs"] + 1))
    axis.legend()
    fig.savefig(
        "figures/simulationensemble.png",
        bbox_inches="tight",
    )

    fig, axis = plt.subplots()
    for i in range(dic["n_i"]):
        axis.plot(
            i,
            sum(dic["miss_ens"][i]) / len(dic["miss_ens"][i]),
            markersize="10",
            marker="o",
            label=r"$N_{ens}=$" + f"{dic['num_ens'][i]}",
            c=tab20s.colors[i],
        )
    axis.set_title(
        r"$O_i=\frac{1}{N_{ens}}\sum_{j}^{N_{ens}}O_{i,j}$, \#"
        + f"HM parameters: {dic['data'].ndim}"
    )
    axis.legend()
    axis.set_xlabel(r"\# iteration [-]")
    axis.set_ylabel("Missmatch [-]")
    axis.set_xticks(range(dic["n_i"]))
    fig.savefig(
        "figures/hm_missmatch.png",
        bbox_inches="tight",
    )
    fig, axis = plt.subplots()
    axis.boxplot(
        [dic["miss_ens"][i] for i in range(dic["n_i"])],
        positions=list(range(dic["n_i"])),
    )
    axis.set_title(
        r"$O_{i,j}=\frac{1}{2N_{obs}}\sum_n^{N_{obs}}((d^{n}_{i,j}-d^{n})/\sigma_n)^2$"
    )
    axis.set_xlabel(r"\# iteration [-]")
    axis.set_ylabel("Missmatch [-]")
    axis.set_xticks(range(dic["n_i"]))
    fig.savefig(
        "figures/dist_missmatch.png",
        bbox_inches="tight",
    )
    fig, axis = plt.subplots()
    axis.boxplot(
        [dic["sim_ens"][i] for i in range(dic["n_i"])],
        positions=list(range(dic["n_i"])),
    )
    axis.set_title(r"$\sum_n^{N_{obs}}d^{n}_{i,j}$")
    axis.set_xlabel(r"\# iteration [-]")
    axis.set_ylabel("EMD distance")
    axis.set_xticks(range(dic["n_i"]))
    fig.savefig(
        "figures/dist_observable.png",
        bbox_inches="tight",
    )


def para_dist(dic):
    """
    Plot the parameter distributions

    Args:
        dig (dict): Global dictionary

    Returns:
        None

    """
    dic["name"] = []
    if "para" in dic:
        with open(dic["para"], "r", encoding="utf8") as file:
            for row in csv.reader(file, delimiter=" "):
                dic["name"].append(row)
        if dic["data"].ndim == 1:
            l_data = 1
        else:
            l_data = len(dic["data"])
        dic["p_a"] = math.ceil(l_data / 3)
        figd = plt.figure(figsize=(25, l_data))
        for k in range(l_data):
            plot_parameters(
                figd,
                [
                    dic["par_dis"][0][i]
                    for i in range(k, len(dic["par_dis"][0]), l_data)
                ],
                [
                    dic["par_dis"][-1][j]
                    for j in range(k, len(dic["par_dis"][-1]), l_data)
                ],
                k + 1,
                dic,
            )
        figd.savefig(
            "figures/parameterdistributions.png",
            bbox_inches="tight",
        )


def plot_parameters(fig, inidist, findist, k, dic):
    """
    Routine to make the plots iteratively
    """
    axis = fig.add_subplot(dic["p_a"], 3, k)
    if dic["n_i"] == 1:
        axis.boxplot([inidist])
        axis.set_title(
            f"Box plot of initial {dic['name'][k-1][0]} parameter distribution"
        )
    else:
        axis.boxplot([inidist, findist])
        axis.set_title(
            f"Box plot of initial and final {dic['name'][k-1][0]} parameter distribution"
        )


def read_hm(dic, i, j):
    """
    Extract relevant hm data

    Args:
        dig (dict): Global dictionary

    Returns:
        None

    """
    if os.path.exists(f"output/simulations/realisation-{j}/iter-{i}/OK") == 1:
        dic["num_ens"][i] += 1
        dic["idrealisation"][i].append(j)
        dic["simulations"][i].append(
            np.genfromtxt(
                f"output/simulations/realisation-{j}/iter-{i}/sim_metrics_0.txt",
                delimiter=" ",
            )
        )
        miss_ens = 0
        sim_ens = 0
        coun = 0
        if dic["observations"].ndim > 1:
            for d_1, d_2 in zip(dic["simulations"][i][-1], dic["observations"]):
                miss_ens += ((d_1 - d_2[0]) / d_2[1]) ** 2
                dic["cum"][i][coun].append(d_1)
                sim_ens += d_1
                coun += 1
        else:
            miss_ens += (
                (dic["simulations"][i][-1] - dic["observations"][0])
                / dic["observations"][1]
            ) ** 2
            dic["cum"][i][0].append(dic["simulations"][i][-1])
            sim_ens += dic["simulations"][i][-1]
            coun += 1
        dic["miss_ens"][i].append(miss_ens / (2.0 * coun))
        dic["sim_ens"][i].append(sim_ens)
        if os.path.exists(
            f"output/simulations/realisation-{j}/iter-{i}/parameters.txt"
        ):
            dic["para"] = f"output/simulations/realisation-{j}/iter-{i}/parameters.txt"
            dic["data"] = np.genfromtxt(dic["para"], delimiter=" ")
            if dic["data"].ndim == 1:
                dic["par_dis"][i].append(dic["data"][1])
            else:
                for k in range(len(dic["data"])):
                    dic["par_dis"][i].append(dic["data"][k, 1])


def initialize_ert(dic):
    """
    Variables for the plotting method

    Args:
        dig (dict): Global dictionary

    Returns:
        None

    """
    dic["n_e"] = len(next(os.walk("output/simulations"))[1])
    dic["n_i"] = 1
    dic["observations"] = np.genfromtxt("deck/obs.txt", delimiter=" ")
    if dic["observations"].ndim == 1:
        dic["no_obs"] = 1
    else:
        dic["no_obs"] = len(dic["observations"])
    for i in range(dic["n_e"]):
        dic["n_i"] = max(
            dic["n_i"], len(next(os.walk(f"output/simulations/realisation-{i}"))[1])
        )

    dic["par_dis"] = [[] for _ in range(dic["n_i"])]
    dic["simulations"] = [[] for _ in range(dic["n_i"])]
    dic["idrealisation"] = [[] for _ in range(dic["n_i"])]
    dic["sim_ens"] = [[] for _ in range(dic["n_i"])]
    dic["miss_ens"] = [[] for _ in range(dic["n_i"])]
    dic["num_ens"] = [0 for _ in range(dic["n_i"])]
    dic["cum"] = [[[] for _ in range(dic["no_obs"])] for _ in range(dic["n_i"])]


def find_optimal(dic):
    """Find the well locations and folder for the 'optimal' obtained solution"""
    dic["ind_batch"] = [0, 0]
    dic["ind_sim"] = [0, 0]
    optimal = []
    file = "everest_output/optimization_output/results.txt"
    with open(file, "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if len(row) > 0:
                if ((row[0].strip()).split()[0]).isdigit():
                    optimal.append(float((row[0].strip()).split()[2]))
    optimal = np.float16(optimal[int(np.nanargmax(np.array(optimal)))])
    batch_size = 0
    file = "everest_output/optimization_output/results.txt"
    with open(file, "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if len(row) > 0:
                if ((row[0].strip()).split()[0]).isdigit():
                    if int((row[0].strip()).split()[1]) == 0:
                        batch_size += 1
                    if np.float16((row[0].strip()).split()[2]) == optimal:
                        dic["ind_batch"][1] = int(
                            int((row[0].strip()).split()[0]) / batch_size
                        )
                        dic["ind_sim"][1] = (
                            int((row[0].strip()).split()[0])
                            - dic["ind_batch"][1] * batch_size
                        )
                        break
    if not os.path.exists(f"{dic['p']}/figures/best_simulation"):
        os.system(f"mkdir {dic['p']}/figures/best_simulation")
    os.chdir(f"{dic['p']}/figures/best_simulation")
    os.system(
        f"cp {dic['p']}/everest_output/sim_output/"
        + f"batch_{dic['ind_batch'][1]}/geo_realization_0/simulation_"
        + f"{dic['ind_sim'][1]}/para.json ."
    )
    os.system(f"python3 {dic['p']}/jobs/copyd.py")
    for job in dic["j"]:
        os.system(f"python3 {dic['p']}/jobs/{str(job)}.py")
    os.system(f"python3 {dic['p']}/jobs/data.py -t {dic['t']} -m {dic['m']}")
    os.system(f"python3 {dic['p']}/jobs/metric.py -t {dic['t']} -e {dic['e']}")
    os.system(f"python3 {dic['p']}/jobs/scale.py")
    print(
        f"Best: {dic['p']}/everest_output/sim_output/batch_{dic['ind_batch'][1]}"
        f"/geo_realization_0/simulation_{dic['ind_sim'][1]}"
    )


def read_results(dic):
    """Get the values over the optimization steps"""
    file = "everest_output/optimization_output/results.txt"
    n, dic["tot_eval"] = 0, 0
    with open(file, "r", encoding="utf8") as file:
        for row in csv.reader(file):
            if len(row) > 0:
                if ((row[0].strip()).split()[0]).isdigit():
                    dic["tot_eval"] += 1
                    if n != int((row[0].strip()).split()[1]):
                        for i in range(3):
                            dic[f"s{i}"].append(dic[f"x{i}"])
                            dic[f"x{i}"] = 0
                        n += 1
                    if (row[0].strip()).split()[2] == "nan":
                        dic["x0"] += 1
                    elif (row[0].strip()).split()[2] == "-1":
                        dic["x1"] += 1
                    else:
                        dic["x2"] += 1
    for i in range(3):
        dic[f"s{i}"].append(dic[f"x{i}"])


def plot_optimization_details(dic):
    """Plot the number of failed and succeed simulations over steps"""
    for i in range(3):
        dic[f"s{i}"] = []
        dic[f"x{i}"] = 0
    read_results(dic)
    colors = ["r", "k", "g"]
    names = [
        f"Failed (no={sum(dic['s0'])})",
        f"Nomonotonic (no={sum(dic['s1'])})",
        f"Succeeded (no={sum(dic['s2'])})",
    ]
    fig, ax = plt.subplots()
    allw = 0
    for i in range(3):
        allw += np.array(dic[f"s{i}"])
    allw = np.array(allw)
    indc = np.argsort(allw)
    indc = range(len(allw))
    ax.bar(range(1, len(allw) + 1), allw, color=colors[0], label=names[0])
    for i in range(2):
        allw -= np.array([dic[f"s{i}"][r] for r in indc])
        if i == 0 and dic["x1"] == 0:
            continue
        ax.bar(range(1, len(allw) + 1), allw, color=colors[i + 1], label=names[i + 1])
    ax.set_title(f"Details on failed and succeed simulations (Total={dic['tot_eval']})")
    ax.set_ylabel(r"Occurence [\#]")
    ax.set_xlabel(r"Step [\#]")
    # ax.set_xlim([-1,1001])
    ax.set_xticks(
        np.linspace(
            0,
            len(allw),
            11,
        )
    )
    ax.legend()
    # ax.set_xticks(range(len(allw)))
    fig.savefig("figures/details.png", bbox_inches="tight", dpi=900)


def plot_optimization_results():
    """Plot the optimization values over steps"""
    optimization = []
    file = "everest_output/optimization_output/optimizer_output.txt"
    with open(file, "r", encoding="utf8") as file:
        for j, row in enumerate(csv.reader(file)):
            optimization.append([j + 1, -float((row[0].strip()).split()[4])])
    if not optimization:
        return
    fig, axis = plt.subplots()
    if len(optimization) > 1:
        axis.step(
            [step[0] for step in optimization],
            [-value[1] * 8.5 * 100 for value in optimization],
            lw=5,
            color="b",
        )
    else:
        axis.plot(
            optimization[0][0],
            -optimization[0][1] * 8.5 * 100,
            marker="*",
            ms=20,
            color="k",
        )
    axis.set_title("Optimization results")
    axis.set_ylabel("Objective value")
    axis.set_xlabel(r"Step [\#]")
    axis.set_xticks(
        np.linspace(
            0,
            optimization[-1][0] + 1,
            11,
        )
    )
    fig.savefig("figures/optimization_results.png", bbox_inches="tight")


def load_parser():
    """Argument options"""
    parser = argparse.ArgumentParser(
        description="Viusalization of optimization studies"
        " using everest (differential_evolution). The figures"
        " are saved in the figures folder."
    )
    parser.add_argument(
        "-p",
        "--path",
        default=".",
        help="Path to the opm simulations.",
    )
    parser.add_argument(
        "-t",
        "--times",
        default="24",
        help="Times in hours for the images.",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        default="equalreg,bcprop,satufunc,flow",
        help="Jobs to run.",
    )
    parser.add_argument(
        "-e",
        "--external",
        default="/home/AD.NORCERESEARCH.NO/dmar/ThirdParty",
        help="Path to the fluidflower data",
    )
    parser.add_argument(
        "-m",
        "--maps",
        default="/Users/dmar/Github/pofff/src/pofff/geology/cellmap.npy",
        help="Path to the cell maps",
    )
    return vars(parser.parse_known_args()[0])


if __name__ == "__main__":
    figures()
