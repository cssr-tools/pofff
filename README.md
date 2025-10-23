[![Build Status](https://github.com/cssr-tools/pofff/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/pofff/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%20to%203.13-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# pofff: An open-source image-based history-matching framework for the FluidFlower Benchmark study using OPM Flow

<img src="docs/text/figs/readme.png" width="830" height="500">

This repository contains runscripts to simulate CO2 injection in the 
[fluidflower benchmark system](https://fluidflower.w.uib.no) using the 
[_OPM Flow_](https://opm-project.org/?page_id=19) simulator and perform history 
matching studies using the ensemble reservoir simulation tool 
[_ERT_](https://github.com/equinor/ert) or [_everest_](https://github.com/equinor/everest).

## Installation
You will first need to install
* OPM Flow (https://opm-project.org, Release 2025.04 or current master branches)

To install the _pofff_ executable from the development version, and companion libraries:

```bash
pip install git+https://github.com/cssr-tools/pofff.git
pip install git+https://github.com/equinor/everest.git
pip install opm # For macOS users, this will not work, then follow the steps in the docs
```

If you are interested in modifying the source code, then you can clone the repository and install the Python requirements in a virtual environment with the following commands:

```bash
# Clone the repo
git clone https://github.com/cssr-tools/pofff.git
# Get inside the folder
cd pofff
# Create virtual environment
python3 -m venv vpofff
# Activate virtual environment
source vpofff/bin/activate
# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
# Install the pofff package
pip install -e .
# Third party companions
pip install git+https://github.com/equinor/everest.git
# For macOS users, this will not work, then skip this and follow the steps in the docs
pip install opm
# For contributions/testing/linting, install the dev-requirements
pip install -r dev-requirements.txt
``` 

See the [_installation_](https://cssr-tools.github.io/pofff/installation.html) for further details on building OPM Flow from the master branches in Linux, Windows (via [_WSL_](https://learn.microsoft.com/en-us/windows/wsl/)), and macOS, as well as the [_opm Python package_](https://pypi.org/project/opm/).

## Running pofff
You can run _pofff_ as a single command line:
```
pofff -i name_of_input_file.toml
```
Run `pofff --help` to see all possible command line argument options.

## Getting started
See the [_examples_](https://cssr-tools.github.io/pofff/examples.html) in the [_documentation_](https://cssr-tools.github.io/pofff/introduction.html).

## Citing
If you use _pofff_ in your research, please cite the following publication:

Landa-Marbán, D., Sandve, T.H., Both, J.W., Nordbotten, J.M., Gasda, S.E. Performance of an open-source image-based history matching framework for CO2 storage. Submitted.

## About pofff
The pofff package is funded by the [_HPC Simulation Software for the Gigatonne Storage Challenge project_](https://www.norceresearch.no/en/projects/hpc-simulation-software-for-the-gigatonne-storage-challenge) [project number 622059] and [_Center for Sustainable Subsurface Resources (CSSR)_](https://cssr.no) [project no. 331841].
Contributions are more than welcome using the fork and pull request approach.
For a new feature, please request this by raising an issue.
