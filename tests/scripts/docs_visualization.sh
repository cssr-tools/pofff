OUT="test_outputs/docs_visualization"
. tests/scripts/initialize_output_folders.sh $OUT
. tests/scripts/get_plopm.sh
mkdir $OUT
WHR="$OUT/appendixb.toml"
cp "publication/appendixb.toml" $WHR
sed -i.bak "s/flow --/mpirun -np 8 flow --/g" $WHR && rm -f $WHR.bak
sed -i.bak "s/8100, 3E-7/300, 3E-7/g" $WHR && rm -f $WHR.bak
sed -i.bak "s/10200, 3E-7/300, 3E-7/g" $WHR && rm -f $WHR.bak
sed -i.bak "s/68100, 68100/3300, 300/g" $WHR && rm -f $WHR.bak
sed -i.bak "s/345600, 86400, 0, 0/64800, 3600, 0, 0],[345600, 21600, 0, 0/g" $WHR && rm -f $WHR.bak
pofff -i $WHR -o $OUT -m single -c '5e-2' -f none
plopm -v xco2l -i "$OUT/DOCS_VISUALIZATION" -o $OUT -fs 16,5 -mv satnum -m gif -dpi 1000 -fz 20 -gl 1 -cbf .1e -cbp 0.30,0.01,0.4,0.02 -gi 437.5 -mt 1e-5 -tu h -cbn 5 -cbl 'CO$_2$ mass fraction in liquid [-]' -t 'FluidFlower simulation (GitHub/cssr-tools/pofff),'
