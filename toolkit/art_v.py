"""Drawing helpers for the cartoon: sky, trees, houses, characters, particles, captions."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
SIL = (7, 8, 18, 255)        # near silhouette
MID = (16, 18, 38, 255)      # mid layer
FAR = (28, 32, 62, 255)      # far hills

INTER_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INTER_L = "/usr/share/fonts/opentype/inter/Inter-Light.otf"
INTER_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
LORA = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"


def font(path, size, var=None):
    f = ImageFont.truetype(path, size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


def down(img, f=2):
    return img.resize((img.width // f, img.height // f), Image.LANCZOS)


# ---------------------------------------------------------------- sky
def sky(top, bot, moon=None, moon_r=46, stars=160, seed=1, w=W, h=H):
    y = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - y) + np.array(bot)[None, None, :] * y)
    arr = np.repeat(arr, w, axis=1).astype(np.float32)
    rnd = random.Random(seed)
    for _ in range(stars):
        x, yy = rnd.randrange(w), rnd.randrange(int(h * 0.7))
        b = rnd.uniform(60, 200) * (1 - yy / (h * 0.8))
        arr[yy, x] += b
        if b > 150 and x + 1 < w:
            arr[yy, x + 1] += b * .4
    if moon:
        mx, my = moon
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
        glow = np.exp(-((d / (moon_r * 5)) ** 2)) * 70 + np.exp(-((d / (moon_r * 1.8)) ** 2)) * 50
        arr += glow[..., None] * np.array([0.8, 0.85, 1.0])
        disk = np.clip((moon_r - d) / 1.5, 0, 1)
        # soft craters
        crat = np.zeros_like(d)
        for cx, cy, cr in ((-12, -10, 12), (14, 8, 9), (-4, 18, 7), (16, -16, 6)):
            dd = np.sqrt((xx - mx - cx) ** 2 + (yy - my - cy) ** 2)
            crat += np.clip((cr - dd) / 4, 0, 1) * 18
        moonc = np.array([238, 234, 214])[None, None, :] - crat[..., None]
        arr = arr * (1 - disk[..., None]) + moonc * disk[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def hills(w, base, amp, color, seed, h=H, freq=1.0):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(4)]
    pts = []
    for x in range(0, w + 8, 8):
        y = base + amp * (0.6 * math.sin(x * 0.004 * freq + ph[0]) + 0.3 * math.sin(x * 0.011 * freq + ph[1])
                          + 0.1 * math.sin(x * 0.03 * freq + ph[2]))
        pts.append((x, y))
    pts += [(w, h), (0, h)]
    ImageDraw.Draw(img).polygon(pts, fill=color)
    return img


def ground(w, y0, color, seed=3, h=H, tufts=True):
    img = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    pts = [(x, 2 * y0 + 6 * math.sin(x * 0.004 + seed)) for x in range(0, 2 * w + 10, 10)]
    d.polygon(pts + [(2 * w, 2 * h), (0, 2 * h)], fill=color)
    if tufts:
        for _ in range(w // 6):
            x = rnd.uniform(0, 2 * w)
            yb = 2 * y0 + 6 * math.sin(x * 0.004 + seed) + 4
            for k in range(rnd.randint(2, 5)):
                hgt = rnd.uniform(10, 40)
                lean = rnd.uniform(-14, 14)
                d.polygon([(x + k * 4 - 3, yb), (x + k * 4 + 3, yb), (x + k * 4 + lean, yb - hgt)], fill=color)
    return down(img)


# ---------------------------------------------------------------- banana tree
def leaf(d, base, ang, length, width, droop, color, rnd, tears=True):
    bx, by = base
    dx, dy = math.cos(ang), math.sin(ang)
    left, right, ctr = [], [], []
    n = 24
    for i in range(n + 1):
        t = i / n
        px = bx + dx * length * t
        py = by + dy * length * t + droop * length * t * t
        tx = dx * length
        ty = dy * length + 2 * droop * length * t
        nl = math.hypot(tx, ty)
        nx, ny = -ty / nl, tx / nl
        wv = width * (math.sin(math.pi * min(1, t * 1.05)) ** 0.7) * (0.25 if t < 0.12 else 1)
        left.append((px + nx * wv, py + ny * wv))
        right.append((px - nx * wv, py - ny * wv))
        ctr.append((px, py))
    d.polygon(left + right[::-1], fill=color)
    d.line(ctr[:4], fill=color, width=int(width * 0.35))
    if tears:
        for _ in range(rnd.randint(4, 9)):
            i = rnd.randint(5, n - 2)
            side = rnd.choice((left, right))
            ex, ey = side[i]
            cx, cy = ctr[i]
            mx, my = ex + (cx - ex) * 0.93, ey + (cy - ey) * 0.93
            d.line([(ex + (ex - cx) * .1, ey + (ey - cy) * .1), (mx, my)], fill=(0, 0, 0, 0), width=max(2, int(width * .07)))


def banana_tree(scale=1.0, seed=0, color=SIL, height=520, bend=None):
    """Returns RGBA image (1x) with trunk base at bottom-center."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(760 * S), int((height + 260) * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bx, by = cw / 2, ch
    th = height * S
    bend = rnd.uniform(-30, 30) * S if bend is None else bend * S
    pts_l, pts_r = [], []
    for i in range(21):
        t = i / 20
        x = bx + bend * t * t
        y = by - th * t
        wv = (26 - 10 * t) * S
        pts_l.append((x - wv, y)); pts_r.append((x + wv, y))
    d.polygon(pts_l + pts_r[::-1], fill=color)
    top = (bx + bend, by - th)
    # dead hanging leaves
    for k in range(rnd.randint(1, 3)):
        a = rnd.uniform(1.2, 1.9)
        leaf(d, (top[0] + rnd.uniform(-10, 10) * S, top[1] + 30 * S), a, rnd.uniform(160, 240) * S,
             rnd.uniform(10, 18) * S, 0.05, color, rnd, tears=False)
    # live leaves
    angs = [-2.7, -2.3, -1.9, -1.55, -1.2, -0.8, -0.4, -3.0, -0.1]
    rnd.shuffle(angs)
    for a in angs[:rnd.randint(7, 9)]:
        a += rnd.uniform(-0.12, 0.12)
        leaf(d, top, a, rnd.uniform(240, 340) * S, rnd.uniform(19, 27) * S, rnd.uniform(0.35, 0.8),
             color, rnd)
    return down(img)


