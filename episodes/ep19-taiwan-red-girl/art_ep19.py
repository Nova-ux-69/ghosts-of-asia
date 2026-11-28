"""Ep19 Taiwan / the little girl in red (mo-sin-a) - art: the world, the family and the ghost (2.1D flat21 style).
New world: a Taiwanese mountain trail near Taichung at the end of the afternoon (a low red sun over a sea of clouds,
layered blue-black ridges, giant tree ferns, tall Japanese cedars and a camphor, stone-and-timber steps climbing into the
mist, hikers' cloth ribbons tied on the branches), a tiny Earth God (Tudi Gong) shrine of red brick with a swallowtail
roof, incense and red candle lamps, the same forest drowned in fog with the ribbons turned red, the inside of a hollow
camphor tree looking out, the steps at night with torch beams, and Mei's room in a Taichung apartment (iron window
grille, a red neon sign outside, a desk fan, the dark doorway). Hero: Mei (mustard windbreaker, black leggings,
ponytail, grey backpack) with Grandpa (grey cap, khaki jacket, bamboo stick), Mum and her little brother. Ghost: the
little girl in red - a small, too-still child in a long-sleeved red dress and red cloth shoes, long straight black hair
with heavy bangs, a pale face with black eyes and red pin-point glints, head tilted, arms a little too long. No gore."""
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


# ============================================================ palette
MSKIN = (196, 150, 118)        # Mei
MJACK = (196, 150, 40)         # mustard windbreaker
MLEG = (26, 26, 32)            # black leggings
MPACK = (78, 82, 88)           # grey backpack
HAIR = (12, 10, 12)
GSKIN_ = (176, 132, 100)       # Grandpa
GJACK = (120, 108, 74)         # khaki jacket
GCAP = (70, 72, 70)
GHAIR = (170, 168, 160)
MUMJ = (40, 70, 72)            # Mum: dark teal jacket
BOYT = (200, 90, 40)           # little brother: orange tee
BOYC = (40, 60, 120)           # blue cap
RED = (172, 18, 26)            # the girl's dress
RED2 = (120, 10, 18)
PALE = (222, 214, 208)         # the girl's skin
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """Taiwan (Republic of China): a red field, a blue canton (a quarter of the flag) with a white sun of twelve
    triangular rays, a blue ring and a white disc - 3:2."""
    global _FLAG
    if _FLAG is None:
        s = 4
        w, h = 300 * s, 200 * s
        im = Image.new("RGBA", (w, h), (200, 16, 46, 255)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w // 2, h // 2], fill=(0, 40, 140, 255))
        cx, cy = 75 * s, 50 * s
        R, r = 30 * s, 15.5 * s
        pts = []
        for k in range(24):
            a = -math.pi / 2 + k * math.pi / 12
            rr = R if k % 2 == 0 else r + 0.5 * s
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        d.polygon(pts, fill=(255, 255, 255, 255))
        d.ellipse([cx - 17 * s, cy - 17 * s, cx + 17 * s, cy + 17 * s], fill=(0, 40, 140, 255))
        d.ellipse([cx - 15 * s, cy - 15 * s, cx + 15 * s, cy + 15 * s], fill=(255, 255, 255, 255))
        _FLAG = im.resize((300, 200), Image.LANCZOS)
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


def trail_ui(now, km, t, k=1.0, danger=False, night=False):
    """The ticking clock: time now vs SUNSET 17:12 (a sun sinking behind a ridge) + the distance to the trailhead."""
    f1 = font(INTER_SB, 40); f2 = font(INTER_M, 24); f3 = font(INTER_SB, 36)
    w, h = 740, 112
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    blink = (math.sin(t * 10) > -0.2) if danger else True
    oc = (255, 50, 40) if danger else (230, 190, 120)
    A = int(255 * k)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 32, fill=(0, 0, 0, int(190 * k)), outline=oc + (int(220 * k),), width=3)
    cx, cy = 58, 62                                                    # sun sinking behind a ridge
    sc = (255, 120, 70, A) if not night else (120, 120, 130, A)
    d.ellipse([cx - 22, cy - 26, cx + 22, cy + 18], fill=sc)
    d.polygon([(cx - 40, cy + 22), (cx - 14, cy - 2), (cx + 4, cy + 12), (cx + 22, cy - 6), (cx + 42, cy + 22)], fill=(0, 0, 0, A))
    d.line([(cx - 40, cy + 22), (cx - 14, cy - 2), (cx + 4, cy + 12), (cx + 22, cy - 6), (cx + 42, cy + 22)], fill=(250, 236, 210, A), width=3)
    d.text((112, 32), "NOW", font=f2, fill=(230, 190, 140, A), anchor="lm")
    if blink:
        d.text((112, 76), now, font=f1, fill=((255, 70, 55) if danger else (248, 240, 228)) + (A,), anchor="lm")
    d.text((262, 32), "SUNSET", font=f2, fill=(230, 190, 140, A), anchor="lm")
    d.text((262, 76), "17:12", font=f3, fill=(200, 190, 180, A), anchor="lm")
    d.line([(400, 22), (400, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    hx, hy = 446, 62                                                  # a little trail sign
    col = (255, 214, 150, A)
    d.rectangle([hx - 3, hy - 30, hx + 3, hy + 34], fill=col)
    d.polygon([(hx - 30, hy - 30), (hx + 24, hy - 30), (hx + 36, hy - 18), (hx + 24, hy - 6), (hx - 30, hy - 6)], fill=col)
    d.text((610, 36), "TRAILHEAD", font=f2, fill=(230, 190, 140, A), anchor="mm")
    d.text((610, 76), km, font=f3, fill=(255, 240, 228, A), anchor="mm")
    return im


def put_ui(out, now, km, t, k=1.0, y=200, danger=False, night=False):
    if k <= 0.01:
        return
    ui = trail_ui(now, km, t, k, danger, night)
    out.alpha_composite(ui, (int(W / 2 - ui.width / 2), int(y)))


def clock_at(m0, m1, u):
    """minutes after 16:00, interpolated -> '16:mm' (or 17:mm)."""
    m = int(m0 + (m1 - m0) * max(0.0, min(1.0, u)))
    return f"{16 + m // 60}:{m % 60:02d}"


# ============================================================ people (back view: climbing / walking away)
_HK = {}
KINDS = {
    "mei":     dict(jack=MJACK, leg=MLEG, skin=MSKIN, hair=HAIR, size=0.92, pack=MPACK, tail=True),
    "grandpa": dict(jack=GJACK, leg=(60, 56, 50), skin=GSKIN_, hair=GHAIR, size=1.0, cap=GCAP, stick=True),
    "mum":     dict(jack=MUMJ, leg=(40, 40, 46), skin=MSKIN, hair=HAIR, size=0.96, bun=True, pack=(110, 50, 50)),
    "boy":     dict(jack=BOYT, leg=(50, 60, 80), skin=MSKIN, hair=HAIR, size=0.66, cap=BOYC),
}


def hiker(kind, phase=0.0, scale=1.0, run=0.0, incense=False):
    """A hiker seen from behind, climbing or walking away from the camera. Returns (RGBA, feet_x, feet_y)."""
    q = (kind, round(phase * 12) % 12, round(run, 1), round(scale, 2), incense)
    if q in _HK:
        return _HK[q]
    K = KINDS[kind]
    w, h = 420, 940
    cx = w / 2
    ph = 2 * math.pi * q[1] / 12
    sw = math.sin(ph) * (0.5 + 0.5 * run)
    lift = {-1: max(0, math.sin(ph)) * (40 + 40 * run), 1: max(0, -math.sin(ph)) * (40 + 40 * run)}

    def legs(d, s):
        for sg in (-1, 1):
            fy = 880 - lift[sg]
            d.line([((cx + sg * 30) * s, 470 * s), ((cx + sg * 32) * s, (680 - lift[sg] * .5) * s), ((cx + sg * 30) * s, fy * s)], fill=255, width=int(50 * s), joint="curve")

    def shoes(d, s):
        for sg in (-1, 1):
            fy = 880 - lift[sg]
            d.ellipse([(cx + sg * 30 - 32) * s, (fy - 20) * s, (cx + sg * 30 + 32) * s, (fy + 14) * s], fill=255)

    def body(d, s):
        d.polygon(P_((cx - 88, 200), (cx + 88, 200), (cx + 82, 360), (cx + 92, 500), (cx - 92, 500), (cx - 82, 360), s=s), fill=255)
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 72 - 30) * s, 188 * s, (cx + sg * 72 + 30) * s, 252 * s], fill=255)
        if K.get("stick") or incense:
            pass

    arms = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 86, 222
        if incense:
            arms[sg] = ((sx, sy), (cx + sg * 60, 340), (cx + sg * 12, 300))
        else:
            a = sg * sw * 0.6
            ex, ey = sx + sg * 10 + math.sin(a) * 30, sy + 120
            arms[sg] = ((sx, sy), (ex, ey), (ex + math.sin(a) * 30 + sg * 4, ey + 110 - 30 * run))

    def armf(d, s):
        for sg in (-1, 1):
            d.line([(x * s, y * s) for x, y in arms[sg]], fill=255, width=int(34 * s), joint="curve")

    def hands(d, s):
        for sg in (-1, 1):
            x, y = arms[sg][2]
            d.ellipse([(x - 16) * s, (y - 16) * s, (x + 16) * s, (y + 16) * s], fill=255)

    def head(d, s):
        d.rectangle([(cx - 22) * s, 150 * s, (cx + 22) * s, 210 * s], fill=255)
        d.ellipse([(cx - 52) * s, 46 * s, (cx + 52) * s, 182 * s], fill=255)

    def hair(d, s):
        d.ellipse([(cx - 55) * s, 40 * s, (cx + 55) * s, 176 * s], fill=255)
        if K.get("tail"):
            d.line([(cx * s, 120 * s), ((cx + 10 + 20 * sw) * s, 220 * s), ((cx + 4 + 34 * sw) * s, 290 * s)], fill=255, width=int(30 * s), joint="curve")
        if K.get("bun"):
            d.ellipse([(cx - 30) * s, 20 * s, (cx + 30) * s, 76 * s], fill=255)

    def cap(d, s):
        d.pieslice([(cx - 58) * s, 34 * s, (cx + 58) * s, 150 * s], 180, 360, fill=255)
        d.rectangle([(cx - 58) * s, 86 * s, (cx + 58) * s, 100 * s], fill=255)

    def pack(d, s):
        d.rounded_rectangle([(cx - 70) * s, 230 * s, (cx + 70) * s, 450 * s], int(34 * s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), K["leg"], 20, rim_strength=1.1))
    img.alpha_composite(shade(shoes, (w, h), (40, 34, 30), 10))
    img.alpha_composite(shade(armf, (w, h), K["jack"], 14))
    img.alpha_composite(shade(hands, (w, h), K["skin"], 8))
    img.alpha_composite(shade(body, (w, h), K["jack"], 40, rim_strength=1.1))
    if K.get("pack"):
        img.alpha_composite(shade(pack, (w, h), K["pack"], 30))
        pd = ImageDraw.Draw(img)
        pd.line([(cx - 50, 300), (cx + 50, 300)], fill=(40, 40, 44, 255), width=4)
    img.alpha_composite(shade(head, (w, h), K["skin"], 24))
    img.alpha_composite(shade(hair, (w, h), K["hair"], 16, rim_strength=1.2))
    if K.get("cap"):
        img.alpha_composite(shade(cap, (w, h), K["cap"], 18))
    d = ImageDraw.Draw(img)
    if K.get("stick"):
        x, y = arms[1][2]
        d.line([(x, y - 40), (x + 30, 900)], fill=(170, 150, 90, 255), width=10)
        for k in range(5):
            yy = y + k * 180
            d.line([(x + (yy - y + 40) / 940 * 30 - 8, yy), (x + (yy - y + 40) / 940 * 30 + 8, yy)], fill=(110, 96, 60, 255), width=4)
    if incense:
        for k in range(3):
            d.line([(cx - 8 + k * 8, 300), (cx - 14 + k * 14, 120)], fill=(170, 60, 40, 255), width=4)
    sc = K["size"] * scale
    if sc != 1.0:
        img = img.resize((max(1, int(w * sc)), max(1, int(h * sc))), Image.LANCZOS)
    out = (img, cx * sc, 890 * sc)
    _HK[q] = out
    return out


