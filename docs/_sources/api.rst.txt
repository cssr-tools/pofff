=================
pofff Python API
=================

The main script for the **pofff** executable is located in the core folder. The data from the
FluidFlower benchmark is located in the fluidflower forlder, which is downloaded and modified
from https://github.com/fluidflower. The geology folder contains the geometry to generate the
corner-point grid. The different jobs called by ERT and everest are located in the jobs folder.
The templeates folder contains mako files to generate the input decks. The utils folder has
scripts to comunicate all parts in the framework. Finally, the visualization folder hosts
scripts to postprocess the data.

.. figure:: figs/content.png

   Files in the pofff package.

.. include:: modules.rst
