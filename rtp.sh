#!/bin/bash
cd /root/scripts
while true
do
/root/scripts/rtp.py --destination-host webpos.sasedemo.net
s=$(shuf -i 1-30 -n 1)
echo "`date` Sleeping for $s seconds"
sleep $s
done
