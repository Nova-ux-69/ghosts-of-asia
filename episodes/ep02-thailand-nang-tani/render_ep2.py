import json, os, subprocess, sys, time
import numpy as np
from PIL import Image
import sys; _EP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _EP); sys.path.insert(1, os.path.join(_EP, "..", "..", "toolkit"))
from art_v import W, H, FPS, caption_img, ease
import scenes_ep2 as S

PART = sys.argv[1]
T = json.load(open(f"{PART}/timing.json"))
starts = {}; acc = 0
for s in T:
    starts[s["id"]] = acc; acc += s["dur"]
NO_FADE_OUT = {"reveal", "outro"}
NO_FADE_IN = {"reveal"}
CAP_TOP = 1320


def maker(sid):
    s = [x for x in T if x["id"] == sid][0]
    D, caps = s["dur"], s["caps"]
    if sid == "silence":
        return S.make_silence(D, caps, [x for x in T if x["id"] == "walk"][0]["dur"]), D, caps
    return getattr(S, "make_" + sid)(D, caps), D, caps


def frame(sid, f, D, caps, t, first):
    arr = f(t)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    for text, a, b in caps:
        if a - 0.1 <= t <= b + 0.2:
            al = min(ease((t - a + 0.1) / 0.12), 1 - ease((t - b) / 0.2))
            c = caption_img(text)
            if al < 1:
                c = c.copy(); c.putalpha(c.split()[3].point(lambda v: int(v * al)))
            img.alpha_composite(c, (int(W / 2 - c.width / 2), CAP_TOP))
    out = np.asarray(img.convert("RGB")).astype(np.float32)
    k = 1.0
    if sid not in NO_FADE_IN and not first:
        k *= ease(t / 0.3)
    if sid not in NO_FADE_OUT:
        k *= 1 - ease((t - (D - 0.3)) / 0.3)
    return (out * k).astype(np.uint8)


def nframes(sid):
    a = starts[sid]; d = [x for x in T if x["id"] == sid][0]["dur"]
    return round((a + d) * FPS) - round(a * FPS)


def render(sid):
    f, D, caps = maker(sid)
    first = sid == T[0]["id"]
    os.makedirs(f"{PART}/out", exist_ok=True)
    tmp = f"{PART}/out/{sid}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "22", "-preset", "veryfast",
                          "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    t0 = time.time(); n = nframes(sid)
    for i in range(n):
        p.stdin.write(frame(sid, f, D, caps, i / FPS, first).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.rename(tmp, f"{PART}/out/{sid}.mp4")
    print(PART, sid, n, "frames", round(time.time() - t0, 1), "s", flush=True)


if __name__ == "__main__":
    if sys.argv[2] == "stills":
        os.makedirs("stills", exist_ok=True)
        for sid, ts in json.loads(sys.argv[3]):
            f, D, caps = maker(sid)
            for t in ts:
                Image.fromarray(frame(sid, f, D, caps, t, False)).resize((540, 960)).save(f"stills/{PART}_{sid}_{t:.1f}.jpg", quality=88)
    else:
        for sid in sys.argv[2:]:
            render(sid)
