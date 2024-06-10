#!/bin/bash
cd /root

function getAddress () {
        INTERFACE=`sort -R /root/goscript/interfaces.txt 2>/dev/null | head -n 1`
}

if [ "$1" != "" ]; then
    echo "Hostname provided $1"
    HOST=$1
else
    echo "no hostname provided using default webpos.cgxdemo.net"
    URL='webpos.cgxdemo.net'

fi

while true
do


        t=$(shuf -i 60-700 -n 1)
        x=$(shuf -i 600-900 -n 1)
        #echo "`date` Running with delay for $t seconds"
        for (( i = 1; i <= t; i++))
                do
                        getAddress
                        #echo "request $i"
                        curl --interface $INTERFACE -sL -m 15  http://$HOST/cgi-bin/get_env.py -o /dev/null
                        curl --interface $INTERFACE -sL -m 15  http://$HOST/cgi-bin/hw.sh -o /dev/null
                done

        for (( i = 1; i <= x; i++))
                do
                        getAddress
                        #echo "`date` NOOOOOO delay for $x seconds"
                        curl --interface $INTERFACE -sL -m 15  http://$HOST/ -o /dev/null
                        curl --interface $INTERFACE -sL -m 15  http://$HOST/ -o /dev/null
                        sleep 1
                done

sleep 1
done
