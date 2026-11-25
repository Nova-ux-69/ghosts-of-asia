"""Ep13 Japan / Hanako-san - art: the world, the characters and the ghost (2.1D flat21 style).
New world: an old three-storey wooden Showa-era schoolhouse in the countryside at dusk under a blood-red evening sky
(cedar trees, a stone gate post, rusty bicycles, a broken clock on the facade, one red-lit window on the third floor);
a long wooden corridor with sliding windows throwing red sunset shafts across polished floorboards; an old tiled girls'
bathroom (three wooden stall doors, a cracked mirror over a row of sinks, a flickering bare bulb); a classroom seen from
under a desk; a blackboard that writes by itself; a wooden stairwell with a 3F plate; Yui's bedroom with her phone.
Ghost: Hanako-san - a small girl with a black bob (okappa) haircut over her eyes, white blouse, red suspender skirt,
red shoes, pale skin, head tilted at a wrong angle, glowing red eyes. No gore."""
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



SKIN = (196, 140, 104)        # Yui
PALE = (214, 210, 204)        # Hanako
HAIR = (12, 10, 12)
NAVY = (30, 34, 58)           # sailor uniform
SCARF = (200, 30, 34)
SKIRT = (168, 22, 26)         # Hanako's red skirt
BLOUSE = (220, 214, 206)
WOOD = (96, 52, 30)
WOOD_D = (52, 26, 16)
VIG = vignette(0.85)
VIG_H = vignette(1.05)
GR = [np.random.default_rng(i).normal(0, 5, (H, W, 1)).astype(np.float32) for i in range(6)]
FOGT = fog_texture(W + 700, H, 113)

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


JP_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
JP_SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"


def jfont(size, serif=False):
    from PIL import ImageFont
    return ImageFont.truetype(JP_SERIF if serif else JP_FONT, size, index=0)


# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """Japan (Nisshoki): white field with a red disc in the centre (diameter 3/5 of the height)."""
    global _FLAG
    if _FLAG is None:
        w, h, s = 300, 200, 3
        im = Image.new("RGBA", (w * s, h * s), (246, 244, 238, 255)); d = ImageDraw.Draw(im)
        cx, cy, r = w * s / 2, h * s / 2, h * s * 0.3
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(188, 0, 45, 255))
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
        fw = flag_wave(t)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 40))


def timer_ui(sec, t, k=1.0, floor="3F"):
    """The ticking clock: the dare stopwatch on Yui's phone (counts down from 3:00, red under 1:00, blinks at 0:00)."""
    sec = max(0.0, sec)
    f1 = font(INTER_SB, 46); f2 = font(INTER_M, 28)
    w, h = 600, 108
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(0, 0, 0, int(185 * k)), outline=(255, 70, 50, int(200 * k)), width=3)
    low = sec < 60
    blink = (math.sin(t * 9) > -0.2) if sec < 20 else True
    red = (255, 70, 50, int(255 * k * (1 if blink else 0.25)))
    wht = (255, 240, 228, int(240 * k))
    col = red if low else wht
    # stopwatch icon
    cx, cy = 62, 58
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=col, width=5)
    d.rectangle([cx - 7, cy - 42, cx + 7, cy - 32], fill=col)
    a = -math.pi / 2 + 2 * math.pi * (1 - sec / 180)
    d.line([(cx, cy), (cx + 20 * math.cos(a), cy + 20 * math.sin(a))], fill=col, width=5)
    d.text((165, h / 2), "DARE", font=f2, fill=(255, 190, 140, int(255 * k)), anchor="mm")
    m, s_ = int(sec) // 60, int(sec) % 60
    d.text((300, h / 2), f"{m}:{s_:02d}", font=f1, fill=col, anchor="mm")
    d.line([(400, 22), (400, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    d.text((500, h / 2 - 17), "FLOOR", font=f2, fill=(255, 190, 140, int(255 * k)), anchor="mm")
    d.text((500, h / 2 + 20), floor, font=f1, fill=wht, anchor="mm")
    return im


def put_timer(out, sec, t, k=1.0, floor="3F", y=170):
    ui = timer_ui(sec, t, k, floor)
    out.alpha_composite(ui, (int(W / 2 - ui.width / 2), y))


# ============================================================ Yui (sailor uniform, ponytail, phone with a torch)
_YC = {}


def yui(phase=0.0, run=0.0, back=False, scale=1.0, phone=True):
    """Yui: black hair in a ponytail, navy sailor uniform (white-striped collar, red scarf), navy pleated skirt,
    white socks, black loafers, phone in her right hand. Returns (RGBA, feet_x, feet_y, phone_xy)."""
    q = (round(phase * 12) % 12, round(run, 1), back, round(scale, 2), phone)
    if q in _YC:
        return _YC[q]
    w, h = 460, 900
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.3 + 0.7 * run)
    lean = 14 * run

    def leg_pts(sg):
        a = sg * sw * 0.55
        hx, hy = cx + lean * 0.3 + sg * 20, 520
        kx, ky = hx + math.sin(a) * 120, hy + math.cos(a) * 150
        fx, fy = kx + math.sin(a - 0.35 * run) * 100, ky + 140
        return (hx, hy), (kx, ky), (fx, fy)

    def legs(d, s):
        for sg in (-1, 1):
            p = leg_pts(sg)
            d.line([(x * s, y * s) for x, y in p], fill=255, width=int(30 * s), joint="curve")

    def socks(d, s):
        for sg in (-1, 1):
            (_, _), (kx, ky), (fx, fy) = leg_pts(sg)
            mx, my = kx + (fx - kx) * 0.45, ky + (fy - ky) * 0.45
            d.line([(mx * s, my * s), (fx * s, fy * s)], fill=255, width=int(32 * s))

    def shoes(d, s):
        for sg in (-1, 1):
            fx, fy = leg_pts(sg)[2]
            d.ellipse([(fx - 28) * s, (fy - 8) * s, (fx + 32) * s, (fy + 14) * s], fill=255)

    def skirt(d, s):
        L = lean * 0.5
        d.polygon(P_((cx - 68 + L, 380), (cx + 68 + L, 380), (cx + 108 + L - 20 * sw, 570), (cx - 108 + L - 20 * sw, 570), s=s), fill=255)

    def torso(d, s):
        L = lean
        d.polygon(P_((cx - 70 + L, 200), (cx + 70 + L, 200), (cx + 66 + L * .6, 400), (cx - 66 + L * .6, 400), s=s), fill=255)
        d.ellipse([(cx - 80 + L) * s, 188 * s, (cx - 36 + L) * s, 252 * s], fill=255)
        d.ellipse([(cx + 36 + L) * s, 188 * s, (cx + 80 + L) * s, 252 * s], fill=255)

    hands = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 64 + lean, 218
        a = -sg * sw * 0.9
        hold = sg == 1 and phone and run < 0.5
        if hold:
            a = 0.25
        ex, ey = sx + math.sin(a) * 86 + sg * 8, sy + math.cos(a) * 100
        b = a - 0.9 * run * sg - (2.0 if hold else 0)
        hx, hy = ex + math.sin(b) * 86, ey + math.cos(b) * 80 - 40 * run
        hands[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            pts = hands[sg]
            d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(22 * s), joint="curve")
            hx, hy = pts[2]
            d.ellipse([(hx - 14) * s, (hy - 14) * s, (hx + 14) * s, (hy + 14) * s], fill=255)

    def sleeves(d, s):
        for sg in (-1, 1):
            (sx, sy), (ex, ey), (hx, hy) = hands[sg]
            mx, my = ex + (hx - ex) * 0.55, ey + (hy - ey) * 0.55
            d.line([(sx * s, sy * s), (ex * s, ey * s), (mx * s, my * s)], fill=255, width=int(36 * s), joint="curve")

    def head(d, s):
        L = lean * 1.2
        d.rectangle([(cx - 17 + L) * s, 150 * s, (cx + 17 + L) * s, 205 * s], fill=255)
        d.ellipse([(cx - 48 + L) * s, 44 * s, (cx + 48 + L) * s, 172 * s], fill=255)

    def hair(d, s):
        L = lean * 1.2
        d.pieslice([(cx - 54 + L) * s, 30 * s, (cx + 54 + L) * s, 150 * s], 180, 360, fill=255)
        # side locks
        d.polygon(P_((cx - 54 + L, 90), (cx - 58 + L, 170), (cx - 40 + L, 160), (cx - 36 + L, 96), s=s), fill=255)
        d.polygon(P_((cx + 54 + L, 90), (cx + 58 + L, 170), (cx + 40 + L, 160), (cx + 36 + L, 96), s=s), fill=255)
        # bangs
        d.polygon(P_((cx - 54 + L, 92), (cx - 50 + L, 52), (cx + 50 + L, 52), (cx + 54 + L, 92), (cx + 28 + L, 82), (cx + 6 + L, 98),
                     (cx - 20 + L, 82), s=s), fill=255)
        # ponytail swinging behind
        pt = 30 + 30 * math.sin(ph + 1) * (0.3 + run)
        d.ellipse([(cx + 30 + L) * s, 40 * s, (cx + 70 + L) * s, 80 * s], fill=255)
        d.polygon(P_((cx + 46 + L, 60), (cx + 80 + L + pt * 0.3, 90), (cx + 74 + L + pt, 230), (cx + 54 + L + pt * 0.8, 236), (cx + 50 + L, 110), s=s), fill=255)
        if back:
            d.ellipse([(cx - 50 + L) * s, 38 * s, (cx + 50 + L) * s, 160 * s], fill=255)
            d.polygon(P_((cx - 26 + L, 80), (cx + 26 + L, 80), (cx + 30 + L + pt * 0.2, 250), (cx - 10 + L + pt * 0.2, 256), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), SKIN, 14))
    img.alpha_composite(shade(socks, (w, h), (226, 222, 214), 10))
    img.alpha_composite(shade(shoes, (w, h), (24, 16, 16), 6))
    sk = shade(skirt, (w, h), NAVY, 30)
    sk = texmul(sk, lambda xx, yy: 1 - 0.3 * ((np.abs((xx - cx) % 34) < 4) & (yy > 410)))       # pleats
    img.alpha_composite(sk)
    img.alpha_composite(shade(arms, (w, h), SKIN, 10))
    img.alpha_composite(shade(torso, (w, h), NAVY, 36))
    img.alpha_composite(shade(sleeves, (w, h), NAVY, 14))
    d = ImageDraw.Draw(img)
    L = lean
    if back:
        # the big square sailor collar on the back, with white stripes
        d.polygon([(cx - 76 + L, 196), (cx + 76 + L, 196), (cx + 70 + L, 320), (cx - 70 + L, 320)], fill=(36, 40, 70, 255))
        for k in (10, 20):
            d.line([(cx - 76 + L + k, 320 - k), (cx + 70 + L - k, 320 - k)], fill=(225, 220, 212, 255), width=4)
            d.line([(cx - 70 + L + k, 320 - k), (cx - 76 + L + k, 198)], fill=(225, 220, 212, 255), width=4)
            d.line([(cx + 70 + L - k, 320 - k), (cx + 76 + L - k, 198)], fill=(225, 220, 212, 255), width=4)
    else:
        # V collar with white stripes + the red scarf bow
        d.polygon([(cx - 60 + L, 200), (cx + L, 300), (cx + 60 + L, 200), (cx + 40 + L, 200), (cx + L, 268), (cx - 40 + L, 200)], fill=(225, 220, 212, 255))
        d.polygon([(cx + L, 286), (cx - 34 + L, 270), (cx - 30 + L, 316), (cx + L, 300), (cx + 30 + L, 316), (cx + 34 + L, 270)], fill=SCARF + (255,))
        d.polygon([(cx - 8 + L, 300), (cx + 8 + L, 300), (cx + 14 + L, 360), (cx - 14 + L, 360)], fill=(170, 22, 26, 255))
    img.alpha_composite(shade(head, (w, h), SKIN, 26))
    img.alpha_composite(shade(hair, (w, h), HAIR, 14, rim_strength=1.1))
    d = ImageDraw.Draw(img)
    Lh = lean * 1.2
    if not back:
        for sg in (-1, 1):
            d.ellipse([cx + sg * 19 - 9 + Lh, 104, cx + sg * 19 + 9 + Lh, 120], fill=(240, 236, 230, 255))
            d.ellipse([cx + sg * 19 - 4 + Lh, 107, cx + sg * 19 + 4 + Lh, 117], fill=(15, 10, 10, 255))
        d.ellipse([cx - 6 + Lh, 142, cx + 6 + Lh, 150], fill=(120, 40, 40, 255))
    px, py = hands[1][2]
    if phone and run < 0.5 and not back:
        d.rounded_rectangle([px - 14, py - 34, px + 14, py + 14], 5, fill=(20, 20, 26, 255), outline=(90, 90, 100, 255), width=2)
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 836 * scale, (px * scale, (py - 30) * scale))
    _YC[q] = out
    return out


