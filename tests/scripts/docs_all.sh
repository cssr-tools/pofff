# Run as . tests/scripts/docs_all.sh
. tests/scripts/docs_hello_world.sh &
. tests/scripts/docs_adding_your_results.sh &
. tests/scripts/docs_visualization.sh &
wait

. tests/scripts/docs_check_outputs.sh
