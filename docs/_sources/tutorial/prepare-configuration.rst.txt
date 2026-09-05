Prepare the configuration
=========================

Goal
----

Review the configuration used for the tutorial and identify the settings that
control the physical model, simulation, benchmark evaluation, and figures.

Configuration
-------------

The tutorial uses ``results.toml``. The maintained configuration is available in
the repository publication folder:

.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/pofff/blob/main/publication/results.toml
         :color: primary
         :outline:
         :expand:

         View results.toml

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/pofff/main/publication/results.toml
         :color: primary
         :outline:
         :expand:

         View raw results.toml

The most important groups of settings are:

* ``flow``: OPM Flow executable and simulator flags;
* ``grid``, ``x``, and ``z``: grid representation and refinement;
* ``thickness`` and ``mult_thickness``: FluidFlower thickness model;
* ``temperature``, ``pressure``, and ``diffusion``: initial and fluid settings;
* ``sources`` and ``inj``: injection locations and schedule;
* ``facie1`` through ``facie6``: facies-dependent rock and saturation data;
* ``krw``, ``krn``, and ``cap``: saturation-function expressions.

See :doc:`../configuration_file` for accepted values, units, array layouts, and
validation rules.

Command
-------

No pofff command is required at this stage. If ``results.toml`` is not already
available locally, download it from the repository or copy it from the
``publication`` directory.

How it works
------------

When the tutorial command starts, pofff validates the TOML input, creates the
shared runtime configuration, generates the selected grid, assigns facies and
benchmark regions, and renders the OPM Flow input files.

Result
------

You should have a reviewed ``results.toml`` file and know which OPM Flow command
and computational resources it requests.

Next
----

Continue with :doc:`run-simulation`.