def incense_tips(img, x, y, sc, t):
    """Glowing incense tips + rising smoke for hiker(incense=True) placed with feet at (x, y)."""
    a = to_arr(img)
    for k in range(3):
        tx, ty = x + (-14 + k * 14 - 210 + 210) * sc * 0.0 + (-14 + k * 14) * sc, y - (890 - 120) * sc
        add_glow(a, gsp(10, (255, 120, 60)), tx, ty, 1.0)
    img = to_img(a)
    d = ImageDraw.Draw(img)
    for k in range(3):
        tx, ty = x + (-14 + k * 14) * sc, y - 770 * sc
        pts = [(tx + 10 * math.sin(t * 1.5 + j * 0.5 + k) * j / 8 * sc * 3, ty - j * 22 * sc) for j in range(12)]
        d.line(pts, fill=(200, 190, 190, 70), width=max(2, int(5 * sc)))
    return img


# ============================================================ Mei (front)
_MF = {}


def mei(pose="stand", phase=0.0, scale=1.0, look=0.0, gasp=0.0, phone=0.0, shout=0.0):
    """Mei seen from the front. pose: "stand", "run" (running toward us), "sit" (sitting on a step / the bed,
    knees up, phone in both hands - phone>0 lights her face), "crouch" (curled up inside the tree, hand over mouth when
    gasp<0). look: eyes up (+) / sideways (-). Returns (RGBA, feet_x, feet_y)."""
    q = (pose, round(phase * 12) % 12, round(scale, 2), round(look, 1), round(gasp, 1), round(phone, 1), round(shout, 1))
    if q in _MF:
        return _MF[q]
    w, h = 520, 960
    cx = w / 2
    ph = 2 * math.pi * q[1] / 12
    run = pose == "run"
    sw = math.sin(ph) if run else 0.0
    sit = pose in ("sit", "crouch")
    hy = 150 if not sit else 330                              # head centre y

    def legs(d, s):
        if sit:
            for sg in (-1, 1):
                d.line([((cx + sg * 58) * s, 640 * s), ((cx + sg * 56) * s, 870 * s)], fill=255, width=int(54 * s))
                d.ellipse([(cx + sg * 58 - 44) * s, 590 * s, (cx + sg * 58 + 44) * s, 690 * s], fill=255)
        else:
            for sg in (-1, 1):
                up = max(0, sg * sw) * 90
                d.line([((cx + sg * 32) * s, 480 * s), ((cx + sg * 36) * s, (690 - up * .6) * s), ((cx + sg * 32) * s, (880 - up) * s)], fill=255, width=int(52 * s), joint="curve")

    def shoes(d, s):
        for sg in (-1, 1):
            if sit:
                x, y = cx + sg * 50, 885
            else:
                x, y = cx + sg * 32, 885 - max(0, sg * sw) * 90
            d.ellipse([(x - 34) * s, (y - 18) * s, (x + 34) * s, (y + 16) * s], fill=255)

    by = 210 if not sit else 390

    def body(d, s):
        bot = 500 if not sit else 700
        d.polygon(P_((cx - 90, by), (cx + 90, by), (cx + 84, by + 160), (cx + 96, bot), (cx - 96, bot), (cx - 84, by + 160), s=s), fill=255)
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 74 - 30) * s, (by - 12) * s, (cx + sg * 74 + 30) * s, (by + 52) * s], fill=255)

    arms = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 88, by + 20
        if pose == "sit" or phone > 0:
            arms[sg] = ((sx, sy), (cx + sg * 110, sy + 150), (cx + sg * 26, sy + 120))
        elif pose == "crouch":
            arms[sg] = ((sx, sy), (cx + sg * 120, sy + 150), (cx + sg * 30, sy + 230)) if (gasp >= 0 or sg == -1) else ((sx, sy), (cx + 100, sy + 60), (cx + 14, hy + 40))
        elif shout > 0:
            arms[sg] = ((sx, sy), (cx + sg * 110, sy - 20), (cx + sg * 44, hy + 30))
        elif run:
            a = -sg * sw * 0.9
            arms[sg] = ((sx, sy), (sx + sg * 20 + math.sin(a) * 60, sy + 100), (sx + sg * 10 + math.sin(a) * 110, sy + 40))
        else:
            arms[sg] = ((sx, sy), (sx + sg * 18, sy + 130), (sx + sg * 16, sy + 250))

    def armf(d, s):
        for sg in (-1, 1):
            d.line([(x * s, y * s) for x, y in arms[sg]], fill=255, width=int(36 * s), joint="curve")

    def hands(d, s):
        for sg in (-1, 1):
            x, y = arms[sg][2]
            d.ellipse([(x - 17) * s, (y - 17) * s, (x + 17) * s, (y + 17) * s], fill=255)

    def head(d, s):
        d.rectangle([(cx - 22) * s, (hy + 20) * s, (cx + 22) * s, (by + 10) * s], fill=255)
        d.ellipse([(cx - 56) * s, (hy - 76) * s, (cx + 56) * s, (hy + 70) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 60) * s, (hy - 86) * s, (cx + 60) * s, (hy + 30) * s], 180, 360, fill=255)
        d.polygon(P_((cx - 60, hy - 30), (cx - 58, hy + 10), (cx - 30, hy - 46), (cx + 20, hy - 54), (cx + 58, hy + 6), (cx + 60, hy - 30), s=s), fill=255)
        d.line([((cx + 40) * s, (hy - 70) * s), ((cx + 90) * s, (hy - 40 + 30 * sw) * s), ((cx + 96) * s, (hy + 60) * s)], fill=255, width=int(26 * s), joint="curve")

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if not sit:
        img.alpha_composite(shade(legs, (w, h), MLEG, 22, rim_strength=1.1))
        img.alpha_composite(shade(shoes, (w, h), (60, 50, 44), 10))
    if sit or phone > 0:
        img.alpha_composite(shade(body, (w, h), MJACK, 44, rim_strength=1.1))
        img.alpha_composite(shade(armf, (w, h), MJACK, 14))
    else:
        img.alpha_composite(shade(armf, (w, h), MJACK, 14))
        img.alpha_composite(shade(body, (w, h), MJACK, 44, rim_strength=1.1))
    bd = ImageDraw.Draw(img)
    bd.line([(cx, by + 10), (cx, (500 if not sit else 700) - 6)], fill=(120, 90, 20, 255), width=4)   # zip
    if sit:
        img.alpha_composite(shade(legs, (w, h), MLEG, 22, rim_strength=1.1))
        img.alpha_composite(shade(shoes, (w, h), (60, 50, 44), 10))
    img.alpha_composite(shade(hair, (w, h), HAIR, 12, rim_strength=1.1))
    img.alpha_composite(shade(head, (w, h), MSKIN, 26))
    img.alpha_composite(shade(hair, (w, h), HAIR, 12, rim_strength=1.1).crop((0, 0, w, int(hy - 20))), (0, 0))
    d = ImageDraw.Draw(img)
    lk = look
    for sg in (-1, 1):
        ex_, ey_ = cx + sg * 22, hy + 4 - (8 if lk > 0 else 0) + (10 if phone > 0 and lk <= 0 else 0)
        r_ = 11 + 4 * max(0, gasp)
        d.ellipse([ex_ - r_, ey_ - r_ * .8, ex_ + r_, ey_ + r_ * .8], fill=(240, 236, 230, 255))
        px = ex_ + (-5 if lk < 0 else 0)
        py = ey_ - 5 * max(0, lk) + (4 if phone > 0 and lk <= 0 else 0)
        d.ellipse([px - 5, py - 6, px + 5, py + 4], fill=(15, 10, 10, 255))
        d.line([(ex_ - 14, ey_ - 20 - 6 * max(0, gasp)), (ex_ + 14, ey_ - 18 - 3 * sg - 6 * max(0, gasp))], fill=(20, 12, 10, 255), width=5)
    if gasp > 0.3 or shout > 0.3:
        o = max(gasp, shout)
        d.ellipse([cx - 11, hy + 38, cx + 11, hy + 38 + 26 * o], fill=(60, 18, 18, 255))
    elif gasp >= 0:
        d.line([(cx - 12, hy + 44), (cx + 12, hy + 44)], fill=(90, 40, 34, 255), width=4)
    img.alpha_composite(shade(hands, (w, h), MSKIN, 8))
    if (pose == "sit" and phone >= 0) or phone > 0:      # the phone (back side to us) between her hands
        px, py = cx, by + 128
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([px - 34, py - 54, px + 34, py + 54], 10, fill=(20, 22, 26, 255), outline=(80, 80, 90, 255), width=3)
        d.ellipse([px - 20, py - 44, px - 8, py - 32], fill=(60, 60, 70, 255))
        img.alpha_composite(shade(hands, (w, h), MSKIN, 8))
    if phone > 0:                                             # cold screen light on her face from below
        a = np.asarray(img, np.float32).copy()
        lm = light_map(w, h, cx, by + 60, 170, 0.0)
        a[..., 0] *= 1 + 0.25 * lm * phone; a[..., 1] *= 1 + 0.45 * lm * phone; a[..., 2] *= 1 + 0.75 * lm * phone
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    if scale != 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    out = (img, cx * scale, 890 * scale)
    _MF[q] = out
    return out


