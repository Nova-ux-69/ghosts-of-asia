"""Cover image (thumbnail) for a Short: a frame from one scene + COUNTRY + PART badge + hook line + Boo badge.

Run from an episode folder:
  python3 ../../toolkit/thumbnail.py <scenes_module> <part> <scene_id> <t_seconds> "<COUNTRY>" "<PART 1>" "<hook text, *word* = yellow>" <out.jpg> [shift_px]
shift_px (optional) moves the picture down, so the ghost's face sits between the PART badge and the hook text (y 650-1350).
Output: 1080x1920 JPEG under 2 MB (YouTube's thumbnail limit).
"""
import os, sys, json, importlib, re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
EP = os.getcwd()
TK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, EP); sys.path.insert(1, TK)
from art_v import W, H, font, LORA, INTER_SB, INTER_M, wrap

GOLD = (214, 180, 116, 255)
CREAM = (248, 240, 228, 255)
YELLOW = (255, 214, 77, 255)


def scene_frame(mod_name, part, sid, t):
    S = importlib.import_module(mod_name)
    T = json.load(open(os.path.join(EP, part, "timing.json")))
    s = [x for x in T if x["id"] == sid][0]
    f = getattr(S, "make_" + sid)(s["dur"], s["caps"])
    return np.clip(f(t), 0, 255).astype(np.uint8)


def fit_font(path, text, max_w, start, var=None):
    size = start
    while size > 40:
        f = font(path, size, var)
        if f.getlength(text) <= max_w:
            return f
        size -= 6
    return font(path, size, var)


def make(frame, country, part_label, hook, out, shift=0):
    img = Image.fromarray(frame).convert("RGBA")
    if shift:  # move the picture down so a face is not hidden behind the title
        moved = Image.new("RGBA", (W, H), (6, 2, 6, 255)); moved.alpha_composite(img, (0, int(shift))); img = moved
    # darken top and bottom so the words pop
    a = np.zeros((H, W), np.float32)
    yy = np.arange(H)[:, None]
    a += np.clip(1 - yy / 760, 0, 1) * 0.8
    a += np.clip((yy - 1080) / 700, 0, 1) * 0.75
    shade = Image.new("RGBA", (W, H), (6, 2, 6, 0)); shade.putalpha(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)))
    img.alpha_composite(shade)
    d = ImageDraw.Draw(img)
    # series label + country
    d.text((W / 2, 190), "GHOSTS  OF  ASIA", font=font(INTER_M, 44), fill=GOLD, anchor="mm")
    cf = fit_font(LORA, country, 960, 210, "Bold")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((W / 2, 340), country, font=cf, fill=(220, 30, 40, 255), anchor="mm")
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 340), country, font=cf, fill=CREAM, anchor="mm", stroke_width=4, stroke_fill=(30, 6, 10, 255))
    # PART badge
    pf = font(INTER_SB, 84)
    tw = pf.getlength(part_label)
    bw, bh = int(tw + 110), 150
    pill = Image.new("RGBA", (bw * 2, bh * 2), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([4, 4, bw * 2 - 5, bh * 2 - 5], bh, fill=(205, 22, 36, 255), outline=(255, 255, 255, 255), width=10)
    pill = pill.resize((bw, bh), Image.LANCZOS)
    ImageDraw.Draw(pill).text((bw / 2, bh / 2 + 2), part_label, font=pf, fill=(255, 255, 255, 255), anchor="mm")
    img.alpha_composite(pill, (int(W / 2 - bw / 2), 500))
    # hook line, *word* in yellow
    hf = font(INTER_SB, 96)
    words = hook.upper().split()
    lines, cur = [], []
    for w_ in words:
        trial = " ".join([x.strip("*") for x in cur + [w_]])
        if hf.getlength(trial) > 960 and cur:
            lines.append(cur); cur = [w_]
        else:
            cur.append(w_)
    lines.append(cur)
    y = 1480 - (len(lines) - 1) * 60
    for ln in lines:
        plain = [w_.strip("*") for w_ in ln]
        total = hf.getlength(" ".join(plain))
        x = W / 2 - total / 2
        for raw, w_ in zip(ln, plain):
            col = YELLOW if raw.startswith("*") else (255, 255, 255, 255)
            d.text((x, y), w_, font=hf, fill=col, anchor="lm", stroke_width=9, stroke_fill=(10, 4, 8, 255))
            x += hf.getlength(w_ + " ")
        y += 120
    # Boo badge
    badge = Image.open(os.path.join(TK, "assets", "boo_badge.png")).convert("RGBA").resize((170, 170), Image.LANCZOS)
    img.alpha_composite(badge, (W - 200, 40))
    img.convert("RGB").save(out, quality=90, optimize=True)
    print(out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    mod, part, sid, t, country, part_label, hook, out = sys.argv[1:9]
    shift = float(sys.argv[9]) if len(sys.argv) > 9 else 0
    make(scene_frame(mod, part, sid, float(t)), country, part_label, hook, out, shift)
