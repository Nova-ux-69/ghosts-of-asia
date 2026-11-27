"""Ep17 Thailand / Mae Nak of Phra Khanong - art: the world, the characters and the ghost (2.1D flat21 style).
New world: the Phra Khanong canal in old Siam on a plum-black night (a pale red moon, teak houses on stilts with steep
gables and curled ngao finials, coconut palms, lotus pads and water hyacinth, Wat Mahabut's chedi and lantern-lit roofs
far down the canal), Nak and Mak's teak house seen as a cutaway (lamp-lit porch with a clay mortar on top, posts, big
glazed water jars and a ladder in the dark underneath), a POV from inside a bush of nat (Blumea) leaves, the temple gate
of Wat Mahabut seen from the inside (white wall, tiered gate roof with chofa horns, sema boundary stones) at night and at
dawn, and Mae Nak's shrine today (rows of offered Thai dresses, a Bo tree wrapped in coloured cloth, toys, incense).
Hero: Mak (indigo shirt, red-checked pha khao ma at the waist, brown knee trousers). Ghost: Mae Nak - crimson sabai with
a gold edge over one shoulder, dark green pha sin, very long black hair, a baby bundle; her arm stretches impossibly
long. No gore."""
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



SKIN = (158, 108, 76)          # Mak
SHIRT = (44, 52, 84)           # indigo shirt
CHECK = (150, 36, 36)          # pha khao ma (red check)
TROU = (104, 70, 44)           # knee trousers
HAIR = (12, 10, 12)
NSKIN = (212, 186, 166)        # Nak (alive-looking)
GSKIN = (214, 210, 206)        # Nak (ghost)
SABAI = (150, 22, 34)
GOLD_ = (214, 170, 80)
SIN = (30, 60, 50)
CLOTH = (222, 214, 200)        # baby's cloth
LIME = (120, 190, 60)

# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """Thailand (Thong Trairong): red, white, double-width blue, white, red - 3:2."""
    global _FLAG
    if _FLAG is None:
        w, h = 300, 200
        im = Image.new("RGBA", (w, h), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
        u = h / 6
        d.rectangle([0, 0, w, u], fill=(165, 25, 49, 255)); d.rectangle([0, 5 * u, w, h], fill=(165, 25, 49, 255))
        d.rectangle([0, 2 * u, w, 4 * u], fill=(45, 42, 74, 255))
        _FLAG = im
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


def night_ui(clock, temple, t, k=1.0, danger=False):
    """The ticking clock: the night running out (time now / dawn 5:52) + the distance to the temple."""
    f1 = font(INTER_SB, 40); f2 = font(INTER_M, 24); f3 = font(INTER_SB, 36)
    w, h = 720, 112
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    blink = (math.sin(t * 10) > -0.2) if danger else True
    oc = (255, 50, 40) if danger else (230, 190, 120)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 32, fill=(0, 0, 0, int(190 * k)), outline=oc + (int(220 * k),), width=3)
    cx, cy = 56, 56                                                   # clock face
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=(250, 236, 210, int(255 * k)), width=4)
    hh, mm = [int(v) for v in clock.split(":")]
    for ang, ln, wd in (((hh % 12 + mm / 60) / 12, 14, 5), (mm / 60, 22, 3)):
        a = ang * 2 * math.pi - math.pi / 2
        d.line([(cx, cy), (cx + math.cos(a) * ln, cy + math.sin(a) * ln)], fill=(250, 236, 210, int(255 * k)), width=wd)
    d.text((104, 32), "NIGHT", font=f2, fill=(230, 190, 140, int(255 * k)), anchor="lm")
    if blink:
        d.text((104, 76), clock, font=f1, fill=((255, 70, 55) if danger else (248, 240, 228)) + (int(255 * k),), anchor="lm")
    d.text((300, 32), "DAWN", font=f2, fill=(230, 190, 140, int(255 * k)), anchor="lm")
    d.text((300, 76), "5:52", font=f3, fill=(200, 190, 180, int(255 * k)), anchor="lm")
    d.line([(420, 22), (420, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    hx, hy = 470, 60                                                  # a little chedi icon
    col = (255, 214, 150, int(255 * k))
    d.polygon([(hx, hy - 36), (hx - 6, hy - 14), (hx + 6, hy - 14)], fill=col)
    d.pieslice([hx - 22, hy - 22, hx + 22, hy + 18], 180, 360, fill=col)
    d.rectangle([hx - 26, hy - 2, hx + 26, hy + 8], fill=col); d.rectangle([hx - 32, hy + 8, hx + 32, hy + 18], fill=col)
    d.text((610, 36), "TEMPLE", font=f2, fill=(230, 190, 140, int(255 * k)), anchor="mm")
    d.text((610, 76), temple, font=f3, fill=(255, 240, 228, int(255 * k)), anchor="mm")
    return im


def put_ui(out, clock, temple, t, k=1.0, y=200, danger=False):
    if k <= 0.01:
        return
    ui = night_ui(clock, temple, t, k, danger)
    out.alpha_composite(ui, (int(W / 2 - ui.width / 2), int(y)))


def clock_at(m0, m1, u):
    """minutes after midnight, interpolated -> 'h:mm'."""
    m = int(m0 + (m1 - m0) * max(0.0, min(1.0, u)))
    return f"{m // 60}:{m % 60:02d}"


# ============================================================ Mak
_MC = {}


def mak(phase=0.0, run=0.0, back=False, scale=1.0, look=0.0, gasp=0.0, oar=False):
    """Mak: indigo short-sleeved shirt, red-checked pha khao ma tied at the waist, brown knee trousers, bare shins,
    short black hair. oar: holding a long rowing oar. Returns (RGBA, feet_x, feet_y)."""
    q = (round(phase * 12) % 12, round(run, 1), back, round(scale, 2), round(look, 1), round(gasp, 1), oar)
    if q in _MC:
        return _MC[q]
    w, h = 560, 940
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.25 + 0.75 * run)
    L = 16 * run
    feet = {}
    for sg in (-1, 1):
        a = sg * sw * 0.5
        feet[sg] = (cx + sg * 26 + math.sin(a) * 84 + L * 0.2, 860 - abs(math.sin(a)) * 34 * run)
    knees = {}
    for sg in (-1, 1):
        fx, fy = feet[sg]
        knees[sg] = (cx + sg * 28 + L * .4 + (fx - cx - sg * 26) * 0.45, 650)

    def thighs(d, s):
        for sg in (-1, 1):
            kx, ky = knees[sg]
            fx, fy = feet[sg]
            mx, my = kx + (fx - kx) * 0.22, ky + (fy - ky) * 0.22
            d.line([((cx + sg * 28 + L * .5) * s, 450 * s), (kx * s, ky * s), (mx * s, my * s)], fill=255, width=int(54 * s), joint="curve")
            d.rectangle([(cx + sg * 4 - 44 + L * .5) * s, 430 * s, (cx + sg * 4 + 44 + L * .5) * s, 520 * s], fill=255)

    def shins(d, s):
        for sg in (-1, 1):
            kx, ky = knees[sg]; fx, fy = feet[sg]
            d.line([(kx * s, (ky + 30) * s), (fx * s, (fy - 16) * s)], fill=255, width=int(32 * s))
            d.ellipse([(fx - 28) * s, (fy - 16) * s, (fx + 30) * s, (fy + 10) * s], fill=255)

    def torso(d, s):
        d.polygon(P_((cx - 82 + L, 200), (cx + 82 + L, 200), (cx + 70 + L * .8, 340), (cx + 72 + L * .6, 470), (cx - 72 + L * .6, 470), (cx - 70 + L * .8, 340), s=s), fill=255)
        d.ellipse([(cx - 100 + L) * s, 188 * s, (cx - 44 + L) * s, 252 * s], fill=255)
        d.ellipse([(cx + 44 + L) * s, 188 * s, (cx + 100 + L) * s, 252 * s], fill=255)

    def belt(d, s):
        d.polygon(P_((cx - 76 + L * .6, 430), (cx + 76 + L * .6, 430), (cx + 80 + L * .5, 486), (cx - 80 + L * .5, 486), s=s), fill=255)
        d.polygon(P_((cx + 30 + L * .5, 470), (cx + 64 + L * .5, 470), (cx + 56 + L * .4, 600), (cx + 30 + L * .4, 590), s=s), fill=255)  # the knot's tail

    hands = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 82 + L, 220
        if oar:
            ex, ey = sx + sg * 30 + 40, sy + 110
            hx, hy = (cx + 150, 300) if sg == 1 else (cx + 110, 420)
        else:
            a = -sg * sw * 0.9
            ex, ey = sx + math.sin(a) * 92 + sg * 12, sy + math.cos(a) * 104
            b = a - 0.9 * run * sg
            hx, hy = ex + math.sin(b) * 88, ey + math.cos(b) * 84 - 40 * run
        hands[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            pts = hands[sg]
            d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(28 * s), joint="curve")
            hx, hy = pts[2]
            d.ellipse([(hx - 17) * s, (hy - 17) * s, (hx + 17) * s, (hy + 17) * s], fill=255)

    def sleeves(d, s):
        for sg in (-1, 1):
            (sx, sy), (ex, ey), _ = hands[sg]
            mx, my = sx + (ex - sx) * 0.5, sy + (ey - sy) * 0.5
            d.line([(sx * s, sy * s), (mx * s, my * s)], fill=255, width=int(46 * s))
            d.ellipse([(sx - 30) * s, (sy - 28) * s, (sx + 30) * s, (sy + 30) * s], fill=255)
    Lh = L * 1.2

    def head(d, s):
        d.rectangle([(cx - 20 + Lh) * s, 140 * s, (cx + 20 + Lh) * s, 200 * s], fill=255)
        d.ellipse([(cx - 52 + Lh) * s, 30 * s, (cx + 52 + Lh) * s, 170 * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 56 + Lh) * s, 20 * s, (cx + 56 + Lh) * s, 130 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 56 + Lh, 76), (cx - 54 + Lh, 104), (cx - 40 + Lh, 64), (cx + 40 + Lh, 60), (cx + 54 + Lh, 100), (cx + 56 + Lh, 76), s=s), fill=255)
        if back:
            d.ellipse([(cx - 54 + Lh) * s, 26 * s, (cx + 54 + Lh) * s, 140 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(shins, (w, h), SKIN, 12))
    img.alpha_composite(shade(thighs, (w, h), TROU, 24, rim_strength=1.1))
    if not back:
        img.alpha_composite(shade(arms, (w, h), SKIN, 10))
    img.alpha_composite(shade(torso, (w, h), SHIRT, 36, rim_strength=1.1))
    img.alpha_composite(shade(belt, (w, h), CHECK, 12))
    bd = ImageDraw.Draw(img)
    for k in range(9):                                                   # the white check lines
        x = cx - 72 + k * 18 + L * .55
        bd.line([(x, 434), (x, 482)], fill=(220, 200, 190, 150), width=3)
    bd.line([(cx - 78 + L * .55, 458), (cx + 78 + L * .55, 458)], fill=(220, 200, 190, 150), width=3)
    img.alpha_composite(shade(sleeves, (w, h), SHIRT, 14))
    if back:
        img.alpha_composite(shade(arms, (w, h), SKIN, 10))
    img.alpha_composite(shade(head, (w, h), SKIN, 26))
    img.alpha_composite(shade(hair, (w, h), HAIR, 10, rim_strength=1.1))
    d = ImageDraw.Draw(img)
    if not back:
        for sg in (-1, 1):
            ex_, ey_ = cx + sg * 20 + Lh, 100 - 6 * look
            r_ = 10 + 3 * gasp
            d.ellipse([ex_ - r_, ey_ - r_ * .8, ex_ + r_, ey_ + r_ * .8], fill=(240, 236, 230, 255))
            d.ellipse([ex_ - 5, ey_ - 6 - 3 * look, ex_ + 5, ey_ + 4 - 3 * look], fill=(15, 10, 10, 255))
            d.line([(ex_ - 13, ey_ - 20 - 6 * gasp), (ex_ + 13, ey_ - 18 - 3 * sg - 6 * gasp)], fill=(20, 12, 10, 255), width=5)
        if gasp > 0.3:
            d.ellipse([cx - 10 + Lh, 132, cx + 10 + Lh, 132 + 24 * gasp], fill=(50, 16, 16, 255))
        else:
            d.line([(cx - 12 + Lh, 140), (cx + 12 + Lh, 140)], fill=(80, 36, 30, 255), width=4)
    if oar:                                                                  # the long oar
        d.line([(cx + 200, 160), (cx - 40, 1000)], fill=(110, 72, 40, 255), width=14)
        img.alpha_composite(shade(arms, (w, h), SKIN, 10))
    if scale != 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    out = (img, cx * scale, 866 * scale)
    _MC[q] = out
    return out


_MCR = {}


def mak_crouch(scale=1.0, look=0.0, cover=0.0):
    """Mak crouched, hugging his knees, one hand over his mouth (cover 0..1); look turns the head up (+)."""
    k = (round(scale, 2), round(look, 1), round(cover, 1))
    if k in _MCR:
        return _MCR[k]
    w, h = 540, 660
    cx = w / 2
    L = look * 26

    def legs(d, s):
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 54 - 62) * s, 290 * s, (cx + sg * 54 + 62) * s, 410 * s], fill=255)
            d.polygon(P_((cx + sg * 54 - 58, 350), (cx + sg * 54 + 58, 350), (cx + sg * 68 + 44, 470), (cx + sg * 68 - 44, 470), s=s), fill=255)
        d.ellipse([(cx - 124) * s, 420 * s, (cx + 124) * s, 560 * s], fill=255)

    def shins(d, s):
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 68 - 36, 460), (cx + sg * 68 + 36, 460), (cx + sg * 70 + 30, 600), (cx + sg * 70 - 30, 600), s=s), fill=255)
            d.ellipse([(cx + sg * 72 - 44) * s, 590 * s, (cx + sg * 72 + 44) * s, 630 * s], fill=255)

    def body(d, s):
        d.polygon(P_((cx - 92, 200), (cx + 92, 200), (cx + 104, 400), (cx - 104, 400), s=s), fill=255)
        d.ellipse([(cx - 112) * s, 186 * s, (cx - 56) * s, 262 * s], fill=255)
        d.ellipse([(cx + 56) * s, 186 * s, (cx + 112) * s, 262 * s], fill=255)

    def arms(d, s):
        d.line([((cx - 100) * s, 232 * s), ((cx - 134) * s, 330 * s), ((cx + 40) * s, 360 * s)], fill=255, width=int(30 * s), joint="curve")
        d.ellipse([(cx + 24) * s, 342 * s, (cx + 58) * s, 376 * s], fill=255)
        hy = 300 - 120 * cover
        d.line([((cx + 100) * s, 232 * s), ((cx + 124) * s, 320 * s), ((cx + 20 + L * .3) * s, hy * s)], fill=255, width=int(28 * s), joint="curve")
        d.ellipse([(cx + 2 + L * .3) * s, (hy - 18) * s, (cx + 38 + L * .3) * s, (hy + 18) * s], fill=255)

    def head(d, s):
        d.ellipse([(cx - 52 + L * .3) * s, (70 - L) * s, (cx + 52 + L * .3) * s, (206 - L) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 56 + L * .3) * s, (60 - L) * s, (cx + 56 + L * .3) * s, (170 - L) * s], 180, 360, fill=255)
        d.polygon(P_((cx - 56 + L * .3, 116 - L), (cx - 52 + L * .3, 142 - L), (cx - 38 + L * .3, 104 - L), (cx + 38 + L * .3, 100 - L), (cx + 52 + L * .3, 140 - L), (cx + 56 + L * .3, 116 - L), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(body, (w, h), SHIRT, 36))
    img.alpha_composite(shade(head, (w, h), SKIN, 28))
    img.alpha_composite(shade(hair, (w, h), HAIR, 10))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ex_ = cx + sg * 20 + L * .3; ey_ = 136 - L * 1.1
        d.ellipse([ex_ - 12, ey_ - 10, ex_ + 12, ey_ + 10], fill=(240, 236, 230, 255))
        d.ellipse([ex_ - 4 + look * 3, ey_ - 8, ex_ + 4 + look * 3, ey_ + 1], fill=(15, 10, 10, 255))
    img.alpha_composite(shade(shins, (w, h), SKIN, 12))
    img.alpha_composite(shade(legs, (w, h), TROU, 30, rim_strength=1.1))
    img.alpha_composite(shade(arms, (w, h), SKIN, 12))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 620 * scale)
    _MCR[k] = out
    return out