_YF = {}


def yui_face(look=0.0, mouth=0.0, side=0.0):
    """Close-up: Yui's head and shoulders (sailor collar), eyes wide. look -1..1 moves the pupils sideways."""
    key = (round(look, 1), round(mouth, 1))
    if key in _YF:
        return _YF[key]
    w, h = 1080, 1300
    cx = 520

    def body(d, s):
        d.polygon(P_((cx - 380, 1300), (cx - 320, 1010), (cx - 120, 930), (cx + 120, 930), (cx + 320, 1010), (cx + 380, 1300), s=s), fill=255)

    def neck(d, s):
        d.rectangle([(cx - 64) * s, 760 * s, (cx + 64) * s, 960 * s], fill=255)

    def head(d, s):
        d.ellipse([(cx - 180) * s, 300 * s, (cx + 180) * s, 830 * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 200) * s, 250 * s, (cx + 200) * s, 700 * s], 180, 360, fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 200, 470), (cx + sg * 214, 900), (cx + sg * 150, 880), (cx + sg * 150, 500), s=s), fill=255)
        d.polygon(P_((cx - 200, 480), (cx - 190, 380), (cx + 190, 380), (cx + 200, 480), (cx + 110, 470), (cx + 40, 510),
                     (cx - 40, 470), (cx - 120, 500), s=s), fill=255)
        d.ellipse([(cx + 120) * s, 230 * s, (cx + 260) * s, 360 * s], fill=255)            # ponytail tie
        d.polygon(P_((cx + 200, 300), (cx + 330, 420), (cx + 330, 1100), (cx + 230, 1100), (cx + 220, 500), s=s), fill=255)

    lt = dict(rim=(255, 70, 50))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(body, (w, h), NAVY, 90, **lt))
    d = ImageDraw.Draw(img)
    d.polygon([(cx - 260, 980), (cx, 1300), (cx + 260, 980), (cx + 200, 960), (cx, 1220), (cx - 200, 960)], fill=(225, 220, 212, 255))
    d.polygon([(cx, 1230), (cx - 110, 1190), (cx - 100, 1300), (cx + 100, 1300), (cx + 110, 1190)], fill=SCARF + (255,))
    img.alpha_composite(shade(neck, (w, h), SKIN, 30, **lt))
    img.alpha_composite(shade(head, (w, h), SKIN, 110, **lt))
    img.alpha_composite(shade(hair, (w, h), HAIR, 40, **lt))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ex, ey = cx + sg * 76, 600
        d.ellipse([ex - 42, ey - 28, ex + 42, ey + 32], fill=(240, 234, 226, 255))
        px = 14 * look
        d.ellipse([ex - 15 + px, ey - 12, ex + 15 + px, ey + 18], fill=(14, 9, 9, 255))
        d.ellipse([ex - 4 + px + 6, ey - 8, ex + 4 + px + 6, ey], fill=(255, 230, 200, 255))
        d.line([(ex - 44, ey - 64), (ex + 40, ey - 70 - sg * 6)], fill=(18, 10, 10, 255), width=12)
    d.line([(cx - 4, 640), (cx + 10, 690)], fill=(150, 96, 70, 255), width=6)
    d.ellipse([cx - 28, 740 - 4 * mouth, cx + 28, 752 + 36 * mouth], fill=(90, 26, 26, 255))
    _YF[key] = img
    return img


_YCR = {}


def yui_crouch(scale=1.0, look=0.0):
    """Yui curled up under a desk, knees up, both hands over her mouth. look 0 = forward, 1 = toward the right."""
    key = (round(scale, 2), round(look, 1))
    if key in _YCR:
        return _YCR[key]
    w, h = 460, 560
    cx = 210

    def body(d, s):
        d.polygon(P_((130, 230), (290, 230), (320, 420), (320, 520), (110, 520), (100, 400), s=s), fill=255)

    def knees(d, s):
        d.polygon(P_((200, 300), (360, 290), (360, 420), (330, 530), (270, 530), (240, 420), s=s), fill=255)

    def head(d, s):
        d.ellipse([(cx - 46) * s, 70 * s, (cx + 46) * s, 186 * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 52) * s, 58 * s, (cx + 52) * s, 162 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 52, 112), (cx - 50, 82), (cx + 50, 82), (cx + 52, 112), (cx + 10, 100), s=s), fill=255)
        d.polygon(P_((cx - 40, 70), (cx - 110, 120), (cx - 120, 260), (cx - 80, 250), (cx - 40, 130), s=s), fill=255)

    def hands(d, s):
        d.ellipse([(cx - 30) * s, 142 * s, (cx + 26) * s, 182 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(body, (w, h), NAVY, 40))
    img.alpha_composite(shade(knees, (w, h), SKIN, 30))
    img.alpha_composite(shade(lambda d, s: d.polygon(P_((190, 300), (370, 296), (360, 420), (200, 420), s=s), fill=255), (w, h), NAVY, 20))
    img.alpha_composite(shade(lambda d, s: d.line([(160 * s, 250 * s), (240 * s, 330 * s), (330 * s, 320 * s)], fill=255, width=int(30 * s), joint="curve"), (w, h), NAVY, 10))
    img.alpha_composite(shade(head, (w, h), SKIN, 26))
    img.alpha_composite(shade(hair, (w, h), HAIR, 14))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ey = 118
        d.ellipse([cx + sg * 18 - 10, ey, cx + sg * 18 + 10, ey + 17], fill=(240, 236, 230, 255))
        px = 4 * look + 1
        d.ellipse([cx + sg * 18 - 4 + px, ey + 4, cx + sg * 18 + 4 + px, ey + 12], fill=(15, 10, 10, 255))
    img.alpha_composite(shade(hands, (w, h), SKIN, 10))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 530 * scale)
    _YCR[key] = out
    return out


# ============================================================ Hanako-san
_HN = {}


