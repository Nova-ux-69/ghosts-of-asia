"""Episode 7 (Myanmar, Ma Phae Wah) drawing helpers: a small Burmese town beside an old graveyard at midnight.
A crimson moon over a hilltop zedi (stupa) with a hti umbrella spire, teak houses on stilts with two-tier gable roofs
and plank shutters, tamarind and banyan trees, whitewashed tombs in tall grass, a dusty road, a woven-bamboo room
with a clay oil lamp. People: Thiri (a girl with thanaka on her cheeks, longyi, hair tied back) and her Grandma
(grey bun, maroon shawl). The ghost: Ma Phae Wah, too tall and too thin, bone-white skin, a mustard-yellow longyi
tied at the chest, a yellow ribbon in very long black hair that waves in a wind nobody else feels, a dark teak coffin
on her shoulder. Palette: near-black and blood red, with the only strong colour being her yellow."""
import math, random, os
os.environ.setdefault("STYLE", "flat21")          # PLAYBOOK 2d: 2.1D flat-but-creative shading
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *
from depth import inflate_shade, dof, god_rays

# ---------------------------------------------------------------- palette
SKY_TOP = (5, 2, 3)
SKY_BOT = (64, 9, 12)
SILH = (5, 2, 3, 255)
MIDC = (20, 7, 8, 255)
FARC = (36, 10, 12, 255)
MOON_RED = (214, 52, 36)
LAMP = (255, 120, 54)
LAMP_GLOW = (255, 90, 40)
YELLOW = (200, 150, 34)
YELLOW_D = (120, 84, 16)
RIBBON = (232, 186, 40)
BONE = (222, 214, 200)
BONE_D = (150, 140, 128)
HAIR = (6, 4, 6, 255)
COFFIN = (46, 24, 18)
COFFIN_D = (24, 12, 9)
TEAK = (52, 24, 16)
TEAK_D = (28, 12, 9)
TOMB = (120, 100, 96)
RIM_RED = (255, 80, 60)


def _rim(img, rim, dx=5, dy=3):
    A = np.array(img.split()[3]).astype(np.int16)
    sh_ = np.zeros_like(A); sh_[dy:, :-dx] = A[:-dy, dx:]
    arr = np.array(img); m = np.clip(A - sh_, 0, 255) > 0
    arr[m, 0], arr[m, 1], arr[m, 2] = rim
    return Image.fromarray(arr)


