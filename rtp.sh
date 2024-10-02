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

# Function to get the IP address of a domain/hostname
getIpAddress() {
  local target_host="$1"  # Use $1 since we're passing the target host
  ip=$(dig +short "$target_host" | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -n 1)

  if [[ -z "$ip" ]]; then
    # Try using nslookup if dig fails
    ip=$(nslookup "$target_host" | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}' | tail -n 1)
  fi

  if [[ -z "$ip" ]]; then
    return 1  # Return 1 (error) if IP couldn't be resolved
  fi

  echo "$ip"  # Return the resolved IP address
  return 0  # Return 0 (success) if IP was resolved
}

# Get the IP address of the target host
IP_ADDRESS=$(getIpAddress "$TARGET_HOST")

# Check if the IP address was successfully retrieved
if [[ $? -ne 0 ]]; then
  echo "Error: Failed to retrieve IP address for '$TARGET_HOST'. Exiting."
  exit 1
fi

echo "IP Address for '$TARGET_HOST' resolved as: $IP_ADDRESS"

while true; do
  # Check if rtp.py exists in the script directory
  if [[ ! -f "$SCRIPT_DIR/rtp.py" ]]; then
    echo "Error: Script 'rtp.py' not found in the script directory."
    exit 1
  fi

  # Run the Python script explicitly with Python3
  sudo python3 "$SCRIPT_DIR/rtp.py" --destination-host "$IP_ADDRESS" || echo "Error: rtp.py execution failed."

  # Generate random sleep time
  s=$(shuf -i 1-30 -n 1)
  echo "$(date) Sleeping for $s seconds"
  sleep $s
done

