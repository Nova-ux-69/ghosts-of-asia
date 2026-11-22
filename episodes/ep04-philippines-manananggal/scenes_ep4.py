"""Episode 4: Manananggal (Philippines), vertical scenes.
New world for this episode: a tropical barrio at dusk and at night (bahay kubo nipa huts on stilts, capiz-shell
windows, coconut palms, a big mango tree, bamboo fences, fireflies), a warm lamplit bamboo room, a dawn sky,
and a woven banig-pattern explainer. Camera: dusk tracking shot, window-frame reveals, a crane-down onto the
roof, low-angle push-ins, a night-to-dawn time-lapse."""
import sys, os, math, random
_EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _EP); sys.path.insert(1, os.path.join(_EP, "..", "..", "toolkit"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *
from art_ep4 import *
from scenes_v import (GY, VIG, VIG_HEAVY, GRAIN, GRAIN_HEAVY, GOLD, CREAM, arr_of, fog_layer, post,
                      compose, centered, pill, series_header, header_layers, card)

NIGHT_MIST = (90, 140, 130)
TEAL_TINT = (0.92, 1.03, 1.0)


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


def place(img, im, x, feet_y):
    img.alpha_composite(im, (int(x - im.width / 2), int(feet_y - im.height)))


def boy_on(img, x, feet_y, **kw):
    b, feet = boy(**kw)
    img.alpha_composite(b, (int(x - feet[0]), int(feet_y - feet[1])))


def zmap(x, y, z, cx, cy):
    """Where a point lands after zoom(img, z, cx, cy)."""
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


class Fireflies:
    def __init__(self, n=26, seed=3, area=(0, 700, W, 1250), color=(200, 255, 140)):
        rnd = random.Random(seed)
        self.q = [dict(x=rnd.uniform(area[0], area[2]), y=rnd.uniform(area[1], area[3]), f=rnd.uniform(0.2, 0.6),
                       ph=rnd.uniform(0, 6.3), r=rnd.uniform(14, 40)) for _ in range(n)]
        self.spr = glow_sprite(16, color, 1.4)

    def draw(self, arr, t, k=1.0, dx=0.0):
        for q in self.q:
            x = q["x"] + q["r"] * math.sin(t * q["f"] + q["ph"]) - dx
            y = q["y"] + q["r"] * 0.6 * math.cos(t * q["f"] * 1.3 + q["ph"])
            br = (0.5 + 0.5 * math.sin(t * q["f"] * 4 + q["ph"])) ** 2
            add_glow(arr, self.spr, x % W, y, br * k)


def ground_layer(w, y0=GY, color=EARTH, seed=3):
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, y0, w, H], fill=color)
    rnd = random.Random(seed)
    for _ in range(w // 9):
        x = rnd.uniform(0, w); hh = rnd.uniform(8, 26)
        d.line([(x, y0 + 4), (x + rnd.uniform(-6, 6), y0 - hh)], fill=color, width=3)
    return img


def barrio(sw, seed, sky_top, sky_bot, moon=None, moon_r=90, huts=(), palms=(), fence=True, mango=None, lit=True,
           far_col=JUNGLE_FAR, mid_col=JUNGLE_MID, stars=140):
    """Static layered village strip. Returns (far RGBA wide W+sw*0.3, near RGBA sw wide, list of glow points)."""
    fw = int(W + sw * 0.3) + 10
    far = sky(sky_top, sky_bot, moon=moon, moon_r=moon_r, stars=stars, seed=seed, w=fw)
    far.alpha_composite(jungle_line(fw, GY - 200, 120, far_col, seed=seed, r0=50, r1=120))
    near = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    near.alpha_composite(jungle_line(sw, GY - 60, 60, mid_col, seed=seed + 1, r0=30, r1=70))
    rnd = random.Random(seed)
    for px, ph in palms:
        pt = palm_tree(rnd.uniform(0.75, 1.0), seed=rnd.randint(0, 99), color=SILH, height=ph)
        near.alpha_composite(pt, (int(px - pt.width / 2), int(GY + 10 - pt.height)))
    glows = []
    if mango is not None:
        mt = mango_tree(mango[1], seed=seed)
        near.alpha_composite(mt, (int(mango[0] - mt.width / 2), int(GY + 14 - mt.height)))
    for hx, hs, hl in huts:
        hut, info = bahay_kubo(hs, seed=int(hx), lit=hl and lit)
        ox, oy = int(hx - hut.width / 2), int(GY + 12 - hut.height)
        near.alpha_composite(hut, (ox, oy))
        glows += [(ox + gx, oy + gy) for gx, gy in info["glows"]]
    near.alpha_composite(ground_layer(sw, GY, seed=seed))
    if fence:
        near.alpha_composite(bamboo_fence(sw, GY + 40))
    return far, near, glows


def view(far, near, cam=0.0):
    fx = int(cam * 0.3)
    img = far.crop((fx, 0, fx + W, H))
    img.alpha_composite(near.crop((int(cam), 0, int(cam) + W, H)))
    return img


WGLOW = glow_sprite(120, LAMP, 2.0)
CGLOW = glow_sprite(90, CAPIZ, 2.0)


# ======================================================================= P1
def make_hook(D, caps):
    far, near, glows = barrio(W, 4, SKY_TOP, SKY_BOT, moon=(700, 640), moon_r=120, huts=((380, 1.3, True),),
                              palms=((930, 640), (100, 520)), fence=False)
    base = view(far, near)
    hdr = series_header("PHILIPPINES", "PART 1")
    t2 = caps[1][1]
    ff = Fireflies(18, seed=4, area=(0, 900, W, 1250))

    def f(t):
        img = base.copy()
        # a winged shape crosses the moon (the viewer sees it; nobody in the story does yet)
        u = (t - 0.6) / 4.2
        if 0 < u < 1:
            ws = wing_shadow(t * 2.2, 0.5)
            x = 1350 - 1700 * u
            y = 700 - 80 * math.sin(math.pi * u)
            img.alpha_composite(ws, (int(x - ws.width / 2), int(y - ws.height / 2)))
        arr = arr_of(img)
        flick = 0.85 + 0.15 * random.Random(int(t * 10)).random()
        for gx, gy in glows:
            add_glow(arr, WGLOW, gx, gy, 0.5 * flick)
        ff.draw(arr, t, 0.8)
        z = 1 + 0.05 * t / D + 0.22 * ease((t - t2) / 2.5)
        arr = arr_of(zoom(to_img(arr), z, 420, 980))
        fog_layer(arr, t, k=0.25, color=NIGHT_MIST)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, tint=TEAL_TINT)
    return f


