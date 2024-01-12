#!/bin/bash

i=0
while :
do
    curl http://localhost:6075/debug/pprof/heap > heap.$i.pprof
    ((i++))
    sleep 1
done