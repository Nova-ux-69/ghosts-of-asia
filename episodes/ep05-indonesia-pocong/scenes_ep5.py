"""Episode 5: Pocong (Indonesia), vertical scenes.
New world for this episode: a Javanese village under a monsoon storm (rice terraces, joglo roofs, a mosque dome,
bamboo groves, a yellow funeral flag), an old graveyard of white nisan headstones under gnarled frangipani trees,
a wooden house lit by a pelita lamp, a soft morning after the rain, and a kawung-batik explainer.
Camera: crane-down through rain, a long dusk pan, a side-tracking run with a torch beam, thump push-ins with
lightning, a face-to-camera two-shot, a feet-to-head tilt, a macro on the knot, a morning crane-up."""
import sys, os, math, random
_EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _EP); sys.path.insert(1, os.path.join(_EP, "..", "..", "toolkit"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *
from art_ep5 import *
from scenes_v import (GY, VIG, VIG_HEAVY, GRAIN, GRAIN_HEAVY, GOLD, CREAM, arr_of, fog_layer, post,
                      compose, centered, pill, series_header, header_layers, card)

MIST = (120, 130, 150)
COLD = (0.94, 0.98, 1.06)
EARTH = (14, 14, 16, 255)


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def zmap(x, y, z, cx, cy):
    cw, ch = W / z, H / z
    x0 = min(max(cx - cw / 2, 0), W - cw)
    y0 = min(max(cy - ch / 2, 0), H - ch)
    return (x - x0) * z, (y - y0) * z


def shake_img(img, t, amp, seed=1):
    if amp < 0.5:
        return img
    r = random.Random(int(t * FPS) + seed)
    return img.transform(img.size, Image.AFFINE, (1, 0, r.uniform(-1, 1) * amp, 0, 1, r.uniform(-1, 1) * amp),
                         resample=Image.BILINEAR)


def place(img, im, x, feet_y):
    img.alpha_composite(im, (int(x - im.width / 2), int(feet_y - im.height)))


_PC = {}


def poc(t, scale, **kw):
    """Cached pocong (quantised so repeated poses are reused)."""
    key = (round(t * 4) / 4, round(scale, 3)) + tuple(sorted((k, round(v, 2) if isinstance(v, float) else v) for k, v in kw.items()))
    if key not in _PC:
        if len(_PC) > 400:
            _PC.clear()
        _PC[key] = pocong(key[0], key[1], **kw)
    return _PC[key]


def hop_y(t, t0, per=0.62, hgt=60):
    """Vertical hop offset (negative = up) for hops starting at t0, plus a squash factor."""
    if t < t0:
        return 0.0, 1.0
    u = ((t - t0) % per) / per
    return -hgt * math.sin(math.pi * u), 1.0 - 0.06 * max(0, math.cos(math.pi * u)) ** 8


def squash(im, k):
    if abs(k - 1) < 0.005:
        return im
    return im.resize((int(im.width * (2 - k)), int(im.height * k)), Image.BILINEAR)


class Flash:
    """Lightning: list of (time, strength). value(t) is a quick double flicker."""
    def __init__(self, times):
        self.times = times

    def value(self, t):
        v = 0.0
        for t0, s in self.times:
            dt = t - t0
            if 0 <= dt < 0.5:
                v = max(v, s * (math.exp(-dt * 14) + 0.6 * math.exp(-((dt - 0.18) / 0.05) ** 2)))
        return v


def apply_flash(arr, fl):
    if fl > 0.01:
        arr *= 1 + 0.9 * fl
        arr += np.array([30, 36, 60], np.float32) * fl
    return arr


def ground_strip(w, y0=GY, color=EARTH, seed=3, grass=(20, 22, 22, 255)):
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y0, w, H], fill=color)
    rnd = random.Random(seed)
    for _ in range(w // 7):
        x = rnd.uniform(0, w); hh = rnd.uniform(8, 30)
        d.line([(x, y0 + 6), (x + rnd.uniform(-8, 8), y0 - hh)], fill=grass, width=3)
    return img


def graveyard(sw, seed, top=STORM_TOP, bot=STORM_BOT, trees=(), graves_back=(), graves_front=(), moon=None,
              far_col=SLATE_FAR, mid_col=SLATE_MID, cloud_col=(30, 34, 48), tree_col=SILH, stone=STONE, flowers=True):
    """Layered graveyard strip. trees: (x, scale). graves_*: (x, scale). Returns (far, mid, front)."""
    fw = int(W + sw * 0.3) + 10
    far = storm_sky(top, bot, w=fw, seed=seed, moon=moon, cloud_col=cloud_col)
    far.alpha_composite(treeline(fw, GY - 160, 90, far_col, seed=seed))
    mid = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    mid.alpha_composite(treeline(sw, GY - 40, 40, mid_col, seed=seed + 1))
    mid.alpha_composite(ground_strip(sw, GY - 30, seed=seed))
    rnd = random.Random(seed)
    for x, sc in graves_back:
        g = grave(sc, seed=int(x), color=stone)
        mid.alpha_composite(g, (int(x - g.width / 2), int(GY - 10 - g.height)))
    for x, sc in trees:
        ft, _ = frangipani_tree(sc, seed=int(x) % 97, color=tree_col, flowers=flowers)
        mid.alpha_composite(ft, (int(x - ft.width / 2), int(GY + 10 - ft.height)))
    front = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    front.alpha_composite(ground_strip(sw, GY + 40, color=(10, 10, 12, 255), seed=seed + 5))
    for x, sc in graves_front:
        g = grave(sc, seed=int(x) + 3, color=stone)
        front.alpha_composite(g, (int(x - g.width / 2), int(GY + 90 - g.height)))
    return far, mid, front


def view(far, *layers, cam=0.0):
    fx = int(cam * 0.3)
    img = far.crop((fx, 0, fx + W, H))
    for L in layers:
        img.alpha_composite(L.crop((int(cam), 0, int(cam) + W, H)))
    return img


def bayu_on(img, x, feet_y, **kw):
    b, feet, tip = bayu(**kw)
    ox, oy = int(x - feet[0]), int(feet_y - feet[1])
    img.alpha_composite(b, (ox, oy))
    return ox + tip[0], oy + tip[1]


def bayu_front(scale=1.0, light=1.0, look=0.0, eyes=1.0):
    """Bayu facing the camera, chest-up: peci cap, collar, torch held low so his face is lit from below.
    look -1..1 moves the eyes sideways. Returns RGBA (canvas 600x700 * scale)."""
    S = 2 * scale
    cw, ch = int(600 * S), int(700 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    body = (16, 18, 24, 255)
    d.rounded_rectangle([cx - 230 * S, 470 * S, cx + 230 * S, ch + 60 * S], 120 * S, fill=body)       # shoulders
    d.polygon([(cx - 60 * S, 470 * S), (cx, 560 * S), (cx + 60 * S, 470 * S)], fill=(40, 40, 46, 255))  # collar
    d.rectangle([cx - 46 * S, 380 * S, cx + 46 * S, 490 * S], fill=(120, 80, 52, 255))               # neck
    skin = tuple(int(v * (0.5 + 0.5 * light)) for v in (196, 140, 96)) + (255,)
    d.ellipse([cx - 130 * S, 150 * S, cx + 130 * S, 440 * S], fill=skin)                             # face
    for s_ in (-1, 1):
        d.ellipse([cx + s_ * 136 * S - 22 * S, 270 * S, cx + s_ * 136 * S + 22 * S, 330 * S], fill=skin)  # ears
    d.polygon([(cx - 140 * S, 200 * S), (cx + 140 * S, 200 * S), (cx + 128 * S, 60 * S), (cx - 128 * S, 60 * S)], fill=(10, 10, 12, 255))  # peci
    d.line([(cx - 128 * S, 196 * S), (cx + 128 * S, 196 * S)], fill=(40, 40, 44, 255), width=int(4 * S))
    if eyes > 0:
        for s_ in (-1, 1):
            ex = cx + s_ * 52 * S
            d.ellipse([ex - 30 * S, 262 * S - 22 * S * eyes, ex + 30 * S, 262 * S + 22 * S * eyes], fill=(246, 244, 236, 255))
            d.ellipse([ex + look * 14 * S - 11 * S, 251 * S, ex + look * 14 * S + 11 * S, 273 * S], fill=(20, 14, 10, 255))
            d.line([(ex - 34 * S, 214 * S - 8 * S * eyes), (ex + 30 * S, 208 * S - 12 * S * eyes)], fill=(30, 20, 14, 255), width=int(8 * S))
    d.ellipse([cx - 20 * S, 360 * S, cx + 20 * S, 392 * S], fill=(60, 30, 24, 255))                 # small "o" mouth
    im = down(img)
    # under-lighting from the torch: warm at the chin, dark at the top
    a = np.array(im).astype(np.float32)
    yy = np.linspace(0, 1, im.height)[:, None]
    g = 0.55 + 0.6 * np.clip((yy - 0.2) / 0.5, 0, 1) * light
    a[..., :3] *= g[..., None] * np.array([1.08, 0.98, 0.86])
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def digger(scale=1.0, color=(30, 24, 20, 255), rim=(255, 220, 170)):
    """The gravedigger: an old man in a caping (cone hat) leaning on a cangkul hoe. Faces left. Anchor bottom centre."""
    cw, ch = 360, 560
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 190
    for s_ in (-1, 1):
        d.line([(cx + s_ * 16, 330), (cx + s_ * 24, 520)], fill=color, width=26)
    d.polygon([(cx - 46, 340), (cx + 46, 340), (cx + 40, 170), (cx - 36, 170)], fill=color)
    d.ellipse([cx - 44, 150, cx + 44, 210], fill=color)
    d.ellipse([cx - 30, 90, cx + 22, 150], fill=color)
    d.polygon([(cx - 100, 112), (cx + 80, 112), (cx - 10, 56)], fill=color)                    # caping
    d.line([(cx - 20, 200), (cx - 80, 260), (cx - 96, 230)], fill=color, width=18)             # arm on the handle
    d.line([(cx - 96, 120), (cx - 110, 520)], fill=color, width=10)                            # hoe handle
    d.polygon([(cx - 140, 500), (cx - 80, 500), (cx - 86, 540), (cx - 134, 540)], fill=color)   # blade
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    from art_ep5 import _rim
    img = _rim(img, rim)
    img = img.resize((int(cw * scale), int(ch * scale)), Image.LANCZOS)
    return img


TGLOW = glow_sprite(130, TORCH, 1.8)
WGLOW = glow_sprite(110, PELITA, 2.0)
RAIN = Rain(240, seed=1)
RAIN2 = Rain(140, seed=7, speed=1500, length=34, color=(140, 150, 180))


# ======================================================================= P1
def make_hook(D, caps):
    far, mid, front = graveyard(W, 5, trees=((150, 1.05), (930, 0.95)), graves_back=((420, 0.42), (680, 0.46), (560, 0.36)),
                                graves_front=((260, 0.85), (880, 0.8)))
    hdr = series_header("INDONESIA", "PART 1")
    t2 = caps[1][1]
    fl = Flash([(0.15, 0.7), (t2 - 0.05, 1.0), (D - 2.2, 0.5)])
    bolt = lightning_bolt(760, 4)
    pet = Petals2(14, seed=3)
    hops = [caps[0][1] + 2.2 + 0.62 * k for k in range(12)]

    def f(t):
        img = far.crop((0, 0, W, H))
        if fl.value(t) > 0.2:
            img.alpha_composite(bolt, (640, 120))
        img.alpha_composite(mid)
        # far away between the trees, something white hops closer with every thump
        n = sum(1 for h in hops if h <= t)
        k = min(1, n / 9 + (ease((t - t2) / 1.2) * 0.25))
        sc = 0.22 + 0.2 * k
        x = 560 + 30 * math.sin(n * 1.7) * (1 - k)
        hy, sq = hop_y(t, hops[0])
        p = squash(poc(t, sc, eyes=ease((t - t2) / 0.5), glow=0.8), sq)
        img.alpha_composite(p, (int(x - p.width / 2), int(GY - 20 + 26 * k + hy * sc - p.height)))
        img.alpha_composite(front)
        pet.draw(img, t, 0.8)
        img.alpha_composite(RAIN2.layer(t, 0.6))
        z = 1.12 - 0.06 * t / D + 0.2 * ease((t - t2) / 2.2)
        cy = 820 + 200 * ease(t / 3.0)
        img = zoom(img, z, 560, cy)
        arr = arr_of(img)
        fog_layer(arr, t, k=0.3, color=MIST, y0=0.42)
        apply_flash(arr, fl.value(t))
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, vig=VIG_HEAVY, tint=COLD)
    return f


def make_village(D, caps):
    sw = 2500
    top, bot = (40, 44, 58), (168, 150, 104)          # sickly yellow storm dusk
    fw = int(W + sw * 0.3) + 10
    far = storm_sky(top, bot, w=fw, seed=12, cloud_col=(54, 54, 64))
    far.alpha_composite(treeline(fw, GY - 330, 70, (60, 60, 64, 255), seed=12))
    mid = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    mid.alpha_composite(treeline(sw, GY - 250, 60, (34, 34, 40, 255), seed=13))
    houses = []
    for hx, hs in ((300, 0.7), (980, 0.85), (2150, 0.75)):
        j, g = joglo(hs, seed=hx, color=(20, 20, 24, 255))
        ox, oy = int(hx - j.width / 2), int(GY - 230 - j.height)
        mid.alpha_composite(j, (ox, oy)); houses += [(ox + a, oy + b) for a, b in g]
    m = mosque(0.62, color=(22, 22, 28, 255))
    mid.alpha_composite(m, (int(1560 - m.width / 2), int(GY - 226 - m.height)))
    mid.alpha_composite(rice_terraces(sw, GY - 232, GY + 60, sky_col_top=(150, 136, 96), sky_col_bot=(70, 66, 60), seed=4, dark=(18, 18, 16)))
    front = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    front.alpha_composite(ground_strip(sw, GY + 60, color=(12, 12, 12, 255), seed=7))
    ft, _ = frangipani_tree(0.9, seed=21, color=(10, 10, 12, 255))
    front.alpha_composite(ft, (int(2300 - ft.width / 2), int(GY + 70 - ft.height)))
    span = sw - W
    t2 = caps[1][1]
    fl = Flash([(3.0, 0.35), (t2 + 1.2, 0.45)])
    bolt = lightning_bolt(500, 9)

    def f(t):
        cam = span * ease(t / D * 0.95 + 0.02)
        img = far.crop((int(cam * 0.3), 0, int(cam * 0.3) + W, H))
        if fl.value(t) > 0.15:
            img.alpha_composite(bolt, (520, 160))
        img.alpha_composite(mid.crop((int(cam), 0, int(cam) + W, H)))
        fr = front.crop((int(cam), 0, int(cam) + W, H))
        img.alpha_composite(fr)
        flag = bamboo_pole_flag(1.0, t)
        place(img, flag, 1980 - cam + 60, GY + 80)
        bayu_on(img, 260 + (1500 - 260) * ease(t / D) - cam * 0.55, GY + 64, phase=t * 2 * math.pi * 0.9, walking=True,
                facing=1, scale=1.7, rim=(255, 210, 140))
        arr = arr_of(img)
        for gx, gy in houses:
            add_glow(arr, WGLOW, gx - cam, gy, 0.5)
        fog_layer(arr, t, k=0.2, color=(150, 140, 110), y0=0.4)
        apply_flash(arr, fl.value(t))
        return post(arr, t, tint=(1.04, 1.0, 0.92))
    return f


def wood_room(warm=1.0, seed=0):
    """Inside a Javanese wooden house: vertical teak planks, a carved gebyok panel, a batik cloth on the wall,
    a rain-streaked window, a woven floor mat."""
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([34, 22, 14]) * warm + np.array([12, 14, 22]) * (1 - warm)
    bot = np.array([78, 50, 28]) * warm + np.array([20, 24, 32]) * (1 - warm)
    base = Image.fromarray(np.repeat(top * (1 - y) + bot * y, W, axis=1).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(base)
    plank = tuple(int(v) for v in (np.array([58, 36, 20]) * warm + np.array([18, 22, 30]) * (1 - warm)))
    for x in range(0, W, 90):
        d.line([(x, 200), (x, 1150)], fill=plank + (255,), width=4)
    # carved gebyok panel (right): rectangles with lattice
    gx0, gx1 = 700, 1040
    d.rectangle([gx0, 330, gx1, 1150], fill=tuple(max(0, v - 10) for v in plank) + (255,))
    for k in range(3):
        y0 = 360 + k * 260
        d.rectangle([gx0 + 20, y0, gx1 - 20, y0 + 220], outline=tuple(min(255, v + 30) for v in plank) + (255,), width=5)
        for j in range(6):
            d.arc([gx0 + 40 + j * 48, y0 + 60, gx0 + 100 + j * 48, y0 + 160], 0, 360, fill=tuple(min(255, v + 18) for v in plank) + (255,), width=3)
    # window with rain outside (left)
    d.rectangle([80, 380, 480, 860], fill=(26, 32, 44, 255))
    d.rectangle([80, 380, 480, 860], outline=(20, 12, 8, 255), width=22)
    d.line([(280, 380), (280, 860)], fill=(20, 12, 8, 255), width=14)
    rnd = random.Random(seed)
    for _ in range(40):
        x, yy = rnd.uniform(100, 460), rnd.uniform(400, 840)
        d.line([(x, yy), (x - 4, yy + rnd.uniform(16, 40))], fill=(110, 124, 150, 200), width=2)
    # batik cloth (parang diagonal stripes) hanging under the window
    bx0, by0, bx1, by1 = 120, 900, 440, 1100
    d.rectangle([bx0, by0, bx1, by1], fill=(70, 40, 20, 255))
    for k in range(-10, 20):
        x = bx0 + k * 30
        d.line([(x, by1), (x + 200, by0)], fill=(140, 96, 50, 255), width=8)
        d.line([(x + 12, by1), (x + 212, by0)], fill=(40, 22, 12, 255), width=3)
    d.rectangle([bx0, by0, bx1, by1], outline=(30, 16, 8, 255), width=6)
    d.rectangle([0, 1150, W, H], fill=tuple(int(v) for v in (np.array([100, 76, 44]) * warm + np.array([24, 28, 36]) * (1 - warm))) + (255,))
    for x in range(-400, W + 400, 36):
        d.line([(x, 1150), (x + 300, H)], fill=(80, 58, 32, 255), width=3)
    return base


def make_warn(D, caps):
    base = wood_room(1.0, seed=2)
    pl, fp = pelita(1.2, 1.0)
    PX, PY = 560, 330
    base.alpha_composite(pl, (PX, PY))
    lt1 = text_img("AFTER A FUNERAL...", font(LORA, 66, "Bold"), fill=CREAM, glow=(170, 90, 10, 230), pad=20)
    lt2 = text_img("NEVER TAKE THE SHORTCUT.", font(LORA, 62, "Bold"), fill=CREAM, glow=(170, 90, 10, 230), pad=20)
    ta = caps[1][1] + 0.1
    tb = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.45
    lamp_g = glow_sprite(420, PELITA, 1.5)
    fl = Flash([(caps[1][2] - 0.4, 0.4)])

    def f(t):
        img = base.copy()
        fi = ease((t - caps[0][1] - 0.6) / 0.8)
        e, ef = eyang(scale=1.6, finger=fi)
        img.alpha_composite(e, (int(380 - ef[0]), int(1180 - ef[1])))
        bayu_on(img, 820, 1200, walking=False, facing=-1, scale=2.4, rim=(255, 190, 110))
        z = 1.06 + 0.1 * ease(t / D)
        cx, cy = 520 - 60 * ease(t / D), 760
        img = zoom(img, z, cx, cy)
        arr = arr_of(img)
        lx, ly = zmap(PX + fp[0], PY + fp[1], z, cx, cy)
        add_glow(arr, lamp_g, lx, ly, 0.5 * (0.9 + 0.1 * math.sin(t * 11)))
        apply_flash(arr, 0.4 * fl.value(t))
        arr = compose(arr, [centered(lt1, 170, ease((t - ta) / 0.4)), centered(lt2, 290, ease((t - tb) / 0.4))])
        return post(arr, t, vig=VIG_HEAVY, tint=(1.06, 0.98, 0.9))
    return f


def gate(scale=1.0, color=(150, 152, 150, 255)):
    """Low whitewashed graveyard wall with a small gapura gate (stepped top). Anchor bottom centre."""
    S = 2 * scale
    cw, ch = int(1000 * S), int(420 * S)
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cw / 2
    d.rectangle([0, ch - 110 * S, cx - 150 * S, ch], fill=color)
    d.rectangle([cx + 150 * S, ch - 110 * S, cw, ch], fill=color)
    for s_ in (-1, 1):
        x = cx + s_ * 120 * S
        d.rectangle([x - 34 * S, ch - 300 * S, x + 34 * S, ch], fill=color)
        for k in range(3):
            w = (34 - k * 8) * S
            d.rectangle([x - w, ch - 300 * S - (k + 1) * 30 * S, x + w, ch - 300 * S - k * 30 * S], fill=color)
    sh = tuple(int(v * 0.6) for v in color[:3]) + (255,)
    for x in range(0, cw, int(60 * S)):
        d.line([(x, ch - 110 * S), (x, ch)], fill=sh, width=int(2 * S))
    return down(img)


def make_shortcut(D, caps):
    sw = 2600
    far, mid, front = graveyard(sw, 33, trees=((900, 0.9), (1450, 1.05), (2050, 0.95), (2500, 0.85)),
                                graves_back=((1100, 0.4), (1300, 0.36), (1700, 0.42), (1900, 0.38), (2300, 0.4)),
                                graves_front=((1250, 0.8), (1820, 0.85), (2400, 0.78)))
    gt = gate(0.8)
    mid.alpha_composite(gt, (int(620 - gt.width / 2), int(GY - 6 - gt.height)))
    t1 = caps[1][1]
    pet = Petals2(16, seed=5)
    fl = Flash([(caps[0][1] + 1.0, 0.55), (t1 + 2.5, 0.4)])

    def f(t):
        # first line: Bayu stops at the gate in the rain; second: he runs in, camera tracks right
        run = ease((t - t1 + 0.3) / (D - t1 + 0.3))
        cam = 1350 * run
        img = view(far, mid, cam=cam)
        bx = 380 + 220 * ease(t / max(0.5, t1 - 0.6)) + (1350 + 140) * run - cam
        moving = t < t1 - 0.6 or run > 0.02
        tip = bayu_on(img, bx, GY + 20, phase=t * 2 * math.pi * (1.4 if run > 0 else 0.9), walking=moving, run=run > 0,
                      facing=1, scale=1.7, rim=(170, 190, 230), torch=1.0)
        img.alpha_composite(front.crop((int(cam), 0, int(cam) + W, H)))
        pet.draw(img, t, 0.7)
        img.alpha_composite(RAIN.layer(t, ease((t - 0.5) / 2.0)))
        arr = arr_of(img)
        arr += beam((W, H), tip, -0.05 + 0.04 * math.sin(t * 7), 760, 0.2, k=0.9)
        add_glow(arr, TGLOW, tip[0], tip[1], 0.6)
        fog_layer(arr, t, k=0.28, color=MIST, y0=0.45)
        apply_flash(arr, fl.value(t))
        return post(arr, t, vig=VIG_HEAVY, tint=COLD)
    return f


def make_thump(D, caps):
    far, mid, front = graveyard(W, 41, trees=((120, 1.0), (860, 1.1)), graves_back=((360, 0.4), (620, 0.44)),
                                graves_front=((980, 0.9),))
    t0 = caps[1][1]
    tb = caps[1][2] - caps[1][1]
    thumps = [t0 + tb * k / 3 + 0.05 for k in range(3)]
    t2 = caps[2][1]
    fl = Flash([(t2 + 0.2, 1.0)])
    bolt = lightning_bolt(700, 13)

    def f(t):
        img = far.crop((0, 0, W, H))
        if fl.value(t) > 0.2:
            img.alpha_composite(bolt, (200, 80))
        img.alpha_composite(mid)
        # the pocong, behind Bayu (left), comes closer in three hops, then keeps hopping
        n = sum(1 for h in thumps if h <= t)
        stage = n + ease((t - t2) / 2.0)
        sc = 0.3 + 0.1 * stage
        x = 260 + 40 * stage
        hy = 0.0
        for h in thumps:
            if h <= t < h + 0.45:
                hy = -70 * math.sin(math.pi * (t - h) / 0.45)
        if t > t2:
            hy, _ = hop_y(t, t2, 0.7, 50)
        p = poc(t, sc, eyes=ease((t - t2 - 0.3) / 0.4), glow=0.9)
        img.alpha_composite(p, (int(x - p.width / 2), int(GY + 10 + 20 * stage + hy * sc * 1.5 - p.height)))
        # Bayu stops, the torch shaking
        tr = 1.5 * math.sin(t * 30) * ease((t - t0) / 0.3)
        tip = bayu_on(img, 760, GY + 70, walking=False, facing=1, scale=2.2, rim=(170, 190, 230), torch=1.0, tremble=tr)
        img.alpha_composite(front)
        img.alpha_composite(RAIN.layer(t, 0.8))
        z = 1.0 + 0.06 * t / D + sum(0.05 * ease((t - h) / 0.15) for h in thumps)
        img = zoom(img, z, 520, 900)
        amp = sum(9 * ease((t - h) / 0.05) * (1 - ease((t - h - 0.08) / 0.3)) for h in thumps)
        img = shake_img(img, t, amp)
        arr = arr_of(img)
        flick = 0.0 if any(h < t < h + 0.12 for h in thumps) else 1.0
        tx, ty = zmap(*tip, z, 520, 900)
        arr += beam((W, H), (tx, ty), 0.05, 700, 0.2, k=0.9 * flick)
        add_glow(arr, TGLOW, tx, ty, 0.6 * flick)
        fog_layer(arr, t, k=0.3, color=MIST, y0=0.45)
        apply_flash(arr, fl.value(t))
        return post(arr, t, vig=VIG_HEAVY, tint=COLD)
    return f


def make_cliff(D, caps):
    bg = storm_sky((4, 6, 10), (30, 36, 50), seed=55)
    bg.alpha_composite(treeline(W, GY - 260, 80, SLATE_FAR, seed=55))
    ft, _ = frangipani_tree(1.1, seed=8, color=(8, 9, 12, 255))
    bg.alpha_composite(ft, (int(820 - ft.width / 2), int(GY - 120 - ft.height)))
    t1, t2, t3 = caps[0][1], caps[1][1], caps[2][1]
    big_t = text_img("PART 2 IS UP NOW", font(LORA, 96, "Bold"), fill=CREAM, glow=(150, 170, 220, 255), pad=24)
    sub_t = text_img("Watch it next on our channel", font(INTER_M, 42), fill=(226, 232, 240, 255), pad=12)
    name_t = text_img("Bayu...", font(LORA, 70, "Italic"), fill=(220, 230, 255, 255), glow=(120, 150, 220, 255), pad=20)
    fl = Flash([(t2 + 0.3, 0.6)])
    face_g = glow_sprite(420, TORCH, 1.6)

    def f(t):
        img = bg.copy()
        # the Pocong rises out of the dark behind Bayu's shoulder (viewers see it; Bayu doesn't)
        u = ease((t - t1) / 3.2)
        p = poc(t, 0.95, eyes=ease((t - t1 - 1.2) / 0.6), glow=0.5 + 0.4 * u)
        px, py = 760, 1680 - 260 * u
        img.alpha_composite(with_alpha(p, 0.15 + 0.85 * u), (int(px - p.width / 2), int(py - p.height)))
        b = bayu_front(0.95, light=1.0, look=-0.6 + 1.2 * ease((t - t2) / 0.6), eyes=1.0 + 0.2 * ease((t - t2) / 0.4))
        img.alpha_composite(b, (int(400 - b.width / 2), int(1300 - b.height + 40)))
        z = 1.0 + 0.05 * t / D + 0.12 * ease((t - t2) / 2.0)
        img = zoom(img, z, 560, 900)
        arr = arr_of(img)
        add_glow(arr, face_g, *zmap(400, 1100, z, 560, 900), 0.35)
        fog_layer(arr, t, k=0.22, color=MIST, y0=0.5)
        apply_flash(arr, fl.value(t))
        a1 = ease((t - t3 + 0.2) / 0.5)
        arr = post(arr, t, vig=VIG_HEAVY, tint=COLD)
        na = ease((t - t2 - 0.4) / 0.6) * (1 - a1)
        if na > 0:
            arr = compose(arr, [(name_t, (640, 330 + 10 * math.sin(t * 2)), na * (0.7 + 0.3 * math.sin(t * 9)))])
        if a1 > 0:
            arr *= 1 - 0.45 * a1
            arr = compose(arr, [centered(big_t, 220, a1), centered(sub_t, 360, ease((t - t3 - 0.3) / 0.5))])
        return arr
    return f


# ======================================================================= P2
def make_recap(D, caps):
    far, mid, front = graveyard(W, 61, trees=((140, 1.0), (900, 0.9)), graves_back=((420, 0.4), (700, 0.42)),
                                graves_front=((200, 0.8),))
    hdr = series_header("INDONESIA", "PART 2")
    t1 = caps[1][1]

    def f(t):
        img = far.crop((0, 0, W, H))
        img.alpha_composite(mid)
        tip = bayu_on(img, 700, GY + 50, walking=False, facing=1, scale=1.7, rim=(170, 190, 230), torch=1.0)
        u = ease((t - t1 + 0.6) / 2.4)
        hy, sq = hop_y(t, t1 - 0.6, 0.66, 60)
        p = squash(poc(t, 0.26 + 0.12 * u, eyes=1.0, glow=0.9), sq)
        x = 260 + 260 * u
        img.alpha_composite(p, (int(x - p.width / 2), int(GY + 10 + 30 * u + hy * 0.4 - p.height)))
        img.alpha_composite(front)
        img.alpha_composite(RAIN.layer(t, 0.7))
        arr = arr_of(zoom(img, 1.04 + 0.05 * t / D, 540, 960))
        tx, ty = zmap(*tip, 1.04 + 0.05 * t / D, 540, 960)
        arr += beam((W, H), (tx, ty), 0.0, 600, 0.2, k=0.8)
        fog_layer(arr, t, k=0.26, color=MIST, y0=0.45)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, vig=VIG_HEAVY, tint=COLD)
    return f


def make_turn(D, caps):
    t0, t1, t2 = caps[0][1], caps[1][1], caps[2][1]
    bg = storm_sky((4, 6, 10), (34, 40, 56), seed=71)
    bg.alpha_composite(treeline(W, GY - 200, 80, SLATE_FAR, seed=71))
    bg.alpha_composite(ground_strip(W, GY + 200, seed=71))
    P = pocong(0.0, 1.6, eyes=0.0, glow=0.6)           # large, for the tilt (eyes added later)
    PE = pocong(0.0, 1.6, eyes=1.0, glow=0.6)
    PX, PB = 540, GY + 330
    knot_g = glow_sprite(140, (200, 220, 255), 1.6)
    fl = Flash([(t2, 0.8)])
    turn_end = t1 - 0.2

    def f(t):
        img = bg.copy()
        if t < turn_end:
            # Bayu (side view) slowly turns around, the torch swinging toward camera
            u = ease((t - t0) / (turn_end - t0))
            tip = bayu_on(img, 560, GY + 170, walking=False, facing=1 if u < 0.5 else -1, scale=3.2, rim=(170, 190, 230),
                          torch=1.0, look_back=u, tremble=1.2 * math.sin(t * 26))
            arr = arr_of(zoom(img, 1.05 + 0.08 * u, 560, 900))
            add_glow(arr, TGLOW, 560 + (-1 if u >= 0.5 else 1) * 180, 760, 0.6)
            fog_layer(arr, t, k=0.25, color=MIST, y0=0.45)
            return post(arr, t, vig=VIG_HEAVY, tint=COLD)
        # then: tilt from the tied feet up to the tied head
        p = PE if t > t2 - 0.1 else P
        img.alpha_composite(p, (int(PX - p.width / 2), int(PB - p.height)))
        img.alpha_composite(RAIN2.layer(t, 0.5))
        tl = ease((t - t1) / max(1.0, (t2 - t1)))
        z = 1.5 - 0.25 * ease((t - t2) / 2.0)
        cy = (PB - 80) + (PB - p.height + 330 - (PB - 80)) * tl
        img = zoom(img, z, 540, cy)
        arr = arr_of(img)
        fk = p.info["knot"]
        fx, fyy = zmap(PX - p.width / 2 + fk[0], PB - p.height + fk[1], z, 540, cy)
        add_glow(arr, knot_g, fx, fyy, 0.4 * ease((t - t1 - (caps[1][2] - t1) * 0.6) / 0.5))
        bx, by_ = zmap(PX, PB - 0.09 * p.height, z, 540, cy)
        add_glow(arr, knot_g, bx, by_, 0.4 * ease((t - t1 - 0.6) / 0.5))
        if t2 < t < t2 + 0.1:
            arr *= 1.4
        fog_layer(arr, t, k=0.22, color=MIST, y0=0.5)
        apply_flash(arr, fl.value(t))
        return post(arr, t, vig=VIG_HEAVY, tint=COLD)
    return f


def make_bow(D, caps):
    far, mid, front = graveyard(W, 81, trees=((180, 1.0), (980, 0.9)), graves_back=((560, 0.42),), graves_front=())
    t1 = caps[1][1]
    knot_g = glow_sprite(110, (210, 230, 255), 1.5)

    def f(t):
        img = far.crop((0, 0, W, H))
        img.alpha_composite(mid)
        bw = ease((t - t1 - 0.2) / 1.6)
        p = poc(t, 0.62, eyes=1.0, glow=0.7, bow=bw)
        PX, PB = 700, GY + 60
        img.alpha_composite(p, (int(PX - p.width / 2), int(PB - p.height)))
        tip = bayu_on(img, 300, GY + 70, walking=False, facing=1, scale=2.3, rim=(170, 190, 230), torch=0.6,
                      tremble=1.0 * math.sin(t * 24))
        img.alpha_composite(front)
        img.alpha_composite(RAIN2.layer(t, 0.5 * (1 - ease(t / D))))
        z = 1.05 + 0.15 * ease((t - t1) / 2.5)
        cx, cy = 520 + 100 * ease((t - t1) / 2.5), 840
        img = zoom(img, z, cx, cy)
        arr = arr_of(img)
        kx, ky = p.info["knot"]
        add_glow(arr, knot_g, *zmap(PX - p.width / 2 + kx, PB - p.height + ky, z, cx, cy), 0.6 * bw)
        tx, ty = zmap(*tip, z, cx, cy)
        arr += beam((W, H), (tx, ty), -0.25, 600, 0.22, k=0.7)
        fog_layer(arr, t, k=0.24, color=MIST, y0=0.45)
        return post(arr, t, vig=VIG_HEAVY, tint=COLD)
    return f


def hand_arm(reach=0.0, pull=0.0, color=(26, 20, 16, 255), rim=(255, 200, 140)):
    """Bayu's forearm and hand reaching in from the lower left (close-up). Returns RGBA W x H."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hx, hy = -100 + 560 * reach - 60 * pull, 1300 - 520 * reach + 40 * pull
    d.line([(-200, 1800), (hx, hy)], fill=color, width=110)
    d.ellipse([hx - 70, hy - 60, hx + 70, hy + 60], fill=color)
    for k in range(4):
        a = -1.2 + k * 0.3
        d.line([(hx, hy), (hx + math.cos(a) * 95, hy + math.sin(a) * 95)], fill=color, width=30)
    from art_ep5 import _rim
    return _rim(img, rim, 7, 5), (hx + 60, hy - 60)


def make_untie(D, caps):
    t0, t1 = caps[0][1], caps[1][1]
    bg = storm_sky((6, 8, 14), (40, 46, 62), seed=91, moon=(820, 300), moon_r=70)
    bg.alpha_composite(treeline(W, GY - 120, 80, SLATE_FAR, seed=91))
    bg.alpha_composite(ground_strip(W, GY, seed=91))
    rnd = random.Random(4)
    motes = [(rnd.uniform(-120, 120), rnd.uniform(0, 1), rnd.uniform(0.6, 1.4)) for _ in range(40)]
    mote = glow_sprite(10, (220, 235, 255), 1.4)
    split = t1 - 0.2

    def f(t):
        img = bg.copy()
        if t < split:
            # macro on the top knot, the hand pulls it loose
            un = ease((t - t0 - 1.2) / 1.6)
            p = poc(t, 2.4, eyes=0.0, glow=0.5, bow=1.0, untie=un)
            kx, ky = p.info["knot"]
            img.alpha_composite(p, (int(540 - kx), int(760 - ky)))
            arm, _ = hand_arm(ease((t - t0) / 1.2), pull=un)
            img.alpha_composite(arm)
            arr = arr_of(img)
            add_glow(arr, glow_sprite(200, (210, 230, 255), 1.5), 540, 760, 0.3 + 0.4 * un)
            return post(arr, t, vig=VIG_HEAVY, tint=COLD)
        # wide: the shroud sighs, sinks and falls empty; light motes rise; the moon breaks through
        u = ease((t - t1 - 0.6) / 2.2)
        p = poc(t, 0.7, eyes=0.0, glow=0.8 * (1 - u), bow=1.0, untie=1.0)
        hh = max(0.02, 1 - u)
        if hh > 0.08:
            pp = p.resize((int(p.width * (1 + 0.3 * u)), int(p.height * hh)), Image.BILINEAR)
            img.alpha_composite(with_alpha(pp, 1 - 0.5 * u), (int(560 - pp.width / 2), int(GY + 40 - pp.height)))
        pile = shroud_pile(0.7)
        img.alpha_composite(with_alpha(pile, ease((u - 0.6) / 0.4)), (int(560 - pile.width / 2), int(GY + 44 - pile.height)))
        bayu_on(img, 230, GY + 70, walking=False, facing=1, scale=2.0, rim=(190, 210, 240))
        arr = arr_of(zoom(img, 1.05 + 0.04 * (t - split) / max(0.1, D - split), 540, 900))
        for dx, ph, sp in motes:
            m = ((t - t1) * 0.25 * sp + ph) % 1.0
            if t > t1 + 0.4:
                add_glow(arr, mote, 560 + dx * (1 + m), GY - 200 - 700 * m, (1 - m) * ease((t - t1 - 0.4) / 0.6))
        fog_layer(arr, t, k=0.2, color=(150, 160, 190), y0=0.5)
        return post(arr, t, vig=VIG_HEAVY, tint=(0.96, 1.0, 1.06))
    return f


def make_morning(D, caps):
    sky_top, sky_bot = (120, 160, 200), (250, 214, 170)
    far, mid, front = graveyard(W, 101, top=sky_top, bot=sky_bot, trees=((160, 1.05), (920, 0.95)),
                                graves_back=((440, 0.4), (720, 0.42)), far_col=(90, 110, 100, 255), mid_col=(50, 70, 56, 255),
                                cloud_col=(220, 210, 210), tree_col=(40, 46, 36, 255), stone=(236, 236, 230, 255))
    fresh = grave(0.95, seed=5, fresh=True, color=(240, 240, 234, 255))
    mid.alpha_composite(fresh, (int(560 - fresh.width / 2), int(GY + 60 - fresh.height)))
    t1 = caps[1][1]
    sun = glow_sprite(520, (255, 220, 160), 1.3)
    pet = Petals2(12, seed=8)

    def f(t):
        img = far.crop((0, 0, W, H))
        img.alpha_composite(mid)
        dg = digger(1.2)
        place(img, dg, 840, GY + 110)
        bayu_on(img, 260, GY + 100, walking=False, facing=1, scale=2.0, rim=(255, 230, 190), color=(40, 36, 36, 255))
        img.alpha_composite(front)
        pet.draw(img, t, 0.8)
        z = 1.15 - 0.1 * ease(t / D)
        cy = 1000 - 120 * ease(t / D)
        arr = arr_of(zoom(img, z, 560, cy))
        add_glow(arr, sun, 620, 360, 0.5)
        fog_layer(arr, t, k=0.18, color=(250, 230, 210), y0=0.45)
        return post(arr, t, tint=(1.04, 1.0, 0.96))
    return f


_BG = None


def kbg():
    global _BG
    if _BG is None:
        _BG = kawung_bg()
    return _BG


def make_explain(D, caps):
    R = 200
    med = Image.new("RGBA", (R * 4, R * 4), (0, 0, 0, 0))
    ImageDraw.Draw(med).ellipse([4, 4, R * 4 - 4, R * 4 - 4], fill=(16, 20, 32, 255), outline=GOLD, width=6)
    med = down(med)
    p = pocong(1.0, 0.36, eyes=1.0, glow=0.6)
    mask = Image.new("L", med.size, 0)
    ImageDraw.Draw(mask).ellipse([6, 6, med.width - 6, med.height - 6], fill=255)
    inner = Image.new("RGBA", med.size, (0, 0, 0, 0))
    inner.alpha_composite(p, (int(med.width / 2 - p.width / 2), int(med.height - p.height + 30)))
    med.alpha_composite(Image.composite(inner, Image.new("RGBA", med.size, (0, 0, 0, 0)), mask))
    lbl = text_img("INDONESIAN  FOLKLORE", font(INTER_M, 30), fill=GOLD, pad=10)
    title = text_img("Pocong", font(LORA, 120, "Bold"), fill=CREAM, glow=(90, 110, 180, 210), pad=20)
    sub = text_img("Javanese: “wrapped in a shroud”", font(INTER_M, 38), fill=(226, 230, 240, 255), pad=8)
    pf = font(INTER_SB, 32)
    pills = [pill(n, pf, fill=(24, 28, 46, 230)) for n in ("Tied at head, neck & feet", "Hops: its feet are tied")]
    c1, c2 = card(450, 330), card(450, 330)
    d1 = ImageDraw.Draw(c1)
    # a little knot drawing
    d1.rounded_rectangle([150, 70, 300, 104], 14, fill=(210, 200, 180, 255))
    for s_ in (-1, 1):
        d1.polygon([(225, 87), (225 + s_ * 70, 40), (225 + s_ * 80, 130)], fill=(236, 234, 224, 255))
    d1.ellipse([205, 70, 245, 104], fill=ROPE + (255,))
    d1.text((225, 205), "Untie the knots", font=font(INTER_SB, 34), fill=CREAM, anchor="mm")
    d1.text((225, 252), "or the body rises,", font=font(INTER_M, 28), fill=(220, 214, 204, 255), anchor="mm")
    d1.text((225, 288), "folk tales say", font=font(INTER_M, 28), fill=(220, 214, 204, 255), anchor="mm")
    d2 = ImageDraw.Draw(c2)
    d2.text((225, 110), "MALAYSIA", font=font(LORA, 50, "Bold"), fill=(255, 214, 77, 255), anchor="mm")
    d2.text((225, 205), "calls it", font=font(INTER_M, 30), fill=(220, 214, 204, 255), anchor="mm")
    d2.text((225, 255), "Hantu Bungkus", font=font(INTER_SB, 38), fill=CREAM, anchor="mm")
    p1t = caps[2][1] + 0.4
    p2t = caps[2][1] + (caps[2][2] - caps[2][1]) * 0.6
    ta = caps[1][2] + 0.2
    tb = caps[2][2] - 0.3

    def f(t):
        arr = kbg().copy()
        fog_layer(arr, t, speed=8, k=0.18, color=(70, 80, 120), y0=0.3)
        layers = [(med, (W / 2 - med.width / 2, 120 + 6 * math.sin(t)), ease(t / 0.7)),
                  centered(lbl, 540, ease((t - 0.3) / 0.6)),
                  centered(title, 570 - 8 * ease(t / 1.0), ease((t - 0.4) / 0.8)),
                  centered(sub, 740, ease((t - caps[1][1] + 0.2) / 0.6))]
        tot = sum(p.width for p in pills) + 18
        if tot > W - 40:
            y = 830
            for p_, tt in zip(pills, (p1t, p2t)):
                layers.append((p_, (W / 2 - p_.width / 2, y - 10 * ease((t - tt) / 0.4)), ease((t - tt) / 0.4))); y += 84
        else:
            x = W / 2 - tot / 2
            for p_, tt in zip(pills, (p1t, p2t)):
                layers.append((p_, (x, 830 - 10 * ease((t - tt) / 0.4)), ease((t - tt) / 0.4)))
                x += p_.width + 18
        cy = 960
        layers.append((c1, (60, cy + 16 * (1 - ease((t - ta) / 0.5))), ease((t - ta) / 0.5) * (1 - 0.0)))
        layers.append((c2, (570, cy + 16 * (1 - ease((t - tb) / 0.5))), ease((t - tb) / 0.5)))
        return post(compose(arr, layers), t)
    return f


def make_outro(D, caps):
    q = text_img("Would YOU untie", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    q2 = text_img("the knot?", font(LORA, 96, "Bold"), fill=CREAM, glow=(90, 110, 180, 210), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Untie it", (30, 50, 100, 235)), ("RUN!", (150, 30, 30, 235)),
            ("Call Eyang", (120, 80, 20, 235)), ("Freeze...", (60, 60, 70, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    rows = [chips[0:2], chips[2:4]]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(214, 220, 232, 255), pad=10)

    def f(t):
        arr = kbg().copy()
        fog_layer(arr, t, speed=8, k=0.18, color=(70, 80, 120), y0=0.3)
        layers = [centered(q, 330, ease(t / 0.6)), centered(q2, 450, ease((t - 0.2) / 0.6))]
        yy, k = 660, 0
        for row in rows:
            tot = sum(c.width for c in row) + 24 * (len(row) - 1)
            x = W / 2 - tot / 2
            for c in row:
                tt = 0.5 + 0.2 * k
                layers.append((c, (x, yy + 12 * (1 - ease((t - tt) / 0.4))), ease((t - tt) / 0.4)))
                x += c.width + 24; k += 1
            yy += 120
        layers.append(centered(cm, 1010, ease((t - caps[1][1]) / 0.4) * (0.85 + 0.15 * math.sin(t * 6))))
        layers.append(centered(fol, 1110, ease((t - caps[1][1] - 0.4) / 0.5)))
        arr = post(compose(arr, layers), t)
        return arr * (1 - ease((t - (D - 0.6)) / 0.6))
    return f
