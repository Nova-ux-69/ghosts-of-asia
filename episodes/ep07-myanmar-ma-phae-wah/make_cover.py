# Graded cover: python3 make_cover.py p1 cliff 6.0 "PART 1" "Pray she *doesn't* stop" ep07_part1_thumb.jpg -90
import sys, os, subprocess, numpy as np
sys.path.insert(0, os.getcwd()); sys.path.insert(1, os.path.join(os.getcwd(), "..", "..", "toolkit"))
from PIL import Image
import thumbnail as T
GRADE = open("../../toolkit/grade.sh").read().split('GRADE="')[1].split('"')[0].replace(",noise=alls=6:allf=t", "")
def graded(part, sid, t):
    fr = T.scene_frame("scenes_ep7", part, sid, t)
    Image.fromarray(fr).save("/tmp/_cover_f.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "/tmp/_cover_f.png", "-vf", GRADE, "/tmp/_cover_g.png"], check=True)
    return np.asarray(Image.open("/tmp/_cover_g.png").convert("RGB"))
part, sid, t, part_label, hook, out, shift = sys.argv[1:8]
T.make(graded(part, sid, float(t)), "MYANMAR", part_label, hook, out, float(shift))
