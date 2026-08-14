WHR="examples/single"
OUT="test_outputs/docs_hello_world"
. tests/scripts/initialize_output_folders.sh $OUT
pofff -i $WHR.toml -o $OUT -t 24,48,72
