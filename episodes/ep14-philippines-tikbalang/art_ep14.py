"""Ep14 Philippines / Tikbalang - art: the world, the characters and the creature (2.1D flat21 style).
New world: a provincial road at night with a concrete waiting shed and the last jeepney pulling away; a bamboo forest
trail (tall culms arching overhead, a broken barangay sign, rain falling from a clear sky under a blood-red moon); a giant
balete tree with curtains of aerial roots; an old plank bridge over a creek (seen from the side and from underneath);
Lola's house with jalousie windows and a glowing parol star lantern; the same window at dawn.
Hero: Paolo (mustard t-shirt with a print, jeans, tsinelas, backpack, phone torch).
Creature: the Tikbalang - very tall and bony, bone-white skin, a long horse head (front view) with glowing red eyes and a
wide flat-toothed grin, a wild black mane of spines with three golden hairs, too-long arms and fingers, backward-bent
legs ending in black hooves; squats with its knees above its head. No gore."""
import os, sys, math
os.environ["STYLE"] = "flat21"
_EP = os.path.dirname(os.path.abspath(__file__)); _TK = os.path.join(_EP, "..", "..", "toolkit")
sys.path.insert(0, _TK)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import W, H, font, text_img, with_alpha, ease, glow_sprite, add_glow, fog_texture, vignette, INTER_SB, INTER_M, LORA
from depth import inflate_shade, dof, bokeh_particles
import demo25_myanmar as D5
from scenes_v import series_header, header_layers, pill

SKIN = (168, 112, 78)         # Paolo
SHIRT = (184, 142, 44)        # mustard tee
SHIRT_IN = (204, 176, 100)    # the same tee inside out (paler, seams showing)
JEANS = (38, 42, 62)
HAIR = (12, 10, 12)
BONE = (196, 190, 180)        # the Tikbalang
BONE_D = (120, 110, 104)
MANE = (14, 10, 12)
HOOF = (20, 14, 14)
GOLDH = (255, 206, 90)
BAMBOO = (70, 22, 20)
BAMBOO_D = (36, 10, 12)
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


# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """Philippines: blue over red, white equilateral triangle at the hoist with a golden 8-ray sun and three stars."""
    global _FLAG
    if _FLAG is None:
        w, h, s = 300, 150, 4
        W2, H2 = w * s, h * s
        im = Image.new("RGBA", (W2, H2), (0, 56, 168, 255)); d = ImageDraw.Draw(im)
        d.rectangle([0, H2 / 2, W2, H2], fill=(206, 17, 38, 255))
        tw = H2 * math.sqrt(3) / 2
        d.polygon([(0, 0), (tw, H2 / 2), (0, H2)], fill=(250, 250, 246, 255))
        gold = (252, 209, 22, 255)
        cx, cy = tw * 0.36, H2 / 2
        r = H2 * 0.095
        for k in range(8):
            a = k * math.pi / 4
            for da in (-0.13, 0, 0.13):
                b = a + da
                d.polygon([(cx + r * 1.1 * math.cos(b - 0.05), cy + r * 1.1 * math.sin(b - 0.05)),
                           (cx + r * 2.15 * math.cos(b), cy + r * 2.15 * math.sin(b)),
                           (cx + r * 1.1 * math.cos(b + 0.05), cy + r * 1.1 * math.sin(b + 0.05))], fill=gold)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=gold)

        def star(x, y, R):
            pts = []
            for k in range(10):
                rr = R if k % 2 == 0 else R * 0.4
                a = -math.pi / 2 + k * math.pi / 5
                pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
            d.polygon(pts, fill=gold)
        sr = H2 * 0.05
        star(H2 * 0.085, H2 * 0.1, sr); star(H2 * 0.085, H2 * 0.9, sr); star(tw * 0.86, H2 / 2, sr)
        _FLAG = im.resize((w, h), Image.LANCZOS)
    return _FLAG


def flag_wave(t, width=240):
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
        fw = flag_wave(t)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 50))


def phone_ui(batt, km, t, k=1.0, place="SAN ISIDRO"):
    """The ticking clock: Paolo's phone battery + the map distance to Lola's barangay (which never goes down)."""
    f1 = font(INTER_SB, 46); f2 = font(INTER_M, 26)
    w, h = 640, 108
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(0, 0, 0, int(185 * k)), outline=(255, 70, 50, int(200 * k)), width=3)
    b = max(0, int(round(batt)))
    blink = (math.sin(t * 9) > -0.2) if b <= 5 else True
    red = (255, 70, 50, int(255 * k * (1 if blink else 0.25)))
    wht = (255, 240, 228, int(240 * k))
    col = red if b < 10 else wht
    # battery icon
    x0, y0 = 30, 34
    d.rounded_rectangle([x0, y0, x0 + 82, y0 + 40], 8, outline=col, width=4)
    d.rectangle([x0 + 84, y0 + 12, x0 + 92, y0 + 28], fill=col)
    fw = int(72 * b / 100)
    if fw > 0:
        d.rectangle([x0 + 5, y0 + 5, x0 + 5 + max(3, fw), y0 + 35], fill=col)
    d.text((190, h / 2), f"{b}%", font=f1, fill=col, anchor="mm")
    d.line([(272, 22), (272, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    # map pin
    px, py = 314, 48
    d.ellipse([px - 16, py - 18, px + 16, py + 14], fill=(255, 190, 140, int(255 * k)))
    d.polygon([(px - 13, py + 4), (px + 13, py + 4), (px, py + 30)], fill=(255, 190, 140, int(255 * k)))
    d.ellipse([px - 6, py - 8, px + 6, py + 4], fill=(0, 0, 0, int(200 * k)))
    d.text((480, h / 2 - 20), place, font=f2, fill=(255, 190, 140, int(255 * k)), anchor="mm")
    txt = "NO SIGNAL" if km is None else f"{km:.1f} KM"
    d.text((480, h / 2 + 18), txt, font=f1 if km is not None else font(INTER_SB, 38), fill=wht if km is not None else red, anchor="mm")
    return im


def put_phone(out, batt, km, t, k=1.0, y=560):
    ui = phone_ui(batt, km, t, k)
    out.alpha_composite(ui, (int(W / 2 - ui.width / 2), y))


# ============================================================ Paolo
_PC = {}


def paolo(phase=0.0, run=0.0, back=False, scale=1.0, phone=True, inside=False, shout=0.0):
    """Paolo: short black hair, mustard t-shirt (red sun print on the front; inside out = paler with seams and a tag),
    dark jeans, rubber tsinelas, a backpack, phone torch in his right hand. Returns (RGBA, feet_x, feet_y, phone_xy)."""
    q = (round(phase * 12) % 12, round(run, 1), back, round(scale, 2), phone, inside, round(shout, 1))
    if q in _PC:
        return _PC[q]
    w, h = 480, 920
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.3 + 0.7 * run)
    lean = 16 * run

    def leg_pts(sg):
        a = sg * sw * 0.55
        hx, hy = cx + lean * 0.3 + sg * 26, 470
        kx, ky = hx + math.sin(a) * 130, hy + math.cos(a) * 180
        fx, fy = kx + math.sin(a - 0.35 * run) * 100, ky + 170
        return (hx, hy), (kx, ky), (fx, fy)

    def legs(d, s):
        for sg in (-1, 1):
            p = leg_pts(sg)
            d.line([(x * s, y * s) for x, y in p], fill=255, width=int(50 * s), joint="curve")
        d.polygon(P_((cx - 62 + lean * .3, 440), (cx + 62 + lean * .3, 440), (cx + 58 + lean * .3, 520), (cx - 58 + lean * .3, 520), s=s), fill=255)

    def feet(d, s):
        for sg in (-1, 1):
            fx, fy = leg_pts(sg)[2]
            d.ellipse([(fx - 30) * s, (fy - 8) * s, (fx + 34) * s, (fy + 16) * s], fill=255)

    def torso(d, s):
        L = lean
        d.polygon(P_((cx - 84 + L, 190), (cx + 84 + L, 190), (cx + 76 + L * .6, 470), (cx - 76 + L * .6, 470), s=s), fill=255)
        d.ellipse([(cx - 100 + L) * s, 180 * s, (cx - 44 + L) * s, 250 * s], fill=255)
        d.ellipse([(cx + 44 + L) * s, 180 * s, (cx + 100 + L) * s, 250 * s], fill=255)

    hands = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 80 + lean, 214
        a = -sg * sw * 0.9
        hold = sg == 1 and phone and run < 0.5
        if hold:
            a = 0.25
        if shout > 0 and sg == -1:
            a = -2.2 * shout
        ex, ey = sx + math.sin(a) * 100 + sg * 10, sy + math.cos(a) * 110
        b = a - 0.9 * run * sg - (2.0 if hold else 0) - (0.6 * shout if sg == -1 else 0)
        hx, hy = ex + math.sin(b) * 96, ey + math.cos(b) * 90 - 40 * run
        hands[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            pts = hands[sg]
            d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(30 * s), joint="curve")
            hx, hy = pts[2]
            d.ellipse([(hx - 18) * s, (hy - 18) * s, (hx + 18) * s, (hy + 18) * s], fill=255)

    def sleeves(d, s):
        for sg in (-1, 1):
            (sx, sy), (ex, ey), _ = hands[sg]
            mx, my = sx + (ex - sx) * 0.6, sy + (ey - sy) * 0.6
            d.line([(sx * s, sy * s), (mx * s, my * s)], fill=255, width=int(50 * s), joint="curve")

    def bag(d, s):
        L = lean
        d.rounded_rectangle([(cx - 74 + L) * s, 210 * s, (cx + 74 + L) * s, 420 * s], int(36 * s), fill=255)

    def head(d, s):
        L = lean * 1.2
        d.rectangle([(cx - 22 + L) * s, 140 * s, (cx + 22 + L) * s, 200 * s], fill=255)
        d.ellipse([(cx - 52 + L) * s, 28 * s, (cx + 52 + L) * s, 164 * s], fill=255)

    def hair(d, s):
        L = lean * 1.2
        d.pieslice([(cx - 58 + L) * s, 14 * s, (cx + 58 + L) * s, 140 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 58 + L, 78), (cx - 54 + L, 108), (cx - 44 + L, 70), (cx + 44 + L, 70), (cx + 56 + L, 104), (cx + 58 + L, 78), s=s), fill=255)
        for k in range(5):                                                  # messy fringe spikes
            x = cx - 40 + k * 20 + L
            d.polygon(P_((x - 12, 60), (x + 12, 60), (x + 4 + (k - 2) * 2, 86), s=s), fill=255)
        if back:
            d.ellipse([(cx - 54 + L) * s, 22 * s, (cx + 54 + L) * s, 150 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), JEANS, 22))
    img.alpha_composite(shade(feet, (w, h), (30, 30, 34), 6))
    if not back:
        img.alpha_composite(shade(arms, (w, h), SKIN, 12))
    shirt_col = SHIRT_IN if inside else SHIRT
    img.alpha_composite(shade(torso, (w, h), shirt_col, 40))
    img.alpha_composite(shade(sleeves, (w, h), shirt_col, 16))
    if back:
        img.alpha_composite(shade(bag, (w, h), (40, 34, 36), 30))
        img.alpha_composite(shade(arms, (w, h), SKIN, 12))
    d = ImageDraw.Draw(img)
    L = lean
    if not back:
        # backpack straps
        for sg in (-1, 1):
            d.line([(cx + sg * 54 + L, 194), (cx + sg * 46 + L * .7, 330)], fill=(34, 30, 32, 255), width=14)
        if inside:
            # seams + a white tag at the collar: the shirt is inside out
            d.line([(cx - 80 + L, 196), (cx - 72 + L * .6, 466)], fill=(150, 120, 60, 255), width=4)
            d.line([(cx + 80 + L, 196), (cx + 72 + L * .6, 466)], fill=(150, 120, 60, 255), width=4)
            d.line([(cx - 76 + L * .6, 456), (cx + 76 + L * .6, 456)], fill=(150, 120, 60, 255), width=3)
            d.rectangle([cx - 14 + L, 194, cx + 14 + L, 220], fill=(244, 240, 230, 255))
            # the print shows through faintly, reversed
            d.ellipse([cx - 30 + L, 290, cx + 30 + L, 350], outline=(190, 120, 80, 150), width=4)
        else:
            # red sun print on the front
            d.ellipse([cx - 30 + L, 290, cx + 30 + L, 350], fill=(186, 34, 30, 255))
            for k in range(8):
                a = k * math.pi / 4
                d.line([(cx + L + 38 * math.cos(a), 320 + 38 * math.sin(a)), (cx + L + 54 * math.cos(a), 320 + 54 * math.sin(a))], fill=(186, 34, 30, 255), width=6)
            d.arc([cx - 62 + L, 190, cx + 62 + L, 226], 0, 180, fill=(140, 100, 30, 255), width=6)   # crew neck
    img.alpha_composite(shade(head, (w, h), SKIN, 28))
    img.alpha_composite(shade(hair, (w, h), HAIR, 14, rim_strength=1.1))
    d = ImageDraw.Draw(img)
    Lh = lean * 1.2
    if not back:
        for sg in (-1, 1):
            d.ellipse([cx + sg * 20 - 10 + Lh, 92, cx + sg * 20 + 10 + Lh, 110], fill=(240, 236, 230, 255))
            d.ellipse([cx + sg * 20 - 5 + Lh, 96, cx + sg * 20 + 5 + Lh, 106], fill=(15, 10, 10, 255))
            d.line([(cx + sg * 20 - 13 + Lh, 82 - 4 * shout), (cx + sg * 20 + 13 + Lh, 84 - 6 * shout * sg)], fill=(20, 12, 10, 255), width=5)
        if shout > 0:
            d.ellipse([cx - 12 + Lh, 128, cx + 12 + Lh, 150], fill=(60, 14, 14, 255))
        else:
            d.line([(cx - 10 + Lh, 136), (cx + 10 + Lh, 136)], fill=(90, 40, 34, 255), width=4)
    px, py = hands[1][2]
    if phone and run < 0.5 and not back:
        d.rounded_rectangle([px - 15, py - 36, px + 15, py + 14], 5, fill=(20, 20, 26, 255), outline=(90, 90, 100, 255), width=2)
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 815 * scale, (px * scale, (py - 30) * scale))
    _PC[q] = out
    return out


