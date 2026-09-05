pofff
=====

.. rst-class:: lead

   An open-source image-based history-matching framework for the FluidFlower
   benchmark using OPM Flow, ERT, and Everest.

**pofff** generates FluidFlower simulation models, runs OPM Flow, writes
benchmark CSV files, compares simulations with experimental and published
results, and supports history matching with ERT and Everest.

.. grid:: 1 2 2 4
   :gutter: 3
   :margin: 4 0 4 0

   .. grid-item-card:: :octicon:`rocket;1.2em` Get started
      :link: introduction
      :link-type: doc

      Learn the main simulation, benchmark, and history-matching workflows.

   .. grid-item-card:: :octicon:`download;1.2em` Install
      :link: installation
      :link-type: doc

      Install pofff, OPM Flow, ERT, Everest, and visualization tools.

   .. grid-item-card:: :octicon:`gear;1.2em` Configure a case
      :link: configuration_file
      :link-type: doc

      Define the grid, thickness, facies, sources, injection schedule, and
      history-matching settings.

   .. grid-item-card:: :octicon:`book;1.2em` Follow the tutorial
      :link: tutorial
      :link-type: doc

      Run a simulation and add its results to the FluidFlower comparisons.

Quick installation
------------------

Install the current development version:

.. code-block:: console

   pip install git+https://github.com/cssr-tools/pofff.git

See :doc:`installation` for virtual environments, OPM Flow, ERT, Everest,
ResInsight, plopm, optional LaTeX support, and installation from source.

Quick start
-----------

Run a FluidFlower simulation and generate benchmark results at 24, 48, and
72 hours:

.. code-block:: console

   pofff -i examples/single.toml -o output -t 24,48,72

Generate only the OPM Flow and workflow input files:

.. code-block:: console

   pofff -i examples/single.toml -o output -m files -f none

Display the available command-line options:

.. code-block:: console

   pofff --help

See :doc:`tutorial` for a guided simulation and comparison workflow,
:doc:`examples` for focused applications, and :doc:`command-line` for exact
syntax, accepted values, defaults, and option compatibility.

What can pofff do?
------------------

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Generate FluidFlower models

      Create Cartesian, tensor, and corner-point grids with geological facies,
      thickness maps, sources, observation sensors, and benchmark regions.

   .. grid-item-card:: Run configurable workflows

      Generate input files, run OPM Flow, process benchmark data, and create
      figures independently or as a connected workflow.

   .. grid-item-card:: Write and compare benchmark results

      Export sparse time-series and dense spatial CSV data, then compare local
      or external simulations with experimental and published results.

   .. grid-item-card:: Perform history matching

      Run ERT ensemble studies or Everest differential-evolution optimization,
      then extract and postprocess the best simulation.

.. toctree::
   :hidden:
   :maxdepth: 2

   introduction
   installation
   configuration_file
   tutorial
   examples
   publication
   command-line
   api
   output_folder
   contributing
   related