def hanako(tilt=0.0, step=0, wave=0.0, reach=0.0):
    """Full body, facing us, ~930 px tall: black bob with straight bangs over the eyes, white short-sleeved blouse,
    red suspender skirt, too-long thin pale arms, white socks, red shoes. tilt = head angle (deg, wrong angle),
    step = 0/1 jerky stop-motion leg pose, wave 0..1 = right hand raised waving, reach 0..1 = both arms forward/up.
    Returns (RGBA, feet_x, feet_y, [eye1, eye2])."""
    key = (round(tilt), step % 2, round(wave, 1), round(reach, 1))
    if key in _HN:
        return _HN[key]
    w, h = 460, 1000
    cx = 230
    ang = math.radians(tilt)
    nx, ny = cx, 245

    def R(*pts):
        return rot(pts, ang, nx, ny)

    def legs(d, s):
        for sg in (-1, 1):
            off = (14 if (step % 2) == (sg > 0) else -4)
            d.line([((cx + sg * 30) * s, 540 * s), ((cx + sg * 34 + off * 0.3) * s, 740 * s), ((cx + sg * 36 + off) * s, 920 * s)], fill=255, width=int(24 * s), joint="curve")

    def socks(d, s):
        for sg in (-1, 1):
            off = (14 if (step % 2) == (sg > 0) else -4)
            d.line([((cx + sg * 35 + off * 0.6) * s, 830 * s), ((cx + sg * 36 + off) * s, 920 * s)], fill=255, width=int(27 * s))

    def shoes(d, s):
        for sg in (-1, 1):
            off = (14 if (step % 2) == (sg > 0) else -4)
            x = cx + sg * 36 + off
            d.ellipse([(x - 26) * s, 908 * s, (x + 26) * s, 940 * s], fill=255)

    def blouse(d, s):
        d.polygon(P_((cx - 70, 262), (cx + 70, 262), (cx + 76, 420), (cx - 76, 420), s=s), fill=255)
        d.ellipse([(cx - 100) * s, 256 * s, (cx - 40) * s, 330 * s], fill=255)          # puff sleeves
        d.ellipse([(cx + 40) * s, 256 * s, (cx + 100) * s, 330 * s], fill=255)

    def skirt(d, s):
        d.polygon(P_((cx - 76, 390), (cx + 76, 390), (cx + 128, 580), (cx - 128, 580), s=s), fill=255)

    def straps(d, s):
        for sg in (-1, 1):
            d.line([((cx + sg * 44) * s, 400 * s), ((cx + sg * 40) * s, 262 * s)], fill=255, width=int(16 * s))

    arm_pts = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 80, 296
        if sg == 1 and wave > 0:
            ex, ey = sx + 90, sy - 60 * wave + 80 * (1 - wave)
            hx, hy = ex + 20 * math.sin(wave * 9), ey - 200 * wave + 150 * (1 - wave)
        elif reach > 0:
            ex, ey = sx + sg * 20, sy + 170 - 90 * reach
            hx, hy = ex - sg * 10, ey + 220 - 300 * reach
        else:
            ex, ey = sx + sg * 26, sy + 220
            hx, hy = sx + sg * 30, sy + 470                     # far too long: the hands hang to her knees
        arm_pts[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            p = arm_pts[sg]
            d.line([(x * s, y * s) for x, y in p], fill=255, width=int(17 * s), joint="curve")
            (ex, ey), (hx, hy) = p[1], p[2]
            vx, vy = hx - ex, hy - ey; n = math.hypot(vx, vy) + 1e-6; vx, vy = vx / n, vy / n
            for k in range(4):                                           # long thin fingers
                a = math.atan2(vy, vx) + (k - 1.5) * 0.16
                d.line([(hx * s, hy * s), ((hx + math.cos(a) * 64) * s, (hy + math.sin(a) * 64) * s)], fill=255, width=int(7 * s))

    def head(d, s):
        d.polygon(P_(*R(*[(cx + 74 * math.cos(a), 150 + 86 * math.sin(a) * (1.1 if math.sin(a) > 0 else 1.0))
                          for a in np.linspace(0, 2 * math.pi, 32)]), s=s), fill=255)
        d.polygon(P_(*R((cx - 22, 220), (cx + 22, 220), (cx + 22, 270), (cx - 22, 270)), s=s), fill=255)

    def bob(d, s):
        # the okappa bob: round crown, straight-cut bangs over the eyes, straight-cut sides at the jaw
        top = [(cx + 96 * math.cos(a), 140 + 104 * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 20)]
        pts = top + [(cx + 98, 150), (cx + 100, 246), (cx + 62, 246), (cx + 62, 172), (cx - 62, 172), (cx - 62, 246), (cx - 100, 246), (cx - 98, 150)]
        d.polygon(P_(*R(*pts), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), PALE, 10, rim_strength=1.0))
    img.alpha_composite(shade(socks, (w, h), (230, 226, 220), 8))
    img.alpha_composite(shade(shoes, (w, h), (176, 14, 20), 8, rim_strength=1.2))
    img.alpha_composite(shade(blouse, (w, h), BLOUSE, 30))
    img.alpha_composite(shade(skirt, (w, h), SKIRT, 34, rim_strength=1.1))
    img.alpha_composite(shade(straps, (w, h), SKIRT, 6))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        d.ellipse([cx + sg * 44 - 7, 392, cx + sg * 44 + 7, 406], fill=(230, 210, 160, 255))     # buttons
    img.alpha_composite(shade(arms, (w, h), PALE, 8, rim_strength=1.0))
    img.alpha_composite(shade(head, (w, h), PALE, 44, rim_strength=0.8))
    img.alpha_composite(shade(bob, (w, h), HAIR, 24, rim_strength=1.4))
    d = ImageDraw.Draw(img)
    eyes = [R((cx - 30, 184))[0], R((cx + 30, 184))[0]]
    for ex, ey in eyes:                                                   # hollow dark eyes just under the bangs
        d.ellipse([ex - 15, ey - 9, ex + 15, ey + 11], fill=(20, 8, 10, 255))
    mx, my = R((cx, 228))[0]
    d.ellipse([mx - 9, my - 5, mx + 9, my + 8], fill=(40, 10, 14, 255))
    out = (img, cx, 930, eyes)
    _HN[key] = out
    return out


def put_hanako(img, x, y, scale, t, eyes=1.0, tilt=0.0, step=0, wave=0.0, reach=0.0, aura=0.5, alpha=1.0, sway=True):
    """Hanako standing with her feet at (x, y). Soft red aura, pulsing red eyes."""
    body, fx, fy, ee = hanako(tilt, step, wave, reach)
    rr = 1.0 * math.sin(t * 0.9) if sway else 0
    g = body.rotate(rr, resample=Image.BICUBIC, center=(fx, fy)) if rr else body
    g = g.resize((max(1, int(g.width * scale)), max(1, int(g.height * scale))), Image.LANCZOS)
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
            eye(img, gx + ex * scale, gy + ey * scale, k, max(0.22, scale * 0.7))
    return img


_HF = {}


def hanako_face(mouth=0.0):
    """Jump-scare close-up: a pale little face framed by a heavy black bob, bangs cut straight over hollow eyes."""
    key = round(mouth, 1)
    if key in _HF:
        return _HF[key]
    w, h = 900, 1200
    cx, cy = 450, 560

    def hair(d, s):
        d.pieslice([(cx - 300) * s, 40 * s, (cx + 300) * s, 760 * s], 180, 360, fill=255)
        d.rectangle([(cx - 300) * s, 398 * s, (cx + 300) * s, 900 * s], fill=255)

    def face(d, s):
        d.ellipse([(cx - 200) * s, 250 * s, (cx + 200) * s, 860 * s], fill=255)

    def bangs(d, s):
        top = [(cx + 280 * math.cos(a), 400 + 330 * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 24)]
        d.polygon(P_(*top, (cx + 286, 420), (cx + 240, 520), (cx - 240, 520), (cx - 286, 420), s=s), fill=255)
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 300, 420), (cx + sg * 300, 900), (cx + sg * 180, 900), (cx + sg * 190, 520), s=s), fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(hair, (w, h), HAIR, 40, rim_strength=1.3))
    img.alpha_composite(shade(face, (w, h), PALE, 90, rim_strength=0.7))
    d = ImageDraw.Draw(img)
    e1, e2 = (cx - 80, 590), (cx + 80, 590)
    for ex, ey in (e1, e2):
        d.ellipse([ex - 56, ey - 40, ex + 56, ey + 40], fill=(18, 6, 8, 255))
        d.arc([ex - 62, ey + 20, ex + 62, ey + 66], 20, 160, fill=(160, 150, 150, 255), width=5)
    d.polygon([(cx - 34, 760), (cx + 34, 760), (cx + 22, 776 + 70 * mouth), (cx - 22, 776 + 70 * mouth)], fill=(30, 8, 12, 255))
    img.alpha_composite(shade(bangs, (w, h), HAIR, 30, rim_strength=1.5))
    d = ImageDraw.Draw(img)
    for k in range(9):                                                   # straight-cut fringe strands
        x = cx - 220 + k * 55
        d.line([(x, 440), (x + 4, 524)], fill=(40, 30, 34, 255), width=3)
    out = (img, e1, e2)
    _HF[key] = out
    return out


