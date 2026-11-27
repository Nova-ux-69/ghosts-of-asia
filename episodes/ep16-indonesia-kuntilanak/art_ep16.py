"""Ep16 Indonesia / Kuntilanak - art: the world, the characters and the ghost (2.1D flat21 style).
New world: midnight on the Kapuas riverfront in Pontianak (far bank with stilt houses and a long lit bridge, the red
moon's road on the black river, a klotok boat, Putri's family noodle stall - a wooden gerobak cart with a red MIE AYAM
sign under a sagging tarp - and a giant banyan with curtains of aerial roots), the old kampung boardwalk on stilts in
one-point perspective, the banyan seen from below, the dark space under a stilt house with red light leaking through
the floor planks, the pos ronda night-watch hut with its kentongan slit drum, and Putri's room with a batik curtain.
Hero: Putri (ochre T-shirt, dark red stall apron, ponytail). The ghost: the Kuntilanak - too tall, long bone-white
gown with a ragged hem, black hair to her waist hiding her face, long pale arms and dark nails, red eyes. No gore."""
import os, sys, math
os.environ["STYLE"] = "flat21"
_EP = os.path.dirname(os.path.abspath(__file__)); _TK = os.path.join(_EP, "..", "..", "toolkit")
sys.path.insert(0, _TK)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import W, H, font, text_img, with_alpha, ease, glow_sprite, add_glow, fog_texture, vignette, INTER_SB, INTER_M, LORA
from depth import inflate_shade, dof, bokeh_particles, god_rays
import demo25_myanmar as D5
from scenes_v import series_header, header_layers, pill

VIG = vignette(0.85)
VIG_H = vignette(1.05)
GR = [np.random.default_rng(i).normal(0, 5, (H, W, 1)).astype(np.float32) for i in range(6)]
FOGT = fog_texture(W + 700, H, 214)

def ss(t, a, b):
    return ease((t - a) / max(1e-3, b - a))


def inflate21(mask, base, light=(-0.55, -0.7, 0.5), rim=(255, 55, 40), radius=40, rim_strength=0.9, **_):
    """2.1D: flat colour, one clear shadow side (55%), a thin bright red edge light, darker edges."""
    from scipy.ndimage import distance_transform_edt, gaussian_filter
    m = np.asarray(mask, np.float32)
    if m.max() > 1.5:
        m = m / 255.0
    inside = m > 0.5
    d = gaussian_filter(distance_transform_edt(inside).astype(np.float32), max(1.5, radius * 0.05))
    u = np.clip(d / radius, 0, 1)
    h = gaussian_filter(np.sqrt(1 - (1 - u) ** 2) * radius, max(2.0, radius * 0.04))
    gy, gx = np.gradient(h)
    n = np.dstack([-gx, -gy, np.ones_like(h)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    diff = np.clip((n * L).sum(2), 0, 1)
    tone = np.where(diff > 0.32, 1.0, 0.55)
    rd = np.array((0.8, -0.2), np.float32); rd /= np.linalg.norm(rd)
    rimv = (1 - n[..., 2]) ** 2.0 * np.clip(n[..., 0] * rd[0] + n[..., 1] * rd[1], 0, 1)
    rimv = gaussian_filter((rimv > 0.1).astype(np.float32), 0.8)
    ao = 0.8 + 0.2 * np.clip(d / 6.0, 0, 1)
    col = np.array(base, np.float32)[None, None] * tone[..., None] * ao[..., None]
    col += np.array(rim, np.float32)[None, None] * (rimv * rim_strength * 0.95)[..., None]
    return Image.fromarray(np.dstack([np.clip(col, 0, 255), m * 255]).astype(np.uint8), "RGBA")


def shade(draw_fn, size, base, radius, **kw):
    m = D5.smooth_mask(draw_fn, size)
    return inflate21(m, base, light=kw.pop("light", (-0.55, -0.7, 0.5)), rim=kw.pop("rim", (255, 55, 40)), radius=radius,
                     rim_strength=kw.pop("rim_strength", 0.9))


def to_arr(img):
    return np.asarray(img.convert("RGB")).astype(np.float32)


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def finish(img, t, vig=VIG, push=1.0, cx=W / 2, cy=H * 0.45, shake=0.0, flash=0.0, flash_col=(255, 255, 255), rotate=0.0):
    push = max(1.0, push)
    if rotate:
        img = img.rotate(rotate, resample=Image.BICUBIC, center=(cx, cy), fillcolor=(4, 1, 2, 255))
        push = max(push, 1.0 + abs(math.radians(rotate)) * 1.6)
    if push != 1.0 or shake:
        sx = shake * math.sin(t * 91) * 14; sy = shake * math.cos(t * 77) * 14
        cw, ch = W / push, H / push
        x0 = min(max(cx - cw / 2 + sx, 0), W - cw); y0 = min(max(cy - ch / 2 + sy, 0), H - ch)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    a = to_arr(img) * vig + GR[int(t * 30) % 6]
    if flash > 0:
        a = a * (1 - flash) + np.array(flash_col, np.float32) * flash
    return a


def fog(img, t, k, y0, y1, speed=18, col=(150, 50, 40), off=0):
    o = int((t * speed + off) % 700)
    f = FOGT[:, o:o + W]
    yy = np.arange(H)[:, None]
    band = np.clip(np.minimum((yy - y0) / 150, (y1 - yy) / 150), 0, 1)
    a = f * band * k
    lay = np.dstack([np.full((H, W), col[0], np.float32), np.full((H, W), col[1], np.float32),
                     np.full((H, W), col[2], np.float32), a * 255]).astype(np.uint8)
    img.alpha_composite(Image.fromarray(lay, "RGBA"))


_GLOW = {}


def gsp(r, col=(255, 90, 70), p=1.6):
    k = (int(r), col, p)
    if k not in _GLOW:
        _GLOW[k] = glow_sprite(int(r), col, p)
    return _GLOW[k]


def glow_on(img, spr, x, y, k):
    a = to_arr(img); add_glow(a, spr, x, y, k)
    return to_img(a)


def eye(img, x, y, k, sc=1.0):
    r = max(4, 11 * sc); R = int(64 * max(sc, 0.35))
    spr = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    ImageDraw.Draw(spr).ellipse([R - r, R - r * 0.75, R + r, R + r * 0.75], fill=(255, 40, 30, int(255 * min(1, k))))
    g = spr.filter(ImageFilter.GaussianBlur(R / 6))
    img.alpha_composite(g, (int(x - R), int(y - R))); img.alpha_composite(g, (int(x - R), int(y - R)))
    img.alpha_composite(spr, (int(x - R), int(y - R)))
    if k > 0.6:
        ImageDraw.Draw(img).ellipse([x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3], fill=(255, 230, 200, int(255 * min(1, k))))


def P_(*p, s=1):
    return [(x * s, y * s) for x, y in p]


def rot(pts, ang, cx, cy):
    c, s_ = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * c - (y - cy) * s_, cy + (x - cx) * s_ + (y - cy) * c) for x, y in pts]


def texmul(im, fn):
    a = np.asarray(im, np.float32).copy()
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    a[..., :3] *= fn(xx, yy)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def tint(im, mul, alpha=1.0, blur=0):
    a = np.asarray(im, np.float32).copy()
    a[..., :3] *= np.array(mul, np.float32)
    a[..., 3] *= alpha
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    return out.filter(ImageFilter.GaussianBlur(blur)) if blur else out


def vgrad(top, mid, bot, ym=0.5, w=W, h=H):
    y = np.linspace(0, 1, h)[:, None]
    top, mid, bot = (np.array(c, np.float32) for c in (top, mid, bot))
    k1 = np.clip(y / ym, 0, 1); k2 = np.clip((y - ym) / (1 - ym), 0, 1)
    col = np.where(y < ym, top * (1 - k1) + mid * k1, mid * (1 - k2) + bot * k2)
    return np.broadcast_to(col[:, None, :], (h, w, 3)).astype(np.float32).copy()


class Persp:
    """One-point perspective: side (+ right), hgt (+ down from the eye), z (depth)."""
    def __init__(self, vx, vy, f):
        self.vx, self.vy, self.f = vx, vy, f

    def p(self, side, hgt, z):
        return (self.vx + side * self.f / z, self.vy + hgt * self.f / z)

    def scale_at(self, z, units, px):
        return units * self.f / z / px




def moon_sky(moon=(720, 430), r=120, top=(5, 1, 3), mid=(46, 6, 12), bot=(120, 22, 24), ym=0.45, h=H, w=W):
    a = vgrad(top, mid, bot, ym=ym, h=h, w=w)
    yy, xx = np.mgrid[0:h, 0:w]
    mx, my = moon
    dd = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
    a += np.exp(-dd / (r * 3.2))[..., None] * np.array([150, 26, 20], np.float32) * 0.9
    disc = np.clip((r - dd) / 2.5, 0, 1)[..., None]
    mcol = np.array([232, 72, 50], np.float32) * (0.9 + 0.1 * np.clip(1 - dd / r, 0, 1))[..., None]
    a = a * (1 - disc) + mcol * disc
    r2 = np.random.default_rng(7)
    for _ in range(90):
        x, y = int(r2.uniform(0, w)), int(r2.uniform(0, h * 0.4))
        a[y:y + 2, x:x + 2] += r2.uniform(30, 90)
    return a


