Simulation setup
================

``flow``
--------

Non-empty OPM Flow command and flags. pofff adds the output directory. Include ``--enable-tuning=true`` when injection rows contain TUNING values.

``grid``
--------

Accepted values are ``cartesian``, ``tensor``, and ``corner-point``. Cartesian grids require one entry in ``x`` and ``z``. Corner-point grids require 11 entries in ``z``.

``thickness`` and ``mult_thickness``
------------------------------------

Select ``initial`` or ``final`` measured thickness, or provide a positive physical thickness. ``mult_thickness`` is a positive multiplier.

``x`` and ``z``
---------------

Positive integer refinement arrays. Their interpretation depends on ``grid``.

``temperature``, ``pressure``, and ``diffusion``
------------------------------------------------

``temperature`` contains bottom and top values [°C]. ``pressure`` is positive [Pa]. ``diffusion`` contains liquid and gas coefficients [m²/s].

``sources`` and ``inj``
-----------------------

``sources`` has two ``[x, z]`` rows [m]. Each injection row contains injection time [s], write time step [s], rates for sources 1 and 2 [kg/s], and optionally one TUNING string.
