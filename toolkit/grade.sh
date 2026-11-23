#!/usr/bin/env bash
# Horror colour grade for Ghosts of Asia (Nova's request, 2026-11-24): deep crushed blacks,
# red pushed into the shadows and mids, other colours pulled down, vignette, film grain.
# Apply to the FINAL muxed video of each part:
#   bash ../../toolkit/grade.sh epNN_part1_raw.mp4 epNN_part1.mp4
set -e
IN="$1"; OUT="$2"
GRADE="huesaturation=saturation=-0.75:colors=y+g+c+b+m:strength=1,huesaturation=saturation=0.3:colors=r:strength=1,curves=all='0/0 0.10/0.02 0.35/0.24 0.7/0.67 1/0.97',colorbalance=rs=0.22:gs=-0.06:bs=-0.06:rm=0.12:gm=-0.04:bm=-0.04:rh=0.03,eq=contrast=1.12,vignette=angle=PI/4.2,noise=alls=7:allf=t"
ffmpeg -y -loglevel error -i "$IN" -vf "$GRADE" -c:v libx264 -crf 25 -preset veryfast -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT"