def put_hface(img, x, y, scale, t, eyes=1.0, mouth=0.0, tilt=0.0, aura=0.7, alpha=1.0):
    fc, e1, e2 = hanako_face(mouth)
    g = fc.rotate(tilt, resample=Image.BICUBIC, center=(450, 560))
    g = g.resize((max(1, int(g.width * scale)), max(1, int(g.height * scale))), Image.LANCZOS)
    if alpha < 1:
        g = with_alpha(g, alpha)
    gx, gy = int(x - 450 * scale), int(y - 560 * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(30))
        lay = Image.new("RGBA", g.size, (255, 40, 30, 0)); lay.putalpha(al.point(lambda v: int(v * aura)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    k = eyes * (0.75 + 0.25 * math.sin(t * 6) ** 2) * alpha
    ca, sa = math.cos(math.radians(-tilt)), math.sin(math.radians(-tilt))
    for ex, ey in (e1, e2):
        dx, dy = ex - 450, ey - 560
        eye(img, x + (dx * ca - dy * sa) * scale, y + (dx * sa + dy * ca) * scale, k, 1.5 * scale)
    return img


# ============================================================ world helpers
def vgrad(top, mid, bot, ym=0.5, w=W, h=H):
    y = np.linspace(0, 1, h)[:, None]
    top, mid, bot = (np.array(c, np.float32) for c in (top, mid, bot))
    k1 = np.clip(y / ym, 0, 1); k2 = np.clip((y - ym) / (1 - ym), 0, 1)
    col = np.where(y < ym, top * (1 - k1) + mid * k1, mid * (1 - k2) + bot * k2)
    return np.broadcast_to(col[:, None, :], (h, w, 3)).astype(np.float32).copy()


def cedar(d, s, x, by, h, wd, seed):
    """Japanese cedar (sugi): a tall narrow spire built from layered drooping tiers."""
    r = np.random.default_rng(seed)
    d.line([(x * s, by * s), (x * s, (by - h) * s)], fill=255, width=int(max(4, wd * 0.12) * s))
    n = 9
    for k in range(n):
        u = k / (n - 1)
        yk = by - h * (0.18 + 0.82 * u)
        ww = wd * (1 - u * 0.85) * r.uniform(0.85, 1.1)
        d.polygon(P_((x - ww, yk + h * 0.1), (x, yk - h * 0.07), (x + ww, yk + h * 0.1), (x + ww * 0.6, yk + h * 0.06), (x, yk + h * 0.04),
                     (x - ww * 0.6, yk + h * 0.06), s=s), fill=255)


class Persp:
    """One-point perspective: side (+ right), hgt (+ down from the eye), z (depth)."""
    def __init__(self, vx, vy, f):
        self.vx, self.vy, self.f = vx, vy, f

    def p(self, side, hgt, z):
        return (self.vx + side * self.f / z, self.vy + hgt * self.f / z)

    def quad(self, d, pts, fill):
        d.polygon([self.p(*q) for q in pts], fill=fill)

    def scale_at(self, z, units, px):
        """sprite scale so that a sprite px tall is `units` tall at depth z"""
        return units * self.f / z / px


# ============================================================ the school (outside)
GY = 1300


class School:
    """The old three-storey wooden schoolhouse under a blood-red evening sky (night=1: red moon, darker)."""
    def __init__(self, night=0.0):
        self.night = night
        if night < 0.5:
            a = vgrad((6, 2, 4), (96, 12, 16), (224, 70, 34), ym=0.42)
            yy, xx = np.mgrid[0:H, 0:W]
            sx, sy = 300, 1150
            dd = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2)
            a += (np.exp(-dd / 380) * 160)[..., None] * np.array([1.0, 0.35, 0.18])
            sun = np.clip((150 - dd) / 2, 0, 1)
            a = a * (1 - sun[..., None]) + np.array([255, 120, 70]) * sun[..., None]
            for yc, th in ((520, 30), (640, 22), (760, 40), (980, 26)):                # long dark cloud streaks
                cl = fog_texture(W, H, yc) * np.exp(-((yy - yc) / th) ** 2)
                a = a * (1 - 0.7 * cl[..., None]) + np.array([30, 6, 8]) * 0.7 * cl[..., None]
        else:
            a = vgrad((3, 1, 2), (40, 6, 9), (96, 18, 16), ym=0.45)
            yy, xx = np.mgrid[0:H, 0:W]
            mx, my = 820, 420
            dd = np.sqrt((xx - mx) ** 2 + (yy - my) ** 2)
            a += (np.exp(-dd / 260) * 130)[..., None] * np.array([1.0, 0.3, 0.2])
            moon = np.clip((96 - dd) / 2, 0, 1)
            a = a * (1 - moon[..., None]) + (np.array([236, 104, 70]) * (0.8 + 0.3 * fog_texture(W, H, 7))[..., None]) * moon[..., None]
        sky = to_img(a)
        # far: a ridge of cedar forest (blurred)
        def far(d, s):
            d.polygon(P_((0, 1080), (200, 1020), (420, 1060), (700, 1000), (W, 1050), (W, GY), (0, GY), s=s), fill=255)
            for i, x in enumerate(range(-20, W + 60, 52)):
                cedar(d, s, x + (i * 17) % 23, 1080 - 20 * math.sin(i), 200 + (i * 37) % 90, 34, 50 + i)
        fl = inflate21(D5.smooth_mask(far, (W, H)), (50, 12, 12) if night < 0.5 else (34, 8, 9), radius=8, rim_strength=0.4)
        sky.alpha_composite(dof(fl, 3))
        self.sky = sky
        # the school building
        self.windows = []
        b = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        x0, x1, top = 130, 990, 860

        def walls(d, s):
            d.rectangle([x0 * s, top * s, x1 * s, GY * s], fill=255)

        bw = shade(walls, (W, H), (70, 34, 22), 20, rim_strength=0.6)
        bw = texmul(bw, lambda xx, yy: 0.85 + 0.15 * ((yy % 18) > 3))                             # wooden siding
        b.alpha_composite(bw)

        def roof(d, s):
            d.polygon(P_((x0 - 50, top + 10), (x0 + 60, top - 110), (x1 - 60, top - 110), (x1 + 50, top + 10), s=s), fill=255)
            d.polygon(P_((470, top - 100), (560, top - 190), (650, top - 100), s=s), fill=255)            # small central gable
        rf = shade(roof, (W, H), (34, 22, 26), 18, rim_strength=1.0)
        rf = texmul(rf, lambda xx, yy: 0.8 + 0.2 * ((yy % 16) > 3))
        b.alpha_composite(rf)
        d = ImageDraw.Draw(b)
        # the stopped clock on the gable: 4:44
        cx, cy = 560, top - 92
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(200, 186, 160, 255), outline=(30, 16, 12, 255), width=6)
        for ang, ln, wd in ((-math.pi / 2 + 2 * math.pi * (4 + 44 / 60) / 12, 22, 6), (-math.pi / 2 + 2 * math.pi * 44 / 60, 32, 4)):
            d.line([(cx, cy), (cx + ln * math.cos(ang), cy + ln * math.sin(ang))], fill=(30, 12, 10, 255), width=wd)
        # windows: 3 floors x 6
        for fl_ in range(3):
            yb = GY - 30 - fl_ * 150
            for i in range(6):
                if fl_ == 0 and i in (2, 3):
                    continue
                wx = x0 + 40 + i * 140
                d.rectangle([wx, yb - 104, wx + 100, yb], fill=(36, 14, 12, 255))
                self.windows.append((wx, yb - 104, wx + 100, yb, fl_, i))
        self.glass = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(self.glass)
        for wx, y0, wx1, y1, fl_, i in self.windows:
            k = 1 - (y0 - 860) / 500
            refl = (int(110 + 60 * k), int(24 + 14 * k), int(18 + 8 * k), 255) if night < 0.5 else (34, 8, 10, 255)
            if fl_ == 2 and i == 5:
                refl = (160, 20, 18, 255)                               # the 3rd-floor bathroom: a dim red light
            gd.rectangle([wx + 4, y0 + 4, wx1 - 4, y1 - 4], fill=refl)
            gd.polygon([(wx + 8, y1 - 8), (wx + 40, y0 + 8), (wx + 60, y0 + 8), (wx + 28, y1 - 8)], fill=(255, 200, 170, 40))
        bd = ImageDraw.Draw(self.glass)
        for wx, y0, wx1, y1, fl_, i in self.windows:                        # window bars
            bd.line([(wx + 50, y0), (wx + 50, y1)], fill=(30, 14, 10, 255), width=6)
            bd.line([(wx, (y0 + y1) / 2), (wx1, (y0 + y1) / 2)], fill=(30, 14, 10, 255), width=6)
        self.bath_win = [w_ for w_ in self.windows if w_[4] == 2 and w_[5] == 5][0]
        # the entrance porch
        def porch(d, s):
            d.rectangle([450 * s, 1150 * s, 670 * s, GY * s], fill=255)
            d.polygon(P_((430, 1160), (560, 1080), (690, 1160), s=s), fill=255)
        b.alpha_composite(shade(porch, (W, H), (60, 28, 20), 14, rim_strength=0.9))
        d = ImageDraw.Draw(b)
        d.rectangle([490, 1180, 630, GY], fill=(12, 4, 5, 255))
        self.building = b
        # the yard + the gate post + bicycles (foreground)
        def yard(d, s):
            d.rectangle([0, (GY - 4) * s, W * s, H * s], fill=255)
        yd = shade(yard, (W, H), (66, 26, 18) if night < 0.5 else (34, 12, 10), 10, rim_strength=0.0)
        rng = np.random.default_rng(4)
        dd_ = ImageDraw.Draw(yd)
        for _ in range(160):
            x, y = rng.uniform(0, W), rng.uniform(GY + 10, H)
            r = rng.uniform(2, 6) * (1 + (y - GY) / 300)
            dd_.ellipse([x - r, y - r * 0.4, x + r, y + r * 0.4], fill=(40, 14, 10, 255))
        self.yard = yd
        def side(d, s):
            cedar(d, s, 40, GY + 30, 900, 120, 3)
            cedar(d, s, 1060, GY + 40, 980, 130, 4)
            # iron bars (tetsubo) on the left of the yard
            for k, hh in enumerate((90, 120, 150)):
                x = 160 + k * 70
                d.rectangle([x * s, (GY + 120 - hh) * s, (x + 6) * s, (GY + 120) * s], fill=255)
                d.rectangle([(x - 64) * s, (GY + 120 - hh) * s, (x + 6) * s, (GY + 126 - hh) * s], fill=255)
        self.side = inflate21(D5.smooth_mask(side, (W, H)), (22, 8, 8), radius=10, rim_strength=1.0)
        def gate(d, s):
            d.rectangle([-40 * s, 980 * s, 150 * s, H * s], fill=255)
            d.rectangle([-60 * s, 950 * s, 170 * s, 1000 * s], fill=255)
        g = shade(gate, (W, H), (92, 80, 74), 30, rim_strength=1.0)
        g = texmul(g, lambda xx, yy: 0.85 + 0.15 * np.sin(xx / 5 + yy / 11) * np.sin(yy / 23))
        gd2 = ImageDraw.Draw(g)
        gd2.rectangle([30, 1060, 120, 1560], fill=(200, 184, 150, 255), outline=(40, 26, 20, 255), width=5)
        jf = jfont(66, serif=True)
        for k, ch in enumerate("夕暮小学校"):
            gd2.text((75, 1110 + k * 92), ch, font=jf, fill=(30, 16, 12, 255), anchor="mm")
        def bikes(d, s):
            for bx in (760, 930):
                for wx in (bx - 70, bx + 70):
                    d.ellipse([(wx - 64) * s, 1610 * s, (wx + 64) * s, 1738 * s], outline=255, width=int(8 * s))
                d.line([((bx - 70) * s, 1674 * s), (bx * s, 1600 * s), ((bx + 70) * s, 1674 * s), ((bx - 10) * s, 1674 * s), ((bx - 70) * s, 1674 * s)], fill=255, width=int(9 * s))
                d.line([(bx * s, 1600 * s), ((bx - 14) * s, 1560 * s)], fill=255, width=int(9 * s))
                d.line([((bx + 50) * s, 1590 * s), ((bx + 70) * s, 1674 * s)], fill=255, width=int(9 * s))
                d.line([((bx + 30) * s, 1586 * s), ((bx + 76) * s, 1580 * s)], fill=255, width=int(10 * s))
        self.bikes = inflate21(D5.smooth_mask(bikes, (W, H)), (40, 30, 30), radius=4, rim_strength=1.2)
        self.gate = g

    def frame(self, t, cam=0.0, extra_win=None, extra_yard=None, extra_front=None, crows=True, gate=True, bikes=True):
        img = self.sky.copy()
        P = lambda k: int(-cam * k)
        if crows and self.night < 0.5:
            d = ImageDraw.Draw(img)
            for i in range(7):
                u = (t * 0.06 + i * 0.13) % 1.0
                x = -60 + u * (W + 120); y = 560 + 80 * math.sin(i * 1.7) + 30 * math.sin(t * 0.7 + i)
                fl = math.sin(t * 9 + i * 2) * 14
                d.line([(x - 26, y - fl), (x, y), (x + 26, y - fl)], fill=(10, 3, 4, 255), width=6)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lay.alpha_composite(self.building); lay.alpha_composite(self.glass)
        if extra_win:
            lay = extra_win(lay, t) or lay
        img.alpha_composite(lay, (P(0.35), 0))
        img.alpha_composite(self.yard)
        img.alpha_composite(self.side, (P(0.6), 0))
        if extra_yard:
            img = extra_yard(img, t, P) or img
        if bikes:
            img.alpha_composite(self.bikes, (P(1.0), 0))
        if extra_front:
            img = extra_front(img, t, P) or img
        if gate:
            img.alpha_composite(dof(self.gate, 2), (P(1.4), 0))
        return img


