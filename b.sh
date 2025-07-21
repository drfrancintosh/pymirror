#!/bin/bash

for i in {1..44}; do
    printf "Processing: %s\n" $i
    open "https://www.accuweather.com/images/weathericons/${i}.svg"
done