_PCR = {}


def paolo_crouch(scale=1.0, look=0.0):
    """Paolo crouched, hugging his knees, hand over his mouth (hiding). Front view. Returns (RGBA, feet_x, feet_y)."""
    k = (round(scale, 2), round(look, 1))
    if k in _PCR:
        return _PCR[k]
    w, h = 520, 640
    cx = w / 2

    def legs(d, s):
        for sg in (-1, 1):
            d.line([((cx + sg * 50) * s, 340 * s), ((cx + sg * 56) * s, 590 * s)], fill=255, width=int(62 * s))
            d.ellipse([(cx + sg * 50 - 50) * s, 290 * s, (cx + sg * 50 + 50) * s, 390 * s], fill=255)

    def feet(d, s):
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 62 - 40) * s, 580 * s, (cx + sg * 62 + 40) * s, 612 * s], fill=255)

    def body(d, s):
        d.polygon(P_((cx - 92, 210), (cx + 92, 210), (cx + 100, 470), (cx - 100, 470), s=s), fill=255)
        d.ellipse([(cx - 110) * s, 200 * s, (cx - 60) * s, 270 * s], fill=255)
        d.ellipse([(cx + 60) * s, 200 * s, (cx + 110) * s, 270 * s], fill=255)

    def arms(d, s):
        d.line([((cx - 100) * s, 240 * s), ((cx - 120) * s, 380 * s), ((cx + 60) * s, 420 * s)], fill=255, width=int(32 * s), joint="curve")
        d.ellipse([(cx + 44) * s, 400 * s, (cx + 84) * s, 440 * s], fill=255)
        d.line([((cx + 100) * s, 240 * s), ((cx + 96) * s, 320 * s), ((cx + 14) * s, 200 * s)], fill=255, width=int(30 * s), joint="curve")
        d.ellipse([(cx - 14) * s, 178 * s, (cx + 34) * s, 216 * s], fill=255)

    def head(d, s):
        L = look * 30
        d.ellipse([(cx - 54 + L) * s, 70 * s, (cx + 54 + L) * s, 212 * s], fill=255)

    def hair(d, s):
        L = look * 30
        d.pieslice([(cx - 60 + L) * s, 56 * s, (cx + 60 + L) * s, 180 * s], 180, 360, fill=255)
        for kk in range(5):
            x = cx - 40 + kk * 20 + L
            d.polygon(P_((x - 12, 100), (x + 12, 100), (x + 4, 126), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(body, (w, h), SHIRT, 40))
    img.alpha_composite(shade(head, (w, h), SKIN, 30))
    img.alpha_composite(shade(hair, (w, h), HAIR, 14))
    d = ImageDraw.Draw(img)
    L = look * 30
    for sg in (-1, 1):                                                      # wide scared eyes looking up
        d.ellipse([cx + sg * 20 - 11 + L, 130, cx + sg * 20 + 11 + L, 152], fill=(240, 236, 230, 255))
        d.ellipse([cx + sg * 20 - 5 + L, 130, cx + sg * 20 + 5 + L, 140], fill=(15, 10, 10, 255))
    img.alpha_composite(shade(legs, (w, h), JEANS, 30))
    img.alpha_composite(shade(feet, (w, h), (30, 30, 34), 6))
    img.alpha_composite(shade(arms, (w, h), SKIN, 14))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 610 * scale)
    _PCR[k] = out
    return out


# ============================================================ the Tikbalang
_TK_C = {}


def tik_head_pts(cx, top, sc=1.0):
    """Front view of a long horse head: wide brow with ears, long narrowing face, a broad muzzle at the bottom."""
    s = sc
    return [(cx - 52 * s, top + 40 * s), (cx - 70 * s, top + 70 * s), (cx - 62 * s, top + 150 * s), (cx - 40 * s, top + 250 * s),
            (cx - 46 * s, top + 300 * s), (cx - 40 * s, top + 340 * s), (cx, top + 356 * s), (cx + 40 * s, top + 340 * s),
            (cx + 46 * s, top + 300 * s), (cx + 40 * s, top + 250 * s), (cx + 62 * s, top + 150 * s), (cx + 70 * s, top + 70 * s),
            (cx + 52 * s, top + 40 * s), (cx, top + 22 * s)]


