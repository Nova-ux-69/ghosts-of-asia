"""Episode 3: Kuchisake-onna (Japan), vertical scenes.
New world for this episode: a narrow Japanese residential street at night (block walls, utility poles and wires,
vending machines, sodium streetlights, a curved traffic mirror), a warm sepia flashback room, and a
seigaiha-pattern explainer. Camera: side-tracking dolly, flicker reveals, a convex-mirror shot, push-ins."""
import sys, os, math, random
_EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _EP); sys.path.insert(1, os.path.join(_EP, "..", "..", "toolkit"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *
from art_ep3 import *
from scenes_v import (GY, VIG, VIG_HEAVY, GRAIN, GRAIN_HEAVY, GOLD, CREAM, arr_of, fog_layer, post, paste_bottom,
                      compose, centered, pill, series_header, header_layers, card)

NIGHT_FOG = (70, 90, 130)
RED_GLOW = (255, 70, 70)


class Street:
    """A strip of street `sw` px wide. lights: list of (x, on); vend: list of x; poles: list of x."""
    def __init__(self, sw=W, seed=1, lights=((560, True),), vend=(), poles=None, mirror=None, moon=None,
                 sky_top=SKY_TOP, sky_bot=SKY_BOT, houses=True, lit=0.6):
        rnd = random.Random(seed)
        self.sw = sw
        fw = int(W + sw * 0.3) + 10
        far = sky(sky_top, sky_bot, moon=moon, moon_r=34, stars=120, seed=seed, w=fw)
        far.alpha_composite(city_layer(fw, GY - 120, seed=seed, lit=lit))
        self.far = far
        near = Image.new("RGBA", (sw, H), (0, 0, 0, 0))
        self.wins = []
        if houses:
            x = rnd.randint(-120, 0)
            while x < sw:
                s = rnd.uniform(0.85, 1.05)
                hi, wins = jp_house(s, seed=rnd.randint(0, 999))
                near.alpha_composite(hi, (int(x), int(GY - 40 - hi.height)))
                self.wins += [(x + wx, GY - 40 - hi.height + wy) for wx, wy in wins]
                x += hi.width + rnd.randint(10, 80)
        near.alpha_composite(block_wall(sw, GY - 150, GY, seed=seed))
        d = ImageDraw.Draw(near)
        d.rectangle([0, GY, sw, H], fill=ROAD)
        d.rectangle([0, GY, sw, GY + 10], fill=(52, 54, 62, 255))
        d.rectangle([0, GY + 64, sw, GY + 74], fill=(170, 170, 160, 255))
        for k in range(sw // 700 + 1):
            mx = 300 + k * 700 + rnd.randint(-80, 80)
            d.ellipse([mx - 70, GY + 120, mx + 70, GY + 150], fill=(34, 36, 44, 255), outline=(48, 50, 58, 255), width=3)
        poles = poles if poles is not None else list(range(rnd.randint(80, 260), sw + 400, 620))
        pole_img = utility_pole(1000)
        for px in poles:
            near.alpha_composite(pole_img, (int(px - 110), int(GY + 14 - 1000)))
        wires(near, [p for p in poles], [GY + 14 - 1000 + 46, GY + 14 - 1000 + 96, GY + 14 - 1000 + 140], sag=50)
        self.vend = []
        for i, vx in enumerate(vend):
            vm = vending_machine(1.0, seed=i, hue=[(220, 40, 50), (40, 110, 200), (240, 240, 240)][i % 3])
            near.alpha_composite(vm, (int(vx - vm.width / 2), int(GY + 6 - vm.height)))
            self.vend.append((vx, GY + 6 - vm.height + 60))
        self.mirror = None
        if mirror is not None:
            mi, (mcx, mcy), mr = curve_mirror(1.0)
            near.alpha_composite(mi, (int(mirror - mi.width / 2), int(GY + 10 - mi.height)))
        self.lamps = []
        for lx, on in lights:
            li, (lpx, lpy) = streetlight(760, on=False)
            near.alpha_composite(li, (int(lx - lpx), int(GY + 20 - 760)))
            self.lamps.append([lx, GY + 20 - 760 + lpy, on])
        self.near = near
        self.vglow = glow_sprite(170, VEND, 2.0)
        self.lglow = glow_sprite(120, SODIUM, 1.6)
        self.wglow = glow_sprite(70, (255, 190, 120), 2.0)

    def compose(self, t, cam=0.0, light=None, actors=None, front=None):
        """light: callable(i, t) -> 0..1 for lamp i (defaults to its on flag)."""
        fx = int(cam * 0.3)
        img = self.far.crop((fx, 0, fx + W, H))
        img.alpha_composite(self.near.crop((int(cam), 0, int(cam) + W, H)))
        ks = []
        for i, (lx, ly, on) in enumerate(self.lamps):
            k = light(i, t) if light else float(on)
            ks.append(k)
            if -300 < lx - cam < W + 300 and k > 0.01:
                light_cone(img, lx - cam, ly, GY + 40, k)
                ImageDraw.Draw(img).rectangle([lx - cam - 37, ly - 6, lx - cam + 37, ly + 2], fill=SODIUM + (int(255 * k),))
        if actors:
            actors(img, t, cam)
        if front:
            front(img, t, cam)
        arr = arr_of(img)
        for (lx, ly, on), k in zip(self.lamps, ks):
            if k > 0.01:
                add_glow(arr, self.lglow, lx - cam, ly + 6, 0.9 * k)
        for vx, vy in self.vend:
            if -200 < vx - cam < W + 200:
                add_glow(arr, self.vglow, vx - cam, vy + 40, 0.45)
        for wx, wy in self.wins:
            if -80 < wx - cam < W + 80:
                add_glow(arr, self.wglow, wx - cam, wy, 0.22)
        return arr


def flicker(t, t_on, seed=3):
    """Streetlight switching on with a stutter."""
    if t < t_on:
        return 0.0
    u = t - t_on
    if u > 0.9:
        return 1.0
    r = random.Random(int(u * 30) + seed)
    return 1.0 if r.random() < 0.25 + 0.7 * u else 0.0


def place(img, im, x, feet_y):
    img.alpha_composite(im, (int(x - im.width / 2), int(feet_y - im.height)))


def woman_on(img, t, x, feet_y, scale, alpha=1.0, **kw):
    """Paste the masked woman with her shoes on feet_y."""
    gh = kuchisake(t, scale, **kw)
    foot = (40 + 812) * scale
    img.alpha_composite(with_alpha(gh, alpha), (int(x - gh.width / 2), int(feet_y - foot)))


def yui_on(img, x, feet_y, **kw):
    s, feet = student(**kw)
    img.alpha_composite(s, (int(x - feet[0]), int(feet_y - feet[1])))


def shake_img(img, t, amp, seed=1):
    if amp < 0.5:
        return img
    r = random.Random(int(t * FPS) + seed)
    return img.transform(img.size, Image.AFFINE, (1, 0, r.uniform(-1, 1) * amp, 0, 1, r.uniform(-1, 1) * amp),
                         resample=Image.BILINEAR)


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")


# ======================================================================= P1
def make_hook(D, caps):
    st = Street(seed=11, lights=((420, True),), vend=(880,), poles=[150, 980], moon=(860, 640))
    hdr = series_header("JAPAN", "PART 1")
    t2 = caps[1][1]

    def f(t):
        def actors(img, tt, cam):
            woman_on(img, t, 540, GY + 20, 0.7, eyes=0.6 * ease((t - t2) / 0.8))
        k = lambda i, tt: 0.75 + 0.25 * (1 if random.Random(int(tt * 12)).random() > 0.08 else 0)
        arr = st.compose(t, light=k, actors=actors)
        z = 1 + 0.06 * t / D + 0.12 * ease((t - t2) / 2.5)
        img = zoom(to_img(arr), z, 540, 860)
        arr = arr_of(img)
        fog_layer(arr, t, k=0.22, color=NIGHT_FOG)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, tint=(0.95, 0.97, 1.05))
    return f


def make_walk(D, caps):
    sw = 2600
    st = Street(sw=sw, seed=21, lights=((700, True), (1500, True), (2250, False)), vend=(1100, 1220), moon=(300, 520))
    span = 1450

    def f(t):
        cam = span * t / D
        def actors(img, tt, c):
            # the woman waits in the dark at the far end: the viewer sees her before Yui does
            woman_on(img, t, 2250 - c, GY + 20, 0.6, alpha=0.55, glow=1.0)
            yui_on(img, 430, GY + 26, phase=t * 2 * math.pi * 0.9, walking=True, facing=1, scale=1.9,
                   rim=(150, 190, 230))
        arr = st.compose(t, cam=cam, actors=actors)
        fog_layer(arr, t, k=0.2, color=NIGHT_FOG)
        return post(arr, t, tint=(0.95, 0.98, 1.06))
    return f


def make_warn(D, caps):
    # warm sepia flashback: shoji window, tatami, low table, grandmother with tea
    base = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    y = np.linspace(0, 1, H)[:, None, None]
    grad = np.repeat(np.array([70, 48, 30]) * (1 - y) + np.array([120, 84, 52]) * y, W, axis=1)
    base = Image.fromarray(grad.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(base)
    # shoji window (bright, morning)
    sx0, sy0, sx1, sy1 = 90, 420, 640, 1040
    d.rectangle([sx0, sy0, sx1, sy1], fill=(250, 226, 180, 255))
    for k in range(1, 5):
        d.line([(sx0 + (sx1 - sx0) * k / 5, sy0), (sx0 + (sx1 - sx0) * k / 5, sy1)], fill=(110, 74, 44, 255), width=8)
    for k in range(1, 7):
        d.line([(sx0, sy0 + (sy1 - sy0) * k / 7), (sx1, sy0 + (sy1 - sy0) * k / 7)], fill=(110, 74, 44, 255), width=8)
    d.rectangle([sx0, sy0, sx1, sy1], outline=(80, 52, 30, 255), width=20)
    # wooden beam + hanging scroll
    d.rectangle([0, 330, W, 360], fill=(60, 38, 22, 255))
    d.rectangle([760, 420, 900, 900], fill=(232, 220, 196, 255), outline=(90, 60, 36, 255), width=8)
    ImageDraw.Draw(base).text((830, 650), "心", font=cjk(110, serif=True), fill=(60, 40, 30, 255), anchor="mm")
    # tatami floor
    d.rectangle([0, 1120, W, H], fill=(150, 130, 74, 255))
    for x in range(-200, W + 200, 360):
        d.line([(x, 1120), (x + 120, H)], fill=(110, 92, 50, 255), width=6)
    d.rectangle([0, 1120, W, 1132], fill=(60, 80, 50, 255))
    # low table
    d.rectangle([300, 1060, 760, 1084], fill=(70, 40, 24, 255))
    d.rectangle([330, 1084, 352, 1160], fill=(60, 34, 20, 255)); d.rectangle([710, 1084, 732, 1160], fill=(60, 34, 20, 255))
    d.rectangle([500, 1024, 540, 1060], fill=(220, 210, 190, 255))
    gm = grandma(scale=2.1)
    base.alpha_composite(gm, (40, 1150 - gm.height + 20))
    warn_t = text_img("NEVER SAY YES.", font(LORA, 92, "Bold"), fill=CREAM, glow=(160, 30, 30, 230), pad=20)
    warn_t2 = text_img("NEVER SAY NO.", font(LORA, 92, "Bold"), fill=CREAM, glow=(160, 30, 30, 230), pad=20)
    ta = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.15
    tb = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.6
    sun = glow_sprite(420, (255, 220, 160), 1.6)

    def f(t):
        img = base.copy()
        dd = ImageDraw.Draw(img)
        for j in range(3):  # steam
            pts = [(520 + 12 * math.sin(t * 1.6 + v * 6 + j) + j * 6, 1020 - 160 * v) for v in np.linspace(0, 1, 20)]
            dd.line(pts, fill=(255, 245, 230, 70), width=4)
        yui_on(img, 880, 1160, walking=False, facing=-1, scale=2.0, color=(40, 28, 20, 255), rim=(255, 210, 150))
        img = zoom(img, 1 + 0.07 * t / D, 520, 900)
        arr = arr_of(img)
        add_glow(arr, sun, 360, 730, 0.35)
        arr = compose(arr, [centered(warn_t, 170, ease((t - ta) / 0.4)), centered(warn_t2, 290, ease((t - tb) / 0.4))])
        g = arr.mean(axis=2, keepdims=True)
        arr = arr * 0.45 + g * np.array([1.08, 0.92, 0.72], np.float32) * 0.55
        arr *= 0.93 + 0.07 * random.Random(int(t * 12)).random()
        return post(arr, t, vig=VIG_HEAVY, grain=GRAIN_HEAVY)
    return f


def make_appear(D, caps):
    st = Street(seed=31, lights=((300, True), (800, False)), vend=(120,), poles=[560], moon=None)
    t_on = caps[1][1] + 0.8
    t_push = caps[2][1]
    t_stop = caps[0][2]

    def f(t):
        def actors(img, tt, cam):
            on = flicker(t, t_on)
            woman_on(img, t, 820, GY + 20, 0.72, alpha=0.18 + 0.82 * on if t >= t_on else 0.18, glow=on)
            walking = t < t_stop
            yui_on(img, 210 + 70 * min(t, t_stop) / max(t_stop, 0.1), GY + 26, phase=t * 2 * math.pi * 0.9, walking=walking,
                   facing=1, scale=1.9, rim=(150, 200, 235), tremble=0.0 if t < t_on else 1.2 * math.sin(t * 30))
        arr = st.compose(t, light=lambda i, tt: 1.0 if i == 0 else flicker(tt, t_on), actors=actors)
        z = 1 + 0.03 * t / D + 0.38 * ease((t - t_push) / 2.8)
        img = zoom(to_img(arr), z, 540 + 260 * ease((t - t_push) / 2.8), 900)
        img = img.rotate(-2.5 * ease((t - t_push) / 2.8), Image.BILINEAR, center=(540, 900))
        arr = arr_of(img)
        fog_layer(arr, t, k=0.22, color=NIGHT_FOG)
        return post(arr, t, tint=(0.95, 0.97, 1.05))
    return f


def bokeh_bg(seed=5):
    rnd = random.Random(seed)
    bg = np.zeros((H, W, 3), np.float32)
    y = np.linspace(0, 1, H)[:, None, None]
    bg += np.repeat(np.array([6, 8, 18]) * (1 - y) + np.array([20, 24, 40]) * y, W, axis=1)
    for _ in range(26):
        c = rnd.choice([SODIUM, VEND, (255, 120, 120), SODIUM])
        add_glow(bg, glow_sprite(rnd.randint(30, 80), c, 0.8), rnd.uniform(0, W), rnd.uniform(200, 1500), rnd.uniform(0.12, 0.3))
    return bg


def make_ask(D, caps):
    bg = bokeh_bg(5)
    t_q = caps[2][1]
    t_step = caps[0][1]

    def f(t):
        img = to_img(bg)
        e = ease((t - t_q) / 0.5)
        s = 2.3 + 0.25 * ease((t - t_step) / 2.0)
        gh = kuchisake(t, s, eyes=e, glow=0.8)
        img.alpha_composite(gh, (int(540 - gh.width / 2), int(330 - 40 * s + 30 * math.sin(t * 0.8) - 40 * e)))
        img = zoom(img, 1 + 0.05 * t / D + 0.18 * e, 540, 520)
        img = shake_img(img, t, 7 * e * (0.5 + 0.5 * math.sin(t * 17)))
        arr = arr_of(img)
        fog_layer(arr, t, k=0.25, color=(90, 60, 80), y0=0.4)
        if t_q < t < t_q + 0.12:
            arr *= 1.5
        return post(arr, t, vig=VIG_HEAVY, tint=(1.04, 0.95, 0.98))
    return f


def fisheye_maps(r_out, src):
    yy, xx = np.mgrid[0:2 * r_out, 0:2 * r_out].astype(np.float32)
    u, v = (xx - r_out) / r_out, (yy - r_out) / r_out
    rho = np.sqrt(u * u + v * v)
    k = (1 + 0.9 * rho ** 2) / 1.9
    sx = np.clip((-u * k + 1) * 0.5 * (src - 1), 0, src - 1).astype(np.int32)   # mirrored horizontally
    sy = np.clip((v * k + 1) * 0.5 * (src - 1), 0, src - 1).astype(np.int32)
    mask = np.clip((r_out - rho * r_out) / 2.0, 0, 1)[..., None]
    shade = (1 - 0.35 * rho ** 3)[..., None]
    return sx, sy, mask * shade, mask


def make_cliff(D, caps):
    # the whole moment, seen in a curved traffic mirror on the corner
    st = Street(seed=41, lights=((620, True),), vend=(), poles=[], moon=None, houses=True)
    R, SRC = 330, 760
    sx, sy, shade, mask = fisheye_maps(R, SRC)
    MX, MY = 540, 860
    dark = Street(seed=42, lights=(), vend=(), poles=[120, 900], houses=True, sky_top=(3, 5, 12), sky_bot=(14, 18, 30))
    mir, (mcx, mcy), mr = curve_mirror(R / 100 * 1.0)
    t_hand = caps[1][1]
    t3 = caps[2][1]
    big_t = text_img("PART 2 TONIGHT", font(LORA, 96, "Bold"), fill=CREAM, glow=(190, 20, 30, 255), pad=24)
    sub_t = text_img("Follow so you don't miss it", font(INTER_M, 42), fill=(232, 226, 230, 255), pad=12)

    def f(t):
        reach = ease((t - t_hand) / 2.6) * 0.85
        def actors(img, tt, cam):
            woman_on(img, t, 620, GY + 20, 0.8, reach=reach, eyes=0.5)
            yui_on(img, 330, GY + 26, walking=False, facing=1, scale=2.2, rim=(255, 190, 120), tremble=1.0 * math.sin(t * 28))
        world = st.compose(t, actors=actors)
        crop = to_img(world).crop((110, 440, 110 + 800, 440 + 800)).resize((SRC, SRC), Image.BILINEAR)
        src = arr_of(crop)
        inside = src[sy, sx] * shade
        back = dark.compose(t, cam=0)
        bimg = to_img(back)
        z = 1 + 0.08 * t / D
        bimg.alpha_composite(mir, (int(MX - mcx), int(MY - mcy)))
        arr = arr_of(bimg)
        x0, y0 = MX - R, MY - R
        reg = arr[y0:y0 + 2 * R, x0:x0 + 2 * R]
        arr[y0:y0 + 2 * R, x0:x0 + 2 * R] = reg * (1 - mask) + inside * mask + 60 * mask * np.clip(0.6 - (np.mgrid[0:2 * R, 0:2 * R][0] / (2 * R))[..., None], 0, 1) * 0.3
        arr = arr_of(zoom(to_img(arr), z, MX, MY))
        fog_layer(arr, t, k=0.25, color=NIGHT_FOG)
        a1 = ease((t - t3 + 0.2) / 0.5)
        arr = post(arr, t, vig=VIG_HEAVY, tint=(1.0, 0.96, 1.0))
        if a1 > 0:
            arr *= 1 - 0.35 * a1
            arr = compose(arr, [centered(big_t, 220, a1), centered(sub_t, 360, ease((t - t3 - 0.3) / 0.5))])
        return arr
    return f


# ======================================================================= P2
def make_recap(D, caps):
    st = Street(seed=51, lights=((780, True), (160, True)), vend=(980,), poles=[480], moon=(200, 620))
    hdr = series_header("JAPAN", "PART 2")

    def f(t):
        def actors(img, tt, cam):
            woman_on(img, t, 760, GY + 20, 0.74, eyes=0.3)
            yui_on(img, 330, GY + 26, walking=False, facing=1, scale=1.9, rim=(150, 200, 235))
        arr = st.compose(t, actors=actors)
        img = zoom(to_img(arr), 1 + 0.07 * t / D, 600, 900)
        arr = arr_of(img)
        fog_layer(arr, t, k=0.22, color=NIGHT_FOG)
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, tint=(0.95, 0.97, 1.05))
    return f


def make_answer(D, caps):
    bg = bokeh_bg(9)
    t_yes = caps[1][1]

    def f(t):
        img = to_img(bg)
        # red coat towering at the right edge, Yui close in profile at the left
        gh = kuchisake(t, 2.2, glow=0.6)
        img.alpha_composite(gh, (int(800 - gh.width / 2), 150))
        e = ease((t - t_yes) / 0.4)
        yui_on(img, 330, 1600, walking=False, facing=1, scale=4.0, rim=(170, 220, 255), look_up=0.6,
               tremble=1.5 * math.sin(t * 26) * (0.4 + e))
        img = zoom(img, 1 + 0.05 * t / D + 0.15 * e, 420, 900)
        arr = arr_of(img)
        fog_layer(arr, t, k=0.2, color=(80, 70, 100), y0=0.45)
        if t_yes < t < t_yes + 0.1:
            arr *= 1.6
        return post(arr, t, vig=VIG_HEAVY, tint=(0.97, 0.97, 1.06))
    return f


def make_mask(D, caps):
    bg = bokeh_bg(13)
    t_reach = caps[0][1]
    t_drop = caps[1][1]
    t_now = caps[2][1]
    cut = caps[2][2] + 0.15

    def f(t):
        if t >= cut:
            return np.zeros((H, W, 3), np.float32)
        img = to_img(bg)
        reach = ease((t - t_reach) / 2.0)
        drop = 0.75 * ease((t - t_drop) / max(0.5, t_now + 0.8 - t_drop))
        e = ease((t - t_now) / 0.5)
        gh = kuchisake(t, 4.2, reach=reach, mask_drop=drop, eyes=0.4 + 0.6 * e, glow=0.9)
        img.alpha_composite(gh, (int(540 - gh.width / 2), int(150 - 170 * 1.0 + 8 * math.sin(t * 1.1))))
        img = zoom(img, 1 + 0.12 * ease(t / cut) + 0.1 * e, 540, 620)
        img = shake_img(img, t, 10 * e + 3 * ease((t - t_drop) / 1.0))
        arr = arr_of(img)
        r = random.Random(int(t * FPS))
        if t > t_drop and r.random() < 0.12:
            arr *= 0.45
        fog_layer(arr, t, k=0.2, color=(90, 40, 50), y0=0.5)
        return post(arr, t, vig=VIG_HEAVY, grain=GRAIN_HEAVY, tint=(1.06, 0.93, 0.95))
    return f


def make_trick(D, caps):
    st = Street(seed=61, lights=((700, True),), vend=(), poles=[200], moon=None)
    t_avg = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.55
    avg_t = text_img("“AVERAGE.”", font(LORA, 120, "Bold"), fill=CREAM, glow=(40, 120, 200, 230), pad=24)

    def f(t):
        fr = ease((t - t_avg) / 0.3)
        def actors(img, tt, cam):
            tw = t if fr < 0.5 else t_avg      # she freezes mid-motion
            woman_on(img, tw, 700, GY + 20, 1.12, reach=0.0, eyes=0.7 * (1 - fr), glow=1 - fr)
            yui_on(img, 300, GY + 26, walking=False, facing=1, scale=2.4, rim=(170, 220, 255), look_up=1.0)
        arr = st.compose(t, actors=actors)
        img = zoom(to_img(arr), 1.12 + 0.05 * t / D, 520, 760)
        arr = arr_of(img)
        if fr > 0:
            g = arr.mean(axis=2, keepdims=True)
            arr = arr * (1 - 0.75 * fr) + g * np.array([0.8, 0.95, 1.15], np.float32) * 0.75 * fr
            r = random.Random(int(t * FPS))
            if t < t_avg + 1.2 and r.random() < 0.4:   # freeze-glitch bands
                y0 = r.randint(300, 1200); h = r.randint(10, 60)
                arr[y0:y0 + h] = np.roll(arr[y0:y0 + h], r.randint(-40, 40), axis=1)
        fog_layer(arr, t, k=0.2, color=NIGHT_FOG)
        arr = compose(arr, [centered(avg_t, 190 - 10 * ease((t - t_avg) / 0.4), ease((t - t_avg) / 0.25))])
        return post(arr, t, tint=(0.96, 0.98, 1.05))
    return f


def make_run(D, caps):
    sw = 3000
    st = Street(sw=sw, seed=71, lights=((420, True), (1250, True), (2100, True)), vend=(1650,), moon=(820, 500))
    home, wins = jp_house(1.2, seed=5, lit=True)
    span = 1750
    t_run = caps[1][1] - 0.4
    door = glow_sprite(260, (255, 200, 130), 1.6)

    def f(t):
        u = ease((t - t_run) / max(0.5, D - t_run)) if t > t_run else 0
        cam = 60 * t / D + span * u
        def actors(img, tt, c):
            woman_on(img, 0, 520 - c, GY + 20, 0.95, eyes=0.0, glow=0.0, alpha=0.85)
            img.alpha_composite(home, (int(2700 - c - home.width / 2), int(GY + 10 - home.height)))
            dd = ImageDraw.Draw(img)
            dd.rectangle([2700 - c - 40, GY - 150, 2700 - c + 40, GY + 8], fill=(255, 210, 150, 255))
            running = t > t_run
            yui_on(img, 360 + 260 * u, GY + 26, phase=t * 2 * math.pi * (1.4 if running else 0), walking=running, run=running,
                   facing=1, scale=1.9, rim=(150, 200, 235))
        arr = st.compose(t, cam=cam, actors=actors)
        add_glow(arr, door, 2700 - cam, GY - 80, 0.5)
        fog_layer(arr, t, k=0.18, color=NIGHT_FOG)
        return post(arr, t, tint=(0.97, 0.98, 1.04))
    return f


_SG = None


def sbg():
    global _SG
    if _SG is None:
        _SG = seigaiha_bg()
    return _SG


def make_explain(D, caps):
    R = 200
    med = Image.new("RGBA", (R * 4, R * 4), (0, 0, 0, 0))
    ImageDraw.Draw(med).ellipse([4, 4, R * 4 - 4, R * 4 - 4], fill=(30, 18, 30, 255), outline=GOLD, width=6)
    med = down(med)
    gh = kuchisake(1.0, 1.05, glow=0.0)
    mask = Image.new("L", med.size, 0)
    ImageDraw.Draw(mask).ellipse([6, 6, med.width - 6, med.height - 6], fill=255)
    inner = Image.new("RGBA", med.size, (0, 0, 0, 0))
    inner.alpha_composite(gh, (int(med.width / 2 - gh.width / 2), 60))
    med.alpha_composite(Image.composite(inner, Image.new("RGBA", med.size, (0, 0, 0, 0)), mask))
    lbl = text_img("JAPANESE  URBAN  LEGEND", font(INTER_M, 30), fill=GOLD, pad=10)
    title = text_img("Kuchisake-onna", font(LORA, 112, "Bold"), fill=CREAM, glow=(190, 20, 30, 200), pad=20)
    kj = text_img("口裂け女", cjk(40, serif=True), fill=(235, 200, 160, 255), pad=8)
    sub = text_img("the slit-mouthed woman", font(INTER_M, 36), fill=(235, 220, 205, 255), pad=8)
    pf = font(INTER_SB, 34)
    pills = [pill(n, pf, fill=(40, 16, 24, 230)) for n in ("“Am I pretty?”", "Always wears a mask")]
    c1, c2 = card(450, 330), card(450, 330)
    d1 = ImageDraw.Draw(c1)
    d1.text((225, 120), "1979", font=font(LORA, 120, "Bold"), fill=(255, 120, 110, 255), anchor="mm")
    d1.text((225, 230), "Rumors swept Japan", font=font(INTER_SB, 32), fill=CREAM, anchor="mm")
    d1.text((225, 280), "Kids walked home in groups", font=font(INTER_M, 28), fill=(220, 210, 200, 255), anchor="mm")
    cd = candy(1.3)
    c2.alpha_composite(cd, (int(225 - cd.width / 2), 50))
    d2 = ImageDraw.Draw(c2)
    d2.text((225, 210), "To escape: say", font=font(INTER_M, 30), fill=(220, 210, 200, 255), anchor="mm")
    d2.text((225, 255), "“average”", font=font(LORA, 44, "Bold"), fill=(255, 214, 77, 255), anchor="mm")
    d2.text((225, 300), "or throw hard candy", font=font(INTER_M, 28), fill=(220, 210, 200, 255), anchor="mm")
    p1t = caps[0][1] + (caps[0][2] - caps[0][1]) * 0.55
    p2t = caps[0][2] - 0.2
    ta = caps[1][1] + 0.3
    tb = caps[2][1] + 0.3

    def f(t):
        arr = sbg().copy()
        fog_layer(arr, t, speed=8, k=0.18, color=(120, 40, 60), y0=0.3)
        layers = [(med, (W / 2 - med.width / 2, 120 + 6 * math.sin(t)), ease(t / 0.7)),
                  centered(lbl, 540, ease((t - 0.3) / 0.6)),
                  centered(title, 570 - 8 * ease(t / 1.0), ease((t - 0.4) / 0.8)),
                  centered(kj, 720, ease((t - 0.9) / 0.6)),
                  centered(sub, 775, ease((t - 1.1) / 0.6))]
        tot = sum(p.width for p in pills) + 18
        x = W / 2 - tot / 2
        for p, tt in zip(pills, (p1t, p2t)):
            layers.append((p, (x, 860 - 10 * ease((t - tt) / 0.4)), ease((t - tt) / 0.4)))
            x += p.width + 18
        layers.append((c1, (60, 960 + 16 * (1 - ease((t - ta) / 0.5))), ease((t - ta) / 0.5)))
        layers.append((c2, (570, 960 + 16 * (1 - ease((t - tb) / 0.5))), ease((t - tb) / 0.5)))
        return post(compose(arr, layers), t)
    return f


def make_outro(D, caps):
    q = text_img("What would YOU", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    q2 = text_img("answer her?", font(LORA, 96, "Bold"), fill=CREAM, glow=(190, 20, 30, 200), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Yes", (200, 40, 50, 235)), ("No", (200, 40, 50, 235)), ("Average", (30, 90, 160, 235)),
            ("Throw candy", (30, 90, 160, 235)), ("RUN!", (40, 16, 24, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    rows = [chips[0:3], chips[3:5]]
    cm = text_img("Comment below", font(INTER_SB, 50), fill=(255, 150, 140, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(225, 214, 214, 255), pad=10)

    def f(t):
        arr = sbg().copy()
        fog_layer(arr, t, speed=8, k=0.18, color=(120, 40, 60), y0=0.3)
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
