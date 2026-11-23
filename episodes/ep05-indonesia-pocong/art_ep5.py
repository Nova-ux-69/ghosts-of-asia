"""Episode 5 (Indonesia, Pocong) drawing helpers: a Javanese village before the monsoon rain.
Rice terraces with flooded paddies, joglo houses with tiered roofs, a village mosque dome, a bamboo grove,
a yellow funeral flag (bendera kuning) on a bamboo pole, an old Muslim graveyard with white nisan headstones
and gnarled frangipani (kamboja) trees, a wall oil lamp (pelita), Eyang (grandmother in kebaya and batik kain),
Bayu (a boy in a black peci cap with a torch) and the Pocong: a white shroud tied at the head, neck and feet.
Palette: storm-cloud slate and steel blue, cold silver lightning, sickly yellow storm dusk, warm amber torch,
pale bone-white shroud, pink-white frangipani."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *

# ---------------------------------------------------------------- palette
STORM_TOP = (8, 10, 18)
STORM_BOT = (48, 56, 74)
SLATE_FAR = (26, 30, 42, 255)
SLATE_MID = (14, 16, 24, 255)
SILH = (5, 6, 10, 255)
TORCH = (255, 196, 110)
PELITA = (255, 170, 70)
SHROUD = (228, 226, 214)
SHROUD_D = (170, 172, 168)
ROPE = (150, 138, 112)
FLAG = (246, 206, 40)
STONE = (196, 198, 196, 255)


# ---------------------------------------------------------------- sky / landscape
def clouds(w, h, seed=0, color=(30, 34, 48), alpha=230, y0=0.0, y1=0.35, n=40, blur=18):
    """Heavy, lumpy monsoon cloud bank (RGBA)."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w // 2, h // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x = rnd.uniform(-0.1, 1.1) * w / 2
        y = rnd.uniform(y0, y1) * h / 2
        r = rnd.uniform(60, 160) / 2
        kk = rnd.uniform(0.8, 1.2)
        c = tuple(min(255, int(v * kk)) for v in color)
        d.ellipse([x - r * 1.6, y - r, x + r * 1.6, y + r], fill=c + (alpha,))
    img = img.filter(ImageFilter.GaussianBlur(blur // 2))
    return img.resize((w, h), Image.BILINEAR)


def storm_sky(top=STORM_TOP, bot=STORM_BOT, w=W, h=H, seed=1, moon=None, moon_r=60, stars=0, cloud_col=(30, 34, 48)):
    s = sky(top, bot, moon=moon, moon_r=moon_r, stars=stars, seed=seed, w=w, h=h)
    s.alpha_composite(clouds(w, h, seed, cloud_col, 235, 0.0, 0.32, n=int(36 * w / W)))
    s.alpha_composite(clouds(w, h, seed + 7, tuple(min(255, v + 14) for v in cloud_col), 150, 0.18, 0.42, n=int(22 * w / W), blur=26))
    return s


def lightning_bolt(h=700, seed=0, w=300):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, y = w / 2, 0
    pts = [(x, y)]
    while y < h:
        x += rnd.uniform(-40, 40); y += rnd.uniform(30, 70)
        pts.append((x, y))
        if rnd.random() < 0.2:
            bx, by = x, y
            br = [(bx, by)]
            for _ in range(3):
                bx += rnd.uniform(-50, 50); by += rnd.uniform(20, 50); br.append((bx, by))
            d.line(br, fill=(220, 230, 255, 200), width=2)
    d.line(pts, fill=(240, 246, 255, 255), width=4)
    g = img.filter(ImageFilter.GaussianBlur(8))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(img)
    return out


def treeline(w, base, amp, color, seed=1):
    """Bamboo grove + mixed trees: tall feathery bamboo clumps between round canopies."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = -40
    while x < w + 40:
        if rnd.random() < 0.45:      # bamboo clump: tall arching culms with leafy tips
            n = rnd.randint(5, 9)
            hh = rnd.uniform(220, 360) + amp * 0.5
            for k in range(n):
                lean = rnd.uniform(-0.5, 0.5)
                pts = []
                for i in range(12):
                    u = i / 11
                    pts.append((x + lean * hh * 0.6 * u * u + (k - n / 2) * 4, base - hh * u))
                d.line(pts, fill=color, width=4)
                tx, ty = pts[-1]
                for j in range(14):
                    a = rnd.uniform(0, math.pi * 2)
                    r = rnd.uniform(10, 34)
                    d.ellipse([tx + math.cos(a) * r - 16, ty + math.sin(a) * r * 0.6 - 6 + j * 3,
                               tx + math.cos(a) * r + 16, ty + math.sin(a) * r * 0.6 + 6 + j * 3], fill=color)
            d.rectangle([x - 40, base - 40, x + 40, H], fill=color)
            x += rnd.uniform(60, 120)
        else:
            r = rnd.uniform(40, 90)
            y = base - rnd.uniform(0, amp)
            d.ellipse([x - r, y - r, x + r, y + r], fill=color)
            d.rectangle([x - r, y, x + r, H], fill=color)
            x += r * rnd.uniform(0.8, 1.3)
    return img


def joglo(scale=1.0, seed=0, color=SILH, lit=True):
    """Javanese joglo house: a tall steep central roof on top of a wide, low-pitched lower roof, wooden walls,
    a front pendopo porch. Returns (img, glow points) in 1x coords. Anchor: bottom centre."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(640 * S), int(420 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    base = ch - 6 * S
    wall_top = base - 130 * S
    d.rectangle([cx - 230 * S, wall_top, cx + 230 * S, base], fill=color)
    # lower wide roof
    d.polygon([(cx - 300 * S, wall_top + 10 * S), (cx - 170 * S, wall_top - 80 * S), (cx + 170 * S, wall_top - 80 * S),
               (cx + 300 * S, wall_top + 10 * S)], fill=color)
    # tall steep central roof (brunjung)
    d.polygon([(cx - 170 * S, wall_top - 76 * S), (cx - 60 * S, wall_top - 250 * S), (cx + 60 * S, wall_top - 250 * S),
               (cx + 170 * S, wall_top - 76 * S)], fill=color)
    d.line([(cx - 74 * S, wall_top - 252 * S), (cx + 74 * S, wall_top - 252 * S)], fill=color, width=int(8 * S))
    for s_ in (-1, 1):   # little upturned ridge ends
        d.polygon([(cx + s_ * 70 * S, wall_top - 248 * S), (cx + s_ * 86 * S, wall_top - 270 * S), (cx + s_ * 62 * S, wall_top - 252 * S)], fill=color)
    # porch posts
    for k in range(-3, 4):
        d.rectangle([cx + k * 66 * S - 5 * S, wall_top + 10 * S, cx + k * 66 * S + 5 * S, base], fill=color)
    glows = []
    if lit:
        for k in (-2, 1):
            if rnd.random() < 0.85:
                x0 = cx + k * 66 * S + 14 * S
                d.rectangle([x0, wall_top + 40 * S, x0 + 38 * S, wall_top + 96 * S], fill=(255, 188, 100, 255))
                d.line([(x0 + 19 * S, wall_top + 40 * S), (x0 + 19 * S, wall_top + 96 * S)], fill=color, width=int(3 * S))
                glows.append(((x0 + 19 * S) / 2, (wall_top + 68 * S) / 2))
    return down(img), glows


def mosque(scale=1.0, color=SILH):
    """Village mosque silhouette: square hall, onion dome with crescent, one slim minaret. Anchor bottom centre."""
    S = 2 * scale
    cw, ch = int(520 * S), int(620 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2 - 40 * S
    base = ch
    d.rectangle([cx - 150 * S, base - 200 * S, cx + 150 * S, base], fill=color)
    d.rectangle([cx - 160 * S, base - 214 * S, cx + 160 * S, base - 196 * S], fill=color)
    # onion dome
    pts = []
    for i in range(41):
        u = i / 40 * math.pi
        r = 110 * S * math.sin(u) ** 0.9 * (1 + 0.15 * math.sin(u * 2))
        pts.append((cx - math.cos(u) * 110 * S, base - 210 * S - math.sin(u) ** 1.2 * 190 * S))
    d.polygon([(cx - 110 * S, base - 206 * S)] + pts + [(cx + 110 * S, base - 206 * S)], fill=color)
    d.line([(cx, base - 400 * S), (cx, base - 440 * S)], fill=color, width=int(5 * S))
    d.ellipse([cx - 16 * S, base - 476 * S, cx + 16 * S, base - 444 * S], fill=color)       # crescent
    d.ellipse([cx - 8 * S, base - 480 * S, cx + 20 * S, base - 452 * S], fill=(0, 0, 0, 0))
    # minaret
    mx = cx + 210 * S
    d.rectangle([mx - 18 * S, base - 470 * S, mx + 18 * S, base], fill=color)
    d.rectangle([mx - 30 * S, base - 400 * S, mx + 30 * S, base - 386 * S], fill=color)
    d.polygon([(mx - 22 * S, base - 470 * S), (mx, base - 540 * S), (mx + 22 * S, base - 470 * S)], fill=color)
    # arched windows (dim)
    for k in (-1, 0, 1):
        x = cx + k * 90 * S
        d.rounded_rectangle([x - 18 * S, base - 150 * S, x + 18 * S, base - 60 * S], 18 * S, fill=(40, 46, 50, 255))
    return down(img)


def rice_terraces(w, y0, y1, sky_col_top=(150, 140, 100), sky_col_bot=(70, 70, 70), seed=0, dark=(10, 14, 12)):
    """Flooded paddies: curved dark dykes with strips of water reflecting the sky, rice seedlings in rows."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y0, w, y1], fill=dark + (255,))
    rows = 7
    y = y0 + 8
    for k in range(rows):
        hh = (y1 - y0) / rows * (0.6 + 0.8 * k / rows)
        u = k / rows
        col = tuple(int(a * (1 - u) + b * u) for a, b in zip(sky_col_top, sky_col_bot))
        pts_top, pts_bot = [], []
        ph = rnd.uniform(0, 6)
        for i in range(0, w + 41, 40):
            off = 10 * math.sin(i / 260 + ph)
            pts_top.append((i, y + off + 5))
            pts_bot.append((i, y + off + hh - 7))
        d.polygon(pts_top + pts_bot[::-1], fill=col + (255,))
        # rows of seedlings
        for i in range(rnd.randint(0, 30), w, rnd.randint(26, 40)):
            off = 10 * math.sin(i / 260 + ph)
            for j in range(3):
                yy = y + off + 10 + j * (hh - 20) / 3
                d.line([(i, yy), (i - 3, yy - 6 - 3 * u)], fill=dark + (255,), width=2)
        y += hh
    return img


def bamboo_pole_flag(scale=1.0, t=0.0, color=SILH, flag=FLAG):
    """A bamboo pole with a small yellow funeral flag waving in the storm wind. Anchor: bottom centre."""
    S = 2 * scale
    cw, ch = int(240 * S), int(520 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    px = 60 * S
    d.line([(px, ch), (px + 6 * S, 20 * S)], fill=color, width=int(8 * S))
    for k in range(1, 7):
        d.line([(px - 5 * S, ch - k * 70 * S), (px + 7 * S, ch - k * 70 * S)], fill=color, width=int(3 * S))
    top, fh = 40 * S, 90 * S
    pts_t, pts_b = [], []
    for i in range(21):
        u = i / 20
        wv = 14 * S * u * math.sin(t * 6 - u * 5)
        pts_t.append((px + 6 * S + 150 * S * u, top + wv + 6 * S * u))
        pts_b.append((px + 6 * S + 150 * S * u, top + fh - 10 * S * u + wv))
    d.polygon(pts_t + pts_b[::-1], fill=flag + (255,))
    for i in range(0, 20, 4):   # fold shading
        a, b = pts_t[i], pts_b[i]
        d.line([a, b], fill=(200, 160, 20, 255), width=int(2 * S))
    return down(img)


def frangipani_tree(scale=1.0, seed=0, color=SILH, flowers=True, flower_col=(250, 236, 226)):
    """Old kamboja tree: short twisted trunk, thick candelabra branches, leaf clusters and pale flowers at tips.
    Anchor: bottom centre. Returns (img, tips list in 1x coords)."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(700 * S), int(760 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tips = []

    def branch(x, y, ang, ln, wd, depth):
        x2, y2 = x + math.cos(ang) * ln, y + math.sin(ang) * ln
        mx, my = (x + x2) / 2 + rnd.uniform(-12, 12) * S, (y + y2) / 2
        d.line([(x, y), (mx, my), (x2, y2)], fill=color, width=int(wd), joint="curve")
        d.ellipse([x2 - wd / 2, y2 - wd / 2, x2 + wd / 2, y2 + wd / 2], fill=color)
        if depth == 0:
            tips.append((x2, y2))
            return
        n = 2 if depth > 1 else rnd.randint(2, 3)
        for k in range(n):
            a = ang + (-0.5 + k / max(1, n - 1)) * 1.0 + rnd.uniform(-0.15, 0.15)
            a = min(-0.35, max(-math.pi + 0.35, a))
            branch(x2, y2, a, ln * rnd.uniform(0.62, 0.8), wd * 0.66, depth - 1)

    bx, by = cw / 2, ch
    d.polygon([(bx - 40 * S, by), (bx + 40 * S, by), (bx + 18 * S, by - 150 * S), (bx - 22 * S, by - 150 * S)], fill=color)
    branch(bx - 4 * S, by - 140 * S, -math.pi / 2 - 0.55, 150 * S, 34 * S, 3)
    branch(bx + 4 * S, by - 140 * S, -math.pi / 2 + 0.5, 140 * S, 32 * S, 3)
    for (x, y) in tips:   # leaf rosettes: long paddle leaves splayed upward
        for k in range(6):
            a = -math.pi / 2 + (k - 2.5) * 0.45 + rnd.uniform(-0.1, 0.1)
            L = rnd.uniform(44, 70) * S
            ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
            nx, ny = -math.sin(a) * 11 * S, math.cos(a) * 11 * S
            d.polygon([(x, y), ((x + ex) / 2 + nx, (y + ey) / 2 + ny), (ex, ey), ((x + ex) / 2 - nx, (y + ey) / 2 - ny)], fill=color)
    im = down(img)
    tips1 = [(x / 2, y / 2) for x, y in tips]
    if flowers:
        dd = ImageDraw.Draw(im)
        for (x, y) in tips1:
            for k in range(rnd.randint(3, 6)):
                fx, fy = x + rnd.uniform(-22, 22) * scale, y + rnd.uniform(-24, 4) * scale
                r = 6 * scale
                for p in range(5):
                    a = p * 2 * math.pi / 5 + k
                    dd.ellipse([fx + math.cos(a) * r - r * 0.8, fy + math.sin(a) * r - r * 0.8,
                                fx + math.cos(a) * r + r * 0.8, fy + math.sin(a) * r + r * 0.8], fill=flower_col + (255,))
                dd.ellipse([fx - r * 0.5, fy - r * 0.5, fx + r * 0.5, fy + r * 0.5], fill=(250, 206, 90, 255))
    return im, tips1


def grave(scale=1.0, seed=0, color=STONE, shade=(120, 124, 128, 255), mound=(36, 34, 30, 255), fresh=False):
    """Javanese Muslim grave, seen from the side-front: a low earth mound (or a white tiled kijing) with two
    white nisan headstones, one at the head and one at the foot. Anchor bottom centre."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(420 * S), int(240 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    base = ch - 4 * S
    if fresh:
        d.ellipse([cx - 170 * S, base - 60 * S, cx + 170 * S, base + 30 * S], fill=(58, 44, 32, 255))
    else:
        d.rectangle([cx - 160 * S, base - 46 * S, cx + 160 * S, base], fill=color)
        d.rectangle([cx - 160 * S, base - 46 * S, cx + 160 * S, base - 38 * S], fill=tuple(min(255, v + 25) for v in color[:3]) + (255,))
        d.rectangle([cx - 150 * S, base - 38 * S, cx + 150 * S, base - 30 * S], fill=mound)
    kind = rnd.choice(("round", "peak", "flat"))
    for s_, hh in ((-1, 150), (1, 110)):
        x = cx + s_ * 130 * S
        h = hh * 1.2 * S * rnd.uniform(0.9, 1.1)
        w = 60 * S
        if kind == "round":
            d.rounded_rectangle([x - w / 2, base - h, x + w / 2, base - 20 * S], int(w / 2), fill=color)
        elif kind == "peak":
            d.polygon([(x - w / 2, base - 20 * S), (x - w / 2, base - h + 20 * S), (x, base - h), (x + w / 2, base - h + 20 * S),
                       (x + w / 2, base - 20 * S)], fill=color)
        else:
            d.rectangle([x - w / 2, base - h, x + w / 2, base - 20 * S], fill=color)
            d.ellipse([x - w / 3, base - h - 14 * S, x + w / 3, base - h + 10 * S], fill=color)
        d.rectangle([x + w / 2 - 10 * S, base - h + 20 * S, x + w / 2, base - 20 * S], fill=shade)
    if fresh:
        for _ in range(26):   # frangipani petals scattered on fresh earth
            x, y = cx + rnd.uniform(-150, 150) * S, base - rnd.uniform(5, 50) * S
            d.ellipse([x - 6 * S, y - 4 * S, x + 6 * S, y + 4 * S], fill=(250, 236, 226, 255))
    return down(img)


def pelita(scale=1.0, flame=1.0, color=(22, 16, 12, 255)):
    """Wall-hung tin oil lamp (pelita / lampu teplok) with a glass chimney. Returns (img, flame point)."""
    S = 2 * scale
    cw, ch = int(120 * S), int(220 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([54 * S, 150 * S, 66 * S, 216 * S], fill=color)                           # wall bracket
    d.rounded_rectangle([32 * S, 150 * S, 88 * S, 190 * S], 10 * S, fill=color)            # tin font
    d.ellipse([34 * S, 56 * S, 86 * S, 150 * S], outline=(230, 210, 170, 140), width=int(3 * S))  # glass chimney
    d.ellipse([50 * S, (110 - 26 * flame) * S, 70 * S, 132 * S], fill=(255, 200, 90, 255))
    d.ellipse([55 * S, (116 - 12 * flame) * S, 65 * S, 130 * S], fill=(255, 250, 220, 255))
    return down(img), (60 * scale, 118 * scale)


# ---------------------------------------------------------------- characters
def _rim(img, rim, dx=5, dy=3):
    A = np.array(img.split()[3]).astype(np.int16)
    sh_ = np.zeros_like(A); sh_[dy:, :-dx] = A[:-dy, dx:]
    arr = np.array(img); m = np.clip(A - sh_, 0, 255) > 0
    arr[m, 0], arr[m, 1], arr[m, 2] = rim
    return Image.fromarray(arr)


def bayu(phase=0.0, walking=True, facing=1, color=(6, 8, 12, 255), rim=(150, 170, 210), scale=1.0, run=False,
         tremble=0.0, torch=0.0, arm_up=0.0, look_back=0.0):
    """Bayu: slim boy in a black peci cap, a sarong-check shirt and long trousers (side view).
    torch 0..1 raises the front arm holding a torch forward. Returns (img, feet anchor, torch tip) in output px."""
    cw, ch = 340, 480
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 150
    amp = float(walking) * (1.5 if run else 1.0)
    bob = -7 * abs(math.cos(phase)) * amp
    lean = 0.2 if run else 0.0
    hip = (cx, 280 + bob)
    sw = math.sin(phase) * amp

    def limb(p, a1, l1, a2, l2, wd):
        k = (p[0] + math.sin(a1) * l1, p[1] + math.cos(a1) * l1)
        e = (k[0] + math.sin(a2) * l2, k[1] + math.cos(a2) * l2)
        d.line([p, k], fill=color, width=wd); d.line([k, e], fill=color, width=wd)
        for q in (p, k):
            d.ellipse([q[0] - wd / 2, q[1] - wd / 2, q[0] + wd / 2, q[1] + wd / 2], fill=color)
        return e

    for s in (1, -1):    # long trouser legs + sandals
        a = 0.45 * sw * s
        bend = 0.6 * max(0, -math.sin(phase + (0 if s > 0 else math.pi))) * amp
        e = limb((hip[0], hip[1] + 10), a, 88, a - bend, 88, 26)
        d.polygon([(e[0] - 10, e[1] + 4), (e[0] + 24, e[1] + 4), (e[0] + 20, e[1] - 6), (e[0] - 8, e[1] - 8)], fill=color)
    sh = (cx + 6 + 60 * lean, 160 + bob + 10 * lean)
    d.polygon([(hip[0] - 28, hip[1] + 6), (hip[0] + 28, hip[1] + 6), (sh[0] + 30, sh[1]), (sh[0] - 30, sh[1])], fill=color)
    d.rounded_rectangle([sh[0] - 34, sh[1] - 8, sh[0] + 34, sh[1] + 40], 14, fill=color)
    # head turned back a little (look_back) + black peci cap (flat top, straight sides)
    hd = (sh[0] + 6 - 8 * look_back, sh[1] - 46)
    d.ellipse([hd[0] - 24, hd[1] - 26, hd[0] + 24, hd[1] + 26], fill=color)
    nose_x = hd[0] + 26 if look_back < 0.5 else hd[0] - 28
    d.ellipse([nose_x - 6, hd[1] - 2, nose_x + 6, hd[1] + 10], fill=color)
    d.rectangle([hd[0] - 9, hd[1] + 18, hd[0] + 11, sh[1]], fill=color)
    d.polygon([(hd[0] - 26, hd[1] - 8), (hd[0] + 25, hd[1] - 12), (hd[0] + 23, hd[1] - 34), (hd[0] - 24, hd[1] - 31)], fill=color)
    # arms: back arm swings, front arm holds the torch
    limb((sh[0] - 4, sh[1] + 8), -0.45 * sw - 0.1, 66, -0.45 * sw - 0.4, 60, 18)
    a1 = 0.4 * sw * (1 - torch) + 0.1 + torch * 1.35 + arm_up * 1.6
    hand = limb((sh[0] + 4, sh[1] + 8), a1, 66, a1 - 0.3 * (1 - torch) - 0.8 * run + torch * 0.25 + arm_up * 0.6, 60, 18)
    tip = hand
    if torch > 0.05:
        ang = a1 + torch * 0.25 - 0.3 * (1 - torch)
        tx, ty = hand[0] + math.sin(ang) * 30, hand[1] + math.cos(ang) * 30
        d.line([hand, (tx, ty)], fill=(30, 34, 40, 255), width=14)
        tip = (tx, ty)
    if rim:
        img = _rim(img, rim)
    if facing < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        tip = (cw - tip[0], tip[1])
    if tremble:
        img = img.rotate(tremble, Image.BICUBIC, center=(cw / 2, ch - 40))
    k = scale / 2
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cw * k / 2, (ch - 40) * k), (tip[0] * k, tip[1] * k)


def eyang(color=(24, 14, 10, 255), rim=(255, 180, 100), scale=1.0, finger=0.0):
    """Eyang (grandmother): upright, kebaya blouse, long narrow batik kain to the ankles, a selendang shawl over one
    shoulder, hair in a round sanggul bun. Faces right; finger 0..1 raises a warning finger.
    Returns (img, feet anchor) in output px."""
    cw, ch = 360, 560
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 150
    d.polygon([(cx - 40, 520), (cx + 46, 520), (cx + 40, 300), (cx - 40, 300)], fill=color)             # kain (narrow)
    d.polygon([(cx - 58, 310), (cx + 56, 310), (cx + 44, 170), (cx - 44, 170)], fill=color)             # kebaya
    d.ellipse([cx - 52, 150, cx + 50, 220], fill=color)
    d.polygon([(cx - 50, 172), (cx - 20, 170), (cx - 64, 420), (cx - 84, 410)], fill=color)              # selendang
    for s_ in (-1, 1):
        d.ellipse([cx + s_ * 18 - 12, 512, cx + s_ * 18 + 22, 528], fill=color)
    d.rectangle([cx - 8, 120, cx + 10, 160], fill=color)
    d.ellipse([cx - 26, 70, cx + 32, 132], fill=color)                     # head
    d.ellipse([cx - 52, 78, cx - 12, 116], fill=color)                     # sanggul bun at the back
    d.polygon([(cx + 30, 100), (cx + 42, 110), (cx + 30, 116)], fill=color)  # nose
    hand = (cx + 70 + 20 * finger, 290 - 150 * finger)
    d.line([(cx + 30, 190), (cx + 60, 250 - 50 * finger), hand], fill=color, width=18, joint="curve")
    d.ellipse([hand[0] - 11, hand[1] - 11, hand[0] + 11, hand[1] + 11], fill=color)
    if finger > 0.3:
        d.line([hand, (hand[0] + 4, hand[1] - 30 * finger)], fill=color, width=8)
    img = _rim(img, rim)
    k = scale
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cx * k, 520 * k)


def pocong(t=0.0, scale=1.0, eyes=1.0, glow=0.6, bow=0.0, untie=0.0, face=True, tint=SHROUD, sway=0.0):
    """The Pocong: a body wrapped in a pale shroud, tied above the head (a flared tuft), at the neck and under the
    feet (a flared hem). An oval opening shows only darkness and two pale eyes, nothing gory.
    bow 0..1 tips the head forward so the top knot faces the viewer. untie 0..1 loosens the top knot.
    Returns RGBA; anchor = bottom centre (feet); face centre at (w/2, ~(230+40*bow)*scale)."""
    S = 2 * scale
    cw, ch = int(380 * S), int(920 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    col = tint + (255,)
    dark = tuple(int(v * 0.74) for v in tint) + (255,)
    by = lambda y: y * S
    hb = 40 * bow
    # body outline (left and right edges), slightly lumpy
    prof = [(130, 0), (175, 62), (240, 78), (300, 98), (380, 104), (500, 100), (640, 92), (760, 80), (820, 50), (850, 46)]
    L, R = [], []
    for y, w in prof:
        wob = 3 * math.sin(y * 0.05 + t * 1.3)
        L.append((cx - (w + wob) * S + sway * (850 - y) * 0.05 * S, by(y + hb * (1 - y / 850))))
        R.append((cx + (w - wob) * S + sway * (850 - y) * 0.05 * S, by(y + hb * (1 - y / 850))))
    # head dome on top
    top_y = by(130 + hb)
    head = []
    for i in range(21):
        u = math.pi + i / 20 * math.pi
        head.append((cx + math.cos(u) * 80 * S, top_y + 70 * S + math.sin(u) * 74 * S))
    d.polygon(head + R[2:] + L[2:][::-1], fill=col)
    d.ellipse([cx - 80 * S, top_y - 4 * S, cx + 80 * S, top_y + 144 * S], fill=col)
    # shading: darker right side + fold lines
    shade = Image.new("L", (cw // 8, ch // 8), 0)
    sd = ImageDraw.Draw(shade)
    sd.polygon([((cx + 30 * S) / 8, by(200 + hb) / 8), ((cx + 110 * S) / 8, by(300) / 8), ((cx + 100 * S) / 8, by(760) / 8),
                ((cx + 30 * S) / 8, by(820) / 8)], fill=70)
    shade = shade.filter(ImageFilter.GaussianBlur(30 * S / 8))
    for k in range(7):
        y0 = 330 + k * 66
        xo = (-60 + 22 * k) % 140 - 70
        d.arc([cx + (xo - 70) * S, by(y0), cx + (xo + 80) * S, by(y0 + 70)], 200, 330, fill=dark, width=int(3 * S))
    d.line([(cx - 20 * S, by(320)), (cx - 34 * S, by(800))], fill=dark, width=int(3 * S))
    d.line([(cx + 40 * S, by(330)), (cx + 52 * S, by(790))], fill=dark, width=int(2 * S))
    # ties: neck + feet (rope bands)
    rope = ROPE + (255,)
    ny = by(268 + hb * 0.8)
    d.rounded_rectangle([cx - 66 * S, ny - 7 * S, cx + 66 * S, ny + 7 * S], 6 * S, fill=rope)
    fy = by(818)
    d.rounded_rectangle([cx - 54 * S, fy - 7 * S, cx + 54 * S, fy + 7 * S], 6 * S, fill=rope)
    # flared hem below the foot tie
    d.polygon([(cx - 50 * S, fy), (cx + 50 * S, fy), (cx + 66 * S, by(900)), (cx + 20 * S, by(890)), (cx - 10 * S, by(904)),
               (cx - 66 * S, by(896))], fill=col)
    # top knot: rope band + flared tuft above the head (opens and droops as it is untied)
    ky = top_y + 8 * S
    tuft_open = 1 - 0.8 * untie
    if untie < 0.6:
        d.rounded_rectangle([cx - 26 * S, ky - 8 * S, cx + 26 * S, ky + 6 * S], 6 * S, fill=rope)
    for s_ in (-1, 1):
        tx = cx + s_ * (30 + 50 * untie) * S
        tyy = ky - (64 * tuft_open + 10) * S
        d.polygon([(cx - 14 * S, ky), (cx + 14 * S, ky), (tx + s_ * 22 * S, tyy + 10 * S * untie), (tx - s_ * 4 * S, tyy - 8 * S)], fill=col)
    if untie > 0.3:   # loose rope end hanging
        d.line([(cx + 20 * S, ky), (cx + 60 * S, ky + 60 * S * untie), (cx + 50 * S, ky + 120 * S * untie)], fill=rope, width=int(5 * S))
    # face opening
    fcy = top_y + (88 + 30 * bow) * S
    if face:
        fh = (56 - 30 * bow) * S
        d.ellipse([cx - 38 * S, fcy - fh, cx + 38 * S, fcy + fh], fill=(26, 28, 32, 255))
        d.arc([cx - 42 * S, fcy - fh - 4 * S, cx + 42 * S, fcy + fh + 4 * S], 0, 360, fill=dark, width=int(5 * S))
        if eyes > 0.05 and bow < 0.8:
            for s_ in (-1, 1):
                ex = cx + s_ * 17 * S
                d.ellipse([ex - 9 * S, fcy - 14 * S * (1 - bow), ex + 9 * S, fcy + 4 * S * (1 - bow)], fill=(238, 240, 232, 255))
                d.ellipse([ex - 3 * S, fcy - 8 * S * (1 - bow), ex + 3 * S, fcy - 2 * S * (1 - bow)], fill=(20, 20, 24, 255))
    im = down(img)
    a = np.array(im).astype(np.float32)
    sh = np.array(shade.resize(im.size)).astype(np.float32) / 255
    a[..., :3] *= (1 - sh[..., None] * 0.9)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    out = Image.new("RGBA", (im.width + int(120 * scale), im.height + int(60 * scale)), (0, 0, 0, 0))
    ox, oy = int(60 * scale), int(30 * scale)
    if glow > 0:
        al = im.split()[3].filter(ImageFilter.GaussianBlur(18 * scale))
        g = Image.new("RGBA", im.size, (200, 220, 255, 0)); g.putalpha(al.point(lambda v: int(v * 0.5 * glow)))
        out.alpha_composite(g, (ox, oy))
    out.alpha_composite(im, (ox, oy))
    if face and eyes > 0.05 and bow < 0.8:
        eg = glow_sprite(int(18 * scale) + 2, (220, 235, 255), 1.6)
        arr = np.asarray(out).astype(np.float32)
        rgb = arr[..., :3]
        for s_ in (-1, 1):
            add_glow(rgb, eg, ox + cw / 4 + s_ * 17 * scale, oy + (fcy - 5 * S) / 2, eyes * 0.8)
        arr[..., :3] = np.clip(rgb, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
    out.info["face"] = (ox + cw / 4, oy + fcy / 2)
    out.info["knot"] = (ox + cw / 4, oy + ky / 2)
    return out


def shroud_pile(scale=1.0, tint=SHROUD):
    """The empty shroud lying on the ground, loosely folded, rope loose. Anchor bottom centre."""
    S = 2 * scale
    cw, ch = int(520 * S), int(140 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = tint + (255,); dark = tuple(int(v * 0.72) for v in tint) + (255,)
    d.polygon([(20 * S, ch), (60 * S, 70 * S), (160 * S, 40 * S), (300 * S, 30 * S), (430 * S, 56 * S), (500 * S, ch)], fill=col)
    for k in range(6):
        x = 70 * S + k * 70 * S
        d.arc([x, 50 * S, x + 90 * S, 160 * S], 200, 320, fill=dark, width=int(3 * S))
    d.line([(150 * S, 110 * S), (220 * S, 90 * S), (260 * S, 120 * S), (330 * S, 100 * S)], fill=ROPE + (255,), width=int(5 * S))
    return down(img)


# ---------------------------------------------------------------- particles
class Rain:
    def __init__(self, n=260, seed=1, speed=1900, slant=0.18, length=46, color=(170, 184, 210)):
        rnd = random.Random(seed)
        self.q = [(rnd.uniform(-200, W + 200), rnd.uniform(0, H), rnd.uniform(0.7, 1.2), rnd.uniform(0.3, 1.0)) for _ in range(n)]
        self.speed, self.slant, self.length, self.color = speed, slant, length, color

    def layer(self, t, k=1.0):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if k <= 0.01:
            return img
        d = ImageDraw.Draw(img)
        for x, y, sp, b in self.q:
            yy = (y + t * self.speed * sp) % (H + 100) - 50
            xx = x + (yy - y) * self.slant * 0 + self.slant * yy
            xx = xx % (W + 200) - 100
            L = self.length * sp
            d.line([(xx, yy), (xx - self.slant * L, yy - L)], fill=self.color + (int(120 * b * k),), width=2)
        return img


class Petals2:
    """Frangipani petals blown sideways by the storm wind."""
    def __init__(self, n=18, seed=2, area=(0, 300, W, 1300)):
        rnd = random.Random(seed)
        self.q = [dict(x=rnd.uniform(area[0], area[2]), y=rnd.uniform(area[1], area[3]), vx=rnd.uniform(60, 140),
                       vy=rnd.uniform(20, 60), ph=rnd.uniform(0, 6.3), r=rnd.uniform(5, 9)) for _ in range(n)]

    def draw(self, img, t, k=1.0):
        if k <= 0.01:
            return
        d = ImageDraw.Draw(img)
        for q in self.q:
            x = (q["x"] + q["vx"] * t) % (W + 60) - 30
            y = q["y"] + q["vy"] * t + 30 * math.sin(t * 2 + q["ph"])
            y = y % H
            r = q["r"]
            a = t * 3 + q["ph"]
            for p in range(5):
                aa = a + p * 2 * math.pi / 5
                d.ellipse([x + math.cos(aa) * r * 0.8 - r * 0.6, y + math.sin(aa) * r * 0.8 - r * 0.6,
                           x + math.cos(aa) * r * 0.8 + r * 0.6, y + math.sin(aa) * r * 0.8 + r * 0.6],
                          fill=(250, 238, 228, int(230 * k)))
            d.ellipse([x - r * 0.35, y - r * 0.35, x + r * 0.35, y + r * 0.35], fill=(250, 206, 90, int(230 * k)))


def beam(img_size, origin, angle, length, spread, color=TORCH, k=1.0, blur=26):
    """Additive torch beam (float RGB array, add it onto a frame)."""
    w, h = img_size[0] // 4, img_size[1] // 4
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    ox, oy = origin[0] / 4, origin[1] / 4
    L = length / 4
    pts = [(ox, oy)]
    for i in range(9):
        a = angle - spread + 2 * spread * i / 8
        pts.append((ox + math.cos(a) * L, oy + math.sin(a) * L))
    d.polygon(pts, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(blur / 4))
    a = np.asarray(m).astype(np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xx - ox) ** 2 + (yy - oy) ** 2) / L
    a = (a * np.clip(1 - dist, 0, 1) ** 1.2).astype(np.float32)
    a = np.asarray(Image.fromarray(a, "F").resize(img_size, Image.BILINEAR))
    return a[..., None] * np.array(color, np.float32) * 0.55 * k


def kawung_bg(top=(16, 18, 30), bot=(44, 34, 30)):
    """Explain/outro background: slate-to-umber gradient with a faint kawung batik pattern (four ovals around a dot)."""
    y = np.linspace(0, 1, H)[:, None, None]
    base = np.repeat(np.array(top) * (1 - y) + np.array(bot) * y, W, axis=1).astype(np.float32)
    tile = 120
    m = Image.new("L", (tile * 2, tile * 2), 0)
    d = ImageDraw.Draw(m)
    c = tile
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        x, y = c + math.cos(ang) * tile * 0.36, c + math.sin(ang) * tile * 0.36
        pts = []
        for i in range(30):
            u = i / 30 * 2 * math.pi
            px, py = math.cos(u) * tile * 0.34, math.sin(u) * tile * 0.17
            pts.append((x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)))
        d.polygon(pts, outline=255, width=4)
    d.ellipse([c - 8, c - 8, c + 8, c + 8], fill=255)
    m = np.asarray(m.resize((tile, tile), Image.LANCZOS)).astype(np.float32) / 255
    pat = np.tile(m, (H // tile + 1, W // tile + 1))[:H, :W]
    base += pat[..., None] * np.array([14, 12, 9], np.float32)
    return base