def put_sprite(img, spr, x, y, fx, fy, alpha=1.0):
    if alpha < 1:
        spr = with_alpha(spr, alpha)
    img.alpha_composite(spr, (int(x - fx), int(y - fy)))
    return img


# ============================================================ the little girl in red
_GL = {}


def girl(pose="stand", tilt=0.0, phase=0.0, smile=0.0):
    """The little girl in red: a small child (about 2/3 of Mei's height) in a long-sleeved red dress to the knees and red
    cloth shoes, long straight black hair with heavy bangs, a pale face with all-black eyes (red glints drawn by
    put_girl), arms a little too long. pose "stand" (front, arms hanging, too still), "back" (walking up the steps,
    seen from behind), "point"? no. tilt: head tilt in degrees (wrong angle). smile 0..1: a thin smile far too wide.
    Returns (RGBA, feet_x, feet_y, [eye points])."""
    key = (pose, round(tilt / 5) * 5, round(phase * 8) % 8, round(smile, 1))
    if key in _GL:
        return _GL[key]
    w, h = 440, 900
    cx = w / 2
    hy = 150
    back = pose == "back"
    ph = 2 * math.pi * key[2] / 8
    lift = {-1: max(0, math.sin(ph)) * 34 * back, 1: max(0, -math.sin(ph)) * 34 * back}

    def legs(d, s):
        for sg in (-1, 1):
            d.line([((cx + sg * 24) * s, 600 * s), ((cx + sg * 24) * s, (850 - lift[sg]) * s)], fill=255, width=int(30 * s))

    def shoes(d, s):
        for sg in (-1, 1):
            y = 856 - lift[sg]
            d.ellipse([(cx + sg * 24 - 28) * s, (y - 16) * s, (cx + sg * 24 + 28) * s, (y + 14) * s], fill=255)

    def dress(d, s):
        d.polygon(P_((cx - 66, 236), (cx + 66, 236), (cx + 80, 420), (cx + 120, 640), (cx - 120, 640), (cx - 80, 420), s=s), fill=255)
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 56 - 28) * s, 222 * s, (cx + sg * 56 + 28) * s, 282 * s], fill=255)

    def sleeves(d, s):
        for sg in (-1, 1):
            d.line([((cx + sg * 62) * s, 252 * s), ((cx + sg * 92) * s, 420 * s), ((cx + sg * 100) * s, 560 * s)], fill=255, width=int(34 * s), joint="curve")

    def hands(d, s):
        for sg in (-1, 1):
            x, y = cx + sg * 102, 590
            d.ellipse([(x - 15) * s, (y - 22) * s, (x + 15) * s, (y + 22) * s], fill=255)
            for f in range(3):
                d.line([((x + sg * (f - 1) * 7) * s, (y + 10) * s), ((x + sg * (f - 1) * 9) * s, (y + 62 + f * 4) * s)], fill=255, width=int(7 * s))

    def head(d, s):
        d.rectangle([(cx - 16) * s, (hy + 40) * s, (cx + 16) * s, 240 * s], fill=255)
        d.ellipse([(cx - 52) * s, (hy - 64) * s, (cx + 52) * s, (hy + 66) * s], fill=255)

    def back_hair(d, s):
        d.polygon(P_((cx - 66, hy - 40), (cx + 66, hy - 40), (cx + 80, 470), (cx + 30, 500), (cx - 30, 496), (cx - 80, 466), s=s), fill=255)
        d.ellipse([(cx - 64) * s, (hy - 84) * s, (cx + 64) * s, (hy + 40) * s], fill=255)

    def front_hair(d, s):
        d.pieslice([(cx - 62) * s, (hy - 84) * s, (cx + 62) * s, (hy + 30) * s], 180, 360, fill=255)
        d.polygon(P_((cx - 62, hy - 30), (cx + 62, hy - 30), (cx + 60, hy - 4), (cx - 60, hy - 4), s=s), fill=255)    # heavy bangs to the brows
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 40, hy - 40), (cx + sg * 64, hy - 40), (cx + sg * 76, 440), (cx + sg * 46, 456), (cx + sg * 44, hy + 30), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if not back:
        img.alpha_composite(shade(back_hair, (w, h), HAIR, 14, rim_strength=1.2))
    img.alpha_composite(shade(legs, (w, h), PALE, 10))
    img.alpha_composite(shade(shoes, (w, h), RED2, 10, rim=(255, 90, 70)))
    img.alpha_composite(shade(sleeves, (w, h), RED, 14, rim=(255, 120, 90)))
    img.alpha_composite(shade(hands, (w, h), PALE, 6))
    img.alpha_composite(shade(dress, (w, h), RED, 40, rim=(255, 120, 90), rim_strength=1.1))
    dd = ImageDraw.Draw(img)
    dd.line([(cx - 118, 630), (cx + 118, 630)], fill=(90, 6, 12, 255), width=6)          # dark hem
    eyes = []
    if back:
        img.alpha_composite(shade(back_hair, (w, h), HAIR, 14, rim_strength=1.2))
    else:
        hd = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        hd.alpha_composite(shade(head, (w, h), PALE, 26))
        d = ImageDraw.Draw(hd)
        eyes = [(cx - 20, hy + 12), (cx + 20, hy + 12)]
        for ex_, ey_ in eyes:
            d.ellipse([ex_ - 13, ey_ - 11, ex_ + 13, ey_ + 11], fill=(8, 4, 6, 255))     # all-black eyes
        if smile > 0.3:
            d.arc([cx - 40, hy + 14, cx + 40, hy + 56], 15, 165, fill=(30, 6, 8, 255), width=4)
            for sg in (-1, 1):
                d.line([(cx + sg * 38, hy + 36), (cx + sg * 48, hy + 24)], fill=(30, 6, 8, 255), width=4)
        else:
            d.line([(cx - 8, hy + 44), (cx + 8, hy + 44)], fill=(150, 120, 120, 255), width=3)
        hd.alpha_composite(shade(front_hair, (w, h), HAIR, 12, rim_strength=1.3))
        if tilt:
            hd = hd.rotate(tilt, resample=Image.BICUBIC, center=(cx, 230))
            a = math.radians(-tilt)
            eyes = [(cx + (x - cx) * math.cos(a) - (y - 230) * math.sin(a), 230 + (x - cx) * math.sin(a) + (y - 230) * math.cos(a)) for x, y in eyes]
        img.alpha_composite(hd)
    out = (img, cx, 866, eyes)
    _GL[key] = out
    return out