# ============================================================ Mae Nak
_NK = {}


def nak(pose="baby", ghost=0.0, sway=0.0):
    """Mae Nak: crimson sabai with a gold edge over her left shoulder, dark green pha sin with a gold hem, very long black
    hair, pale face. pose: "baby" (standing, cradling a baby bundle), "stand" (arms down), "float" (ghost: arms far too
    long, hair over her face, feet off the ground), "kneel" (sitting on her folded legs by the mortar, right arm left
    out - drawn by long_arm from the returned shoulder point). ghost 0..1: paler + red eyes.
    Returns (RGBA, anchor_x, anchor_y (feet / seat), [eyes], right_shoulder)."""
    key = (pose, round(ghost, 1), round(sway, 1))
    if key in _NK:
        return _NK[key]
    w, h = 640, 1400
    cx = w / 2
    r = np.random.default_rng(17)
    sw = sway * 30
    kneel = pose == "kneel"
    hx0, hy0 = cx, 170
    sh = 262
    waist = 520
    bot = 1200 if not kneel else 760
    skin = tuple(int(a * (1 - ghost) + b * ghost) for a, b in zip(NSKIN, GSKIN))

    def back_hair(d, s):
        hb = 900 if not kneel else 700
        d.polygon(P_((hx0 - 70, hy0 - 40), (hx0 + 70, hy0 - 40), (hx0 + 110 + sw, hb), (hx0 + 40 + sw, hb + 50), (hx0 - 60 + sw, hb + 30), (hx0 - 110 + sw, hb - 20), s=s), fill=255)

    def skirt(d, s):
        if kneel:
            d.polygon(P_((cx - 90, waist), (cx + 90, waist), (cx + 190, bot - 60), (cx + 200, bot), (cx - 210, bot), (cx - 170, bot - 70), s=s), fill=255)
        else:
            d.polygon(P_((cx - 92, waist), (cx + 92, waist), (cx + 104, 900), (cx + 98 + sw * .3, bot), (cx - 98 + sw * .3, bot), (cx - 104, 900), s=s), fill=255)

    def feet(d, s):
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 40 - 30) * s, (bot - 10) * s, (cx + sg * 40 + 30) * s, (bot + 22) * s], fill=255)

    def torso(d, s):
        d.polygon(P_((cx - 78, sh - 12), (cx + 78, sh - 12), (cx + 64, waist), (cx - 64, waist), s=s), fill=255)
        d.ellipse([(cx - 96) * s, (sh - 28) * s, (cx - 40) * s, (sh + 30) * s], fill=255)
        d.ellipse([(cx + 40) * s, (sh - 28) * s, (cx + 96) * s, (sh + 30) * s], fill=255)

    def sabai(d, s):
        d.polygon(P_((cx - 90, sh - 24), (cx - 34, sh - 24), (cx + 80, sh + 150), (cx + 68, waist - 40), (cx - 68, waist - 30), (cx - 84, sh + 60), s=s), fill=255)
        d.polygon(P_((cx - 96, sh - 20), (cx - 58, sh - 20), (cx - 66, sh + 420), (cx - 104, sh + 400), s=s), fill=255)   # tail down the back

    arm = {}
    if pose == "baby":
        arm[-1] = ((cx - 78, sh), (cx - 96, sh + 150), (cx + 10, sh + 200))
        arm[1] = ((cx + 78, sh), (cx + 92, sh + 120), (cx - 10, sh + 120))
    elif pose == "float":
        for sg in (-1, 1):
            arm[sg] = ((cx + sg * 80, sh), (cx + sg * 104, sh + 290), (cx + sg * 116 + sw * .4, sh + 640))
    elif pose == "kneel":
        arm[-1] = ((cx - 78, sh), (cx - 120, sh + 190), (cx - 160, sh + 330))
    else:
        for sg in (-1, 1):
            arm[sg] = ((cx + sg * 80, sh), (cx + sg * 98, sh + 200), (cx + sg * 100, sh + 390))

    def arms(d, s):
        for sg, pts in arm.items():
            d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(24 * s), joint="curve")
            x, y = pts[2]
            d.ellipse([(x - 16) * s, (y - 16) * s, (x + 16) * s, (y + 16) * s], fill=255)

    def fingers(d, s):
        if pose != "float":
            return
        for sg in (-1, 1):
            (_, _), (ex, ey), (hx, hy) = arm[sg]
            a0 = math.atan2(hy - ey, hx - ex)
            for f in range(4):
                a = a0 + (f - 1.5) * 0.18
                d.line([(hx * s, hy * s), ((hx + math.cos(a) * 80) * s, (hy + math.sin(a) * 80) * s)], fill=255, width=int(8 * s))

    def bundle(d, s):
        d.ellipse([(cx - 90) * s, (sh + 90) * s, (cx + 100) * s, (sh + 220) * s], fill=255)
        d.ellipse([(cx + 30) * s, (sh + 70) * s, (cx + 120) * s, (sh + 160) * s], fill=255)

    def head(d, s):
        d.rectangle([(hx0 - 22) * s, (hy0 + 40) * s, (hx0 + 22) * s, (sh) * s], fill=255)
        d.ellipse([(hx0 - 52) * s, (hy0 - 70) * s, (hx0 + 52) * s, (hy0 + 74) * s], fill=255)

    def front_hair(d, s):
        d.pieslice([(hx0 - 62) * s, (hy0 - 86) * s, (hx0 + 62) * s, (hy0 + 30) * s], 180, 360, fill=255)
        for sg in (-1, 1):
            d.polygon(P_((hx0 + sg * 10, hy0 - 82), (hx0 + sg * 62, hy0 - 40), (hx0 + sg * 74, hy0 + 140), (hx0 + sg * 54, hy0 + 200), (hx0 + sg * 44, hy0 + 20), (hx0 + sg * 30, hy0 - 50), s=s), fill=255)
        if ghost > 0.5 and pose == "float":                                  # strands over the face
            for k in range(14):
                x = hx0 - 46 + k * 7
                if abs(x - hx0 - 0) < 6 or abs(abs(x - hx0) - 22) < 7:
                    continue
                d.line([(x * s, (hy0 - 60) * s), ((x + r.uniform(-8, 8)) * s, (hy0 + r.uniform(120, 300)) * s)], fill=255, width=int(r.uniform(4, 8) * s))

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(back_hair, (w, h), HAIR, 14, rim_strength=1.1))
    img.alpha_composite(shade(skirt, (w, h), SIN, 50, rim_strength=1.0))
    gd = ImageDraw.Draw(img)
    if kneel:
        gd.line([(cx - 200, bot - 14), (cx + 196, bot - 14)], fill=GOLD_ + (255,), width=12)
    else:
        gd.rectangle([cx - 99 + sw * .3, bot - 46, cx + 99 + sw * .3, bot - 20], fill=GOLD_ + (255,))
        for k in range(6):                                                     # pleat in front
            gd.line([(cx - 10 + k * 4, waist + 20), (cx - 14 + k * 5 + sw * .2, bot - 50)], fill=(18, 40, 34, 160), width=2)
    gd.rectangle([cx - 90, waist - 6, cx + 90, waist + 14], fill=GOLD_ + (255,))
    if pose in ("baby", "stand"):
        img.alpha_composite(shade(feet, (w, h), skin, 8))
    img.alpha_composite(shade(torso, (w, h), skin, 30))
    img.alpha_composite(shade(sabai, (w, h), SABAI, 26, rim_strength=1.0))
    sd = ImageDraw.Draw(img)
    sd.line([(cx - 34, sh - 22), (cx + 80, sh + 150)], fill=GOLD_ + (255,), width=6)
    sd.line([(cx - 66, waist - 32), (cx + 68, waist - 42)], fill=GOLD_ + (255,), width=5)
    img.alpha_composite(shade(arms, (w, h), skin, 10))
    img.alpha_composite(shade(fingers, (w, h), (70, 50, 50), 3, rim_strength=0.6))
    if pose == "baby":
        img.alpha_composite(shade(bundle, (w, h), CLOTH, 34))
        bd = ImageDraw.Draw(img)
        bd.ellipse([cx + 46, sh + 92, cx + 104, sh + 146], fill=(28, 18, 20, 255))         # the bundle's dark opening (no face)
        for k in range(3):
            bd.arc([cx - 80 + k * 30, sh + 100, cx + 40 + k * 30, sh + 230], 200, 300, fill=(170, 160, 150, 255), width=3)
        img.alpha_composite(shade(arms, (w, h), skin, 10))
    img.alpha_composite(shade(head, (w, h), skin, 30))
    d = ImageDraw.Draw(img)
    eyes = [(hx0 - 20, hy0 + 2), (hx0 + 20, hy0 + 2)]
    for ex_, ey_ in eyes:
        if ghost > 0.5:
            d.ellipse([ex_ - 13, ey_ - 9, ex_ + 13, ey_ + 11], fill=(24, 8, 10, 255))
        else:
            d.ellipse([ex_ - 10, ey_ - 6, ex_ + 10, ey_ + 6], fill=(30, 20, 20, 255))
            d.line([(ex_ - 12, ey_ - 14), (ex_ + 12, ey_ - 14)], fill=(20, 12, 10, 255), width=4)
    if ghost > 0.5:
        d.arc([hx0 - 30, hy0 + 18, hx0 + 30, hy0 + 54], 20, 160, fill=(40, 8, 10, 255), width=5)
    else:
        d.arc([hx0 - 16, hy0 + 26, hx0 + 16, hy0 + 44], 20, 160, fill=(120, 40, 40, 255), width=4)   # a soft smile
    img.alpha_composite(shade(front_hair, (w, h), HAIR, 12, rim_strength=1.2))
    out = (img, cx, bot + 12 if not kneel else bot, eyes, (cx + 78, sh))
    _NK[key] = out
    return out


