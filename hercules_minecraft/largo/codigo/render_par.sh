#!/bin/bash
# Render en paralelo: N tramos -> seg/s##.mp4 -> visual.mp4
N=${1:-6}; DUR=$(python -c "import json;print(json.load(open('bloques.json',encoding='utf-8'))[-1]['t1'])")
mkdir -p seg; rm -f seg/*.mp4
for i in $(seq 0 $((N-1))); do a=$(python -c "print(round($DUR*$i/$N*30)/30)"); b=$(python -c "print(round($DUR*($i+1)/$N*30)/30)");
  FMT=jpeg PORT=$((9600+i)) node render.js http://127.0.0.1:8766/index.html seg/s$(printf %02d $i).mp4 $a $b > seg/log$i.txt 2>&1 & done
wait; ls seg/*.mp4 | sed "s/.*/file '&'/; s#seg/##" > seg/lista.txt
ffmpeg -v error -y -f concat -safe 0 -i seg/lista.txt -c copy visual.mp4 && echo ok visual.mp4
