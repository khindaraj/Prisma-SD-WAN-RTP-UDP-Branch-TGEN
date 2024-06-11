#!/bin/bash

# Get the script directory and target host from arguments
SCRIPT_DIR="$1"
TARGET_HOST="$2"

# Check if arguments are provided
if [[ -z "$SCRIPT_DIR" || -z "$TARGET_HOST" ]]; then
  echo "Error: Please provide both script directory and target host as arguments."
  echo "Usage: $0 <script_directory> <target_host>"
  exit 1
fi

# Check if the script directory exists
if [[ ! -d "$SCRIPT_DIR" ]]; then
  echo "Error: Script directory '$SCRIPT_DIR' does not exist."
  exit 1
fi

while true; do
  # Check if rtp.py exists (optional, adjust for your script name)
  if [[ ! -f "$SCRIPT_DIR/rtp.py" ]]; then
    echo "Error: Script 'rtp.py' not found in the script directory."
    exit 1
  fi

  # Run rtp.py with error handling (adjust for your script's arguments)
  "$SCRIPT_DIR/rtp.py" --destination-host "$TARGET_HOST" || echo "Error: rtp.py execution failed."

  # Generate random sleep time
  s=$(shuf -i 1-30 -n 1)
  echo "$(date) Sleeping for $s seconds"
  sleep $s
done
