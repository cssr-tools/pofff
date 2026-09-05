Hello world
===========

Overview
--------

The repository `examples folder
<https://github.com/cssr-tools/pofff/tree/main/examples>`_ contains configuration
files with low grid resolution and short simulation times for initial testing.
This example runs one of those small cases and generates benchmark products at
24, 48, and 72 hours.

Command
-------

.. code-block:: console

   pofff -i single.toml -t 24,48,72

Result
------

The following figure is ``map_24h.png``. Compare your generated result with this
figure to check that the example ran correctly.

.. figure:: ../figs/map_24h.png
   :alt: FluidFlower simulation and experimental contours after 24 hours

   Spatial benchmark map after 24 hours.

Reproduce the example
---------------------

Run the maintained documentation script from the repository root:

.. code-block:: console

   . ./tests/scripts/docs_hello_world.sh

.. grid:: 1 1 2 2
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/pofff/blob/main/tests/scripts/docs_hello_world.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/pofff/main/tests/scripts/docs_hello_world.sh
         :color: primary
         :outline:
         :expand:

         View raw script

.. button-ref:: ../examples
   :color: primary

   Back to examples gallery
