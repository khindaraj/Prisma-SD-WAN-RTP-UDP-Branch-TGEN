#!/bin/bash
cd /root

# Function to get the reachable interface
function getReachableInterface() {
  while true; do
    INTERFACE=$(ip route get "$1" | grep via | awk '{print $5}')
    if [[ ! -z "$INTERFACE" ]]; then
      break
    fi
    sleep 1  # Add a small wait between attempts in case the route isn't immediately available
  done
  echo "$INTERFACE"
}

if [ "$1" != "" ]; then
  echo "Hostname provided $1"
  TARGET_HOST=$1
else
  echo "No hostname provided. Using default TARGET_HOST=webpos.sadedemo.net"
  TARGET_HOST='webpos.sadedemo.net'
fi

# Check if reachable interface exists for the target host before the loop
REACHABLE_INTERFACE=$(getReachableInterface "$TARGET_HOST")

while true; do
  # Skip the entire loop iteration if no reachable interface was found for the target host initially
  if [[ -z "$REACHABLE_INTERFACE" ]]; then
    echo "No reachable interface found for $TARGET_HOST. Skipping loop iteration..."
    sleep 60  # Increase sleep time between retries if no interface is reachable
    continue
  fi

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
