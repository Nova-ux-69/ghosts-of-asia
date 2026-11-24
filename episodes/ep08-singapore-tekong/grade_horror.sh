#!/bin/bash
# Gritty colour horror grade (Nova's reference, 2026-11-24): desaturated sickly green, crushed blacks, drifting smoke, grain, flicker.
# usage: grade_horror.sh in.mp4 out.mp4 header_seconds   (header_seconds: keep the real-colour flag on top for that long)
IN=$1; OUT=$2; HS=$3; D=$(dirname "$0")
ffmpeg -v error -y -i "$IN" -loop 1 -i "$D/smoke.png" -loop 1 -i "$D/flag170.png" -filter_complex "\
[0:v]format=gbrp,curves=all='0/0 0.12/0.16 0.5/0.52 1/0.96',hue=s=0.45,colorbalance=rs=-0.08:gs=0.05:bs=-0.01:rm=-0.05:gm=0.05:bm=-0.03:rh=0.06:gh=0.02:bh=-0.06,gblur=sigma=0.9[v];\
[1:v]crop=1080:1920:'100+60*sin(t/3)':'100+mod(t*14\,400)',format=gbrp,colorchannelmixer=rr=0.42:gg=0.48:bb=0.42,curves=all='0/0 1/0.8'[sm];\
[v][sm]blend=all_mode=screen:all_opacity=0.38:shortest=1,unsharp=5:5:0.8,noise=alls=16:allf=t+u,eq=contrast=1.15:brightness='0.015*sin(t*29)*sin(t*7)':eval=frame,vignette=angle=PI/3.4,format=yuv420p[g];\
[g][2:v]overlay=455:51:enable='lt(t\,$HS)':shortest=1,format=yuv420p[o]" -map "[o]" -map 0:a -c:v libx264 -crf 29 -preset veryfast -maxrate 9M -bufsize 18M -c:a copy -movflags +faststart -shortest "$OUT"
