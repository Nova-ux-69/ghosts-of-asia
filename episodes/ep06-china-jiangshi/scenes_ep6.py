"""Episode 6: Jiangshi (China), vertical scenes.
New world for this episode: Xiangxi in western Hunan. Jade-green night over tall karst pillars, a mountain ridge
road, a river town of diaojiaolou stilt houses with red lanterns reflected in the water, a warm inn room with a
lattice window, a plank shed striped with moonlight, a pink-jade dawn procession along the river, and a
xiangyun-cloud explainer.
Camera: a slow push-in on a distant procession, a long river pan, a two-shot dolly, a candle-lit macro on the
talisman, a face close-up that pulls back as the arms rise, a side-tracking chase, a breath-hold two-shot that
sways with the ghost's head, a dawn crane-up."""
import sys, os, math, random
_EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _EP); sys.path.insert(1, os.path.join(_EP, "..", "..", "toolkit"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *
from art_ep6 import *
from scenes_v import (GY, VIG, VIG_HEAVY, GRAIN, arr_of, fog_layer, post, compose, centered, pill, series_header,
                      header_layers, card)

GOLD = (214, 180, 116, 255)
CREAM = (244, 238, 226, 255)
MIST_C = (130, 190, 172)
JADE_TINT = (0.92, 1.04, 1.0)
WATER_Y = 1300


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


def place(img, im, x, feet_y, anchor_x=None):
    ax = im.width / 2 if anchor_x is None else anchor_x
    img.alpha_composite(im, (int(x - ax), int(feet_y - im.height)))


def hop_y(t, t0, per=0.75, hgt=60):
    if t < t0:
        return 0.0
    u = ((t - t0) % per) / per
    return -hgt * math.sin(math.pi * min(1, u / 0.7)) if u < 0.7 else 0.0


_JS, _JF, _MF = {}, {}, {}


def js(scale, arms=1.0, eyes=0.0, paper=1.0, paper_ang=0.0, facing=1, rim=MOONLIGHT):
    key = (round(scale, 3), round(arms, 1), round(eyes, 1), round(paper, 1), round(paper_ang, 1), facing, rim)
    if key not in _JS:
        if len(_JS) > 300:
            _JS.clear()
        _JS[key] = jiangshi_side(key[0], key[1], key[2], key[3], key[4], facing, rim)
    return _JS[key]


def jsf(scale, arms=0.0, eyes=0.0, paper=1.0, paper_ang=0.0, sniff=0.0):
    key = (round(scale, 3), round(arms, 1), round(eyes, 1), round(paper, 1), round(paper_ang, 1), round(sniff, 1))
    if key not in _JF:
        if len(_JF) > 200:
            _JF.clear()
        _JF[key] = jiangshi_front(*key)
    return _JF[key]


def mf(scale, light=1.0, look=0.0, eyes=1.0, hold=0.0, warm=(1.08, 0.96, 0.84)):
    key = (round(scale, 3), round(light, 1), round(look, 1), round(eyes, 1), round(hold, 1), warm)
    if key not in _MF:
        if len(_MF) > 200:
            _MF.clear()
        _MF[key] = mei_front(*key)
    return _MF[key]


def put_js(img, x, feet_y, scale, **kw):
    im, (fx, fy) = js(scale, **kw)
    img.alpha_composite(im, (int(x - fx), int(feet_y - fy)))
    return im, (int(x - fx), int(feet_y - fy))


def put_mei(img, x, feet_y, **kw):
    im, feet, tip = mei(**kw)
    ox, oy = int(x - feet[0]), int(feet_y - feet[1])
    img.alpha_composite(im, (ox, oy))
    return ox + tip[0], oy + tip[1]


def put_priest(img, x, feet_y, **kw):
    im, feet, bell_p, lan_p = priest(**kw)
    ox, oy = int(x - feet[0]), int(feet_y - feet[1])
    img.alpha_composite(im, (ox, oy))
    return (ox + bell_p[0], oy + bell_p[1]), ((ox + lan_p[0], oy + lan_p[1]) if lan_p else None)


LGLOW = glow_sprite(90, LANTERN_GLOW, 1.8)
LGLOW_BIG = glow_sprite(260, LANTERN_GLOW, 1.8)
CGLOW = glow_sprite(150, CANDLE, 1.7)
PGLOW = glow_sprite(40, (255, 220, 100), 1.6)
EGLOW = glow_sprite(26, (140, 255, 190), 1.5)


def mountain_world(sw, seed, top=JADE_TOP, bot=JADE_BOT, moon=(780, 360), far_col=PEAK_FAR, mid_col=PEAK_MID, mist_col=(150, 200, 186)):
    fw = int(W + sw * 0.3) + 10
    far = jade_sky(w=fw, top=top, bot=bot, moon=moon, seed=seed)
    far.alpha_composite(karst(fw, GY - 60, far_col, seed=seed))
    far.alpha_composite(mist_band(fw, GY - 220, 220, color=mist_col, seed=seed))
    mid = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    mid.alpha_composite(karst(sw, GY + 80, mid_col, seed=seed + 3, hmin=260, hmax=520, wmin=110, wmax=200, gap=(120, 320)))
    mid.alpha_composite(mist_band(sw, GY - 20, 160, color=mist_col, alpha=110, seed=seed + 1))
    return far, mid


def view(far, *layers, cam=0.0):
    fx = int(cam * 0.3)
    img = far.crop((fx, 0, fx + W, H))
    for L in layers:
        img.alpha_composite(L.crop((int(cam), 0, int(cam) + W, H)))
    return img


def ridge(sw, y, color=SILH, seed=0):
    rnd = random.Random(seed)
    img = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(x, y + 20 * math.sin(x / 300 + seed) + rnd.uniform(-4, 4)) for x in range(0, sw + 41, 40)]
    d.polygon(pts + [(sw, H), (0, H)], fill=color)
    for _ in range(sw // 10):
        x = rnd.uniform(0, sw); yy = y + 20 * math.sin(x / 300 + seed)
        d.line([(x, yy + 4), (x + rnd.uniform(-6, 6), yy - rnd.uniform(6, 22))], fill=color, width=3)
    return img


def pine(scale=1.0, color=SILH, seed=0):
    """A wind-bent pine silhouette leaning over the frame edge. Anchor bottom-left."""
    rnd = random.Random(seed)
    S = 2 * scale
    img = Image.new("RGBA", (int(520 * S), int(900 * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(40 * S, 900 * S), (70 * S, 700 * S), (60 * S, 520 * S), (120 * S, 360 * S), (220 * S, 240 * S)]
    d.line(pts, fill=color, width=int(30 * S), joint="curve")
    for k, (x, y) in enumerate(pts[1:]):
        L = (220 - k * 20) * S
        d.line([(x, y), (x + L, y - 30 * S)], fill=color, width=int(10 * S))
        for j in range(5):
            cx_ = x + L * (0.3 + 0.17 * j); cy_ = y - 30 * S * (0.3 + 0.17 * j) - 10 * S
            d.ellipse([cx_ - 60 * S, cy_ - 22 * S, cx_ + 60 * S, cy_ + 22 * S], fill=color)
    return down(img)


# ======================================================================= P1
def make_hook(D, caps):
    far, mid = mountain_world(W + 60, 3, moon=(860, 640))
    rd = ridge(W + 60, GY - 30, color=(8, 18, 18, 255), seed=2)
    pn = pine(0.9, seed=1)
    hdr = series_header("CHINA", "PART 1")
    t2 = caps[1][1]
    mist = Mist(10, seed=4, y0=GY - 120, y1=GY + 40, alpha=70)

    def f(t):
        img = far.crop((0, 0, W, H))
        img.alpha_composite(mid.crop((20, 0, 20 + W, H)))
        img.alpha_composite(rd.crop((20, 0, 20 + W, H)))
        # the procession on the ridge: priest with a lantern in front, three stiff figures hopping behind
        walk = 150 + 260 * t / D
        lan = None
        bell_p, lan = put_priest(img, walk + 300, GY - 24, scale=0.62, phase=t * 5, walking=True, rim=(255, 160, 90),
                                 bell_up=0.4 + 0.2 * math.sin(t * 9))
        papers, faces = [], []
        for k in range(3):
            x = walk + 200 - k * 95
            hy = hop_y(t, 0.1 + 0.08 * k, 0.75, 26)
            im, (ox, oy) = put_js(img, x, GY - 22 + hy, 0.19, arms=1.0, eyes=1.0 if (k == 0 and t > t2) else 0.0)
            papers.append((x + 8, oy + 40)); faces.append((x + 6, oy + 34))
        img.alpha_composite(mist.layer(t, 1.0))
        img.alpha_composite(pn, (-40, H - pn.height + 160))
        z = 1.0 + 0.08 * t / D + 0.55 * ease((t - t2 + 0.3) / 1.6)
        cx, cy = 560 + 40 * ease((t - t2) / 1.6), 1020
        img = zoom(img, z, cx, cy)
        arr = arr_of(img)
        if lan:
            add_glow(arr, LGLOW, *zmap(*lan, z, cx, cy), 0.9)
        for p in papers:
            add_glow(arr, PGLOW, *zmap(*p, z, cx, cy), 0.35 * z)
        if t > t2:
            fx, fy = zmap(*faces[0], z, cx, cy)
            add_glow(arr, EGLOW, fx, fy, 1.2 * ease((t - t2) / 0.4))
        fog_layer(arr, t, k=0.22, color=MIST_C, y0=0.5)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, vig=VIG_HEAVY, tint=JADE_TINT)
    return f


def boardwalk(sw, y, color=(14, 12, 10, 255)):
    img = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y, sw, y + 26], fill=color)
    for x in range(0, sw, 60):
        d.rectangle([x, y + 26, x + 10, y + 140], fill=color)
    d.line([(0, y + 4), (sw, y + 4)], fill=(60, 48, 36, 255), width=2)
    return img


def make_inn(D, caps):
    sw = 2400
    far, mid = mountain_world(sw, 12, moon=(700, 330))
    houses, glows, hooks = Image.new("RGBA", (sw, H), (0, 0, 0, 0)), [], []
    for hx, hs, sd in ((260, 0.62, 1), (760, 0.72, 2), (1260, 0.66, 3), (1760, 0.78, 4), (2240, 0.7, 5)):
        h, g, hk = stilt_house(hs, seed=sd)
        ox, oy = int(hx - h.width / 2), int(WATER_Y + 30 - h.height)
        houses.alpha_composite(h, (ox, oy)); glows += [(ox + a, oy + b) for a, b in g]; hooks += [(ox + a, oy + b) for a, b in hk]
    lan = lantern(0.5)
    for hx, hy in hooks:
        houses.alpha_composite(lan, (int(hx - lan.width / 2), int(hy)))
    lpts = [(hx, hy + lan.height * 0.4) for hx, hy in hooks]
    water = river(sw, WATER_Y + 20, H, seed=3)
    bw = boardwalk(sw, WATER_Y, )
    span = sw - W
    t2 = caps[1][1]
    mist = Mist(14, seed=7, y0=WATER_Y - 80, y1=WATER_Y + 60, alpha=60, w=W)

    def f(t):
        cam = span * ease(t / D * 0.92 + 0.04)
        img = view(far, mid, cam=cam)
        img.alpha_composite(water.crop((int(cam), 0, int(cam) + W, H)))
        img.alpha_composite(houses.crop((int(cam), 0, int(cam) + W, H)))
        img.alpha_composite(bw.crop((int(cam), 0, int(cam) + W, H)))
        # the priest has arrived at the inn (right end) with three stiff travellers behind him
        arrive = ease((t - t2 + 1.5) / 2.0)
        px = 1930 - 160 * (1 - arrive) - cam
        ring = (t > t2) * (0.5 + 0.5 * math.sin(t * 14))
        bell_p, lan_p = put_priest(img, px, WATER_Y + 2, scale=1.25, rim=(255, 170, 100), bell_up=0.2 + 0.6 * ring * (t > t2 + 0.6),
                                   walking=arrive < 0.99, phase=t * 5)
        papers = []
        for k in range(3):
            x = px - 140 - k * 120
            hy = hop_y(t, 0.0, 0.75, 22) if arrive < 0.99 else 0.0
            im, (ox, oy) = put_js(img, x, WATER_Y + 2 + hy, 0.34, arms=1.0, rim=(255, 170, 120))
            papers.append((x + 14, oy + 76))
        put_mei(img, 2180 - cam, WATER_Y + 2, facing=-1, scale=1.5, rim=(255, 190, 120))
        img.alpha_composite(mist.layer(t, 1.0))
        arr = arr_of(img)
        for gx, gy in glows:
            add_glow(arr, LGLOW, gx - cam, gy, 0.5)
        for lx, ly in lpts:
            add_glow(arr, LGLOW, lx - cam, ly, 0.9)
            reflect(arr, lx - cam, WATER_Y + 40, 420, LANTERN_GLOW, k=0.8, t=t)
        if lan_p:
            add_glow(arr, LGLOW, *lan_p, 1.0)
        for p in papers:
            add_glow(arr, PGLOW, *p, 0.5)
        reflect(arr, 700 - cam * 0.3, WATER_Y + 40, 500, (160, 230, 200), k=0.5, t=t, width=60)
        fog_layer(arr, t, k=0.15, color=MIST_C, y0=0.5)
        return post(arr, t, tint=(1.0, 1.02, 0.98))
    return f


def inn_room(seed=0):
    """Inn interior: dark timber walls, a round lattice window with moonlight and three silhouettes outside, a red
    lantern, a low table with a teapot."""
    y = np.linspace(0, 1, H)[:, None, None]
    base = Image.fromarray(np.repeat(np.array([30, 16, 10]) * (1 - y) + np.array([70, 40, 22]) * y, W, axis=1).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(base)
    for x in range(0, W, 120):
        d.rectangle([x, 160, x + 8, 1180], fill=(40, 22, 12, 255))
    d.rectangle([0, 160, W, 190], fill=(36, 20, 10, 255))
    # moon-gate lattice window
    cx, cy, r = 330, 600, 230
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 120, 108, 255))
    win = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    wd = ImageDraw.Draw(win)
    for k in range(3):
        im, (fx, fy) = jiangshi_side(0.26, arms=1.0, eyes=0.0, paper=1.0, rim=None)
        win.alpha_composite(im, (int(60 + k * 120), int(2 * r - im.height + 10)))
    wd.rectangle([0, 2 * r - 40, 2 * r, 2 * r], fill=(10, 24, 22, 255))
    for k in range(0, 2 * r, 46):
        wd.line([(k, 0), (k, 2 * r)], fill=(34, 18, 8, 255), width=8)
        wd.line([(0, k), (2 * r, k)], fill=(34, 18, 8, 255), width=8)
    m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    base.paste(win, (cx - r, cy - r), Image.composite(win, Image.new("RGBA", win.size, (0, 0, 0, 0)), m).split()[3])
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(26, 14, 6, 255), width=26)
    # floor + table + teapot
    d.rectangle([0, 1180, W, H], fill=(56, 34, 20, 255))
    for x in range(-400, W + 400, 60):
        d.line([(x, 1180), (x + 240, H)], fill=(46, 28, 16, 255), width=3)
    d.rectangle([380, 1060, 720, 1090], fill=(28, 14, 8, 255))
    for x in (400, 690):
        d.rectangle([x, 1090, x + 16, 1190], fill=(28, 14, 8, 255))
    d.ellipse([500, 990, 590, 1062], fill=(170, 190, 170, 255))
    d.line([(586, 1010), (622, 990)], fill=(170, 190, 170, 255), width=10)
    d.arc([470, 1000, 520, 1050], 90, 270, fill=(170, 190, 170, 255), width=8)
    for x in (620, 660):
        d.rectangle([x, 1040, x + 26, 1062], fill=(200, 210, 196, 255))
    return base


