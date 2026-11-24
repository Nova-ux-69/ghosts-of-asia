"""Ep08 Singapore / Pulau Tekong - 2.1D survival version. make_<id>(D, caps) -> f(t) -> float RGB (H, W, 3)."""
import os, sys, math
os.environ["STYLE"] = "flat21"
_EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_EP, "..", "ep07b-myanmar-2p1d")); sys.path.insert(0, os.path.join(_EP, "..", "..", "toolkit"))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import W, H, font, text_img, with_alpha, ease, glow_sprite, add_glow, fog_texture, INTER_SB, INTER_M, LORA
from depth import dof, bokeh_particles
import demo25_myanmar as D5
from scenes_v import series_header, header_layers, pill
from scenes_ep7b import ss, shade, to_arr, finish, fog, eye, VIG, VIG_H, YEL

GY = 1180
TORCH = glow_sprite(300, (255, 235, 190), 1.6)
TORCH_S = glow_sprite(40, (255, 250, 230), 1.2)
FLOOD = glow_sprite(420, (255, 230, 200), 1.7)


# ============================================================ flag + header
def sg_flag(w=240):
    h = int(w * 2 / 3)
    s = 3
    im = Image.new("RGBA", (w * s, h * s), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w * s, h * s // 2], fill=(238, 36, 53, 255))
    R = h * s * 0.2; cx, cy = w * s * 0.25, h * s * 0.25
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 255, 255, 255))
    d.ellipse([cx - R + R * 0.35, cy - R * 0.95, cx + R * 1.3, cy + R * 0.95], fill=(238, 36, 53, 255))
    sr = R * 0.18
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        sx, sy = cx + R * 0.95 + math.cos(a) * R * 0.5, cy + math.sin(a) * R * 0.5
        pts = []
        for j in range(10):
            rr = sr if j % 2 == 0 else sr * 0.42
            b = -math.pi / 2 + j * math.pi / 5
            pts.append((sx + math.cos(b) * rr, sy + math.sin(b) * rr))
        d.polygon(pts, fill=(255, 255, 255, 255))
    return im.resize((w, h), Image.LANCZOS)


FLAG = sg_flag(170)


def flag_layer(t):
    """Waving flag (vertical sine shear) with a soft shadow."""
    w, h = FLAG.size
    a = np.asarray(FLAG)
    out = np.zeros((h + 30, w, 4), np.uint8)
    for x in range(w):
        dy = int(8 * math.sin(t * 4 - x / 30) * (x / w))
        out[15 + dy:15 + dy + h, x] = a[:, x]
    im = Image.fromarray(out, "RGBA")
    # shading of the folds
    sh = np.asarray(im, np.float32).copy()
    xs = np.arange(w)[None, :]
    sh[..., :3] *= (0.85 + 0.15 * np.sin(t * 4 - xs / 30))[..., None]
    return Image.fromarray(np.clip(sh, 0, 255).astype(np.uint8), "RGBA")


def header(img, t, part):
    hdr = series_header("SINGAPORE", part)
    for im, (x, y), al in header_layers(hdr, t):
        if al > 0.01:
            img.alpha_composite(with_alpha(im, al), (int(x), int(y)))
    fl = flag_layer(t)
    img.alpha_composite(fl, (int(W / 2 - fl.width / 2), 36))


_HDR = {}


# ============================================================ characters
_SC = {}