def put_girl(img, x, y, scale, t, pose="stand", tilt=0.0, phase=0.0, smile=0.0, eyes=1.0, aura=0.0, alpha=1.0, dark=0.0, blur=0):
    body, ax, ay, ee = girl(pose, tilt, phase, smile)
    g = body.resize((max(1, int(body.width * scale)), max(1, int(body.height * scale))), Image.LANCZOS)
    if dark > 0:
        g = tint(g, (1 - 0.8 * dark, 1 - 0.85 * dark, 1 - 0.85 * dark))
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
    if eyes > 0 and ee:
        k = eyes * alpha * (0.65 + 0.35 * math.sin(t * 5) ** 2)
        for ex, ey in ee:
            pin(img, gx + ex * scale, gy + ey * scale, k, max(0.15, scale))
    return img


def pin(img, x, y, k, sc=1.0):
    """A red pin-point glint inside an all-black eye (smaller and colder than the usual glowing eyes)."""
    r = max(2.0, 4.5 * sc); R = int(max(10, 40 * sc))
    spr = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    ImageDraw.Draw(spr).ellipse([R - r, R - r, R + r, R + r], fill=(255, 40, 30, int(255 * min(1, k))))
    g = spr.filter(ImageFilter.GaussianBlur(R / 5))
    img.alpha_composite(g, (int(x - R), int(y - R))); img.alpha_composite(spr, (int(x - R), int(y - R)))


_GF = {}


def girl_face(mode="still", inv=False):
    """Close-up for the jump scares: a small, bone-pale child's face under heavy black bangs, long straight hair either
    side, huge all-black eyes; mode "still" = no expression, "smile" = a thin grin far too wide, "scream" = a dark open
    mouth (no teeth, no gore); the red dress collar at the bottom. Face centre (450, 470)."""
    k = (mode, inv)
    if k in _GF:
        return _GF[k]
    w, h = 900, 1100
    cx, cy = 450, 470

    def face(d, s):
        d.ellipse([(cx - 190) * s, (cy - 250) * s, (cx + 190) * s, (cy + 270) * s], fill=255)

    def neck(d, s):
        d.rectangle([(cx - 70) * s, (cy + 200) * s, (cx + 70) * s, h * s], fill=255)

    def collar(d, s):
        d.polygon(P_((cx - 420, h), (cx - 300, cy + 430), (cx + 300, cy + 430), (cx + 420, h), s=s), fill=255)

    def hair(d, s):
        r = np.random.default_rng(91)
        d.pieslice([(cx - 250) * s, (cy - 360) * s, (cx + 250) * s, (cy + 60) * s], 180, 360, fill=255)
        d.rectangle([(cx - 230) * s, (cy - 160) * s, (cx + 230) * s, (cy - 92) * s], fill=255)       # bangs
        for x in range(cx - 228, cx + 230, 14):                                   # a straight-cut fringe, a few strands longer
            d.rectangle([x * s, (cy - 100) * s, (x + 15) * s, (cy - 86 + r.uniform(0, 14) + (40 if r.random() < 0.12 else 0)) * s], fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 150, cy - 300), (cx + sg * 260, cy - 180), (cx + sg * 300, cy + 680), (cx + sg * 170, cy + 700), (cx + sg * 176, cy - 60), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(neck, (w, h), PALE, 40))
    img.alpha_composite(shade(collar, (w, h), RED, 60, rim=(255, 120, 90)))
    img.alpha_composite(shade(face, (w, h), PALE, 110, rim_strength=0.9))
    d = ImageDraw.Draw(img)
    eyes = [(cx - 82, cy + 0), (cx + 82, cy + 0)]
    for ex, ey in eyes:
        d.ellipse([ex - 62, ey - 52, ex + 62, ey + 52], fill=(6, 2, 4, 255))
    d.polygon([(cx - 10, cy + 76), (cx + 10, cy + 76), (cx + 14, cy + 104), (cx - 14, cy + 104)], fill=(190, 180, 176, 255))
    if mode == "scream":
        d.ellipse([cx - 60, cy + 140, cx + 60, cy + 300], fill=(22, 4, 6, 255))
        d.ellipse([cx - 42, cy + 160, cx + 42, cy + 280], fill=(6, 0, 2, 255))
    elif mode == "smile":
        d.arc([cx - 150, cy + 70, cx + 150, cy + 190], 18, 162, fill=(28, 6, 8, 255), width=8)
        for sg in (-1, 1):
            d.line([(cx + sg * 142, cy + 152), (cx + sg * 166, cy + 118)], fill=(28, 6, 8, 255), width=7)
    else:
        d.line([(cx - 26, cy + 172), (cx + 26, cy + 172)], fill=(150, 120, 120, 255), width=6)
    img.alpha_composite(shade(hair, (w, h), HAIR, 24, rim_strength=1.3))
    if inv:
        img = img.rotate(180, resample=Image.BICUBIC, center=(cx, cy))
        eyes = [(2 * cx - x, 2 * cy - y) for x, y in eyes]
    _GF[k] = (img, eyes)
    return _GF[k]


def put_gface(img, x, y, scale, t, mode="still", tilt=0.0, aura=0.7, alpha=1.0, inv=False, eyes=1.0):
    fimg, ee = girl_face(mode, inv)
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
            pin(img, gx + rx * scale, gy + ry * scale, k, scale * 2.4)
    return img


def gface_full(t, t0, mode="smile", inv=False, scale=1.25, y=880, bg=(6, 1, 2), tilt=0.0, x=540):
    img = Image.new("RGBA", (W, H), bg + (255,))
    return put_gface(img, x, y + 120 * ss(t, t0, t0 + 0.15) * (1 if not inv else -1), scale, t, mode=mode, aura=0.9, inv=inv, tilt=tilt)


def small_hand(img, x, y, sc, ang=0.0, curl=1.0):
    """A small pale hand with fingers a little too long, curling around an edge (pointing along ang)."""
    d = ImageDraw.Draw(img)
    c, s_ = math.cos(ang), math.sin(ang)
    def P(u, v):
        return (x + (u * c - v * s_) * sc, y + (u * s_ + v * c) * sc)
    d.ellipse([x - 26 * sc, y - 22 * sc, x + 26 * sc, y + 22 * sc], fill=PALE + (255,), outline=(30, 20, 22, 255), width=3)
    for f in range(4):
        v = -18 + f * 12
        pts = [P(10, v), P(60, v * 1.1), P(60 + 40 * curl, v * 1.1 + 34 * curl)]
        d.line(pts, fill=(30, 20, 22, 255), width=int(13 * sc) + 4, joint="curve")
        d.line(pts, fill=PALE + (255,), width=int(13 * sc), joint="curve")
    return img


# ============================================================ set pieces
def fern_frond(d, x0, y0, a, ln, droop, s=1, wd=0.17, teeth=14):
    """One long fern frond: a filled, tapering, serrated leaf shape along an arching curve."""
    pts = []
    for j in range(13):
        u = j / 12
        pts.append((x0 + math.cos(a) * ln * u, y0 + math.sin(a) * ln * u * 0.75 + droop * ln * u * u))
    left, right = [], []
    for j in range(len(pts)):
        u = j / 12
        if j < len(pts) - 1:
            dx, dy = pts[j + 1][0] - pts[j][0], pts[j + 1][1] - pts[j][1]
        L_ = math.hypot(dx, dy) + 1e-6
        nx, ny = -dy / L_, dx / L_
        ww = ln * wd * math.sin(math.pi * min(1, u * 1.05)) * (0.4 + 0.6 * (1 - u))
        for sub in (0.0, 0.5):
            k = ww * (1.0 if sub == 0 else 0.55)
            left.append((pts[j][0] + nx * k + dx * sub, pts[j][1] + ny * k + dy * sub + k * 0.2))
            right.append((pts[j][0] - nx * k + dx * sub, pts[j][1] - ny * k + dy * sub + k * 0.2))
    d.polygon([(p[0] * s, p[1] * s) for p in left + right[::-1]], fill=255)


def tree_fern(d, x, by, hgt, s=1, rnd=None, lean=0.0):
    """A Taiwanese tree fern (Cyathea): a thin dark trunk and a crown of long arching, feathery fronds."""
    rnd = rnd or np.random.default_rng(1)
    tx, ty = x + lean * hgt, by - hgt
    d.line([(x * s, by * s), ((x + lean * hgt * .5) * s, (by - hgt * .5) * s), (tx * s, ty * s)], fill=255, width=int(max(3, hgt / 20) * s), joint="curve")
    n = 10
    for k in range(n):
        a = -math.pi * (0.02 + 0.96 * k / (n - 1)) + rnd.uniform(-0.1, 0.1)
        ln = hgt * rnd.uniform(0.45, 0.62)
        fern_frond(d, tx, ty, a, ln, 0.55, s)
    d.ellipse([(tx - hgt * .05) * s, (ty - hgt * .04) * s, (tx + hgt * .05) * s, (ty + hgt * .05) * s], fill=255)


def ground_ferns(d, pts, size, s=1, rnd=None, n=3):
    """Low fern clumps along a list of (x, y, scale) points."""
    rnd = rnd or np.random.default_rng(2)
    for x, y, sc in pts:
        for k in range(n):
            a = -math.pi * rnd.uniform(0.1, 0.9)
            fern_frond(d, x, y, a, size * sc * rnd.uniform(0.6, 1.0), 0.7, s, wd=0.2)


