#!/usr/bin/env bash
# Horror colour grade for Ghosts of Asia (Nova's request, 2026-11-24): deep crushed blacks,
# red pushed into the shadows and mids, other colours pulled down, vignette, film grain.
# Apply to the FINAL muxed video of each part:
#   bash ../../toolkit/grade.sh epNN_part1_raw.mp4 epNN_part1.mp4
set -e
IN="$1"; OUT="$2"
GRADE="huesaturation=saturation=-0.6:colors=y+g+c+b+m:strength=1,huesaturation=saturation=0.3:colors=r:strength=1,curves=all='0/0 0.06/0.03 0.4/0.37 0.75/0.76 1/1',colorbalance=rs=0.18:gs=-0.05:bs=-0.05:rm=0.09:gm=-0.03:bm=-0.03,eq=contrast=1.05:brightness=0.02,vignette=angle=PI/5.5,noise=alls=6:allf=t"
ffmpeg -y -loglevel error -i "$IN" -vf "$GRADE" -c:v libx264 -crf 25 -preset veryfast -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT"