def put_nak(img, x, y, scale, t, pose="baby", ghost=0.0, sway=None, eyes=None, aura=0.0, alpha=1.0, dark=0.0):
    """Returns (img, right_shoulder_xy_on_screen)."""
    sw = math.sin(t * 1.1) * 0.5 if sway is None else sway
    body, ax, ay, ee, shr = nak(pose, ghost, round(sw * 5) / 5)
    g = body.resize((max(1, int(body.width * scale)), max(1, int(body.height * scale))), Image.LANCZOS)
    if dark > 0:
        g = tint(g, (1 - 0.85 * dark, 1 - 0.9 * dark, 1 - 0.9 * dark))
    if alpha < 1:
        g = with_alpha(g, alpha)
    gx, gy = int(x - ax * scale), int(y - ay * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(max(3, 30 * scale)))
        lay = Image.new("RGBA", g.size, (255, 40, 30, 0)); lay.putalpha(al.point(lambda v: int(v * aura * alpha)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    ek = ghost if eyes is None else eyes
    if ek > 0:
        k = ek * alpha * (0.65 + 0.35 * math.sin(t * 5) ** 2)
        for ex, ey in ee:
            eye(img, gx + ex * scale, gy + ey * scale, k, max(0.2, scale * 0.9))
    return img, (gx + shr[0] * scale, gy + shr[1] * scale)


def long_arm(img, p0, p1, t, width=24, bend=0.0, fingers=1.0, skin=GSKIN):
    """Her arm, stretched impossibly long from the shoulder p0 to the hand at p1: pale and bony, a dark edge, a thin red
    edge light, knuckle creases at three joints, long fingers spread toward the target. No gore."""
    d = ImageDraw.Draw(img)
    x0, y0 = p0; x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy) + 1e-6
    ux, uy = dx / ln, dy / ln; nx, ny = -uy, ux
    pts = []
    for i in range(9):
        u = i / 8
        off = bend * ln * 0.06 * math.sin(u * math.pi) + 6 * math.sin(u * 13 + t * 3) * (1 - abs(2 * u - 1))
        pts.append((x0 + dx * u + nx * off, y0 + dy * u + ny * off))
    wd = [int(width * (1.1 - 0.35 * i / 8)) for i in range(9)]
    for i in range(8):
        d.line([pts[i], pts[i + 1]], fill=(20, 10, 12, 255), width=wd[i] + 8)
    for i in range(8):
        d.line([pts[i], pts[i + 1]], fill=tuple(int(c * 0.8) for c in skin) + (255,), width=wd[i])
        d.line([(pts[i][0] - nx * wd[i] * .2, pts[i][1] - ny * wd[i] * .2), (pts[i + 1][0] - nx * wd[i] * .2, pts[i + 1][1] - ny * wd[i] * .2)], fill=skin + (255,), width=max(2, wd[i] // 2))
        d.line([(pts[i][0] + nx * wd[i] * .45, pts[i][1] + ny * wd[i] * .45), (pts[i + 1][0] + nx * wd[i] * .45, pts[i + 1][1] + ny * wd[i] * .45)], fill=(255, 60, 44, 230), width=2)
    for i in (2, 4, 6):                                                    # knuckle creases at the joints
        px, py = pts[i]
        for j in (-1, 1):
            d.line([(px + ux * j * 5 - nx * wd[i] * .4, py + uy * j * 5 - ny * wd[i] * .4), (px + ux * j * 5 + nx * wd[i] * .3, py + uy * j * 5 + ny * wd[i] * .3)], fill=(110, 100, 100, 255), width=2)
    hw = width * 0.9
    d.ellipse([x1 - hw, y1 - hw, x1 + hw, y1 + hw], fill=skin + (255,), outline=(20, 10, 12, 255), width=3)
    if fingers > 0:
        a0 = math.atan2(uy, ux)
        for f in range(4):
            a = a0 + (f - 1.5) * 0.28 * fingers
            fl = width * (3.0 + 0.4 * (1 - abs(f - 1.5)))
            ex, ey = x1 + math.cos(a) * fl, y1 + math.sin(a) * fl
            d.line([(x1, y1), (ex, ey)], fill=(20, 10, 12, 255), width=int(width * .42) + 4)
            d.line([(x1, y1), (ex, ey)], fill=skin + (255,), width=int(width * .42))
            d.line([((x1 + ex * 3) / 4, (y1 + ey * 3) / 4), (ex, ey)], fill=(60, 40, 40, 255), width=int(width * .3))
    return img


_NF = {}


def nak_face(mode="smile", inv=False):
    """Close-up for the jump scares: a bone-pale face between two curtains of centre-parted black hair, strands across
    it, deep eye hollows (red glow drawn by put_nface), the crimson sabai with its gold edge at the shoulder.
    mode "smile" = a thin smile far too wide; "scream" = a dark open mouth (no teeth, no gore). Face centre (450, 470)."""
    k = (mode, inv)
    if k in _NF:
        return _NF[k]
    w, h = 900, 1100
    cx, cy = 450, 470

    def face(d, s):
        d.polygon(P_((cx - 175, cy - 230), (cx + 175, cy - 230), (cx + 195, cy - 20), (cx + 150, cy + 210), (cx + 64, cy + 310),
                     (cx, cy + 330), (cx - 64, cy + 310), (cx - 150, cy + 210), (cx - 195, cy - 20), s=s), fill=255)
        d.ellipse([(cx - 195) * s, (cy - 370) * s, (cx + 195) * s, (cy + 40) * s], fill=255)

    def neck(d, s):
        d.rectangle([(cx - 84) * s, (cy + 200) * s, (cx + 84) * s, h * s], fill=255)

    def sab(d, s):
        d.polygon(P_((cx - 430, h), (cx - 330, cy + 400), (cx - 150, cy + 380), (cx + 260, h), s=s), fill=255)

    def hair(d, s):
        r = np.random.default_rng(31)
        d.pieslice([(cx - 245) * s, (cy - 420) * s, (cx + 245) * s, (cy + 60) * s], 180, 360, fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 14, cy - 410), (cx + sg * 240, cy - 210), (cx + sg * 330, cy + 660), (cx + sg * 160, cy + 680), (cx + sg * 170, cy + 40), (cx + sg * 90, cy - 260), s=s), fill=255)
        for kk in range(10):
            x = cx - 170 + kk * 38 + r.uniform(-8, 8)
            if abs(abs(x - cx) - 85) < 36 or abs(x - cx) < 30:
                continue
            ln = r.uniform(300, 620)
            d.line([(x * s, (cy - 250) * s), ((x + r.uniform(-30, 30)) * s, (cy - 250 + ln * .5) * s), ((x + r.uniform(-50, 50)) * s, (cy - 250 + ln) * s)],
                   fill=255, width=int(r.uniform(8, 14) * s), joint="curve")

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(neck, (w, h), GSKIN, 40))
    img.alpha_composite(shade(sab, (w, h), SABAI, 50))
    ImageDraw.Draw(img).line([(cx - 150, cy + 380), (cx + 260, h)], fill=GOLD_ + (255,), width=14)
    img.alpha_composite(shade(face, (w, h), GSKIN, 110, rim_strength=0.9))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        d.ellipse([cx + sg * 85 - 56, cy - 50, cx + sg * 85 + 56, cy + 38], fill=(26, 10, 12, 255))
        d.line([(cx + sg * 30, cy - 98), (cx + sg * 134, cy - 70)], fill=(90, 70, 70, 255), width=6)
    d.polygon([(cx - 12, cy + 70), (cx + 12, cy + 70), (cx + 20, cy + 116), (cx - 20, cy + 116)], fill=(180, 172, 168, 255))
    if mode == "scream":
        d.ellipse([cx - 70, cy + 140, cx + 70, cy + 300], fill=(22, 4, 6, 255))
        d.ellipse([cx - 50, cy + 160, cx + 50, cy + 280], fill=(8, 0, 2, 255))
    else:
        d.arc([cx - 200, cy + 60, cx + 200, cy + 250], 15, 165, fill=(28, 6, 8, 255), width=12)
        for sg in (-1, 1):
            d.line([(cx + sg * 190, cy + 170), (cx + sg * 226, cy + 118)], fill=(28, 6, 8, 255), width=10)
    img.alpha_composite(shade(hair, (w, h), HAIR, 24, rim_strength=1.3))
    eyes = [(cx - 85, cy - 6), (cx + 85, cy - 6)]
    if inv:
        img = img.rotate(180, resample=Image.BICUBIC, center=(cx, cy))
        eyes = [(2 * cx - x, 2 * cy - y) for x, y in eyes]
    _NF[k] = (img, eyes)
    return _NF[k]


