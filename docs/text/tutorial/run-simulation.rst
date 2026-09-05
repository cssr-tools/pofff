Run the simulation
==================

Goal
----

Generate the FluidFlower model, run OPM Flow, process benchmark data, and create
all supported comparison figures with one command.

Configuration
-------------

Use the reviewed ``results.toml`` configuration. The tutorial requests benchmark
output at 24, 48, 72, 96, and 120 hours and enables all figure products.

Command
-------

.. code-block:: console

   pofff -i results.toml -o YOURS -m single -t 24,48,72,96,120 -f all

How it works
------------

The command performs the connected workflow in sequence:

#. Generate the OPM deck, include files, grid properties, and saturation tables.
#. Run OPM Flow with the executable and flags specified by ``flow``.
#. Convert the simulation results to benchmark time-series and spatial CSV data.
#. Calculate benchmark metrics for the requested experimental realization.
#. Generate the basic comparison figures and the Wasserstein-distance products
   enabled by ``-f all``.

The output directory is named ``YOURS``. pofff also uses this name to label the
new simulation in comparison figures.

Result
------

The ``YOURS`` directory contains the generated simulation input, OPM Flow
results, benchmark CSV files, metrics, and figures. See
:doc:`../output_folder` for the complete output organization.

Next
----

Continue with :doc:`inspect-data`.