def make_village(D, caps):
    sw = 2500
    far, near, glows = barrio(sw, 14, (12, 22, 44), (168, 92, 64), moon=None, huts=((620, 0.85, True), (1500, 0.95, True)),
                              palms=((180, 600), (1050, 680), (1900, 560), (2350, 700)), fence=True, stars=30,
                              far_col=(30, 34, 46, 255), mid_col=(16, 18, 26, 255))
    # Lito's hut (window that closes) is drawn per frame from a small cache
    states = {}
    hx = 2050
    span = 1350
    t_shut = caps[1][1] + 0.6
    perch = wing_shadow(0.0, 0.16, flap=-1.0)
    eye = glow_sprite(8, (255, 210, 60), 1.4)

    def hut_state(k):
        k = round(k, 1)
        if k not in states:
            states[k] = bahay_kubo(1.15, seed=7, lit=True, window_open=k)
        return states[k]

    def f(t):
        cam = span * ease(t / D * 0.92 + 0.04)
        img = view(far, near, cam)
        wo = 1 - ease((t - t_shut) / 1.6)
        hut, info = hut_state(wo)
        ox, oy = int(hx - cam - hut.width / 2), int(GY + 12 - hut.height)
        img.alpha_composite(hut, (ox, oy))
        # the shape perched on the far palm, wings folded
        px, py = 1500 - cam, GY + 12 - 532 + 6 - perch.height * 0.12
        img.alpha_composite(perch, (int(px - perch.width / 2), int(py - perch.height / 2)))
        boy_on(img, 380 + 120 * t / D, GY + 30, phase=t * 2 * math.pi * 0.9, walking=True, facing=1, scale=1.8,
               rim=(255, 170, 110))
        arr = arr_of(img)
        for gx, gy in glows:
            add_glow(arr, WGLOW, gx - cam, gy, 0.45)
        for gx, gy in info["glows"]:
            add_glow(arr, CGLOW if wo < 0.5 else WGLOW, ox + gx, oy + gy, 0.55)
        blink = 1.0 if (t * 0.7) % 1 > 0.1 else 0.0
        for s_ in (-1, 1):
            add_glow(arr, eye, px + s_ * 5, py - perch.height / 2 + 175 * 0.16 - 2, 0.9 * blink)
        fog_layer(arr, t, k=0.18, color=(150, 100, 90))
        return post(arr, t, tint=(1.04, 0.97, 0.95))
    return f


