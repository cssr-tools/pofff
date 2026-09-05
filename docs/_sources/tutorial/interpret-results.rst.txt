Interpret and improve the results
=================================

Goal
----

Use the generated comparisons and error table to identify model settings that
could improve agreement with the FluidFlower observations.

Configuration
-------------

Keep the original ``results.toml`` unchanged as a baseline. Create a copy before
changing grid resolution, facies properties, capillary pressure, relative
permeability, dispersion, diffusion, thickness, or injection controls.

Command
-------

Run a modified case in a different output directory so that the baseline is
preserved:

.. code-block:: console

   pofff -i modified_results.toml -o MODIFIED -m single -t 24,48,72,96,120 -f all

How it works
------------

Use the outputs together:

* time-series plots show the evolution of pressures and regional CO2 quantities;
* spatial maps show where gaseous and dissolved CO2 differ from experimental
  segmentations;
* sparse-data comparisons summarize selected benchmark observables;
* ``error_table_satmin-0.01_conmin-0.1.csv`` reports relative errors,
  Wasserstein distance, and their combined metric for the default thresholds.

.. tip::

   Change one physical or numerical choice at a time when diagnosing its effect.
   Use a separate output directory for every case so results remain reproducible.

Result
------

You should be able to identify whether disagreement is primarily temporal,
spatial, or associated with a specific benchmark region or observable.
Configurations producing better benchmark metrics are welcome in the repository
examples through the fork and pull request workflow.

Next
----

Continue with :doc:`reproduce` to run the maintained tutorial script.