_SC = {}


def school(night=0.0):
    k = night >= 0.5
    if k not in _SC:
        _SC[k] = School(1.0 if k else 0.0)
    return _SC[k]


# ============================================================ the corridor (3rd floor)
class Corridor:
    """A long wooden school corridor, one-point perspective. Left: sliding windows with red sunset light shafts on the
    floor. Right: classroom sliding doors with class plates. Far end: a dark wall and the bathroom door (red light)."""
    WH, FL, CE, ZN, ZF = 0.6, 1.1, -0.95, 0.42, 7.0

    def __init__(self):
        P = self.P = Persp(540, 880, 560)
        wh, fl, ce, zn, zf = self.WH, self.FL, self.CE, self.ZN, self.ZF
        img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
        P.quad(d, [(-wh, fl, zn), (wh, fl, zn), (wh, fl, zf), (-wh, fl, zf)], (70, 34, 22, 255))       # floor
        P.quad(d, [(-wh, ce, zn), (wh, ce, zn), (wh, ce, zf), (-wh, ce, zf)], (30, 16, 14, 255))       # ceiling
        P.quad(d, [(-wh, ce, zn), (-wh, fl, zn), (-wh, fl, zf), (-wh, ce, zf)], (60, 30, 22, 255))     # left wall
        P.quad(d, [(wh, ce, zn), (wh, fl, zn), (wh, fl, zf), (wh, ce, zf)], (54, 28, 20, 255))         # right wall
        P.quad(d, [(-wh, ce, zf), (wh, ce, zf), (wh, fl, zf), (-wh, fl, zf)], (16, 8, 8, 255))         # end wall
        # floor boards (converging) + joints
        for k in range(-6, 7):
            sd = k * wh / 6
            d.line([P.p(sd, fl, zn), P.p(sd, fl, zf)], fill=(44, 20, 14, 255), width=3)
        z = zn
        while z < zf:
            d.line([P.p(-wh, fl, z), P.p(wh, fl, z)], fill=(50, 24, 16, 255), width=max(1, int(4 / z)))
            z *= 1.18
        # wainscot rail on both walls + ceiling beams
        for sg in (-1, 1):
            d.line([P.p(sg * wh, 0.25, zn), P.p(sg * wh, 0.25, zf)], fill=(36, 16, 12, 255), width=6)
        z = 0.6
        self.lamps = []
        while z < zf:
            P.quad(d, [(-wh, ce, z), (wh, ce, z), (wh, ce, z + 0.12), (-wh, ce, z + 0.12)], (20, 10, 9, 255))
            self.lamps.append(z + 0.06)
            z += 0.9
        # left windows (sliding, wooden frames) -> glass panes stored for the light
        self.win = []
        z = 0.55
        while z < zf - 0.6:
            z1 = z + 0.55
            P.quad(d, [(-wh, -0.55, z), (-wh, 0.15, z), (-wh, 0.15, z1), (-wh, -0.55, z1)], (190, 60, 34, 255))
            for zz in (z, (z + z1) / 2, z1):
                d.line([P.p(-wh, -0.55, zz), P.p(-wh, 0.15, zz)], fill=(40, 18, 12, 255), width=max(2, int(10 / zz)))
            d.line([P.p(-wh, -0.2, z), P.p(-wh, -0.2, z1)], fill=(40, 18, 12, 255), width=max(2, int(6 / z)))
            self.win.append((z, z1))
            z = z1 + 0.18
        # right: classroom doors with little windows and class plates
        jf = font(INTER_SB, 40)
        for i, z in enumerate((0.7, 1.9, 3.4, 5.0)):
            z1 = z + 0.6
            P.quad(d, [(wh, -0.35, z), (wh, fl, z), (wh, fl, z1), (wh, -0.35, z1)], (84, 42, 26, 255))
            P.quad(d, [(wh, -0.25, z + 0.08), (wh, 0.1, z + 0.08), (wh, 0.1, z + 0.3), (wh, -0.25, z + 0.3)], (24, 10, 10, 255))
            P.quad(d, [(wh, -0.25, z + 0.34), (wh, 0.1, z + 0.34), (wh, 0.1, z + 0.52), (wh, -0.25, z + 0.52)], (24, 10, 10, 255))
            # plate sticking out of the wall
            x0, y0 = P.p(wh, -0.55, z + 0.05); x1, y1 = P.p(wh - 0.12, -0.42, z + 0.05)
            d.rectangle([min(x0, x1), y0, max(x0, x1), y1], fill=(210, 196, 170, 255))
            if i < 3:
                fs = max(10, int(40 / z))
                d.text(((x0 + x1) / 2, (y0 + y1) / 2), f"3-{i + 1}", font=font(INTER_SB, fs), fill=(30, 14, 10, 255), anchor="mm")
        # the bathroom door at the far end with a red glow under it + a small sign
        P.quad(d, [(-0.18, -0.25, zf), (0.18, -0.25, zf), (0.18, fl, zf), (-0.18, fl, zf)], (40, 18, 14, 255))
        self.end_door = P.p(0, 0.4, zf)
        self.base = img
        # light shafts on the floor (from the windows, sun low on the left)
        lm = Image.new("L", (W, H), 0); ld = ImageDraw.Draw(lm)
        vm = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(vm)
        for z, z1 in self.win:
            pts = [(-wh, fl, z + 0.15), (-wh, fl, z1 + 0.15), (wh * 0.5, fl, z1 + 0.55), (wh * 0.5, fl, z + 0.55)]
            ld.polygon([P.p(*q) for q in pts], fill=255)
            vol = [P.p(-wh, -0.55, z), P.p(-wh, -0.55, z1), P.p(wh * 0.5, fl, z1 + 0.55), P.p(wh * 0.5, fl, z + 0.55)]
            vd.polygon(vol, fill=70)
        self.shaft = np.asarray(lm.filter(ImageFilter.GaussianBlur(6)), np.float32)[..., None] / 255
        self.vol = np.asarray(vm.filter(ImageFilter.GaussianBlur(30)), np.float32)[..., None] / 255
        self.dust = fog_texture(W, H, 77)

    def frame(self, t, light=1.0, extras=None, lamps=0.0):
        a = to_arr(self.base)
        fl = light * (0.9 + 0.1 * math.sin(t * 2.3))
        a += self.shaft * np.array([230, 90, 50], np.float32) * 0.75 * fl
        a += self.vol * np.array([255, 110, 70], np.float32) * 0.6 * fl * (0.7 + 0.3 * self.dust[..., None])
        if lamps > 0:
            for z in self.lamps:
                x, y = self.P.p(0, self.CE + 0.05, z)
                add_glow(a, gsp(int(160 / z), (255, 200, 150)), x, y, lamps)
        ex, ey = self.end_door
        add_glow(a, gsp(90, (255, 40, 30)), ex, ey + 70, 0.6 * (0.8 + 0.2 * math.sin(t * 13)))
        img = to_img(a)
        if extras:
            for z, fn in sorted(extras, key=lambda e: -e[0]):
                img = fn(img, t) or img
        bokeh_particles(img, 22, 31, t, color=(255, 150, 110), size=(2, 6), blur=(0, 2), area=(0, 300, W, 1700), drift=(6, -4))
        return img


_CO = None


def corridor():
    global _CO
    if _CO is None:
        _CO = Corridor()
    return _CO


