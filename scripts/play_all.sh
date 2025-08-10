#!/bin/bash

for i in sounds/*.wav; do
  echo $i
  wav.play "$i"
  sleep 2
done