def soldier(phase=0.0, run=0.0, torch=True, ghost=False, back=False, scale=1.0, tilt=0.0):
    q = (round(phase * 12) % 12, round(run, 1), torch, ghost, back, round(scale, 2), round(tilt, 1))
    if q in _SC:
        return _SC[q]
    w, h = 440, 880
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.3 + 0.7 * run)
    L = 14 * run
    uni = (46, 52, 40) if ghost else (66, 80, 48)
    skin = (168, 178, 176) if ghost else (150, 104, 78)
    def legs(d, s):
        for sg in (-1, 1):
            a = sg * sw * 0.55
            hx, hy = cx + L * 0.3 + sg * 26, 430
            kx, ky = hx + math.sin(a) * 150, hy + math.cos(a) * 160
            fx, fy = kx + math.sin(a - 0.35 * run) * 130, ky + 170
            d.line([(hx * s, hy * s), (kx * s, ky * s), (fx * s, fy * s)], fill=255, width=int(44 * s), joint="curve")
    def boots(d, s):
        for sg in (-1, 1):
            a = sg * sw * 0.55
            hx, hy = cx + L * 0.3 + sg * 26, 430
            kx, ky = hx + math.sin(a) * 150, hy + math.cos(a) * 160
            fx, fy = kx + math.sin(a - 0.35 * run) * 130, ky + 170
            d.rounded_rectangle([(fx - 26) * s, (fy - 30) * s, (fx + 36) * s, (fy + 14) * s], int(10 * s), fill=255)
    def torso(d, s):
        d.polygon([(x * s, y * s) for x, y in ((cx - 86 + L, 190), (cx + 86 + L, 190), (cx + 74 + L * 0.6, 450), (cx - 74 + L * 0.6, 450))], fill=255)
        d.ellipse([(cx - 90 + L) * s, 175 * s, (cx - 40 + L) * s, 240 * s], fill=255); d.ellipse([(cx + 40 + L) * s, 175 * s, (cx + 90 + L) * s, 240 * s], fill=255)
    def arms(d, s):
        for sg in (-1, 1):
            sx, sy = cx + sg * 76 + L, 210
            if ghost:
                ex, ey, hx, hy = sx + sg * 10, sy + 130, sx + sg * 14, sy + 260
            else:
                a = -sg * sw * 0.9
                ex, ey = sx + math.sin(a) * 100 + sg * 8, sy + math.cos(a) * 110
                b = a - 0.9 * run * sg
                hx, hy = ex + math.sin(b) * 100, ey + math.cos(b) * 90 - 40 * run
            d.line([(sx * s, sy * s), (ex * s, ey * s), (hx * s, hy * s)], fill=255, width=int(34 * s), joint="curve")
    def hands(d, s):
        for sg in (-1, 1):
            sx, sy = cx + sg * 76 + L, 210
            if ghost:
                hx, hy = sx + sg * 14, sy + 270
            else:
                a = -sg * sw * 0.9
                ex, ey = sx + math.sin(a) * 100 + sg * 8, sy + math.cos(a) * 110
                b = a - 0.9 * run * sg
                hx, hy = ex + math.sin(b) * 100, ey + math.cos(b) * 90 - 40 * run
            d.ellipse([(hx - 18) * s, (hy - 14) * s, (hx + 18) * s, (hy + 22) * s], fill=255)
    def head(d, s):
        LL = L * 1.2
        d.rectangle([(cx - 22 + LL) * s, 140 * s, (cx + 22 + LL) * s, 200 * s], fill=255)
        d.ellipse([(cx - 52 + LL) * s, 50 * s, (cx + 52 + LL) * s, 172 * s], fill=255)
    def helmet(d, s):   # short army haircut (no helmet, like the reference photo)
        LL = L * 1.2
        d.pieslice([(cx - 55 + LL) * s, 44 * s, (cx + 55 + LL) * s, 150 * s], 180, 360, fill=255)
        if ghost:   # wet hair strands stuck to the forehead
            for k in range(5):
                x = cx - 40 + k * 20 + LL
                d.polygon([((x - 7) * s, 90 * s), ((x + 7) * s, 90 * s), ((x + 2) * s, (128 + 10 * (k % 2)) * s)], fill=255)
    def vest(d, s):     # webbing with pouches
        for x0 in (-70, -22, 26):
            d.rounded_rectangle([(cx + x0 + L * 0.8) * s, 330 * s, (cx + x0 + 44 + L * 0.8) * s, 400 * s], int(6 * s), fill=255)
        d.rectangle([(cx - 76 + L * 0.6) * s, 412 * s, (cx + 76 + L * 0.6) * s, 438 * s], fill=255)
    def rifle(d, s):
        pts = [(cx - 120, 420), (cx + 110, 260), (cx + 122, 276), (cx - 104, 438)]
        d.polygon([((x + L) * s, y * s) for x, y in pts], fill=255)
        d.polygon([((x + L) * s, y * s) for x, y in ((cx - 20, 360), (cx + 4, 344), (cx + 30, 400), (cx + 8, 414))], fill=255)
        d.polygon([((x + L) * s, y * s) for x, y in ((cx - 120, 420), (cx - 170, 440), (cx - 160, 470), (cx - 104, 438))], fill=255)
    def straps(d, s):
        for sg in (-1, 1):
            d.line([((cx + sg * 55 + L) * s, 195 * s), ((cx + sg * 40 + L * 0.7) * s, 440 * s)], fill=255, width=int(16 * s))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.alpha_composite(shade(legs, (w, h), uni, 18))
    im.alpha_composite(shade(boots, (w, h), (24, 22, 22), 10))
    im.alpha_composite(shade(torso, (w, h), uni, 40))
    im.alpha_composite(shade(straps, (w, h), (40, 46, 32), 6))
    im.alpha_composite(shade(arms, (w, h), uni, 14))
    im.alpha_composite(shade(hands, (w, h), skin, 10))
    im.alpha_composite(shade(head, (w, h), skin, 30))
    im.alpha_composite(shade(vest, (w, h), (58, 64, 44) if not ghost else (36, 40, 32), 8))
    im.alpha_composite(shade(helmet, (w, h), (16, 14, 14), 12))
    d = ImageDraw.Draw(im)
    LL = L * 1.2
    # uniform camo blotches
    rng = np.random.default_rng(3)
    a = np.asarray(im, np.float32).copy()
    tex = fog_texture(w, h, 17 if not ghost else 18)
    body = (a[..., 3] > 0)
    yy = np.arange(h)[:, None]
    t2 = fog_texture(w, h, 27 if not ghost else 28); t3 = fog_texture(w, h, 37)
    cloth = (body & (yy > 185)) | (body & (yy < 0))
    cl = np.zeros((h, w), bool); cl[:, :] = False
    xx = np.arange(w)[None, :]
    cloth = body & (yy > 185) & ~((yy > 860))
    for m, col in (((tex > 0.5), (40, 70, 32)), ((t2 > 0.53), (78, 54, 34)), ((t3 > 0.6), (18, 18, 16))):
        mm = (m & cloth)[..., None]
        sh = a[..., :3] / (np.array(uni, np.float32) + 1e-3)          # keep the light/shadow of the base shading
        lum = np.clip(sh.mean(2, keepdims=True), 0.25, 1.1)
        a[..., :3] = np.where(mm, np.array(col, np.float32) * lum, a[..., :3])
    if ghost:
        a[..., :3] *= 0.6
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(im)
    if ghost:
        # hollow black eye sockets and an open mouth; water dripping down the uniform
        for sg in (-1, 1):
            d.ellipse([cx + sg * 22 - 16 + LL, 104, cx + sg * 22 + 16 + LL, 132], fill=(8, 6, 6, 255))
        d.ellipse([cx - 12 + LL, 144, cx + 12 + LL, 166], fill=(10, 6, 6, 255))
        for x in range(int(cx - 70), int(cx + 70), 18):
            d.line([(x, 250 + (x * 7) % 60), (x, 330 + (x * 13) % 120)], fill=(120, 150, 150, 120), width=3)
        eyes = ((cx - 22 + LL, 120), (cx + 22 + LL, 120))
    elif not back:
        for sg in (-1, 1):        # camo face paint on the cheeks and forehead
            d.line([(cx + sg * 44 + LL, 136), (cx + sg * 22 + LL, 142)], fill=(36, 48, 28, 150), width=7)
        d.line([(cx - 30 + LL, 92), (cx + 26 + LL, 96)], fill=(36, 48, 28, 140), width=6)
        for sg in (-1, 1):
            d.ellipse([cx + sg * 20 - 9 + LL, 112, cx + sg * 20 + 9 + LL, 128], fill=(240, 236, 230, 255))
            d.ellipse([cx + sg * 20 - 4 + LL, 116, cx + sg * 20 + 4 + LL, 124], fill=(15, 10, 10, 255))
        d.ellipse([cx - 7 + LL, 148, cx + 7 + LL, 158], fill=(70, 30, 30, 255))
        eyes = None
    else:
        eyes = None
    if not ghost and not back and run < 0.5:
        im.alpha_composite(shade(rifle, (w, h), (26, 26, 26), 6, rim_strength=0.5))
        d = ImageDraw.Draw(im)
    tp = None
    if torch and not ghost and not back:
        tx, ty = cx - 40 + L, 260
        d.rounded_rectangle([tx - 14, ty - 18, tx + 14, ty + 18], 5, fill=(30, 30, 30, 255))
        d.ellipse([tx - 9, ty - 9, tx + 9, ty + 9], fill=(255, 250, 220, 255))
        tp = (tx, ty)
    if tilt:
        im = im.rotate(tilt, Image.BICUBIC, center=(cx, 180))
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    sc = scale
    out = (im, cx * sc, 870 * sc, (tp[0] * sc, tp[1] * sc) if tp else None, [(e[0] * sc, e[1] * sc) for e in eyes] if eyes else None)
    _SC[q] = out
    return out


