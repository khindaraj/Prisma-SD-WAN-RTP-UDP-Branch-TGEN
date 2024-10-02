#!/bin/bash
#cd /root

# Function to get the IP address for a given domain
function getIpAddress() {
  local domain_name="$1"

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

# Function to get the reachable interface for a given IP
function getReachableInterface() {
  local ip_address="$1"
  
  if [[ -z "$ip_address" ]]; then
    echo "Invalid IP address"
    return 1
  fi

  while true; do
    INTERFACE=$(ip route get "$ip_address" | grep via | awk '{print $5}')
    if [[ -n "$INTERFACE" ]]; then
      break
    fi
    sleep 1  # Adding sleep to avoid high CPU usage in case of waiting
  done
  echo "$INTERFACE"
}

# Main script logic

if [ "$1" != "" ]; then
  echo "Hostname provided: $1"
  TARGET_HOST=$1
else
  echo "No hostname provided. Using default TARGET_HOST=webpos.sasedemo.net"
  TARGET_HOST='webpos.sasedemo.net'
fi

# Get the IP address for the target host
IP_ADDRESS=$(getIpAddress "$TARGET_HOST")

if [[ $? -ne 0 ]]; then
  echo "Failed to retrieve IP address for $TARGET_HOST. Exiting."
  exit 1
fi

echo "IP Address for $TARGET_HOST: $IP_ADDRESS"

# Get the reachable interface for the retrieved IP address
REACHABLE_INTERFACE=$(getReachableInterface "$IP_ADDRESS")

# Check if reachable interface exists for the target host before the loop
if [[ -z "$REACHABLE_INTERFACE" ]]; then
  echo "No reachable interface found for $TARGET_HOST. Exiting."
  exit 1
fi

echo "Reachable Interface: $REACHABLE_INTERFACE"

while true; do
  t=$(shuf -i 60-700 -n 1)
  x=$(shuf -i 600-900 -n 1)

  # Use the previously found reachable interface throughout the loop
  INTERFACE="$REACHABLE_INTERFACE"

  for ((i = 1; i <= t; i++)); do
    echo "Request $i using interface $INTERFACE"
    curl --interface "$INTERFACE" -sL -m 15 http://${TARGET_HOST}/cgi-bin/get_env.py -o /dev/null
    curl --interface "$INTERFACE" -sL -m 15 http://${TARGET_HOST}/cgi-bin/hw.sh -o /dev/null
  done

  for ((i = 1; i <= x; i++)); do
    echo "Request $i using interface $INTERFACE"
    curl --interface "$INTERFACE" -sL -m 15 http://${TARGET_HOST}/ -o /dev/null
    curl --interface "$INTERFACE" -sL -m 15 http://${TARGET_HOST}/ -o /dev/null
    sleep 1
  done

  sleep 31  # Increased sleep between loop iterations
done
