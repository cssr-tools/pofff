Tutorial
========

.. image:: ./figs/readme.png

Add your results to the FluidFlower comparison
----------------------------------------------

This tutorial runs one complete pofff workflow and adds the resulting simulation
to the published FluidFlower comparisons. It is the recommended starting point
for users who already have OPM Flow installed and want to understand how model
generation, simulation, benchmark processing, and plotting connect.

The tutorial uses ``results.toml`` and writes everything below an output folder
named ``YOURS``. The output folder name is also used as the simulation label in
the comparison figures.

Prerequisites
-------------

Before starting, verify that:

* pofff is installed in the active Python environment;
* OPM Flow is available through the command configured by ``flow`` in
  ``results.toml``;
* the ``results.toml`` configuration is available in the current directory, or
  its path is supplied with ``--input``;
* LaTeX is installed if you want the recommended figure typography.

Check the command-line tools with:

.. code-block:: console

   pofff --help
   flow --help

.. note::

   The complete workflow can require substantial time and computational
   resources. Runtime depends on the grid, OPM Flow settings, requested output
   times, and available processors.

Tutorial sequence
-----------------

.. toctree::
   :maxdepth: 1
   :numbered:

   tutorial/prepare-configuration
   tutorial/run-simulation
   tutorial/inspect-data
   tutorial/generate-comparisons
   tutorial/interpret-results
   tutorial/reproduce
