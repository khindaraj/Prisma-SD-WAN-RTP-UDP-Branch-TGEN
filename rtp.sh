#!/bin/bash

# Function to get the IP address for a given domain
function getIpAddress() {
  local domain_name="$2"  # Use $2 for the target host

  if [[ -z "$domain_name" ]]; then
    echo "Domain name is required"
    return 1
  fi

  # 1. Check host file for IP (faster)
  IP_FROM_HOSTFILE=$(grep "$domain_name" /etc/hosts | awk '{print $1}')

  if [[ -n "$IP_FROM_HOSTFILE" ]]; then
    echo "$IP_FROM_HOSTFILE"
    return 0  # Exit function with success (0) if found in host file
  fi

  # 2. Fallback to DNS resolution if not found in host file
  IP_FROM_DNS=$(getent ahosts "$domain_name" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')

  if [[ -n "$IP_FROM_DNS" ]]; then
    echo "$IP_FROM_DNS"
    return 0  # Exit function with success (0) if found via DNS
  fi

  echo "IP address not found for $domain_name"
  return 1  # Exit function with failure (1) if not found
}

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

# Get the IP address of the target host
IP_ADDRESS=$(getIpAddress "$TARGET_HOST")

# Check if the IP address was successfully retrieved
if [[ $? -ne 0 ]]; then
  echo "Error: Failed to retrieve IP address for '$TARGET_HOST'. Exiting."
  exit 1
fi

echo "IP Address for '$TARGET_HOST' resolved as: $IP_ADDRESS"

while true; do
  # Check if rtp.py exists (optional, adjust for your script name)
  if [[ ! -f "$SCRIPT_DIR/rtp.py" ]]; then
    echo "Error: Script 'rtp.py' not found in the script directory."
    exit 1
  fi

  # Run rtp.py with the resolved IP address
  python3 "$SCRIPT_DIR/rtp.py" --destination-host "$IP_ADDRESS" || echo "Error: rtp.py execution failed."

  # Generate random sleep time
  s=$(shuf -i 1-30 -n 1)
  echo "$(date) Sleeping for $s seconds"
  sleep $s
done