def put_nface(img, x, y, scale, t, mode="smile", tilt=0.0, aura=0.7, alpha=1.0, inv=False, eyes=1.0):
    fimg, ee = nak_face(mode, inv)
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


def nface_full(t, t0, mode="smile", inv=False, scale=1.25, y=880, bg=(6, 1, 2), tilt=0.0, x=540):
    img = Image.new("RGBA", (W, H), bg + (255,))
    return put_nface(img, x, y + 120 * ss(t, t0, t0 + 0.15) * (1 if not inv else -1), scale, t, mode=mode, aura=0.9, inv=inv, tilt=tilt)


# ============================================================ small cast + props
_SP = {}


def boat_sprite(length=620):
    """A long, low wooden canal boat (rua) with upturned ends."""
    k = ("boat", length)
    if k not in _SP:
        w, h = length + 80, 150
        def hull(d, s):
            d.polygon(P_((40, 40), (100, 80), (w - 100, 80), (w - 40, 30), (w - 70, 120), (110, 124), s=s), fill=255)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        im.alpha_composite(shade(hull, (w, h), (84, 52, 34), 16))
        dd = ImageDraw.Draw(im)
        dd.line([(100, 84), (w - 100, 84)], fill=(140, 90, 56, 255), width=5)
        for x in range(160, w - 140, 90):
            dd.line([(x, 84), (x + 6, 118)], fill=(50, 30, 20, 255), width=3)
        _SP[k] = im
    return _SP[k]


def boatman_sprite():
    """The old boatman, sitting in his boat: a wide ngob palm-leaf hat, dark clothes, a grey beard."""
    k = "boatman"
    if k not in _SP:
        w, h = 360, 420
        def body(d, s):
            d.polygon(P_((110, 220), (250, 220), (290, 400), (70, 400), s=s), fill=255)
        def head(d, s):
            d.ellipse([140 * s, 130 * s, 220 * s, 230 * s], fill=255)
        def hat(d, s):
            d.polygon(P_((40, 160), (180, 70), (320, 160), (180, 180), s=s), fill=255)
        def arm(d, s):
            d.line([(240 * s, 240 * s), (300 * s, 300 * s), (250 * s, 320 * s)], fill=255, width=int(26 * s), joint="curve")
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        im.alpha_composite(shade(body, (w, h), (40, 34, 36), 30))
        im.alpha_composite(shade(head, (w, h), (150, 104, 76), 20))
        dd = ImageDraw.Draw(im)
        dd.polygon([(150, 200), (210, 200), (196, 250), (164, 250)], fill=(190, 184, 176, 255))   # beard
        im.alpha_composite(shade(arm, (w, h), (150, 104, 76), 8))
        im.alpha_composite(shade(hat, (w, h), (150, 120, 70), 20))
        _SP[k] = im
    return _SP[k]