def bamboo_room(warm=1.0, window=None, seed=0):
    """Inside a bahay kubo: bamboo slat walls, floor mats, a beam. Returns RGBA base."""
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([40, 26, 14]) * warm + np.array([10, 20, 30]) * (1 - warm)
    bot = np.array([90, 60, 30]) * warm + np.array([16, 28, 40]) * (1 - warm)
    grad = np.repeat(top * (1 - y) + bot * y, W, axis=1)
    base = Image.fromarray(grad.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(base)
    rnd = random.Random(seed)
    slat = tuple(int(v) for v in (np.array([70, 48, 24]) * warm + np.array([20, 32, 40]) * (1 - warm)))
    for x in range(0, W, 26):
        d.line([(x, 260), (x, 1150)], fill=slat + (255,), width=3)
        if rnd.random() < 0.5:
            yy = rnd.randint(300, 1100)
            d.line([(x - 6, yy), (x + 6, yy)], fill=slat + (255,), width=4)
    beam = tuple(max(0, v - 25) for v in slat)
    d.rectangle([0, 230, W, 270], fill=beam + (255,))
    d.rectangle([0, 600, W, 616], fill=beam + (255,))
    floor = tuple(int(v) for v in (np.array([120, 90, 50]) * warm + np.array([26, 36, 44]) * (1 - warm)))
    d.rectangle([0, 1150, W, H], fill=floor + (255,))
    for x in range(-400, W + 400, 40):
        d.line([(x, 1150), (x + 300, H)], fill=tuple(max(0, v - 18) for v in floor) + (255,), width=4)
        d.line([(x + 300, 1150), (x, H)], fill=tuple(max(0, v - 10) for v in floor) + (255,), width=3)
    return base


def capiz_window(w, h, open_k=0.0, outside=None, frame=(40, 26, 14, 255), shell=(250, 234, 196, 255)):
    """A large capiz window seen from inside: a sliding panel of small square shells. outside: RGBA shown where open."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if outside is not None:
        img.alpha_composite(outside.resize((w, h)) if outside.size != (w, h) else outside)
    d = ImageDraw.Draw(img)
    pw = int(w * (1 - open_k))
    if pw > 2:
        panel = Image.new("RGBA", (w, h), shell)
        pd = ImageDraw.Draw(panel)
        n = 9
        for k in range(1, n):
            pd.line([(w * k / n, 0), (w * k / n, h)], fill=frame, width=6)
        m = int(n * h / w)
        for k in range(1, m + 1):
            pd.line([(0, h * k / (m + 1)), (w, h * k / (m + 1))], fill=frame, width=6)
        img.alpha_composite(panel.crop((w - pw, 0, w, h)), (0, 0))
        d.rectangle([pw - 8, 0, pw + 6, h], fill=frame)
    d.rectangle([0, 0, w - 1, h - 1], outline=frame, width=22)
    return img


def make_warn(D, caps):
    base = bamboo_room(1.0, seed=2)
    win = capiz_window(420, 520, 0.0)
    base.alpha_composite(win, (70, 420))
    d = ImageDraw.Draw(base)
    d.rectangle([780, 860, 1040, 880], fill=(50, 30, 14, 255))         # shelf by the door
    d.rectangle([870, 300, 1080, 1150], fill=(28, 16, 8, 255))          # door
    jar = salt_jar(1.1); base.alpha_composite(jar, (790, 860 - jar.height))
    gl = garlic(0.8); base.alpha_composite(gl, (930, 860 - gl.height))
    lt1 = text_img("KEEP THE WINDOWS SHUT.", font(LORA, 64, "Bold"), fill=CREAM, glow=(170, 60, 10, 230), pad=20)
    lt2 = text_img("SALT BY THE DOOR.", font(LORA, 64, "Bold"), fill=CREAM, glow=(170, 60, 10, 230), pad=20)
    ta = caps[1][1] + 0.1
    tb = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.5
    lamp_g = glow_sprite(420, LAMP, 1.5)
    jar_g = glow_sprite(130, (230, 250, 255), 2.0)

    def f(t):
        img = base.copy()
        lu = ease(t / 1.5)
        lm, feet, hand = lola(scale=1.55, lamp_up=lu)
        lx = 470
        img.alpha_composite(lm, (int(lx - feet[0]), int(1160 - feet[1])))
        ga, fp = gasera(1.2, flame=0.8 + 0.2 * math.sin(t * 13))
        hx, hy = lx - feet[0] + hand[0], 1160 - feet[1] + hand[1]
        img.alpha_composite(ga, (int(hx - ga.width / 2), int(hy - ga.height * 0.75)))
        # slow pan from the window toward the salt jar
        u = ease((t - tb + 0.4) / 2.0)
        z = 1.08 + 0.06 * t / D
        cx = 420 + 360 * u
        img = zoom(img, z, cx, 860)
        arr = arr_of(img)
        sx, sy = zmap(hx, hy - 40, z, cx, 860)
        add_glow(arr, lamp_g, sx, sy, 0.45 * (0.9 + 0.1 * math.sin(t * 11)))
        jx, jy = zmap(850, 800, z, cx, 860)
        add_glow(arr, jar_g, jx, jy, 0.35 * ease((t - tb) / 0.5))
        arr = compose(arr, [centered(lt1, 170, ease((t - ta) / 0.4)), centered(lt2, 290, ease((t - tb) / 0.4))])
        return post(arr, t, vig=VIG_HEAVY, tint=(1.06, 0.98, 0.9))
    return f


def outside_view(w, h, legs_k=1.0, seed=5, t=0.0):
    """What Lito sees through the window: moonlit yard, mango tree, and (tiny) the standing legs."""
    img = sky((6, 20, 26), (40, 80, 76), moon=(int(w * 0.8), int(h * 0.18)), moon_r=40, stars=60, seed=seed, w=w, h=h)
    gy = int(h * 0.78)
    img.alpha_composite(jungle_line(w, gy - 60, 50, JUNGLE_FAR, seed=seed, r0=24, r1=50).crop((0, 0, w, h)))
    mt = mango_tree(0.42, seed=3)
    img.alpha_composite(mt, (int(w * 0.5 - mt.width / 2), gy + 6 - mt.height))
    if legs_k > 0:
        lg = legs(0.24, t, mist=True)
        img.alpha_composite(with_alpha(lg, legs_k), (int(w * 0.5 - lg.width / 2), gy + 2 - lg.height))
    ImageDraw.Draw(img).rectangle([0, gy, w, h], fill=EARTH)
    return img


def make_open(D, caps):
    base = bamboo_room(0.35, seed=4)
    WX, WY, WW, WH = 150, 430, 620, 600
    outside = outside_view(WW, WH, legs_k=1.0)
    t_open = caps[1][1] + 0.3
    moon_g = glow_sprite(380, (150, 220, 210), 1.6)

    def f(t):
        img = base.copy()
        k = 0.55 * ease((t - t_open) / 1.4)
        img.alpha_composite(capiz_window(WW, WH, k, outside, frame=(18, 22, 24, 255), shell=(120, 130, 128, 255)), (WX, WY))
        # Lito fans himself, then pushes the panel
        fan = 0.35 + 0.35 * math.sin(t * 9) if t < t_open - 0.4 else 0.0
        boy_on(img, 860, 1260, walking=False, facing=-1, scale=3.4, rim=(140, 220, 205),
               arm_out=max(fan, 0.9 * ease((t - t_open + 0.4) / 0.8)))
        z = 1 + 0.05 * t / D + 0.25 * ease((t - t_open - 0.6) / 2.5)
        img = zoom(img, z, 470, 760)
        arr = arr_of(img)
        mx, my = zmap(WX + WW * 0.75, WY + WH * 0.35, z, 470, 760)
        add_glow(arr, moon_g, mx, my, 0.35 * k / 0.55 if k else 0)
        return post(arr, t, vig=VIG_HEAVY, tint=(0.9, 1.02, 1.04))
    return f


def make_legs(D, caps):
    far, near, glows = barrio(W, 24, (4, 14, 18), (30, 70, 66), moon=(860, 420), moon_r=70, huts=((90, 0.5, True),),
                              palms=((1000, 560),), fence=False, mango=(560, 1.3))
    base = view(far, near)
    ff = Fireflies(30, seed=9, area=(80, 700, 1000, 1250))
    t1, t2 = caps[1][1], caps[2][1]
    dap = glow_sprite(160, (170, 230, 210), 1.4)

    def f(t):
        img = base.copy()
        lg = legs(1.2, t)
        img.alpha_composite(lg, (int(560 - lg.width / 2), int(GY + 30 - lg.height)))
        arr = arr_of(img)
        for gx, gy in glows:
            add_glow(arr, WGLOW, gx, gy, 0.5)
        add_glow(arr, dap, 560, GY - 160, 0.35 + 0.05 * math.sin(t * 1.3))
        ff.draw(arr, t, 0.9)
        z = 1 + 0.08 * t / D + 0.25 * ease((t - t1) / 1.6) + 0.18 * ease((t - t2) / 0.6)
        img = zoom(to_img(arr), z, 560, 1000 + 40 * ease((t - t1) / 1.6))
        img = shake_img(img, t, 6 * ease((t - t2) / 0.3) * (1 - ease((t - t2 - 0.8) / 0.6)))
        arr = arr_of(img)
        if t2 < t < t2 + 0.1:
            arr *= 1.5
        fog_layer(arr, t, k=0.3, color=NIGHT_MIST)
        return post(arr, t, vig=VIG_HEAVY, tint=TEAL_TINT)
    return f


def make_cliff(D, caps):
    sky_bg = sky((2, 8, 12), (22, 48, 50), moon=(860, 360), moon_r=60, stars=120, seed=31)
    sky_bg.alpha_composite(jungle_line(W, GY - 220, 100, JUNGLE_FAR, seed=31))
    hut, info = bahay_kubo(1.9, seed=3, lit=True, window_open=0.55)
    HX, HY = 500, GY + 260
    sky_bg.alpha_composite(hut, (int(HX - hut.width / 2), int(HY - hut.height)))
    ox, oy = HX - hut.width / 2, HY - hut.height
    wx0, wy0, wx1, wy1 = info["win"]
    # Lito's small silhouette in the open part of the window
    lito, feet = boy(walking=False, facing=1, scale=1.6, rim=None, look_up=1.0)
    sky_bg.alpha_composite(lito.crop((0, 0, lito.width, int(lito.height * 0.42))),
                           (int(ox + wx1 - 70 - lito.width / 2), int(oy + wy1 - lito.height * 0.42 + 4)))
    roof_y = oy + 30
    t_land = caps[0][1]
    t2, t3 = caps[1][1], caps[2][1]
    big_t = text_img("PART 2 IS UP NOW", font(LORA, 96, "Bold"), fill=CREAM, glow=(20, 150, 120, 255), pad=24)
    sub_t = text_img("Watch it next on our channel", font(INTER_M, 42), fill=(226, 236, 232, 255), pad=12)
    eye = glow_sprite(14, (255, 210, 60), 1.4)

    def f(t):
        img = sky_bg.copy()
        u = ease((t - t_land) / 2.4)
        sc = 0.55
        flap = math.sin(t * 2 * math.pi * 1.1) * (1 - 0.7 * u) - 0.3 * u
        ws = wing_shadow(t, sc, flap=flap)
        cx = HX + 40
        cy = -300 + (roof_y + 10 + 300) * u
        img.alpha_composite(ws, (int(cx - ws.width / 2), int(cy - ws.height * 0.43)))
        z = 1 + 0.06 * t / D + 0.25 * ease((t - t2) / 2.0)
        img = zoom(img, z, 520, 640)
        flaps = 4 * abs(math.sin(t * 2 * math.pi * 1.1)) * (1 - u) * float(t > t_land)
        img = shake_img(img, t, flaps)
        arr = arr_of(img)
        for gx, gy in info["glows"]:
            add_glow(arr, WGLOW, *zmap(ox + gx, oy + gy, z, 520, 640), 0.6)
        ey = cy - 0.43 * ws.height + 175 * sc
        for s_ in (-1, 1):
            ex_, ey_ = zmap(cx + s_ * 9 * sc * 2, ey, z, 520, 640)
            add_glow(arr, eye, ex_, ey_, ease((t - t_land - 1.6) / 0.5))
        fog_layer(arr, t, k=0.25, color=NIGHT_MIST)
        a1 = ease((t - t3 + 0.2) / 0.5)
        arr = post(arr, t, vig=VIG_HEAVY, tint=TEAL_TINT)
        if a1 > 0:
            arr *= 1 - 0.4 * a1
            arr = compose(arr, [centered(big_t, 220, a1), centered(sub_t, 360, ease((t - t3 - 0.3) / 0.5))])
        return arr
    return f


# ======================================================================= P2
def make_recap(D, caps):
    far, near, glows = barrio(W, 44, SKY_TOP, SKY_BOT, moon=(820, 640), moon_r=80, huts=((830, 0.9, True),),
                              palms=((60, 600),), fence=False, mango=(300, 0.9))
    base = view(far, near)
    hdr = series_header("PHILIPPINES", "PART 2")
    lg = legs(0.6, 0.0)
    t2 = caps[1][1]
    ff = Fireflies(16, seed=12, area=(0, 900, W, 1250))

    def f(t):
        img = base.copy()
        l2 = legs(0.6, t)
        img.alpha_composite(l2, (int(300 - l2.width / 2), int(GY + 20 - l2.height)))
        u = ease((t - t2) / 1.8)
        if u > 0:
            ws = wing_shadow(t, 0.34, flap=math.sin(t * 7) * (1 - u) - 0.4 * u)
            img.alpha_composite(ws, (int(830 - ws.width / 2), int(-200 + (GY - 590 + 200) * u - ws.height * 0.45)))
        arr = arr_of(img)
        for gx, gy in glows:
            add_glow(arr, WGLOW, gx, gy, 0.5)
        ff.draw(arr, t, 0.8)
        arr = arr_of(zoom(to_img(arr), 1 + 0.06 * t / D, 560, 960))
        fog_layer(arr, t, k=0.24, color=NIGHT_MIST)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, tint=TEAL_TINT)
    return f


def make_face(D, caps):
    # inside looking out: the open window frames her as she rises
    sky_bg = sky((2, 10, 14), (24, 60, 58), moon=(820, 380), moon_r=70, stars=90, seed=51)
    t0, t1, t2 = caps[0][1], caps[1][1], caps[2][1]
    room = bamboo_room(0.3, seed=8)
    WX, WY, WW, WH = 60, 300, 960, 1060
    hole = Image.new("L", (W, H), 255)
    ImageDraw.Draw(hole).rectangle([WX, WY, WX + WW, WY + WH], fill=0)
    frame = room.copy(); frame.putalpha(hole)
    fd = ImageDraw.Draw(frame)
    fd.rectangle([WX - 10, WY - 10, WX + WW + 10, WY + WH + 10], outline=(14, 18, 20, 255), width=40)
    panel = capiz_window(int(WW * 0.22), WH, 0.0, None, frame=(14, 18, 20, 255), shell=(96, 110, 108, 255))
    frame.alpha_composite(panel, (WX, WY))

    def f(t):
        img = sky_bg.copy()
        rise = ease((t - t0) / 3.0)
        tilt = ease((t - t2) / 1.6)
        sc = 1.15
        m = manananggal(t, sc, eyes=ease((t - t0 - 1.5) / 0.6), hair_up=0.7, arms=0.3 * ease((t - t1) / 1.0),
                        span=0.9 + 0.1 * ease((t - t1) / 0.8))
        fx = 600
        fy = 1700 - (1700 - 720) * rise - 150 * tilt
        img.alpha_composite(m, (int(fx - m.width / 2), int(fy - 300 * sc)))
        img.alpha_composite(frame)
        z = 1.02 + 0.05 * t / D + 0.1 * ease((t - t1) / 1.5)
        img = zoom(img, z, 560, 900 + 160 * tilt)
        arr = arr_of(img)
        if t1 < t < t1 + 0.1:
            arr *= 1.4
        fog_layer(arr, t, k=0.2, color=NIGHT_MIST, y0=0.5)
        return post(arr, t, vig=VIG_HEAVY, tint=TEAL_TINT)
    return f


def make_lola(D, caps):
    base = bamboo_room(0.8, seed=10)
    ga, fp = gasera(1.3, flame=1.0)
    base.alpha_composite(ga, (160, 1150 - ga.height))
    jar = salt_jar(1.0)
    lamp_g = glow_sprite(380, LAMP, 1.5)
    t_push = caps[0][1] + 1.2
    t_now = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.75
    now_t = text_img("NOW!", font(LORA, 150, "Bold"), fill=CREAM, glow=(190, 70, 10, 240), pad=24)

    def f(t):
        img = base.copy()
        lu = 0.6 * ease((t - t_push) / 0.8)
        lm, feet, hand = lola(scale=1.6, lamp_up=lu, rim=(255, 180, 100))
        lx = 360
        img.alpha_composite(lm, (int(lx - feet[0]), int(1170 - feet[1])))
        hx, hy = lx - feet[0] + hand[0], 1170 - feet[1] + hand[1]
        bx = 820
        u = ease((t - t_push) / 1.0)
        jx = hx + (bx - 80 - hx) * u
        img.alpha_composite(jar, (int(jx - jar.width / 2 + 10), int(hy - jar.height / 2)))
        boy_on(img, bx, 1180, walking=False, facing=-1, scale=3.0, rim=(255, 190, 110), arm_out=0.8 * u,
               tremble=1.2 * math.sin(t * 24))
        img = zoom(img, 1.05 + 0.05 * t / D, 600, 860)
        img = shake_img(img, t, 6 * ease((t - t_now) / 0.2) * (1 - ease((t - t_now - 0.5) / 0.4)))
        arr = arr_of(img)
        add_glow(arr, lamp_g, 540 + (220 - 600) * 1.08, 960 + (1050 - 860) * 1.08, 0.5 * (0.9 + 0.1 * math.sin(t * 12)))
        arr = compose(arr, [centered(now_t, 190, ease((t - t_now) / 0.2))])
        return post(arr, t, vig=VIG_HEAVY, tint=(1.04, 0.98, 0.92))
    return f


def make_salt(D, caps):
    far, near, glows = barrio(W, 64, (3, 12, 16), (26, 64, 60), moon=(300, 420), moon_r=70, huts=((980, 0.6, True),),
                              palms=(), fence=False, mango=(520, 1.25))
    base = view(far, near)
    t_pour = caps[0][1] + 1.6
    t_scream = caps[1][1]
    rnd = random.Random(5)
    grains = [(rnd.uniform(-40, 40), rnd.uniform(0, 1.2), rnd.uniform(0.8, 1.3)) for _ in range(220)]
    spark = glow_sprite(5, (240, 250, 255), 1.0)
    flash = glow_sprite(260, (230, 255, 240), 1.2)

    def f(t):
        img = base.copy()
        lg = legs(0.9, t)
        tr = 2.5 * math.sin(t * 40) * ease((t - t_pour - 0.5) / 0.5)
        lg = lg.rotate(tr, Image.BICUBIC, center=(lg.width / 2, lg.height))
        img.alpha_composite(lg, (int(520 - lg.width / 2), int(GY + 26 - lg.height)))
        run = ease((t - 0.2) / max(0.3, t_pour - 0.8))
        bx = -120 + (330 + 120) * run
        boy_on(img, bx, GY + 40, phase=t * 2 * math.pi * 1.4, walking=run < 0.98, run=run < 0.98, facing=1, scale=2.4,
               rim=(160, 230, 215), arm_out=ease((t - t_pour + 0.3) / 0.4))
        # the creature, small and high in the sky, screaming
        sc = ease((t - t_scream + 0.6) / 0.8)
        if sc > 0:
            m = manananggal(t, 0.42, eyes=1.0, arms=sc, scream=sc, glow=0.9, hair_up=0.9)
            img.alpha_composite(with_alpha(m, sc), (int(760 - m.width / 2), int(300 + 20 * math.sin(t * 3) - 300 * 0.42)))
        arr = arr_of(img)
        for gx, gy in glows:
            add_glow(arr, WGLOW, gx, gy, 0.45)
        if t > t_pour:
            hx, hy = bx + 95, GY - 175
            for gx_, ph, sp in grains:
                u = ((t - t_pour) * sp + ph) % 1.2
                if t - t_pour < ph:
                    continue
                x = hx + 30 * u + gx_ * u * 0.8
                y = hy + 420 * u * u + 40 * u
                if y < GY + 10:
                    add_glow(arr, spark, x, y, 0.9)
        if t_scream < t < t_scream + 0.12:
            arr *= 1.5
        add_glow(arr, flash, 760, 330, 0.4 * ease((t - t_scream) / 0.3) * (1 - ease((t - t_scream - 0.8) / 1.0)))
        img = zoom(to_img(arr), 1.05 + 0.04 * t / D, 540, 860 - 160 * ease((t - t_scream + 0.6) / 1.2))
        img = shake_img(img, t, 8 * ease((t - t_scream) / 0.2) * (1 - ease((t - t_scream - 1.0) / 0.6)))
        arr = arr_of(img)
        fog_layer(arr, t, k=0.25, color=NIGHT_MIST)
        return post(arr, t, vig=VIG_HEAVY, tint=TEAL_TINT)
    return f


def make_dawn(D, caps):
    night_far, near, _ = barrio(W, 74, (3, 12, 16), (26, 64, 60), moon=None, huts=((850, 0.7, False),),
                                palms=((150, 640), (980, 560)), fence=True, mango=(470, 0.8), stars=120)
    dawn_far, _, _ = barrio(W, 74, (40, 60, 110), (255, 170, 110), moon=None, huts=(), palms=(), fence=False, stars=0,
                            far_col=(40, 40, 60, 255))
    n_arr = arr_of(night_far.crop((0, 0, W, H)))
    d_arr = arr_of(dawn_far.crop((0, 0, W, H)))
    sun = glow_sprite(520, (255, 200, 120), 1.3)
    disc = glow_sprite(90, (255, 240, 200), 0.6)
    t_sun = caps[1][1]

    def f(t):
        u = ease((t - 0.5) / (D - 1.0))
        bg = n_arr * (1 - u) + d_arr * u
        sy = GY - 120 + 260 * (1 - ease((t - t_sun + 1.0) / 2.5))
        add_glow(bg, sun, 600, sy, 0.9 * u)
        add_glow(bg, disc, 600, sy, 1.2 * ease((t - t_sun) / 1.5))
        img = to_img(bg)
        img.alpha_composite(near)
        # she circles, smaller and smaller, then melts into the light
        g = ease((t - t_sun) / 1.8)
        a = 1 - g
        if a > 0.02:
            ws = wing_shadow(t * 1.6, 0.3 * (1 - 0.6 * u))
            x = 600 + 260 * math.cos(t * 1.4)
            y = 520 + 80 * math.sin(t * 1.4) - 120 * u
            img.alpha_composite(with_alpha(ws, a), (int(x - ws.width / 2), int(y - ws.height / 2)))
        lg = legs(0.42, t, rim=(255, 190, 140))
        img.alpha_composite(with_alpha(lg, 1 - ease((t - t_sun - 0.6) / 1.2)), (int(470 - lg.width / 2), int(GY + 20 - lg.height)))
        img = zoom(img, 1.0 + 0.06 * t / D, 560, 900)
        arr = arr_of(img)
        fog_layer(arr, t, k=0.2 + 0.1 * u, color=(200, 150, 120))
        return post(arr, t, tint=(1.0 + 0.06 * u, 1.0, 1.0 - 0.04 * u))
    return f


_BG = None


def bbg():
    global _BG
    if _BG is None:
        _BG = banig_bg()
    return _BG


def make_explain(D, caps):
    R = 200
    med = Image.new("RGBA", (R * 4, R * 4), (0, 0, 0, 0))
    ImageDraw.Draw(med).ellipse([4, 4, R * 4 - 4, R * 4 - 4], fill=(10, 30, 32, 255), outline=GOLD, width=6)
    med = down(med)
    m = manananggal(1.0, 0.62, eyes=1.0, glow=0.0, hair_up=0.7, mist=True)
    mask = Image.new("L", med.size, 0)
    ImageDraw.Draw(mask).ellipse([6, 6, med.width - 6, med.height - 6], fill=255)
    inner = Image.new("RGBA", med.size, (0, 0, 0, 0))
    inner.alpha_composite(m, (int(med.width / 2 - m.width / 2), int(med.height / 2 - 300 * 0.62 + 10)))
    med.alpha_composite(Image.composite(inner, Image.new("RGBA", med.size, (0, 0, 0, 0)), mask))
    lbl = text_img("PHILIPPINE  FOLKLORE", font(INTER_M, 30), fill=GOLD, pad=10)
    title = text_img("Manananggal", font(LORA, 112, "Bold"), fill=CREAM, glow=(20, 140, 110, 210), pad=20)
    sub = text_img("from tanggal: “to separate”", font(INTER_M, 38), fill=(220, 236, 228, 255), pad=8)
    pf = font(INTER_SB, 34)
    pills = [pill(n, pf, fill=(14, 40, 40, 230)) for n in ("Huge bat-like wings", "Flies at night")]
    c1, c2 = card(450, 330), card(450, 330)
    jar = salt_jar(0.7); gl = garlic(0.6)
    c1.alpha_composite(jar, (int(225 - jar.width - 10), 40)); c1.alpha_composite(gl, (235, 60))
    d1 = ImageDraw.Draw(c1)
    d1.text((225, 215), "Salt, garlic or ash", font=font(INTER_SB, 32), fill=CREAM, anchor="mm")
    d1.text((225, 262), "on her lower half", font=font(INTER_M, 28), fill=(220, 210, 200, 255), anchor="mm")
    d1.text((225, 298), "= she can't rejoin", font=font(INTER_M, 28), fill=(220, 210, 200, 255), anchor="mm")
    d2 = ImageDraw.Draw(c2)
    d2.ellipse([165, 50, 285, 170], fill=(255, 190, 90, 255))
    for k in range(10):
        a = k * math.pi / 5
        d2.line([(225 + math.cos(a) * 72, 110 + math.sin(a) * 72), (225 + math.cos(a) * 96, 110 + math.sin(a) * 96)],
                fill=(255, 190, 90, 255), width=6)
    d2.text((225, 215), "SUNRISE", font=font(LORA, 44, "Bold"), fill=(255, 214, 77, 255), anchor="mm")
    d2.text((225, 262), "She must rejoin", font=font(INTER_M, 28), fill=(220, 210, 200, 255), anchor="mm")
    d2.text((225, 298), "before dawn", font=font(INTER_M, 28), fill=(220, 210, 200, 255), anchor="mm")
    p1t = caps[0][1] + (caps[0][2] - caps[0][1]) * 0.55
    p2t = caps[0][2] - 0.2
    ta = caps[2][1] + 0.3
    tb = caps[2][1] + (caps[2][2] - caps[2][1]) * 0.6

    def f(t):
        arr = bbg().copy()
        fog_layer(arr, t, speed=8, k=0.18, color=(40, 120, 110), y0=0.3)
        layers = [(med, (W / 2 - med.width / 2, 120 + 6 * math.sin(t)), ease(t / 0.7)),
                  centered(lbl, 540, ease((t - 0.3) / 0.6)),
                  centered(title, 570 - 8 * ease(t / 1.0), ease((t - 0.4) / 0.8)),
                  centered(sub, 735, ease((caps[1][1] - 0.2 - t) * -1 / 0.6) if t > caps[1][1] - 0.2 else 0.0)]
        tot = sum(p.width for p in pills) + 18
        x = W / 2 - tot / 2
        for p, tt in zip(pills, (p1t, p2t)):
            layers.append((p, (x, 830 - 10 * ease((t - tt) / 0.4)), ease((t - tt) / 0.4)))
            x += p.width + 18
        layers.append((c1, (60, 950 + 16 * (1 - ease((t - ta) / 0.5))), ease((t - ta) / 0.5)))
        layers.append((c2, (570, 950 + 16 * (1 - ease((t - tb) / 0.5))), ease((t - tb) / 0.5)))
        return post(compose(arr, layers), t)
    return f


def make_outro(D, caps):
    q = text_img("Would YOU open", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    q2 = text_img("the window?", font(LORA, 96, "Bold"), fill=CREAM, glow=(20, 140, 110, 210), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Never!", (20, 100, 90, 235)), ("Just a little", (20, 100, 90, 235)),
            ("Salt ready", (150, 70, 20, 235)), ("Call Lola!", (150, 70, 20, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    rows = [chips[0:2], chips[2:4]]
    cm = text_img("What did YOUR lola warn you about?", font(INTER_SB, 44), fill=(255, 200, 150, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(214, 226, 222, 255), pad=10)

    def f(t):
        arr = bbg().copy()
        fog_layer(arr, t, speed=8, k=0.18, color=(40, 120, 110), y0=0.3)
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
