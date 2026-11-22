"""Episode 4 (Philippines, Manananggal) drawing helpers: a barrio at night in the tropics.
Bahay kubo on bamboo stilts with nipa-thatch roofs and glowing capiz-shell windows, coconut palms,
a big mango tree, a bamboo fence, a kerosene gasera lamp, a jar of salt and garlic, Lito (a boy in
shorts and a t-shirt), Lola holding a lamp, the standing lower half (a checked patadyong skirt wrapped
in mist, never anything gory) and the flying upper half with huge bat wings.
Palette: deep teal-green jungle night, silver-green moon, warm amber lamplight, pearly capiz."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *

# ---------------------------------------------------------------- palette
SKY_TOP = (3, 12, 16)
SKY_BOT = (20, 56, 58)
JUNGLE_FAR = (12, 36, 38, 255)
JUNGLE_MID = (7, 22, 24, 255)
SILH = (3, 9, 10, 255)
EARTH = (14, 20, 16, 255)
LAMP = (255, 168, 64)
CAPIZ = (252, 232, 190)
NIPA = (22, 26, 18, 255)
BAMBOO = (18, 22, 16, 255)
SKIN_G = (176, 186, 168, 255)     # her skin: pale, grey-green in the moonlight
BLOUSE = (214, 218, 200, 255)
HAIR = (8, 8, 10, 255)
WING = (30, 20, 30, 240)
WING_B = (14, 8, 14, 255)
EYE = (255, 210, 60)


# ---------------------------------------------------------------- landscape
def jungle_line(w, base, amp, color, seed=1, r0=40, r1=110):
    """Bumpy treeline made of overlapping round canopies."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = -60
    while x < w + 60:
        r = rnd.uniform(r0, r1)
        y = base - rnd.uniform(0, amp)
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)
        d.rectangle([x - r, y, x + r, H], fill=color)
        x += r * rnd.uniform(0.7, 1.2)
    return img


