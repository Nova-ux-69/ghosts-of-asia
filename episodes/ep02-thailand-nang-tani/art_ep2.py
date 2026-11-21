"""Episode 2 (Thailand, Nang Tani) drawing helpers."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *

RIBBON_COLS = [(220, 50, 70), (240, 120, 170), (250, 200, 60), (60, 170, 110), (240, 240, 235), (230, 110, 40)]


def ribbons_layer(trunk_x, base_y, scale, height, n=5, seed=1, light=1.0, w=W, h=H):
    """Colored cloth bands wrapped around a straight banana trunk, plus a hanging bow tail."""
    S = 2
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    th = height * scale
    cols = RIBBON_COLS[:]
    rnd.shuffle(cols)
    y = base_y - 70
    tails = []
    for i in range(n):
        hgt = th - (base_y - y)
        u = (base_y - y) / th
        hw = (26 - 10 * u) * scale + 2
        bh = rnd.uniform(16, 24) * scale * 0.7
        slant = rnd.uniform(-6, 6) * scale
        c = tuple(int(v * light) for v in cols[i % len(cols)]) + (255,)
        x0, x1 = trunk_x - hw, trunk_x + hw
        d.polygon([(x0 * S, (y + slant) * S), (x1 * S, (y - slant) * S), (x1 * S, (y - slant - bh) * S),
                   (x0 * S, (y + slant - bh) * S)], fill=c)
        # thin darker edge
        d.line([(x0 * S, (y + slant) * S), (x1 * S, (y - slant) * S)], fill=tuple(int(v * 0.6) for v in c[:3]) + (255,), width=3)
        if i in (1, 3):
            tails.append((x1 - 2, y - bh / 2, c))
        y -= bh + rnd.uniform(6, 14) * scale
    return down(img), tails


def draw_tails(img, tails, t, scale=1.0):
    d = ImageDraw.Draw(img)
    for k, (x, y, c) in enumerate(tails):
        for side in (0, 1):
            pts = []
            for i in range(9):
                v = i / 8
                pts.append((x + (14 + 46 * v) * scale * (1 if side else 0.7) + 8 * scale * math.sin(t * 2.2 + v * 4 + k),
                            y + 70 * v * scale * (1.0 if side else 0.8)))
            d.line(pts, fill=c, width=int(7 * scale))


def offerings(scale=1.0, light=1.0):
    S = 2
    cw, ch = int(320 * scale * S), int(140 * scale * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    k = scale * S
    def L(c): return tuple(int(v * light) for v in c) + (255,)
    # plate with fruit
    d.ellipse([20 * k, 110 * k, 140 * k, 132 * k], fill=L((200, 190, 170)))
    for i, (fx, fy, r, c) in enumerate(((50, 100, 16, (240, 160, 40)), (80, 96, 18, (220, 60, 50)), (110, 102, 15, (250, 210, 70)),
                                        (66, 82, 14, (230, 120, 40)))):
        d.ellipse([(fx - r) * k, (fy - r) * k, (fx + r) * k, (fy + r) * k], fill=L(c))
    # garland
    for i in range(18):
        a = i / 18 * 2 * math.pi
        x, y = 220 + 34 * math.cos(a), 118 + 10 * math.sin(a)
        d.ellipse([(x - 6) * k, (y - 6) * k, (x + 6) * k, (y + 6) * k], fill=L((248, 246, 236) if i % 3 else (240, 190, 60)))
    # incense holder + sticks
    d.rectangle([270 * k, 110 * k, 300 * k, 132 * k], fill=L((150, 110, 60)))
    tips = []
    for j, ang in enumerate((-0.15, 0.0, 0.15)):
        x0, y0 = 285 * k, 112 * k
        x1, y1 = x0 + math.sin(ang) * 70 * k, y0 - math.cos(ang) * 70 * k
        d.line([(x0, y0), (x1, y1)], fill=L((120, 60, 40)), width=int(3 * k))
        tips.append((x1 / S, y1 / S))
    return down(img), tips


def smoke(img, tips, t, ox, oy, alpha=0.5):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for j, (tx, ty) in enumerate(tips):
        pts = []
        for i in range(30):
            v = i / 29
            pts.append((ox + tx + 18 * v * math.sin(t * 1.3 + v * 6 + j * 2) + 8 * v, oy + ty - 220 * v))
        d.line(pts, fill=(220, 220, 230, int(110 * alpha)), width=3)
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(2.2)))


def thai_house(scale=1.0, color=SIL, lit=True, seed=0):
    S = 2 * scale
    cw, ch = int(460 * S), int(460 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bw, bh = 280 * S, 120 * S
    x0 = (cw - bw) / 2
    floor = ch - 100 * S
    for sx in np.linspace(x0 + 12 * S, x0 + bw - 12 * S, 5):
        d.rectangle([sx - 6 * S, floor, sx + 6 * S, ch], fill=color)
    # walls lean slightly inward (Thai style)
    d.polygon([(x0, floor), (x0 + bw, floor), (x0 + bw - 10 * S, floor - bh), (x0 + 10 * S, floor - bh)], fill=color)
    d.rectangle([x0 - 16 * S, floor - 6 * S, x0 + bw + 16 * S, floor + 6 * S], fill=color)
    # tall steep roof with curved finials (kalae)
    top = floor - bh - 190 * S
    d.polygon([(x0 - 30 * S, floor - bh + 8 * S), (cw / 2, top), (x0 + bw + 30 * S, floor - bh + 8 * S)], fill=color)
    for sgn in (-1, 1):
        px = cw / 2
        d.line([(px, top + 6 * S), (px + sgn * 36 * S, top - 40 * S)], fill=color, width=int(8 * S))
        d.ellipse([px + sgn * 36 * S - 7 * S, top - 47 * S, px + sgn * 36 * S + 7 * S, top - 33 * S], fill=color)
        ex = x0 - 30 * S if sgn < 0 else x0 + bw + 30 * S
        d.line([(ex, floor - bh + 8 * S), (ex + sgn * 22 * S, floor - bh - 18 * S)], fill=color, width=int(6 * S))
    # stairs
    for k in range(6):
        d.line([(x0 - 30 * S - k * 9 * S, floor + k * 16 * S), (x0 - 6 * S - k * 9 * S, floor + k * 16 * S)], fill=color, width=int(4 * S))
    d.line([(x0 - 4 * S, floor), (x0 - 60 * S, ch)], fill=color, width=int(4 * S))
    wins = []
    if lit:
        for wx in (x0 + 50 * S, x0 + 170 * S):
            ww, wh = 60 * S, 64 * S
            wy = floor - bh + 30 * S
            d.rectangle([wx, wy, wx + ww, wy + wh], fill=(255, 196, 110, 255))
            d.line([(wx + ww / 2, wy), (wx + ww / 2, wy + wh)], fill=color, width=int(4 * S))
            wins.append((wx / 2, wy / 2, ww / 2, wh / 2))
    return down(img), wins


def ghost_tani(t, scale=1.0, eyes=0.0, closed=False):
    """Woman in green Thai dress, hair in a bun, floating; hem fades into mist. eyes: 0..1 green glow."""
    S = 2 * scale
    cw, ch = int(360 * S), int(820 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    top = 70 * S
    skin = (226, 214, 198, 255)
    hair = (18, 14, 14, 255)
    dress = (36, 128, 84, 255)
    dress_d = (24, 92, 60, 255)
    gold = (214, 176, 92, 255)
    sash = (60, 160, 110, 255)
    # skirt (pha sin)
    sk = []
    for i in range(21):
        u = i / 20
        y = top + 270 * S + u * 470 * S
        wv = (52 + 40 * u) * S + 5 * S * math.sin(t * 1.7 + u * 5)
        sk.append((cx + wv, y))
    hem = [(cx + (92 - 184 * i / 20) * S, top + 740 * S + 12 * S * math.sin(i * 0.8 + t * 2)) for i in range(21)]
    left = [(2 * cx - p[0] + 4 * S * math.sin(t * 2 + k), p[1]) for k, p in enumerate(sk)]
    d.polygon(sk + hem + left[::-1], fill=dress)
    for k in range(4):
        fx = cx + (-36 + 24 * k) * S
        d.line([(fx, top + 300 * S), (fx + (k - 1.5) * 16 * S, top + 730 * S)], fill=dress_d, width=int(4 * S))
    for yb in (560, 600):
        y = top + yb * S
        u = (yb - 270) / 470
        wv = (52 + 40 * u) * S
        d.line([(cx - wv, y), (cx + wv, y)], fill=gold, width=int(7 * S))
    # belt
    d.rectangle([cx - 54 * S, top + 262 * S, cx + 54 * S, top + 282 * S], fill=gold)
    # torso / bodice
    d.polygon([(cx - 46 * S, top + 120 * S), (cx + 46 * S, top + 120 * S), (cx + 52 * S, top + 266 * S), (cx - 52 * S, top + 266 * S)], fill=dress)
    # bare shoulder (right side, Thai sabai style)
    d.ellipse([cx + 18 * S, top + 108 * S, cx + 62 * S, top + 140 * S], fill=skin)
    # sabai sash over left shoulder, diagonal
    d.polygon([(cx - 60 * S, top + 112 * S), (cx - 20 * S, top + 108 * S), (cx + 54 * S, top + 236 * S), (cx + 40 * S, top + 270 * S),
               (cx - 56 * S, top + 160 * S)], fill=sash)
    d.line([(cx - 20 * S, top + 110 * S), (cx + 50 * S, top + 240 * S)], fill=gold, width=int(4 * S))
    # sash tail hanging behind left shoulder
    d.polygon([(cx - 60 * S, top + 118 * S), (cx - 44 * S, top + 120 * S), (cx - 56 * S + 6 * S * math.sin(t * 1.5), top + 380 * S),
               (cx - 74 * S + 6 * S * math.sin(t * 1.5), top + 376 * S)], fill=sash)
    # arms
    for s_ in (1, -1):
        sx, sy = cx + s_ * 48 * S, top + 128 * S
        ex, ey = sx + s_ * (20 * S + 3 * S * math.sin(t * 1.4 + s_)), top + 400 * S
        d.line([(sx, sy), (ex, ey)], fill=skin, width=int(15 * S))
        d.ellipse([ex - 9 * S, ey - 4 * S, ex + 9 * S, ey + 26 * S], fill=skin)
        d.ellipse([sx - 10 * S, top + 236 * S, sx + 10 * S, top + 250 * S], fill=gold)  # bracelet hint
    # neck + collar
    d.rectangle([cx - 13 * S, top + 80 * S, cx + 13 * S, top + 118 * S], fill=skin)
    d.arc([cx - 40 * S, top + 92 * S, cx + 40 * S, top + 140 * S], 20, 160, fill=gold, width=int(5 * S))
    # head
    d.ellipse([cx - 34 * S, top, cx + 34 * S, top + 94 * S], fill=skin)
    d.ellipse([cx - 38 * S, top - 6 * S, cx + 38 * S, top + 40 * S], fill=hair)
    d.ellipse([cx - 24 * S, top - 42 * S, cx + 24 * S, top - 2 * S], fill=hair)       # bun
    d.rectangle([cx - 36 * S, top + 8 * S, cx - 28 * S, top + 52 * S], fill=hair)
    d.rectangle([cx + 28 * S, top + 8 * S, cx + 36 * S, top + 52 * S], fill=hair)
    d.ellipse([cx + 14 * S, top - 30 * S, cx + 30 * S, top - 14 * S], fill=gold)      # hair pin flower
    # eyes
    ey_ = top + 50 * S
    for s_ in (-1, 1):
        ex = cx + s_ * 14 * S
        if closed:
            d.arc([ex - 9 * S, ey_ - 6 * S, ex + 9 * S, ey_ + 4 * S], 20, 160, fill=(60, 40, 40, 255), width=int(2 * S))
        else:
            d.ellipse([ex - 8 * S, ey_ - 4 * S, ex + 8 * S, ey_ + 4 * S], fill=(20, 16, 18, 255))
            if eyes > 0:
                g = int(255 * eyes)
                d.ellipse([ex - 6 * S, ey_ - 3 * S, ex + 6 * S, ey_ + 3 * S], fill=(120, 255, 170, g))
    d.line([(cx - 7 * S, top + 74 * S), (cx + 7 * S, top + 74 * S)], fill=(170, 110, 110, 255), width=int(2 * S))
    im = down(img)
    # fade the hem into mist
    a = np.array(im.split()[3]).astype(np.float32)
    hh = a.shape[0]
    ramp = np.clip((hh * 0.97 - np.arange(hh)) / (hh * 0.22), 0, 1)[:, None]
    a *= ramp
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    al = im.split()[3].filter(ImageFilter.GaussianBlur(20 * scale))
    g = Image.new("RGBA", im.size, (110, 255, 170, 0)); g.putalpha(al.point(lambda v: int(v * 0.7)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g); out.alpha_composite(im)
    if eyes > 0.05:
        eg = glow_sprite(int(26 * scale), (120, 255, 170), 1.6)
        arr = np.asarray(out).astype(np.float32)
        rgb = arr[..., :3]
        for s_ in (-1, 1):
            add_glow(rgb, eg, out.width / 2 + s_ * 14 * scale, 70 * scale + 50 * scale, eyes * 1.2)
        arr[..., :3] = np.clip(rgb, 0, 255)
        out = Image.fromarray(arr.astype(np.uint8))
    return out


class FallingRibbons:
    def __init__(self, x, y0, y1, scale=1.0, n=6, seed=3):
        rnd = random.Random(seed)
        self.p = [dict(x=x + rnd.uniform(-20, 20), y0=y0 - rnd.uniform(0, 160), y1=y1 - rnd.uniform(0, 20),
                       c=RIBBON_COLS[i % len(RIBBON_COLS)], ph=rnd.uniform(0, 6), dx=rnd.uniform(-160, 160),
                       delay=rnd.uniform(0, 1.6)) for i in range(n)]
        self.scale = scale

    def draw(self, img, t, t0):
        d = ImageDraw.Draw(img)
        for q in self.p:
            u = ease((t - t0 - q["delay"]) / 1.6)
            if t < t0 + q["delay"]:
                continue
            x = q["x"] + q["dx"] * u + 18 * math.sin(t * 3 + q["ph"]) * (1 - u)
            y = q["y0"] + (q["y1"] - q["y0"]) * u
            ang = math.sin(t * 4 + q["ph"]) * (1 - u) * 0.9 + u * 1.45
            L = 70 * self.scale
            pts = []
            for i in range(8):
                v = i / 7
                pts.append((x + math.cos(ang) * L * v + 6 * math.sin(v * 5 + t * 3) * (1 - u), y + math.sin(ang) * L * v * 0.4))
            d.line(pts, fill=q["c"] + (255,), width=int(9 * self.scale))