# ---------------------------------------------------------------- sky + landscape
def crimson_sky(w=W, h=H, moon=(800, 380), moon_r=78, seed=1, top=SKY_TOP, bot=SKY_BOT, stars=70, moon_k=1.0):
    y = np.linspace(0, 1, h)[:, None, None]
    arr = np.repeat(np.array(top)[None, None, :] * (1 - y) + np.array(bot)[None, None, :] * y, w, axis=1).astype(np.float32)
    rnd = random.Random(seed)
    for _ in range(stars):
        x, yy = rnd.randrange(w), rnd.randrange(int(h * 0.5))
        arr[yy, x] += rnd.uniform(40, 120) * (1 - yy / (h * 0.6)) * np.array([1.0, 0.8, 0.8])
    if moon:
        mx, my = moon
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
        glow = np.exp(-((d / (moon_r * 5)) ** 2)) * 80 + np.exp(-((d / (moon_r * 1.7)) ** 2)) * 70
        arr += (glow[..., None] * np.array([1.0, 0.28, 0.2])) * moon_k
        disk = np.clip((moon_r - d) / 1.5, 0, 1) * moon_k
        crat = np.zeros_like(d)
        for cx, cy, cr in ((-22, -16, 20), (24, 12, 15), (-6, 30, 11), (26, -26, 9)):
            dd = np.sqrt((xx - mx - cx) ** 2 + (yy - my - cy) ** 2)
            crat += np.clip((cr - dd) / 5, 0, 1) * 30
        moonc = np.array(MOON_RED, np.float32)[None, None, :] + np.array([30, 20, 14])[None, None, :] * (1 - d[..., None] / moon_r) - crat[..., None]
        arr = arr * (1 - disk[..., None]) + moonc * disk[..., None]
    # thin cloud bands across the moon
    cl = Image.new("L", (w // 4, h // 4), 0)
    dc = ImageDraw.Draw(cl)
    for _ in range(9):
        x, yy = rnd.uniform(-100, w / 4), rnd.uniform(40, h / 4 * 0.45)
        dc.ellipse([x, yy, x + rnd.uniform(60, 160), yy + rnd.uniform(3, 7)], fill=rnd.randint(90, 160))
    cl = np.asarray(cl.filter(ImageFilter.GaussianBlur(3)).resize((w, h), Image.BILINEAR)).astype(np.float32)[..., None] / 255
    arr = arr * (1 - cl * 0.7) + np.array([14, 4, 5], np.float32) * cl * 0.7
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def hill(w, base, amp, color, seed, h=H):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ph = rnd.uniform(0, 6)
    pts = [(x, base - amp * (0.6 * math.sin(x / 260 + ph) + 0.4 * math.sin(x / 97 + 2 * ph))) for x in range(0, w + 21, 20)]
    ImageDraw.Draw(img).polygon(pts + [(w, h), (0, h)], fill=color)
    return img


def zedi(scale=1.0, color=SILH, rim=(255, 120, 70), gold=0.0):
    """Burmese stupa silhouette: three square terraces, a bell dome, ringed banana-bud spire, hti umbrella.
    gold 0..1 paints it dim gold (dawn). Anchor: bottom centre."""
    S = 2 * scale
    cw, ch = int(520 * S), int(900 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    col = tuple(int(color[i] * (1 - gold) + (150, 104, 40)[i] * gold) for i in range(3)) + (255,)
    y = ch
    for k, (hw, hh) in enumerate(((250, 60), (205, 55), (165, 50))):
        d.rectangle([cx - hw * S, y - hh * S, cx + hw * S, y], fill=col); y -= hh * S
    d.rectangle([cx - 130 * S, y - 30 * S, cx + 130 * S, y], fill=col); y -= 30 * S
    d.chord([cx - 140 * S, y - 250 * S, cx + 140 * S, y + 60 * S], 180, 360, fill=col)                # bell dome
    d.polygon([(cx - 140 * S, y), (cx + 140 * S, y), (cx + 150 * S, y + 6 * S), (cx - 150 * S, y + 6 * S)], fill=col)
    y -= 190 * S
    for k in range(6):                                                                                   # rings
        r = (70 - k * 9) * S
        d.ellipse([cx - r, y - 22 * S, cx + r, y + 8 * S], fill=col); y -= 26 * S
    d.polygon([(cx - 26 * S, y + 6 * S), (cx + 26 * S, y + 6 * S), (cx + 4 * S, y - 150 * S), (cx - 4 * S, y - 150 * S)], fill=col)  # bud
    y -= 150 * S
    d.polygon([(cx - 34 * S, y + 20 * S), (cx + 34 * S, y + 20 * S), (cx, y - 18 * S)], fill=col)     # hti
    d.line([(cx, y), (cx, y - 60 * S)], fill=col, width=int(4 * S))
    d.polygon([(cx, y - 60 * S), (cx + 30 * S, y - 50 * S), (cx, y - 42 * S)], fill=col)                # little flag
    im = down(img)
    return _rim(im, rim, 4, 2) if rim else im


def tamarind(scale=1.0, color=SILH, seed=0):
    """Round, feathery tamarind canopy on a crooked trunk. Anchor bottom centre."""
    rnd = random.Random(seed)
    S = 2 * scale
    img = Image.new("RGBA", (int(700 * S), int(820 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 350 * S
    d.line([(cx, 820 * S), (cx - 20 * S, 600 * S), (cx + 30 * S, 420 * S)], fill=color, width=int(46 * S), joint="curve")
    d.line([(cx + 10 * S, 520 * S), (cx - 160 * S, 360 * S)], fill=color, width=int(22 * S))
    d.line([(cx + 20 * S, 470 * S), (cx + 190 * S, 340 * S)], fill=color, width=int(22 * S))
    for _ in range(70):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(0, 1) ** 0.6
        x, y = cx + math.cos(a) * 280 * S * r, 300 * S + math.sin(a) * 190 * S * r
        rr = rnd.uniform(40, 80) * S
        d.ellipse([x - rr, y - rr * 0.7, x + rr, y + rr * 0.7], fill=color)
    for _ in range(260):                                                                                 # leaf fringe
        a = rnd.uniform(0, 2 * math.pi)
        x, y = cx + math.cos(a) * 300 * S, 300 * S + math.sin(a) * 210 * S
        d.line([(x, y), (x + math.cos(a) * 30 * S, y + math.sin(a) * 30 * S + 10 * S)], fill=color, width=int(5 * S))
    return down(img)


def banyan(scale=1.0, color=SILH, seed=0):
    """Wide banyan with hanging aerial roots (graveyard tree). Anchor bottom centre."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw = int(900 * S)
    img = Image.new("RGBA", (cw, int(900 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    d.polygon([(cx - 90 * S, 900 * S), (cx - 40 * S, 380 * S), (cx + 50 * S, 380 * S), (cx + 100 * S, 900 * S)], fill=color)
    for _ in range(50):
        x, y = cx + rnd.uniform(-420, 420) * S, rnd.uniform(140, 360) * S
        rr = rnd.uniform(60, 110) * S
        d.ellipse([x - rr, y - rr * 0.55, x + rr, y + rr * 0.55], fill=color)
    for _ in range(46):
        x = cx + rnd.uniform(-400, 400) * S
        y0 = rnd.uniform(300, 400) * S
        L = rnd.uniform(160, 520) * S
        d.line([(x, y0), (x + rnd.uniform(-10, 10) * S, y0 + L)], fill=color, width=int(rnd.uniform(3, 7) * S))
    return down(img)


def tomb(scale=1.0, seed=0, col=TOMB):
    """Whitewashed grave: a low plinth with a small domed or pointed headstone, stained and chipped."""
    rnd = random.Random(seed)
    S = 2 * scale
    img = Image.new("RGBA", (int(260 * S), int(260 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = tuple(int(v * rnd.uniform(0.75, 1.0)) for v in col) + (255,)
    sh = tuple(int(v * 0.55) for v in c[:3]) + (255,)
    d.rectangle([20 * S, 190 * S, 240 * S, 260 * S], fill=c)
    d.rectangle([20 * S, 236 * S, 240 * S, 260 * S], fill=sh)
    kind = rnd.random()
    if kind < 0.5:
        d.rectangle([80 * S, 90 * S, 180 * S, 192 * S], fill=c)
        d.pieslice([80 * S, 40 * S, 180 * S, 140 * S], 180, 360, fill=c)
    else:
        d.polygon([(90 * S, 192 * S), (170 * S, 192 * S), (160 * S, 80 * S), (130 * S, 30 * S), (100 * S, 80 * S)], fill=c)
    d.line([(150 * S, 100 * S), (164 * S, 190 * S)], fill=sh, width=int(6 * S))
    img = img.rotate(rnd.uniform(-5, 5), Image.BICUBIC, center=(130 * S, 260 * S))
    return down(img)


def grass(w, y, color=SILH, seed=0, hgt=70, dens=6):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, w, H], fill=color)
    for _ in range(w // dens):
        x = rnd.uniform(0, w); hh = rnd.uniform(0.3, 1) * hgt
        d.line([(x, y + 4), (x + rnd.uniform(-14, 14), y - hh)], fill=color, width=2)
    return img


def teak_house(scale=1.0, seed=0, color=SILH, lit=1.0, shutter=0.0, plank=(30, 12, 9, 255), rim=None):
    """Burmese teak house on stilts: a two-tier gable roof with crossed finials, plank walls, one shuttered window,
    a door at the top of wooden steps on the right. shutter 0 = closed, 1 = open (lamp light shows inside).
    Returns (img, info) with info['win'] (window centre) and info['step'] (doorstep centre) in output px."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(820 * S), int(880 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    floor = 560 * S
    for x in (90, 250, 420, 590):                                                                          # stilts
        d.rectangle([x * S, floor, (x + 26) * S, ch], fill=color)
    d.rectangle([60 * S, 300 * S, 640 * S, floor + 20 * S], fill=plank)                                     # walls
    for x in range(60, 640, 34):
        d.line([(x * S, 300 * S), (x * S, floor + 20 * S)], fill=color, width=int(3 * S))
    d.rectangle([40 * S, floor + 14 * S, 680 * S, floor + 36 * S], fill=color)                              # floor beam
    # lower roof + upper tier
    d.polygon([(10 * S, 320 * S), (690 * S, 320 * S), (600 * S, 190 * S), (100 * S, 190 * S)], fill=color)
    d.polygon([(150 * S, 200 * S), (550 * S, 200 * S), (350 * S, 40 * S)], fill=color)
    d.polygon([(220 * S, 120 * S), (480 * S, 120 * S), (350 * S, 10 * S)], fill=color)
    for fx in (350,):                                                                                       # crossed finial
        d.line([(fx * S, 14 * S), ((fx - 30) * S, -20 * S)], fill=color, width=int(8 * S))
        d.line([(fx * S, 14 * S), ((fx + 30) * S, -20 * S)], fill=color, width=int(8 * S))
    # window with two plank shutters
    wx0, wy0, wx1, wy1 = 170 * S, 360 * S, 330 * S, 500 * S
    wc = (wx0 + wx1) / 2
    if lit > 0:
        lc = tuple(int(c * lit) for c in (240, 110, 50)) + (255,)
        d.rectangle([wx0, wy0, wx1, wy1], fill=lc)
    else:
        d.rectangle([wx0, wy0, wx1, wy1], fill=(10, 4, 4, 255))
    half = (wx1 - wx0) / 2
    for s_ in (-1, 1):                                                                                      # shutters swing out
        hinge = wx0 if s_ < 0 else wx1
        wdt = half * (1 - shutter * 0.85)
        x_in = hinge - s_ * wdt
        poly = [(hinge, wy0), (x_in, wy0 + 6 * S * shutter), (x_in, wy1 - 6 * S * shutter), (hinge, wy1)]
        if shutter > 0.05:
            x_out = hinge + s_ * half * shutter * 0.7
            poly = [(hinge, wy0), (x_out, wy0 - 10 * S * shutter), (x_out, wy1 + 10 * S * shutter), (hinge, wy1)]
        d.polygon(poly, fill=color)
        if shutter <= 0.05:
            d.line([(wc, wy0), (wc, wy1)], fill=(int(80 * lit), int(30 * lit), 14, 255), width=int(4 * S))
    d.rectangle([wx0 - 8 * S, wy1, wx1 + 8 * S, wy1 + 12 * S], fill=color)
    # door + steps on the right
    dx0, dx1 = 470 * S, 590 * S
    d.rectangle([dx0, 330 * S, dx1, floor + 20 * S], fill=(14, 5, 4, 255))
    d.rectangle([dx0, 330 * S, dx1, 342 * S], fill=color)
    step_top = (dx0 + dx1) / 2, floor + 20 * S
    for k in range(6):
        y = floor + 36 * S + k * 46 * S
        x0 = dx0 + 70 * S + k * 30 * S
        d.rectangle([x0 - 120 * S, y, x0 + 40 * S, y + 12 * S], fill=color)
    d.line([(dx1 + 40 * S, floor + 30 * S), (dx1 + 210 * S, ch)], fill=color, width=int(12 * S))
    im = down(img)
    if rim:
        im = _rim(im, rim, 4, 2)
    return im, {"win": (wc / 2, (wy0 + wy1) / 4), "step": (step_top[0] / 2, step_top[1] / 2)}


# ---------------------------------------------------------------- interior
def bamboo_wall(w=W, h=H, base=(44, 20, 14), seed=0):
    """Woven bamboo (thatch-mat) wall: a diagonal twill weave, warm brown in the dark."""
    yy, xx = np.mgrid[0:h, 0:w]
    u, v = (xx + yy) // 26, (xx - yy) // 26
    weave = ((u + (v // 3)) % 2).astype(np.float32)
    shade = 0.75 + 0.25 * weave
    stripe = 0.92 + 0.08 * np.sin((xx + yy) * 0.45) * weave + 0.08 * np.sin((xx - yy) * 0.45) * (1 - weave)
    arr = np.array(base, np.float32)[None, None, :] * (shade * stripe)[..., None]
    rng = np.random.default_rng(seed)
    arr *= (0.9 + 0.1 * rng.random((h, w, 1))).astype(np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def oil_lamp(scale=1.0, lit=1.0):
    """Clay oil lamp on a little stand. Returns (img, flame point) - anchor bottom centre."""
    S = 2 * scale
    img = Image.new("RGBA", (int(200 * S), int(300 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = (60, 26, 16, 255)
    d.polygon([(60 * S, 300 * S), (140 * S, 300 * S), (110 * S, 200 * S), (90 * S, 200 * S)], fill=(30, 14, 10, 255))
    d.chord([40 * S, 150 * S, 160 * S, 220 * S], 0, 180, fill=c)
    d.polygon([(150 * S, 186 * S), (182 * S, 170 * S), (156 * S, 196 * S)], fill=c)
    fp = (176 * S, 150 * S)
    if lit > 0.05:
        d.ellipse([fp[0] - 9 * S, fp[1] - 26 * S * lit, fp[0] + 9 * S, fp[1] + 14 * S], fill=(255, 210, 120, int(255 * lit)))
        d.ellipse([fp[0] - 4 * S, fp[1] - 6 * S, fp[0] + 4 * S, fp[1] + 10 * S], fill=(255, 250, 220, int(255 * lit)))
    return down(img), (fp[0] / 2, fp[1] / 2)


def shutter_frame(w, h, open_=0.0, wood=(40, 18, 12), light=(255, 90, 60), slat_light=0.0, seed=0):
    """A shuttered window seen from inside (two vertical-plank shutters). open_ 0..1 swings the right shutter out,
    showing the night. slat_light adds red moonlight lines through the plank gaps. RGBA with a transparent hole."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fr = 34
    d.rectangle([0, 0, w, h], outline=(18, 8, 6, 255), width=fr)
    half = (w - 2 * fr) / 2
    # left shutter stays closed
    for k in range(5):
        x0 = fr + k * half / 5
        tone = 0.85 + 0.15 * ((k * 37 + seed) % 3) / 2
        d.rectangle([x0, fr, x0 + half / 5 - 4, h - fr], fill=tuple(int(c * tone) for c in wood) + (255,))
        if slat_light > 0:
            d.rectangle([x0 + half / 5 - 4, fr, x0 + half / 5, h - fr], fill=light + (int(200 * slat_light),))
    # right shutter swings open (gets narrower, darker)
    vis = half * (1 - open_)
    for k in range(5):
        x0 = fr + half + k * vis / 5
        d.rectangle([x0, fr, x0 + max(1, vis / 5 - 4), h - fr], fill=tuple(int(c * (0.9 - 0.4 * open_)) for c in wood) + (255,))
        if slat_light > 0 and open_ < 0.05:
            d.rectangle([x0 + vis / 5 - 4, fr, x0 + vis / 5, h - fr], fill=light + (int(200 * slat_light),))
    if open_ > 0.0:
        d.rectangle([fr + half + vis, fr, w - fr, h - fr], fill=(0, 0, 0, 0))
    d.rectangle([fr + half - 3, fr, fr + half + 3, h - fr], fill=(14, 6, 4, 255))
    return img


# ---------------------------------------------------------------- the ghost
def _hair_strands(d, top, length, width, wind, t, S, n=18, col=HAIR, seed=3):
    """Long hair hanging from `top`, blown sideways by `wind` (-1..1) with a slow ripple."""
    rnd = random.Random(seed)
    hx, hy = top
    for i in range(n):
        off = (i / (n - 1) - 0.5) * width
        L = length * rnd.uniform(0.8, 1.05)
        pts = []
        for k in range(14):
            u = k / 13
            sway = wind * L * 0.45 * u ** 1.4 + 18 * S * math.sin(t * 2.2 + u * 5 + i * 0.7) * u
            pts.append((hx + off * (1 - 0.3 * u) + sway, hy + L * u * (1 - 0.25 * abs(wind) * u)))
        d.line(pts, fill=col, width=int(rnd.uniform(9, 16) * S), joint="curve")


def coffin_side(S, length=520, hgt=120):
    """A teak coffin seen from above and to the side: the classic six-sided lid (wide at the shoulders, narrow at
    head and foot) on top of a deep wooden box."""
    L = length * S
    wid = 150 * S
    lidH = wid * 0.34
    depth = hgt * 0.75 * S
    img = Image.new("RGBA", (int(L + 4 * S), int(2 * lidH + depth + 10 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cy = lidH + 4 * S
    xs = [0.0, 0.28, 1.0]
    hw = [0.34, 0.5, 0.38]
    top = [(L * x, cy - h * 2 * lidH) for x, h in zip(xs, hw)]
    bot = [(L * x, cy + h * 2 * lidH * 0.5) for x, h in zip(xs, hw)]
    side = bot + [(x, y + depth) for x, y in reversed(bot)]
    d.polygon(side, fill=COFFIN + (255,))
    for x in (0.28, 0.64):
        d.line([(L * x, cy + 10 * S), (L * x, cy + depth)], fill=COFFIN_D + (255,), width=int(4 * S))
    d.line([(x, y + depth - 3 * S) for x, y in bot], fill=COFFIN_D + (255,), width=int(5 * S))
    lid = top + list(reversed(bot))
    d.polygon(lid, fill=tuple(min(255, int(c * 1.5)) for c in COFFIN) + (255,))
    inner = [(L * 0.04 + (x - L * 0.04) * 0.92, cy + (y - cy) * 0.6) for x, y in lid]
    d.polygon(inner, outline=COFFIN_D + (255,), width=int(4 * S))
    return img


def ghost_side(scale=1.0, t=0.0, step=0.0, facing=1, turn=0.0, eyes=0.0, lower=0.0, wind=-0.8, rim=RIM_RED, coffin=True):
    """Ma Phae Wah in profile (faces right when facing=1). Very tall and thin; the coffin rides on her far shoulder.
    step: walk phase (a dragging shuffle). turn 0..1: the head twists round toward the camera, past where a neck
    should allow, tilting sideways (shows a sliver of pale face and glowing eyes). lower 0..1: the coffin comes down
    off the shoulder to the ground in front of her. Returns (img, info) with feet anchor and 'face' in output px.
    Full height ~1050*scale px (ground to coffin top)."""
    S = 2 * scale
    cw, ch = int(900 * S), int(1180 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 400 * S
    feet_y = 1150 * S
    sh_y = 330 * S                      # shoulders (very high: she is too tall)
    sk = BONE + (255,)
    skd = BONE_D + (255,)
    yl = YELLOW + (255,)
    yld = YELLOW_D + (255,)
    sw = math.sin(step)
    # feet: bare, pale, dragging (barely lifting)
    for s_, ph in ((1, 0), (-1, math.pi)):
        fx = cx + 34 * S * math.sin(step + ph)
        lift = max(0, math.sin(step + ph)) * 8 * S
        d.polygon([(fx - 20 * S, feet_y - lift), (fx + 46 * S, feet_y - lift), (fx + 40 * S, feet_y - 18 * S - lift),
                   (fx - 14 * S, feet_y - 26 * S - lift)], fill=skd if s_ < 0 else sk)
    # longyi: tied at the chest, straight to the ankles, a little flare, a fold line
    d.polygon([(cx - 70 * S, sh_y + 70 * S), (cx + 62 * S, sh_y + 70 * S), (cx + 92 * S + 10 * S * sw, feet_y - 30 * S),
               (cx - 96 * S + 10 * S * sw, feet_y - 30 * S)], fill=yl)
    d.polygon([(cx - 70 * S, sh_y + 70 * S), (cx - 20 * S, sh_y + 70 * S), (cx - 46 * S + 10 * S * sw, feet_y - 30 * S),
               (cx - 96 * S + 10 * S * sw, feet_y - 30 * S)], fill=yld)
    d.line([(cx + 20 * S, sh_y + 90 * S), (cx + 40 * S + 10 * S * sw, feet_y - 34 * S)], fill=yld, width=int(5 * S))
    d.rectangle([cx - 74 * S, sh_y + 62 * S, cx + 66 * S, sh_y + 84 * S], fill=yld)                    # chest knot band
    # bare shoulders + thin neck
    d.rounded_rectangle([cx - 66 * S, sh_y - 10 * S, cx + 56 * S, sh_y + 76 * S], 30 * S, fill=sk)
    d.rectangle([cx - 14 * S, sh_y - 90 * S, cx + 16 * S, sh_y + 10 * S], fill=sk)
    # coffin on the far shoulder (drawn first so the head and hair sit in front of it)
    head = (cx + 6 * S + 40 * S * turn, sh_y - 140 * S + 20 * S * turn)
    if coffin:
        cf = coffin_side(S)
        ang = -7 * (1 - lower) - 10 * math.sin(math.pi * lower)
        cf = cf.rotate(ang, Image.BICUBIC, expand=True)
        ox = cx - cf.width * 0.42 + 120 * S * lower
        oy = sh_y - cf.height + 30 * S + (feet_y - sh_y - 40 * S) * lower ** 1.3
        img.alpha_composite(cf, (int(ox), int(oy)))
        d = ImageDraw.Draw(img)
    # near arm: long, pale, hanging (or reaching down with the coffin)
    ax, ay = cx + 34 * S, sh_y + 20 * S
    if lower > 0.02:
        ex = (ax + 140 * S * lower, ay + 300 * S + 380 * S * lower)
    else:
        ex = (ax + 10 * S + 14 * S * sw, ay + 520 * S)
    mid = ((ax + ex[0]) / 2 + 20 * S, (ay + ex[1]) / 2)
    d.line([(ax, ay), mid, ex], fill=sk, width=int(24 * S), joint="curve")
    for k in range(4):                                                                                    # long fingers
        d.line([ex, (ex[0] + (k - 1.5) * 9 * S, ex[1] + 70 * S)], fill=sk, width=int(7 * S))
    # head: seen from behind/side mostly hair; hair falls down her back to the hips, floating backwards
    hx, hy = head
    _hair_strands(d, (hx - 26 * S, hy - 50 * S), 560 * S, 90 * S, wind * 0.45, t, S, n=18)
    d.ellipse([hx - 62 * S, hy - 80 * S, hx + 62 * S, hy + 80 * S], fill=HAIR)
    d.polygon([(hx - 62 * S, hy), (hx + 40 * S, hy + 40 * S), (hx + 30 * S, hy + 200 * S), (hx - 70 * S, hy + 220 * S)], fill=HAIR)
    if turn > 0.25:
        k = min(1, (turn - 0.25) / 0.6)
        d.ellipse([hx - 14 * S - 30 * S * k, hy - 54 * S, hx + 14 * S + 30 * S * k, hy + 70 * S], fill=sk)
        d.polygon([(hx - 70 * S, hy - 80 * S), (hx - 10 * S * k, hy - 66 * S), (hx - 46 * S, hy + 160 * S)], fill=HAIR)
        d.polygon([(hx + 70 * S, hy - 80 * S), (hx + 12 * S * k, hy - 66 * S), (hx + 48 * S, hy + 160 * S)], fill=HAIR)
    else:
        d.polygon([(hx + 30 * S, hy - 20 * S), (hx + 70 * S, hy + 6 * S), (hx + 36 * S, hy + 40 * S)], fill=HAIR)   # profile nose in hair
    # the yellow ribbon tied in her hair, two tails fluttering
    rb = (hx - 30 * S, hy - 30 * S)
    d.polygon([(rb[0] - 30 * S, rb[1] - 18 * S), (rb[0], rb[1]), (rb[0] - 30 * S, rb[1] + 18 * S)], fill=RIBBON + (255,))
    d.polygon([(rb[0] + 30 * S, rb[1] - 18 * S), (rb[0], rb[1]), (rb[0] + 30 * S, rb[1] + 18 * S)], fill=RIBBON + (255,))
    for j in (0, 1):
        pts = [(rb[0] + (k * 22 * wind * facing) * S, rb[1] + (k * 26 + j * 10) * S + 10 * S * math.sin(t * 6 + k + j * 2)) for k in range(7)]
        d.line(pts, fill=RIBBON + (255,), width=int(9 * S), joint="curve")
    im = down(img)
    if rim:
        im = _rim(im, rim, 5, 3)
    face = (hx / 2, (hy + 6 * S) / 2)
    if turn > 0.25 and eyes > 0.02:
        a = np.asarray(im).astype(np.float32)
        rgb = a[..., :3]
        g = glow_sprite(int(14 * scale) + 3, (255, 236, 220), 1.4)
        k = min(1, (turn - 0.25) / 0.6)
        for s_ in (-1, 1):
            add_glow(rgb, g, face[0] + s_ * 16 * scale * k, face[1] - 6 * scale, 1.6 * eyes)
        a[..., :3] = np.clip(rgb, 0, 255)
        im = Image.fromarray(a.astype(np.uint8))
    if turn > 0.05:
        # the head keeps twisting: tilt the whole top of the figure a little toward the wrong side
        pass
    if facing < 0:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
        face = (im.width - face[0], face[1])
        fxp = im.width - cx / 2
    else:
        fxp = cx / 2
    return im, {"feet": (fxp, feet_y / 2), "face": face}


def ghost_front(scale=1.0, t=0.0, eyes=1.0, tilt=0.0, part=0.5, coffin=True, wind=0.0):
    """Ma Phae Wah facing the camera, waist up: hair hangs over the face with a narrow parting (part 0..1 = how much
    face shows), two pale glowing eyes, the yellow longyi tied over the chest, bone-white shoulders, long arms.
    The coffin's end (a dark hexagon) rises beside her head. tilt in degrees (head at a wrong angle).
    RGBA, anchor bottom centre; .info['face'] = face centre."""
    S = 2 * scale
    cw, ch = int(820 * S), int(1200 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    sk = BONE + (255,)
    sh_y = 560 * S
    if coffin:                                                                                             # coffin end, on her left shoulder
        ccx, ccy = cx + 210 * S, sh_y - 150 * S
        hexa = [(ccx - 90 * S, ccy - 150 * S), (ccx + 90 * S, ccy - 150 * S), (ccx + 120 * S, ccy - 40 * S),
                (ccx + 80 * S, ccy + 150 * S), (ccx - 80 * S, ccy + 150 * S), (ccx - 120 * S, ccy - 40 * S)]
        d.polygon(hexa, fill=COFFIN + (255,))
        inner = [(ccx + (x - ccx) * 0.8, ccy + (y - ccy) * 0.8) for x, y in hexa]
        d.polygon(inner, outline=COFFIN_D + (255,), width=int(8 * S))
    d.rounded_rectangle([cx - 230 * S, sh_y, cx + 230 * S, ch + 80 * S], 110 * S, fill=sk)              # shoulders/torso
    d.rectangle([cx - 40 * S, sh_y - 120 * S, cx + 40 * S, sh_y + 30 * S], fill=sk)                     # neck
    d.polygon([(cx - 214 * S, sh_y + 230 * S), (cx + 214 * S, sh_y + 230 * S), (cx + 260 * S, ch), (cx - 260 * S, ch)], fill=YELLOW + (255,))
    d.rectangle([cx - 216 * S, sh_y + 220 * S, cx + 216 * S, sh_y + 262 * S], fill=YELLOW_D + (255,))
    d.polygon([(cx + 40 * S, sh_y + 240 * S), (cx + 110 * S, sh_y + 300 * S), (cx + 70 * S, sh_y + 330 * S)], fill=YELLOW_D + (255,))
    for s_ in (-1, 1):                                                                                     # arms hanging
        d.line([(cx + s_ * 200 * S, sh_y + 60 * S), (cx + s_ * 250 * S, ch)], fill=(196, 188, 174, 255), width=int(60 * S))
    # head (separate so it can tilt)
    hd = Image.new("RGBA", (int(520 * S), int(760 * S)), (0, 0, 0, 0))
    dh = ImageDraw.Draw(hd)
    hx, hy = 260 * S, 250 * S
    dh.ellipse([hx - 130 * S, hy - 170 * S, hx + 130 * S, hy + 170 * S], fill=HAIR)
    pw = 30 * S + 80 * S * part
    dh.ellipse([hx - pw, hy - 120 * S, hx + pw, hy + 160 * S], fill=sk)
    for s_ in (-1, 1):
        ex = hx + s_ * 46 * S
        dh.ellipse([ex - 30 * S, hy - 20 * S, ex + 30 * S, hy + 22 * S], fill=(40, 30, 30, 255))
        if eyes > 0.05:
            dh.ellipse([ex - 18 * S, hy - 10 * S * eyes, ex + 18 * S, hy + 10 * S * eyes], fill=(255, 246, 236, 255))
            dh.ellipse([ex - 5 * S, hy - 5 * S, ex + 5 * S, hy + 5 * S], fill=(120, 10, 10, 255))
    dh.line([(hx - 18 * S, hy + 100 * S), (hx + 18 * S, hy + 100 * S)], fill=(120, 100, 96, 255), width=int(5 * S))
    # hair curtain over the face, parted in the middle
    for s_ in (-1, 1):
        dh.polygon([(hx + s_ * 140 * S, hy - 160 * S), (hx + s_ * (pw * 0.55), hy - 150 * S), (hx + s_ * (pw * 0.9), hy + 40 * S),
                    (hx + s_ * pw * 0.7, hy + 500 * S), (hx + s_ * 180 * S, hy + 500 * S)], fill=HAIR)
    rnd = random.Random(5)
    for i in range(26):
        x0 = hx + rnd.choice((-1, 1)) * rnd.uniform(0.75 * pw / S, 150) * S
        pts = [(x0 + 16 * S * math.sin(t * 2 + k * 0.6 + i) * k / 8 + wind * k * 14 * S, hy - 80 * S + k * 64 * S) for k in range(9)]
        dh.line(pts, fill=HAIR, width=int(rnd.uniform(8, 14) * S), joint="curve")
    rb = (hx - 110 * S, hy - 120 * S)
    dh.polygon([(rb[0] - 36 * S, rb[1] - 24 * S), rb, (rb[0] - 36 * S, rb[1] + 24 * S)], fill=RIBBON + (255,))
    dh.polygon([(rb[0] + 36 * S, rb[1] - 24 * S), rb, (rb[0] + 36 * S, rb[1] + 24 * S)], fill=RIBBON + (255,))
    for j in (0, 1):
        pts = [(rb[0] - k * 10 * S + j * 14 * S, rb[1] + k * 30 * S + 8 * S * math.sin(t * 5 + k + j)) for k in range(7)]
        dh.line(pts, fill=RIBBON + (255,), width=int(10 * S), joint="curve")
    if tilt:
        hd = hd.rotate(tilt, Image.BICUBIC, center=(hx, hy + 240 * S))
    ox, oy = int(cx - hx), int(sh_y - 120 * S - hy - 80 * S)
    img.alpha_composite(hd, (ox, oy))
    im = down(img)
    im = _rim(im, RIM_RED, 6, 4)
    th = math.radians(tilt)
    pcx, pcy = hx, hy + 240 * S

    def rot(x, y):
        return (ox + pcx + (x - pcx) * math.cos(th) + (y - pcy) * math.sin(th)) / 2, (oy + pcy - (x - pcx) * math.sin(th) + (y - pcy) * math.cos(th)) / 2
    fcx, fcy = rot(hx, hy)
    if eyes > 0.05:
        a = np.asarray(im).astype(np.float32)
        rgb = a[..., :3]
        g = glow_sprite(int(30 * scale) + 3, (255, 220, 200), 1.5)
        for s_ in (-1, 1):
            add_glow(rgb, g, *rot(hx + s_ * 46 * S, hy), 1.0 * eyes)
        a[..., :3] = np.clip(rgb, 0, 255)
        im = Image.fromarray(a.astype(np.uint8))
    im.info["face"] = (fcx, fcy)
    return im


# ---------------------------------------------------------------- people
def thiri_side(phase=0.0, walking=False, facing=1, color=(8, 4, 4, 255), rim=(255, 140, 80), scale=1.0, reach=0.0,
               kneel=0.0, hands=0.0, tremble=0.0):
    """Thiri (side view, faces right): a slim girl in a longyi with a loose blouse, hair tied in a low ponytail.
    reach 0..1 pushes a hand forward and up (opening a shutter). kneel 0..1 kneels; hands 0..1 presses the palms
    together in prayer. Returns (img, feet anchor, hand point)."""
    cw, ch = 340, 480
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 150
    amp = float(walking)
    bob = -5 * abs(math.cos(phase)) * amp + 110 * kneel
    sw = math.sin(phase) * amp
    hip = (cx - 30 * kneel, 290 + bob)
    if kneel > 0.5:
        d.polygon([(hip[0] - 40, hip[1] - 6), (hip[0] + 90, hip[1] + 60), (hip[0] + 96, 440), (hip[0] - 60, 440), (hip[0] - 50, hip[1] + 40)], fill=color)
    else:
        d.polygon([(hip[0] - 34, hip[1] - 10), (hip[0] + 34, hip[1] - 10), (hip[0] + 30 + 10 * sw, 430), (hip[0] - 30 + 10 * sw, 430)], fill=color)
        for s in (1, -1):
            fx = hip[0] + 16 * sw * s
            d.polygon([(fx - 10, 426), (fx + 26, 426), (fx + 22, 440), (fx - 10, 440)], fill=color)
    sh = (cx + 4 + 6 * kneel, 176 + bob)
    d.polygon([(hip[0] - 34, hip[1]), (hip[0] + 34, hip[1]), (sh[0] + 28, sh[1]), (sh[0] - 28, sh[1])], fill=color)
    d.rounded_rectangle([sh[0] - 30, sh[1] - 8, sh[0] + 30, sh[1] + 40], 14, fill=color)
    hd = (sh[0] + 8, sh[1] - 44)
    d.ellipse([hd[0] - 22, hd[1] - 25, hd[0] + 22, hd[1] + 25], fill=color)
    d.ellipse([hd[0] + 18, hd[1] - 2, hd[0] + 28, hd[1] + 8], fill=color)
    d.line([(hd[0] - 18, hd[1] - 8), (hd[0] - 40, hd[1] + 30), (hd[0] - 44, hd[1] + 70)], fill=color, width=12)  # ponytail
    d.rectangle([hd[0] - 8, hd[1] + 18, hd[0] + 10, sh[1]], fill=color)
    if hands > 0.05:
        hp = (sh[0] + 46, sh[1] + 10)
        d.line([(sh[0], sh[1] + 10), (sh[0] + 30, sh[1] + 50), hp], fill=color, width=14)
        d.polygon([(hp[0] - 6, hp[1] + 6), (hp[0] + 10, hp[1] - 40), (hp[0] + 14, hp[1] + 4)], fill=color)
        tip = hp
    else:
        a1 = 0.35 * sw + 0.15 + reach * 2.0
        k = (sh[0] + 4 + math.sin(a1) * 62, sh[1] + 8 + math.cos(a1) * 62)
        a2 = a1 - 0.3 + reach * 0.3
        e = (k[0] + math.sin(a2) * 56, k[1] + math.cos(a2) * 56)
        d.line([(sh[0] + 4, sh[1] + 8), k, e], fill=color, width=16, joint="curve")
        tip = e
    if rim:
        img = _rim(img, rim)
    if facing < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        tip = (cw - tip[0], tip[1])
    if tremble:
        img = img.rotate(tremble, Image.BICUBIC, center=(cw / 2, ch - 40))
    k = scale / 2
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cw * k / 2, 440 * k), (tip[0] * k, tip[1] * k)


def grandma_side(facing=1, color=(8, 4, 4, 255), rim=(255, 140, 80), scale=1.0, kneel=0.0, hands=0.0, pull=0.0):
    """Grandma (side view): a little stooped, hair in a high bun, shawl over the shoulders, longyi.
    pull 0..1 reaches an arm out and back (pulling someone). Returns (img, feet anchor)."""
    cw, ch = 360, 480
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 170
    bob = 110 * kneel
    hip = (cx - 30 * kneel, 290 + bob)
    if kneel > 0.5:
        d.polygon([(hip[0] - 46, hip[1] - 6), (hip[0] + 90, hip[1] + 60), (hip[0] + 96, 440), (hip[0] - 64, 440), (hip[0] - 54, hip[1] + 40)], fill=color)
    else:
        d.polygon([(hip[0] - 38, hip[1] - 10), (hip[0] + 38, hip[1] - 10), (hip[0] + 34, 430), (hip[0] - 34, 430)], fill=color)
        d.polygon([(hip[0] - 12, 426), (hip[0] + 30, 426), (hip[0] + 26, 440), (hip[0] - 12, 440)], fill=color)
    sh = (cx + 18, 186 + bob)
    d.polygon([(hip[0] - 40, hip[1]), (hip[0] + 36, hip[1]), (sh[0] + 34, sh[1] + 10), (sh[0] - 40, sh[1] - 4)], fill=color)
    d.polygon([(sh[0] - 50, sh[1] - 6), (sh[0] + 40, sh[1] + 6), (sh[0] + 30, sh[1] + 70), (sh[0] - 56, sh[1] + 80)], fill=color)  # shawl
    hd = (sh[0] + 22, sh[1] - 40)
    d.ellipse([hd[0] - 22, hd[1] - 24, hd[0] + 22, hd[1] + 24], fill=color)
    d.ellipse([hd[0] + 16, hd[1] - 2, hd[0] + 26, hd[1] + 8], fill=color)
    d.ellipse([hd[0] - 18, hd[1] - 46, hd[0] + 10, hd[1] - 18], fill=color)                                   # high bun
    if hands > 0.05:
        hp = (sh[0] + 54, sh[1] + 16)
        d.line([(sh[0] + 6, sh[1] + 14), (sh[0] + 36, sh[1] + 56), hp], fill=color, width=14)
        d.polygon([(hp[0] - 6, hp[1] + 6), (hp[0] + 10, hp[1] - 40), (hp[0] + 14, hp[1] + 4)], fill=color)
    else:
        a1 = 0.2 + pull * 1.4
        k = (sh[0] + math.sin(a1) * 66, sh[1] + 10 + math.cos(a1) * 66)
        e = (k[0] + math.sin(a1 - 0.6 * pull) * 60, k[1] + math.cos(a1 - 0.6 * pull) * 60)
        d.line([(sh[0], sh[1] + 10), k, e], fill=color, width=16, joint="curve")
    if rim:
        img = _rim(img, rim)
    if facing < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    k = scale / 2
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cw * k / 2, 440 * k)


def thiri_front(scale=1.0, look=0.0, eyes=1.0, mouth=0.0, fear=0.0, warm=(1.12, 0.86, 0.72), light=1.0):
    """Thiri chest-up facing the camera: black hair pulled back, round thanaka patches on her cheeks, a jasmine
    flower behind one ear, a pale blouse. mouth 0..1 opens the lips (whisper); fear lifts the brows."""
    S = 2 * scale
    cw, ch = int(600 * S), int(720 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    d.rounded_rectangle([cx - 220 * S, 490 * S, cx + 220 * S, ch + 60 * S], 120 * S, fill=(200, 186, 170, 255))    # blouse
    d.polygon([(cx - 60 * S, 486 * S), (cx, 560 * S), (cx + 60 * S, 486 * S)], fill=(150, 112, 90, 255))
    skin = (176, 124, 92, 255)
    d.rectangle([cx - 40 * S, 380 * S, cx + 40 * S, 480 * S], fill=(150, 104, 76, 255))
    d.ellipse([cx - 118 * S, 150 * S, cx + 118 * S, 440 * S], fill=skin)
    for s_ in (-1, 1):                                                                                     # thanaka
        d.ellipse([cx + s_ * 72 * S - 40 * S, 300 * S, cx + s_ * 72 * S + 40 * S, 370 * S], fill=(214, 190, 140, 230))
    hair = (12, 8, 8, 255)
    d.chord([cx - 124 * S, 118 * S, cx + 124 * S, 330 * S], 180, 360, fill=hair)
    d.polygon([(cx - 124 * S, 226 * S), (cx - 30 * S, 140 * S), (cx - 110 * S, 290 * S)], fill=hair)
    d.polygon([(cx + 124 * S, 226 * S), (cx + 30 * S, 140 * S), (cx + 110 * S, 290 * S)], fill=hair)
    for k in range(5):                                                                                     # jasmine
        a = k * 1.256
        d.ellipse([cx + 120 * S + math.cos(a) * 14 * S - 10 * S, 200 * S + math.sin(a) * 14 * S - 10 * S,
                   cx + 120 * S + math.cos(a) * 14 * S + 10 * S, 200 * S + math.sin(a) * 14 * S + 10 * S], fill=(240, 236, 220, 255))
    if eyes > 0:
        for s_ in (-1, 1):
            ex = cx + s_ * 50 * S
            op = 20 * S * eyes * (1 + 0.3 * fear)
            d.ellipse([ex - 30 * S, 270 * S - op, ex + 30 * S, 270 * S + op], fill=(246, 242, 236, 255))
            r = 11 * S * (1 - 0.3 * fear)
            d.ellipse([ex + look * 14 * S - r, 270 * S - r, ex + look * 14 * S + r, 270 * S + r], fill=(24, 14, 10, 255))
            d.line([(ex - 30 * S, 228 * S - 14 * S * fear), (ex + 28 * S, 226 * S - 16 * S * fear + s_ * 6 * S * fear)], fill=(30, 18, 14, 255), width=int(6 * S))
    mo = 6 * S + 24 * S * mouth
    d.ellipse([cx - 18 * S, 386 * S - mo / 2, cx + 18 * S, 386 * S + mo / 2], fill=(90, 34, 30, 255))
    im = down(img)
    a = np.array(im).astype(np.float32)
    yy = np.linspace(0, 1, im.height)[:, None]
    g = 0.45 + 0.6 * np.clip((yy - 0.1) / 0.5, 0, 1) * light
    a[..., :3] *= g[..., None] * np.array(warm)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def grandma_front(scale=1.0, mouth=0.0, look=0.0, warm=(1.12, 0.86, 0.72), light=1.0):
    """Grandma chest-up: grey hair in a high bun, deep lines on the face, a maroon shawl, thanaka on her cheeks."""
    S = 2 * scale
    cw, ch = int(640 * S), int(760 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    d.rounded_rectangle([cx - 250 * S, 500 * S, cx + 250 * S, ch + 60 * S], 130 * S, fill=(96, 20, 24, 255))     # shawl
    d.polygon([(cx - 70 * S, 500 * S), (cx, 600 * S), (cx + 70 * S, 500 * S)], fill=(170, 150, 130, 255))
    for k in range(8):
        d.line([(cx - 240 * S + k * 60 * S, 540 * S), (cx - 220 * S + k * 60 * S, ch)], fill=(74, 14, 18, 255), width=int(5 * S))
    skin = (160, 110, 82, 255)
    d.rectangle([cx - 40 * S, 400 * S, cx + 40 * S, 500 * S], fill=(140, 96, 70, 255))
    d.ellipse([cx - 120 * S, 170 * S, cx + 120 * S, 470 * S], fill=skin)
    for s_ in (-1, 1):
        d.ellipse([cx + s_ * 72 * S - 36 * S, 330 * S, cx + s_ * 72 * S + 36 * S, 392 * S], fill=(196, 170, 124, 210))
    grey = (150, 146, 140, 255)
    d.chord([cx - 126 * S, 140 * S, cx + 126 * S, 340 * S], 180, 360, fill=grey)
    d.ellipse([cx - 64 * S, 50 * S, cx + 64 * S, 160 * S], fill=grey)
    for k in range(5):
        d.arc([cx - 100 * S + k * 10 * S, 150 * S + k * 6 * S, cx + 100 * S - k * 10 * S, 300 * S], 200, 340, fill=(110, 108, 104, 255), width=int(3 * S))
    for s_ in (-1, 1):
        ex = cx + s_ * 50 * S
        d.ellipse([ex - 26 * S, 290 * S - 14 * S, ex + 26 * S, 290 * S + 14 * S], fill=(236, 226, 214, 255))
        d.ellipse([ex + look * 12 * S - 10 * S, 280 * S, ex + look * 12 * S + 10 * S, 300 * S], fill=(24, 14, 10, 255))
        d.line([(ex - 28 * S, 270 * S), (ex + 26 * S, 266 * S + s_ * 6 * S)], fill=(120, 116, 110, 255), width=int(7 * S))
        d.arc([ex - 30 * S, 296 * S, ex + 30 * S, 330 * S], 20, 160, fill=(110, 72, 54, 255), width=int(3 * S))   # eye bags
        d.arc([cx + s_ * 60 * S - 40 * S, 360 * S, cx + s_ * 60 * S + 40 * S, 440 * S], 90 + 60 * s_, 180 + 60 * s_ if s_ < 0 else 150, fill=(120, 80, 60, 255), width=int(3 * S))
    mo = 6 * S + 20 * S * mouth
    d.ellipse([cx - 24 * S, 414 * S - mo / 2, cx + 24 * S, 414 * S + mo / 2], fill=(80, 30, 28, 255))
    im = down(img)
    a = np.array(im).astype(np.float32)
    yy = np.linspace(0, 1, im.height)[:, None]
    g = 0.45 + 0.6 * np.clip((yy - 0.1) / 0.5, 0, 1) * light
    a[..., :3] *= g[..., None] * np.array(warm)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def monk(scale=1.0, phase=0.0, color=(70, 22, 12, 255), rim=(255, 150, 80)):
    """A monk walking the morning alms round (side view): shaved head, robe over one shoulder, alms bowl held in
    front. Anchor (img, feet)."""
    cw, ch = 300, 480
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 140
    bob = -4 * abs(math.cos(phase))
    sw = math.sin(phase)
    for s in (1, -1):
        d.line([(cx, 360 + bob), (cx + 18 * sw * s, 440)], fill=(30, 14, 8, 255), width=18)
    d.polygon([(cx - 40, 170 + bob), (cx + 38, 170 + bob), (cx + 52, 420 + bob), (cx - 54, 420 + bob)], fill=color)
    d.ellipse([cx - 24, 104 + bob, cx + 28, 162 + bob], fill=(60, 34, 24, 255))
    d.chord([cx + 10, 200 + bob, cx + 80, 260 + bob], 0, 180, fill=(20, 10, 8, 255))
    d.line([(cx + 10, 190 + bob), (cx + 40, 232 + bob)], fill=color, width=16)
    img = _rim(img, rim)
    k = scale / 2
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cx * k, 440 * k)


# ---------------------------------------------------------------- particles + backgrounds
class Embers:
    """Tiny red sparks / dust motes drifting upward in a lamp or moonlight."""
    def __init__(self, n=40, seed=1, area=(0, W, 200, 1700), color=(255, 110, 70)):
        rnd = random.Random(seed)
        self.q = [(rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3]), rnd.uniform(4, 22), rnd.uniform(0, 6), rnd.uniform(0.4, 1))
                  for _ in range(n)]
        self.area, self.spr = area, glow_sprite(6, color, 1.5)

    def draw(self, arr, t, k=1.0):
        a0, a1, b0, b1 = self.area
        for x, y, v, ph, b in self.q:
            yy = b0 + (y - b0 - v * t) % (b1 - b0)
            xx = x + 14 * math.sin(t * 0.8 + ph)
            add_glow(arr, self.spr, xx, yy, k * b * (0.6 + 0.4 * math.sin(t * 3 + ph)))


def acheik_bg(top=(14, 3, 5), bot=(54, 10, 12), line=(96, 22, 20)):
    """Explain/outro background: maroon gradient with a faint acheik (Burmese wave-weave) pattern."""
    y = np.linspace(0, 1, H)[:, None, None]
    base = np.repeat(np.array(top) * (1 - y) + np.array(bot) * y, W, axis=1).astype(np.float32)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for row in range(0, H + 120, 120):
        for k in range(3):
            pts = [(x, row + k * 16 + 34 * math.sin(x / 70.0 + row * 0.03)) for x in range(-20, W + 21, 10)]
            d.line(pts, fill=255, width=5)
    a = np.asarray(m.filter(ImageFilter.GaussianBlur(1))).astype(np.float32)[..., None] / 255 * 0.22
    base = base * (1 - a) + np.array(line, np.float32) * a
    return base


def shade21(img, radius=40, rim=(255, 55, 40), light=(-0.55, -0.7, 0.5), rim_k=1.0):
    """2.1D pass (PLAYBOOK 2d) on a finished flat sprite: keeps its colours, adds ONE soft shadow side and a thin
    red edge light, using toolkit/depth.py inflate_shade on the sprite's alpha."""
    a = img.split()[3]
    mult = np.asarray(inflate_shade(a, (255, 255, 255), light=light, rim=(0, 0, 0), radius=radius)).astype(np.float32)[..., :3] / 255
    rl = np.asarray(inflate_shade(a, (0, 0, 0), light=light, rim=rim, radius=radius)).astype(np.float32)[..., :3]
    rgb = np.asarray(img).astype(np.float32)
    rgb[..., :3] = rgb[..., :3] * mult + rl * rim_k
    return Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
