"""Episode 3 (Japan, Kuchisake-onna) drawing helpers: a Japanese residential street at night,
utility poles and wires, block walls, vending machines, sodium streetlights, a curved traffic mirror,
a schoolgirl (Yui), a grandmother, and the masked woman in a long red coat."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from art_v import *

CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
CJK_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"


def cjk(size, serif=False):
    return ImageFont.truetype(CJK_SERIF if serif else CJK, size, index=0)


# ---------------------------------------------------------------- palette (cold indigo night + sodium orange + red coat)
SKY_TOP = (6, 10, 22)
SKY_BOT = (34, 46, 70)
CITY = (20, 26, 44, 255)
HOUSE = (12, 15, 26, 255)
WALL = (40, 42, 52, 255)
ROAD = (22, 24, 32, 255)
SODIUM = (255, 176, 92)
VEND = (190, 240, 255)
COAT = (150, 22, 30, 255)
COAT_D = (100, 12, 20, 255)
COAT_L = (190, 44, 48, 255)
HAIR = (10, 8, 12, 255)
SKIN = (232, 226, 222, 255)
MASK = (244, 246, 248, 255)
MASK_D = (196, 204, 214, 255)


def city_layer(w, base, seed=3, lit=0.5):
    """Far apartment blocks with a few lit windows."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = -20
    while x < w:
        bw = rnd.randint(90, 220); bh = rnd.randint(120, 330)
        d.rectangle([x, base - bh, x + bw, base], fill=CITY)
        if rnd.random() < 0.3:
            d.rectangle([x + bw * 0.4, base - bh - 40, x + bw * 0.45, base - bh], fill=CITY)
        for wy in range(base - bh + 16, base - 10, 26):
            for wx in range(x + 10, x + bw - 14, 22):
                if rnd.random() < 0.12 * lit:
                    c = rnd.choice([(255, 214, 150), (200, 230, 255), (255, 240, 200)])
                    d.rectangle([wx, wy, wx + 9, wy + 12], fill=c + (int(150 + 80 * rnd.random()),))
        x += bw + rnd.randint(-10, 20)
    return img