# ============================================================ the girls' bathroom (wide)
class Bathroom:
    """Old tiled girls' bathroom, one-point perspective: sinks + a long cracked mirror on the left, three wooden stall
    doors on the right (stall 3 is the last one), a bare bulb, a small high window with red light at the end."""
    WH, FL, CE, ZN, ZF, SF = 0.62, 1.1, -1.0, 0.42, 4.2, 0.22

    def __init__(self):
        P = self.P = Persp(540, 860, 560)
        wh, fl, ce, zn, zf, sf = self.WH, self.FL, self.CE, self.ZN, self.ZF, self.SF
        img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
        P.quad(d, [(-wh, fl, zn), (wh, fl, zn), (wh, fl, zf), (-wh, fl, zf)], (74, 62, 62, 255))
        P.quad(d, [(-wh, ce, zn), (wh, ce, zn), (wh, ce, zf), (-wh, ce, zf)], (34, 26, 26, 255))
        for sg, col in ((-1, (96, 80, 78)), (1, (88, 74, 72))):
            P.quad(d, [(sg * wh, ce, zn), (sg * wh, fl, zn), (sg * wh, fl, zf), (sg * wh, ce, zf)], col + (255,))
            P.quad(d, [(sg * wh, ce, zn), (sg * wh, -0.15, zn), (sg * wh, -0.15, zf), (sg * wh, ce, zf)], (62, 44, 40, 255))
        P.quad(d, [(-wh, ce, zf), (wh, ce, zf), (wh, fl, zf), (-wh, fl, zf)], (70, 58, 56, 255))
        # floor tiles
        for k in range(-10, 11):
            d.line([P.p(k * wh / 10, fl, zn), P.p(k * wh / 10, fl, zf)], fill=(46, 38, 38, 255), width=2)
        z = zn
        while z < zf:
            d.line([P.p(-wh, fl, z), P.p(wh, fl, z)], fill=(46, 38, 38, 255), width=2)
            z += 0.12 * z
        # wall tiles (left + end)
        for hgt in np.arange(-0.15, fl, 0.12):
            d.line([P.p(-wh, hgt, zn), P.p(-wh, hgt, zf)], fill=(64, 52, 50, 255), width=2)
            d.line([P.p(-wh, hgt, zf), P.p(wh, hgt, zf)], fill=(54, 44, 42, 255), width=1)
        # end-wall window (high, small) with red light
        P.quad(d, [(-0.22, -0.85, zf), (0.22, -0.85, zf), (0.22, -0.5, zf), (-0.22, -0.5, zf)], (200, 40, 28, 255))
        d.line([P.p(0, -0.85, zf), P.p(0, -0.5, zf)], fill=(30, 12, 10, 255), width=4)
        self.endwin = P.p(0, -0.67, zf)
        # left: mirror strip + sinks
        P.quad(d, [(-wh, -0.7, 0.8), (-wh, -0.18, 0.8), (-wh, -0.18, 3.2), (-wh, -0.7, 3.2)], (34, 26, 30, 255))
        rng = np.random.default_rng(13)
        for _ in range(5):
            z0 = rng.uniform(0.9, 3.0); h0 = rng.uniform(-0.65, -0.25)
            pts = [P.p(-wh, h0 + rng.uniform(-0.15, 0.15), z0 + rng.uniform(-0.25, 0.25)) for _ in range(3)]
            d.line([P.p(-wh, h0, z0)] + pts, fill=(140, 120, 120, 255), width=2)
        for z in (1.0, 1.7, 2.4):
            P.quad(d, [(-wh, 0.22, z), (-wh + 0.34, 0.22, z), (-wh + 0.34, 0.22, z + 0.45), (-wh, 0.22, z + 0.45)], (170, 160, 150, 255))
            P.quad(d, [(-wh + 0.34, 0.22, z), (-wh + 0.34, 0.42, z + 0.05), (-wh + 0.34, 0.42, z + 0.4), (-wh + 0.34, 0.22, z + 0.45)], (120, 110, 104, 255))
            d.line([P.p(-wh + 0.05, 0.1, z + 0.22), P.p(-wh + 0.14, 0.1, z + 0.22)], fill=(150, 150, 150, 255), width=max(2, int(8 / z)))
        # right: three stalls (fronts on the plane side = sf), doors with numbers; partitions between them
        self.doors = []
        jf = font(INTER_SB, 30)
        stalls = list(enumerate((1.0, 1.95, 2.9)))
        sf = wh
        P.quad(d, [(sf, ce, 0.9), (sf, -0.78, 0.9), (sf, -0.78, 3.8), (sf, ce, 3.8)], (26, 16, 16, 255))       # open tops: dark
        for i, z in stalls:
            z1 = z + 0.85
            P.quad(d, [(sf, -0.8, z - 0.03), (sf, fl, z - 0.03), (sf, fl, z + 0.04), (sf, -0.8, z + 0.04)], (40, 20, 14, 255))
            P.quad(d, [(sf, -0.75, z + 0.04), (sf, 1.0, z + 0.04), (sf, 1.0, z1 - 0.04), (sf, -0.75, z1 - 0.04)], (112, 60, 36, 255))
            P.quad(d, [(sf, 1.0, z + 0.04), (sf, fl, z + 0.04), (sf, fl, z1 - 0.04), (sf, 1.0, z1 - 0.04)], (14, 6, 6, 255))
            for zz in np.linspace(z + 0.12, z1 - 0.12, 5):
                d.line([P.p(sf, -0.7, zz), P.p(sf, 0.95, zz)], fill=(94, 48, 30, 255), width=max(1, int(3 / z)))
            pcx, pcy = P.p(sf, -0.52, z + 0.42); r = 0.075 * P.f / (z + 0.42)
            d.ellipse([pcx - r * 0.7, pcy - r, pcx + r * 0.7, pcy + r], fill=(220, 210, 190, 255))
            fs = max(10, int(r * 1.3))
            d.text((pcx, pcy), str(i + 1), font=font(INTER_SB, fs), fill=(150, 20, 20, 255), anchor="mm")
        P.quad(d, [(sf, -0.8, 3.72), (sf, fl, 3.72), (sf, fl, 3.8), (sf, -0.8, 3.8)], (40, 20, 14, 255))
        self.doors = [(z, z + 0.85) for _, z in stalls]
        self.SF = sf
        self.gap3 = [P.p(sf, 1.05, 2.95), P.p(sf, 1.05, 3.7)]
        self.base = texmul(img, lambda xx, yy: 0.92 + 0.08 * np.sin(xx / 31 + yy / 17) * np.sin(yy / 53))
        self.bulb = P.p(0.0, -0.62, 2.0)
        self.cord = P.p(0.0, ce, 2.0)

    def frame(self, t, bulb=1.0, extras=None, gap_glow=0.5):
        a = to_arr(self.base)
        fl = bulb * (0.75 + 0.25 * (math.sin(t * 31) > -0.7) * (0.8 + 0.2 * math.sin(t * 7)))
        a *= 0.55 + 0.45 * fl
        bx, by = self.bulb
        add_glow(a, gsp(520, (255, 180, 120)), bx, by, 0.55 * fl)
        add_glow(a, gsp(60, (255, 240, 210)), bx, by, 1.0 * fl)
        ex, ey = self.endwin
        add_glow(a, gsp(220, (255, 50, 30)), ex, ey, 0.7)
        (gx0, gy0), (gx1, gy1) = self.gap3
        add_glow(a, gsp(110, (255, 40, 30)), (gx0 + gx1) / 2, (gy0 + gy1) / 2, gap_glow * (0.7 + 0.3 * math.sin(t * 11)))
        img = to_img(a)
        d = ImageDraw.Draw(img)
        d.line([self.cord, (bx, by - 14)], fill=(20, 12, 10, 255), width=3)
        d.ellipse([bx - 13, by - 16, bx + 13, by + 14], fill=(255, 236, 200, int(90 + 165 * fl)))
        if extras:
            for z, fn in sorted(extras, key=lambda e: -e[0]):
                img = fn(img, t) or img
        return img


_BR = None


def bathroom():
    global _BR
    if _BR is None:
        _BR = Bathroom()
    return _BR


