"""Ep20 Malaysia / the Toyol - art: the world, the people and the spirit (2.1D flat21 style).
New world: a kampung kedai runcit (family sundry shop) in Kelantan at ten at night - a wooden shopfront under a zinc
roof with a half-rolled shutter, a hand-painted KEDAI RUNCIT sign, coconut palms and a red moon, a big new concrete
house across the road with one lit window and a jar on the sill; inside: dark teal plank walls, shelves of tins and
packets, hanging snack strips, a flickering fluorescent tube, a red-glowing AIS KRIM freezer, a round convex shop
mirror high in the corner, and the counter with glass sweet jars, an old wooden cash drawer and Tok Wan's bowl of green
beans; the dark under the counter (a hiding POV), and the little sister's room seen from under her bed. Hero: Aiman
(teal t-shirt with a white band, black track pants, selipar). Tok Wan (dusky-rose baju kurung, white tudung).
Spirit: the toyol - a small bald child spirit with grey-green skin, big pointed ears, red eyes, a thin body with a round
belly, long fingers, a dark loincloth, a too-wide grin with small pointed teeth (no gore)."""
import os, sys, math
os.environ["STYLE"] = "flat21"
_EP = os.path.dirname(os.path.abspath(__file__)); _TK = os.path.join(_EP, "..", "..", "toolkit")
sys.path.insert(0, _TK)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
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


def colorize(mask, col):
    lay = Image.new("RGBA", mask.size, tuple(col) + (0,)); lay.putalpha(mask)
    return lay



def put_sprite(img, spr, x, y, fx, fy, alpha=1.0):
    if alpha < 1:
        spr = with_alpha(spr, alpha)
    img.alpha_composite(spr, (int(x - fx), int(y - fy)))
    return img


def sc_spr(spr, sc):
    return spr.resize((max(1, int(spr.width * sc)), max(1, int(spr.height * sc))), Image.LANCZOS)


# ============================================================ palette
ASKIN = (176, 128, 96)         # Aiman
ATEE = (36, 92, 108)           # teal t-shirt
ABAND = (226, 222, 210)        # white chest band
APANT = (22, 22, 28)
HAIR = (12, 10, 12)
WSKIN = (170, 124, 98)         # Tok Wan
KURUNG = (150, 82, 92)         # dusky rose baju kurung
TUDUNG = (226, 222, 214)
TSKIN = (118, 138, 108)        # the toyol: grey-green
TSKIN2 = (84, 102, 78)
LOIN = (52, 34, 26)
WOOD = (74, 46, 30)
TEAL = (24, 58, 60)

# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """Malaysia (Jalur Gemilang): 14 red and white stripes (red on top), a dark blue canton over the top 8 stripes and
    the hoist half, with a yellow crescent and a yellow 14-point star - 1:2."""
    global _FLAG
    if _FLAG is None:
        s = 4
        w, h = 400 * s, 200 * s
        im = Image.new("RGBA", (w, h), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
        sh = h / 14
        for k in range(14):
            if k % 2 == 0:
                d.rectangle([0, k * sh, w, (k + 1) * sh], fill=(204, 0, 1, 255))
        cw, ch = w / 2, 8 * sh
        d.rectangle([0, 0, cw, ch], fill=(1, 0, 102, 255))
        cx, cy, R = cw * 0.36, ch / 2, ch * 0.40
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 204, 0, 255))
        d.ellipse([cx - R * 0.80 + R * 0.26, cy - R * 0.80, cx + R * 0.80 + R * 0.26, cy + R * 0.80], fill=(1, 0, 102, 255))
        sx, sy, ro, ri = cw * 0.69, ch / 2, ch * 0.33, ch * 0.14
        pts = []
        for k in range(28):
            a = -math.pi / 2 + k * math.pi / 14
            rr = ro if k % 2 == 0 else ri
            pts.append((sx + math.cos(a) * rr, sy + math.sin(a) * rr))
        d.polygon(pts, fill=(255, 204, 0, 255))
        _FLAG = im.resize((300, 150), Image.LANCZOS)
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
        fw = flag_wave(t, 210)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 48))


def shop_ui(now, till, t, k=1.0, danger=False):
    """The ticking clock: time NOW vs ABAH BACK 23:00 + the money in the TILL (it halves)."""
    f1 = font(INTER_SB, 40); f2 = font(INTER_M, 24); f3 = font(INTER_SB, 38)
    w, h = 800, 112
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    blink = (math.sin(t * 10) > -0.2) if danger else True
    oc = (255, 50, 40) if danger else (150, 210, 170)
    A = int(255 * k)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 32, fill=(0, 0, 0, int(190 * k)), outline=oc + (int(220 * k),), width=3)
    cx, cy = 58, 56                                                     # a clock face
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], outline=(240, 236, 226, A), width=4)
    ang = t * 1.5
    d.line([(cx, cy), (cx + 20 * math.sin(ang), cy - 20 * math.cos(ang))], fill=(255, 80, 60, A), width=4)
    d.line([(cx, cy), (cx + 12, cy + 4)], fill=(240, 236, 226, A), width=4)
    d.text((110, 32), "NOW", font=f2, fill=(170, 220, 190, A), anchor="lm")
    d.text((110, 76), now, font=f1, fill=(248, 240, 228, A), anchor="lm")
    d.text((250, 32), "ABAH BACK", font=f2, fill=(170, 220, 190, A), anchor="lm")
    d.text((250, 76), "23:00", font=f3, fill=(200, 200, 190, A), anchor="lm")
    d.line([(410, 22), (410, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    for i in range(3):                                                  # a little coin stack
        d.ellipse([440, 72 - i * 14, 492, 92 - i * 14], fill=(220, 180, 70, A), outline=(120, 90, 30, A), width=2)
    d.text((620, 32), "TILL", font=f2, fill=(170, 220, 190, A), anchor="mm")
    if blink:
        d.text((620, 76), till, font=f3, fill=((255, 70, 55) if danger else (255, 240, 228)) + (A,), anchor="mm")
    return im


def put_ui(out, now, till, t, k=1.0, y=200, danger=False):
    if k <= 0.01:
        return
    ui = shop_ui(now, till, t, k, danger)
    out.alpha_composite(ui, (int(W / 2 - ui.width / 2), int(y)))


def clock_at(m0, m1, u):
    """minutes after 22:00, interpolated -> '22:mm'."""
    m = int(m0 + (m1 - m0) * max(0.0, min(1.0, u)))
    return f"{22 + m // 60}:{m % 60:02d}"


def big_text(img, s, x, y, k, red=False, sc=1.0):
    """A big popping number/word (the counting)."""
    if k <= 0:
        return img
    f = font(INTER_SB, int(104 * sc))
    col = (255, 60, 50) if red else (235, 255, 225)
    ti = text_img(s, f, fill=col + (255,), glow=(200, 20, 20, 220) if red else (0, 0, 0, 220), pad=20)
    s2 = 0.6 + 0.4 * ease(min(1, k * 1.5))
    ti = ti.resize((max(1, int(ti.width * s2)), max(1, int(ti.height * s2))), Image.LANCZOS)
    img.alpha_composite(with_alpha(ti, min(1, k)), (int(x - ti.width / 2), int(y - ti.height / 2)))
    return img


# ============================================================ Aiman (front view)
_AF = {}


def aiman(pose="stand", look=0.0, gasp=0.0, scale=1.0, phase=0.0, dark=0.0):
    """Aiman seen from the front. pose: "stand", "count" (notes held at the chest, eyes down), "throw" (right arm flung up
    and out), "crouch" (knees up under the counter, hand over mouth when gasp<0), "hold" (both arms up holding something
    in front of his face - the mirror is drawn by the scene), "run". look: eyes up (+) / sideways (-).
    Returns (RGBA, feet_x, feet_y)."""
    q = (pose, round(look, 1), round(gasp, 1), round(scale, 2), round(phase * 12) % 12)
    if q in _AF:
        return _AF[q]
    w, h = 560, 980
    cx = w / 2
    ph = 2 * math.pi * q[4] / 12
    run = pose == "run"
    sw = math.sin(ph) if run else 0.0
    sit = pose == "crouch"
    hy = 150 if not sit else 340
    by = 214 if not sit else 404

    def legs(d, s):
        if sit:
            for sg in (-1, 1):
                d.line([((cx + sg * 60) * s, 650 * s), ((cx + sg * 58) * s, 880 * s)], fill=255, width=int(58 * s))
                d.ellipse([(cx + sg * 60 - 46) * s, 600 * s, (cx + sg * 60 + 46) * s, 700 * s], fill=255)
        else:
            for sg in (-1, 1):
                up = max(0, sg * sw) * 90
                d.line([((cx + sg * 34) * s, 500 * s), ((cx + sg * 38) * s, (700 - up * .6) * s), ((cx + sg * 34) * s, (890 - up) * s)], fill=255, width=int(56 * s), joint="curve")

    def feet(d, s):
        for sg in (-1, 1):
            x, y = (cx + sg * 52, 894) if sit else (cx + sg * 34, 894 - max(0, sg * sw) * 90)
            d.ellipse([(x - 36) * s, (y - 14) * s, (x + 36) * s, (y + 16) * s], fill=255)

    def body(d, s):
        bot = 520 if not sit else 700
        d.polygon(P_((cx - 100, by), (cx + 100, by), (cx + 92, by + 170), (cx + 98, bot), (cx - 98, bot), (cx - 92, by + 170), s=s), fill=255)
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 82 - 32) * s, (by - 12) * s, (cx + sg * 82 + 32) * s, (by + 56) * s], fill=255)

    arms = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 96, by + 24
        if pose == "count":
            arms[sg] = ((sx, sy), (cx + sg * 118, sy + 150), (cx + sg * 30, sy + 130))
        elif pose == "hold":
            arms[sg] = ((sx, sy), (cx + sg * 150, sy - 10), (cx + sg * 110, hy - 40))
        elif pose == "throw" and sg == 1:
            arms[sg] = ((sx, sy), (sx + 110, sy - 90), (sx + 230, sy - 200))
        elif pose == "crouch":
            arms[sg] = ((sx, sy), (cx + sg * 126, sy + 150), (cx + sg * 30, sy + 236)) if (gasp >= 0 or sg == -1) else ((sx, sy), (cx + 104, sy + 60), (cx + 14, hy + 42))
        elif run:
            a = -sg * sw * 0.9
            arms[sg] = ((sx, sy), (sx + sg * 20 + math.sin(a) * 60, sy + 100), (sx + sg * 10 + math.sin(a) * 110, sy + 40))
        else:
            arms[sg] = ((sx, sy), (sx + sg * 18, sy + 136), (sx + sg * 16, sy + 262))

    def armf(d, s):
        for sg in (-1, 1):
            d.line([(x * s, y * s) for x, y in arms[sg]], fill=255, width=int(40 * s), joint="curve")

    def sleeves(d, s):
        for sg in (-1, 1):
            (x0, y0), (x1, y1) = arms[sg][0], arms[sg][1]
            d.line([(x0 * s, y0 * s), ((x0 + (x1 - x0) * .45) * s, (y0 + (y1 - y0) * .45) * s)], fill=255, width=int(56 * s))

    def hands(d, s):
        for sg in (-1, 1):
            x, y = arms[sg][2]
            d.ellipse([(x - 19) * s, (y - 19) * s, (x + 19) * s, (y + 19) * s], fill=255)

    def head(d, s):
        d.rectangle([(cx - 24) * s, (hy + 20) * s, (cx + 24) * s, (by + 10) * s], fill=255)
        d.ellipse([(cx - 58) * s, (hy - 76) * s, (cx + 58) * s, (hy + 72) * s], fill=255)
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 58 - 12) * s, (hy - 6) * s, (cx + sg * 58 + 12) * s, (hy + 26) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 62) * s, (hy - 88) * s, (cx + 62) * s, (hy + 20) * s], 180, 360, fill=255)
        d.polygon(P_((cx - 62, hy - 34), (cx - 60, hy - 4), (cx - 36, hy - 40), (cx - 10, hy - 30), (cx + 20, hy - 44), (cx + 60, hy - 8), (cx + 62, hy - 34), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if not sit:
        img.alpha_composite(shade(legs, (w, h), APANT, 22, rim_strength=1.1))
        img.alpha_composite(shade(feet, (w, h), (40, 70, 120), 10))
    front_arms = pose in ("count", "crouch", "hold")
    if not front_arms:
        img.alpha_composite(shade(armf, (w, h), ASKIN, 14))
    img.alpha_composite(shade(body, (w, h), ATEE, 46, rim_strength=1.1))
    bd = ImageDraw.Draw(img)
    bb = by + 110
    bd.polygon([(cx - 95, bb), (cx + 95, bb), (cx + 94, bb + 30), (cx - 94, bb + 30)], fill=ABAND + (255,))     # white band
    bd.ellipse([cx - 30, by - 8, cx + 30, by + 22], fill=tuple(int(c * .6) for c in ATEE) + (255,))              # collar
    img.alpha_composite(shade(sleeves, (w, h), ATEE, 14))
    if sit:
        img.alpha_composite(shade(legs, (w, h), APANT, 22, rim_strength=1.1))
        img.alpha_composite(shade(feet, (w, h), (40, 70, 120), 10))
    img.alpha_composite(shade(head, (w, h), ASKIN, 28))
    img.alpha_composite(shade(hair, (w, h), HAIR, 12, rim_strength=1.1))
    d = ImageDraw.Draw(img)
    lk = look
    for sg in (-1, 1):
        ex_, ey_ = cx + sg * 23, hy + 6 - (8 if lk > 0 else 0) + (10 if pose == "count" else 0)
        r_ = 11 + 4 * max(0, gasp)
        d.ellipse([ex_ - r_, ey_ - r_ * .8, ex_ + r_, ey_ + r_ * .8], fill=(240, 236, 230, 255))
        px = ex_ + (-5 if lk < 0 else 0)
        py = ey_ - 5 * max(0, lk) + (4 if pose == "count" else 0)
        d.ellipse([px - 5, py - 6, px + 5, py + 4], fill=(15, 10, 10, 255))
        d.line([(ex_ - 15, ey_ - 21 - 6 * max(0, gasp)), (ex_ + 15, ey_ - 19 - 3 * sg - 6 * max(0, gasp))], fill=(20, 12, 10, 255), width=6)
    if gasp > 0.3:
        d.ellipse([cx - 12, hy + 40, cx + 12, hy + 40 + 28 * gasp], fill=(60, 18, 18, 255))
    elif gasp >= 0:
        d.line([(cx - 13, hy + 46), (cx + 13, hy + 46)], fill=(90, 40, 34, 255), width=4)
    if front_arms:
        img.alpha_composite(shade(armf, (w, h), ASKIN, 14))
        img.alpha_composite(shade(sleeves, (w, h), ATEE, 14))
    if pose == "count":                                              # a fan of ringgit notes in his hands
        d = ImageDraw.Draw(img)
        for i, col in enumerate(((190, 80, 90), (90, 120, 200), (200, 110, 60), (190, 80, 90))):
            nx = cx - 70 + i * 26
            d.polygon([(nx, by + 110), (nx + 110, by + 96 + i * 6), (nx + 116, by + 160 + i * 6), (nx + 6, by + 176)], fill=col + (255,), outline=(30, 20, 20, 255))
    img.alpha_composite(shade(hands, (w, h), ASKIN, 8))
    if dark > 0:
        img = tint(img, (1 - dark, 1 - dark * 1.05, 1 - dark * 1.05))
    if scale != 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    out = (img, cx * scale, 900 * scale)
    _AF[q] = out
    return out


def put_aiman(img, x, y, sc, pose="stand", alpha=1.0, **kw):
    spr, fx, fy = aiman(pose, **kw)
    return put_sprite(img, sc_spr(spr, sc), x, y, fx * sc, fy * sc, alpha)


# ============================================================ Tok Wan
_TW = None


def tokwan():
    """Tok Wan from the front, slightly stooped: white tudung over head and shoulders, dusky-rose baju kurung to the
    knees over a dark batik sarong, kind face, small round glasses. Returns (RGBA, feet_x, feet_y)."""
    global _TW
    if _TW is None:
        w, h = 520, 940
        cx, hy = 260, 170

        def sarong(d, s):
            d.polygon(P_((cx - 100, 560), (cx + 100, 560), (cx + 112, 900), (cx - 112, 900), s=s), fill=255)

        def kurung(d, s):
            d.polygon(P_((cx - 96, 250), (cx + 96, 250), (cx + 130, 650), (cx - 130, 650), s=s), fill=255)
            for sg in (-1, 1):
                d.line([((cx + sg * 100) * s, 280 * s), ((cx + sg * 130) * s, 460 * s), ((cx + sg * 70) * s, 520 * s)], fill=255, width=int(46 * s), joint="curve")

        def tud(d, s):
            d.ellipse([(cx - 82) * s, (hy - 96) * s, (cx + 82) * s, (hy + 90) * s], fill=255)
            d.polygon(P_((cx - 80, hy + 10), (cx + 80, hy + 10), (cx + 128, 360), (cx, 400), (cx - 128, 360), s=s), fill=255)

        def face(d, s):
            d.ellipse([(cx - 52) * s, (hy - 54) * s, (cx + 52) * s, (hy + 70) * s], fill=255)

        def hands(d, s):
            for sg in (-1, 1):
                d.ellipse([(cx + sg * 70 - 20) * s, 500 * s, (cx + sg * 70 + 20) * s, 540 * s], fill=255)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        img.alpha_composite(shade(sarong, (w, h), (60, 40, 50), 30))
        sd = ImageDraw.Draw(img)
        for y in range(600, 900, 46):                                   # batik lines
            sd.line([(cx - 104, y), (cx + 108, y + 10)], fill=(120, 80, 50, 255), width=5)
        img.alpha_composite(shade(kurung, (w, h), KURUNG, 46, rim_strength=1.0))
        img.alpha_composite(shade(tud, (w, h), TUDUNG, 40, rim_strength=0.8))
        img.alpha_composite(shade(face, (w, h), WSKIN, 30))
        d = ImageDraw.Draw(img)
        for sg in (-1, 1):
            d.ellipse([cx + sg * 22 - 15, hy + 2, cx + sg * 22 + 15, hy + 28], outline=(60, 50, 40, 255), width=3)
            d.ellipse([cx + sg * 22 - 4, hy + 11, cx + sg * 22 + 4, hy + 19], fill=(20, 14, 12, 255))
        d.line([(cx - 8, hy + 15), (cx + 8, hy + 15)], fill=(60, 50, 40, 255), width=3)
        d.arc([cx - 18, hy + 34, cx + 18, hy + 52], 20, 160, fill=(100, 50, 44, 255), width=4)
        img.alpha_composite(shade(hands, (w, h), WSKIN, 8))
        _TW = (img, cx, 900)
    return _TW


# ============================================================ the toyol
_TY = {}


def toyol(pose="squat", phase=0.0, tilt=0.0, grin=0.0, reach=0.0):
    """The toyol: a small bald child spirit (about 45% of Aiman's height) with a big egg-shaped head, huge pointed ears,
    grey-green skin, a thin body with a round belly, long thin fingers, a dark loincloth. pose: "squat" (crouched,
    knees up, hands down in front - counting), "stand" (front, arms hanging, too still), "run" (scurrying, side-on to the
    right, stop-motion phase), "crawl". tilt: head tilt (deg). grin 0..1: a too-wide grin with small pointed teeth.
    reach 0..1: the right hand reaching forward/down. Returns (RGBA, feet_x, feet_y, [eye points])."""
    key = (pose, round(tilt / 5) * 5, round(phase * 8) % 8, round(grin, 1), round(reach, 1))
    if key in _TY:
        return _TY[key]
    w, h = 520, 620
    cx = 260
    ph = 2 * math.pi * key[2] / 8
    squat = pose == "squat"; run = pose == "run"
    hy = 190 if not squat else 250              # head centre
    hr = 104                                     # head radius (big head)
    by0 = hy + 92                                # neck bottom

    def legs(d, s):
        if squat:
            for sg in (-1, 1):
                d.line([((cx + sg * 30) * s, 470 * s), ((cx + sg * 78) * s, 430 * s), ((cx + sg * 62) * s, 580 * s)], fill=255, width=int(30 * s), joint="curve")
        elif run:
            for sg in (-1, 1):
                a = sg * math.sin(ph) * 0.8
                d.line([(cx * s, 440 * s), ((cx + 70 * math.sin(a)) * s, 510 * s), ((cx + 110 * math.sin(a) - 10) * s, 590 * s)], fill=255, width=int(26 * s), joint="curve")
        else:
            for sg in (-1, 1):
                d.line([((cx + sg * 26) * s, 440 * s), ((cx + sg * 30) * s, 520 * s), ((cx + sg * 26) * s, 586 * s)], fill=255, width=int(28 * s), joint="curve")

    def feet(d, s):
        pts = []
        if squat:
            pts = [(cx - 62, 590, -1), (cx + 62, 590, 1)]
        elif run:
            for sg in (-1, 1):
                a = sg * math.sin(ph) * 0.8
                pts.append((cx + 110 * math.sin(a) - 4, 596, 1))
        else:
            pts = [(cx - 26, 596, -1), (cx + 26, 596, 1)]
        for x, y, sg in pts:
            d.ellipse([(x - 26 + 8 * sg) * s, (y - 12) * s, (x + 26 + 8 * sg) * s, (y + 10) * s], fill=255)

    def body(d, s):
        top, bot = by0, (480 if squat else 450)
        d.polygon(P_((cx - 40, top), (cx + 40, top), (cx + 56, top + 80), (cx + 62, bot - 40), (cx + 44, bot), (cx - 44, bot), (cx - 62, bot - 40), (cx - 56, top + 80), s=s), fill=255)
        d.ellipse([(cx - 66) * s, (top + 70) * s, (cx + 66) * s, (bot + 6) * s], fill=255)      # round belly

    arms = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 44, by0 + 16
        if squat:
            rk = reach if sg == 1 else 0.0
            arms[sg] = ((sx, sy), (cx + sg * 90, sy + 110), (cx + sg * 40 + rk * 60, sy + 200 + rk * 40))
        elif run:
            a = -sg * math.sin(ph) * 0.9
            arms[sg] = ((sx, sy), (sx + math.sin(a) * 70, sy + 90), (sx + math.sin(a) * 120 + 30, sy + 60))
        else:
            rk = reach if sg == 1 else 0.0
            arms[sg] = ((sx, sy), (cx + sg * 70 + rk * 40, sy + 120 - rk * 40), (cx + sg * 74 + rk * 120, sy + 250 - rk * 150))

    def armf(d, s):
        for sg in (-1, 1):
            d.line([(x * s, y * s) for x, y in arms[sg]], fill=255, width=int(20 * s), joint="curve")

    def hands(d, s):
        for sg in (-1, 1):
            (x1, y1), (x, y) = arms[sg][1], arms[sg][2]
            ang = math.atan2(y - y1, x - x1)
            d.ellipse([(x - 14) * s, (y - 14) * s, (x + 14) * s, (y + 14) * s], fill=255)
            for f in range(4):                                       # long thin fingers
                a = ang + (f - 1.5) * 0.32
                d.line([(x * s, y * s), ((x + math.cos(a) * 46) * s, (y + math.sin(a) * 46) * s)], fill=255, width=int(7 * s))

    def head(d, s):
        d.rectangle([(cx - 18) * s, (hy + 50) * s, (cx + 18) * s, (by0 + 10) * s], fill=255)
        d.ellipse([(cx - hr) * s, (hy - hr * 1.12) * s, (cx + hr) * s, (hy + hr * 0.9) * s], fill=255)
        for sg in (-1, 1):                                            # huge pointed ears
            d.polygon(P_((cx + sg * (hr - 18), hy - 30), (cx + sg * (hr + 92), hy - 96), (cx + sg * (hr + 40), hy + 4), (cx + sg * (hr - 8), hy + 30), s=s), fill=255)

    def loin(d, s):
        bot = 480 if squat else 450
        d.polygon(P_((cx - 50, bot - 34), (cx + 50, bot - 34), (cx + 30, bot + 34), (cx - 30, bot + 34), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), TSKIN, 12, rim=(255, 60, 40)))
    img.alpha_composite(shade(feet, (w, h), TSKIN2, 8))
    img.alpha_composite(shade(body, (w, h), TSKIN, 36, rim=(255, 60, 40), rim_strength=1.1))
    bd = ImageDraw.Draw(img)
    for k in range(3):                                                # ribs
        bd.arc([cx - 40, by0 + 34 + k * 18, cx + 40, by0 + 64 + k * 18], 200, 340, fill=TSKIN2 + (255,), width=3)
    img.alpha_composite(shade(loin, (w, h), LOIN, 10))
    img.alpha_composite(shade(armf, (w, h), TSKIN, 9, rim=(255, 60, 40)))
    img.alpha_composite(shade(hands, (w, h), TSKIN, 6))
    hd = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd.alpha_composite(shade(head, (w, h), TSKIN, 70, rim=(255, 60, 40), rim_strength=1.1))
    d = ImageDraw.Draw(hd)
    for sg in (-1, 1):                                                # dark inner ears + brow ridge + veins
        d.polygon([(cx + sg * (hr + 8), hy - 26), (cx + sg * (hr + 70), hy - 80), (cx + sg * (hr + 30), hy - 6)], fill=TSKIN2 + (255,))
        d.line([(cx + sg * 20, hy - 70), (cx + sg * 34, hy - 40), (cx + sg * 28, hy - 20)], fill=TSKIN2 + (255,), width=3)
    eyes = [(cx - 40, hy + 4), (cx + 40, hy + 4)]
    for ex_, ey_ in eyes:
        d.ellipse([ex_ - 38, ey_ - 30, ex_ + 36, ey_ + 30], fill=(52, 62, 48, 255))
        d.ellipse([ex_ - 28, ey_ - 18, ex_ + 28, ey_ + 20], fill=(10, 6, 6, 255))
        d.line([(ex_ - 30, ey_ - 22), (ex_ + 24, ey_ - 26 if ex_ < cx else ey_ - 18)], fill=TSKIN2 + (255,), width=6)
    d.polygon([(cx - 8, hy + 36), (cx + 8, hy + 36), (cx + 4, hy + 46), (cx - 4, hy + 46)], fill=TSKIN2 + (255,))
    if grin > 0.3:
        d.chord([cx - 70, hy + 30, cx + 70, hy + 100], 10, 170, fill=(24, 8, 8, 255))
        for k in range(9):                                            # small pointed teeth along the top
            x = cx - 56 + k * 14
            d.polygon([(x - 6, hy + 62), (x + 6, hy + 62), (x, hy + 76)], fill=(236, 230, 210, 255))
    else:
        d.arc([cx - 40, hy + 52, cx + 40, hy + 76], 20, 160, fill=(30, 14, 12, 255), width=4)
    if tilt:
        hd = hd.rotate(tilt, resample=Image.BICUBIC, center=(cx, by0))
        a = math.radians(-tilt)
        eyes = [(cx + (x - cx) * math.cos(a) - (y - by0) * math.sin(a), by0 + (x - cx) * math.sin(a) + (y - by0) * math.cos(a)) for x, y in eyes]
    img.alpha_composite(hd)
    out = (img, cx, 600, eyes)
    _TY[key] = out
    return out


def put_toyol(img, x, y, scale, t, pose="squat", tilt=0.0, phase=0.0, grin=0.0, reach=0.0, eyes=1.0, aura=0.0,
              alpha=1.0, dark=0.0, blur=0, flip=False):
    body, ax, ay, ee = toyol(pose, phase, tilt, grin, reach)
    g = sc_spr(body, scale)
    if flip:
        g = g.transpose(Image.FLIP_LEFT_RIGHT); ee = [(body.width - ex, ey) for ex, ey in ee]; ax = body.width - ax
    if dark > 0:
        g = tint(g, (1 - 0.8 * dark, 1 - 0.75 * dark, 1 - 0.8 * dark))
    if blur:
        g = g.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1:
        g = with_alpha(g, alpha)
    gx, gy = int(x - ax * scale), int(y - ay * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(max(3, 30 * scale)))
        lay = Image.new("RGBA", g.size, (255, 40, 30, 0)); lay.putalpha(al.point(lambda v: int(v * aura * alpha)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    if eyes > 0:
        k = eyes * alpha * (0.7 + 0.3 * math.sin(t * 5) ** 2)
        for ex, ey in ee:
            eye(img, gx + ex * scale, gy + ey * scale, k, max(0.2, scale * 1.4))
    return img


_TF = {}


def toyol_face(mode="grin", inv=False):
    """Close-up for the jump scares: the big bald grey-green head filling the frame, huge pointed ears, deep-set red
    eyes, veins on the scalp; mode "grin" = too-wide grin with small pointed teeth, "scream" = a dark open mouth (teeth
    at the edge, no gore), "still". Face centre (450, 520)."""
    k = (mode, inv)
    if k in _TF:
        return _TF[k]
    w, h = 900, 1100
    cx, cy = 450, 520

    def head(d, s):
        d.ellipse([(cx - 300) * s, (cy - 380) * s, (cx + 300) * s, (cy + 280) * s], fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 250, cy - 90), (cx + sg * 470, cy - 330), (cx + sg * 380, cy + 10), (cx + sg * 270, cy + 90), s=s), fill=255)

    def neck(d, s):
        d.polygon(P_((cx - 110, cy + 200), (cx + 110, cy + 200), (cx + 200, h), (cx - 200, h), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(neck, (w, h), TSKIN, 50, rim=(255, 60, 40)))
    img.alpha_composite(shade(head, (w, h), TSKIN, 150, rim=(255, 60, 40), rim_strength=1.0))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        d.polygon([(cx + sg * 280, cy - 80), (cx + sg * 430, cy - 280), (cx + sg * 360, cy - 10)], fill=TSKIN2 + (255,))
        d.line([(cx + sg * 60, cy - 330), (cx + sg * 100, cy - 250), (cx + sg * 90, cy - 190), (cx + sg * 120, cy - 150)], fill=TSKIN2 + (255,), width=6)
    eyes = [(cx - 115, cy - 20), (cx + 115, cy - 20)]
    for ex, ey in eyes:
        d.ellipse([ex - 112, ey - 86, ex + 104, ey + 92], fill=(46, 56, 42, 255))
        d.ellipse([ex - 84, ey - 50, ex + 84, ey + 62], fill=(8, 3, 3, 255))
        d.line([(ex - 90, ey - 70), (ex + 80, ey - 84 if ex < cx else ey - 56)], fill=TSKIN2 + (255,), width=14)
    d.polygon([(cx - 20, cy + 60), (cx + 20, cy + 60), (cx + 12, cy + 90), (cx - 12, cy + 90)], fill=TSKIN2 + (255,))
    if mode == "scream":
        d.ellipse([cx - 120, cy + 120, cx + 120, cy + 300], fill=(20, 4, 4, 255))
        for k in range(8):
            x = cx - 98 + k * 28
            d.polygon([(x - 11, cy + 134), (x + 11, cy + 134), (x, cy + 166)], fill=(236, 230, 210, 255))
    elif mode == "grin":
        d.chord([cx - 230, cy + 60, cx + 230, cy + 260], 8, 172, fill=(20, 4, 4, 255))
        for k in range(15):
            x = cx - 196 + k * 28
            d.polygon([(x - 12, cy + 150), (x + 12, cy + 150), (x, cy + 186)], fill=(236, 230, 210, 255))
    else:
        d.arc([cx - 90, cy + 140, cx + 90, cy + 190], 20, 160, fill=(30, 14, 12, 255), width=8)
    if inv:
        img = img.rotate(180, resample=Image.BICUBIC, center=(cx, cy))
        eyes = [(2 * cx - x, 2 * cy - y) for x, y in eyes]
    _TF[k] = (img, eyes)
    return _TF[k]


def put_tface(img, x, y, scale, t, mode="grin", tilt=0.0, aura=0.7, alpha=1.0, inv=False, eyes=1.0):
    fimg, ee = toyol_face(mode, inv)
    cxf, cyf = 450, 520
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
            eye(img, gx + rx * scale, gy + ry * scale, k, scale * 2.6)
    return img


def tface_full(t, t0, mode="grin", inv=False, scale=1.25, y=880, bg=(6, 1, 2), tilt=0.0, x=540):
    img = Image.new("RGBA", (W, H), bg + (255,))
    return put_tface(img, x, y + 120 * ss(t, t0, t0 + 0.15) * (1 if not inv else -1), scale, t, mode=mode, aura=0.9, inv=inv, tilt=tilt)


def small_hand(img, x, y, sc, ang=0.0, curl=1.0):
    """A small grey-green hand with long thin fingers, pointing along ang."""
    d = ImageDraw.Draw(img)
    c, s_ = math.cos(ang), math.sin(ang)

    def P(u, v):
        return (x + (u * c - v * s_) * sc, y + (u * s_ + v * c) * sc)
    d.ellipse([x - 24 * sc, y - 20 * sc, x + 24 * sc, y + 20 * sc], fill=TSKIN + (255,), outline=(20, 26, 18, 255), width=3)
    for f in range(4):
        v = -16 + f * 11
        pts = [P(10, v), P(70, v * 1.2), P(70 + 44 * curl, v * 1.2 + 30 * curl)]
        d.line(pts, fill=(20, 26, 18, 255), width=int(10 * sc) + 4, joint="curve")
        d.line(pts, fill=TSKIN + (255,), width=int(10 * sc), joint="curve")
    return img


# ============================================================ set pieces
def palm(d, x, by, hgt, s=1, lean=0.0, rnd=None):
    """A coconut palm silhouette into a mask: a curved trunk and drooping fronds."""
    r = rnd or np.random.default_rng(int(x))
    tx, ty = x + lean * hgt, by - hgt
    pts = [(x + (tx - x) * u + 30 * math.sin(u * 3) * lean, by - hgt * u) for u in np.linspace(0, 1, 12)]
    d.line([(px * s, py * s) for px, py in pts], fill=255, width=int(max(8, hgt * 0.05) * s), joint="curve")
    for k in range(9):
        a = -math.pi / 2 + (k - 4) * 0.42 + r.uniform(-.1, .1)
        ln = hgt * r.uniform(0.32, 0.42)
        p = [(tx, ty)]
        for u in np.linspace(0.1, 1, 8):
            p.append((tx + math.cos(a) * ln * u, ty + math.sin(a) * ln * u + (u ** 2) * ln * 0.55))
        for i in range(len(p) - 1):
            d.line([(p[i][0] * s, p[i][1] * s), (p[i + 1][0] * s, p[i + 1][1] * s)], fill=255, width=int(max(3, 10 * (1 - i / 8)) * s))
            for sg in (-1, 1):
                px, py = p[i + 1]
                d.line([(px * s, py * s), ((px + sg * 6 + math.cos(a) * 10) * s, (py + 22) * s)], fill=255, width=int(2 * s))
    for k in range(3):
        d.ellipse([(tx - 12 + k * 9) * s, (ty + 4) * s, (tx + 2 + k * 9) * s, (ty + 18) * s], fill=255)


def products(d, x0, x1, y, rnd, tall=170):
    """A shelf of tins, boxes, bottles and packets standing on y."""
    cols = [(150, 40, 36), (196, 160, 60), (60, 90, 150), (210, 206, 190), (190, 110, 40), (70, 120, 80), (120, 50, 90), (40, 40, 44)]
    x = x0
    while x < x1 - 30:
        kind = rnd.integers(0, 4)
        c = cols[rnd.integers(0, len(cols))]
        wd = rnd.uniform(36, 80); ht = rnd.uniform(0.45, 1.0) * tall
        dk = tuple(int(v * .6) for v in c)
        if kind == 0:                                        # tin
            d.rectangle([x, y - ht * .6, x + wd * .8, y], fill=c + (255,))
            d.rectangle([x, y - ht * .45, x + wd * .8, y - ht * .25], fill=(230, 220, 200, 255))
            d.ellipse([x, y - ht * .6 - 6, x + wd * .8, y - ht * .6 + 6], fill=dk + (255,))
            x += wd * .8 + 6
        elif kind == 1:                                      # box
            d.rectangle([x, y - ht, x + wd, y], fill=c + (255,))
            d.rectangle([x + 6, y - ht * .7, x + wd - 6, y - ht * .45], fill=(240, 230, 200, 255))
            d.line([(x + wd, y - ht), (x + wd, y)], fill=dk + (255,), width=4)
            x += wd + 5
        elif kind == 2:                                      # bottle
            bw = wd * .45
            d.rectangle([x, y - ht * .7, x + bw, y], fill=c + (255,))
            d.rectangle([x + bw * .3, y - ht * .9, x + bw * .7, y - ht * .7], fill=c + (255,))
            d.rectangle([x + bw * .25, y - ht * .95, x + bw * .75, y - ht * .88], fill=(200, 40, 30, 255))
            x += bw + 8
        else:                                                # stacked packets
            for k in range(3):
                d.rounded_rectangle([x, y - (k + 1) * 26, x + wd, y - k * 26 - 2], 6, fill=c + (255,), outline=dk + (255,))
            x += wd + 6


class Shop:
    """The kedai runcit from behind the counter's customer side: teal plank back wall with three shelves of goods, hanging
    snack strips, a wall clock and a calendar, a round convex mirror high on the left, the fluorescent tube, the half-
    rolled shutter on the right with the red night outside, the glowing AIS KRIM freezer sign; in front the counter with
    glass sweet jars, Tok Wan's bowl of green beans, the wooden cash drawer and a calculator. Counter top y=1250."""
    TOP = 1250

    def __init__(self):
        r = np.random.default_rng(201)
        a = vgrad((10, 22, 24), (22, 52, 54), (16, 38, 40), ym=0.55)
        img = to_img(a)
        d = ImageDraw.Draw(img)
        for x in range(0, 800, 72):                                      # plank seams
            d.line([(x, 140), (x, 1250)], fill=(8, 20, 22, 255), width=4)
        d.rectangle([0, 0, W, 130], fill=(10, 10, 12, 255))               # ceiling
        for x in range(0, W, 120):
            d.line([(x, 0), (x + 40, 130)], fill=(20, 20, 24, 255), width=3)
        # the doorway with the half-rolled shutter (right)
        dx0, dx1 = 800, 1080
        out = to_img(vgrad((20, 4, 8), (90, 16, 20), (40, 10, 12), ym=0.55, w=dx1 - dx0, h=1250 - 130))
        om = Image.new("L", out.size, 0); od = ImageDraw.Draw(om)
        palm(od, 120, 1040, 640, 1, 0.25, r); palm(od, 260, 1060, 520, 1, -0.2, r)
        od.rectangle([0, 960, dx1 - dx0, 1250], fill=255)
        out.alpha_composite(colorize(om, (8, 3, 4)))
        ImageDraw.Draw(out).polygon([(40, 1120), (240, 1120), (280, 1250 - 130), (0, 1250 - 130)], fill=(30, 10, 12, 255))
        img.alpha_composite(out, (dx0, 130))
        d.rectangle([dx0, 130, dx1, 600], fill=(96, 98, 100, 255))        # shutter (rolled half down)
        for y in range(140, 600, 22):
            d.line([(dx0, y), (dx1, y)], fill=(60, 62, 66, 255), width=6)
            d.line([(dx0, y + 8), (dx1, y + 8)], fill=(130, 132, 134, 255), width=2)
        d.rectangle([dx0 - 4, 592, dx1, 612], fill=(70, 70, 74, 255))
        d.rectangle([dx0 - 18, 130, dx0, 1250], fill=(40, 30, 24, 255))
        self.door = (dx0, dx1)
        # shelves
        for y in (520, 790, 1060):
            products(d, 40, 760, y, r, 190)
            d.rectangle([20, y, 780, y + 22], fill=(96, 64, 40, 255)); d.line([(20, y + 22), (780, y + 22)], fill=(40, 26, 18, 255), width=4)
        for k in range(3):                                               # hanging snack strips
            x = 560 + k * 70
            d.line([(x, 130), (x, 470)], fill=(160, 150, 120, 255), width=3)
            for j in range(6):
                c = [(200, 60, 40), (220, 180, 50), (60, 120, 200)][(k + j) % 3]
                d.rounded_rectangle([x - 26, 150 + j * 54, x + 26, 196 + j * 54], 5, fill=c + (255,), outline=(40, 30, 20, 255), width=2)
        d.rectangle([300, 230, 420, 380], fill=(220, 214, 196, 255))      # calendar
        d.rectangle([300, 230, 420, 270], fill=(170, 30, 30, 255))
        for j in range(4):
            for i in range(5):
                d.rectangle([310 + i * 22, 284 + j * 22, 324 + i * 22, 298 + j * 22], fill=(120, 110, 100, 255))
        self.clock = (470, 300)                                            # wall clock (hands drawn per frame)
        d.ellipse([415, 245, 525, 355], fill=(230, 226, 214, 255), outline=(30, 26, 22, 255), width=8)
        # the convex mirror (top left)
        self.mirror = (150, 300, 96)
        d.line([(150, 130), (150, 200)], fill=(60, 60, 60, 255), width=8)
        self.base_noobj = img.copy()
        # AIS KRIM freezer peeking above the counter (red key light)
        d.rounded_rectangle([30, 1080, 290, 1250], 14, fill=(200, 200, 205, 255))
        d.rectangle([44, 1096, 276, 1160], fill=(150, 14, 20, 255))
        f = font(INTER_SB, 46)
        d.text((160, 1128), "AIS KRIM", font=f, fill=(255, 236, 226, 255), anchor="mm")
        self.freezer = (160, 1128)
        self.base = img
        # the counter (front layer)
        cnt = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def ctop(dd, s):
            dd.rectangle([-10 * s, 1240 * s, (W + 10) * s, (H + 10) * s], fill=255)
        cnt.alpha_composite(shade(ctop, (W, H), WOOD, 50, rim=(255, 90, 60), rim_strength=0.6))
        cd = ImageDraw.Draw(cnt)
        cd.rectangle([0, 1240, W, 1300], fill=(120, 80, 50, 255)); cd.line([(0, 1300), (W, 1300)], fill=(40, 24, 14, 255), width=6)
        for x in range(0, W, 90):
            cd.line([(x, 1306), (x, H)], fill=(44, 28, 18, 255), width=4)
        cd.rectangle([120, 1420, 300, 1520], fill=(200, 180, 60, 255)); cd.text((210, 1470), "RM", font=font(INTER_SB, 50), fill=(60, 30, 20, 255), anchor="mm")
        self.counter = cnt
        # counter objects (drawn on top of the counter, sitting on y=1250)
        ob = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for i, (x, sc_) in enumerate(((830, 1.0), (940, 0.9), (1035, 1.05))):
            jar = Image.new("RGBA", (130, 240), (0, 0, 0, 0)); jd = ImageDraw.Draw(jar)
            jd.rounded_rectangle([10, 40, 120, 236], 20, fill=(150, 190, 190, 90), outline=(200, 230, 230, 200), width=4)
            rr = np.random.default_rng(i)
            for k in range(26):
                c = [(220, 40, 50), (240, 200, 60), (60, 160, 90), (240, 120, 160)][k % 4]
                px, py = rr.uniform(26, 104), rr.uniform(120, 222)
                jd.ellipse([px - 11, py - 9, px + 11, py + 9], fill=c + (230,))
            jd.rounded_rectangle([4, 20, 126, 50], 8, fill=(170, 24, 28, 255))
            jar = sc_spr(jar, sc_)
            ob.alpha_composite(jar, (int(x - jar.width / 2), int(1252 - jar.height)))
        self.jars = [(830, 1050), (940, 1070), (1035, 1040)]
        self.bowl = (420, 1250)
        od = ImageDraw.Draw(ob)
        od.rectangle([540, 1150, 760, 1252], fill=(92, 58, 34, 255), outline=(40, 24, 14, 255), width=5)   # cash drawer box
        od.rectangle([560, 1170, 740, 1206], fill=(60, 36, 22, 255))
        od.ellipse([642, 1214, 658, 1230], fill=(200, 170, 80, 255))
        self.till = (650, 1150)
        self.objects = ob

    def bowl_img(self, n_beans=1.0):
        """Tok Wan's enamel bowl heaped with green beans (n_beans 0..1 how full)."""
        b = Image.new("RGBA", (220, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(b)
        rr = np.random.default_rng(3)
        n = int(150 * n_beans)
        for k in range(150):
            px = rr.uniform(34, 186); py = rr.uniform(20, 58) + abs(px - 110) * 0.15
            g = rr.integers(0, 40)
            if k < n:
                d.ellipse([px - 8, py - 5, px + 8, py + 5], fill=(80 + int(g), 140 + int(g), 50, 255), outline=(40, 70, 30, 255))
        d.chord([10, -10, 210, 126], 0, 180, fill=(232, 230, 222, 255))
        d.arc([10, -10, 210, 126], 0, 180, fill=(30, 60, 120, 255), width=6)
        d.line([(12, 58), (208, 58)], fill=(30, 60, 120, 255), width=5)
        return b

    def frame(self, t, back=None, counter=None, light=1.0, beans=1.0, mirror=None, clock_m=14, flicker=0.0, red=1.0, wall_mirror=True):
        a = to_arr(self.base)
        a = a * (0.25 + 0.75 * light)
        # fluorescent tube
        fl = light * (1.0 if flicker <= 0 else (0.2 if math.sin(t * 37) * math.sin(t * 11) > 0.3 else 1.0))
        add_glow(a, gsp(520, (190, 255, 220)), 540, 160, 0.30 * fl)
        add_glow(a, gsp(300, (255, 30, 30)), self.freezer[0], self.freezer[1], 0.55 * red * (0.9 + 0.1 * math.sin(t * 3)))
        add_glow(a, gsp(380, (255, 40, 40)), 940, 1000, 0.3 * red)
        img = to_img(a)
        d = ImageDraw.Draw(img)
        if fl > 0.05:
            d.rounded_rectangle([330, 136, 750, 160], 10, fill=(int(230 * fl + 20), int(255 * fl), int(240 * fl + 10), 255))
        else:
            d.rounded_rectangle([330, 136, 750, 160], 10, fill=(40, 44, 44, 255))
        cx, cy = self.clock                                                # clock hands 10:mm
        ang_m = 2 * math.pi * clock_m / 60; ang_h = 2 * math.pi * (10 + clock_m / 60) / 12
        d.line([(cx, cy), (cx + 40 * math.sin(ang_m), cy - 40 * math.cos(ang_m))], fill=(20, 20, 20, 255), width=5)
        d.line([(cx, cy), (cx + 26 * math.sin(ang_h), cy - 26 * math.cos(ang_h))], fill=(20, 20, 20, 255), width=7)
        d.line([(cx, cy), (cx + 44 * math.sin(t * 6.28), cy - 44 * math.cos(t * 6.28))], fill=(200, 30, 30, 255), width=2)
        # convex mirror: a dark distorted reflection + highlight
        mx, my, mr = self.mirror
        ref = to_img(vgrad((20, 40, 40), (40, 70, 66), (30, 20, 20), ym=0.5, w=2 * mr, h=2 * mr) * (0.4 + 0.6 * light))
        rd = ImageDraw.Draw(ref)
        rd.rectangle([0, mr * 1.3, 2 * mr, 2 * mr], fill=(60, 36, 24, 255))
        for k in range(4):
            rd.line([(k * 50, 0), (mr, mr)], fill=(30, 50, 50, 255), width=3)
        for fn in (mirror or []):
            ref = fn(ref, t) or ref
        m = Image.new("L", ref.size, 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * mr - 1, 2 * mr - 1], fill=255)
        ref.putalpha(m)
        if wall_mirror:
            img.alpha_composite(ref, (mx - mr, my - mr))
            d = ImageDraw.Draw(img)
            d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=(200, 140, 40, 255), width=8)
            d.arc([mx - mr * .7, my - mr * .7, mx + mr * .3, my + mr * .3], 200, 260, fill=(255, 255, 255, 160), width=6)
        else:
            d = ImageDraw.Draw(img)
            d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=(14, 30, 30, 255), width=6)
        for fn in (back or []):
            img = fn(img, t) or img
        img.alpha_composite(self.counter)
        img.alpha_composite(self.objects)
        b = self.bowl_img(beans)
        img.alpha_composite(b, (int(self.bowl[0] - 110), int(self.bowl[1] - 128)))
        for fn in (counter or []):
            img = fn(img, t) or img
        if light < 1:
            a = to_arr(img)
            a *= (0.35 + 0.65 * light)
            img = to_img(a)
        return img


