***********
Publication
***********

This section adds details in the steps to reproduce the figures in the `pofff paper <https://link.springer.com/article/10.1007/s11242-025-02275-0>`_.

To this end, we use our friend `plopm <https://github.com/cssr-tools/plopm>`_. All commands are executed from the pofff main directory,
and the figures are saved in new folders corresponding to the figure number.

.. tip::
    You can install `plopm <https://github.com/cssr-tools/plopm>`_ by executing in the terminal:
    
    .. code-block:: bash
        
        pip install git+https://github.com/cssr-tools/plopm.git

Figure 3:

.. code-block:: bash

    pofff -i examples/input.toml -o figure3 -f none
    plopm -i figure3/FIGURe3 -c '101;64;147 81;124;66 181;73;57 193;127;97 127;148;191 193;147;56' -cticks '[G, F, E, D, C, ESF]' -v 'pvtnum - 1 - satnum' -grid 'black,1e-2' -remove 1,1,0,1 -d 20,15 -o figure3 -save figure3a -f 20 -clabel 'Sand'
    plopm -i figure3/FIGURe3 -v 'multx * 1.75' -grid 'black,1e-2' -remove 1,1,0,1 -d 20,15 -clabel 'Thickness map [cm]' -cformat .2f -cnum 5 -f 20 -o figure3 -save figure3b

Figure 4 requires running the SPE11A cases using `pyopmspe11 <https://github.com/OPM/pyopmspe11>`_, which uses the simulation grid. You might need to edit the configuration files to
adjust the computational resources to your machine (e.g., `r3_cp_1cmish_capmax2500Pa.toml <https://github.com/OPM/pyopmspe11/blob/main/benchmark/spe11a/r3_cp_1cmish_capmax2500Pa.toml>`_ is run with 32 cpus).

.. tip::
    You can install `pyopmspe11 <https://github.com/OPM/pyopmspe11>`_ by executing in the terminal:
    
    .. code-block:: bash
        
        pip install git+https://github.com/OPM/pyopmspe11.git

.. code-block:: bash

    mkdir figure4 && cd figure4
    curl -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/benchmark/spe11a/r3_cp_1cmish_capmax2500Pa.toml
    curl -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/benchmark/spe11a/r3_cp_1cmish_capmax2500Pa.toml
    curl -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/benchmark/spe11a/r4_Cart_1mm_capmax2500Pa.toml
    curl -O https://raw.githubusercontent.com/OPM/pyopmspe11/refs/heads/main/benchmark/spe11a/r5_Cart_1mm_capmax2500Pa_strictol.toml
    pyopmspe11 -i r2_Cart_1cm_capmax2500Pa.toml -o r2_Cart_1cm_capmax2500Pa -t 1 -r 280,1,120 -w 0.16666666666666666
    pyopmspe11 -i r3_cp_1cmish_capmax2500Pa.toml -o r3_cp_1cmish_capmax2500Pa -t 1 -r 280,1,120 -w 0.16666666666666666
    pyopmspe11 -i r4_Cart_1mm_capmax2500Pa.toml -o r4_Cart_1mm_capmax2500Pa -t 1 -r 280,1,120 -w 0.16666666666666666
    pyopmspe11 -i r5_Cart_1mm_capmax2500Pa_strictol.toml -o r5_Cart_1mm_capmax2500Pa_strictol -t 1 -r 280,1,120 -w 0.16666666666666666
    plopm -v xco2l -r 53 -mask satnum -maskthr 7e-5 -i 'r2_Cart_1cm_capmax2500Pa/flow/R2_CART_1CM_CAPMAX2500PA r3_cp_1cmish_capmax2500Pa/flow/R3_CP_1CMISH_CAPMAX2500PA r4_Cart_1mm_capmax2500Pa/flow/R4_CART_1MM_CAPMAX2500PA r5_Cart_1mm_capmax2500Pa_strictol/flow/R5_CART_1MM_CAPMAX2500PA_STRICTOL' -cnum 3 -xlnum 8 -clabel 'OPM results for SPE11A: CO$_2$ mass fraction (liquid phase) after 2 days' -d 16,6.5 -t "(a) Cartesian grid 1cm  (b) Corner-point grid 1cmish  (c) Cartesian grid 1mm  (d) Cartesian grid 1mm stricter tolerances" -yunits cm -xunits cm -yformat .0f -xformat .0f -f 16 -save figure4 -cformat .2e -suptitle 0 -subfigs 2,2 -cbsfax 0.35,0.97,0.3,0.02 -delax 1 -c '#9ca245 #9da347 #9fa44a #a0a64d #a2a750 #a3a953 #a5aa56 #a6ac59 #a8ad5c #a9af5f #abb062 #adb164 #aeb367 #b0b46a #b1b66d #b3b770 #b4b973 #b6ba76 #b7bc79 #b9bd7c #babf7f #bcc082 #bec184 #bfc387 #c1c48a #c2c68d #c4c790 #c5c993 #c7ca96 #c8cc99 #cacd9c #cbcf9f #cdd0a2 #cfd1a4 #d0d3a7 #d2d4aa #d3d6ad #d5d7b0 #d6d9b3 #d8dab6 #d9dcb9 #dbddbc #dcdfbf #dee0c1 #e0e1c4 #e1e3c7 #e3e4ca #e4e6cd #e6e7d0 #e7e9d3 #e9ead6 #eaecd9 #eceddc #edefdf #eff0e1 #f1f1e4 #f2f3e7 #f4f4ea #f5f6ed #f7f7f0 #f8f9f3 #fafaf6 #fbfcf9 #fdfdfc #ffffff #fefbfb #fdf7f7 #fcf3f3 #fbefef #faebeb #f9e7e7 #f8e3e3 #f7e0e0 #f6dcdc #f5d8d8 #f4d4d4 #f3d0d0 #f2cccc #f1c8c8 #f0c5c5 #efc1c1 #eebdbd #edb9b9 #ecb5b5 #ebb1b1 #eaadad #e9aaaa #e8a6a6 #e7a2a2 #e69e9e #e59a9a #e49696 #e39292 #e28f8f #e18b8b #e08787 #df8383 #de7f7f #dd7b7b #dc7777 #db7474 #da7070 #d96c6c #d86868 #d76464 #d66060 #d55c5c #d45959 #d35555 #d25151 #d14d4d #d04949 #cf4545 #ce4141 #cd3e3e #cc3a3a #cb3636 #ca3232 #c92e2e #c82a2a #c72626 #c62323 #c51f1f #c41b1b #c31717 #c21313 #c10f0f #c00b0b'