def jp_house(scale=1.0, seed=0, lit=None, color=HOUSE):
    """Two-storey Japanese house: hipped tile roofs (two tiers), small windows, AC unit, laundry pole."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(420 * S), int(460 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bw = 300 * S; x0 = (cw - bw) / 2; floor = ch
    # ground floor + first roof (skirt roof)
    d.rectangle([x0, floor - 150 * S, x0 + bw, floor], fill=color)
    d.polygon([(x0 - 30 * S, floor - 150 * S), (x0 + bw + 30 * S, floor - 150 * S), (x0 + bw - 10 * S, floor - 185 * S),
               (x0 + 10 * S, floor - 185 * S)], fill=color)
    # upper floor
    ux0, ux1 = x0 + 30 * S, x0 + bw - 40 * S
    d.rectangle([ux0, floor - 320 * S, ux1, floor - 180 * S], fill=color)
    # top hipped roof with slightly curved eaves
    d.polygon([(ux0 - 40 * S, floor - 316 * S), (ux1 + 40 * S, floor - 316 * S), (ux1 - 40 * S, floor - 390 * S),
               (ux0 + 40 * S, floor - 390 * S)], fill=color)
    for sgn, ex in ((-1, ux0 - 40 * S), (1, ux1 + 40 * S)):
        d.line([(ex, floor - 316 * S), (ex + sgn * 10 * S, floor - 326 * S)], fill=color, width=int(5 * S))
    # tile lines (subtle lighter)
    tl = tuple(min(255, v + 10) for v in color[:3]) + (255,)
    for k in range(1, 5):
        yy = floor - 316 * S - k * 12 * S
        d.line([(ux0 - 40 * S + k * 13 * S, yy), (ux1 + 40 * S - k * 13 * S, yy)], fill=tl, width=max(1, int(1.5 * S)))
    # AC unit + laundry pole on the balcony
    d.rectangle([ux1 - 70 * S, floor - 230 * S, ux1 - 20 * S, floor - 195 * S], fill=tl)
    d.line([(ux0 + 10 * S, floor - 250 * S), (ux1 - 80 * S, floor - 250 * S)], fill=tl, width=int(3 * S))
    wins = []
    lit = rnd.random() < 0.5 if lit is None else lit
    if lit:
        c = rnd.choice([(255, 206, 140), (255, 230, 190), (210, 235, 255)])
        for wx, wy, ww, wh in ((ux0 + 30 * S, floor - 290 * S, 70 * S, 60 * S), (x0 + 40 * S, floor - 120 * S, 90 * S, 70 * S)):
            if rnd.random() < 0.7:
                d.rectangle([wx, wy, wx + ww, wy + wh], fill=c + (255,))
                d.line([(wx + ww / 2, wy), (wx + ww / 2, wy + wh)], fill=color, width=int(3 * S))
                d.line([(wx, wy + wh / 2), (wx + ww, wy + wh / 2)], fill=color, width=int(2 * S))
                wins.append(((wx + ww / 2) / 2, (wy + wh / 2) / 2))
    return down(img), wins


def block_wall(w, y_top, y_bot, color=WALL, seed=1):
    """Grey concrete block wall that lines Japanese streets, with block seams."""
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y_top, w, y_bot], fill=color)
    seam = tuple(max(0, v - 10) for v in color[:3]) + (255,)
    bh = (y_bot - y_top) / 4
    for r in range(5):
        yy = y_top + r * bh
        d.line([(0, yy), (w, yy)], fill=seam, width=2)
        off = 0 if r % 2 else 60
        for x in range(-off, w, 120):
            d.line([(x, yy), (x, yy + bh)], fill=seam, width=2)
    d.rectangle([0, y_top - 8, w, y_top], fill=tuple(min(255, v + 12) for v in color[:3]) + (255,))
    return img


def utility_pole(h=900, color=SIL):
    img = Image.new("RGBA", (220, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(100, 0), (120, 0), (126, h), (94, h)], fill=color)
    for y, wdt in ((40, 100), (90, 80)):
        d.rectangle([110 - wdt, y, 110 + wdt, y + 10], fill=color)
        for x in (110 - wdt + 6, 110 + wdt - 6):
            d.rectangle([x - 4, y - 14, x + 4, y], fill=color)
    d.rectangle([128, 150, 168, 210], fill=color)          # transformer
    for k in range(6):                                     # step bolts
        y = 300 + k * 60
        d.line([(92 if k % 2 else 128, y), (80 if k % 2 else 140, y)], fill=color, width=4)
    return img


def wires(img, xs, ys, sag=60, color=(5, 6, 14, 255), width=3):
    """Catenary wires between consecutive pole tops."""
    d = ImageDraw.Draw(img)
    for i in range(len(xs) - 1):
        for dy, sg in zip(ys, (sag, sag * 1.2, sag * 0.8)):
            pts = []
            for k in range(25):
                u = k / 24
                pts.append((xs[i] + (xs[i + 1] - xs[i]) * u, dy + sg * 4 * u * (1 - u)))
            d.line(pts, fill=color, width=width)


def vending_machine(scale=1.0, seed=0, hue=(220, 40, 50)):
    S = 2 * scale
    cw, ch = int(170 * S), int(300 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    d.rounded_rectangle([0, 0, cw - 1, ch - 1], 8 * S, fill=hue + (255,))
    d.rectangle([12 * S, 14 * S, cw - 12 * S, 170 * S], fill=(225, 245, 255, 255))
    cols = [(240, 60, 60), (40, 120, 220), (250, 200, 40), (60, 180, 90), (250, 250, 250), (140, 70, 40), (240, 130, 30)]
    for r in range(3):
        y = 24 * S + r * 50 * S
        for c in range(6):
            x = 20 * S + c * 22 * S
            col = rnd.choice(cols)
            d.rounded_rectangle([x, y, x + 15 * S, y + 32 * S], 4 * S, fill=col + (255,))
            d.rectangle([x + 3 * S, y + 36 * S, x + 12 * S, y + 40 * S], fill=(255, 90, 60, 255))
    d.rectangle([12 * S, 190 * S, cw - 60 * S, 205 * S], fill=(20, 20, 28, 255))
    d.rectangle([cw - 50 * S, 185 * S, cw - 16 * S, 235 * S], fill=(200, 205, 215, 255))
    d.rectangle([20 * S, 250 * S, cw - 20 * S, 285 * S], fill=(20, 20, 28, 255))
    return down(img)


def streetlight(h=760, color=SIL, on=True):
    img = Image.new("RGBA", (300, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([40, 60, 52, h], fill=color)
    d.arc([40, 30, 200, 130], 180, 270, fill=color, width=12)
    d.rectangle([120, 26, 210, 44], fill=color)
    if on:
        d.rectangle([128, 44, 202, 52], fill=SODIUM + (255,))
    return img, (165, 50)          # lamp position


def light_cone(img, x, y, ground_y, k=1.0, color=SODIUM, spread=230):
    """Soft cone of streetlight + pool on the road."""
    if k <= 0.01:
        return
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.polygon([(x - 20, y), (x + 20, y), (x + spread, ground_y), (x - spread, ground_y)], fill=color + (int(46 * k),))
    d.ellipse([x - spread * 1.25, ground_y - 40, x + spread * 1.25, ground_y + 60], fill=color + (int(70 * k),))
    img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(26)))


def curve_mirror(scale=1.0, color=(230, 110, 30, 255)):
    """Orange-poled curved traffic mirror. Returns (img, mirror centre, radius)."""
    S = 2 * scale
    cw, ch = int(260 * S), int(820 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = cw / 2, 120 * S, 100 * S
    d.rectangle([cx - 8 * S, cy, cx + 8 * S, ch], fill=color)
    d.ellipse([cx - r - 12 * S, cy - r - 12 * S, cx + r + 12 * S, cy + r + 12 * S], fill=color)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 70, 90, 255))
    return down(img), (cx / 2, cy / 2), r / 2


# ---------------------------------------------------------------- characters
def student(phase=0.0, walking=True, facing=1, color=(10, 10, 20, 255), rim=(120, 140, 200), scale=1.0, run=False,
            tremble=0.0, look_up=0.0):
    """Schoolgirl in a sailor uniform (side view): bob hair, pleated skirt, shoulder bag. Returns (img, feet anchor)."""
    cw, ch = 320, 500
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 150
    amp = float(walking) * (1.5 if run else 1.0)
    bob = -8 * abs(math.cos(phase)) * amp
    lean = 0.18 if run else 0.0
    hip = (cx, 280 + bob)
    sw = math.sin(phase) * amp

    def limb(p, a1, l1, a2, l2, wd):
        k = (p[0] + math.sin(a1) * l1, p[1] + math.cos(a1) * l1)
        e = (k[0] + math.sin(a2) * l2, k[1] + math.cos(a2) * l2)
        d.line([p, k], fill=color, width=wd); d.line([k, e], fill=color, width=wd)
        for q in (p, k):
            d.ellipse([q[0] - wd / 2, q[1] - wd / 2, q[0] + wd / 2, q[1] + wd / 2], fill=color)
        return e

    for s in (1, -1):
        a = 0.42 * sw * s
        bend = 0.55 * max(0, -math.sin(phase + (0 if s > 0 else math.pi))) * amp
        e = limb((hip[0], hip[1] + 20), a, 92, a - bend, 92, 18)
        d.polygon([(e[0] - 10, e[1] + 4), (e[0] + 24, e[1] + 4), (e[0] + 20, e[1] - 8), (e[0] - 8, e[1] - 10)], fill=color)
    sh = (cx + 6 + 60 * lean, 150 + bob + 10 * lean)
    # pleated skirt
    d.polygon([(hip[0] - 26, hip[1] - 10), (hip[0] + 26, hip[1] - 10), (hip[0] + 46 + 8 * sw, hip[1] + 62),
               (hip[0] - 44 + 8 * sw, hip[1] + 62)], fill=color)
    # torso (blouse) with sailor collar flap at the back
    d.polygon([(hip[0] - 22, hip[1] - 6), (hip[0] + 22, hip[1] - 6), (sh[0] + 26, sh[1]), (sh[0] - 26, sh[1])], fill=color)
    d.polygon([(sh[0] - 28, sh[1] - 4), (sh[0] - 4, sh[1] - 4), (sh[0] - 6, sh[1] + 40), (sh[0] - 34, sh[1] + 36)], fill=color)
    # head: bob haircut
    hd = (sh[0] + 6, sh[1] - 46 - 4 * look_up)
    d.ellipse([hd[0] - 26, hd[1] - 30, hd[0] + 26, hd[1] + 28], fill=color)
    d.ellipse([hd[0] + 16, hd[1] - 2 - 6 * look_up, hd[0] + 30, hd[1] + 12 - 6 * look_up], fill=color)
    d.rectangle([hd[0] - 9, hd[1] + 18, hd[0] + 11, sh[1]], fill=color)
    d.polygon([(hd[0] - 34, hd[1] - 14), (hd[0] - 2, hd[1] - 40), (hd[0] + 28, hd[1] - 30), (hd[0] + 28, hd[1] - 10),
               (hd[0] - 4, hd[1] - 16), (hd[0] - 30, hd[1] + 34), (hd[0] - 40, hd[1] + 30)], fill=color)
    # arms
    limb((sh[0] - 4, sh[1] + 8), -0.45 * sw - 0.1, 70, -0.45 * sw - 0.4, 64, 15)
    hand = limb((sh[0] + 4, sh[1] + 8), 0.4 * sw + 0.1, 70, 0.4 * sw - 0.3 - 0.8 * run, 64, 15)
    # school bag on the shoulder strap
    bx, by = hip[0] - 46, hip[1] - 40
    d.line([(sh[0] - 4, sh[1] + 4), (bx + 20, by)], fill=color, width=5)
    d.rounded_rectangle([bx - 18, by - 6 + 4 * sw, bx + 26, by + 48 + 4 * sw], 8, fill=color)
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


def grandma(color=(30, 20, 14, 255), rim=(255, 200, 140), scale=1.0):
    """Grandmother kneeling (seiza) seen from the side, hair in a small bun, cup in hand."""
    cw, ch = 320, 320
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([50, 248, 236, 300], 26, fill=color)                     # folded legs (seiza)
    d.polygon([(70, 262), (176, 262), (192, 150), (150, 112), (92, 120), (66, 170)], fill=color)  # hunched back + kimono
    d.ellipse([62, 104, 176, 214], fill=color)                                   # rounded back
    d.ellipse([160, 72, 226, 140], fill=color)                                   # head (forward)
    d.ellipse([140, 60, 176, 96], fill=color)                                    # bun
    d.polygon([(220, 102), (234, 110), (222, 118)], fill=color)                  # nose
    d.line([(170, 160), (214, 222), (246, 204)], fill=color, width=18)           # arm to cup
    d.rectangle([240, 186, 268, 214], fill=color)                                # tea cup
    A = np.array(img.split()[3]).astype(np.int16)
    sh_ = np.zeros_like(A); sh_[3:, :-5] = A[:-3, 5:]
    arr = np.array(img); m = np.clip(A - sh_, 0, 255) > 0
    arr[m, 0], arr[m, 1], arr[m, 2] = rim
    img = Image.fromarray(arr)
    k = scale / 2
    return img.resize((int(cw * k * 2), int(ch * k * 2)), Image.LANCZOS)


def kuchisake(t, scale=1.0, reach=0.0, mask_drop=0.0, eyes=0.0, glow=0.7, crop_legs=False):
    """Tall woman: long straight black hair with blunt bangs, pale face, big white surgical mask,
    long red belted coat. reach 0..1 lifts her right hand to the mask; mask_drop 0..1 slides the mask
    down a little, but the area under it is always kept in deep shadow (no mouth is ever shown).
    eyes 0..1 = small red glints. Returns RGBA anchored centre-top."""
    S = 2 * scale
    cw, ch = int(360 * S), int(900 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    top = 40 * S
    sw = math.sin(t * 0.9)
    # hair behind the body (long, to the waist)
    d.polygon([(cx - 58 * S, top + 40 * S), (cx + 58 * S, top + 40 * S), (cx + 70 * S + 4 * S * sw, top + 360 * S),
               (cx - 70 * S + 4 * S * sw, top + 360 * S)], fill=HAIR)
    # legs + shoes below the coat
    for s_ in (-1, 1):
        d.rectangle([cx + s_ * 22 * S - 7 * S, top + 700 * S, cx + s_ * 22 * S + 7 * S, top + 800 * S], fill=(30, 24, 30, 255))
        d.ellipse([cx + s_ * 22 * S - 14 * S, top + 792 * S, cx + s_ * 22 * S + 14 * S, top + 812 * S], fill=(16, 10, 14, 255))
    # long coat (A-line)
    d.polygon([(cx - 64 * S, top + 140 * S), (cx + 64 * S, top + 140 * S), (cx + 104 * S, top + 710 * S),
               (cx - 104 * S, top + 710 * S)], fill=COAT)
    # front opening + buttons + belt
    d.line([(cx + 6 * S, top + 170 * S), (cx + 18 * S, top + 708 * S)], fill=COAT_D, width=int(5 * S))
    for k in range(4):
        y = top + (200 + k * 50) * S
        d.ellipse([cx - 22 * S, y - 5 * S, cx - 12 * S, y + 5 * S], fill=COAT_D)
    d.rectangle([cx - 76 * S, top + 360 * S, cx + 76 * S, top + 384 * S], fill=COAT_D)
    d.rectangle([cx - 12 * S, top + 356 * S, cx + 16 * S, top + 388 * S], outline=(60, 8, 12, 255), width=int(4 * S))
    d.polygon([(cx + 30 * S, top + 384 * S), (cx + 44 * S, top + 384 * S), (cx + 52 * S + 3 * S * sw, top + 520 * S),
               (cx + 38 * S + 3 * S * sw, top + 520 * S)], fill=COAT_D)    # belt tail
    # fold lines in the skirt of the coat
    for k in (-1, 1):
        d.line([(cx + k * 40 * S, top + 400 * S), (cx + k * 70 * S, top + 700 * S)], fill=COAT_D, width=int(3 * S))
    # lapels / wide collar
    d.polygon([(cx - 64 * S, top + 140 * S), (cx - 6 * S, top + 150 * S), (cx + 6 * S, top + 250 * S), (cx - 40 * S, top + 200 * S)], fill=COAT_L)
    d.polygon([(cx + 64 * S, top + 140 * S), (cx + 6 * S, top + 150 * S), (cx + 10 * S, top + 250 * S), (cx + 44 * S, top + 200 * S)], fill=COAT_L)
    # arms (sleeves); right arm (viewer's left) may reach to the mask
    d.polygon([(cx + 64 * S, top + 146 * S), (cx + 84 * S, top + 160 * S), (cx + 96 * S, top + 420 * S), (cx + 72 * S, top + 424 * S)], fill=COAT)
    d.line([(cx + 66 * S, top + 160 * S), (cx + 74 * S, top + 420 * S)], fill=COAT_D, width=int(3 * S))
    d.rectangle([cx + 72 * S, top + 414 * S, cx + 96 * S, top + 426 * S], fill=COAT_D)
    d.ellipse([cx + 75 * S, top + 422 * S, cx + 93 * S, top + 446 * S], fill=SKIN)
    r = ease(reach)
    shx, shy = cx - 70 * S, top + 152 * S
    hx = (cx - 84 * S) * (1 - r) + (cx - 30 * S) * r
    hy = (top + 430 * S) * (1 - r) + (top + 120 * S) * r
    elx = shx - 30 * S * r - 14 * S * (1 - r)
    ely = (shy + 140 * S) * (1 - r) + (shy + 110 * S) * r
    d.line([(shx, shy), (elx, ely)], fill=COAT, width=int(28 * S))
    d.line([(elx, ely), (hx, hy)], fill=COAT, width=int(24 * S))
    d.ellipse([elx - 14 * S, ely - 14 * S, elx + 14 * S, ely + 14 * S], fill=COAT)
    # neck
    d.rectangle([cx - 11 * S, top + 100 * S, cx + 11 * S, top + 146 * S], fill=(200, 192, 190, 255))
    d.polygon([(cx - 30 * S, top + 142 * S), (cx + 30 * S, top + 142 * S), (cx, top + 168 * S)], fill=COAT_D)
    # face
    d.ellipse([cx - 37 * S, top - 4 * S, cx + 37 * S, top + 118 * S], fill=SKIN)
    # mask: shadow under it first (always dark), then the mask itself
    md = 20 * S * mask_drop
    d.polygon([(cx - 36 * S, top + 66 * S), (cx + 36 * S, top + 66 * S), (cx + 26 * S, top + 114 * S), (cx - 26 * S, top + 114 * S)],
              fill=(14, 10, 16, 255) if mask_drop > 0 else SKIN)
    mx0, mx1, my0, my1 = cx - 41 * S, cx + 41 * S, top + 64 * S + md, top + 120 * S + md
    d.rounded_rectangle([mx0, my0, mx1, my1], 14 * S, fill=MASK)
    d.rounded_rectangle([mx0, my1 - 12 * S, mx1, my1], 10 * S, fill=MASK_D)
    d.line([(cx, my0 + 4 * S), (cx, my0 + 16 * S)], fill=MASK_D, width=int(2 * S))
    for k in range(3):
        yy = my0 + (14 + 14 * k) * S
        d.line([(mx0 + 8 * S, yy), (mx1 - 8 * S, yy)], fill=MASK_D, width=int(2 * S))
    for s_ in (-1, 1):
        d.line([(cx + s_ * 44 * S, my0 + 6 * S), (cx + s_ * 40 * S, top + 40 * S)], fill=MASK_D, width=int(3 * S))
    # hair: bangs + side curtains over the face edges
    d.chord([cx - 44 * S, top - 22 * S, cx + 44 * S, top + 60 * S], 180, 360, fill=HAIR)
    d.rectangle([cx - 44 * S, top + 18 * S, cx + 44 * S, top + 32 * S], fill=HAIR)
    for s_ in (-1, 1):
        d.polygon([(cx + s_ * 44 * S, top + 20 * S), (cx + s_ * 32 * S, top + 36 * S), (cx + s_ * 38 * S, top + 200 * S),
                   (cx + s_ * 60 * S + 3 * S * sw, top + 260 * S), (cx + s_ * 62 * S, top + 40 * S)], fill=HAIR)
    # eyes (narrow, unblinking)
    ey = top + 47 * S
    for s_ in (-1, 1):
        ex = cx + s_ * 17 * S
        d.ellipse([ex - 9 * S, ey - 3.5 * S, ex + 9 * S, ey + 3.5 * S], fill=(16, 10, 14, 255))
        d.ellipse([ex - 2 * S + s_ * S, ey - 2 * S, ex + 2 * S + s_ * S, ey + 2 * S],
                  fill=(255, 90 + int(140 * (1 - eyes)), 90 + int(140 * (1 - eyes)), 255))
    # hand over the mask when reaching
    if r > 0.02:
        d.rounded_rectangle([hx - 14 * S, hy - 22 * S, hx + 14 * S, hy + 20 * S], 12 * S, fill=SKIN)
        d.line([(hx - 6 * S, hy - 20 * S), (hx - 6 * S, hy + 4 * S)], fill=(205, 196, 194, 255), width=int(2 * S))
        d.line([(hx + 4 * S, hy - 20 * S), (hx + 4 * S, hy + 4 * S)], fill=(205, 196, 194, 255), width=int(2 * S))
    im = down(img)
    if crop_legs:
        a = np.array(im.split()[3]).astype(np.float32)
        hh = a.shape[0]
        a *= np.clip((hh * 0.95 - np.arange(hh)) / (hh * 0.25), 0, 1)[:, None]
        im.putalpha(Image.fromarray(a.astype(np.uint8)))
    if glow > 0:
        al = im.split()[3].filter(ImageFilter.GaussianBlur(18 * scale))
        g = Image.new("RGBA", im.size, (255, 60, 60, 0)); g.putalpha(al.point(lambda v: int(v * 0.45 * glow)))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(g); out.alpha_composite(im)
        im = out
    if eyes > 0.05:
        eg = glow_sprite(int(24 * scale), (255, 50, 50), 1.6)
        arr = np.asarray(im).astype(np.float32)
        rgb = arr[..., :3]
        for s_ in (-1, 1):
            add_glow(rgb, eg, im.width / 2 + s_ * 17 * scale, (40 + 47) * scale, eyes * 0.9)
        arr[..., :3] = np.clip(rgb, 0, 255)
        im = Image.fromarray(arr.astype(np.uint8))
    return im


def candy(scale=1.0, col=(240, 170, 40)):
    """Wrapped hard candy icon."""
    S = 2 * scale
    img = Image.new("RGBA", (int(160 * S), int(80 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = 80 * S, 40 * S
    d.polygon([(cx - 34 * S, cy), (cx - 70 * S, cy - 26 * S), (cx - 70 * S, cy + 26 * S)], fill=(250, 230, 200, 255))
    d.polygon([(cx + 34 * S, cy), (cx + 70 * S, cy - 26 * S), (cx + 70 * S, cy + 26 * S)], fill=(250, 230, 200, 255))
    d.ellipse([cx - 36 * S, cy - 28 * S, cx + 36 * S, cy + 28 * S], fill=col + (255,))
    d.ellipse([cx - 20 * S, cy - 18 * S, cx - 4 * S, cy - 8 * S], fill=(255, 240, 200, 220))
    return down(img)


def seigaiha_bg(top=(8, 14, 30), bot=(40, 12, 22), seed=0):
    """Explain/outro background: indigo-to-crimson gradient with a faint seigaiha (wave) pattern."""
    y = np.linspace(0, 1, H)[:, None, None]
    base = np.repeat(np.array(top) * (1 - y) + np.array(bot) * y, W, axis=1).astype(np.float32)
    pat = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(pat)
    R = 60
    for row in range(-1, H // (R // 2) + 2):
        yy = row * R / 2
        off = 0 if row % 2 else R
        for x in range(-R * 2, W + R * 2, R * 2):
            for k in (1.0, 0.75, 0.5):
                rr = R * k
                d.arc([x + off - rr, yy - rr, x + off + rr, yy + rr], 180, 360, fill=255, width=2)
    p = np.asarray(pat).astype(np.float32)[..., None] / 255
    base += p * 14
    return base
