"""Vertical (1080x1920) scenes for Ghosts of Asia Ep.1 Pontianak, Part 1 and Part 2."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *

GY = 1180                       # ground line
VIG = vignette(0.8)
VIG_HEAVY = vignette(1.0)
GRAIN = grain_frames(6, 4)
GRAIN_HEAVY = grain_frames(6, 8, seed=3)
FOG = fog_texture(W * 2, H, seed=2)
GOLD = (214, 180, 116, 255)
CREAM = (244, 238, 226, 255)


def arr_of(img):
    return np.asarray(img.convert("RGB")).astype(np.float32)


def fog_layer(arr, t, speed=12, k=0.35, color=(120, 130, 170), y0=0.45, y1=1.0):
    off = int(t * speed) % W
    f = FOG[:, off:off + W]
    yy = np.linspace(0, 1, H)
    ramp = (np.clip((yy - y0) / max(1e-3, (0.6 - y0)), 0, 1) ** 0.8 * (1 - np.clip((yy - 0.635) / 0.12, 0, 1)) ** 1.5)[:, None]
    a = (f * ramp * k)[..., None]
    arr[:] = arr * (1 - a) + np.array(color, np.float32) * a


def post(arr, t, vig=VIG, grain=GRAIN, tint=None):
    if tint is not None:
        arr *= np.array(tint, np.float32)
    arr *= vig
    arr += grain[int(t * FPS) % len(grain)]
    return arr


def paste_bottom(canvas, img, x, base_y):
    canvas.alpha_composite(img, (int(x - img.width / 2), int(base_y - img.height)))


def sway(img, deg):
    return img.rotate(deg, Image.BICUBIC, center=(img.width / 2, img.height))


def compose(arr, layers):
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    for im, (x, y), a in layers:
        if a > 0.01:
            img.alpha_composite(with_alpha(im, a), (int(x), int(y)))
    return arr_of(img)


def centered(im, y, a=1.0):
    return (im, (W / 2 - im.width / 2, y), a)


def pill(text, f, outline=GOLD, fill=(30, 24, 50, 225), color=CREAM, h=70):
    tw = f.getlength(text)
    img = Image.new("RGBA", (int(tw + 60) * 2, h * 2), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([2, 2, img.width - 3, img.height - 3], h, outline=outline, width=4, fill=fill)
    img = down(img)
    ImageDraw.Draw(img).text((img.width / 2, img.height / 2), text, font=f, fill=color, anchor="mm")
    return img


def series_header(country, part=None):
    lbl = text_img("GHOSTS  OF  ASIA", font(INTER_M, 34), fill=GOLD, pad=10)
    big = text_img(country, font(LORA, 124, "Bold"), fill=CREAM, glow=(170, 20, 35, 230), pad=24)
    p = pill(part, font(INTER_SB, 52), outline=(255, 90, 90, 255), fill=(170, 18, 30, 240), h=96) if part else None
    return lbl, big, p


def header_layers(hdr, t, t0=-1.2, y=210):
    # t0=-1.2: the series header is fully visible from frame 0, so the first frame works as a cover (country + PART)
    lbl, big, p = hdr
    out = [centered(lbl, y, ease((t - t0) / 0.6)),
           centered(big, y + 40 - 10 * ease((t - t0) / 0.9), ease((t - t0 - 0.2) / 0.8))]
    if p is not None:
        out.append(centered(p, y + 215, ease((t - t0 - 0.6) / 0.5)))
    return out


def night_sky(moon=(800, 420), r=52, seed=11, w=W, top=(4, 5, 18), bot=(40, 32, 74)):
    return sky(top, bot, moon=moon, moon_r=r, stars=260, seed=seed, w=w)


# ======================================================================= shared world: path
class Path:
    def __init__(self):
        self.bg = night_sky((820, 430), 46, seed=13)
        self.far = hills(W * 2, 1010, 45, FAR, 7)
        S = 2600
        mid = Image.new("RGBA", (S + W, H), (0, 0, 0, 0))
        rnd = random.Random(4)
        x = 60
        while x < S:
            if rnd.random() < 0.65:
                paste_bottom(mid, banana_tree(rnd.uniform(0.85, 1.1), seed=int(x), color=MID), x, 1110)
            else:
                paste_bottom(mid, palm_tree(rnd.uniform(0.8, 1.0), seed=int(x), color=MID), x, 1110)
            x += rnd.uniform(220, 330)
        mid.paste(mid.crop((0, 0, W, H)), (S, 0), mid.crop((0, 0, W, H)))
        self.mid, self.MS = mid, S
        N = 3200
        near = Image.new("RGBA", (N + W, H), (0, 0, 0, 0))
        for x, s in ((350, 1.7), (1500, 1.55), (2550, 1.8)):
            paste_bottom(near, banana_tree(s, seed=x + 7, height=480), x, GY + 60)
        g = ground(N, GY, SIL, 5)
        near.alpha_composite(g)
        near.alpha_composite(g.crop((0, 0, W, H)), (N, 0))
        self.near, self.NS = near, N
        self.warm_big = glow_sprite(420, (255, 160, 70), 1.6)
        self.warm_small = glow_sprite(64, (255, 220, 150), 1.5)
        self.flies = Fireflies(30, seed=8, area=(0, W, 650, 1250))
        self.AX, self.AY = 470, GY + 22

    def frame(self, t, pos, phase, amp, flies_k=1.0, petals=None, petals_a=0, fog_k=0.3, z=1.0,
              flicker=0.0, facing=1, squash=1.0, extra=None):
        img = self.bg.copy()
        fx = int(pos * 0.08) % W
        img.alpha_composite(self.far.crop((fx, 0, fx + W, H)))
        mx = int(pos * 0.4) % self.MS
        img.alpha_composite(self.mid.crop((mx, 0, mx + W, H)))
        nx = int(pos) % self.NS
        if extra:
            extra(img, t)
        img.alpha_composite(self.near.crop((nx, 0, nx + W, H)))
        a, feet, lp = amir(phase, amp, facing=facing, squash=squash, scale=1.75)
        ox, oy = int(self.AX - feet[0]), int(self.AY - feet[1])
        img.alpha_composite(a, (ox, oy))
        arr = arr_of(img)
        lx, ly = ox + lp[0], oy + lp[1]
        fl = 1 + flicker * (0.5 * math.sin(t * 23) + 0.3 * math.sin(t * 37 + 1))
        add_glow(arr, self.warm_big, lx, ly + 60, 0.42 * fl)
        add_glow(arr, self.warm_small, lx, ly, 0.9 * fl)
        self.flies.draw(arr, t, flies_k)
        fog_layer(arr, t, k=fog_k)
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
        if petals is not None:
            petals.draw(im, t, petals_a)
        im = zoom(im, z, self.AX + 60, 900)
        return arr_of(im)


_PATH = None


def path():
    global _PATH
    if _PATH is None:
        _PATH = Path()
    return _PATH


SPEED, STEP = 150.0, 2 * math.pi * 0.85


# ======================================================================= P1: HOOK
def make_hook(D, caps):
    bg = night_sky((300, 520), 58, seed=21)
    bg.alpha_composite(hills(W, 1030, 50, FAR, 4))
    bg.alpha_composite(hills(W, 1100, 30, MID, 5))
    tr = banana_tree(1.9, seed=34, height=560)
    tl = banana_tree(1.5, seed=21, height=430)
    gr = ground(W, GY, SIL, 9)
    pet = Petals(16, seed=5)
    hdr = series_header("MALAYSIA", "PART 1")

    def f(t):
        img = bg.copy()
        ga = 0.16 + 0.08 * math.sin(t * 2.3)
        gh = ghost(t, 0.8)
        img.alpha_composite(with_alpha(gh, ga), (int(720 - gh.width / 2), int(560 + 8 * math.sin(t))))
        paste_bottom(img, sway(tr, -0.9 * math.sin(t * 0.7)), 860, GY + 70)
        paste_bottom(img, sway(tl, 1.0 * math.sin(t * 0.8)), 120, GY + 70)
        img.alpha_composite(gr)
        pet.draw(img, t + 3, 0.9)
        img = zoom(img, 1 + 0.06 * t / D, 600, 900)
        arr = arr_of(img)
        fog_layer(arr, t, k=0.32)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t)
    return f


# ======================================================================= P1: VILLAGE
def make_village(D, caps):
    WW = W + 320
    world = night_sky((260, 400), 44, seed=12, w=WW)
    world.alpha_composite(hills(WW, 980, 50, FAR, 6))
    world.alpha_composite(hills(WW, 1060, 25, MID, 8, freq=1.6))
    for x, s in ((560, 1.25), (1250, 1.3)):
        paste_bottom(world, palm_tree(s, seed=int(x)), x, GY - 10)
    wins = []
    for x, s, sd in ((300, 1.25, 1), (980, 1.35, 2)):
        h, w_ = house(s, seed=sd)
        ox, oy = int(x - h.width / 2), int(GY + 10 - h.height)
        world.alpha_composite(h, (ox, oy))
        wins += [(ox + wx + ww / 2, oy + wy + wh / 2) for wx, wy, ww, wh in w_]
    eld, ef, _ = amir(walking=False, facing=-1, lantern=False, color=SIL, rim=(60, 66, 110), scale=1.25)
    kid, kf, _ = amir(walking=False, facing=1, lantern=False, color=SIL, rim=(60, 66, 110), scale=0.75)
    world.alpha_composite(eld, (int(700 - ef[0]), int(GY + 26 - ef[1])))
    world.alpha_composite(kid, (int(610 - kf[0]), int(GY + 24 - kf[1])))
    paste_bottom(world, banana_tree(1.6, seed=56, height=470), WW - 70, GY + 80)
    world.alpha_composite(ground(WW, GY, SIL, 4))
    warm = glow_sprite(120, (255, 170, 80), 2.0)
    flies = Fireflies(30, seed=3, area=(0, WW, 700, 1220))

    def f(t):
        ox = int(320 * ease(t / D))
        arr = arr_of(world.crop((ox, 0, ox + W, H)))
        for i, (x, y) in enumerate(wins):
            add_glow(arr, warm, x - ox, y, 0.38 + 0.06 * math.sin(t * 7 + i * 2))
        flies.draw(arr, t, 1.0, dx=ox)
        fog_layer(arr, t, k=0.25)
        return post(arr, t)
    return f


# ======================================================================= P1: WALK / SILENCE
def make_walk(D, caps):
    p = path()

    def f(t):
        return post(p.frame(t, SPEED * t, STEP * t, 1.0, flicker=0.15), t)
    return f


def make_silence(D, caps, walk_D):
    p = path()
    pet = Petals(20, seed=9)
    t_stop = caps[0][1]
    start_pos, start_ph = SPEED * walk_D, STEP * walk_D
    ts = np.arange(0, D + 1, 1 / FPS)
    vs = np.array([1 - ease(x / max(0.5, t_stop + 0.6)) for x in ts])
    cum = np.concatenate([[0], np.cumsum(vs[:-1]) / FPS])

    def f(t):
        i = min(len(cum) - 1, int(round(t * FPS)))
        arr = p.frame(t + walk_D, start_pos + SPEED * cum[i], start_ph + STEP * cum[i], vs[i],
                      flies_k=1 - ease((t - t_stop) / 0.7), petals=pet, petals_a=ease((t - caps[1][1]) / 1.5),
                      fog_k=0.3 + 0.25 * ease(t / D), z=1 + 0.14 * ease(t / D),
                      flicker=0.15 + 0.3 * ease((t - t_stop) / 2))
        cold = 1 - 0.12 * ease((t - t_stop) / 2)
        return post(arr, t, tint=(cold, cold, 1.0))
    return f


# ======================================================================= CRY (P1) / RECAP (P2)
def ring_overlay(rings, color=(205, 215, 255)):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for (cx, cy, r, a, wdt) in rings:
        if a > 0.01 and r > 1:
            d.ellipse([cx - r, cy - r * 0.45, cx + r, cy + r * 0.45], outline=color + (int(255 * a),), width=int(wdt))
    return ov.filter(ImageFilter.GaussianBlur(0.8))


class CryWorld:
    def __init__(self, moon=(240, 420)):
        bg = night_sky(moon, 40, seed=14, top=(3, 5, 18), bot=(26, 30, 62))
        bg.alpha_composite(hills(W, 960, 22, FAR, 9, freq=2.5))
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rnd = random.Random(2)
        for x in range(0, W + 80, 85):
            paste_bottom(tl, banana_tree(rnd.uniform(0.32, 0.42), seed=x, color=MID, height=300), x + rnd.uniform(-20, 20), 992)
        bg.alpha_composite(tl)
        bg.alpha_composite(ground(W, 985, (26, 30, 58, 255), 6, tufts=False))
        bg.alpha_composite(ground(W, GY + 40, SIL, 7))
        a, feet, lp = amir(walking=False, facing=-1, scale=1.3)
        AX, AY = 800, GY + 58
        ox, oy = int(AX - feet[0]), int(AY - feet[1])
        self.lpos = (ox + lp[0], oy + lp[1])
        bg.alpha_composite(a, (ox, oy))
        self.bg = bg
        self.warm_big = glow_sprite(300, (255, 160, 70), 1.6)
        self.warm_small = glow_sprite(50, (255, 220, 150), 1.5)
        self.src = (230, 990)

    def frame(self, t, D, emits, layers=()):
        img = self.bg.copy()
        rings = []
        for e in emits:
            u = (t - e) / 2.6
            if 0 <= u <= 1:
                rings.append((self.src[0], self.src[1], 20 + 620 * u, (1 - u) ** 1.5 * 0.85, 4))
        if rings:
            img.alpha_composite(ring_overlay(rings))
        img = zoom(img, 1 + 0.04 * t / D, 540, 960)
        arr = arr_of(img)
        z = 1 + 0.04 * t / D
        lx = (self.lpos[0] - 540) * z + 540
        ly = (self.lpos[1] - 960) * z + 960
        add_glow(arr, self.warm_big, lx, ly + 40, 0.38)
        add_glow(arr, self.warm_small, lx, ly, 0.85)
        fog_layer(arr, t, k=0.35, y0=0.5)
        if layers:
            arr = compose(arr, layers)
        return post(arr, t, tint=(0.9, 0.92, 1.0))


def make_cry(D, caps):
    cw = CryWorld()
    w1, w2 = caps[0][2] - 0.6, caps[1][2] - 0.3
    emits = [w1 + k * 0.4 for k in range(8)] + [w2 + k * 0.4 for k in range(6)]
    return lambda t: cw.frame(t, D, emits)


def make_recap(D, caps):
    cw = CryWorld(moon=(860, 640))
    emits = [0.3 + k * 0.45 for k in range(6)] + [caps[1][1] + k * 0.45 for k in range(5)]
    hdr = series_header("MALAYSIA", "PART 2")
    return lambda t: cw.frame(t, D, emits, header_layers(hdr, t))


# ======================================================================= P1: CLIFFHANGER
def make_cliff(D, caps):
    bg = night_sky((860, 720), 40, seed=31, top=(2, 3, 12), bot=(22, 24, 50))
    bg.alpha_composite(hills(W, 1010, 40, FAR, 10))
    big = banana_tree(1.7, seed=91, color=(14, 15, 32, 255), height=470)
    gr = ground(W, GY, SIL, 11)
    warm_big = glow_sprite(420, (255, 160, 70), 1.6)
    warm_small = glow_sprite(64, (255, 220, 150), 1.5)
    t2 = caps[2][1]
    big_t = text_img("PART 2 TONIGHT", font(LORA, 92, "Bold"), fill=CREAM, glow=(170, 20, 35, 255), pad=24)
    sub_t = text_img("Follow so you don't miss it", font(INTER_M, 42), fill=(220, 214, 236, 255), pad=12)
    AX, AY = 700, GY + 22

    def f(t):
        img = bg.copy()
        paste_bottom(img, sway(big, 0.8 * math.sin(t * 0.6)), 250, GY + 70)
        ga = (0.12 + 0.3 * ease((t - caps[1][1]) / 2.5)) * (0.85 + 0.15 * math.sin(t * 5))
        gh = ghost(t, 0.75)
        img.alpha_composite(with_alpha(gh, ga), (int(260 - gh.width / 2), int(560 + 8 * math.sin(t * 1.2))))
        img.alpha_composite(gr)
        a, feet, lp = amir(walking=False, facing=1, scale=1.9)
        ox, oy = int(AX - feet[0]), int(AY - feet[1])
        img.alpha_composite(a, (ox, oy))
        z = 1 + 0.12 * ease(t / (t2 + 0.5))
        img = zoom(img, z, 480, 900)
        arr = arr_of(img)
        cw_, ch_ = W / z, H / z
        x0 = min(max(480 - cw_ / 2, 0), W - cw_); y0 = min(max(900 - ch_ / 2, 0), H - ch_)
        lx, ly = (ox + lp[0] - x0) * z, (oy + lp[1] - y0) * z
        fl = 1 + 0.3 * math.sin(t * 21) * math.sin(t * 7)
        add_glow(arr, warm_big, lx, ly + 50, 0.38 * fl)
        add_glow(arr, warm_small, lx, ly, 0.85 * fl)
        fog_layer(arr, t, k=0.42, y0=0.4)
        a1 = ease((t - t2 + 0.2) / 0.5)
        if a1 > 0:
            arr *= 1 - 0.45 * a1
            arr = compose(arr, [centered(big_t, 300, a1), centered(sub_t, 440, ease((t - t2 - 0.3) / 0.5))])
        return post(arr, t, vig=VIG_HEAVY, tint=(0.84, 0.87, 1.0))
    return f


# ======================================================================= P2: GRANDMA
def make_grandma(D, caps):
    S = 2
    room = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 255))
    d = ImageDraw.Draw(room)
    for y in range(0, H * S, 6):
        u = y / (H * S)
        d.rectangle([0, y, W * S, y + 6], fill=(int(72 - 34 * u), int(46 - 22 * u), int(29 - 13 * u)))
    for x in range(0, W * S, 150):
        d.line([(x, 0), (x, GY * S)], fill=(38, 24, 14), width=6)
    d.rectangle([0, GY * S, W * S, H * S], fill=(34, 22, 14))
    for y in range(GY * S, H * S, 40):
        d.line([(0, y), (W * S, y)], fill=(24, 15, 9), width=4)
    wx0, wy0, wx1, wy1 = 640 * S, 520 * S, 980 * S, 880 * S
    night = sky((8, 10, 30), (30, 34, 70), moon=(120, 90), moon_r=34, stars=50, seed=3, w=(wx1 - wx0) // S, h=(wy1 - wy0) // S)
    nt = night.resize((wx1 - wx0, wy1 - wy0))
    ImageDraw.Draw(nt).polygon([(0, nt.height), (0, nt.height * 0.72), (200, nt.height * 0.64), (420, nt.height * 0.76),
                                (nt.width, nt.height * 0.62), (nt.width, nt.height)], fill=(8, 8, 18, 255))
    room.paste(nt, (wx0, wy0))
    d.rectangle([wx0 - 20, wy0 - 20, wx1 + 20, wy1 + 20], outline=(30, 18, 10), width=30)
    for k in range(1, 4):
        xx = wx0 + (wx1 - wx0) * k / 4
        d.line([(xx, wy0), (xx, wy1)], fill=(30, 18, 10), width=14)
    C = (22, 12, 7, 255)
    K = 1.5 * S
    def P(x, y):
        return ((x - 340) * K + 40 * S, (y - 565) * K + (GY + 5) * S)
    def R(x0, y0, x1, y1):
        a, b = P(x0, y0), P(x1, y1)
        return [a[0], a[1], b[0], b[1]]
    d.rectangle(R(370, 470, 480, 486), fill=C)
    for lx in (380, 465):
        d.line([P(lx, 486), P(lx, 565)], fill=C, width=int(7 * K))
    d.ellipse(R(375, 400, 470, 480), fill=C)
    d.polygon([P(380, 450), P(395, 350), P(430, 320), P(470, 330), P(480, 420), P(470, 470)], fill=C)
    d.ellipse(R(435, 255, 500, 322), fill=C)
    d.ellipse(R(418, 258, 452, 292), fill=C)
    d.ellipse(R(492, 285, 504, 297), fill=C)
    d.polygon([P(450, 440), P(560, 448), P(565, 470), P(450, 476)], fill=C)
    d.polygon([P(540, 450), P(566, 450), P(560, 560), P(536, 560)], fill=C)
    d.polygon([P(530, 552), P(585, 552), P(585, 564), P(530, 564)], fill=C)
    d.line([P(465, 345), P(520, 420), P(545, 440)], fill=C, width=int(15 * K), joint="curve")
    d.line([P(590, 290), P(560, 565)], fill=C, width=int(5 * K))
    d.rectangle(R(600, 440, 700, 452), fill=C)
    for lx in (612, 688):
        d.line([P(lx, 452), P(lx, 565)], fill=C, width=int(5 * K))
    d.polygon([P(632, 440), P(668, 440), P(660, 418), P(640, 418)], fill=C)
    d.ellipse(R(636, 380, 664, 420), outline=C, width=int(3 * K))
    d.ellipse(R(730, 520, 830, 566), fill=C)
    d.polygon([P(755, 530), P(805, 530), P(798, 468), P(762, 468)], fill=C)
    d.ellipse(R(752, 418, 802, 470), fill=C)
    d.ellipse(R(745, 440, 757, 452), fill=C)
    room = down(room)
    flame_xy = (P(650, 400)[0] / S, P(650, 400)[1] / S)
    flame = glow_sprite(20, (255, 230, 160), 1.2)
    warm = glow_sprite(600, (255, 150, 60), 1.5)
    f1 = font(LORA, 64, "Bold")
    t1 = text_img("Loud cry = far away", f1, fill=(255, 236, 200, 255), glow=(0, 0, 0, 255), pad=24)
    t2 = text_img("Soft cry = right behind you", f1, fill=(255, 120, 100, 255), glow=(0, 0, 0, 255), pad=24)
    lum_w = np.array([0.3, 0.59, 0.11], np.float32)

    def f(t):
        img = zoom(room, 1 + 0.05 * t / D, 540, 1000)
        arr = arr_of(img)
        fl = 1 + 0.08 * math.sin(t * 11) + 0.05 * math.sin(t * 29 + 1)
        add_glow(arr, warm, flame_xy[0], flame_xy[1], 0.55 * fl)
        add_glow(arr, flame, flame_xy[0], flame_xy[1] + math.sin(t * 9), 1.6)
        lum = (arr * lum_w).sum(-1, keepdims=True)
        arr = arr * 0.35 + lum * np.array([1.12, 0.92, 0.68], np.float32) * 0.65
        arr = compose(arr, [centered(t1, 230, ease((t - caps[1][1]) / 0.6)),
                            centered(t2, 340, ease((t - caps[2][1]) / 0.6))])
        return post(arr, t, vig=VIG_HEAVY, grain=GRAIN_HEAVY)
    return f


# ======================================================================= P2: SOFTER
def make_softer(D, caps):
    bg = night_sky(None, 0, seed=15, top=(2, 3, 12), bot=(20, 22, 46))
    bg.alpha_composite(hills(W, 1020, 35, FAR, 10))
    tm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x, s in ((620, 0.9), (900, 1.0)):
        paste_bottom(tm, banana_tree(s, seed=x + 3, color=MID), x, 1110)
    bg.alpha_composite(tm)
    big = banana_tree(1.7, seed=91, color=(14, 15, 32, 255), height=470)
    gr = ground(W, GY, SIL, 11)
    warm_big = glow_sprite(420, (255, 160, 70), 1.6)
    warm_small = glow_sprite(64, (255, 220, 150), 1.5)
    t_turn = caps[2][1]
    src = (260, 1000)
    emits = [(caps[0][2] - 0.2 + k * 0.3, 1.0) for k in range(6)] + [(caps[1][2] - 0.1 + k * 0.3, 0.6) for k in range(5)]
    AX, AY = 760, GY + 22

    def f(t):
        img = bg.copy()
        paste_bottom(img, sway(big, 0.8 * math.sin(t * 0.6)), 250, GY + 70)
        ga = 0.42 * ease((t - 0.3) / max(0.5, t_turn - 0.3)) * (0.85 + 0.15 * math.sin(t * 5))
        if ga > 0.01:
            gh = ghost(t, 0.75)
            img.alpha_composite(with_alpha(gh, ga), (int(260 - gh.width / 2), int(560 + 8 * math.sin(t * 1.2))))
        img.alpha_composite(gr)
        u = ease((t - t_turn) / 1.1)
        if u <= 0:
            facing, sq = 1, 1.0
        else:
            c = math.cos(math.pi * u)
            facing, sq = (1 if c >= 0 else -1), max(0.08, abs(c))
        a, feet, lp = amir(walking=False, facing=facing, squash=sq, scale=1.9)
        ox, oy = int(AX - feet[0]), int(AY - feet[1])
        img.alpha_composite(a, (ox, oy))
        rings = [(src[0], src[1], 10 + 90 * uu, (1 - uu) * 0.5 * k, 3) for e, k in emits
                 for uu in [(t - e) / 1.4] if 0 <= uu <= 1]
        if rings:
            img.alpha_composite(ring_overlay(rings))
        z = 1 + 0.16 * ease(t / D)
        img = zoom(img, z, 520, 950)
        arr = arr_of(img)
        cw_, ch_ = W / z, H / z
        x0 = min(max(520 - cw_ / 2, 0), W - cw_); y0 = min(max(950 - ch_ / 2, 0), H - ch_)
        lx, ly = (ox + lp[0] - x0) * z, (oy + lp[1] - y0) * z
        fl = 1 + 0.35 * math.sin(t * 21) * math.sin(t * 7)
        add_glow(arr, warm_big, lx, ly + 50, 0.36 * fl)
        add_glow(arr, warm_small, lx, ly, 0.8 * fl)
        fog_layer(arr, t, k=0.45, y0=0.4)
        return post(arr, t, vig=VIG_HEAVY, tint=(0.82, 0.86, 1.0))
    return f


# ======================================================================= P2: REVEAL
def make_reveal(D, caps):
    bg = night_sky(None, 0, seed=16, top=(2, 2, 8), bot=(16, 12, 30))
    tree = banana_tree(2.6, seed=93, color=(15, 14, 32, 255), height=330)
    gr = ground(W, GY + 200, SIL, 12)
    cut = D - 1.0
    rnd = random.Random(5)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(int(D * FPS) + 5)]
    warm = glow_sprite(500, (255, 150, 60), 1.5)

    def f(t):
        if t >= cut:
            return np.zeros((H, W, 3), np.float32)
        img = bg.copy()
        paste_bottom(img, sway(tree, 0.6 * math.sin(t * 0.5)), 540, H + 300)
        gh = ghost(t, 1.9)
        img.alpha_composite(gh, (int(540 - gh.width / 2), int(260 + 14 * math.sin(t * 1.3))))
        img.alpha_composite(gr)
        img = zoom(img, 1.0 + 0.06 * t / D, 540, 800)
        i = int(t * FPS)
        amp = 20 * math.exp(-t * 3.5) + (8 if t > cut - 0.5 else 0)
        if amp > 0.5:
            img = img.transform(img.size, Image.AFFINE, (1, 0, shake[i][0] * amp, 0, 1, shake[i][1] * amp), resample=Image.BILINEAR)
        arr = arr_of(img)
        add_glow(arr, warm, 980, 1500, 0.32)
        fog_layer(arr, t, k=0.35, color=(110, 120, 160), y0=0.5)
        if t < 0.5 or t > cut - 0.6:
            arr *= 0.55 + 0.6 * rnd.random()
        return post(arr, t, vig=VIG_HEAVY, tint=(0.88, 0.9, 1.0))
    return f


# ======================================================================= P2: EXPLAIN / OUTRO background
class ExplainBG:
    def __init__(self):
        y = np.linspace(0, 1, H)[:, None, None]
        top, bot = np.array([10, 9, 24]), np.array([32, 23, 52])
        self.base = np.repeat(top * (1 - y) + bot * y, W, axis=1).astype(np.float32)
        rnd = random.Random(7)
        for _ in range(200):
            self.base[rnd.randrange(H), rnd.randrange(W)] += rnd.uniform(30, 110)

    def frame(self, t):
        arr = self.base.copy()
        fog_layer(arr, t, speed=8, k=0.22, color=(90, 80, 140), y0=0.3)
        return arr


_EB = None


def ebg():
    global _EB
    if _EB is None:
        _EB = ExplainBG()
    return _EB


def card(w, h):
    img = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([2, 2, w * 2 - 3, h * 2 - 3], 40, fill=(24, 20, 44, 235), outline=(214, 180, 116, 150), width=3)
    return down(img)


def make_explain(D, caps):
    R = 200
    med = Image.new("RGBA", (R * 4, R * 4), (0, 0, 0, 0))
    ImageDraw.Draw(med).ellipse([4, 4, R * 4 - 4, R * 4 - 4], fill=(16, 14, 34, 255), outline=GOLD, width=6)
    med = down(med)
    gh = ghost(1.0, 0.44)
    mask = Image.new("L", med.size, 0)
    ImageDraw.Draw(mask).ellipse([6, 6, med.width - 6, med.height - 6], fill=255)
    inner = Image.new("RGBA", med.size, (0, 0, 0, 0))
    inner.alpha_composite(gh, (int(med.width / 2 - gh.width / 2), 34))
    med.alpha_composite(Image.composite(inner, Image.new("RGBA", med.size, (0, 0, 0, 0)), mask))
    lbl = text_img("SOUTHEAST  ASIAN  FOLKLORE", font(INTER_M, 30), fill=GOLD, pad=10)
    title = text_img("Pontianak", font(LORA, 128, "Bold"), fill=CREAM, glow=(150, 30, 40, 200), pad=20)
    pf = font(INTER_SB, 34)
    pills = [pill(n, pf) for n in ("Malaysia", "Singapore", "Indonesia")]
    c1, c2 = card(450, 330), card(450, 330)
    tree = banana_tree(0.5, seed=5, color=(150, 196, 150, 255), height=210)
    c1.alpha_composite(tree, (int(225 - tree.width / 2), int(242 - tree.height)))
    fl = frangipani(150)
    c2.alpha_composite(fl, (int(225 - fl.width / 2), 60))
    lf = font(INTER_SB, 32)
    ImageDraw.Draw(c1).text((225, 285), "Hides in banana trees", font=lf, fill=CREAM, anchor="mm")
    ImageDraw.Draw(c2).text((225, 285), "Frangipani = she is near", font=lf, fill=CREAM, anchor="mm")
    l0 = caps[0][2] - caps[0][1]
    pt = [caps[0][1] + l0 * k for k in (0.62, 0.76, 0.9)]
    ta = caps[1][1]
    tb = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.5

    def f(t):
        arr = ebg().frame(t)
        layers = [(med, (W / 2 - med.width / 2, 150 + 6 * math.sin(t)), ease(t / 0.7)),
                  centered(lbl, 580, ease((t - 0.3) / 0.6)),
                  centered(title, 610 - 8 * ease(t / 1.0), ease((t - 0.4) / 0.8))]
        tot = sum(p.width for p in pills) + 2 * 18
        x = W / 2 - tot / 2
        for p, tt in zip(pills, pt):
            layers.append((p, (x, 810 - 10 * ease((t - tt) / 0.4)), ease((t - tt) / 0.4)))
            x += p.width + 18
        layers.append((c1, (60, 920 + 16 * (1 - ease((t - ta) / 0.5))), ease((t - ta) / 0.5)))
        layers.append((c2, (570, 920 + 16 * (1 - ease((t - tb) / 0.5))), ease((t - tb) / 0.5)))
        return post(compose(arr, layers), t)
    return f


# ======================================================================= P2: ENDING
def make_ending(D, caps):
    p = path()
    pet = Petals(22, seed=12)
    bg = p.bg.copy()
    bg.alpha_composite(p.far.crop((300, 0, 300 + W, H)))
    bg.alpha_composite(p.mid.crop((900, 0, 900 + W, H)))
    bg.alpha_composite(p.near.crop((1300, 0, 1300 + W, H)))
    L = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.polygon([(60, 80), (180, 80), (196, 184), (44, 184)], fill=(12, 12, 24, 255))
    d.rectangle([80, 100, 160, 168], fill=(255, 190, 90, 255))
    d.arc([80, 28, 160, 108], 180, 360, fill=(12, 12, 24, 255), width=8)
    L = L.rotate(-78, Image.BICUBIC, expand=True)
    L = L.resize((int(L.width * 0.55), int(L.height * 0.55)), Image.LANCZOS)
    LX, LY = 540, GY + 18
    bg.alpha_composite(L, (int(LX - L.width / 2), int(LY - L.height)))
    lc = (LX, LY - L.height / 2)
    warm_big = glow_sprite(360, (255, 160, 70), 1.6)
    warm_small = glow_sprite(56, (255, 220, 150), 1.5)
    txt = text_img("Don't turn around.", font(LORA, 96, "Bold"), fill=(250, 236, 230, 255), glow=(200, 20, 30, 255), pad=24)
    tt = caps[1][1]

    def f(t):
        img = bg.copy()
        pet.draw(img, t, 0.8)
        z = 1 + 0.12 * ease(t / D)
        img = zoom(img, z, LX, 1000)
        arr = arr_of(img)
        ch_ = H / z; y0 = min(max(1000 - ch_ / 2, 0), H - ch_)
        cw_ = W / z; x0 = min(max(LX - cw_ / 2, 0), W - cw_)
        gx, gy = (lc[0] - x0) * z, (lc[1] - y0) * z
        fl = 1 + 0.4 * math.sin(t * 19) * math.sin(t * 5.3)
        add_glow(arr, warm_big, gx, gy + 20, 0.48 * fl)
        add_glow(arr, warm_small, gx, gy, 0.95 * fl)
        fog_layer(arr, t, k=0.45, y0=0.35)
        a = ease((t - tt - 0.1) / 0.5)
        if a > 0:
            arr = compose(arr, [centered(txt, 520, a)])
        arr = post(arr, t, vig=VIG_HEAVY, tint=(0.85, 0.87, 1.0))
        return arr * (1 - ease((t - (D - 0.9)) / 0.8))
    return f


# ======================================================================= P2: OUTRO
def make_outro(D, caps):
    q = text_img("Which country", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    q2 = text_img("should be next?", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    pf = font(INTER_SB, 40)
    names = ["Thailand", "Japan", "Philippines", "Indonesia", "China", "Myanmar", "India", "Vietnam"]
    chips = [pill(n, pf, h=84) for n in names]
    cm = text_img("Comment below", font(INTER_SB, 50), fill=(255, 214, 140, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(205, 200, 222, 255), pad=10)
    rows = [chips[0:3], chips[3:6], chips[6:8]]

    def f(t):
        arr = ebg().frame(t)
        layers = [centered(q, 330, ease(t / 0.6)), centered(q2, 450, ease((t - 0.2) / 0.6))]
        y = 640
        k = 0
        for row in rows:
            tot = sum(c.width for c in row) + 22 * (len(row) - 1)
            x = W / 2 - tot / 2
            for c in row:
                tt = 0.5 + 0.18 * k
                layers.append((c, (x, y + 12 * (1 - ease((t - tt) / 0.4))), ease((t - tt) / 0.4)))
                x += c.width + 22; k += 1
            y += 112
        layers.append(centered(cm, 1010, ease((t - caps[1][1]) / 0.4) * (0.85 + 0.15 * math.sin(t * 6))))
        layers.append(centered(fol, 1110, ease((t - caps[1][1] - 0.4) / 0.5)))
        arr = post(compose(arr, layers), t)
        return arr * (1 - ease((t - (D - 0.6)) / 0.6))
    return f
