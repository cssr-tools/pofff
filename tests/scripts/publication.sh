NCPUS=${1:-64}
WHR="$PWD"
OUT="test_outputs/publication"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_plopm.sh
# Figure 3a and 3b
pofff -i examples/input.toml -o $OUT/figure3 -f none
plopm -i $OUT/figure3/FIGURE3 -c '101;64;147 81;124;66 181;73;57 193;127;97 127;148;191 193;147;56' -cticks '[G, F, E, D, C, ESF]' -v 'pvtnum - 1 - satnum' -grid 'black,1e-2' -remove 1,1,0,1 -d 20,15 -o $OUT/figure3 -save _figure3a -f 20 -clabel 'Sand'
plopm -i $OUT/figure3/FIGURE3 -v 'multx * 1.75' -grid 'black,1e-2' -remove 1,1,0,1 -d 20,15 -clabel 'Thickness map [cm]' -cformat .2f -cnum 5 -f 20 -o $OUT/figure3 -save _figure3b
# Figure 4
mkdir $OUT/figure4 && cd $OUT/figure4
curl -L -O https://darus.uni-stuttgart.de/api/access/datafile/375719
unzip 375719 && rm 375719
curl -L -O https://darus.uni-stuttgart.de/api/access/datafile/375716
unzip 375716 && rm 375716
curl -L -O https://darus.uni-stuttgart.de/api/access/datafile/375707
unzip 375707 && rm 375707
plopm -v xco2l -i 'spe11a/opm2/spe11a_spatial_map_48h spe11a/opm3/spe11a_spatial_map_48h spe11a/opm4/spe11a_spatial_map_48h' -csv "1,2,5;1,2,5;1,2,5" -c cet_diverging_gwr_55_95_c38 -cnum 3 -xlnum 8 -clabel 'OPM results for SPE11A: CO$_2$ mass fraction (liquid phase) after 2 days' -d 16,6.5 -t "(a) Cartesian grid 1cm  (b) Corner-point grid 1cmish  (c) Cartesian grid 1mm" -yunits cm -xunits cm -yformat .0f -xformat .0f -f 16 -save _figure4ish -cformat .2e -suptitle 0 -subfigs 2,2 -cbsfax 0.35,0.97,0.3,0.02 -delax 1
cd $WHR
# Figures 5-8 and Table 4 (error_table_satmin-0.01_conmin-0.1.csv)
mkdir $OUT/table4_figures5-8 && cd $OUT/table4_figures5-8
pofff -m fair &
cd $WHR
# Figures 10-11 and Table 5 (error_table_satmin-0.01_conmin-0.05.csv)
mkdir $OUT/table5_figures10-11 && cd $OUT/table5_figures10-11
pofff -m fair -c 0.05
cd $WHR
# Figures 5d to 5f:
mkdir $OUT/figures5d-f
cp "publication/results.toml" $OUT/figures5d-f/results.toml
if [ "$NCPUS" -eq 16 ]; then
    sed -i.bak "s/140/70/g" $OUT/figures5d-f/results.toml && rm -f $OUT/figures5d-f/results.toml.bak
    sed -i.bak "s/7,5,5,5,5,5,5,8,10,9,5/4,3,3,3,3,3,3,4,5,5,3/g" $OUT/figures5d-f/results.toml && rm -f $OUT/figures5d-f/results.toml.bak
fi
sed -i.bak "s/flow --/mpirun -np $NCPUS flow --partition-method=metis --edge-weights-method=logtrans --/g" $OUT/figures5d-f/results.toml && rm -f $OUT/figures5d-f/results.toml.bak
pofff -i $OUT/figures5d-f/results.toml -o $OUT/figures5d-f -m single -t 24,48,72,96,120
plopm -i $OUT/figures5d-f/FIGURES5D-F -v xco2l -o $OUT/figures5d-f -remove 1,1,1,1 -r 3 -save _figure5d -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
plopm -i $OUT/figures5d-f/FIGURES5D-F -v xco2l -o $OUT/figures5d-f -remove 1,1,1,1 -r 5 -save _figure5e -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
plopm -i $OUT/figures5d-f/FIGURES5D-F -v xco2l -o $OUT/figures5d-f -remove 1,1,1,1 -r 7 -save _figure5f -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
# Figures 10d to 10f:
mkdir $OUT/figures10d-f
cp "publication/appendixb.toml" $OUT/figures10d-f/appendixb.toml
if [ "$NCPUS" -eq 16 ]; then
    sed -i.bak "s/140/70/g" $OUT/figures10d-f/appendixb.toml && rm -f $OUT/figures10d-f/appendixb.toml.bak
    sed -i.bak "s/7,5,5,5,5,5,5,8,10,9,5/4,3,3,3,3,3,3,4,5,5,3/g" $OUT/figures10d-f/appendixb.toml && rm -f $OUT/figures10d-f/appendixb.toml.bak
