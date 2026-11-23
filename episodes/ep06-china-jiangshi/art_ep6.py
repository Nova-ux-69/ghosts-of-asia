"""Episode 6 (China, Jiangshi) drawing helpers: a river town in Xiangxi, western Hunan, at night.
Tall misty karst pillars with pines, wooden diaojiaolou stilt houses over a river with grey tile roofs and upturned
eaves, red paper lanterns, a lattice-window inn room, a plank shed with moonlight slats, a Taoist priest with a hand
bell, Mei (a young innkeeper with a hair bun and a mandarin-collar tunic) and the Jiangshi: a stiff corpse in a
Qing official's robe and hat, a yellow paper talisman hanging over its face, arms held straight out.
Palette: jade-green mist and night, pale jade moon, vermilion lanterns, talisman yellow with cinnabar script,
indigo robes with teal trim."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *

# ---------------------------------------------------------------- palette
JADE_TOP = (4, 14, 16)
JADE_BOT = (36, 72, 66)
PEAK_FAR = (40, 70, 66, 255)
PEAK_MID = (20, 40, 40, 255)
SILH = (4, 9, 10, 255)
LANTERN = (230, 60, 34)
LANTERN_GLOW = (255, 110, 60)
CANDLE = (255, 190, 110)
PAPER = (240, 204, 70)
CINNABAR = (196, 30, 24)
ROBE = (22, 28, 52)
ROBE_TRIM = (52, 104, 112)
SKIN_DEAD = (150, 170, 152)
MOONLIGHT = (180, 230, 210)
CJK = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"


def cjk(size):
    from PIL import ImageFont
    return ImageFont.truetype(CJK, size, index=0)


# ---------------------------------------------------------------- landscape
def karst(w, base, color, seed=1, hmin=380, hmax=760, wmin=90, wmax=180, gap=(40, 160), pines=True):
    """Tall limestone pillars (Xiangxi / Zhangjiajie style): near-vertical sides, rounded tops, pine tufts."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = rnd.uniform(-60, 40)
    while x < w + 100:
        pw = rnd.uniform(wmin, wmax); ph = rnd.uniform(hmin, hmax)
        top = base - ph
        pts = []
        for i in range(13):
            u = i / 12
            pts.append((x - pw / 2 - 10 * math.sin(u * 7 + seed) - 12 * u, top + 30 + (base - top) * u))
        L = pts
        R = [(x + pw / 2 + 10 * math.sin(u * 5 + seed) + 12 * (i / 12), y) for i, ((_, y), u) in enumerate(zip(pts, [k / 12 for k in range(13)]))]
        d.polygon(L + R[::-1], fill=color)
        d.ellipse([x - pw / 2 - 2, top, x + pw / 2 + 2, top + 70], fill=color)
        if pines:
            for k in range(rnd.randint(2, 4)):
                px = x + rnd.uniform(-pw / 2.4, pw / 2.4); py = top + rnd.uniform(0, 14)
                th = rnd.uniform(30, 60)
                d.line([(px, py + 10), (px + rnd.uniform(-6, 6), py - th)], fill=color, width=4)
                for j in range(4):
                    yy = py - th * (0.3 + 0.2 * j); ww = 30 - 6 * j
                    d.ellipse([px - ww, yy - 7, px + ww, yy + 7], fill=color)
        # streaks down the cliff face
        for k in range(3):
            sx = x + rnd.uniform(-pw / 3, pw / 3)
            d.line([(sx, top + 60), (sx + rnd.uniform(-8, 8), base)], fill=tuple(max(0, v - 10) for v in color[:3]) + (255,), width=3)
        x += pw + rnd.uniform(*gap)
    return img


def mist_band(w, y, h, color=(150, 200, 186), alpha=150, seed=0):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w // 4, H // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(int(w / 60)):
        x = rnd.uniform(-50, w / 4 + 50); yy = (y + rnd.uniform(-h / 3, h / 3)) / 4
        r = rnd.uniform(40, 110) / 4
        d.ellipse([x - r * 3, yy - r * 0.6, x + r * 3, yy + r * 0.6], fill=color + (alpha,))
    img = img.filter(ImageFilter.GaussianBlur(8))
    return img.resize((w, H), Image.BILINEAR)


def jade_sky(w=W, top=JADE_TOP, bot=JADE_BOT, moon=(780, 360), moon_r=70, seed=1, stars=90):
    s = sky(top, bot, moon=moon, moon_r=moon_r, stars=stars, seed=seed, w=w)
    if moon:
        a = np.asarray(s).astype(np.float32)
        g = glow_sprite(int(moon_r * 4), (120, 200, 170), 2.2)
        add_glow(a[..., :3], g, moon[0], moon[1], 0.45)
        s = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return s