def tik_face_details(d, cx, top, s, grin):
    """Nostrils, a long flat-toothed grin, deep eye hollows (eyes are drawn as glows by the caller)."""
    for sg in (-1, 1):
        d.ellipse([cx + sg * 26 - 12 * s, top + 300 * s, cx + sg * 26 + 12 * s, top + 326 * s], fill=(30, 14, 14, 255))
        d.polygon([(cx + sg * 24 * s, top + 100 * s), (cx + sg * 66 * s, top + 96 * s), (cx + sg * 58 * s, top + 136 * s),
                   (cx + sg * 30 * s, top + 132 * s)], fill=(26, 10, 12, 255))
    if grin > 0:
        gw = (34 + 30 * grin) * s
        y = top + 334 * s
        d.chord([cx - gw, y - 18 * s * grin, cx + gw, y + 26 * s * grin], 0, 180, fill=(30, 8, 10, 255))
        n = 8
        for k in range(n):
            x0 = cx - gw * 0.86 + k * (gw * 1.72 / n)
            d.rectangle([x0 + 1, y + 2 * s, x0 + gw * 1.72 / n - 2, y + 11 * s * (0.6 + grin)], fill=(232, 226, 206, 255))
    # a few long creases on the face
    for sg in (-1, 1):
        d.line([(cx + sg * 14 * s, top + 160 * s), (cx + sg * 18 * s, top + 280 * s)], fill=(150, 140, 132, 255), width=max(2, int(3 * s)))