def put(img, spr, x, feet_y):
    im, fx, fy, tp, eyes = spr
    ox, oy = int(x - fx), int(feet_y - fy)
    img.alpha_composite(im, (ox, oy))
    return (ox + tp[0], oy + tp[1]) if tp else None, [(ox + e[0], oy + e[1]) for e in eyes] if eyes else None


def put_ghost(img, x, feet_y, scale, t, eyes_k=1.0, aura=0.5, tilt=-12):
    spr = soldier(0, 0, False, ghost=True, scale=scale, tilt=tilt)
    im = spr[0]
    if aura > 0:
        gl = im.split()[3].filter(ImageFilter.GaussianBlur(max(2, 30 * scale)))
        lay = Image.new("RGBA", im.size, (200, 230, 220, 0)); lay.putalpha(gl.point(lambda v: int(v * aura)))
        img.alpha_composite(lay, (int(x - spr[1]), int(feet_y - spr[2])))
    _, eyes = put(img, spr, x + 3 * math.sin(t * 1.1), feet_y)
    if eyes and eyes_k > 0:
        k = eyes_k * (0.6 + 0.4 * math.sin(t * 5) ** 2)
        for e in eyes:
            eye(img, e[0], e[1], k, scale * 0.9)


# ============================================================ worlds
RAIN = []
for i in range(6):
    r = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(r)
    rg = np.random.default_rng(100 + i)
    for _ in range(420):
        x, y = rg.uniform(-100, W), rg.uniform(-100, H); L_ = rg.uniform(40, 110)
        d.line([(x, y), (x + L_ * 0.18, y + L_)], fill=(220, 200, 200, int(rg.uniform(40, 110))), width=int(rg.choice([1, 2, 2, 3])))
    RAIN.append(r)


def rain(img, t, k=1.0):
    r = RAIN[int(t * 30) % 6]
    img.alpha_composite(with_alpha(r, k) if k < 1 else r)