fi
sed -i.bak "s/flow --/mpirun -np $NCPUS flow --partition-method=metis --edge-weights-method=logtrans --/g" $OUT/figures10d-f/appendixb.toml && rm -f $OUT/figures10d-f/appendixb.toml.bak
pofff -i $OUT/figures10d-f/appendixb.toml -o $OUT/figures10d-f -c '5e-2' -m single -t 24,48,72,96,120
plopm -i $OUT/figures10d-f/FIGURES10D-F -v xco2l -o $OUT/figures10d-f -remove 1,1,1,1 -r 3 -save _figure10d -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
plopm -i $OUT/figures10d-f/FIGURES10D-F -v xco2l -o $OUT/figures10d-f -remove 1,1,1,1 -r 5 -save _figure10e -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
plopm -i $OUT/figures10d-f/FIGURES10D-F -v xco2l -o $OUT/figures10d-f -remove 1,1,1,1 -r 7 -save _figure10f -c '#636b45 #636b45 #fffd00 #fffc00 #fffb00 #fffa00 #fff900 #fff800 #fff700 #fff600 #fff500 #fff400 #fff300 #fff200 #fff100 #fff000 #ffef00 #ffee00 #ffed00 #ffec00 #ffeb00 #ffea00 #ffe900 #ffe800 #ffe700 #ffe600 #ffe500 #ffe400 #ffe300 #ffe200 #ffe100 #ffe000 #ffdf00 #ffde00 #ffdd00 #ffdc00 #ffdb00 #ffda00 #ffd900 #ffd800 #ffd700 #ffd600 #ffd500 #ffd400 #ffd300 #ffd200 #ffd100 #ffd000 #ffcf00 #ffce00 #ffcd00 #ffcc00 #ffcb00 #ffca00 #ffc900 #ffc800 #ffc700 #ffc600 #ffc500 #ffc400 #ffc300 #ffc200 #ffc100 #ffc000 #ffbf00 #ffbe00 #ffbd00 #ffbc00 #ffbb00 #ffba00 #ffb900 #ffb800 #ffb700 #ffb600 #ffb500 #ffb400 #ffb300 #ffb200 #ffb100 #ffb000 #ffaf00 #ffae00 #ffad00 #ffac00 #ffab00 #ffaa00 #ffa900 #ffa800 #ffa700 #ffa600 #ffa500 #ffa400 #ffa300 #ffa200 #ffa100 #ffa000 #ff9f00 #ff9e00 #ff9d00 #ff9c00 #ff9b00 #ff9a00 #ff9900 #ff9800 #ff9700 #ff9600 #ff9500 #ff9400 #ff9300 #ff9200 #ff9100 #ff9000 #ff8f00 #ff8e00 #ff8d00 #ff8c00 #ff8b00 #ff8a00 #ff8900 #ff8800 #ff8700 #ff8600 #ff8500 #ff8400 #ff8300 #ff8200 #ff8100 #ff8000 #ff7f00 #ff7e00 #ff7d00 #ff7c00 #ff7b00 #ff7a00 #ff7900 #ff7800 #ff7700 #ff7600 #ff7500 #ff7400 #ff7300 #ff7200 #ff7100 #ff7000 #ff6f00 #ff6e00 #ff6d00 #ff6c00 #ff6b00 #ff6a00 #ff6900 #ff6800 #ff6700 #ff6600 #ff6500 #ff6400 #ff6300 #ff6200 #ff6100 #ff6000 #ff5f00 #ff5e00 #ff5d00 #ff5c00 #ff5b00 #ff5a00 #ff5900 #ff5800 #ff5700 #ff5600 #ff5500 #ff5400 #ff5300 #ff5200 #ff5100 #ff5000 #ff4f00 #ff4e00 #ff4d00 #ff4c00 #ff4b00 #ff4a00 #ff4900 #ff4800 #ff4700 #ff4600 #ff4500 #ff4400 #ff4300 #ff4200 #ff4100 #ff4000 #ff3f00 #ff3e00 #ff3d00 #ff3c00 #ff3b00 #ff3a00 #ff3900 #ff3800 #ff3700 #ff3600 #ff3500 #ff3400 #ff3300 #ff3200 #ff3100 #ff3000 #ff2f00 #ff2e00 #ff2d00 #ff2c00 #ff2b00 #ff2a00 #ff2900 #ff2800 #ff2700 #ff2600 #ff2500 #ff2400 #ff2300 #ff2200 #ff2100 #ff2000 #ff1f00 #ff1e00 #ff1d00 #ff1c00 #ff1b00 #ff1a00 #ff1900 #ff1800 #ff1700 #ff1600 #ff1500 #ff1400 #ff1300 #ff1200 #ff1100 #ff1000 #ff0f00 #ff0e00 #ff0d00 #ff0c00 #ff0b00 #ff0a00 #ff0900 #ff0800 #ff0700 #ff0600 #ff0500 #ff0400 #ff0300 #ff0200 #ff0100 #ff0000'
# Table 7 and Figure 12
mkdir $OUT/table7_figure12 && cd $OUT/table7_figure12
cp $WHR/publication/profiling.py .
cp $WHR/publication/appendixc.mako .
if [ "$NCPUS" -eq 16 ]; then
    sed -i.bak "s/64, 32, 16/16/g" profiling.py && rm -f profiling.py.bak
    sed -i.bak "s/popsize = 16/popsize = 4/g" appendixc.mako && rm -f appendixc.mako.bak
    sed -i.bak "s/max_function_evaluations = 64/max_function_evaluations = 16/g" appendixc.mako && rm -f appendixc.mako.bak
    sed -i.bak "s/140/70/g" appendixc.mako && rm -f appendixc.mako.bak
    sed -i.bak "s/7,5,5,5,5,5,5,8,10,9,5/4,3,3,3,3,3,3,4,5,5,3/g" appendixc.mako && rm -f appendixc.mako.bak
