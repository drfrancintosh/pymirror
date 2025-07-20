#!/bin/bash

# Method 1: Using an array
# numbers=(01 02 03 04 09 10 11 13 50)
numbers=(50)

for num in "${numbers[@]}"; do
    printf "Processing: %s\n" $num
    curl "https://openweathermap.org/img/wn/${num}d@2x.png" > "weather_icons/${num}d@2x.png"
done