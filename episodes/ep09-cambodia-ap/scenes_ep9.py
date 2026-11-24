"""Ep09 Cambodia / the Ap (floating head) - 2.1D survival version.
New world: a stilt-house village near Siem Reap under a blood moon: rice paddies, sugar palms (thnot),
the five towers of Angkor far on the horizon, a laundry line with a white sarong and a red krama,
the dark space under the house (posts, a big clay water jar, a hammock, thorny branches), a lamplit room
with a mosquito net, and a pale morning doorway.
Each make_<id>(D, caps) returns f(t) -> float RGB array (H, W, 3)."""
import os, sys, math
os.environ["STYLE"] = "flat21"
_EP = os.path.dirname(os.path.abspath(__file__)); _TK = os.path.join(_EP, "..", "..", "toolkit")
sys.path.insert(0, _TK)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import W, H, font, text_img, with_alpha, ease, glow_sprite, add_glow, fog_texture, vignette, INTER_SB, INTER_M, LORA
from depth import inflate_shade, dof, god_rays, bokeh_particles
import demo25_myanmar as D5
from scenes_v import series_header, header_layers, pill

HZ = 1010            # horizon of the rice field
GY = 1240            # ground line under the house / near ground
RED = (255, 55, 40)
MOON = (300, 400)
VIG = vignette(0.85)
VIG_H = vignette(1.05)
GR = [np.random.default_rng(i).normal(0, 5, (H, W, 1)).astype(np.float32) for i in range(6)]
FOGT = fog_texture(W + 700, H, 91)


def ss(t, a, b):
    return ease((t - a) / max(1e-3, b - a))


def shade(draw_fn, size, base, radius, **kw):
    return D5.shaded(draw_fn, size, base, radius, **kw)


def to_arr(img):
    return np.asarray(img.convert("RGB")).astype(np.float32)


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def finish(img, t, vig=VIG, push=1.0, cx=W / 2, cy=H * 0.45, shake=0.0, flash=0.0, flash_col=(255, 255, 255)):
    push = max(1.0, push)
    if push != 1.0 or shake:
        sx = shake * math.sin(t * 91) * 14; sy = shake * math.cos(t * 77) * 14
        cw, ch = W / push, H / push
        x0 = min(max(cx - cw / 2 + sx, 0), W - cw); y0 = min(max(cy - ch / 2 + sy, 0), H - ch)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    a = to_arr(img) * vig + GR[int(t * 30) % 6]
    if flash > 0:
        a = a * (1 - flash) + np.array(flash_col, np.float32) * flash
    return a


def fog(img, t, k, y0, y1, speed=18, col=(140, 40, 40), off=0):
    o = int((t * speed + off) % 700)
    f = FOGT[:, o:o + W]
    yy = np.arange(H)[:, None]
    band = np.clip(np.minimum((yy - y0) / 150, (y1 - yy) / 150), 0, 1)
    a = f * band * k
    lay = np.dstack([np.full((H, W), col[0], np.float32), np.full((H, W), col[1], np.float32), np.full((H, W), col[2], np.float32), a * 255]).astype(np.uint8)
    img.alpha_composite(Image.fromarray(lay, "RGBA"))


def glow_on(img, spr, x, y, k):
    """Additive glow onto a PIL RGBA image (returns a new image)."""
    a = to_arr(img); add_glow(a, spr, x, y, k)
    return to_img(a)


# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """Cambodia: blue / red (double height) / blue, white Angkor Wat in the middle. Drawn at 2x then reduced."""
    global _FLAG
    if _FLAG is None:
        w, h = 300, 190
        s = 2
        im = Image.new("RGBA", (w * s, h * s), (3, 46, 161, 255)); d = ImageDraw.Draw(im)
        d.rectangle([0, h * s / 4, w * s, h * s * 3 / 4], fill=(224, 0, 37, 255))
        cx, by = w * s / 2, h * s * 0.70
        white = (255, 255, 255, 255)
        d.rectangle([cx - 92 * s, by - 8 * s, cx + 92 * s, by], fill=white)            # base terrace
        d.rectangle([cx - 80 * s, by - 18 * s, cx + 80 * s, by - 8 * s], fill=white)
        for dx, th, tw in ((-64, 46, 12), (64, 46, 12), (-34, 60, 15), (34, 60, 15), (0, 78, 19)):
            x = cx + dx * s
            d.rectangle([x - tw * s, by - (th - 26) * s, x + tw * s, by - 18 * s], fill=white)
            d.polygon([(x - tw * s, by - (th - 26) * s), (x - tw * 0.55 * s, by - th * s), (x, by - (th + 10) * s),
                       (x + tw * 0.55 * s, by - th * s), (x + tw * s, by - (th - 26) * s)], fill=white)
        for dx in (-48, -18, 18, 48):                       # dark doorways / gaps
            d.rectangle([cx + dx * s - 3 * s, by - 16 * s, cx + dx * s + 3 * s, by - 9 * s], fill=(224, 0, 37, 255))
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
        lum = 1.0 + 0.16 * math.cos(ph)
        col = a[:, x].copy(); col[:, :3] *= lum
        out[12 + dy:12 + dy + h, x] = col
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    # a small pole on the left
    im2 = Image.new("RGBA", (w + 14, h + 24), (0, 0, 0, 0)); im2.alpha_composite(im, (14, 0))
    ImageDraw.Draw(im2).rectangle([0, 0, 7, h + 23], fill=(200, 190, 170, 255))
    sc = width / im2.width
    return im2.resize((width, int(im2.height * sc)), Image.LANCZOS)


def put_header(out, hdr, t, flag=True):
    lays = header_layers(hdr, t)
    for im, (x, y), al in lays:
        if al > 0.01:
            out.alpha_composite(with_alpha(im, al), (int(x), int(y)))
    if flag:
        fw = flag_wave(t)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 40))