def make_warn(D, caps):
    base = inn_room()
    lan = lantern(1.3)
    LX, LY = 940, 440
    base.alpha_composite(lan, (int(LX - lan.width / 2), LY))
    lt1 = text_img("THEY SLEEP IN YOUR SHED.", font(LORA, 62, "Bold"), fill=CREAM, glow=(170, 40, 20, 230), pad=20)
    lt2 = text_img("NEVER TOUCH", font(LORA, 82, "Bold"), fill=CREAM, glow=(170, 40, 20, 230), pad=20)
    lt3 = text_img("THE YELLOW PAPER.", font(LORA, 76, "Bold"), fill=(255, 214, 77, 255), glow=(170, 40, 20, 230), pad=20)
    tal = talisman(1.2)
    t1, t2 = caps[1][1], caps[2][1]

    def f(t):
        img = base.copy()
        hold = ease((t - t2 + 0.4) / 0.6)
        bell_p, _ = put_priest(img, 330, 1240, scale=2.3, rim=(255, 150, 90), bell_up=0.6 * hold, lantern_pole=False)
        if hold > 0.05:
            tl = with_alpha(tal, hold)
            img.alpha_composite(tl, (int(bell_p[0] - tl.width / 2), int(bell_p[1] - tl.height - 20)))
        put_mei(img, 860, 1240, facing=-1, scale=2.2, rim=(255, 180, 110), tremble=0.6 * math.sin(t * 20) * hold)
        z = 1.04 + 0.12 * ease(t / D)
        cx, cy = 560, 860 + 60 * hold
        img = zoom(img, z, cx, cy)
        arr = arr_of(img)
        add_glow(arr, LGLOW_BIG, *zmap(LX, LY + lan.height * 0.45, z, cx, cy), 0.45 * (0.92 + 0.08 * math.sin(t * 9)))
        if hold > 0.05:
            add_glow(arr, glow_sprite(140, (255, 220, 110), 1.6), *zmap(bell_p[0], bell_p[1] - 120, z, cx, cy), 0.4 * hold)
        arr = compose(arr, [centered(lt1, 1500 - 1500 + 200, ease((t - t1) / 0.4) * (1 - ease((t - t2 + 0.2) / 0.3))),
                            centered(lt2, 170, ease((t - t2) / 0.4)), centered(lt3, 290, ease((t - t2 - 0.5) / 0.4))])
        return post(arr, t, vig=VIG_HEAVY, tint=(1.06, 0.98, 0.9))
    return f


