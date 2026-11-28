#!/usr/bin/env bash
# p1|p2 -> concat + mux (finalize.sh), lift the mids (the BLACK grade alone crushes these night scenes), BLACK grade,
# re-burn crisp captions on top. Usage: bash post.sh p1 1 "hook setup ..."
set -e
P=$1; N=$2; IDS=$3
[ -f ep20_part${N}_raw.mp4 ] || bash finalize.sh $P "$IDS" ep20_part${N}_raw.mp4
ffmpeg -v error -y -i ep20_part${N}_raw.mp4 -vf "curves=all='0/0 0.06/0.2 0.3/0.58 0.65/0.86 1/1'" -c:v libx264 -crf 18 -preset veryfast -c:a copy ep20_part${N}_lift.mp4
bash ../../toolkit/grade_black.sh ep20_part${N}_lift.mp4 ep20_part${N}_graded.mp4
python3 caps_overlay.py $P ep20_part${N}_graded.mp4 ep20_part${N}_caps.mp4
python3 header_overlay.py $P ep20_part${N}_caps.mp4 ep20_part${N}.mp4