def palm_tree(scale=1.0, seed=0, color=SIL, height=560):
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(700 * S), int((height + 220) * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bx, by = cw / 2, ch
    th = height * S
    bend = rnd.choice((-1, 1)) * rnd.uniform(60, 120) * S
    pl, pr = [], []
    for i in range(31):
        t = i / 30
        x = bx + bend * math.sin(t * 1.4) / math.sin(1.4)
        y = by - th * t
        wv = (16 - 6 * t) * S
        pl.append((x - wv, y)); pr.append((x + wv, y))
    d.polygon(pl + pr[::-1], fill=color)
    top = (bx + bend, by - th)
    for k in range(9):
        a = -math.pi + k * math.pi / 8 + rnd.uniform(-.15, .15)
        L = rnd.uniform(170, 250) * S
        pts = []
        for i in range(30):
            t = i / 29
            x = top[0] + math.cos(a) * L * t
            y = top[1] + math.sin(a) * L * t + 0.55 * L * t * t
            pts.append((x, y))
        d.line(pts, fill=color, width=int(5 * S))
        for i in range(3, 29, 1):
            x, y = pts[i]
            x2, y2 = pts[i + 1]
            tx, ty = x2 - x, y2 - y
            nl = math.hypot(tx, ty) or 1
            nx, ny = -ty / nl, tx / nl
            ll = (34 * math.sin(math.pi * i / 29) + 6) * S
            for sgn in (1, -1):
                d.line([(x, y), (x + (nx * sgn + tx / nl * .6) * ll, y + (ny * sgn + tx / nl * .2 + 0.6) * ll)],
                       fill=color, width=int(2.4 * S))
    d.ellipse([top[0] - 14 * S, top[1] - 4 * S, top[0] + 14 * S, top[1] + 24 * S], fill=color)
    return down(img)


def house(scale=1.0, color=SIL, seed=0):
    """Kampong house on stilts. Returns (img, windows list[(x,y,w,h)] in img coords)."""
    rnd = random.Random(seed)
    S = 2 * scale
    cw, ch = int(420 * S), int(380 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bw, bh = 300 * S, 120 * S
    x0 = (cw - bw) / 2
    floor = ch - 90 * S
    for sx in np.linspace(x0 + 10 * S, x0 + bw - 10 * S, 6):
        d.rectangle([sx - 5 * S, floor, sx + 5 * S, ch], fill=color)
    d.rectangle([x0, floor - bh, x0 + bw, floor], fill=color)
    d.rectangle([x0 - 10 * S, floor - 6 * S, x0 + bw + 10 * S, floor + 6 * S], fill=color)
    rt = floor - bh - 130 * S
    d.polygon([(x0 - 40 * S, floor - bh + 10 * S), (cw / 2, rt), (x0 + bw + 40 * S, floor - bh + 10 * S),
               (x0 + bw + 50 * S, floor - bh - 4 * S), (cw / 2, rt - 14 * S), (x0 - 50 * S, floor - bh - 4 * S)],
              fill=color)
    # stairs
    for k in range(5):
        d.line([(x0 + bw + 8 * S + k * 10 * S, floor + k * 18 * S), (x0 + bw + 30 * S + k * 10 * S, floor + k * 18 * S)],
               fill=color, width=int(4 * S))
    d.line([(x0 + bw + 6 * S, floor), (x0 + bw + 56 * S, ch)], fill=color, width=int(4 * S))
    wins = []
    for k_, wx in enumerate((x0 + 40 * S, x0 + 170 * S)):
        if k_ == 0 or rnd.random() < 0.85:
            ww, wh = 70 * S, 60 * S
            wy = floor - bh + 30 * S
            d.rectangle([wx, wy, wx + ww, wy + wh], fill=(255, 196, 110, 255))
            d.line([(wx + ww / 2, wy), (wx + ww / 2, wy + wh)], fill=color, width=int(4 * S))
            d.line([(wx, wy + wh / 2), (wx + ww, wy + wh / 2)], fill=color, width=int(4 * S))
            wins.append((wx / 2, wy / 2, ww / 2, wh / 2))
    return down(img), wins


# ---------------------------------------------------------------- glow sprites
def glow_sprite(r, color, power=2.0):
    s = int(r * 2)
    yy, xx = np.mgrid[0:s, 0:s]
    d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
    a = np.clip(1 - d, 0, 1) ** power
    return (a[..., None] * np.array(color)[None, None, :]).astype(np.float32)


def add_glow(arr, spr, cx, cy, k=1.0):
    h, w = spr.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(arr.shape[1], x0 + w), min(arr.shape[0], y0 + h)
    if xa >= xb or ya >= yb:
        return
    arr[ya:yb, xa:xb] += spr[ya - y0:yb - y0, xa - x0:xb - x0] * k


# ---------------------------------------------------------------- characters
def amir(phase=0.0, walking=True, facing=1, squash=1.0, color=(12, 12, 24, 255), lantern=True, rim=(78, 88, 140), scale=1.0):
    """Young man silhouette. Returns (img 1x, feet anchor (x,y), lantern pos (x,y) relative to img)."""
    cw, ch = 300, 480
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 150
    amp = float(walking)
    bob = -8 * abs(math.cos(phase)) * amp
    hip = (cx, 272 + bob)
    sw = math.sin(phase) * amp

    def limb(p, a1, l1, a2, l2, wd):
        k = (p[0] + math.sin(a1) * l1, p[1] + math.cos(a1) * l1)
        e = (k[0] + math.sin(a2) * l2, k[1] + math.cos(a2) * l2)
        d.line([p, k], fill=color, width=wd); d.line([k, e], fill=color, width=wd)
        for q in (p, k):
            d.ellipse([q[0] - wd / 2, q[1] - wd / 2, q[0] + wd / 2, q[1] + wd / 2], fill=color)
        return e

    # legs
    for s in (1, -1):
        a = 0.45 * sw * s
        bend = 0.5 * max(0, -math.sin(phase + (0 if s > 0 else math.pi))) * amp
        e = limb(hip, a, 98, a - bend, 98, 28)
        d.polygon([(e[0] - 12, e[1] + 4), (e[0] + 28, e[1] + 4), (e[0] + 22, e[1] - 10), (e[0] - 10, e[1] - 12)], fill=color)
    # torso
    sh = (cx + 8, 140 + bob)
    d.polygon([(hip[0] - 24, hip[1] + 6), (hip[0] + 24, hip[1] + 6), (sh[0] + 32, sh[1]), (sh[0] - 30, sh[1])], fill=color)
    d.ellipse([sh[0] - 32, sh[1] - 12, sh[0] + 34, sh[1] + 22], fill=color)
    # head + hair
    hd = (sh[0] + 6, sh[1] - 50)
    d.ellipse([hd[0] - 28, hd[1] - 32, hd[0] + 28, hd[1] + 30], fill=color)
    d.ellipse([hd[0] + 18, hd[1] - 4, hd[0] + 34, hd[1] + 12], fill=color)  # nose
    d.rectangle([hd[0] - 10, hd[1] + 20, hd[0] + 12, sh[1]], fill=color)
    d.polygon([(hd[0] - 30, hd[1] - 10), (hd[0] - 6, hd[1] - 40), (hd[0] + 26, hd[1] - 30), (hd[0] + 8, hd[1] - 22)], fill=color)
    # back arm swings
    limb((sh[0] - 6, sh[1] + 6), -0.4 * sw, 80, -0.4 * sw - 0.3, 76, 22)
    # lantern arm (forward, bent)
    hand = limb((sh[0] + 6, sh[1] + 6), 0.35 + 0.06 * sw, 80, -0.25, 64, 22)
    lpos = None
    if lantern:
        lx, ly = hand[0], hand[1] + 10
        d.line([(hand[0], hand[1]), (lx, ly)], fill=color, width=4)
        d.polygon([(lx - 12, ly), (lx + 12, ly), (lx + 15, ly + 34), (lx - 15, ly + 34)], fill=color)
        d.rectangle([lx - 9, ly + 6, lx + 9, ly + 28], fill=(255, 190, 90, 255))
        lpos = (lx, ly + 18)
    if rim:
        A = np.array(img.split()[3]).astype(np.int16)
        sh_ = np.zeros_like(A); sh_[3:, :-5] = A[:-3, 5:]
        edge = np.clip(A - sh_, 0, 255).astype(np.uint8)
        arr = np.array(img)
        lamp = (arr[..., 0] > 200)
        m = (edge > 0) & ~lamp
        arr[m, 0], arr[m, 1], arr[m, 2] = rim[0], rim[1], rim[2]
        img = Image.fromarray(arr)
    if facing < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        if lpos: lpos = (cw - lpos[0], lpos[1])
    if squash != 1.0:
        nw = max(2, int(cw * abs(squash)))
        img2 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        img2.paste(img.resize((nw, ch), Image.BILINEAR), ((cw - nw) // 2, 0))
        img = img2
        if lpos: lpos = (cw / 2 + (lpos[0] - cw / 2) * abs(squash), lpos[1])
    k = scale / 2
    img = img.resize((int(cw * k), int(ch * k)), Image.LANCZOS)
    feet = (cw * k / 2, (ch - 40) * k)
    return img, feet, (lpos[0] * k, lpos[1] * k) if lpos else None


def ghost(t, scale=1.0):
    """Woman in white, long hair over face. Returns RGBA 1x image (with glow) anchored center-top."""
    S = 2 * scale
    cw, ch = int(360 * S), int(800 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    white = (232, 235, 242, 255)
    skin = (214, 218, 226, 255)
    hair = (6, 6, 10, 255)
    top = 60 * S
    # dress
    pts = []
    for i in range(21):
        y = top + 110 * S + i / 20 * 560 * S
        wv = (50 + 90 * (i / 20) ** 1.2) * S + 6 * S * math.sin(t * 2 + i * .5)
        pts.append((cx + wv, y))
    hem = []
    for i in range(41):
        x = cx + (140 - 280 * i / 40) * S
        hem.append((x, top + 670 * S + 20 * S * math.sin(i * 0.9 + t * 3.2) + 10 * S * math.sin(i * 2.3 - t * 2)))
    left = [(2 * cx - p[0] + 4 * S * math.sin(t * 2.3 + k), p[1]) for k, p in enumerate(pts)]
    d.polygon(pts + hem + left[::-1], fill=white)
    for k in range(5):
        fx = cx + (-60 + 30 * k) * S
        d.line([(fx, top + 260 * S), (fx * 1.0 + (k - 2) * 18 * S + 5 * S * math.sin(t * 2 + k), top + 650 * S)],
               fill=(205, 210, 222, 255), width=int(3 * S))
    # head
    d.ellipse([cx - 40 * S, top, cx + 40 * S, top + 104 * S], fill=skin)
    # arms (outside the hair)
    for s in (1, -1):
        sx, sy = cx + s * 50 * S, top + 132 * S
        ex = sx + s * (30 * S + 4 * S * math.sin(t * 1.5 + s))
        ey = top + 450 * S
        d.line([(sx, sy), (ex, ey)], fill=skin, width=int(16 * S))
        d.ellipse([sx - 10 * S, sy - 10 * S, sx + 10 * S, sy + 10 * S], fill=white)
        for f_ in range(4):
            d.line([(ex, ey), (ex + s * (f_ - 1.5) * 5 * S, ey + (44 + 7 * f_) * S)], fill=skin, width=int(4 * S))
    # hair: cap + curtain over the face + strands
    d.ellipse([cx - 47 * S, top - 10 * S, cx + 47 * S, top + 86 * S], fill=hair)
    L_, R_ = [], []
    n = 26
    for i in range(n + 1):
        u = i / n
        y = top + 30 * S + u * 360 * S
        sway = 7 * S * math.sin(t * 1.3 + u * 3) * u
        wv = (44 - 14 * u + 3 * math.sin(u * 9 + t)) * S
        L_.append((cx - wv + sway, y)); R_.append((cx + wv + sway, y))
    bottom = []
    for k in range(13):
        u = k / 12
        x = R_[-1][0] + (L_[-1][0] - R_[-1][0]) * u
        y = L_[-1][1] + (40 * S if k % 2 else 0) + 10 * S * math.sin(t * 2 + k)
        bottom.append((x, y))
    d.polygon(L_ + bottom[::-1][::-1] if False else L_ + bottom[::-1] + R_[::-1], fill=hair)
    # side locks over shoulders
    for s in (1, -1):
        for j in range(3):
            pts = [(cx + s * (36 + 5 * j) * S + s * 6 * S * math.sin(t * 1.2 + v * 4 + j) * v,
                    top + 50 * S + v * (250 + 30 * j) * S) for v in np.linspace(0, 1, 14)]
            d.line(pts, fill=hair, width=int(7 * S))
    # long loose strands
    for k in range(10):
        x0 = cx + (-34 + 7.5 * k) * S
        pts = [(x0 + 9 * S * math.sin(t * 1.4 + k + v * 4) * v, top + 330 * S + v * (90 + 12 * (k % 3)) * S)
               for v in np.linspace(0, 1, 10)]
        d.line(pts, fill=hair, width=int(4 * S))
    # strand texture
    for k in range(7):
        x0 = cx + (-30 + 10 * k) * S
        pts = [(x0 + 4 * S * math.sin(v * 6 + k + t), top + 20 * S + v * 340 * S) for v in np.linspace(0, 1, 12)]
        d.line(pts, fill=(26, 26, 36, 255), width=int(2 * S))
    # thin pale gap in the hair (a glimpse of face)
    d.line([(cx + 7 * S, top + 46 * S), (cx + 9 * S, top + 92 * S)], fill=(190, 194, 205, 255), width=int(3 * S))
    im = down(img)
    # glow
    a = im.split()[3].filter(ImageFilter.GaussianBlur(18 * scale))
    g = Image.new("RGBA", im.size, (170, 200, 255, 0)); g.putalpha(a.point(lambda v: int(v * 0.75)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g); out.alpha_composite(im)
    return out


def frangipani(size=30):
    S = 4
    c = size * S
    img = Image.new("RGBA", (c, c), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for k in range(5):
        a = k * 2 * math.pi / 5
        pts = []
        for i in range(25):
            u = i / 24 * math.pi
            r = c * 0.48 * math.sin(u) ** 0.8
            ang = a + (u - math.pi / 2) * 0.45 + 0.25 * math.sin(u)
            pts.append((c / 2 + math.cos(ang) * r, c / 2 + math.sin(ang) * r))
        d.polygon(pts, fill=(248, 246, 238, 255))
    yy, xx = np.mgrid[0:c, 0:c]
    arr = np.array(img).astype(np.float32)
    dd = np.sqrt((xx - c / 2) ** 2 + (yy - c / 2) ** 2) / (c * 0.3)
    y = np.clip(1 - dd, 0, 1)[..., None]
    arr[..., :3] = arr[..., :3] * (1 - y) + np.array([250, 200, 80]) * y
    return down(Image.fromarray(arr.astype(np.uint8)), S)


# ---------------------------------------------------------------- particles
class Petals:
    def __init__(self, n, seed=0, sizes=(14, 18, 24), area=(0, W, -50, H)):
        rnd = random.Random(seed)
        self.sprites = {}
        for s in sizes:
            base = frangipani(s)
            self.sprites[s] = [base.rotate(a, Image.BICUBIC, expand=True) for a in range(0, 360, 12)]
        self.p = [dict(x=rnd.uniform(area[0], area[1]), y=rnd.uniform(area[2], area[3]), s=rnd.choice(sizes),
                       vy=rnd.uniform(18, 40), sw=rnd.uniform(20, 50), ph=rnd.uniform(0, 6.28),
                       rot=rnd.uniform(0, 360), vr=rnd.uniform(-60, 60)) for _ in range(n)]

    def draw(self, img, t, alpha=1.0, wind=10):
        if alpha <= 0.01:
            return
        for q in self.p:
            y = (q["y"] + q["vy"] * t) % (H + 80) - 40
            x = (q["x"] + wind * t + q["sw"] * math.sin(t * 0.9 + q["ph"])) % (W + 60) - 30
            rot = int(((q["rot"] + q["vr"] * t) % 360) / 12) % 30
            sp = self.sprites[q["s"]][rot]
            if alpha < 1:
                sp = sp.copy(); sp.putalpha(sp.split()[3].point(lambda v: int(v * alpha)))
            img.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))


class Fireflies:
    def __init__(self, n, seed=0, area=(0, W, 250, 650)):
        rnd = random.Random(seed)
        self.spr = glow_sprite(14, (190, 255, 120), 2.2)
        self.p = [dict(x=rnd.uniform(*area[:2]), y=rnd.uniform(*area[2:]), a=rnd.uniform(.3, .9), b=rnd.uniform(.3, .9),
                       ph=rnd.uniform(0, 6.28), f=rnd.uniform(.6, 1.6)) for _ in range(n)]

    def draw(self, arr, t, k=1.0, dx=0):
        if k <= 0.01:
            return
        for q in self.p:
            x = q["x"] + 40 * math.sin(t * q["a"] + q["ph"]) - dx
            y = q["y"] + 25 * math.sin(t * q["b"] + q["ph"] * 2)
            br = (0.5 + 0.5 * math.sin(t * q["f"] * 3 + q["ph"])) ** 2
            add_glow(arr, self.spr, x % W, y, br * k)


def fog_texture(w, h, seed=0):
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    for sc, amp in ((64, 1.0), (24, 0.5), (10, 0.25)):
        small = rng.random((h // sc + 2, w // sc + 2)).astype(np.float32)
        im = Image.fromarray((small * 255).astype(np.uint8)).resize((w + 2 * sc, h + 2 * sc), Image.BICUBIC)
        acc += np.array(im)[:h, :w].astype(np.float32) / 255 * amp
    acc /= acc.max()
    return np.clip((acc - 0.35) * 1.8, 0, 1)


# ---------------------------------------------------------------- post
def vignette(strength=0.75, w=W, h=H):
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    return (1 - strength * np.clip(d - 0.45, 0, 1) ** 1.4).astype(np.float32)[..., None]


def grain_frames(n=8, amt=7, seed=0):
    rng = np.random.default_rng(seed)
    return [rng.normal(0, amt, (H, W, 1)).astype(np.float32) for _ in range(n)]


def zoom(img, z, cx=W / 2, cy=H / 2):
    if abs(z - 1) < 1e-4:
        return img
    cw, ch = W / z, H / z
    x0 = min(max(cx - cw / 2, 0), W - cw)
    y0 = min(max(cy - ch / 2, 0), H - ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


def wrap(text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if f.getlength(trial) <= maxw:
            cur = trial
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    return lines


_cap_cache = {}


def caption_img(text):
    if text in _cap_cache:
        return _cap_cache[text]
    f = font(INTER_SB, 50)
    lines = wrap(text, f, 860)
    lh = 64
    tw = max(f.getlength(l) for l in lines)
    bw, bh = int(tw + 44), int(lh * len(lines) + 24)
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, bw - 1, bh - 1], 22, fill=(0, 0, 0, 165))
    for i, l in enumerate(lines):
        d.text((bw / 2, 12 + lh * i + lh / 2), l, font=f, fill=(250, 248, 240, 255), anchor="mm")
    _cap_cache[text] = img
    return img


def text_img(text, f, fill=(240, 236, 225, 255), spacing=0, glow=None, pad=40):
    tw = int(f.getlength(text) + spacing * len(text)) + 2 * pad
    asc, desc = f.getmetrics()
    th = asc + desc + 2 * pad
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if spacing:
        x = pad
        for ch_ in text:
            d.text((x, pad), ch_, font=f, fill=fill)
            x += f.getlength(ch_) + spacing
    else:
        d.text((pad, pad), text, font=f, fill=fill)
    if glow:
        a = img.split()[3].filter(ImageFilter.GaussianBlur(14))
        g = Image.new("RGBA", img.size, glow[:3] + (0,)); g.putalpha(a.point(lambda v: int(v * glow[3] / 255)))
        out = Image.new("RGBA", img.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(img)
        return out
    return img


def with_alpha(img, a):
    if a >= 0.999:
        return img
    im = img.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * max(0, a))))
    return im


def ease(x):
    x = min(1, max(0, x))
    return x * x * (3 - 2 * x)
