files=(
    "test_outputs/docs_hello_world/map_24h.png"
    "test_outputs/docs_adding_your_results/map_120h.png"
    "test_outputs/docs_adding_your_results/compare_all_time_series.png"
    "test_outputs/docs_adding_your_results/compare_all_sparse.png"
    "test_outputs/docs_adding_your_results/error_table_satmin-0.01_conmin-0.1.csv"
    "test_outputs/docs_adding_your_results/zoom_means_segmented_snapshots_satmin-0.01_conmin-0.1.png"
    "test_outputs/docs_visualization/docs_visualization_xco2l.gif"
)

missing_file="test_outputs/missing_docs_files.txt"
missing=0

rm -f "$missing_file"

for f in "${files[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "$f" >> "$missing_file"
        ((missing++))
    fi
done

if (( missing == 0 )); then
    echo "All figures and files exist."
else
    echo "$missing figure(s) or file(s) missing."
    echo "See $missing_file"
fi
