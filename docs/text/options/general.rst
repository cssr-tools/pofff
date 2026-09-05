General options
===============

The following options control the input configuration, output directory,
execution mode, benchmark evaluation, and segmentation thresholds.

.. program:: pofff

Input configuration
-------------------

.. option:: -i <file>, --input <file>

   TOML configuration file. The default is ``input.toml``.

   This option is not used by the ``fair`` and ``none`` modes.

Output directory
----------------

.. option:: -o <directory>, --output <directory>

   Output directory. The default is ``output``.

Figure generation
-----------------

.. option:: -f <mode>, --figures <mode>

   Select which benchmark figures to generate.

   Accepted values are:

   ``all``
      Generate all benchmark figures, including the Wasserstein-distance
      comparisons.

   ``basic``
      Generate the basic comparison figures without the slower
      Wasserstein-distance plots. This is the default.

   ``none``
      Do not generate figures.

Execution mode
--------------

.. option:: -m <mode>, --mode <mode>

   Select the pofff workflow to execute.

   Accepted values are:

   ``single``
      Generate the input files, run OPM Flow, process the benchmark data, and
      optionally generate figures. This is the default.

   ``files``
      Generate the input files without running OPM Flow.

   ``data``
      Generate benchmark data from existing simulation results.

   ``everest``
      Run an Everest optimization workflow.

   ``ert``
      Run an ERT ensemble history-matching workflow.

   ``fair``
      Generate the maintained FAIR benchmark comparisons using the
      workflow-specific settings.

   ``none``
      Skip model generation and simulation. Use this mode to postprocess
      existing benchmark-format results.

Evaluation times
----------------

.. option:: -t <hours>, --times <hours>

   Comma-separated positive finite evaluation times in hours.

   The default is ``0.25``. For example:

   .. code-block:: console

      pofff -t 24,48,72,96,120

Experimental realization
------------------------

.. option:: -e <experiment>, --experiment <experiment>

   Experimental FluidFlower realization used for comparison or history
   matching.

   Accepted values are ``C1``, ``C2``, ``C3``, ``C4``, and ``C5``. The default
   is ``C2``.

Minimum gas saturation
----------------------

.. option:: -s <threshold>, --minimumsaturation <threshold>

   Minimum gas saturation used when segmenting gaseous CO2.

   The value must be finite and lie between 0 and 1, inclusive. The default is
   ``1e-2``.

Minimum dissolved concentration
-------------------------------

.. option:: -c <threshold>, --minimumconcentration <threshold>

   Minimum concentration used when segmenting dissolved CO2.

   Accepted values are ``5e-2`` and ``1e-1``. The default is ``1e-1``.

Precomputed Wasserstein distances
---------------------------------

.. option:: -u <choice>, --use <choice>

   Control whether precomputed Wasserstein-distance values may be used when
   available.

   Accepted values are:

   ``1``
      Use precomputed values when available. This is the default.

   ``0``
      Recalculate the Wasserstein distances.