def boy_sprite(lime_up=0.0):
    """A little temple boy (dek wat): shaved head, white shirt, dark shorts, a woven basket on one arm; lime_up raises
    his right hand with a green lime in it."""
    k = ("boy", round(lime_up, 1))
    cx = 180
    if k not in _SP:
        w, h = 360, 600
        hand = (cx + 70 + 40 * lime_up, 330 - 190 * lime_up)
        def legs(d, s):
            for sg in (-1, 1):
                d.line([((cx + sg * 22) * s, 400 * s), ((cx + sg * 26) * s, 560 * s)], fill=255, width=int(26 * s))
        def shorts(d, s):
            d.polygon(P_((cx - 60, 360), (cx + 60, 360), (cx + 66, 450), (cx - 66, 450), s=s), fill=255)
        def shirt(d, s):
            d.polygon(P_((cx - 64, 220), (cx + 64, 220), (cx + 62, 380), (cx - 62, 380), s=s), fill=255)
        def arms(d, s):
            d.line([((cx - 60) * s, 240 * s), ((cx - 80) * s, 330 * s), ((cx - 70) * s, 400 * s)], fill=255, width=int(20 * s), joint="curve")
            d.line([((cx + 60) * s, 240 * s), ((cx + 84) * s, 300 * s), (hand[0] * s, hand[1] * s)], fill=255, width=int(20 * s), joint="curve")
        def head(d, s):
            d.ellipse([(cx - 52) * s, 100 * s, (cx + 52) * s, 226 * s], fill=255)
        def basket(d, s):
            d.ellipse([(cx - 150) * s, 360 * s, (cx - 40) * s, 470 * s], fill=255)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        im.alpha_composite(shade(legs, (w, h), (150, 104, 76), 10))
        im.alpha_composite(shade(shorts, (w, h), (40, 36, 44), 14))
        im.alpha_composite(shade(shirt, (w, h), (224, 220, 210), 30))
        im.alpha_composite(shade(basket, (w, h), (150, 110, 60), 24))
        bd = ImageDraw.Draw(im)
        for k2 in range(5):
            bd.line([(cx - 146 + k2 * 22, 380), (cx - 140 + k2 * 22, 460)], fill=(100, 70, 36, 255), width=3)
        im.alpha_composite(shade(arms, (w, h), (150, 104, 76), 8))
        im.alpha_composite(shade(head, (w, h), (150, 104, 76), 26))
        dd = ImageDraw.Draw(im)
        dd.pieslice([cx - 54, 96, cx + 54, 190], 180, 360, fill=(40, 34, 34, 255))           # shaved head shadow
        for sg in (-1, 1):
            dd.ellipse([cx + sg * 18 - 9, 156, cx + sg * 18 + 9, 170], fill=(20, 14, 14, 255))
        dd.arc([cx - 14, 180, cx + 14, 200], 200, 340, fill=(80, 36, 30, 255), width=3)      # not smiling
        if lime_up > 0:
            hx, hy = hand
            dd.ellipse([hx - 26, hy - 34, hx + 26, hy + 14], fill=LIME + (255,), outline=(40, 70, 20, 255), width=3)
            dd.ellipse([hx - 12, hy - 26, hx - 2, hy - 14], fill=(200, 240, 150, 255))
        _SP[k] = im
    return _SP[k], cx, 566


