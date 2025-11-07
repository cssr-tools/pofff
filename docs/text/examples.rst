********
Examples
********

For additional examples, see the scripts in the `tests <https://github.com/OPM/pyopmspe11/blob/main/tests>`_ folder.

===========
Hello world 
===========

The `examples <https://github.com/OPM/pyopmspe11/blob/main/examples>`_ folder contains a few configuration files
with low grid resolution and shorter injection times (for initial testing of the framework). For example, by executing:

.. code-block:: bash

    pofff -i single.toml -t 24,48,72 

The following is the figure `map_24h.png`. You can compare your example results to this figure to evaluate if your example ran correctly:

.. figure:: figs/map_24h.png

===========
Publication 
===========

The `publication <https://github.com/cssr-tools/pofff/blob/main/publication>`_ folder contains the configuration files used for the results in the
`pofff paper <https://arxiv.org/abs/2510.20614>`_. For example, running inside that folder:

.. code-block:: bash

    pofff -i results.toml -o results -m single -t 24,48,72,96,120 -f all

generates the figures in the paper in addition to the new simulation labeled as "YOURS", e.g., for the compare_all_time_series.png:

.. figure:: figs/compare_all_time_series.png

.. tip::
    
    One can always modify the plotting scripts to change the labels, colors, etc. 

We welcome pull request with your configuration files to the examples folder for cases with better results (less error in the error_table_satmin-0.01_conmin-0.1.csv).

To generate the figures in the paper (including the appendix) without adding a new simulation, this can be achieved by:

.. code-block:: bash

    pofff -m fair
    pofff -m fair -c 0.05

where fair attempts to align with `these principles <https://www.nature.com/articles/sdata201618>`_. 
