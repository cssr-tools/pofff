OUT="test_outputs/docs_adding_your_results"
. tests/scripts/initialize_output_folders.sh $OUT
mkdir $OUT
WHR="$OUT/results.toml"
cp "publication/results.toml" $WHR
sed -i.bak "s/flow --/mpirun -np 8 flow --/g" $WHR && rm -f $WHR.bak
pofff -i $WHR -o $OUT -m single -t 24,48,72,96,120 -f all
