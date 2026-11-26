"""Ep15 Laos / Phi Pop - art: the world, the characters and the spirit (2.1D flat21 style).
New world: Grandma's Lao stilt house at night (woven bamboo walls, a clay oil lamp, a mosquito net, a khene on the wall,
a sticky-rice basket on a low rattan table, a wooden shutter), the village yard with a slatted rice barn on posts and the
temple far across the paddies under a blood-red moon, the inside of the rice barn (red moonlight through the slats, rice
sacks, a hole in the thatch), a paddy dike running to the temple, and the temple gate with naga-serpent stair rails.
Hero: Noy (white blouse, dark red sinh with a gold hem, hair in a bun, white baci strings on her wrists) and her little
brother Tou. The spirit: the Phi Pop inside the kind neighbour, Auntie Kham - too tall, head tilted, arms too long,
glowing red eyes, a thin smile far too wide; on the wall its shadow has a long stretching neck. No gore."""
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

SKIN = (176, 124, 90)         # Noy + Tou
BLOUSE = (214, 200, 180)
SINH = (112, 18, 26)          # her tube skirt
SINH_HEM = (196, 146, 62)
TSHIRT = (190, 186, 176)      # Tou
SHORTS = (34, 40, 66)
HAIR = (12, 10, 12)
GHOST = (204, 198, 190)       # Auntie Kham, possessed (bone-pale)
KSKIN = (150, 108, 84)        # Auntie Kham, herself again
KSINH = (30, 18, 30)
KSASH = (150, 24, 30)
STRING = (250, 246, 236)
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
    """Laos: red / blue (double height) / red, a white disc in the middle (diameter 0.8 of the blue band)."""
    global _FLAG
    if _FLAG is None:
        w, h, s = 300, 200, 4
        W2, H2 = w * s, h * s
        im = Image.new("RGBA", (W2, H2), (206, 17, 38, 255)); d = ImageDraw.Draw(im)
        d.rectangle([0, H2 / 4, W2, H2 * 3 / 4], fill=(0, 40, 104, 255))
        r = H2 / 2 * 0.8 / 2
        d.ellipse([W2 / 2 - r, H2 / 2 - r, W2 / 2 + r, H2 / 2 + r], fill=(255, 255, 255, 255))
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


def clock_ui(strings, clock, t, k=1.0, label="DAWN DRUM 5:30"):
    """The ticking clock: Grandma's three white strings (each one that snaps turns red and broken) + the time."""
    f1 = font(INTER_SB, 46); f2 = font(INTER_M, 24)
    w, h = 640, 108
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(0, 0, 0, int(185 * k)), outline=(255, 70, 50, int(200 * k)), width=3)
    blink = math.sin(t * 9) > -0.2
    for i in range(3):
        x = 40 + i * 62
        ok = i < strings
        if ok:
            col = (250, 246, 236, int(255 * k))
            pts = [(x + 10 * math.sin(j * 0.9 + i), 24 + j * 6) for j in range(11)]
            d.line(pts, fill=col, width=6, joint="curve")
            d.ellipse([x - 9, 50, x + 9, 66], fill=col)
        else:
            col = (255, 60, 40, int(255 * k * (1 if blink else 0.35)))
            d.line([(x - 4, 24), (x + 6, 46), (x - 2, 52)], fill=col, width=6)
            d.line([(x + 4, 66), (x - 6, 74), (x + 2, 86)], fill=col, width=6)
    d.line([(222, 22), (222, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    # clock icon
    cx, cy = 270, 54
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=(255, 190, 140, int(255 * k)), width=4)
    d.line([(cx, cy), (cx, cy - 14)], fill=(255, 190, 140, int(255 * k)), width=4)
    d.line([(cx, cy), (cx + 10, cy + 6)], fill=(255, 190, 140, int(255 * k)), width=4)
    d.text((455, h / 2 - 22), label, font=f2, fill=(255, 190, 140, int(255 * k)), anchor="mm")
    dawn = clock == "DAWN"
    d.text((455, h / 2 + 18), clock, font=f1, fill=((255, 214, 120) if dawn else (255, 240, 228)) + (int(250 * k),), anchor="mm")
    return im


def put_clock(out, strings, clock, t, k=1.0, y=200):
    ui = clock_ui(strings, clock, t, k)
    out.alpha_composite(ui, (int(W / 2 - ui.width / 2), int(y)))


# ============================================================ Noy
_NC = {}


def noy(phase=0.0, run=0.0, back=False, scale=1.0, strings=True, lift=0.0, carry=False):
    """Noy: white blouse, dark red sinh (tube skirt) with a gold hem, black hair in a bun, bare feet, white strings on her
    wrists. lift: arms raised in front (lifting the net / reaching). carry: holding Tou on her hip.
    Returns (RGBA, feet_x, feet_y)."""
    q = (round(phase * 12) % 12, round(run, 1), back, round(scale, 2), strings, round(lift, 1), carry)
    if q in _NC:
        return _NC[q]
    w, h = 460, 920
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.25 + 0.75 * run)
    L = 14 * run

    def feet_pts(sg):
        a = sg * sw * 0.5
        return cx + sg * 22 + math.sin(a) * 70 + L * 0.2, 860 - (abs(math.sin(a)) * 30 * run)

    def legs(d, s):
        for sg in (-1, 1):
            fx, fy = feet_pts(sg)
            d.line([((cx + sg * 22 + L * .3) * s, 760 * s), (fx * s, fy * s)], fill=255, width=int(30 * s))
            d.ellipse([(fx - 24) * s, (fy - 6) * s, (fx + 26) * s, (fy + 12) * s], fill=255)

    def skirt(d, s):
        flare = 18 * run * math.sin(ph)
        d.polygon(P_((cx - 70 + L * .6, 420), (cx + 70 + L * .6, 420), (cx + 78 + flare + L * .3, 800), (cx - 78 + flare + L * .3, 800), s=s), fill=255)

    def torso(d, s):
        d.polygon(P_((cx - 66 + L, 200), (cx + 66 + L, 200), (cx + 50 + L * .8, 330), (cx + 60 + L * .7, 440), (cx - 60 + L * .7, 440), (cx - 50 + L * .8, 330), s=s), fill=255)
        d.ellipse([(cx - 80 + L) * s, 192 * s, (cx - 36 + L) * s, 240 * s], fill=255)
        d.ellipse([(cx + 36 + L) * s, 192 * s, (cx + 80 + L) * s, 240 * s], fill=255)

    hands = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 70 + L, 216
        a = -sg * sw * 0.9
        if lift > 0:
            a = -sg * 0.3 * (1 - lift) + (-2.4 * lift if not back else 2.6 * lift) * (1 if sg < 0 else 1)
            ex, ey = sx + sg * 30 * (1 - lift), sy + 110 - 160 * lift
            hx, hy = ex - sg * 30 * lift, ey + 80 - 170 * lift
        elif carry and sg == -1:
            ex, ey = sx - 20, sy + 120
            hx, hy = cx + 40, 400
        else:
            ex, ey = sx + math.sin(a) * 90 + sg * 8, sy + math.cos(a) * 100
            b = a - 0.9 * run * sg
            hx, hy = ex + math.sin(b) * 86, ey + math.cos(b) * 82 - 40 * run
        hands[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            pts = hands[sg]
            d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(26 * s), joint="curve")
            hx, hy = pts[2]
            d.ellipse([(hx - 15) * s, (hy - 15) * s, (hx + 15) * s, (hy + 15) * s], fill=255)

    def sleeves(d, s):
        for sg in (-1, 1):
            (sx, sy), (ex, ey), _ = hands[sg]
            mx, my = sx + (ex - sx) * 0.35, sy + (ey - sy) * 0.35
            d.line([(sx * s, sy * s), (mx * s, my * s)], fill=255, width=int(36 * s))
            d.ellipse([(sx - 26) * s, (sy - 24) * s, (sx + 26) * s, (sy + 26) * s], fill=255)
            d.ellipse([(mx - 18) * s, (my - 18) * s, (mx + 18) * s, (my + 18) * s], fill=255)

    def head(d, s):
        Lh = L * 1.2
        d.rectangle([(cx - 18 + Lh) * s, 140 * s, (cx + 18 + Lh) * s, 200 * s], fill=255)
        d.ellipse([(cx - 48 + Lh) * s, 34 * s, (cx + 48 + Lh) * s, 166 * s], fill=255)

    def hair(d, s):
        Lh = L * 1.2
        d.pieslice([(cx - 52 + Lh) * s, 26 * s, (cx + 52 + Lh) * s, 140 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 52 + Lh, 82), (cx - 48 + Lh, 112), (cx - 30 + Lh, 70), (cx + 30 + Lh, 70), (cx + 48 + Lh, 112), (cx + 52 + Lh, 82), s=s), fill=255)
        d.ellipse([(cx - 30 + Lh) * s, 0, (cx + 30 + Lh) * s, 56 * s], fill=255)                # the bun
        if back:
            d.ellipse([(cx - 50 + Lh) * s, 30 * s, (cx + 50 + Lh) * s, 158 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), SKIN, 14))
    img.alpha_composite(shade(skirt, (w, h), SINH, 36))
    d = ImageDraw.Draw(img)
    flare = 18 * run * math.sin(ph)
    for k_, (y0, wd) in enumerate(((742, 22), (772, 8), (788, 6))):              # the woven gold hem
        d.line([(cx - 76 + flare + L * .3, y0), (cx + 76 + flare + L * .3, y0)], fill=SINH_HEM + (255,), width=wd)
    for j in range(9):
        x = cx - 64 + j * 16 + flare + L * .3
        d.polygon([(x, 734), (x + 8, 742), (x, 750), (x - 8, 742)], fill=(90, 12, 18, 255))
    if not back:
        img.alpha_composite(shade(arms, (w, h), SKIN, 10))
    img.alpha_composite(shade(torso, (w, h), BLOUSE, 34))
    img.alpha_composite(shade(sleeves, (w, h), BLOUSE, 14))
    if back:
        img.alpha_composite(shade(arms, (w, h), SKIN, 10))
    img.alpha_composite(shade(head, (w, h), SKIN, 26))
    img.alpha_composite(shade(hair, (w, h), HAIR, 12, rim_strength=1.1))
    d = ImageDraw.Draw(img)
    Lh = L * 1.2
    if not back:
        for sg in (-1, 1):
            d.ellipse([cx + sg * 18 - 9 + Lh, 96, cx + sg * 18 + 9 + Lh, 112], fill=(240, 236, 230, 255))
            d.ellipse([cx + sg * 18 - 5 + Lh, 99, cx + sg * 18 + 5 + Lh, 109], fill=(15, 10, 10, 255))
            d.line([(cx + sg * 18 - 11 + Lh, 86), (cx + sg * 18 + 11 + Lh, 88 - 3 * sg)], fill=(20, 12, 10, 255), width=4)
        d.ellipse([cx - 7 + Lh, 136, cx + 7 + Lh, 146], fill=(80, 30, 28, 255))
        d.line([(cx - 34 + L, 202), (cx + L, 236), (cx + 34 + L, 202)], fill=(170, 150, 130, 255), width=4)   # collar
    if strings:
        for sg in (-1, 1):
            (_, _), (ex, ey), (hx, hy) = hands[sg]
            wx, wy = ex + (hx - ex) * 0.78, ey + (hy - ey) * 0.78
            d.line([(wx - 13, wy - 3), (wx + 13, wy + 3)], fill=STRING + (255,), width=4)
            d.line([(wx - 13, wy + 4), (wx + 13, wy + 9)], fill=STRING + (255,), width=3)
    if carry:
        tb, tfx, tfy = tou("hip", 0.62)
        img.alpha_composite(tb, (int(cx + 10 - tb.width / 2 + (60 if not back else -60)), 170))
        if not back:
            img.alpha_composite(shade(arms, (w, h), SKIN, 10))
    if scale != 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    out = (img, cx * scale, 866 * scale)
    _NC[q] = out
    return out