def ridge_mask(w, h, yb, amp, seed, peaks=5):
    r = np.random.default_rng(seed)
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    xs = np.linspace(-20, w + 20, 80)
    ph = r.uniform(0, 6, 3)
    ys = yb - amp * (0.55 * np.sin(xs / w * peaks * 3.1 + ph[0]) + 0.3 * np.sin(xs / w * peaks * 7.3 + ph[1]) + 0.15 * np.sin(xs / w * 23 + ph[2]))
    d.polygon([(x, y) for x, y in zip(xs, ys)] + [(w + 20, h), (-20, h)], fill=255)
    return m


def dusk_sky(sun=(640, 790), night=False):
    if night:
        a = vgrad((2, 3, 8), (8, 8, 16), (22, 16, 24), ym=0.5)
        r2 = np.random.default_rng(3)
        for _ in range(60):
            x, y = int(r2.uniform(0, W)), int(r2.uniform(0, 700))
            a[y:y + 2, x:x + 2] += r2.uniform(20, 60)
        return a
    a = vgrad((6, 6, 14), (54, 22, 34), (170, 62, 42), ym=0.36)
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.sqrt((xx - sun[0]) ** 2 + (yy - sun[1]) ** 2)
    a += np.exp(-dd / 260)[..., None] * np.array([170, 60, 30], np.float32)
    disc = np.clip((64 - dd) / 2.5, 0, 1)[..., None]
    a = a * (1 - disc) + np.array([255, 170, 120], np.float32) * disc
    return a


class Path:
    """A path climbing away from the camera: centre x(u), y(u), half width hw(u) for u in 0 (near) .. 1 (far)."""
    def __init__(self, vy=880, x0=540, wig=70, hw0=540):
        self.vy, self.x0, self.wig, self.hw0 = vy, x0, wig, hw0

    def y(self, u):
        return self.vy + (H + 60 - self.vy) * (1 - u) ** 1.7

    def x(self, u):
        return self.x0 + self.wig * math.sin(2.4 * u + 0.4) - self.wig * math.sin(0.4)

    def hw(self, u):
        return 26 + self.hw0 * (1 - u) ** 1.5

    def at(self, u, side=0.0):
        """screen x, y and a person scale (a 890 px tall sprite) for a spot on the path."""
        return self.x(u) + side * self.hw(u), self.y(u), self.hw(u) / 800


RIB = [(230, 200, 60), (238, 236, 226), (230, 120, 160), (80, 150, 230), (240, 150, 40), (238, 236, 226)]


def ribbon(img, x, y, ln, t, col, sc=1.0, seed=0):
    """A hiker's cloth trail ribbon tied on a branch, fluttering."""
    d = ImageDraw.Draw(img)
    pts_l, pts_r = [], []
    wd = 10 * sc
    for j in range(8):
        u = j / 7
        sx = x + (8 * math.sin(t * 4 + j * 0.9 + seed) * u + 10 * u) * sc
        sy = y + ln * u * sc
        pts_l.append((sx - wd / 2, sy)); pts_r.append((sx + wd / 2, sy))
    d.polygon(pts_l + pts_r[::-1], fill=tuple(int(c) for c in col) + (255,))
    d.ellipse([x - 5 * sc, y - 5 * sc, x + 5 * sc, y + 5 * sc], fill=tuple(int(c * .6) for c in col) + (255,))


class Trail:
    """Stone-and-timber steps climbing into the mountain forest near Taichung, seen from below: a low red sun over a sea
    of clouds between blue-black ridges (dusk) or a starless night, giant tree ferns and tall cedars on both banks,
    mossy rocks, hikers' ribbons on the branches, mist between the layers and blurred fern fronds in front."""
    def __init__(self, night=False):
        r = np.random.default_rng(191 if not night else 192)
        self.night = night
        self.P = P = Path()
        a = dusk_sky(night=night)
        img = to_img(a)
        cols = [(46, 28, 40), (32, 20, 30), (22, 14, 22)] if not night else [(14, 14, 22), (10, 10, 16), (7, 7, 12)]
        for k, (yb, amp) in enumerate(((830, 70), (880, 60), (930, 50))):
            img.alpha_composite(colorize(ridge_mask(W, H, yb, amp, 30 + k).filter(ImageFilter.GaussianBlur(2 - k * .6)), cols[k]))
            if not night:
                fog(img, 0.0, 0.5 - 0.12 * k, yb - 30, yb + 70, col=(200, 110, 90), off=k * 140)
        self.sky = img
        # banks + forest walls (left and right of the path)
        m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
        us = np.linspace(0, 1, 60)
        left = [(P.x(u) - P.hw(u), P.y(u)) for u in us]
        right = [(P.x(u) + P.hw(u), P.y(u)) for u in us]
        d.polygon(left + [(-10, P.y(1) - 40), (-10, H + 20)], fill=255)
        d.polygon(right + [(W + 10, P.y(1) - 40), (W + 10, H + 20)], fill=255)
        self.banks = colorize(m, (30, 22, 22) if not night else (12, 11, 14))
        # the steps
        st = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        N = 30
        for i in range(N - 1, -1, -1):
            u0, u1 = i / N, (i + 1) / N
            um = u0 + (u1 - u0) * 0.42
            def quad(ua, ub):
                return [(P.x(ua) - P.hw(ua), P.y(ua)), (P.x(ua) + P.hw(ua), P.y(ua)), (P.x(ub) + P.hw(ub), P.y(ub)), (P.x(ub) - P.hw(ub), P.y(ub))]
            lit = 1.0 - 0.5 * u0
            tread = (96, 86, 78) if not night else (40, 40, 46)
            riser = (44, 36, 34) if not night else (20, 20, 24)
            sd.polygon(quad(u0, um), fill=tuple(int(c * lit) for c in riser) + (255,))
            sd.polygon(quad(um, u1), fill=tuple(int(c * lit) for c in tread) + (255,))
            sd.line([(P.x(um) - P.hw(um), P.y(um)), (P.x(um) + P.hw(um), P.y(um))], fill=(96, 60, 36, 255) if not night else (40, 30, 26, 255), width=max(1, int(10 * (1 - u0) ** 1.5)))
            for k in range(3):                                                         # stone joints
                xx = P.x(u0) + P.hw(u0) * r.uniform(-0.8, 0.8)
                sd.line([(xx, P.y(u0)), (xx + r.uniform(-4, 4), P.y(um))], fill=(30, 24, 22, 255), width=max(1, int(4 * (1 - u0))))
        self.steps = st
        # vegetation on the banks: far to near
        vm_far = Image.new("L", (W, H), 0); vf = ImageDraw.Draw(vm_far)
        vm_mid = Image.new("L", (W, H), 0); vmd = ImageDraw.Draw(vm_mid)
        vm_near = Image.new("L", (W, H), 0); vn = ImageDraw.Draw(vm_near)
        self.anchors = []
        for k in range(26):
            u = r.uniform(0.55, 0.98); side = r.choice([-1, 1])
            x = P.x(u) + side * (P.hw(u) + r.uniform(10, 260) * (1 - u) + 20)
            tree_fern(vf, x, P.y(u) + 10, r.uniform(120, 260) * (1.2 - u), 1, r, lean=r.uniform(-.15, .15))
        for k in range(5):                                                              # far cedars
            u = r.uniform(0.75, 0.95); side = [-1, 1][k % 2]
            x = P.x(u) + side * (P.hw(u) + r.uniform(120, 320))
            wd = r.uniform(8, 16)
            vf.polygon([(x - wd, P.y(u) + 10), (x + wd, P.y(u) + 10), (x + wd * .5, -10), (x - wd * .5, -10)], fill=255)
        for k in range(10):
            u = r.uniform(0.25, 0.6); side = [-1, 1][k % 2]
            x = P.x(u) + side * (P.hw(u) + r.uniform(30, 200))
            hgt = r.uniform(380, 620) * (1.15 - u)
            tree_fern(vmd, x, P.y(u) + 20, hgt, 1, r, lean=side * r.uniform(0.02, 0.15))
            if k < 8:
                self.anchors.append((x - side * hgt * 0.25, P.y(u) - hgt * 0.78, 1.15 - u, k))
        ground_ferns(vmd, [(P.x(u) + sd_ * (P.hw(u) + 10), P.y(u) + 6, 1.1 - u) for u in np.linspace(0.05, 0.85, 22) for sd_ in (-1, 1)], 170, 1, r, 3)
        for k, (x, wd) in enumerate(((-10, 70), (1090, 80))):        # two near cedars at the edges
            vmd.polygon([(x - wd, H), (x + wd, H), (x + wd * .6, -10), (x - wd * .6, -10)], fill=255)
        for k in range(6):
            u = r.uniform(0.0, 0.25); side = [-1, 1][k % 2]
            x = P.x(u) + side * (P.hw(u) + r.uniform(40, 140))
            tree_fern(vn, x, P.y(u) + 60, r.uniform(700, 900), 1, r, lean=side * 0.12)
        fc = (16, 14, 16) if not night else (6, 6, 8)
        self.far = colorize(vm_far.filter(ImageFilter.GaussianBlur(1.6)), (34, 24, 30) if not night else (10, 10, 14))
        self.mid = shade(lambda dd, s_: dd.bitmap((0, 0), vm_mid.resize((W * s_, H * s_)), fill=255), (W, H), (40, 34, 32) if not night else (14, 14, 16), 14, rim=(255, 90, 60) if not night else (120, 130, 160), rim_strength=0.8)
        self.near = colorize(vm_near, fc)
        rocks = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        def rk(dd, s_):
            for k in range(14):
                u = r.uniform(0.02, 0.5); side = r.choice([-1, 1])
                x = P.x(u) + side * (P.hw(u) + r.uniform(-10, 60) * (1 - u)); y = P.y(u) + 10
                rr = r.uniform(40, 110) * (1 - u)
                dd.ellipse([(x - rr) * s_, (y - rr * .7) * s_, (x + rr) * s_, (y + rr * .3) * s_], fill=255)
        rocks.alpha_composite(shade(rk, (W, H), (52, 58, 44) if not night else (20, 22, 22), 20, rim=(255, 90, 60)))
        self.rocks = rocks
        fg = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(fg)
        for x, y in ((-120, 1900), (1180, 1880), (-60, 300), (1150, 260)):
            tree_fern(gd, x, y + 500, 900, 1, r, lean=0.0)
        self.fg = colorize(fg, (6, 4, 6)).filter(ImageFilter.GaussianBlur(10))
        self.sun = (640, 790)

    def frame(self, t, cam=0.0, far_extras=None, path_extras=None, fogk=0.35, red=0.0, veil=0.0, ribbons=True, sun=1.0):
        o = lambda par: int(-cam * par)
        img = self.sky.copy()
        if cam:
            img = img.transform((W, H), Image.AFFINE, (1, 0, cam * 0.05, 0, 1, 0))
        img.alpha_composite(self.far, (o(0.2), 0))
        fog(img, t, fogk, 760, 1040, speed=8, col=(190, 100, 90) if not self.night else (90, 90, 110))
        img.alpha_composite(self.banks, (o(0.5), 0))
        img.alpha_composite(self.steps, (o(0.5), 0))
        img.alpha_composite(self.rocks, (o(0.6), 0))
        for fn in (far_extras or []):
            img = fn(img, t) or img
        img.alpha_composite(self.mid, (o(0.6), 0))
        if ribbons:
            for x, y, sc, k in self.anchors:
                col = np.array(RIB[k % len(RIB)], np.float32) * (1 - red) + np.array((200, 24, 28), np.float32) * red
                if self.night:
                    col = col * 0.45
                ribbon(img, x + o(0.6), y, 70, t, col, sc, seed=k)
        fog(img, t, fogk * 0.7, 1100, 1500, speed=12, col=(170, 90, 90) if not self.night else (80, 80, 96), off=300)
        for fn in (path_extras or []):
            img = fn(img, t) or img
        img.alpha_composite(self.near, (o(1.0), 0))
        img.alpha_composite(self.fg, (o(1.5), 0))
        if veil > 0:
            lay = Image.new("RGBA", (W, H), (150, 130, 130, int(200 * veil)) if not self.night else (60, 60, 70, int(200 * veil)))
            img.alpha_composite(lay)
        bokeh_particles(img, 12, 191, t, color=(255, 200, 150), size=(2, 6), blur=(0, 3), area=(0, 500, W, 1600), drift=(5, -4))
        return img


