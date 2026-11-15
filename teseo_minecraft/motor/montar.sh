#!/bin/bash
# Une los trozos, añade mezcla de audio y subtítulos quemados; saca versión final 1080p y copia ligera para el móvil
set -e; cd /home/user/teseo
ls trozos/t*.mp4 | sort | sed "s|^|file '$PWD/|; s|$|'|" > trozos/concat.txt
ffmpeg -y -loglevel error -f concat -safe 0 -i trozos/concat.txt -c copy /tmp/claude-0/video_mudo.mp4
ffmpeg -y -loglevel error -i /tmp/claude-0/video_mudo.mp4 -i mezcla.wav -vf "subtitles=subs.ass:fontsdir=fonts" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart -shortest final/teseo_minotauro_1080p.mp4
ffmpeg -y -loglevel error -i final/teseo_minotauro_1080p.mp4 -vf "scale=640:360:flags=lanczos" -c:v libx264 -preset slow -b:v 330k -maxrate 420k -bufsize 800k -pix_fmt yuv420p -c:a aac -b:a 48k -ac 1 -movflags +faststart final/teseo_minotauro_movil.mp4
ls -la final/
