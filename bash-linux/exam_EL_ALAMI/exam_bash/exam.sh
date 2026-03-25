#!/bin/bash

date >> sales.txt

function get_sale {
    gpu=$1
    echo "$(curl -s "http://0.0.0.0:5000/$gpu")"
}

for x in 'rtx3060' 'rtx3070' 'rtx3080' 'rtx3090' 'rx6700'
do
    result=$(get_sale $x)
    echo "$x:$result" >> sales.txt
done
