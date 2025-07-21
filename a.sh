#!/bin/bash

for i in {1..44}; do
    printf "Processing: %s\n" $i
    curl --http1.1 \
         --retry 3 \
         --retry-delay 1 \
         --connect-timeout 10 \
         --max-time 30 \
         "https://www.accuweather.com/images/weathericons/${i}.svg" \
         -o "weather_icons/${i}.svg"
done