def bahay_kubo(scale=1.0, seed=0, lit=True, color=NIPA, window_open=0.0, glow_col=CAPIZ):
    """Nipa hut on stilts: steep thatched roof, bamboo slat walls, a capiz-shell window grid that slides open,
    a bamboo ladder. Returns (img, info) with window rect and lamp glow points in img coords (1x)."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(520 * S), int(560 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    floor = ch - 150 * S          # floor level (stilts below)
    x0, x1 = 90 * S, cw - 90 * S
    # stilts
    for k in range(5):
        sx = x0 + 14 * S + k * (x1 - x0 - 28 * S) / 4
        d.rectangle([sx - 7 * S, floor, sx + 7 * S, ch], fill=color)
    d.line([(x0 + 14 * S, floor + 60 * S), (x1 - 14 * S, floor + 20 * S)], fill=color, width=int(5 * S))
    d.line([(x0 + 14 * S, floor + 20 * S), (x1 - 14 * S, floor + 60 * S)], fill=color, width=int(5 * S))
    # floor beam + walls
    d.rectangle([x0 - 10 * S, floor - 12 * S, x1 + 10 * S, floor + 6 * S], fill=color)
    wall_top = floor - 170 * S
    d.rectangle([x0, wall_top, x1, floor], fill=color)
    lt = tuple(min(255, v + 9) for v in color[:3]) + (255,)
    for k in range(int((x1 - x0) / (10 * S))):
        xx = x0 + k * 10 * S
        d.line([(xx, wall_top + 4 * S), (xx, floor - 4 * S)], fill=lt, width=max(1, int(1.2 * S)))
    d.line([(x0, wall_top + 60 * S), (x1, wall_top + 60 * S)], fill=color, width=int(5 * S))
    # window: capiz grid; window_open slides the panel left
    wx0, wy0, wx1, wy1 = x0 + 150 * S, wall_top + 40 * S, x0 + 290 * S, wall_top + 130 * S
    info = {"win": (wx0 / 2, wy0 / 2, wx1 / 2, wy1 / 2), "glows": []}
    if lit:
        d.rectangle([wx0, wy0, wx1, wy1], fill=glow_col + (255,))
        info["glows"].append(((wx0 + wx1) / 4, (wy0 + wy1) / 4))
        if window_open > 0:   # opening shows warm room light (lamp) instead of pearly shell
            ox = wx0 + (wx1 - wx0) * (1 - window_open)
            d.rectangle([ox, wy0, wx1, wy1], fill=(255, 190, 110, 255))
        pw = (wx1 - wx0) * (1 - window_open)
        px0 = wx0 - (wx1 - wx0) * window_open * 0.0
        gx0, gx1 = wx0, wx0 + pw
        for k in range(1, 6):
            xx = gx0 + (gx1 - gx0) * k / 6
            if pw > 4:
                d.line([(xx, wy0), (xx, wy1)], fill=color, width=max(1, int(2.2 * S)))
        if pw > 4:
            for k in range(1, 5):
                yy = wy0 + (wy1 - wy0) * k / 5
                d.line([(gx0, yy), (gx1, yy)], fill=color, width=max(1, int(2.2 * S)))
            d.rectangle([gx1 - 3 * S, wy0, gx1 + 3 * S, wy1], fill=color)
    else:
        d.rectangle([wx0, wy0, wx1, wy1], fill=lt)
    d.rectangle([wx0 - 6 * S, wy0 - 6 * S, wx1 + 6 * S, wy1 + 6 * S], outline=color, width=int(6 * S))
    # small second window
    sx0, sy0, sx1, sy1 = x1 - 110 * S, wall_top + 50 * S, x1 - 40 * S, wall_top + 120 * S
    if lit and rnd.random() < 0.6:
        d.rectangle([sx0, sy0, sx1, sy1], fill=(255, 196, 120, 255))
        d.line([((sx0 + sx1) / 2, sy0), ((sx0 + sx1) / 2, sy1)], fill=color, width=int(3 * S))
        info["glows"].append(((sx0 + sx1) / 4, (sy0 + sy1) / 4))
    # door + ladder
    dx0 = x0 + 30 * S
    d.rectangle([dx0, wall_top + 30 * S, dx0 + 70 * S, floor], fill=tuple(max(0, v - 6) for v in color[:3]) + (255,))
    for s_ in (0, 1):
        d.line([(dx0 + 10 * S + s_ * 50 * S, floor), (dx0 - 30 * S + s_ * 50 * S, ch)], fill=color, width=int(6 * S))
    for k in range(1, 5):
        u = k / 5
        yy = floor + (ch - floor) * u
        d.line([(dx0 + 10 * S - 40 * S * u, yy), (dx0 + 60 * S - 40 * S * u, yy)], fill=color, width=int(5 * S))
    # steep thatched roof (overhanging), ragged edge + thatch strands
    peak = wall_top - 230 * S
    rl, rr = x0 - 70 * S, x1 + 70 * S
    eave = wall_top + 26 * S
    pts = [((rl + rr) / 2 - 18 * S, peak), ((rl + rr) / 2 + 18 * S, peak), (rr, eave)]
    n = 26
    for k in range(n + 1):
        xx = rr - (rr - rl) * k / n
        pts.append((xx, eave + (6 if k % 2 else -2) * S + rnd.uniform(-3, 3) * S))
    pts.append((rl, eave))
    d.polygon(pts, fill=color)
    for k in range(40):
        u = rnd.random()
        xa = (rl + rr) / 2 + (rr - rl) / 2 * (2 * u - 1) * 0.12
        xb = rl + (rr - rl) * u
        d.line([(xa, peak + 20 * S), (xb, eave - 4 * S)], fill=lt, width=max(1, int(1.2 * S)))
    d.line([((rl + rr) / 2 - 30 * S, peak + 4 * S), ((rl + rr) / 2 + 30 * S, peak + 4 * S)], fill=color, width=int(8 * S))
    return down(img), info


def mango_tree(scale=1.0, seed=0, color=SILH, fruit=True):
    """Short thick trunk + wide, dense dome canopy, a few hanging mangoes. Anchor: bottom centre."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(760 * S), int(720 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    d.polygon([(cx - 40 * S, ch), (cx + 40 * S, ch), (cx + 24 * S, ch - 300 * S), (cx - 26 * S, ch - 300 * S)], fill=color)
    for s_ in (-1, 1):   # roots + branches
        d.polygon([(cx + s_ * 30 * S, ch), (cx + s_ * 90 * S, ch), (cx + s_ * 34 * S, ch - 40 * S)], fill=color)
        d.line([(cx, ch - 260 * S), (cx + s_ * 170 * S, ch - 420 * S)], fill=color, width=int(22 * S))
        d.line([(cx, ch - 280 * S), (cx + s_ * 60 * S, ch - 480 * S)], fill=color, width=int(18 * S))
    for _ in range(46):
        a = rnd.uniform(math.pi, 2 * math.pi)
        rr = rnd.uniform(0.2, 1.0)
        x = cx + math.cos(a) * 320 * S * rr
        y = ch - 430 * S + math.sin(a) * 210 * S * rr
        r = rnd.uniform(60, 110) * S
        d.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85], fill=color)
    d.ellipse([cx - 340 * S, ch - 470 * S, cx + 340 * S, ch - 300 * S], fill=color)
    if fruit:
        for _ in range(7):
            x = cx + rnd.uniform(-260, 260) * S
            y = ch - 300 * S + rnd.uniform(-10, 30) * S
            d.line([(x, y - 20 * S), (x, y)], fill=color, width=int(2 * S))
            d.ellipse([x - 9 * S, y - 2 * S, x + 9 * S, y + 22 * S], fill=color)
    return down(img)