def tree_trunk(seed, height=1500, width=70, base=(34, 22, 20)):
    rng = np.random.default_rng(seed)
    w = int(width * 4) + 120
    def dr(d, s):
        cx = w / 2
        pts = [(cx - width / 2, height), (cx - width * 0.4, 0), (cx + width * 0.4, 0), (cx + width / 2, height)]
        d.polygon([(x * s, y * s) for x, y in pts], fill=255)
        for k in range(3):        # buttress roots
            sg = rng.choice([-1, 1])
            d.polygon([((cx + sg * width * 0.3) * s, (height - 220) * s), ((cx + sg * (width * 0.5 + rng.uniform(40, 90))) * s, height * s), ((cx + sg * width * 0.2) * s, height * s)], fill=255)
        for k in range(2):        # vines
            x0 = cx + rng.uniform(-width, width)
            d.line([(x0 * s, 0), ((x0 + rng.uniform(-30, 30)) * s, rng.uniform(300, 900) * s)], fill=255, width=int(6 * s))
    return shade(dr, (w, height), base, max(10, width * 0.5))


class Jungle:
    def __init__(self):
        y = np.linspace(0, 1, H)[:, None]
        top = np.array([3, 2, 3]); mid = np.array([26, 6, 8]); hor = np.array([58, 14, 14])
        k = np.clip(y / 0.62, 0, 1) ** 1.5
        col = top * (1 - k) + mid * k
        col = col * (1 - np.clip((y - 0.5) / 0.15, 0, 1)) + hor * np.clip((y - 0.5) / 0.15, 0, 1)
        sk = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
        cl = fog_texture(W, H, 61)
        sk = sk * (0.8 + 0.4 * cl[..., None])
        self.sky = Image.fromarray(np.clip(sk, 0, 255).astype(np.uint8)).convert("RGBA")
        self.far = dof(D5.treeline(11, 120, 1.4, (26, 10, 12), 900), 4)
        self.mid = dof(D5.treeline(12, 60, 1.6, (12, 5, 7), 800), 2)
        self.trunks_far = [dof(tree_trunk(s, 1300, 40, (40, 22, 20)), 2.5) for s in range(4)]
        self.trunks = [tree_trunk(10 + s, 1700, 70 + 15 * (s % 3)) for s in range(5)]
        LW = 2400
        g = np.zeros((H, W, 4), np.float32)
        yy = np.arange(H)[:, None]
        gt = np.clip((yy - GY) / 700, 0, 1)
        g[..., 0] = 30 - 22 * gt; g[..., 1] = 11 - 8 * gt; g[..., 2] = 9 - 6 * gt
        g[..., :3] *= (0.6 + 0.8 * fog_texture(W, H, 63))[..., None]
        g[..., 3] = 255 * (yy >= GY)
        # red-earth track: a lighter band, wet
        track = ((yy >= GY + 40) & (yy <= GY + 170)).astype(np.float32)
        g[..., :3] = g[..., :3] * (1 - track[..., None]) + np.array([70, 30, 20]) * (0.7 + 0.5 * fog_texture(W, H, 64))[..., None] * track[..., None]
        self.ground = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGBA")
        gr = Image.new("L", (W + 600, 600), 0); d = ImageDraw.Draw(gr)
        rg = np.random.default_rng(66)
        for _ in range(260):
            x = rg.uniform(0, W + 600); hh = rg.uniform(150, 560); lean = rg.uniform(-80, 80)
            d.polygon([(x - 7, 600), (x + 7, 600), (x + lean, 600 - hh)], fill=255)
        self.grass = dof(Image.merge("RGBA", (Image.new("L", gr.size, 8), Image.new("L", gr.size, 4), Image.new("L", gr.size, 4), gr)), 7)

    def frame(self, t, cam, back=None, front=None, near=True, grass=True, fog_k=0.35):
        img = self.sky.copy()
        P = lambda k: int(-cam * k)
        img.alpha_composite(self.far, (P(0.08) % 300 - 300, GY - 900 + 160))
        for i, tr in enumerate(self.trunks_far):
            x = (P(0.25) + 140 + i * 290) % (W + 300) - 150
            img.alpha_composite(tr, (x - tr.width // 2, GY - tr.height + 40))
        img.alpha_composite(self.mid, (P(0.3) % 300 - 300, GY - 800 + 120))
        fog(img, t, fog_k, GY - 500, GY + 50, speed=14, col=(120, 40, 38))
        img.alpha_composite(self.ground)
        if back:
            back(img, t, P)
        if near:
            for i, tr in enumerate(self.trunks):
                x = (P(0.75) + 60 + i * 300) % (W + 500) - 250
                img.alpha_composite(tr, (x - tr.width // 2, GY + 60 - tr.height + (i % 2) * 40))
        if front:
            front(img, t, P)
        fog(img, t, fog_k * 0.8, GY - 100, GY + 500, speed=24, col=(130, 45, 42), off=200)
        if grass:
            img.alpha_composite(self.grass, (P(1.6) % 600 - 600, H - 600 + 90))
        return img


_J = None


def jungle():
    global _J
    if _J is None:
        _J = Jungle()
    return _J


def torch_glow(img, pos, k=1.0, beam_dir=1):
    if pos is None or k <= 0:
        return img
    a = to_arr(img)
    add_glow(a, TORCH, pos[0] + beam_dir * 120, pos[1] + 140, 0.55 * k)
    add_glow(a, TORCH_S, pos[0], pos[1], 1.2 * k)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


# ============================================================ scenes
def make_hook(D, caps):
    J = jungle()
    t2 = caps[1][1]
    def f(t):
        def back(img, tt, P):
            if tt > t2 - 0.2:
                put_ghost(img, P(0.5) + 820, GY + 30, 0.42, tt, eyes_k=ss(tt, t2, t2 + 0.8), aura=0.3)
        img = J.frame(t, cam=-60 + 50 * t / D, back=back)
        rain(img, t)
        push = 1.0 + 0.04 * t / D + 0.12 * ss(t, t2 + 0.5, D)
        a = finish(img, t, VIG_H, push=push, cx=700, cy=GY - 300)
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        header(out, t, "PART 1")
        return to_arr(out)
    return f


def make_ferry(D, caps):
    y = np.linspace(0, 1, H)[:, None]
    def f(t):
        sk = np.broadcast_to((np.array([8, 4, 6]) * (1 - y) + np.array([90, 24, 22]) * y)[:, None, :], (H, W, 3)).copy()
        img = Image.fromarray(np.clip(sk, 0, 255).astype(np.uint8)).convert("RGBA")
        J = jungle()
        img.alpha_composite(J.far, (-150 - int(10 * t), 1020 - 900 + 100))         # the island
        d = ImageDraw.Draw(img)
        sea = np.zeros((H, W, 4), np.float32); yy = np.arange(H)[:, None]
        sea[..., 0] = 40; sea[..., 1] = 10; sea[..., 2] = 14
        sea[..., :3] *= (0.6 + 0.6 * np.abs(np.sin(yy / 9 + t * 2 + np.arange(W)[None, :] / 70)))[..., None] * 0.9
        sea[..., 3] = 255 * (yy >= 1040)
        img.alpha_composite(Image.fromarray(np.clip(sea, 0, 255).astype(np.uint8), "RGBA"))
        # ferry crossing
        bx = 900 - 520 * t / D; by = 1190 + 6 * math.sin(t * 2)
        d = ImageDraw.Draw(img)
        d.polygon([(bx - 260, by - 40), (bx + 260, by - 40), (bx + 220, by + 40), (bx - 230, by + 40)], fill=(26, 22, 24, 255))
        d.rectangle([bx - 150, by - 130, bx + 120, by - 40], fill=(40, 36, 38, 255))
        for k in range(5):
            d.rectangle([bx - 130 + k * 50, by - 110, bx - 100 + k * 50, by - 80], fill=(255, 210, 140, 255))
        a = to_arr(img)
        for k in range(5):
            add_glow(a, glow_sprite(60, (255, 200, 120), 1.4), bx - 115 + k * 50, by - 95, 0.6)
        add_glow(a, glow_sprite(160, (255, 40, 30), 1.6), bx + 250, by - 50, 0.5 * (math.sin(t * 6) > 0))
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        fog(img, t, 0.35, 900, 1300, speed=10)
        rain(img, t)
        lbl = text_img("PULAU TEKONG", font(LORA, 92, "Bold"), fill=(250, 240, 225, 255), glow=(170, 20, 35, 220), pad=20)
        img.alpha_composite(with_alpha(lbl, ss(t, 0.3, 1.0) * (1 - ss(t, caps[1][1] - 0.3, caps[1][1] + 0.2))), (int(W / 2 - lbl.width / 2), 420))
        return finish(img, t, push=1.06 - 0.05 * t / D)
    return f


def make_rule(D, caps):
    J = jungle()
    def f(t):
        tps = []
        def front(img, tt, P):
            for i in range(5):
                spr = soldier((tt * 0.8 + i * 0.2) % 1, 0, True, scale=0.5)
                tp, _ = put(img, spr, P(0.9) + 420 + i * 120, GY + 120)
                tps.append(tp)
            sg = soldier(0, 0, False, back=True, scale=0.75)
            put(img, sg, 170, GY + 150)
        img = J.frame(t, cam=20 * t, front=front)
        for tp in tps:
            img = torch_glow(img, tp, 0.6)
        rain(img, t)
        return finish(img, t, push=1.02 + 0.05 * t / D)
    return f


def make_fall(D, caps):
    J = jungle()
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        info = {}
        def back(img, tt, P):
            # the platoon's torches far ahead on the track, fading away
            a = to_arr(img)
            k = 1 - ss(tt, t3 - 1.0, t3 + 0.5)
            for i in range(5):
                add_glow(a, glow_sprite(40, (255, 240, 200), 1.2), 760 + i * 40 + 30 * tt, GY + 40, 0.9 * k)
            img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"))
        def front(img, tt, P):
            spr = soldier((tt * 0.5) % 1, 0, True, scale=0.95)
            tp, _ = put(img, spr, 330, GY + 140)
            info["tp"] = tp
        img = J.frame(t, cam=30 * t, back=back, front=front)
        fl = 1.0
        if t > t2:
            fl = 0.5 + 0.5 * (math.sin(t * 23) > -0.3) * (math.sin(t * 7) > -0.6)
        img = torch_glow(img, info["tp"], fl)
        rain(img, t)
        return finish(img, t, vig=VIG_H if t > t3 else VIG, push=1.03 + 0.08 * ss(t, t3, D), cx=330, cy=GY - 300)
    return f


def make_voice(D, caps):
    J = jungle()
    words = [text_img("Darren...", font(LORA, 64 + 10 * i, "Bold"), fill=(230, 220, 215, 255), glow=(160, 20, 20, 200), pad=16) for i in range(3)]
    def f(t):
        info = {}
        def front(img, tt, P):
            spr = soldier(0, 0, True, scale=0.95)
            info["tp"], _ = put(img, spr, 760, GY + 140)
        img = J.frame(t, cam=0, front=front)
        img = torch_glow(img, info["tp"], 0.7 + 0.3 * (math.sin(t * 19) > 0), beam_dir=-1)
        for i, (wx, wy, tt) in enumerate(((180, 640, 0.4), (330, 900, 1.6), (120, 1080, 3.0))):
            k = ss(t, tt, tt + 0.6) * (1 - ss(t, tt + 1.8, tt + 2.6))
            if k > 0:
                img.alpha_composite(with_alpha(words[i], k * 0.85), (int(wx + 10 * math.sin(t * 3 + i)), int(wy)))
        rain(img, t)
        return finish(img, t, vig=VIG_H, push=1.0 + 0.1 * t / D, cx=600, cy=900)
    return f


def make_answer(D, caps):
    J = jungle()
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        info = {}
        def back(img, tt, P):
            a = to_arr(img)
            if tt > t2 - 0.3:   # the buddy's torch far ahead
                add_glow(a, glow_sprite(60, (255, 240, 200), 1.2), 820, GY + 30, 1.0 * ss(tt, t2 - 0.3, t2 + 0.3))
            img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"))
            if tt > t3 - 0.4:   # the viewer sees it between the trees on the left
                put_ghost(img, 130, GY + 60, 0.55, tt, eyes_k=ss(tt, t3, t3 + 0.6), aura=0.3)
        def front(img, tt, P):
            spr = soldier(0, 0, True, back=True, scale=1.0)
            put(img, spr, 560, GY + 160)
        img = J.frame(t, cam=-40 + 20 * t / D, back=back, front=front)
        rain(img, t)
        z = 1.0 + 0.05 * t / D + 0.2 * ss(t, t3, D)
        return finish(img, t, vig=VIG_H, push=z, cx=300 if t > t3 else W / 2, cy=GY - 200)
    return f


def make_cliff(D, caps):
    J = jungle()
    t2, t3, t4 = caps[1][1], caps[2][1], caps[3][1]
    def f(t):
        info = {}
        dark = t > t2 + 0.3
        def back(img, tt, P):
            sc = 0.6 + 0.25 * ss(tt, 0.2, t2)
            put_ghost(img, 250 + 60 * ss(tt, 0.2, t2), GY + 120, sc, tt, eyes_k=1.0, aura=0.4)
        def front(img, tt, P):
            spr = soldier(0, 0, True, scale=1.0)
            info["tp"], _ = put(img, spr, 720, GY + 160)
            if tt > t3:   # it's right behind him
                put_ghost(img, 820, GY + 180, 1.05, tt, eyes_k=1.0, aura=0.2, tilt=-20)
        img = J.frame(t, cam=0, back=back if t < t3 else None, front=front)
        if not dark:
            img = torch_glow(img, info["tp"], 0.8 + 0.2 * (math.sin(t * 29) > 0))
        a = to_arr(img)
        if dark:
            a *= 0.35
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        if dark:   # only the eyes stay bright in the dark
            if t < t3:
                pass
        rain(img, t, 0.6 if dark else 1.0)
        z = 1.0 + 0.04 * t / D + 2.4 * ss(t, t4 + 0.2, t4 + 1.1)
        fl = 0.85 if t4 + 1.1 <= t < t4 + 1.18 else 0.0
        a = finish(img, t, vig=VIG_H, push=z, cx=800, cy=GY - 680, flash=fl, flash_col=(255, 30, 20))
        if t > D - 0.45:
            a *= 0.0
        return a
    return f


# ----------------------------------------------------------------- part 2
def make_recap(D, caps):
    J = jungle()
    def f(t):
        info = {}
        def front(img, tt, P):
            spr = soldier(0, 0, True, scale=1.0)
            info["tp"], _ = put(img, spr, 620, GY + 160)
            put_ghost(img, 760, GY + 190, 1.05, tt, eyes_k=1.0, aura=0.2, tilt=-20)
        img = J.frame(t, cam=0, front=front)
        img = torch_glow(img, info["tp"], 0.5 * (math.sin(t * 17) > 0))
        rain(img, t)
        a = finish(img, t, vig=VIG_H, push=1.0 + 0.06 * t / D, cy=1000)
        out = Image.fromarray(np.clip(a * 0.8, 0, 255).astype(np.uint8)).convert("RGBA")
        header(out, t, "PART 2")
        return to_arr(out)
    return f


def make_run(D, caps):
    J = jungle()
    t2 = caps[1][1]
    cuts = [t2 + 0.3, t2 + 1.3, t2 + 2.3]
    def f(t):
        n = sum(1 for c in cuts if t > c)
        def back(img, tt, P):
            if n:
                put_ghost(img, 90 + 60 * n, GY + 80 + 30 * n, [0.4, 0.55, 0.72][n - 1], tt, eyes_k=1.0, aura=0.4)
        def front(img, tt, P):
            spr = soldier((tt * 1.8) % 1, run=1.0, torch=False, scale=0.95)
            put(img, spr, 620, GY + 150 + 8 * abs(math.sin(tt * 11)))
        img = J.frame(t, cam=520 * t, back=back, front=front)
        a = to_arr(img) * 0.75
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        rain(img, t)
        fl = 0.7 if any(c <= t < c + 0.08 for c in cuts) else 0.0
        return finish(img, t, vig=VIG_H, push=1.05, shake=0.6, flash=fl, flash_col=(255, 30, 20))
    return f


def make_lights(D, caps):
    J = jungle()
    t2, t3 = caps[1][1], caps[2][1]
    tag = pill("2 HOURS MISSING", font(INTER_SB, 52), outline=(255, 90, 90, 255), fill=(150, 18, 26, 235), h=96)
    def f(t):
        if t < t2 - 0.2:   # camp floodlights glowing through the trees
            img = J.frame(t, cam=200 * t, near=True)
            a = to_arr(img)
            for i in range(3):
                add_glow(a, FLOOD, 700 + i * 180 - 200 * t * 0.3, GY - 380, 0.6 * ss(t, 0.2, 1.4))
            img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
            rain(img, t)
            return finish(img, t, push=1.04)
        # the parade square under floodlights, the platoon staring
        y = np.linspace(0, 1, H)[:, None]
        sk = np.broadcast_to((np.array([10, 6, 8]) * (1 - y) + np.array([60, 30, 28]) * y)[:, None, :], (H, W, 3)).copy()
        img = Image.fromarray(np.clip(sk, 0, 255).astype(np.uint8)).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.rectangle([0, 980, W, H], fill=(70, 66, 64, 255))
        for i in range(0, W, 180):
            d.line([(i, 980), (i - 300, H)], fill=(84, 80, 78, 255), width=3)
        d.rectangle([120, 640, 960, 980], fill=(30, 26, 28, 255))            # barrack block
        for i in range(8):
            d.rectangle([150 + i * 100, 700, 200 + i * 100, 760], fill=(200, 180, 120, 255))
        for x in (60, 1000):
            d.rectangle([x, 380, x + 14, 980], fill=(20, 20, 20, 255))
        for i in range(6):
            spr = soldier(0, 0, False, scale=0.55)
            put(img, spr, 200 + i * 135, 1160)
        spr = soldier(0, 0, False, scale=0.9, tilt=70)
        put(img, spr, 560, 1520)                                       # Darren on the ground
        a = to_arr(img)
        for x in (67, 1007):
            add_glow(a, FLOOD, x, 390, 0.9)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        rain(img, t, 0.7)
        if t > t3 - 0.2:
            k = ss(t, t3 - 0.2, t3 + 0.3)
            img.alpha_composite(with_alpha(tag, k), (int(W / 2 - tag.width / 2), 360))
        return finish(img, t, push=1.0 + 0.05 * (t - t2) / D)
    return f


def bunk_room():
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    a = np.zeros((H, W, 3), np.float32)
    a[..., 0] = 40; a[..., 1] = 36; a[..., 2] = 40
    a *= (0.75 + 0.35 * fog_texture(W, H, 81))[..., None]
    a[np.broadcast_to(y > 1300, (H, W))] = np.array([46, 40, 40])
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    return img


DOORS = [(130, 640, 330, 1300), (440, 640, 640, 1300), (750, 640, 950, 1300)]


def draw_room(img, t, third_open=0.0, count=0, ghost_k=0.0, ghost_scale=0.62):
    d = ImageDraw.Draw(img)
    for i, (x0, y0, x1, y1) in enumerate(DOORS):
        if i == 2:
            d.rectangle([x0, y0, x1, y1], fill=(6, 8, 10, 255))          # dark opening behind
            if ghost_k > 0:
                put_ghost(img, (x0 + x1) / 2, y1 + 10, ghost_scale, t, eyes_k=ghost_k, aura=0.35 * ghost_k, tilt=-14)
            w = (x1 - x0) * (1 - 0.8 * third_open)
            d = ImageDraw.Draw(img)
            d.rectangle([x0, y0, x0 + w, y1], fill=(70, 74, 62, 255))
            d.rectangle([x0 + w - 30, (y0 + y1) / 2, x0 + w - 18, (y0 + y1) / 2 + 30], fill=(170, 150, 90, 255))
        else:
            d.rectangle([x0, y0, x1, y1], fill=(70, 74, 62, 255))
            d.rectangle([x1 - 30, (y0 + y1) / 2, x1 - 18, (y0 + y1) / 2 + 30], fill=(170, 150, 90, 255))
        d.rectangle([x0 - 8, y0 - 8, x1 + 8, y0], fill=(30, 30, 30, 255))
    # metal double-decker beds in the foreground, green lockers
    for bx in (-60, 760):
        d.rectangle([bx, 1180, bx + 380, 1205], fill=(90, 96, 100, 255)); d.rectangle([bx, 1450, bx + 380, 1480], fill=(90, 96, 100, 255))
        d.rectangle([bx, 1205, bx + 380, 1240], fill=(110, 120, 90, 255)); d.rectangle([bx, 1480, bx + 380, 1520], fill=(110, 120, 90, 255))
        for px in (bx, bx + 370):
            d.rectangle([px, 1100, px + 12, 1700], fill=(80, 86, 90, 255))
    f = font(LORA, 150, "Bold")
    for i in range(min(count, 3)):
        x0, y0, x1, y1 = DOORS[i]
        d.text(((x0 + x1) / 2, y0 - 110), str(i + 1), font=f, fill=(255, 220, 200, 255) if i < 2 else (255, 60, 50, 255), anchor="mm")


def make_bunk(D, caps):
    t2, t3 = caps[1][1], caps[2][1]
    base = bunk_room()
    clock = text_img("03:00", font(INTER_SB, 80), fill=(255, 70, 60, 255), glow=(255, 30, 20, 200), pad=16)
    def f(t):
        img = base.copy()
        cnt = 0
        for k, tt in enumerate((t2 + 1.4, t2 + 2.0, t2 + 2.6)):
            if t > tt:
                cnt = k + 1
        draw_room(img, t, third_open=0.0, count=cnt)
        a = to_arr(img)
        add_glow(a, glow_sprite(500, (120, 140, 200), 1.6), W / 2, 300, 0.35)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        img.alpha_composite(with_alpha(clock, ss(t, 0.2, 0.8)), (int(W / 2 - clock.width / 2), 180))
        z = 1.0 + 0.05 * t / D + 0.35 * ss(t, t3, D)
        return finish(img, t, vig=VIG_H, push=z, cx=850, cy=950)
    return f


def make_twist(D, caps):
    t2 = caps[1][1]
    base = bunk_room()
    def f(t):
        img = base.copy()
        draw_room(img, t, third_open=ss(t, 0.2, 1.6), count=3, ghost_k=ss(t, 0.8, 1.6))
        a = to_arr(img)
        add_glow(a, glow_sprite(500, (120, 140, 200), 1.6), W / 2, 300, 0.25)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        jt = D - 1.1
        if t > jt:
            put_ghost(img, W / 2 + 40, 2900, 2.6, t, eyes_k=1.0, aura=0.6, tilt=-16)
        fl = 0.85 if jt <= t < jt + 0.08 else 0.0
        z = 1.0 + 0.4 * ss(t, 1.0, jt) + (0.4 if t > jt else 0)
        return finish(img, t, vig=VIG_H, push=z, cx=850 if t < jt else W / 2, cy=900 if t < jt else 800, shake=0.8 if t > jt else 0, flash=fl, flash_col=(255, 30, 20))
    return f


def make_explain(D, caps):
    base = bunk_room()
    title = text_img("PULAU TEKONG", font(LORA, 104, "Bold"), fill=(250, 240, 225, 255), glow=(200, 30, 30, 220), pad=20)
    sub = text_img("Singapore's army ghost story", font(INTER_SB, 48), fill=(255, 214, 120, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("Singapore's army training island", pf, fill=(110, 20, 24, 235), h=80),
             pill("The lost Charlie Company recruit", pf, fill=(110, 20, 24, 235), h=80),
             pill("The bunk with a 3rd door", pf, fill=(110, 20, 24, 235), h=80)]
    ts = [caps[0][1] + 0.5, caps[1][1], caps[2][1]]
    def f(t):
        img = base.copy()
        draw_room(img, t, third_open=0.8, count=3, ghost_k=1.0)
        a = finish(img, t, vig=VIG_H) * 0.7
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        fl = flag_layer(t)
        out.alpha_composite(with_alpha(fl, ss(t, 0, 0.5)), (int(W / 2 - fl.width / 2), 40))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 230))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 380))
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.2, tt + 0.3)
            if k > 0:
                out.alpha_composite(with_alpha(c, k), (int(W / 2 - c.width / 2), int(480 + i * 100 + 14 * (1 - k))))
        return to_arr(out)
    return f