A similar figure without the need of running the simulations (not showing the sands in the background and using the reporting grid) can be obtained by downloading the SPE11A benchmark data in csv format available at 
`this website <https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4750>`_ (the submitted benchmark data does not include the `r5_Cart_1mm_capmax2500Pa_strictol.toml <https://github.com/OPM/pyopmspe11/blob/main/benchmark/spe11a/r5_Cart_1mm_capmax2500Pa_strictol.toml>`_ results):

.. code-block:: bash

    mkdir figure4 && cd figure4
    curl -L -O https://darus.uni-stuttgart.de/api/access/datafile/375719
    unzip 375719
    curl -L -O https://darus.uni-stuttgart.de/api/access/datafile/375716
    unzip 375716
    curl -L -O https://darus.uni-stuttgart.de/api/access/datafile/375707
    unzip 375707
    plopm -v xco2l -i 'spe11a/opm2/spe11a_spatial_map_48h spe11a/opm3/spe11a_spatial_map_48h spe11a/opm4/spe11a_spatial_map_48h' -csv "1,2,5;1,2,5;1,2,5" -c cet_diverging_gwr_55_95_c38 -cnum 3 -xlnum 8 -clabel 'OPM results for SPE11A: CO$_2$ mass fraction (liquid phase) after 2 days' -d 16,6.5 -t "(a) Cartesian grid 1cm  (b) Corner-point grid 1cmish  (c) Cartesian grid 1mm" -yunits cm -xunits cm -yformat .0f -xformat .0f -f 16 -save figure4ish -cformat .2e -suptitle 0 -subfigs 2,2 -cbsfax 0.35,0.97,0.3,0.02 -delax 1

Figures 5 (g, h, i), 6, 7, and 8 (in addition, the values on Table 4 are obtained from the generated error_table_satmin-0.01_conmin-0.1.csv):

.. code-block:: bash

    mkdir figures5-8 && cd figures5-8
    pofff -m fair

where fair attempts to aling with `these principles <https://www.nature.com/articles/sdata201618>`_.