def bamboo_fence(w, y, color=BAMBOO, h=90):
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(0, w, 34):
        hh = h + (x * 37 % 23)
        d.rectangle([x, y - hh, x + 14, y], fill=color)
        d.line([(x, y - hh + 30), (x + 14, y - hh + 30)], fill=tuple(min(255, v + 12) for v in color[:3]) + (255,), width=2)
    d.rectangle([0, y - h + 20, w, y - h + 30], fill=color)
    d.rectangle([0, y - 30, w, y - 22], fill=color)
    return img


def gasera(scale=1.0, flame=1.0, color=(20, 14, 10, 255)):
    """Small kerosene bottle lamp. Returns (img, flame point)."""
    S = 2 * scale
    cw, ch = int(80 * S), int(140 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([18 * S, 60 * S, 62 * S, 136 * S], 10 * S, fill=color)
    d.rectangle([34 * S, 44 * S, 46 * S, 62 * S], fill=color)
    d.ellipse([30 * S, (36 - 18 * flame) * S, 50 * S, 52 * S], fill=(255, 200, 90, 255))
    d.ellipse([36 * S, (40 - 8 * flame) * S, 44 * S, 50 * S], fill=(255, 250, 220, 255))
    return down(img), (40 * scale, 42 * scale)


def salt_jar(scale=1.0):
    S = 2 * scale
    img = Image.new("RGBA", (int(120 * S), int(150 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([10 * S, 30 * S, 110 * S, 146 * S], 22 * S, fill=(200, 220, 224, 200), outline=(240, 250, 250, 255), width=int(3 * S))
    d.rounded_rectangle([16 * S, 64 * S, 104 * S, 140 * S], 16 * S, fill=(250, 250, 246, 255))
    rnd = random.Random(2)
    for _ in range(40):
        x, y = rnd.uniform(22, 98) * S, rnd.uniform(68, 134) * S
        d.point((x, y), fill=(200, 210, 214, 255))
    d.rounded_rectangle([18 * S, 6 * S, 102 * S, 34 * S], 8 * S, fill=(150, 90, 50, 255))
    return down(img)


def garlic(scale=1.0):
    S = 2 * scale
    img = Image.new("RGBA", (int(110 * S), int(120 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for dx in (-24, 0, 24):
        d.ellipse([(55 + dx - 26) * S, 36 * S, (55 + dx + 26) * S, 112 * S], fill=(242, 234, 220, 255), outline=(200, 186, 170, 255), width=int(2 * S))
    d.polygon([(48 * S, 40 * S), (62 * S, 40 * S), (58 * S, 6 * S), (52 * S, 6 * S)], fill=(230, 220, 200, 255))
    return down(img)


# ---------------------------------------------------------------- characters
def boy(phase=0.0, walking=True, facing=1, color=(6, 10, 10, 255), rim=(120, 200, 180), scale=1.0, run=False,
        tremble=0.0, look_up=0.0, arm_out=0.0):
    """Lito: a boy in a t-shirt and shorts, messy short hair (side view). Returns (img, feet anchor).
    arm_out 0..1 stretches the front arm forward (pouring / pushing a window)."""
    cw, ch = 320, 460
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 150
    amp = float(walking) * (1.5 if run else 1.0)
    bob = -7 * abs(math.cos(phase)) * amp
    lean = 0.2 if run else 0.0
    hip = (cx, 270 + bob)
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
        e = limb((hip[0], hip[1] + 14), a, 86, a - bend, 86, 22)
        d.polygon([(e[0] - 10, e[1] + 4), (e[0] + 22, e[1] + 4), (e[0] + 18, e[1] - 6), (e[0] - 8, e[1] - 8)], fill=color)
    sh = (cx + 6 + 60 * lean, 150 + bob + 10 * lean)
    # shorts
    d.polygon([(hip[0] - 26, hip[1] - 12), (hip[0] + 26, hip[1] - 12), (hip[0] + 34 + 6 * sw, hip[1] + 40),
               (hip[0] - 32 + 6 * sw, hip[1] + 40)], fill=color)
    # t-shirt torso
    d.polygon([(hip[0] - 30, hip[1] - 6), (hip[0] + 30, hip[1] - 6), (sh[0] + 33, sh[1]), (sh[0] - 33, sh[1])], fill=color)
    d.rounded_rectangle([sh[0] - 38, sh[1] - 8, sh[0] + 38, sh[1] + 40], 16, fill=color)
    # head: round, messy spiky short hair
    hd = (sh[0] + 6, sh[1] - 44 - 4 * look_up)
    d.ellipse([hd[0] - 25, hd[1] - 28, hd[0] + 25, hd[1] + 27], fill=color)
    d.ellipse([hd[0] + 16, hd[1] - 2 - 6 * look_up, hd[0] + 29, hd[1] + 11 - 6 * look_up], fill=color)
    d.rectangle([hd[0] - 9, hd[1] + 18, hd[0] + 11, sh[1]], fill=color)
    d.ellipse([hd[0] - 30, hd[1] - 34, hd[0] + 24, hd[1] + 6], fill=color)      # hair volume
    for k in range(5):
        a = -2.7 + k * 0.45
        d.polygon([(hd[0] + math.cos(a) * 24, hd[1] + math.sin(a) * 24 - 8),
                   (hd[0] + math.cos(a + 0.22) * 36, hd[1] + math.sin(a + 0.22) * 36 - 8),
                   (hd[0] + math.cos(a + 0.4) * 24, hd[1] + math.sin(a + 0.4) * 24 - 8)], fill=color)
    # arms
    limb((sh[0] - 4, sh[1] + 8), -0.45 * sw - 0.1, 66, -0.45 * sw - 0.4, 60, 18)
    a1 = 0.4 * sw + 0.1 + arm_out * 1.3
    limb((sh[0] + 4, sh[1] + 8), a1, 66, a1 - 0.3 - 0.8 * run + arm_out * 0.4, 60, 18)
    if rim:
        A = np.array(img.split()[3]).astype(np.int16)
        sh_ = np.zeros_like(A); sh_[3:, :-5] = A[:-3, 5:]
        edge = np.clip(A - sh_, 0, 255).astype(np.uint8)
        arr = np.array(img)
        m = edge > 0
        arr[m, 0], arr[m, 1], arr[m, 2] = rim
        img = Image.fromarray(arr)
    if facing < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if tremble:
        img = img.rotate(tremble, Image.BICUBIC, center=(cw / 2, ch - 40))
    k = scale / 2
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cw * k / 2, (ch - 40) * k)


def lola(color=(26, 16, 10, 255), rim=(255, 190, 110), scale=1.0, lamp_up=0.0, holding="lamp"):
    """Lola standing, a little stooped, hair in a bun, loose duster dress; one hand holds a lamp (or the salt jar).
    Faces right. Returns (img, feet anchor, hand point) in output pixels."""
    cw, ch = 340, 520
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 150
    d.polygon([(cx - 60, 470), (cx + 64, 470), (cx + 40, 210), (cx + 6, 170), (cx - 40, 180), (cx - 58, 230)], fill=color)  # dress
    for s_ in (-1, 1):
        d.rectangle([cx + s_ * 20 - 8, 466, cx + s_ * 20 + 8, 494], fill=color)
        d.ellipse([cx + s_ * 20 - 10, 488, cx + s_ * 20 + 22, 502], fill=color)
    d.ellipse([cx - 52, 150, cx + 40, 250], fill=color)                     # rounded shoulders
    d.ellipse([cx + 0, 96, cx + 66, 164], fill=color)                       # head, forward
    d.ellipse([cx - 22, 84, cx + 16, 120], fill=color)                      # bun
    d.polygon([(cx + 62, 126), (cx + 76, 136), (cx + 62, 142)], fill=color)  # nose
    hy = 290 - 120 * lamp_up
    hand = (cx + 110, hy)
    d.line([(cx + 20, 190), (cx + 70, 250 - 40 * lamp_up), hand], fill=color, width=20, joint="curve")
    d.ellipse([hand[0] - 12, hand[1] - 12, hand[0] + 12, hand[1] + 12], fill=color)
    A = np.array(img.split()[3]).astype(np.int16)
    sh_ = np.zeros_like(A); sh_[3:, :-5] = A[:-3, 5:]
    arr = np.array(img); m = np.clip(A - sh_, 0, 255) > 0
    arr[m, 0], arr[m, 1], arr[m, 2] = rim
    img = Image.fromarray(arr)
    k = scale
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    return img, (cx * k, 500 * k), (hand[0] * k, hand[1] * k)


def mist_puff(w, h, seed=0, t=0.0, color=(190, 214, 206), alpha=200):
    """Soft rolling mist blob (used to hide the waist line of the standing legs and the trail under her torso)."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w // 2, h // 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for k in range(14):
        x = rnd.uniform(0.28, 0.72) * w / 2 + 6 * math.sin(t * 0.9 + k)
        y = rnd.uniform(0.38, 0.62) * h / 2 + 4 * math.cos(t * 0.7 + k * 1.3)
        r = rnd.uniform(0.11, 0.2) * w / 2
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=color + (int(alpha * rnd.uniform(0.4, 0.8)),))
    img = img.filter(ImageFilter.GaussianBlur(max(2, w // 28)))
    return img.resize((w, h), Image.BILINEAR)


def legs(scale=1.0, t=0.0, mist=True, color=(70, 30, 46, 255), check=(36, 14, 26, 255), rim=(150, 220, 200),
         skin=(150, 160, 146, 255)):
    """The standing lower half: a checked patadyong (tube skirt) to mid-calf, bare ankles, feet together.
    The top is always wrapped in mist. Anchor: feet at bottom centre."""
    S = 2 * scale
    cw, ch = int(260 * S), int(560 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    top = 120 * S
    d.polygon([(cx - 62 * S, top), (cx + 62 * S, top), (cx + 74 * S, top + 300 * S), (cx - 74 * S, top + 300 * S)], fill=color)
    for k in range(1, 6):     # checks (plaid stripes)
        y = top + k * 50 * S
        d.line([(cx - 70 * S, y), (cx + 70 * S, y)], fill=check, width=int(5 * S))
    for k in (-2, -1, 0, 1, 2):
        d.line([(cx + k * 26 * S, top), (cx + k * 30 * S, top + 300 * S)], fill=check, width=int(4 * S))
    d.line([(cx + 30 * S, top + 10 * S), (cx + 40 * S, top + 300 * S)], fill=(8, 8, 12, 255), width=int(3 * S))  # fold
    for s_ in (-1, 1):
        d.rectangle([cx + s_ * 22 * S - 9 * S, top + 296 * S, cx + s_ * 22 * S + 9 * S, top + 400 * S], fill=skin)
        d.ellipse([cx + s_ * 22 * S - 12 * S, top + 392 * S, cx + s_ * 22 * S + 26 * S, top + 412 * S], fill=skin)
    im = down(img)
    if rim:
        A = np.array(im.split()[3]).astype(np.int16)
        sh_ = np.zeros_like(A); sh_[:, 3:] = A[:, :-3]
        arr = np.array(im); m = np.clip(A - sh_, 0, 255) > 0
        arr[m, 0], arr[m, 1], arr[m, 2] = rim
        im = Image.fromarray(arr)
    a = np.array(im.split()[3]).astype(np.float32)
    y0 = top / 2
    a *= np.clip((np.arange(a.shape[0]) - y0) / (50 * scale), 0, 1)[:, None]     # soft top edge, hidden in mist
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    out = Image.new("RGBA", (im.width + int(200 * scale), im.height), (0, 0, 0, 0))
    out.alpha_composite(im, (int(100 * scale), 0))
    if mist:
        mp = mist_puff(int(out.width * 1.15), int(300 * scale), seed=4, t=t, alpha=230)
        out.alpha_composite(mp, (int(-0.075 * out.width), int(y0 - 140 * scale)))
    return out


def _wing(d, sx, sy, side, flap, S, span=1.0):
    """One bat wing from shoulder (sx,sy). side=+1 right, -1 left. flap -1 (down) .. 1 (up)."""
    L1, L2 = 170 * S * span, 230 * S * span
    a0 = math.radians(-28 - 38 * flap)          # arm angle above horizontal (negative = up)
    wx, wy = sx + side * math.cos(a0) * L1, sy + math.sin(a0) * L1
    tips = []
    for k, (da, ln) in enumerate(((-0.35, 1.0), (0.15, 1.05), (0.6, 0.95), (1.05, 0.8))):
        a = a0 + da + 0.25 * flap * (k / 3)
        tips.append((wx + side * math.cos(a) * L2 * ln, wy + math.sin(a) * L2 * ln))
    body = (sx - side * 6 * S, sy + 150 * S)
    poly = [(sx, sy), (wx, wy), tips[0]]
    for i in range(len(tips) - 1):
        a, b = tips[i], tips[i + 1]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        cx_, cy_ = wx, wy
        # scallop: pull the midpoint toward the wrist
        poly += [(mx * 0.78 + cx_ * 0.22, my * 0.78 + cy_ * 0.22), b]
    poly += [((tips[-1][0] + body[0]) / 2 * 0.85 + wx * 0.15, (tips[-1][1] + body[1]) / 2 * 0.85 + wy * 0.15), body]
    d.polygon(poly, fill=WING)
    d.line([(sx, sy), (wx, wy)], fill=WING_B, width=int(9 * S))
    for tp in tips:
        d.line([(wx, wy), tp], fill=WING_B, width=int(4 * S))
    d.polygon([(wx, wy), (wx + side * 4 * S, wy - 26 * S), (wx + side * 10 * S, wy - 2 * S)], fill=WING_B)   # thumb claw


def manananggal(t, scale=1.0, flap=None, eyes=1.0, glow=0.7, hair_up=0.6, arms=0.0, scream=0.0, span=1.0, mist=True):
    """Flying upper half: long wild hair, pale grey-green face, cream blouse, huge bat wings.
    Below the waist there is only a soft mist trail (never anything gory). flap None = automatic flapping.
    arms 0..1 raises the clawed hands. scream 0..1 opens a small dark mouth (no teeth, no blood).
    Returns RGBA; the face centre is at (img.width/2, 300*scale)."""
    if flap is None:
        flap = math.sin(t * 2 * math.pi * 0.7)
    S = 2 * scale
    cw, ch = int(1000 * S * max(1.0, span)), int(760 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    fy = 300 * S                     # face centre
    bob = 10 * S * flap
    fy += bob
    sy = fy + 78 * S                 # shoulder line
    for side in (-1, 1):
        _wing(d, cx + side * 40 * S, sy + 6 * S, side, flap, S, span)
    # hair streaming up and back
    hw = math.sin(t * 1.3)
    hp = [(cx - 52 * S, fy - 10 * S)]
    for k in range(9):
        u = k / 8
        x = cx + (-190 + 380 * u) * S + 18 * S * math.sin(t * 2 + k)
        y = fy - (40 + 190 * hair_up * math.sin(math.pi * u) ** 0.7 + 26 * math.sin(t * 1.7 + k * 0.9)) * S
        hp.append((x, y))
    hp += [(cx + 130 * S + 20 * S * hw, fy + 60 * S), (cx + 80 * S + 10 * S * hw, fy + 170 * S), (cx + 40 * S, fy + 110 * S),
           (cx - 40 * S, fy + 110 * S), (cx - 80 * S - 10 * S * hw, fy + 170 * S), (cx - 130 * S - 20 * S * hw, fy + 60 * S)]
    d.polygon(hp, fill=HAIR)
    for k in range(7):   # loose strands
        x0 = cx + (-90 + 30 * k) * S
        pts = [(x0 + (k - 3) * 40 * S * v + 30 * S * math.sin(t * 1.5 + k + v * 3) * v, fy - (40 + 260 * v * hair_up) * S) for v in np.linspace(0, 1, 10)]
        d.line(pts, fill=HAIR, width=int(5 * S))
    # torso: blouse (camisa) to the waist; the waist dissolves into mist
    d.polygon([(cx - 56 * S, sy), (cx + 56 * S, sy), (cx + 44 * S, sy + 190 * S), (cx - 44 * S, sy + 190 * S)], fill=BLOUSE)
    d.ellipse([cx - 64 * S, sy - 16 * S, cx + 64 * S, sy + 40 * S], fill=BLOUSE)
    d.line([(cx, sy + 20 * S), (cx, sy + 180 * S)], fill=(180, 186, 170, 255), width=int(3 * S))
    # arms with long pale hands
    for side in (-1, 1):
        a = side * (0.35 + 0.9 * arms)
        el = (cx + side * 70 * S + side * 20 * S * arms, sy + 100 * S - 120 * S * arms)
        hd = (el[0] + side * (30 + 40 * arms) * S, el[1] + (70 - 150 * arms) * S)
        d.line([(cx + side * 54 * S, sy + 12 * S), el], fill=BLOUSE, width=int(26 * S))
        d.line([el, hd], fill=SKIN_G, width=int(16 * S))
        for f in range(4):
            fa = -math.pi / 2 + side * (0.2 + f * 0.25) if arms > 0.5 else math.pi / 2 + side * (-0.4 + f * 0.25)
            d.line([hd, (hd[0] + math.cos(fa) * 26 * S, hd[1] + math.sin(fa) * 26 * S)], fill=SKIN_G, width=int(5 * S))
    # neck + face
    d.rectangle([cx - 15 * S, fy + 40 * S, cx + 15 * S, sy + 4 * S], fill=SKIN_G)
    d.ellipse([cx - 44 * S, fy - 56 * S, cx + 44 * S, fy + 62 * S], fill=SKIN_G)
    # hair framing the face (middle part)
    d.polygon([(cx - 4 * S, fy - 58 * S), (cx - 50 * S, fy - 40 * S), (cx - 54 * S, fy + 90 * S), (cx - 34 * S, fy + 20 * S),
               (cx - 22 * S, fy - 30 * S)], fill=HAIR)
    d.polygon([(cx + 4 * S, fy - 58 * S), (cx + 50 * S, fy - 40 * S), (cx + 54 * S, fy + 90 * S), (cx + 34 * S, fy + 20 * S),
               (cx + 22 * S, fy - 30 * S)], fill=HAIR)
    # hair on top of the head (middle part)
    d.chord([cx - 50 * S, fy - 64 * S, cx + 50 * S, fy + 14 * S], 180, 360, fill=HAIR)
    d.line([(cx, fy - 62 * S), (cx, fy - 34 * S)], fill=(40, 44, 40, 255), width=int(2 * S))
    # eyes: dark sockets + glowing pupils, angry brows
    for s_ in (-1, 1):
        ex = cx + s_ * 18 * S
        d.ellipse([ex - 12 * S, fy - 10 * S, ex + 12 * S, fy + 6 * S], fill=(20, 18, 16, 255))
        d.ellipse([ex - 4 * S, fy - 5 * S, ex + 4 * S, fy + 2 * S], fill=EYE + (255,))
        d.line([(ex - s_ * 14 * S, fy - 20 * S), (ex + s_ * 12 * S, fy - 12 * S)], fill=(40, 40, 36, 255), width=int(4 * S))
    d.line([(cx, fy + 4 * S), (cx - 4 * S, fy + 22 * S), (cx + 2 * S, fy + 24 * S)], fill=(140, 150, 134, 255), width=int(2 * S))
    if scream > 0.02:
        d.ellipse([cx - 9 * S, fy + 34 * S - 10 * S * scream, cx + 9 * S, fy + 38 * S + 12 * S * scream], fill=(24, 10, 16, 255))
    else:
        d.line([(cx - 12 * S, fy + 38 * S), (cx + 12 * S, fy + 38 * S)], fill=(60, 50, 50, 255), width=int(3 * S))
    im = down(img)
    # soft fade at the waist + mist trail
    a = np.array(im.split()[3]).astype(np.float32)
    hh = a.shape[0]
    ys = np.arange(hh)
    wy = (sy + 150 * S) / 2
    fade = np.clip(1 - (ys - wy) / (40 * scale), 0, 1)
    body_cols = np.zeros(a.shape[1], bool)
    body_cols[int(cx / 2 - 70 * scale):int(cx / 2 + 70 * scale)] = True
    a[:, body_cols] *= fade[:, None]
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    if glow > 0:
        al = im.split()[3].filter(ImageFilter.GaussianBlur(16 * scale))
        g = Image.new("RGBA", im.size, (120, 255, 190, 0)); g.putalpha(al.point(lambda v: int(v * 0.35 * glow)))
        out.alpha_composite(g)
    if mist:
        mp = mist_puff(int(220 * scale), int(260 * scale), seed=9, t=t, color=(170, 210, 196), alpha=170)
        out.alpha_composite(mp, (int(cx / 2 - 110 * scale), int(wy - 60 * scale)))
    out.alpha_composite(im)
    if eyes > 0.05:
        eg = glow_sprite(int(22 * scale) + 2, (255, 200, 60), 1.6)
        arr = np.asarray(out).astype(np.float32)
        rgb = arr[..., :3]
        for s_ in (-1, 1):
            add_glow(rgb, eg, out.width / 2 + s_ * 18 * scale, fy / 2 - 1.5 * scale, eyes)
        arr[..., :3] = np.clip(rgb, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
    return out


def wing_shadow(t, scale=1.0, flap=None, color=(2, 4, 6, 255)):
    """Flat dark silhouette of the flying creature (for the moon crossing / roof shadow)."""
    if flap is None:
        flap = math.sin(t * 2 * math.pi * 0.7)
    S = 2 * scale
    cw, ch = int(1000 * S), int(600 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, sy = cw / 2, 260 * S
    for side in (-1, 1):
        _wing(d, cx + side * 30 * S, sy, side, flap, S)
    d.ellipse([cx - 40 * S, sy - 130 * S, cx + 40 * S, sy - 40 * S], fill=WING_B)
    d.polygon([(cx - 50 * S, sy - 60 * S), (cx + 50 * S, sy - 60 * S), (cx + 30 * S, sy + 150 * S), (cx - 30 * S, sy + 150 * S)], fill=WING_B)
    for k in range(5):
        d.line([(cx - 30 * S + k * 15 * S, sy - 110 * S), (cx - 60 * S + k * 30 * S + 20 * S * math.sin(t * 2 + k), sy - 200 * S)],
               fill=WING_B, width=int(7 * S))
    im = down(img)
    if color != (2, 4, 6, 255):
        arr = np.array(im); m = arr[..., 3] > 0
        arr[m, 0], arr[m, 1], arr[m, 2] = color[:3]
        im = Image.fromarray(arr)
    return im


def banig_bg(top=(10, 28, 30), bot=(40, 18, 30), seed=0):
    """Explain/outro background: teal-to-plum gradient with a faint woven banig (sleeping mat) pattern."""
    y = np.linspace(0, 1, H)[:, None, None]
    base = np.repeat(np.array(top) * (1 - y) + np.array(bot) * y, W, axis=1).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    u, v = (xx + yy) // 36, (xx - yy) // 36
    weave = ((u + v) % 2).astype(np.float32)
    band = ((u // 4 + v // 4) % 3 == 0).astype(np.float32)
    base += (weave * 9 + band * 7)[..., None] * np.array([1.0, 0.9, 0.7])
    return base