def lime_sprite(r=16):
    k = ("lime", r)
    if k not in _SP:
        im = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse([r, r * 1.2, r * 3, r * 2.9], fill=LIME + (255,), outline=(40, 70, 20, 255), width=max(1, r // 6))
        d.ellipse([r * 1.4, r * 1.5, r * 1.9, r * 1.9], fill=(210, 245, 160, 255))
        _SP[k] = im
    return _SP[k]


def put_lime(img, x, y, r=16, glow=0.6):
    if glow > 0:
        img = glow_on(img, gsp(int(r * 3), (170, 255, 120), 2.0), x, y, glow)
    s = lime_sprite(r)
    img.alpha_composite(s, (int(x - 2 * r), int(y - 2 * r)))
    return img


def dog_sprite(bark=0.0):
    k = ("dog", round(bark, 1))
    if k not in _SP:
        w, h = 300, 220
        def body(d, s):
            d.ellipse([60 * s, 80 * s, 220 * s, 150 * s], fill=255)
            for x in (80, 110, 180, 205):
                d.line([(x * s, 130 * s), ((x + 4) * s, 200 * s)], fill=255, width=int(14 * s))
            d.line([(70 * s, 100 * s), (30 * s, 70 * s)], fill=255, width=int(10 * s))             # tail
            hy = 60 - 20 * bark
            d.ellipse([190 * s, (hy - 10) * s, 260 * s, (hy + 50) * s], fill=255)
            d.polygon(P_((240, hy + 10), (290, hy + 22 - 12 * bark), (250, hy + 40), s=s), fill=255)
            d.polygon(P_((200, hy), (214, hy - 30), (226, hy), s=s), fill=255)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        im.alpha_composite(shade(body, (w, h), (60, 44, 34), 16))
        _SP[k] = im
    return _SP[k]


# ============================================================ sets
def colorize(mask, col):
    lay = Image.new("RGBA", mask.size, tuple(col) + (0,)); lay.putalpha(mask)
    return lay


def thai_house_mask(d, x, base, w, wall, roof, s=1, posts=60):
    """A teak house on stilts seen from the side of the canal: posts, a panelled wall, a steep gable roof with curled
    ngao finials at the eaves and a horn at the top."""
    fl = base - posts
    for k in range(5):
        px = x + 8 + k * (w - 16) / 4
        d.rectangle([(px - 3) * s, fl * s, (px + 3) * s, base * s], fill=255)
    d.rectangle([x * s, (fl - wall) * s, (x + w) * s, fl * s], fill=255)
    d.rectangle([(x - 8) * s, (fl - 4) * s, (x + w + 8) * s, (fl + 4) * s], fill=255)
    top = fl - wall
    d.polygon(P_((x - 14, top + 6), (x + w + 14, top + 6), (x + w / 2, top - roof), s=s), fill=255)
    for ex, sg in ((x - 14, -1), (x + w + 14, 1)):                        # ngao curls
        d.arc([(ex - 10) * s, (top - 14) * s, (ex + 10) * s, (top + 6) * s], 90 if sg > 0 else 0, 270 if sg > 0 else 180, fill=255, width=max(1, int(3 * s)))
    d.line([((x + w / 2) * s, (top - roof) * s), ((x + w / 2 + 6) * s, (top - roof - 18) * s)], fill=255, width=max(1, int(4 * s)))


class Klong:
    """The Phra Khanong canal at night in old Siam: plum-black sky with a pale red moon, a far tree line with Wat Mahabut's
    white chedi and lantern-lit roofs on the right, teak houses on stilts with steep gables along the far bank, coconut
    palms, black water with the moon's road, lotus pads and drifting water hyacinth, and the near bank's dirt path with
    reeds. Parallax layers; cam pans right."""
    def __init__(self):
        r = np.random.default_rng(171)
        self.WW = WW = W + 600
        self.sky = to_img(moon_sky((700, 380), 105, top=(3, 1, 6), mid=(34, 8, 26), bot=(100, 26, 36), ym=0.5))
        # far: tree line + the temple
        m = Image.new("L", (WW, H), 0); d = ImageDraw.Draw(m)
        for k in range(70):
            x = r.uniform(0, WW); rr = r.uniform(30, 80)
            d.ellipse([x - rr, 900 - rr * 1.4 - r.uniform(0, 40), x + rr, 960], fill=255)
        d.rectangle([0, 930, WW, 975], fill=255)
        self.far = colorize(m.filter(ImageFilter.GaussianBlur(1.2)), (24, 7, 16))
        tm = Image.new("L", (WW, H), 0); td = ImageDraw.Draw(tm)
        tx = WW - 330
        self.temple_x = tx
        td.polygon([(tx - 70, 930), (tx + 70, 930), (tx + 50, 860), (tx - 50, 860)], fill=255)          # chedi base
        td.pieslice([tx - 60, 780, tx + 60, 900], 180, 360, fill=255)                                      # bell
        td.rectangle([tx - 20, 760, tx + 20, 842], fill=255)
        td.polygon([(tx - 18, 770), (tx + 18, 770), (tx, 600)], fill=255)                                  # spire
        for k in range(4):
            td.ellipse([tx - 14 + k * 2, 740 - k * 30, tx + 14 - k * 2, 756 - k * 30], fill=255)
        ux = tx - 230                                                                                      # ubosot roof tiers
        for k, (wd, y0) in enumerate(((240, 900), (190, 860), (140, 824))):
            td.polygon([(ux - wd / 2, y0 + 20), (ux + wd / 2, y0 + 20), (ux + 20, y0 - 40), (ux - 20, y0 - 40)], fill=255)
            td.line([(ux + wd / 2, y0 + 20), (ux + wd / 2 + 14, y0 - 6)], fill=255, width=4)               # chofa horns
            td.line([(ux - wd / 2, y0 + 20), (ux - wd / 2 - 14, y0 - 6)], fill=255, width=4)
        td.rectangle([ux - 110, 920, ux + 110, 960], fill=255)
        self.temple = colorize(tm, (62, 30, 34))
        self.temple_lamps = [(tx - 80 + k * 40, 935) for k in range(5)] + [(ux - 90 + k * 45, 925) for k in range(5)]
        # mid: teak houses on stilts + coconut palms on the far bank
        hm = Image.new("L", (WW, H), 0); hd = ImageDraw.Draw(hm)
        pm = Image.new("L", (WW, H), 0); pd = ImageDraw.Draw(pm)
        x = 20; self.lit = []
        while x < WW - 520:
            wd = r.uniform(130, 190); wall = r.uniform(50, 70); roof = wd * r.uniform(0.55, 0.7)
            thai_house_mask(hd, x, 1000, wd, wall, roof, posts=r.uniform(50, 70))
            if r.random() < 0.45:
                self.lit.append((x + wd * r.uniform(.25, .7), 1000 - 60 - wall / 2))
            if r.random() < 0.7:
                sugar_palm(pd, x + wd + r.uniform(10, 40), 1000, r.uniform(240, 340), 1, r)
            x += wd + r.uniform(60, 160)
        self.houses = colorize(hm, (52, 26, 26))
        self.palms = colorize(pm, (30, 10, 18))
        hdd = ImageDraw.Draw(self.houses)
        for lx, ly in self.lit:
            hdd.rectangle([lx - 12, ly - 14, lx + 12, ly + 12], fill=(255, 160, 80, 255))
        # water
        self.wy = (990, 1420)
        self.water = vgrad((30, 8, 20), (16, 4, 12), (8, 2, 6), 0.5, W, self.wy[1] - self.wy[0])
        # floating lotus + hyacinth (water layer, par .7)
        fl = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
        def pads(d, s):
            rr = np.random.default_rng(5)
            for k in range(26):
                x = rr.uniform(0, WW); y = rr.uniform(1250, 1410); a = rr.uniform(26, 60)
                d.ellipse([(x - a) * s, (y - a * .32) * s, (x + a) * s, (y + a * .32) * s], fill=255)
        fl.alpha_composite(shade(pads, (WW, H), (34, 56, 40), 10, rim=(255, 80, 60)))
        fd = ImageDraw.Draw(fl)
        for k in range(6):
            x = r.uniform(100, WW - 100); y = r.uniform(1290, 1400)
            fd.line([(x, y), (x + 4, y - 70)], fill=(30, 50, 34, 255), width=4)
            fd.ellipse([x - 16, y - 100, x + 22, y - 64], fill=(200, 110, 130, 255))                       # a lotus bud
        self.pads = fl
        # near bank: path, reeds, grass
        nb = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); nd = ImageDraw.Draw(nb)
        nd.polygon([(0, 1430), (WW, 1410), (WW, H), (0, H)], fill=(40, 22, 22, 255))
        nd.polygon([(0, 1560), (WW, 1540), (WW, 1720), (0, 1740)], fill=(70, 44, 34, 255))                   # the path
        for k in range(40):
            x = r.uniform(0, WW); y = r.uniform(1560, 1720)
            nd.ellipse([x - 20, y - 4, x + 20, y + 4], fill=(56, 34, 28, 255))
        for k in range(160):                                                                                 # reeds along the water
            x = r.uniform(0, WW); y = r.uniform(1420, 1470); hgt = r.uniform(50, 160)
            nd.line([(x, y), (x + r.uniform(-20, 20), y - hgt)], fill=(30, 26, 22, 255), width=int(r.uniform(2, 4)))
        for k in range(120):
            x = r.uniform(0, WW); y = r.uniform(1740, H); hgt = r.uniform(30, 90)
            nd.line([(x, y), (x + r.uniform(-14, 14), y - hgt)], fill=(36, 30, 24, 255), width=3)
        self.bank = nb
        self.path_y = 1640
        fg = Image.new("L", (WW, H), 0); gd = ImageDraw.Draw(fg)
        for k in range(30):
            x = r.choice([r.uniform(-40, 220), r.uniform(WW - 300, WW)])
            gd.line([(x, H + 10), (x + r.uniform(-60, 60), r.uniform(1300, 1700))], fill=255, width=int(r.uniform(8, 18)))
        self.fg = colorize(fg, (8, 2, 6)).filter(ImageFilter.GaussianBlur(9))

    def frame(self, t, cam=0.0, water_extras=None, bank_extras=None, fogk=0.35, temple_glow=1.0):
        o = lambda par: int(-300 - cam * par)
        img = self.sky.copy()
        img.alpha_composite(self.far, (o(0.12), 0))
        img.alpha_composite(self.temple, (o(0.12), 0))
        a = to_arr(img)
        for lx, ly in self.temple_lamps:
            x = lx + o(0.12)
            if -30 < x < W + 30:
                add_glow(a, gsp(26, (255, 170, 90)), x, ly, 0.8 * temple_glow)
        img = to_img(a)
        fog(img, t, fogk, 820, 1000, speed=8, col=(140, 50, 60))
        img.alpha_composite(self.palms, (o(0.3), 0))
        img.alpha_composite(self.houses, (o(0.3), 0))
        a = to_arr(img)
        for lx, ly in self.lit:
            x = lx + o(0.3)
            if -40 < x < W + 40:
                add_glow(a, gsp(50, (255, 140, 70)), x, ly, 0.5)
        y0, y1 = self.wy
        a[y0:y1] = self.water
        for lx, ly in self.lit:                                                        # window reflections
            x = int(lx + o(0.3))
            for j in range(6):
                yy = y0 + 8 + j * 16
                x0 = x - 6 + int(6 * math.sin(t * 2 + j))
                if 0 < x0 < W - 12:
                    a[yy:yy + 4, x0:x0 + 12] += np.array([120, 60, 30], np.float32) * (1 - j / 6)
        mx = 700
        for j in range(28):                                                            # the moon road
            yy = y0 + 6 + j * 15
            wd = 30 + j * 10 + 20 * math.sin(t * 2 + j)
            x0 = int(mx - wd / 2 + 12 * math.sin(t * 1.3 + j * 0.7)); x1 = int(mx + wd / 2)
            a[yy:yy + 4, max(0, x0):max(0, min(W, x1))] = np.array([190, 70, 60], np.float32) * (1 - j / 32)
        img = to_img(a)
        img.alpha_composite(self.pads, (o(0.7), int(3 * math.sin(t * 1.2))))
        for fn in (water_extras or []):
            img = fn(img, t, o(0.7) + 300) or img
        fog(img, t, fogk * 0.6, 1200, 1450, speed=14, col=(120, 40, 50), off=200)
        img.alpha_composite(self.bank, (o(1.0), 0))
        for fn in (bank_extras or []):
            img = fn(img, t, o(1.0) + 300) or img
        img.alpha_composite(self.fg, (o(1.5), 0))
        bokeh_particles(img, 12, 171, t, color=(255, 200, 140), size=(2, 6), blur=(0, 3), area=(0, 600, W, 1600), drift=(6, -3))
        return img


_KL = None


def klong():
    global _KL
    if _KL is None:
        _KL = Klong()
    return _KL


class House:
    """Nak and Mak's teak house as a cutaway, front view: a steep gable roof with curled ngao finials and a tall horn,
    panelled fa pakon walls with a lamp-lit door, the open porch (chan) on the right with a clay mortar and an oil lamp
    on a post, and in the dark underneath: the stilts, two big glazed water jars, a ladder, a puddle. Lamp light leaks
    down through the plank gaps. The plank gap the arm comes through is at self.gap; the lime lands at self.lime."""
    def __init__(self):
        r = np.random.default_rng(172)
        self.floor = 900; self.ground = 1600
        a = moon_sky((880, 300), 80, top=(3, 1, 6), mid=(30, 8, 24), bot=(70, 20, 30), ym=0.55)
        img = to_img(a)
        bm = Image.new("L", (W, H), 0); bd = ImageDraw.Draw(bm)
        for k in range(4):
            sugar_palm(bd, r.uniform(0, W), 1300, r.uniform(500, 800), 1, r)
        for k in range(30):
            x = r.uniform(0, W); rr = r.uniform(40, 90)
            bd.ellipse([x - rr, 1150 - rr, x + rr, 1320], fill=255)
        img.alpha_composite(colorize(bm.filter(ImageFilter.GaussianBlur(2)), (22, 6, 14)))
        d = ImageDraw.Draw(img)
        d.rectangle([0, self.ground - 40, W, H], fill=(30, 18, 18, 255))                       # earth
        for k in range(60):
            x = r.uniform(0, W); y = r.uniform(self.ground - 30, H)
            d.ellipse([x - 30, y - 5, x + 30, y + 5], fill=(40, 24, 22, 255))
        d.ellipse([540, self.ground + 40, 900, self.ground + 90], fill=(40, 20, 26, 255))      # puddle

        def posts(dd, s):
            for x in (170, 330, 490, 650, 810, 950):
                dd.polygon(P_((x - 20, self.floor), (x + 20, self.floor), (x + 24, self.ground + 10), (x - 24, self.ground + 10), s=s), fill=255)

        def beam(dd, s):
            dd.rectangle([100 * s, self.floor * s, 990 * s, (self.floor + 44) * s], fill=255)

        def wall(dd, s):
            dd.rectangle([130 * s, 540 * s, 610 * s, self.floor * s], fill=255)

        def roof(dd, s):
            dd.polygon(P_((80, 560), (660, 560), (370, 120), s=s), fill=255)

        def jars(dd, s):
            for x, sc in ((250, 1.0), (560, 0.8)):
                dd.ellipse([(x - 90 * sc) * s, (self.ground - 220 * sc) * s, (x + 90 * sc) * s, (self.ground + 8) * s], fill=255)
                dd.rectangle([(x - 50 * sc) * s, (self.ground - 236 * sc) * s, (x + 50 * sc) * s, (self.ground - 196 * sc) * s], fill=255)

        def ladder(dd, s):
            for x in (880, 960):
                dd.line([(x * s, self.floor * s), ((x + 40) * s, (self.ground + 10) * s)], fill=255, width=int(14 * s))
            for k in range(8):
                y = self.floor + 50 + k * 85
                u = (y - self.floor) / (self.ground - self.floor)
                dd.line([((880 + 40 * u) * s, y * s), ((960 + 40 * u) * s, y * s)], fill=255, width=int(10 * s))

        def rail(dd, s):
            dd.rectangle([620 * s, 800 * s, 980 * s, 816 * s], fill=255)
            for x in range(630, 980, 34):
                dd.rectangle([x * s, 816 * s, (x + 10) * s, self.floor * s], fill=255)
            dd.rectangle([968 * s, 560 * s, 984 * s, self.floor * s], fill=255)                  # lamp post

        img.alpha_composite(shade(posts, (W, H), (64, 40, 30), 14))
        img.alpha_composite(shade(jars, (W, H), (120, 70, 44), 50, rim=(255, 120, 60)))
        jd = ImageDraw.Draw(img)
        for x, sc in ((250, 1.0), (560, 0.8)):                                                # glaze dragons = simple bands
            jd.arc([x - 80 * sc, self.ground - 180 * sc, x + 80 * sc, self.ground - 40 * sc], 200, 340, fill=(150, 110, 50, 255), width=5)
        img.alpha_composite(shade(ladder, (W, H), (90, 60, 40), 6))
        img.alpha_composite(shade(wall, (W, H), (92, 54, 36), 40))
        wd_ = ImageDraw.Draw(img)
        for x in range(130, 611, 80):                                                         # fa pakon panel frames
            wd_.line([(x, 540), (x, self.floor)], fill=(60, 34, 24, 255), width=8)
        for y in (620, 700, 780, 860):
            wd_.line([(130, y), (610, y)], fill=(60, 34, 24, 255), width=6)
        wd_.rectangle([300, 640, 430, self.floor], fill=(255, 170, 90, 255))                   # the lit doorway
        wd_.rectangle([300, 640, 430, self.floor], outline=(50, 28, 20, 255), width=8)
        self.door = (365, 770)
        img.alpha_composite(shade(roof, (W, H), (56, 26, 24), 60, rim=(255, 70, 50)))
        rd = ImageDraw.Draw(img)
        rd.line([(80, 560), (370, 120), (660, 560)], fill=(120, 70, 40, 255), width=14)        # bargeboards
        for ex, sg in ((80, -1), (660, 1)):
            rd.arc([ex - 26, 520, ex + 26, 572], 90 if sg > 0 else 0, 270 if sg > 0 else 180, fill=(120, 70, 40, 255), width=10)
        rd.line([(370, 120), (384, 60)], fill=(120, 70, 40, 255), width=10)
        for k in range(10):
            y = 160 + k * 40; hw = (y - 120) / 440 * 290
            rd.line([(370 - hw, y), (370 + hw, y)], fill=(40, 18, 16, 255), width=3)
        img.alpha_composite(shade(beam, (W, H), (100, 62, 40), 10))
        img.alpha_composite(shade(rail, (W, H), (100, 62, 40), 6))
        bd2 = ImageDraw.Draw(img)
        self.gap = (750, self.floor + 22)
        bd2.rectangle([742, self.floor, 758, self.floor + 44], fill=(6, 2, 2, 255))           # the plank gap
        for x in range(160, 990, 46):
            bd2.line([(x, self.floor + 2), (x, self.floor + 42)], fill=(50, 30, 20, 255), width=2)
        self.lamp = (976, 586)
        bd2.rectangle([958, 560, 994, 612], fill=(60, 40, 30, 255))
        self.mortar = (700, self.floor)
        self.lime = (790, self.ground + 4)
        base = to_arr(img)
        lm = light_map(W, H, 840, 760, 420, 0.0)[..., None] * np.array([1.0, 0.62, 0.36], np.float32)
        under = np.zeros((H, W, 1), np.float32); under[self.floor + 44:self.ground + 60] = 1
        self.base = base * (0.55 + 0.6 * lm) * (1 - 0.35 * under)
        self.slits = list(range(180, 990, 46))

    def mortar_img(self, img, pest=0.0):
        d = ImageDraw.Draw(img)
        x, y = self.mortar
        d.polygon([(x - 46, y - 70), (x + 46, y - 70), (x + 30, y), (x - 30, y)], fill=(130, 70, 44, 255), outline=(40, 20, 14, 255))
        d.ellipse([x - 48, y - 80, x + 48, y - 60], fill=(60, 30, 20, 255))
        py = y - 140 - 60 * pest
        d.line([(x + 6, py), (x - 4, py + 110)], fill=(170, 130, 90, 255), width=14)
        return img

    def frame(self, t, lamp=1.0, extras=None, porch=None, wall_fx=None, under_light=1.0):
        a = self.base.copy()
        fl = lamp * (0.86 + 0.14 * (math.sin(t * 19) > -0.8))
        add_glow(a, gsp(340, (255, 140, 70)), self.lamp[0], self.lamp[1], 0.5 * fl)
        add_glow(a, gsp(26, (255, 230, 170)), self.lamp[0], self.lamp[1], 1.0 * fl)
        add_glow(a, gsp(160, (255, 150, 80)), self.door[0], self.door[1], 0.35 * fl)
        for x in self.slits:                                                               # light leaking down
            a[self.floor + 46:self.floor + 300, x - 1:x + 2] += np.linspace(60, 0, 254)[:, None, None] * np.array([1, .6, .3], np.float32) * fl * under_light
        img = to_img(a)
        for fn in (wall_fx or []):
            img = fn(img, t) or img
        for fn in (porch or []):
            img = fn(img, t) or img
        fog(img, t, 0.3, 1300, 1700, speed=12, col=(120, 40, 50))
        for fn in (extras or []):
            img = fn(img, t) or img
        bokeh_particles(img, 10, 172, t, color=(255, 190, 120), size=(2, 5), blur=(0, 2), area=(0, 400, W, 1600), drift=(4, -5))
        return img


_HS = None


def house():
    global _HS
    if _HS is None:
        _HS = House()
    return _HS


def nat_leaf(d, x, y, ln, wd, ang, s=1, teeth=7):
    """An oblong, toothed nat (Blumea) leaf."""
    pts = []
    for side in (1, -1):
        rng_ = range(0, teeth * 2 + 1) if side == 1 else range(teeth * 2, -1, -1)
        for i in rng_:
            u = i / (teeth * 2)
            ww = wd * math.sin(math.pi * u) * (1.0 + (0.12 if i % 2 else 0.0))
            px, py = u * ln, side * ww / 2
            c, s_ = math.cos(ang), math.sin(ang)
            pts.append(((x + px * c - py * s_) * s, (y + px * s_ + py * c) * s))
    d.polygon(pts, fill=255)


class NatBush:
    """POV from inside a bush of nat leaves on the canal bank: big, oblong, toothed grey-green leaves frame the view
    (sharp ones + blurred ones in front), and through the gap: the dark bank, the canal and the moon."""
    def __init__(self):
        r = np.random.default_rng(173)
        a = moon_sky((760, 360), 70, top=(3, 1, 6), mid=(26, 6, 20), bot=(60, 18, 28), ym=0.5)
        a[980:1120] = vgrad((24, 6, 16), (14, 3, 10), (10, 2, 8), 0.5, W, 140)
        a[1120:] = vgrad((34, 20, 20), (30, 18, 18), (20, 10, 12), 0.5, W, H - 1120)
        for j in range(8):
            yy = 990 + j * 16; wd = 30 + j * 12
            a[yy:yy + 3, int(760 - wd / 2):int(760 + wd / 2)] = np.array([160, 60, 54], np.float32) * (1 - j / 9)
        img = to_img(a)
        tm = Image.new("L", (W, H), 0); td = ImageDraw.Draw(tm)
        for k in range(5):
            thai_house_mask(td, r.uniform(-50, 1000), 980, r.uniform(140, 200), 60, 100, posts=50)
        img.alpha_composite(colorize(tm.filter(ImageFilter.GaussianBlur(2.5)), (24, 8, 16)))
        self.bg = img
        sharp, front = [], []
        while len(sharp) + len(front) < 170:
            x, y = r.uniform(-150, W + 150), r.uniform(-150, H + 150)
            if ((x - 540) / 330) ** 2 + ((y - 1000) / 620) ** 2 < 1.0:
                continue
            ang = math.atan2(1000 - y, 540 - x) + r.uniform(-0.7, 0.7)
            ln = r.uniform(140, 250)
            (front if r.random() < 0.22 else sharp).append((x, y, ln, ang))

        def leaves(dd, s_):
            for x, y, ln, ang in sharp:
                nat_leaf(dd, x, y, ln, ln * 0.38, ang, s=s_)
        self.leaves = shade(leaves, (W, H), (74, 96, 76), 18, rim=(255, 70, 60))
        lv = ImageDraw.Draw(self.leaves)
        for x, y, ln, ang in sharp:                                       # midribs
            lv.line([(x, y), (x + math.cos(ang) * ln * .9, y + math.sin(ang) * ln * .9)], fill=(110, 130, 100, 200), width=3)
        fm = Image.new("L", (W, H), 0); fd = ImageDraw.Draw(fm)
        for x, y, ln, ang in front:
            nat_leaf(fd, x - math.cos(ang) * 80, y - math.sin(ang) * 80, ln * 1.5, ln * 0.55, ang)
        self.fgl = colorize(fm, (18, 28, 22)).filter(ImageFilter.GaussianBlur(10))

    def frame(self, t, extras=None, sway=1.0, part=0.0):
        img = self.bg.copy()
        fog(img, t, 0.3, 900, 1300, speed=10, col=(120, 40, 50))
        for fn in (extras or []):
            img = fn(img, t) or img
        dx = int(6 * sway * math.sin(t * 1.7)) - int(120 * part); dy = int(4 * sway * math.cos(t * 1.3))
        img.alpha_composite(self.leaves, (dx, dy))
        if part > 0:
            img.alpha_composite(self.leaves.transpose(Image.FLIP_LEFT_RIGHT).crop((0, 0, int(240 * part) + 1, H)), (W - int(240 * part) - 1, dy))
        img.alpha_composite(self.fgl, (int(10 * sway * math.sin(t * 1.1 + 1)), 0))
        return img


_NB = None


def natbush():
    global _NB
    if _NB is None:
        _NB = NatBush()
    return _NB


class TempleGate:
    """Wat Mahabut from the inside, looking out through the gate: a whitewashed wall with leaf-shaped merlons, the gate
    with a two-tier red-and-gold roof with chofa horns and two red lanterns, sema boundary stones on lotus pedestals,
    a gold threshold line on the stone floor; outside: the canal path, palms and the moon (or dawn)."""
    def __init__(self, dawn=False):
        r = np.random.default_rng(174 + int(dawn))
        self.dawn = dawn
        if dawn:
            a = vgrad((70, 60, 90), (190, 120, 120), (240, 180, 150), 0.6)
        else:
            a = moon_sky((560, 1000), 90, top=(3, 1, 6), mid=(30, 8, 24), bot=(90, 24, 34), ym=0.6)
        img = to_img(a)
        d = ImageDraw.Draw(img)
        out_col = (40, 26, 30) if dawn else (16, 6, 12)
        pm = Image.new("L", (W, H), 0); pd = ImageDraw.Draw(pm)
        for k in range(5):
            sugar_palm(pd, r.uniform(200, 900), 1300, r.uniform(300, 500), 1, r)
        img.alpha_composite(colorize(pm, out_col))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1280, W, 1500], fill=((60, 44, 44) if dawn else (26, 14, 16)) + (255,))
        d.rectangle([0, 1250, W, 1300], fill=((80, 70, 90) if dawn else (20, 6, 14)) + (255,))       # the canal
        self.gate = (340, 760, 740, 1500)
        wall_col = (196, 188, 178) if dawn else (120, 104, 104)

        def wall(dd, s):
            dd.rectangle([0, 720 * s, W * s, 1500 * s], fill=255)
            for x in range(0, W, 90):
                dd.polygon(P_((x + 10, 720), (x + 80, 720), (x + 80, 690), (x + 45, 640), (x + 10, 690), s=s), fill=255)

        def opening(dd, s):
            gx0, gy0, gx1, gy1 = self.gate
            dd.rectangle([gx0 * s, (gy0 + 100) * s, gx1 * s, gy1 * s], fill=255)
            dd.ellipse([gx0 * s, gy0 * s, gx1 * s, (gy0 + 200) * s], fill=255)

        wl = shade(wall, (W, H), wall_col, 30, rim=(255, 120, 90) if dawn else (255, 60, 50))
        om = D5.smooth_mask(opening, (W, H))
        wa = np.asarray(wl).copy(); wa[..., 3] = (wa[..., 3].astype(np.float32) * (1 - np.asarray(om, np.float32) / 255)).astype(np.uint8)
        img.alpha_composite(Image.fromarray(wa, "RGBA"))

        def roof(dd, s):
            for (wd, y0, y1) in ((620, 600, 700), (480, 520, 610)):
                dd.polygon(P_((540 - wd / 2, y1), (540 + wd / 2, y1), (540 + wd / 2 - 70, y0), (540 - wd / 2 + 70, y0), s=s), fill=255)
            dd.polygon(P_((480, 520), (600, 520), (540, 440), s=s), fill=255)

        def pillars(dd, s):
            for x in (300, 740):
                dd.rectangle([x * s, 700 * s, (x + 40) * s, 1500 * s], fill=255)
        img.alpha_composite(shade(pillars, (W, H), wall_col, 10))
        img.alpha_composite(shade(roof, (W, H), (150, 46, 30), 30, rim=(255, 120, 70)))
        rd = ImageDraw.Draw(img)
        gold = (214, 164, 70, 255)
        for (wd, y0, y1) in ((620, 600, 700), (480, 520, 610)):
            rd.line([(540 - wd / 2, y1), (540 - wd / 2 + 70, y0), (540 + wd / 2 - 70, y0), (540 + wd / 2, y1)], fill=gold, width=8)
            for sg in (-1, 1):                                                                       # chofa horns
                ex = 540 + sg * wd / 2
                rd.line([(ex, y1), (ex + sg * 20, y1 - 30), (ex + sg * 10, y1 - 56)], fill=gold, width=8)
        rd.line([(540, 440), (540, 380)], fill=gold, width=8)
        d2 = ImageDraw.Draw(img)                                                                     # courtyard floor
        fc = (150, 140, 134) if dawn else (54, 42, 44)
        d2.rectangle([0, 1500, W, H], fill=fc + (255,))
        for k in range(1, 9):
            y = 1500 + (k ** 1.6) * 14
            d2.line([(0, y), (W, y)], fill=tuple(int(c * .7) for c in fc) + (255,), width=3)
        for k in range(-6, 7):
            d2.line([(540 + k * 60, 1500), (540 + k * 260, H)], fill=tuple(int(c * .7) for c in fc) + (255,), width=3)
        d2.line([(340, 1502), (740, 1502)], fill=gold, width=8)                                     # the holy line
        self.line_y = 1502

        def sema(dd, s):
            for x in (150, 930):
                dd.polygon(P_((x - 60, 1640), (x + 60, 1640), (x + 44, 1690), (x - 44, 1690), s=s), fill=255)
                dd.polygon(P_((x - 40, 1640), (x + 40, 1640), (x + 46, 1500), (x, 1420), (x - 46, 1500), s=s), fill=255)
        img.alpha_composite(shade(sema, (W, H), (170, 160, 150) if dawn else (96, 86, 84), 20))
        self.lanterns = [(410, 740), (670, 740)]
        for x, y in self.lanterns:
            d2 = ImageDraw.Draw(img)
            d2.line([(x, 700), (x, y - 26)], fill=(40, 20, 20, 255), width=3)
            d2.ellipse([x - 22, y - 30, x + 22, y + 30], fill=(200, 40, 34, 255))
        base = to_arr(img)
        if not dawn:
            lm = light_map(W, H, 540, 900, 520, 0.0)[..., None] * np.array([1.0, .55, .4], np.float32)
            base = base * (0.6 + 0.5 * lm)
        self.base = base

    def frame(self, t, outside=None, inside=None, line_glow=0.0):
        a = self.base.copy()
        for x, y in self.lanterns:
            add_glow(a, gsp(90, (255, 90, 60)), x, y, (0.45 if not self.dawn else 0.2) * (0.9 + 0.1 * math.sin(t * 7 + x)))
        img = to_img(a)
        if outside:
            gx0, gy0, gx1, gy1 = self.gate
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            for fn in outside:
                lay = fn(lay, t) or lay
            m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
            md.rectangle([gx0, gy0 + 100, gx1, gy1 + 40], fill=255); md.ellipse([gx0, gy0, gx1, gy0 + 200], fill=255)
            la = np.asarray(lay).copy(); la[..., 3] = (la[..., 3].astype(np.float32) * np.asarray(m, np.float32) / 255).astype(np.uint8)
            img.alpha_composite(Image.fromarray(la, "RGBA"))
        if line_glow > 0:
            img = glow_on(img, gsp(220, (255, 200, 110), 1.4), 540, self.line_y, line_glow)
        fog(img, t, 0.25 if not self.dawn else 0.15, 1350, 1700, speed=10, col=(140, 60, 60) if not self.dawn else (220, 190, 180))
        for fn in (inside or []):
            img = fn(img, t) or img
        bokeh_particles(img, 10, 174, t, color=(255, 200, 140), size=(2, 5), blur=(0, 2), area=(0, 500, W, 1700), drift=(4, -5))
        return img