# ============================================================ stall 3, seen from the front
class DoorFront:
    """Stall door 3 straight on: tiled wall, wooden door with an enamel '3' plate, the lock indicator
    (空 vacant / 使用中 occupied) and the gap under the door. open(u) swings it in, showing an empty squat toilet."""
    X0, X1, Y0, Y1 = 250, 830, 300, 1660

    def __init__(self):
        a = vgrad((50, 40, 40), (84, 70, 68), (60, 48, 48), ym=0.5)
        wall = to_img(a); d = ImageDraw.Draw(wall)
        for y in range(0, H, 64):
            d.line([(0, y), (W, y)], fill=(48, 38, 38, 255), width=3)
        for x in range(0, W, 64):
            d.line([(x, 0), (x, H)], fill=(48, 38, 38, 255), width=3)
        d.rectangle([0, 1760, W, H], fill=(56, 46, 46, 255))                       # floor
        for x in range(-400, W + 400, 90):
            d.line([(540 + (x - 540) * 0.6, 1760), (x, H)], fill=(40, 32, 32, 255), width=2)
        # stall frame posts + top rail
        X0, X1, Y0, Y1 = self.X0, self.X1, self.Y0, self.Y1
        def frame_(d, s):
            d.rectangle([(X0 - 70) * s, (Y0 - 60) * s, (X0 - 10) * s, 1770 * s], fill=255)
            d.rectangle([(X1 + 10) * s, (Y0 - 60) * s, (X1 + 70) * s, 1770 * s], fill=255)
            d.rectangle([(X0 - 70) * s, (Y0 - 60) * s, (X1 + 70) * s, (Y0 - 10) * s], fill=255)
        wall.alpha_composite(shade(frame_, (W, H), (90, 46, 30), 16, rim_strength=1.0))
        self.wall = wall
        # interior of the stall (seen when open)
        it = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(it)
        d.rectangle([X0, Y0, X1, 1760], fill=(60, 50, 50, 255))
        for y in range(Y0, 1760, 48):
            d.line([(X0, y), (X1, y)], fill=(44, 36, 36, 255), width=2)
        d.rectangle([X0, 1400, X1, 1760], fill=(70, 60, 60, 255))                                 # raised step
        d.ellipse([X0 + 150, 1500, X1 - 150, 1640], fill=(200, 192, 186, 255))                       # squat toilet
        d.ellipse([X0 + 190, 1525, X1 - 190, 1625], fill=(40, 36, 38, 255))
        d.arc([X0 + 150, 1440, X1 - 150, 1560], 180, 360, fill=(220, 212, 206, 255), width=22)        # the hood
        d.rectangle([X0 + 200, 420, X1 - 200, 560], fill=(170, 162, 156, 255))                       # high tank
        d.line([(X1 - 230, 560), (X1 - 230, 900)], fill=(120, 120, 120, 255), width=4)                 # pull chain
        d.ellipse([X1 - 244, 896, X1 - 216, 930], fill=(150, 150, 150, 255))
        self.inside = it
        # the door
        def door(d, s):
            d.rectangle([X0 * s, Y0 * s, X1 * s, Y1 * s], fill=255)
        dr = shade(door, (W, H), (122, 64, 38), 36, rim_strength=0.9)
        dr = texmul(dr, lambda xx, yy: 0.84 + 0.16 * np.sin(xx / 9 + 3 * np.sin(yy / 140)) ** 2)
        d = ImageDraw.Draw(dr)
        d.rectangle([X0 + 40, Y0 + 40, X1 - 40, Y1 - 40], outline=(84, 40, 24, 255), width=6)
        d.ellipse([480, 380, 600, 500], fill=(222, 214, 196, 255), outline=(60, 30, 20, 255), width=5)
        d.text((540, 440), "3", font=font(INTER_SB, 84), fill=(160, 16, 20, 255), anchor="mm")
        d.rectangle([740, 950, 800, 1050], fill=(150, 146, 140, 255))                                  # latch plate
        d.ellipse([750, 990, 790, 1030], fill=(110, 106, 100, 255))
        for k in range(4):                                                                              # scratches
            x = 330 + k * 40
            d.line([(x, 1250 + k * 20), (x + 60, 1300 + k * 18)], fill=(80, 40, 26, 255), width=3)
        self.door = dr

    def indicator(self, occupied, k=1.0):
        im = Image.new("RGBA", (190, 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        col = (200, 20, 24, int(255 * k)) if occupied else (40, 130, 70, int(255 * k))
        d.rounded_rectangle([0, 0, 189, 69], 10, fill=(20, 18, 18, 255), outline=(150, 146, 140, 255), width=4)
        d.rounded_rectangle([10, 10, 179, 59], 6, fill=col)
        d.text((95, 35), "使用中" if occupied else "空", font=jfont(38), fill=(255, 245, 235, 255), anchor="mm")
        return im

    def frame(self, t, open_u=0.0, occupied=0, inside=None, gap=None, front=None, glow=0.5):
        img = self.wall.copy()
        if open_u > 0:
            img.alpha_composite(self.inside)
            if inside:
                img = inside(img, t) or img
            # door swings inward on its left hinge: right edge moves left and recedes
            u = open_u
            X0, X1, Y0, Y1 = self.X0, self.X1, self.Y0, self.Y1
            xr = X1 - (X1 - X0 - 60) * u
            dy = 70 * u
            src = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
            dst = [(X0, Y0), (xr, Y0 + dy), (xr, Y1 - dy), (X0, Y1)]
            dr = to_img(to_arr(self.door) * (1 - 0.5 * u))
            coeffs = _persp_coeffs(dst, src)
            warped = dr.transform((W, H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
            img.alpha_composite(warped)
        else:
            img.alpha_composite(self.door)
            ind = self.indicator(occupied > 0.5)
            img.alpha_composite(ind, (676, 860))
        a = to_arr(img)
        # light from under the door (the gap)
        if open_u <= 0:
            a[self.Y1:1762, self.X0:self.X1] = np.array([10, 3, 4], np.float32)
            add_glow(a, gsp(260, (255, 40, 30)), 540, 1720, glow * (0.7 + 0.3 * math.sin(t * 9)))
        img = to_img(a)
        if gap and open_u <= 0:
            img = gap(img, t) or img
        if front:
            img = front(img, t) or img
        return img


def _persp_coeffs(dst, src):
    """PIL perspective coefficients mapping output pixel (dst quad) -> input pixel (src quad)."""
    A = []; B = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


_DF = None


def doorfront():
    global _DF
    if _DF is None:
        _DF = DoorFront()
    return _DF


def red_shoes(img, x, y, sc=1.0, k=1.0, step=0):
    """Just her red shoes + white socks + thin pale ankles, seen in the gap under a door (feet at y)."""
    body, fx, fy, _ = hanako(0, step)
    crop = body.crop((0, 836, body.width, 950))
    crop = crop.resize((int(crop.width * sc), int(crop.height * sc)), Image.LANCZOS)
    if k < 1:
        crop = with_alpha(crop, k)
    img.alpha_composite(crop, (int(x - fx * sc), int(y - (fy - 836) * sc)))
    return img


# ============================================================ classroom, seen from under a desk
class UnderDesk:
    """POV from under a wooden school desk: the desk's underside across the top, its metal legs framing the view,
    rows of desk and chair legs receding over the floorboards, the sliding door at the back with red light."""
    def __init__(self):
        P = self.P = Persp(540, 930, 520)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 255)); d = ImageDraw.Draw(img)
        fl, zf = 0.55, 9.0
        P.quad(d, [(-4, fl, 0.3), (4, fl, 0.3), (4, fl, zf), (-4, fl, zf)], (64, 30, 20, 255))
        P.quad(d, [(-4, -2, zf), (4, -2, zf), (4, fl, zf), (-4, fl, zf)], (40, 20, 16, 255))         # back wall
        for k in range(-30, 31):
            d.line([P.p(k * 0.14, fl, 0.3), P.p(k * 0.14, fl, zf)], fill=(46, 20, 13, 255), width=2)
        # the sliding door at the back (left), half open, red light
        P.quad(d, [(-2.4, -1.4, zf), (-1.4, -1.4, zf), (-1.4, fl, zf), (-2.4, fl, zf)], (190, 40, 28, 255))
        P.quad(d, [(-1.9, -1.4, zf - 0.01), (-1.0, -1.4, zf - 0.01), (-1.0, fl, zf - 0.01), (-1.9, fl, zf - 0.01)], (70, 34, 22, 255))
        self.door = P.p(-2.0, -0.4, zf)
        self.base = img
        # desk + chair legs (metal tubes) in rows
        legs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        def lg(d, s):
            for z, xss in ((1.25, (-1.7, 1.9)), (2.0, (-2.6, -1.4, 0.2, 1.4, 2.6)), (3.2, (-2.6, -1.4, 0.2, 1.4, 2.6)),
                           (4.6, (-2.6, -1.4, 0.2, 1.4, 2.6)), (6.4, (-2.6, -1.4, 0.2, 1.4, 2.6))):
                for xs in xss:
                    for dx in (-0.25, 0.25):
                        x, y0 = P.p(xs + dx, -0.4, z); _, y1 = P.p(xs + dx, fl, z)
                        d.line([(x * s, y0 * s), (x * s, y1 * s)], fill=255, width=int(max(3, 40 / z) * s))
                    cx_, cy0 = P.p(xs + 0.05, 0.05, z + 0.45); _, cy1 = P.p(xs, fl, z + 0.45)            # chair legs
                    for dx in (-0.18, 0.18):
                        x2, _ = P.p(xs + dx, 0, z + 0.45)
                        d.line([(x2 * s, cy0 * s), (x2 * s, cy1 * s)], fill=255, width=int(max(3, 30 / z) * s))
                    # desk box underside
                    xa, ya = P.p(xs - 0.3, -0.45, z); xb, yb = P.p(xs + 0.3, -0.3, z)
                    d.rectangle([xa * s, ya * s, xb * s, yb * s], fill=255)
        legs.alpha_composite(inflate21(D5.smooth_mask(lg, (W, H)), (92, 84, 86), radius=4, rim_strength=1.1))
        self.legs = dof(legs, 1.5)
        # our desk: underside plank across the top + two big legs + the book shelf
        def ours(d, s):
            d.rectangle([-50 * s, -50 * s, (W + 50) * s, 420 * s], fill=255)
            d.rectangle([20 * s, 300 * s, 120 * s, (H + 50) * s], fill=255)
            d.rectangle([(W - 120) * s, 300 * s, (W - 20) * s, (H + 50) * s], fill=255)
            d.rectangle([20 * s, 1840 * s, (W - 20) * s, 1880 * s], fill=255)
        od = inflate21(D5.smooth_mask(ours, (W, H)), (44, 24, 18), radius=30, rim_strength=0.8)
        od = texmul(od, lambda xx, yy: 0.85 + 0.15 * np.sin(xx / 13 + 2 * np.sin(yy / 50)) ** 2 * (yy < 420))
        dd = ImageDraw.Draw(od)
        for k in range(6):                                                   # carved / scribbled underside
            dd.line([(150 + k * 140, 330), (210 + k * 140, 380)], fill=(30, 16, 12, 255), width=3)
        self.ours = od

    def floor_xy(self, side, z):
        return self.P.p(side, 0.55, z)

    def frame(self, t, extras=None, light=1.0):
        a = to_arr(self.base)
        x, y = self.door
        add_glow(a, gsp(380, (255, 40, 28)), x, y, 0.8 * light * (0.85 + 0.15 * math.sin(t * 9)))
        img = to_img(a)
        img.alpha_composite(self.legs)
        if extras:
            for z, fn in sorted(extras, key=lambda e: -e[0]):
                img = fn(img, t) or img
        img.alpha_composite(self.ours)
        return img


_UD = None


def underdesk():
    global _UD
    if _UD is None:
        _UD = UnderDesk()
    return _UD


def shoes_legs(img, x, y, sc, step=0, k=1.0):
    """Hanako from the knees down (red shoes, white socks, thin pale legs) with feet at (x, y)."""
    body, fx, fy, _ = hanako(0, step, reach=1.0)
    crop = body.crop((0, 600, body.width, 950))
    crop = crop.resize((max(1, int(crop.width * sc)), max(1, int(crop.height * sc))), Image.LANCZOS)
    if k < 1:
        crop = with_alpha(crop, k)
    img.alpha_composite(crop, (int(x - fx * sc), int(y - (fy - 600) * sc)))
    return img


# ============================================================ the blackboard
class Blackboard:
    def __init__(self):
        a = vgrad((40, 22, 18), (70, 38, 28), (36, 18, 14), ym=0.6)
        img = to_img(a); d = ImageDraw.Draw(img)
        d.rectangle([0, 1320, W, H], fill=(56, 28, 18, 255))                         # wainscot
        for x in range(0, W, 60):
            d.line([(x, 1320), (x, H)], fill=(40, 20, 12, 255), width=3)
        def board(d, s):
            d.rectangle([40 * s, 500 * s, (W - 40) * s, 1220 * s], fill=255)
        bd = shade(board, (W, H), (98, 50, 30), 20, rim_strength=0.8)
        img.alpha_composite(bd)
        d = ImageDraw.Draw(img)
        d.rectangle([62, 522, W - 62, 1198], fill=(26, 38, 32, 255))
        sm = fog_texture(W, H, 41)
        arr = to_arr(img)
        msk = np.zeros((H, W), np.float32); msk[522:1198, 62:W - 62] = 1
        arr += (sm * msk)[..., None] * np.array([40, 46, 42]) * 0.6                    # old chalk smears
        img = to_img(arr); d = ImageDraw.Draw(img)
        d.rectangle([50, 1220, W - 50, 1250], fill=(70, 36, 22, 255))                   # chalk tray
        for k, c in enumerate(((230, 226, 214), (220, 80, 70), (230, 220, 120))):
            d.rounded_rectangle([200 + k * 70, 1206, 250 + k * 70, 1220], 5, fill=c + (255,))
        # wall clock 4:44
        cx, cy = 540, 330
        d.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=(210, 200, 184, 255), outline=(40, 24, 18, 255), width=10)
        for k in range(12):
            a_ = 2 * math.pi * k / 12
            d.line([(cx + 70 * math.cos(a_), cy + 70 * math.sin(a_)), (cx + 80 * math.cos(a_), cy + 80 * math.sin(a_))], fill=(40, 24, 18, 255), width=4)
        self.clock = (cx, cy)
        # the teacher's podium (kyotaku)
        def pod(d, s):
            d.polygon(P_((360, 1420), (720, 1420), (700, 1920), (380, 1920), s=s), fill=255)
            d.rectangle([330 * s, 1390 * s, 750 * s, 1440 * s], fill=255)
        img.alpha_composite(shade(pod, (W, H), (90, 46, 28), 24, rim_strength=1.0))
        self.base = img
        # window light shafts from the left
        lm = Image.new("L", (W, H), 0); ld = ImageDraw.Draw(lm)
        for k in range(3):
            x = -200 + k * 330
            ld.polygon([(x, 380), (x + 160, 380), (x + 560, 1500), (x + 400, 1500)], fill=60)
        self.shaft = np.asarray(lm.filter(ImageFilter.GaussianBlur(24)), np.float32)[..., None] / 255
        # chalk writing layers (rendered once; revealed with a left-to-right wipe)
        self.w1 = self._chalk("あそぼ", jfont(250), (540, 760))
        self.w2 = self._chalk("ゆいちゃん", jfont(120), (540, 1010))
        self.w3 = self._chalk("let's play, Yui", font(INTER_SB, 54), (540, 1140), small=True)

    def _chalk(self, text, f, c, small=False):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text(c, text, font=f, fill=(236, 232, 222, 255), anchor="mm")
        a = np.asarray(lay, np.float32).copy()
        n = fog_texture(W, H, 91 if small else 92)
        a[..., 3] *= np.clip(0.55 + 0.6 * n, 0, 1)                                    # chalky
        bbox = lay.getbbox()
        return Image.fromarray(a.astype(np.uint8), "RGBA"), bbox

    def frame(self, t, write=(0, 0, 0), hand=None, extras=None, light=1.0):
        a = to_arr(self.base)
        a += self.shaft * np.array([255, 90, 60]) * 0.7 * light
        img = to_img(a)
        d = ImageDraw.Draw(img)
        cx, cy = self.clock
        for ang, ln, wd in ((-math.pi / 2 + 2 * math.pi * (4 + 44 / 60) / 12, 44, 8), (-math.pi / 2 + 2 * math.pi * 44 / 60, 66, 5)):
            d.line([(cx, cy), (cx + ln * math.cos(ang), cy + ln * math.sin(ang))], fill=(30, 14, 12, 255), width=wd)
        tips = []
        for (lay, bb), u in zip((self.w1, self.w2, self.w3), write):
            if u <= 0:
                continue
            x_ = bb[0] + (bb[2] - bb[0]) * min(1, u)
            m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([0, 0, x_, H], fill=255)
            l2 = lay.copy(); l2.putalpha(Image.fromarray(np.minimum(np.asarray(lay.split()[3]), np.asarray(m))))
            img.alpha_composite(l2)
            if u < 1:
                tips.append((x_, (bb[1] + bb[3]) / 2 + 30 * math.sin(t * 23)))
        if tips:                                                              # the chalk itself, moving on its own
            x_, y_ = tips[-1]
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([x_ - 8, y_ - 30, x_ + 8, y_ + 12], 5, fill=(240, 236, 226, 255))
            d = None
            img = glow_on(img, gsp(60, (255, 240, 220)), x_, y_, 0.3)
        if extras:
            for z, fn in extras:
                img = fn(img, t) or img
        return img


_BB = None


def blackboard():
    global _BB
    if _BB is None:
        _BB = Blackboard()
    return _BB


# ============================================================ the stairwell (side view)
class Stairs:
    STEP_W, STEP_H, X0, Y0, N = 84, 66, -60, 760, 15

    def __init__(self):
        a = vgrad((30, 14, 12), (62, 34, 26), (30, 14, 12), ym=0.45)
        img = to_img(a); d = ImageDraw.Draw(img)
        for x in range(0, W, 120):
            d.line([(x, 0), (x, H)], fill=(52, 28, 22, 255), width=2)
        # landing window (top left) with red light
        d.rectangle([60, 260, 330, 620], fill=(40, 16, 12, 255))
        d.rectangle([76, 276, 314, 604], fill=(196, 46, 30, 255))
        d.line([(195, 276), (195, 604)], fill=(40, 16, 12, 255), width=10)
        d.line([(76, 440), (314, 440)], fill=(40, 16, 12, 255), width=10)
        self.win = (195, 440)
        sw, sh, x0, y0, n = self.STEP_W, self.STEP_H, self.X0, self.Y0, self.N
        def steps(d, s):
            pts = [(x0, y0)]
            for k in range(n):
                pts += [(x0 + (k + 1) * sw, y0 + k * sh), (x0 + (k + 1) * sw, y0 + (k + 1) * sh)]
            pts += [(W + 200, y0 + n * sh), (W + 200, H + 10), (x0, H + 10)]
            d.polygon(P_(*pts, s=s), fill=255)
            d.rectangle([-100 * s, (y0 - 6) * s, (x0 + sw) * s, (H + 10) * s], fill=255)
        st = shade(steps, (W, H), (110, 58, 34), 10, rim_strength=1.2)
        sd = ImageDraw.Draw(st)
        for k in range(n):
            x = x0 + (k + 1) * sw; y = y0 + k * sh
            sd.line([(x - sw, y), (x, y)], fill=(160, 90, 52, 255), width=5)           # nosing
        under = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ud = ImageDraw.Draw(under)
        ud.polygon([(x0, y0 + 120), (x0 + n * sw, y0 + n * sh + 120), (W + 200, H + 10), (x0, H + 10)], fill=(20, 8, 7, 230))
        st.alpha_composite(under)
        img.alpha_composite(st)
        def rail(d, s):
            d.line([((x0 + 20) * s, (y0 - 230) * s), ((x0 + n * sw + 40) * s, (y0 + n * sh - 230) * s)], fill=255, width=int(26 * s))
            for k in range(0, n, 2):
                x = x0 + (k + 0.5) * sw; y = y0 + k * sh
                d.line([(x * s, y * s), (x * s, (y - 230 + 0.5 * sh) * s)], fill=255, width=int(10 * s))
        self.rail = shade(rail, (W, H), (80, 40, 24), 8, rim_strength=1.2)
        self.base = img

    def surf(self, x):
        k = int((x - self.X0) // self.STEP_W)
        k = max(0, min(self.N - 1, k))
        return self.Y0 + k * self.STEP_H

    def plate(self, label, k=1.0):
        im = Image.new("RGBA", (300, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, 299, 199], 16, fill=(214, 204, 182, int(255 * k)), outline=(50, 26, 18, int(255 * k)), width=8)
        d.text((150, 102), label, font=font(INTER_SB, 120), fill=(150, 16, 20, int(255 * k)), anchor="mm")
        return im

    def frame(self, t, label="3F", flip=0.0, extras=None):
        a = to_arr(self.base)
        add_glow(a, gsp(420, (255, 50, 34)), *self.win, 0.7 * (0.85 + 0.15 * math.sin(t * 7)))
        img = to_img(a)
        pl = self.plate(label)
        if flip > 0:                                                      # the plate flips (squash) when the floor changes
            sq = abs(math.cos(math.pi * flip))
            pl = pl.resize((300, max(2, int(200 * sq))), Image.LANCZOS)
        img.alpha_composite(pl, (720, 560 + (200 - pl.height) // 2))
        if extras:
            for z, fn in extras:
                img = fn(img, t) or img
        img.alpha_composite(self.rail)
        return img


_ST = None


def stairs():
    global _ST
    if _ST is None:
        _ST = Stairs()
    return _ST


# ============================================================ Yui's phone (the dare photo)
class Phone:
    SX0, SY0, SX1, SY1 = 250, 330, 830, 1580

    def __init__(self):
        a = vgrad((6, 2, 3), (22, 8, 9), (8, 3, 4), ym=0.5)
        bg = to_img(a); d = ImageDraw.Draw(bg)
        d.rectangle([700, 120, 1000, 520], fill=(70, 16, 14, 255))                     # bedroom window, red moon light
        d.line([(850, 120), (850, 520)], fill=(10, 4, 5, 255), width=10)
        self.bg = dof(bg, 10)
        D = doorfront()
        self.photo_base = D.frame(0.0, open_u=1.0)
        self.D = D

    def photo(self, t, ghost=0.0, wave=1.0):
        img = self.photo_base.copy()
        if ghost > 0:
            g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            g = put_hanako(g, 560, 1600, 1.02, t, eyes=1.0, wave=wave, aura=0.6, sway=False)
            img.alpha_composite(with_alpha(g, ghost))
        a = to_arr(img) * 1.25 + 12                                                    # camera flash look
        cx0, cy0, cx1, cy1 = 150, 230, 930, 1800
        ph = to_img(a).crop((cx0, cy0, cx1, cy1))
        return ph.resize((self.SX1 - self.SX0, self.SY1 - self.SY0), Image.BICUBIC)

    def frame(self, t, ghost=0.0, wave=1.0, glow=1.0):
        img = self.bg.copy()
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([210, 230, 870, 1700], 70, fill=(14, 14, 18, 255), outline=(70, 70, 80, 255), width=6)
        img.alpha_composite(self.photo(t, ghost, wave), (self.SX0, self.SY0))
        d = ImageDraw.Draw(img)
        d.rectangle([self.SX0, self.SY0 - 64, self.SX1, self.SY0], fill=(0, 0, 0, 255))
        d.text((self.SX0 + 30, self.SY0 - 32), "4:44", font=font(INTER_SB, 34), fill=(240, 240, 240, 255), anchor="lm")
        d.rounded_rectangle([self.SX1 - 90, self.SY0 - 46, self.SX1 - 30, self.SY0 - 18], 6, outline=(240, 240, 240, 255), width=3)
        d.rectangle([self.SX1 - 86, self.SY0 - 42, self.SX1 - 70, self.SY0 - 22], fill=(255, 70, 50, 255))
        d.rectangle([self.SX0, self.SY1, self.SX1, self.SY1 + 70], fill=(0, 0, 0, 255))
        d.text((540, self.SY1 + 35), "DARE.jpg", font=font(INTER_M, 30), fill=(200, 200, 200, 255), anchor="mm")
        # her hands holding the phone
        def hands(d, s):
            d.ellipse([120 * s, 1380 * s, 330 * s, 1760 * s], fill=255)
            d.ellipse([750 * s, 1380 * s, 960 * s, 1760 * s], fill=255)
            d.rectangle([140 * s, 1650 * s, 330 * s, (H + 20) * s], fill=255)
            d.rectangle([750 * s, 1650 * s, 940 * s, (H + 20) * s], fill=255)
        img.alpha_composite(shade(hands, (W, H), SKIN, 60, rim=(255, 200, 170)))
        def cuffs(d, s):
            d.rectangle([110 * s, 1800 * s, 360 * s, (H + 20) * s], fill=255)
            d.rectangle([720 * s, 1800 * s, 970 * s, (H + 20) * s], fill=255)
        img.alpha_composite(shade(cuffs, (W, H), NAVY, 30))
        a = to_arr(img)
        add_glow(a, gsp(700, (220, 220, 255)), 540, 960, 0.18 * glow)
        return to_img(a)


_PH = None


def phone():
    global _PH
    if _PH is None:
        _PH = Phone()
    return _PH
