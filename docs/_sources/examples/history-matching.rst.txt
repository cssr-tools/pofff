History matching with ERT and Everest
=====================================

Overview
--------

Set ``--mode`` to ``ert`` or ``everest`` to run history matching. These modes
require additional TOML variables, including the parameters to history match,
the number of parallel runs, resource limits, and a random seed when
reproducibility is required.

Refer to the external references for the underlying configuration keywords:

* `Everest configuration reference
  <https://everest.readthedocs.io/en/latest/configuration/reference.html>`__
* `ERT configuration keyword reference
  <https://ert.readthedocs.io/en/latest/reference/configuration/keywords.html>`__

Everest example
---------------

The following command runs the final history-matching iteration used in the
pofff paper with ``everest_iter_3.toml``:

.. code-block:: console

   pofff -i everest_iter_3.toml -o everest_iter_3 -m everest -t 24,48,72,96,120 -f all

.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/pofff/blob/main/publication/everest_iter_3.toml
         :color: primary
         :outline:
         :expand:

         View everest_iter_3.toml

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/pofff/main/publication/everest_iter_3.toml
         :color: primary
         :outline:
         :expand:

         View raw everest_iter_3.toml

.. warning::

   The publication configuration uses ``cores = 50`` and
   ``max_function_evaluations = 200000``. When running it locally, decrease the
   number of parallel runs and maximum function evaluations to match the CPU,
   memory, and time available on your system.

History-matching parameters
---------------------------

The possible history-matching variables include the supported facies properties
for facies 1 through 6, for example ``permx2`` and ``pen5``. The current
configuration model supports the numbered properties ``poroN``, ``permN``,
``permxN``, ``permyN``, ``permzN``, ``dispercN``, ``swiN``, ``sniN``,
``penN``, ``nkrwN``, ``nkrnN``, ``npeN``, ``threN``, and ``npntN`` where
applicable. Isotropic permeability can be selected with a variable such as
``perm3``. The ``thicknessmult`` variable scales the thickness map.

.. note::

   History-matching values use different layouts for the two workflows. ERT
   parameters contain a distribution name and two parameters. Everest
   parameters contain ``[initial, minimum, maximum, scale]``. See
   :doc:`../configuration_file` for the maintained TOML reference.

Additional examples
-------------------

Additional ERT and Everest examples are available in the pofff repository:

* `Tests <https://github.com/cssr-tools/pofff/tree/main/tests>`__
* `Publication configurations
  <https://github.com/cssr-tools/pofff/tree/main/publication>`__
* `Configuration data class
  <https://github.com/cssr-tools/pofff/blob/main/src/pofff/config/config.py>`__

Generated configurations and direct execution
---------------------------------------------

pofff exposes the most commonly used ERT and Everest options through TOML. After
pofff generates ``everest.yml`` or ``ert.txt``, you may add supported keywords
that are not yet exposed by pofff and then run the corresponding Everest or ERT
command-line executable directly.

Please raise a `pofff issue <https://github.com/cssr-tools/pofff/issues>`_ when a
useful TOML keyword is missing, so it can be considered for the maintained
configuration model.

Separate generation, execution, and postprocessing
--------------------------------------------------

After ERT or Everest has run, pofff can postprocess the existing results and
generate figures without starting another history-matching study:

.. code-block:: console

   pofff -o HISTORY_MATCHING_OUTPUT -m none -t 24,48,72,96,120 -f all

The publication ``profiling.py`` workflow demonstrates how to separate file
generation, Everest execution, and postprocessing:

.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/pofff/blob/main/publication/profiling.py
         :color: primary
         :outline:
         :expand:

         View profiling.py

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/pofff/main/publication/profiling.py
         :color: primary
         :outline:
         :expand:

         View raw profiling.py

Outputs
-------

ERT and Everest produce different runtime directories, but both postprocessing
workflows create a ``figures/best_simulation`` folder containing the closest or
optimal simulation and its benchmark tables and figures. See
:doc:`../output_folder` for the output layouts.

.. button-ref:: ../examples
   :color: primary

   Back to examples gallery