_TG = {}


def temple(dawn=False):
    if dawn not in _TG:
        _TG[dawn] = TempleGate(dawn)
    return _TG[dawn]


class Shrine:
    """Mae Nak's shrine today: a Bo tree trunk wrapped in pink, yellow and green cloth, rows of offered Thai dresses on
    racks on both sides, garlands, small toys for her baby, candles and incense smoke."""
    def __init__(self):
        r = np.random.default_rng(175)
        a = vgrad((10, 4, 8), (40, 16, 18), (30, 14, 14), 0.6)
        img = to_img(a); d = ImageDraw.Draw(img)

        def trunk(dd, s):
            dd.polygon(P_((420, 1500), (660, 1500), (610, 900), (600, 300), (480, 300), (470, 900), s=s), fill=255)
        img.alpha_composite(shade(trunk, (W, H), (80, 60, 50), 60))
        d = ImageDraw.Draw(img)
        cols = [(220, 110, 150), (230, 190, 70), (90, 160, 90), (200, 70, 70), (230, 140, 60)]
        for k in range(14):
            y = 640 + k * 50
            d.polygon([(470, y), (610, y - 10), (612, y + 26), (468, y + 36)], fill=cols[k % 5] + (255,))
        for side in (-1, 1):
            for row in range(3):
                y0 = 520 + row * 330
                d.line([(540 + side * 120, y0), (540 + side * 520, y0)], fill=(140, 110, 70, 255), width=6)
                for k in range(5):
                    x = 540 + side * (170 + k * 78)
                    c = cols[(k + row) % 5]; c = tuple(int(v * 0.8) for v in c)
                    d.line([(x, y0), (x, y0 + 20)], fill=(120, 100, 80, 255), width=3)
                    d.polygon([(x - 26, y0 + 20), (x + 26, y0 + 20), (x + 40, y0 + 280), (x - 40, y0 + 280)], fill=c + (255,))
                    d.rectangle([x - 26, y0 + 70, x + 26, y0 + 84], fill=(220, 180, 90, 255))
        d.rectangle([0, 1500, W, H], fill=(40, 24, 20, 255))
        d.rectangle([260, 1480, 820, 1560], fill=(90, 50, 30, 255))                          # offering table
        for k in range(6):                                                                   # toys + garlands
            x = 300 + k * 90
            d.ellipse([x - 22, 1430, x + 22, 1480], fill=cols[k % 5] + (255,))
            d.ellipse([x - 12, 1400, x + 12, 1430], fill=(230, 220, 200, 255))
        for k in range(30):
            x = 280 + k * 18
            d.ellipse([x - 6, 1560 + 8 * math.sin(k), x + 6, 1572 + 8 * math.sin(k)], fill=(250, 240, 220, 255))
        self.candles = [(300 + k * 120, 1470) for k in range(5)]
        for x, y in self.candles:
            d.rectangle([x - 6, y - 50, x + 6, y], fill=(240, 230, 200, 255))
        self.base = to_arr(img)

    def frame(self, t, extras=None):
        a = self.base.copy()
        for x, y in self.candles:
            add_glow(a, gsp(80, (255, 160, 80)), x, y - 60, 0.6 * (0.85 + 0.15 * math.sin(t * 9 + x)))
            add_glow(a, gsp(10, (255, 240, 200)), x, y - 58, 1.0)
        img = to_img(a)
        fog(img, t, 0.35, 300, 1500, speed=16, col=(200, 170, 160))
        for fn in (extras or []):
            img = fn(img, t) or img
        return img


_SH = None


def shrine():
    global _SH
    if _SH is None:
        _SH = Shrine()
    return _SH
