#!/bin/bash

# --- Configuration ---
FIO_PATH="/home/haakonks/fio"
JOB_DIR="$FIO_PATH/job"
OUTPUT_DIR="$FIO_PATH/out"

# --- Usage Check ---
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <job> <interface>"
  exit 1
fi

# --- Setup Variables ---
SUBDIR="$1"          # This will be used as both the job subdirectory and the prefix.
SUFFIX="$2"
JOB_SUBDIR="$JOB_DIR/$SUBDIR"
OUTPUT_SUBDIR="$OUTPUT_DIR/$SUBDIR"



# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_SUBDIR"

# --- Find and Run Fio Job Files Recursively ---
# For each .fio file found under JOB_SUBDIR (including in subdirectories)
find "$JOB_SUBDIR" -type f -name "*.fio" | while read -r jobfile; do
  jobname=$(basename "$jobfile" .fio)
  output_file="${SUBDIR}_${jobname}_${SUFFIX}.json"
  echo "Running fio job: $jobfile"
  echo "Output will be saved as: $OUTPUT_SUBDIR/$output_file"
  fio --output="$OUTPUT_SUBDIR/$output_file" --output-format=json "$jobfile"
done