_TR = {}


def trail(night=False):
    if night not in _TR:
        _TR[night] = Trail(night)
    return _TR[night]


class Shrine:
    """A tiny Earth God (Tudi Gong) shrine beside the trail: red brick walls on a stone base, a swallowtail roof with
    curled ridge ends and a pearl, a gold plaque "福德祠", red couplet strips, the small seated god inside between two red
    candle lamps, a bronze incense burner in front, two red lanterns on the eaves; dusk forest behind."""
    def __init__(self):
        r = np.random.default_rng(193)
        img = to_img(dusk_sky(sun=(220, 640)))
        img.alpha_composite(colorize(ridge_mask(W, H, 760, 60, 41).filter(ImageFilter.GaussianBlur(1.5)), (40, 24, 34)))
        fog(img, 0.0, 0.5, 700, 820, col=(200, 110, 90))
        vm = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(vm)
        for k in range(7):
            tree_fern(vd, r.uniform(-60, W + 60), r.uniform(1050, 1150), r.uniform(380, 600), 1, r, lean=r.uniform(-.12, .12))
        for x, wd in ((120, 34), (980, 40), (840, 18)):
            vd.polygon([(x - wd, 1200), (x + wd, 1200), (x + wd * .6, -10), (x - wd * .6, -10)], fill=255)
        img.alpha_composite(colorize(vm.filter(ImageFilter.GaussianBlur(1.2)), (28, 20, 24)))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1180, W, H], fill=(34, 26, 24, 255))
        for k in range(6):                                                    # steps going up on the left
            y = 1500 - k * 60; x0 = 40 + k * 30
            d.polygon([(x0, y), (x0 + 260 - k * 24, y), (x0 + 250 - k * 24, y - 30), (x0 + 10, y - 30)], fill=(70, 62, 56, 255))
            d.line([(x0, y), (x0 + 260 - k * 24, y)], fill=(96, 60, 36, 255), width=6)
        cx = 690; self.cx = cx

        def base(dd, s):
            dd.rectangle([(cx - 250) * s, 1440 * s, (cx + 250) * s, 1520 * s], fill=255)

        def body(dd, s):
            dd.rectangle([(cx - 190) * s, 1040 * s, (cx + 190) * s, 1440 * s], fill=255)

        def roof(dd, s):
            dd.polygon(P_((cx - 250, 1060), (cx + 250, 1060), (cx + 200, 950), (cx - 200, 950), s=s), fill=255)
            dd.rectangle([(cx - 210) * s, 920 * s, (cx + 210) * s, 955 * s], fill=255)
            for sg in (-1, 1):                                                # swallowtail ridge ends
                dd.polygon(P_((cx + sg * 190, 920), (cx + sg * 210, 955), (cx + sg * 290, 870), (cx + sg * 300, 840), (cx + sg * 262, 880), s=s), fill=255)
                dd.polygon(P_((cx + sg * 250, 1060), (cx + sg * 210, 1040), (cx + sg * 290, 1010), s=s), fill=255)
            dd.ellipse([(cx - 22) * s, 880 * s, (cx + 22) * s, 924 * s], fill=255)

        def burner(dd, s):
            dd.ellipse([(cx - 80) * s, 1460 * s, (cx + 80) * s, 1560 * s], fill=255)
            dd.rectangle([(cx - 90) * s, 1450 * s, (cx + 90) * s, 1480 * s], fill=255)
            for sg in (-1, 0, 1):
                dd.rectangle([(cx + sg * 56 - 8) * s, 1540 * s, (cx + sg * 56 + 8) * s, 1590 * s], fill=255)

        img.alpha_composite(shade(base, (W, H), (90, 86, 80), 16))
        img.alpha_composite(shade(body, (W, H), (150, 52, 38), 60, rim=(255, 120, 70)))
        bd = ImageDraw.Draw(img)
        for k, y in enumerate(range(1060, 1440, 22)):                         # brick courses
            bd.line([(cx - 190, y), (cx + 190, y)], fill=(110, 36, 28, 255), width=2)
            for x in range(cx - 190 + (k % 2) * 22, cx + 190, 44):
                bd.line([(x, y), (x, y + 22)], fill=(110, 36, 28, 255), width=2)
        bd.rectangle([cx - 92, 1180, cx + 92, 1440], fill=(26, 8, 8, 255))      # the doorway
        bd.pieslice([cx - 92, 1110, cx + 92, 1250], 180, 360, fill=(26, 8, 8, 255))
        for sg in (-1, 1):                                                     # red couplets
            bd.rectangle([cx + sg * 140 - 20, 1110, cx + sg * 140 + 20, 1400], fill=(200, 30, 30, 255))
            for k in range(5):
                bd.ellipse([cx + sg * 140 - 6, 1140 + k * 52, cx + sg * 140 + 6, 1152 + k * 52], fill=(220, 180, 80, 255))
        bd.rectangle([cx - 110, 1066, cx + 110, 1120], fill=(30, 14, 12, 255), outline=(220, 180, 80, 255), width=4)
        bd.text((cx, 1093), "福德祠", font=ImageFont.truetype(CJK, 40), fill=(230, 190, 90, 255), anchor="mm")
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))                           # the little seated god
        def god(dd, s):
            dd.ellipse([(cx - 30) * s, 1250 * s, (cx + 30) * s, 1312 * s], fill=255)
            dd.polygon(P_((cx - 60, 1420), (cx + 60, 1420), (cx + 44, 1310), (cx - 44, 1310), s=s), fill=255)
        g.alpha_composite(shade(god, (W, H), (190, 140, 60), 20, rim=(255, 140, 70)))
        gd2 = ImageDraw.Draw(g)
        gd2.polygon([(cx - 20, 1296), (cx + 20, 1296), (cx, 1350)], fill=(235, 230, 220, 255))   # white beard
        gd2.rectangle([cx - 34, 1236, cx + 34, 1256], fill=(40, 30, 20, 255))                     # cap
        img.alpha_composite(g)
        img.alpha_composite(shade(roof, (W, H), (120, 40, 28), 30, rim=(255, 120, 70)))
        rd = ImageDraw.Draw(img)
        for x in range(cx - 240, cx + 250, 26):
            rd.line([(x, 1058), (cx + (x - cx) * 0.8, 954)], fill=(80, 24, 18, 255), width=3)
        img.alpha_composite(shade(burner, (W, H), (150, 110, 50), 26, rim=(255, 160, 80)))
        self.base = img
        self.lamps = [(cx - 60, 1330), (cx + 60, 1330)]
        self.lanterns = [(cx - 230, 1110), (cx + 230, 1110)]
        self.incense = (cx, 1450)

    def frame(self, t, extras=None, fogk=0.3, smoke=1.0, dim=1.0):
        a = to_arr(self.base)
        fl = 0.85 + 0.15 * (math.sin(t * 17) > -0.7)
        for x, y in self.lamps:
            add_glow(a, gsp(70, (255, 90, 50)), x, y, 0.9 * fl * dim)
            add_glow(a, gsp(12, (255, 220, 160)), x, y, 1.0 * dim)
        for x, y in self.lanterns:
            add_glow(a, gsp(110, (255, 60, 40)), x, y + 30, 0.6 * fl * dim)
        img = to_img(a)
        d = ImageDraw.Draw(img)
        for x, y in self.lanterns:
            d.line([(x, y - 40), (x, y)], fill=(40, 20, 16, 255), width=3)
            d.ellipse([x - 30, y, x + 30, y + 64], fill=(210, 40, 30, 255), outline=(90, 20, 14, 255), width=3)
            d.rectangle([x - 16, y - 4, x + 16, y + 4], fill=(200, 160, 70, 255)); d.rectangle([x - 16, y + 60, x + 16, y + 68], fill=(200, 160, 70, 255))
        x0, y0 = self.incense
        for k in range(3):                                                     # incense sticks + smoke
            sx = x0 - 20 + k * 20
            d.line([(sx, y0 + 10), (sx + (k - 1) * 6, y0 - 90)], fill=(170, 60, 40, 255), width=4)
            tip = (sx + (k - 1) * 6, y0 - 92)
            d.ellipse([tip[0] - 4, tip[1] - 4, tip[0] + 4, tip[1] + 4], fill=(255, 150, 80, 255))
            if smoke > 0:
                pts = [(tip[0] + 14 * math.sin(t * 1.4 + j * 0.45 + k) * j / 6, tip[1] - j * 26) for j in range(16)]
                d.line(pts, fill=(210, 200, 200, int(80 * smoke)), width=5, joint="curve")
        fog(img, t, fogk, 1150, 1500, speed=10, col=(180, 100, 90))
        for fn in (extras or []):
            img = fn(img, t) or img
        bokeh_particles(img, 10, 193, t, color=(255, 190, 120), size=(2, 5), blur=(0, 2), area=(0, 600, W, 1600), drift=(4, -6))
        return img