_SHOP = None


def shop():
    global _SHOP
    if _SHOP is None:
        _SHOP = Shop()
    return _SHOP


class Outside:
    """The kampung road at night: red moon, palms, the shop on the left (zinc roof, KEDAI RUNCIT sign, half-rolled
    shutter with the green-white light inside, a hanging bulb, a kapcai motorbike), the big new two-storey house across
    the road on the right with a gate and one upper window where a jar sits on the sill (self.jar), the road running
    away between them. dawn 0..1 turns the sky pink-grey."""
    def __init__(self):
        r = np.random.default_rng(202)
        self.sky = moon_sky(moon=(560, 470), r=110, top=(6, 2, 4), mid=(40, 8, 14), bot=(110, 26, 26), ym=0.55)
        self.sky_dawn = vgrad((60, 50, 70), (170, 110, 110), (230, 170, 140), ym=0.6)
        far = Image.new("L", (W, H), 0); fd = ImageDraw.Draw(far)
        for k in range(9):
            palm(fd, r.uniform(-50, W + 50), 1260, r.uniform(380, 620), 1, r.uniform(-.3, .3), r)
        fd.rectangle([0, 1180, W, 1300], fill=255)
        self.far = dof(colorize(far, (22, 8, 12)), 2)
        # the house across the road (right)
        hs = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def walls(dd, s):
            dd.rectangle([640 * s, 760 * s, 1090 * s, 1320 * s], fill=255)
        hs.alpha_composite(shade(walls, (W, H), (150, 140, 130), 30, rim=(255, 60, 40)))
        hd = ImageDraw.Draw(hs)
        hd.polygon([(610, 770), (865, 610), (1110, 770)], fill=(70, 30, 28, 255))           # tiled roof
        for k in range(8):
            hd.line([(610 + k * 30, 770 - k * 19), (1110 - k * 30, 770 - k * 19)], fill=(50, 20, 20, 255), width=3)
        hd.line([(640, 1010), (1090, 1010)], fill=(110, 100, 94, 255), width=10)             # floor line
        for x0 in (690, 950):                                                               # windows
            hd.rectangle([x0, 820, x0 + 100, 960], fill=(20, 16, 20, 255), outline=(200, 190, 170, 255), width=6)
            hd.rectangle([x0, 1060, x0 + 100, 1220], fill=(20, 16, 20, 255), outline=(200, 190, 170, 255), width=6)
        self.jar = (1000, 920)
        hd.rectangle([830, 1080, 900, 1320], fill=(70, 46, 32, 255))                        # door
        for x in range(600, 1100, 26):                                                     # gate
            hd.line([(x, 1200), (x, 1360)], fill=(30, 30, 34, 255), width=6)
        hd.line([(600, 1210), (1100, 1210)], fill=(30, 30, 34, 255), width=8); hd.line([(600, 1350), (1100, 1350)], fill=(30, 30, 34, 255), width=8)
        self.house = hs
        # the shop (left)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def front(dd, s):
            dd.rectangle([-20 * s, 800 * s, 520 * s, 1440 * s], fill=255)
        sh.alpha_composite(shade(front, (W, H), (110, 74, 46), 30, rim=(255, 60, 40)))
        sd = ImageDraw.Draw(sh)
        for x in range(-20, 520, 40):
            sd.line([(x, 800), (x, 1440)], fill=(70, 46, 28, 255), width=3)
        sd.polygon([(-40, 790), (560, 790), (600, 700), (-40, 640)], fill=(120, 120, 124, 255))  # zinc roof
        for k in range(16):
            x = -40 + k * 40
            sd.line([(x, 640 + k * 4), (x + 40, 790)], fill=(90, 90, 96, 255), width=4)
        sd.rectangle([20, 820, 480, 900], fill=(236, 226, 196, 255), outline=(150, 30, 30, 255), width=6)   # sign
        sd.text((250, 860), "KEDAI RUNCIT", font=font(INTER_SB, 58), fill=(170, 24, 24, 255), anchor="mm")
        self.opening = (60, 990, 440, 1420)
        x0, y0, x1, y1 = self.opening
        sd.rectangle([x0, y0, x1, y1], fill=(190, 230, 200, 255))
        for k in range(3):
            products(sd, x0 + 10, x1 - 10, y0 + 130 + k * 110, r, 90)
        sd.rectangle([x0, y0, x1, y0 + 120], fill=(110, 112, 114, 255))                      # shutter half down
        for y in range(y0, y0 + 120, 16):
            sd.line([(x0, y), (x1, y)], fill=(70, 72, 76, 255), width=5)
        sd.rectangle([x0, 1330, x1, 1420], fill=(92, 58, 34, 255))                            # counter seen inside
        self.shop = sh
        self.ground = to_img(vgrad((20, 12, 12), (30, 18, 18), (14, 8, 8), ym=0.4, h=H))
        ga = np.asarray(self.ground).copy(); ga[:1260, :, 3] = 0; self.ground = Image.fromarray(ga, "RGBA")
        gd = ImageDraw.Draw(self.ground)
        gd.polygon([(500, 1300), (600, 1300), (1200, H), (-120, H)], fill=(36, 32, 34, 255))     # the road
        for k in range(6):
            yy = 1320 + k * k * 18
            gd.rectangle([544 - k * 4, yy, 556 + k * 4, yy + 8 + k * 6], fill=(200, 190, 160, 255))
        # a kapcai motorbike in front of the shop
        mb = Image.new("RGBA", (W, H), (0, 0, 0, 0)); md = ImageDraw.Draw(mb)
        for wx in (330, 520):
            md.ellipse([wx - 50, 1480, wx + 50, 1580], fill=(14, 12, 14, 255)); md.ellipse([wx - 22, 1508, wx + 22, 1552], fill=(80, 80, 84, 255))
        md.polygon([(320, 1500), (400, 1440), (500, 1440), (540, 1500), (460, 1520), (360, 1520)], fill=(150, 30, 34, 255))
        md.rectangle([380, 1420, 470, 1440], fill=(20, 20, 22, 255)); md.line([(520, 1500), (560, 1400), (600, 1390)], fill=(60, 60, 64, 255), width=8)
        self.moto = mb

    def frame(self, t, mid=None, front=None, dawn=0.0, jar_glow=1.0, shop_light=1.0):
        a = self.sky * (1 - dawn) + self.sky_dawn * dawn
        img = to_img(a)
        img.alpha_composite(self.far)
        fog(img, t, 0.35 * (1 - dawn * .5), 1050, 1320, speed=12, col=(140, 50, 50) if dawn < .5 else (200, 170, 170))
        img.alpha_composite(self.ground)
        img.alpha_composite(self.house)
        a = to_arr(img)
        jx, jy = self.jar
        add_glow(a, gsp(120, (150, 255, 160)), jx, jy, 0.5 * jar_glow * (0.85 + 0.15 * math.sin(t * 4)))
        img = to_img(a)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([jx - 26, jy - 10, jx + 26, jy + 40], 10, fill=(60, 50, 30, 255), outline=(150, 220, 150, 255), width=3)   # the jar
        d.rectangle([jx - 16, jy - 22, jx + 16, jy - 8], fill=(100, 60, 30, 255))
        img.alpha_composite(self.shop)
        a = to_arr(img)
        x0, y0, x1, y1 = self.opening
        add_glow(a, gsp(330, (190, 255, 210)), (x0 + x1) / 2, y1 + 40, 0.35 * shop_light)
        add_glow(a, gsp(60, (255, 230, 170)), 250, 950, 0.9 * shop_light)
        img = to_img(a)
        for fn in (mid or []):
            img = fn(img, t) or img
        img.alpha_composite(self.moto)
        bokeh_particles(img, 14, 5, t, color=(200, 255, 150), size=(3, 8), blur=(0, 3), area=(0, 900, W, 1500), drift=(6, -10))
        for fn in (front or []):
            img = fn(img, t) or img
        if dawn > 0:
            a = to_arr(img) * (1 + 0.3 * dawn)
            img = to_img(a)
        return img