def tikbalang(pose="stand", tilt=0.0, step=0, reach=0.0, grin=0.0):
    """Full body, ~1500 px tall standing. pose: "stand" | "squat" (knees above its head). Returns (RGBA, feet_x, feet_y, [eyes])."""
    key = (pose, round(tilt), step % 2, round(reach, 1), round(grin, 1))
    if key in _TK_C:
        return _TK_C[key]
    w, h = 900, 1600
    cx = w / 2
    ang = math.radians(tilt)
    squat = pose == "squat"
    head_top = 760 if squat else 40
    nx, ny = cx, head_top + 340

    def R(*pts):
        return rot(pts, ang, nx, ny)

    st = step % 2
    if squat:
        # hips low, knees FAR above the head, shins down to the hooves on the ground
        hip_y = 1340
        legs_pts = {sg: [(cx + sg * 70, hip_y), (cx + sg * 250, 640), (cx + sg * 190, 1540)] for sg in (-1, 1)}
        torso = [(cx - 90, 1060), (cx + 90, 1060), (cx + 70, 1360), (cx - 70, 1360)]
        sh_y = 1080
    else:
        hip_y = 820
        legs_pts = {}
        for sg in (-1, 1):
            off = (30 if (st == 0) == (sg > 0) else -10)
            legs_pts[sg] = [(cx + sg * 56, hip_y), (cx + sg * 80 + off * 0.3, 1130), (cx + sg * 64 + off * 0.6, 1300),   # knee, backward-bent hock
                            (cx + sg * 74 + off, 1540)]
        torso = [(cx - 110, 430), (cx + 110, 430), (cx + 70, 840), (cx - 70, 840)]
        sh_y = 450

    def legs(d, s):
        for sg in (-1, 1):
            d.line([(x * s, y * s) for x, y in legs_pts[sg]], fill=255, width=int(40 * s), joint="curve")
            kx, ky = legs_pts[sg][1]
            d.ellipse([(kx - 32) * s, (ky - 32) * s, (kx + 32) * s, (ky + 32) * s], fill=255)

    def hooves(d, s):
        for sg in (-1, 1):
            fx, fy = legs_pts[sg][-1]
            d.polygon(P_((fx - 34, fy - 40), (fx + 34, fy - 40), (fx + 42, fy + 14), (fx - 42, fy + 14), s=s), fill=255)

    def body(d, s):
        d.polygon(P_(*torso, s=s), fill=255)
        x0, y0 = torso[0]
        d.ellipse([(x0 - 30) * s, (y0 - 20) * s, (x0 + 60) * s, (y0 + 60) * s], fill=255)
        x1, _ = torso[1]
        d.ellipse([(x1 - 60) * s, (y0 - 20) * s, (x1 + 30) * s, (y0 + 60) * s], fill=255)
        d.line([(cx * s, (y0 - 60) * s), (cx * s, (y0 + 30) * s)], fill=255, width=int(70 * s))       # neck

    arm_pts = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 118, sh_y + 10
        if squat:
            ex, ey = sx + sg * 40, sy + 250
            hx, hy = cx + sg * 60, 1520                                        # hands hang to the ground between the shins
        elif reach > 0:
            ex, ey = sx + sg * 60, sy + 260 - 220 * reach
            hx, hy = ex + sg * 40 - sg * 120 * reach, ey + 420 - 640 * reach
        else:
            ex, ey = sx + sg * 50, sy + 380
            hx, hy = sx + sg * 70, sy + 860                                    # far too long: hands below the knees
        arm_pts[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            p = arm_pts[sg]
            d.line([(x * s, y * s) for x, y in p], fill=255, width=int(30 * s), joint="curve")
            (ex, ey), (hx, hy) = p[1], p[2]
            vx, vy = hx - ex, hy - ey; n = math.hypot(vx, vy) + 1e-6; vx, vy = vx / n, vy / n
            for k in range(4):                                                 # long bony fingers
                a = math.atan2(vy, vx) + (k - 1.5) * 0.17
                d.line([(hx * s, hy * s), ((hx + math.cos(a) * 110) * s, (hy + math.sin(a) * 110) * s)], fill=255, width=int(11 * s))

    def head(d, s):
        d.polygon(P_(*R(*tik_head_pts(cx, head_top)), s=s), fill=255)
        for sg in (-1, 1):                                                     # pointed ears
            d.polygon(P_(*R((cx + sg * 30, head_top + 40), (cx + sg * 76, head_top - 50), (cx + sg * 66, head_top + 60)), s=s), fill=255)

    def mane(d, s):
        r = np.random.default_rng(4)
        # wild spiky mane: from the crown it falls down both sides of the long face, past the shoulders
        for k in range(34):
            u = k / 33
            sg = -1 if u < 0.5 else 1
            v = abs(u - 0.5) * 2
            bx = cx + sg * (30 + 50 * v)
            by = head_top + 30 + 40 * v
            ln = 260 + r.uniform(0, 300)
            tip = (bx + sg * (60 + 160 * v + r.uniform(0, 60)), by + ln)
            d.polygon(P_(*R((bx - 20, by), (bx + 20, by), tip), s=s), fill=255)
        for k in range(9):                                                     # forelock spikes over the brow
            x = cx - 60 + k * 15
            d.polygon(P_(*R((x - 14, head_top + 20), (x + 14, head_top + 20), (x + r.uniform(-20, 20), head_top + 110 + r.uniform(0, 40))), s=s), fill=255)
        d.ellipse([(cx - 70) * s, (head_top + 10) * s, (cx + 70) * s, (head_top + 80) * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if not squat:
        img.alpha_composite(shade(legs, (w, h), BONE, 18, rim_strength=1.0))
        img.alpha_composite(shade(hooves, (w, h), HOOF, 10, rim_strength=1.2))
    img.alpha_composite(shade(body, (w, h), BONE, 50, rim_strength=0.9))
    d = ImageDraw.Draw(img)
    rib_y0 = torso[0][1] + 60
    for k in range(5):                                                         # bony ribs (lines only)
        y = rib_y0 + k * 34
        for sg in (-1, 1):
            d.arc([cx - 90 + (sg > 0) * 90 - (sg < 0) * 0, y - 20, cx + (sg > 0) * 90, y + 30], 200 if sg < 0 else 270, 340 if sg < 0 else 360,
                  fill=BONE_D + (255,), width=5)
    img.alpha_composite(shade(arms, (w, h), BONE, 12, rim_strength=1.0))
    if squat:
        img.alpha_composite(shade(legs, (w, h), BONE, 20, rim_strength=1.0))
        img.alpha_composite(shade(hooves, (w, h), HOOF, 10, rim_strength=1.2))
    img.alpha_composite(shade(mane, (w, h), MANE, 16, rim_strength=1.4))
    img.alpha_composite(shade(head, (w, h), BONE, 46, rim_strength=0.9))
    d = ImageDraw.Draw(img)
    # the three golden hairs in the mane
    for k, (sg, off) in enumerate(((-1, 84), (1, 80), (1, 104))):
        p0 = R((cx + sg * off, head_top + 70))[0]
        pm = R((cx + sg * (off + 60), head_top + 260 + 30 * k))[0]
        p1 = R((cx + sg * (off + 90), head_top + 470 + 50 * k))[0]
        d.line([p0, pm, p1], fill=GOLDH + (255,), width=4, joint="curve")
    # face details, rotated with the head: draw on a temp layer
    fl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); fd = ImageDraw.Draw(fl)
    tik_face_details(fd, cx, head_top, 1.0, grin)
    if tilt:
        fl = fl.rotate(-tilt, resample=Image.BICUBIC, center=(nx, ny))
    img.alpha_composite(fl)
    eyes = [R((cx - 44, head_top + 118))[0], R((cx + 44, head_top + 118))[0]]
    out = (img, cx, 1550, eyes)
    _TK_C[key] = out
    return out


def put_tik(img, x, y, scale, t, pose="stand", eyes=1.0, tilt=0.0, step=0, reach=0.0, grin=0.0, aura=0.5, alpha=1.0, sway=True, dark=0.0):
    """Tikbalang with its hooves at (x, y). Soft red aura, pulsing red eyes. dark 0..1 = silhouette (backlit)."""
    body, fx, fy, ee = tikbalang(pose, tilt, step, reach, grin)
    rr = 0.8 * math.sin(t * 0.8) if sway else 0
    g = body.rotate(rr, resample=Image.BICUBIC, center=(fx, fy)) if rr else body
    g = g.resize((max(1, int(g.width * scale)), max(1, int(g.height * scale))), Image.LANCZOS)
    if dark > 0:
        g = tint(g, (1 - 0.9 * dark, 1 - 0.93 * dark, 1 - 0.93 * dark))
    if alpha < 1:
        g = with_alpha(g, alpha)
    gx, gy = int(x - fx * scale), int(y - fy * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(max(3, 30 * scale)))
        lay = Image.new("RGBA", g.size, (255, 40, 30, 0)); lay.putalpha(al.point(lambda v: int(v * aura * alpha)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    if eyes > 0:
        k = eyes * alpha * (0.65 + 0.35 * math.sin(t * 5) ** 2)
        for ex, ey in ee:
            eye(img, gx + ex * scale, gy + ey * scale, k, max(0.22, scale * 1.1))
    return img


_TF = {}


def tik_face(grin=0.6, inv=False):
    """Big head close-up for jump scares (~760 px tall). inv=True: upside down (leaning under a bridge), with the mane
    hanging down from the crown. Returns (RGBA, eyes); the face centre is at (450, 450)."""
    k = (round(grin, 1), inv)
    if k in _TF:
        return _TF[k]
    w, h = 900, 1000
    cx, top, sc = 450, 120, 2.2

    def head(d, s):
        d.polygon(P_(*tik_head_pts(cx, top, sc), s=s), fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 66, top + 88), (cx + sg * 167, top - 80), (cx + sg * 145, top + 132), s=s), fill=255)

    def mane(d, s):
        r = np.random.default_rng(9)
        for kk in range(36):
            u = kk / 35
            sg = -1 if u < 0.5 else 1
            v = abs(u - 0.5) * 2
            bx = cx + sg * (60 + 110 * v)
            by = top + 60 + 90 * v
            ln = 420 + r.uniform(0, 380)
            d.polygon(P_((bx - 30, by), (bx + 30, by), (bx + sg * (120 + 260 * v + r.uniform(0, 80)), by + ln), s=s), fill=255)
        for kk in range(10):
            x = cx - 130 + kk * 29
            d.polygon(P_((x - 26, top + 40), (x + 26, top + 40), (x + r.uniform(-30, 30), top + 230 + r.uniform(0, 70)), s=s), fill=255)
        d.ellipse([(cx - 150) * s, (top + 10) * s, (cx + 150) * s, (top + 170) * s], fill=255)

    if inv:
        hl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        hl.alpha_composite(shade(head, (w, h), BONE, 90, rim_strength=0.9))
        tik_face_details(ImageDraw.Draw(hl), cx, top, sc, grin)
        hl = hl.rotate(180, resample=Image.BICUBIC, center=(450, 450))
        H2 = 1500
        img = Image.new("RGBA", (w, H2), (0, 0, 0, 0))

        def hang(d, s):
            r = np.random.default_rng(13)
            for kk in range(40):
                u = kk / 39
                bx = cx + (u - 0.5) * 330
                by = 640 + abs(u - 0.5) * 120
                ln = 380 + r.uniform(0, 420)
                d.polygon(P_((bx - 26, by), (bx + 26, by), (bx + (u - 0.5) * 160 + r.uniform(-30, 30), by + ln), s=s), fill=255)
            d.ellipse([(cx - 170) * s, 600 * s, (cx + 170) * s, 820 * s], fill=255)
        img.alpha_composite(shade(hang, (w, H2), MANE, 24, rim_strength=1.4))
        d = ImageDraw.Draw(img)
        for kk, off in enumerate((-120, 30, 110)):
            d.line([(cx + off, 700), (cx + off * 1.2 + 30, 980 + 40 * kk), (cx + off * 1.3, 1280)], fill=GOLDH + (255,), width=6, joint="curve")
        img.alpha_composite(hl)
        eyes = [(900 - (cx - 97), 900 - (top + 260)), (900 - (cx + 97), 900 - (top + 260))]
        _TF[k] = (img, eyes)
        return _TF[k]
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(mane, (w, h), MANE, 24, rim_strength=1.4))
    img.alpha_composite(shade(head, (w, h), BONE, 90, rim_strength=0.9))
    d = ImageDraw.Draw(img)
    tik_face_details(d, cx, top, sc, grin)
    for kk, (sg, off) in enumerate(((-1, 190), (1, 180), (1, 230))):
        d.line([(cx + sg * off, top + 150), (cx + sg * (off + 90), top + 480 + 60 * kk), (cx + sg * (off + 130), top + 840)], fill=GOLDH + (255,), width=6, joint="curve")
    eyes = [(cx - 97, top + 260), (cx + 97, top + 260)]
    _TF[k] = (img, eyes)
    return _TF[k]


def put_tface(img, x, y, scale, t, eyes=1.0, grin=0.6, tilt=0.0, aura=0.7, alpha=1.0, inv=False):
    """Head close-up centred at (x, y) (centre of the face)."""
    fimg, ee = tik_face(grin, inv)
    g = fimg
    cxf, cyf = 450, 450
    if tilt:
        g = g.rotate(tilt, resample=Image.BICUBIC, center=(cxf, cyf))
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
            eye(img, gx + rx * scale, gy + ry * scale, k, scale * 2.0)
    return img


# ============================================================ shared environment bits
def moon_sky(moon=(720, 430), r=120, top=(5, 1, 3), mid=(46, 6, 12), bot=(120, 22, 24), ym=0.45, h=H):
    a = vgrad(top, mid, bot, ym=ym, h=h)
    yy, xx = np.mgrid[0:h, 0:W]
    mx, my = moon
    dd = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
    a += np.exp(-dd / (r * 3.2))[..., None] * np.array([150, 26, 20], np.float32) * 0.9
    disc = np.clip((r - dd) / 2.5, 0, 1)[..., None]
    mcol = np.array([232, 72, 50], np.float32) * (0.9 + 0.1 * np.clip(1 - dd / r, 0, 1))[..., None]
    a = a * (1 - disc) + mcol * disc
    r2 = np.random.default_rng(7)                                            # a few faint stars
    for _ in range(90):
        x, y = int(r2.uniform(0, W)), int(r2.uniform(0, h * 0.4))
        a[y:y + 2, x:x + 2] += r2.uniform(30, 90)
    return a


def culm(d, s, x, by, ty, wd, lean, seg=110):
    """One bamboo culm from (x, by) up to ty, leaning sideways by `lean` px at the top, with node rings."""
    n = 18
    pts = [(x + lean * (k / n) ** 1.6, by + (ty - by) * k / n) for k in range(n + 1)]
    d.line([(px * s, py * s) for px, py in pts], fill=255, width=max(1, int(wd * s)), joint="curve")
    return pts


def leaf_spray(d, s, x, y, size, rnd, droop=1.0):
    for k in range(7):
        a = rnd.uniform(-0.3, math.pi + 0.3)
        ln = size * rnd.uniform(0.6, 1.0)
        tx, ty = x + math.cos(a) * ln, y + abs(math.sin(a)) * ln * 0.25 + ln * 0.5 * droop
        wv = size * 0.09
        d.polygon(P_((x, y - wv), (tx, ty), (x, y + wv), s=s), fill=255)


def rain_layers(seed=5, n=3):
    out = []
    for k in range(n):
        r = np.random.default_rng(seed + k)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        cnt = 260 - 60 * k; ln = 40 + 30 * k; al = 70 + 50 * k; wd = 1 + k
        for _ in range(cnt):
            x, y = r.uniform(-60, W), r.uniform(0, H)
            d.line([(x, y), (x + ln * 0.12, y + ln)], fill=(255, 190, 170, al), width=wd)
        out.append(im)
    return out


_RAIN = None


def rain(img, t, k=1.0):
    global _RAIN
    if _RAIN is None:
        _RAIN = rain_layers()
    if k <= 0:
        return img
    for i, L in enumerate(_RAIN):
        off = int((t * (900 + 500 * i)) % H)
        arr = np.asarray(L)
        rolled = np.roll(arr, off, axis=0)
        if k < 1:
            rolled = rolled.copy(); rolled[..., 3] = (rolled[..., 3] * k).astype(np.uint8)
        img.alpha_composite(Image.fromarray(rolled, "RGBA"))
    return img


# ============================================================ the bamboo forest trail
class BambooPath:
    """Night trail through a bamboo forest: tall culms arch over the path, a red moon through the gap, puddles, fog
    between the layers. Layers shift with the camera (parallax). frame(t, cam, extras=[(z, fn)], rain_k, light)."""
    def __init__(self, seed=21, moon=(700, 380)):
        self.P = P = Persp(540, 1000, 620)
        self.moon = moon
        sky = moon_sky(moon, 110, top=(4, 1, 2), mid=(40, 5, 10), bot=(96, 16, 18), ym=0.5)
        ground = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ground)
        d.rectangle([0, 1000, W, H], fill=(34, 10, 10, 255))
        d.polygon([P.p(-0.55, 1.0, 0.45), P.p(0.55, 1.0, 0.45), P.p(0.3, 1.0, 14), P.p(-0.3, 1.0, 14)], fill=(54, 20, 16, 255))
        r = np.random.default_rng(seed)
        for _ in range(7):                                                     # puddles with the moon in them
            z = r.uniform(0.9, 5); sd = r.uniform(-0.3, 0.3)
            x, y = P.p(sd, 1.0, z); rw = r.uniform(50, 110) / z
            d.ellipse([x - rw, y - rw * 0.2, x + rw, y + rw * 0.2], fill=(26, 6, 8, 255))
            d.arc([x - rw, y - rw * 0.2, x + rw, y + rw * 0.2], 190, 340, fill=(200, 60, 44, 255), width=max(1, int(4 / z)))
        for _ in range(260):                                                   # undergrowth along both edges
            z = r.uniform(0.6, 9); sg = r.choice([-1, 1]); sd = sg * r.uniform(0.5, 1.6)
            x, y = P.p(sd, 1.0, z); hh = r.uniform(60, 220) / z
            for j in range(3):
                d.polygon([(x - 5 / z - j * 4, y), (x + 5 / z + j * 4, y), (x + r.uniform(-40, 40) / z, y - hh * r.uniform(0.6, 1))], fill=(16, 4, 5, 255))
        for _ in range(140):                                                   # stones / roots
            z = r.uniform(0.6, 8); sd = r.uniform(-1.2, 1.2)
            x, y = P.p(sd, 1.0, z); rr = r.uniform(4, 14) / z * 2
            d.ellipse([x - rr, y - rr * 0.5, x + rr, y + rr * 0.5], fill=(20, 6, 6, 255))
        self.sky = sky
        self.ground = ground
        # bamboo layers: (z range, colour, parallax, blur)
        specs = [((5.0, 11.0), (92, 26, 28), 0.15, 2.0), ((2.4, 5.0), (62, 16, 18), 0.4, 0.8), ((1.0, 2.4), (40, 10, 12), 0.75, 0.0)]
        self.layers = []
        for (z0, z1), col, par, bl in specs:
            lay = Image.new("RGBA", (W + 400, H), (0, 0, 0, 0))
            m = Image.new("L", ((W + 400), H), 0)
            md = ImageDraw.Draw(m)
            lm = Image.new("L", ((W + 400), H), 0); ld = ImageDraw.Draw(lm)
            n = 34 if z0 > 4 else (26 if z0 > 2 else 14)
            for i in range(n):
                z = r.uniform(z0, z1)
                sg = -1 if i % 2 == 0 else 1
                sd = sg * (r.uniform(0.6, 1.1) if z0 < 2 else r.uniform(0.62, 1.8))
                x, y = P.p(sd, 1.0, z); x += 200
                wd = max(3, 0.09 * P.f / z)
                lean = -sg * r.uniform(40, 180) / max(1, z * 0.5)
                pts = culm(md, 1, x, y + 4, -260, wd, lean)
                for k in range(3, 18, 2):                                     # leaf sprays along the upper culm
                    px, py = pts[k]
                    if py < y - 300:
                        leaf_spray(ld, 1, px, py, r.uniform(40, 110) * (2.4 / max(1.4, z)) ** 0.6, r, droop=1.0)
            mask = Image.fromarray(np.maximum(np.asarray(m), np.asarray(lm)))
            base = inflate21(m, col, radius=max(4, 14 / (1 + z0 * 0.3)), rim=(255, 70, 50), rim_strength=0.9 if z0 < 4 else 0.5)
            lc = Image.new("RGBA", m.size, tuple(int(c * 0.8) for c in col) + (0,)); lc.putalpha(lm)
            lay.alpha_composite(lc); lay.alpha_composite(base)
            # node rings on the culms (darker bands)
            if bl:
                lay = lay.filter(ImageFilter.GaussianBlur(bl))
            self.layers.append((lay, par))
        # foreground: big blurred leaves at the frame edges
        fg = Image.new("L", (W + 400, H), 0); fd = ImageDraw.Draw(fg)
        for i in range(10):
            x = r.choice([r.uniform(0, 240), r.uniform(W + 160, W + 400)])
            y = r.uniform(-100, 600) if i % 2 else r.uniform(1500, 2000)
            leaf_spray(fd, 1, x, y, r.uniform(200, 360), r, droop=0.6 if y < 900 else -0.9)
        fgl = Image.new("RGBA", fg.size, (10, 2, 3, 0)); fgl.putalpha(fg)
        self.fg = fgl.filter(ImageFilter.GaussianBlur(9))

    def frame(self, t, cam=0.0, extras=None, rain_k=0.0, light=1.0, fogk=0.35, fg=True):
        a = self.sky.copy()
        img = to_img(a)
        img.alpha_composite(self.ground)
        P = self.P
        layer_z = [8.0, 3.5, 1.6]
        ex = sorted(extras or [], key=lambda e: -e[0])
        for (lay, par), lz in zip(self.layers, layer_z):
            while ex and ex[0][0] > lz:
                z, fn = ex.pop(0); img = fn(img, t, -cam * (0.15 + 0.6 / z)) or img
            img.alpha_composite(lay, (int(-200 - cam * par), 0))
            fog(img, t, fogk * (1.0 if lz > 3 else 0.6), 700, 1250, speed=14, col=(150, 44, 40), off=int(lz * 100))
        for z, fn in ex:
            img = fn(img, t, -cam * (0.15 + 0.6 / z)) or img
        if fg:
            img.alpha_composite(self.fg, (int(-200 - cam * 1.6), 0))
        if rain_k > 0:
            img = rain(img, t, rain_k)
        bokeh_particles(img, 14, 41, t, color=(255, 140, 100), size=(2, 7), blur=(0, 3), area=(0, 300, W, 1700), drift=(6, -5))
        if light != 1.0:
            img = to_img(to_arr(img) * light)
        return img


