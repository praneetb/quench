#!/usr/bin/env bash

vagrant ssh -c "ifconfig eth0 | grep 'inet addr' | awk '{ print $2 }' | cut -d ':' -f 2 | cut -d ' ' -f 1"
