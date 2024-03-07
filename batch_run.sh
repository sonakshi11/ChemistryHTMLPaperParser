#!/bin/bash

csv_file="/data/sonakshi/SynthesisRecipes/data/wiley_ROP_DOIs.csv"

# Read the CSV file and store DOIs into an array
mapfile -t dois < <(awk -F ',' '{print $1}' "$csv_file")

file_directory="/data/pranav/prod/structured_files/wiley/"

batch_size=100
total_dois=${#dois[@]}
batches=$((total_dois / batch_size + (total_dois % batch_size > 0)))

master_log="logs_nohup/master_nohup_wiley.log"
echo "Starting batch processing" > "$master_log"

for ((batch=0; batch<batches; batch++)); do
  start=$((batch * batch_size))
  end=$((start + batch_size - 1))

  if [ $end -ge $total_dois ]; then
    end=$((total_dois - 1))
  fi

  for index in $(seq $start $end); do
    doi=${dois[$index]}
    modified_doi="${doi//\//@}.html"
    filepath="$file_directory$modified_doi"
    log_path="logs/${doi//\//@}.log"
    echo "Processing DOI: $doi" >> "$master_log" 2>&1 &
    if [[ ! -f "$filepath" ]]; then
        echo "File not found for DOI: $doi, expected at $filepath" >> "$master_log"
        continue 
    fi
    nohup python tests/process_articles.py --input_dir "$filepath" --log_path "$log_path" --output_dir ./output-ROP >> "$master_log" 2>&1 &
  done

  wait

  # break
done
