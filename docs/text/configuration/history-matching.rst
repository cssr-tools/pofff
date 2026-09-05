ERT and Everest settings
========================

History matching requires ``cores``, ``min_realizations_success``, and at least one facies or thickness parameter.

ERT
---

ERT additionally requires ``ertargs``, ``ensembles``, ``enkf_alpha``, and positive ``errors``. Optional ``random_seed`` controls reproducibility.

Everest
-------

Everest requires ``max_function_evaluations`` and ``popsize``. Supported differential-evolution options include ``strategy``, ``maxiter``, ``tol``, ``mutation``, ``recombination``, ``rng``, ``disp``, ``polish``, ``init``, ``atol``, ``updating``, ``workers``, ``x0``, ``integrality``, and ``vectorized``.

History-matching parameters
---------------------------

ERT parameters use a distribution name and two parameters. Everest parameters use ``[initial, minimum, maximum, scale]``. Facies properties may be selected by their numbered key, isotropic permeability may use ``permN``, and ``thicknessmult`` controls the thickness multiplier.

``monotonic = true`` only has an effect when at least two optimized variables form a comparable same-property facies sequence.
