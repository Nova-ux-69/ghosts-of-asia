"""Ep11 Vietnam / the Ma Da - art: the world, the characters and the ghost (2.1D flat21 style).
New world: a Mekong Delta canal at midnight under a low blood-red moon: water-coconut (nipa) palms growing out of the
water, tall coconut palms and tin-roofed stilt houses on the far bank (one red lantern, one lit window), a bamboo
"monkey bridge" (cau khi) with a single handrail on crossed bamboo legs, black water that mirrors everything;
a wooden sampan with an arched woven-bamboo canopy and big painted eyes on the bow; grandma's plank house with the
ancestor altar; a little red-roofed roadside shrine with incense; a red plastic wash basin at dawn.
Ghost: the Ma Da - a drowned woman rising from the water: soaked bone-white ao ba ba blouse, very long black hair
hanging in wet clumps tangled with river weed, too-long thin arms and fingers, water dripping, glowing red eyes.
No gore: never bloated, never wounded."""
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

HZ = 1010                 # far bank waterline
MOON = (300, 440)         # low red moon, up-left
WALK_Y = 1232             # bamboo walkway (wide view)
RAIL_Y = 1062
LEG_Y = 1470              # bridge legs enter the water
VIG = vignette(0.85)
VIG_H = vignette(1.05)
GR = [np.random.default_rng(i).normal(0, 5, (H, W, 1)).astype(np.float32) for i in range(6)]
FOGT = fog_texture(W + 700, H, 111)
SKIN = (172, 116, 80)         # Bao
PALE = (206, 204, 196)        # the Ma Da
BLOUSE = (178, 174, 168)
HAIR = (10, 9, 10)
WEED = (36, 54, 30)
BAMBOO = (132, 80, 40)
SHIRT = (156, 98, 34)         # Bao's ochre T-shirt


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


# ============================================================ flag + UI
_FLAG = None


def flag_base():
    """Vietnam: red field with a five-pointed yellow star in the centre."""
    global _FLAG
    if _FLAG is None:
        w, h, s = 300, 200, 3
        im = Image.new("RGBA", (w * s, h * s), (218, 37, 29, 255)); d = ImageDraw.Draw(im)
        cx, cy, r = w * s / 2, h * s / 2, h * s * 0.31
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.382
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=(255, 222, 0, 255))
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


def torch_ui(pct, t, home="600 M", k=1.0, lost=False):
    """The ticking clock: the torch battery (drains, then LOST) + distance home."""
    f1 = font(INTER_SB, 40); f2 = font(INTER_M, 30)
    w, h = 620, 108
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=(0, 0, 0, int(180 * k)), outline=(255, 70, 50, int(200 * k)), width=3)
    blink = math.sin(t * 9) > -0.2
    red = (255, 70, 50, int(255 * k * (1 if blink else 0.3)))
    wht = (255, 240, 228, int(240 * k))
    # torch icon
    d.rounded_rectangle([30, 44, 74, 64], 6, fill=wht if not lost else red)
    d.polygon([(74, 40), (92, 32), (92, 76), (74, 68)], fill=wht if not lost else red)
    # battery
    d.rounded_rectangle([110, 32, 196, 76], 8, outline=wht, width=4)
    d.rectangle([197, 46, 204, 62], fill=wht)
    if not lost:
        fw = max(4, int(78 * pct / 100))
        d.rounded_rectangle([114, 36, 114 + fw, 72], 5, fill=red if pct <= 15 else wht)
        d.text((270, h / 2), f"{int(pct)}%", font=f1, fill=red if pct <= 15 else wht, anchor="mm")
    else:
        d.line([(116, 72), (192, 36)], fill=red, width=6)
        d.text((270, h / 2), "LOST", font=f1, fill=red, anchor="mm")
    d.line([(350, 22), (350, h - 22)], fill=(255, 255, 255, int(90 * k)), width=2)
    d.text((488, h / 2 - 17), "HOME", font=f2, fill=(255, 190, 140, int(255 * k)), anchor="mm")
    d.text((488, h / 2 + 20), home, font=f1, fill=wht, anchor="mm")
    return im


# ============================================================ Bao
_HC = {}


def bao(phase=0.0, run=0.0, back=False, scale=1.0, torch=True):
    """Bao: short black hair, ochre T-shirt, dark shorts, flip-flops, a small torch in his right hand.
    Returns (RGBA, feet_x, feet_y, torch_xy)."""
    q = (round(phase * 12) % 12, round(run, 1), back, round(scale, 2), torch)
    if q in _HC:
        return _HC[q]
    w, h = 440, 880
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.35 + 0.65 * run)
    lean = 16 * run

    def leg_pts(sg):
        a = sg * sw * 0.6
        hx, hy = cx + lean * 0.3 + sg * 22, 470
        kx, ky = hx + math.sin(a) * 130, hy + math.cos(a) * 160
        fx, fy = kx + math.sin(a - 0.35 * run) * 110, ky + 150
        return (hx, hy), (kx, ky), (fx, fy)

    def legs(d, s):
        for sg in (-1, 1):
            p = leg_pts(sg)
            d.line([(x * s, y * s) for x, y in p], fill=255, width=int(36 * s), joint="curve")

    def shorts(d, s):
        L = lean * 0.4
        d.polygon(P_((cx - 72 + L, 430), (cx + 72 + L, 430), (cx + 84 + L, 560), (cx + 6 + L, 566), (cx + L, 520), (cx - 6 + L, 566), (cx - 84 + L, 560), s=s), fill=255)

    def shoes(d, s):
        for sg in (-1, 1):
            fx, fy = leg_pts(sg)[2]
            d.ellipse([(fx - 30) * s, (fy - 8) * s, (fx + 34) * s, (fy + 12) * s], fill=255)

    def torso(d, s):
        L = lean
        d.polygon(P_((cx - 76 + L, 195), (cx + 76 + L, 195), (cx + 72 + L * .6, 450), (cx - 72 + L * .6, 450), s=s), fill=255)
        d.ellipse([(cx - 84 + L) * s, 182 * s, (cx - 40 + L) * s, 250 * s], fill=255)
        d.ellipse([(cx + 40 + L) * s, 182 * s, (cx + 84 + L) * s, 250 * s], fill=255)

    hands = {}
    for sg in (-1, 1):
        sx, sy = cx + sg * 68 + lean, 212
        a = -sg * sw * 0.9
        if sg == 1 and torch and run < 0.5:
            a = -0.9                                             # torch arm points forward
        ex, ey = sx + math.sin(a) * 90 + sg * 10, sy + math.cos(a) * 105
        b = a - 0.9 * run * sg - (0.5 if sg == 1 and torch and run < 0.5 else 0)
        hx, hy = ex + math.sin(b) * 92 + (40 if sg == 1 and torch and run < 0.5 else 0), ey + math.cos(b) * 84 - 40 * run
        hands[sg] = ((sx, sy), (ex, ey), (hx, hy))

    def arms(d, s):
        for sg in (-1, 1):
            pts = hands[sg]
            d.line([(x * s, y * s) for x, y in pts], fill=255, width=int(24 * s), joint="curve")
            hx, hy = pts[2]
            d.ellipse([(hx - 15) * s, (hy - 15) * s, (hx + 15) * s, (hy + 15) * s], fill=255)

    def sleeves(d, s):
        for sg in (-1, 1):
            (sx, sy), (ex, ey), _ = hands[sg]
            mx, my = sx + (ex - sx) * 0.45, sy + (ey - sy) * 0.45
            d.line([(sx * s, sy * s), (mx * s, my * s)], fill=255, width=int(40 * s))

    def head(d, s):
        L = lean * 1.2
        d.rectangle([(cx - 19 + L) * s, 140 * s, (cx + 19 + L) * s, 200 * s], fill=255)
        d.ellipse([(cx - 50 + L) * s, 40 * s, (cx + 50 + L) * s, 168 * s], fill=255)

    def hair(d, s):
        L = lean * 1.2
        d.pieslice([(cx - 55 + L) * s, 26 * s, (cx + 55 + L) * s, 140 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 55 + L, 90), (cx - 52 + L, 50), (cx + 50 + L, 50), (cx + 56 + L, 86), (cx + 30 + L, 64), (cx + 4 + L, 80), (cx - 26 + L, 64), s=s), fill=255)
        if back:
            d.ellipse([(cx - 52 + L) * s, 34 * s, (cx + 52 + L) * s, 150 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(legs, (w, h), SKIN, 16))
    img.alpha_composite(shade(shoes, (w, h), (30, 20, 20), 6))
    img.alpha_composite(shade(shorts, (w, h), (38, 34, 40), 26))
    img.alpha_composite(shade(arms, (w, h), SKIN, 11))
    sh = shade(torso, (w, h), SHIRT, 38)
    sh = texmul(sh, lambda xx, yy: 1 - 0.18 * ((yy > 330) & (yy < 350)))         # one dark stripe
    img.alpha_composite(sh)
    img.alpha_composite(shade(sleeves, (w, h), SHIRT, 14))
    img.alpha_composite(shade(head, (w, h), SKIN, 28))
    img.alpha_composite(shade(hair, (w, h), HAIR, 16))
    d = ImageDraw.Draw(img)
    L = lean * 1.2
    if not back:
        for sg in (-1, 1):
            d.ellipse([cx + sg * 20 - 9 + L, 96, cx + sg * 20 + 9 + L, 112], fill=(240, 236, 230, 255))
            d.ellipse([cx + sg * 20 - 4 + L + 3, 99, cx + sg * 20 + 4 + L + 3, 109], fill=(15, 10, 10, 255))
            d.line([(cx + sg * 20 - 12 + L, 86), (cx + sg * 20 + 12 + L, 84 - sg * 2)], fill=(20, 12, 12, 255), width=5)
        d.ellipse([cx - 7 + L, 136, cx + 7 + L, 146], fill=(70, 30, 26, 255))
    tx, ty = hands[1][2]
    if torch and run < 0.5:
        d.rounded_rectangle([tx - 12, ty - 10, tx + 38, ty + 10], 5, fill=(60, 56, 60, 255))
        d.polygon([(tx + 38, ty - 14), (tx + 52, ty - 18), (tx + 52, ty + 18), (tx + 38, ty + 14)], fill=(90, 86, 90, 255))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 776 * scale, ((tx + 52) * scale, ty * scale))
    _HC[q] = out
    return out