def lantern(scale=1.0, color=LANTERN, lit=1.0):
    """Red paper lantern: oval body with ribs, gold caps, a red tassel. Anchor: top centre (string)."""
    S = 2 * scale
    cw, ch = int(100 * S), int(190 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    body = tuple(int(v * (0.55 + 0.45 * lit)) for v in color) + (255,)
    d.line([(cx, 0), (cx, 20 * S)], fill=(20, 14, 10, 255), width=int(2 * S))
    d.ellipse([cx - 46 * S, 26 * S, cx + 46 * S, 126 * S], fill=body)
    for k in (-2, -1, 0, 1, 2):
        d.arc([cx - abs(k) * 14 * S - 4 * S, 26 * S, cx + abs(k) * 14 * S + 4 * S, 126 * S], 270 if k < 0 else 90, 90 if k < 0 else 270,
              fill=tuple(int(v * 0.7) for v in body[:3]) + (255,), width=int(2 * S))
    gold = (200, 150, 60, 255)
    d.rectangle([cx - 22 * S, 18 * S, cx + 22 * S, 32 * S], fill=gold)
    d.rectangle([cx - 22 * S, 120 * S, cx + 22 * S, 134 * S], fill=gold)
    for k in range(-3, 4):
        d.line([(cx + k * 3 * S, 134 * S), (cx + k * 4 * S, 186 * S)], fill=(200, 30, 24, 255), width=int(2 * S))
    return down(img)


def stilt_house(scale=1.0, seed=0, color=SILH, lit=True, roof=(30, 36, 40, 255)):
    """Diaojiaolou: a wooden house on tall stilts over the river, a hanging balcony with railings, a grey tile roof
    with upturned flying-eave corners. Returns (img, window glow points, lantern hook points) in 1x coords.
    Anchor: bottom centre = where the stilts meet the water."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(560 * S), int(700 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    base = ch
    floor = base - 260 * S
    for k in range(-3, 4):                                   # stilts + cross braces
        x = cx + k * 70 * S
        d.rectangle([x - 6 * S, floor, x + 6 * S, base], fill=color)
    d.line([(cx - 210 * S, floor + 80 * S), (cx + 210 * S, floor + 80 * S)], fill=color, width=int(6 * S))
    for k in range(-3, 3):
        x = cx + k * 70 * S
        d.line([(x, floor + 20 * S), (x + 70 * S, floor + 160 * S)], fill=color, width=int(4 * S))
    wall_top = floor - 200 * S
    d.rectangle([cx - 200 * S, wall_top, cx + 200 * S, floor], fill=color)
    # hanging balcony (front, lower) with railing
    by = floor - 20 * S
    d.rectangle([cx - 240 * S, by, cx + 240 * S, by + 18 * S], fill=color)
    d.line([(cx - 240 * S, by - 60 * S), (cx + 240 * S, by - 60 * S)], fill=color, width=int(6 * S))
    for k in range(-12, 13):
        d.line([(cx + k * 20 * S, by - 60 * S), (cx + k * 20 * S, by)], fill=color, width=int(3 * S))
    # roof: tiles + upturned corners
    ry = wall_top + 6 * S
    d.polygon([(cx - 270 * S, ry), (cx - 140 * S, ry - 120 * S), (cx + 140 * S, ry - 120 * S), (cx + 270 * S, ry)], fill=roof)
    for s_ in (-1, 1):
        d.polygon([(cx + s_ * 250 * S, ry + 2 * S), (cx + s_ * 300 * S, ry - 34 * S), (cx + s_ * 284 * S, ry - 6 * S),
                   (cx + s_ * 270 * S, ry + 6 * S)], fill=roof)
    for k in range(-13, 14):                                 # tile ridges
        x0 = cx + k * 20 * S
        d.line([(x0, ry - 2 * S), (cx + k * 10.5 * S, ry - 118 * S)], fill=tuple(max(0, v - 12) for v in roof[:3]) + (255,), width=int(2 * S))
    d.line([(cx - 150 * S, ry - 122 * S), (cx + 150 * S, ry - 122 * S)], fill=roof, width=int(10 * S))
    for s_ in (-1, 1):
        d.polygon([(cx + s_ * 140 * S, ry - 126 * S), (cx + s_ * 172 * S, ry - 150 * S), (cx + s_ * 160 * S, ry - 118 * S)], fill=roof)
    glows, hooks = [], []
    if lit:
        for k in (-1, 1):
            if rnd.random() < 0.9:
                x0 = cx + k * 100 * S - 40 * S; y0 = wall_top + 50 * S
                d.rectangle([x0, y0, x0 + 80 * S, y0 + 70 * S], fill=(255, 176, 96, 255))
                for j in range(1, 4):   # lattice
                    d.line([(x0 + j * 20 * S, y0), (x0 + j * 20 * S, y0 + 70 * S)], fill=color, width=int(2 * S))
                d.line([(x0, y0 + 35 * S), (x0 + 80 * S, y0 + 35 * S)], fill=color, width=int(2 * S))
                glows.append(((x0 + 40 * S) / 2, (y0 + 35 * S) / 2))
    for s_ in (-1, 1):
        hooks.append(((cx + s_ * 230 * S) / 2, (ry + 4 * S) / 2))
    return down(img), glows, hooks


def river(w, y0, y1, top=(20, 46, 44), bot=(6, 16, 18), seed=0):
    """Dark river with horizontal ripple lines (RGBA)."""
    rnd = random.Random(seed)
    yy = np.linspace(0, 1, y1 - y0)[:, None, None]
    col = np.array(top) * (1 - yy) + np.array(bot) * yy
    arr = np.repeat(col, w, axis=1)
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    img.paste(Image.fromarray(arr.astype(np.uint8)).convert("RGBA"), (0, y0))
    d = ImageDraw.Draw(img)
    for _ in range(int(w / 6)):
        x = rnd.uniform(0, w); y = rnd.uniform(y0 + 4, y1)
        ln = rnd.uniform(20, 90) * (0.5 + (y - y0) / (y1 - y0))
        d.line([(x, y), (x + ln, y)], fill=(60, 100, 96, rnd.randint(40, 110)), width=2)
    return img


def reflect(arr, x, y0, length, color, k=1.0, t=0.0, width=26):
    """Shimmering vertical reflection streak on water (additive on float RGB array)."""
    for i in range(0, int(length), 6):
        yy = int(y0 + i)
        if yy >= arr.shape[0]:
            break
        a = (1 - i / length) ** 1.5 * k * (0.5 + 0.5 * math.sin(i * 0.25 + t * 5))
        ww = width * (0.6 + 0.6 * i / length)
        xx = int(x + 8 * math.sin(i * 0.11 + t * 3))
        x0, x1 = max(0, int(xx - ww / 2)), min(arr.shape[1], int(xx + ww / 2))
        if x1 > x0:
            arr[yy:yy + 3, x0:x1] += np.array(color, np.float32) * a * 0.6


# ---------------------------------------------------------------- talisman
_TAL = {}


def talisman(scale=1.0, blank=False):
    """Yellow paper fulu strip with cinnabar-red script: 敕令 at the top, then swirling strokes. Anchor top centre."""
    key = (round(scale, 3), blank)
    if key in _TAL:
        return _TAL[key]
    S = 2 * scale
    cw, ch = int(64 * S), int(190 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, cw - 1, ch - 1], fill=PAPER + (255,))
    d.rectangle([0, 0, cw - 1, ch - 1], outline=(200, 160, 40, 255), width=int(2 * S))
    if not blank:
        f = cjk(int(26 * S))
        d.text((cw / 2, 26 * S), "敕", font=f, fill=CINNABAR + (255,), anchor="mm")
        d.text((cw / 2, 56 * S), "令", font=f, fill=CINNABAR + (255,), anchor="mm")
        rnd = random.Random(4)
        pts = []
        for i in range(26):
            u = i / 25
            pts.append((cw / 2 + 18 * S * math.sin(u * 13 + 1), 80 * S + u * 96 * S))
        d.line(pts, fill=CINNABAR + (255,), width=int(3 * S), joint="curve")
        for k in range(3):
            y = 96 * S + k * 30 * S
            d.arc([cw / 2 - 16 * S, y, cw / 2 + 16 * S, y + 20 * S], 180, 360, fill=CINNABAR + (255,), width=int(3 * S))
    im = down(img)
    _TAL[key] = im
    return im


# ---------------------------------------------------------------- characters
def _rim(img, rim, dx=5, dy=3):
    A = np.array(img.split()[3]).astype(np.int16)
    sh_ = np.zeros_like(A); sh_[dy:, :-dx] = A[:-dy, dx:]
    arr = np.array(img); m = np.clip(A - sh_, 0, 255) > 0
    arr[m, 0], arr[m, 1], arr[m, 2] = rim
    return Image.fromarray(arr)


def qing_hat_side(d, hx, hy, S, color=(16, 16, 20, 255), red=(170, 26, 24, 255)):
    """Qing official's winter hat from the side: upturned dark brim, red-tassel dome, a knob on top."""
    d.polygon([(hx - 52 * S, hy), (hx + 52 * S, hy), (hx + 46 * S, hy - 26 * S), (hx - 46 * S, hy - 26 * S)], fill=color)
    d.pieslice([hx - 40 * S, hy - 62 * S, hx + 40 * S, hy + 2 * S], 180, 360, fill=red)
    for k in range(-4, 5):
        d.line([(hx, hy - 60 * S), (hx + k * 10 * S, hy - 26 * S)], fill=(120, 14, 14, 255), width=int(2 * S))
    d.ellipse([hx - 9 * S, hy - 78 * S, hx + 9 * S, hy - 58 * S], fill=(190, 160, 70, 255))


def jiangshi_side(scale=1.0, arms=1.0, eyes=0.0, paper=1.0, paper_ang=0.0, facing=1, rim=MOONLIGHT, lean=0.0):
    """The Jiangshi in profile (faces right): indigo Qing robe to the ankles with teal trim, white-soled boots,
    long queue braid, Qing winter hat, pale grey-green skin. arms 0..1 lifts both arms straight forward.
    eyes 0..1 opens glowing eyes. paper 0..1 = talisman attached (alpha), paper_ang tilts it (wind).
    Returns (img, feet anchor) in output px. Body ~ 900*scale px tall."""
    S = 2 * scale
    cw, ch = int(460 * S), int(940 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 170 * S
    robe = ROBE + (255,)
    trim = ROBE_TRIM + (255,)
    skin = SKIN_DEAD + (255,)
    base = ch - 20 * S
    # boots with thick white soles
    d.rectangle([cx - 30 * S, base - 60 * S, cx + 50 * S, base - 14 * S], fill=(12, 12, 14, 255))
    d.rectangle([cx - 34 * S, base - 16 * S, cx + 58 * S, base], fill=(226, 224, 214, 255))
    # robe
    sh_y = 300 * S
    d.polygon([(cx - 62 * S, sh_y), (cx + 58 * S, sh_y), (cx + 82 * S, base - 50 * S), (cx - 86 * S, base - 50 * S)], fill=robe)
    d.rectangle([cx - 86 * S, base - 80 * S, cx + 82 * S, base - 50 * S], fill=trim)
    d.line([(cx + 30 * S, sh_y + 10 * S), (cx + 52 * S, base - 80 * S)], fill=trim, width=int(6 * S))   # front opening
    # queue braid down the back
    d.line([(cx - 34 * S, 200 * S), (cx - 70 * S, 330 * S), (cx - 66 * S, 470 * S)], fill=(10, 10, 12, 255), width=int(12 * S), joint="curve")
    # neck + head (profile)
    d.rectangle([cx - 16 * S, 230 * S, cx + 22 * S, sh_y + 10 * S], fill=skin)
    d.ellipse([cx - 52 * S, 130 * S, cx + 52 * S, 254 * S], fill=skin)
    d.polygon([(cx + 46 * S, 186 * S), (cx + 64 * S, 212 * S), (cx + 46 * S, 218 * S)], fill=skin)       # nose
    d.line([(cx + 30 * S, 234 * S), (cx + 48 * S, 232 * S)], fill=(70, 80, 72, 255), width=int(3 * S))    # lips
    d.ellipse([cx + 14 * S, 160 * S, cx + 40 * S, 190 * S], fill=(96, 112, 100, 255))                     # sunken eye socket
    if eyes > 0.05:
        e = eyes
        d.ellipse([cx + 22 * S, 174 * S - 7 * S * e, cx + 38 * S, 174 * S + 7 * S * e], fill=(210, 255, 220, 255))
    else:
        d.line([(cx + 18 * S, 176 * S), (cx + 38 * S, 178 * S)], fill=(60, 70, 62, 255), width=int(3 * S))
    qing_hat_side(d, cx + 2 * S, 150 * S, S)
    # arms: sleeve from the shoulder, rotating from hanging (0) to straight forward (1)
    a = (1 - arms) * math.pi / 2 * 0.92               # angle from horizontal-forward, downward
    sx, sy = cx + 10 * S, sh_y + 30 * S
    L = 230 * S
    ex, ey = sx + math.cos(a) * L, sy + math.sin(a) * L
    nx, ny = -math.sin(a), math.cos(a)
    w0, w1 = 34 * S, 46 * S
    d.polygon([(sx - nx * w0, sy - ny * w0), (ex - nx * w1, ey - ny * w1), (ex + nx * w1, ey + ny * w1), (sx + nx * w0, sy + ny * w0)], fill=robe)
    d.polygon([(ex - nx * w1, ey - ny * w1), (ex - nx * w1 + math.cos(a) * 22 * S, ey - ny * w1 + math.sin(a) * 22 * S),
               (ex + nx * w1 + math.cos(a) * 22 * S, ey + ny * w1 + math.sin(a) * 22 * S), (ex + nx * w1, ey + ny * w1)], fill=trim)
    hx, hy = ex + math.cos(a) * 40 * S, ey + math.sin(a) * 40 * S
    d.ellipse([hx - 22 * S, hy - 16 * S, hx + 22 * S, hy + 16 * S], fill=skin)
    for k in range(4):                                  # drooping fingers
        fx = hx + math.cos(a) * 14 * S + nx * (k - 1.5) * 7 * S
        fy = hy + math.sin(a) * 14 * S + ny * (k - 1.5) * 7 * S
        d.line([(fx, fy), (fx + math.cos(a + 1.1) * 34 * S, fy + math.sin(a + 1.1) * 34 * S)], fill=skin, width=int(6 * S))
    im = down(img)
    if rim:
        im = _rim(im, rim)
    # talisman hanging from the hat brim over the face
    if paper > 0.02:
        tl = talisman(0.62 * scale)
        tl = tl.rotate(-paper_ang * 57.3, Image.BICUBIC, expand=True, center=(tl.width / 2, 0))
        tl = with_alpha(tl, paper)
        im.alpha_composite(tl, (int((cx + 46 * S) / 2 - tl.width / 2), int(144 * S / 2)))
    if lean:
        im = im.rotate(-lean * 57.3, Image.BICUBIC, center=(cx / 2, base / 2))
    if facing < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        return im, (im.width - cx / 2, base / 2)
    return im, (cx / 2, base / 2)


def jiangshi_front(scale=1.0, arms=1.0, eyes=0.0, paper=1.0, paper_ang=0.0, sniff=0.0):
    """The Jiangshi facing the camera: Qing hat, pale face, mandarin-square badge on the robe, arms raised toward
    the viewer (two big sleeve ovals with hanging hands). sniff -1..1 tilts the head left/right.
    Returns RGBA, anchor bottom centre; .info['face'] = face centre."""
    S = 2 * scale
    cw, ch = int(760 * S), int(1100 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    robe = ROBE + (255,); trim = ROBE_TRIM + (255,); skin = SKIN_DEAD + (255,)
    sh_y = 430 * S
    d.polygon([(cx - 200 * S, sh_y + 40 * S), (cx - 150 * S, sh_y), (cx + 150 * S, sh_y), (cx + 200 * S, sh_y + 40 * S),
               (cx + 250 * S, ch), (cx - 250 * S, ch)], fill=robe)
    d.polygon([(cx - 60 * S, sh_y), (cx, sh_y + 70 * S), (cx + 60 * S, sh_y)], fill=trim)                 # collar
    # mandarin square badge: gold frame, crane over waves
    bx, by = cx, sh_y + 260 * S
    d.rectangle([bx - 110 * S, by - 110 * S, bx + 110 * S, by + 110 * S], fill=(40, 34, 60, 255), outline=(200, 160, 70, 255), width=int(8 * S))
    for k in range(4):
        d.arc([bx - 100 * S + k * 50 * S, by + 50 * S, bx - 50 * S + k * 50 * S, by + 100 * S], 180, 360, fill=(80, 140, 150, 255), width=int(5 * S))
    d.ellipse([bx + 30 * S, by - 80 * S, bx + 70 * S, by - 40 * S], fill=(200, 60, 40, 255))               # sun
    d.polygon([(bx - 70 * S, by + 10 * S), (bx - 10 * S, by - 40 * S), (bx + 40 * S, by - 20 * S), (bx - 20 * S, by + 20 * S)], fill=(230, 226, 214, 255))  # crane
    d.line([(bx - 10 * S, by - 40 * S), (bx - 30 * S, by - 80 * S)], fill=(230, 226, 214, 255), width=int(6 * S))
    d.ellipse([bx - 40 * S, by - 92 * S, bx - 22 * S, by - 76 * S], fill=(200, 40, 30, 255))
    # neck + face
    tilt = sniff * 40 * S
    fx, fy = cx + tilt, 300 * S
    d.rectangle([cx - 44 * S, 360 * S, cx + 44 * S, sh_y + 30 * S], fill=skin)
    d.ellipse([fx - 120 * S, fy - 150 * S, fx + 120 * S, fy + 150 * S], fill=skin)
    sock = (96, 112, 100, 255)
    for s_ in (-1, 1):
        ex = fx + s_ * 50 * S
        d.ellipse([ex - 36 * S, fy - 40 * S, ex + 36 * S, fy + 14 * S], fill=sock)
        if eyes > 0.05:
            d.ellipse([ex - 22 * S, fy - 14 * S - 12 * S * eyes, ex + 22 * S, fy - 14 * S + 12 * S * eyes], fill=(214, 255, 226, 255))
            d.ellipse([ex - 6 * S, fy - 20 * S, ex + 6 * S, fy - 8 * S], fill=(40, 90, 70, 255))
        else:
            d.arc([ex - 24 * S, fy - 30 * S, ex + 24 * S, fy - 4 * S], 20, 160, fill=(50, 60, 54, 255), width=int(4 * S))
    d.line([(fx, fy), (fx - 8 * S, fy + 50 * S), (fx + 10 * S, fy + 56 * S)], fill=(110, 128, 114, 255), width=int(4 * S))
    d.line([(fx - 34 * S, fy + 96 * S), (fx + 34 * S, fy + 96 * S)], fill=(70, 80, 72, 255), width=int(5 * S))
    # hat (front): wide upturned brim + red dome + knob
    hy = fy - 120 * S
    d.ellipse([fx - 170 * S, hy - 30 * S, fx + 170 * S, hy + 30 * S], fill=(16, 16, 20, 255))
    d.pieslice([fx - 130 * S, hy - 140 * S, fx + 130 * S, hy + 20 * S], 180, 360, fill=(170, 26, 24, 255))
    for k in range(-6, 7):
        d.line([(fx, hy - 140 * S), (fx + k * 20 * S, hy - 50 * S)], fill=(120, 14, 14, 255), width=int(3 * S))
    d.ellipse([fx - 22 * S, hy - 176 * S, fx + 22 * S, hy - 134 * S], fill=(190, 160, 70, 255))
    # arms toward the viewer: sleeves as big ovals at chest height, pale hands drooping below
    ar = arms
    for s_ in (-1, 1):
        ax = cx + s_ * (170 - 40 * ar) * S
        ay = sh_y + (360 - 260 * ar) * S
        rw, rh = (70 + 30 * ar) * S, (130 - 50 * ar) * S
        d.ellipse([ax - rw, ay - rh, ax + rw, ay + rh], fill=robe)
        d.ellipse([ax - rw * 0.8, ay - rh * 0.8, ax + rw * 0.8, ay + rh * 0.8], fill=trim)
        d.ellipse([ax - rw * 0.62, ay - rh * 0.62, ax + rw * 0.62, ay + rh * 0.62], fill=(8, 10, 16, 255))
        if ar > 0.4:
            for k in range(4):
                x = ax + (k - 1.5) * 22 * S
                d.line([(x, ay + rh * 0.3), (x + (k - 1.5) * 3 * S, ay + rh * 0.3 + 90 * S * ar)], fill=skin, width=int(16 * S))
    im = down(img)
    im = _rim(im, MOONLIGHT, 6, 4)
    if paper > 0.02:
        tl = talisman(1.42 * scale)
        tl = tl.rotate(-paper_ang * 57.3, Image.BICUBIC, expand=True, center=(tl.width / 2, 0))
        im.alpha_composite(with_alpha(tl, paper), (int(fx / 2 - tl.width / 2), int((hy + 10 * S) / 2)))
    if eyes > 0.05:
        a = np.asarray(im).astype(np.float32)
        g = glow_sprite(int(40 * scale) + 2, (140, 255, 190), 1.6)
        rgb = a[..., :3]
        for s_ in (-1, 1):
            add_glow(rgb, g, (fx + s_ * 50 * S) / 2, (fy - 14 * S) / 2, 0.7 * eyes * (1 - 0.8 * paper))
        a[..., :3] = np.clip(rgb, 0, 255)
        im = Image.fromarray(a.astype(np.uint8))
    im.info["face"] = (fx / 2, fy / 2)
    return im


def mei(phase=0.0, walking=False, facing=1, color=(10, 8, 10, 255), rim=(255, 190, 120), scale=1.0, run=False,
        candle=0.0, reach=0.0, tremble=0.0):
    """Mei (side view): slim young woman with a hair bun and hairpin, mandarin-collar tunic to the hips, loose trousers,
    cloth shoes. candle 0..1 holds a candle forward; reach 0..1 lifts the hand up and forward.
    Returns (img, feet anchor, hand point) in output px."""
    cw, ch = 340, 480
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 150
    amp = float(walking) * (1.5 if run else 1.0)
    bob = -6 * abs(math.cos(phase)) * amp
    hip = (cx, 290 + bob)
    sw = math.sin(phase) * amp

    def limb(p, a1, l1, a2, l2, wd):
        k = (p[0] + math.sin(a1) * l1, p[1] + math.cos(a1) * l1)
        e = (k[0] + math.sin(a2) * l2, k[1] + math.cos(a2) * l2)
        d.line([p, k], fill=color, width=wd); d.line([k, e], fill=color, width=wd)
        for q in (p, k):
            d.ellipse([q[0] - wd / 2, q[1] - wd / 2, q[0] + wd / 2, q[1] + wd / 2], fill=color)
        return e

    for s in (1, -1):
        a = 0.45 * sw * s
        bend = 0.6 * max(0, -math.sin(phase + (0 if s > 0 else math.pi))) * amp
        e = limb((hip[0], hip[1] + 6), a, 84, a - bend, 84, 28)
        d.polygon([(e[0] - 8, e[1] + 4), (e[0] + 22, e[1] + 4), (e[0] + 18, e[1] - 6), (e[0] - 6, e[1] - 8)], fill=color)
    lean = 0.25 if run else 0.0
    sh = (cx + 4 + 60 * lean, 176 + bob + 8 * lean)
    d.polygon([(hip[0] - 36, hip[1] + 20), (hip[0] + 36, hip[1] + 20), (sh[0] + 26, sh[1]), (sh[0] - 26, sh[1])], fill=color)  # tunic
    d.rounded_rectangle([sh[0] - 30, sh[1] - 8, sh[0] + 30, sh[1] + 36], 14, fill=color)
    hd = (sh[0] + 6, sh[1] - 44)
    d.ellipse([hd[0] - 22, hd[1] - 25, hd[0] + 22, hd[1] + 25], fill=color)
    d.ellipse([hd[0] + 18, hd[1] - 2, hd[0] + 28, hd[1] + 8], fill=color)                     # nose
    d.ellipse([hd[0] - 40, hd[1] - 30, hd[0] - 6, hd[1] + 2], fill=color)                     # bun
    d.line([(hd[0] - 46, hd[1] - 26), (hd[0] - 2, hd[1] - 8)], fill=color, width=4)           # hairpin
    d.rectangle([hd[0] - 8, hd[1] + 18, hd[0] + 10, sh[1]], fill=color)
    limb((sh[0] - 4, sh[1] + 8), -0.45 * sw - 0.1, 62, -0.45 * sw - 0.3, 56, 16)
    a1 = 0.4 * sw * (1 - candle) * (1 - reach) + 0.1 + candle * 1.0 + reach * 1.9
    hand = limb((sh[0] + 4, sh[1] + 8), a1, 62, a1 - 0.3 * (1 - candle) + candle * 0.5 - 0.7 * run + reach * 0.2, 56, 16)
    tip = hand
    if candle > 0.05:
        d.rectangle([hand[0] - 6, hand[1] - 34, hand[0] + 6, hand[1] + 4], fill=(230, 220, 200, 255))
        tip = (hand[0], hand[1] - 40)
    if rim:
        img = _rim(img, rim)
    if facing < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        tip = (cw - tip[0], tip[1])
    if tremble:
        img = img.rotate(tremble, Image.BICUBIC, center=(cw / 2, ch - 40))
    k = scale / 2
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cw * k / 2 if facing > 0 else cw * k / 2, (ch - 40) * k), (tip[0] * k, tip[1] * k)


def mei_front(scale=1.0, light=1.0, look=0.0, eyes=1.0, hold=0.0, warm=(1.08, 0.96, 0.84)):
    """Mei chest-up facing the camera: black hair with a centre part and a bun, a jade hairpin, a red
    mandarin-collar tunic with knot buttons. hold 0..1 = holding her breath (puffed cheeks, pressed lips).
    look -1..1 moves the eyes sideways."""
    S = 2 * scale
    cw, ch = int(600 * S), int(720 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    tunic = (120, 26, 30, 255)
    d.rounded_rectangle([cx - 220 * S, 490 * S, cx + 220 * S, ch + 60 * S], 120 * S, fill=tunic)
    d.rectangle([cx - 50 * S, 456 * S, cx + 50 * S, 500 * S], fill=(140, 34, 36, 255))         # mandarin collar
    for k in range(3):
        d.ellipse([cx + 40 * S - 9 * S, 530 * S + k * 50 * S, cx + 40 * S + 9 * S, 548 * S + k * 50 * S], fill=(220, 190, 120, 255))
    skin = (226, 186, 150, 255)
    d.rectangle([cx - 40 * S, 380 * S, cx + 40 * S, 470 * S], fill=(200, 160, 126, 255))
    cheek = 14 * hold
    d.ellipse([cx - (120 + cheek) * S, 150 * S, cx + (120 + cheek) * S, 440 * S], fill=skin)
    hair = (12, 10, 12, 255)
    d.chord([cx - 126 * S, 120 * S, cx + 126 * S, 330 * S], 180, 360, fill=hair)              # hair cap
    d.polygon([(cx - 126 * S, 226 * S), (cx - 4 * S, 150 * S), (cx - 96 * S, 300 * S)], fill=hair)
    d.polygon([(cx + 126 * S, 226 * S), (cx + 4 * S, 150 * S), (cx + 96 * S, 300 * S)], fill=hair)
    d.ellipse([cx - 70 * S, 40 * S, cx + 70 * S, 150 * S], fill=hair)                          # bun
    d.line([(cx - 95 * S, 78 * S), (cx + 95 * S, 108 * S)], fill=(90, 170, 130, 255), width=int(8 * S))  # jade hairpin
    if eyes > 0:
        for s_ in (-1, 1):
            ex = cx + s_ * 50 * S
            d.ellipse([ex - 30 * S, 276 * S - 20 * S * eyes, ex + 30 * S, 276 * S + 20 * S * eyes], fill=(248, 246, 240, 255))
            d.ellipse([ex + look * 14 * S - 11 * S, 265 * S, ex + look * 14 * S + 11 * S, 287 * S], fill=(26, 16, 12, 255))
            d.line([(ex - 30 * S, 236 * S - 6 * S * eyes), (ex + 28 * S, 230 * S - 10 * S * eyes)], fill=(30, 20, 16, 255), width=int(6 * S))
    if hold > 0.3:
        d.line([(cx - 26 * S, 376 * S), (cx + 26 * S, 376 * S)], fill=(150, 60, 60, 255), width=int(6 * S))
        for s_ in (-1, 1):
            d.ellipse([cx + s_ * 80 * S - 26 * S, 336 * S, cx + s_ * 80 * S + 26 * S, 366 * S], fill=(236, 140, 130, int(160 * hold)))
    else:
        d.ellipse([cx - 18 * S, 360 * S, cx + 18 * S, 394 * S], fill=(110, 40, 40, 255))
    im = down(img)
    a = np.array(im).astype(np.float32)
    yy = np.linspace(0, 1, im.height)[:, None]
    g = 0.5 + 0.6 * np.clip((yy - 0.15) / 0.5, 0, 1) * light
    a[..., :3] *= g[..., None] * np.array(warm)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def priest(scale=1.0, color=(8, 8, 10, 255), rim=(255, 170, 100), bell_up=0.0, lantern_pole=True, phase=0.0, walking=False, facing=1):
    """Taoist corpse-driver (side view, faces right): long robe with wide sleeves, black flat-topped hat, a little
    beard, a hand bell raised in the front hand, a lantern on a pole over the shoulder.
    Returns (img, feet anchor, bell point, lantern point) in output px."""
    cw, ch = 420, 560
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 190
    amp = float(walking)
    bob = -5 * abs(math.cos(phase)) * amp
    sw = math.sin(phase) * amp
    for s in (1, -1):
        d.line([(cx + s * 10, 400 + bob), (cx + s * 10 + 24 * sw * s, 520)], fill=color, width=24)
        d.ellipse([cx + s * 10 + 24 * sw * s - 10, 508, cx + s * 10 + 24 * sw * s + 26, 528], fill=color)
    d.polygon([(cx - 50, 180 + bob), (cx + 46, 180 + bob), (cx + 66, 470 + bob), (cx - 70, 470 + bob)], fill=color)
    d.ellipse([cx - 30, 100 + bob, cx + 30, 164 + bob], fill=color)                     # head
    d.polygon([(cx + 22, 140 + bob), (cx + 40, 176 + bob), (cx + 14, 170 + bob)], fill=color)  # beard
    d.rectangle([cx - 34, 86 + bob, cx + 30, 110 + bob], fill=color)                      # hat
    d.rectangle([cx - 40, 102 + bob, cx + 36, 112 + bob], fill=color)
    # back arm with lantern pole over the shoulder
    lp_ = None
    if lantern_pole:
        d.line([(cx - 10, 200 + bob), (cx - 110, 60 + bob)], fill=color, width=8)
        lp_ = (cx - 110, 60 + bob)
    # front arm with bell
    a = 0.5 + 1.6 * bell_up
    hx, hy = cx + 20 + math.sin(a) * 120, 200 + bob + math.cos(a) * 110
    d.line([(cx + 10, 200 + bob), (hx, hy)], fill=color, width=30)
    d.polygon([(hx - 12, hy + 6), (hx + 12, hy + 6), (hx + 18, hy + 34), (hx - 18, hy + 34)], fill=color)   # bell
    bp_ = (hx, hy + 24)
    img = _rim(img, rim)
    if facing < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        bp_ = (cw - bp_[0], bp_[1])
        lp_ = (cw - lp_[0], lp_[1]) if lp_ else None
    k = scale / 2
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cx * k if facing > 0 else (cw - cx) * k, 520 * k), (bp_[0] * k, bp_[1] * k), (lp_[0] * k, lp_[1] * k) if lp_ else None


# ---------------------------------------------------------------- particles
class Mist:
    """Slow drifting wisps (RGBA layer) in a vertical band."""
    def __init__(self, n=14, seed=1, y0=900, y1=1300, color=(170, 220, 200), alpha=60, w=W):
        rnd = random.Random(seed)
        self.q = [(rnd.uniform(-300, w), rnd.uniform(y0, y1), rnd.uniform(160, 380), rnd.uniform(10, 40)) for _ in range(n)]
        self.color, self.alpha, self.w = color, alpha, w

    def layer(self, t, k=1.0):
        img = Image.new("RGBA", (self.w // 4, H // 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for x, y, r, v in self.q:
            xx = ((x + v * t) % (self.w + 600) - 300) / 4
            d.ellipse([xx - r / 4, y / 4 - r / 16, xx + r / 4, y / 4 + r / 16], fill=self.color + (int(self.alpha * k),))
        return img.filter(ImageFilter.GaussianBlur(6)).resize((self.w, H), Image.BILINEAR)


def xiangyun_bg(top=(8, 22, 24), bot=(40, 22, 20)):
    """Explain/outro background: jade-to-maroon gradient with a faint auspicious-cloud (xiangyun) pattern."""
    y = np.linspace(0, 1, H)[:, None, None]
    base = np.repeat(np.array(top) * (1 - y) + np.array(bot) * y, W, axis=1).astype(np.float32)
    tile = 180
    m = Image.new("L", (tile * 2, tile * 2), 0)
    d = ImageDraw.Draw(m)
    c = tile
    for dx, r in ((-50, 50), (30, 64), (100, 40)):
        d.arc([c + dx - r, c - r, c + dx + r, c + r], 180, 360, fill=255, width=6)
    for dx, r in ((-50, 26), (30, 34)):
        d.arc([c + dx - r, c - r * 0.3, c + dx + r, c + r * 1.4], 200, 340, fill=255, width=5)
    d.line([(c - 130, c + 4), (c + 160, c + 4)], fill=255, width=5)
    m = np.asarray(m.resize((tile, tile), Image.LANCZOS)).astype(np.float32) / 255
    pat = np.tile(m, (H // tile + 2, W // tile + 2))
    pat = np.roll(pat, tile // 2, axis=1)[:H, :W]
    base += pat[..., None] * np.array([10, 16, 12], np.float32)
    return base
