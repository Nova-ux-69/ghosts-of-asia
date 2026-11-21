"""Episode 2: Nang Tani (Thailand), vertical scenes."""
import os, sys, math, random
_EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _EP)
sys.path.insert(1, os.path.join(_EP, "..", "..", "toolkit"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import *
from art_ep2 import *
import scenes_v as V
from scenes_v import (GY, VIG, VIG_HEAVY, GRAIN, GRAIN_HEAVY, GOLD, CREAM, arr_of, fog_layer, post, paste_bottom, sway,
                      compose, centered, pill, series_header, header_layers, night_sky, ebg, card)

GREEN = (110, 255, 170)
TREE_H = 470


def tree_img(scale, ribbons=True, seed=77, color=SIL):
    return banana_tree(scale, seed=seed, color=color, height=TREE_H, bend=0)


class Yard:
    """House on the left, haunted banana tree on the right."""
    def __init__(self, sky_top, sky_bot, moon=None, moon_r=60, tree_x=760, tree_s=1.7, house_x=250, lit=True,
                 ribbons=True, offer=True, light=0.75, seed=5, stars=True):
        bg = sky(sky_top, sky_bot, moon=moon, moon_r=moon_r, stars=260 if stars else 0, seed=seed)
        bg.alpha_composite(hills(W, 1010, 45, FAR, 7))
        bg.alpha_composite(hills(W, 1090, 25, MID, 9, freq=1.4))
        for x, s in ((520, 0.8), (980, 0.9)):
            paste_bottom(bg, palm_tree(s, seed=x), x, 1120)
        self.house, wins = thai_house(1.15, lit=lit)
        hx, hy = int(house_x - self.house.width / 2), int(GY + 14 - self.house.height)
        self.wins = [(hx + wx + ww / 2, hy + wy + wh / 2) for wx, wy, ww, wh in wins]
        self.hpos = (hx, hy)
        self.bg = bg
        self.tree = tree_img(tree_s)
        self.tree_x, self.tree_s = tree_x, tree_s
        self.base_y = GY + 70
        self.rib, self.tails = ribbons_layer(tree_x, self.base_y, tree_s, TREE_H, n=5, light=light)
        self.offer_img, tips = offerings(1.0, light=light)
        self.offer_pos = (tree_x - 70, GY + 30 - self.offer_img.height)
        self.tips = tips
        self.ground = ground(W, GY, SIL, 4)
        self.ribbons, self.offer = ribbons, offer
        self.light = light

    def compose(self, t, sway_deg=0.6, ribbons=None, offer=None, house=True, before_ground=None, after=None,
                rib_alpha=1.0):
        img = self.bg.copy()
        if house:
            img.alpha_composite(self.house, self.hpos)
        paste_bottom(img, sway(self.tree, sway_deg * math.sin(t * 0.7)), self.tree_x, self.base_y)
        rb = self.ribbons if ribbons is None else ribbons
        if rb and rib_alpha > 0.01:
            img.alpha_composite(with_alpha(self.rib, rib_alpha))
            tl = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw_tails(tl, [(x, y, tuple(int(v * self.light) for v in c[:3]) + (255,)) for x, y, c in self.tails], t, self.tree_s * 0.8)
            img.alpha_composite(with_alpha(tl, rib_alpha))
        if before_ground:
            before_ground(img, t)
        img.alpha_composite(self.ground)
        of = self.offer if offer is None else offer
        if of:
            img.alpha_composite(self.offer_img, (int(self.offer_pos[0]), int(self.offer_pos[1])))
            smoke(img, self.tips, t, self.offer_pos[0], self.offer_pos[1], 0.6)
        if after:
            after(img, t)
        return img


def glow_tips(arr, yard, k=1.0):
    sp = glow_sprite(10, (255, 150, 70), 1.4)
    for tx, ty in yard.tips:
        add_glow(arr, sp, yard.offer_pos[0] + tx, yard.offer_pos[1] + ty, 1.2 * k)


def leaf_glow(arr, yard, t, k):
    if k <= 0.01:
        return
    g = glow_sprite(380, GREEN, 1.8)
    ty = yard.base_y - TREE_H * yard.tree_s
    add_glow(arr, g, yard.tree_x, ty + 40, k * (0.55 + 0.15 * math.sin(t * 3.1)))


# ======================================================================= P1
def make_hook(D, caps):
    y = Yard((3, 6, 16), (26, 40, 52), moon=(560, 760), moon_r=120, tree_x=560, tree_s=2.0, house_x=-400, light=0.85)
    hdr = series_header("THAILAND", "PART 1")
    flies = Fireflies(26, seed=4, area=(0, W, 650, 1200))

    def f(t):
        img = y.compose(t, house=False)
        img = zoom(img, 1 + 0.07 * t / D, 540, 1000)
        arr = arr_of(img)
        z = 1 + 0.07 * t / D
        flies.draw(arr, t, 0.8)
        fog_layer(arr, t, k=0.28, color=(110, 150, 140))
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, tint=(0.9, 1.0, 0.98))
    return f


def make_move(D, caps):
    y = Yard((40, 30, 70), (230, 120, 80), moon=None, tree_x=800, house_x=280, lit=True, light=1.0, stars=False)
    warm = glow_sprite(110, (255, 170, 80), 2.0)

    def f(t):
        u = min(1, t / (D * 0.8))
        x = -60 + 520 * u
        def after(img, tt):
            a, feet, _ = amir(t * 2 * math.pi * 0.85, 1.0 - ease((u - 0.92) / 0.08), facing=1, lantern=False, scale=1.6, rim=(160, 110, 110))
            img.alpha_composite(a, (int(x - feet[0]), int(GY + 22 - feet[1])))
        img = y.compose(t, after=after)
        arr = arr_of(img)
        for i, (wx, wy) in enumerate(y.wins):
            add_glow(arr, warm, wx, wy, 0.3)
        glow_tips(arr, y)
        fog_layer(arr, t, k=0.12, color=(200, 140, 140))
        return post(arr, t, tint=(1.0, 0.95, 0.95))
    return f


def make_warn(D, caps):
    y = Yard((20, 18, 50), (150, 80, 90), moon=None, tree_x=840, house_x=170, lit=True, light=0.9, stars=False)
    warm = glow_sprite(110, (255, 170, 80), 2.0)
    eld, ef, _ = amir(walking=False, facing=1, lantern=False, color=SIL, scale=1.45, rim=(120, 90, 110))
    som, sf_, _ = amir(walking=False, facing=-1, lantern=False, color=SIL, scale=1.6, rim=(120, 90, 110))

    def f(t):
        def after(img, tt):
            d = ImageDraw.Draw(img)
            ex = 380
            img.alpha_composite(eld, (int(ex - ef[0]), int(GY + 22 - ef[1])))
            d.line([(ex + 50, GY - 190), (ex + 64, GY + 20)], fill=SIL, width=6)   # walking stick
            img.alpha_composite(som, (int(620 - sf_[0]), int(GY + 22 - sf_[1])))
        img = y.compose(t, after=after)
        img = zoom(img, 1 + 0.06 * t / D, 600, 1000)
        arr = arr_of(img)
        glow_tips(arr, y, 0.8)
        fog_layer(arr, t, k=0.15, color=(170, 120, 150))
        return post(arr, t)
    return f


def make_rip(D, caps):
    y = Yard((4, 6, 18), (30, 34, 66), moon=(250, 420), moon_r=40, tree_x=720, house_x=150, lit=True, light=0.8)
    fall = FallingRibbons(720, GY - 120, GY + 20, scale=1.0, n=7)
    t_rip = caps[1][1]
    t_kick = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.6
    warm = glow_sprite(110, (255, 170, 80), 2.0)

    def f(t):
        gone = t > t_rip + 0.3
        k = ease((t - t_kick) / 0.6)
        def after(img, tt):
            fall.draw(img, t, t_rip)
            a, feet, lp = amir(walking=False, facing=1, lantern=True, scale=1.7)
            img.alpha_composite(a, (int(560 - feet[0]), int(GY + 22 - feet[1])))
        img = y.compose(t, ribbons=True, rib_alpha=1 - ease((t - t_rip) / 0.35), offer=False, after=after)
        if k < 1:
            oi = y.offer_img.rotate(-70 * k, Image.BICUBIC, expand=True)
            img.alpha_composite(with_alpha(oi, 1 - k), (int(y.offer_pos[0] + 260 * k), int(y.offer_pos[1] - 120 * math.sin(math.pi * k))))
        img = zoom(img, 1 + 0.08 * t / D, 640, 1000)
        arr = arr_of(img)
        for i, (wx, wy) in enumerate(y.wins):
            add_glow(arr, warm, wx, wy, 0.32)
        fog_layer(arr, t, k=0.25)
        return post(arr, t)
    return f


def make_night(D, caps):
    y = Yard((2, 4, 14), (22, 30, 56), moon=(760, 520), moon_r=110, tree_x=760, house_x=250, lit=True, light=0.7)
    y_dark = Yard((2, 4, 14), (22, 30, 56), moon=(760, 520), moon_r=110, tree_x=760, house_x=250, lit=False, light=0.7)
    warm = glow_sprite(110, (255, 170, 80), 2.0)
    t_off = caps[0][2]

    def f(t):
        yy = y if t < t_off else y_dark
        img = yy.compose(t, ribbons=False, offer=False, sway_deg=0.6 + 1.2 * ease((t - caps[2][1]) / 2))
        img = zoom(img, 1 + 0.1 * t / D, 700, 950)
        arr = arr_of(img)
        if t < t_off:
            for wx, wy in y.wins:
                add_glow(arr, warm, wx, wy, 0.32)
        z = 1 + 0.1 * t / D
        leaf_glow(arr, y, t, ease((t - caps[1][1]) / 3) * 0.9)
        fog_layer(arr, t, k=0.32, color=(100, 140, 130))
        return post(arr, t, tint=(0.85, 0.95, 0.95))
    return f


def make_cliff(D, caps):
    y = Yard((2, 4, 14), (22, 30, 56), moon=(820, 420), moon_r=80, tree_x=600, tree_s=1.9, house_x=-600, light=0.7)
    t2 = caps[2][1]
    big_t = text_img("PART 2 TOMORROW", font(LORA, 92, "Bold"), fill=CREAM, glow=(20, 140, 80, 255), pad=24)
    sub_t = text_img("Follow so you don't miss it", font(INTER_M, 42), fill=(220, 236, 228, 255), pad=12)
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    WX0, WY0, WX1, WY1 = 110, 560, 970, 1380
    d.rectangle([0, 0, W, WY0], fill=(16, 11, 8, 255)); d.rectangle([0, WY1, W, H], fill=(16, 11, 8, 255))
    d.rectangle([0, 0, WX0, H], fill=(16, 11, 8, 255)); d.rectangle([WX1, 0, W, H], fill=(16, 11, 8, 255))
    d.rectangle([WX0 - 24, WY0 - 24, WX1 + 24, WY1 + 24], outline=(36, 24, 16, 255), width=30)
    for k in range(1, 4):
        xx = WX0 + (WX1 - WX0) * k / 4
        d.line([(xx, WY0), (xx, WY1)], fill=(36, 24, 16, 255), width=16)
    for x in range(0, W, 120):
        d.line([(x, 0), (x, WY0 - 40)], fill=(26, 18, 12, 255), width=4)

    def f(t):
        ga = (0.1 + 0.35 * ease((t - caps[0][1]) / 3)) * (0.85 + 0.15 * math.sin(t * 4))
        def before(img, tt):
            gh = ghost_tani(t, 0.75)
            img.alpha_composite(with_alpha(gh, ga), (int(600 - gh.width / 2), int(560 + 10 * math.sin(t * 1.1))))
        img = y.compose(t, ribbons=False, offer=False, before_ground=before, sway_deg=1.6)
        img = zoom(img, 1.05 + 0.08 * t / D, 600, 950)
        arr = arr_of(img)
        leaf_glow(arr, y, t, 0.9)
        fog_layer(arr, t, k=0.35, color=(100, 140, 130))
        arr = compose(arr, [(frame, (0, 0), 1.0)])
        a1 = ease((t - t2 + 0.2) / 0.5)
        if a1 > 0:
            arr *= 1 - 0.4 * a1
            arr = compose(arr, [centered(big_t, 220, a1), centered(sub_t, 360, ease((t - t2 - 0.3) / 0.5))])
        return post(arr, t, vig=VIG_HEAVY, tint=(0.88, 0.98, 0.95))
    return f


# ======================================================================= P2
def make_recap(D, caps):
    y = Yard((2, 4, 14), (22, 30, 56), moon=(760, 640), moon_r=100, tree_x=640, tree_s=1.9, house_x=-600, light=0.7)
    hdr = series_header("THAILAND", "PART 2")
    rib = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(rib)
    rnd = random.Random(2)
    for i in range(6):
        x = 420 + rnd.uniform(0, 380); yy = GY + 20 + rnd.uniform(0, 40)
        c = tuple(int(v * 0.7) for v in RIBBON_COLS[i]) + (255,)
        pts = [(x + 12 * k, yy + 6 * math.sin(k * 0.9 + i)) for k in range(8)]
        d.line(pts, fill=c, width=9)

    def f(t):
        img = y.compose(t, ribbons=False, offer=False, after=lambda im, tt: im.alpha_composite(rib), sway_deg=1.2)
        img = zoom(img, 1 + 0.05 * t / D, 600, 1000)
        arr = arr_of(img)
        leaf_glow(arr, y, t, 0.8)
        fog_layer(arr, t, k=0.3, color=(100, 140, 130))
        arr = compose(arr, header_layers(hdr, t))
        return post(arr, t, tint=(0.88, 0.98, 0.95))
    return f


def make_door(D, caps):
    y = Yard((2, 4, 14), (22, 30, 56), moon=(880, 420), moon_r=90, tree_x=820, house_x=230, lit=True, light=0.7)
    warm = glow_sprite(110, (255, 170, 80), 2.0)
    t_g = caps[1][1]

    def f(t):
        ga = ease((t - t_g) / 1.2) * (0.85 + 0.1 * math.sin(t * 4))
        def before(img, tt):
            if ga > 0.01:
                gh = ghost_tani(t, 0.62)
                img.alpha_composite(with_alpha(gh, ga), (int(740 - gh.width / 2), int(640 + 10 * math.sin(t * 1.2))))
        def after(img, tt):
            a, feet, _ = amir(walking=False, facing=1, lantern=True, scale=1.6)
            img.alpha_composite(a, (int(430 - feet[0]), int(GY + 22 - feet[1])))
        img = y.compose(t, ribbons=False, offer=False, before_ground=before, after=after)
        img = zoom(img, 1 + 0.08 * t / D, 600, 1000)
        arr = arr_of(img)
        for wx, wy in y.wins:
            add_glow(arr, warm, wx, wy, 0.3)
        leaf_glow(arr, y, t, 0.6 + 0.4 * ga)
        fog_layer(arr, t, k=0.32, color=(100, 140, 130))
        return post(arr, t, tint=(0.88, 0.98, 0.95))
    return f


def make_float(D, caps):
    bg = sky((2, 4, 14), (20, 30, 50), moon=(800, 400), moon_r=70, stars=200, seed=31)
    bg.alpha_composite(hills(W, 1060, 30, FAR, 12))
    tree = tree_img(2.2, color=(14, 18, 30, 255))
    gr = ground(W, GY + 120, SIL, 13)
    t_feet = caps[1][1]

    def f(t):
        img = bg.copy()
        paste_bottom(img, sway(tree, 1.0 * math.sin(t * 0.6)), 300, GY + 200)
        gh = ghost_tani(t, 1.15)
        img.alpha_composite(gh, (int(560 - gh.width / 2), int(330 + 18 * math.sin(t * 1.3))))
        img.alpha_composite(gr)
        u = ease((t - t_feet) / 1.6)
        img = zoom(img, 1.0 + 0.12 * u, 560, 880 + 360 * u)
        arr = arr_of(img)
        fog_layer(arr, t, k=0.4, color=(110, 150, 140), y0=0.5)
        return post(arr, t, vig=VIG_HEAVY, tint=(0.9, 1.0, 0.97))
    return f


def make_reveal(D, caps):
    bg = sky((1, 3, 8), (10, 20, 24), moon=None, stars=40, seed=32)
    tree = tree_img(2.6, color=(12, 24, 22, 255))
    cut = D - 1.0
    rnd = random.Random(7)
    shake = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(int(D * FPS) + 5)]
    t_eyes = caps[1][1]

    def f(t):
        if t >= cut:
            return np.zeros((H, W, 3), np.float32)
        img = bg.copy()
        e = ease((t - t_eyes) / 0.6)
        paste_bottom(img, sway(tree, (0.6 + 3.0 * e) * math.sin(t * (0.6 + 5 * e))), 540, H + 300)
        gh = ghost_tani(t, 2.0, eyes=e)
        img.alpha_composite(gh, (int(540 - gh.width / 2), int(300 + 10 * math.sin(t * 1.2) - 60 * e)))
        img = zoom(img, 1.0 + 0.25 * ease(t / cut), 540, 640)
        i = int(t * FPS)
        amp = 16 * e * (0.5 + 0.5 * math.sin(t * 20)) + (8 if t > cut - 0.5 else 0)
        if amp > 0.5:
            img = img.transform(img.size, Image.AFFINE, (1, 0, shake[i][0] * amp, 0, 1, shake[i][1] * amp), resample=Image.BILINEAR)
        arr = arr_of(img)
        fog_layer(arr, t, k=0.3, color=(90, 140, 120), y0=0.55)
        if t > cut - 0.6 or (t_eyes < t < t_eyes + 0.25):
            arr *= 0.55 + 0.7 * rnd.random()
        return post(arr, t, vig=VIG_HEAVY, tint=(0.88, 1.0, 0.95))
    return f