_BP = {}


def bamboo(seed=21):
    if seed not in _BP:
        _BP[seed] = BambooPath(seed)
    return _BP[seed]


def broken_sign(scale=1.0):
    """A leaning wooden post with a cracked arrow plank: SAN ISIDRO ->  (half the arrow broken off)."""
    w, h = 520, 640
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def post(d, s):
        d.polygon(P_((240, 640), (270, 640), (300, 120), (272, 116), s=s), fill=255)

    def plank(d, s):
        d.polygon(P_((40, 150), (430, 110), (470, 160), (436, 200), (50, 236), (70, 196), (36, 190), s=s), fill=255)
    im.alpha_composite(shade(post, (w, h), (70, 40, 26), 10))
    pl = shade(plank, (w, h), (150, 120, 88), 14)
    im.alpha_composite(pl)
    d = ImageDraw.Draw(im)
    f = font(INTER_SB, 46)
    txt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(txt).text((250, 172), "SAN ISIDRO", font=f, fill=(40, 16, 12, 255), anchor="mm")
    im.alpha_composite(txt.rotate(5, center=(250, 172)))
    d.line([(120, 140), (150, 230)], fill=(30, 14, 10, 255), width=5)                       # crack
    d.polygon([(330, 116), (360, 112), (380, 228), (350, 226)], fill=(0, 0, 0, 0))
    im = im.rotate(-7, resample=Image.BICUBIC, center=(255, 640))
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im, 255 * scale, 640 * scale


_SG = {}


def sign_c(scale):
    k = round(scale, 2)
    if k not in _SG:
        _SG[k] = broken_sign(k)
    return _SG[k]