_NCR = {}


def noy_crouch(scale=1.0, look=0.0, strings=3, arm_out=0.0):
    """Noy crouched in the barn, hugging her knees, hand near her mouth. look: head turns up (+) / right. arm_out: her
    left wrist held out to the side (for the snapping string). Returns (RGBA, feet_x, feet_y, wrist_xy)."""
    k = (round(scale, 2), round(look, 1), strings, round(arm_out, 1))
    if k in _NCR:
        return _NCR[k]
    w, h = 520, 640
    cx = w / 2

    def skirt(d, s):
        d.polygon(P_((cx - 96, 330), (cx + 96, 330), (cx + 130, 600), (cx - 130, 600), s=s), fill=255)
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 50 - 56) * s, 290 * s, (cx + sg * 50 + 56) * s, 400 * s], fill=255)

    def feet(d, s):
        for sg in (-1, 1):
            d.ellipse([(cx + sg * 64 - 38) * s, 588 * s, (cx + sg * 64 + 38) * s, 618 * s], fill=255)

    def body(d, s):
        d.polygon(P_((cx - 84, 200), (cx + 84, 200), (cx + 90, 360), (cx - 90, 360), s=s), fill=255)
        d.ellipse([(cx - 100) * s, 190 * s, (cx - 54) * s, 256 * s], fill=255)
        d.ellipse([(cx + 54) * s, 190 * s, (cx + 100) * s, 256 * s], fill=255)

    wx, wy = cx - 150 - 120 * arm_out, 380 - 40 * arm_out

    def arms(d, s):
        d.line([((cx - 92) * s, 230 * s), ((cx - 120 - 60 * arm_out) * s, 330 * s), (wx * s, wy * s)], fill=255, width=int(28 * s), joint="curve")
        d.ellipse([(wx - 16) * s, (wy - 16) * s, (wx + 16) * s, (wy + 16) * s], fill=255)
        d.line([((cx + 92) * s, 230 * s), ((cx + 90) * s, 310 * s), ((cx + 14) * s, 190 * s)], fill=255, width=int(26 * s), joint="curve")
        d.ellipse([(cx - 10) * s, 170 * s, (cx + 30) * s, 206 * s], fill=255)

    L = look * 26

    def head(d, s):
        d.ellipse([(cx - 50 + L * .3) * s, (70 - L) * s, (cx + 50 + L * .3) * s, (204 - L) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 56 + L * .3) * s, (58 - L) * s, (cx + 56 + L * .3) * s, (176 - L) * s], 180, 360, fill=255)
        d.ellipse([(cx - 28 + L * .3) * s, (30 - L) * s, (cx + 28 + L * .3) * s, (84 - L) * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(body, (w, h), BLOUSE, 36))
    img.alpha_composite(shade(head, (w, h), SKIN, 28))
    img.alpha_composite(shade(hair, (w, h), HAIR, 12))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):                                                      # wide scared eyes
        ex_ = cx + sg * 19 + L * .3; ey_ = 136 - L * 1.1
        d.ellipse([ex_ - 10, ey_ - 9, ex_ + 10, ey_ + 9], fill=(240, 236, 230, 255))
        d.ellipse([ex_ - 4 + look * 2, ey_ - 8, ex_ + 4 + look * 2, ey_ + 1], fill=(15, 10, 10, 255))
    img.alpha_composite(shade(skirt, (w, h), SINH, 34))
    d = ImageDraw.Draw(img)
    d.line([(cx - 126, 578), (cx + 126, 578)], fill=SINH_HEM + (255,), width=16)
    img.alpha_composite(shade(feet, (w, h), SKIN, 6))
    img.alpha_composite(shade(arms, (w, h), SKIN, 12))
    d = ImageDraw.Draw(img)
    for i in range(strings):                                                 # the strings left on her wrist
        d.line([(wx - 15, wy - 10 + i * 8), (wx + 15, wy - 4 + i * 8)], fill=STRING + (255,), width=4)
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 610 * scale, (wx * scale, wy * scale))
    _NCR[k] = out
    return out


# ============================================================ Tou
_TC = {}


def tou(pose="sleep", scale=1.0):
    """Tou, about six: white tee, dark shorts, black hair. pose: "sleep" (curled on his side), "sit" (side view, eating a
    ball of sticky rice), "hip" (held on Noy's hip, arms round her). Returns (RGBA, x_anchor, y_anchor)."""
    k = (pose, round(scale, 2))
    if k in _TC:
        return _TC[k]
    w, h = 360, 420
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if pose == "sleep":
        def body(d, s):
            d.ellipse([110 * s, 250 * s, 270 * s, 340 * s], fill=255)
        def legs(d, s):
            d.line([(250 * s, 300 * s), (320 * s, 330 * s), (300 * s, 370 * s)], fill=255, width=int(34 * s), joint="curve")
        def head(d, s):
            d.ellipse([40 * s, 250 * s, 130 * s, 330 * s], fill=255)
        def hair(d, s):
            d.pieslice([34 * s, 244 * s, 136 * s, 336 * s], 150, 330, fill=255)
        img.alpha_composite(shade(legs, (w, h), SHORTS, 14))
        img.alpha_composite(shade(body, (w, h), TSHIRT, 30))
        img.alpha_composite(shade(head, (w, h), SKIN, 24))
        img.alpha_composite(shade(hair, (w, h), HAIR, 10))
        d = ImageDraw.Draw(img)
        d.arc([62, 282, 82, 296], 0, 180, fill=(30, 16, 14, 255), width=3)          # closed eye
        ax, ay = 180, 380
    elif pose == "sit":
        def legs(d, s):
            d.line([(150 * s, 330 * s), (250 * s, 330 * s), (262 * s, 400 * s)], fill=255, width=int(36 * s), joint="curve")
        def body(d, s):
            d.polygon(P_((110, 190), (190, 190), (196, 340), (104, 340), s=s), fill=255)
        def arm(d, s):
            d.line([(160 * s, 210 * s), (210 * s, 270 * s), (196 * s, 160 * s)], fill=255, width=int(22 * s), joint="curve")
        def head(d, s):
            d.ellipse([100 * s, 70 * s, 200 * s, 180 * s], fill=255)
        def hair(d, s):
            d.pieslice([94 * s, 62 * s, 204 * s, 168 * s], 170, 360, fill=255)
            d.ellipse([94 * s, 66 * s, 150 * s, 150 * s], fill=255)
        img.alpha_composite(shade(legs, (w, h), SHORTS, 16))
        img.alpha_composite(shade(body, (w, h), TSHIRT, 30))
        img.alpha_composite(shade(head, (w, h), SKIN, 26))
        img.alpha_composite(shade(hair, (w, h), HAIR, 12))
        img.alpha_composite(shade(arm, (w, h), SKIN, 10))
        d = ImageDraw.Draw(img)
        d.ellipse([180, 132, 214, 162], fill=(236, 230, 214, 255))                   # sticky rice ball
        d.ellipse([174, 108, 186, 120], fill=(20, 10, 10, 255))                      # eye
        ax, ay = 160, 400
    else:  # hip
        def body(d, s):
            d.rounded_rectangle([140 * s, 150 * s, 236 * s, 300 * s], int(30 * s), fill=255)
        def legs(d, s):
            d.line([(160 * s, 290 * s), (110 * s, 330 * s), (120 * s, 380 * s)], fill=255, width=int(28 * s), joint="curve")
        def head(d, s):
            d.ellipse([140 * s, 40 * s, 240 * s, 150 * s], fill=255)
        def hair(d, s):
            d.pieslice([134 * s, 32 * s, 246 * s, 140 * s], 180, 360, fill=255)
        img.alpha_composite(shade(legs, (w, h), SHORTS, 14))
        img.alpha_composite(shade(body, (w, h), TSHIRT, 30))
        img.alpha_composite(shade(head, (w, h), SKIN, 24))
        img.alpha_composite(shade(hair, (w, h), HAIR, 10))
        d = ImageDraw.Draw(img)
        d.arc([196, 92, 214, 104], 0, 180, fill=(30, 16, 14, 255), width=3)
        ax, ay = 180, 400
    if scale != 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    out = (img, ax * scale, ay * scale)
    _TC[k] = out
    return out


# ============================================================ Auntie Kham + the Phi Pop
_KC = {}


