"""Ep10 India / the Chudail - 2.1D survival version.
New world: a Rajasthan desert road under a huge blood-red moon: rippled dunes, a hill fort with chhatri domes far
away, twisted khejri trees, an old peepal tree with red and yellow threads and a roadside shrine with a diya,
a red scooter with a dying headlight; an old stepwell (baori) with zigzag stairs; Dadi's lamplit mud-walled room
with a charpai; a small white temple with a brass bell at grey dawn; a terracotta village doorway with a marigold toran.
Ghost: the Chudail - too tall, a red sari with a gold border over her head, black hair over the face, glowing eyes,
silver anklets and BACKWARD feet (toes point behind her), no gore.
Each make_<id>(D, caps) returns f(t) -> float RGB array (H, W, 3)."""
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

HZ = 1080            # desert horizon
MOON = (770, 430)
VIG = vignette(0.85)
VIG_H = vignette(1.05)
GR = [np.random.default_rng(i).normal(0, 5, (H, W, 1)).astype(np.float32) for i in range(6)]
FOGT = fog_texture(W + 700, H, 101)
SKIN = (150, 96, 70)          # Arjun
PALE = (222, 212, 204)        # the Chudail's skin
SAREE = (150, 14, 22)
GOLDB = (190, 140, 50)


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


def fog(img, t, k, y0, y1, speed=18, col=(150, 50, 40), off=0):
    o = int((t * speed + off) % 700)
    f = FOGT[:, o:o + W]
    yy = np.arange(H)[:, None]
    band = np.clip(np.minimum((yy - y0) / 150, (y1 - yy) / 150), 0, 1)
    a = f * band * k
    lay = np.dstack([np.full((H, W), col[0], np.float32), np.full((H, W), col[1], np.float32), np.full((H, W), col[2], np.float32), a * 255]).astype(np.uint8)
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


# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """India: saffron / white / green, navy Ashoka Chakra (24 spokes). Drawn at 3x then reduced."""
    global _FLAG
    if _FLAG is None:
        w, h, s = 300, 200, 3
        im = Image.new("RGBA", (w * s, h * s), (255, 153, 51, 255)); d = ImageDraw.Draw(im)
        d.rectangle([0, h * s / 3, w * s, h * s * 2 / 3], fill=(255, 255, 255, 255))
        d.rectangle([0, h * s * 2 / 3, w * s, h * s], fill=(19, 136, 8, 255))
        cx, cy, r = w * s / 2, h * s / 2, h * s / 6 * 0.92
        navy = (0, 0, 128, 255)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=navy, width=int(5 * s / 3 * 2))
        for k in range(24):
            a = 2 * math.pi * k / 24
            d.line([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], fill=navy, width=4)
        d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18], fill=navy)
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
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 40))