def make_morning(D, caps):
    y = Yard((90, 110, 170), (250, 180, 150), moon=None, tree_x=760, house_x=230, lit=False, light=1.0, stars=False)
    n_rib = 5
    t0, t1 = 0.6, caps[0][2]
    t_off = caps[1][1]

    def f(t):
        frac = ease((t - t0) / max(0.5, t1 - t0))
        def after(img, tt):
            a, feet, _ = amir(walking=False, facing=1, lantern=False, scale=1.6, rim=(255, 200, 170))
            img.alpha_composite(a, (int(600 - feet[0]), int(GY + 22 - feet[1])))
        img = y.compose(t, ribbons=True, rib_alpha=frac, offer=t > t_off, after=after)
        img = zoom(img, 1 + 0.06 * t / D, 640, 1000)
        arr = arr_of(img)
        sun = glow_sprite(500, (255, 200, 150), 1.5)
        add_glow(arr, sun, 900, 950, 0.35)
        if t > t_off:
            glow_tips(arr, y, ease((t - t_off) / 0.6))
        fog_layer(arr, t, k=0.12, color=(240, 200, 190))
        return post(arr, t, tint=(1.0, 0.97, 0.95))
    return f


def make_explain(D, caps):
    R = 200
    med = Image.new("RGBA", (R * 4, R * 4), (0, 0, 0, 0))
    ImageDraw.Draw(med).ellipse([4, 4, R * 4 - 4, R * 4 - 4], fill=(12, 24, 22, 255), outline=GOLD, width=6)
    med = down(med)
    gh = ghost_tani(1.0, 0.44, closed=True)
    mask = Image.new("L", med.size, 0)
    ImageDraw.Draw(mask).ellipse([6, 6, med.width - 6, med.height - 6], fill=255)
    inner = Image.new("RGBA", med.size, (0, 0, 0, 0))
    inner.alpha_composite(gh, (int(med.width / 2 - gh.width / 2), 30))
    med.alpha_composite(Image.composite(inner, Image.new("RGBA", med.size, (0, 0, 0, 0)), mask))
    lbl = text_img("THAI  FOLKLORE", font(INTER_M, 30), fill=GOLD, pad=10)
    title = text_img("Nang Tani", font(LORA, 128, "Bold"), fill=CREAM, glow=(20, 140, 80, 200), pad=20)
    pf = font(INTER_SB, 34)
    pills = [pill(n, pf) for n in ("Lady of the banana tree", "Full moon nights")]
    c1, c2 = card(450, 330), card(450, 330)
    tr = banana_tree(0.5, seed=5, color=(150, 196, 150, 255), height=210, bend=0)
    c1.alpha_composite(tr, (int(225 - tr.width / 2), int(250 - tr.height)))
    rl, _ = ribbons_layer(225, 250, 0.5, 210, n=4, w=450, h=330)
    c1.alpha_composite(rl)
    of, _ = offerings(1.1)
    c2.alpha_composite(of, (int(225 - of.width / 2), 90))
    lf = font(INTER_SB, 30)
    ImageDraw.Draw(c1).text((225, 290), "Colorful cloth on her tree", font=lf, fill=CREAM, anchor="mm")
    ImageDraw.Draw(c2).text((225, 290), "Food and incense for her", font=lf, fill=CREAM, anchor="mm")
    p1t = caps[0][1] + (caps[0][2] - caps[0][1]) * 0.45
    p2t = caps[1][1] + (caps[1][2] - caps[1][1]) * 0.3
    ta = caps[2][1]
    tb = caps[2][1] + (caps[2][2] - caps[2][1]) * 0.55

    def f(t):
        arr = ebg().frame(t)
        layers = [(med, (W / 2 - med.width / 2, 150 + 6 * math.sin(t)), ease(t / 0.7)),
                  centered(lbl, 580, ease((t - 0.3) / 0.6)),
                  centered(title, 610 - 8 * ease(t / 1.0), ease((t - 0.4) / 0.8))]
        tot = sum(p.width for p in pills) + 18
        x = W / 2 - tot / 2
        for p, tt in zip(pills, (p1t, p2t)):
            layers.append((p, (x, 810 - 10 * ease((t - tt) / 0.4)), ease((t - tt) / 0.4)))
            x += p.width + 18
        layers.append((c1, (60, 920 + 16 * (1 - ease((t - ta) / 0.5))), ease((t - ta) / 0.5)))
        layers.append((c2, (570, 920 + 16 * (1 - ease((t - tb) / 0.5))), ease((t - tb) / 0.5)))
        return post(compose(arr, layers), t)
    return f