_SHR = None


def shrine():
    global _SHR
    if _SHR is None:
        _SHR = Shrine()
    return _SHR


class FogWood:
    """Off the trail, deep in the fog: a winding earth path between huge cedar and camphor trunks with buttress roots,
    ferns underneath, red ribbons tied on the trunks leading deeper, and the giant hollow camphor on the right with a
    black opening at its base (self.hollow). Everything fades into grey-red mist with distance."""
    def __init__(self):
        r = np.random.default_rng(194)
        self.P = P = Path(vy=900, x0=500, wig=-120, hw0=300)
        a = vgrad((30, 26, 30), (80, 64, 66), (60, 46, 48), ym=0.5)
        img = to_img(a)
        layers = []
        for depth in (0.95, 0.8, 0.62):                                      # trunk rows fading into the mist
            m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
            for k in range(7):
                x = r.uniform(-40, W + 40); wd = (1.05 - depth) * r.uniform(60, 120) + 6
                d.polygon([(x - wd, 1200), (x + wd, 1200), (x + wd * .7, -10), (x - wd * .7, -10)], fill=255)
                for j in range(3):
                    by = r.uniform(100, 700); sg = r.choice([-1, 1])
                    d.line([(x, by), (x + sg * wd * 4, by - wd * 3)], fill=255, width=max(2, int(wd / 3)))
            mix = depth
            col = tuple(int(c1 * (1 - mix) + c2 * mix) for c1, c2 in zip((14, 10, 12), (86, 70, 72)))
            img.alpha_composite(colorize(m.filter(ImageFilter.GaussianBlur(3 * depth)), col))
            fog(img, 0.0, 0.45, 300, 1300, col=(130, 110, 110), off=int(depth * 400))
        d = ImageDraw.Draw(img)
        us = np.linspace(0, 1, 50)
        d.polygon([(-10, P.y(1) - 10), (W + 10, P.y(1) - 10), (W + 10, H), (-10, H)], fill=(36, 28, 26, 255))
        d.polygon([(P.x(u) - P.hw(u), P.y(u)) for u in us] + [(P.x(u) + P.hw(u), P.y(u)) for u in us[::-1]], fill=(70, 54, 46, 255))
        for k in range(60):
            u = r.uniform(0, 1); x = P.x(u) + P.hw(u) * r.uniform(-1, 1)
            d.ellipse([x - 20 * (1 - u), P.y(u) - 4 * (1 - u), x + 20 * (1 - u), P.y(u) + 4 * (1 - u)], fill=(54, 40, 34, 255))
        self.base = img
        # near trunks (sharp) incl. the hollow camphor
        nm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        hx, hy = 800, 1250
        self.hollow = (hx, hy)
        def trunks(dd, s):
            for x, wd, y0 in ((90, 110, 1700), (330, 60, 1180), (hx, 200, hy + 160)):
                dd.polygon(P_((x - wd * 1.5, y0), (x - wd, y0 - 160), (x - wd * .8, -10), (x + wd * .8, -10), (x + wd, y0 - 160), (x + wd * 1.5, y0), s=s), fill=255)
                for sg in (-1, 1):                                             # buttress roots
                    dd.polygon(P_((x + sg * wd * .6, y0 - 200), (x + sg * wd * 2.4, y0 + 10), (x + sg * wd * 1.0, y0 + 10), s=s), fill=255)
        nm.alpha_composite(shade(trunks, (W, H), (58, 46, 40), 60, rim=(255, 80, 60), rim_strength=0.8))
        nd = ImageDraw.Draw(nm)
        for x, wd in ((90, 110), (330, 60), (hx, 200)):                     # bark furrows
            for k in range(-3, 4):
                nd.line([(x + k * wd * .22, 0), (x + k * wd * .2 + r.uniform(-8, 8), 1300)], fill=(36, 28, 24, 200), width=3)
        nd.ellipse([hx - 110, hy - 230, hx + 110, hy + 120], fill=(6, 3, 4, 255))       # the hollow
        nd.polygon([(hx - 110, hy - 40), (hx - 70, hy - 250), (hx, hy - 290), (hx + 70, hy - 250), (hx + 110, hy - 40)], fill=(6, 3, 4, 255))
        gm = Image.new("L", (W, H), 0); gdd = ImageDraw.Draw(gm)
        ground_ferns(gdd, [(r.uniform(0, W), r.uniform(1350, 1900), r.uniform(0.8, 1.6)) for _ in range(18)], 200, 1, r, 4)
        nm.alpha_composite(colorize(gm, (24, 30, 22)))
        self.near = nm
        self.rib = [(330 + 50, 700, 1.0), (hx - 190, 820, 1.2), (560, 960, 0.5), (520, 1000, 0.4), (470, 1030, 0.3)]
        fg = Image.new("L", (W, H), 0); fdd = ImageDraw.Draw(fg)
        tree_fern(fdd, -260, 2400, 1000, 1, r, lean=0.05)
        self.fg = colorize(fg, (6, 5, 6)).filter(ImageFilter.GaussianBlur(10))

    def frame(self, t, far_extras=None, near_extras=None, fogk=0.7, red=1.0, sil=None):
        img = self.base.copy()
        fog(img, t, fogk, 600, 1300, speed=14, col=(150, 120, 120))
        for fn in (far_extras or []):
            img = fn(img, t) or img
        fog(img, t, fogk * 0.8, 900, 1500, speed=20, col=(140, 110, 110), off=250)
        img.alpha_composite(self.near)
        for k, (x, y, sc) in enumerate(self.rib):
            col = np.array((200, 24, 28), np.float32) * red + np.array((238, 236, 226), np.float32) * (1 - red)
            ribbon(img, x, y, 80, t, col, sc * 1.3, seed=k)
        for fn in (near_extras or []):
            img = fn(img, t) or img
        fog(img, t, fogk * 0.5, 1300, 1900, speed=24, col=(130, 100, 100), off=500)
        img.alpha_composite(self.fg)
        bokeh_particles(img, 14, 194, t, color=(230, 210, 210), size=(2, 6), blur=(1, 3), area=(0, 300, W, 1700), drift=(6, -2))
        return img


_FW = None


def fogwood():
    global _FW
    if _FW is None:
        _FW = FogWood()
    return _FW


