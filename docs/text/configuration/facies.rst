Facies and saturation functions
===============================

Six required ``facieN`` tables define permeability, porosity, dispersion, residual saturations, capillary entry pressure, Corey exponents, capillary exponent, threshold, and table resolution.

Required keys
-------------

For each facies ``N``: ``permxN``, ``permzN``, ``poroN``, ``dispercN``, ``swiN``, ``sniN``, ``penN``, ``nkrwN``, ``nkrnN``, ``npeN``, ``threN``, and ``npntN``. ``npntN`` is an integer of at least 2. Porosity and residual saturations lie in [0, 1], and ``swiN + sniN <= 1``.

``krw``, ``krn``, and ``cap``
-----------------------------

These required strings are valid Python expressions used to generate wetting relative permeability, non-wetting relative permeability, and capillary-pressure tables. ``threN`` prevents evaluation too close to a singular endpoint, and ``npntN`` controls the number of table points.
