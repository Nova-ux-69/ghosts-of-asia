#!/usr/bin/env bash
# grade still frames the same way toolkit/grade.sh grades videos: in.jpg -> in_g.jpg
for f in "$@"; do
ffmpeg -y -loglevel error -i "$f" -vf "huesaturation=saturation=-0.6:colors=y+g+c+b+m:strength=1,huesaturation=saturation=0.3:colors=r:strength=1,curves=all='0/0 0.06/0.03 0.4/0.37 0.75/0.76 1/1',colorbalance=rs=0.18:gs=-0.05:bs=-0.05:rm=0.09:gm=-0.03:bm=-0.03,eq=contrast=1.05:brightness=0.02,vignette=angle=PI/5.5" "${f%.jpg}_g.jpg"
done