# ============================================================ the balete tree
class Balete:
    """A giant balete (strangler fig): a trunk of twisted root strands, wide branches, curtains of aerial roots, the
    red moon behind it, tall grass. Branch perch for the Tikbalang at self.perch."""
    def __init__(self):
        sky = moon_sky((540, 520), 230, top=(4, 1, 2), mid=(52, 6, 12), bot=(110, 18, 20), ym=0.42)
        self.sky = to_img(sky)
        r = np.random.default_rng(3)
        w, h = W, H
        m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
        cx, gy = 540, 1560
        for k in range(40):                                                    # twisted strands of the trunk
            x0 = cx + r.uniform(-260, 260) * (1.2 if k % 3 == 0 else 0.8)
            pts = []
            for j in range(20):
                u = j / 19
                y = gy + 40 - u * 900
                x = cx + (x0 - cx) * (1 - 0.55 * u) + 26 * math.sin(u * 7 + k)
                pts.append((x, y))
            d.line(pts, fill=255, width=int(r.uniform(14, 36)), joint="curve")
        for sg, ang, ln in ((-1, 0.35, 620), (1, 0.3, 640), (-1, 0.9, 420), (1, 1.0, 440)):   # big branches
            x0, y0 = cx + sg * 60, gy - 820
            pts = [(x0 + sg * math.cos(ang) * ln * u + sg * 40 * math.sin(u * 3), y0 - math.sin(ang) * ln * u + 60 * u * u) for u in np.linspace(0, 1, 12)]
            d.line(pts, fill=255, width=60, joint="curve")
        d.ellipse([cx - 400, gy - 40, cx + 400, gy + 80], fill=255)                # root flare
        self.perch = (cx + 300, gy - 930)
        trunk = inflate21(m, (60, 22, 22), radius=30, rim=(255, 70, 50), rim_strength=1.0)
        # hollow in the trunk
        dd = ImageDraw.Draw(trunk)
        dd.polygon([(cx - 40, gy - 430), (cx + 30, gy - 400), (cx + 54, gy - 260), (cx + 20, gy - 130), (cx - 50, gy - 150), (cx - 64, gy - 300)], fill=(6, 1, 2, 255))
        # canopy
        cm = Image.new("L", (w, h), 0); cd = ImageDraw.Draw(cm)
        for _ in range(70):
            x = cx + r.normal(0, 380); y = gy - 1060 + r.normal(0, 170) - max(0, 300 - abs(x - cx)) * 0.4
            rr = r.uniform(60, 150)
            cd.ellipse([x - rr, y - rr * 0.7, x + rr, y + rr * 0.7], fill=255)
        canopy = inflate21(cm, (34, 8, 10), radius=40, rim=(255, 60, 40), rim_strength=0.8)
        # aerial roots (curtains)
        am = Image.new("L", (w, h), 0); ad = ImageDraw.Draw(am)
        for _ in range(120):
            x = cx + r.uniform(-640, 640); y0 = gy - 900 - r.uniform(0, 200) + abs(x - cx) * 0.25
            ln = r.uniform(200, 900)
            ad.line([(x, y0), (x + r.uniform(-14, 14), y0 + ln * 0.5), (x + r.uniform(-20, 20), y0 + ln)], fill=255, width=int(r.uniform(2, 6)))
        roots = Image.new("RGBA", (w, h), (40, 10, 12, 0)); roots.putalpha(am)
        # grass
        gm = Image.new("L", (w, h), 0); gd = ImageDraw.Draw(gm)
        gd.rectangle([0, gy + 20, w, h], fill=255)
        for _ in range(500):
            x = r.uniform(0, w); hh = r.uniform(40, 200)
            gd.polygon([(x - 6, gy + 40), (x + 6, gy + 40), (x + r.uniform(-30, 30), gy + 40 - hh)], fill=255)
        grass = Image.new("RGBA", (w, h), (14, 4, 5, 0)); grass.putalpha(gm)
        self.back = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.back.alpha_composite(canopy); self.back.alpha_composite(trunk)
        self.roots = roots
        self.grass = grass
        self.far = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        fd = ImageDraw.Draw(self.far)
        for i in range(14):                                                    # far bamboo clumps on the horizon
            x = r.uniform(0, w); hh = r.uniform(300, 600)
            for j in range(6):
                fd.line([(x + j * 12, gy), (x + j * 12 + r.uniform(-90, 90), gy - hh)], fill=(70, 16, 20, 255), width=6)
        self.far = self.far.filter(ImageFilter.GaussianBlur(2))

    def frame(self, t, cam=0.0, extras=None, fogk=0.4):
        img = self.sky.copy()
        img.alpha_composite(self.far, (int(-cam * 0.15), 0))
        fog(img, t, fogk, 1200, 1600, speed=10, col=(150, 40, 36))
        img.alpha_composite(self.back, (int(-cam * 0.4), 0))
        for z, fn in sorted(extras or [], key=lambda e: -e[0]):
            img = fn(img, t, -cam * 0.4) or img
        img.alpha_composite(self.roots, (int(-cam * 0.45), 0))
        fog(img, t, fogk * 0.7, 1450, 1800, speed=16, col=(130, 34, 30), off=300)
        img.alpha_composite(self.grass, (int(-cam * 0.8), 0))
        bokeh_particles(img, 16, 52, t, color=(255, 120, 90), size=(2, 8), blur=(0, 3), area=(0, 400, W, 1800), drift=(5, -8))
        return img


_BL = None


def balete():
    global _BL
    if _BL is None:
        _BL = Balete()
    return _BL


# ============================================================ the roadside: waiting shed + last jeepney
def jeepney_rear(scale=1.0, lights=1.0):
    """Rear view of a jeepney: boxy body, rounded roof with a LAST TRIP sign, rear step + ladder, chrome trim, red lights."""
    w, h = 700, 640
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def body(d, s):
        d.rounded_rectangle([60 * s, 110 * s, 640 * s, 560 * s], int(30 * s), fill=255)
        d.rounded_rectangle([40 * s, 80 * s, 660 * s, 150 * s], int(30 * s), fill=255)

    def wheels(d, s):
        for x in (110, 530):
            d.rounded_rectangle([x * s, 520 * s, (x + 70) * s, 620 * s], int(18 * s), fill=255)
    im.alpha_composite(shade(wheels, (w, h), (14, 10, 10), 10))
    im.alpha_composite(shade(body, (w, h), (120, 34, 30), 40, rim=(255, 120, 80)))
    d = ImageDraw.Draw(im)
    d.rectangle([220, 170, 480, 520], fill=(10, 4, 4, 255))                         # rear opening
    for k in range(4):
        d.line([(240, 230 + k * 70), (460, 230 + k * 70)], fill=(70, 30, 26, 255), width=4)     # benches inside
    for x in (190, 510):
        d.line([(x, 170), (x, 540)], fill=(210, 200, 190, 255), width=8)            # chrome grab bars
    d.rectangle([200, 520, 500, 548], fill=(200, 190, 180, 255))                    # step
    for x, c in ((100, (255, 50, 36)), (600, (255, 50, 36))):
        d.rounded_rectangle([x - 30, 380, x + 30, 470], 10, fill=c + (255,))
    d.rounded_rectangle([200, 92, 500, 140], 10, fill=(240, 210, 120, 255))
    d.text((350, 116), "LAST TRIP", font=font(INTER_SB, 34), fill=(120, 20, 16, 255), anchor="mm")
    d.text((350, 300), "", font=font(INTER_SB, 30))
    for k in range(6):                                                              # painted stripes
        d.line([(70, 170 + k * 8), (200, 170 + k * 8)], fill=(250, 200, 90, 255) if k % 2 else (40, 120, 140, 255), width=4)
        d.line([(500, 170 + k * 8), (630, 170 + k * 8)], fill=(250, 200, 90, 255) if k % 2 else (40, 120, 140, 255), width=4)
    if scale != 1.0:
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    return im


class Roadside:
    """A provincial road at night: concrete waiting shed with a tin roof and bench, a sodium lamp, a green road sign,
    the dark bamboo forest with a trail opening, mountains under the red moon. The road runs into the distance."""
    def __init__(self):
        self.P = P = Persp(540, 1060, 620)
        a = moon_sky((300, 520), 90, top=(4, 1, 2), mid=(56, 8, 14), bot=(128, 26, 26), ym=0.5)
        img = to_img(a); d = ImageDraw.Draw(img)
        r = np.random.default_rng(8)
        pts = [(0, 1060)] + [(x, 1060 - 160 - 120 * math.sin(x / 210 + 1) - r.uniform(0, 40)) for x in range(0, W + 60, 60)] + [(W, 1060)]
        d.polygon(pts, fill=(40, 8, 12, 255))
        pts = [(0, 1060)] + [(x, 1060 - 60 - 60 * math.sin(x / 130)) for x in range(0, W + 60, 60)] + [(W, 1060)]
        d.polygon(pts, fill=(26, 5, 8, 255))
        d.rectangle([0, 1060, W, H], fill=(22, 8, 8, 255))
        d.polygon([P.p(-0.6, 1, 0.35), P.p(0.9, 1, 0.35), P.p(0.06, 1, 30), P.p(-0.04, 1, 30)], fill=(40, 30, 32, 255))   # asphalt
        z = 0.6
        while z < 20:
            d.line([P.p(0.15, 1, z), P.p(0.15, 1, z * 1.25)], fill=(200, 180, 120, 255), width=max(1, int(10 / z)))
            z *= 1.6
        self.base = img
        # the bamboo forest on the right, with a dark trail opening
        m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
        for i in range(40):
            x = r.uniform(620, W + 80); by = 1150 + r.uniform(-40, 80)
            culm(md, 1, x, by, -200, r.uniform(10, 26), r.uniform(-260, -60))
        for i in range(60):
            leaf_spray(md, 1, r.uniform(560, W), r.uniform(100, 900), r.uniform(60, 130), r)
        md.polygon([(780, 1190), (850, 1190), (836, 960), (800, 960)], fill=0)        # trail opening
        self.forest = inflate21(m, (48, 12, 14), radius=10, rim=(255, 70, 50), rim_strength=0.8)
        # waiting shed (left)
        sm = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def walls(d, s):
            d.rectangle([60 * s, 980 * s, 470 * s, 1300 * s], fill=255)

        def roof(d, s):
            d.polygon(P_((20, 990), (510, 990), (480, 930), (40, 930), s=s), fill=255)
        sm.alpha_composite(shade(walls, (W, H), (150, 138, 126), 20))
        sm.alpha_composite(shade(roof, (W, H), (110, 90, 84), 10))
        sd = ImageDraw.Draw(sm)
        sd.rectangle([110, 1020, 420, 1240], fill=(12, 4, 6, 255))                   # inside (dark)
        sd.rectangle([120, 1170, 410, 1190], fill=(90, 60, 50, 255))                 # bench
        sd.text((265, 960), "WAITING SHED", font=font(INTER_SB, 30), fill=(60, 20, 16, 255), anchor="mm")
        for k in range(8):
            sd.line([(30 + k * 62, 935), (24 + k * 62, 990)], fill=(80, 64, 60, 255), width=3)     # corrugations
        self.shed = sm
        # lamp post + road sign
        lm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lm)
        ld.line([(560, 1240), (560, 700), (640, 680)], fill=(30, 26, 28, 255), width=12)
        ld.rectangle([610, 670, 680, 690], fill=(60, 50, 50, 255))
        self.lamp_xy = (645, 700)
        ld.line([(950, 1230), (950, 1000)], fill=(160, 160, 160, 255), width=10)
        ld.rounded_rectangle([830, 900, 1070, 1010], 10, fill=(18, 88, 48, 255), outline=(230, 230, 230, 255), width=4)
        ld.text((950, 935), "SAN ISIDRO", font=font(INTER_SB, 34), fill=(240, 240, 240, 255), anchor="mm")
        ld.text((950, 978), "2 KM  →", font=font(INTER_SB, 34), fill=(240, 240, 240, 255), anchor="mm")
        self.lamp = lm

    def frame(self, t, cam=0.0, extras=None, lamp=1.0):
        a = to_arr(self.base)
        fl = lamp * (0.85 + 0.15 * (math.sin(t * 23) > -0.7))
        add_glow(a, gsp(260, (255, 110, 50)), self.lamp_xy[0], self.lamp_xy[1] + 40, 0.9 * fl)
        img = to_img(a)
        img.alpha_composite(self.forest, (int(-cam * 0.4), 0))
        fog(img, t, 0.3, 1000, 1250, speed=12, col=(150, 44, 40))
        for z, fn in sorted(extras or [], key=lambda e: -e[0]):
            img = fn(img, t, -cam * 0.6) or img
        img.alpha_composite(self.lamp, (int(-cam * 0.7), 0))
        img.alpha_composite(self.shed, (int(-cam * 0.8), 0))
        a = to_arr(img)
        add_glow(a, gsp(120, (255, 170, 90)), self.lamp_xy[0] - cam * 0.7, self.lamp_xy[1] + 10, 0.8 * fl)
        img = to_img(a)
        bokeh_particles(img, 14, 61, t, color=(255, 150, 90), size=(2, 6), blur=(0, 2), area=(0, 500, W, 1600), drift=(8, -10))
        return img