def fuel_ui(level, t, km="12 KM", k=1.0):
    """The ticking clock: a fuel gauge with 5 bars (the last one blinks red) + distance to the village."""
    f1 = font(INTER_SB, 40); f2 = font(INTER_M, 30)
    w, h = 600, 108
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(0, 0, 0, int(180 * k)), outline=(255, 70, 50, int(200 * k)), width=3)
    blink = math.sin(t * 9) > -0.2
    ic = (255, 70, 50, int(255 * k)) if level <= 0.2 and blink else (255, 235, 220, int(230 * k))
    d.rounded_rectangle([34, 30, 70, 82], 5, fill=ic)                 # fuel pump icon
    d.rectangle([42, 38, 62, 52], fill=(0, 0, 0, int(200 * k)))
    d.line([(70, 44), (84, 52), (84, 76), (92, 76)], fill=ic, width=5)
    n = int(math.ceil(level * 5 - 1e-6))
    for i in range(5):
        x0 = 112 + i * 42
        on = i < n
        col = (255, 245, 235, int(240 * k)) if on else (90, 70, 70, int(160 * k))
        if on and n == 1:
            col = (255, 60, 40, int(255 * k * (1 if blink else 0.25)))
        d.rounded_rectangle([x0, 34, x0 + 30, 76], 6, fill=col)
    if n == 0:
        d.text((214, h / 2), "EMPTY", font=f1, fill=(255, 70, 50, int(255 * k * (1 if blink else 0.4))), anchor="mm")
    d.line([(338, 22), (338, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    d.text((470, h / 2 - 17), "VILLAGE", font=f2, fill=(255, 190, 140, int(255 * k)), anchor="mm")
    d.text((470, h / 2 + 20), km, font=f1, fill=(255, 245, 235, int(255 * k)), anchor="mm")
    return im


# ============================================================ characters: Arjun
_HC = {}


def arjun(phase=0.0, run=0.0, back=False, scale=1.0):
    """Arjun: short black hair, maroon checked shirt, dark jeans, sandals. Returns (RGBA, feet_x, feet_y)."""
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
            hx, hy = cx + lean * 0.3 + sg * 22, 420
            kx, ky = hx + math.sin(a) * 140, hy + math.cos(a) * 180
            fx, fy = kx + math.sin(a - 0.35 * run) * 120, ky + 170
            d.line([(hx * s, hy * s), (kx * s, ky * s), (fx * s, fy * s)], fill=255, width=int(40 * s), joint="curve")

    def shoes(d, s):
        for sg in (-1, 1):
            a = sg * sw * 0.6
            hx, hy = cx + lean * 0.3 + sg * 22, 420
            kx, ky = hx + math.sin(a) * 140, hy + math.cos(a) * 180
            fx, fy = kx + math.sin(a - 0.35 * run) * 120, ky + 170
            d.ellipse([(fx - 30) * s, (fy - 10) * s, (fx + 36) * s, (fy + 16) * s], fill=255)

    def torso(d, s):
        L = lean
        d.polygon(P_((cx - 78 + L, 195), (cx + 78 + L, 195), (cx + 70 + L * .6, 450), (cx - 70 + L * .6, 450), s=s), fill=255)
        d.ellipse([(cx - 84 + L) * s, 182 * s, (cx - 40 + L) * s, 240 * s], fill=255)
        d.ellipse([(cx + 40 + L) * s, 182 * s, (cx + 84 + L) * s, 240 * s], fill=255)

    def arms(d, s):
        L = lean
        for sg in (-1, 1):
            sx, sy = cx + sg * 68 + L, 212
            a = -sg * sw * 0.9
            ex, ey = sx + math.sin(a) * 90 + sg * 10, sy + math.cos(a) * 105
            b = a - 0.9 * run * sg
            hx, hy = ex + math.sin(b) * 92, ey + math.cos(b) * 84 - 40 * run
            d.line([(sx * s, sy * s), (ex * s, ey * s), (hx * s, hy * s)], fill=255, width=int(26 * s), joint="curve")
            d.ellipse([(hx - 15) * s, (hy - 15) * s, (hx + 15) * s, (hy + 15) * s], fill=255)

    def head(d, s):
        L = lean * 1.2
        d.rectangle([(cx - 19 + L) * s, 140 * s, (cx + 19 + L) * s, 200 * s], fill=255)
        d.ellipse([(cx - 50 + L) * s, 40 * s, (cx + 50 + L) * s, 168 * s], fill=255)

    def hair(d, s):
        L = lean * 1.2
        d.pieslice([(cx - 55 + L) * s, 28 * s, (cx + 55 + L) * s, 140 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 55 + L, 86), (cx - 50 + L, 52), (cx + 52 + L, 52), (cx + 56 + L, 90), (cx + 20 + L, 70), (cx - 30 + L, 74), s=s), fill=255)
        if back:
            d.ellipse([(cx - 52 + L) * s, 34 * s, (cx + 52 + L) * s, 150 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), (40, 42, 60), 18))
    img.alpha_composite(shade(shoes, (w, h), (40, 24, 18), 8))
    sh = shade(torso, (w, h), (120, 34, 40), 38)
    sh = texmul(sh, lambda xx, yy: 1 - 0.22 * (((xx // 20) % 2) ^ ((yy // 20) % 2)) - 0.12 * ((xx % 40) < 4))
    img.alpha_composite(sh)
    img.alpha_composite(shade(arms, (w, h), (120, 34, 40), 11))
    img.alpha_composite(shade(head, (w, h), SKIN, 28))
    img.alpha_composite(shade(hair, (w, h), (16, 11, 11), 16))
    d = ImageDraw.Draw(img)
    L = lean * 1.2
    if not back:
        for sg in (-1, 1):
            d.ellipse([cx + sg * 20 - 9 + L, 96, cx + sg * 20 + 9 + L, 112], fill=(240, 236, 230, 255))
            d.ellipse([cx + sg * 20 - 4 + L, 99, cx + sg * 20 + 4 + L, 109], fill=(15, 10, 10, 255))
            d.line([(cx + sg * 20 - 12 + L, 86), (cx + sg * 20 + 12 + L, 84 - sg * 2)], fill=(20, 12, 12, 255), width=5)
        d.ellipse([cx - 7 + L, 136, cx + 7 + L, 146], fill=(60, 26, 26, 255))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 776 * scale)
    _HC[q] = out
    return out


_CR = {}


def arjun_crouch(scale=1.0, look_up=0.0):
    """Arjun crouched, knees up, hands over his mouth. Feet at bottom-centre."""
    key = (round(scale, 2), round(look_up, 1))
    if key in _CR:
        return _CR[key]
    w, h = 460, 560
    cx = 230
    up = look_up * 26

    def body(d, s):
        d.polygon(P_((150, 230), (300, 230), (330, 420), (330, 520), (120, 520), (110, 400), s=s), fill=255)

    def knees(d, s):
        d.ellipse([200 * s, 250 * s, 350 * s, 390 * s], fill=255)
        d.polygon(P_((240, 330), (340, 320), (330, 530), (270, 530), s=s), fill=255)

    def head(d, s):
        d.ellipse([(cx - 48) * s, (66 - up) * s, (cx + 48) * s, (186 - up) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 53) * s, (56 - up) * s, (cx + 53) * s, (160 - up) * s], 180, 360, fill=255)
        d.polygon(P_((cx - 53, 108 - up), (cx - 50, 80 - up), (cx + 50, 80 - up), (cx + 53, 108 - up), (cx + 10, 92 - up), s=s), fill=255)

    def hands(d, s):
        d.ellipse([(cx - 32) * s, (140 - up) * s, (cx + 26) * s, (180 - up) * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = shade(body, (w, h), (110, 32, 38), 40)
    img.alpha_composite(texmul(sh, lambda xx, yy: 1 - 0.22 * (((xx // 18) % 2) ^ ((yy // 18) % 2))))
    img.alpha_composite(shade(knees, (w, h), (40, 42, 60), 30))
    img.alpha_composite(shade(lambda d, s: d.line([(170 * s, 250 * s), (250 * s, 340 * s), (330 * s, 330 * s)], fill=255, width=int(26 * s), joint="curve"), (w, h), (110, 32, 38), 10))
    img.alpha_composite(shade(head, (w, h), SKIN, 26))
    img.alpha_composite(shade(hair, (w, h), (16, 11, 11), 14))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ey = 114 - up - (6 if look_up > 0.5 else 0)
        d.ellipse([cx + sg * 19 - 10, ey, cx + sg * 19 + 10, ey + 17], fill=(240, 236, 230, 255))
        d.ellipse([cx + sg * 19 - 4, ey + (0 if look_up > 0.5 else 4), cx + sg * 19 + 4, ey + (8 if look_up > 0.5 else 12)], fill=(15, 10, 10, 255))
    img.alpha_composite(shade(hands, (w, h), SKIN, 10))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 530 * scale)
    _CR[key] = out
    return out


_FACE = {}


def arjun_face(mouth=0.0):
    """Close-up: Arjun's head and shoulders, eyes wide, lantern light from the right."""
    key = round(mouth, 1)
    if key in _FACE:
        return _FACE[key]
    w, h = 1080, 1300
    cx = 500

    def body(d, s):
        d.polygon(P_((cx - 360, 1300), (cx - 300, 1000), (cx - 120, 930), (cx + 120, 930), (cx + 300, 1000), (cx + 360, 1300), s=s), fill=255)

    def neck(d, s):
        d.rectangle([(cx - 70) * s, 760 * s, (cx + 70) * s, 960 * s], fill=255)

    def head(d, s):
        d.ellipse([(cx - 190) * s, 300 * s, (cx + 190) * s, 840 * s], fill=255)
        d.ellipse([(cx - 215) * s, 540 * s, (cx - 160) * s, 640 * s], fill=255)
        d.ellipse([(cx + 160) * s, 540 * s, (cx + 215) * s, 640 * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 205) * s, 270 * s, (cx + 205) * s, 700 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 205, 485), (cx - 195, 400), (cx + 195, 400), (cx + 205, 485), (cx + 60, 420), (cx - 80, 440), s=s), fill=255)

    lt = dict(rim=(255, 150, 80), rim_dir=(1.0, -0.1))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sh = shade(body, (w, h), (110, 32, 38), 90, **lt)
    img.alpha_composite(texmul(sh, lambda xx, yy: 1 - 0.22 * (((xx // 40) % 2) ^ ((yy // 40) % 2))))
    img.alpha_composite(shade(neck, (w, h), SKIN, 30, **lt))
    img.alpha_composite(shade(head, (w, h), SKIN, 110, **lt))
    img.alpha_composite(shade(hair, (w, h), (16, 11, 11), 40, **lt))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ex, ey = cx + sg * 78, 600
        d.ellipse([ex - 40, ey - 26, ex + 40, ey + 30], fill=(240, 234, 226, 255))
        d.ellipse([ex - 13, ey - 10, ex + 13, ey + 16], fill=(14, 9, 9, 255))
        d.ellipse([ex - 3 + 6, ey - 6, ex + 4 + 6, ey + 1], fill=(255, 230, 200, 255))
        d.line([(ex - 46, ey - 62 - 8), (ex + 40, ey - 70 - sg * 8)], fill=(18, 10, 10, 255), width=14)
    d.polygon([(cx - 8, 610), (cx + 26, 700), (cx - 18, 706)], fill=(126, 78, 56, 255))
    mo = mouth
    d.ellipse([cx - 34, 750 - 4 * mo, cx + 34, 762 + 40 * mo], fill=(52, 18, 18, 255))
    out = img
    _FACE[key] = out
    return out


_RIDE = {}


def scooter_rider(lamp=1.0, rider=True, bob=0):
    """Side view (facing right): a small red scooter with Arjun riding. Returns (RGBA, headlamp_xy, wheel_y)."""
    key = (round(lamp, 1), rider, bob)
    if key in _RIDE:
        return _RIDE[key]
    w, h = 820, 980
    oy = 500

    def wheels(d, s):
        for x in (170, 620):
            d.ellipse([(x - 66) * s, (oy + 334) * s, (x + 66) * s, (oy + 466) * s], fill=255)

    def body(d, s):
        d.ellipse([60 * s, (oy + 220) * s, 380 * s, (oy + 420) * s], fill=255)                  # rear side panel
        d.rectangle([300 * s, (oy + 360) * s, 540 * s, (oy + 400) * s], fill=255)              # floorboard
        d.polygon(P_((520, oy + 400), (560, oy + 170), (630, oy + 160), (650, oy + 330), (600, oy + 400), s=s), fill=255)
        d.pieslice([540 * s, (oy + 320) * s, 700 * s, (oy + 470) * s], 180, 330, fill=255)    # front mudguard
        d.line([(590 * s, (oy + 165) * s), (600 * s, (oy + 100) * s)], fill=255, width=int(16 * s))
        d.line([(555 * s, (oy + 100) * s), (640 * s, (oy + 92) * s)], fill=255, width=int(14 * s))

    def seat(d, s):
        d.rounded_rectangle([110 * s, (oy + 196) * s, 360 * s, (oy + 236) * s], 18 * s, fill=255)

    def rider_legs(d, s):
        d.line([(250 * s, (oy + 190 + bob) * s), (420 * s, (oy + 170 + bob) * s), (440 * s, (oy + 350) * s)], fill=255, width=int(44 * s), joint="curve")

    def rider_up(d, s):
        b = bob
        d.polygon(P_((190, oy + 205 + b), (310, oy + 205 + b), (320, oy - 60 + b), (200, oy - 70 + b), s=s), fill=255)
        d.ellipse([190 * s, (oy - 100 + b) * s, 330 * s, (oy - 20 + b) * s], fill=255)

    def rider_arm(d, s):
        b = bob
        d.line([(270 * s, (oy - 40 + b) * s), (400 * s, (oy + 40 + b) * s), (560 * s, (oy + 100) * s)], fill=255, width=int(28 * s), joint="curve")

    def rider_head(d, s):
        b = bob
        d.rectangle([238 * s, (oy - 140 + b) * s, 278 * s, (oy - 70 + b) * s], fill=255)
        d.ellipse([200 * s, (oy - 260 + b) * s, 310 * s, (oy - 125 + b) * s], fill=255)

    def rider_hair(d, s):
        b = bob
        d.pieslice([194 * s, (oy - 272 + b) * s, 316 * s, (oy - 150 + b) * s], 180, 360, fill=255)
        d.polygon(P_((194, oy - 212 + b), (186, oy - 196 + b), (230, oy - 230 + b), (316, oy - 212 + b), (300, oy - 250 + b), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(wheels, (w, h), (16, 10, 10), 20))
    if rider:
        img.alpha_composite(shade(rider_up, (w, h), (110, 32, 38), 40))
        img.alpha_composite(shade(rider_legs, (w, h), (40, 42, 60), 18))
    img.alpha_composite(shade(body, (w, h), (140, 20, 26), 50, rim_strength=1.1))
    img.alpha_composite(shade(seat, (w, h), (20, 14, 14), 12))
    if rider:
        img.alpha_composite(shade(rider_arm, (w, h), (110, 32, 38), 12))
        img.alpha_composite(shade(rider_head, (w, h), SKIN, 30))
        img.alpha_composite(shade(rider_hair, (w, h), (16, 11, 11), 16))
        d = ImageDraw.Draw(img)
        d.ellipse([282, oy - 206 + bob, 296, oy - 192 + bob], fill=(240, 236, 230, 255))
        d.ellipse([288, oy - 203 + bob, 295, oy - 195 + bob], fill=(14, 9, 9, 255))
    d = ImageDraw.Draw(img)
    for x in (170, 620):
        d.ellipse([x - 26, oy + 374, x + 26, oy + 426], fill=(90, 80, 80, 255))
    lc = (int(80 + 175 * lamp), int(50 + 190 * lamp), int(40 + 150 * lamp), 255)
    d.ellipse([614, oy + 128, 654, oy + 176], fill=lc)
    d.rectangle([20, oy + 290, 50, oy + 314], fill=(int(90 + 120 * lamp), 20, 20, 255))
    out = (img, (636, oy + 152), oy + 466)
    _RIDE[key] = out
    return out


def beam(img, x, y, k, length=900, spread=220, direction=1):
    """Headlight cone (additive) from (x, y) in direction +x (1) or -x (-1)."""
    if k <= 0.01:
        return img
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(x, y - 12), (x + direction * length, y - spread * 0.55), (x + direction * length, y + spread)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(26))
    a = to_arr(img)
    xx = np.arange(W)[None, :]
    fall = np.clip(1 - np.abs(xx - x) / length, 0, 1) ** 0.8
    a += (np.asarray(m, np.float32) / 255 * fall)[..., None] * np.array([255, 200, 150]) * 0.5 * k
    add_glow(a, gsp(90, (255, 230, 190)), x, y, 1.0 * k)
    return to_img(a)


# ============================================================ characters: the Chudail
_CH = {}


def chudail(tilt=0.0, lantern=True, lamp=1.0, arm_up=0.0):
    """Full figure, three-quarter view facing right, ~1450 px tall: red sari with gold border draped over her head,
    black hair falling over her face, very long pale arms, a hurricane lantern, silver anklets, BACKWARD feet
    (toes point to the left, behind her). Returns (RGBA, eye1, eye2, lantern_xy, feet_y)."""
    key = (round(tilt, 2), lantern, round(lamp, 1), round(arm_up, 1))
    if key in _CH:
        return _CH[key]
    w, h = 760, 1560
    cx = 360
    hy = 190                       # head centre
    ang = math.radians(tilt)

    def R(*pts):
        return rot(pts, ang, cx, hy + 120)

    def hair_back(d, s):
        d.polygon(P_(*R((cx - 110, hy - 40), (cx + 60, hy - 120), (cx + 40, hy + 120)), (cx - 60, 900), (cx - 190, 980), (cx - 150, 500), s=s), fill=255)

    def sari(d, s):
        d.polygon(P_((cx - 120, 330), (cx + 110, 320), (cx + 150, 900), (cx + 190, 1400), (cx - 170, 1410), (cx - 140, 900), s=s), fill=255)

    def pallu(d, s):   # the end of the sari over her head and down her back
        d.polygon(P_(*R((cx - 128, hy - 30), (cx - 70, hy - 128), (cx + 60, hy - 132), (cx + 108, hy - 40), (cx + 90, hy + 60)),
                     (cx + 120, 360), (cx + 40, 700), (cx - 150, 1180), (cx - 200, 1100), (cx - 150, 400), s=s), fill=255)

    def face(d, s):
        d.ellipse([x * s for x in (cx - 62, hy - 86, cx + 74, hy + 96)], fill=255) if tilt == 0 else \
            d.polygon(P_(*R(*[(cx + 6 + 68 * math.cos(a), hy + 5 + 91 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 28)]), s=s), fill=255)

    def hair_front(d, s):
        d.polygon(P_(*R((cx - 90, hy - 90), (cx + 80, hy - 92), (cx + 70, hy + 10), (cx + 52, hy + 220), (cx + 20, hy + 360),
                        (cx + 30, hy + 120), (cx + 18, hy - 20), (cx - 10, hy - 10), (cx - 30, hy + 260), (cx - 80, hy + 380), (cx - 70, hy + 120)), s=s), fill=255)

    def arm(d, s):
        sx, sy = cx + 70, 380
        ex, ey = sx + 60, 640 - 120 * arm_up
        hx2, hy2 = ex + 120, 800 - 260 * arm_up
        d.line([(sx * s, sy * s), (ex * s, ey * s), (hx2 * s, hy2 * s)], fill=255, width=int(30 * s), joint="curve")
        for k in range(4):   # long fingers
            a = 1.2 + 0.18 * k - 1.2 * arm_up
            d.line([(hx2 * s, hy2 * s), ((hx2 + math.cos(a) * 70) * s, (hy2 + math.sin(a) * 70) * s)], fill=255, width=int(9 * s))

    def feet(d, s):
        # backward feet: heel at the front (right), toes behind (left)
        for fx, lift in ((cx - 70, 0), (cx + 60, 0)):
            d.rectangle([(fx - 22) * s, 1380 * s, (fx + 22) * s, 1470 * s], fill=255)
            d.polygon(P_((fx + 30, 1440), (fx + 34, 1490), (fx - 120, 1500), (fx - 130, 1482), (fx - 60, 1452), (fx - 20, 1440), s=s), fill=255)
            d.ellipse([(fx + 4) * s, 1446 * s, (fx + 42) * s, 1500 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(hair_back, (w, h), (14, 9, 10), 40, rim_strength=1.3))
    img.alpha_composite(shade(feet, (w, h), PALE, 16, rim_strength=0.8))
    sr = shade(sari, (w, h), SAREE, 80, rim_strength=1.2)
    sr = texmul(sr, lambda xx, yy: 0.88 + 0.12 * np.sin(xx / 9 + yy / 140))                 # pleats
    img.alpha_composite(sr)
    d = ImageDraw.Draw(img)
    d.line([(cx - 170, 1400), (cx + 190, 1390)], fill=GOLDB + (255,), width=22)              # gold hem border
    d.line([(cx - 170, 1372), (cx + 186, 1362)], fill=(110, 70, 30, 255), width=4)
    for k in range(10):                                                                     # silver anklets (payal)
        for fx in (cx - 70, cx + 60):
            bx = fx - 22 + k * 5
            d.ellipse([bx - 5, 1452, bx + 5, 1462], fill=(225, 225, 230, 255))
    for fx in (cx - 70, cx + 60):                                                           # red alta on the soles
        d.line([(fx - 126, 1496), (fx + 30, 1492)], fill=(200, 20, 30, 255), width=6)
    pl = shade(pallu, (w, h), (130, 10, 18), 50, rim_strength=1.4)
    img.alpha_composite(pl)
    img.alpha_composite(shade(face, (w, h), PALE, 46, rim_strength=0.6))
    d = ImageDraw.Draw(img)
    e1 = rot([(cx - 18, hy + 6)], ang, cx, hy + 120)[0]; e2 = rot([(cx + 40, hy + 4)], ang, cx, hy + 120)[0]
    for ex, ey in (e1, e2):
        d.ellipse([ex - 17, ey - 11, ex + 17, ey + 13], fill=(26, 8, 10, 255))
    img.alpha_composite(shade(hair_front, (w, h), (16, 10, 11), 20, rim_strength=1.5))
    d = ImageDraw.Draw(img)
    bp = rot([(cx - 92, hy - 70), (cx - 60, hy - 124), (cx + 64, hy - 126), (cx + 104, hy - 40)], ang, cx, hy + 120)
    d.line(bp, fill=GOLDB + (255,), width=14, joint="curve")                                # gold border of the veil
    img.alpha_composite(shade(arm, (w, h), PALE, 13, rim_strength=0.9))
    lx, ly = cx + 190, 800 - 260 * arm_up + 70
    if lantern:
        d = ImageDraw.Draw(img)
        d.arc([lx - 40, ly - 90, lx + 40, ly - 20], 180, 360, fill=(60, 40, 30, 255), width=6)
        d.rectangle([lx - 34, ly - 50, lx + 34, ly - 38], fill=(70, 46, 30, 255))
        gl = (int(90 + 165 * lamp), int(40 + 170 * lamp), int(30 + 90 * lamp), 255)
        d.ellipse([lx - 30, ly - 40, lx + 30, ly + 40], fill=gl)
        d.rectangle([lx - 36, ly + 34, lx + 36, ly + 50], fill=(70, 46, 30, 255))
        for sg in (-1, 1):
            d.line([(lx + sg * 34, ly - 40), (lx + sg * 34, ly + 36)], fill=(60, 40, 30, 255), width=4)
    out = (img, e1, e2, (lx, ly), 1500)
    _CH[key] = out
    return out


def put_chudail(img, x, y_feet, scale=1.0, t=0.0, eyes=1.0, tilt=0.0, lantern=True, lamp=1.0, aura=0.5, arm_up=0.0, flip=False):
    """Composite the full Chudail with her feet at (x, y_feet)."""
    body, e1, e2, (lx, ly), fy = chudail(tilt, lantern, lamp, arm_up)
    sway = 1.5 * math.sin(t * 0.9)
    g = body.rotate(sway, resample=Image.BICUBIC, center=(360, fy))
    if flip:
        g = g.transpose(Image.FLIP_LEFT_RIGHT)
    if scale != 1.0:
        g = g.resize((max(1, int(g.width * scale)), max(1, int(g.height * scale))), Image.LANCZOS)
    ox = 360 if not flip else g.width / scale - 360
    gx, gy = int(x - ox * scale), int(y_feet - fy * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(max(2, 30 * scale)))
        lay = Image.new("RGBA", g.size, (255, 50, 40, 0)); lay.putalpha(al.point(lambda v: int(v * aura)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    def mx(px):
        return px if not flip else g.width / scale - px
    if eyes > 0:
        k = eyes * (0.65 + 0.35 * math.sin(t * 5) ** 2)
        for ex, ey in (e1, e2):
            eye(img, gx + mx(ex) * scale, gy + ey * scale, k, max(0.25, scale * 0.8))
    if lantern and lamp > 0.05:
        fl = lamp * (0.85 + 0.15 * math.sin(t * 19) * math.sin(t * 7))
        img = glow_on(img, gsp(max(40, 330 * scale), (255, 120, 60)), gx + mx(lx) * scale, gy + ly * scale, 0.75 * fl)
    return img


_FT = {}


def feet_closeup(phase=0.0, hem=SAREE, border=GOLDB, step=True):
    """Close-up (ground level): two pale BACKWARD feet walking to the right - heels lead, toes trail behind -
    silver anklets with tiny bells, red alta on the soles, the hem of the sari above. 1080 x 900."""
    key = (round(phase * 16) % 16, hem, step)
    if key in _FT:
        return _FT[key]
    w, h = 1080, 900
    ph = 2 * math.pi * key[0] / 16
    gy = 830
    hemy = 500
    lifts = [max(0, math.sin(ph)) * 60 if step else 0, max(0, math.sin(ph + math.pi)) * 60 if step else 0]
    xs = [420 + 50 * math.cos(ph) * (1 if step else 0), 860 + 50 * math.cos(ph + math.pi) * (1 if step else 0)]

    def foot(ax, lift):
        g = gy - lift; ay = g - 150
        return [(ax - 52, ay - 30), (ax + 56, ay - 30), (ax + 74, ay + 30), (ax + 92, g - 50), (ax + 84, g - 12), (ax + 56, g),
                (ax - 200, g), (ax - 262, g - 6), (ax - 280, g - 24), (ax - 262, g - 46), (ax - 200, g - 62), (ax - 120, g - 80),
                (ax - 60, ay + 40)]

    def legs(d, s):
        for ax, lf in zip(xs, lifts):
            ay = gy - lf - 150
            d.polygon(P_((ax - 70, hemy), (ax + 80, hemy), (ax + 60, ay - 10), (ax - 50, ay - 10), s=s), fill=255)
            d.ellipse([(ax + 30) * s, (ay - 20) * s, (ax + 80) * s, (ay + 30) * s], fill=255)          # ankle bone

    def feet(d, s):
        for ax, lf in zip(xs, lifts):
            d.polygon(P_(*foot(ax, lf), s=s), fill=255)
            g = gy - lf
            for k in range(5):        # toes at the BACK (left)
                tx = ax - 262 + k * 30; ty = g - 40 - k * 6; r = 22 - k * 2
                d.ellipse([(tx - r) * s, (ty - r) * s, (tx + r) * s, (ty + r) * s], fill=255)

    def hemf(d, s):
        pts = [(0, 0), (w, 0), (w, hemy + 10)]
        for i in range(24):
            x = w - i * w / 23
            pts.append((x, hemy + 10 + 24 * math.sin(i * 0.9 + ph)))
        d.polygon(P_(*pts, s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), PALE, 34, rim_strength=0.9))
    img.alpha_composite(shade(feet, (w, h), PALE, 40, rim_strength=1.0))
    d = ImageDraw.Draw(img)
    for ax, lf in zip(xs, lifts):
        g = gy - lf; ay = g - 150
        d.line([(ax - 255, g - 2), (ax + 60, g - 2)], fill=(200, 20, 30, 255), width=12)               # alta on the sole
        for k in range(5):
            tx = ax - 262 + k * 30; ty = g - 40 - k * 6
            d.ellipse([tx - 15, ty - 10, tx - 3, ty + 2], fill=(190, 24, 32, 255))                     # painted toenails
            if k:
                d.line([(tx - 14, ty + 4), (tx - 10, ty + 18)], fill=(150, 130, 130, 255), width=3)
        for k in range(18):                                                                           # payal + bells
            bx = ax - 50 + k * 7; by = ay - 18 + 7 * math.sin(k * 0.7)
            d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(225, 226, 232, 255))
            if k % 3 == 1:
                d.ellipse([bx - 9, by + 5, bx + 9, by + 23], fill=(205, 205, 215, 255))
                d.line([(bx, by + 18), (bx, by + 23)], fill=(60, 60, 70, 255), width=2)
        # a ground shadow
    hm = shade(hemf, (w, h), hem, 40, rim_strength=1.2)
    hm = texmul(hm, lambda xx, yy: 0.86 + 0.14 * np.sin(xx / 14))
    img.alpha_composite(hm)
    d = ImageDraw.Draw(img)
    d.line([(x, hemy - 6 + 24 * math.sin((w - x) / w * 23 * 0.9 + ph)) for x in range(0, w + 1, 40)], fill=border + (255,), width=24)
    _FT[key] = img
    return img


_CF = {}


def chud_face(mouth=0.0):
    """Jump-scare close-up: red veil with gold border, black hair parted over a pale face, sunken eyes, a red bindi."""
    key = round(mouth, 1)
    if key in _CF:
        return _CF[key]
    w, h = 900, 1200
    cx, cy = 450, 560

    def veil(d, s):
        d.polygon(P_((cx - 330, 1200), (cx - 300, cy - 200), (cx - 180, cy - 420), (cx + 180, cy - 420), (cx + 300, cy - 200), (cx + 330, 1200), s=s), fill=255)

    def hair(d, s):
        d.polygon(P_((cx - 230, cy - 260), (cx + 230, cy - 260), (cx + 250, 1200), (cx - 250, 1200), s=s), fill=255)

    def face(d, s):
        d.ellipse([(cx - 150) * s, (cy - 210) * s, (cx + 150) * s, (cy + 230) * s], fill=255)

    def strands(d, s):
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 20, cy - 250), (cx + sg * 200, cy - 230), (cx + sg * 190, 1200), (cx + sg * 110, 1200),
                         (cx + sg * 105, cy + 120), (cx + sg * 70, cy - 120), s=s), fill=255)
        d.polygon(P_((cx - 30, cy - 240), (cx - 6, cy - 240), (cx - 14, cy + 260), (cx - 26, cy + 250), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(veil, (w, h), (140, 10, 18), 80, rim_strength=1.4))
    d = ImageDraw.Draw(img)
    d.line(P_((cx - 300, 1200), (cx - 300, cy - 200), (cx - 180, cy - 420), (cx + 180, cy - 420), (cx + 300, cy - 200), (cx + 300, 1200)), fill=GOLDB + (255,), width=26)
    img.alpha_composite(shade(hair, (w, h), (14, 9, 10), 40))
    img.alpha_composite(shade(face, (w, h), PALE, 80, rim_strength=0.7))
    d = ImageDraw.Draw(img)
    e1, e2 = (cx - 62, cy + 10), (cx + 62, cy + 10)
    for ex, ey in (e1, e2):
        d.ellipse([ex - 46, ey - 28, ex + 46, ey + 32], fill=(26, 8, 10, 255))
    d.ellipse([cx - 13, cy - 110, cx + 13, cy - 84], fill=(200, 16, 26, 255))      # bindi
    d.line([(cx - 44, cy + 160), (cx, cy + 166 + 10 * mouth), (cx + 44, cy + 160)], fill=(70, 18, 22, 255), width=7)
    if mouth > 0.3:
        d.ellipse([cx - 26, cy + 154, cx + 26, cy + 176 + 40 * mouth], fill=(18, 5, 7, 255))
    img.alpha_composite(shade(strands, (w, h), (16, 10, 11), 24, rim_strength=1.5))
    out = (img, e1, e2)
    _CF[key] = out
    return out


def put_face(img, x, y, scale, t, eyes=1.0, mouth=0.0, tilt=0.0, aura=0.7):
    fc, e1, e2 = chud_face(mouth)
    g = fc.rotate(tilt, resample=Image.BICUBIC, center=(450, 560))
    g = g.resize((int(g.width * scale), int(g.height * scale)), Image.LANCZOS)
    gx, gy = int(x - 450 * scale), int(y - 560 * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(30))
        lay = Image.new("RGBA", g.size, (255, 50, 40, 0)); lay.putalpha(al.point(lambda v: int(v * aura)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    k = eyes * (0.75 + 0.25 * math.sin(t * 6) ** 2)
    ca, sa = math.cos(math.radians(-tilt)), math.sin(math.radians(-tilt))
    for ex, ey in (e1, e2):
        dx, dy = ex - 450, ey - 560
        eye(img, x + (dx * ca - dy * sa) * scale, y + (dx * sa + dy * ca) * scale, k, 1.4 * scale)
    return img


# ============================================================ Dadi
_DD = {}


def dadi(pose="sit", eyes_red=0.0, smile=1.0):
    """Arjun's grandmother: white sari with a thin red border over grey hair, round glasses.
    pose 'sit' = on the charpai, finger raised in warning; 'door' = standing in a doorway (upper body)."""
    key = (pose, round(eyes_red, 1), smile)
    if key in _DD:
        return _DD[key]
    w, h = W, H
    if pose == "sit":
        cx, hy, by = 520, 820, 1330
    else:
        cx, hy, by = 540, 700, 1920
    WHITE = (214, 206, 196)

    def body(d, s):
        if pose == "sit":
            d.polygon(P_((cx - 110, hy + 100), (cx + 110, hy + 100), (cx + 230, by), (cx - 250, by), s=s), fill=255)
            d.ellipse([(cx - 280) * s, (by - 140) * s, (cx + 260) * s, (by + 40) * s], fill=255)
        else:
            d.polygon(P_((cx - 150, hy + 140), (cx + 150, hy + 140), (cx + 260, by), (cx - 260, by), s=s), fill=255)

    def veil(d, s):
        d.polygon(P_((cx - 150, hy + 230), (cx - 125, hy - 60), (cx - 75, hy - 140), (cx + 75, hy - 140), (cx + 125, hy - 60), (cx + 155, hy + 230), s=s), fill=255)

    def face(d, s):
        d.ellipse([(cx - 80) * s, (hy - 96) * s, (cx + 80) * s, (hy + 100) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 80) * s, (hy - 104) * s, (cx + 80) * s, (hy - 10) * s], 180, 360, fill=255)

    def arm(d, s):
        if pose == "sit":
            d.line([((cx + 120) * s, (hy + 180) * s), ((cx + 230) * s, (hy + 320) * s), ((cx + 250) * s, (hy + 120) * s)], fill=255, width=int(34 * s), joint="curve")
            d.line([((cx + 250) * s, (hy + 120) * s), ((cx + 256) * s, (hy + 40) * s)], fill=255, width=int(14 * s))
        else:
            d.line([((cx - 140) * s, (hy + 200) * s), ((cx - 170) * s, (hy + 480) * s), ((cx - 60) * s, (hy + 560) * s)], fill=255, width=int(34 * s), joint="curve")

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    lt = dict(rim=(255, 170, 100))
    bd = shade(body, (w, h), WHITE, 70, **lt)
    img.alpha_composite(texmul(bd, lambda xx, yy: 0.9 + 0.1 * np.sin(xx / 16 + yy / 200)))
    img.alpha_composite(shade(veil, (w, h), WHITE, 40, **lt))
    d = ImageDraw.Draw(img)
    d.line(P_((cx - 150, hy + 230), (cx - 125, hy - 60), (cx - 75, hy - 140), (cx + 75, hy - 140), (cx + 125, hy - 60), (cx + 155, hy + 230)), fill=(170, 30, 30, 255), width=9)
    img.alpha_composite(shade(face, (w, h), (140, 92, 70), 40, **lt))
    img.alpha_composite(shade(hair, (w, h), (170, 166, 160), 16, **lt))
    img.alpha_composite(shade(arm, (w, h), (140, 92, 70), 14, **lt))
    d = ImageDraw.Draw(img)
    E1, E2 = (cx - 32, hy - 6), (cx + 32, hy - 6)
    for ex, ey in (E1, E2):
        if eyes_red < 0.5:
            if smile:
                d.arc([ex - 16, ey - 8, ex + 16, ey + 12], 200, 340, fill=(30, 16, 14, 255), width=5)
            else:
                d.ellipse([ex - 7, ey - 5, ex + 7, ey + 7], fill=(24, 14, 12, 255))
        else:
            d.ellipse([ex - 15, ey - 10, ex + 15, ey + 12], fill=(20, 8, 8, 255))
        d.ellipse([ex - 26, ey - 22, ex + 26, ey + 24], outline=(60, 50, 40, 255), width=4)        # glasses
    d.line([(cx - 6, hy - 6), (cx + 6, hy - 6)], fill=(60, 50, 40, 255), width=4)
    for k in range(3):                                                                      # wrinkles
        d.arc([cx - 60, hy + 20 + k * 10, cx - 30, hy + 50 + k * 10], 100, 170, fill=(110, 70, 54, 255), width=2)
        d.arc([cx + 30, hy + 20 + k * 10, cx + 60, hy + 50 + k * 10], 10, 80, fill=(110, 70, 54, 255), width=2)
    if smile:
        d.arc([cx - 36, hy + 30, cx + 36, hy + 72], 20, 160, fill=(80, 30, 30, 255), width=6)
    else:
        d.line([(cx - 26, hy + 56), (cx + 26, hy + 56)], fill=(80, 30, 30, 255), width=6)
    if eyes_red > 0:
        for ex, ey in (E1, E2):
            eye(img, ex, ey, eyes_red, 0.9)
    out = img
    _DD[key] = out
    return out


# ============================================================ props
def lantern_sprite(lamp=1.0):
    w, h = 120, 180
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = 60
    d.arc([cx - 40, 0, cx + 40, 70], 180, 360, fill=(60, 40, 30, 255), width=6)
    d.rectangle([cx - 34, 40, cx + 34, 54], fill=(70, 46, 30, 255))
    gl = (int(90 + 165 * lamp), int(40 + 170 * lamp), int(30 + 90 * lamp), 255)
    d.ellipse([cx - 32, 50, cx + 32, 140], fill=gl)
    d.rectangle([cx - 38, 134, cx + 38, 152], fill=(70, 46, 30, 255))
    return im


def khejri(seed=0, height=520):
    """Khejri tree of the Thar desert: twisted trunk, forked branches, flat feathery canopy."""
    rng = np.random.default_rng(seed)
    w, h = 620, height + 120
    cx = w / 2

    def trunk(d, s):
        pts = [(cx + 20 * math.sin(k * 0.8 + seed), h - k * (height * 0.55) / 6) for k in range(7)]
        d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(30 * s), joint="curve")
        top = pts[-1]
        for a in (-2.4, -1.9, -1.3, -0.8):
            L = rng.uniform(140, 220)
            e = (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.6)
            d.line([(top[0] * s, top[1] * s), (e[0] * s, e[1] * s)], fill=255, width=int(14 * s))

    def canopy(d, s):
        top_y = h - height * 0.55 - 120
        for k in range(110):
            x = cx + rng.normal(0, 150); y = top_y + rng.normal(0, 40) - (1 - abs(x - cx) / 300) * 30
            r = rng.uniform(16, 40)
            d.ellipse([(x - r * 1.6) * s, (y - r * 0.6) * s, (x + r * 1.6) * s, (y + r * 0.6) * s], fill=255)

    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.alpha_composite(shade(trunk, (w, h), (40, 16, 14), 10))
    im.alpha_composite(shade(canopy, (w, h), (30, 10, 12), 24, rim_strength=1.2))
    return im


def fort_far():
    """A Rajasthan hill fort on the horizon: rocky hill, crenellated walls, round bastions, chhatri domes."""
    w, h = 900, 380

    def dr(d, s):
        d.polygon(P_((0, 380), (120, 300), (260, 250), (420, 220), (600, 236), (760, 290), (900, 380), s=s), fill=255)
        d.rectangle([200 * s, 170 * s, 690 * s, 250 * s], fill=255)
        for x in range(200, 690, 22):
            d.rectangle([x * s, 156 * s, (x + 12) * s, 172 * s], fill=255)
        for x in (200, 360, 530, 690):
            d.ellipse([(x - 34) * s, 140 * s, (x + 34) * s, 260 * s], fill=255)
        d.rectangle([380 * s, 90 * s, 560 * s, 175 * s], fill=255)          # palace block
        for x, top in ((410, 36), (470, 16), (530, 36)):                    # chhatris: domes on pillars
            d.rectangle([(x - 22) * s, (top + 26) * s, (x + 22) * s, (top + 34) * s], fill=255)
            for px in (x - 18, x + 14):
                d.rectangle([px * s, (top + 30) * s, (px + 4) * s, 92 * s], fill=255)
            d.pieslice([(x - 22) * s, (top - 6) * s, (x + 22) * s, (top + 40) * s], 180, 360, fill=255)
            d.line([(x * s, (top - 4) * s), (x * s, (top - 18) * s)], fill=255, width=int(3 * s))

    im = shade(dr, (w, h), (70, 18, 18), 20, rim_strength=0.6)
    a = np.asarray(im, np.float32).copy()
    a[..., :3] = a[..., :3] * 0.5 + np.array([95, 22, 20]) * 0.5
    im = Image.fromarray(a.astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    for x, y in ((402, 118), (438, 118), (500, 118), (536, 140), (300, 200)):         # a few lit windows
        d.rectangle([x, y, x + 9, y + 14], fill=(255, 150, 70, 255))
    return dof(im, 1.6)


def peepal_tree():
    """An old peepal tree: fluted trunk with buttress roots, hanging aerial roots, heart-shaped leaves with drip tips,
    red and yellow sacred threads wound round the trunk, and a small sindoor-painted shrine stone with a diya."""
    w, h = 1100, 1500
    rng = np.random.default_rng(77)
    cx = 520

    def trunk(d, s):
        d.polygon(P_((cx - 170, 1500), (cx - 90, 1380), (cx - 70, 900), (cx - 40, 640), (cx + 60, 640), (cx + 80, 900), (cx + 100, 1380), (cx + 200, 1500), s=s), fill=255)
        for a, L, wd in ((-2.5, 380, 60), (-2.0, 300, 46), (-1.1, 320, 50), (-0.6, 380, 56), (-1.6, 260, 40)):
            d.line([(cx * s, 700 * s), ((cx + math.cos(a) * L) * s, (700 + math.sin(a) * L) * s)], fill=255, width=int(wd * s))

    def roots(d, s):
        for k in range(16):
            x0 = cx + rng.uniform(-420, 420); y0 = rng.uniform(420, 620); L = rng.uniform(250, 600)
            pts = [(x0 + 12 * math.sin(i * 0.8 + k), y0 + L * i / 10) for i in range(11)]
            d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(rng.uniform(4, 9) * s))

    def canopy(d, s):
        for k in range(1500):
            ang = rng.uniform(0, 2 * math.pi); rr = rng.uniform(0, 1) ** 0.6
            x = cx + math.cos(ang) * rr * 520; y = 400 + math.sin(ang) * rr * 330
            sz = rng.uniform(18, 32); a = rng.uniform(0, 2 * math.pi)
            ca, sa = math.cos(a), math.sin(a)
            leaf = [(-0.5, -0.1), (-0.35, -0.5), (0, -0.4), (0.35, -0.5), (0.5, -0.1), (0.2, 0.4), (0, 1.0), (-0.2, 0.4)]
            d.polygon([((x + (u * ca - v * sa) * sz) * s, (y + (u * sa + v * ca) * sz) * s) for u, v in leaf], fill=255)

    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.alpha_composite(shade(roots, (w, h), (36, 16, 14), 6))
    tr = shade(trunk, (w, h), (64, 34, 28), 60)
    tr = texmul(tr, lambda xx, yy: 1 - 0.22 * (np.sin(xx / 7 + np.sin(yy / 60) * 2) > 0.7))
    im.alpha_composite(tr)
    tm = Image.new("L", (w, h), 0); shade_m = ImageDraw.Draw(tm)
    shade_m.polygon(P_((cx - 120, 1500), (cx - 90, 1380), (cx - 70, 900), (cx + 80, 900), (cx + 100, 1380), (cx + 150, 1500)), fill=255)
    th = Image.new("RGBA", (w, h), (0, 0, 0, 0)); td = ImageDraw.Draw(th)
    for k in range(9):                                                   # sacred threads (kalava)
        y = 1060 + k * 13
        col = (200, 26, 30, 255) if k % 3 else (220, 170, 40, 255)
        td.line([(cx - 120, y + 8), (cx + 120, y - 8)], fill=col, width=6)
    th.putalpha(Image.fromarray(np.minimum(np.asarray(th.split()[3]), np.asarray(tm))))
    im.alpha_composite(th)
    im.alpha_composite(shade(canopy, (w, h), (34, 10, 12), 50, rim_strength=1.3))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([cx + 170, 1400, cx + 250, 1490], 20, fill=(190, 60, 26, 255))         # shrine stone (sindoor)
    d.ellipse([cx + 196, 1420, cx + 224, 1446], fill=(240, 200, 80, 255))
    d.chord([cx + 260, 1462, cx + 310, 1500], 0, 180, fill=(120, 60, 40, 255))                 # diya
    return im, (cx + 285, 1452)


def ripple(xx, yy, k=1.0):
    return 1 - 0.16 * k * (np.sin(yy / 5 + np.sin(xx / 70) * 3) > 0.6)


def dune_layer(seed, base, amp, col, width, height=900, lit=1.0, period=None):
    """A row of dunes: smooth crests, the moon side lit with a red rim, ripples on the sand."""
    rng = np.random.default_rng(seed)
    xs = np.arange(width)
    per = period or width
    a1, a2, a3 = rng.uniform(0, 6, 3)
    hh = base - amp * (0.45 * np.sin(2 * np.pi * xs / per + a1) + 0.3 * np.sin(2 * np.pi * xs / per * 2 + a2)
                       + 0.55 * (1 - np.abs(np.sin(np.pi * xs / per * 3 + a3))) ** 1.6)
    yy = np.arange(height)[:, None]
    inside = yy >= hh[None, :]
    slope = np.gradient(hh)
    litk = np.clip(0.5 - slope * 3, 0, 1)
    depth = np.clip((yy - hh[None, :]) / 300, 0, 1)
    c = np.array(col, np.float32)
    a = np.zeros((height, width, 4), np.float32)
    a[..., :3] = c * (0.75 + 0.5 * litk[None, :, None] * lit) [..., :] * (1 - 0.4 * depth[..., None])
    rim = (yy - hh[None, :] < 5) & inside
    a[rim, :3] = a[rim, :3] * 0.4 + np.array([255, 90, 60]) * 0.6 * lit
    xxg = np.broadcast_to(xs[None, :], (height, width)); yyg = np.broadcast_to(yy, (height, width))
    a[..., :3] *= ripple(xxg, yyg - hh[None, :], 0.8)[..., None]
    a[..., 3] = inside * 255
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def scrub_strip(period=600, width=None):
    """Periodic foreground of dry desert grass + a few small rocks (tileable, for side scrolling)."""
    width = width or W + 2 * period
    m = Image.new("L", (width, 700), 0); d = ImageDraw.Draw(m)
    rng = np.random.default_rng(5)
    blades = [(rng.uniform(0, period), rng.uniform(80, 360), rng.uniform(-70, 70)) for _ in range(40)]
    rocks = [(rng.uniform(0, period), rng.uniform(30, 70)) for _ in range(2)]
    for rep in range(width // period + 1):
        for x, hg, lean in blades:
            X = x + rep * period
            d.polygon([(X - 8, 700), (X + 8, 700), (X + lean, 700 - hg)], fill=255)
        for x, r in rocks:
            X = x + rep * period
            d.ellipse([X - r * 1.5, 700 - r, X + r * 1.5, 700 + r], fill=255)
    im = Image.new("RGBA", m.size, (8, 3, 4, 0)); im.putalpha(m)
    return im


# ============================================================ worlds
class Desert:
    """Night desert: blood-red moon, the hill fort, dunes, khejri trees, the road (perspective or side view)."""
    SW = W + 2400

    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W]
        y = yy / H
        top = np.array([3, 1, 2], np.float32); mid = np.array([36, 5, 8], np.float32); hor = np.array([160, 34, 22], np.float32)
        k1 = np.clip(y / 0.42, 0, 1) ** 1.4; k2 = np.clip((y - 0.36) / 0.2, 0, 1) ** 1.3
        col = top * (1 - k1[..., None]) + mid * k1[..., None]; col = col * (1 - k2[..., None]) + hor * k2[..., None]
        dd = np.sqrt((xx - MOON[0]) ** 2 + (yy - MOON[1]) ** 2)
        col += (np.exp(-dd / 330) * 140)[..., None] * np.array([1.0, 0.32, 0.22])
        moon = np.clip((125 - dd) / 2, 0, 1)
        tex = fog_texture(W, H, 19)
        mcol = np.array([240, 116, 74], np.float32) * (0.78 + 0.28 * tex)[..., None]
        mcol *= (0.85 + 0.15 * np.clip((MOON[1] - yy + 125) / 250, 0, 1))[..., None]
        col = col * (1 - moon[..., None]) + mcol * moon[..., None]
        cl = fog_texture(W, H, 29) * np.exp(-((yy - 470) / 90) ** 2)
        col = col * (1 - 0.6 * cl[..., None]) + np.array([30, 6, 8]) * 0.6 * cl[..., None]
        rng = np.random.default_rng(4)
        for _ in range(120):
            sx, sy = rng.uniform(0, W), rng.uniform(0, 700)
            if math.hypot(sx - MOON[0], sy - MOON[1]) > 200:
                col[int(sy), int(sx)] = (200, 150, 140)
        col[yy >= HZ] = 0
        self.sky = to_img(col)
        self.fort = fort_far()
        self.dune_far = dof(dune_layer(1, 120, 50, (80, 20, 18), self.SW, 420, period=1200), 2)
        self.dune_mid = dof(dune_layer(2, 160, 110, (52, 12, 12), self.SW, 600, period=1200), 1)
        # flat desert floor (perspective ripples)
        g = np.clip((yy - HZ) / (H - HZ), 0, 1)
        f = np.zeros((H, W, 3), np.float32)
        f[..., 0] = 70 - 40 * g; f[..., 1] = 16 - 9 * g; f[..., 2] = 14 - 8 * g
        f *= (1 - 0.18 * (np.sin(300 / (yy - HZ + 6) * 9 + xx / 140) > 0.6))[..., None]
        f += (np.exp(-((xx - MOON[0]) / (80 + 300 * g)) ** 2) * np.exp(-g * 3) * 40)[..., None] * np.array([1, 0.3, 0.2])
        alpha = (yy >= HZ).astype(np.float32) * 255
        self.floor = Image.fromarray(np.dstack([np.clip(f, 0, 255), alpha]).astype(np.uint8), "RGBA")
        # perspective road to the horizon
        r = np.zeros((H, W, 4), np.float32)
        half = (yy - HZ) / (H - HZ) * 600 + 5
        on = (np.abs(xx - 540) < half) & (yy > HZ)
        r[..., 0] = 26; r[..., 1] = 12; r[..., 2] = 12
        r[..., :3] *= (0.8 + 0.4 * fog_texture(W, H, 41))[..., None]
        z = 260 / (yy - HZ + 4)
        dash = on & (np.abs(xx - 540) < half * 0.018 + 1) & (np.sin(z * 9) > 0.1)
        r[dash, :3] = (190, 150, 120)
        edge = on & (np.abs(np.abs(xx - 540) - half * 0.94) < half * 0.012 + 0.8)
        r[edge, :3] = (120, 90, 70)
        r[..., 3] = on * 255
        sandover = fog_texture(W, H, 43)
        r[..., 3] *= np.clip(1.3 - sandover * 0.9, 0, 1)
        self.road_p = Image.fromarray(np.clip(r, 0, 255).astype(np.uint8), "RGBA")
        self.khejri = [khejri(i, hg) for i, hg in ((1, 460), (2, 560), (3, 400), (4, 520))]
        pt, diya = peepal_tree()
        self.peepal, self.diya = pt, diya
        self.fg = dof(D5.foreground(), 9)
        self.scrub = dof(scrub_strip(), 7)
        self.road_side = self._road_side()

    def _road_side(self):
        w = W + 400
        a = np.zeros((260, w, 4), np.float32)
        yy, xx = np.mgrid[0:260, 0:w]
        a[..., 0] = 28; a[..., 1] = 13; a[..., 2] = 12
        a[..., :3] *= (0.8 + 0.4 * fog_texture(w, 260, 47))[..., None]
        a[(yy > 118) & (yy < 132) & ((xx % 200) < 110), :3] = (190, 150, 120)
        a[(yy < 8) | (yy > 250), :3] = (110, 80, 64)
        a[..., 3] = 255
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")

    def frame(self, t, cam=0.0, side=False, tree_x=None, tree_scale=1.0, kh=True, extra_back=None, extra_mid=None, extra_front=None,
              fg=True, diya=1.0, road=True):
        img = self.sky.copy()
        P = lambda k: int(-cam * k)
        img.alpha_composite(self.fort, (P(0.05) + 40, HZ - 380 + 30))
        img.alpha_composite(self.dune_far, (-(int(cam * 0.12) % 1200) - 300, HZ - 420 + 30))
        img.alpha_composite(self.floor)
        img.alpha_composite(self.dune_mid, (-(int(cam * 0.3) % 1200) - 300, HZ - 600 + 170))
        if road and not side:
            img.alpha_composite(self.road_p)
        if extra_back:
            img = extra_back(img, t, P) or img
        if kh:
            if side:
                for i, (k_, x) in enumerate(zip(self.khejri, (100, 700, 1300, 1900))):
                    X = (x - cam * 0.55) % 2400 - 600
                    img.alpha_composite(k_, (int(X), HZ + 230 + i * 12 - k_.height))
            else:
                for i, (k_, x, sc) in enumerate(zip(self.khejri[:3], (760, -80, 920), (0.55, 0.42, 0.35))):
                    kk = k_.resize((int(k_.width * sc), int(k_.height * sc)), Image.LANCZOS) if sc != 1 else k_
                    img.alpha_composite(kk, (P(0.4) + x, HZ + 40 + i * 6 - kk.height))
        if side and road:
            img.alpha_composite(self.road_side, (-(int(cam) % 200) - 100, 1400))
        if extra_mid:
            img = extra_mid(img, t, P) or img
        if tree_x is not None:
            pt = self.peepal if tree_scale == 1.0 else self.peepal.resize((int(self.peepal.width * tree_scale), int(self.peepal.height * tree_scale)), Image.LANCZOS)
            ty = HZ + 420 - pt.height if tree_scale >= 0.8 else HZ + 200 - pt.height
            img.alpha_composite(pt, (P(0.7) + tree_x, ty))
            if diya > 0:
                a = to_arr(img)
                fl = diya * (0.8 + 0.2 * math.sin(t * 21) * math.sin(t * 6))
                add_glow(a, gsp(int(140 * tree_scale), (255, 160, 70)), P(0.7) + tree_x + self.diya[0] * tree_scale, ty + self.diya[1] * tree_scale, 0.8 * fl)
                img = to_img(a)
        if extra_front:
            img = extra_front(img, t, P) or img
        if fg:
            if side:
                img.alpha_composite(self.scrub, (-(int(cam * 1.6) % 600) - 100, H - 700 + 140))
            else:
                img.alpha_composite(self.fg, (-220 + P(1.4), H - 700 + 110))
        return img


_DS = None


def desert():
    global _DS
    if _DS is None:
        _DS = Desert()
    return _DS


class Stepwell:
    """An old baori seen from a landing halfway down: the far wall is a cascade of zigzag stairs,
    dark colonnades on both sides, black water below with the moon's reflection, a red glow from the top."""
    def __init__(self):
        S2 = 2
        im = Image.new("RGBA", (W * S2, H * S2), (26, 8, 8, 255)); d = ImageDraw.Draw(im)
        for y in range(0, 230 * S2):
            k = y / (230 * S2)
            d.line([(0, y), (W * S2, y)], fill=(int(120 - 80 * k), int(20 - 10 * k), int(18 - 8 * k), 255))
        tiers = 8
        self.tier_y = [236 + k * 162 for k in range(tiers + 1)]
        for k in range(tiers):
            y0, y1 = self.tier_y[k], self.tier_y[k + 1]
            sx = 1 - 0.045 * k
            X = lambda x: (540 + (x - 540) * sx) * S2
            dim = 1 - k / (tiers + 3)
            ledge = tuple(int(c * dim) for c in (170, 70, 50)) + (255,)
            mass = tuple(int(c * dim) for c in (92, 34, 27)) + (255,)
            tread = tuple(int(c * dim) for c in (160, 64, 46)) + (255,)
            riser = tuple(int(c * dim) for c in (46, 15, 13)) + (255,)
            d.rectangle([0, y0 * S2, W * S2, (y0 + 14) * S2], fill=ledge)
            off = 0 if k % 2 == 0 else 165
            for j in range(-2, 6):
                xa = off + j * 330
                for sg in (-1, 1):
                    d.polygon([(X(xa), (y0 + 14) * S2), (X(xa + sg * 165), y1 * S2), (X(xa), y1 * S2)], fill=mass)
                    n = 8
                    for i in range(1, n + 1):
                        yy_ = y0 + 14 + (y1 - y0 - 14) * i / n
                        xe = xa + sg * 165 * i / n
                        d.line([(X(xa), yy_ * S2), (X(xe), yy_ * S2)], fill=tread, width=4 * S2)
                        d.line([(X(xa), (yy_ - 6) * S2), (X(xe - sg * 165 / n), (yy_ - 6) * S2)], fill=riser, width=6 * S2)
        im = im.resize((W, H), Image.LANCZOS)
        a = to_arr(im)
        yy, xx = np.mgrid[0:H, 0:W]
        a *= (0.75 + 0.45 * fog_texture(W, H, 53))[..., None] * 0.6 + 0.4
        # water at the bottom
        wy = 1560
        wat = yy > wy
        g = np.clip((yy - wy) / (H - wy), 0, 1)
        wc = np.stack([18 - 8 * g, 5 - 2 * g, 6 - 2 * g], -1)
        refl = np.exp(-((xx - 640) / (40 + 120 * g)) ** 2) * (0.5 + 0.5 * np.sin(yy / 4) ** 6)
        wc += refl[..., None] * np.array([200, 70, 50]) * 0.8
        a = np.where(wat[..., None], wc, a)
        self.base = to_img(a)
        # colonnades left and right (in front of the far wall)
        def cols(d, s):
            for x0, x1 in ((0, 150), (930, W)):
                d.rectangle([x0 * s, 0, x1 * s, H * s], fill=255)
        cm = Image.new("L", (W * 2, H * 2), 0); cd = ImageDraw.Draw(cm); cols(cd, 2)
        for x0, x1 in ((20, 130), (950, 1060)):
            for k in range(5):
                y = 300 + k * 260
                cd.rectangle([x0 * 2, y * 2, x1 * 2, (y + 170) * 2], fill=0)
                cd.pieslice([x0 * 2, (y - 55) * 2, x1 * 2, (y + 55) * 2], 180, 360, fill=0)
        cm = cm.resize((W, H), Image.LANCZOS)
        self.cols = inflate_shade(cm, (48, 18, 16), radius=30, rim=(255, 70, 50))
        # near landing (foreground): big stone ledge + a pillar on the right
        def near(d, s):
            d.polygon(P_((0, 1640), (W, 1600), (W, H), (0, H), s=s), fill=255)
            d.rectangle([820 * s, 400 * s, W * s, 1640 * s], fill=255)
            d.pieslice([600 * s, 260 * s, 1080 * s, 620 * s], 180, 270, fill=255)
        nr = shade(near, (W, H), (70, 28, 22), 50)
        self.near = texmul(nr, lambda xx, yy: 1 - 0.16 * ((yy % 90) < 4) - 0.1 * ((xx % 160) < 4))
        # her path down the zigzag stairs: (x, feet_y, scale)
        self.path = []
        for k in range(len(self.tier_y)):
            sx = 1 - 0.045 * k
            x = 540 + ((380 if k % 2 == 0 else 700) - 540) * sx
            self.path.append((x, self.tier_y[k] + 12, 0.13 + 0.03 * k))

    def pos(self, u):
        """u in 0..1 along the path -> (x, y, scale)."""
        n = len(self.path) - 1
        u = min(max(u, 0), 1) * n
        i = min(int(u), n - 1); f = u - i
        a, b = self.path[i], self.path[i + 1]
        return tuple(a[j] + (b[j] - a[j]) * f for j in range(3))

    def frame(self, t, extra_mid=None, glow=1.0, near=True, extra_front=None):
        img = self.base.copy()
        a = to_arr(img)
        fl = glow * (0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 4))
        add_glow(a, gsp(520, (255, 60, 40)), 540, 120, 0.9 * fl)
        add_glow(a, gsp(140, (255, 200, 150)), 540, 180, 0.5 * fl)
        img = to_img(a)
        if extra_mid:
            img = extra_mid(img, t) or img
        img.alpha_composite(self.cols)
        if near:
            img.alpha_composite(self.near)
        if extra_front:
            img = extra_front(img, t) or img
        return img


_SW = None


def stepwell():
    global _SW
    if _SW is None:
        _SW = Stepwell()
    return _SW


def room_bg():
    """Dadi's room: lime-washed mud wall, a niche with an oil lamp, a rolled quilt, a charpai."""
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    a = np.zeros((H, W, 3), np.float32)
    a[..., 0] = 70; a[..., 1] = 40; a[..., 2] = 30
    a *= (0.7 + 0.45 * fog_texture(W, H, 83))[..., None]
    fl = np.broadcast_to(y > 1420, (H, W))
    a[fl] *= 0.5
    im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([140, 640, 300, 860], fill=(24, 12, 10, 255)); d.pieslice([140, 560, 300, 720], 180, 360, fill=(24, 12, 10, 255))  # niche
    d.chord([180, 820, 260, 860], 0, 180, fill=(140, 70, 40, 255))                               # diya in the niche
    for i in range(6):                                                                         # mandana dots painted on the wall
        d.ellipse([720 + (i % 3) * 60, 360 + (i // 3) * 60, 736 + (i % 3) * 60, 376 + (i // 3) * 60], fill=(150, 110, 90, 255))
    # charpai: wooden frame + woven rope
    d.rectangle([150, 1330, 930, 1350], fill=(90, 54, 34, 255)); d.rectangle([130, 1470, 950, 1490], fill=(90, 54, 34, 255))
    for x0 in (150, 910):
        d.rectangle([x0, 1330, x0 + 24, 1640], fill=(80, 48, 30, 255))
    for k in range(0, 800, 22):
        d.line([(150 + k, 1350), (130 + k + 60, 1470)], fill=(170, 140, 100, 255), width=4)
        d.line([(190 + k, 1350), (130 + k, 1470)], fill=(150, 120, 86, 255), width=4)
    return im


def temple(dawn=0.0):
    """A small white village temple: curved shikhara tower with ribs, an amalaka and kalash on top, a saffron flag,
    a porch on pillars with a brass bell hanging in the middle. Returns (RGBA, bell_xy, flag_base_xy)."""
    w, h = 900, 1200

    def tower(d, s):
        pts = []
        for k in range(21):
            u = k / 20
            pts.append((450 - 200 * (1 - u ** 1.6) - 30, 900 - 560 * u))
        pts += [(450 + 30 + 200 * (1 - (k / 20) ** 1.6), 900 - 560 * k / 20) for k in range(20, -1, -1)]
        d.polygon(P_(*pts, s=s), fill=255)
        d.ellipse([380 * s, 300 * s, 520 * s, 360 * s], fill=255)                   # amalaka
        d.polygon(P_((430, 310), (470, 310), (460, 250), (450, 230), (440, 250), s=s), fill=255)
        d.line([(450 * s, 240 * s), (450 * s, 120 * s)], fill=255, width=int(6 * s))

    def porch(d, s):
        d.rectangle([150 * s, 760 * s, 750 * s, 800 * s], fill=255)
        d.polygon(P_((130, 760), (450, 690), (770, 760), s=s), fill=255)
        for x in (180, 330, 570, 720):
            d.rectangle([(x - 16) * s, 800 * s, (x + 16) * s, 1080 * s], fill=255)
        d.rectangle([100 * s, 1080 * s, 800 * s, 1200 * s], fill=255)

    base = tuple(int(c) for c in np.array([150, 120, 115]) * (1 - dawn) + np.array([235, 200, 190]) * dawn)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tw = shade(tower, (w, h), base, 70, rim_strength=0.8)
    tw = texmul(tw, lambda xx, yy: 1 - 0.18 * ((yy % 34) < 5))
    im.alpha_composite(tw)
    im.alpha_composite(shade(porch, (w, h), base, 30, rim_strength=0.8))
    d = ImageDraw.Draw(im)
    d.rectangle([380, 820, 520, 1080], fill=(30, 12, 10, 255))                       # sanctum doorway
    d.ellipse([430, 980, 470, 1020], fill=(255, 180, 80, 255))                       # diya inside
    return im, (450, 860), (450, 120)


def bell_sprite(swing=0.0):
    w, h = 220, 320
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    def dr(d, s):
        d.line([(110 * s, 0), (110 * s, 90 * s)], fill=255, width=int(8 * s))
        d.ellipse([60 * s, 80 * s, 160 * s, 170 * s], fill=255)
        d.polygon(P_((60, 125), (160, 125), (172, 230), (196, 262), (24, 262), (48, 230), s=s), fill=255)
        d.ellipse([24 * s, 246 * s, 196 * s, 280 * s], fill=255)
    b = shade(dr, (w, h), (190, 130, 50), 30, rim=(255, 220, 150))
    b = b.rotate(swing, resample=Image.BICUBIC, center=(110, 0))
    return b


def door_bg(dawn=1.0):
    """Arjun's home at dawn: terracotta wall, an arched wooden doorway, a marigold toran above."""
    yy, xx = np.mgrid[0:H, 0:W]
    a = np.zeros((H, W, 3), np.float32)
    a[..., 0] = 140; a[..., 1] = 64; a[..., 2] = 44
    a *= (0.65 + 0.45 * fog_texture(W, H, 87))[..., None]
    a *= (0.55 + 0.45 * dawn)
    im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([250, 560, 830, H], fill=(30, 14, 12, 255))
    d.pieslice([250, 380, 830, 740], 180, 360, fill=(30, 14, 12, 255))
    d.rectangle([250, 560, 830, H], outline=(90, 50, 30, 255), width=20)
    for k in range(14):                                                    # toran: marigolds + leaves
        x = 270 + k * 42; y = 420 + 30 * math.sin(k / 13 * math.pi)
        d.line([(x, y - 30), (x, y + 30)], fill=(60, 40, 20, 255), width=3)
        d.ellipse([x - 16, y + 18, x + 16, y + 50], fill=(240, 130, 30, 255))
        d.polygon([(x + 20, y), (x + 34, y + 40), (x + 24, y + 70)], fill=(40, 50, 20, 255))
    d.line([(250, 400), (830, 400)], fill=(80, 60, 30, 255), width=6)
    return im


def peacock(t, k=1.0):
    """A peacock bursting out of the tree: body, neck and crest, flapping wings, long trailing tail."""
    w, h = 700, 420
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    flap = math.sin(t * 28)
    col = (18, 10, 14, 255)
    d.ellipse([300, 180, 430, 250], fill=col)
    d.line([(420, 200), (470, 130), (480, 110)], fill=col, width=18)
    d.ellipse([462, 92, 500, 124], fill=col)
    for k in range(3):
        d.line([(482, 96), (476 + k * 8, 70)], fill=col, width=3)
        d.ellipse([472 + k * 8, 62, 480 + k * 8, 72], fill=col)
    for sg in (-1, 1):
        tip = (360 + 40 * sg, 210 - 170 * flap * sg if sg < 0 else 210 + 120 * flap)
        d.polygon([(330, 200), (420, 200), tip], fill=col)
    for k in range(12):
        a = math.pi + (k - 6) * 0.05
        d.line([(310, 220), (310 + math.cos(a) * 300, 220 + math.sin(a) * 300 * 0.3 + 30)], fill=col, width=8)
        d.ellipse([310 + math.cos(a) * 300 - 9, 220 + math.sin(a) * 90 + 21, 310 + math.cos(a) * 300 + 9, 220 + math.sin(a) * 90 + 39], fill=(60, 30, 30, 255))
    return with_alpha(im, k)


def footprints_scene(t, t0=0.0):
    """Looking down at moonlit sand: a trail of bare footprints appears, one by one, coming toward Arjun's sandals
    at the bottom of the frame - but every print's toes point AWAY from him (backward feet)."""
    global _SAND
    if _SAND is None:
        yy, xx = np.mgrid[0:H, 0:W]
        a = np.zeros((H, W, 3), np.float32)
        a[..., 0] = 120; a[..., 1] = 40; a[..., 2] = 30
        a *= (0.75 + 0.35 * fog_texture(W, H, 61))[..., None]
        a *= ripple(xx, yy + 30 * np.sin(xx / 200), 1.2)[..., None]
        a *= (0.55 + 0.45 * np.exp(-((xx - 760) ** 2 + (yy - 300) ** 2) / (2 * 700 ** 2)))[..., None]
        _SAND = to_img(a)
    img = _SAND.copy()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    n_show = int((t - t0) / 0.32) + 1
    for i in range(7):
        if i >= n_show:
            break
        y = 120 + i * 205
        x = 540 + (70 if i % 2 else -70)
        fw, fh = 92, 230
        # toes at the TOP of each print (pointing away from Arjun), heel at the bottom
        for (cx_, cy_, rx, ry) in ((x, y + fh * 0.3, fw * 0.42, fh * 0.22), (x, y - fh * 0.05, fw * 0.5, fh * 0.26)):
            d.ellipse([cx_ - rx - 6, cy_ - ry - 6, cx_ + rx + 6, cy_ + ry + 6], fill=(200, 90, 70, 120))
            d.ellipse([cx_ - rx, cy_ - ry, cx_ + rx, cy_ + ry], fill=(30, 8, 8, 235))
        for k in range(5):
            tx = x - fw * 0.42 + k * fw * 0.21; ty = y - fh * 0.36 - (8 - abs(k - 1) * 4); r = 17 - k * 2
            d.ellipse([tx - r - 4, ty - r - 4, tx + r + 4, ty + r + 4], fill=(200, 90, 70, 120))
            d.ellipse([tx - r, ty - r, tx + r, ty + r], fill=(30, 8, 8, 235))
    lay = lay.filter(ImageFilter.GaussianBlur(2.2))
    img.alpha_composite(lay)
    # Arjun's sandals at the bottom edge (pointing up, toward the prints)
    sd = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(sd)
    for x in (400, 680):
        d2.rounded_rectangle([x - 62, 1700, x + 62, 2000], 60, fill=(50, 30, 22, 255))
        d2.rounded_rectangle([x - 44, 1740, x + 44, 2000], 44, fill=SKIN + (255,))
        d2.rectangle([x - 62, 1800, x + 62, 1840], fill=(80, 40, 30, 255))
    img.alpha_composite(sd)
    a = to_arr(img)
    add_glow(a, gsp(500, (255, 90, 60)), 800, 200, 0.5)
    return to_img(a)


_SAND = None


# ============================================================ scenes: PART 1
def make_hook(D, caps):
    D_ = desert()
    hdr = series_header("INDIA", "PART 1")
    t2 = caps[1][1]
    cut = t2 - 0.15
    def f(t):
        if t < cut:
            def mid(img, tt, P):
                # the viewer sees her first: a too-tall woman with a lantern under the peepal tree
                return put_chudail(img, P(0.7) + 300 + 640 * 0.0 + 120, HZ + 420 - 70 + 0, scale=0.36, t=tt, eyes=0.6, lamp=1.0, aura=0.4)
            img = D_.frame(t, cam=-30 + 40 * t / D, tree_x=-200, extra_front=mid)
            fog(img, t, 0.35, HZ - 120, HZ + 380, speed=16)
            bokeh_particles(img, 24, 3, t, color=(255, 110, 80), size=(2, 10), blur=(0, 6), area=(0, 400, W, 1500))
            a = finish(img, t, VIG_H, push=1.0 + 0.1 * t / cut, cx=330, cy=1150)
        else:
            tt = t - cut
            ft = feet_closeup(tt * 1.3)
            img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            bg = D_.frame(t, cam=0, kh=False, fg=False, road=False)
            img.alpha_composite(dof(bg, 6))
            img.alpha_composite(ft, (int(-140 + 110 * tt), 1000))
            a = to_arr(img)
            add_glow(a, gsp(500, (255, 110, 60)), 980, 900, 0.7 * (0.85 + 0.15 * math.sin(t * 17)))
            img = to_img(a)
            fog(img, t, 0.3, 1500, 1900, speed=30)
            fl = 0.5 if tt < 0.07 else 0.0
            a = finish(img, t, VIG_H, push=1.08 + 0.08 * tt, cx=560, cy=1300, flash=fl, flash_col=(255, 40, 30), shake=0.25 * (1 - ss(tt, 0, 0.5)))
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_road(D, caps):
    D_ = desert()
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        cam = 300 * t
        def mid(img, tt, P):
            # far back by a khejri tree: a red figure that is there... and gone (only the viewer sees it)
            if 3.0 < tt < 5.4:
                xx = 1250 - (cam * 0.55 - 0) % 2400 + 600 * 0
                xx = 900 - (tt - 3.0) * 300 * 0.55
                img = put_chudail(img, xx, HZ + 230, scale=0.15, t=tt, eyes=1.0, lamp=0.8, aura=0.3)
            bob = int(3 * math.sin(tt * 18))
            sp, lamp_xy, wy = scooter_rider(lamp=1.0, bob=bob)
            sx, sy = 160, 1530 - wy
            img.alpha_composite(sp, (sx, sy + int(2 * math.sin(tt * 11))))
            img = beam(img, sx + lamp_xy[0], sy + lamp_xy[1], 0.9, length=700, spread=200)
            return img
        img = D_.frame(t, cam=cam, side=True, extra_mid=mid)
        fog(img, t, 0.3, HZ - 120, HZ + 300, speed=60)
        bokeh_particles(img, 18, 7, t, color=(255, 120, 90), size=(2, 9), blur=(0, 5), area=(0, 500, W, 1500), drift=(-260, -10))
        out = to_img(finish(img, t, VIG_H, push=1.06, cx=520, cy=1150))
        if t > t2 - 0.2:
            lev = 0.4 if t < t3 - 0.2 else 0.2
            ui = fuel_ui(lev, t, "12 KM", ss(t, t2 - 0.2, t2 + 0.3))
            out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
        return to_arr(out)
    return f


def make_rule(D, caps):
    bg = room_bg()
    dd = dadi("sit", smile=0)
    lampg = gsp(420, (255, 170, 80))
    f1 = font(INTER_SB, 46)
    chips = [pill("1. LOOK AT HER FEET", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("2. FEET BACKWARDS? DON'T ANSWER", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92),
             pill("3. DON'T STOP", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [caps[1][1], caps[2][1], caps[2][1] + 2.0]
    def f(t):
        img = bg.copy()
        img.alpha_composite(dd)
        a = to_arr(img)
        fl = 0.8 + 0.2 * math.sin(t * 13) * math.sin(t * 5)
        add_glow(a, lampg, 220, 810, 1.0 * fl)
        lum = a.mean(2, keepdims=True)                        # faded memory look
        a = a * 0.45 + lum * np.array([1.25, 0.85, 0.6]) * 0.55
        a *= 0.92 + 0.08 * math.sin(t * 40)
        img = to_img(a)
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.15, tt + 0.3)
            if k > 0:
                img.alpha_composite(with_alpha(c, k), (int(W / 2 - c.width / 2), int(250 + i * 120 + 20 * (1 - k))))
        return finish(img, t, vig=VIG_H, push=1.0 + 0.06 * t / D, cx=560, cy=1000)
    return f


def make_tree(D, caps):
    D_ = desert()
    die = caps[0][1] + 2.4               # "...and died."
    pk = caps[0][2] + 0.1                # false scare: a peacock screams out of the tree
    def f(t):
        lamp = 1.0 if t < die - 0.9 else (0.0 if t > die else (0.5 + 0.5 * math.sin(t * 60)) * (1 - ss(t, die - 0.9, die)))
        def front(img, tt, P):
            sp, lamp_xy, wy = scooter_rider(lamp=round(lamp, 1), bob=0)
            sx, sy = 260 + P(0.9), 1640 - wy
            img.alpha_composite(sp, (sx, sy))
            img = beam(img, sx + lamp_xy[0], sy + lamp_xy[1], lamp * 0.9, length=600, spread=180)
            if pk <= tt < pk + 1.4:
                u = ss(tt, pk, pk + 1.4)
                pc = peacock(tt, 1.0 - ss(tt, pk + 1.0, pk + 1.4))
                img.alpha_composite(pc, (int(80 + 700 * u + P(0.7)), int(300 + 80 * math.sin(u * 3))))
            return img
        img = D_.frame(t, cam=-40 + 40 * t / D, tree_x=-180, extra_front=front, road=False)
        fog(img, t, 0.35, HZ - 100, HZ + 420, speed=14)
        if t > die:
            bokeh_particles(img, 12, 9, t, color=(80, 30, 20), size=(5, 12), blur=(0, 3), area=(0, 300, 900, 1200), drift=(20, 60))
        out = to_img(finish(img, t, VIG_H, push=1.03 + 0.06 * t / D + 0.04 * ss(t, pk, pk + 0.2), cx=500, cy=1100,
                           shake=0.5 * (1 - ss(t, pk, pk + 0.6)) if t > pk else 0))
        lev = 0.2 if t < die else 0.0
        ui = fuel_ui(lev, t, "9 KM")
        out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
        return to_arr(out)
    return f


def make_woman(D, caps):
    D_ = desert()
    t1, t2 = caps[1][1], caps[2][1]
    cut = t2 - 0.15
    def f(t):
        if t < cut:
            tilt = -16 * ss(t, t1, t1 + 1.6)
            def front(img, tt, P):
                img = put_chudail(img, 690 + P(0.8), 1360, scale=0.62, t=tt, eyes=0.0, tilt=tilt, lamp=1.0, aura=0.35)
                # Arjun, seen from behind (over his shoulder), next to the dead scooter
                h, fx, fy = arjun(0, 0, back=True, scale=1.25)
                img.alpha_composite(h, (int(230 - fx), int(2030 - fy)))
                return img
            img = D_.frame(t, cam=0, tree_x=60, extra_front=front, road=False, fg=False)
            fog(img, t, 0.3, HZ - 80, HZ + 360, speed=12)
            # tall grass at her feet: hides them from Arjun
            img.alpha_composite(D_.scrub, (-300, 1400 - 700 + 120))
            a = finish(img, t, VIG_H, push=1.04 + 0.07 * t / cut, cx=640, cy=950)
        else:
            tt = t - cut
            img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            bg = D_.frame(t, cam=0, kh=False, fg=False, road=False, tree_x=-100)
            img.alpha_composite(dof(bg, 7))
            ft = feet_closeup(0.0, step=False)
            img.alpha_composite(ft, (-60, 1000))
            # the lantern hanging down into the frame
            ls = lantern_sprite(1.0)
            img.alpha_composite(ls, (820, 640 + int(8 * math.sin(t * 2))))
            a = to_arr(img)
            add_glow(a, gsp(520, (255, 120, 60)), 880, 760, 0.8 * (0.85 + 0.15 * math.sin(t * 17)))
            img = to_img(a)
            fog(img, t, 0.25, 1500, 1920, speed=20)
            a = finish(img, t, VIG_H, push=1.0 + 0.12 * ss(tt, 0, D - cut), cx=420, cy=1450)
        return a
    return f


def make_mistake(D, caps):
    D_ = desert()
    t1, t2 = caps[1][1], caps[2][1]
    def f(t):
        if t < t1 - 0.1:
            img = Image.new("RGBA", (W, H), (10, 3, 4, 255))
            bg = D_.frame(t, cam=0, kh=True, fg=False, road=False)
            img.alpha_composite(dof(bg, 8))
            talk = caps[0][1] + 1.2 <= t <= caps[0][2]
            fc = arjun_face(0.6 if talk and math.sin(t * 20) > 0 else 0.15)
            img.alpha_composite(fc, (40, 620))
            a = to_arr(img)
            add_glow(a, gsp(600, (255, 130, 60)), 1080, 900, 0.7 * (0.85 + 0.15 * math.sin(t * 15)))
            return finish(to_img(a), t, VIG_H, push=1.02 + 0.05 * t / t1, cx=540, cy=1150)
        if t < t2 - 0.1:
            # the lantern goes out: black. Only her eyes, high up, much too high.
            tt = t - t1
            img = D_.frame(t, cam=0, tree_x=60, road=False, fg=False, diya=0.0)
            img = put_chudail(img, 690, 1360, scale=0.62, t=t, eyes=0.0, tilt=-16, lamp=max(0, 1 - tt * 6), aura=0.2)
            img = to_img(to_arr(img) * (1 - 0.72 * ss(tt, 0, 0.2)))
            body, e1, e2, _, fy = chudail(-16, True, 1.0, 0.0)
            k = ss(tt, 0.5, 1.0) * (0.65 + 0.35 * math.sin(t * 5) ** 2)
            for ex, ey in (e1, e2):
                eye(img, 690 + (ex - 360) * 0.62, 1360 + (ey - fy) * 0.62, k, 0.5)
            fl = 0.35 if 0.1 < tt < 0.16 else 0.0
            return finish(img, t, VIG_H, push=1.1 + 0.05 * tt, cx=700, cy=700, flash=fl, flash_col=(0, 0, 0))
        img = footprints_scene(t, t2 - 0.1)
        return finish(img, t, VIG_H, push=1.0 + 0.1 * ss(t, t2, D), cx=540, cy=1100)
    return f


def make_cliff(D, caps):
    SW_ = stepwell()
    t1, t2 = caps[1][1], caps[2][1]
    jt = caps[2][2] + 0.15
    def f(t):
        if t >= jt:
            img = Image.new("RGBA", (W, H), (8, 2, 3, 255))
            img = put_face(img, 540, 920, 1.5, t, eyes=1.0, mouth=0.3, tilt=-12, aura=0.8)
            fl = 0.85 if t < jt + 0.08 else 0.0
            a = finish(img, t, vig=VIG_H, push=1.0 + 0.6 * ss(t, jt, jt + 0.25), cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
            if t > D - 0.45:
                a *= 0.0
            return a
        if t < 1.6:
            # Arjun running down into the stepwell
            def mid(img, tt):
                u = ss(tt, 0, 1.6)
                h, fx, fy = arjun((tt * 1.8) % 1, run=1.0, scale=0.55)
                x, y = 300 + 300 * u, 900 + 600 * u
                img.alpha_composite(h, (int(x - fx), int(y - fy)))
                return img
            img = SW_.frame(t, extra_mid=mid, near=False)
            return finish(img, t, VIG_H, push=1.05, cy=1000, shake=0.2)
        # stop-motion: each beat she is suddenly further down the stairs
        def mid(img, tt):
            if tt >= t1 - 0.3:
                beat = int((tt - (t1 - 0.3)) / 0.55)
                u = min(0.62, 0.05 + beat * 0.08)
                x, y, sc = SW_.pos(u)
                img = put_chudail(img, x, y, scale=sc * 1.5, t=tt, eyes=1.0, lamp=0.0, lantern=False, aura=0.6)
            return img
        def front(img, tt):
            h, fx, fy = arjun_crouch(1.1, look_up=ss(tt, t2, t2 + 0.6))
            img.alpha_composite(h, (int(330 - fx), int(1790 - fy)))
            return img
        img = SW_.frame(t, extra_mid=mid, extra_front=front)
        fog(img, t, 0.25, 1300, 1700, col=(120, 30, 30))
        push = 1.05 + 0.04 * math.sin(t * 1.3) + 0.12 * ss(t, t2, jt)
        cy = 1200 - 400 * ss(t, t2 + 0.3, jt)
        return finish(img, t, vig=VIG_H, push=push, cx=460, cy=cy)
    return f


# ============================================================ scenes: PART 2
def make_recap(D, caps):
    SW_ = stepwell()
    hdr = series_header("INDIA", "PART 2")
    def f(t):
        def mid(img, tt):
            x, y, sc = SW_.pos(0.55 + 0.03 * ss(tt, 0, D))
            return put_chudail(img, x, y, scale=sc * 1.5, t=tt, eyes=1.0, lantern=False, aura=0.6)
        def front(img, tt):
            h, fx, fy = arjun_crouch(1.1, look_up=0.0)
            img.alpha_composite(h, (int(330 - fx), int(1790 - fy)))
            return img
        img = SW_.frame(t, extra_mid=mid, extra_front=front)
        fog(img, t, 0.25, 1300, 1700, col=(120, 30, 30))
        out = to_img(finish(img, t, vig=VIG_H, push=1.02 + 0.06 * t / D, cy=1000))
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_steps(D, caps):
    SW_ = stepwell()
    t1 = caps[1][1]
    cut = t1 - 0.2
    def f(t):
        if t < cut:
            # low angle: her backward feet coming down the steps toward us
            img = Image.new("RGBA", (W, H), (10, 3, 4, 255))
            d = ImageDraw.Draw(img)
            for k in range(9):
                y = 300 + k * 190
                c = int(30 + k * 9)
                d.rectangle([0, y, W, y + 190], fill=(c + 20, c // 3, c // 3, 255))
                d.rectangle([0, y, W, y + 18], fill=(c + 70, c // 2 + 10, c // 3 + 6, 255))
            beat = int(t / 0.7)
            fy = 160 + beat * 190
            ft = feet_closeup(0.0, step=False)
            img.alpha_composite(ft, (60, int(min(fy, 1100))))
            a = to_arr(img)
            add_glow(a, gsp(600, (255, 60, 40)), 540, 0, 0.8)
            img = to_img(a)
            fog(img, t, 0.25, 200, 1900, col=(110, 25, 25))
            return finish(img, t, VIG_H, push=1.04 + 0.03 * (t % 0.7), cy=1000, shake=0.15 if (t % 0.7) < 0.08 else 0)
        # close on Arjun: behind him in the dark, her hair hangs down and a long pale hand reaches in
        tt = t - cut
        def mid(img, t_):
            return img
        img = SW_.frame(t, near=True)
        a = to_arr(img) * 0.5
        img = to_img(a)
        k = ss(tt, 0.4, 2.6)
        face_y = -400 + 820 * k
        img = put_face(img, 700, face_y, 0.9, t, eyes=ss(tt, 0.6, 1.2), tilt=170, aura=0.5)
        h, fx, fy = arjun_crouch(2.3, look_up=0.0)
        img.alpha_composite(h, (int(450 - fx), int(2050 - fy)))
        reach = ss(tt, 1.0, D - cut - 0.6)
        bx, by = 1120 - 380 * reach, 980 + 150 * reach
        def hand_d(d, s_):
            d.polygon(P_((1180, 760), (1180, 830), (bx + 30, by + 26), (bx + 10, by - 22), s=s_), fill=255)       # long forearm
            d.ellipse([(bx - 60) * s_, (by - 40) * s_, (bx + 30) * s_, (by + 40) * s_], fill=255)                  # palm
            for j in range(4):                                                                                  # long bony fingers, curling down
                fx0, fy0 = bx - 50, by - 24 + j * 16
                pts = [(fx0, fy0), (fx0 - 80, fy0 + 10 + j * 4), (fx0 - 130, fy0 + 60 + j * 6)]
                d.line([(x * s_, y * s_) for x, y in pts], fill=255, width=int(13 * s_), joint="curve")
        img.alpha_composite(shade(hand_d, (W, H), PALE, 12, rim_strength=1.0))
        hit = caps[1][2] + 0.2
        fl = 0.6 if hit <= t < hit + 0.07 else 0.0
        return finish(img, t, VIG_H, push=1.03 + 0.05 * tt, cx=560, cy=1100, flash=fl, flash_col=(255, 30, 20), shake=0.6 * (1 - ss(t, hit, hit + 0.6)) if t > hit else 0)
    return f


def make_escape(D, caps):
    D_ = desert()
    bg = room_bg()
    dd = dadi("sit", smile=0)
    t1, t2 = caps[1][1], caps[2][1]
    f1 = font(INTER_SB, 36)
    chip = pill("WALK TO THE TEMPLE LIGHT. NEVER LOOK BACK.", f1, outline=(255, 200, 120, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)
    T_ = temple(0.0)[0]
    tsm = T_.resize((int(T_.width * 0.16), int(T_.height * 0.16)), Image.LANCZOS)
    def f(t):
        if t < t2 - 0.1:
            img = bg.copy(); img.alpha_composite(dd)
            a = to_arr(img)
            add_glow(a, gsp(420, (255, 170, 80)), 220, 810, 0.9)
            lum = a.mean(2, keepdims=True)
            a = a * 0.45 + lum * np.array([1.25, 0.85, 0.6]) * 0.55
            img = to_img(a)
            k = ss(t, t1 - 0.15, t1 + 0.3)
            if k > 0:
                c = chip if chip.width <= W - 40 else chip.resize((W - 40, int(chip.height * (W - 40) / chip.width)), Image.LANCZOS)
                img.alpha_composite(with_alpha(c, k), (int(W / 2 - c.width / 2), 300))
            return finish(img, t, vig=VIG_H, push=1.03 + 0.05 * t / t2, cx=560, cy=1000)
        tt = t - t2
        cam = 380 * tt
        def back(img, t_, P):
            img.alpha_composite(tsm, (860, HZ + 20 - tsm.height))
            a = to_arr(img); add_glow(a, gsp(120, (255, 190, 100)), 932, HZ - 20, 0.9); return to_img(a)
        def mid(img, t_, P):
            h, fx, fy = arjun((t_ * 1.9) % 1, run=1.0, scale=0.9)
            img.alpha_composite(h, (int(560 - fx), int(1560 - fy + 6 * abs(math.sin(t_ * 11)))))
            beat = int(tt / 0.6)
            img = put_chudail(img, 40 + beat * 70, 1500, scale=0.5, t=t_, eyes=1.0, lantern=False, aura=0.6)
            return img
        img = D_.frame(t, cam=cam, side=True, extra_back=back, extra_mid=mid)
        fog(img, t, 0.3, HZ - 100, HZ + 300, speed=70)
        return finish(img, t, VIG_H, push=1.04, cx=540, cy=1150, shake=0.15)
    return f


def make_bell(D, caps):
    D_ = desert()
    t1 = caps[1][1]
    ring = t1 + 1.2
    def f(t):
        dawn = ss(t, ring + 0.3, D)
        if t < t1 - 0.1:
            # running up to the temple; red eyes in the dark on both sides
            u = ss(t, 0, t1)
            tm, bxy, _ = temple(0.0)
            sc = 0.45 + 0.35 * u
            tms = tm.resize((int(tm.width * sc), int(tm.height * sc)), Image.LANCZOS)
            img = D_.frame(t, cam=0, kh=False, road=False, fg=False)
            img.alpha_composite(tms, (int(540 - tms.width / 2), int(HZ + 220 * sc + 60 - tms.height)))
            a = to_arr(img); add_glow(a, gsp(int(200 * sc), (255, 190, 100)), 540, HZ + 220 * sc + 60 - tms.height + 1000 * sc, 0.9); img = to_img(a)
            h, fx, fy = arjun((t * 1.9) % 1, run=1.0, back=True, scale=0.95 - 0.25 * u)
            img.alpha_composite(h, (int(540 - fx), int(1850 - 150 * u - fy)))
            for i, (ex, ey) in enumerate(((90, 1200), (1000, 1050), (160, 760))):
                if (t * 2 + i) % 3 < 2.2:
                    eye(img, ex, ey, 0.9, 0.5); eye(img, ex + 40, ey + 2, 0.9, 0.5)
            fog(img, t, 0.35, HZ - 100, HZ + 500, speed=20)
            return finish(img, t, VIG_H, push=1.03, cy=1100, shake=0.12)
        # at the temple: Arjun rings the bell; the sky turns grey and pink; she dissolves into the fog
        tm, bxy, fxy = temple(dawn)
        y = np.linspace(0, 1, H)[:, None, None]
        night = to_arr(D_.frame(t, cam=0, kh=False, road=False, fg=False))
        dsky = np.broadcast_to(np.array([120, 90, 110]) * (1 - y) + np.array([240, 150, 120]) * y, (H, W, 3))
        a = night * (1 - 0.75 * dawn) + dsky * 0.75 * dawn
        img = to_img(a)
        img.alpha_composite(tm, (90, 600))
        sw = 26 * math.sin((t - ring) * 7) * math.exp(-max(0, t - ring) * 0.7) if t > ring else 0
        b = bell_sprite(sw)
        img.alpha_composite(b, (90 + bxy[0] - 110, 600 + bxy[1] - 10))
        h, fx, fy = arjun(0.0, 0, back=True, scale=0.95)
        img.alpha_composite(h, (int(700 - fx), int(1900 - fy)))
        if t > ring:   # sound rings
            rl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rd = ImageDraw.Draw(rl)
            for k in range(3):
                r = ((t - ring) * 420 + k * 140) % 600
                al = int(160 * (1 - r / 600) * (1 - dawn * 0.5))
                rd.ellipse([90 + bxy[0] - r, 600 + bxy[1] + 200 - r, 90 + bxy[0] + r, 600 + bxy[1] + 200 + r], outline=(255, 220, 160, al), width=6)
            img.alpha_composite(rl)
        if t < ring + 1.4:
            k = 1 - ss(t, ring, ring + 1.4)
            img = put_chudail(img, 120, 1720, scale=0.6, t=t, eyes=k, lantern=False, aura=0.6 * k) if k > 0.6 else img
            if 0 < k <= 0.6:
                ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ghost = put_chudail(ghost, 120, 1720, scale=0.6, t=t, eyes=k, lantern=False, aura=0.3)
                img.alpha_composite(with_alpha(ghost, k / 0.6))
        fog(img, t, 0.35, 1100, 1900, speed=20, col=(200, 120, 110) if dawn > 0.5 else (140, 40, 40))
        return finish(img, t, VIG if dawn > 0.5 else VIG_H, push=1.02 + 0.04 * ss(t, ring, ring + 0.2), cy=1100, shake=0.3 * (1 - ss(t, ring, ring + 0.5)) if t > ring else 0)
    return f


def make_twist(D, caps):
    t1, t2 = caps[1][1], caps[2][1]
    jt = D - 1.0
    bg = door_bg(1.0)
    dd = dadi("door", smile=1)
    dd_red = dadi("door", eyes_red=1.0, smile=1)
    def f(t):
        if t < t2 - 0.1:
            img = bg.copy()
            img.alpha_composite(dd)
            u = ss(t, 0, t1)
            h, fx, fy = arjun(0.0, 0, back=True, scale=1.5 + 0.4 * ss(t, t1, t2))
            img.alpha_composite(h, (int(820 - 200 * ss(t, t1 - 0.6, t1 + 0.6) - fx), int(2150 - fy)))
            a = to_arr(img)
            add_glow(a, gsp(500, (255, 190, 130)), 540, 300, 0.6)
            return finish(to_img(a), t, VIG, push=1.0 + 0.06 * u + 0.08 * ss(t, t1, t2), cx=540, cy=900)
        if t < jt:
            # tilt down: below the white sari, BACKWARD feet with anklets on the threshold
            tt = t - (t2 - 0.1)
            img = bg.copy()
            d = ImageDraw.Draw(img)
            d.rectangle([0, 1500, W, H], fill=(70, 40, 30, 255))
            ft = feet_closeup(0.0, hem=(214, 206, 196), border=(170, 30, 30), step=False)
            img.alpha_composite(ft, (-60, 1000))
            return finish(img, t, VIG_H, push=1.15 + 0.15 * ss(tt, 0, jt - t2), cx=480, cy=1500 + 80 * ss(tt, 0, 1.2))
        img = bg.copy()
        img.alpha_composite(dd_red)
        fl = 0.85 if t < jt + 0.08 else 0.0
        return finish(img, t, VIG_H, push=1.6 + 0.6 * ss(t, jt, jt + 0.2), cx=540, cy=720, shake=1.0, flash=fl, flash_col=(255, 30, 20))
    return f


def make_explain(D, caps):
    D_ = desert()
    title = text_img("THE CHUDAIL", font(LORA, 116, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("India's most feared ghost  ·  also Churel / Churail", font(INTER_SB, 38), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("Spirit of a woman who died in childbirth", pf, fill=(110, 20, 24, 235), h=80),
             pill("...or who was treated cruelly", pf, fill=(110, 20, 24, 235), h=80),
             pill("Her feet point BACKWARDS", pf, fill=(110, 20, 24, 235), h=80),
             pill("Calls men by name on lonely roads", pf, fill=(110, 20, 24, 235), h=80)]
    ts = [caps[1][1], caps[1][1] + 2.0, caps[2][1], caps[2][1] + 2.0]
    def f(t):
        def front(img, tt, P):
            return put_chudail(img, 700, 1640, scale=0.72, t=tt, eyes=1.0, lamp=1.0, aura=0.5)
        img = D_.frame(t, cam=-20 + 20 * t / D, tree_x=-200, extra_front=front, road=False)
        fog(img, t, 0.35, HZ - 100, HZ + 500)
        a = finish(img, t, vig=VIG_H, push=1.0)
        out = to_img(a * 0.8)
        fw = flag_wave(t, 150)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 70))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 170))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 330))
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.2, tt + 0.3)
            if k > 0:
                cc = c if c.width <= W - 40 else c.resize((W - 40, int(c.height * (W - 40) / c.width)), Image.LANCZOS)
                out.alpha_composite(with_alpha(cc, k), (int(W / 2 - cc.width / 2), int(430 + i * 96 + 14 * (1 - k))))
        return to_arr(out)
    return f


def make_outro(D, caps):
    D_ = desert()
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("have answered?", font(LORA, 100, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Answer", (120, 25, 25, 235)), ("Look at her feet", (60, 40, 40, 235)), ("Keep walking", (140, 70, 20, 235)), ("RUN!", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    def f(t):
        def front(img, tt, P):
            return put_chudail(img, 300, HZ + 300, scale=0.3, t=tt, eyes=1.0, lamp=1.0, aura=0.4)
        img = D_.frame(t, cam=0, tree_x=-260, tree_scale=0.8, extra_front=front)
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