def make_outro(D, caps):
    J = jungle()
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("have answered?", font(LORA, 100, "Bold"), fill=(255, 210, 60, 255), glow=(200, 40, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Answer", (120, 25, 25, 235)), ("Keep walking", (60, 70, 50, 235)), ("Turn around", (140, 100, 20, 235)), ("RUN!", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    def f(t):
        img = J.frame(t, cam=0)
        rain(img, t, 0.6)
        a = finish(img, t, vig=VIG_H) * 0.5
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        fl = flag_layer(t)
        out.alpha_composite(fl, (int(W / 2 - fl.width / 2), 120))
        out.alpha_composite(with_alpha(q, ss(t, 0, 0.6)), (int(W / 2 - q.width / 2), 330))
        out.alpha_composite(with_alpha(q2, ss(t, 0.2, 0.8)), (int(W / 2 - q2.width / 2), 450))
        yy, k = 660, 0
        for row in (chips[:2], chips[2:]):
            tot = sum(c.width for c in row) + 24
            x = W / 2 - tot / 2
            for c in row:
                tt = 0.5 + 0.2 * k
                out.alpha_composite(with_alpha(c, ss(t, tt, tt + 0.4)), (int(x), int(yy + 12 * (1 - ss(t, tt, tt + 0.4)))))
                x += c.width + 24; k += 1
            yy += 120
        out.alpha_composite(with_alpha(cm, ss(t, caps[1][1], caps[1][1] + 0.4) * (0.85 + 0.15 * math.sin(t * 6))), (int(W / 2 - cm.width / 2), 1010))
        out.alpha_composite(with_alpha(fol, ss(t, caps[1][1] + 0.4, caps[1][1] + 0.9)), (int(W / 2 - fol.width / 2), 1110))
        return to_arr(out) * (1 - ease((t - (D - 0.6)) / 0.6))
    return f
