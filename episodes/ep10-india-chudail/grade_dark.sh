#!/usr/bin/env bash
# Ep10 India: the standard horror grade (toolkit/grade.sh) a bit DARKER (Nova, 2026-11-25):
# deeper shadows, lower mids, stronger vignette. bash grade_dark.sh in.mp4 out.mp4
set -e
IN="$1"; OUT="$2"
GRADE="huesaturation=saturation=-0.6:colors=y+g+c+b+m:strength=1,huesaturation=saturation=0.35:colors=r:strength=1,curves=all='0/0 0.08/0.03 0.4/0.34 0.75/0.72 1/1',colorbalance=rs=0.2:gs=-0.06:bs=-0.05:rm=0.1:gm=-0.04:bm=-0.03,eq=contrast=1.07:brightness=0.0,vignette=angle=PI/4.6,noise=alls=7:allf=t"
ffmpeg -y -loglevel error -i "$IN" -vf "$GRADE" -c:v libx264 -crf 25 -preset veryfast -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT"
