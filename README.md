[![Build Status](https://github.com/cssr-tools/pofff/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/pofff/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12%20to%203.13-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# pofff: An open-source image-based history-matching framework for the FluidFlower benchmark study using OPM Flow

<center><img src="docs/text/figs/pofff+plopm_xco2l.gif" width="830" height="auto" /></center>
<center><img src="docs/text/figs/pofff.png" width="830" height="auto"></center>

This repository contains runscripts to simulate CO2 injection in the 
[_fluidflower benchmark system_](https://fluidflower.w.uib.no) using the 
[_OPM Flow_](https://opm-project.org/?page_id=19) simulator and perform history 
matching studies using the ensemble reservoir simulation tool 
[_ERT_](https://github.com/equinor/ert) or the decision-making tool [_everest_](https://github.com/equinor/everest-tutorials).

See this [_nice video_](https://cssr-tools.github.io/pofff/introduction.html#) for a dynamic comparison of the FluidFlower experiment and
OPM simulations.

## Installation
You will first need to install
* OPM Flow (https://opm-project.org, Release 2025.10 or current master branches)

To install the _pofff_ executable from the development version:

```bash
pip install git+https://github.com/cssr-tools/pofff.git
```

If you are interested in a specific version (e.g., v2025.10) or in modifying the source code, then you can clone the repository and install the Python requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/cssr-tools/pofff.git
# Get inside the folder
cd pofff
# For a specific version (e.g., v2025.10), or skip this step (i.e., edge version)
git checkout v2025.10
# Create virtual environment (to specific Python, python3.13 -m venv vpofff)
python3 -m venv vpofff
# Activate virtual environment
source vpofff/bin/activate
# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
# Install the pofff package
pip install -e .
# For contributions/testing/linting, install the dev-requirements
pip install -r dev-requirements.txt
``` 

See the [_installation_](https://cssr-tools.github.io/pofff/installation.html) for further details on building OPM Flow from the master branches in Linux, Windows (via [_WSL_](https://learn.microsoft.com/en-us/windows/wsl/)), and macOS.

## Running pofff
You can run _pofff_ as a single command line:
```
pofff -i name_of_input_file.toml
```
Run `pofff --help` to see all possible command line argument options.

## Getting started
See the [_examples_](https://cssr-tools.github.io/pofff/examples.html) in the [_documentation_](https://cssr-tools.github.io/pofff/introduction.html).

## Citing

* Landa-Marbán, D., Sandve, T.H., Both, J.W., Nordbotten, J.M., and Gasda, S.E., 2026. Performance of an open-source image-based history matching framework for CO2 storage. Transp Porous Med 153, 21, https://doi.org/10.1007/s11242-025-02275-0.

## About pofff
The pofff package is funded by the [_Center for Sustainable Subsurface Resources (CSSR)_](https://cssr.no) [project no. 331841].
Contributions are more than welcome using the fork and pull request approach.
For a new feature, please request this by raising an issue.