def shed(moon_k=1.0):
    """Plank shed at night: vertical boards, a high slatted window with moonlight shafts, straw on the floor."""
    y = np.linspace(0, 1, H)[:, None, None]
    base = Image.fromarray(np.repeat(np.array([10, 16, 16]) * (1 - y) + np.array([30, 34, 30]) * y, W, axis=1).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(base)
    rnd = random.Random(3)
    for x in range(0, W, 72):
        c = rnd.randint(22, 34)
        d.rectangle([x + 2, 0, x + 70, 1350], fill=(c, c + 4, c + 2, 255))
        d.line([(x, 0), (x, 1350)], fill=(6, 8, 8, 255), width=4)
        for _ in range(2):
            yy = rnd.uniform(100, 1300)
            d.ellipse([x + 26, yy, x + 40, yy + 22], fill=(14, 18, 16, 255))
    d.rectangle([0, 1350, W, H], fill=(36, 32, 22, 255))
    for _ in range(260):
        x, yy = rnd.uniform(0, W), rnd.uniform(1350, H)
        a = rnd.uniform(0, math.pi)
        d.line([(x, yy), (x + math.cos(a) * 30, yy + math.sin(a) * 6)], fill=(120, 100, 60, 255), width=2)
    # window
    d.rectangle([700, 180, 980, 360], fill=(70, 130, 116, 255))
    for k in range(5):
        d.rectangle([700 + k * 60, 180, 712 + k * 60, 360], fill=(6, 8, 8, 255))
    d.rectangle([700, 180, 980, 360], outline=(6, 8, 8, 255), width=14)
    return base


def moon_shafts(t, k=1.0):
    m = Image.new("L", (W // 4, H // 4), 0)
    d = ImageDraw.Draw(m)
    for j in range(4):
        x0 = (712 + j * 60 + 10) / 4
        d.polygon([(x0, 180 / 4), (x0 + 12, 180 / 4), (x0 - 80, 1500 / 4), (x0 - 120, 1500 / 4)], fill=110)
    m = m.filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
    a = np.asarray(m).astype(np.float32)[..., None] / 255
    return a * np.array(MOONLIGHT, np.float32) * 0.5 * k * (0.92 + 0.08 * math.sin(t * 0.8))


class Dust:
    def __init__(self, n=50, seed=2):
        rnd = random.Random(seed)
        self.q = [(rnd.uniform(0, W), rnd.uniform(200, 1500), rnd.uniform(0, 6), rnd.uniform(6, 20)) for _ in range(n)]

    def draw(self, arr, t, k=1.0, wind=0.0):
        for x, y, ph, sp in self.q:
            xx = (x + math.sin(t * 0.5 + ph) * 30 + wind * t * 400 * (sp / 13)) % W
            yy = y + math.cos(t * 0.4 + ph) * 20
            arr[int(yy):int(yy) + 3, int(xx):int(xx) + 3] += 60 * k


DUST = Dust()


def make_paper(D, caps):
    base = shed()
    t1, t2 = caps[1][1], caps[2][1]
    XS = (250, 540, 830)
    FEET = 1400
    SC = 0.5

    def f(t):
        img = base.copy()
        lift = ease((t - t1 - 0.6) / 1.6)
        fly = ease((t - t2 - 0.2) / 1.4)
        for k, x in enumerate(XS):
            if k == 1:
                ang = -1.0 * lift + 0.3 * math.sin(t * 10) * lift
                p = jsf(SC, arms=0.0, eyes=0.0, paper=0.0 if fly > 0 else 1.0, paper_ang=ang)
            else:
                p = jsf(SC, arms=0.0, eyes=0.0, paper=1.0)
            img.alpha_composite(p, (int(x - p.width / 2), int(FEET - p.height)))
        face = jsf(SC).info["face"]
        fx, fy = XS[1] - jsf(SC).width / 2 + face[0], FEET - jsf(SC).height + face[1]
        # the paper blows away (it's drawn separately once it leaves the face)
        if fly > 0:
            tl = talisman(SC * 1.42).rotate(-t * 400 % 360, Image.BICUBIC, expand=True)
            px, py = fx + 600 * fly, fy - 120 - 500 * fly + 120 * math.sin(fly * 6)
            img.alpha_composite(tl, (int(px - tl.width / 2), int(py - tl.height / 2)))
        walk = ease(t / max(0.5, t1 - 0.2))
        mx = -60 + (fx - 140 + 60) * walk
        tip = put_mei(img, mx, FEET + 10, facing=1, scale=2.0, walking=walk < 0.98, phase=t * 6, candle=1.0 - 0.0,
                      reach=lift * 0.8, rim=(255, 190, 120))
        z = 1.0 + 0.7 * ease((t - t1 + 0.3) / 1.6) - 0.25 * fly
        cx, cy = fx - 60, fy + 120
        img = zoom(img, z, cx, cy)
        arr = arr_of(img)
        arr += moon_shafts(t)
        flame = 1 - ease((t - t2 - 0.3) / 0.5)
        tx, ty = zmap(*tip, z, cx, cy)
        add_glow(arr, CGLOW, tx, ty, 0.9 * flame * (0.9 + 0.1 * math.sin(t * 23)) + 0.4 * flame)
        if fly > 0:
            add_glow(arr, PGLOW, *zmap(fx + 600 * fly, fy - 120 - 500 * fly + 120 * math.sin(fly * 6), z, cx, cy), 0.7)
        DUST.draw(arr, t, 1.0, wind=2.0 * ease((t - t2) / 0.3))
        arr *= 0.75 + 0.25 * flame
        return post(arr, t, vig=VIG_HEAVY, tint=(1.0, 1.0, 0.96))
    return f


def make_wake(D, caps):
    base = shed()
    t0, t1, t2 = caps[0][1], caps[1][1], caps[2][1]
    SC = 1.25
    FEET = 1760

    def f(t):
        img = base.copy()
        eyes = ease((t - t0 - 1.0) / 0.5)
        arms = ease((t - t1 - 0.2) / 1.4)
        jump = ease((t - t2 - 0.3) / 0.25) * (1 - ease((t - t2 - 0.7) / 0.25))
        p = jsf(SC, arms=arms, eyes=eyes, paper=0.0)
        y = FEET - 140 * jump
        img.alpha_composite(p, (int(W / 2 - p.width / 2), int(y - p.height)))
        face = (W / 2 - p.width / 2 + p.info["face"][0], y - p.height + p.info["face"][1])
        z = 2.0 - 0.95 * ease((t - t1 + 0.2) / 1.8)
        cx, cy = face[0], face[1] + 200 * (1 - ease((t - t1) / 1.8)) + 120
        img = zoom(img, z, cx, cy)
        amp = 18 * ease((t - t2 - 0.95) / 0.05) * (1 - ease((t - t2 - 1.0) / 0.5))
        img = shake_img(img, t, amp)
        arr = arr_of(img)
        arr += moon_shafts(t, 0.8)
        if eyes > 0:
            ex, ey = zmap(*face, z, cx, cy)
            add_glow(arr, glow_sprite(int(220 * z / 2) + 10, (120, 255, 180), 1.8), ex, ey - 20 * z, 0.35 * eyes)
        DUST.draw(arr, t, 1.0 + 2 * ease((t - t2 - 0.95) / 0.1))
        if t2 + 0.95 < t < t2 + 1.05:
            arr *= 1.3
        return post(arr, t, vig=VIG_HEAVY, tint=(0.94, 1.04, 1.0))
    return f


def make_cliff(D, caps):
    base = shed()
    d = ImageDraw.Draw(base)
    t1, t2 = caps[1][1], caps[2][1]
    big_t = text_img("PART 2 IS UP NOW", font(LORA, 96, "Bold"), fill=CREAM, glow=(40, 170, 120, 255), pad=24)
    sub_t = text_img("Watch it next on our channel", font(INTER_M, 42), fill=(226, 236, 232, 255), pad=12)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bg2 = jade_sky(moon=(820, 330), moon_r=60, seed=21)
    bg2 = Image.fromarray((np.asarray(bg2).astype(np.float32) * 0.6).astype(np.uint8))

    def f(t):
        if t < t1 - 0.2:
            # side-tracking chase: Mei runs for the door, the Jiangshi hops after her, gaining
            u = t / (t1 - 0.2)
            cam = 200 * u
            img = base.copy().crop((0, 0, W, H))
            mx = 520 + 260 * u
            put_mei(img, mx - cam, 1420, facing=1, scale=2.0, walking=True, run=True, phase=t * 9, rim=(160, 220, 200))
            jx = 80 + 560 * ease(u)
            hy = hop_y(t, 0.0, 0.65, 70)
            put_js(img, jx - cam, 1420 + hy, 0.62, arms=1.0, eyes=1.0, paper=0.0)
            amp = 7 if (t % 0.65) > 0.45 else 0
            img = shake_img(img, t, amp)
            arr = arr_of(img)
            arr += moon_shafts(t, 0.8)
            return post(arr, t, vig=VIG_HEAVY, tint=JADE_TINT)
        # face to face: one breath away
        img = bg2.copy()
        u = ease((t - t1 + 0.2) / 1.6)
        p = jsf(1.05, arms=1.0, eyes=1.0, paper=0.0)
        px = 720 - 60 * u
        img.alpha_composite(p, (int(px - p.width / 2), int(1900 - p.height + 260 - 200 * u)))
        m = mf(0.95, light=0.8, look=0.8, eyes=1.0 + 0.2 * u, warm=(0.96, 1.04, 1.0))
        img.alpha_composite(m, (int(330 - m.width / 2), int(1320 - m.height + 60)))
        z = 1.0 + 0.1 * ease((t - t1) / 3.0)
        img = zoom(img, z, 520, 900)
        arr = arr_of(img)
        # her breath: small pale puffs drifting toward it
        ph = (t * 0.8) % 1.0
        add_glow(arr, glow_sprite(60, (200, 230, 220), 1.4), *zmap(330 + 200 * ph, 1150 - 40 * ph, z, 520, 900), 0.4 * (1 - ph))
        a1 = ease((t - t2 + 0.2) / 0.5)
        arr = post(arr, t, vig=VIG_HEAVY, tint=JADE_TINT)
        if a1 > 0:
            arr *= 1 - 0.45 * a1
            arr = compose(arr, [centered(big_t, 220, a1), centered(sub_t, 360, ease((t - t2 - 0.3) / 0.5))])
        return arr
    return f


# ======================================================================= P2
def make_recap(D, caps):
    base = shed()
    tal = talisman(0.5).rotate(80, Image.BICUBIC, expand=True)
    base.alpha_composite(tal, (140, 1560))
    hdr = series_header("CHINA", "PART 2")
    t1 = caps[1][1]

    def f(t):
        img = base.copy()
        put_mei(img, 860, 1440, facing=-1, scale=2.0, rim=(160, 220, 200), tremble=0.8 * math.sin(t * 22))
        u = ease((t - t1 + 0.8) / 3.0)
        jx = 200 + 360 * u
        hy = hop_y(t, t1 - 0.8, 0.65, 70) if t > t1 - 0.8 else 0.0
        put_js(img, jx, 1440 + hy, 0.62, arms=1.0, eyes=1.0, paper=0.0)
        z = 1.03 + 0.06 * t / D
        arr = arr_of(zoom(img, z, 540, 1000))
        arr += moon_shafts(t, 0.9)
        add_glow(arr, PGLOW, *zmap(190, 1610, z, 540, 1000), 0.4)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, vig=VIG_HEAVY, tint=JADE_TINT)
    return f


def make_breath(D, caps):
    t0, t1, t2 = caps[0][1], caps[1][1], caps[2][1]
    bg = jade_sky(moon=None, seed=33, top=(4, 10, 12), bot=(24, 44, 40))
    memo = text_img("HOLD YOUR BREATH...", font(LORA, 78, "Italic"), fill=(255, 214, 120, 255), glow=(160, 110, 20, 230), pad=20)
    memo2 = text_img("...and it cannot find you", font(LORA, 54, "Italic"), fill=(240, 226, 200, 255), pad=16)
    ghost_p, _, _, _ = priest(3.0, color=(70, 58, 40, 255), rim=(255, 220, 160), bell_up=0.8, lantern_pole=False)

    def f(t):
        img = bg.copy()
        hold = ease((t - t2) / 0.5)
        if t < t2 - 0.1:
            # memory: the priest's silhouette fades in behind her
            ga = ease((t - t1 + 0.4) / 0.8) * 0.7
            if ga > 0.01:
                img.alpha_composite(with_alpha(ghost_p, ga), (int(860 - ghost_p.width / 2), int(1500 - ghost_p.height)))
            m = mf(1.25, light=0.9, look=0.0, eyes=1.0 + 0.25 * ease((t - t0 - 0.3) / 0.5), warm=(1.02, 1.0, 0.94))
            img.alpha_composite(m, (int(540 - m.width / 2), int(1500 - m.height + 120)))
            z = 1.0 + 0.08 * t / t2
            arr = arr_of(zoom(img, z, 540, 900))
            arr = compose(arr, [centered(memo, 220, ease((t - t1) / 0.5)), centered(memo2, 340, ease((t - t1 - 0.8) / 0.5))])
            return post(arr, t, vig=VIG_HEAVY, tint=JADE_TINT)
        # two-shot: she holds her breath, its face sways left... then right, searching
        ln = caps[2][2] - t2
        sn = 0.0
        if t > t2 + ln * 0.35:
            sn = -ease((t - t2 - ln * 0.35) / (ln * 0.25)) + 2 * ease((t - t2 - ln * 0.65) / (ln * 0.3))
        p = jsf(1.0, arms=1.0, eyes=1.0, paper=0.0, sniff=sn)
        px = 700 + 110 * sn
        img.alpha_composite(p, (int(px - p.width / 2), int(1880 - p.height - 120)))
        m = mf(1.0, light=0.85, look=0.9, eyes=1.1, hold=hold, warm=(0.98, 1.02, 0.96))
        img.alpha_composite(m, (int(300 - m.width / 2), int(1360 - m.height + 60)))
        z = 1.02 + 0.06 * ease((t - t2) / ln)
        arr = arr_of(zoom(img, z, 520, 900))
        pulse = 0.5 + 0.5 * math.sin(t * 7)
        arr[..., 0] += 22 * hold * pulse * (VIG_HEAVY[..., 0] < 0.8)
        return post(arr, t, vig=VIG_HEAVY, tint=JADE_TINT)
    return f


def make_bell(D, caps):
    t0, t1, t2 = caps[0][1], caps[1][1], caps[2][1]
    base = shed()
    d = ImageDraw.Draw(base)
    door = (20, 520, 250, 1400)
    bg = jade_sky(moon=None, seed=41, top=(6, 10, 12), bot=(30, 40, 38))
    slap_t = t1 + 2.4

    def f(t):
        if t < t1 - 0.1:
            # close-up: her chest burns (red pulse), the ghost face hovering just behind
            img = bg.copy()
            p = jsf(1.0, arms=1.0, eyes=1.0, paper=0.0, sniff=1.0)
            img.alpha_composite(p, (int(780 - p.width / 2), int(1880 - p.height - 80)))
            m = mf(1.2, light=0.85, look=0.6, eyes=1.0, hold=1.0, warm=(1.04, 0.98, 0.94))
            img.alpha_composite(m, (int(430 - m.width / 2), int(1450 - m.height + 120)))
            u = t / max(0.1, t1)
            img = shake_img(zoom(img, 1.05 + 0.1 * u, 480, 900), t, 2 + 3 * u)
            arr = arr_of(img)
            pulse = (0.5 + 0.5 * math.sin(t * (7 + 5 * u))) * (0.4 + 0.6 * u)
            arr[..., 0] += 50 * pulse * (1 - VIG_HEAVY[..., 0])
            arr[..., 1:] *= 1 - 0.25 * pulse * (1 - VIG_HEAVY)
            return post(arr, t, vig=VIG_HEAVY)
        img = base.copy()
        dd = ImageDraw.Draw(img)
        op = ease((t - t1 - 0.6) / 0.5)
        dd.rectangle(door, fill=(int(30 + 200 * op), int(34 + 140 * op), int(30 + 80 * op), 255))
        enter = ease((t - t1 - 0.9) / 1.2)
        frozen = t > slap_t
        put_js(img, 600, 1430, 0.62, arms=1.0, eyes=0.0 if frozen else 1.0, paper=ease((t - slap_t) / 0.15),
               facing=1, rim=MOONLIGHT)
        put_mei(img, 920, 1430, facing=-1, scale=2.0, rim=(160, 220, 200), tremble=0.0 if frozen else 0.8 * math.sin(t * 22))
        bell_p, _ = put_priest(img, 60 + 330 * enter, 1430, scale=2.1, rim=(255, 190, 120), lantern_pole=False,
                               walking=0.02 < enter < 0.98, phase=t * 8, bell_up=0.3 + 0.5 * math.sin(t * 16) ** 2 if t < slap_t - 0.6 else 1.0)
        z = 1.0 + 0.1 * ease((t - slap_t) / 2.0)
        cx, cy = 560, 1000
        img = zoom(img, z, cx, cy)
        amp = 12 * ease((t - slap_t) / 0.04) * (1 - ease((t - slap_t - 0.05) / 0.4))
        img = shake_img(img, t, amp)
        arr = arr_of(img)
        arr += moon_shafts(t, 0.7)
        add_glow(arr, glow_sprite(320, (255, 190, 110), 1.6), *zmap(135, 960, z, cx, cy), 0.5 * op)
        if frozen:
            fl = math.exp(-(t - slap_t) * 4)
            add_glow(arr, glow_sprite(300, (255, 220, 110), 1.4), *zmap(640, 1020, z, cx, cy), 1.2 * fl + 0.15)
        if t > t2:
            ph = ((t - t2) * 0.6) % 1.0
            add_glow(arr, glow_sprite(50, (200, 230, 220), 1.4), *zmap(870 - 120 * ph, 1150 - 30 * ph, z, cx, cy), 0.5 * (1 - ph))
        return post(arr, t, vig=VIG_HEAVY, tint=JADE_TINT)
    return f


def make_dawn(D, caps):
    sw = W + 400
    top, bot = (40, 70, 96), (236, 176, 150)
    far, mid = mountain_world(sw, 51, top=top, bot=bot, moon=None, far_col=(120, 130, 150, 255), mid_col=(60, 74, 84, 255),
                              mist_col=(240, 214, 210))
    water = river(sw, WATER_Y + 20, H, top=(150, 130, 140), bot=(40, 50, 64), seed=6)
    bw = boardwalk(sw, WATER_Y, color=(30, 30, 36, 255))
    h, g, hk = stilt_house(0.7, seed=9, color=(30, 32, 40, 255), roof=(40, 44, 52, 255))
    houses = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    houses.alpha_composite(h, (int(180 - h.width / 2), int(WATER_Y + 30 - h.height)))
    mist = Mist(16, seed=9, y0=WATER_Y - 120, y1=WATER_Y + 40, color=(250, 230, 226), alpha=80, w=W)
    sun = glow_sprite(480, (255, 200, 170), 1.3)

    def f(t):
        cam = 400 * ease(t / D)
        img = view(far, mid, cam=cam)
        img.alpha_composite(water.crop((int(cam), 0, int(cam) + W, H)))
        img.alpha_composite(houses.crop((int(cam), 0, int(cam) + W, H)))
        img.alpha_composite(bw.crop((int(cam), 0, int(cam) + W, H)))
        put_mei(img, 330 - cam, WATER_Y + 2, facing=1, scale=1.3, color=(30, 24, 28, 255), rim=(255, 210, 190))
        lead = 820 + 560 * t / D - cam
        bell_p, lan_p = put_priest(img, lead, WATER_Y + 2, scale=0.95, color=(30, 28, 34, 255), rim=(255, 200, 170),
                                   walking=True, phase=t * 5, bell_up=0.4 + 0.3 * math.sin(t * 8))
        for k in range(3):
            x = lead - 110 - k * 95
            put_js(img, x, WATER_Y + 2 + hop_y(t, 0.1 * k, 0.8, 26), 0.25, arms=1.0, rim=(255, 210, 190))
        img.alpha_composite(mist.layer(t, 1.0))
        arr = arr_of(img)
        add_glow(arr, sun, 700 - cam * 0.3, 900, 0.45)
        if lan_p:
            add_glow(arr, LGLOW, *lan_p, 0.6)
        reflect(arr, 700 - cam * 0.3, WATER_Y + 40, 500, (255, 210, 180), k=0.6, t=t, width=80)
        z = 1.12 - 0.1 * ease(t / D)
        arr = arr_of(zoom(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA"), z, 540, 1100 - 150 * ease(t / D)))
        fog_layer(arr, t, k=0.15, color=(240, 220, 214), y0=0.45)
        return post(arr, t, tint=(1.04, 1.0, 0.98))
    return f


_BG = None


def xbg():
    global _BG
    if _BG is None:
        _BG = xiangyun_bg()
    return _BG


def make_explain(D, caps):
    R = 200
    med = Image.new("RGBA", (R * 4, R * 4), (0, 0, 0, 0))
    ImageDraw.Draw(med).ellipse([4, 4, R * 4 - 4, R * 4 - 4], fill=(14, 32, 32, 255), outline=GOLD, width=6)
    med = down(med)
    p = jiangshi_front(0.5, arms=1.0, eyes=0.0, paper=1.0)
    mask = Image.new("L", med.size, 0)
    ImageDraw.Draw(mask).ellipse([6, 6, med.width - 6, med.height - 6], fill=255)
    inner = Image.new("RGBA", med.size, (0, 0, 0, 0))
    inner.alpha_composite(p, (int(med.width / 2 - p.width / 2), int(-10)))
    med.alpha_composite(Image.composite(inner, Image.new("RGBA", med.size, (0, 0, 0, 0)), mask))
    lbl = text_img("CHINESE  FOLKLORE", font(INTER_M, 30), fill=GOLD, pad=10)
    title = text_img("Jiangshi", font(LORA, 120, "Bold"), fill=CREAM, glow=(40, 150, 110, 210), pad=20)
    hz = text_img("僵尸", cjk(64), fill=(230, 70, 50, 255), pad=10)
    sub = text_img("means “stiff corpse”", font(INTER_M, 40), fill=(226, 236, 232, 255), pad=8)
    pf = font(INTER_SB, 32)
    pills = [pill(n, pf, fill=(16, 40, 40, 230)) for n in ("Qing dynasty official's robes", "Paper talisman stops it")]
    c1, c2 = card(450, 330), card(450, 330)
    d1 = ImageDraw.Draw(c1)
    d1.text((225, 80), "HUNAN", font=font(LORA, 50, "Bold"), fill=(255, 214, 77, 255), anchor="mm")
    for i, ln in enumerate(("Priests walked", "the dead home", "only at night,", "ringing bells")):
        d1.text((225, 150 + i * 42), ln, font=font(INTER_M, 30), fill=(226, 220, 210, 255), anchor="mm")
    d2 = ImageDraw.Draw(c2)
    tl = talisman(0.62)
    c2.alpha_composite(tl, (int(225 - tl.width / 2), 30))
    d2.text((225, 205), "Old tales:", font=font(INTER_M, 30), fill=(226, 220, 210, 255), anchor="mm")
    d2.text((225, 250), "hold your breath", font=font(INTER_SB, 34), fill=CREAM, anchor="mm")
    d2.text((225, 290), "to hide from it", font=font(INTER_SB, 34), fill=CREAM, anchor="mm")
    p1t = caps[1][1] + 0.2
    p2t = caps[1][1] + 1.6
    ta = caps[2][1] + 0.2
    tb = caps[2][1] + (caps[2][2] - caps[2][1]) * 0.55

    def f(t):
        arr = xbg().copy()
        fog_layer(arr, t, speed=8, k=0.16, color=(60, 110, 96), y0=0.3)
        layers = [(med, (W / 2 - med.width / 2, 110 + 6 * math.sin(t)), ease(t / 0.7)),
                  centered(lbl, 530, ease((t - 0.3) / 0.6)),
                  (title, (W / 2 - (title.width + hz.width) / 2, 556 - 8 * ease(t / 1.0)), ease((t - 0.4) / 0.8)),
                  (hz, (W / 2 - (title.width + hz.width) / 2 + title.width, 600), ease((t - 0.8) / 0.8)),
                  centered(sub, 730, ease((t - caps[0][1] - 1.6) / 0.6))]
        y = 820
        for p_, tt in zip(pills, (p1t, p2t)):
            layers.append((p_, (W / 2 - p_.width / 2, y - 10 * ease((t - tt) / 0.4)), ease((t - tt) / 0.4))); y += 84
        cy = 1000
        layers.append((c1, (60, cy + 16 * (1 - ease((t - ta) / 0.5))), ease((t - ta) / 0.5)))
        layers.append((c2, (570, cy + 16 * (1 - ease((t - tb) / 0.5))), ease((t - tb) / 0.5)))
        return post(compose(arr, layers), t)
    return f


def make_outro(D, caps):
    q = text_img("Could YOU hold", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    q2 = text_img("your breath?", font(LORA, 96, "Bold"), fill=CREAM, glow=(40, 150, 110, 210), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Hold it!", (20, 80, 70, 235)), ("RUN!", (150, 30, 30, 235)),
            ("Ring the bell", (120, 90, 20, 235)), ("Sticky rice", (60, 60, 70, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    rows = [chips[0:2], chips[2:4]]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(214, 226, 222, 255), pad=10)
    tl = talisman(0.9)

    def f(t):
        arr = xbg().copy()
        fog_layer(arr, t, speed=8, k=0.16, color=(60, 110, 96), y0=0.3)
        layers = [(tl, (W / 2 - tl.width / 2, 40 + 8 * math.sin(t * 2)), ease(t / 0.6) * 0.9),
                  centered(q, 330, ease(t / 0.6)), centered(q2, 450, ease((t - 0.2) / 0.6))]
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