def clock_ui(now, k=1.0):
    """'10:02 PM | SUNRISE 5:40' pill: the ticking clock of the episode."""
    f1 = font(INTER_SB, 46); f2 = font(INTER_M, 32)
    w, h = 520, 108
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(0, 0, 0, int(175 * k)), outline=(255, 70, 50, int(200 * k)), width=3)
    d.text((140, h / 2), now, font=f1, fill=(255, 245, 235, int(255 * k)), anchor="mm")
    d.line([(272, 22), (272, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    # small sun icon
    d.pieslice([292, 40, 342, 90], 180, 360, fill=(255, 150, 60, int(255 * k)))
    d.text((430, h / 2 - 16), "SUNRISE", font=f2, fill=(255, 190, 140, int(255 * k)), anchor="mm")
    d.text((430, h / 2 + 18), "5:40 AM", font=f2, fill=(255, 190, 140, int(255 * k)), anchor="mm")
    return im


def fmt_clock(minutes):
    """minutes after 22:00 -> '10:02 PM' style."""
    m = int(22 * 60 + minutes) % (24 * 60)
    hh, mm = divmod(m, 60)
    ap = "AM" if hh < 12 else "PM"
    h12 = hh % 12 or 12
    return f"{h12}:{mm:02d} {ap}"


# ============================================================ characters
_HC = {}


def hero(phase=0.0, run=0.0, back=False, scale=1.0):
    """Dara: ponytail, faded maroon t-shirt, dark patterned sampot skirt. Returns (RGBA, feet_x, feet_y)."""
    q = (round(phase * 12) % 12, round(run, 1), back, round(scale, 2))
    if q in _HC:
        return _HC[q]
    w, h = 440, 880
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.35 + 0.65 * run)
    lean = 16 * run

    def legs(d, s):
        for sg in (-1, 1):
            a = sg * sw * 0.6
            hx, hy = cx + lean * 0.3 + sg * 16, 600
            kx, ky = hx + math.sin(a) * 115, hy + math.cos(a) * 105
            fx, fy = kx + math.sin(a - 0.35 * run) * 105, ky + 100
            d.line([(hx * s, hy * s), (kx * s, ky * s), (fx * s, fy * s)], fill=255, width=int(26 * s), joint="curve")
            d.ellipse([(fx - 26) * s, (fy - 10) * s, (fx + 30) * s, (fy + 12) * s], fill=255)

    def skirt(d, s):
        sp = abs(sw) * 46
        d.polygon([(x * s, y * s) for x, y in ((cx - 58 + lean * .5, 400), (cx + 58 + lean * .5, 400), (cx + 66 + sp, 640), (cx - 66 - sp, 640))], fill=255)

    def torso(d, s):
        L = lean
        d.polygon([(x * s, y * s) for x, y in ((cx - 70 + L, 195), (cx + 70 + L, 195), (cx + 58 + L * .6, 415), (cx - 58 + L * .6, 415))], fill=255)
        d.ellipse([(cx - 76 + L) * s, 182 * s, (cx - 36 + L) * s, 236 * s], fill=255)
        d.ellipse([(cx + 36 + L) * s, 182 * s, (cx + 76 + L) * s, 236 * s], fill=255)

    def arms(d, s):
        L = lean
        for sg in (-1, 1):
            sx, sy = cx + sg * 62 + L, 210
            a = -sg * sw * 0.9
            ex, ey = sx + math.sin(a) * 85 + sg * 8, sy + math.cos(a) * 95
            b = a - 0.9 * run * sg
            hx, hy = ex + math.sin(b) * 88, ey + math.cos(b) * 78 - 40 * run
            d.line([(sx * s, sy * s), (ex * s, ey * s), (hx * s, hy * s)], fill=255, width=int(22 * s), joint="curve")
            d.ellipse([(hx - 14) * s, (hy - 14) * s, (hx + 14) * s, (hy + 14) * s], fill=255)

    def head(d, s):
        L = lean * 1.2
        d.rectangle([(cx - 17 + L) * s, 140 * s, (cx + 17 + L) * s, 200 * s], fill=255)
        d.ellipse([(cx - 48 + L) * s, 44 * s, (cx + 48 + L) * s, 166 * s], fill=255)

    def hair(d, s):
        L = lean * 1.2
        d.pieslice([(cx - 53 + L) * s, 34 * s, (cx + 53 + L) * s, 150 * s], 180, 360, fill=255)
        d.polygon([(x * s, y * s) for x, y in ((cx - 53 + L, 92), (cx - 48 + L, 60), (cx + 20 + L, 72), (cx + 53 + L, 92), (cx + 50 + L, 58), (cx - 46 + L, 58))], fill=255)
        tail = -1 if not back else 0
        px = cx + 46 + L if not back else cx + L
        swing = 30 * run * math.sin(ph * 2)
        d.polygon([(x * s, y * s) for x, y in ((px - 12, 70), (px + 14, 70), (px + 34 - 60 * run + swing, 250), (px + 10 - 70 * run + swing, 262))], fill=255)
        if back:
            d.ellipse([(cx - 50 + L) * s, 40 * s, (cx + 50 + L) * s, 160 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    skin = (170, 112, 86)
    img.alpha_composite(shade(legs, (w, h), skin, 12))
    sk = shade(skirt, (w, h), (60, 26, 40), 30)
    a = np.asarray(sk, np.float32)                       # woven sampot pattern: little diamonds
    yy, xx = np.mgrid[0:h, 0:w]
    pat = (((xx + yy) // 18 + (xx - yy) // 18) % 2) * 0.18 + ((yy % 60) < 6) * 0.25
    a[..., :3] *= (1 - pat)[..., None]
    img.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    img.alpha_composite(shade(torso, (w, h), (118, 70, 72), 36))
    img.alpha_composite(shade(arms, (w, h), skin, 11))
    img.alpha_composite(shade(head, (w, h), skin, 28))
    img.alpha_composite(shade(hair, (w, h), (20, 14, 14), 16))
    d = ImageDraw.Draw(img)
    L = lean * 1.2
    if not back:
        for sg in (-1, 1):
            d.ellipse([cx + sg * 19 - 9 + L, 98, cx + sg * 19 + 9 + L, 113], fill=(240, 236, 230, 255))
            d.ellipse([cx + sg * 19 - 4 + L, 101, cx + sg * 19 + 4 + L, 110], fill=(15, 10, 10, 255))
        d.ellipse([cx - 6 + L, 136, cx + 6 + L, 146], fill=(70, 28, 28, 255))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 812 * scale)
    _HC[q] = out
    return out


_CR = {}


def hero_crouch(scale=1.0, look_up=0.0):
    """Dara crouched, knees up, hands over her mouth (holding her breath). Feet at the bottom-centre."""
    key = (round(scale, 2), round(look_up, 1))
    if key in _CR:
        return _CR[key]
    w, h = 460, 560
    cx = 230
    up = look_up * 26

    def body(d, s):
        d.polygon([(x * s, y * s) for x, y in ((150, 230), (300, 230), (330, 420), (330, 520), (120, 520), (110, 400))], fill=255)

    def knees(d, s):
        d.ellipse([200 * s, 250 * s, 350 * s, 390 * s], fill=255)
        d.polygon([(x * s, y * s) for x, y in ((240, 330), (340, 320), (330, 530), (270, 530))], fill=255)

    def head(d, s):
        d.ellipse([(cx - 46) * s, (70 - up) * s, (cx + 46) * s, (186 - up) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 51) * s, (60 - up) * s, (cx + 51) * s, (170 - up) * s], 180, 360, fill=255)
        d.polygon([(x * s, y * s) for x, y in ((cx - 51, 115 - up), (cx - 60, 230), (cx - 30, 220), (cx - 40, 120 - up))], fill=255)

    def hands(d, s):
        d.ellipse([(cx - 30) * s, (140 - up) * s, (cx + 24) * s, (178 - up) * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    skin = (170, 112, 86)
    img.alpha_composite(shade(body, (w, h), (92, 52, 58), 40))
    sk = shade(knees, (w, h), (60, 26, 40), 30)
    a = np.asarray(sk, np.float32); yy, xx = np.mgrid[0:h, 0:w]
    pat = (((xx + yy) // 16 + (xx - yy) // 16) % 2) * 0.2
    a[..., :3] *= (1 - pat)[..., None]
    img.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    img.alpha_composite(shade(lambda d, s: d.line([(170 * s, 250 * s), (250 * s, 340 * s), (330 * s, 330 * s)], fill=255, width=int(26 * s), joint="curve"), (w, h), (170, 112, 86), 10))
    img.alpha_composite(shade(head, (w, h), skin, 26))
    img.alpha_composite(shade(hair, (w, h), (20, 14, 14), 14))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ey = 116 - up - (6 if look_up > 0.5 else 0)
        d.ellipse([cx + sg * 18 - 9, ey, cx + sg * 18 + 9, ey + 16], fill=(240, 236, 230, 255))
        d.ellipse([cx + sg * 18 - 4, ey + (0 if look_up > 0.5 else 4), cx + sg * 18 + 4, ey + (8 if look_up > 0.5 else 12)], fill=(15, 10, 10, 255))
    img.alpha_composite(shade(hands, (w, h), skin, 10))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 530 * scale)
    _CR[key] = out
    return out


_AP = {}


def ap_sprite(open_mouth=0.0):
    """The Ap: a woman's pale floating head, very long black hair streaming down, closed thin lips.
    Below the chin there is NO body: only a soft trail of light (drawn separately). Returns (RGBA, eye1, eye2, chin)."""
    key = round(open_mouth, 1)
    if key in _AP:
        return _AP[key]
    w, h = 640, 1000
    cx, cy = 320, 300

    def hair_back(d, s):
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        d.ellipse([(cx - 120) * s, (cy - 150) * s, (cx + 120) * s, (cy + 120) * s], fill=255)
        strands = []
        for i in range(13):
            u = (i / 12 - 0.5)
            x0 = cx + u * 230
            L = 420 + 240 * (1 - abs(u) * 1.5) + 60 * math.sin(i * 2.3)
            wob = 50 * math.sin(i * 1.7)
            strands.append((x0, L, wob))
        for x0, L, wob in strands:
            d.polygon(P((x0 - 26, cy - 40), (x0 + 26, cy - 40), (x0 + 14 + wob, cy + L * 0.6), (x0 + wob * 1.6, cy + L), (x0 - 12 + wob, cy + L * 0.6)), fill=255)

    def face(d, s):
        d.ellipse([(cx - 74) * s, (cy - 92) * s, (cx + 74) * s, (cy + 110) * s], fill=255)
        d.polygon([(x * s, y * s) for x, y in ((cx - 60, cy + 40), (cx + 60, cy + 40), (cx + 22, cy + 136), (cx - 22, cy + 136))], fill=255)

    def hair_front(d, s):
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        d.pieslice([(cx - 112) * s, (cy - 148) * s, (cx + 112) * s, (cy + 80) * s], 180, 360, fill=255)
        for sg in (-1, 1):   # curtains of hair over the sides of the face
            d.polygon(P((cx + sg * 112, cy - 40), (cx + sg * 30, cy - 70), (cx + sg * 46, cy + 30), (cx + sg * 60, cy + 200),
                        (cx + sg * 52, cy + 380), (cx + sg * 96, cy + 300), (cx + sg * 122, cy + 120)), fill=255)
        for x, y1 in ((cx - 14, cy + 40), (cx + 18, cy + 10)):
            d.polygon(P((x - 8, cy - 80), (x + 8, cy - 80), (x + 3, y1), (x - 2, y1)), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hb = shade(hair_back, (w, h), (16, 11, 12), 40, rim_strength=1.4)
    a = np.asarray(hb, np.float32)
    yy = np.arange(h)[:, None]
    a[..., 3] *= np.clip((h - 60 - yy) / 260, 0, 1)            # hair ends fade into the dark
    img.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    img.alpha_composite(shade(face, (w, h), (214, 206, 198), 46, rim_strength=0.7))
    d = ImageDraw.Draw(img)
    e1, e2 = (cx - 32, cy + 6), (cx + 32, cy + 6)
    for ex, ey in (e1, e2):                                     # dark sunken eyes
        d.ellipse([ex - 24, ey - 15, ex + 24, ey + 17], fill=(28, 10, 12, 255))
    mo = open_mouth
    d.line([(cx - 26, cy + 92), (cx, cy + 96 + 6 * mo), (cx + 26, cy + 92)], fill=(70, 20, 24, 255), width=5)
    if mo > 0.3:
        d.ellipse([cx - 16, cy + 88, cx + 16, cy + 100 + 22 * mo], fill=(20, 6, 8, 255))
    img.alpha_composite(shade(hair_front, (w, h), (18, 12, 13), 22, rim_strength=1.5))
    out = (img, e1, e2, (cx, cy + 135), (cx, cy))
    _AP[key] = out
    return out


_TRAIL = {}


def trail_sprite(length=520):
    """A tapering ribbon of light under the head: will-o'-the-wisp glow, no organs, no gore."""
    if length in _TRAIL:
        return _TRAIL[length]
    w, h = 300, length + 60
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    for i in range(40):
        u = i / 39
        y = 20 + u * length
        x = w / 2 + 40 * math.sin(u * 5.5) * u
        r = 46 * (1 - u) ** 1.3 + 3
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(14))
    core = m.point(lambda v: min(255, int(v * 1.6)))
    arr = np.zeros((h, w, 4), np.float32)
    mv = np.asarray(m, np.float32) / 255; cv = np.asarray(core, np.float32) / 255
    yy = np.linspace(0, 1, h)[:, None]
    arr[..., 0] = 255
    arr[..., 1] = 60 + 170 * cv * (1 - yy)
    arr[..., 2] = 50 + 150 * cv * (1 - yy)
    arr[..., 3] = 255 * np.clip(mv * 0.9, 0, 1) * (1 - 0.5 * yy)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    _TRAIL[length] = out
    return out


def eye(img, x, y, k, sc=1.0):
    r = max(4, 11 * sc); R = int(64 * max(sc, 0.35))
    spr = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    ImageDraw.Draw(spr).ellipse([R - r, R - r * 0.75, R + r, R + r * 0.75], fill=(255, 40, 30, int(255 * min(1, k))))
    g = spr.filter(ImageFilter.GaussianBlur(R / 6))
    img.alpha_composite(g, (int(x - R), int(y - R))); img.alpha_composite(g, (int(x - R), int(y - R)))
    img.alpha_composite(spr, (int(x - R), int(y - R)))
    if k > 0.6:
        ImageDraw.Draw(img).ellipse([x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3], fill=(255, 230, 200, int(255 * min(1, k))))


_GLOW = {}


def gsp(r, col=(255, 90, 70), p=1.6):
    k = (r, col, p)
    if k not in _GLOW:
        _GLOW[k] = glow_sprite(r, col, p)
    return _GLOW[k]


def put_ap(img, x, y, scale=1.0, t=0.0, eyes=1.0, tilt=0.0, trail=1.0, aura=0.55, mouth=0.0, glow=1.0, flip_trail=False):
    """Composite the Ap with its head centre at (x, y). Returns the new image (glow is additive)."""
    body, e1, e2, chin, ctr = ap_sprite(mouth)
    ang = tilt + 4 * math.sin(t * 1.1)
    if trail > 0:
        tr = trail_sprite()
        sw = tr.rotate(8 * math.sin(t * 1.7) + (25 if flip_trail else 0), resample=Image.BICUBIC, center=(tr.width / 2, 0))
        sw = sw.resize((max(1, int(sw.width * scale)), max(1, int(sw.height * scale))), Image.LANCZOS)
        img.alpha_composite(with_alpha(sw, trail), (int(x - sw.width / 2), int(y + 110 * scale)))
    g = body.rotate(ang, resample=Image.BICUBIC, center=ctr)
    if scale != 1.0:
        g = g.resize((max(1, int(g.width * scale)), max(1, int(g.height * scale))), Image.LANCZOS)
    gx, gy = int(x - ctr[0] * scale), int(y - ctr[1] * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(max(2, 34 * scale)))
        lay = Image.new("RGBA", g.size, (255, 60, 50, 0)); lay.putalpha(al.point(lambda v: int(v * aura)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    if eyes > 0:
        k = eyes * (0.65 + 0.35 * math.sin(t * 5) ** 2)
        ca, sa = math.cos(math.radians(-ang)), math.sin(math.radians(-ang))
        for ex, ey in (e1, e2):
            dx, dy = ex - ctr[0], ey - ctr[1]
            rx, ry = dx * ca - dy * sa, dx * sa + dy * ca
            eye(img, x + rx * scale, y + ry * scale, k, scale)
    if glow > 0:
        img = glow_on(img, gsp(int(max(40, 260 * scale)), (255, 80, 60)), x, y + 40 * scale, 0.55 * glow)
    return img


def dog(bark=0.0, eyes=0.0, flip=False):
    """Village dog silhouette, standing. bark in 0..1 lifts the head and opens the jaw."""
    w, h = 300, 220
    m = Image.new("L", (w * 2, h * 2), 0); d = ImageDraw.Draw(m)
    S = lambda pts: [(x * 2, y * 2) for x, y in pts]
    d.polygon(S([(60, 110), (200, 100), (220, 140), (60, 150)]), fill=255)
    for x0 in (70, 95, 185, 205):
        d.line(S([(x0, 140), (x0 + 4, 212)]), fill=255, width=16)
    d.line(S([(62, 115), (30, 80 + 20 * bark), (24, 60)]), fill=255, width=14)
    a = -0.25 - 0.55 * bark
    hx, hy = 205, 100
    tip = (hx + math.cos(a) * 70, hy + math.sin(a) * 70)
    d.polygon(S([(hx - 20, hy + 22), (hx + 10, hy - 24), (tip[0], tip[1] - 6), (tip[0] + 4, tip[1] + 6)]), fill=255)
    if bark > 0.3:
        jaw = a + 0.45 * bark
        d.polygon(S([(hx, hy + 16), (hx + math.cos(jaw) * 62, hy + math.sin(jaw) * 62 + 10), (hx + math.cos(jaw) * 50, hy + math.sin(jaw) * 50 + 20)]), fill=255)
    d.polygon(S([(hx - 6, hy - 18), (hx - 4, hy - 62), (hx + 20, hy - 26)]), fill=255)
    m = m.resize((w, h), Image.LANCZOS)
    im = Image.new("RGBA", (w, h), (8, 3, 4, 0)); im.putalpha(m)
    if eyes > 0:
        eye(im, hx + math.cos(a) * 26, hy + math.sin(a) * 26 - 6, eyes, 0.22)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


# ============================================================ props
def sugar_palm(seed=0, height=760):
    """Thnot (sugar palm): tall straight trunk, round spiky crown of fan leaves."""
    rng = np.random.default_rng(seed)
    w, h = 460, height + 260
    cx = w / 2 + rng.uniform(-20, 20)
    top = 230

    def trunk(d, s):
        d.polygon([((cx - 13) * s, top * s), ((cx + 13) * s, top * s), ((cx + 20) * s, h * s), ((cx - 20) * s, h * s)], fill=255)

    def crown(d, s):
        for k in range(26):
            ang = -math.pi + k * math.pi / 13 + rng.uniform(-.1, .1)
            L = rng.uniform(140, 200)
            ex, ey = cx + math.cos(ang) * L, top + math.sin(ang) * L * 0.85 + 20
            for j in range(5):                       # fan leaf: a spray of spikes
                a2 = ang + (j - 2) * 0.09
                d.polygon([(cx * s, top * s), ((cx + math.cos(a2) * L * 1.05) * s, (top + math.sin(a2) * L * 0.9 + 20) * s),
                           ((cx + math.cos(a2 + .05) * L * .7) * s, (top + math.sin(a2 + .05) * L * .6 + 14) * s)], fill=255)
        d.ellipse([(cx - 46) * s, (top - 34) * s, (cx + 46) * s, (top + 40) * s], fill=255)

    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tr = shade(trunk, (w, h), (40, 24, 22), 10)
    a = np.asarray(tr, np.float32); yy = np.arange(h)[:, None]
    a[..., :3] *= (1 - 0.3 * ((yy % 26) < 5))[..., None]       # ring scars
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    im.alpha_composite(shade(crown, (w, h), (30, 20, 20), 26, rim_strength=1.2))
    return im


def angkor_far():
    """The five lotus-bud towers of Angkor Wat, a hazy silhouette on the horizon."""
    w, h = 760, 300
    def dr(d, s):
        P = lambda *p: [(x * s, y * s) for x, y in p]
        d.rectangle([20 * s, 250 * s, 740 * s, 300 * s], fill=255)
        d.rectangle([90 * s, 210 * s, 670 * s, 252 * s], fill=255)
        for x, top, wd in ((190, 120, 34), (570, 120, 34), (290, 80, 40), (470, 80, 40), (380, 20, 52)):
            d.rectangle([(x - wd) * s, (top + 70) * s, (x + wd) * s, 215 * s], fill=255)
            d.polygon(P((x - wd, top + 72), (x - wd * .7, top + 30), (x - wd * .3, top + 8), (x, top), (x + wd * .3, top + 8), (x + wd * .7, top + 30), (x + wd, top + 72)), fill=255)
            for k in range(4):
                y = top + 70 - k * 16
                d.line([((x - wd * (1 - k * .18)) * s, y * s), ((x + wd * (1 - k * .18)) * s, y * s)], fill=0, width=int(2 * s))
    im = shade(dr, (w, h), (60, 16, 18), 20, rim_strength=0.5)
    a = np.asarray(im, np.float32)
    a[..., :3] = a[..., :3] * 0.45 + np.array([90, 20, 20]) * 0.55
    return dof(Image.fromarray(a.astype(np.uint8), "RGBA"), 2.0)


def stilt_house():
    """Khmer stilt house: tall posts, plank walls, steep roof with horn finials, a ladder, a lamplit window."""
    w, h = 900, 1250
    def posts(d, s):
        for x in (120, 330, 560, 780):
            d.rectangle([(x - 20) * s, 600 * s, (x + 20) * s, 1250 * s], fill=255)
        d.rectangle([90 * s, 600 * s, 810 * s, 640 * s], fill=255)
    def walls(d, s):
        d.rectangle([110 * s, 360 * s, 790 * s, 610 * s], fill=255)
    def roof(d, s):
        d.polygon([(40 * s, 380 * s), (450 * s, 70 * s), (860 * s, 380 * s), (860 * s, 410 * s), (40 * s, 410 * s)], fill=255)
        for x0, dx in ((450, 0),):
            d.polygon([((x0 - 8) * s, 80 * s), ((x0 + 8) * s, 80 * s), ((x0 + 30) * s, 20 * s), ((x0 + 18) * s, 18 * s)], fill=255)
        d.polygon([(40 * s, 385 * s), (20 * s, 330 * s), (34 * s, 328 * s), (62 * s, 380 * s)], fill=255)
        d.polygon([(860 * s, 385 * s), (880 * s, 330 * s), (866 * s, 328 * s), (838 * s, 380 * s)], fill=255)
    def ladder(d, s):
        d.line([(600 * s, 610 * s), (690 * s, 1250 * s)], fill=255, width=int(16 * s))
        d.line([(680 * s, 610 * s), (770 * s, 1250 * s)], fill=255, width=int(16 * s))
        for k in range(8):
            y = 680 + k * 75; x = 600 + (y - 610) * 90 / 640
            d.line([(x * s, y * s), ((x + 80) * s, y * s)], fill=255, width=int(12 * s))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.alpha_composite(shade(posts, (w, h), (54, 32, 26), 12))
    wl = shade(walls, (w, h), (78, 44, 34), 20)
    a = np.asarray(wl, np.float32); xx = np.arange(w)[None, :]
    a[..., :3] *= (1 - 0.35 * ((xx % 38) < 4))[..., None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    rf = shade(roof, (w, h), (70, 36, 30), 30)
    a = np.asarray(rf, np.float32); yy = np.arange(h)[:, None]
    a[..., :3] *= (0.8 + 0.2 * np.sin(yy / 7 + xx / 40))[..., None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    im.alpha_composite(shade(ladder, (w, h), (66, 40, 30), 8))
    d = ImageDraw.Draw(im)
    d.rectangle([200, 440, 330, 560], fill=(255, 150, 70, 255))          # lamplit window
    d.line([(265, 440), (265, 560)], fill=(60, 30, 20, 255), width=8)
    d.rectangle([460, 430, 560, 610], fill=(30, 14, 12, 255))           # door
    return im, (265, 500)


def jar(scale=1.0):
    """Big glazed clay water jar (pieng) with a lid tilted against it."""
    w, h = 520, 600
    def dr(d, s):
        d.ellipse([30 * s, 90 * s, 490 * s, 590 * s], fill=255)
        d.rectangle([150 * s, 40 * s, 370 * s, 140 * s], fill=255)
        d.ellipse([130 * s, 20 * s, 390 * s, 80 * s], fill=255)
    im = shade(dr, (w, h), (92, 46, 30), 90, rim_strength=1.0)
    a = np.asarray(im, np.float32); yy, xx = np.mgrid[0:h, 0:w]
    a[..., :3] *= (1 - 0.18 * (np.sin(yy / 14) > 0.85))[..., None]       # throwing rings
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    for k in range(3):                                                  # dragon-glaze dabs
        d.arc([120 + k * 90, 220, 200 + k * 90, 300], 200, 340, fill=(160, 110, 50, 255), width=6)
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


def thorn_branch(seed=0, length=520, col=(30, 16, 14)):
    rng = np.random.default_rng(seed)
    w, h = length + 80, 220
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def branch(x, y, ang, L, wd, depth):
        if depth == 0 or L < 20:
            return
        x2, y2 = x + math.cos(ang) * L, y + math.sin(ang) * L
        d.line([(x, y), (x2, y2)], fill=col + (255,), width=max(2, int(wd)))
        n = int(L / 18)
        for k in range(n):
            u = (k + .5) / n; px, py = x + (x2 - x) * u, y + (y2 - y) * u
            sg = 1 if k % 2 else -1
            na = ang + sg * 1.1
            d.polygon([(px - 3, py), (px + 3, py), (px + math.cos(na) * 16, py + math.sin(na) * 16)], fill=col + (255,))
        for _ in range(2):
            branch(x + (x2 - x) * rng.uniform(.3, .8), y + (y2 - y) * rng.uniform(.3, .8), ang + rng.uniform(-.8, .8), L * .5, wd * .6, depth - 1)
    branch(40, h / 2 + 20, -0.05, length, 9, 3)
    return im


def laundry(t, flap=1.0, sarong=True, gust=0.0):
    """A line between two posts with a white sarong and a red checked krama, flapping."""
    w, h = 900, 700
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def post(d2, s, x):
        d2.rectangle([(x - 12) * s, 60 * s, (x + 12) * s, 700 * s], fill=255)
    im.alpha_composite(shade(lambda d2, s: post(d2, s, 40), (w, h), (50, 30, 24), 8))
    im.alpha_composite(shade(lambda d2, s: post(d2, s, 860), (w, h), (50, 30, 24), 8))
    sag = lambda x: 90 + 60 * math.sin(math.pi * (x - 40) / 820)
    d.line([(x, sag(x)) for x in range(40, 861, 20)], fill=(150, 130, 120, 255), width=4)
    def cloth(x0, x1, L, col, check=False):
        pts_top = [(x, sag(x)) for x in np.linspace(x0, x1, 12)]
        pts_bot = []
        for i, x in enumerate(np.linspace(x1, x0, 12)):
            u = i / 11
            wv = (22 * math.sin(t * 4 + u * 5) * flap + 140 * gust * math.sin(t * 13 + u * 4)) * (0.6 + 0.4 * u)
            pts_bot.append((x + wv * 0.7, sag(x) + L + 18 * math.sin(t * 3 + u * 6) * flap + wv * 0.3))
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).polygon(pts_top + pts_bot, fill=255)
        c = shade(lambda d2, s: d2.polygon([(x * s, y * s) for x, y in pts_top + pts_bot], fill=255), (w, h), col, 24, rim_strength=0.8)
        a = np.asarray(c, np.float32)
        yy, xx = np.mgrid[0:h, 0:w]
        fold = 0.9 + 0.1 * np.sin(xx / 38 + np.sin(yy / 90 + t * 2) * 1.2)
        a[..., :3] *= fold[..., None]
        if check:
            a[..., :3] *= (1 - 0.45 * (((xx // 22) % 2) ^ ((yy // 22) % 2)))[..., None]
        im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    cloth(110, 290, 230, (170, 40, 40), check=True)          # krama
    if sarong:
        cloth(420, 760, 420, (226, 220, 210))                 # white sarong
    return im


# ============================================================ worlds
class Village:
    """Night village: blood-red moon, Angkor far away, sugar palms, rice paddies with reflections, a stilt house."""
    def __init__(self):
        y = np.linspace(0, 1, H)[:, None]
        top = np.array([3, 1, 2], np.float32); mid = np.array([30, 4, 6], np.float32); hor = np.array([130, 26, 20], np.float32)
        k1 = np.clip(y / 0.5, 0, 1) ** 1.5; k2 = np.clip((y - 0.38) / 0.16, 0, 1)
        col = top * (1 - k1) + mid * k1; col = col * (1 - k2) + hor * k2
        col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
        yy, xx = np.mgrid[0:H, 0:W]
        dd = np.sqrt((xx - MOON[0]) ** 2 + (yy - MOON[1]) ** 2)
        col += (np.exp(-dd / 300) * 120)[..., None] * np.array([1.0, 0.3, 0.22])
        moon = np.clip((110 - dd) / 2, 0, 1)
        tex = fog_texture(W, H, 17)
        mcol = np.array([235, 110, 80], np.float32) * (0.8 + 0.25 * tex)[..., None]
        col = col * (1 - moon[..., None]) + mcol * moon[..., None]
        cl = fog_texture(W, H, 23) * np.exp(-((yy - 520) / 140) ** 2)
        col = col * (1 - 0.55 * cl[..., None]) + np.array([40, 8, 10]) * 0.55 * cl[..., None]
        col[yy >= HZ] = 0
        self.sky = to_img(col)
        # rice paddy water: moon reflection column, dikes in perspective
        f = np.zeros((H, W, 3), np.float32)
        g = np.clip((yy - HZ) / (H - HZ), 0, 1)
        f[..., 0] = 60 - 45 * g; f[..., 1] = 10 - 7 * g; f[..., 2] = 12 - 8 * g
        rip = fog_texture(W, H, 61)
        refl = np.exp(-((xx - MOON[0]) / (60 + 260 * g)) ** 2) * (0.5 + 0.5 * np.sin(yy / (3 + 10 * g)) ** 8)
        f += refl[..., None] * np.array([200, 70, 50]) * (1 - g * 0.6)[..., None] * (0.6 + 0.6 * rip)[..., None]
        # dikes
        for k in range(7):
            yk = HZ + 14 + (k ** 1.8) * 22
            m = (np.abs(yy - yk) < 2 + k * 1.6)
            f[m] = np.array([24, 8, 8])
        f[yy < HZ] = 0
        alpha = (yy >= HZ).astype(np.float32) * 255
        self.field = Image.fromarray(np.dstack([np.clip(f, 0, 255), alpha]).astype(np.uint8), "RGBA")
        self.angkor = angkor_far()
        self.far = dof(D5.treeline(3, 30, 0.6, (34, 8, 10), 360), 3)
        self.palms = [dof(sugar_palm(i, hgt), 1.2) for i, hgt in ((1, 620), (2, 760), (3, 540), (4, 700))]
        hs, wn = stilt_house(); HSC = 0.72
        self.house = hs.resize((int(hs.width * HSC), int(hs.height * HSC)), Image.LANCZOS); self.win = (wn[0] * HSC, wn[1] * HSC)
        self.fg = dof(D5.foreground(), 9)
        self.rice = self._rice()

    def _rice(self):
        m = Image.new("L", (W + 400, 420), 0); d = ImageDraw.Draw(m)
        rng = np.random.default_rng(8)
        for row in range(4):
            y0 = 120 + row * 90
            for x in range(-20, W + 420, 34):
                xx = x + rng.uniform(-8, 8)
                for k in range(5):
                    a = -math.pi / 2 + (k - 2) * 0.25 + rng.uniform(-.1, .1)
                    L = rng.uniform(50, 90) * (0.6 + row * 0.2)
                    d.line([(xx, y0), (xx + math.cos(a) * L, y0 + math.sin(a) * L)], fill=255, width=3 + row)
        im = Image.new("RGBA", m.size, (14, 5, 6, 0)); im.putalpha(m)
        return im

    def frame(self, t, cam, house=True, palms=True, extra_back=None, extra_mid=None, extra_front=None, lamp=1.0, rice=True):
        img = self.sky.copy()
        P = lambda k: int(-cam * k)
        img.alpha_composite(self.angkor, (P(0.08) + 60, HZ - 300 + 10))
        img.alpha_composite(self.far, (P(0.12) % 300 - 300, HZ - 360 + 8))
        img.alpha_composite(self.field)
        if extra_back:
            img = extra_back(img, t, P) or img
        if palms:
            for i, (pl, x) in enumerate(zip(self.palms, (-60, 230, 520, 880))):
                sway = pl.rotate(0.8 * math.sin(t * 0.7 + i), resample=Image.BICUBIC, center=(pl.width / 2, pl.height))
                img.alpha_composite(sway, (P(0.3) + x, HZ + 40 + i * 10 - pl.height))
        if extra_mid:
            img = extra_mid(img, t, P) or img
        hx = P(0.6) + 400
        if house:
            img.alpha_composite(self.house, (hx, GY - self.house.height + 40))
        if rice:
            img.alpha_composite(self.rice, (P(0.9) % 400 - 400, H - 420 - 80))
        if extra_front:
            img = extra_front(img, t, P) or img
        a = to_arr(img)
        if house and lamp > 0:
            fl = lamp * (0.85 + 0.15 * math.sin(t * 23) * math.sin(t * 6))
            add_glow(a, gsp(220, (255, 150, 70)), hx + self.win[0], GY - self.house.height + 40 + self.win[1], 0.55 * fl)
        return to_img(a)


_V = None


def village():
    global _V
    if _V is None:
        _V = Village()
    return _V


class Under:
    """Under the stilt house: floor planks above with lamp light slits, posts, dirt floor, the big jar, a hammock,
    the view out to the moonlit field between the posts."""
    def __init__(self):
        V = village()
        out = V.frame(0, 0, house=False, rice=False)
        self.out = dof(out, 2.5)
        a = np.zeros((H, W, 4), np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        # ceiling planks (the floor of the house) at the top
        ceil = yy < 330
        a[..., 0] = 34; a[..., 1] = 16; a[..., 2] = 14
        a[..., :3] *= (1 - 0.4 * ((xx % 90) < 5))[..., None]
        a[..., 3] = 255 * ceil
        self.slits = ceil & ((xx % 90) >= 5) & ((xx % 90) < 9) & (yy > 40)
        # dirt floor
        fl = yy > GY - 40
        g = np.clip((yy - GY) / 600, 0, 1)
        tex = fog_texture(W, H, 33)
        dirt = np.stack([46 - 26 * g, 20 - 12 * g, 16 - 10 * g], -1) * (0.7 + 0.6 * tex)[..., None]
        a[..., :3] = np.where(fl[..., None], dirt, a[..., :3])
        a[..., 3] = np.where(fl, 255, a[..., 3])
        self.shell = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
        def posts(d, s):
            for x, wd in ((40, 70), (420, 46), (700, 40), (1010, 80)):
                d.rectangle([(x - wd / 2) * s, 0, (x + wd / 2) * s, (H - 300) * s], fill=255)
            d.rectangle([0, 300 * s, W * s, 340 * s], fill=255)                          # beam
        self.posts = shade(posts, (W, H - 300), (60, 34, 26), 20)
        self.jar = jar(1.0)
        self.thorns = [thorn_branch(i, 520) for i in range(4)]
        self.hammock = self._hammock()
        self.lamp_slit = gsp(160, (255, 160, 80))

    def _hammock(self):
        im = Image.new("RGBA", (W, 400), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        pts = [(420 + u * 280, 40 + 150 * math.sin(math.pi * u)) for u in np.linspace(0, 1, 20)]
        d.line(pts, fill=(90, 40, 40, 255), width=26, joint="curve")
        for k in range(6):
            d.line([(p[0], p[1] + k * 5 - 12) for p in pts], fill=(120, 60, 50, 255), width=2)
        return im

    def frame(self, t, cam=0.0, thorns=True, slit_k=1.0, extra_out=None, jar_x=-40):
        P = lambda k: int(-cam * k)
        img = self.out.copy()
        if extra_out:
            img = extra_out(img, t, P) or img
        img.alpha_composite(self.shell)
        img.alpha_composite(self.posts, (P(0.8), 0))
        img.alpha_composite(self.hammock, (P(0.8), 330))
        if thorns:
            for i, th in enumerate(self.thorns):
                img.alpha_composite(th, (P(0.9) - 120 + i * 360, GY - 150))
        a = to_arr(img)
        if slit_k > 0:
            fl = slit_k * (0.8 + 0.2 * math.sin(t * 17) * math.sin(t * 5))
            m = self.slits
            a[m] = a[m] * 0.3 + np.array([255, 170, 90]) * 0.7 * fl
        return to_img(a)


_U = None


def under():
    global _U
    if _U is None:
        _U = Under()
    return _U


def room_bg(warm=1.0):
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    a = np.zeros((H, W, 3), np.float32)
    a[..., 0] = 40; a[..., 1] = 20; a[..., 2] = 16
    a *= (1 - 0.4 * ((x % 110) < 5))[..., None]
    a *= (0.7 + 0.4 * fog_texture(W, H, 79))[..., None]
    fl = y > 1300
    a[np.broadcast_to(fl, (H, W))] *= 0.55
    # woven palm-leaf wall panel and shuttered window
    im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([700, 420, 960, 760], fill=(14, 6, 6, 255))
    d.line([(830, 420), (830, 760)], fill=(70, 36, 26, 255), width=10)
    return im


def mosquito_net(lying=True):
    """A white mosquito net hanging over a sleeping mat; Aunt Srey's shape inside."""
    w, h = 900, 760
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    def mat(d, s):
        d.polygon([(60 * s, 640 * s), (840 * s, 640 * s), (880 * s, 740 * s), (20 * s, 740 * s)], fill=255)
    m = shade(mat, (w, h), (120, 80, 50), 20)
    a = np.asarray(m, np.float32); xx = np.arange(w)[None, :]
    a[..., :3] *= (1 - 0.25 * ((xx % 24) < 4))[..., None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    if lying:
        def aunt(d, s):
            d.ellipse([140 * s, 560 * s, 260 * s, 660 * s], fill=255)
            d.polygon([(250 * s, 600 * s), (700 * s, 590 * s), (760 * s, 660 * s), (250 * s, 670 * s)], fill=255)
            d.ellipse([380 * s, 520 * s, 560 * s, 650 * s], fill=255)     # the baby bump under the blanket
        im.alpha_composite(shade(aunt, (w, h), (90, 50, 60), 30))
    net = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(net)
    d.polygon([(90, 120), (810, 120), (850, 700), (50, 700)], fill=(235, 225, 215, 70))
    for k in range(0, 40):
        x0 = 90 + k * 18; x1 = 50 + k * 20
        d.line([(x0, 120), (x1, 700)], fill=(245, 235, 225, 40), width=2)
    d.line([(90, 120), (810, 120)], fill=(245, 235, 225, 160), width=4)
    im.alpha_composite(net)
    return im


def aunt_sitting():
    """Aunt Srey sitting, hands on her pregnant belly, hair in a bun, a krama over her shoulder."""
    w, h = W, H
    def body(d, s):
        P = lambda *p: [(x * s, y * s) for x, y in p]
        d.polygon(P((470, 900), (610, 900), (720, 1300), (360, 1300)), fill=255)
    def belly(d, s):
        d.ellipse([500 * s, 1010 * s, 690 * s, 1230 * s], fill=255)
    def face(d, s):
        d.ellipse([485 * s, 760 * s, 595 * s, 895 * s], fill=255)
    def hair(d, s):
        d.pieslice([480 * s, 750 * s, 600 * s, 850 * s], 180, 360, fill=255)
        d.ellipse([512 * s, 712 * s, 568 * s, 766 * s], fill=255)
    def hands(d, s):
        d.ellipse([560 * s, 1080 * s, 640 * s, 1130 * s], fill=255)
        d.ellipse([530 * s, 1150 * s, 610 * s, 1200 * s], fill=255)
    def krama(d, s):
        d.polygon([(x * s, y * s) for x, y in ((480, 905), (530, 900), (640, 1110), (600, 1130))], fill=255)
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g.alpha_composite(shade(body, (w, h), (96, 60, 70), 40, rim=(255, 170, 90)))
    g.alpha_composite(shade(belly, (w, h), (106, 66, 76), 50, rim=(255, 170, 90)))
    kr = shade(krama, (w, h), (170, 50, 40), 12, rim=(255, 170, 90))
    a = np.asarray(kr, np.float32); yy, xx = np.mgrid[0:h, 0:w]
    a[..., :3] *= (1 - 0.4 * (((xx // 16) % 2) ^ ((yy // 16) % 2)))[..., None]
    g.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    g.alpha_composite(shade(face, (w, h), (176, 120, 96), 30, rim=(255, 190, 120)))
    g.alpha_composite(shade(hair, (w, h), (26, 18, 18), 20, rim=(255, 190, 120)))
    g.alpha_composite(shade(hands, (w, h), (176, 120, 96), 14, rim=(255, 190, 120)))
    gd = ImageDraw.Draw(g)
    gd.ellipse([508, 812, 526, 826], fill=(30, 15, 15, 255)); gd.ellipse([554, 812, 572, 826], fill=(30, 15, 15, 255))
    gd.line([(522, 862), (540, 856), (558, 862)], fill=(80, 30, 30, 255), width=4)     # serious mouth
    return g


def neighbour(eyes_red=0.0, smile=1.0, scale=1.0):
    """The kind neighbour: upper body, hair in a low bun, krama over the shoulder, a bowl of rice soup."""
    w, h = 900, 1300
    cx = 450
    def body(d, s):
        d.polygon([(x * s, y * s) for x, y in ((cx - 170, 640), (cx + 170, 640), (cx + 230, 1300), (cx - 230, 1300))], fill=255)
        d.ellipse([(cx - 200) * s, 600 * s, (cx - 100) * s, 720 * s], fill=255)
        d.ellipse([(cx + 100) * s, 600 * s, (cx + 200) * s, 720 * s], fill=255)
    def neck(d, s):
        d.rectangle([(cx - 40) * s, 520 * s, (cx + 40) * s, 660 * s], fill=255)
    def face(d, s):
        d.ellipse([(cx - 130) * s, 240 * s, (cx + 130) * s, 580 * s], fill=255)
    def hair(d, s):
        d.pieslice([(cx - 140) * s, 220 * s, (cx + 140) * s, 470 * s], 180, 360, fill=255)
        d.polygon([(x * s, y * s) for x, y in ((cx - 140, 345), (cx - 130, 280), (cx - 20, 262), (cx - 140, 420))], fill=255)
        d.ellipse([(cx + 90) * s, 300 * s, (cx + 190) * s, 400 * s], fill=255)
    def arms(d, s):
        d.ellipse([(cx - 230) * s, 980 * s, (cx + 230) * s, 1110 * s], fill=255)
    def bowl(d, s):
        d.chord([(cx - 150) * s, 880 * s, (cx + 150) * s, 1060 * s], 0, 180, fill=255)
        d.ellipse([(cx - 150) * s, 940 * s, (cx + 150) * s, 990 * s], fill=255)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lt = dict(rim=(255, 120, 80))
    im.alpha_composite(shade(body, (w, h), (90, 70, 110), 60, **lt))
    kr = shade(lambda d, s: d.polygon([(x * s, y * s) for x, y in ((cx - 190, 640), (cx - 110, 630), (cx + 60, 1300), (cx - 60, 1300))], fill=255), (w, h), (180, 50, 44), 20, **lt)
    a = np.asarray(kr, np.float32); yy, xx = np.mgrid[0:h, 0:w]
    a[..., :3] *= (1 - 0.4 * (((xx // 26) % 2) ^ ((yy // 26) % 2)))[..., None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    im.alpha_composite(shade(neck, (w, h), (176, 124, 100), 20, **lt))
    im.alpha_composite(shade(face, (w, h), (186, 132, 106), 60, **lt))
    im.alpha_composite(shade(hair, (w, h), (22, 15, 15), 30, **lt))
    im.alpha_composite(shade(arms, (w, h), (176, 124, 100), 30, **lt))
    im.alpha_composite(shade(bowl, (w, h), (200, 190, 175), 30, **lt))
    d = ImageDraw.Draw(im)
    d.ellipse([cx - 140, 935, cx + 140, 985], fill=(235, 225, 200, 255))                 # the rice soup
    for k in range(5):
        d.ellipse([cx - 80 + k * 38, 950, cx - 66 + k * 38, 962], fill=(255, 250, 235, 255))
    E1, E2 = (cx - 52, 390), (cx + 52, 390)
    if eyes_red < 0.5:
        for ex, ey in (E1, E2):                                                       # smiling closed eyes
            d.arc([ex - 30, ey - 16, ex + 30, ey + 22], 200, 340, fill=(40, 20, 20, 255), width=7)
    else:
        for ex, ey in (E1, E2):
            d.ellipse([ex - 28, ey - 16, ex + 28, ey + 18], fill=(28, 10, 12, 255))
    if smile > 0:
        d.arc([cx - 62, 430, cx + 62, 500], 20, 160, fill=(110, 40, 40, 255), width=8)
    # the thorn scratch on her right cheek (thin, not bloody)
    d.line([(cx + 66, 440), (cx + 96, 462), (cx + 118, 470)], fill=(150, 40, 40, 255), width=4)
    if eyes_red > 0:
        for ex, ey in (E1, E2):
            eye(im, ex, ey, eyes_red, 1.4)
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


def steam(img, t, x, y, k=1.0):
    d = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(d)
    for j in range(3):
        pts = [(x - 60 + j * 60 + 20 * math.sin(t * 2 + i * 0.6 + j), y - i * 22) for i in range(12)]
        dd.line(pts, fill=(255, 245, 235, int(90 * k)), width=10, joint="curve")
    img.alpha_composite(d.filter(ImageFilter.GaussianBlur(5)))


# ============================================================ scenes: PART 1
def make_hook(D, caps):
    V = village()
    hdr = series_header("CAMBODIA", "PART 1")
    t2 = caps[1][1]
    def f(t):
        def back(img, tt, P):
            # the viewer sees a tiny light far over the field before anyone else does
            k = ss(tt, t2 - 1.0, t2)
            if k > 0:
                x = 90 + 60 * ss(tt, t2 - 1, D); y = HZ - 30 + 20 * math.sin(tt * 2)
                img = glow_on(img, gsp(110, (255, 120, 90)), x + P(0.2), y, 1.0 * k * (0.7 + 0.3 * math.sin(tt * 9)))
                img = glow_on(img, gsp(26, (255, 235, 220)), x + P(0.2), y, k)
            return img
        def front(img, tt, P):
            gust = 1.0 if tt > D - 1.2 else 0.0
            ln = laundry(tt, 1.0, True, gust * ss(tt, D - 1.2, D - 1.0))
            img.alpha_composite(ln, (P(1.0) + 60, 640))
            return img
        img = V.frame(t, cam=-60 + 50 * t / D, extra_back=back, extra_front=front)
        fog(img, t, 0.35, HZ + 150, HZ + 520, speed=16)
        bokeh_particles(img, 26, 3, t, color=(255, 110, 80), size=(2, 11), blur=(0, 6), area=(0, 500, W, 1500))
        img.alpha_composite(V.fg, (-200, H - 700 + 80))
        push = 1.0 + 0.05 * t / D + 0.1 * ss(t, t2, t2 + 1.5)
        a = finish(img, t, VIG_H, push=push, cx=640, cy=1000, shake=0.4 if t > D - 1.2 else 0)
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_village(D, caps):
    V = village()
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        def front(img, tt, P):
            # Dara climbing the ladder with a bag of groceries
            u = ss(tt, 0.3, t2 + 1.0)
            h, fx, fy = hero(tt * 0.9 % 1, 0, back=True, scale=0.5)
            x = P(0.6) + 400 + 530 - 50 * u; y = 1280 - 280 * u
            img.alpha_composite(h, (int(x - fx), int(y - fy)))
            return img
        img = V.frame(t, cam=80 * t / D - 40, extra_front=front)
        fog(img, t, 0.3, HZ - 100, HZ + 300, speed=12)
        img.alpha_composite(V.fg, (-260, H - 700 + 90))
        out = to_img(finish(img, t, push=1.03 + 0.05 * t / D, cy=900))
        if t > t3 - 0.2:
            ui = clock_ui("10:02 PM", ss(t, t3 - 0.2, t3 + 0.3))
            out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
        return to_arr(out)
    return f


def make_rule(D, caps):
    bg = room_bg()
    au = aunt_sitting()
    lampg = gsp(420, (255, 170, 80))
    f1 = font(INTER_SB, 46)
    chips = [pill("1. THORNS AROUND THE HOUSE", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("2. LAUNDRY INSIDE", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("3. DOGS BARK AT A LIGHT? STAY IN", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [caps[1][1], caps[1][1] + 1.3, caps[2][1]]
    tb = thorn_branch(5, 600, (60, 34, 24))
    def f(t):
        img = bg.copy()
        img.alpha_composite(tb, (140, 1250))
        img.alpha_composite(au)
        d = ImageDraw.Draw(img)
        d.rectangle([760, 1180, 800, 1260], fill=(70, 46, 30, 255)); d.ellipse([768, 1150, 792, 1182], fill=(255, 210, 130, 255))
        a = to_arr(img)
        fl = 0.8 + 0.2 * math.sin(t * 13) * math.sin(t * 5)
        add_glow(a, lampg, 780, 1160, 1.0 * fl)
        lum = a.mean(2, keepdims=True)                       # faded memory look
        a = a * 0.45 + lum * np.array([1.25, 0.85, 0.6]) * 0.55
        a *= 0.92 + 0.08 * math.sin(t * 40)
        img = to_img(a)
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.15, tt + 0.3)
            if k > 0:
                img.alpha_composite(with_alpha(c, k), (int(W / 2 - c.width / 2), int(250 + i * 120 + 20 * (1 - k))))
        return finish(img, t, vig=VIG_H, push=1.0 + 0.06 * t / D, cy=1000)
    return f


def make_dogs(D, caps):
    V = village()
    t2 = caps[1][1]
    xs = [(80, False), (330, True), (600, False)]
    def f(t):
        if t < t2 - 0.2:
            def front(img, tt, P):
                for i, (x, fl) in enumerate(xs):
                    b = 0.5 + 0.5 * math.sin(tt * 9 + i * 2.1)
                    dg = dog(b, flip=fl)
                    img.alpha_composite(dg, (int(x + P(0.95) + 30 * math.sin(tt * 1.3 + i)), GY + 60 - dg.height))
                return img
            img = V.frame(t, cam=-30 + 30 * t, extra_front=front)
            fog(img, t, 0.3, HZ - 100, HZ + 300)
            img.alpha_composite(V.fg, (-200, H - 700 + 80))
            out = to_img(finish(img, t, vig=VIG_H, push=1.04 + 0.04 * t, cy=1000))
            ui = clock_ui("12:00 AM", 1.0)
            out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
            return to_arr(out)
        # the white sarong, alone on the line, glowing in the red moonlight
        tt = t - t2
        def front2(img, t_, P):
            img.alpha_composite(laundry(t_, 0.8, True), (P(1.0) - 40, 520))
            return img
        img = V.frame(t, cam=-140, extra_front=front2, house=False)
        fog(img, t, 0.35, HZ + 80, HZ + 500)
        return finish(img, t, vig=VIG_H, push=1.15 + 0.12 * ss(t, t2, D), cx=700, cy=1000)
    return f


def make_light(D, caps):
    V = village()
    t2 = caps[1][1]
    rev = t2 + 1.3          # "A woman's head. Glowing."
    def f(t):
        if t < rev:
            u = ss(t, 0, rev)
            def back(img, tt, P):
                x = 300 + 250 * u + 30 * math.sin(tt * 1.7); y = HZ - 60 + 80 * u + 12 * math.sin(tt * 2.3)
                k = 0.7 + 0.3 * math.sin(tt * 7)
                img = glow_on(img, gsp(int(60 + 90 * u), (255, 130, 100)), x, y, 1.1 * k)
                img = glow_on(img, gsp(int(20 + 30 * u), (255, 235, 220)), x, y, 1.0)
                # its reflection in the paddy water
                img = glow_on(img, gsp(int(40 + 60 * u), (255, 90, 70)), x, 2 * HZ - y + 60 + 120 * u, 0.5 * k)
                return img
            img = V.frame(t, cam=0, extra_back=back, house=True)
            fog(img, t, 0.35, HZ - 120, HZ + 260, speed=14)
            img.alpha_composite(V.fg, (-220, H - 700 + 80))
            return finish(img, t, vig=VIG_H, push=1.0 + 0.08 * u, cx=540, cy=1000)
        # reveal: the head over the water, hair streaming, a trail of light, eyes igniting
        tt = t - rev
        def mid(img, t_, P):
            return put_ap(img, 560, 760 + 14 * math.sin(t_ * 1.4), scale=0.85, t=t_, eyes=ss(t_, rev + 0.3, rev + 0.8), tilt=-8, aura=0.6)
        img = V.frame(t, cam=0, extra_mid=mid, house=False)
        fog(img, t, 0.4, HZ - 140, HZ + 300, speed=20)
        fl = 0.6 if 0 <= tt < 0.08 else 0.0
        return finish(img, t, vig=VIG_H, push=1.05 + 0.18 * ss(t, rev, D), cx=560, cy=820, flash=fl, flash_col=(255, 40, 30), shake=0.3 * (1 - ss(t, rev, rev + 0.6)))
    return f


def make_mistake(D, caps):
    V = village()
    U = under()
    t2 = caps[1][1]
    cut = t2 + 1.6          # "...the thorns under the house were gone."
    def f(t):
        if t < t2 - 0.1:
            u = ss(t, 0, t2)
            def front(img, tt, P):
                img.alpha_composite(laundry(tt, 1.0, True), (P(1.0) - 40, 640))
                h, fx, fy = hero((tt * 1.7) % 1, run=1.0, scale=0.8)
                x = 1000 - 520 * u
                img.alpha_composite(h.transpose(Image.FLIP_LEFT_RIGHT), (int(x - (h.width - fx)), int(GY + 160 - fy + 6 * abs(math.sin(tt * 11)))))
                return img
            def back(img, tt, P):
                # the light is already much closer, between the palms (the viewer sees it, Dara doesn't)
                return put_ap(img, 230, 760, scale=0.3, t=tt, eyes=1.0, aura=0.5, glow=0.7)
            img = V.frame(t, cam=60 * t, extra_back=back, extra_front=front)
            fog(img, t, 0.3, HZ + 150, HZ + 500)
            img.alpha_composite(V.fg, (-200 - int(60 * t * 1.6) % 300, H - 700 + 80))
            return finish(img, t, vig=VIG_H, push=1.04, shake=0.2)
        if t < cut:
            # silence: the dogs stand frozen, heads down, eyes glowing, all looking the same way
            def front(img, tt, P):
                for i, (x, fl) in enumerate(((120, False), (420, False), (700, True))):
                    img.alpha_composite(dog(0.0, eyes=ss(tt, t2 + 0.2, t2 + 0.8), flip=fl), (x, GY + 60 - 220))
                return img
            img = V.frame(t, cam=-20, extra_front=front, lamp=0.4)
            fog(img, t, 0.45, HZ - 100, HZ + 400, speed=8)
            return finish(img, t, vig=VIG_H, push=1.06 + 0.05 * ss(t, t2, cut))
        # under the house: drag marks where the thorny branches used to be
        img = U.frame(t, cam=-30 + 30 * (t - cut), thorns=False)
        d = ImageDraw.Draw(img)
        for k in range(5):
            y0 = GY + 60 + k * 40
            d.line([(80 + k * 30, y0), (900 - k * 40, y0 + 30)], fill=(24, 10, 8, 255), width=6)
        img.alpha_composite(U.jar, (-40, GY + 330 - U.jar.height))
        fog(img, t, 0.3, GY - 200, GY + 300, col=(120, 30, 30))
        return finish(img, t, vig=VIG_H, push=1.05 + 0.08 * ss(t, cut, D), cy=1250)
    return f


def make_cliff(D, caps):
    U = under()
    t2, t3 = caps[1][1], caps[2][1]
    jt = caps[2][2] + 0.15    # the jump scare right after "Would you look up?"
    def f(t):
        if t >= jt:
            # JUMP SCARE: her face fills the screen, mouth slightly open, then black
            img = Image.new("RGBA", (W, H), (8, 2, 3, 255))
            img = put_ap(img, 540, 900, scale=2.6, t=t, eyes=1.0, tilt=-14, trail=0.0, aura=0.8, mouth=0.25, glow=1.0)
            fl = 0.85 if t < jt + 0.08 else 0.0
            a = finish(img, t, vig=VIG_H, push=1.0 + 0.6 * ss(t, jt, jt + 0.25), cy=860, shake=1.0, flash=fl, flash_col=(255, 30, 20))
            if t > D - 0.45:
                a *= 0.0
            return a
        # light coming down from above: it moves across the field outside, then hovers over the jar
        lk = ss(t, t2 - 1.5, t2 + 0.5)
        lx = 900 - 380 * lk
        ly = 80 + 140 * lk
        img = U.frame(t, cam=0, thorns=False, slit_k=0.6)
        h, fx, fy = hero_crouch(1.25, look_up=ss(t, t3, t3 + 0.6))
        img.alpha_composite(h, (int(360 - fx), int(GY + 470 - fy)))
        img.alpha_composite(U.jar, (-160, GY + 520 - U.jar.height))
        a = to_arr(img)
        k = 0.4 + 0.8 * lk
        fl = k * (0.85 + 0.15 * math.sin(t * 8))
        add_glow(a, gsp(520, (255, 70, 55)), lx, ly, 0.9 * fl)
        add_glow(a, gsp(180, (255, 200, 180)), lx, ly, 0.5 * fl)
        # breath held: tiny camera breathing + slow tilt up at the end
        push = 1.05 + 0.04 * math.sin(t * 1.3) + 0.12 * ss(t, t3, jt)
        cy = 1150 - 450 * ss(t, t3 + 0.3, jt)
        return finish(to_img(a), t, vig=VIG_H, push=push, cx=420, cy=cy)
    return f


# ============================================================ scenes: PART 2
def make_recap(D, caps):
    U = under()
    hdr = series_header("CAMBODIA", "PART 2")
    def f(t):
        img = U.frame(t, cam=0, thorns=False, slit_k=0.5)
        h, fx, fy = hero_crouch(1.1, look_up=0.0)
        img.alpha_composite(h, (int(380 - fx), int(GY + 470 - fy)))
        img.alpha_composite(U.jar, (-160, GY + 520 - U.jar.height))
        img = put_ap(img, 450, 820 + 10 * math.sin(t * 1.2), scale=0.75, t=t, eyes=1.0, tilt=12, aura=0.6, trail=0.9)
        fog(img, t, 0.25, GY - 200, GY + 300, col=(120, 30, 30))
        out = to_img(finish(img, t, vig=VIG_H, push=1.02 + 0.06 * t / D, cy=1000))
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_whisper(D, caps):
    U = under()
    t2 = caps[1][1]
    def f(t):
        img = U.frame(t, cam=0, thorns=False, slit_k=0.4)
        h, fx, fy = hero_crouch(2.3, look_up=0.0)
        img.alpha_composite(h, (int(560 - fx), int(1980 - fy)))
        # strands of her hair sliding down into frame and touching Dara's hair
        d = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(d)
        L = 300 + 500 * ss(t, 0.2, t2)
        for i in range(9):
            x0 = 380 + i * 40
            pts = [(x0 + 30 * math.sin(t * 1.5 + i + y / 120), y) for y in np.linspace(-20, L + 30 * math.sin(i), 20)]
            dd.line(pts, fill=(14, 9, 10, 255), width=12, joint="curve")
        img.alpha_composite(d)
        if t > t2 - 0.4:
            # her face slides in upside-down-tilted from the top of the frame
            k = ss(t, t2 - 0.4, t2 + 0.9)
            img = put_ap(img, 560, -260 + 520 * k, scale=1.1, t=t, eyes=k, tilt=168, trail=0.0, aura=0.6, glow=0.8)
        else:
            img = glow_on(img, gsp(400, (255, 70, 55)), 560, -60, 0.8)
        return finish(img, t, vig=VIG_H, push=1.02 + 0.06 * t / D, cy=900)
    return f


def make_escape(D, caps):
    U = under()
    t2, t3 = caps[1][1], caps[2][1]
    br = thorn_branch(9, 700, (120, 78, 50))
    def f(t):
        if t < t3 - 0.2:
            img = U.frame(t, cam=0, thorns=False, slit_k=0.6)
            sw = ss(t, t2 - 0.9, t2 - 0.4)                  # the swing
            back = ss(t, t2 - 0.4, t3 - 0.2)               # the head flies away
            hx = 560 - 80 * sw + 400 * back; hy = 640 - 520 * back
            img = put_ap(img, hx, hy, scale=0.95 * (1 - 0.6 * back), t=t, eyes=1.0, tilt=-20 * sw, aura=0.6, mouth=0.9 * ss(t, t2 - 0.45, t2), flip_trail=back > 0)
            h, fx, fy = hero(0.25, run=0.6, scale=1.1)
            img.alpha_composite(h, (int(300 - fx), int(1860 - fy)))
            b = br.rotate(-70 + 110 * sw, resample=Image.BICUBIC, expand=True, center=(40, br.height / 2))
            img.alpha_composite(b, (int(330 - b.width / 2 + 80), int(1050 - b.height / 2 - 60 * sw)))
            fl = 0.7 if t2 - 0.45 <= t < t2 - 0.37 else 0.0
            return finish(img, t, vig=VIG_H, push=1.04, cy=1000, shake=0.8 * ss(t, t2 - 0.45, t2 - 0.3) * (1 - ss(t, t2, t2 + 0.6)), flash=fl, flash_col=(255, 40, 30))
        # upstairs: thorns around Aunt Srey's mosquito net, lamp flickering
        img = room_bg()
        net = mosquito_net(True)
        img.alpha_composite(net, (90, 760))
        u = ss(t, t3, D - 0.4)
        for i in range(4):
            if u > i / 4:
                tb = thorn_branch(20 + i, 420, (130, 86, 56))
                img.alpha_composite(tb, (60 + (i % 2) * 520, 1440 + (i // 2) * 60))
        h, fx, fy = hero(0, 0, scale=0.9)
        img.alpha_composite(h, (int(880 - fx), int(1560 - fy)))
        a = to_arr(img)
        add_glow(a, gsp(360, (255, 170, 80)), 160, 1300, 0.9 * (0.85 + 0.15 * math.sin(t * 13)))
        return finish(to_img(a), t, vig=VIG_H, push=1.02 + 0.06 * (t - t3), cy=1150)
    return f


def make_dawn(D, caps):
    V = village()
    t2 = caps[1][1]
    def f(t):
        k = ss(t, t2 - 0.3, t2 + 2.0)                        # night -> sunrise
        img = V.frame(t, cam=0, lamp=1 - k)
        a = to_arr(img)
        y = np.linspace(0, 1, H)[:, None, None]
        dawn = (np.array([90, 50, 90]) * (1 - y) + np.array([255, 150, 100]) * y)
        sky_mask = (np.arange(H) < HZ)[:, None, None]
        a = np.where(sky_mask, a * (1 - 0.75 * k) + dawn * 0.75 * k, a * (1 + 0.8 * k))
        add_glow(a, gsp(380, (255, 190, 120)), 250, HZ - 10, 1.2 * k)
        img = to_img(a)
        if t < t2 + 1.4:
            # the light circling the house all night
            ang = t * 2.2
            x = 760 + 330 * math.cos(ang); y = 600 + 120 * math.sin(ang)
            img = put_ap(img, x, y, scale=0.32, t=t, eyes=1.0, aura=0.5, glow=0.8)
        else:
            # racing back to the forest
            u = ss(t, t2 + 1.4, t2 + 2.6)
            img = put_ap(img, 760 - 760 * u, 600 + 280 * u, scale=0.32 * (1 - 0.6 * u), t=t, eyes=1.0, aura=0.5, glow=0.8, flip_trail=True)
        if t > t2 + 1.0:
            d = ImageDraw.Draw(img)
            for i in range(5):
                bx = (200 + i * 150 + t * 70) % W; by = 420 + 40 * math.sin(i + t)
                d.line([(bx - 18, by), (bx, by + 8), (bx + 18, by)], fill=(30, 20, 30, 255), width=4)
        fog(img, t, 0.3, HZ - 100, HZ + 300, col=(255, 170, 140) if k > 0.5 else (140, 40, 40))
        out = to_img(finish(img, t, vig=VIG, push=1.04 - 0.03 * t / D))
        mins = 120 + (460 - 120) * ss(t, 0.2, t2 + 0.2)      # 12:00 AM -> 5:40 AM
        ui = clock_ui(fmt_clock(mins), 1.0)
        out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
        return to_arr(out)
    return f


def make_twist(D, caps):
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.0
    V = village()
    def doorway(t):
        y = np.linspace(0, 1, H)[:, None, None]
        sky = np.broadcast_to(np.array([255, 190, 140]) * (1 - y) + np.array([210, 120, 90]) * y, (H, W, 3))
        img = to_img(sky)
        for i, (pl, x) in enumerate(zip(V.palms, (-120, 260, 700))):
            sil = Image.new("RGBA", pl.size, (110, 60, 50, 0)); sil.putalpha(pl.split()[3])
            img.alpha_composite(sil, (x, 1150 - pl.height + 200))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 170, H], fill=(60, 34, 26, 255)); d.rectangle([910, 0, W, H], fill=(60, 34, 26, 255))
        d.rectangle([0, 0, W, 160], fill=(50, 28, 22, 255))
        return img
    def f(t):
        img = doorway(t)
        if t >= jt:
            nb = neighbour(eyes_red=1.0, smile=0.0)
        else:
            nb = neighbour(eyes_red=0.0, smile=1.0)
        img.alpha_composite(nb, (90, 620))
        steam(img, t, 540, 1540, 1.0 - ss(t, t2, t2 + 1))
        if t < t2:
            return finish(img, t, vig=VIG, push=1.0 + 0.05 * t / t2, cy=1100)
        # push in to her cheek ... the scratch
        z = 1.0 + 1.3 * ss(t, t2, t3 + 0.6)
        if t >= jt:
            fl = 0.85 if t < jt + 0.08 else 0.0
            return finish(img, t, vig=VIG_H, push=z + 0.7 * ss(t, jt, jt + 0.2), cx=540, cy=1010, shake=1.0, flash=fl, flash_col=(255, 30, 20))
        return finish(img, t, vig=VIG_H, push=z, cx=600 + 60 * ss(t, t2, t3 + 0.6), cy=1060)
    return f


def make_explain(D, caps):
    V = village()
    title = text_img("THE AP", font(LORA, 130, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("Cambodia's floating head  ·  Krasue in Thailand", font(INTER_SB, 40), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("A normal woman by day", pf, fill=(110, 20, 24, 235), h=80),
             pill("At night her head flies off to hunt", pf, fill=(110, 20, 24, 235), h=80),
             pill("Afraid of thorns and guard dogs", pf, fill=(110, 20, 24, 235), h=80),
             pill("Bring your laundry in at night", pf, fill=(110, 20, 24, 235), h=80)]
    ts = [caps[1][1], caps[1][1] + 1.6, caps[2][1], caps[2][1] + 2.0]
    def f(t):
        img = V.frame(t, cam=-30 + 20 * t / D, house=True)
        img = put_ap(img, 540, 1100 + 14 * math.sin(t * 1.3), scale=0.62, t=t, eyes=1.0, aura=0.5)
        fog(img, t, 0.35, HZ - 100, HZ + 500)
        a = finish(img, t, vig=VIG_H, push=1.0)
        out = to_img(a * 0.8)
        fw = flag_wave(t, 150)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 70))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 170))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 340))
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.2, tt + 0.3)
            if k > 0:
                out.alpha_composite(with_alpha(c, k), (int(W / 2 - c.width / 2), int(440 + i * 96 + 14 * (1 - k))))
        return to_arr(out)
    return f


def make_outro(D, caps):
    V = village()
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("have survived?", font(LORA, 100, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Look up", (120, 25, 25, 235)), ("Stay still", (60, 40, 40, 235)), ("Grab the thorns", (140, 70, 20, 235)), ("RUN!", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    def f(t):
        img = V.frame(t, cam=0)
        img = put_ap(img, 260 + 20 * math.sin(t * 0.8), 980, scale=0.3, t=t, eyes=1.0, aura=0.5, glow=0.7)
        fog(img, t, 0.4, HZ - 200, HZ + 600)
        a = finish(img, t, vig=VIG_H) * 0.55
        out = to_img(a)
        fw = flag_wave(t, 150)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 140))
        out.alpha_composite(with_alpha(q, ss(t, 0, 0.6)), (int(W / 2 - q.width / 2), 300))
        out.alpha_composite(with_alpha(q2, ss(t, 0.2, 0.8)), (int(W / 2 - q2.width / 2), 420))
        yy, k = 640, 0
        for row in (chips[:2], chips[2:]):
            tot = sum(c.width for c in row) + 24
            x = W / 2 - tot / 2
            for c in row:
                tt = 0.5 + 0.2 * k
                out.alpha_composite(with_alpha(c, ss(t, tt, tt + 0.4)), (int(x), int(yy + 12 * (1 - ss(t, tt, tt + 0.4)))))
                x += c.width + 24; k += 1
            yy += 120
        out.alpha_composite(with_alpha(cm, ss(t, caps[1][1], caps[1][1] + 0.4) * (0.85 + 0.15 * math.sin(t * 6))), (int(W / 2 - cm.width / 2), 1000))
        out.alpha_composite(with_alpha(fol, ss(t, caps[1][1] + 0.4, caps[1][1] + 0.9)), (int(W / 2 - fol.width / 2), 1100))
        return to_arr(out) * (1 - ease((t - (D - 0.6)) / 0.6))
    return f