fi
python3 profiling.py
cd $WHR
# Table 8
mkdir $OUT/table8 && cd $OUT/table8
cp $WHR/publication/sensitivity.py .
cp $WHR/publication/appendixc.mako .
if [ "$NCPUS" -eq 16 ]; then
    sed -i.bak "s/64/16/g" sensitivity.py && rm -f sensitivity.py.bak
    sed -i.bak "s/popsize = 16/popsize = 4/g" appendixc.mako && rm -f appendixc.mako.bak
    sed -i.bak "s/max_function_evaluations = 64/max_function_evaluations = 16/g" appendixc.mako && rm -f appendixc.mako.bak
    sed -i.bak "s/140/70/g" appendixc.mako && rm -f appendixc.mako.bak
    sed -i.bak "s/7,5,5,5,5,5,5,8,10,9,5/4,3,3,3,3,3,3,4,5,5,3/g" appendixc.mako && rm -f appendixc.mako.bak
fi
python3 sensitivity.py
cd $WHR
# Table 9
mkdir $OUT/table9 && cd $OUT/table9
cp $WHR/publication/accuracy.py .
cp $WHR/publication/appendixc.mako .
python3 accuracy.py
cd $WHR

files="
test_outputs/publication/figure3/_figure3a.png
test_outputs/publication/figure3/_figure3b.png
test_outputs/publication/figure4/_figure4ish.png
test_outputs/publication/figures5d-f/_figure5d.png
test_outputs/publication/figures5d-f/_figure5e.png
test_outputs/publication/figures5d-f/_figure5f.png
test_outputs/publication/figures10d-f/_figure10d.png
test_outputs/publication/figures10d-f/_figure10e.png
test_outputs/publication/figures10d-f/_figure10f.png
test_outputs/publication/table4_figures5-8/output/zoom_means_segmented_snapshots_satmin-0.01_conmin-0.1.png
test_outputs/publication/table4_figures5-8/output/compare_all_time_series.png
test_outputs/publication/table4_figures5-8/output/map_24h.png
test_outputs/publication/table4_figures5-8/output/map_72h.png
test_outputs/publication/table4_figures5-8/output/map_120h.png
test_outputs/publication/table4_figures5-8/output/error_table_satmin-0.01_conmin-0.1.csv
test_outputs/publication/table4_figures5-8/output/sparse_data.csv
test_outputs/publication/table5_figures10-11/output/zoom_means_segmented_snapshots_satmin-0.01_conmin-0.05.png
test_outputs/publication/table5_figures10-11/output/map_24h.png
test_outputs/publication/table5_figures10-11/output/map_72h.png
test_outputs/publication/table5_figures10-11/output/map_120h.png
test_outputs/publication/table5_figures10-11/output/error_table_satmin-0.01_conmin-0.05.csv
test_outputs/publication/table5_figures10-11/output/sparse_data.csv
test_outputs/publication/table7_figure12/profiling/profiling_ncpu_16.txt
test_outputs/publication/table7_figure12/profiling/figure12.png
test_outputs/publication/table8/sensitivity/table8.txt
test_outputs/publication/table9/accuracy/accuracy-time-trade-offs.txt
"

missing_file="test_outputs/missing_publication_files.txt"
missing=0

rm -f "$missing_file"

printf '%s\n' "$files" | while IFS= read -r f; do
    [ -z "$f" ] && continue
    if [ ! -f "$f" ]; then
        echo "$f" >> "$missing_file"
    fi
done

if [ "$missing" -eq 0 ]; then
    echo "All figures and files exist."
    return 0
else
    echo "$missing figure(s) or file(s) missing."
    echo "See $missing_file"
    return 1
fi