def make_outro(D, caps):
    q = text_img("Which country", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    q2 = text_img("should be next?", font(LORA, 96, "Bold"), fill=CREAM, pad=20)
    pf = font(INTER_SB, 40)
    names = ["Japan", "Philippines", "Indonesia", "China", "Myanmar", "India", "Vietnam", "Korea"]
    chips = [pill(n, pf, h=84) for n in names]
    cm = text_img("Comment below", font(INTER_SB, 50), fill=(160, 240, 190, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(205, 222, 214, 255), pad=10)
    rows = [chips[0:3], chips[3:6], chips[6:8]]

    def f(t):
        arr = ebg().frame(t)
        layers = [centered(q, 330, ease(t / 0.6)), centered(q2, 450, ease((t - 0.2) / 0.6))]
        yy, k = 640, 0
        for row in rows:
            tot = sum(c.width for c in row) + 22 * (len(row) - 1)
            x = W / 2 - tot / 2
            for c in row:
                tt = 0.5 + 0.18 * k
                layers.append((c, (x, yy + 12 * (1 - ease((t - tt) / 0.4))), ease((t - tt) / 0.4)))
                x += c.width + 22; k += 1
            yy += 112
        layers.append(centered(cm, 1010, ease((t - caps[1][1]) / 0.4) * (0.85 + 0.15 * math.sin(t * 6))))
        layers.append(centered(fol, 1110, ease((t - caps[1][1] - 0.4) / 0.5)))
        arr = post(compose(arr, layers), t)
        return arr * (1 - ease((t - (D - 0.6)) / 0.6))
    return f