_CR = {}


def bao_crouch(scale=1.0, look=0.0):
    """Bao crouched, knees up, hands over his mouth. look: 0 = forward, 1 = looking right (toward the stern)."""
    key = (round(scale, 2), round(look, 1))
    if key in _CR:
        return _CR[key]
    w, h = 460, 560
    cx = 230

    def body(d, s):
        d.polygon(P_((150, 230), (300, 230), (330, 420), (330, 520), (120, 520), (110, 400), s=s), fill=255)

    def knees(d, s):
        d.ellipse([200 * s, 250 * s, 350 * s, 390 * s], fill=255)
        d.polygon(P_((240, 330), (340, 320), (330, 530), (270, 530), s=s), fill=255)

    def head(d, s):
        d.ellipse([(cx - 48) * s, 66 * s, (cx + 48) * s, 186 * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 53) * s, 56 * s, (cx + 53) * s, 160 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 53, 108), (cx - 50, 80), (cx + 50, 80), (cx + 53, 108), (cx + 10, 92), s=s), fill=255)

    def hands(d, s):
        d.ellipse([(cx - 32) * s, 140 * s, (cx + 26) * s, 180 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(body, (w, h), SHIRT, 40))
    img.alpha_composite(shade(knees, (w, h), SKIN, 30))
    img.alpha_composite(shade(lambda d, s: d.polygon(P_((200, 300), (350, 300), (350, 400), (200, 400), s=s), fill=255), (w, h), (38, 34, 40), 20))
    img.alpha_composite(shade(lambda d, s: d.line([(170 * s, 250 * s), (250 * s, 340 * s), (330 * s, 330 * s)], fill=255, width=int(26 * s), joint="curve"), (w, h), SKIN, 10))
    img.alpha_composite(shade(head, (w, h), SKIN, 26))
    img.alpha_composite(shade(hair, (w, h), HAIR, 14))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ey = 114
        d.ellipse([cx + sg * 19 - 10, ey, cx + sg * 19 + 10, ey + 17], fill=(240, 236, 230, 255))
        px = 4 + 4 * look
        d.ellipse([cx + sg * 19 - 4 + px, ey + 4, cx + sg * 19 + 4 + px, ey + 12], fill=(15, 10, 10, 255))
    img.alpha_composite(shade(hands, (w, h), SKIN, 10))
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = (img, cx * scale, 530 * scale)
    _CR[key] = out
    return out


_FACE = {}


def bao_face(mouth=0.0, look=0.0, wet=False):
    """Close-up: Bao's head and shoulders, eyes wide. look -1..1 moves the pupils (down = +)."""
    key = (round(mouth, 1), round(look, 1), wet)
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
        d.pieslice([(cx - 205) * s, 268 * s, (cx + 205) * s, 700 * s], 180, 360, fill=255)
        d.polygon(P_((cx - 205, 485), (cx - 196, 396), (cx + 196, 396), (cx + 205, 485), (cx + 90, 430), (cx + 10, 470), (cx - 80, 430), s=s), fill=255)

    lt = dict(rim=(255, 70, 50))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(body, (w, h), SHIRT, 90, **lt))
    img.alpha_composite(shade(neck, (w, h), SKIN, 30, **lt))
    img.alpha_composite(shade(head, (w, h), SKIN, 110, **lt))
    img.alpha_composite(shade(hair, (w, h), HAIR, 40, **lt))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ex, ey = cx + sg * 78, 600
        d.ellipse([ex - 40, ey - 26, ex + 40, ey + 30], fill=(240, 234, 226, 255))
        py = 10 * look
        d.ellipse([ex - 13, ey - 10 + py, ex + 13, ey + 16 + py], fill=(14, 9, 9, 255))
        d.ellipse([ex - 3 + 6, ey - 6 + py, ex + 4 + 6, ey + 1 + py], fill=(255, 230, 200, 255))
        d.line([(ex - 46, ey - 70), (ex + 40, ey - 70 - sg * 8)], fill=(18, 10, 10, 255), width=14)
    d.polygon([(cx - 8, 610), (cx + 26, 700), (cx - 18, 706)], fill=(134, 86, 60, 255))
    d.ellipse([cx - 34, 750 - 4 * mouth, cx + 34, 762 + 40 * mouth], fill=(56, 20, 18, 255))
    if wet:
        rng = np.random.default_rng(3)
        for _ in range(16):
            x, y = rng.uniform(cx - 170, cx + 170), rng.uniform(420, 820)
            d.ellipse([x - 5, y - 7, x + 5, y + 7], fill=(255, 220, 200, 150))
    _FACE[key] = img
    return img


# ============================================================ grandma (Ba)
_BA = None


