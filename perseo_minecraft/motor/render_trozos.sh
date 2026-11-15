#!/bin/bash
# Render reanudable por trozos de 20 s (720p, 24 fps). Salta los trozos ya hechos. Al final une todo en visual.mp4
cd "$(dirname "$0")"; mkdir -p trozos
curl -s -o /dev/null http://127.0.0.1:8766/index.html || (setsid nohup python3 -m http.server 8766 --bind 127.0.0.1 >/tmp/srv.log 2>&1 &); sleep 1
DUR=$(python3 -c "import json;print(json.load(open('bloques.json',encoding='utf-8'))[-1]['t1'])"); T=20
N=$(python3 -c "import math;print(math.ceil($DUR/$T))")
for i in $(seq 0 $((N-1))); do f=trozos/c$(printf %03d $i).mp4; [ -s $f ] && continue
  a=$((i*T)); b=$(python3 -c "print(min($DUR,$a+$T))")
  DSF=0.6666667 FPS=24 FMT=jpeg node render.js http://127.0.0.1:8766/index.html trozos/tmp.mp4 $a $b > trozos/log.txt 2>&1 && mv trozos/tmp.mp4 $f && echo "$(date -u +%H:%M) trozo $i/$N"; done
ls trozos/c*.mp4 | sed "s#trozos/##; s/.*/file '&'/" > trozos/lista.txt
[ $(wc -l < trozos/lista.txt) -eq $N ] && ffmpeg -v error -y -f concat -safe 0 -i trozos/lista.txt -c copy visual.mp4 && echo "ok visual.mp4"