def kham(pose="stand", tilt=0.0, possessed=True, step=0, reach=0.0, scale=1.0):
    """Auntie Kham. possessed: bone-pale skin, arms far too long with long fingers, head tilted (tilt deg), hair loose
    from its bun; herself: brown skin, normal arms, tidy bun. Dark sinh, red pha biang sash over one shoulder.
    pose: "stand" | "side" (running in profile, stop-motion step 0/1) | "kneel" (fallen to her knees, head bowed).
    reach 0..1: her right arm lifts toward the viewer. Returns (RGBA, feet_x, feet_y, [eye xy])."""
    key = (pose, round(tilt), possessed, step % 2, round(reach, 1), round(scale, 2))
    if key in _KC:
        return _KC[key]
    w, h = 700, 1300
    cx = w / 2
    skin = GHOST if possessed else KSKIN
    long_ = 1.0 if possessed else 0.0
    kneel = pose == "kneel"; side = pose == "side"
    by = 1240                                                     # feet
    hip = 700 if not kneel else 1000
    sh = 300 if not kneel else 640
    head_c = (cx + (40 if kneel else 0), sh - 120 + (60 if kneel else 0))
    ang = math.radians(tilt + (35 if kneel else 0))

    def R(*pts):
        return rot(pts, ang, head_c[0], head_c[1] + 70)

    lean = 60 if side else 0

    def skirt(d, s):
        if kneel:
            d.polygon(P_((cx - 110, hip - 60), (cx + 110, hip - 60), (cx + 170, by), (cx - 150, by), s=s), fill=255)
        elif side:
            a = 1 if step % 2 else -1
            d.polygon(P_((cx - 80 + lean, hip - 30), (cx + 80 + lean, hip - 30), (cx + 110 + 60 * a, by - 60), (cx - 110 + 40 * a, by - 60), s=s), fill=255)
        else:
            d.polygon(P_((cx - 90, hip - 30), (cx + 90, hip - 30), (cx + 96, by - 40), (cx - 96, by - 40), s=s), fill=255)

    def feet(d, s):
        if kneel:
            return
        for sg in (-1, 1):
            off = (50 * (1 if (step % 2) == (sg > 0) else -1)) if side else sg * 40
            d.line([((cx + off * 0.5 + lean * .5) * s, (by - 80) * s), ((cx + off) * s, (by - 6) * s)], fill=255, width=int(26 * s))
            d.ellipse([(cx + off - 24) * s, (by - 16) * s, (cx + off + 30) * s, (by + 4) * s], fill=255)

    def torso(d, s):
        L = lean
        d.polygon(P_((cx - 80 + L, sh), (cx + 80 + L, sh), (cx + 62 + L * .6, hip), (cx - 62 + L * .6, hip), s=s), fill=255)
        d.ellipse([(cx - 100 + L) * s, (sh - 14) * s, (cx - 40 + L) * s, (sh + 50) * s], fill=255)
        d.ellipse([(cx + 40 + L) * s, (sh - 14) * s, (cx + 100 + L) * s, (sh + 50) * s], fill=255)
        d.line([(head_c[0] * s, (head_c[1] + 60) * s), ((cx + L) * s, (sh + 10) * s)], fill=255, width=int(40 * s))

    arm = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 84 + lean, sh + 20
        if kneel:
            ex, ey = sx + sg * 40, sy + 200; hx, hy = sx + sg * 70, by - 20
        elif side:
            sw_ = (1 if (step % 2) == (sg > 0) else -1)
            ex, ey = sx + 90 * sw_ * long_ + 40, sy + 200
            hx, hy = ex + 150 * sw_ + 120 * long_, ey + 160 + 120 * long_
        elif reach > 0 and sg == 1:
            ex, ey = sx + 90, sy + 200 - 160 * reach
            hx, hy = ex + 60 - 160 * reach, ey + 250 - 380 * reach
        else:
            ex, ey = sx + sg * 26, sy + 260 + 60 * long_
            hx, hy = sx + sg * 40, sy + 520 + 300 * long_                # far too long: hands at her knees
        arm[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            p = arm[sg]
            d.line([(x * s, y * s) for x, y in p], fill=255, width=int(24 * s), joint="curve")
            (ex, ey), (hx, hy) = p[1], p[2]
            vx, vy = hx - ex, hy - ey; n = math.hypot(vx, vy) + 1e-6; vx, vy = vx / n, vy / n
            fl = 34 + 70 * long_
            for k in range(4):
                a = math.atan2(vy, vx) + (k - 1.5) * 0.16
                d.line([(hx * s, hy * s), ((hx + math.cos(a) * fl) * s, (hy + math.sin(a) * fl) * s)], fill=255, width=int(8 * s))

    def sash(d, s):
        L = lean
        d.polygon(P_((cx - 84 + L, sh + 6), (cx - 40 + L, sh - 6), (cx + 70 + L * .7, sh + 260), (cx + 40 + L * .7, sh + 300), s=s), fill=255)

    hx0, hy0 = head_c

    def head(d, s):
        d.polygon(P_(*R((hx0 - 44, hy0 - 50), (hx0 + 44, hy0 - 50), (hx0 + 50, hy0 + 20), (hx0 + 30, hy0 + 70), (hx0, hy0 + 84), (hx0 - 30, hy0 + 70), (hx0 - 50, hy0 + 20)), s=s), fill=255)
        d.ellipse([(hx0 - 50) * s, (hy0 - 90) * s, (hx0 + 50) * s, (hy0 + 10) * s], fill=255) if not ang else None

    def hair(d, s):
        r = np.random.default_rng(15)
        d.polygon(P_(*R((hx0 - 56, hy0 - 20), (hx0 - 50, hy0 - 82), (hx0, hy0 - 100), (hx0 + 50, hy0 - 82), (hx0 + 56, hy0 - 20), (hx0 + 30, hy0 - 56), (hx0, hy0 - 62), (hx0 - 30, hy0 - 56)), s=s), fill=255)
        if possessed:                                                # loose strands falling over her face and shoulders
            for k in range(16):
                x = hx0 - 54 + k * 7.2
                ln = r.uniform(120, 360)
                d.line([(x * s, (hy0 - 70) * s)] + [p_ * s for p_ in R((x + r.uniform(-20, 20), hy0 + ln))[0]], fill=255, width=int(r.uniform(5, 11) * s))
            for sg in (-1, 1):
                d.polygon(P_(*R((hx0 + sg * 50, hy0 - 40), (hx0 + sg * 64, hy0 - 10), (hx0 + sg * 90, hy0 + 300), (hx0 + sg * 40, hy0 + 160)), s=s), fill=255)
        else:
            d.ellipse([(hx0 - 30) * s, (hy0 - 130) * s, (hx0 + 30) * s, (hy0 - 74) * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(feet, (w, h), skin, 10))
    img.alpha_composite(shade(skirt, (w, h), KSINH, 40, rim_strength=1.0))
    d = ImageDraw.Draw(img)
    hy_ = by - 70 if not kneel else by - 30
    d.line([(cx - 100, hy_), (cx + 100, hy_)], fill=(110, 70, 34, 255), width=14)
    img.alpha_composite(shade(torso, (w, h), KSINH if possessed else (60, 40, 44), 36))
    img.alpha_composite(shade(sash, (w, h), KSASH, 16))
    img.alpha_composite(shade(arms, (w, h), skin, 10, rim_strength=1.0))
    img.alpha_composite(shade(head, (w, h), skin, 30))
    img.alpha_composite(shade(hair, (w, h), HAIR, 10, rim_strength=1.2))
    d = ImageDraw.Draw(img)
    fl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); fd = ImageDraw.Draw(fl)
    if possessed:
        for sg in (-1, 1):                                           # dark eye hollows (the glow is drawn by put_kham)
            fd.ellipse([hx0 + sg * 20 - 13, hy0 - 4, hx0 + sg * 20 + 13, hy0 + 14], fill=(20, 8, 10, 255))
        fd.arc([hx0 - 40, hy0 + 8, hx0 + 40, hy0 + 58], 20, 160, fill=(30, 8, 10, 255), width=5)      # a smile too wide
    else:
        for sg in (-1, 1):
            fd.ellipse([hx0 + sg * 18 - 7, hy0 + 2, hx0 + sg * 18 + 7, hy0 + 12], fill=(20, 12, 10, 255))
        fd.line([(hx0 - 12, hy0 + 44), (hx0 + 12, hy0 + 44)], fill=(90, 40, 34, 255), width=4)
        fd.ellipse([hx0 - 56, hy0 + 18, hx0 - 46, hy0 + 30], fill=(220, 180, 80, 255))               # gold earring
    if ang:
        fl = fl.rotate(-math.degrees(ang), resample=Image.BICUBIC, center=(head_c[0], head_c[1] + 70))
    img.alpha_composite(fl)
    eyes = [R((hx0 - 20, hy0 + 5))[0], R((hx0 + 20, hy0 + 5))[0]]
    if scale != 1.0:
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
        eyes = [(x * scale, y * scale) for x, y in eyes]
    out = (img, cx * scale, by * scale, eyes)
    _KC[key] = out
    return out


def put_kham(img, x, y, scale, t, pose="stand", tilt=0.0, possessed=True, step=0, reach=0.0, eyes=1.0, aura=0.4, alpha=1.0, dark=0.0):
    body, fx, fy, ee = kham(pose, tilt, possessed, step, reach)
    g = body.resize((max(1, int(body.width * scale)), max(1, int(body.height * scale))), Image.LANCZOS)
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
    if eyes > 0 and possessed:
        k = eyes * alpha * (0.65 + 0.35 * math.sin(t * 5) ** 2)
        for ex, ey in ee:
            eye(img, gx + ex * scale, gy + ey * scale, k, max(0.2, scale * 0.8))
    return img


_KF = {}


def kham_face(grin=1.0, inv=False):
    """Close-up of the possessed face for jump scares: bone-pale, wet black hair falling in strands over it, deep eye
    hollows (red glow drawn by put_kface), a thin smile far too wide (no teeth, no gore), red sash at the bottom.
    inv: upside down (looking down from the roof), the hair hanging. Face centre at (450, 470)."""
    k = (round(grin, 1), inv)
    if k in _KF:
        return _KF[k]
    w, h = 900, 1100
    cx, cy = 450, 470

    def face(d, s):
        d.polygon(P_((cx - 190, cy - 230), (cx + 190, cy - 230), (cx + 220, cy - 20), (cx + 170, cy + 200), (cx + 70, cy + 300),
                     (cx, cy + 320), (cx - 70, cy + 300), (cx - 170, cy + 200), (cx - 220, cy - 20), s=s), fill=255)
        d.ellipse([(cx - 220) * s, (cy - 380) * s, (cx + 220) * s, (cy + 40) * s], fill=255)

    def neck(d, s):
        d.rectangle([(cx - 90) * s, (cy + 200) * s, (cx + 90) * s, h * s], fill=255)

    def hair(d, s):
        r = np.random.default_rng(23)
        d.pieslice([(cx - 250) * s, (cy - 420) * s, (cx + 250) * s, (cy + 60) * s], 180, 360, fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 120, cy - 300), (cx + sg * 250, cy - 180), (cx + sg * 290, cy + 560), (cx + sg * 170, cy + 600), (cx + sg * 200, cy - 60), s=s), fill=255)
        for kk in range(14):                                          # strands across the face
            x = cx - 200 + kk * 31 + r.uniform(-8, 8)
            if abs(x - cx - 0) < 40 or abs(abs(x - cx) - 80) < 26:
                continue
            ln = r.uniform(240, 640)
            d.line([(x * s, (cy - 250) * s), ((x + r.uniform(-30, 30)) * s, (cy - 250 + ln * .5) * s), ((x + r.uniform(-50, 50)) * s, (cy - 250 + ln) * s)],
                   fill=255, width=int(r.uniform(9, 18) * s), joint="curve")

    def sash(d, s):
        d.polygon(P_((cx - 300, h), (cx - 160, cy + 330), (cx + 40, cy + 360), (cx - 60, h), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(neck, (w, h), GHOST, 40))
    img.alpha_composite(shade(sash, (w, h), KSASH, 30))
    img.alpha_composite(shade(face, (w, h), GHOST, 110, rim_strength=0.9))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        d.ellipse([cx + sg * 80 - 52, cy - 50, cx + sg * 80 + 52, cy + 34], fill=(26, 10, 12, 255))
        d.line([(cx + sg * 30, cy - 92), (cx + sg * 128, cy - 74 + 14 * sg * 0)], fill=(80, 60, 60, 255), width=6)
    d.polygon([(cx - 12, cy + 70), (cx + 12, cy + 70), (cx + 20, cy + 120), (cx - 20, cy + 120)], fill=(170, 160, 152, 255))
    gw = 120 + 90 * grin                                               # a thin smile, far too wide, curling up
    d.arc([cx - gw, cy + 60, cx + gw, cy + 230 + 30 * grin], 15, 165, fill=(28, 6, 8, 255), width=12)
    for sg in (-1, 1):
        d.line([(cx + sg * gw * 0.95, cy + 170), (cx + sg * (gw + 30), cy + 120)], fill=(28, 6, 8, 255), width=10)
    img.alpha_composite(shade(hair, (w, h), HAIR, 24, rim_strength=1.3))
    eyes = [(cx - 80, cy - 8), (cx + 80, cy - 8)]
    if inv:
        img = img.rotate(180, resample=Image.BICUBIC, center=(cx, cy))
        eyes = [(2 * cx - x, 2 * cy - y) for x, y in eyes]
    _KF[k] = (img, eyes)
    return _KF[k]


def put_kface(img, x, y, scale, t, eyes=1.0, grin=1.0, tilt=0.0, aura=0.7, alpha=1.0, inv=False):
    fimg, ee = kham_face(grin, inv)
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


def pop_shadow_mask(neck=0.0, turn=0.0, reach=0.0, seated=True, w=900, h=1300, child=False):
    """The Phi Pop's shadow (an 'L' mask): a person's silhouette whose neck stretches up (neck 0..1 adds ~420 px), the
    head long and narrow, turning toward the viewer (turn 0..1), long fingers reaching out (reach 0..1).
    Anchor: bottom centre (w/2, h)."""
    m = Image.new("L", (w * 2, h * 2), 0); d = ImageDraw.Draw(m); s = 2
    cx = w / 2
    sc = 0.62 if child else 1.0
    base = h
    if seated:
        d.ellipse([(cx - 230 * sc) * s, (base - 200 * sc) * s, (cx + 230 * sc) * s, (base + 60) * s], fill=255)       # folded legs
    sh_y = base - (520 if seated else 820) * sc
    d.polygon(P_((cx - 120 * sc, sh_y), (cx + 120 * sc, sh_y), (cx + 140 * sc, base - 120 * sc), (cx - 140 * sc, base - 120 * sc), s=s), fill=255)
    d.ellipse([(cx - 150 * sc) * s, (sh_y - 20) * s, (cx + 150 * sc) * s, (sh_y + 90 * sc) * s], fill=255)
    nk = 70 * sc + 420 * neck * sc
    hx = cx + 30 * sc * turn
    top = sh_y - nk
    d.line([(cx * s, (sh_y + 20) * s), ((cx + 40 * neck * sc) * s, (sh_y - nk * 0.5) * s), (hx * s, (top + 20) * s)], fill=255, width=int(56 * sc * (1 - 0.35 * neck) * s), joint="curve")
    hl = (190 + 90 * neck) * sc; hw = (74 - 6 * neck) * sc
    ang = math.radians(-38 * turn)                                     # the head tilts over as it turns to us
    def Rh(*pts):
        return [(hx + (x - hx) * math.cos(ang) - (y - top) * math.sin(ang), top + (x - hx) * math.sin(ang) + (y - top) * math.cos(ang)) for x, y in pts]
    hcx, hcy = hx, top - hl * 0.42
    ell = [(hcx + hw * math.cos(u) * (1 - 0.25 * max(0, math.sin(u))), hcy + hl * 0.55 * math.sin(u)) for u in np.linspace(0, 2 * math.pi, 40)]
    headp = Rh(*ell)
    d.polygon(P_(*headp, s=s), fill=255)
    # hair hangs straight down (gravity) from the crown of the tilted head: long, past the chin
    upper = [p for p, u in zip(headp, np.linspace(0, 2 * math.pi, 40)) if math.sin(u) < 0.15]
    xl = min(p[0] for p in upper); xr = max(p[0] for p in upper)
    ybot = max(p[1] for p in headp) + (90 + 220 * neck) * sc
    upper = sorted(upper, key=lambda p: p[0])
    d.polygon(P_(*([(xl - 14 * sc, ybot)] + upper + [(xr + 14 * sc, ybot), (xr - 20 * sc, ybot - 30 * sc), (xl + 20 * sc, ybot - 40 * sc)]), s=s), fill=255)
    for k_ in range(9):                                                # ragged ends
        x = xl + (xr - xl) * k_ / 8
        d.polygon(P_((x - 12 * sc, ybot - 45 * sc), (x + 12 * sc, ybot - 45 * sc), (x + (k_ % 3 - 1) * 8, ybot + (30 + 20 * (k_ % 2)) * sc), s=s), fill=255)
    if not child:
        bx, by_ = Rh((hcx, hcy - hl * 0.6))[0]
        d.ellipse([(bx - 40 * sc) * s, (by_ - 40 * sc) * s, (bx + 40 * sc) * s, (by_ + 36 * sc) * s], fill=255)  # the bun
    for sg in (-1, 1):                                                 # arms + long fingers
        sx, sy = cx + sg * 130 * sc, sh_y + 30
        if reach > 0 and sg == 1:
            hx2, hy2 = sx + 380 * reach * sc, sy - 120 * reach * sc
        else:
            hx2, hy2 = sx + sg * 60 * sc, base - 160 * sc
        d.line([(sx * s, sy * s), (hx2 * s, hy2 * s)], fill=255, width=int(40 * sc * s))
        fl = (60 + 110 * max(neck, reach)) * sc
        a0 = math.atan2(hy2 - sy, hx2 - sx)
        for f in range(5):
            a = a0 + (f - 2) * 0.18
            d.line([(hx2 * s, hy2 * s), ((hx2 + math.cos(a) * fl) * s, (hy2 + math.sin(a) * fl) * s)], fill=255, width=int(12 * sc * s))
    eyes = Rh((hcx - hw * 0.42, hcy + hl * 0.02), (hcx + hw * 0.42, hcy + hl * 0.02))
    eyes = [(x / 1.0, y / 1.0) for x, y in eyes]
    return m.resize((w, h), Image.LANCZOS), (eyes if turn >= 0.5 else eyes[1:])


# ============================================================ environment helpers
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


def khene(scale=1.0):
    """The khene: a Lao mouth organ, two rows of long bamboo pipes through a wooden wind chest."""
    w, h = 160, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def pipes(d, s):
        for k in range(7):
            x = 30 + k * 16
            ln = 700 - abs(k - 3) * 70
            d.rounded_rectangle([x * s, (h - 20 - ln) * s, (x + 12) * s, (h - 20) * s], int(5 * s), fill=255)

    def chest(d, s):
        d.ellipse([28 * s, 470 * s, 140 * s, 560 * s], fill=255)
        d.polygon(P_((76, 550), (92, 550), (88, 640), (80, 640), s=s), fill=255)
    im.alpha_composite(shade(pipes, (w, h), (150, 110, 60), 6))
    im.alpha_composite(shade(chest, (w, h), (60, 30, 20), 14))
    d = ImageDraw.Draw(im)
    for y in (180, 300, 600):
        d.line([(28, y), (140, y)], fill=(40, 20, 14, 255), width=5)
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


def tip_khao(scale=1.0):
    """Sticky-rice basket: a woven cylinder with a conical lid on a short foot, a carrying string."""
    w, h = 220, 300
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def body(d, s):
        d.polygon(P_((50, 120), (170, 120), (160, 250), (60, 250), s=s), fill=255)
        d.polygon(P_((80, 250), (140, 250), (150, 290), (70, 290), s=s), fill=255)

    def lid(d, s):
        d.polygon(P_((40, 128), (110, 40), (180, 128), s=s), fill=255)
    im.alpha_composite(shade(body, (w, h), (170, 120, 60), 24))
    im.alpha_composite(shade(lid, (w, h), (150, 104, 52), 18))
    d = ImageDraw.Draw(im)
    for k in range(10):
        y = 130 + k * 12
        d.line([(54 + k, y), (166 - k, y)], fill=(110, 70, 34, 255), width=2)
    d.arc([60, 20, 160, 220], 200, 340, fill=(60, 30, 20, 255), width=3)
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


def oil_lamp(scale=1.0):
    """A small clay oil lamp on a wooden block."""
    w, h = 160, 160
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def body(d, s):
        d.ellipse([30 * s, 70 * s, 130 * s, 120 * s], fill=255)
        d.polygon(P_((100, 86), (150, 70), (146, 84), (110, 104), s=s), fill=255)
        d.rectangle([20 * s, 118 * s, 140 * s, 150 * s], fill=255)
    im.alpha_composite(shade(body, (w, h), (120, 60, 36), 12))
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


# ============================================================ Grandma's room (inside the stilt house)
class Room:
    """Looking at the back wall of Grandma's room: woven bamboo wall, a plank door on the left, a wooden shutter on the
    right (open = the red moon and a palm), a khene hanging on the wall, a low rattan table with a sticky-rice basket,
    a clay oil lamp on the floor, a red mosquito net on the right. All lit by the flickering lamp.
    frame(t, cam, lamp, shadow=(mask, x, y, k), shutter, net, door_shake, dawn, extras_back, extras_front)."""
    LAMP = (300, 1470)

    def __init__(self):
        w, h = W + 200, H
        self.w = w
        alb = np.zeros((h, w, 3), np.float32)
        wv = weave(w, h, 22, 3)
        wall = np.array([118, 64, 44], np.float32)
        alb[:] = wall * wv[..., None]
        # posts + beams
        for x in (60, 640, w - 60):
            alb[:1420, x - 26:x + 26] = np.array([70, 36, 26], np.float32)
        alb[:150] = np.array([34, 16, 12], np.float32)
        alb[150:186] = np.array([70, 36, 26], np.float32)
        # floor planks (perspective)
        P = Persp(540 + 100, 880, 900)
        fy = 1420
        alb[fy:] = np.array([82, 44, 30], np.float32)
        yy, xx = np.mgrid[fy:h, 0:w].astype(np.float32)
        for k in range(-14, 15):
            xb = P.vx + k * 130 * (yy - P.vy) / (fy - P.vy)
            alb[fy:][np.abs(xx - xb) < 2.0 + (yy - fy) / 300] *= 0.55
        alb[fy - 8:fy + 4] = np.array([50, 26, 18], np.float32)
        self.alb = alb
        self.lm = light_map(w, h, self.LAMP[0] + 100, self.LAMP[1] - 160, 900, 0.0)[..., None] * np.array([1.25, 0.78, 0.5], np.float32)
        self.amb = np.array([0.16, 0.05, 0.06], np.float32)
        # moonlight patch from the open shutter onto the floor
        self.moonm = np.zeros((h, w), np.float32)
        poly = Image.new("L", (w, h), 0); ImageDraw.Draw(poly).polygon([(880, 1430), (1110, 1430), (1250, 1900), (700, 1900)], fill=255)
        self.moonm = (np.asarray(poly.filter(ImageFilter.GaussianBlur(30)), np.float32) / 255)[..., None] * np.array([1.0, 0.28, 0.22], np.float32)
        # the door (left) + frame
        dl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(dl)
        self.door_box = (130, 620, 420, 1420)
        x0, y0, x1, y1 = self.door_box
        d.rectangle([x0 - 26, y0 - 26, x1 + 26, y1], fill=(54, 28, 20, 255))
        door = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0)); dd = ImageDraw.Draw(door)
        for k in range(0, x1 - x0, 48):
            dd.rectangle([k + 3, 0, k + 44, y1 - y0], fill=(92, 50, 34, 255))
        for y in (90, (y1 - y0) // 2, y1 - y0 - 90):
            dd.rectangle([0, y - 14, x1 - x0, y + 14], fill=(74, 40, 28, 255))
        dd.rectangle([x1 - x0 - 60, (y1 - y0) // 2 - 50, x1 - x0 - 44, (y1 - y0) // 2 + 50], fill=(40, 22, 16, 255))   # bolt
        self.door = door
        self.door_gaps = [x0 + k + 1 for k in range(0, x1 - x0, 48)][1:]
        self.frame_l = dl
        # the shutter (right)
        self.win_box = (800, 470, 1100, 840)
        # khene on the wall
        self.khene = khene(0.8)
        # low rattan table with the sticky-rice basket
        tl = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        def table(d, s):
            d.ellipse([440 * s, 1440 * s, 760 * s, 1500 * s], fill=255)
            d.polygon(P_((470, 1470), (730, 1470), (700, 1590), (500, 1590), s=s), fill=255)
            d.ellipse([480 * s, 1560 * s, 720 * s, 1610 * s], fill=255)
        tl.alpha_composite(shade(table, (w, h), (120, 70, 40), 20))
        td = ImageDraw.Draw(tl)
        for k in range(6):
            td.line([(486 + k * 6, 1500 + k * 16), (714 - k * 6, 1500 + k * 16)], fill=(80, 44, 26, 255), width=3)
        tk = tip_khao(0.85)
        tl.alpha_composite(tk, (600 - tk.width // 2 + 20, 1468 - tk.height))
        self.table = tl
        self.lamp_img = oil_lamp(0.9)
        # mosquito net (frame, curtain shapes)
        self.net_box = (720, 900, 1170, 1560)

    def net_layer(self, empty=False, lift=0.0, t=0.0, tou_sleep=True):
        x0, y0, x1, y1 = self.net_box
        w, h = x1 - x0 + 40, y1 - y0 + 40
        lay = Image.new("RGBA", (self.w, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.polygon([(x0 + 10, y1 - 40), (x1 + 30, y1 - 40), (x1, y1 + 30), (x0 - 20, y1 + 30)], fill=(60, 30, 26, 255))    # sleeping mat
        d.ellipse([x0 + 40, y1 - 50, x0 + 150, y1 - 10], fill=(150, 120, 100, 255))                                       # pillow
        if not empty and tou_sleep:
            tb, ax, ay = tou("sleep", 0.9)
            lay.alpha_composite(tb, (int(x0 + 60), int(y1 - tb.height + 20)))
        net = Image.new("RGBA", (self.w, H), (0, 0, 0, 0)); nd = ImageDraw.Draw(net)
        sway = 6 * math.sin(t * 1.3)
        lift_px = 360 * lift
        nd.polygon([(x0, y0), (x1, y0), (x1 + 20 + sway, y1), (x0 - 20 + sway, y1 - lift_px * 0.2)], fill=(200, 60, 60, 70))
        if lift > 0:
            nd.polygon([(x0 - 20 + sway, y1 - lift_px), (x0 + 200, y1 - lift_px * 0.8), (x0 + 200, y1), (x0 - 20, y1)], fill=(0, 0, 0, 0))
        for k in range(9):
            x = x0 + (x1 - x0) * k / 8
            nd.line([(x, y0), (x + sway + (k - 4) * 4, y1 - (lift_px if k < 3 else 0))], fill=(240, 120, 110, 60), width=3)
        nd.line([(x0, y0), (x1, y0)], fill=(240, 140, 120, 140), width=4)
        for x in (x0, x1):
            nd.line([(x, 150), (x, y0)], fill=(200, 180, 160, 120), width=2)
        lay.alpha_composite(net)
        return lay

    def frame(self, t, cam=0.0, lamp=1.0, shadow=None, shutter=0.0, net=None, door_shake=0.0, door_light=0.0,
              door_fig=0.0, dawn=0.0, back=None, front=None, khene_on=True):
        flick = lamp * (0.86 + 0.08 * math.sin(t * 13) + 0.06 * math.sin(t * 31 + 1))
        lm = self.lm
        if shadow is not None:
            m, sx, sy, k = shadow                                        # shadow mask on the wall: blocks the lamp light
            sh = np.zeros(lm.shape[:2], np.float32)
            mm = np.asarray(m.filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
            x0, y0 = int(sx - m.width / 2 + 100), int(sy - m.height)
            xa, ya = max(0, x0), max(0, y0); xb, yb = min(self.w, x0 + m.width), min(1420, y0 + m.height)
            if xb > xa and yb > ya:
                sh[ya:yb, xa:xb] = mm[ya - y0:yb - y0, xa - x0:xb - x0] * k
            lm = lm * (1 - 0.92 * sh[..., None])
        light = self.amb + flick * lm + dawn * np.array([0.55, 0.30, 0.26], np.float32)
        if shadow is not None:
            light = light * (1 - 0.6 * sh[..., None])
        a = self.alb * light
        if shutter > 0:
            a += self.alb * self.moonm * 0.8 * shutter
        img = to_img(a)
        # khene
        if khene_on:
            img.alpha_composite(tint(self.khene, (0.5 + 0.5 * flick, 0.45 + 0.4 * flick, 0.4 + 0.35 * flick)), (520 + 100, 330))
        # door
        x0, y0, x1, y1 = self.door_box
        img.alpha_composite(self.frame_l)
        dimg = tint(self.door, (0.45 + 0.6 * flick, 0.4 + 0.4 * flick, 0.4 + 0.3 * flick))
        dx = int(door_shake * 6 * math.sin(t * 80))
        img.alpha_composite(dimg, (x0 + 100 + dx, y0))
        if door_light > 0:                                                # red moonlight through the door gaps, cut by a figure
            dl = Image.new("RGBA", (self.w, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dl)
            for gx in self.door_gaps:
                for yy in range(y0, y1, 6):
                    fig = door_fig > 0 and abs(yy - (y0 + 330)) < 360 - 0 and abs(gx - (x0 + x1) / 2) < 110 * door_fig
                    head = door_fig > 0 and abs(yy - (y0 + 30)) < 70 and abs(gx - (x0 + x1) / 2) < 60 * door_fig
                    if fig or head:
                        continue
                    dd.rectangle([gx + 100 + dx, yy, gx + 103 + dx, yy + 6], fill=(255, 60, 40, int(220 * door_light)))
            img.alpha_composite(dl)
            img = glow_on(img, gsp(160, (255, 50, 36)), (x0 + x1) / 2 + 100, y1 - 200, 0.25 * door_light)
        # shutter
        wx0, wy0, wx1, wy1 = self.win_box
        dw = ImageDraw.Draw(img)
        dw.rectangle([wx0 + 100 - 20, wy0 - 20, wx1 + 100 + 20, wy1 + 20], fill=(54, 28, 20, 255))
        if shutter > 0:
            sky = moon_sky((wx1 - 70, wy0 + 90), 60, w=wx1 - wx0, h=wy1 - wy0, top=(20, 2, 6), mid=(80, 10, 16), bot=(150, 30, 28)) if not hasattr(self, "_wsky") else self._wsky
            self._wsky = sky
            sk = to_img(sky); sd = ImageDraw.Draw(sk)
            for k in range(6):                                                    # a palm silhouette
                a_ = -2.6 + k * 0.4
                sd.line([(70, 200), (70 + 160 * math.cos(a_), 200 + 90 * math.sin(a_) + 40)], fill=(8, 2, 3, 255), width=10)
            sd.line([(70, 200), (90, wy1 - wy0)], fill=(8, 2, 3, 255), width=12)
            img.alpha_composite(sk, (wx0 + 100, wy0))
            pw = int((wx1 - wx0) * (1 - shutter))
            if pw > 4:
                dw.rectangle([wx0 + 100, wy0, wx0 + 100 + pw, wy1], fill=(90, 50, 34, 255))
        else:
            dw.rectangle([wx0 + 100, wy0, wx1 + 100, wy1], fill=(90, 50, 34, 255))
            for k in range(1, 6):
                dw.line([(wx0 + 100, wy0 + k * (wy1 - wy0) / 6), (wx1 + 100, wy0 + k * (wy1 - wy0) / 6)], fill=(60, 30, 22, 255), width=4)
        if back:
            for fn in back:
                img = fn(img, t) or img
        # table + basket, lamp
        img.alpha_composite(tint(self.table, (0.4 + 0.65 * flick, 0.35 + 0.5 * flick, 0.32 + 0.4 * flick)))
        lx, ly = self.LAMP
        img.alpha_composite(self.lamp_img, (lx + 100 - self.lamp_img.width // 2, ly - self.lamp_img.height + 30))
        if net is not None:
            img.alpha_composite(self.net_layer(**net, t=t))
        if front:
            for fn in front:
                img = fn(img, t) or img
        a = to_arr(img)
        fl_k = flick * (1 if lamp > 0.05 else 0)
        add_glow(a, gsp(220, (255, 120, 50)), lx + 100, ly - 40, 0.55 * fl_k)
        add_glow(a, gsp(26, (255, 230, 170)), lx + 100 + 26 + 2 * math.sin(t * 17), ly - 52, 1.0 * fl_k)
        img = to_img(a)
        bokeh_particles(img, 10, 71, t, color=(255, 150, 90), size=(2, 5), blur=(0, 2), area=(0, 300, self.w, 1600), drift=(4, -6))
        x = int(100 + cam)
        return img.crop((x, 0, x + W, H))


_RM = None


def room():
    global _RM
    if _RM is None:
        _RM = Room()
    return _RM


# ============================================================ the village at night (outside)
def temple_sil(scale=1.0, lit=1.0):
    """A Lao temple (sim) far away: three stacked sweeping roofs with upturned naga-tail eaves and a chofa finial at each
    end, a white-gold stupa behind, rows of small lanterns. Mostly a dark silhouette with red-gold edge light."""
    w, h = 620, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def stupa(d, s):
        d.polygon(P_((440, 470), (560, 470), (540, 330), (520, 260), (506, 120), (500, 40), (494, 120), (480, 260), (460, 330), s=s), fill=255)

    def sim(d, s):
        d.rectangle([110 * s, 330 * s, 450 * s, 470 * s], fill=255)
        for k, (yb, half, hh) in enumerate(((340, 230, 80), (270, 180, 74), (205, 130, 66))):
            cx = 280
            d.polygon(P_((cx - half - 30, yb), (cx - half, yb - 12), (cx, yb - hh), (cx + half, yb - 12), (cx + half + 30, yb),
                         (cx + half + 44, yb - 26), (cx + half + 30, yb + 6), (cx - half - 30, yb + 6), (cx - half - 44, yb - 26), s=s), fill=255)
        d.polygon(P_((276, 140), (284, 140), (280, 110), s=s), fill=255)
        d.rectangle([0, 466 * s, w * s, h * s], fill=255)
    im.alpha_composite(shade(stupa, (w, h), (130, 80, 50), 20, rim=(255, 150, 80)))
    im.alpha_composite(shade(sim, (w, h), (40, 12, 14), 14, rim=(255, 120, 70)))
    d = ImageDraw.Draw(im)
    for k in range(9):
        x = 130 + k * 38
        d.ellipse([x - 5, 390, x + 5, 402], fill=(255, 190, 90, int(255 * lit)))
    d.rectangle([255, 380, 305, 470], fill=(255, 150, 70, int(200 * lit)))                     # the open door, lit
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


def sugar_palm(d, x, by, hgt, s=1, rnd=None):
    rnd = rnd or np.random.default_rng(1)
    top = by - hgt
    d.line([(x * s, by * s), ((x + rnd.uniform(-10, 10)) * s, top * s)], fill=255, width=int(max(3, hgt / 60) * s))
    for k in range(22):
        a = -math.pi + k * math.pi / 21 + rnd.uniform(-0.05, 0.05)
        ln = hgt * 0.14
        d.line([(x * s, top * s), ((x + math.cos(a) * ln) * s, (top + math.sin(a) * ln * 0.9) * s)], fill=255, width=int(max(2, hgt / 120) * s))
    d.ellipse([(x - hgt * 0.05) * s, (top - hgt * 0.04) * s, (x + hgt * 0.05) * s, (top + hgt * 0.05) * s], fill=255)


class Village:
    """Grandma's stilt house (woven walls, steep leaf roof, a porch and a ladder, a loom and firewood underneath), the rice
    barn on posts with slatted walls, paddies with the moon in the water, sugar palms, and the temple far away with its
    lanterns. Parallax layers. Anchors: self.porch (Noy at the top of the ladder), self.ladder, self.barn_door."""
    def __init__(self):
        r = np.random.default_rng(31)
        self.sky = to_img(moon_sky((800, 380), 140, top=(4, 1, 2), mid=(50, 6, 12), bot=(128, 24, 24), ym=0.52))
        # far: hills + temple + lanterns
        far = Image.new("RGBA", (W + 300, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(far)
        pts = [(0, 1080)] + [(x, 980 - 70 * math.sin(x / 240 + 0.5) - 40 * math.sin(x / 90)) for x in range(0, W + 360, 40)] + [(W + 300, 1080)]
        fd.polygon(pts, fill=(36, 7, 11, 255))
        tp = temple_sil(0.44)
        far.alpha_composite(tp, (610, 1040 - tp.height))
        self.temple_xy = (610 + int(0.44 * 280), 1040 - tp.height + int(0.44 * 430))
        fm = Image.new("L", (W + 300, H), 0); fmd = ImageDraw.Draw(fm)
        for k in range(10):
            sugar_palm(fmd, r.choice([r.uniform(200, 600), r.uniform(900, W + 300)]), 1060, r.uniform(260, 420), 1, r)
        fl = Image.new("RGBA", fm.size, (24, 5, 8, 0)); fl.putalpha(fm)
        far.alpha_composite(fl)
        self.far = far.filter(ImageFilter.GaussianBlur(1.2))
        # mid: paddies with moon reflections
        mid = Image.new("RGBA", (W + 300, H), (0, 0, 0, 0)); md = ImageDraw.Draw(mid)
        md.rectangle([0, 1050, W + 300, H], fill=(30, 8, 9, 255))
        for k in range(9):
            y = 1060 + k * k * 9
            md.rectangle([0, y, W + 300, y + 6 + k * 2], fill=(60, 12, 14, 255))
            md.line([(0, y), (W + 300, y)], fill=(170, 46, 34, 255), width=2)
        md.ellipse([840 + 150 - 90, 1100, 840 + 150 + 90, 1124], fill=(220, 70, 50, 200))         # the moon in the water
        for _ in range(240):
            x = r.uniform(0, W + 300); y = r.uniform(1070, 1300)
            md.line([(x, y), (x + r.uniform(-4, 4), y - r.uniform(8, 22))], fill=(20, 6, 6, 255), width=2)
        self.mid = mid
        # the house (left) and the barn (right) - one layer
        hl = Image.new("RGBA", (W + 300, H), (0, 0, 0, 0))
        HX0, HX1, FL = 60, 620, 860                     # house walls x, floor y
        self.floor_y = FL

        def posts(d, s):
            for x in (HX0 + 20, HX0 + 200, HX0 + 380, HX1 - 20):
                d.rectangle([(x - 16) * s, FL * s, (x + 16) * s, 1480 * s], fill=255)
            d.rectangle([(HX0 - 20) * s, (FL - 10) * s, (HX1 + 80) * s, (FL + 26) * s], fill=255)       # floor beam + porch

        def walls(d, s):
            d.rectangle([HX0 * s, 560 * s, HX1 * s, FL * s], fill=255)

        def roof(d, s):
            d.polygon(P_((HX0 - 90, 600), (HX1 + 110, 600), (HX1 - 40, 260), ((HX0 + HX1) / 2 + 40, 120), (HX0 + 60, 260), s=s), fill=255)

        hl.alpha_composite(shade(posts, (W + 300, H), (70, 36, 26), 14))
        wl = shade(walls, (W + 300, H), (120, 66, 44), 30)
        wv = weave(W + 300, H, 16, 5)
        wa = np.asarray(wl, np.float32).copy(); wa[..., :3] *= wv[..., None]
        hl.alpha_composite(Image.fromarray(np.clip(wa, 0, 255).astype(np.uint8), "RGBA"))
        hd = ImageDraw.Draw(hl)
        hd.rectangle([HX0 + 300, 640, HX0 + 420, 800], fill=(255, 150, 70, 255))                    # lit window
        hd.rectangle([HX0 + 300, 640, HX0 + 420, 800], outline=(60, 30, 20, 255), width=10)
        hd.line([(HX0 + 360, 640), (HX0 + 360, 800)], fill=(60, 30, 20, 255), width=6)
        self.window_xy = (HX0 + 360, 720)
        hd.rectangle([HX1 - 150, 600, HX1 - 40, FL], fill=(30, 12, 10, 255))                       # doorway
        rf = shade(roof, (W + 300, H), (60, 22, 20), 40, rim=(255, 80, 50))
        ra = np.asarray(rf, np.float32).copy()
        yy = np.arange(H)[:, None]
        ra[..., :3] *= (0.85 + 0.15 * np.sin(yy / 7.0))[..., None]                                 # thatch lines
        hl.alpha_composite(Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8), "RGBA"))
        # porch rail + ladder
        hd = ImageDraw.Draw(hl)
        hd.line([(HX1, FL - 90), (HX1 + 80, FL - 90)], fill=(70, 36, 26, 255), width=10)
        hd.line([(HX1 + 80, FL - 90), (HX1 + 80, FL)], fill=(70, 36, 26, 255), width=10)
        self.porch = (HX1 + 10, FL)
        lx0, lx1 = HX1 + 40, HX1 + 140
        for x in (lx0, lx1):
            hd.line([(x, FL), (x + 120, 1480)], fill=(90, 50, 32, 255), width=14)
        for k in range(1, 8):
            u = k / 8
            hd.line([(lx0 + 120 * u, FL + (1480 - FL) * u), (lx1 + 120 * u, FL + (1480 - FL) * u)], fill=(110, 64, 40, 255), width=10)
        self.ladder = ((lx0 + lx1) / 2, FL, (lx0 + lx1) / 2 + 120, 1480)
        # under the house: loom frame + firewood stack + a hanging fish trap
        hd.rectangle([HX0 + 40, 1260, HX0 + 260, 1460], outline=(40, 18, 14, 255), width=10)
        for k in range(8):
            hd.line([(HX0 + 60 + k * 26, 1270), (HX0 + 60 + k * 26, 1450)], fill=(160, 120, 90, 160), width=2)
        for k in range(5):
            hd.rounded_rectangle([HX0 + 300, 1360 + k * 22, HX0 + 470, 1380 + k * 22], 8, fill=(80, 44, 30, 255))
        hd.ellipse([HX0 + 470, 960, HX0 + 540, 1080], outline=(110, 70, 40, 255), width=6)
        self.house = hl
        self.under_dark = (HX0, FL + 26, HX1, 1480)
        # the rice barn (right)
        bl = Image.new("RGBA", (W + 300, H), (0, 0, 0, 0))
        BX0, BX1, BF = 860, 1180, 1080

        def bposts(d, s):
            for x in (BX0 + 20, BX1 - 20):
                d.rectangle([(x - 14) * s, BF * s, (x + 14) * s, 1460 * s], fill=255)
                d.ellipse([(x - 30) * s, (BF + 40) * s, (x + 30) * s, (BF + 70) * s], fill=255)        # rat guards

        def bwalls(d, s):
            d.rectangle([BX0 * s, 840 * s, BX1 * s, BF * s], fill=255)

        def broof(d, s):
            d.polygon(P_((BX0 - 60, 860), (BX1 + 60, 860), ((BX0 + BX1) / 2, 650), s=s), fill=255)
        bl.alpha_composite(shade(bposts, (W + 300, H), (70, 36, 26), 12))
        bl.alpha_composite(shade(bwalls, (W + 300, H), (104, 60, 40), 24))
        bd = ImageDraw.Draw(bl)
        for x in range(BX0 + 30, BX1, 34):
            bd.line([(x, 846), (x, BF - 4)], fill=(20, 6, 6, 255), width=5)                         # slat gaps
        bd.rectangle([BX0 + 120, 900, BX0 + 200, BF], fill=(16, 5, 6, 255))                         # small door
        bl.alpha_composite(shade(broof, (W + 300, H), (60, 22, 20), 30, rim=(255, 80, 50)))
        for k in range(5):
            u = (k + 1) / 6
            bd.line([(BX0 + 140, BF + (1460 - BF) * u), (BX0 + 190, BF + (1460 - BF) * u)], fill=(110, 64, 40, 255), width=8)
        bd.line([(BX0 + 136, BF), (BX0 + 136, 1460)], fill=(90, 50, 32, 255), width=10)
        bd.line([(BX0 + 194, BF), (BX0 + 194, 1460)], fill=(90, 50, 32, 255), width=10)
        self.barn = bl
        self.barn_door = (BX0 + 160, 1460)
        # ground
        g = Image.new("RGBA", (W + 300, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.rectangle([0, 1420, W + 300, H], fill=(40, 14, 12, 255))
        for _ in range(500):
            x = r.uniform(0, W + 300); y = r.uniform(1430, H)
            gd.ellipse([x - 6, y - 2, x + 6, y + 2], fill=(30, 10, 9, 255))
        self.ground = g
        # foreground: blurred banana leaves at the edges
        fg = Image.new("L", (W + 300, H), 0); fdd = ImageDraw.Draw(fg)
        for i in range(5):
            x = r.choice([r.uniform(-60, 160), r.uniform(W + 120, W + 360)]); y = r.uniform(1500, 2000)
            for k in range(3):
                a = -math.pi / 2 + r.uniform(-0.9, 0.9)
                ln = r.uniform(360, 620)
                fdd.polygon([(x, y), (x + math.cos(a - 0.2) * ln * 0.6, y + math.sin(a - 0.2) * ln * 0.6),
                             (x + math.cos(a) * ln, y + math.sin(a) * ln), (x + math.cos(a + 0.2) * ln * 0.6, y + math.sin(a + 0.2) * ln * 0.6)], fill=255)
        fgl = Image.new("RGBA", fg.size, (8, 2, 3, 0)); fgl.putalpha(fg)
        self.fg = fgl.filter(ImageFilter.GaussianBlur(10))

    def frame(self, t, cam=0.0, extras=None, window=1.0, lanterns=1.0, fogk=0.35, mid_extras=None):
        img = self.sky.copy()
        o = lambda par: int(-150 - cam * par)
        img.alpha_composite(self.far, (o(0.15), 0))
        a = to_arr(img)
        tx, ty = self.temple_xy
        add_glow(a, gsp(90, (255, 150, 70)), tx + o(0.15), ty - 20, 0.5 * lanterns * (0.9 + 0.1 * math.sin(t * 3)))
        img = to_img(a)
        fog(img, t, fogk, 950, 1200, speed=10, col=(150, 40, 36))
        img.alpha_composite(self.mid, (o(0.35), 0))
        for fn in (mid_extras or []):
            img = fn(img, t, o(0.35) + 150) or img
        img.alpha_composite(self.ground, (o(0.7), 0))
        img.alpha_composite(self.barn, (o(0.7), 0))
        img.alpha_composite(self.house, (o(0.7), 0))
        a = to_arr(img)
        wx, wy = self.window_xy
        add_glow(a, gsp(150, (255, 130, 60)), wx + o(0.7), wy, 0.5 * window * (0.9 + 0.1 * math.sin(t * 11)))
        img = to_img(a)
        for fn in (extras or []):
            img = fn(img, t, o(0.7) + 150) or img
        fog(img, t, fogk * 0.6, 1350, 1700, speed=16, col=(130, 34, 30), off=300)
        img.alpha_composite(self.fg, (o(1.6), 0))
        bokeh_particles(img, 14, 81, t, color=(255, 140, 100), size=(2, 7), blur=(0, 3), area=(0, 300, W, 1700), drift=(6, -5))
        return img


_VL = None


def village():
    global _VL
    if _VL is None:
        _VL = Village()
    return _VL


# ============================================================ inside the rice barn
class Barn:
    """Inside the rice barn: a back wall of vertical planks with gaps that let in red moonlight (stripes across the floor),
    thatch above with a hole showing the red sky, piles of rice sacks, woven baskets, a wooden rice mortar.
    frame(t, cam, occl=fn(L-mask) for things outside blocking the gaps, extras, dawn)."""
    def __init__(self):
        w, h = W + 200, H
        self.w = w
        r = np.random.default_rng(41)
        base = Image.new("RGBA", (w, h), (14, 5, 6, 255))
        d = ImageDraw.Draw(base)
        self.gaps = []
        x = 20
        while x < w:
            pw = int(r.uniform(70, 96))
            col = tuple(int(c * r.uniform(0.8, 1.1)) for c in (66, 32, 24))
            d.rectangle([x, 240, x + pw, 1460], fill=col + (255,))
            for k in range(3):
                yk = r.uniform(300, 1400)
                d.line([(x + 10, yk), (x + pw - 10, yk + r.uniform(-6, 6))], fill=(46, 22, 16, 255), width=2)
            self.gaps.append(x + pw + 2)
            x += pw + int(r.uniform(6, 12))
        d.rectangle([0, 700, w, 740], fill=(50, 24, 18, 255))                                    # cross beam
        # floor
        d.rectangle([0, 1460, w, h], fill=(48, 22, 16, 255))
        for k in range(12):
            y = 1470 + k * k * 4
            d.line([(0, y), (w, y)], fill=(34, 14, 10, 255), width=2)
        # thatch roof with the hole
        rm = Image.new("L", (w, h), 0); rd = ImageDraw.Draw(rm)
        rd.polygon([(0, 0), (w, 0), (w, 300), (0, 300)], fill=255)
        self.hole = (640, 40, 900, 210)
        rd.ellipse(self.hole, fill=0)
        sky = to_img(moon_sky((800, 110), 70, w=w, h=320, top=(30, 3, 8), mid=(110, 14, 20), bot=(150, 30, 28)))
        base.alpha_composite(sky.resize((w, 320)), (0, 0))
        roof = inflate21(rm, (54, 22, 16), radius=20, rim=(255, 80, 50), rim_strength=0.6)
        ra = np.asarray(roof, np.float32).copy()
        yy, xx = np.mgrid[0:h, 0:w]
        ra[..., :3] *= (0.75 + 0.25 * np.sin(xx / 5.0 + np.sin(yy / 40.0) * 3))[..., None]
        base.alpha_composite(Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8), "RGBA"))
        d = ImageDraw.Draw(base)
        for k in range(30):                                                                     # straw ends round the hole
            a = r.uniform(0, 2 * math.pi)
            cx, cy = 770, 125
            d.line([(cx + 140 * math.cos(a), cy + 95 * math.sin(a)), (cx + 110 * math.cos(a), cy + 70 * math.sin(a))], fill=(90, 50, 30, 255), width=4)
        self.base = base
        # light from the gaps: a mask of thin vertical slits + floor stripes
        gm = Image.new("L", (w, h), 0); gd = ImageDraw.Draw(gm)
        for gx in self.gaps:
            gd.rectangle([gx - 4, 240, gx + 3, 1460], fill=255)
        self.gapmask = np.asarray(gm, np.float32) / 255
        fm = Image.new("L", (w, h), 0); fdd = ImageDraw.Draw(fm)
        for gx in self.gaps:
            fdd.polygon([(gx - 4, 1460), (gx + 4, 1460), (gx + 4 + (gx - 540) * 0.5 + 60, h), (gx - 30 + (gx - 540) * 0.5, h)], fill=120)
        self.floormask = np.asarray(fm.filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
        # sacks + baskets + mortar (props layer)
        pl = Image.new("RGBA", (w, h), (0, 0, 0, 0))

        def sacks(d, s):
            for (x, y, rw, rh) in ((40, 1300, 170, 130), (190, 1340, 160, 120), (90, 1180, 150, 120), (880, 1310, 190, 140),
                                   (1060, 1330, 170, 130), (960, 1190, 170, 130), (1150, 1200, 140, 120)):
                d.rounded_rectangle([x * s, y * s, (x + rw) * s, (y + rh) * s], int(50 * s), fill=255)
        pl.alpha_composite(shade(sacks, (w, h), (150, 118, 80), 40, rim=(255, 90, 60)))
        pd = ImageDraw.Draw(pl)
        for (x, y) in ((120, 1240), (270, 1400), (970, 1380), (1040, 1250)):
            pd.line([(x - 30, y - 4), (x + 30, y + 4)], fill=(90, 60, 40, 255), width=4)                  # sack stitching
        self.sack_top = (1000, 1190)

        def baskets(d, s):
            d.polygon(P_((380, 1330), (520, 1330), (500, 1470), (400, 1470), s=s), fill=255)
            d.ellipse([370 * s, 1310 * s, 530 * s, 1350 * s], fill=255)

        def mortar(d, s):
            d.polygon(P_((640, 1350), (790, 1350), (770, 1480), (660, 1480), s=s), fill=255)
            d.line([(720 * s, 1350 * s), (690 * s, 1010 * s)], fill=255, width=int(26 * s))
        pl.alpha_composite(shade(baskets, (w, h), (140, 96, 50), 22))
        pl.alpha_composite(shade(mortar, (w, h), (80, 44, 28), 22))
        pd = ImageDraw.Draw(pl)
        for k in range(6):
            pd.line([(384 + k * 3, 1350 + k * 20), (516 - k * 3, 1350 + k * 20)], fill=(90, 56, 28, 255), width=3)
        self.props = pl

    def frame(self, t, cam=0.0, occl=None, extras=None, back=None, light=1.0, dawn=0.0, hole_extra=None):
        img = self.base.copy()
        if hole_extra:
            img = hole_extra(img, t) or img
        gl = self.gapmask.copy(); fl = self.floormask.copy()
        if occl is not None:
            om = occl(t)                                              # L-mask (W+200 wide): what blocks the moonlight outside
            if om is not None:
                o = np.asarray(om, np.float32) / 255
                gl *= (1 - o)
                # the floor stripes of blocked gaps go dark too (sample the occluder at a mid height per column)
                col = 1 - o[600:1300].max(0)
                fl *= col[None, :]
        mcol = np.array([255, 70, 46], np.float32) * (1 - dawn) + np.array([255, 190, 120], np.float32) * dawn
        a = to_arr(img)
        a += gl[..., None] * mcol * 0.9 * light
        img = to_img(a)
        if back:
            for fn in back:
                img = fn(img, t) or img
        a = to_arr(img)
        a += fl[..., None] * mcol * 0.55 * light
        a = a * (0.85 + 0.15 * light)
        img = to_img(a)
        img.alpha_composite(self.props)
        for fn in (extras or []):
            img = fn(img, t) or img
        bokeh_particles(img, 22, 91, t, color=(255, 170, 120), size=(1, 4), blur=(0, 1), area=(0, 200, self.w, 1600), drift=(3, 8))
        x = int(100 + cam)
        return img.crop((x, 0, x + W, H))


_BN = None


def barn():
    global _BN
    if _BN is None:
        _BN = Barn()
    return _BN


# ============================================================ the paddy dike to the temple (side view) + the temple gate
class Dike:
    """Side view across the paddies at the last hour of night: a raised earth dike running left to right, flooded fields
    with the sky in them, rice seedlings, sugar palms, and the temple on the right (big, with lanterns, a drum pavilion).
    A wide panorama (3000 px); cam pans it. dawn 0..1 lifts the horizon from red-black to crimson-gold."""
    def __init__(self):
        PW = 3000
        self.PW = PW
        r = np.random.default_rng(51)
        a = vgrad((8, 2, 4), (70, 10, 16), (190, 50, 38), ym=0.5, h=H, w=PW)
        self.sky_n = a
        self.sky_d = vgrad((24, 5, 12), (130, 28, 34), (255, 150, 90), ym=0.5, h=H, w=PW)
        far = Image.new("RGBA", (PW, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(far)
        pts = [(0, 950)] + [(x, 860 - 90 * math.sin(x / 300) - 40 * math.sin(x / 120 + 1)) for x in range(0, PW + 40, 40)] + [(PW, 950)]
        fd.polygon(pts, fill=(30, 6, 9, 255))
        pm = Image.new("L", (PW, H), 0); pmd = ImageDraw.Draw(pm)
        for k in range(16):
            sugar_palm(pmd, r.uniform(0, PW - 700), 940, r.uniform(320, 520), 1, r)
        pl = Image.new("RGBA", (PW, H), (16, 3, 5, 0)); pl.putalpha(pm)
        far.alpha_composite(pl)
        tp = temple_sil(1.5)
        self.temple_x = 1560
        far.alpha_composite(tp, (self.temple_x, 980 - tp.height))
        self.lantern_y = 980 - tp.height + int(1.5 * 396)
        self.far = far
        mid = Image.new("RGBA", (PW, H), (0, 0, 0, 0)); md = ImageDraw.Draw(mid)
        
        for k in range(10):
            y = 960 + k * k * 6
            md.line([(0, y), (PW, y)], fill=(170, 50, 36, 150), width=2)
        for _ in range(1400):
            x = r.uniform(0, PW); y = r.uniform(960, 1500)
            hh = 8 + (y - 960) / 18
            md.line([(x, y), (x + r.uniform(-3, 3), y - hh)], fill=(16, 5, 5, 255), width=2)
        self.mid = mid
        dk = Image.new("RGBA", (PW, H), (0, 0, 0, 0))

        def dike(d, s):
            d.polygon(P_((0, 1150), (PW, 1150), (PW, 1290), (0, 1290), s=s), fill=255)
        dk.alpha_composite(shade(dike, (PW, H), (110, 48, 34), 30, rim=(255, 110, 70)))
        dd = ImageDraw.Draw(dk)
        for _ in range(600):
            x = r.uniform(0, PW); dd.line([(x, 1152), (x + r.uniform(-6, 6), 1152 - r.uniform(10, 40))], fill=(24, 8, 7, 255), width=3)
        self.dike = dk
        self.dike_y = 1165
        fg = Image.new("L", (PW, H), 0); fgd = ImageDraw.Draw(fg)
        for _ in range(90):
            x = r.uniform(0, PW); hh = r.uniform(160, 420)
            fgd.polygon([(x - 14, H), (x + 14, H), (x + r.uniform(-60, 60), H - hh)], fill=255)
        fgl = Image.new("RGBA", fg.size, (6, 1, 2, 0)); fgl.putalpha(fg)
        self.fg = fgl.filter(ImageFilter.GaussianBlur(8))
        self.water_mask = None

    def frame(self, t, cam=0.0, extras=None, dawn=0.0, drum=0.0):
        x0 = int(cam)
        a = (self.sky_n * (1 - dawn) + self.sky_d * dawn)[:, x0:x0 + W].copy()
        # the water mirrors the sky (darker)
        refl = a[np.clip(2 * 960 - np.arange(960, H), 0, H - 1)]
        a[960:] = refl * 0.7
        img = to_img(a)
        img.alpha_composite(self.far.crop((int(x0 * 0.6), 0, int(x0 * 0.6) + W, H)))
        aa = to_arr(img)
        lx = self.temple_x + 420 - x0 * 0.6
        add_glow(aa, gsp(200, (255, 160, 80)), lx, self.lantern_y - 30, (0.5 + 0.6 * drum) * (0.9 + 0.1 * math.sin(t * 3)))
        img = to_img(aa)
        fog(img, t, 0.35, 850, 1100, speed=10, col=(160, 50, 40))
        img.alpha_composite(self.mid.crop((int(x0 * 0.8), 0, int(x0 * 0.8) + W, H)))
        img.alpha_composite(self.dike.crop((x0, 0, x0 + W, H)))
        for fn in (extras or []):
            img = fn(img, t, -x0) or img
        img.alpha_composite(self.fg.crop((int(x0 * 1.4) % (self.PW - W), 0, int(x0 * 1.4) % (self.PW - W) + W, H)))
        bokeh_particles(img, 14, 61, t, color=(255, 150, 100), size=(2, 6), blur=(0, 2), area=(0, 400, W, 1700), drift=(-30, -6))
        return img


_DK = None


def dike_set():
    global _DK
    if _DK is None:
        _DK = Dike()
    return _DK


def naga_rail(flip=False, scale=1.0):
    """A naga serpent stair rail seen from the front-side: the scaly body sweeping down the stairs, rising at the bottom
    into a raised hood of five heads."""
    w, h = 520, 900
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def body(d, s):
        pts = [(480, 40), (430, 200), (340, 420), (230, 600), (170, 720)]
        d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(70 * s), joint="curve")
        d.line([(170 * s, 720 * s), (140 * s, 560 * s)], fill=255, width=int(80 * s))
        for k in range(5):                                       # the hood of heads
            a = -math.pi / 2 + (k - 2) * 0.38
            hx, hy = 140 + math.cos(a) * 150, 520 + math.sin(a) * 130
            d.line([(140 * s, 560 * s), (hx * s, hy * s)], fill=255, width=int(44 * s))
            d.ellipse([(hx - 34) * s, (hy - 30) * s, (hx + 34) * s, (hy + 30) * s], fill=255)
        d.rectangle([90 * s, 720 * s, 260 * s, 820 * s], fill=255)       # plinth
    im.alpha_composite(shade(body, (w, h), (190, 140, 70), 30, rim=(255, 120, 70)))
    d = ImageDraw.Draw(im)
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.38
        hx, hy = 140 + math.cos(a) * 150, 520 + math.sin(a) * 130
        d.ellipse([hx - 8, hy - 8, hx + 8, hy + 4], fill=(150, 20, 20, 255))
    for k in range(14):                                          # scales along the body
        u = k / 13
        x = 480 - 310 * u; y = 40 + 680 * u
        d.arc([x - 22, y - 12, x + 22, y + 12], 0, 180, fill=(120, 80, 40, 255), width=3)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


class Gate:
    """The temple gate from the front, at first light: a white-and-gold arched gate with a tiered roof, stairs going up
    between two naga rails, lanterns, the drum pavilion glowing beyond, the stupa against a crimson-gold sky."""
    def __init__(self):
        sky = vgrad((10, 2, 6), (100, 20, 28), (255, 130, 70), ym=0.55)
        img = to_img(sky)
        tp = temple_sil(1.2)
        img.alpha_composite(tp, (W // 2 - tp.width // 2 + 160, 760 - tp.height + 120))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        def wall(d, s):
            d.rectangle([0, 900 * s, W * s, 1200 * s], fill=255)

        def arch(d, s):
            d.rectangle([300 * s, 640 * s, 780 * s, 1200 * s], fill=255)
            d.polygon(P_((260, 660), (820, 660), (720, 520), (540, 430), (360, 520), s=s), fill=255)
            d.polygon(P_((340, 520), (740, 520), (640, 400), (540, 340), (440, 400), s=s), fill=255)
            d.polygon(P_((536, 340), (544, 340), (540, 250), s=s), fill=255)
        g.alpha_composite(shade(wall, (W, H), (150, 120, 100), 20, rim=(255, 120, 70)))
        g.alpha_composite(shade(arch, (W, H), (190, 170, 150), 40, rim=(255, 140, 80)))
        gd = ImageDraw.Draw(g)
        gd.rounded_rectangle([400, 760, 680, 1200], 120, fill=(255, 170, 90, 255))              # the opening, glowing
        for y in (660, 520):
            gd.line([(300, y), (780, y)], fill=(210, 160, 70, 255), width=8)
        img.alpha_composite(g)
        # stairs
        sd = ImageDraw.Draw(img)
        for k in range(9):
            y = 1200 + k * 40
            x0 = 380 - k * 22; x1 = 700 + k * 22
            sd.rectangle([x0, y, x1, y + 40], fill=(120 - k * 4, 90 - k * 4, 80 - k * 4, 255))
            sd.line([(x0, y), (x1, y)], fill=(200, 150, 110, 255), width=3)
        sd.rectangle([0, 1560, W, H], fill=(40, 16, 12, 255))
        nl = naga_rail(False, 0.9); nr = naga_rail(True, 0.9)
        img.alpha_composite(nl, (80, 1560 - nl.height + 40))
        img.alpha_composite(nr, (W - 80 - nr.width, 1560 - nr.height + 40))
        self.base = img
        self.door = (540, 1000)

    def frame(self, t, extras=None, drum=0.0):
        a = to_arr(self.base)
        add_glow(a, gsp(300, (255, 170, 90)), self.door[0], self.door[1], 0.6 + 0.5 * drum)
        img = to_img(a)
        fog(img, t, 0.35, 1400, 1800, speed=12, col=(170, 70, 50))
        for fn in (extras or []):
            img = fn(img, t) or img
        bokeh_particles(img, 18, 33, t, color=(255, 200, 130), size=(2, 6), blur=(0, 2), area=(0, 300, W, 1700), drift=(4, -10))
        return img


_GT = None


def gate():
    global _GT
    if _GT is None:
        _GT = Gate()
    return _GT
