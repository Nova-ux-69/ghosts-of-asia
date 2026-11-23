"""Episode 7: Ma Phae Wah (Myanmar), vertical scenes.
New world for this episode: a small Burmese town at midnight under a blood-red moon. A hilltop zedi with a hti
spire, teak houses on stilts with two-tier gable roofs, a dusty road lined with tamarind trees, an old graveyard of
whitewashed tombs under a banyan with hanging roots, a woven-bamboo room lit by a clay oil lamp, plank shutters
that let red moonlight through their gaps, a grey-red dawn with monks on the alms round, and an acheik-wave
explainer.
Camera: a wide street shot that pushes in on her turning head, a long pan from the graveyard to the house, an
over-the-shutter POV through a narrow gap, stop-motion approach cuts that jump closer, a low doorstep angle, a crane
down to the ribbon on the step."""
import sys, os, math, random
_EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _EP); sys.path.insert(1, os.path.join(_EP, "..", "..", "toolkit"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *
from art_ep7 import *
from scenes_v import (VIG, VIG_HEAVY, GRAIN, arr_of, fog_layer, post, compose, centered, pill, series_header,
                      header_layers, card)

GOLD = (214, 180, 116, 255)
CREAM = (244, 238, 226, 255)
RED_TINT = (1.06, 0.9, 0.88)
FOG_C = (90, 30, 30)
ROAD_Y = 1250


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


def stop(t, fps=6):
    """Stop-motion time: the ghost only updates a few times a second (it moves wrong)."""
    return math.floor(t * fps) / fps


_GS, _GF = {}, {}


def gs(scale, t, step=0.0, facing=1, turn=0.0, eyes=0.0, lower=0.0, wind=-0.8, rim=RIM_RED):
    key = (round(scale, 3), round(t * 12) / 12, round(step, 1), facing, round(turn, 2), round(eyes, 1), round(lower, 2), wind, rim)
    if key not in _GS:
        if len(_GS) > 260:
            _GS.clear()
        _GS[key] = ghost_side(key[0], key[1], key[2], facing, key[4], key[5], key[6], wind, rim)
    return _GS[key]


def gf(scale, t, eyes=1.0, tilt=0.0, part=0.5, coffin=True):
    key = (round(scale, 3), round(t * 12) / 12, round(eyes, 1), round(tilt, 1), round(part, 2), coffin)
    if key not in _GF:
        if len(_GF) > 200:
            _GF.clear()
        _GF[key] = ghost_front(key[0], key[1], key[2], key[3], key[4], coffin)
    return _GF[key]


def put_ghost(img, x, feet_y, scale, t, **kw):
    im, info = gs(scale, t, **kw)
    ox, oy = int(x - info["feet"][0]), int(feet_y - info["feet"][1])
    img.alpha_composite(im, (ox, oy))
    return ox + info["face"][0], oy + info["face"][1]


def put_side(img, fn, x, feet_y, **kw):
    r = fn(**kw)
    im, feet = r[0], r[1]
    img.alpha_composite(im, (int(x - feet[0]), int(feet_y - feet[1])))
    return r


def flash(arr, t, t0, color=(255, 40, 30), frames=3):
    if t0 <= t < t0 + frames / FPS:
        k = 1 - (t - t0) / (frames / FPS) * 0.5
        arr[:] = arr * (1 - 0.75 * k) + np.array(color, np.float32) * 0.75 * k
    return arr


LGLOW = glow_sprite(120, LAMP_GLOW, 1.7)
LGLOW_BIG = glow_sprite(520, (255, 80, 36), 1.8)
EYE = glow_sprite(40, (255, 230, 210), 1.5)
EMB = Embers(36, seed=3, area=(0, W, 300, 1700))
EMB_IN = Embers(26, seed=5, area=(0, W, 200, 1600), color=(255, 140, 70))
_MOVE = {}


# ======================================================================= the street (wide world)
def street(sw=W + 200, seed=1, dawn=False, moon=(820, 360)):
    """Midnight street layers: sky, hill with the zedi, a row of teak houses, tamarinds, the dusty road, grass."""
    key = (sw, seed, dawn, moon)
    if key in _MOVE:
        return _MOVE[key]
    if dawn:
        sky_ = crimson_sky(w=sw, moon=None, top=(26, 8, 12), bot=(150, 60, 34), stars=0, seed=seed)
        a = np.asarray(sky_).astype(np.float32)
        yy = np.linspace(0, 1, H)[:, None]
        a[..., :3] += (np.exp(-((yy - 0.55) / 0.12) ** 2) * 90)[..., None] * np.array([1.0, 0.55, 0.25])
        sky_ = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        far_c, mid_c, sil = (60, 24, 22, 255), (34, 14, 12, 255), (14, 6, 6, 255)
    else:
        sky_ = crimson_sky(w=sw, moon=moon, seed=seed)
        far_c, mid_c, sil = FARC, MIDC, SILH
    back = sky_.copy()
    back.alpha_composite(hill(sw, 1010, 50, far_c, seed + 2))
    z = zedi(0.62, color=far_c[:3] + (255,), rim=(255, 150, 80) if dawn else (255, 90, 60), gold=0.7 if dawn else 0.0)
    back.alpha_composite(z, (110, 1000 - z.height + 30))
    mid = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    rnd = random.Random(seed)
    x = -120
    while x < sw:
        if rnd.random() < 0.55:
            h_, _ = teak_house(rnd.uniform(0.42, 0.5), seed=int(x), color=mid_c, lit=rnd.choice((0, 0, 0.5)), plank=mid_c)
            mid.alpha_composite(h_, (int(x), 1180 - h_.height))
            x += h_.width + rnd.uniform(10, 60)
        else:
            tr = tamarind(rnd.uniform(0.45, 0.6), color=mid_c, seed=int(x))
            mid.alpha_composite(tr, (int(x), 1190 - tr.height))
            x += tr.width * 0.6
    road = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(road)
    d.rectangle([0, 1170, sw, H], fill=sil)
    rc = (54, 20, 16) if not dawn else (96, 50, 34)
    for y in range(1180, 1420, 4):                                                    # dusty road band, lit by the moon
        k = 1 - abs((y - 1290) / 120)
        d.line([(0, y), (sw, y)], fill=tuple(int(c * (0.35 + 0.65 * k)) for c in rc) + (255,))
    for _ in range(sw // 7):
        xx, yy = rnd.uniform(0, sw), rnd.uniform(1185, 1410)
        d.ellipse([xx, yy, xx + 3, yy + 2], fill=(20, 8, 6, 255))
    road.alpha_composite(grass(sw, 1430, color=sil, seed=seed + 4, hgt=90))
    _MOVE[key] = (back, mid, road)
    return back, mid, road


def street_view(layers, cam=0.0):
    back, mid, road = layers
    img = back.crop((int(cam * 0.3), 0, int(cam * 0.3) + W, H))
    img.alpha_composite(mid.crop((int(cam * 0.7), 0, int(cam * 0.7) + W, H)))
    img.alpha_composite(road.crop((int(cam), 0, int(cam) + W, H)))
    return img


# ======================================================================= P1
def make_hook(D, caps):
    L = street(W + 200, seed=1)
    hdr = series_header("MYANMAR", "PART 1")
    t2 = caps[1][1]
    stop_t = t2 - 0.4
    fg = tamarind(1.3, seed=9)

    def f(t):
        img = street_view(L, cam=40 * t / D)
        ts = stop(min(t, stop_t), 5)
        x = 120 + 440 * ts / stop_t
        turn = ease((t - t2 - 0.2) / 1.2)
        fx, fy = put_ghost(img, x, ROAD_Y + 40, 0.56, t, step=ts * 5, turn=turn, eyes=ease((t - t2 - 0.9) / 0.3))
        img.alpha_composite(fg, (W - fg.width + 330, H - fg.height + 120))
        z = 1.0 + 0.05 * t / D + 1.0 * ease((t - t2 + 0.2) / 1.8)
        cx, cy = x + 40 * ease((t - t2) / 1.8), 900 + (fy - 900) * ease((t - t2) / 1.8)
        jump = t2 + 1.6
        if t > jump:
            z += 0.6 * ease((t - jump) / 0.12)
            cx, cy = fx, fy
        img = zoom(img, z, cx, cy)
        if t > jump:
            g = gf(1.5, t, eyes=1.0, tilt=35 + 4 * math.sin(t * 30), part=0.7)
            img.alpha_composite(g, (int(W / 2 - g.width / 2 - 60), int(1000 - g.info["face"][1])))
        img = shake_img(img, t, 16 * ease((t - jump) / 0.05) * (1 - ease((t - jump - 0.1) / 0.5)))
        arr = arr_of(img)
        if turn > 0.6 and t < jump:
            ex, ey = zmap(fx, fy, z, cx, cy)
            add_glow(arr, glow_sprite(int(40 * z) + 4, (255, 200, 180), 1.6), ex, ey, 0.35 * ease((t - t2 - 0.9) / 0.3))
        EMB.draw(arr, t, 0.7)
        fog_layer(arr, t, k=0.25, color=FOG_C, y0=0.55)
        flash(arr, t, jump)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
    return f


def make_town(D, caps):
    """Long pan from the graveyard (left) to Thiri's house (right). A woman in yellow stands among the tombs:
    the viewer sees her, nobody in the story does."""
    sw = W + 760
    back = crimson_sky(w=sw, moon=(1500, 330), seed=4)
    back.alpha_composite(hill(sw, 1030, 40, FARC, 6))
    z = zedi(0.5, color=FARC, rim=(255, 90, 60))
    back.alpha_composite(z, (1120, 1030 - z.height + 30))
    gy = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    by = banyan(1.1, color=MIDC, seed=2)
    gy.alpha_composite(by, (-200, 1260 - by.height))
    rnd = random.Random(7)
    graves = []
    for i in range(11):
        sc = rnd.uniform(0.45, 0.7)
        x, y = rnd.uniform(-40, 760), rnd.uniform(1230, 1400)
        graves.append((y, x, sc, i))
    gy.alpha_composite(grass(sw, 1240, color=SILH, seed=3, hgt=60))
    yard = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
    for y, x, sc, i in sorted(graves):
        tb = tomb(sc, seed=i, col=(104, 82, 78))
        yard.alpha_composite(tb, (int(x), int(y - tb.height)))
    house_open, info = teak_house(1.0, seed=3, lit=1.0, shutter=0.85, rim=(150, 34, 24))
    house_shut, _ = teak_house(1.0, seed=3, lit=1.0, shutter=0.0, rim=(150, 34, 24))
    hx, hy = 1040, 1420 - house_open.height
    tr = tamarind(0.9, seed=5)
    fg = grass(sw, 1560, color=SILH, seed=8, hgt=120)
    t2 = caps[1][1]
    ghost_on = (0.6, 4.6)

    def f(t):
        u = ease(t / (D - 0.3))
        cam = (sw - W) * u
        img = back.crop((int(cam * 0.5), 0, int(cam * 0.5) + W, H))
        layer = gy.copy()
        # the woman in yellow among the tombs (flickers out with a glitch)
        if ghost_on[0] < t < ghost_on[1] and not (3.1 < t < 3.2):
            put_ghost(layer, 520 + (40 if t > 3.2 else 0), 1300, 0.3, t, step=0.0, wind=-0.6)
        layer.alpha_composite(yard)
        sh = 1 - ease((t - t2 - 0.3) / 0.8)
        hs = house_open if sh > 0.5 else house_shut
        layer.alpha_composite(tr, (hx - 520, 1430 - tr.height))
        layer.alpha_composite(hs, (hx, hy))
        if sh > 0.5:   # Grandma's dark shape in the lit window, reaching for the shutters
            wx, wy = hx + info["win"][0], hy + info["win"][1]
            ImageDraw.Draw(layer).ellipse([wx - 22, wy - 30, wx + 22, wy + 14], fill=(16, 6, 4, 255))
            ImageDraw.Draw(layer).rectangle([wx - 34, wy + 10, wx + 34, wy + 70], fill=(16, 6, 4, 255))
        img.alpha_composite(layer.crop((int(cam), 0, int(cam) + W, H)))
        img.alpha_composite(fg.crop((int(cam * 1.2) % (sw - W), 0, int(cam * 1.2) % (sw - W) + W, H)))
        arr = arr_of(img)
        wx, wy = hx + info["win"][0] - cam, hy + info["win"][1]
        add_glow(arr, LGLOW_BIG, wx, wy + 40, 0.35 * (0.4 + 0.6 * sh) * (1 + 0.1 * math.sin(t * 17)))
        if ghost_on[0] < t < ghost_on[1]:
            add_glow(arr, glow_sprite(60, (200, 150, 40), 1.5), 520 + 30 - cam, 1180, 0.25)
        fog_layer(arr, t, k=0.3, color=FOG_C, y0=0.55)
        EMB.draw(arr, t, 0.5)
        return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
    return f


def room(seed=0, slats=1.0, lamp_x=210, lamp_y=1500, shutter_x=640):
    wall = bamboo_wall(seed=seed)
    fr = shutter_frame(360, 520, open_=0.0, slat_light=slats, seed=seed)
    wall.alpha_composite(fr, (shutter_x, 520))
    floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(floor)
    d.rectangle([0, 1560, W, H], fill=(30, 12, 8, 255))
    for y in range(1560, H, 46):
        d.line([(0, y), (W, y)], fill=(16, 6, 4, 255), width=3)
    wall.alpha_composite(floor)
    lamp, fp = oil_lamp(1.0)
    wall.alpha_composite(lamp, (lamp_x - lamp.width // 2, lamp_y - lamp.height))
    return wall, (lamp_x - lamp.width // 2 + fp[0], lamp_y - lamp.height + fp[1])


def lamp_light(arr, t, lp, k=1.0, big=0.55, small=True):
    fl = 1 + 0.12 * math.sin(t * 19) + 0.08 * math.sin(t * 31 + 1)
    add_glow(arr, LGLOW_BIG, lp[0], lp[1] + 80, big * k * fl)
    if small:
        add_glow(arr, LGLOW, lp[0], lp[1], 0.9 * k * fl)


def darken_far(arr, lp, k=0.55):
    yy, xx = np.mgrid[0:H:8, 0:W:8]
    d = np.sqrt((xx - lp[0]) ** 2 + (yy - lp[1]) ** 2) / 1400
    m = np.clip(1 - k * d, 0.25, 1).astype(np.float32)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    arr *= m[..., None]
    return arr


def mouth_open(t, caps, idx=None, speed=11):
    for i, (txt, a, b) in enumerate(caps):
        if (idx is None or i in idx) and a <= t <= b:
            return 0.5 + 0.5 * abs(math.sin(t * speed))
    return 0.0


def make_warn(D, caps):
    base, lp = room(seed=1, slats=0.6, lamp_x=160, lamp_y=1700, shutter_x=660)
    t2 = caps[1][1]

    def f(t):
        img = base.copy()
        u = ease((t - t2 + 0.2) / 2.0)
        sc = 1.6 + 0.2 * u
        g = grandma_front(round(sc, 3), mouth=mouth_open(t, caps, speed=10), look=0.4 * math.sin(t * 0.7) - 0.3 * u)
        img.alpha_composite(g, (int(440 - g.width / 2), int(900 - 310 * sc)))
        arr = arr_of(img)
        # a shadow slides across the shutter gaps behind her (only the viewer notices)
        if t > t2 + 0.4:
            sx = 640 + (t - t2 - 0.4) / 1.6 * 420
            if sx < 1100:
                yy, xx = np.mgrid[520:1040, 0:W]
                m = np.exp(-((xx - sx) / 60.0) ** 2)
                arr[520:1040] *= (1 - 0.8 * m)[..., None]
        lamp_light(arr, t, lp, small=False)
        arr = darken_far(arr, lp, 0.45)
        EMB_IN.draw(arr, t, 0.4)
        return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
    return f


def slit_mask(gap, cx=540, soft=6):
    """Black overlay with a vertical gap (looking out between two shutters)."""
    m = np.ones((H, W), np.float32)
    x0, x1 = int(cx - gap / 2), int(cx + gap / 2)
    m[:, max(0, x0):min(W, x1)] = 0
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(soft))).astype(np.float32) / 255
    return m[..., None]


def make_look(D, caps):
    base, lp = room(seed=2, slats=1.0, lamp_x=200, lamp_y=1640, shutter_x=600)
    close = bamboo_wall(seed=4)
    big = shutter_frame(W + 120, H + 120, open_=0.0, slat_light=1.0, seed=2)
    L = street(W + 200, seed=11, moon=(700, 420))
    t1, t2, t3 = caps[1][1], caps[2][1], caps[3][1]
    M = {g: slit_mask(g) for g in (40, 90, 140, 200, 260, 320)}

    def f(t):
        if t < t1 - 0.2:
            img = base.copy()
            put_side(img, thiri_side, 470 + 10 * ease(t / 2), 1640, facing=1, scale=3.0, rim=(255, 130, 70),
                     tremble=0.6 * math.sin(t * 20))
            arr = arr_of(zoom(img, 1.05 + 0.04 * t, 600, 1100))
            lamp_light(arr, t, zmap(*lp, 1.05 + 0.04 * t, 600, 1100))
            arr = darken_far(arr, lp, 0.4)
            return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
        if t < t3 - 0.2:
            # close on the shutter: red moonlight through the gaps; something passes outside (shuffle... shuffle)
            img = close.copy()
            op = 0.22 * ease((t - t2 - 0.4) / 1.4)
            sh = shutter_frame(W + 120, H + 120, open_=op, slat_light=1.0, seed=2) if op > 0.01 else big
            if op > 0.01:
                vis = Image.new("RGBA", (W, H), (0, 0, 0, 255))
                vis.alpha_composite(street_view(L, 60))
                img.alpha_composite(vis.crop((0, 0, W, H)))
            img.alpha_composite(sh, (-60, -60))
            if t2 - 0.2 < t:
                hd = put_side(img, thiri_side, 1020, 2100, facing=1, scale=3.4, rim=(255, 120, 60), reach=0.9 + 0.1 * op / 0.22)
            arr = arr_of(img)
            if t < t2:
                sx = -200 + 700 * stop(t - t1 + 0.2, 4)
                yy, xx = np.mgrid[0:H, 0:W]
                m = np.exp(-((xx - sx) / 110.0) ** 2) * (yy > 260)
                arr *= (1 - 0.85 * m)[..., None]
            return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
        # POV through the gap: the woman in yellow walks down the road with a coffin on her shoulder
        u = (t - t3 + 0.2) / (D - t3 + 0.2)
        img = street_view(L, 60)
        ts = stop(t, 6)
        put_ghost(img, 300 + 380 * stop(u, 5), ROAD_Y + 40, 0.62, t, step=ts * 5, facing=1)
        z = 1.25 + 0.2 * u
        img = zoom(img, z, 520, 1080)
        arr = arr_of(img)
        EMB.draw(arr, t, 0.6)
        fog_layer(arr, t, k=0.22, color=FOG_C, y0=0.55)
        arr = post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
        gap = min(M.keys(), key=lambda g: abs(g - (260 + 60 * u)))
        mk = M[gap]
        arr = arr * (1 - mk) + np.array((18, 7, 5), np.float32) * mk
        return arr
    return f


def make_call(D, caps):
    base, lp = room(seed=3, slats=0.8, lamp_x=120, lamp_y=1760, shutter_x=700)
    L = street(W + 200, seed=11, moon=(700, 420))
    t1, t2 = caps[1][1], caps[2][1]
    mk = slit_mask(300)
    fbg = crimson_sky(moon=(760, 330), moon_r=60, seed=31)
    jump = caps[2][2] + 0.25

    def f(t):
        if t < t1 - 0.15:
            img = base.copy()
            tf = thiri_front(1.6, look=0.6, mouth=mouth_open(t, caps, (0,), 9) * 0.7, fear=0.6)
            img.alpha_composite(tf, (int(560 - tf.width / 2), int(880 - 290 * 1.6)))
            arr = arr_of(zoom(img, 1.08 + 0.05 * t, 560, 1100))
            lamp_light(arr, t, zmap(*lp, 1.08, 560, 1100), 1.2)
            arr = darken_far(arr, lp, 0.35)
            return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
        if t < t2 - 0.1:
            img = street_view(L, 60)
            put_ghost(img, 300 + 380 * 0.95, ROAD_Y + 40, 0.62, t, step=0.0, wind=-1.0)
            z = 1.45 + 0.3 * ease((t - t1) / 2.0)
            img = zoom(img, z, 660, 1000)
            arr = arr_of(img)
            fog_layer(arr, t, k=0.22, color=FOG_C, y0=0.55)
            arr = post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
            return arr * (1 - mk) + np.array((18, 7, 5), np.float32) * mk
        # her head turns too far, then the jump: fast zoom, red flash, shake
        u = t - t2 + 0.1
        img = fbg.copy()
        tilt = 70 * ease(u / 1.8) + (6 * math.sin(t * 40) if u > 1.4 else 0)
        g = gf(1.15, t, eyes=ease((u - 0.9) / 0.15), tilt=tilt, part=0.35 + 0.4 * ease((u - 1.0) / 0.6))
        oy = int(880 - g.info["face"][1])
        img.alpha_composite(g, (int(W / 2 - g.width / 2), oy))
        face = (W / 2 - g.width / 2 + g.info["face"][0], oy + g.info["face"][1])
        z = 1.0 + 0.1 * ease(u / 2) + 1.2 * ease((t - jump) / 0.12)
        img = zoom(img, z, face[0], face[1] + 60)
        img = shake_img(img, t, 22 * ease((t - jump) / 0.04) * (1 - ease((t - jump - 0.1) / 0.6)))
        arr = arr_of(img)
        flash(arr, t, jump, frames=3)
        if t < jump:
            arr *= 0.75 + 0.25 * ease(u / 0.4)
        return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
    return f


def doorstep_scene(seed=5):
    """Low angle at the foot of Thiri's house: the steps on the right, the dusty yard, the road behind."""
    L = street(W + 200, seed=seed, moon=(300, 330))
    img = street_view(L, 100)
    h_, info = teak_house(2.2, seed=3, lit=0.6, shutter=0.0, rim=(170, 40, 26))
    hx, hy = 240, 1720 - h_.height
    img.alpha_composite(h_, (hx, hy))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1700, W, H], fill=(22, 8, 6, 255))
    for _ in range(400):
        x, y = random.uniform(0, W), random.uniform(1700, H)
        d.ellipse([x, y, x + 4, y + 2], fill=(40, 16, 12, 255))
    step = (hx + info["step"][0], hy + info["step"][1])
    return img, step


def make_cliff(D, caps):
    base, step = doorstep_scene()
    t1, t2 = caps[1][1], caps[2][1]
    big_t = text_img("PART 2 IS UP NOW", font(LORA, 96, "Bold"), fill=CREAM, glow=(200, 30, 30, 255), pad=24)
    sub_t = text_img("Watch it next on our channel", font(INTER_M, 42), fill=(236, 222, 214, 255), pad=12)
    # approach cuts: each cut she is closer (no frames in between)
    cuts = [(0.0, 140, 1640, 0.42), (1.3, 420, 1700, 0.6), (2.5, 640, 1790, 0.82), (3.5, 760, 1880, 1.0)]

    def f(t):
        img = base.copy()
        if t < t1 - 0.1:
            k = max(i for i, c in enumerate(cuts) if t >= c[0])
            _, x, fy, sc = cuts[k]
            glitch = any(c[0] <= t < c[0] + 2 / FPS for c in cuts[1:])
            put_ghost(img, x, fy, sc, t, step=0.0, facing=1, wind=-1.0)
            z = 1.0 + 0.02 * t
            img = zoom(img, z, 540, 1100)
            arr = arr_of(img)
            if glitch:
                arr[:, :, 0] = np.roll(arr[:, :, 0], 18, axis=1)
                arr *= 1.25
        else:
            u = ease((t - t1) / max(0.5, t2 - t1 - 0.3))
            put_ghost(img, 820, 1880, 1.0, t, step=0.0, facing=1, lower=0.85 * u, wind=-1.0)
            z = 1.05 + 0.25 * u
            img = zoom(img, z, 760, 1300)
            arr = arr_of(img)
        EMB.draw(arr, t, 0.6)
        fog_layer(arr, t, k=0.28, color=FOG_C, y0=0.6)
        arr = post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
        a1 = ease((t - t2 + 0.2) / 0.5)
        if a1 > 0:
            arr *= 1 - 0.5 * a1
            arr = compose(arr, [centered(big_t, 220, a1), centered(sub_t, 360, ease((t - t2 - 0.3) / 0.5))])
        return arr
    return f


# ======================================================================= P2
def make_recap(D, caps):
    base, step = doorstep_scene()
    hdr = series_header("MYANMAR", "PART 2")
    t1 = caps[1][1]

    def f(t):
        img = base.copy()
        u = ease((t - t1 + 0.4) / 3.0)
        put_ghost(img, 820, 1880, 1.0, t, step=0.0, facing=1, lower=0.3 + 0.55 * u, wind=-1.0)
        z = 1.08 + 0.12 * t / D
        img = zoom(img, z, 700, 1250)
        arr = arr_of(img)
        EMB.draw(arr, t, 0.6)
        fog_layer(arr, t, k=0.28, color=FOG_C, y0=0.6)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
    return f


def make_pray(D, caps):
    base, lp = room(seed=6, slats=1.0, lamp_x=560, lamp_y=1600, shutter_x=640)
    t1, t2 = caps[1][1], caps[2][1]
    out_t = caps[2][2] - 0.3
    shadow = Image.new("L", (W // 4, H // 4), 0)
    gim, _ = ghost_side(1.1, 0.0, 0.0, 1, 0.0, 0.0, 0.0, -0.6, None)
    sil = gim.split()[3].resize((gim.width // 4, gim.height // 4))

    def f(t):
        if t < t1 - 0.1:
            img = base.copy()
            p = ease((t - 0.6) / 1.2)
            put_side(img, grandma_side, 260 + 40 * p, 1570, facing=1, scale=3.1, pull=p, rim=(255, 130, 70))
            put_side(img, thiri_side, 820 - 260 * p, 1570, facing=1, scale=3.0, reach=0.6 * (1 - p), rim=(255, 130, 70))
            arr = arr_of(img)
            lamp_light(arr, t, lp)
            arr = darken_far(arr, lp, 0.45)
            return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
        if t < t2 - 0.1:
            img = base.copy()
            g = grandma_front(1.7, mouth=mouth_open(t, caps, (1,), 7) * 0.5, look=-0.5)
            img.alpha_composite(g, (int(560 - g.width / 2), int(900 - 310 * 1.7)))
            z = 1.1 + 0.08 * ease((t - t1) / 3)
            arr = arr_of(zoom(img, z, 560, 1100))
            lamp_light(arr, t, zmap(*lp, z, 560, 1100), 1.1)
            arr = darken_far(arr, lp, 0.4)
            return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
        # kneeling and praying by the lamp; a huge shadow with a coffin slides over the wall; then the lamp dies
        img = base.copy()
        put_side(img, grandma_side, 330, 1520, facing=1, scale=3.1, kneel=1.0, hands=1.0, rim=(255, 130, 70))
        put_side(img, thiri_side, 800, 1520, facing=-1, scale=3.0, kneel=1.0, hands=1.0, rim=(255, 130, 70),
                 tremble=0.8 * math.sin(t * 24))
        arr = arr_of(img)
        u = (t - t2) / (out_t - t2)
        sh = Image.new("L", (W // 4, H // 4), 0)
        sh.paste(sil, (int((-200 + 900 * u) / 4), int(180 / 4)))
        sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BILINEAR)).astype(np.float32)[..., None] / 255
        arr *= 1 - 0.75 * sh
        lit = 1.0 if t < out_t else max(0.0, 1 - (t - out_t) / 0.25)
        flick = 1.0 if t < out_t - 1.2 else (0.5 + 0.5 * (math.sin(t * 50) > -0.2))
        lamp_light(arr, t, lp, lit * flick)
        arr = darken_far(arr, lp, 0.45)
        if t > out_t:
            arr *= 0.25 + 0.75 * lit
        return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
    return f


def door_img(shake=0.0):
    img = bamboo_wall(seed=8)
    d = ImageDraw.Draw(img)
    x0, x1, y0, y1 = 200, 880, 260, 1760
    d.rectangle([x0 - 30, y0 - 30, x1 + 30, y1], fill=(16, 6, 4, 255))
    for k in range(6):
        xx = x0 + k * (x1 - x0) / 6
        tone = 0.8 + 0.2 * ((k * 3) % 4) / 3
        d.rectangle([xx + 3, y0, xx + (x1 - x0) / 6 - 3, y1], fill=tuple(int(c * tone) for c in (58, 26, 16)) + (255,))
    d.rectangle([x0 - 40, 900, x1 + 60, 950], fill=(30, 14, 8, 255))           # wooden bar
    d.rectangle([x1 + 40, 880, x1 + 80, 970], fill=(20, 8, 6, 255))
    d.rectangle([0, y1, W, H], fill=(26, 10, 6, 255))
    return img


def make_door(D, caps):
    base = door_img()
    t1, t2 = caps[1][1], caps[2][1]
    knocks = [caps[0][1] + caps[0][2] * 0.5 + k * 0.45 for k in range(3)]
    sbg = bamboo_wall(seed=9)
    L = street(W + 200, seed=13, moon=(540, 520))
    jump = caps[2][2] + 0.05
    win_closed = shutter_frame(820, 1100, open_=0.0, slat_light=1.0, seed=9)
    win_open = shutter_frame(820, 1100, open_=1.0, slat_light=1.0, seed=9)
    outside = street_view(L, 80).crop((130, 300, 950, 1400))

    def f(t):
        if t < t2 - 0.1:
            img = base.copy()
            hit = max([ease(1 - (t - k) / 0.18) if k <= t < k + 0.18 else 0 for k in knocks] + [0])
            img = shake_img(img, t, 10 * hit)
            z = 1.0 + (0.12 * ease((t - t1) / (t2 - t1)) if t > t1 else 0)
            arr = arr_of(zoom(img, z, 540, 1000))
            # red moonlight leaking under the door; the shadow of two feet blocks it
            yy = int(zmap(0, 1760, z, 540, 1000)[1])
            arr[max(0, yy - 14):yy + 4, :] += np.array((120, 20, 14), np.float32) * 0.8
            for fx in (470, 600):
                xx = int(zmap(fx, 0, z, 540, 1000)[0])
                arr[max(0, yy - 14):yy + 4, max(0, xx - 40):xx + 40] *= 0.2
            if hit > 0:
                arr *= 1 + 0.15 * hit
            return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
        # the closed shutter, slow push... then it bangs open and her face fills the window for a split second
        img = sbg.copy()
        img.alpha_composite(outside, (130, 300))
        if jump <= t < jump + 0.5:
            g = gf(1.6, t, eyes=1.0, tilt=-18, part=0.8, coffin=False)
            img.alpha_composite(g.crop((int(g.width / 2 - 410), 0, int(g.width / 2 + 410), 1100)), (130, 300))
        img.alpha_composite(win_open if t >= jump else win_closed, (130, 300))
        z = 1.0 + 0.12 * ease((t - t2) / (jump - t2)) + 0.45 * ease((t - jump) / 0.1) * (1 - ease((t - jump - 0.5) / 0.2))
        img = zoom(img, z, 540, 820)
        img = shake_img(img, t, 20 * ease((t - jump) / 0.04) * (1 - ease((t - jump - 0.1) / 0.6)))
        arr = arr_of(img)
        if t < jump:
            arr *= 0.85 + 0.15 * math.sin(t * 13)
        flash(arr, t, jump, frames=3)
        return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
    return f


def make_empty(D, caps):
    """Nobody there: the empty road through the open window, a few long black hairs floating down."""
    sbg = bamboo_wall(seed=9)
    L = street(W + 200, seed=13, moon=(540, 520))
    win_open = shutter_frame(820, 1100, open_=1.0, slat_light=1.0, seed=9)
    outside = street_view(L, 80).crop((130, 300, 950, 1400))
    hairs = [(random.uniform(200, 880), random.uniform(450, 1100), random.uniform(0, 6)) for _ in range(5)]

    def f(t):
        u = t / D
        img = sbg.copy()
        img.alpha_composite(outside, (130, 300))
        d = ImageDraw.Draw(img)
        for x, y, ph in hairs:
            yy = y + 160 * u
            pts = [(x + 20 * math.sin(ph + k * 0.5 + t * 1.5), yy + k * 30) for k in range(8)]
            d.line(pts, fill=(4, 2, 2, 255), width=3, joint="curve")
        img.alpha_composite(win_open, (130, 300))
        arr = arr_of(zoom(img, 1.05 + 0.1 * u, 540, 860))
        EMB.draw(arr, t, 0.5)
        return post(arr, t, vig=VIG_HEAVY, tint=RED_TINT)
    return f


def make_dawn(D, caps):
    L = street(W + 400, seed=21, dawn=True)
    h_, info = teak_house(1.1, seed=3, lit=0.0, shutter=0.0, color=(14, 6, 6, 255), plank=(40, 18, 12, 255), rim=(255, 140, 80))
    t1 = caps[1][1]
    planks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(planks)
    for k in range(9):
        y = k * 230
        tone = 0.85 + 0.15 * ((k * 5) % 3) / 2
        d.rectangle([0, y + 4, W, y + 226], fill=tuple(int(c * tone) for c in (92, 52, 34)) + (255,))
        for _ in range(14):
            yy = y + random.uniform(20, 210)
            d.line([(0, yy), (W, yy + random.uniform(-6, 6))], fill=(70, 38, 24, 255), width=2)

    def ribbon_img(t):
        im = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        pts = [(400 + k * 110, 1900 + 120 * math.sin(k * 0.8) + 16 * math.sin(t * 0.8 + k)) for k in range(14)]
        dr.line(pts, fill=RIBBON + (255,), width=70, joint="curve")
        dr.line([(p[0], p[1] - 18) for p in pts], fill=(255, 226, 120, 255), width=12, joint="curve")
        bx, by = 1080, 1980
        dr.polygon([(bx - 160, by - 90), (bx, by), (bx - 160, by + 90)], fill=RIBBON + (255,))
        dr.polygon([(bx + 160, by - 90), (bx, by), (bx + 160, by + 90)], fill=RIBBON + (255,))
        dr.ellipse([bx - 36, by - 36, bx + 36, by + 36], fill=(180, 130, 24, 255))
        return down(im)

    def f(t):
        if t < t1 - 0.15:
            u = t / t1
            img = street_view(L, 120 * u)
            img.alpha_composite(h_, (480, 1440 - h_.height))
            for k in range(4):
                x = -100 + 160 * k + 140 * t
                put_side(img, monk, x, 1300, scale=0.7, phase=t * 4 + k)
            arr = arr_of(zoom(img, 1.0 + 0.04 * u, 700, 1100))
            arr *= 0.95
            return post(arr, t, vig=VIG, tint=(1.04, 0.92, 0.86))
        u = ease((t - t1 + 0.15) / 2.5)
        img = planks.copy()
        img.alpha_composite(ribbon_img(t))
        arr = arr_of(zoom(img, 1.25 - 0.2 * u, 540, 1000))
        add_glow(arr, glow_sprite(500, (255, 160, 90), 1.8), 800, 400, 0.35)
        return post(arr, t, vig=VIG_HEAVY, tint=(1.04, 0.92, 0.86))
    return f


def card7(w, h):
    c = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle([2, 2, w * 2 - 3, h * 2 - 3], 40, fill=(22, 6, 8, 235), outline=(200, 150, 40, 255), width=4)
    return down(c)


def make_explain(D, caps):
    R = 200
    med = Image.new("RGBA", (R * 4, R * 4), (0, 0, 0, 0))
    ImageDraw.Draw(med).ellipse([4, 4, R * 4 - 4, R * 4 - 4], fill=(40, 8, 10, 255), outline=(220, 170, 50, 255), width=8)
    med = down(med)
    p = ghost_front(0.42, 0.3, eyes=0.6, tilt=0, part=0.55, coffin=True)
    mask = Image.new("L", med.size, 0)
    ImageDraw.Draw(mask).ellipse([6, 6, med.width - 6, med.height - 6], fill=255)
    inner = Image.new("RGBA", med.size, (0, 0, 0, 0))
    inner.alpha_composite(p, (int(med.width / 2 - p.width / 2 - 20), 10))
    med.alpha_composite(Image.composite(inner, Image.new("RGBA", med.size, (0, 0, 0, 0)), mask))
    lbl = text_img("BURMESE  FOLKLORE", font(INTER_M, 30), fill=GOLD, pad=10)
    title = text_img("Ma Phae Wah", font(LORA, 120, "Bold"), fill=CREAM, glow=(190, 30, 30, 220), pad=20)
    sub = text_img("means “yellow-ribbon lady”", font(INTER_M, 42), fill=(255, 214, 110, 255), pad=8)
    pf = font(INTER_SB, 34)
    pills = [pill(n, pf, outline=(220, 170, 50, 255), fill=(60, 12, 14, 230)) for n in ("Guardian spirit of graveyards", "A king made it official")]
    c1, c2 = card7(450, 340), card7(450, 340)
    d1 = ImageDraw.Draw(c1)
    d1.text((225, 80), "MIDNIGHT", font=font(LORA, 50, "Bold"), fill=(255, 214, 77, 255), anchor="mm")
    for i, ln in enumerate(("She carries", "a coffin on her", "shoulder through", "the town")):
        d1.text((225, 150 + i * 44), ln, font=font(INTER_M, 32), fill=(236, 222, 214, 255), anchor="mm")
    d2 = ImageDraw.Draw(c2)
    cf = down(coffin_side(0.9))
    c2.alpha_composite(cf, (int(225 - cf.width / 2), 40))
    for i, ln in enumerate(("Where she puts", "it down, someone", "falls sick")):
        d2.text((225, 200 + i * 44), ln, font=font(INTER_SB, 32), fill=CREAM, anchor="mm")
    p1t = caps[1][1] + 0.2
    p2t = caps[1][1] + 1.8
    ta = caps[2][1] + 0.2
    tb = caps[3][1] + 0.2
    BG = acheik_bg()

    def f(t):
        arr = BG.copy()
        fog_layer(arr, t, speed=8, k=0.16, color=(90, 24, 22), y0=0.3)
        layers = [(med, (W / 2 - med.width / 2, 110 + 6 * math.sin(t)), ease(t / 0.7)),
                  centered(lbl, 530, ease((t - 0.3) / 0.6)),
                  centered(title, 556 - 8 * ease(t / 1.0), ease((t - 0.4) / 0.8)),
                  centered(sub, 730, ease((t - caps[0][1] - 2.4) / 0.6))]
        y = 820
        for p_, tt in zip(pills, (p1t, p2t)):
            layers.append((p_, (W / 2 - p_.width / 2, y - 10 * ease((t - tt) / 0.4)), ease((t - tt) / 0.4))); y += 84
        cy = 1000
        layers.append((c1, (60, cy + 16 * (1 - ease((t - ta) / 0.5))), ease((t - ta) / 0.5)))
        layers.append((c2, (570, cy + 16 * (1 - ease((t - tb) / 0.5))), ease((t - tb) / 0.5)))
        arr = compose(arr, layers)
        EMB.draw(arr, t, 0.3)
        return post(arr, t)
    return f


def make_outro(D, caps):
    q = text_img("Would YOU open", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    q2 = text_img("the shutter?", font(LORA, 96, "Bold"), fill=CREAM, glow=(190, 30, 30, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Never!", (60, 12, 14, 235)), ("Just a peek", (150, 30, 30, 235)),
            ("Call out", (120, 90, 20, 235)), ("Pray with Grandma", (50, 40, 44, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    rows = [chips[0:2], chips[2:4]]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(236, 222, 214, 255), pad=10)
    BG = acheik_bg()
    rb = Image.new("RGBA", (600, 200), (0, 0, 0, 0))
    dr = ImageDraw.Draw(rb)
    dr.polygon([(140, 20), (300, 100), (140, 180)], fill=RIBBON + (255,))
    dr.polygon([(460, 20), (300, 100), (460, 180)], fill=RIBBON + (255,))
    dr.ellipse([270, 70, 330, 130], fill=(180, 130, 24, 255))
    rb = down(rb)

    def f(t):
        arr = BG.copy()
        fog_layer(arr, t, speed=8, k=0.16, color=(90, 24, 22), y0=0.3)
        layers = [(rb, (W / 2 - rb.width / 2, 180 + 8 * math.sin(t * 2)), ease(t / 0.6)),
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