class Hollow:
    """POV from inside the hollow camphor: a ragged ring of dark ridged wood all round, lit faintly from the opening,
    and through the opening (centre (540, 1000)): the fog, roots, ferns and red ribbons outside."""
    def __init__(self):
        r = np.random.default_rng(195)
        a = vgrad((70, 58, 60), (110, 90, 90), (60, 46, 44), ym=0.55)
        out = to_img(a)
        m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
        for k in range(6):
            x = r.uniform(0, W); wd = r.uniform(14, 40)
            d.polygon([(x - wd, 1250), (x + wd, 1250), (x + wd * .7, 0), (x - wd * .7, 0)], fill=255)
        out.alpha_composite(colorize(m.filter(ImageFilter.GaussianBlur(4)), (50, 40, 42)))
        od = ImageDraw.Draw(out)
        od.rectangle([0, 1250, W, H], fill=(52, 40, 34, 255))
        gm = Image.new("L", (W, H), 0); gdd = ImageDraw.Draw(gm)
        ground_ferns(gdd, [(r.uniform(0, W), r.uniform(1300, 1500), r.uniform(0.6, 1.0)) for _ in range(10)], 180, 1, r, 3)
        out.alpha_composite(colorize(gm, (30, 34, 28)))
        self.outside = out
        # the wood ring
        self.cx, self.cy, self.rx, self.ry = 540, 1000, 330, 560
        hole = Image.new("L", (W, H), 0); hd = ImageDraw.Draw(hole)
        pts = []
        for k in range(64):
            a_ = 2 * math.pi * k / 64
            rr = 1 + 0.06 * math.sin(a_ * 7 + 1) + r.uniform(-0.04, 0.04)
            pts.append((self.cx + math.cos(a_) * self.rx * rr, self.cy + math.sin(a_) * self.ry * rr * (1.1 if math.sin(a_) < 0 else 1.0)))
        hd.polygon(pts, fill=255)
        ring = 255 - np.asarray(hole.filter(ImageFilter.GaussianBlur(2)), np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        ridges = 0.72 + 0.28 * np.sin(xx / 13 + 5 * np.sin(yy / 140) + 2 * np.sin(xx / 61))
        dist = np.sqrt(((xx - self.cx) / self.rx) ** 2 + ((yy - self.cy) / self.ry) ** 2)
        lit = np.clip(1.6 - dist, 0, 1) ** 1.5
        wood = np.dstack([46 + 70 * lit, 30 + 46 * lit, 26 + 36 * lit]) * ridges[..., None]
        self.ring = Image.fromarray(np.dstack([np.clip(wood, 0, 255), ring]).astype(np.uint8), "RGBA")
        self.mask_hole = hole

    def frame(self, t, outside_extras=None, edge_extras=None, fogk=0.6, sway=1.0, flash=0.0):
        img = self.outside.copy()
        fog(img, t, fogk, 700, 1400, speed=16, col=(150, 120, 120))
        for fn in (outside_extras or []):
            img = fn(img, t) or img
        if flash > 0:
            a = to_arr(img) + np.array([255, 170, 90], np.float32) * flash * 0.8
            img = to_img(a)
        dx = int(4 * sway * math.sin(t * 1.3)); dy = int(3 * sway * math.cos(t * 1.1))
        img.alpha_composite(self.ring, (dx, dy))
        for fn in (edge_extras or []):
            img = fn(img, t) or img
        return img


_HO = None


def hollow():
    global _HO
    if _HO is None:
        _HO = Hollow()
    return _HO


class Room:
    """Mei's room in a Taichung apartment at night: a window with a decorative iron grille, a red neon sign and lit
    apartment windows outside, a desk with a fan and a lamp off, posters, Mei's bed in front, and the dark doorway on
    the right of the back wall (self.door = where someone would stand)."""
    def __init__(self):
        r = np.random.default_rng(196)
        a = vgrad((16, 14, 20), (22, 18, 24), (12, 10, 14), ym=0.5)
        img = to_img(a)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1300, W, H], fill=(20, 16, 18, 255))                    # floor
        wx0, wy0, wx1, wy1 = 90, 420, 560, 960                                  # window
        out = to_img(vgrad((8, 6, 14), (30, 10, 20), (60, 14, 24), ym=0.6, w=wx1 - wx0, h=wy1 - wy0))
        od = ImageDraw.Draw(out)
        for k in range(5):
            bx = r.uniform(-40, wx1 - wx0); bw = r.uniform(80, 160); bt = r.uniform(80, 300)
            od.rectangle([bx, bt, bx + bw, wy1 - wy0], fill=(14, 12, 18, 255))
            for j in range(12):
                if r.random() < 0.35:
                    x = bx + 10 + (j % 4) * bw / 4; y = bt + 20 + (j // 4) * 40
                    od.rectangle([x, y, x + 14, y + 18], fill=(255, 200, 120, 255) if r.random() < .7 else (180, 220, 255, 255))
        od.rectangle([40, 300, 200, 360], fill=(240, 40, 50, 255))             # a red neon sign
        img.alpha_composite(out, (wx0, wy0))
        gr = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(gr)              # iron grille
        for x in range(wx0, wx1 + 1, 66):
            gd.line([(x, wy0), (x, wy1)], fill=255, width=6)
        for y in range(wy0, wy1 + 1, 90):
            gd.line([(wx0, y), (wx1, y)], fill=255, width=6)
        for x in range(wx0 + 33, wx1, 66):
            for y in range(wy0 + 45, wy1, 90):
                gd.arc([x - 22, y - 22, x + 22, y + 22], 0, 360, fill=255, width=4)
        gd.rectangle([wx0 - 14, wy0 - 14, wx1 + 14, wy1 + 14], outline=255, width=14)
        img.alpha_composite(colorize(gr, (30, 30, 34)))
        self.neon = (wx0 + 120, wy0 + 330)
        dx0, dx1, dy0 = 720, 960, 560                                          # the doorway (dark hallway)
        d.rectangle([dx0 - 16, dy0 - 16, dx1 + 16, 1300], fill=(46, 36, 34, 255))
        d.rectangle([dx0, dy0, dx1, 1300], fill=(4, 3, 5, 255))
        d.polygon([(dx0, dy0), (dx0 - 70, dy0 + 40), (dx0 - 70, 1340), (dx0, 1300)], fill=(56, 44, 40, 255))   # open door
        self.door = ((dx0 + dx1) / 2, 1300)
        d.rectangle([600, 1000, 700, 1300], fill=(40, 30, 28, 255))            # desk side
        d.rectangle([560, 980, 720, 1000], fill=(60, 46, 40, 255))
        d.ellipse([590, 860, 680, 950], outline=(80, 80, 86, 255), width=6)     # desk fan
        d.line([(635, 950), (635, 980)], fill=(80, 80, 86, 255), width=8)
        for k, (x, y, c) in enumerate(((260, 1010, (60, 70, 120)), (420, 1040, (110, 40, 50)))):   # posters
            d.rectangle([x, y - 20, x + 110, y + 130], fill=c + (255,))
        def bed(dd, s):
            dd.rectangle([-20 * s, 1500 * s, (W + 20) * s, (H + 20) * s], fill=255)
            dd.rounded_rectangle([60 * s, 1380 * s, 420 * s, 1520 * s], int(40 * s), fill=255)
        img.alpha_composite(shade(bed, (W, H), (60, 70, 90), 40, rim=(120, 160, 255)))
        bd = ImageDraw.Draw(img)
        for k in range(8):
            bd.line([(0, 1560 + k * 50), (W, 1530 + k * 50)], fill=(48, 56, 74, 255), width=4)
        self.base = img

    def frame(self, t, back_extras=None, front_extras=None, neon=1.0):
        a = to_arr(self.base)
        fl = neon * (0.8 + 0.2 * (math.sin(t * 23) > -0.9))
        add_glow(a, gsp(300, (255, 40, 50)), self.neon[0], self.neon[1], 0.35 * fl)
        img = to_img(a)
        for fn in (back_extras or []):
            img = fn(img, t) or img
        for fn in (front_extras or []):
            img = fn(img, t) or img
        return img


_RM = None


def room():
    global _RM
    if _RM is None:
        _RM = Room()
    return _RM


def camcorder(img, t, stamp="16:21:07", play=True, k=1.0):
    """The phone video look: soft and low-res, scanlines, a little colour bleed, a PLAY label and a time stamp."""
    if k <= 0:
        return img
    small = img.convert("RGB").resize((W // 3, H // 3), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    a = np.asarray(small, np.float32).copy()
    a[:, 4:, 0] = a[:, :-4, 0]
    a[::4] *= 0.82
    a = a * (0.92 + 0.08 * math.sin(t * 40))
    out = np.asarray(img.convert("RGB"), np.float32) * (1 - k) + a * k
    im = to_img(out)
    d = ImageDraw.Draw(im)
    f = font(INTER_SB, 40)
    A = int(255 * k)
    if play:
        d.polygon([(70, 1560), (70, 1600), (104, 1580)], fill=(250, 250, 250, A))
        d.text((120, 1580), "PLAY", font=f, fill=(250, 250, 250, A), anchor="lm")
    d.text((1010, 1580), stamp, font=f, fill=(250, 250, 250, A), anchor="rm")
    for (x, y, sx, sy) in ((40, 640, 1, 1), (1040, 640, -1, 1), (40, 1640, 1, -1), (1040, 1640, -1, -1)):
        d.line([(x, y), (x + 60 * sx, y)], fill=(250, 250, 250, A), width=5); d.line([(x, y), (x, y + 60 * sy)], fill=(250, 250, 250, A), width=5)
    return im


def count_num(img, n, x, y, k, red=False, sc=1.0):
    """A big counting number popping over a person on the video."""
    if k <= 0:
        return img
    f = font(INTER_SB, int(110 * sc))
    col = (255, 60, 50) if red else (255, 255, 255)
    ti = text_img(str(n), f, fill=col + (255,), glow=(200, 20, 20, 220) if red else (0, 0, 0, 200), pad=20)
    s2 = 0.6 + 0.4 * ease(min(1, k * 1.5))
    ti = ti.resize((max(1, int(ti.width * s2)), max(1, int(ti.height * s2))), Image.LANCZOS)
    img.alpha_composite(with_alpha(ti, min(1, k)), (int(x - ti.width / 2), int(y - ti.height / 2)))
    d = ImageDraw.Draw(img)
    return img