def weave(w, h, cell=22, seed=0):
    """Woven split-bamboo wall (2/2 twill): a brightness map 0.6..1.1."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx + yy) / cell; v = (xx - yy) / cell
    a = np.floor(u).astype(int); b = np.floor(v).astype(int)
    horiz = ((a // 2 + b // 2) % 2) == 0
    fu = u - np.floor(u); fv = v - np.floor(v)
    strip = np.where(horiz, np.sin(np.pi * fu), np.sin(np.pi * fv))
    r = np.random.default_rng(seed)
    noise = r.normal(0, 0.04, (h // 8 + 1, w // 8 + 1)).repeat(8, 0).repeat(8, 1)[:h, :w]
    return (0.62 + 0.42 * strip ** 0.6 + noise).astype(np.float32)


def light_map(w, h, x, y, r, amb=0.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - x) ** 2 + ((yy - y) * 1.1) ** 2)
    return (amb + np.exp(-(d / r) ** 1.4)).astype(np.float32)

def sugar_palm(d, x, by, hgt, s=1, rnd=None):
    rnd = rnd or np.random.default_rng(1)
    top = by - hgt
    d.line([(x * s, by * s), ((x + rnd.uniform(-10, 10)) * s, top * s)], fill=255, width=int(max(3, hgt / 60) * s))
    for k in range(22):
        a = -math.pi + k * math.pi / 21 + rnd.uniform(-0.05, 0.05)
        ln = hgt * 0.14
        d.line([(x * s, top * s), ((x + math.cos(a) * ln) * s, (top + math.sin(a) * ln * 0.9) * s)], fill=255, width=int(max(2, hgt / 120) * s))
    d.ellipse([(x - hgt * 0.05) * s, (top - hgt * 0.04) * s, (x + hgt * 0.05) * s, (top + hgt * 0.05) * s], fill=255)


from art_v import frangipani, Petals

SKIN = (170, 118, 86)         # Putri
SHIRT = (176, 112, 46)        # her ochre T-shirt
APRON = (70, 22, 26)          # dark red stall apron
PANTS = (30, 24, 34)
HAIR = (12, 10, 12)
GOWN = (214, 208, 200)        # the Kuntilanak: bone-white gown
GHOST = (222, 214, 206)       # her skin
NAIL = (60, 40, 40)
BATIK = (120, 24, 28)

# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """Indonesia (Sang Saka Merah-Putih): red over white, 3:2."""
    global _FLAG
    if _FLAG is None:
        w, h, s = 300, 200, 4
        im = Image.new("RGBA", (w * s, h * s), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w * s, h * s // 2], fill=(206, 17, 38, 255))
        _FLAG = im.resize((w, h), Image.LANCZOS)
    return _FLAG


def flag_wave(t, width=230):
    fb = flag_base()
    a = np.asarray(fb, np.float32)
    h, w = a.shape[:2]
    out = np.zeros((h + 24, w, 4), np.float32)
    for x in range(w):
        ph = x / 34 - t * 5.5
        dy = int(round(7 * math.sin(ph) * (x / w + 0.15)))
        lum = 1.0 + 0.12 * math.cos(ph) - 0.06
        col = a[:, x].copy(); col[:, :3] *= lum
        out[12 + dy:12 + dy + h, x] = col
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    im2 = Image.new("RGBA", (w + 14, h + 24), (0, 0, 0, 0)); im2.alpha_composite(im, (14, 0))
    ImageDraw.Draw(im2).rectangle([0, 0, 7, h + 23], fill=(200, 190, 170, 255))
    sc = width / im2.width
    return im2.resize((width, int(im2.height * sc)), Image.LANCZOS)


def put_header(out, hdr, t, flag=True):
    for im, (x, y), al in header_layers(hdr, t):
        if al > 0.01:
            out.alpha_composite(with_alpha(im, al), (int(x), int(y)))
    if flag:
        fw = flag_wave(t, 190)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 40))


def laugh_ui(near, home, t, k=1.0):
    """The ticking clock: HER LAUGH meter (loud = FAR = safe, soft = NEAR = danger; 5 bars fill red as she comes
    closer) + the distance home."""
    f1 = font(INTER_SB, 40); f2 = font(INTER_M, 24); f3 = font(INTER_SB, 34)
    w, h = 720, 112
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    danger = near > 0.6
    blink = (math.sin(t * 10) > -0.2) if danger else True
    d.rounded_rectangle([0, 0, w - 1, h - 1], 32, fill=(0, 0, 0, int(190 * k)),
                        outline=((255, 50, 40) if danger else (255, 170, 140)) + (int(220 * k),), width=3)
    # sound icon: a mouth-ish dot + arcs (fewer, smaller arcs when she is near = a soft laugh)
    cx, cy = 52, 56
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(250, 240, 230, int(255 * k)))
    n_arcs = 3 - int(round(2 * near))
    for i in range(n_arcs):
        r = 20 + i * 13
        d.arc([cx - r, cy - r, cx + r, cy + r], -50, 50, fill=(250, 240, 230, int(230 * k)), width=4)
    d.text((112, 30), "HER LAUGH", font=f2, fill=(255, 190, 160, int(255 * k)), anchor="lm")
    st = "NEAR" if danger else ("FAR" if near < 0.35 else "CLOSER")
    col = (255, 60, 45) if danger else ((240, 236, 228) if near < 0.35 else (255, 170, 90))
    if blink:
        d.text((112, 76), st, font=f1, fill=col + (int(255 * k),), anchor="lm")
    for i in range(5):                                                # nearness bars
        x = 270 + i * 30
        on = near * 5 > i + 0.2
        bh = 18 + i * 8
        d.rounded_rectangle([x, 86 - bh, x + 18, 86], 4, fill=((255, 50, 40) if on else (90, 70, 70)) + (int(255 * k),))
    d.line([(436, 22), (436, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    hx, hy = 476, 58                                                  # a little house icon
    d.polygon([(hx - 22, hy - 2), (hx, hy - 24), (hx + 22, hy - 2)], fill=(255, 214, 160, int(255 * k)))
    d.rectangle([hx - 16, hy - 2, hx + 16, hy + 22], fill=(255, 214, 160, int(255 * k)))
    d.rectangle([hx - 5, hy + 8, hx + 5, hy + 22], fill=(0, 0, 0, int(255 * k)))
    d.text((600, 36), "HOME", font=f2, fill=(255, 190, 160, int(255 * k)), anchor="mm")
    d.text((600, 76), home, font=f3, fill=(255, 240, 228, int(255 * k)), anchor="mm")
    return im


def put_ui(out, near, home, t, k=1.0, y=200):
    if k <= 0.01:
        return
    ui = laugh_ui(near, home, t, k)
    out.alpha_composite(ui, (int(W / 2 - ui.width / 2), int(y)))


# ============================================================ Putri
_PC = {}


def putri(phase=0.0, run=0.0, back=False, scale=1.0, look=0.0, strike=-1.0, apron=True):
    """Putri: ochre T-shirt, dark red stall apron, dark trousers, sandals, black hair in a ponytail.
    strike 0..1 (>=0): right arm raised with a wooden stick (1 = up, 0 = hitting forward). look: pupils up (+).
    Returns (RGBA, feet_x, feet_y)."""
    q = (round(phase * 12) % 12, round(run, 1), back, round(scale, 2), round(look, 1), round(strike, 1), apron)
    if q in _PC:
        return _PC[q]
    w, h = 520, 920
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.25 + 0.75 * run)
    L = 14 * run

    feet = {}
    for sg in (-1, 1):
        a = sg * sw * 0.5
        feet[sg] = (cx + sg * 24 + math.sin(a) * 80 + L * 0.2, 860 - abs(math.sin(a)) * 34 * run)

    def legs(d, s):
        for sg in (-1, 1):
            fx, fy = feet[sg]
            kx = cx + sg * 26 + L * .4 + (fx - cx - sg * 24) * 0.45
            d.line([((cx + sg * 26 + L * .5) * s, 450 * s), (kx * s, 650 * s), (fx * s, (fy - 20) * s)], fill=255, width=int(44 * s), joint="curve")
            d.rectangle([(cx + sg * 4 - 40 + L * .5) * s, 430 * s, (cx + sg * 4 + 40 + L * .5) * s, 520 * s], fill=255)

    def soles(d, s):
        for sg in (-1, 1):
            fx, fy = feet[sg]
            d.ellipse([(fx - 28) * s, (fy - 14) * s, (fx + 30) * s, (fy + 10) * s], fill=255)

    def torso(d, s):
        d.polygon(P_((cx - 72 + L, 200), (cx + 72 + L, 200), (cx + 64 + L * .8, 340), (cx + 74 + L * .6, 480), (cx - 74 + L * .6, 480), (cx - 64 + L * .8, 340), s=s), fill=255)
        d.ellipse([(cx - 90 + L) * s, 190 * s, (cx - 40 + L) * s, 250 * s], fill=255)
        d.ellipse([(cx + 40 + L) * s, 190 * s, (cx + 90 + L) * s, 250 * s], fill=255)

    def apr(d, s):
        d.polygon(P_((cx - 50 + L, 270), (cx + 50 + L, 270), (cx + 70 + L * .6, 600), (cx - 70 + L * .6, 600), s=s), fill=255)

    hands = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 76 + L, 220
        a = -sg * sw * 0.9
        if strike >= 0 and sg == 1:
            u = strike
            ex, ey = sx + 60 - 10 * u, sy + 60 - 170 * u
            hx, hy = ex + 110 - 90 * u, ey + 40 - 150 * u
        else:
            ex, ey = sx + math.sin(a) * 90 + sg * 10, sy + math.cos(a) * 104
            b = a - 0.9 * run * sg
            hx, hy = ex + math.sin(b) * 88, ey + math.cos(b) * 84 - 40 * run
        hands[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            pts = hands[sg]
            d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(26 * s), joint="curve")
            hx, hy = pts[2]
            d.ellipse([(hx - 16) * s, (hy - 16) * s, (hx + 16) * s, (hy + 16) * s], fill=255)

    def sleeves(d, s):
        for sg in (-1, 1):
            (sx, sy), (ex, ey), _ = hands[sg]
            mx, my = sx + (ex - sx) * 0.45, sy + (ey - sy) * 0.45
            d.line([(sx * s, sy * s), (mx * s, my * s)], fill=255, width=int(42 * s))
            d.ellipse([(sx - 28) * s, (sy - 26) * s, (sx + 28) * s, (sy + 28) * s], fill=255)

    Lh = L * 1.2

    def head(d, s):
        d.rectangle([(cx - 18 + Lh) * s, 140 * s, (cx + 18 + Lh) * s, 200 * s], fill=255)
        d.ellipse([(cx - 50 + Lh) * s, 32 * s, (cx + 50 + Lh) * s, 168 * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 54 + Lh) * s, 24 * s, (cx + 54 + Lh) * s, 140 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 54 + Lh, 82), (cx - 50 + Lh, 118), (cx - 34 + Lh, 66), (cx + 34 + Lh, 66), (cx + 50 + Lh, 118), (cx + 54 + Lh, 82), s=s), fill=255)
        swing = 30 * sw + 40 * run
        if back:
            d.ellipse([(cx - 52 + Lh) * s, 28 * s, (cx + 52 + Lh) * s, 160 * s], fill=255)
            d.polygon(P_((cx - 18 + Lh, 70), (cx + 18 + Lh, 70), (cx + 24 + Lh - swing, 300), (cx + Lh - swing, 330), (cx - 20 + Lh - swing, 290), s=s), fill=255)
        else:
            d.polygon(P_((cx + 40 + Lh, 50), (cx + 66 + Lh, 70), (cx + 86 + Lh - swing, 240), (cx + 62 + Lh - swing, 260), (cx + 50 + Lh, 120), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(soles, (w, h), (40, 30, 30), 6))
    img.alpha_composite(shade(legs, (w, h), PANTS, 22, rim_strength=1.1))
    if not back:
        img.alpha_composite(shade(arms, (w, h), SKIN, 10))
    img.alpha_composite(shade(torso, (w, h), SHIRT, 34))
    if apron and not back:
        img.alpha_composite(shade(apr, (w, h), APRON, 20))
    img.alpha_composite(shade(sleeves, (w, h), SHIRT, 14))
    if back:
        img.alpha_composite(shade(arms, (w, h), SKIN, 10))
        if apron:
            dd = ImageDraw.Draw(img)
            dd.line([(cx - 70 + L, 300), (cx + 70 + L, 300)], fill=APRON + (255,), width=8)   # apron strings
            dd.line([(cx + L, 300), (cx - 14 + L, 350)], fill=APRON + (255,), width=6)
    img.alpha_composite(shade(head, (w, h), SKIN, 26))
    img.alpha_composite(shade(hair, (w, h), HAIR, 12, rim_strength=1.1))
    d = ImageDraw.Draw(img)
    if not back:
        for sg in (-1, 1):
            ex_, ey_ = cx + sg * 19 + Lh, 104 - 6 * look
            d.ellipse([ex_ - 10, ey_ - 8, ex_ + 10, ey_ + 8], fill=(240, 236, 230, 255))
            d.ellipse([ex_ - 5, ey_ - 6 - 3 * look, ex_ + 5, ey_ + 4 - 3 * look], fill=(15, 10, 10, 255))
            d.line([(ex_ - 12, ey_ - 18), (ex_ + 12, ey_ - 16 - 3 * sg)], fill=(20, 12, 10, 255), width=4)
        d.ellipse([cx - 7 + Lh, 136, cx + 9 + Lh, 148], fill=(70, 26, 24, 255))
    if strike >= 0:                                                       # the wooden stick (kentongan beater)
        (_, _), (ex, ey), (hx, hy) = hands[1]
        a = math.atan2(hy - ey, hx - ex) - 0.4
        d.line([(hx - math.cos(a) * 20, hy - math.sin(a) * 20), (hx + math.cos(a) * 150, hy + math.sin(a) * 150)], fill=(120, 80, 46, 255), width=14)
    if scale != 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    out = (img, cx * scale, 866 * scale)
    _PC[q] = out
    return out


_PCR = {}


def putri_crouch(scale=1.0, look=0.0, cover=0.0):
    """Putri crouched, hugging her knees, one hand over her mouth (cover 0..1). look: head turns up (+).
    Returns (RGBA, feet_x, feet_y)."""
    k = (round(scale, 2), round(look, 1), round(cover, 1))
    if k in _PCR:
        return _PCR[k]
    w, h = 520, 660
    cx = w / 2
    L = look * 26

    def legs(d, s):
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 52 - 60) * s, 290 * s, (cx + sg * 52 + 60) * s, 410 * s], fill=255)       # knees
            d.polygon(P_((cx + sg * 52 - 56, 350), (cx + sg * 52 + 56, 350), (cx + sg * 66 + 40, 600), (cx + sg * 66 - 40, 600), s=s), fill=255)
        d.ellipse([(cx - 120) * s, 420 * s, (cx + 120) * s, 620 * s], fill=255)

    def feet(d, s):
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 70 - 42) * s, 594 * s, (cx + sg * 70 + 42) * s, 630 * s], fill=255)

    def body(d, s):
        d.polygon(P_((cx - 88, 200), (cx + 88, 200), (cx + 100, 400), (cx - 100, 400), s=s), fill=255)
        d.ellipse([(cx - 106) * s, 188 * s, (cx - 54) * s, 260 * s], fill=255)
        d.ellipse([(cx + 54) * s, 188 * s, (cx + 106) * s, 260 * s], fill=255)

    def arms(d, s):
        d.line([((cx - 96) * s, 232 * s), ((cx - 130) * s, 330 * s), ((cx + 40) * s, 360 * s)], fill=255, width=int(28 * s), joint="curve")
        d.ellipse([(cx + 24) * s, 342 * s, (cx + 58) * s, 376 * s], fill=255)
        hy = 300 - 120 * cover
        d.line([((cx + 96) * s, 232 * s), ((cx + 120) * s, 320 * s), ((cx + 20 + L * .3) * s, hy * s)], fill=255, width=int(26 * s), joint="curve")
        d.ellipse([(cx + 2 + L * .3) * s, (hy - 18) * s, (cx + 38 + L * .3) * s, (hy + 18) * s], fill=255)

    def head(d, s):
        d.ellipse([(cx - 50 + L * .3) * s, (70 - L) * s, (cx + 50 + L * .3) * s, (204 - L) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 56 + L * .3) * s, (58 - L) * s, (cx + 56 + L * .3) * s, (176 - L) * s], 180, 360, fill=255)
        d.polygon(P_((cx - 56 + L * .3, 116 - L), (cx - 52 + L * .3, 150 - L), (cx - 36 + L * .3, 100 - L), (cx + 36 + L * .3, 100 - L), (cx + 52 + L * .3, 150 - L), (cx + 56 + L * .3, 116 - L), s=s), fill=255)
        d.polygon(P_((cx - 40 + L * .3, 80 - L), (cx - 70, 110), (cx - 96, 270), (cx - 70, 290), (cx - 50, 160), s=s), fill=255)  # ponytail over her shoulder

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(body, (w, h), SHIRT, 36))
    img.alpha_composite(shade(head, (w, h), SKIN, 28))
    img.alpha_composite(shade(hair, (w, h), HAIR, 12))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):                                                      # wide scared eyes
        ex_ = cx + sg * 19 + L * .3; ey_ = 136 - L * 1.1
        d.ellipse([ex_ - 11, ey_ - 9, ex_ + 11, ey_ + 9], fill=(240, 236, 230, 255))
        d.ellipse([ex_ - 4 + look * 3, ey_ - 8, ex_ + 4 + look * 3, ey_ + 1], fill=(15, 10, 10, 255))
    img.alpha_composite(shade(legs, (w, h), PANTS, 30, rim_strength=1.1))
    img.alpha_composite(shade(feet, (w, h), (40, 30, 30), 6))
    img.alpha_composite(shade(arms, (w, h), SKIN, 12))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 620 * scale)
    _PCR[k] = out
    return out


# ============================================================ the Kuntilanak
_KU = {}


def kunti(pose="float", sway=0.0):
    """The Kuntilanak: a too-tall woman in a long bone-white gown with a ragged hem, black hair down to her waist hiding
    most of her face, pale hands with long dark nails, red eyes (drawn by put_kunti). No gore.
    pose: "float" (standing in the air, no feet), "perch" (crouched on a branch, gown + hair hanging),
          "hang" (upside down from above: gown at the top, head at the bottom, hair hanging down).
    sway -1..1 bends the hair and hem. Returns (RGBA, anchor_x, anchor_y, [eyes]).
    Anchors: float = bottom of the hem centre, perch = the branch point, hang = top centre."""
    key = (pose, round(sway, 1))
    if key in _KU:
        return _KU[key]
    w, h = 760, 1600
    cx = w / 2
    r = np.random.default_rng(16)
    sw = sway * 40
    if pose == "hang":
        img, ax, ay, ee = _kunti_hang(sw)
        _KU[key] = (img, ax, ay, ee)
        return _KU[key]
    perch = pose == "perch"
    hc = (cx, 220 if not perch else 520)                                  # head centre
    sh = hc[1] + 120                                                       # shoulders
    hem = 1460 if not perch else 1500

    def gown(d, s):
        if perch:
            d.ellipse([(cx - 190) * s, (sh + 80) * s, (cx + 190) * s, (sh + 380) * s], fill=255)                   # knees drawn up
            d.polygon(P_((cx - 120, sh), (cx + 120, sh), (cx + 190, sh + 260), (cx + 220 + sw, hem), (cx - 220 + sw, hem), (cx - 190, sh + 260), s=s), fill=255)
        else:
            d.polygon(P_((cx - 110, sh), (cx + 110, sh), (cx + 130, sh + 300), (cx + 300 + sw, hem), (cx - 300 + sw, hem), (cx - 130, sh + 300), s=s), fill=255)
            d.ellipse([(cx - 140) * s, (sh - 30) * s, (cx + 140) * s, (sh + 90) * s], fill=255)
        n = 14                                                             # ragged hem
        for k in range(n):
            x = cx - 290 + sw + k * 580 / (n - 1)
            dy = r.uniform(30, 120)
            d.polygon(P_((x - 26, hem - 20), (x + 26, hem - 20), (x + sw * .5 + r.uniform(-10, 10), hem + dy), s=s), fill=255)

    arm = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 118, sh + 30
        if perch:
            ex, ey = sx + sg * 70, sy + 200; hx, hy = cx + sg * 80, sy + 320            # hands on her knees / the branch
        else:
            ex, ey = sx + sg * 40, sy + 300; hx, hy = sx + sg * 60 + sw * .3, sy + 640   # far too long
        arm[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def sleeves(d, s):
        for sg in (-1, 1):
            p = arm[sg]
            d.line([(x * s, y * s) for x, y in p[:2]] + [((p[1][0] * .4 + p[2][0] * .6) * s, (p[1][1] * .4 + p[2][1] * .6) * s)], fill=255, width=int(56 * s), joint="curve")

    def hands(d, s):
        for sg in (-1, 1):
            (ex, ey), (hx, hy) = arm[sg][1], arm[sg][2]
            d.line([(((ex + hx) / 2) * s, ((ey + hy) / 2) * s), (hx * s, hy * s)], fill=255, width=int(26 * s))
            d.ellipse([(hx - 20) * s, (hy - 20) * s, (hx + 20) * s, (hy + 20) * s], fill=255)

    def nails(d, s):
        for sg in (-1, 1):
            (ex, ey), (hx, hy) = arm[sg][1], arm[sg][2]
            a0 = math.atan2(hy - ey, hx - ex)
            for f in range(4):
                a = a0 + (f - 1.5) * 0.2
                d.line([(hx * s, hy * s), ((hx + math.cos(a) * 70) * s, (hy + math.sin(a) * 70) * s)], fill=255, width=int(8 * s))

    hx0, hy0 = hc

    def head(d, s):
        d.ellipse([(hx0 - 56) * s, (hy0 - 74) * s, (hx0 + 56) * s, (hy0 + 80) * s], fill=255)
        d.rectangle([(hx0 - 24) * s, (hy0 + 40) * s, (hx0 + 24) * s, (sh + 10) * s], fill=255)

    def hair(d, s):
        d.ellipse([(hx0 - 74) * s, (hy0 - 96) * s, (hx0 + 74) * s, (hy0 + 40) * s], fill=255)
        bot = hy0 + (700 if not perch else 760)
        for sg in (-1, 1):                                                  # two curtains, a slit of face between them
            d.polygon(P_((hx0 + sg * 8, hy0 - 80), (hx0 + sg * 74, hy0 - 40), (hx0 + sg * 150 + sw, bot - 80), (hx0 + sg * 90 + sw, bot),
                         (hx0 + sg * 20 + sw * .6, bot - 120), (hx0 + sg * 22, hy0 + 60), s=s), fill=255)
        for k in range(22):                                                 # strands
            x = hx0 - 140 + k * 13
            ln = r.uniform(380, 760)
            d.line([(x * .5 + hx0 * .5) * s, (hy0 - 40) * s, (x + sw * (ln / 700)) * s, (hy0 + ln) * s], fill=255, width=int(r.uniform(6, 12) * s))

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(gown, (w, h), GOWN, 70, rim_strength=1.0))
    gd = ImageDraw.Draw(img)
    for k in range(9):                                                      # long folds in the gown
        x = cx - 160 + k * 40
        gd.line([(x * .7 + cx * .3, sh + 120), (x + sw * .6, hem - 40)], fill=(150, 140, 136, 120), width=3)
    img.alpha_composite(shade(sleeves, (w, h), GOWN, 22))
    img.alpha_composite(shade(hands, (w, h), GHOST, 10))
    img.alpha_composite(shade(nails, (w, h), NAIL, 3, rim_strength=0.6))
    img.alpha_composite(shade(head, (w, h), GHOST, 34))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        d.ellipse([hx0 + sg * 22 - 14, hy0 - 6, hx0 + sg * 22 + 14, hy0 + 14], fill=(24, 8, 10, 255))       # eye hollows
    d.arc([hx0 - 34, hy0 + 18, hx0 + 34, hy0 + 62], 20, 160, fill=(40, 8, 10, 255), width=5)              # a thin smile
    img.alpha_composite(shade(hair, (w, h), HAIR, 12, rim_strength=1.2))
    eyes = [(hx0 - 22, hy0 + 4), (hx0 + 22, hy0 + 4)]
    out = (img, cx, hem if not perch else sh + 330, eyes)
    _KU[key] = out
    return out


def _kunti_hang(sw):
    """Upside down: hanging from a gap above. Gown at the top, then her shoulders, then her upside-down face, and her
    black hair hanging straight down below it. Anchor: top centre."""
    w, h = 760, 1600
    cx = w / 2
    r = np.random.default_rng(17)
    hy0 = 900                                                              # head centre
    sh = hy0 - 130

    def gown(d, s):
        d.polygon(P_((cx - 170, 0), (cx + 170, 0), (cx + 130, sh), (cx - 130, sh), s=s), fill=255)
        d.ellipse([(cx - 140) * s, (sh - 80) * s, (cx + 140) * s, (sh + 30) * s], fill=255)

    def arms(d, s):                                                    # wide sleeves to the elbow
        for sg in (-1, 1):
            d.line([((cx + sg * 110) * s, (sh - 40) * s), ((cx + sg * 130) * s, (sh + 150) * s)], fill=255, width=int(54 * s))

    def forearms(d, s):
        for sg in (-1, 1):
            d.line([((cx + sg * 130) * s, (sh + 150) * s), ((cx + sg * 118) * s, (sh + 420) * s)], fill=255, width=int(24 * s))
            d.ellipse([(cx + sg * 118 - 18) * s, (sh + 402) * s, (cx + sg * 118 + 18) * s, (sh + 438) * s], fill=255)

    def nails(d, s):
        for sg in (-1, 1):
            hx, hy = cx + sg * 118, sh + 420
            for f in range(4):
                a = math.pi / 2 + (f - 1.5) * 0.2
                d.line([(hx * s, hy * s), ((hx + math.cos(a) * 74) * s, (hy + math.sin(a) * 74) * s)], fill=255, width=int(8 * s))

    def head(d, s):
        d.ellipse([(cx - 58) * s, (hy0 - 80) * s, (cx + 58) * s, (hy0 + 76) * s], fill=255)
        d.rectangle([(cx - 24) * s, (sh - 10) * s, (cx + 24) * s, (hy0 - 40) * s], fill=255)

    def hair(d, s):
        d.ellipse([(cx - 70) * s, (hy0 + 36) * s, (cx + 70) * s, (hy0 + 120) * s], fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 50, hy0 - 70), (cx + sg * 66, hy0 - 70), (cx + sg * 74, hy0 + 60), (cx + sg * 40, hy0 + 60), s=s), fill=255)
        d.polygon(P_((cx - 76, hy0 + 70), (cx + 76, hy0 + 70), (cx + 110 + sw, h - 60), (cx - 110 + sw, h - 60), s=s), fill=255)
        for k in range(20):
            x = cx - 100 + k * 10.5
            d.line([(x * s, (hy0 + 80) * s), ((x + sw * 1.2 + r.uniform(-14, 14)) * s, (h - r.uniform(0, 80)) * s)], fill=255, width=int(r.uniform(6, 12) * s))

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(gown, (w, h), GOWN, 60))
    img.alpha_composite(shade(forearms, (w, h), GHOST, 10))
    img.alpha_composite(shade(arms, (w, h), GOWN, 16))
    img.alpha_composite(shade(nails, (w, h), NAIL, 3, rim_strength=0.6))
    img.alpha_composite(shade(head, (w, h), GHOST, 34))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):                                                     # upside-down face: eyes below the smile
        d.ellipse([cx + sg * 22 - 14, hy0 - 14, cx + sg * 22 + 14, hy0 + 6], fill=(24, 8, 10, 255))
    d.arc([cx - 34, hy0 - 62, cx + 34, hy0 - 18], 200, 340, fill=(40, 8, 10, 255), width=5)
    img.alpha_composite(shade(hair, (w, h), HAIR, 12, rim_strength=1.2))
    return img, cx, 0, [(cx - 22, hy0 - 4), (cx + 22, hy0 - 4)]


def put_kunti(img, x, y, scale, t, pose="float", sway=None, eyes=1.0, aura=0.5, alpha=1.0, dark=0.0, rot=0.0):
    sw = math.sin(t * 1.3) * 0.6 if sway is None else sway
    body, ax, ay, ee = kunti(pose, round(sw * 5) / 5)
    if rot:
        Dd = int(max(body.width, body.height) * 1.1)
        big = Image.new("RGBA", (2 * Dd, 2 * Dd), (0, 0, 0, 0)); big.alpha_composite(body, (int(Dd - ax), int(Dd - ay)))
        ee = [(ex - ax + Dd, ey - ay + Dd) for ex, ey in ee]
        body = big.rotate(rot, resample=Image.BICUBIC, center=(Dd, Dd))
        c, s_ = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))
        ee = [(Dd + (ex - Dd) * c - (ey - Dd) * s_, Dd + (ex - Dd) * s_ + (ey - Dd) * c) for ex, ey in ee]
        bb = body.getbbox() or (0, 0, 1, 1)
        body = body.crop(bb); ax, ay = Dd - bb[0], Dd - bb[1]; ee = [(ex - bb[0], ey - bb[1]) for ex, ey in ee]
    g = body.resize((max(1, int(body.width * scale)), max(1, int(body.height * scale))), Image.LANCZOS)
    if dark > 0:
        g = tint(g, (1 - 0.85 * dark, 1 - 0.9 * dark, 1 - 0.9 * dark))
    if alpha < 1:
        g = with_alpha(g, alpha)
    gx, gy = int(x - ax * scale), int(y - ay * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(max(3, 34 * scale)))
        lay = Image.new("RGBA", g.size, (255, 40, 30, 0)); lay.putalpha(al.point(lambda v: int(v * aura * alpha)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    if eyes > 0:
        k = eyes * alpha * (0.65 + 0.35 * math.sin(t * 5) ** 2)
        for ex, ey in ee:
            eye(img, gx + ex * scale, gy + ey * scale, k, max(0.2, scale * 0.9))
    return img


_KF = {}


def kunti_face(grin=1.0, inv=False):
    """Close-up for the jump scares: bone-pale face between two curtains of black hair, strands across it, deep eye
    hollows (red glow drawn by put_kface), a thin smile far too wide (no teeth, no gore), the white gown's collar.
    inv: upside down. Face centre at (450, 470)."""
    k = (round(grin, 1), inv)
    if k in _KF:
        return _KF[k]
    w, h = 900, 1100
    cx, cy = 450, 470

    def face(d, s):
        d.polygon(P_((cx - 180, cy - 230), (cx + 180, cy - 230), (cx + 205, cy - 20), (cx + 160, cy + 200), (cx + 70, cy + 300),
                     (cx, cy + 320), (cx - 70, cy + 300), (cx - 160, cy + 200), (cx - 205, cy - 20), s=s), fill=255)
        d.ellipse([(cx - 205) * s, (cy - 380) * s, (cx + 205) * s, (cy + 40) * s], fill=255)

    def neck(d, s):
        d.rectangle([(cx - 90) * s, (cy + 200) * s, (cx + 90) * s, h * s], fill=255)

    def collar(d, s):
        d.polygon(P_((cx - 420, h), (cx - 300, cy + 380), (cx - 90, cy + 330), (cx, cy + 420), (cx + 90, cy + 330), (cx + 300, cy + 380), (cx + 420, h), s=s), fill=255)

    def hair(d, s):
        r = np.random.default_rng(29)
        d.pieslice([(cx - 250) * s, (cy - 430) * s, (cx + 250) * s, (cy + 60) * s], 180, 360, fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 30, cy - 400), (cx + sg * 250, cy - 200), (cx + sg * 320, cy + 640), (cx + sg * 150, cy + 660), (cx + sg * 175, cy + 40), (cx + sg * 110, cy - 250), s=s), fill=255)
        for kk in range(12):
            x = cx - 190 + kk * 34 + r.uniform(-8, 8)
            if abs(abs(x - cx) - 85) < 34:
                continue
            ln = r.uniform(300, 700)
            d.line([(x * s, (cy - 260) * s), ((x + r.uniform(-30, 30)) * s, (cy - 260 + ln * .5) * s), ((x + r.uniform(-50, 50)) * s, (cy - 260 + ln) * s)],
                   fill=255, width=int(r.uniform(8, 16) * s), joint="curve")

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(neck, (w, h), GHOST, 40))
    img.alpha_composite(shade(collar, (w, h), GOWN, 50))
    img.alpha_composite(shade(face, (w, h), GHOST, 110, rim_strength=0.9))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        d.ellipse([cx + sg * 85 - 54, cy - 48, cx + sg * 85 + 54, cy + 36], fill=(26, 10, 12, 255))
        d.line([(cx + sg * 30, cy - 94), (cx + sg * 132, cy - 80)], fill=(90, 70, 70, 255), width=6)
    d.polygon([(cx - 12, cy + 70), (cx + 12, cy + 70), (cx + 20, cy + 118), (cx - 20, cy + 118)], fill=(180, 170, 164, 255))
    gw = 120 + 90 * grin
    d.arc([cx - gw, cy + 60, cx + gw, cy + 230 + 30 * grin], 15, 165, fill=(28, 6, 8, 255), width=12)
    for sg in (-1, 1):
        d.line([(cx + sg * gw * 0.95, cy + 170), (cx + sg * (gw + 30), cy + 120)], fill=(28, 6, 8, 255), width=10)
    img.alpha_composite(shade(hair, (w, h), HAIR, 24, rim_strength=1.3))
    eyes = [(cx - 85, cy - 6), (cx + 85, cy - 6)]
    if inv:
        img = img.rotate(180, resample=Image.BICUBIC, center=(cx, cy))
        eyes = [(2 * cx - x, 2 * cy - y) for x, y in eyes]
    _KF[k] = (img, eyes)
    return _KF[k]


def put_kface(img, x, y, scale, t, eyes=1.0, grin=1.0, tilt=0.0, aura=0.7, alpha=1.0, inv=False):
    fimg, ee = kunti_face(grin, inv)
    cxf, cyf = 450, 470
    g = fimg.rotate(tilt, resample=Image.BICUBIC, center=(cxf, cyf)) if tilt else fimg
    g = g.resize((int(g.width * scale), int(g.height * scale)), Image.LANCZOS)
    if alpha < 1:
        g = with_alpha(g, alpha)
    gx, gy = int(x - cxf * scale), int(y - cyf * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(30))
        lay = Image.new("RGBA", g.size, (255, 40, 30, 0)); lay.putalpha(al.point(lambda v: int(v * aura * alpha)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    if eyes > 0:
        a = math.radians(-tilt)
        k = eyes * alpha * (0.75 + 0.25 * math.sin(t * 6) ** 2)
        for ex, ey in ee:
            dx, dy = ex - cxf, ey - cyf
            rx, ry = cxf + dx * math.cos(a) - dy * math.sin(a), cyf + dx * math.sin(a) + dy * math.cos(a)
            eye(img, gx + rx * scale, gy + ry * scale, k, scale * 2.2)
    return img


def kface_full(t, t0, inv=False, scale=1.25, y=880, bg=(6, 1, 2), tilt=0.0, x=540):
    img = Image.new("RGBA", (W, H), bg + (255,))
    return put_kface(img, x, y + 120 * ss(t, t0, t0 + 0.15) * (1 if not inv else -1), scale, t, eyes=1.0, grin=1.0, aura=0.9, inv=inv, tilt=tilt)


_FR = {}


def flower(size, rot=0):
    k = (int(size), int(rot) // 15)
    if k not in _FR:
        _FR[k] = frangipani(int(size)).rotate(k[1] * 15, Image.BICUBIC, expand=True)
    return _FR[k]


# ============================================================ sets
def banyan_canopy(d, cx, cy, rx, ry, rnd, n=60, s=1):
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi); rr = math.sqrt(rnd.uniform(0, 1))
        x = cx + math.cos(a) * rx * rr; y = cy + math.sin(a) * ry * rr
        r = rnd.uniform(40, 110)
        d.ellipse([(x - r) * s, (y - r * 0.8) * s, (x + r) * s, (y + r * 0.8) * s], fill=255)


class Riverfront:
    """Midnight on the Kapuas riverfront in Pontianak: the far bank with stilt houses and a long lit bridge, the black
    river with the red moon's road on it, a wooden klotok boat, the plank promenade, Putri's family noodle stall (a
    wooden gerobak cart with a glass case and a red 'MIE AYAM' sign under a sagging tarp, a hanging bulb, red plastic
    stools) and a giant banyan on the left with curtains of aerial roots. Parallax layers, cam pans right."""
    def __init__(self):
        r = np.random.default_rng(161)
        WW = W + 300
        self.sky = to_img(moon_sky((800, 360), 120, top=(4, 1, 2), mid=(46, 6, 12), bot=(120, 22, 24), ym=0.48))
        far = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(far)
        fd.rectangle([0, 930, WW, 990], fill=(30, 6, 9, 255))
        x = 0
        while x < WW:                                                   # stilt houses on the far bank
            bw = r.uniform(60, 130); bh = r.uniform(30, 70)
            fd.rectangle([x, 930 - bh, x + bw, 950], fill=(30, 6, 9, 255))
            fd.polygon([(x - 8, 930 - bh), (x + bw / 2, 930 - bh - r.uniform(14, 30)), (x + bw + 8, 930 - bh)], fill=(36, 7, 10, 255))
            if r.random() < 0.3:
                fd.rectangle([x + bw * .3, 930 - bh + 12, x + bw * .3 + 12, 930 - bh + 24], fill=(255, 140, 70, 255))
            x += bw + r.uniform(4, 30)
        for k in range(6):
            sugar_palm(fd, r.uniform(0, WW), 930, r.uniform(110, 170), 1, r)
        # the long bridge
        fd.rectangle([180, 842, WW - 60, 856], fill=(44, 9, 12, 255))
        for k in range(9):
            bx = 220 + k * 150
            fd.rectangle([bx, 856, bx + 14, 960], fill=(40, 8, 11, 255))
        self.lamps = [(200 + k * 50, 836) for k in range(int((WW - 260) / 50))]
        self.far = far.filter(ImageFilter.GaussianBlur(1.0))
        # river
        self.river_y = (960, 1310)
        riv = vgrad((24, 5, 7), (16, 3, 5), (10, 2, 3), 0.5, WW, self.river_y[1] - self.river_y[0])
        self.river = riv
        # klotok boat
        bl = Image.new("RGBA", (WW, H), (0, 0, 0, 0))

        def hull(d, s):
            d.polygon(P_((700, 1150), (1240, 1150), (1290, 1120), (1250, 1196), (740, 1196), (660, 1130), s=s), fill=255)

        def cabin(d, s):
            d.rectangle([860 * s, 1060 * s, 1100 * s, 1152 * s], fill=255)
            d.polygon(P_((840, 1066), (1120, 1066), (1100, 1040), (860, 1040), s=s), fill=255)
        bl.alpha_composite(shade(hull, (WW, H), (70, 30, 24), 16))
        bl.alpha_composite(shade(cabin, (WW, H), (90, 50, 36), 12))
        bd = ImageDraw.Draw(bl)
        for k in range(4):
            bd.rectangle([880 + k * 56, 1080, 916 + k * 56, 1110], fill=(16, 4, 5, 255))
        bd.line([(700, 1164), (1250, 1164)], fill=(150, 40, 30, 255), width=4)
        self.boat = bl
        # promenade + stall
        nl = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); nd = ImageDraw.Draw(nl)
        nd.rectangle([0, 1300, WW, H], fill=(62, 34, 26, 255))
        for k in range(26):
            y = 1300 + (k ** 1.5) * 4.2
            nd.line([(0, y), (WW, y)], fill=(30, 14, 10, 255), width=3)
        for k in range(16):
            x = k * 90
            nd.rectangle([x, 1250, x + 12, 1310], fill=(50, 26, 20, 255))
        nd.rectangle([0, 1246, WW, 1258], fill=(70, 38, 28, 255))                     # low rail
        self.near_floor = nl
        st = Image.new("RGBA", (WW, H), (0, 0, 0, 0))

        def poles(d, s):
            for x in (470, 980):
                d.rectangle([(x - 9) * s, 880 * s, (x + 9) * s, 1560 * s], fill=255)

        def tarp(d, s):
            pts = [(440, 870), (1010, 850)] + [(1010 - k * 57, 900 + 26 * math.sin(k / 10 * math.pi)) for k in range(11)]
            d.polygon(P_(*pts, s=s), fill=255)

        def cart(d, s):
            d.rectangle([560 * s, 1310 * s, 920 * s, 1560 * s], fill=255)
            d.rectangle([548 * s, 1296 * s, 932 * s, 1320 * s], fill=255)

        def glass(d, s):
            d.rectangle([580 * s, 1170 * s, 900 * s, 1300 * s], fill=255)

        def stools(d, s):
            for x, y in ((300, 1600), (400, 1660)):
                d.ellipse([(x - 50) * s, (y - 14) * s, (x + 50) * s, (y + 14) * s], fill=255)
                d.polygon(P_((x - 46, y), (x + 46, y), (x + 38, y + 90), (x - 38, y + 90), s=s), fill=255)
        st.alpha_composite(shade(poles, (WW, H), (110, 90, 60), 6))
        st.alpha_composite(shade(tarp, (WW, H), (130, 30, 30), 30, rim=(255, 120, 80)))
        st.alpha_composite(shade(cart, (WW, H), (120, 64, 38), 20))
        gl = shade(glass, (WW, H), (60, 40, 40), 10)
        st.alpha_composite(with_alpha(gl, 0.75))
        sd = ImageDraw.Draw(st)
        sd.rectangle([580, 1170, 900, 1300], outline=(160, 120, 90, 255), width=6)
        for k in range(5):                                                          # bowls + noodle nests in the case
            sd.ellipse([600 + k * 58, 1250, 650 + k * 58, 1280], fill=(230, 220, 200, 255))
            sd.ellipse([610 + k * 58, 1240, 640 + k * 58, 1260], fill=(230, 190, 90, 255))
        sd.rectangle([590, 1340, 890, 1430], fill=(160, 24, 28, 255))                  # the sign
        sd.text((740, 1385), "MIE AYAM", font=font(LORA, 58, "Bold"), fill=(255, 214, 120, 255), anchor="mm")
        sd.ellipse([590, 1520, 680, 1610], fill=(30, 16, 12, 255)); sd.ellipse([800, 1520, 890, 1610], fill=(30, 16, 12, 255))  # wheels
        sd.ellipse([615, 1545, 655, 1585], fill=(90, 60, 40, 255)); sd.ellipse([825, 1545, 865, 1585], fill=(90, 60, 40, 255))
        sd.arc([620, 1090, 760, 1190], 0, 180, fill=(40, 40, 44, 255), width=14)        # the wok on the stove
        sd.line([(600, 1130), (640, 1130)], fill=(40, 40, 44, 255), width=10)
        st.alpha_composite(shade(stools, (WW, H), (180, 30, 30), 14))
        sd = ImageDraw.Draw(st)
        sd.line([(700, 896), (700, 970)], fill=(30, 20, 20, 255), width=3)            # bulb cord
        sd.ellipse([686, 966, 714, 1000], fill=(255, 220, 150, 255))
        self.bulb = (700 + 150, 984)
        self.stall = st
        # banyan (left): trunk, buttresses, canopy, aerial roots
        bn = Image.new("RGBA", (WW, H), (0, 0, 0, 0))

        def trunk(d, s):
            d.polygon(P_((40, 1700), (360, 1700), (300, 1400), (260, 900), (250, 520), (130, 520), (110, 900), (60, 1400), s=s), fill=255)
            for x0, x1 in ((-60, 60), (330, 460)):
                d.polygon(P_((x0, 1700), (x1, 1700), (230, 1300), s=s), fill=255)
            for a, ln in ((-0.9, 520), (-0.5, 600), (-1.6, 300), (-2.3, 360)):
                d.line([(190 * s, 600 * s), ((190 + math.cos(a) * ln) * s, (600 + math.sin(a) * ln) * s)], fill=255, width=int(70 * s))

        def canopy(d, s):
            banyan_canopy(d, 330, 260, 520, 260, np.random.default_rng(5), 90, s)
        bn.alpha_composite(shade(trunk, (WW, H), (52, 30, 26), 40, rim=(255, 70, 50)))
        cn = shade(canopy, (WW, H), (26, 10, 10), 40, rim=(255, 60, 40), rim_strength=0.7)
        bn.alpha_composite(cn)
        bd = ImageDraw.Draw(bn)
        for k in range(60):                                                        # aerial roots
            x = r.uniform(-40, 760); y0 = r.uniform(300, 480); y1 = y0 + r.uniform(300, 1100)
            bd.line([(x, y0), (x + r.uniform(-12, 12), y1)], fill=(40, 22, 20, 255), width=int(r.uniform(2, 6)))
        self.banyan = bn
        self.perch = (450, 520)                                                    # a branch out in the canopy
        # foreground: blurred roots + leaves
        fg = Image.new("L", (WW, H), 0); fdd = ImageDraw.Draw(fg)
        for k in range(14):
            x = r.choice([r.uniform(-40, 140), r.uniform(WW - 160, WW)])
            fdd.line([(x, -10), (x + r.uniform(-30, 30), r.uniform(600, 1500))], fill=255, width=int(r.uniform(10, 26)))
        banyan_canopy(fdd, WW - 60, -40, 240, 160, np.random.default_rng(8), 22)
        fgl = Image.new("RGBA", fg.size, (8, 2, 3, 0)); fgl.putalpha(fg)
        self.fg = fgl.filter(ImageFilter.GaussianBlur(9))

    def frame(self, t, cam=0.0, extras=None, mid_extras=None, tree_extras=None, bulb=1.0, fogk=0.35):
        o = lambda par: int(-150 - cam * par)
        img = self.sky.copy()
        img.alpha_composite(self.far, (o(0.12), 0))
        a = to_arr(img)
        ry0, ry1 = self.river_y
        a[ry0:ry1] = self.river[:, -o(0.3):-o(0.3) + W] if -o(0.3) + W <= self.river.shape[1] else self.river[:, :W]
        for lx, ly in self.lamps:                                                 # bridge lamps + their streaks
            x = lx + o(0.12)
            if -20 < x < W + 20:
                add_glow(a, gsp(12, (255, 150, 70)), x, ly, 0.9)
                for j in range(5):
                    a[ry0 + 6 + j * 14: ry0 + 12 + j * 14, max(0, int(x - 3)):int(x + 3)] += np.array([90, 40, 20], np.float32) * (1 - j / 5)
        mx = 800 + o(0.0) + 150                                                     # the moon road
        for j in range(26):
            y = ry0 + 10 + j * 13
            wd = 30 + j * 9 + 18 * math.sin(t * 2 + j)
            x0 = int(mx - wd / 2 + 10 * math.sin(t * 1.3 + j * 0.7)); x1 = int(mx + wd / 2)
            a[y:y + 4, max(0, x0):max(0, min(W, x1))] = np.array([200, 56, 40], np.float32) * (1 - j / 30)
        img = to_img(a)
        fog(img, t, fogk, 900, 1150, speed=10, col=(150, 40, 36))
        bob = 6 * math.sin(t * 1.4)
        img.alpha_composite(self.boat, (o(0.4), int(bob)))
        for fn in (mid_extras or []):
            img = fn(img, t, o(0.4) + 150) or img
        img.alpha_composite(self.near_floor, (o(1.0), 0))
        img.alpha_composite(self.banyan, (o(1.0), 0))
        for fn in (tree_extras or []):
            img = fn(img, t, o(1.0) + 150) or img
        img.alpha_composite(self.stall, (o(1.0), 0))
        a = to_arr(img)
        bx, by = self.bulb
        fl = bulb * (0.88 + 0.12 * (math.sin(t * 23) > -0.85))
        add_glow(a, gsp(360, (255, 140, 70)), bx + o(1.0), by + 200, 0.42 * fl)
        add_glow(a, gsp(30, (255, 230, 180)), bx + o(1.0), by, 1.0 * fl)
        img = to_img(a)
        for fn in (extras or []):
            img = fn(img, t, o(1.0) + 150) or img
        fog(img, t, fogk * 0.5, 1350, 1750, speed=16, col=(130, 34, 30), off=300)
        img.alpha_composite(self.fg, (o(1.5), 0))
        bokeh_particles(img, 12, 161, t, color=(255, 150, 100), size=(2, 6), blur=(0, 3), area=(0, 300, W, 1600), drift=(5, -4))
        return img


_RF = None


def riverfront():
    global _RF
    if _RF is None:
        _RF = Riverfront()
    return _RF


class Boardwalk:
    """The old kampung boardwalk on stilts over the water, in one-point perspective: a plank walk running away from us,
    wooden houses with zinc roofs on both sides (dark windows, one lit), a lone streetlamp, black water with the red
    moon's glints under the walk, and at the far end the giant banyan with the red moon behind it.
    Ground placement: self.at(z) -> (y_feet, scale for a 1.6 m person)."""
    def __init__(self, flip=False):
        r = np.random.default_rng(162 + int(flip))
        self.P = P = Persp(540, 860, 900)
        a = vgrad((4, 1, 2), (52, 7, 13), (110, 20, 22), 0.44)
        yy, xx = np.mgrid[0:H, 0:W]
        mx, my, mr = 560, 560, 120
        dd = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
        a += np.exp(-dd / (mr * 3.2))[..., None] * np.array([150, 26, 20], np.float32) * 0.9
        disc = np.clip((mr - dd) / 2.5, 0, 1)[..., None]
        a = a * (1 - disc) + np.array([232, 72, 50], np.float32) * disc
        img = to_img(a); d = ImageDraw.Draw(img)
        # far banyan silhouette over the moon
        cm = Image.new("L", (W, H), 0); cd = ImageDraw.Draw(cm)
        banyan_canopy(cd, 540, 640, 330, 150, np.random.default_rng(3), 70)
        cd.polygon([(500, 860), (580, 860), (566, 700), (514, 700)], fill=255)
        for k in range(30):
            x = r.uniform(250, 830); cd.line([(x, 640), (x, 640 + r.uniform(60, 220))], fill=255, width=2)
        cl = Image.new("RGBA", (W, H), (22, 4, 7, 0)); cl.putalpha(cm)
        img.alpha_composite(cl)
        self.tree_top = (540, 640)
        # water
        d = ImageDraw.Draw(img)
        d.rectangle([0, 860, W, H], fill=(12, 2, 4, 255))
        # houses on both sides
        houses = []
        z = 2.0
        while z < 34:
            dz = r.uniform(2.4, 4.0)
            houses.append((z, z + dz * 0.9)); z += dz
        self.lit = []
        for side in (-1, 1):
            for i, (z0, z1) in enumerate(houses):
                s0 = side * 1.55
                fog_k = min(1, (z0 - 2) / 30)
                base = np.array(r.choice([(96, 52, 36), (80, 44, 32), (110, 60, 40)]), np.float32)
                col = tuple(int(c) for c in base * (1 - 0.75 * fog_k) + np.array([40, 8, 10]) * 0.75 * fog_k)
                top = -1.7 - r.uniform(0, 0.4)
                q = [P.p(s0, 1.6, z0), P.p(s0, top, z0), P.p(s0, top, z1), P.p(s0, 1.6, z1)]
                d.polygon(q, fill=col + (255,))
                for k in range(1, 6):                                            # horizontal siding
                    hh = 1.6 + (top - 1.6) * k / 6
                    d.line([P.p(s0, hh, z0), P.p(s0, hh, z1)], fill=tuple(int(c * 0.7) for c in col) + (255,), width=max(1, int(4 / z0 * 3)))
                # zinc roof edge
                rc = tuple(int(c) for c in np.array([70, 60, 62]) * (1 - 0.7 * fog_k) + np.array([40, 8, 10]) * 0.7 * fog_k)
                d.polygon([P.p(s0, top, z0 - 0.1), P.p(s0 - side * 0.6, top - 0.5, z0 - 0.1), P.p(s0 - side * 0.6, top - 0.5, z1 + 0.1), P.p(s0, top, z1 + 0.1)], fill=rc + (255,))
                # window + door
                wz0, wz1 = z0 + (z1 - z0) * 0.15, z0 + (z1 - z0) * 0.45
                lit = (side == 1 and i == 2) or (side == -1 and i == 4)
                wcol = (255, 150, 70) if lit else tuple(int(c * 0.25) for c in col)
                wq = [P.p(s0, -0.1, wz0), P.p(s0, -1.0, wz0), P.p(s0, -1.0, wz1), P.p(s0, -0.1, wz1)]
                d.polygon(wq, fill=wcol + (255,))
                if lit:
                    self.lit.append(tuple(np.mean(wq, 0)))
                dz0, dz1 = z0 + (z1 - z0) * 0.6, z0 + (z1 - z0) * 0.85
                d.polygon([P.p(s0, 1.6, dz0), P.p(s0, -0.6, dz0), P.p(s0, -0.6, dz1), P.p(s0, 1.6, dz1)], fill=tuple(int(c * 0.4) for c in col) + (255,))
                # stilts into the water
                for zz in (z0, z1):
                    x, y = P.p(s0, 1.6, zz); x2, y2 = P.p(s0, 2.8, zz)
                    d.line([(x, y), (x2, y2)], fill=(40, 20, 16, 255), width=max(2, int(36 / zz)))
        # the walk
        d.polygon([P.p(-1.1, 1.6, 0.8), P.p(1.1, 1.6, 0.8), P.p(1.1, 1.6, 40), P.p(-1.1, 1.6, 40)], fill=(78, 44, 30, 255))
        zz = 0.8
        while zz < 40:
            d.line([P.p(-1.1, 1.6, zz), P.p(1.1, 1.6, zz)], fill=(30, 14, 10, 255), width=max(1, int(8 / zz)))
            zz += 0.35
        for sg in (-1, 1):
            d.line([P.p(sg * 1.1, 1.6, 0.8), P.p(sg * 1.1, 1.6, 40)], fill=(40, 20, 14, 255), width=6)
            d.polygon([P.p(sg * 1.1, 1.6, 0.8), P.p(sg * 1.1, 1.75, 0.8), P.p(sg * 1.1, 1.75, 40), P.p(sg * 1.1, 1.6, 40)], fill=(44, 22, 16, 255))
        # streetlamp
        lz = 9.0
        x0, y0 = P.p(1.25, 1.6, lz); x1, y1 = P.p(1.25, -2.6, lz)
        d.line([(x0, y0), (x1, y1)], fill=(30, 26, 26, 255), width=8)
        x2, y2 = P.p(0.8, -2.6, lz)
        d.line([(x1, y1), (x2, y2)], fill=(30, 26, 26, 255), width=6)
        self.lamp = (x2, y2 + 10)
        d.ellipse([x2 - 10, y2, x2 + 10, y2 + 20], fill=(255, 210, 150, 255))
        if flip:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            self.lamp = (W - self.lamp[0], self.lamp[1])
            self.lit = [(W - x, y) for x, y in self.lit]
        base = to_arr(img)
        lm = light_map(W, H, self.lamp[0], self.lamp[1] + 300, 520, 0.0)[..., None] * np.array([1.0, 0.6, 0.4], np.float32)
        self.base = base * (0.62 + 0.55 * lm)
        self.glints = [(r.uniform(0, W), r.uniform(880, H), r.uniform(20, 90)) for _ in range(70)]
        self.petals = Petals(26, seed=7, sizes=(12, 16, 22), area=(80, W - 80, -50, H))

    def at(self, z, side=0.0):
        x, y = self.P.p(side, 1.6, z)
        return x, y, (1.6 * 900 / z) / 860

    def frame(self, t, extras=None, petals=0.0, lamp=1.0, fogk=0.35, glow_lit=1.0):
        a = self.base.copy()
        for gx, gy, wd in self.glints:                                       # moonlight glints on the water
            k = 0.5 + 0.5 * math.sin(t * 2.2 + gx * 0.05)
            x0 = int(gx + 12 * math.sin(t + gy)); y0 = int(gy)
            if y0 < H - 3:
                a[y0:y0 + 3, max(0, x0):max(0, min(W, x0 + int(wd * (gy - 860) / 1000)))] += np.array([110, 30, 24], np.float32) * k
        fl = lamp * (0.85 + 0.15 * (math.sin(t * 17) > -0.8))
        add_glow(a, gsp(220, (255, 140, 80)), self.lamp[0], self.lamp[1], 0.5 * fl)
        add_glow(a, gsp(20, (255, 230, 190)), self.lamp[0], self.lamp[1], 1.0 * fl)
        for lx, ly in self.lit:
            add_glow(a, gsp(60, (255, 130, 60)), lx, ly, 0.4 * glow_lit)
        img = to_img(a)
        fog(img, t, fogk, 700, 950, speed=12, col=(150, 40, 36))
        for fn in (extras or []):
            img = fn(img, t) or img
        if petals > 0:
            self.petals.draw(img, t, petals, wind=6)
        fog(img, t, fogk * 0.5, 1450, 1900, speed=18, col=(120, 30, 28), off=250)
        bokeh_particles(img, 10, 162, t, color=(255, 150, 100), size=(2, 5), blur=(0, 2), area=(0, 300, W, 1600), drift=(4, -5))
        return img


_BW = {}


def boardwalk(flip=False):
    if flip not in _BW:
        _BW[flip] = Boardwalk(flip)
    return _BW[flip]


class BanyanUp:
    """Looking straight up the giant banyan: the trunk rising from the bottom, huge branches spreading to the edges,
    dark leaf clouds with gaps of red sky, curtains of aerial roots hanging toward us, the red moon through a gap with
    god rays. self.perch: the branch where she crouches."""
    def __init__(self):
        r = np.random.default_rng(163)
        sky = moon_sky((760, 420), 110, top=(60, 8, 14), mid=(110, 18, 22), bot=(60, 8, 12), ym=0.4)
        img = to_img(sky)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def wood(d, s):
            d.polygon(P_((240, H + 20), (860, H + 20), (680, 1100), (600, 760), (480, 760), (420, 1100), s=s), fill=255)
            for (x0, y0, x1, y1, wd) in ((540, 900, -80, 380, 110), (560, 860, 1160, 300, 120), (540, 820, 380, -60, 80),
                                         (560, 820, 820, -60, 90), (520, 980, -80, 1100, 70), (580, 1000, 1160, 1180, 70)):
                d.line([(x0 * s, y0 * s), ((x0 + x1) / 2 * s, ((y0 + y1) / 2 - 40) * s), (x1 * s, y1 * s)], fill=255, width=int(wd * s), joint="curve")

        def leaves(d, s):
            rr = np.random.default_rng(4)
            for (cx, cy, rx, ry, n) in ((80, 260, 300, 260, 50), (1000, 200, 300, 240, 50), (540, 40, 420, 160, 40),
                                        (60, 1000, 200, 200, 20), (1040, 1100, 200, 200, 20)):
                banyan_canopy(d, cx, cy, rx, ry, rr, n, s)
        lay.alpha_composite(shade(leaves, (W, H), (24, 8, 9), 50, rim=(255, 60, 40), rim_strength=0.7))
        lay.alpha_composite(shade(wood, (W, H), (58, 32, 28), 60, rim=(255, 70, 50)))
        d = ImageDraw.Draw(lay)
        for k in range(120):                                                    # bark lines
            x = r.uniform(300, 800); y = r.uniform(800, H)
            d.line([(x, y), (x + r.uniform(-10, 10), y + r.uniform(40, 160))], fill=(30, 16, 14, 255), width=3)
        for k in range(50):                                                     # aerial roots hanging toward us
            x = r.uniform(0, W); y = r.uniform(100, 700)
            d.line([(x, y), (x + (x - 540) * r.uniform(0.05, 0.25), y + r.uniform(150, 600))], fill=(36, 20, 18, 255), width=int(r.uniform(2, 7)))
        img.alpha_composite(lay)
        occ = np.asarray(lay.split()[3], np.float32) / 255
        a = to_arr(img)
        a = god_rays(a, (760, 420), occ, color=(255, 70, 50), strength=0.5)
        self.base = a
        self.perch = (330, 560)

    def frame(self, t, extras=None, petals=None):
        img = to_img(self.base.copy())
        for fn in (extras or []):
            img = fn(img, t) or img
        fog(img, t, 0.25, 0, 500, speed=8, col=(150, 40, 36))
        bokeh_particles(img, 14, 163, t, color=(255, 240, 230), size=(3, 8), blur=(0, 3), area=(0, 0, W, 1500), drift=(5, 30))
        return img


_BU = None


def banyan_up():
    global _BU
    if _BU is None:
        _BU = BanyanUp()
    return _BU


class UnderHouse:
    """Under a house on stilts: the floor planks overhead running away from us, with red light leaking through the
    gaps, rows of dark wooden posts receding into the dark, black mud and puddles of water below with red reflections.
    A wider gap in the floor near us (self.gap) where things can come down."""
    def __init__(self):
        r = np.random.default_rng(164)
        P = self.P = Persp(540, 900, 820)
        a = np.zeros((H, W, 3), np.float32) + np.array([8, 2, 3], np.float32)
        img = to_img(a); d = ImageDraw.Draw(img)
        # far: the boardwalk / water beyond, a little red glow
        d.rectangle([0, 860, W, 960], fill=(60, 12, 14, 255))
        # ceiling planks (hgt -1.0) running in depth, gaps glowing red
        for k in range(-18, 19):
            s0 = k * 0.28
            q = [P.p(s0, -1.0, 0.6), P.p(s0 + 0.26, -1.0, 0.6), P.p(s0 + 0.26, -1.0, 30), P.p(s0, -1.0, 30)]
            c = 40 + 10 * r.random()
            d.polygon(q, fill=(int(c * 1.3), int(c * 0.7), int(c * 0.55), 255))
        self.gap = (P.p(-0.08, -1.0, 1.4), P.p(0.6, -1.0, 2.6))
        # floor joists across
        for z in (1.2, 2.0, 3.0, 4.5, 6.5, 9.5, 14):
            d.polygon([P.p(-6, -1.0, z), P.p(6, -1.0, z), P.p(6, -0.85, z), P.p(-6, -0.85, z)], fill=(26, 12, 10, 255))
        # ground (hgt 0.9): mud + puddles
        d.polygon([P.p(-8, 0.9, 0.5), P.p(8, 0.9, 0.5), P.p(8, 0.9, 30), P.p(-8, 0.9, 30)], fill=(26, 10, 9, 255))
        for _ in range(16):
            z = r.uniform(1.0, 12); s0 = r.uniform(-3, 3)
            x, y = P.p(s0, 0.9, z); rw = r.uniform(0.4, 1.2) * 820 / z; rh = rw * 0.18
            d.ellipse([x - rw, y - rh, x + rw, y + rh], fill=(50, 10, 12, 255))
            d.line([(x - rw * 0.6, y), (x + rw * 0.3, y)], fill=(170, 40, 34, 255), width=2)
        for _ in range(300):
            x = r.uniform(0, W); y = r.uniform(960, H)
            d.ellipse([x - 5, y - 2, x + 5, y + 2], fill=(18, 6, 6, 255))
        # posts
        self.posts = []
        for z in (1.8, 3.4, 5.6, 8.6, 13):
            for s0 in (-2.6, -1.2, 1.6, 3.0):
                x0, y0 = P.p(s0, -1.0, z); x1, y1 = P.p(s0, 0.95, z)
                wpx = 0.18 * 820 / z
                c = max(0.25, 1 - z / 16)
                d.rectangle([x0 - wpx / 2, y0, x0 + wpx / 2, y1], fill=(int(70 * c), int(38 * c), int(28 * c), 255))
                d.line([(x0 + wpx * 0.3, y0), (x0 + wpx * 0.3, y1)], fill=(int(200 * c), int(50 * c), int(36 * c), 255), width=max(1, int(wpx * 0.12)))
        base = to_arr(img)
        # light leaking through the plank gaps: thin red lines on the ceiling + dusty shafts down
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        shafts = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shafts)
        for k in range(-18, 19):
            s0 = k * 0.28 + 0.26
            if r.random() < 0.55:
                ld.line([P.p(s0, -1.0, 0.7), P.p(s0, -1.0, 12)], fill=(255, 60, 40, 220), width=3)
                if abs(k) < 9 and r.random() < 0.5:
                    z = r.uniform(1.5, 6)
                    x0, y0 = P.p(s0, -1.0, z); x1, y1 = P.p(s0, 0.9, z + 1.2)
                    sd.polygon([(x0 - 3, y0), (x0 + 3, y0), (x1 + 30, y1), (x1 - 30, y1)], fill=(255, 50, 36, 34))
        self.lines = lay
        self.shafts = shafts.filter(ImageFilter.GaussianBlur(8))
        self.base = base

    def frame(self, t, extras=None, back=None, gap_light=1.0, fogk=0.3):
        img = to_img(self.base)
        for fn in (back or []):
            img = fn(img, t) or img
        fl = 0.8 + 0.2 * math.sin(t * 9) * math.sin(t * 3.1)
        img.alpha_composite(with_alpha(self.lines, 0.7 + 0.3 * fl))
        img.alpha_composite(with_alpha(self.shafts, fl))
        (gx0, gy0), (gx1, gy1) = self.gap
        a = to_arr(img)
        add_glow(a, gsp(160, (255, 50, 36)), (gx0 + gx1) / 2, (gy0 + gy1) / 2, 0.35 * gap_light)
        img = to_img(a)
        for fn in (extras or []):
            img = fn(img, t) or img
        fog(img, t, fogk, 1100, 1700, speed=10, col=(110, 26, 24))
        bokeh_particles(img, 16, 164, t, color=(255, 120, 90), size=(2, 5), blur=(0, 2), area=(0, 200, W, 1700), drift=(3, 8))
        return img


_UH = None


def under_house():
    global _UH
    if _UH is None:
        _UH = UnderHouse()
    return _UH


def kentongan(scale=1.0):
    """A kentongan: a hollow log slit drum hanging from a rope, the night-watch alarm of an Indonesian kampung."""
    w, h = 140, 420
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def log(d, s):
        d.rounded_rectangle([20 * s, 80 * s, 120 * s, 400 * s], int(40 * s), fill=255)
    im.alpha_composite(shade(log, (w, h), (120, 70, 40), 30))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 140, 80, 350], 8, fill=(20, 8, 6, 255))                     # the slit
    for y in (110, 380):
        d.line([(26, y), (114, y)], fill=(70, 40, 24, 255), width=6)
    d.line([(70, 0), (70, 84)], fill=(160, 140, 110, 255), width=6)                     # rope
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


class Ronda:
    """Side view along the kampung: the pos ronda (night-watch hut: four posts, a zinc roof, a bench, a bare bulb, the
    kentongan hanging from the beam) on the left, a row of stilt houses behind with windows that light up one by one,
    the boardwalk across the bottom over black water, and the banyan towering on the right under the red moon.
    Anchors: self.walk_y, self.kent (kentongan centre), self.perch (branch)."""
    def __init__(self):
        r = np.random.default_rng(165)
        WW = W + 1300
        self.sky = to_img(moon_sky((860, 300), 110, top=(4, 1, 2), mid=(50, 7, 13), bot=(120, 22, 24), ym=0.5))
        hs = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
        self.windows = []
        x = 300
        while x < WW:
            bw = r.uniform(260, 340)
            top = r.uniform(820, 900)

            def house(d, s, x=x, bw=bw, top=top):
                d.rectangle([x * s, top * s, (x + bw) * s, 1420 * s], fill=255)
            col = tuple(int(c) for c in r.choice([(84, 46, 34), (96, 52, 38), (74, 40, 30)]))
            hs.alpha_composite(shade(house, (WW, H), col, 24))
            d = ImageDraw.Draw(hs)
            d.polygon([(x - 30, top + 10), (x + bw / 2, top - 120), (x + bw + 30, top + 10)], fill=(66, 58, 60, 255))
            d.line([(x - 30, top + 10), (x + bw / 2, top - 120), (x + bw + 30, top + 10)], fill=(200, 60, 44, 255), width=3)
            for k in range(1, 10):
                d.line([(x, top + k * (1420 - top) / 10), (x + bw, top + k * (1420 - top) / 10)], fill=tuple(int(c * .7) for c in col) + (255,), width=3)
            for j in range(2):
                wx = x + 40 + j * (bw - 140)
                self.windows.append((wx, top + 110, wx + 90, top + 240))
            d.rectangle([x + bw / 2 - 40, top + 260, x + bw / 2 + 40, 1420], fill=tuple(int(c * .35) for c in col) + (255,))
            self.windows.append((x + bw / 2 - 40, top + 260, x + bw / 2 + 40, 1420))     # the door
            for sx in (x + 10, x + bw - 10):
                d.rectangle([sx - 8, 1420, sx + 8, 1600], fill=(40, 20, 16, 255))
            x += bw + r.uniform(30, 70)
        self.houses = hs
        bn = Image.new("RGBA", (WW, H), (0, 0, 0, 0))

        def trunk(d, s):
            d.polygon(P_((1050, 1500), (1300, 1500), (1260, 900), (1240, 600), (1120, 600), (1090, 900), s=s), fill=255)
            d.line([(1180 * s, 700 * s), (880 * s, 520 * s), (700 * s, 480 * s)], fill=255, width=int(60 * s), joint="curve")

        def canopy(d, s):
            banyan_canopy(d, 1100, 380, 520, 260, np.random.default_rng(9), 90, s)
        bn.alpha_composite(shade(canopy, (WW, H), (26, 10, 10), 40, rim=(255, 60, 40), rim_strength=0.7))
        bn.alpha_composite(shade(trunk, (WW, H), (52, 30, 26), 40))
        bd = ImageDraw.Draw(bn)
        for k in range(50):
            x = r.uniform(600, WW); y0 = r.uniform(400, 560)
            bd.line([(x, y0), (x + r.uniform(-10, 10), y0 + r.uniform(200, 800))], fill=(40, 22, 20, 255), width=int(r.uniform(2, 6)))
        self.banyan = bn
        self.perch = (820, 760)
        nl = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); nd = ImageDraw.Draw(nl)
        nd.rectangle([0, 1600, WW, H], fill=(10, 2, 4, 255))
        nd.rectangle([0, 1480, WW, 1540], fill=(78, 44, 30, 255))                         # the walk (side)
        for k in range(0, WW, 46):
            nd.line([(k, 1480), (k, 1540)], fill=(36, 18, 12, 255), width=3)
        for k in range(0, WW, 180):
            nd.rectangle([k, 1540, k + 16, 1700], fill=(40, 20, 16, 255))
        self.walk_y = 1490
        # pos ronda hut (left)
        hut = Image.new("RGBA", (WW, H), (0, 0, 0, 0))

        def hposts(d, s):
            for x in (120, 520):
                d.rectangle([(x - 12) * s, 980 * s, (x + 12) * s, 1490 * s], fill=255)
            d.rectangle([150 * s, 1300 * s, 490 * s, 1330 * s], fill=255)                  # bench
            for x in (180, 460):
                d.rectangle([(x - 8) * s, 1330 * s, (x + 8) * s, 1480 * s], fill=255)

        def hroof(d, s):
            d.polygon(P_((60, 1000), (600, 960), (600, 990), (60, 1030), s=s), fill=255)
        hut.alpha_composite(shade(hposts, (WW, H), (90, 54, 36), 10))
        hut.alpha_composite(shade(hroof, (WW, H), (90, 84, 86), 10, rim=(255, 90, 60)))
        hd = ImageDraw.Draw(hut)
        hd.rectangle([110, 1052, 330, 1104], fill=(40, 24, 18, 255), outline=(230, 210, 170, 255), width=3)
        hd.text((220, 1078), "POS RONDA", font=font(INTER_SB, 30), fill=(230, 210, 170, 255), anchor="mm")
        hd.line([(250, 1104), (250, 1140)], fill=(30, 20, 20, 255), width=3)
        self.hbulb = (250, 1150)
        kt = kentongan(1.0)
        hut.alpha_composite(kt, (420 - kt.width // 2, 1000))
        self.kent = (420, 1000 + 270)
        self.hut = hut
        self.near = nl

    def frame(self, t, cam=0.0, extras=None, tree_extras=None, lights=0.0, bulb=1.0, kshake=0.0):
        o = lambda par: int(-150 - cam * par)
        img = self.sky.copy()
        img.alpha_composite(self.banyan, (o(0.5), 0))
        for fn in (tree_extras or []):
            img = fn(img, t, o(0.5) + 150) or img
        fog(img, t, 0.3, 1100, 1450, speed=10, col=(150, 40, 36))
        hs = self.houses.copy()
        d = ImageDraw.Draw(hs)
        n = len(self.windows)
        order = sorted(range(n), key=lambda i: (i * 7) % n)
        for j, i in enumerate(order):
            x0, y0, x1, y1 = self.windows[i]
            k = np.clip(lights * n - j, 0, 1)
            col = tuple(int(c) for c in np.array([20, 6, 6]) * (1 - k) + np.array([255, 170, 90]) * k)
            d.rectangle([x0, y0, x1, y1], fill=col + (255,))
            d.rectangle([x0, y0, x1, y1], outline=(30, 14, 10, 255), width=6)
        img.alpha_composite(hs, (o(0.8), 0))
        if lights > 0:
            a = to_arr(img)
            for j, i in enumerate(order):
                k = np.clip(lights * n - j, 0, 1)
                if k > 0:
                    x0, y0, x1, y1 = self.windows[i]
                    add_glow(a, gsp(110, (255, 140, 70)), (x0 + x1) / 2 + o(0.8), (y0 + y1) / 2, 0.45 * k)
            img = to_img(a)
        img.alpha_composite(self.near, (o(1.0), 0))
        hut = self.hut
        img.alpha_composite(hut, (o(1.0), 0))
        if kshake:
            pass
        a = to_arr(img)
        bx, by = self.hbulb
        fl = bulb * (0.85 + 0.15 * (math.sin(t * 19) > -0.7))
        add_glow(a, gsp(260, (255, 150, 80)), bx + o(1.0) + 150, by + 120, 0.5 * fl)
        add_glow(a, gsp(18, (255, 230, 190)), bx + o(1.0) + 150, by, 1.0 * fl)
        img = to_img(a)
        for fn in (extras or []):
            img = fn(img, t, o(1.0) + 150) or img
        fog(img, t, 0.2, 1500, 1900, speed=16, col=(120, 30, 28), off=200)
        bokeh_particles(img, 10, 165, t, color=(255, 150, 100), size=(2, 6), blur=(0, 3), area=(0, 300, W, 1600), drift=(5, -4))
        return img


_RD = None


def ronda():
    global _RD
    if _RD is None:
        _RD = Ronda()
    return _RD


class Bedroom:
    """Putri's small room in Grandma's wooden house: vertical plank walls, a window with a red batik curtain and red
    moonlight, a plank door with a bolt (left), a low bed with a batik blanket and a white pillow, a small bedside lamp.
    self.pillow: where the flower lies."""
    def __init__(self):
        r = np.random.default_rng(166)
        a = np.zeros((H, W, 3), np.float32)
        for k in range(0, W, 72):                                                   # plank wall
            c = np.array([92, 52, 36], np.float32) * r.uniform(0.85, 1.05)
            a[:1380, k:k + 70] = c
            a[:1380, k + 68:k + 72] = np.array([40, 20, 14], np.float32)
        a[1380:] = np.array([70, 40, 28], np.float32)
        for k in range(10):
            y = 1380 + k * k * 6
            a[y:y + 3] = np.array([40, 20, 14], np.float32)
        img = to_img(a); d = ImageDraw.Draw(img)
        # window (right) with moon + curtain
        wx0, wy0, wx1, wy1 = 640, 420, 980, 900
        sky = to_img(moon_sky((860, 120), 60, w=wx1 - wx0, h=wy1 - wy0, top=(20, 2, 6), mid=(80, 10, 16), bot=(140, 28, 26)))
        sd = ImageDraw.Draw(sky)
        banyan_canopy(sd, 80, 380, 200, 140, np.random.default_rng(2), 25)
        img.alpha_composite(sky.convert("RGBA"), (wx0, wy0))
        d.rectangle([wx0 - 22, wy0 - 22, wx1 + 22, wy1 + 22], outline=(50, 26, 18, 255), width=22)
        d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(50, 26, 18, 255), width=10)
        self.win = (wx0, wy0, wx1, wy1)

        def curtain(d_, s):
            d_.polygon(P_((wx0 - 40, wy0 - 40), (wx0 + 110, wy0 - 40), (wx0 + 60, wy1 + 60), (wx0 - 50, wy1 + 60), s=s), fill=255)
        cu = shade(curtain, (W, H), BATIK, 20)
        cd = ImageDraw.Draw(cu)
        for k in range(14):
            y = wy0 + k * 38
            cd.ellipse([wx0 - 10, y, wx0 + 30, y + 26], outline=(220, 170, 90, 255), width=3)
            cd.ellipse([wx0 + 40, y + 16, wx0 + 70, y + 40], outline=(220, 170, 90, 255), width=3)
        img.alpha_composite(cu)
        # door (left)
        d.rectangle([90, 560, 380, 1380], fill=(70, 38, 26, 255))
        d.rectangle([90, 560, 380, 1380], outline=(40, 20, 14, 255), width=14)
        d.rectangle([330, 920, 380, 950], fill=(150, 140, 120, 255))                       # the bolt
        self.bolt = (355, 935)
        # bed

        def bed(d_, s):
            d_.rectangle([380 * s, 1440 * s, W * s, 1600 * s], fill=255)

        def mattress(d_, s):
            d_.rounded_rectangle([400 * s, 1360 * s, (W + 40) * s, 1470 * s], int(30 * s), fill=255)

        def pillow(d_, s):
            d_.rounded_rectangle([440 * s, 1290 * s, 700 * s, 1390 * s], int(40 * s), fill=255)
        img.alpha_composite(shade(bed, (W, H), (80, 44, 30), 14))
        mt = shade(mattress, (W, H), BATIK, 24)
        md = ImageDraw.Draw(mt)
        for k in range(16):
            x = 420 + k * 44
            md.ellipse([x, 1390, x + 30, 1420], outline=(230, 180, 90, 255), width=3)
        img.alpha_composite(mt)
        img.alpha_composite(shade(pillow, (W, H), (220, 214, 204), 30))
        self.pillow = (570, 1320)
        # bedside lamp
        d = ImageDraw.Draw(img)
        d.polygon([(200, 1240), (300, 1240), (280, 1170), (220, 1170)], fill=(200, 140, 80, 255))
        d.rectangle([244, 1240, 256, 1330], fill=(60, 40, 30, 255)); d.rectangle([200, 1330, 300, 1350], fill=(60, 40, 30, 255))
        self.lamp = (250, 1210)
        self.alb = to_arr(img)
        self.lm = light_map(W, H, 250, 1210, 700, 0.0)[..., None] * np.array([1.2, 0.8, 0.55], np.float32)
        poly = Image.new("L", (W, H), 0)
        ImageDraw.Draw(poly).polygon([(wx0, 1380), (wx1, 1380), (wx1 + 200, H), (wx0 - 100, H)], fill=255)
        self.moonm = (np.asarray(poly.filter(ImageFilter.GaussianBlur(30)), np.float32) / 255)[..., None] * np.array([0.9, 0.25, 0.2], np.float32)

    def frame(self, t, lamp=1.0, extras=None, back=None):
        fl = lamp * (0.9 + 0.1 * math.sin(t * 7))
        light = np.array([0.22, 0.08, 0.09], np.float32) + fl * self.lm + self.moonm * 0.6
        a = self.alb * light
        wx0, wy0, wx1, wy1 = self.win
        a[wy0:wy1, wx0 + 40:wx1] = self.alb[wy0:wy1, wx0 + 40:wx1]                  # the window stays bright
        img = to_img(a)
        for fn in (back or []):
            img = fn(img, t) or img
        for fn in (extras or []):
            img = fn(img, t) or img
        a = to_arr(img)
        add_glow(a, gsp(200, (255, 150, 80)), self.lamp[0], self.lamp[1], 0.45 * fl)
        img = to_img(a)
        bokeh_particles(img, 8, 166, t, color=(255, 160, 110), size=(2, 4), blur=(0, 2), area=(0, 300, W, 1500), drift=(3, -4))
        return img


_BR = None


def bedroom():
    global _BR
    if _BR is None:
        _BR = Bedroom()
    return _BR
