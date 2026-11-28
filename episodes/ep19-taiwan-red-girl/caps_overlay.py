"""Re-burn crisp captions on top of the BLACK-graded video (the grade dims the captions that were rendered into the
frames). Same caption image, same position (y=1320), shown from a to b+0.1 of each line. Usage: python3 caps_overlay.py p1 in.mp4 out.mp4"""
import json, os, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
from art_v import W, FPS, caption_img
P, IN, OUT = sys.argv[1:4]
T = json.load(open(f"{P}/timing.json"))
acc = 0; items = []
for s in T:
    f0 = round(acc * FPS) / FPS
    for text, a, b in s["caps"]:
        items.append((text, f0 + a + 0.02, f0 + b + 0.1))
    acc += s["dur"]
os.makedirs(f"{P}/caps", exist_ok=True)
args = ["ffmpeg", "-v", "error", "-y", "-i", IN]
for i, (text, a, b) in enumerate(items):
    c = caption_img(text); fn = f"{P}/caps/c{i}.png"; c.save(fn)
    args += ["-i", fn]
chain = []; last = "0:v"
for i, (text, a, b) in enumerate(items):
    c = caption_img(text)
    x = int(W / 2 - c.width / 2)
    chain.append(f"[{last}][{i + 1}:v]overlay={x}:1320:enable='between(t,{a:.3f},{b:.3f})'[v{i}]"); last = f"v{i}"
open(f"{P}/caps.txt", "w").write(";".join(chain))
args += ["-filter_complex_script", f"{P}/caps.txt", "-map", f"[{last}]", "-map", "0:a", "-c:v", "libx264", "-crf", "27",
         "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", OUT]
subprocess.run(args, check=True)
print(P, len(items), "captions re-burned")
