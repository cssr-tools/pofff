Reproduce the tutorial
======================

Goal
----

Run the maintained repository script that reproduces the Add your results
workflow.

Configuration
-------------

Run the script from the pofff repository root. Review its commands and
configuration paths before execution, especially on systems with limited CPU or
memory resources.

Command
-------

.. code-block:: console

   . ./tests/scripts/docs_adding_your_results.sh

How it works
------------

The script runs the documented simulation and comparison workflow using the
maintained repository inputs. It provides a reproducible check that the tutorial
commands remain aligned with the current source code.

Result
------

The generated output should contain the benchmark CSV products and comparison
figures described in the previous lessons.

Reproducibility links
---------------------

.. grid:: 1 1 3 3
   :gutter: 2

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/pofff/blob/main/tests/scripts/docs_adding_your_results.sh
         :color: primary
         :outline:
         :expand:

         View script

   .. grid-item::

      .. button-link:: https://raw.githubusercontent.com/cssr-tools/pofff/main/tests/scripts/docs_adding_your_results.sh
         :color: primary
         :outline:
         :expand:

         View raw script

   .. grid-item::

      .. button-link:: https://github.com/cssr-tools/pofff/blob/main/publication/results.toml
         :color: secondary
         :outline:
         :expand:

         View results.toml

Where to continue
-----------------

* Use :doc:`../examples` for external-simulator, history-matching, and plopm workflows.
* Use :doc:`../publication` to reproduce the paper figures and tables.
* Use :doc:`../command-line` for exact CLI choices and defaults.
* Use :doc:`../configuration_file` for the complete TOML reference.
