#!/usr/bin/env bash

hostname=$1

# run chef-client so chef-server gets the node ipaddress
echo "Starting the knife-status check"
STATUS=0
while [ $STATUS -eq 0 ]; do
    out=`knife status | awk '/'$hostname'/{print}'`
    echo "The knife-status output is: " $out

    ret=`echo "$out" | awk -F "," '{print NF-1}'`
    echo "The return is: " $ret
    if [ $ret -ge 4 ]; then
        break
    fi
    sleep 5
done

