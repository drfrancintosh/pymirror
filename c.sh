#!/bin/bash

for i in weather_icons/*.svg; do
    printf "Processing: %s\n" $i
    rsvg-convert -f png -o "${i%.svg}.png" "$i"
done