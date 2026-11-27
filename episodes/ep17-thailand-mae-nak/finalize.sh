#!/usr/bin/env bash
# Concatenate scene clips, mux the mix with loudness normalisation, re-encode small. Usage: bash finalize.sh p1 "hook walk ..." out.mp4
set -e
P=$1; IDS=$2; OUT=$3
rm -f $P/list.txt; for s in $IDS; do echo "file 'out/$s.mp4'" >> $P/list.txt; done
ffmpeg -y -loglevel error -f concat -safe 0 -i $P/list.txt -c copy $P/video.mp4
ffmpeg -y -loglevel error -i $P/video.mp4 -i $P/mix.wav -map 0:v -map 1:a -af loudnorm=I=-14:TP=-1.5:LRA=11 \
  -c:v libx264 -crf 25 -preset veryfast -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k -ar 48000 -shortest $OUT
