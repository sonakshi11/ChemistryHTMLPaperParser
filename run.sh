#!/bin/bash

# Define the path to the CSV file
csv_file="/data/sonakshi/SynthesisRecipes/data/wiley_ROP_DOIs.csv"

# Read and process the CSV file using awk
mapfile -t dois < <(awk -F ',' '{print $1}' "$csv_file")

file_directory="/data/pranav/prod/structured_files/wiley/"

for doi in "${dois[@]}"; do
  modified_doi="${doi//\//@}.html"
  filepath="$file_directory$modified_doi"
  log_path="logs/${doi//\//@}.log"
  nohup python tests/process_articles.py --input_dir "$filepath" --log_path "$log_path" >"nohup_wiley.out" 2>&1 &
done