_RS = None


def roadside():
    global _RS
    if _RS is None:
        _RS = Roadside()
    return _RS


# ============================================================ the old plank bridge
class Bridge:
    """Side view: an old plank bridge on wooden posts over a black creek with the red moon reflected; bamboo on both
    banks. self.deck_y = top of the planks; self.under = (x0, x1) space under the deck."""
    def __init__(self):
        a = moon_sky((780, 420), 100, top=(4, 1, 2), mid=(44, 6, 12), bot=(104, 18, 20), ym=0.5)
        img = to_img(a); d = ImageDraw.Draw(img)
        d.rectangle([0, 1180, W, H], fill=(10, 3, 4, 255))                         # water
        yy = np.arange(H)
        r = np.random.default_rng(12)
        for k in range(26):                                                      # moon reflection ripples
            y = 1200 + k * 18 + r.uniform(-4, 4); wd = 90 - k * 2 + r.uniform(-20, 20)
            d.line([(780 - wd, y), (780 + wd, y)], fill=(200, 50, 36, 200 - k * 6), width=4)
        # banks
        d.polygon([(0, 1060), (260, 1100), (330, 1220), (0, 1260)], fill=(30, 10, 10, 255))
        d.polygon([(W, 1040), (820, 1090), (760, 1220), (W, 1260)], fill=(30, 10, 10, 255))
        self.base = img
        m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
        for i in range(24):
            x = r.choice([r.uniform(-60, 260), r.uniform(830, W + 60)])
            culm(md, 1, x, 1120, -200, r.uniform(12, 26), (1 if x < 500 else -1) * r.uniform(60, 240))
        for i in range(50):
            leaf_spray(md, 1, r.choice([r.uniform(0, 330), r.uniform(760, W)]), r.uniform(100, 800), r.uniform(60, 120), r)
        self.bamboo = inflate21(m, (46, 12, 14), radius=10, rim=(255, 70, 50), rim_strength=0.8)
        self.deck_y = 1010

        def deck(d, s):
            d.rectangle([140 * s, 1010 * s, 940 * s, 1050 * s], fill=255)
            for x in (220, 420, 640, 860):
                d.rectangle([(x - 14) * s, 1040 * s, (x + 14) * s, 1300 * s], fill=255)
            d.line([(140 * s, 930 * s), (940 * s, 940 * s)], fill=255, width=int(12 * s))       # rail
            for x in (160, 360, 560, 760, 920):
                d.line([(x * s, 930 * s), (x * s, 1012 * s)], fill=255, width=int(10 * s))
        self.deck = shade(deck, (W, H), (84, 54, 38), 8, rim=(255, 90, 60))
        dd = ImageDraw.Draw(self.deck)
        for x in range(150, 940, 46):
            dd.line([(x, 1012), (x, 1048)], fill=(30, 16, 12, 255), width=3)
        dd.line([(560, 1010), (600, 1050)], fill=(10, 4, 4, 255), width=6)                     # broken plank

    def frame(self, t, cam=0.0, extras=None, under=None):
        img = self.base.copy()
        fog(img, t, 0.35, 1050, 1300, speed=10, col=(150, 44, 40))
        if under:
            img = under(img, t) or img
        img.alpha_composite(self.deck, (int(-cam * 0.6), 0))
        for z, fn in sorted(extras or [], key=lambda e: -e[0]):
            img = fn(img, t, -cam * 0.6) or img
        img.alpha_composite(self.bamboo, (int(-cam * 0.9), 0))
        bokeh_particles(img, 12, 71, t, color=(255, 140, 100), size=(2, 6), blur=(0, 2), area=(0, 400, W, 1500), drift=(5, -6))
        return img


_BR = None


def bridge():
    global _BR
    if _BR is None:
        _BR = Bridge()
    return _BR


class UnderBridge:
    """POV hiding under the bridge, looking up: planks across the top of the frame with thin gaps of red moonlight,
    two posts, black water below with ripples, the bank on the left. hooves(x) block the light in the gaps."""
    def __init__(self):
        a = vgrad((10, 3, 4), (6, 2, 3), (14, 4, 5), ym=0.5)
        img = to_img(a); d = ImageDraw.Draw(img)
        self.gaps = []
        y = 0
        P = Persp(540, 1100, 700)
        # planks seen from below: converging toward the far end
        for k in range(14):
            z0, z1 = 0.5 + k * 0.35, 0.5 + (k + 1) * 0.35
            x0, y0 = P.p(-1.6, -1.3, z0); x1, y1 = P.p(1.6, -1.3, z0)
            x2, y2 = P.p(1.6, -1.3, z1 - 0.04); x3, y3 = P.p(-1.6, -1.3, z1 - 0.04)
            d.polygon([(x0, y0), (x1, y1), (x2, y2), (x3, y3)], fill=(54, 30, 22, 255) if k % 2 else (62, 36, 26, 255))
            gx0, gy0 = P.p(-1.6, -1.3, z1 - 0.04); gx1, gy1 = P.p(1.6, -1.3, z1)
            self.gaps.append((gy0, gy1))
        for sx in (-1.2, 1.2):
            xa, ya = P.p(sx, -1.3, 1.6); xb, yb = P.p(sx, 1.4, 1.6)
            d.rectangle([xa - 40, ya, xa + 40, yb], fill=(30, 16, 12, 255))
        d.polygon([(0, 1380), (300, 1300), (520, 1500), (560, H), (0, H)], fill=(26, 10, 8, 255))   # bank
        self.P = P
        self.base = img
        gm = np.zeros((H, W), np.float32)
        for g0, g1 in self.gaps:
            gm[int(g0):int(max(g1, g0 + 2)) + 1, :] = 1.0
        self.gapmask = gm

    def frame(self, t, hooves=(), dust=0.0, extras=None, light=1.0):
        a = to_arr(self.base)
        gm = self.gapmask.copy()
        for hx, hw in hooves:                                                    # hooves block the light
            x0, x1 = int(max(0, hx - hw)), int(min(W, hx + hw))
            gm[:, x0:x1] *= 0.05
        fl = light * (0.85 + 0.15 * math.sin(t * 3))
        a += gm[..., None] * np.array([255, 70, 50], np.float32) * fl
        # light shafts down from the gaps
        sh = Image.fromarray((gm * 90 * fl).astype(np.uint8)).resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H))
        a += np.asarray(sh, np.float32)[..., None] / 255 * np.array([255, 60, 40], np.float32) * 0.8
        img = to_img(a)
        d = ImageDraw.Draw(img)
        for k in range(18):                                                      # water ripples
            y = 1450 + k * 26
            off = 30 * math.sin(t * 1.5 + k)
            d.line([(560 + off, y), (W - 80 + off, y)], fill=(110, 26, 22, 120), width=3)
        if dust > 0:
            r = np.random.default_rng(int(t * 10) % 5)
            for hx, hw in hooves:
                for _ in range(int(30 * dust)):
                    x = hx + r.uniform(-hw, hw); y = (r.uniform(300, 1400) + t * 400) % 1400 + 250
                    d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 140, 110, int(160 * dust)))
        for z, fn in sorted(extras or [], key=lambda e: -e[0]):
            img = fn(img, t) or img
        return img


_UB = None


def underbridge():
    global _UB
    if _UB is None:
        _UB = UnderBridge()
    return _UB


