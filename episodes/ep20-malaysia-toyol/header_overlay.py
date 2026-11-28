"""Re-burn the series header + waving flag over the graded hook (Part 1) / recap (Part 2) so the first frame keeps
the real flag colours and a readable GHOSTS OF ASIA / MALAYSIA / PART N (the BLACK grade's vignette dims the top).
Usage: python3 header_overlay.py p1 in.mp4 out.mp4"""
import json, os, sys, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art_ep20 import put_header, W
from art_v import FPS
from scenes_v import series_header
P, IN, OUT = sys.argv[1:4]
T = json.load(open(f"{P}/timing.json"))
s0 = T[0]
end = s0["dur"] - (0.7 if P == "p1" else 0.0)
hdr = series_header("MALAYSIA", "PART 1" if P == "p1" else "PART 2")
os.makedirs(f"{P}/hdr", exist_ok=True)
n = int(end * FPS)
for i in range(n):
    im = Image.new("RGBA", (W, 560), (0, 0, 0, 0))
    put_header(im, hdr, i / FPS)
    im.save(f"{P}/hdr/{i:04d}.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{P}/hdr/%04d.png", "-c:v", "png", f"{P}/hdr.mov"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", IN, "-i", f"{P}/hdr.mov", "-filter_complex",
                f"[0:v][1:v]overlay=0:0:eof_action=pass:enable='lt(t,{end:.3f})'[v]", "-map", "[v]", "-map", "0:a",
                "-c:v", "libx264", "-crf", "27", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", OUT], check=True)
print(P, "header re-burned for", round(end, 2), "s")
