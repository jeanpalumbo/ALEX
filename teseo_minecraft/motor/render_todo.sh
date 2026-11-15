#!/bin/bash
cd /home/user/teseo; export NODE_PATH=$(npm root -g); export QS="?st=1"
cat trozos/lista.txt | xargs -P 4 -L 1 bash -c 'for i in 1 2 3; do [ -s "$2" ] && ffprobe -v error "$2" >/dev/null 2>&1 && break; node render.js $0 $1 $2 && break; done' >> trozos/render.log 2>&1
echo TODO_FIN >> trozos/render.log