Similarly, Figures 10 (g, h, i) and 11 (in addition, the values on Table 5 are obtained from the generated error_table_satmin-0.01_conmin-0.05.csv)

.. code-block:: bash

    mkdir figures10-11 && cd figures10-11
    pofff -m fair -c 0.05
 
See the **Adding your results** subsection in the :doc:`examples <./examples>` to compare your customized simulation results to the paper results.

For the spatial maps of CO2 concentration in Figures 5d to 5f:

.. code-block:: bash

    pofff -i publication/results.toml -o figures5d-f -m single -t 24,48,72,96,120
    plopm -i figures5d-f/FIGURES5D-F -v xco2l -o figures5d-f -remove 1,1,1,1 -r 3 -save figure5d -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
    plopm -i figures5d-f/FIGURES5D-F -v xco2l -o figures5d-f -remove 1,1,1,1 -r 5 -save figure5e -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
    plopm -i figures5d-f/FIGURES5D-F -v xco2l -o figures5d-f -remove 1,1,1,1 -r 7 -save figure5f -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'

Similarly, for the spatial maps of CO2 concentration in Figures 10d to 10f:

.. code-block:: bash

    pofff -i publication/appendixb.toml -o figures10d-f -c '5e-2' -m single -t 24,48,72,96,120
    plopm -i figures10d-f/FIGURES10D-F -v xco2l -o figures10d-f -remove 1,1,1,1 -r 3 -save figure10d -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
    plopm -i figures10d-f/FIGURES10D-F -v xco2l -o figures10d-f -remove 1,1,1,1 -r 5 -save figure10e -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
    plopm -i figures10d-f/FIGURES10D-F -v xco2l -o figures10d-f -remove 1,1,1,1 -r 7 -save figure10f -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'

.. tip::

    If your OPM flow supports MPI, then to speed up the simulations you could change Line 3 in `results.toml <https://github.com/cssr-tools/pofff/blob/main/publication/results.toml>`_
    and `appendixb.toml <https://github.com/cssr-tools/pofff/blob/main/publication/appendixb.toml>`_ to:

    .. code-block:: bash
        
        flow="mpirun -np 8 flow --newton-min-iterations=1 --solver-max-restarts=20 --time-step-control=newtoniterationcount --solver-growth-factor=1.6 --linear-solver=cpr_trueimpes --time-step-control-growth-rate=1.1 --solver-restart-factor=0.5 --time-step-control-decay-rate=0.65 --enable-opm-rst-file=true"

    The values in the flags were manually set trying to speed up the simulations. Then, you could also try to run the cases with different flags.

For the Computational details results in the Appendix C, we use the templated configuration file `appendixc.mako <https://github.com/cssr-tools/pofff/blob/main/publication/appendixc.mako>`_,
in combination to Python commands, which gives flexibility to generate the different cases.  

The Wasserstein distance (obtained from the generated error_table_satmin-0.01_conmin-0.1.csv) for the 
base case and random seed for the sensitivity study regarding setup choices in Table 8 can be generated by executing the 
`sensitivity.py <https://github.com/cssr-tools/pofff/blob/main/publication/sensitivity.py>`_ script (if you have a Mac as well, then execute the script in 
there to see the sensitivity to the operative system). For example, the content of this Python script is the following:

.. code-block:: python

    import subprocess
    from mako.template import Template

    mytemplate = Template(filename="appendixc.mako")
    for case, rng in zip(["base", "rng"], [7, 11]):
        # Modify the number of cores according to your resources
        var = {"cores": 64, "rng": rng, "cnv": 1e-2, "cnv_relaxed": 1}
        filledtemplate = mytemplate.render(**var)
        with open(
            f"{case}.toml",
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)
        subprocess.run(
            [
                "pofff",
                "-i", f"{case}.toml",
                "-o", case,
                "-m", "everest",
                "-t", "24,48,72,96,120",
                "-f", "all",
            ],
            check=True,
        )

The values in Table 7 and Figure 8 can be generated by (increase or decrease the number of cores to adapt to your interest and computer limitations):

.. code-block:: bash

    cd publication && python3 profiling.py

Finally, for accuracy-time trade-off Table 9 you can run:

.. code-block:: bash

    cd publication && python3 accuracy.py

.. warning::
    
    These scripts are set to run with 64 cores, then you should edit them if your machine has less available cpus.