# ============================================================ Lola's house (night) + the window at dawn
def parol(size=1.0, k=1.0):
    """A parol: the five-pointed Christmas star lantern, glowing (red and gold) with tails."""
    w = int(320 * size)
    im = Image.new("RGBA", (w, int(w * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy, R = w / 2, w / 2, w * 0.45
    pts = []
    for i in range(10):
        rr = R if i % 2 == 0 else R * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=(255, 70, 40, int(255 * k)))
    inner = [(cx + (x - cx) * 0.6, cy + (y - cy) * 0.6) for x, y in pts]
    d.polygon(inner, fill=(255, 200, 90, int(255 * k)))
    d.ellipse([cx - R * 0.18, cy - R * 0.18, cx + R * 0.18, cy + R * 0.18], fill=(255, 245, 200, int(255 * k)))
    for j in (-1, 0, 1):
        d.line([(cx + j * R * 0.25, cy + R * 0.4), (cx + j * R * 0.4, cy + R * 2.2)], fill=(255, 120, 60, int(230 * k)), width=max(2, int(8 * size)))
    return im


class House:
    """Lola's house at the edge of the barangay: concrete lower floor, wooden upper floor with jalousie windows, a
    corrugated roof, a bamboo fence and gate, a parol star lantern glowing at the window. dawn=1: grey-pink morning,
    lights off, hoofprints circling in the mud."""
    def __init__(self, dawn=0.0):
        self.dawn = dawn
        if dawn:
            a = vgrad((70, 50, 64), (176, 110, 110), (210, 150, 130), ym=0.55)
        else:
            a = moon_sky((860, 360), 80, top=(4, 1, 2), mid=(48, 6, 12), bot=(110, 20, 22), ym=0.55)
        img = to_img(a); d = ImageDraw.Draw(img)
        r = np.random.default_rng(31)
        d.rectangle([0, 1220, W, H], fill=(46, 22, 18, 255) if dawn else (24, 8, 8, 255))
        self.base = img
        hm = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def lower(d, s):
            d.rectangle([180 * s, 960 * s, 900 * s, 1240 * s], fill=255)

        def upper(d, s):
            d.rectangle([150 * s, 640 * s, 930 * s, 970 * s], fill=255)

        def roof(d, s):
            d.polygon(P_((90, 660), (990, 660), (800, 470), (280, 470), s=s), fill=255)
        mul = 1.6 if dawn else 1.0
        hm.alpha_composite(shade(lower, (W, H), tuple(int(c * mul) for c in (96, 86, 80)), 20))
        hm.alpha_composite(shade(upper, (W, H), tuple(min(255, int(c * mul)) for c in (86, 50, 34)), 20))
        hm.alpha_composite(shade(roof, (W, H), tuple(min(255, int(c * mul)) for c in (70, 30, 28)), 16))
        hd = ImageDraw.Draw(hm)
        for x in range(160, 930, 26):
            hd.line([(x, 650), (x, 960)], fill=(50, 28, 20, 255), width=2)                    # wooden siding
        self.windows = [(250, 720, 470, 900), (610, 720, 830, 900)]
        for x0, y0, x1, y1 in self.windows:
            hd.rectangle([x0 - 10, y0 - 10, x1 + 10, y1 + 10], fill=(40, 20, 14, 255))
        hd.rectangle([470, 1020, 610, 1240], fill=(40, 22, 16, 255))                         # door
        self.house = hm
        fm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fm)
        for x in range(0, W, 22):                                                           # bamboo fence
            if 420 < x < 660:
                continue
            fd.rectangle([x, 1180 + (x % 3) * 6, x + 16, 1340], fill=(90, 70, 40, 255) if dawn else (44, 30, 20, 255))
        fd.rectangle([0, 1220, W, 1232], fill=(70, 50, 30, 255) if dawn else (34, 22, 16, 255))
        self.fence = fm
        self.prints = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if dawn:
            pd = ImageDraw.Draw(self.prints)
            for k in range(34):                                                              # hoofprints circling
                a_ = k / 34 * 2 * math.pi
                x = 540 + 470 * math.cos(a_); y = 1560 + 220 * math.sin(a_)
                if y < 1360:
                    continue
                sc = 0.6 + 0.4 * (y - 1340) / 440
                pd.chord([x - 26 * sc, y - 18 * sc, x + 26 * sc, y + 22 * sc], 160, 380, fill=(20, 8, 6, 255))
                pd.ellipse([x - 9 * sc, y - 4 * sc, x + 9 * sc, y + 12 * sc], fill=(46, 22, 18, 255))

    def frame(self, t, cam=0.0, extras=None, lights=1.0, star=1.0):
        a = to_arr(self.base)
        img = to_img(a)
        if not self.dawn:
            fog(img, t, 0.3, 1100, 1300, speed=10, col=(150, 44, 40))
        img.alpha_composite(self.house, (int(-cam * 0.5), 0))
        d = ImageDraw.Draw(img)
        for x0, y0, x1, y1 in self.windows:
            x0 -= cam * 0.5; x1 -= cam * 0.5
            col = (255, 170, 90) if lights > 0 and not self.dawn else ((120, 110, 120) if self.dawn else (20, 8, 8))
            for k in range(8):                                                               # jalousie slats
                y = y0 + k * (y1 - y0) / 8
                d.rectangle([x0, y + 2, x1, y + (y1 - y0) / 8 - 4], fill=col + (255,))
        a = to_arr(img)
        if lights > 0 and not self.dawn:
            for x0, y0, x1, y1 in self.windows:
                add_glow(a, gsp(200, (255, 150, 70)), (x0 + x1) / 2 - cam * 0.5, (y0 + y1) / 2, 0.55 * lights)
        img = to_img(a)
        if star > 0:
            p = parol(0.7, 1.0)
            px, py = 540 - cam * 0.5, 560
            a = to_arr(img); add_glow(a, gsp(180, (255, 90, 50)), px, py + 110, 0.9 * star * (0.85 + 0.15 * math.sin(t * 3)))
            img = to_img(a)
            img.alpha_composite(with_alpha(p, star), (int(px - p.width / 2), int(py)))
        img.alpha_composite(self.prints, (int(-cam * 0.9), 0))
        img.alpha_composite(self.fence, (int(-cam * 0.9), 0))
        for z, fn in sorted(extras or [], key=lambda e: -e[0]):
            img = fn(img, t, -cam * 0.5) or img
        return img


_HS = {}


def house(dawn=0.0):
    if dawn not in _HS:
        _HS[dawn] = House(dawn)
    return _HS[dawn]


class Window:
    """Close-up of Paolo's jalousie window at dawn: wooden frame and sill, glass slats tilted open, the pale morning
    outside, three long golden hairs lying on the sill. face(img, t) draws whatever is behind the glass."""
    def __init__(self):
        a = vgrad((40, 26, 30), (60, 38, 40), (30, 18, 18), ym=0.5)
        img = to_img(a); d = ImageDraw.Draw(img)
        d.rectangle([120, 260, 960, 1260], fill=(60, 34, 24, 255))                      # frame
        self.glass = (170, 310, 910, 1200)
        self.base = img
        sm = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def sill(d, s):
            d.polygon(P_((60, 1230), (1020, 1230), (1080, 1330), (0, 1330), s=s), fill=255)
        sm.alpha_composite(shade(sill, (W, H), (110, 72, 48), 16, rim=(255, 180, 140)))
        sd = ImageDraw.Draw(sm)
        for k, (x0, x1, yy) in enumerate(((180, 820, 1262), (260, 900, 1282), (220, 760, 1300))):
            pts = [(x0 + (x1 - x0) * u, yy + 8 * math.sin(u * 9 + k)) for u in np.linspace(0, 1, 16)]
            sd.line(pts, fill=GOLDH + (255,), width=4, joint="curve")
        self.sill = sm
        self.outside = vgrad((150, 120, 140), (200, 150, 140), (120, 90, 80), ym=0.6)

    def frame(self, t, face=None, hair_glow=1.0):
        img = self.base.copy()
        x0, y0, x1, y1 = self.glass
        out = to_img(self.outside)
        od = ImageDraw.Draw(out)
        for k in range(30):                                                               # bamboo far outside
            x = 100 + k * 34
            od.line([(x, 1300), (x + 30 * math.sin(k), 300)], fill=(110, 70, 76, 255), width=8)
        if face:
            out = face(out, t) or out
        img.paste(out.crop((x0, y0, x1, y1)), (x0, y0))
        d = ImageDraw.Draw(img)
        n = 9
        for k in range(n + 1):                                                            # slats (tilted glass)
            y = y0 + k * (y1 - y0) / n
            d.rectangle([x0, y - 6, x1, y + 8], fill=(150, 150, 160, 120))
            d.line([(x0, y + 8), (x1, y + 8)], fill=(230, 230, 240, 160), width=2)
        d.rectangle([x0 - 10, y0, x0, y1], fill=(60, 34, 24, 255))
        img.alpha_composite(self.sill)
        a = to_arr(img)
        if hair_glow > 0:
            add_glow(a, gsp(160, (255, 200, 90)), 540, 1280, 0.35 * hair_glow * (0.8 + 0.2 * math.sin(t * 4)))
        return to_img(a)


_WN = None


def window():
    global _WN
    if _WN is None:
        _WN = Window()
    return _WN