_OUT = None


def outside():
    global _OUT
    if _OUT is None:
        _OUT = Outside()
    return _OUT


class Under:
    """POV from the dark under the counter (kind "counter") or under a bed (kind "bed"): the dark underside above and
    to the sides, and the floor running away from us in perspective, lit faintly red (counter: grey-and-red tiles,
    scattered green beans, the shelves' bottom row; bed: wooden floorboards, a pink rug, the sister's red coin tin,
    a few coins, the window light). Floor point (fx, fy) -> scale via self.at(u, side)."""
    def __init__(self, kind="counter"):
        r = np.random.default_rng(203 if kind == "counter" else 204)
        self.kind = kind
        self.vx, self.vy = 540, 820
        img = to_img(vgrad((14, 22, 24), (30, 40, 40), (20, 14, 14), ym=0.6) if kind == "counter" else vgrad((14, 10, 20), (36, 24, 40), (24, 16, 20), ym=0.6))
        d = ImageDraw.Draw(img)
        if kind == "counter":
            products(d, 40, 1040, 900, r, 150)
            d.rectangle([0, 900, W, 930], fill=(80, 52, 34, 255))
        else:
            d.rectangle([680, 520, 900, 800], fill=(60, 30, 40, 255))
            d.rectangle([700, 540, 880, 780], fill=(120, 40, 50, 255))                       # moonlit window, red
            for x in range(700, 881, 45):
                d.line([(x, 540), (x, 780)], fill=(30, 20, 26, 255), width=6)
            d.rectangle([120, 640, 400, 900], fill=(50, 36, 50, 255))                         # a wardrobe
        fl = Image.new("RGBA", (W, H - 930), (0, 0, 0, 0)); fdd = ImageDraw.Draw(fl)
        for k in range(16):                                                                 # floor in perspective
            z0, z1 = 1 + k * 0.6, 1 + (k + 1) * 0.6
            y0 = 900 / z1 - 0; y1 = 900 / z0
            for i in range(-10, 11):
                xa0, xa1 = 540 + i * 300 / z1, 540 + (i + 1) * 300 / z1
                xb0, xb1 = 540 + i * 300 / z0, 540 + (i + 1) * 300 / z0
                if kind == "counter":
                    c = (70, 66, 64) if (i + k) % 2 == 0 else (110, 34, 34)
                else:
                    c = (82 + (i * 7) % 16, 52, 34)
                fdd.polygon([(xa0, 990 - y0 - 930 + 830), (xa1, 990 - y0 - 930 + 830), (xb1, 990 - y1 - 930 + 830), (xb0, 990 - y1 - 930 + 830)], fill=c + (255,))
        img.alpha_composite(fl.transpose(Image.FLIP_TOP_BOTTOM), (0, 930))
        d = ImageDraw.Draw(img)
        if kind == "bed":
            d.ellipse([200, 1350, 900, 1700], fill=(150, 70, 100, 255))                     # pink rug
        rr = np.random.default_rng(9)
        self.scatter = []
        for k in range(60 if kind == "counter" else 12):
            u, side = rr.uniform(0.1, 1.0), rr.uniform(-1.4, 1.4)
            x, y, s = self.at(u, side)
            if kind == "counter":
                d.ellipse([x - 9 * s, y - 6 * s, x + 9 * s, y + 6 * s], fill=(90, 150, 60, 255))
            else:
                d.ellipse([x - 16 * s, y - 8 * s, x + 16 * s, y + 8 * s], fill=(210, 180, 80, 255), outline=(110, 80, 30, 255))
        a = to_arr(img)
        yy = np.arange(H)[:, None, None]
        a *= np.clip(0.35 + 0.65 * (yy - 800) / 1100, 0.25, 1.0)
        self.base = to_img(a)
        # the dark frame: underside above + posts at the sides + near floor edge
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); frd = ImageDraw.Draw(fr)
        top = 760 if kind == "counter" else 700
        frd.rectangle([0, 0, W, top], fill=(16, 10, 8, 255))
        for k in range(8 if kind == "counter" else 6):
            y = top - 60 - k * 90
            frd.line([(0, y), (W, y + (6 if kind == "counter" else 0))], fill=(40, 26, 18, 255), width=6)
            if kind == "bed":
                frd.rectangle([0, y - 30, W, y], fill=(30, 22, 30, 255))
        frd.polygon([(0, top), (80, top), (40, H), (0, H)], fill=(12, 8, 6, 255))
        frd.polygon([(W, top), (W - 80, top), (W - 40, H), (W, H)], fill=(12, 8, 6, 255))
        frd.rectangle([0, top - 20, W, top], fill=(60, 40, 28, 255))
        self.frame_img = fr.filter(ImageFilter.GaussianBlur(1.5))

    def at(self, u, side=0.0):
        """u 0 (far) .. 1 (right in front of us); returns floor (x, y, scale)."""
        z = 1 + (1 - u) * 9
        return 540 + side * 300 / z, 1910 - 900 / z * 0 - 1090 * (1 - 1 / z), 1.6 / z

    def frame(self, t, floor=None, edge=None, red=1.0):
        a = to_arr(self.base)
        add_glow(a, gsp(500, (255, 40, 40)), 540, 900, 0.35 * red)
        img = to_img(a)
        for fn in (floor or []):
            img = fn(img, t) or img
        img.alpha_composite(self.frame_img)
        for fn in (edge or []):
            img = fn(img, t) or img
        return img


_UN = {}


def under(kind="counter"):
    if kind not in _UN:
        _UN[kind] = Under(kind)
    return _UN[kind]