def grandma():
    """Bao's grandmother: grey hair in a bun, dark-maroon ao ba ba, a black-and-white checked khan ran scarf,
    sitting on the plank bed, one finger raised in warning."""
    global _BA
    if _BA is not None:
        return _BA
    cx, hy, by = 600, 860, 1400
    FACE = (150, 100, 74)

    def body(d, s):
        d.polygon(P_((cx - 120, hy + 110), (cx + 120, hy + 110), (cx + 220, by), (cx - 240, by), s=s), fill=255)
        d.ellipse([(cx - 270) * s, (by - 130) * s, (cx + 250) * s, (by + 40) * s], fill=255)

    def face(d, s):
        d.ellipse([(cx - 82) * s, (hy - 100) * s, (cx + 82) * s, (hy + 100) * s], fill=255)

    def hair(d, s):
        d.pieslice([(cx - 86) * s, (hy - 112) * s, (cx + 86) * s, (hy - 4) * s], 180, 360, fill=255)
        d.ellipse([(cx - 10) * s, (hy - 160) * s, (cx + 80) * s, (hy - 80) * s], fill=255)       # bun

    def scarf(d, s):
        d.polygon(P_((cx - 110, hy + 90), (cx + 110, hy + 90), (cx + 90, hy + 170), (cx + 30, hy + 150), (cx + 10, hy + 330), (cx - 50, hy + 330), (cx - 40, hy + 150), (cx - 90, hy + 170), s=s), fill=255)

    def arm(d, s):
        d.line([((cx + 120) * s, (hy + 190) * s), ((cx + 230) * s, (hy + 330) * s), ((cx + 250) * s, (hy + 130) * s)], fill=255, width=int(36 * s), joint="curve")
        d.line([((cx + 250) * s, (hy + 130) * s), ((cx + 256) * s, (hy + 50) * s)], fill=255, width=int(14 * s))

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lt = dict(rim=(255, 170, 100), light=(-0.6, -0.6, 0.5))
    bd = shade(body, (W, H), (92, 28, 30), 70, **lt)
    img.alpha_composite(texmul(bd, lambda xx, yy: 0.92 + 0.08 * np.sin(xx / 16 + yy / 200)))
    d = ImageDraw.Draw(img)
    for k in range(4):                                         # ao ba ba buttons
        d.ellipse([cx - 6, hy + 200 + k * 60, cx + 6, hy + 212 + k * 60], fill=(200, 180, 160, 255))
    sc = shade(scarf, (W, H), (220, 214, 204), 20, **lt)
    sc = texmul(sc, lambda xx, yy: np.where((((xx // 18) + (yy // 18)) % 2) == 0, 0.18, 1.0))       # black/white checks
    img.alpha_composite(sc)
    img.alpha_composite(shade(face, (W, H), FACE, 40, **lt))
    img.alpha_composite(shade(hair, (W, H), (168, 164, 160), 18, **lt))
    img.alpha_composite(shade(arm, (W, H), FACE, 14, **lt))
    d = ImageDraw.Draw(img)
    for sg in (-1, 1):
        ex, ey = cx + sg * 32, hy - 4
        d.ellipse([ex - 7, ey - 5, ex + 7, ey + 7], fill=(24, 14, 12, 255))
        d.line([(ex - 16, ey - 20), (ex + 16, ey - 22 - sg * 3)], fill=(120, 110, 104, 255), width=4)
    for k in range(3):
        d.arc([cx - 62, hy + 18 + k * 10, cx - 30, hy + 50 + k * 10], 100, 170, fill=(110, 70, 54, 255), width=2)
        d.arc([cx + 30, hy + 18 + k * 10, cx + 62, hy + 50 + k * 10], 10, 80, fill=(110, 70, 54, 255), width=2)
    d.line([(cx - 26, hy + 58), (cx + 26, hy + 58)], fill=(110, 30, 30, 255), width=6)
    _BA = img
    return img


# ============================================================ the Ma Da
_MD = {}


def mada(tilt=0.0, reach=0.0):
    """Upper body + hips, ~1500 px tall, facing us: a soaked ao ba ba blouse, very long wet hair in clumps with river
    weed, too-long thin pale arms (reach 0 = hanging, 1 = reaching forward/up), long fingers.
    Returns (RGBA, eye1, eye2, drip_points)."""
    key = (round(tilt, 1), round(reach, 1))
    if key in _MD:
        return _MD[key]
    w, h = 760, 1500
    cx, hy = 380, 210
    ang = math.radians(tilt)

    def R(*pts):
        return rot(pts, ang, cx, hy + 160)

    tips = [(cx - 170, 1230), (cx - 105, 1310), (cx - 40, 1180), (cx + 60, 1240), (cx + 120, 1320), (cx + 175, 1210)]

    def hair_back(d, s):
        pts = R((cx - 115, hy - 60), (cx, hy - 140), (cx + 115, hy - 60), (cx + 150, hy + 120)) + \
            [(cx + 190, 700), (cx + 200, 1000)] + tips[::-1] + [(cx - 200, 1000), (cx - 190, 700)] + R((cx - 150, hy + 120))
        d.polygon(P_(*pts, s=s), fill=255)

    def blouse(d, s):
        d.polygon(P_((cx - 150, 420), (cx - 60, 380), (cx + 60, 380), (cx + 150, 420), (cx + 170, 900), (cx + 190, 1500),
                     (cx - 190, 1500), (cx - 170, 900), s=s), fill=255)

    def face(d, s):
        d.polygon(P_(*R(*[(cx + 64 * math.cos(a), hy + 10 + 96 * math.sin(a) * (1.08 if math.sin(a) > 0 else 1.0))
                          for a in np.linspace(0, 2 * math.pi, 32)]), s=s), fill=255)

    def neck(d, s):
        d.polygon(P_(*R((cx - 30, hy + 80), (cx + 30, hy + 80)), (cx + 34, 400), (cx - 34, 400), s=s), fill=255)

    def hair_front(d, s):
        # parted in the middle: two heavy wet curtains over the cheeks, long clumps down the front
        for sg in (-1, 1):
            pts = R((cx + sg * 8, hy - 100), (cx + sg * 90, hy - 80), (cx + sg * 80, hy + 40), (cx + sg * 70, hy + 200)) + \
                [(cx + sg * 110, 700), (cx + sg * 90, 980), (cx + sg * 60, 860), (cx + sg * 40, 600)] + \
                R((cx + sg * 34, hy + 150), (cx + sg * 30, hy + 20), (cx + sg * 14, hy - 60))
            d.polygon(P_(*pts, s=s), fill=255)
        for x0 in (-24, 26):                                                  # a few strands across the face
            p = R((cx + x0, hy - 70), (cx + x0 + 6, hy + 40), (cx + x0 - 4, hy + 160))
            d.line([(x * s, y * s) for x, y in p], fill=255, width=int(8 * s), joint="curve")

    sh_l, sh_r = (cx - 140, 430), (cx + 140, 430)

    def arm_pts(sg):
        sx, sy = (sh_l if sg < 0 else sh_r)
        # hanging: elbow low, hand near the bottom; reach: forearm swings forward/up
        ex, ey = sx + sg * 40, sy + 360 - 120 * reach
        hx, hy2 = ex + sg * (20 - 10 * reach), ey + 420 - 520 * reach
        return (sx, sy), (ex, ey), (hx, hy2)

    def arms(d, s):
        for sg in (-1, 1):
            p = arm_pts(sg)
            d.line([(x * s, y * s) for x, y in p], fill=255, width=int(28 * s), joint="curve")
            hx, hy2 = p[2]
            d.ellipse([(hx - 26) * s, (hy2 - 30) * s, (hx + 26) * s, (hy2 + 30) * s], fill=255)
            for k in range(4):                                                # long thin fingers
                a = math.pi / 2 + (k - 1.5) * 0.18 - (math.pi * 0.9 * reach) * 1.0
                L = 120 - 8 * abs(k - 1.5)
                mx_, my_ = hx + math.cos(a) * L * 0.55, hy2 + math.sin(a) * L * 0.55
                fx_, fy_ = hx + math.cos(a + 0.25 * sg) * L, hy2 + math.sin(a + 0.25 * sg) * L
                d.line([(hx * s, hy2 * s), (mx_ * s, my_ * s), (fx_ * s, fy_ * s)], fill=255, width=int(10 * s), joint="curve")

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(hair_back, (w, h), HAIR, 40, rim_strength=1.3))
    bl = shade(blouse, (w, h), BLOUSE, 80, rim_strength=1.1)
    bl = texmul(bl, lambda xx, yy: 0.82 + 0.18 * (np.sin(xx / 11 + np.sin(yy / 60) * 2) > -0.3) - 0.1 * (np.sin(xx / 37 + yy / 300) > 0.6))   # wet folds
    img.alpha_composite(bl)
    d = ImageDraw.Draw(img)
    for k in range(5):                                                       # ao ba ba buttons + pocket lines
        d.ellipse([cx - 7, 470 + k * 90, cx + 7, 484 + k * 90], fill=(120, 118, 112, 255))
    d.line([(cx - 150, 1000), (cx - 60, 1000)], fill=(120, 116, 110, 255), width=4)
    d.line([(cx + 60, 1000), (cx + 150, 1000)], fill=(120, 116, 110, 255), width=4)
    img.alpha_composite(shade(neck, (w, h), PALE, 16, rim_strength=0.6))
    img.alpha_composite(shade(face, (w, h), PALE, 46, rim_strength=0.6))
    d = ImageDraw.Draw(img)
    e1 = rot([(cx - 28, hy + 8)], ang, cx, hy + 160)[0]; e2 = rot([(cx + 28, hy + 8)], ang, cx, hy + 160)[0]
    for ex, ey in (e1, e2):
        d.ellipse([ex - 19, ey - 12, ex + 19, ey + 14], fill=(22, 10, 12, 255))
    mo = rot([(cx - 14, hy + 72), (cx + 14, hy + 72), (cx + 10, hy + 92), (cx - 10, hy + 92)], ang, cx, hy + 160)
    d.polygon(mo, fill=(30, 12, 14, 255))
    img.alpha_composite(shade(hair_front, (w, h), (14, 12, 13), 20, rim_strength=1.5))
    img.alpha_composite(shade(arms, (w, h), PALE, 12, rim_strength=0.9))
    # river weed tangled in the hair: wavy dark-green strands with tiny leaves
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(7)
    for k in range(9):
        x0 = cx + rng.uniform(-170, 170); y0 = rng.uniform(380, 820); L = rng.uniform(220, 420)
        pts = [(x0 + 14 * math.sin(j * 0.9 + k), y0 + j * L / 10) for j in range(11)]
        d.line(pts, fill=WEED + (255,), width=5, joint="curve")
        for j in range(2, 10, 2):
            px, py = pts[j]
            sg = 1 if j % 4 else -1
            d.polygon([(px, py), (px + sg * 22, py + 8), (px + sg * 4, py + 22)], fill=(48, 70, 36, 255))
    drips = [p for p in tips] + [arm_pts(-1)[2], arm_pts(1)[2]]
    out = (img, e1, e2, drips)
    _MD[key] = out
    return out


def ripple_rings(img, x, y, rx, t, k=1.0, n=3, speed=0.6, col=(255, 120, 90)):
    """Expanding flat rings on the water surface around (x, y)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(n):
        u = ((t * speed + i / n) % 1.0)
        r = rx * (0.5 + 1.2 * u)
        al = int(140 * k * (1 - u))
        d.ellipse([x - r, y - r * 0.16, x + r, y + r * 0.16], outline=col + (al,), width=max(2, int(4 * (1 - u)) + 1))
    img.alpha_composite(lay)


def put_mada(img, x, y_water, scale=1.0, t=0.0, eyes=1.0, tilt=0.0, rise=1.0, aura=0.5, reach=0.0, rings=True, drip=True):
    """The Ma Da rising out of the water at (x, y_water). rise 0 = only the top of the head, 1 = out to the hips."""
    body, e1, e2, drips = mada(tilt, reach)
    sway = 1.2 * math.sin(t * 0.8)
    g = body.rotate(sway, resample=Image.BICUBIC, center=(380, 900))
    wl = int(120 + rise * 1080)                     # waterline in sprite coords
    wl = max(10, min(g.height - 1, wl))
    top = g.crop((0, 0, g.width, wl))
    under = g.crop((0, wl, g.width, min(g.height, wl + 260)))
    sc = scale
    top = top.resize((max(1, int(top.width * sc)), max(1, int(top.height * sc))), Image.LANCZOS)
    gx, gy = int(x - 380 * sc), int(y_water - wl * sc)
    if aura > 0:
        al = top.split()[3].filter(ImageFilter.GaussianBlur(max(2, 30 * sc)))
        lay = Image.new("RGBA", top.size, (255, 50, 40, 0)); lay.putalpha(al.point(lambda v: int(v * aura)))
        img.alpha_composite(lay, (gx, gy))
    if under.height > 2:
        u2 = under.resize((max(1, int(under.width * sc)), max(1, int(under.height * sc))), Image.BILINEAR)
        u2 = tint(u2, (0.45, 0.22, 0.22), 0.35, blur=3)
        a = np.asarray(u2, np.float32).copy()
        a[..., 3] *= np.linspace(1, 0, a.shape[0])[:, None]
        img.alpha_composite(Image.fromarray(a.astype(np.uint8), "RGBA"), (gx, int(y_water)))
    img.alpha_composite(top, (gx, gy))
    if eyes > 0:
        k = eyes * (0.65 + 0.35 * math.sin(t * 5) ** 2)
        for ex, ey in (e1, e2):
            if ey < wl:
                eye(img, gx + ex * sc, gy + ey * sc, k, max(0.25, sc * 0.8))
    if drip:
        d = ImageDraw.Draw(img)
        for i, (dx, dy) in enumerate(drips):
            if dy * sc + gy < y_water - 4:
                ph = (t * 1.3 + i * 0.37) % 1.0
                yy = gy + dy * sc + ph * 120 * sc
                if yy < y_water:
                    d.ellipse([gx + dx * sc - 4 * sc - 1, yy - 7 * sc - 1, gx + dx * sc + 4 * sc + 1, yy + 7 * sc + 1], fill=(230, 200, 190, 200))
    if rings:
        ripple_rings(img, x, y_water, 260 * sc, t, 0.9)
    return img


_SUB = {}


def swimmer(scale=1.0):
    """The Ma Da swimming just under the surface (horizontal, head to the LEFT), dark-tinted and blurred."""
    k = round(scale, 2)
    if k not in _SUB:
        body = mada(0.0, 0.0)[0]
        g = body.rotate(90, expand=True, resample=Image.BICUBIC)       # head now on the left
        g = g.resize((int(g.width * k), int(g.height * k)), Image.LANCZOS)
        _SUB[k] = tint(g, (0.75, 0.48, 0.45), 0.66, blur=3)
    return _SUB[k]


_MF = {}


def mada_face(mouth=0.0):
    """Jump-scare close-up: wet black hair stuck to a pale face, weed strands, sunken eyes, dark lips, drops of water."""
    key = round(mouth, 1)
    if key in _MF:
        return _MF[key]
    w, h = 900, 1200
    cx, cy = 450, 560

    def hair(d, s):
        d.polygon(P_((cx - 260, cy - 200), (cx - 150, cy - 380), (cx + 150, cy - 380), (cx + 260, cy - 200), (cx + 300, 1200), (cx - 300, 1200), s=s), fill=255)

    def face(d, s):
        d.ellipse([(cx - 150) * s, (cy - 220) * s, (cx + 150) * s, (cy + 250) * s], fill=255)

    def strands(d, s):
        for sg in (-1, 1):
            d.polygon(P_((cx + sg * 16, cy - 300), (cx + sg * 210, cy - 250), (cx + sg * 200, 1200), (cx + sg * 120, 1200),
                         (cx + sg * 112, cy + 140), (cx + sg * 80, cy - 110), (cx + sg * 30, cy - 220), s=s), fill=255)
        for x0, x1 in ((-40, -50), (8, 0), (54, 70), (-96, -110)):
            d.line([((cx + x0) * s, (cy - 260) * s), ((cx + (x0 + x1) / 2 + 6) * s, cy * s), ((cx + x1) * s, (cy + 280) * s)], fill=255, width=int(9 * s), joint="curve")

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(hair, (w, h), HAIR, 40, rim_strength=1.3))
    img.alpha_composite(shade(face, (w, h), PALE, 80, rim_strength=0.7))
    d = ImageDraw.Draw(img)
    e1, e2 = (cx - 62, cy + 6), (cx + 62, cy + 6)
    for ex, ey in (e1, e2):
        d.ellipse([ex - 48, ey - 30, ex + 48, ey + 34], fill=(24, 10, 12, 255))
        d.arc([ex - 56, ey + 18, ex + 56, ey + 58], 20, 160, fill=(150, 146, 140, 255), width=5)     # dark rings under the eyes
    d.polygon([(cx - 40, cy + 156), (cx + 40, cy + 156), (cx + 30, cy + 170 + 50 * mouth), (cx - 30, cy + 170 + 50 * mouth)], fill=(26, 10, 14, 255))
    img.alpha_composite(shade(strands, (w, h), (14, 12, 13), 24, rim_strength=1.5))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(9)
    for k in range(6):                                                    # weed
        x0 = cx + rng.uniform(-260, 260); y0 = rng.uniform(cy - 300, cy + 200)
        pts = [(x0 + 12 * math.sin(j * 0.8 + k), y0 + j * 40) for j in range(12)]
        d.line(pts, fill=WEED + (255,), width=6, joint="curve")
        for j in range(1, 11, 3):
            px, py = pts[j]
            d.polygon([(px, py), (px + 24, py + 10), (px + 6, py + 26)], fill=(48, 70, 36, 255))
    for _ in range(26):                                                    # water drops
        x, y = rng.uniform(cx - 160, cx + 160), rng.uniform(cy - 200, cy + 260)
        d.ellipse([x - 5, y - 8, x + 5, y + 8], fill=(255, 225, 215, 140))
    out = (img, e1, e2)
    _MF[key] = out
    return out


def put_face(img, x, y, scale, t, eyes=1.0, mouth=0.0, tilt=0.0, aura=0.7, alpha=1.0):
    fc, e1, e2 = mada_face(mouth)
    g = fc.rotate(tilt, resample=Image.BICUBIC, center=(450, 560))
    g = g.resize((max(1, int(g.width * scale)), max(1, int(g.height * scale))), Image.LANCZOS)
    if alpha < 1:
        g = with_alpha(g, alpha)
    gx, gy = int(x - 450 * scale), int(y - 560 * scale)
    if aura > 0:
        al = g.split()[3].filter(ImageFilter.GaussianBlur(30))
        lay = Image.new("RGBA", g.size, (255, 50, 40, 0)); lay.putalpha(al.point(lambda v: int(v * aura)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    k = eyes * (0.75 + 0.25 * math.sin(t * 6) ** 2) * alpha
    ca, sa = math.cos(math.radians(-tilt)), math.sin(math.radians(-tilt))
    for ex, ey in (e1, e2):
        dx, dy = ex - 450, ey - 560
        eye(img, x + (dx * ca - dy * sa) * scale, y + (dx * sa + dy * ca) * scale, k, 1.4 * scale)
    return img


# ============================================================ the world: the canal
def palm(d, s, x, by, h, lean, seed, fronds=9):
    """Coconut palm silhouette into mask d."""
    rng = np.random.default_rng(seed)
    pts = [(x + lean * (i / 10) ** 2 * h * 0.35, by - h * i / 10) for i in range(11)]
    for i in range(10):
        wdt = 16 * (1 - 0.45 * i / 10)
        d.line([(pts[i][0] * s, pts[i][1] * s), (pts[i + 1][0] * s, pts[i + 1][1] * s)], fill=255, width=max(1, int(wdt * s)))
    tx, ty = pts[-1]
    for k in range(fronds):
        a = -math.pi / 2 + (k - (fronds - 1) / 2) * 0.42 + rng.uniform(-0.1, 0.1)
        L = h * rng.uniform(0.3, 0.4)
        fp = [(tx + math.cos(a) * L * u, ty + math.sin(a) * L * u + 0.9 * L * u * u * (0.6 + 0.4 * abs(math.cos(a)))) for u in np.linspace(0, 1, 12)]
        d.line([(px * s, py * s) for px, py in fp], fill=255, width=max(1, int(5 * s)))
        for j in range(1, 11):
            px, py = fp[j]; qx, qy = fp[j + 1]
            nx, ny = -(qy - py), (qx - px); nl = math.hypot(nx, ny) + 1e-6
            ll = 34 * (1 - j / 12) + 8
            for sg in (-1, 1):
                d.line([(px * s, py * s), ((px + sg * nx / nl * ll + (qx - px) * 0.8) * s, (py + sg * ny / nl * ll + abs(ny / nl) * ll * 0.6 + 10) * s)],
                       fill=255, width=max(1, int(4 * s)))


def nipa(d, s, x, by, h, seed, n=7, spread=1.0):
    """Water-coconut (nipa) clump: long feather fronds rising straight out of the water."""
    rng = np.random.default_rng(seed)
    for k in range(n):
        a = -math.pi / 2 + (k - (n - 1) / 2) * 0.22 * spread + rng.uniform(-0.08, 0.08)
        L = h * rng.uniform(0.7, 1.0)
        bend = rng.uniform(0.15, 0.35) * (1 if a > -math.pi / 2 else -1)
        fp = []
        for u in np.linspace(0, 1, 14):
            aa = a + bend * u * u
            fp.append((x + math.cos(aa) * L * u, by + math.sin(aa) * L * u + 0.25 * L * u ** 3))
        d.line([(px * s, py * s) for px, py in fp], fill=255, width=max(1, int(6 * s)))
        for j in range(2, 13):
            px, py = fp[j]; qx, qy = fp[j + 1]
            nx, ny = -(qy - py), (qx - px); nl = math.hypot(nx, ny) + 1e-6
            ll = 46 * math.sin(math.pi * j / 13) + 6
            for sg in (-1, 1):
                d.line([(px * s, py * s), ((px + sg * nx / nl * ll + (qx - px) * 1.4) * s, (py + sg * ny / nl * ll + 14) * s)], fill=255, width=max(1, int(5 * s)))


def stilt_house(d, s, x, by, w, h, roof=70):
    d.rectangle([x * s, (by - 50 - h) * s, (x + w) * s, (by - 50) * s], fill=255)
    for k in range(5):
        px = x + 10 + k * (w - 20) / 4
        d.line([(px * s, (by - 52) * s), (px * s, by * s)], fill=255, width=max(1, int(6 * s)))
    d.polygon([((x - 24) * s, (by - 50 - h + 6) * s), ((x + w * 0.5) * s, (by - 50 - h - roof) * s), ((x + w + 24) * s, (by - 50 - h + 6) * s)], fill=255)


class Canal:
    """Mekong Delta canal at midnight: red moon, far bank (palms + stilt houses), nipa clumps, the monkey bridge,
    black mirror water with a rippling moon road."""
    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W]
        y = yy / H
        top = np.array([3, 1, 2], np.float32); mid = np.array([34, 5, 9], np.float32); hor = np.array([150, 28, 22], np.float32)
        k1 = np.clip(y / 0.4, 0, 1) ** 1.4; k2 = np.clip((y - 0.34) / 0.19, 0, 1) ** 1.2
        col = top * (1 - k1[..., None]) + mid * k1[..., None]; col = col * (1 - k2[..., None]) + hor * k2[..., None]
        dd = np.sqrt((xx - MOON[0]) ** 2 + (yy - MOON[1]) ** 2)
        col += (np.exp(-dd / 300) * 150)[..., None] * np.array([1.0, 0.3, 0.2])
        moon = np.clip((118 - dd) / 2, 0, 1)
        tex = fog_texture(W, H, 23)
        mcol = np.array([236, 104, 70], np.float32) * (0.78 + 0.3 * tex)[..., None]
        col = col * (1 - moon[..., None]) + mcol * moon[..., None]
        cl = fog_texture(W, H, 31) * np.exp(-((yy - 520) / 70) ** 2)
        col = col * (1 - 0.65 * cl[..., None]) + np.array([24, 5, 7]) * 0.65 * cl[..., None]
        rng = np.random.default_rng(6)
        for _ in range(110):
            sx, sy = rng.uniform(0, W), rng.uniform(0, 650)
            if math.hypot(sx - MOON[0], sy - MOON[1]) > 190:
                col[int(sy), int(sx)] = (200, 150, 140)
        sky = to_img(col)
        # far-far treeline (lighter, blurred) and the far bank (palms + stilt houses), shaded
        def far(d, s):
            for i, x in enumerate(range(-40, W + 80, 95)):
                palm(d, s, x + (i % 3) * 20, HZ - 20, 240 + (i * 37) % 110, ((i % 4) - 1.5) * 0.4, 100 + i, fronds=7)
            d.rectangle([0, (HZ - 40) * s, W * s, HZ * s], fill=255)
        farl = inflate21(D5.smooth_mask(far, (W, H)), (62, 14, 14), radius=8, rim_strength=0.5)
        sky.alpha_composite(dof(farl, 3))
        self.windows = []
        def bank(d, s):
            for x, by, w, h in ((90, HZ, 210, 120), (610, HZ + 4, 250, 140), (900, HZ, 170, 100)):
                stilt_house(d, s, x, by, w, h)
            for i, (x, hh, ln) in enumerate(((20, 430, 0.6), (380, 520, -0.5), (470, 380, 0.8), (880, 470, -0.7), (1040, 560, 0.3), (240, 300, 0.4))):
                palm(d, s, x, HZ + 2, hh, ln, 10 + i)
            d.polygon(P_((0, HZ - 28), (200, HZ - 40), (420, HZ - 24), (700, HZ - 36), (W, HZ - 26), (W, HZ + 6), (0, HZ + 6), s=s), fill=255)
        bk = inflate21(D5.smooth_mask(bank, (W, H)), (24, 7, 8), radius=10, rim_strength=0.9)
        dk = ImageDraw.Draw(bk)
        for x0, y0, x1, y1 in ((150, HZ - 130, 190, HZ - 92), (680, HZ - 150, 724, HZ - 108)):
            dk.rectangle([x0, y0, x1, y1], fill=(255, 130, 70, 255))
            self.windows.append(((x0 + x1) / 2, (y0 + y1) / 2))
        lx, ly = 860, HZ - 120                                                 # red lantern under the eave
        dk.line([(lx, ly - 40), (lx, ly - 22)], fill=(30, 10, 10, 255), width=3)
        dk.ellipse([lx - 16, ly - 24, lx + 16, ly + 18], fill=(230, 40, 30, 255))
        self.lantern = (lx, ly)
        sky.alpha_composite(dof(bk, 1.2))
        self.above = sky                                                       # rows < HZ used; also reflected
        # the bridge (cau khi): one bamboo walkway pole, one handrail, crossed bamboo legs
        self.legs = [40, 300, 560, 820, 1060]
        def poles(d, s):
            for x in self.legs:
                for sg in (-1, 1):
                    d.line([((x - sg * 80) * s, LEG_Y * s), ((x + sg * 62) * s, (RAIL_Y - 30) * s)], fill=255, width=int(14 * s))
        def walk(d, s):
            d.line([(px * s, self.walk_y(px) * s) for px in range(-40, W + 41, 40)], fill=255, width=int(18 * s), joint="curve")
            d.line([(px * s, self.rail_y(px) * s) for px in range(-40, W + 41, 40)], fill=255, width=int(12 * s), joint="curve")
        br = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        br.alpha_composite(texmul(shade(poles, (W, H), (100, 58, 30), 7, rim_strength=1.0), lambda xx, yy: 1 - 0.35 * ((yy % 90) < 5)))
        br.alpha_composite(texmul(shade(walk, (W, H), BAMBOO, 8, rim_strength=1.0), lambda xx, yy: 1 - 0.35 * ((xx % 120) < 5)))
        self.bridge = br
        # nipa clumps at the water's edge (mid layer) and blurred fronds in the foreground
        def mids(d, s):
            nipa(d, s, 60, 1290, 520, 1, n=8)
            nipa(d, s, 990, 1310, 560, 2, n=8)
            nipa(d, s, 1130, 1150, 400, 3, n=6)
        self.nipa = dof(inflate21(D5.smooth_mask(mids, (W + 200, H)), (30, 10, 9), radius=7, rim_strength=1.0), 0.8)
        def fgm(d, s):
            nipa(d, s, -60, 2100, 900, 4, n=6, spread=0.7)
            nipa(d, s, 1180, 2150, 980, 5, n=6, spread=0.7)
        self.fg = dof(inflate21(D5.smooth_mask(fgm, (W + 300, H)), (10, 4, 5), radius=10, rim_strength=0.6), 9)
        # static water: base + reflections (sky/bank flipped, the bridge flipped at the leg line) + the moon road
        self.water = {b: self._water(b) for b in (True, False)}

    @staticmethod
    def walk_y(x):
        return WALK_Y + 16 * math.sin(math.pi * min(max(x, 0), W) / W)

    @staticmethod
    def rail_y(x):
        return RAIL_Y + 10 * math.sin(math.pi * min(max(x, 0), W) / W)

    def _water(self, with_bridge):
        n = H - HZ
        yy, xx = np.mgrid[0:n, 0:W]
        g = yy / n
        base = np.stack([26 - 16 * g, 6 - 4 * g, 8 - 5 * g], -1).astype(np.float32)
        ab = to_arr(self.above)
        src = np.clip(HZ - 1 - (yy * 0.9).astype(int), 0, HZ - 1)
        refl = ab[src, xx] * (0.42 * (1 - 0.55 * g))[..., None]
        a = base + refl
        if with_bridge:
            bra = np.asarray(self.bridge, np.float32)
            ys = np.clip(2 * LEG_Y - (yy + HZ), 0, H - 1)
            bsrc = bra[ys, xx]
            m = (bsrc[..., 3:4] / 255) * ((yy + HZ) > LEG_Y)[..., None] * 0.55
            a = a * (1 - m) + bsrc[..., :3] * 0.4 * m
        noise = fog_texture(W, n, 57)
        streak = (np.sin(yy * 0.85 + noise * 9) > 0.5).astype(np.float32)
        road = np.exp(-((xx - MOON[0]) / (24 + 190 * g)) ** 2) * streak * (1 - 0.4 * g)
        a += road[..., None] * np.array([255, 96, 64], np.float32) * 0.85
        hl = (np.sin(yy * 0.55 + np.sin(xx / 90) * 2.5 + noise * 5) > 0.93).astype(np.float32) * 0.6 * (0.3 + g)
        a += hl[..., None] * np.array([90, 26, 20], np.float32)
        return a

    def water_rows(self, t, with_bridge=True, calm=1.0):
        st = self.water[with_bridge]
        n = st.shape[0]
        y = np.arange(n)
        g = y / n
        off = ((5 + 20 * g) * np.sin(y * 0.06 - t * 2.4) + 4 * np.sin(y * 0.23 + t * 3.1)) * calm
        idx = np.clip(np.arange(W)[None, :] + off[:, None].astype(int), 0, W - 1)
        return st[y[:, None], idx]

    def frame(self, t, cam=0.0, bridge=True, extra_water=None, extra_mid=None, extra_bridge=None, extra_front=None,
              fg=True, flies=True, lights=1.0, calm=1.0):
        a = to_arr(self.above)
        a[HZ:] = self.water_rows(t, bridge, calm)
        fl = lights * (0.82 + 0.18 * math.sin(t * 17) * math.sin(t * 5.3))
        for wx, wy in self.windows:
            add_glow(a, gsp(90, (255, 120, 60)), wx, wy, 0.7 * fl)
            add_glow(a, gsp(60, (255, 90, 50)), wx, 2 * HZ - wy + 30, 0.35 * fl)
        add_glow(a, gsp(120, (255, 50, 35)), *self.lantern, 0.9 * fl)
        img = to_img(a)
        P = lambda k: int(-cam * k)
        if extra_water:
            img = extra_water(img, t, P) or img
        img.alpha_composite(self.nipa, (P(0.5) - 100, 0))
        if extra_mid:
            img = extra_mid(img, t, P) or img
        if bridge:
            img.alpha_composite(self.bridge)
        if extra_bridge:
            img = extra_bridge(img, t, P) or img
        if flies:
            bokeh_particles(img, 18, 11, t, color=(255, 170, 90), size=(2, 7), blur=(0, 3), area=(0, 700, W, 1500), drift=(14, -8))
        if extra_front:
            img = extra_front(img, t, P) or img
        if fg:
            img.alpha_composite(self.fg, (P(1.6) - 150, 0))
        return img


_CN = None


def canal():
    global _CN
    if _CN is None:
        _CN = Canal()
    return _CN


def beam(img, x, y, k, length=700, spread=200, direction=1, down=0.0):
    """Torch cone (additive) from (x, y); direction +1 right / -1 left, down tilts it toward the water."""
    if k <= 0.01:
        return img
    m = Image.new("L", (W, H), 0)
    ex = x + direction * length
    ImageDraw.Draw(m).polygon([(x, y - 8), (ex, y - spread * 0.5 + down * length), (ex, y + spread + down * length)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(24))
    a = to_arr(img)
    xx = np.arange(W)[None, :]
    fall = np.clip(1 - np.abs(xx - x) / length, 0, 1) ** 0.8
    a += (np.asarray(m, np.float32) / 255 * fall)[..., None] * np.array([255, 220, 170]) * 0.45 * k
    add_glow(a, gsp(70, (255, 235, 200)), x, y, 1.0 * k)
    return to_img(a)


# ============================================================ the boat (inside + bow)
class BoatInside:
    """Inside a small sampan under the arched woven-bamboo canopy (mui), looking out of the open stern at the canal."""
    OX0, OY0, OX1, OY1 = 170, 380, 910, 1460       # opening

    def __init__(self):
        def canopy(d, s):
            d.rectangle([0, 0, W * s, H * s], fill=255)
            d.rectangle([self.OX0 * s, (self.OY0 + 250) * s, self.OX1 * s, self.OY1 * s], fill=0)
            d.ellipse([self.OX0 * s, self.OY0 * s, self.OX1 * s, (self.OY0 + 500) * s], fill=0)
        cm = D5.smooth_mask(canopy, (W, H))
        cp = inflate21(cm, (66, 34, 20), radius=70, rim_strength=1.1)
        cp = texmul(cp, lambda xx, yy: 0.62 + 0.38 * ((((xx + yy) // 22) % 2) ^ (((xx - yy) // 22) % 2)) * (0.8 + 0.2 * np.sin(yy / 90)))
        cp = texmul(cp, lambda xx, yy: 1 - 0.5 * np.clip(np.abs(xx - W / 2) / 700, 0, 1))      # ribs darker to the sides
        d = ImageDraw.Draw(cp)
        for k in range(7):                                                                    # bamboo ribs
            yk = 120 + k * 170
            d.arc([-260, yk - 300, W + 260, yk + 900], 200, 340, fill=(40, 18, 10, 255), width=10)
        # floor planks (perspective) + the stern beam across the opening
        fl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(fl)
        fd.polygon([(0, 1480), (W, 1480), (W, H), (0, H)], fill=(58, 26, 16, 255))
        for k in range(-6, 8):
            fd.line([(540 + k * 40, 1480), (540 + k * 260, H)], fill=(30, 12, 8, 255), width=5)
        for y in (1560, 1680, 1830):
            fd.line([(0, y), (W, y)], fill=(36, 14, 9, 255), width=3)
        self.floor = texmul(fl, lambda xx, yy: 0.85 + 0.15 * np.sin(xx / 7 + yy / 50))
        def beam_(d, s):
            d.rectangle([(self.OX0 - 40) * s, 1420 * s, (self.OX1 + 40) * s, 1500 * s], fill=255)
        self.beam = shade(beam_, (W, H), (92, 44, 26), 26, rim_strength=1.2)
        self.canopy = cp
        om = Image.new("L", (W, H), 0); od = ImageDraw.Draw(om)
        od.rectangle([self.OX0, self.OY0 + 250, self.OX1, self.OY1], fill=255)
        od.ellipse([self.OX0, self.OY0, self.OX1, self.OY0 + 500], fill=255)
        self.open_mask = om

    def frame(self, t, outside=True, behind_beam=None, front=None, water_floor=0.0, hair=None):
        img = Image.new("RGBA", (W, H), (6, 2, 3, 255))
        if outside:
            o = canal().frame(t, bridge=False, fg=False, flies=True)
            img.paste(o, (0, 0), self.open_mask)
        if behind_beam:
            img = behind_beam(img, t) or img
        img.alpha_composite(self.floor)
        if water_floor > 0:
            wl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); wd = ImageDraw.Draw(wl)
            y1 = 1500 + 420 * water_floor
            wd.polygon([(260 - 140 * water_floor, 1500), (820 + 160 * water_floor, 1500), (900 + 200 * water_floor, y1), (180 - 220 * water_floor, y1)],
                       fill=(16, 4, 6, 220))
            for k in range(5):
                yy = 1510 + k * 80 * water_floor + 10 * math.sin(t * 3 + k)
                wd.line([(330 - 60 * k * water_floor, yy), (760 + 60 * k * water_floor, yy)], fill=(255, 90, 60, int(110 * water_floor)), width=3)
            img.alpha_composite(wl)
        img.alpha_composite(self.beam)
        if hair:
            img = hair(img, t) or img
        img.alpha_composite(self.canopy)
        # drips from the canopy edge
        d = ImageDraw.Draw(img)
        for i, x in enumerate((300, 520, 760)):
            ph = (t * 0.8 + i * 0.41) % 1.0
            y = self.OY0 + 260 + ph * 900
            d.ellipse([x - 5, y - 9, x + 5, y + 9], fill=(255, 190, 170, int(200 * (1 - ph))))
        if front:
            img = front(img, t) or img
        return img


_BI = None


def boat_inside():
    global _BI
    if _BI is None:
        _BI = BoatInside()
    return _BI


_BOW = None


def boat_bow():
    """Side view of the sampan on the water, bow to the LEFT: dark hull, red band, a big painted eye on the bow,
    an arched woven canopy. Returns (RGBA 1080x700, eye_xy, waterline_y)."""
    global _BOW
    if _BOW is not None:
        return _BOW
    w, h = 1080, 700
    wl = 560

    def hull(d, s):
        d.polygon(P_((40, 380), (140, 420), (900, 450), (1060, 430), (1040, 520), (930, wl + 40), (180, wl + 40), (90, 480), s=s), fill=255)

    def canopy(d, s):
        d.rectangle([430 * s, 270 * s, 900 * s, 450 * s], fill=255)
        d.ellipse([430 * s, 170 * s, 900 * s, 380 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cp = shade(canopy, (w, h), (78, 40, 22), 40, rim_strength=1.1)
    cp = texmul(cp, lambda xx, yy: 0.65 + 0.35 * ((((xx + yy) // 14) % 2) ^ (((xx - yy) // 14) % 2)))
    img.alpha_composite(cp)
    hl = shade(hull, (w, h), (54, 24, 16), 40, rim_strength=1.1)
    hl = texmul(hl, lambda xx, yy: 1 - 0.18 * ((yy % 34) < 3))
    img.alpha_composite(hl)
    d = ImageDraw.Draw(img)
    d.line([(60, 392), (140, 428), (900, 456), (1050, 438)], fill=(150, 20, 18, 255), width=18)       # red band
    d.polygon([(46, 392), (150, 430), (240, 520), (120, 520), (84, 478)], fill=(128, 18, 16, 255))     # red-painted bow
    ex, ey = 175, 470
    d.ellipse([ex - 62, ey - 30, ex + 62, ey + 30], fill=(18, 8, 8, 255))
    d.polygon([(ex - 58, ey), (ex - 10, ey - 26), (ex + 50, ey - 14), (ex + 58, ey + 4), (ex + 10, ey + 24), (ex - 40, ey + 18)], fill=(232, 226, 212, 255))
    d.ellipse([ex - 18, ey - 18, ex + 18, ey + 18], fill=(10, 6, 6, 255))
    d.ellipse([ex - 6, ey - 12, ex + 4, ey - 2], fill=(255, 255, 255, 255))
    d.arc([ex - 70, ey - 50, ex + 70, ey + 10], 200, 340, fill=(240, 190, 60, 255), width=6)          # brow
    _BOW = (img, (ex, ey), wl)
    return _BOW


# ============================================================ shrine, house, props
_SH = None


def shrine():
    """A small roadside shrine (mieu): a weathered pillar, a little red house with an upturned tiled roof,
    an incense bowl inside. Returns (RGBA 520x980, incense_xy)."""
    global _SH
    if _SH is not None:
        return _SH
    w, h = 520, 980
    cx = 260

    def pillar(d, s):
        d.rectangle([(cx - 50) * s, 520 * s, (cx + 50) * s, 940 * s], fill=255)
        d.rectangle([(cx - 90) * s, 900 * s, (cx + 90) * s, 980 * s], fill=255)

    def house(d, s):
        d.rectangle([(cx - 150) * s, 300 * s, (cx + 150) * s, 530 * s], fill=255)

    def roof(d, s):
        d.polygon(P_((cx - 230, 300), (cx - 200, 286), (cx - 120, 160), (cx + 120, 160), (cx + 200, 286), (cx + 230, 300),
                     (cx + 250, 262), (cx + 240, 320), (cx - 240, 320), (cx - 250, 262), s=s), fill=255)
        d.rectangle([(cx - 120) * s, 140 * s, (cx + 120) * s, 166 * s], fill=255)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(texmul(shade(pillar, (w, h), (120, 106, 98), 30), lambda xx, yy: 0.8 + 0.2 * np.sin(xx / 5 + yy / 13) ** 2))
    img.alpha_composite(shade(house, (w, h), (168, 36, 28), 40))
    d = ImageDraw.Draw(img)
    d.rectangle([cx - 100, 340, cx + 100, 520], fill=(24, 8, 6, 255))                                   # niche
    d.rectangle([cx - 104, 336, cx + 104, 344], fill=(220, 170, 60, 255))
    d.chord([cx - 50, 470, cx + 50, 530], 0, 180, fill=(150, 110, 50, 255))                            # incense bowl
    d.rectangle([cx - 50, 490, cx + 50, 500], fill=(150, 110, 50, 255))
    img.alpha_composite(texmul(shade(roof, (w, h), (150, 40, 26), 26), lambda xx, yy: 1 - 0.25 * ((xx % 26) < 4)))
    _SH = (img, (cx, 480))
    return _SH


def room_bg(dawn=0.0):
    """Grandma's stilt house: vertical plank walls, a shuttered window on the river, the ancestor altar with red lamps,
    a kerosene lamp, the plank bed."""
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    a = np.zeros((H, W, 3), np.float32)
    a[..., 0] = 72; a[..., 1] = 34; a[..., 2] = 22
    a *= (0.78 + 0.22 * ((x % 120) > 6))[..., None] * (0.75 + 0.35 * fog_texture(W, H, 87))[..., None]
    im = to_img(a); d = ImageDraw.Draw(im)
    # window
    d.rectangle([110, 470, 470, 860], fill=(40, 8, 10, 255))
    for k in range(6):
        d.line([(110, 700 + k * 30), (470, 700 + k * 30 + 4)], fill=(150, 40, 30, 255), width=3)
    d.ellipse([170, 520, 260, 610], fill=(230, 100, 70, 255))
    d.rectangle([100, 460, 480, 474], fill=(44, 20, 12, 255)); d.rectangle([100, 856, 480, 872], fill=(44, 20, 12, 255))
    d.polygon([(110, 470), (20, 500), (20, 840), (110, 860)], fill=(50, 22, 14, 255))
    d.polygon([(470, 470), (560, 500), (560, 840), (470, 860)], fill=(50, 22, 14, 255))
    # ancestor altar shelf
    d.rectangle([640, 520, 1010, 540], fill=(90, 30, 18, 255))
    d.rectangle([650, 540, 1000, 620], fill=(140, 20, 22, 255))
    d.rectangle([760, 380, 880, 516], fill=(30, 20, 18, 255)); d.rectangle([772, 392, 868, 504], fill=(90, 80, 74, 255))
    d.rectangle([700, 470, 740, 516], fill=(160, 120, 60, 255))
    for k in range(3):
        d.line([(712 + k * 8, 470), (708 + k * 10, 420)], fill=(150, 60, 40, 255), width=3)
    # plank bed
    d.rectangle([0, 1380, W, 1430], fill=(96, 50, 30, 255)); d.rectangle([0, 1430, W, H], fill=(36, 16, 10, 255))
    for k in range(0, W, 140):
        d.line([(k, 1380), (k, 1430)], fill=(60, 28, 16, 255), width=4)
    # kerosene lamp on a stool
    d.rectangle([150, 1180, 330, 1200], fill=(70, 34, 20, 255))
    d.ellipse([200, 1100, 280, 1180], fill=(150, 110, 60, 255))
    d.ellipse([212, 1010, 268, 1110], fill=(255, 190, 110, 200))
    return im


def home_bg():
    """Bao's house at dawn: plank wall, an open window with grey-pink light, a wooden stand with a red plastic basin."""
    a = np.zeros((H, W, 3), np.float32)
    x = np.arange(W)[None, :]
    a[..., 0] = 88; a[..., 1] = 48; a[..., 2] = 36
    a *= (0.8 + 0.2 * ((x % 130) > 6))[..., None] * (0.78 + 0.3 * fog_texture(W, H, 91))[..., None]
    im = to_img(a); d = ImageDraw.Draw(im)
    d.rectangle([600, 300, 980, 760], fill=(186, 150, 150, 255))
    for k in range(4):
        d.line([(600, 340 + k * 110), (980, 330 + k * 110)], fill=(150, 110, 110, 255), width=3)
    d.rectangle([590, 290, 990, 306], fill=(50, 24, 16, 255)); d.rectangle([590, 754, 990, 770], fill=(50, 24, 16, 255))
    d.rectangle([780, 300, 796, 760], fill=(50, 24, 16, 255))
    d.rectangle([0, 1560, W, H], fill=(46, 22, 14, 255))
    return im


def basin_sprite():
    """A red plastic wash basin on a little wooden stand (side view), 620x520."""
    w, h = 620, 520
    def b(d, s):
        d.polygon(P_((40, 150), (580, 150), (520, 300), (100, 300), s=s), fill=255)
        d.ellipse([20 * s, 120 * s, 600 * s, 180 * s], fill=255)
    def stand(d, s):
        d.rectangle([80 * s, 300 * s, 540 * s, 330 * s], fill=255)
        for x in (110, 490):
            d.line([(x * s, 330 * s), ((x + (x - 300) * 0.2) * s, 520 * s)], fill=255, width=int(24 * s))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(shade(stand, (w, h), (90, 48, 28), 12))
    img.alpha_composite(shade(b, (w, h), (196, 28, 30), 30))
    d = ImageDraw.Draw(img)
    d.ellipse([44, 128, 576, 172], fill=(40, 10, 12, 255))
    return img


def heron(flap):
    """Night heron silhouette in flight (false scare), wings at angle flap (-1..1). 420x260."""
    w, h = 420, 260
    def body(d, s):
        d.ellipse([140 * s, 110 * s, 300 * s, 160 * s], fill=255)
        d.ellipse([280 * s, 90 * s, 330 * s, 130 * s], fill=255)
        d.polygon(P_((328, 104), (400, 116), (328, 120), s=s), fill=255)
        d.polygon(P_((150, 130), (60, 150), (150, 146), s=s), fill=255)
        ay = 130 - 110 * flap
        d.polygon(P_((170, 125), (260, 125), (300, ay - 10), (120, ay), s=s), fill=255)
    return shade(body, (w, h), (30, 22, 24), 14, rim_strength=1.2)
