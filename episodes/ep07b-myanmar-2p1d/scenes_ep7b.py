"""Ep07 Myanmar / Ma Phae Wah - 2.1D survival version. Each make_<id>(D, caps) returns f(t) -> float RGB array (H, W, 3)."""
import os, sys, math
os.environ["STYLE"] = "flat21"
_EP = os.path.dirname(os.path.abspath(__file__)); _TK = os.path.join(_EP, "..", "..", "toolkit")
sys.path.insert(0, _TK)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from art_v import W, H, font, text_img, with_alpha, ease, glow_sprite, add_glow, fog_texture, vignette, INTER_SB, INTER_M, LORA
from depth import inflate_shade, dof, god_rays, bokeh_particles
import demo25_myanmar as D5
from scenes_v import series_header, header_layers, pill, centered

GY = 1180
RED = (255, 55, 40)
YEL = (255, 200, 40)
VIG = vignette(0.85)
VIG_H = vignette(1.05)
GR = [np.random.default_rng(i).normal(0, 5, (H, W, 1)).astype(np.float32) for i in range(6)]
FOGT = fog_texture(W + 700, H, 41)


def ss(t, a, b):
    return ease((t - a) / max(1e-3, b - a))


def shade(draw_fn, size, base, radius, **kw):
    return D5.shaded(draw_fn, size, base, radius, **kw)


def to_arr(img):
    return np.asarray(img.convert("RGB")).astype(np.float32)


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


def fog(img, t, k, y0, y1, speed=18, col=(150, 45, 42), off=0):
    o = int((t * speed + off) % 700)
    f = FOGT[:, o:o + W]
    yy = np.arange(H)[:, None]
    band = np.clip(np.minimum((yy - y0) / 150, (y1 - yy) / 150), 0, 1)
    a = f * band * k
    lay = np.dstack([np.full((H, W), col[0], np.float32), np.full((H, W), col[1], np.float32), np.full((H, W), col[2], np.float32), a * 255]).astype(np.uint8)
    img.alpha_composite(Image.fromarray(lay, "RGBA"))


# ============================================================ characters
_HCACHE = {}


def hero(phase=0.0, run=0.0, phone=1.0, back=False, scale=1.0):
    """Min: t-shirt + longyi. phase in [0,1) for the walk/run cycle. Returns (RGBA, feet_x, feet_y, phone_xy)."""
    q = (round(phase * 12) % 12, round(run, 1), round(phone), back, round(scale, 2))
    if q in _HCACHE:
        return _HCACHE[q]
    w, h = 420, 860
    cx = w / 2
    ph = 2 * math.pi * q[0] / 12
    sw = math.sin(ph) * (0.35 + 0.65 * run)
    lean = 14 * run

    def P(*pts):
        return [(x, y) for x, y in pts]
    def legs(d, s):
        for sg in (-1, 1):
            a = sg * sw * 0.55
            hx, hy = cx + lean * 0.3 + sg * 18, 600
            kx, ky = hx + math.sin(a) * 120, hy + math.cos(a) * 110
            fx, fy = kx + math.sin(a - 0.3 * run * (1 + sg * math.sin(ph))) * 110, ky + 105
            d.line([(hx * s, hy * s), (kx * s, ky * s), (fx * s, fy * s)], fill=255, width=int(30 * s), joint="curve")
            d.ellipse([(fx - 30) * s, (fy - 12) * s, (fx + 34) * s, (fy + 14) * s], fill=255)
    def longyi(d, s):
        sp = abs(sw) * 40
        d.polygon([(p[0] * s, p[1] * s) for p in P((cx - 62 + lean * 0.5, 400), (cx + 62 + lean * 0.5, 400), (cx + 75 + sp, 690), (cx - 75 - sp, 690))], fill=255)
    def torso(d, s):
        L = lean
        d.polygon([(p[0] * s, p[1] * s) for p in P((cx - 80 + L, 190), (cx + 80 + L, 190), (cx + 64 + L * 0.6, 420), (cx - 64 + L * 0.6, 420))], fill=255)
        d.ellipse([(cx - 82 + L) * s, 175 * s, (cx - 40 + L) * s, 235 * s], fill=255)
        d.ellipse([(cx + 40 + L) * s, 175 * s, (cx + 82 + L) * s, 235 * s], fill=255)
    def arms(d, s):
        L = lean
        for sg in (-1, 1):
            sx, sy = cx + sg * 70 + L, 205
            if phone and sg == 1 and not back and run < 0.5:
                ex, ey = sx + 18, 330; hx, hy = cx + 20 + L, 300
            else:
                a = -sg * sw * 0.9
                ex, ey = sx + math.sin(a) * 90 + sg * 8, sy + math.cos(a) * 100
                b = a - 0.9 * run * sg
                hx, hy = ex + math.sin(b) * 95, ey + math.cos(b) * 80 - 40 * run
            d.line([(sx * s, sy * s), (ex * s, ey * s), (hx * s, hy * s)], fill=255, width=int(26 * s), joint="curve")
            d.ellipse([(hx - 16) * s, (hy - 16) * s, (hx + 16) * s, (hy + 16) * s], fill=255)
        return None
    def head(d, s):
        L = lean * 1.2
        d.rectangle([(cx - 20 + L) * s, 140 * s, (cx + 20 + L) * s, 200 * s], fill=255)
        d.ellipse([(cx - 52 + L) * s, 40 * s, (cx + 52 + L) * s, 168 * s], fill=255)
    def hair(d, s):
        L = lean * 1.2
        d.pieslice([(cx - 56 + L) * s, 30 * s, (cx + 56 + L) * s, 150 * s], 180, 360, fill=255)
        d.polygon([(p[0] * s, p[1] * s) for p in P((cx - 56 + L, 90), (cx - 30 + L, 60), (cx + 10 + L, 70), (cx + 56 + L, 90), (cx + 50 + L, 60), (cx - 50 + L, 60))], fill=255)
        if back:
            d.ellipse([(cx - 54 + L) * s, 36 * s, (cx + 54 + L) * s, 160 * s], fill=255)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    skin = (178, 122, 96)
    img.alpha_composite(shade(legs, (w, h), skin, 12))
    lo = shade(longyi, (w, h), (120, 38, 46), 30)
    a = np.asarray(lo, np.float32)            # checks on the longyi
    yy, xx = np.mgrid[0:h, 0:w]
    chk = ((xx // 22 + yy // 22) % 2) * 0.12 + ((xx % 44 < 4) | (yy % 44 < 4)) * 0.18
    a[..., :3] *= (1 - chk)[..., None]
    img.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    img.alpha_composite(shade(torso, (w, h), (58, 66, 86), 40))
    img.alpha_composite(shade(arms, (w, h), skin, 12))
    img.alpha_composite(shade(head, (w, h), skin, 30))
    img.alpha_composite(shade(hair, (w, h), (22, 16, 16), 18))
    d = ImageDraw.Draw(img)
    L = lean * 1.2
    pxy = None
    if not back:
        for sg in (-1, 1):   # wide scared eyes
            d.ellipse([cx + sg * 20 - 9 + L, 96, cx + sg * 20 + 9 + L, 112], fill=(240, 236, 230, 255))
            d.ellipse([cx + sg * 20 - 4 + L, 100, cx + sg * 20 + 4 + L, 108], fill=(15, 10, 10, 255))
        d.ellipse([cx - 7 + L, 136, cx + 7 + L, 148], fill=(60, 25, 25, 255))
        if phone and run < 0.5:
            px, py = cx + 20 + lean, 296
            d.rounded_rectangle([px - 16, py - 30, px + 16, py + 30], 6, fill=(20, 20, 26, 255))
            d.rounded_rectangle([px - 13, py - 27, px + 13, py + 27], 5, fill=(200, 225, 255, 255))
            pxy = (px, py)
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        pxy = (pxy[0] * scale, pxy[1] * scale) if pxy else None
    out = (img, cx * scale, 815 * scale, pxy)
    _HCACHE[q] = out
    return out


_GC = {}


def ghost(carry=True):
    """Ma Phae Wah: pale yellow robe, long black hair, a yellow ribbon, a coffin on her shoulder (carry=True)."""
    if carry in _GC:
        return _GC[carry]
    w, h = 1000, 1250
    ox, oy = 190, 100           # offset of the 620x1150 body inside this canvas
    cx = ox + 310
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def S(f):
        return lambda d, s: f(d, s)
    def hair_back(d, s):
        P = lambda *pts: [((x) * s, (y) * s) for x, y in pts]
        d.ellipse([(cx - 105) * s, (oy + 80) * s, (cx + 105) * s, (oy + 330) * s], fill=255)
        d.polygon(P((cx - 105, oy + 200), (cx - 150, oy + 520), (cx - 180, oy + 820), (cx - 120, oy + 740), (cx - 95, oy + 880), (cx - 40, oy + 560), (cx + 40, oy + 560),
                    (cx + 100, oy + 900), (cx + 125, oy + 740), (cx + 175, oy + 840), (cx + 150, oy + 520), (cx + 105, oy + 200)), fill=255)
    def hair_front(d, s):
        P = lambda *pts: [((x) * s, (y) * s) for x, y in pts]
        d.pieslice([(cx - 98) * s, (oy + 88) * s, (cx + 98) * s, (oy + 300) * s], 180, 360, fill=255)
        for sg in (-1, 1):
            d.polygon(P((cx + sg * 98, oy + 190), (cx + sg * 40, oy + 200), (cx + sg * 52, oy + 330), (cx + sg * 70, oy + 660), (cx + sg * 58, oy + 790), (cx + sg * 95, oy + 720), (cx + sg * 118, oy + 520)), fill=255)
        for x, y1 in ((cx - 22, oy + 330), (cx + 6, oy + 380), (cx + 30, oy + 300)):
            d.polygon(P((x - 9, oy + 190), (x + 9, oy + 190), (x + 3, y1), (x - 2, y1)), fill=255)
    def face(d, s):
        d.ellipse([(cx - 62) * s, (oy + 170) * s, (cx + 62) * s, (oy + 345) * s], fill=255)
    def dress(d, s):
        hem = [(cx + 250 - i * 500 / 14, oy + 1120 - (40 if i % 2 else 0) - 30 * math.sin(i * 1.7)) for i in range(15)]
        pts = [(cx - 20, oy + 330), (cx + 20, oy + 330), (cx + 95, oy + 410), (cx + 150, oy + 700), (cx + 250, oy + 1120), *hem[1:-1], (cx - 250, oy + 1120), (cx - 150, oy + 700), (cx - 95, oy + 410)]
        d.polygon([(x * s, y * s) for x, y in pts], fill=255)
    def arms(d, s):
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        sides = (1,) if carry else (-1, 1)
        for sg in sides:
            d.polygon(P((cx + sg * 90, oy + 410), (cx + sg * 125, oy + 420), (cx + sg * 165, oy + 760), (cx + sg * 150, oy + 770)), fill=255)
            d.polygon(P((cx + sg * 150, oy + 760), (cx + sg * 170, oy + 760), (cx + sg * 178, oy + 880), (cx + sg * 168, oy + 900), (cx + sg * 155, oy + 870)), fill=255)
        if carry:   # left arm raised to hold the coffin on the left shoulder
            d.polygon(P((cx - 90, oy + 410), (cx - 120, oy + 400), (cx - 175, oy + 250), (cx - 150, oy + 232)), fill=255)
            d.ellipse([(cx - 190) * s, (oy + 220) * s, (cx - 150) * s, (oy + 262) * s], fill=255)
    def coffin(d, s):
        # long box resting on the left shoulder, tilted down to the back
        c, sn = math.cos(-0.22), math.sin(-0.22)
        x0, y0 = cx - 120, oy + 170
        pts = [(-330, -60), (230, -70), (250, 0), (230, 70), (-330, 60), (-360, 0)]
        d.polygon([((x0 + px * c - py * sn) * s, (y0 + px * sn + py * c) * s) for px, py in pts], fill=255)
    body.alpha_composite(shade(hair_back, (w, h), (16, 12, 12), 40, rim_strength=1.3))
    dr = shade(dress, (w, h), (205, 192, 150), 70, rim_strength=1.0)
    a = np.asarray(dr, np.float32)
    yy = np.arange(h)[:, None]; xx = np.arange(w)[None, :]
    fold = 0.5 + 0.5 * np.sin((xx - cx) / 23 + np.sin(yy / 90) * 1.5)
    a[..., :3] *= (1 - (0.2 + np.clip((yy - oy - 420) / 600, 0, 1) * 0.4) * fold)[..., None]
    a[..., 3] *= np.clip((oy + 1110 - yy) / 330, 0, 1) ** 0.8
    body.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    body.alpha_composite(shade(arms, (w, h), (190, 196, 192), 14, rim_strength=0.9))
    body.alpha_composite(shade(face, (w, h), (198, 204, 200), 40, rim_strength=0.6))
    fd = ImageDraw.Draw(body)
    fd.ellipse([cx - 44, oy + 232, cx - 12, oy + 264], fill=(25, 10, 12, 255))
    fd.ellipse([cx + 12, oy + 232, cx + 44, oy + 264], fill=(25, 10, 12, 255))
    fd.ellipse([cx - 8, oy + 300, cx + 8, oy + 318], fill=(30, 12, 14, 255))
    body.alpha_composite(shade(hair_front, (w, h), (18, 13, 13), 22, rim_strength=1.4))
    # yellow ribbon tied in the hair, two tails blowing
    rb = Image.new("RGBA", (w, h), (0, 0, 0, 0)); rd = ImageDraw.Draw(rb)
    bx, by = cx + 78, oy + 150
    rd.polygon([(bx, by), (bx + 46, by - 30), (bx + 50, by + 24)], fill=YEL + (255,))
    rd.polygon([(bx, by), (bx - 40, by - 34), (bx - 44, by + 20)], fill=YEL + (255,))
    rd.ellipse([bx - 12, by - 12, bx + 12, by + 12], fill=(230, 160, 20, 255))
    rd.line([(bx + 4, by + 8), (bx + 40, by + 120), (bx + 20, by + 220)], fill=YEL + (255,), width=14, joint="curve")
    rd.line([(bx - 4, by + 8), (bx + 6, by + 140), (bx - 14, by + 250)], fill=(235, 175, 25, 255), width=12, joint="curve")
    body.alpha_composite(rb)
    if carry:
        body.alpha_composite(shade(coffin, (w, h), (78, 46, 34), 40, rim_strength=1.1))
        # wood planks + a faded gold band
        cd = ImageDraw.Draw(body)
        c, sn = math.cos(-0.22), math.sin(-0.22)
        x0, y0 = cx - 120, oy + 170
        for px in (-200, -40, 120):
            p1 = (x0 + px * c - (-60) * sn, y0 + px * sn + (-60) * c); p2 = (x0 + px * c - 60 * sn, y0 + px * sn + 60 * c)
            cd.line([p1, p2], fill=(150, 110, 50, 255), width=8)
        # her hand in front of the coffin
        body.alpha_composite(shade(lambda d, s: d.ellipse([(cx - 186) * s, (oy + 205) * s, (cx - 146) * s, (oy + 250) * s], fill=255), (w, h), (190, 196, 192), 10))
    out = (body, cx, oy + 1120, (cx - 28, oy + 248), (cx + 28, oy + 248))
    _GC[carry] = out
    return out


_CF = None


def coffin_ground():
    global _CF
    if _CF is None:
        w, h = 700, 260
        def dr(d, s):
            d.polygon([(30 * s, 120 * s), (60 * s, 60 * s), (640 * s, 50 * s), (680 * s, 110 * s), (650 * s, 220 * s), (50 * s, 230 * s)], fill=255)
        _CF = shade(dr, (w, h), (78, 46, 34), 40, rim_strength=1.1)
        d = ImageDraw.Draw(_CF)
        for x in (200, 360, 520):
            d.line([(x, 56), (x - 8, 226)], fill=(150, 110, 50, 255), width=8)
    return _CF


def put_ghost(img, x, feet_y, scale=1.0, carry=True, t=0.0, eyes=1.0, aura=0.45, sway=1.0):
    body, cx, fy, e1, e2 = ghost(carry)
    g = body.rotate(1.5 * sway * math.sin(t * 0.9), resample=Image.BICUBIC, center=(cx, 300))
    if scale != 1.0:
        g = g.resize((max(1, int(g.width * scale)), max(1, int(g.height * scale))), Image.LANCZOS)
    gx, gy = int(x - cx * scale), int(feet_y - fy * scale + 10 * math.sin(t * 1.3) * scale)
    if aura > 0:
        gl = g.split()[3].filter(ImageFilter.GaussianBlur(max(2, 40 * scale)))
        lay = Image.new("RGBA", g.size, (255, 60, 50, 0)); lay.putalpha(gl.point(lambda v: int(v * aura)))
        img.alpha_composite(lay, (gx, gy))
    img.alpha_composite(g, (gx, gy))
    if eyes > 0:
        k = eyes * (0.6 + 0.4 * math.sin(t * 5) ** 2)
        for e in (e1, e2):
            eye(img, gx + e[0] * scale, gy + e[1] * scale, k, scale)
    return gx, gy, g.size


def eye(img, x, y, k, sc=1.0):
    r = max(4, 9 * sc); R = int(60 * max(sc, 0.4))
    spr = Image.new("RGBA", (2 * R, 2 * R), (0, 0, 0, 0))
    ImageDraw.Draw(spr).ellipse([R - r, R - r * 0.8, R + r, R + r * 0.8], fill=(255, 40, 30, int(255 * min(1, k))))
    g = spr.filter(ImageFilter.GaussianBlur(R / 6))
    img.alpha_composite(g, (int(x - R), int(y - R))); img.alpha_composite(g, (int(x - R), int(y - R)))
    img.alpha_composite(spr, (int(x - R), int(y - R)))


def dog(howl=1.0, eyes=0.0, flip=False):
    w, h = 260, 260
    m = Image.new("L", (w * 2, h * 2), 0); d = ImageDraw.Draw(m)
    S = lambda pts: [(x * 2, y * 2) for x, y in pts]
    d.polygon(S([(60, 250), (70, 160), (100, 120), (150, 110), (170, 150), (175, 250)]), fill=255)       # sitting body
    hx, hy = 150, 110
    a = -1.2 * howl - 0.2 * (1 - howl)                    # head up when howling
    tip = (hx + math.cos(a) * 85, hy + math.sin(a) * 85)
    d.polygon(S([(hx - 20, hy + 20), (hx + 22, hy + 10), (tip[0] + 6, tip[1] + 4), (tip[0] - 4, tip[1] - 6), (hx - 16, hy - 28)]), fill=255)
    d.polygon(S([(hx - 16, hy - 26), (hx - 30, hy - 70), (hx - 2, hy - 36)]), fill=255)                # ear
    d.line(S([(62, 245), (20, 250), (10, 225)]), fill=255, width=20)                                     # tail
    m = m.resize((w, h), Image.LANCZOS)
    im = Image.new("RGBA", (w, h), (6, 3, 4, 0)); im.putalpha(m)
    if eyes > 0:
        e = (hx + math.cos(a) * 30 + 4, hy + math.sin(a) * 30 - 6)
        eye(im, e[0], e[1], eyes, 0.25)
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im


# ============================================================ worlds
class Lane:
    """The lane beside the cemetery wall: red sky, stupa, banyan and graves behind a whitewashed wall, a street lamp."""
    def __init__(self):
        self.sky = D5.sky()
        self.far = dof(D5.treeline(1, 40, 0.7, (40, 10, 12), 420), 3)
        st = D5.stupa_layer(); self.stupa = dof(st.resize((st.width * 2 // 3, st.height * 2 // 3), Image.LANCZOS), 2.0)
        self.mid = dof(D5.treeline(2, 10, 1.1, (14, 5, 7), 520), 1.5)
        self.banyan = D5.banyan()
        self.graves = [D5.grave(s, 0.45, ln) for s, ln in ((1, -4), (2, 5), (3, -2), (4, 6))]
        LW = 3200
        def wall(d, s):
            d.rectangle([0, (GY - 300) * s, LW * s, (GY + 10) * s], fill=255)
        wl = Image.new("RGBA", (LW, H), (0, 0, 0, 0))
        base = np.zeros((H, LW, 4), np.float32)
        yy = np.arange(H)[:, None]
        on = ((yy >= GY - 300) & (yy <= GY + 10)).astype(np.float32) * np.ones((1, LW))
        stain = fog_texture(LW, H, 5)
        base[..., 0] = 118 * (0.75 + 0.3 * stain); base[..., 1] = 66 * (0.75 + 0.3 * stain); base[..., 2] = 64 * (0.75 + 0.3 * stain)
        base[..., :3] *= (1 - 0.45 * np.clip((yy - (GY - 120)) / 130, 0, 1))[..., None]
        base[..., :3] *= (0.55 + 0.45 * np.clip((yy - (GY - 300)) / 300, 0, 1))[..., None] * 0 + 1
        cap = ((yy >= GY - 318) & (yy < GY - 296)).astype(np.float32) * np.ones((1, LW))
        base[..., :3] = base[..., :3] * (1 - cap[..., None]) + np.array([150, 92, 86]) * cap[..., None]
        xx = np.arange(LW)[None, :]
        pil = ((xx % 420) < 34) * on
        base[..., :3] *= (1 - 0.25 * pil)[..., None]
        base[..., 3] = 255 * np.clip(on + cap, 0, 1)
        self.wall = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGBA")
        self.LW = LW
        road = np.zeros((H, W, 4), np.float32)
        g = np.clip((yy - GY) / 700, 0, 1)
        road[..., 0] = 34 - 24 * g; road[..., 1] = 14 - 10 * g; road[..., 2] = 16 - 10 * g
        tex = fog_texture(W, H, 13)
        road[..., :3] *= (0.6 + 0.8 * tex)[..., None]
        road[..., 3] = 255 * (yy >= GY)
        self.road = Image.fromarray(np.clip(road, 0, 255).astype(np.uint8), "RGBA")
        self.lamp = self._lamp()
        self.lglow = glow_sprite(360, (255, 140, 60), 1.8)
        self.fg = dof(D5.foreground(), 9)

    def _lamp(self):
        def dr(d, s):
            d.rectangle([60 * s, 60 * s, 76 * s, 1000 * s], fill=255)
            d.line([(68 * s, 70 * s), (150 * s, 40 * s), (190 * s, 60 * s)], fill=255, width=int(12 * s))
            d.polygon([(165 * s, 55 * s), (215 * s, 55 * s), (205 * s, 80 * s), (175 * s, 80 * s)], fill=255)
        return shade(dr, (240, 1010), (40, 34, 36), 8)

    def frame(self, t, cam, lamp_k=1.0, extra_back=None, extra_front=None, dogs=None, wall=True):
        img = self.sky.copy()
        P = lambda k: int(-cam * k)
        img.alpha_composite(self.far, (P(0.1) % 300 - 300, GY - 400))
        img.alpha_composite(self.stupa, (P(0.15) + 640, GY - 380 - 120))
        img.alpha_composite(self.mid, (P(0.25) % 300 - 300, GY - 470))
        img.alpha_composite(self.banyan, (P(0.4) + 120, GY - 1500 + 250))
        for i, g in enumerate(self.graves):
            img.alpha_composite(g, (P(0.45) + 80 + i * 260, GY - 300 - g.height + 120))
        if extra_back:
            extra_back(img, t, P)
        if wall:
            x = P(0.7) % 420 - 420
            img.alpha_composite(self.wall.crop((0, 0, W + 840, H)), (x, 0))
        if dogs:
            for (dx, dimg) in dogs:
                img.alpha_composite(dimg, (int(dx + P(0.7)), GY - 318 - dimg.height + 30))
        img.alpha_composite(self.road)
        lx = P(1.0) + 760
        img.alpha_composite(self.lamp, (lx, GY - 1000 + 40))
        if extra_front:
            extra_front(img, t, P)
        a = to_arr(img)
        fl = lamp_k * (0.85 + 0.15 * math.sin(t * 31) * math.sin(t * 7))
        if lamp_k > 0:
            add_glow(a, self.lglow, lx + 190, GY - 1000 + 110, 0.8 * fl)
            # pool of lamp light on the road
            add_glow(a, self.lglow, lx + 120, GY + 140, 0.35 * fl)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


_LANE = None


def lane():
    global _LANE
    if _LANE is None:
        _LANE = Lane()
    return _LANE


def phone_ui(pct, k=1.0):
    w, h = 300, 120
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=(0, 0, 0, int(170 * k)))
    d.rounded_rectangle([30, 32, 150, 88], 10, outline=(240, 240, 240, int(255 * k)), width=5)
    d.rectangle([150, 48, 160, 72], fill=(240, 240, 240, int(255 * k)))
    fillw = int(110 * pct / 100)
    if fillw > 0:
        d.rectangle([36, 38, 36 + max(4, fillw), 82], fill=(255, 50, 40, int(255 * k)))
    d.text((235, 60), f"{pct}%", font=font(INTER_SB, 46), fill=(255, 80, 70, int(255 * k)), anchor="mm")
    return im


def house_front():
    """Min's wooden house: zinc roof, plank walls, door with a step."""
    w, h = 1080, 1300
    def walls(d, s):
        d.rectangle([90 * s, 380 * s, 990 * s, 1180 * s], fill=255)
    def roof(d, s):
        d.polygon([(40 * s, 400 * s), (540 * s, 120 * s), (1040 * s, 400 * s), (1040 * s, 440 * s), (40 * s, 440 * s)], fill=255)
    def door(d, s):
        d.rectangle([420 * s, 640 * s, 660 * s, 1150 * s], fill=255)
    def step(d, s):
        d.rectangle([380 * s, 1150 * s, 700 * s, 1210 * s], fill=255)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wl = shade(walls, (w, h), (92, 58, 44), 20)
    a = np.asarray(wl, np.float32)
    yy = np.arange(h)[:, None]
    a[..., :3] *= (1 - 0.35 * ((yy % 46) < 4))[..., None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    rf = shade(roof, (w, h), (90, 88, 92), 30)
    a = np.asarray(rf, np.float32); xx = np.arange(w)[None, :]
    a[..., :3] *= (0.8 + 0.2 * np.sin(xx / 9))[..., None]
    im.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    im.alpha_composite(shade(door, (w, h), (60, 34, 26), 20))
    im.alpha_composite(shade(step, (w, h), (80, 76, 76), 14))
    d = ImageDraw.Draw(im)
    for x0 in (160, 760):       # shuttered windows, dark
        d.rectangle([x0, 600, x0 + 160, 820], fill=(18, 8, 8, 255))
        d.line([(x0 + 80, 600), (x0 + 80, 820)], fill=(70, 40, 30, 255), width=6)
    d.ellipse([620, 890, 640, 910], fill=(180, 150, 80, 255))  # door handle
    return im


def interior():
    """Dark wooden room seen from inside, door in the centre with a bright gap."""
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    a = np.zeros((H, W, 3), np.float32)
    a[..., 0] = 26; a[..., 1] = 12; a[..., 2] = 12
    planks = ((x % 120) < 5)
    a *= (1 - 0.4 * planks)[..., None]
    a *= (0.7 + 0.4 * fog_texture(W, H, 77))[..., None]
    floor = y > 1350
    a[np.broadcast_to(floor, (H, W))] *= 0.6
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


DOOR = (330, 520, 750, 1360)    # x0, y0, x1, y1 of the door in the interior shot


def door_layer(open_px=0.0, shake=0.0, t=0.0):
    x0, y0, x1, y1 = DOOR
    w, h = x1 - x0, y1 - y0
    def dr(d, s):
        d.rectangle([0, 0, w * s, h * s], fill=255)
    im = shade(dr, (w, h), (70, 40, 30), 30)
    d = ImageDraw.Draw(im)
    for yy in range(40, h, 140):
        d.line([(10, yy), (w - 10, yy)], fill=(40, 22, 18, 255), width=6)
    d.rectangle([w - 70, h // 2 - 10, w - 50, h // 2 + 30], fill=(170, 140, 70, 255))
    return im


# ============================================================ scenes
def make_hook(D, caps):
    L = lane()
    hdr = series_header("MYANMAR", "PART 1")
    dogs_h = [(80, dog(1.0)), (330, dog(1.0, flip=True)), (620, dog(1.0)), (900, dog(1.0, flip=True))]
    t2 = caps[1][1]

    def f(t):
        hw = 0.5 + 0.5 * math.sin(t * 2.2)
        dg = [(x, dog(0.6 + 0.4 * hw if i % 2 else 1 - 0.4 * hw, flip=(i % 2 == 1))) for i, (x, _) in enumerate(dogs_h)]
        img = L.frame(t, cam=-80 + 40 * t / D, dogs=dg)
        fog(img, t, 0.35, GY - 200, GY + 300, speed=16)
        bokeh_particles(img, 30, 2, t, color=(255, 110, 80), size=(2, 12), blur=(0, 6), area=(0, 400, W, 1500))
        img.alpha_composite(L.fg, (-200, H - 700 + 60))
        push = 1.0 + 0.05 * t / D + 0.08 * ss(t, t2, t2 + 1.2)
        a = finish(img, t, VIG_H, push=push, cy=GY - 200)
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        for im, (x, y), al in header_layers(hdr, t):
            if al > 0.01:
                out.alpha_composite(with_alpha(im, al), (int(x), int(y)))
        return to_arr(out)
    return f


def make_bus(D, caps):
    L = lane()
    t2 = caps[1][1]
    def bus(img, t, P):
        # the last bus pulling away to the right, tail lights glowing
        bx = 300 + 900 * ss(t, 0.2, t2 + 1.5)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([bx, GY - 330, bx + 700, GY + 40], 30, fill=(30, 22, 24, 255))
        for k in range(5):
            d.rectangle([bx + 40 + k * 130, GY - 290, bx + 140 + k * 130, GY - 180], fill=(120, 90, 60, 255))
        d.ellipse([bx + 80, GY - 10, bx + 180, GY + 90], fill=(10, 8, 8, 255)); d.ellipse([bx + 520, GY - 10, bx + 620, GY + 90], fill=(10, 8, 8, 255))
        d.rectangle([bx - 6, GY - 120, bx + 14, GY - 70], fill=(255, 40, 30, 255))
    def front(img, t, P):
        h, fx, fy, pxy = hero(0, 0, phone=1, scale=0.85)
        img.alpha_composite(h, (int(330 - fx), int(GY + 110 - fy)))
        if pxy:
            a = to_arr(img); add_glow(a, glow_sprite(140, (180, 210, 255), 1.6), 330 - fx + pxy[0], GY + 110 - fy + pxy[1], 0.7)
            img.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"))
    ui = phone_ui(3)
    def f(t):
        img = L.frame(t, cam=40 * t / D, extra_back=None, extra_front=lambda im, tt, P: (bus(im, tt, P), front(im, tt, P)))
        fog(img, t, 0.25, GY - 100, GY + 400, speed=14)
        img.alpha_composite(L.fg, (-260, H - 700 + 80))
        if t > t2:
            k = ss(t, t2, t2 + 0.3) * (0.6 + 0.4 * (math.sin(t * 6) > 0))
            img.alpha_composite(with_alpha(ui, k), (W - ui.width - 60, 140))
        return finish(img, t, push=1.02 + 0.04 * t / D)
    return f


def make_rule(D, caps):
    # flashback: grandma by an oil lamp, warm and faded
    bg = interior()
    def gma_body(d, s):
        P = lambda *p: [(x * s, y * s) for x, y in p]
        d.polygon(P((480, 900), (640, 900), (740, 1270), (380, 1270)), fill=255)
    def gma_face(d, s):
        d.ellipse([505 * s, 770 * s, 615 * s, 900 * s], fill=255)
    def gma_hair(d, s):
        d.pieslice([500 * s, 760 * s, 620 * s, 860 * s], 180, 360, fill=255)
        d.ellipse([532 * s, 722 * s, 588 * s, 776 * s], fill=255)
    def gma_hands(d, s):
        d.ellipse([560 * s, 1040 * s, 640 * s, 1090 * s], fill=255)
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g.alpha_composite(shade(gma_body, (W, H), (110, 70, 60), 40, rim=(255, 170, 90)))
    g.alpha_composite(shade(gma_face, (W, H), (190, 140, 110), 30, rim=(255, 190, 120)))
    g.alpha_composite(shade(gma_hair, (W, H), (200, 200, 200), 20, rim=(255, 190, 120)))
    g.alpha_composite(shade(gma_hands, (W, H), (190, 140, 110), 14, rim=(255, 190, 120)))
    gd = ImageDraw.Draw(g)
    gd.arc([525, 820, 553, 840], 200, 340, fill=(60, 30, 25, 255), width=4); gd.arc([567, 820, 595, 840], 200, 340, fill=(60, 30, 25, 255), width=4)
    gd.arc([540, 855, 580, 875], 20, 160, fill=(90, 40, 35, 255), width=4)
    lampg = glow_sprite(420, (255, 170, 80), 1.6)
    rib = text_img("yellow ribbon", font(LORA, 70, "Bold"), fill=(255, 210, 60, 255), glow=(255, 150, 20, 200), pad=20)
    t2 = caps[1][1]
    def f(t):
        img = bg.copy()
        img.alpha_composite(g, (0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle([700, 1180, 760, 1260], fill=(60, 40, 30, 255)); d.ellipse([712, 1150, 748, 1185], fill=(255, 200, 120, 255))
        a = to_arr(img)
        fl = 0.8 + 0.2 * math.sin(t * 13) * math.sin(t * 5)
        add_glow(a, lampg, 730, 1160, 1.0 * fl)
        # sepia memory look + film flicker
        lum = a.mean(2, keepdims=True)
        a = a * 0.4 + lum * np.array([1.2, 0.85, 0.6]) * 0.6
        a *= 0.92 + 0.08 * math.sin(t * 40)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        if t > t2 - 0.2:
            img.alpha_composite(with_alpha(rib, ss(t, t2 - 0.2, t2 + 0.4)), (int(W / 2 - rib.width / 2), 430))
        return finish(img, t, vig=VIG_H, push=1.0 + 0.06 * t / D, cy=1000)
    return f


def make_dogs(D, caps):
    L = lane()
    t2 = caps[1][1]                      # "Then, all at once... they stopped."
    xs = [(60, False), (300, True), (560, False), (820, True)]
    def f(t):
        stop = t > t2 + 0.9
        dg = []
        for i, (x, fl) in enumerate(xs):
            if stop:   # silent dogs, heads turned down to the cemetery, eyes glowing
                dg.append((x, dog(0.0, eyes=ss(t, t2 + 0.9, t2 + 1.6), flip=fl)))
            else:
                dg.append((x, dog(0.75 + 0.25 * math.sin(t * 2.5 + i), flip=fl)))
        def walker(img, tt, P):
            h, fx, fy, pxy = hero(tt * 0.9 % 1, 0, phone=1, scale=0.85)
            img.alpha_composite(h, (int(540 - fx), int(GY + 110 - fy)))
        img = L.frame(t, cam=60 * t, dogs=dg, extra_front=walker, lamp_k=0.0 if (stop and int(t * 12) % 5 == 0) else 1.0)
        fog(img, t, 0.3, GY - 200, GY + 350)
        img.alpha_composite(L.fg, (-200 - int(60 * t * 1.6) % 400, H - 700 + 80))
        return finish(img, t, vig=VIG_H if stop else VIG, push=1.03 + 0.1 * ss(t, t2 + 0.9, D))
    return f


def make_ribbon(D, caps):
    L = lane()
    t2, t3 = caps[1][1], caps[2][1]
    def back(img, t, P):
        # she stands among the graves behind the wall, coffin on her shoulder
        k = ss(t, t2 - 0.3, t2 + 0.8)
        if k > 0:
            put_ghost(img, P(0.45) + 380, GY - 120, scale=0.55, t=t, eyes=ss(t, t3, t3 + 0.6), aura=0.5 * k)
    rib = Image.new("RGBA", (420, 200), (0, 0, 0, 0))
    def f(t):
        if t < t2 - 0.3:   # close-up: the ribbon lying on the wet road, fluttering
            img = L.frame(t, cam=0, wall=True)
            a = to_arr(img)
            d = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(d)
            wv = [(220 + i * 40, 1500 + 18 * math.sin(t * 4 + i * 0.7)) for i in range(16)]
            dd.line(wv, fill=YEL + (255,), width=30, joint="curve")
            dd.line([(p[0] + 10, p[1] + 34) for p in wv[4:]], fill=(230, 170, 20, 255), width=22, joint="curve")
            img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); img.alpha_composite(d)
            fog(img, t, 0.3, 1300, 1900, speed=10)
            return finish(img, t, push=1.6 - 0.15 * t / max(0.1, t2), cy=1450)
        img = L.frame(t, cam=-40, extra_back=back, wall=False)
        fog(img, t, 0.4, GY - 260, GY + 200, speed=20)
        img.alpha_composite(L.fg, (-200, H - 700 + 80))
        push = 1.0 + 0.25 * ss(t, t3, D)
        return finish(img, t, vig=VIG_H, push=push, cx=420, cy=GY - 420)
    return f


def make_run(D, caps):
    L = lane()
    t2 = caps[1][1]
    cuts = [t2 + 0.2, t2 + 1.2, t2 + 2.2]
    def f(t):
        dead = t > caps[0][1] + 1.0                   # "His phone died."
        n = sum(1 for c in cuts if t > c)
        def back(img, tt, P):
            if n:
                sc = [0.3, 0.42, 0.58][n - 1]
                put_ghost(img, 80 + 70 * n, GY + 60 + 25 * n, scale=sc, t=tt, eyes=1.0, aura=0.6)
        def runner(img, tt, P):
            h, fx, fy, _ = hero((tt * 1.8) % 1, run=1.0, phone=0, scale=0.9)
            img.alpha_composite(h, (int(600 - fx), int(GY + 120 - fy + 8 * abs(math.sin(tt * 11)))))
        img = L.frame(t, cam=500 * t, extra_front=lambda im, tt, P: (back(im, tt, P), runner(im, tt, P)), lamp_k=0.25 if dead else 1.0)
        fog(img, t, 0.3, GY - 200, GY + 380, speed=60)
        img.alpha_composite(L.fg, (-int(500 * t * 1.6) % 400 - 200, H - 700 + 80))
        fl = 0.0
        for c in cuts:
            if c <= t < c + 0.08:
                fl = 0.7
        if dead and t < caps[0][1] + 1.15:
            fl = 0.5
        return finish(img, t, vig=VIG_H, push=1.05, shake=0.6, flash=fl, flash_col=(255, 30, 20))
    return f


def make_cliff(D, caps):
    bg = interior()
    hf = house_front()
    L = lane()
    t2, t3, t4 = caps[1][1], caps[2][1], caps[3][1]
    def outside(t):
        """What Min sees through the gap: the doorstep in red moonlight, the ghost arriving."""
        img = L.sky.copy()
        img.alpha_composite(L.mid, (-150, GY - 470))
        img.alpha_composite(L.road)
        k = ss(t, t2 - 0.6, t2 + 0.6)
        if t < t3:
            put_ghost(img, 540, GY + 420, scale=0.9 * (0.7 + 0.3 * k), t=t, carry=True, eyes=1.0)
        else:
            cf = coffin_ground()
            put_ghost(img, 540, GY + 420, scale=0.9, t=t, carry=False, eyes=1.0)
            img.alpha_composite(cf, (120, GY + 300 + int(40 * (1 - ss(t, t3, t3 + 0.8)))))
        return img
    def f(t):
        img = bg.copy()
        x0, y0, x1, y1 = DOOR
        gap = 46 + 20 * ss(t, 0, 0.6) + 70 * ss(t, t4 - 0.4, t4 + 0.6)
        out = outside(t).crop((W / 2 - gap / 2, y0, W / 2 + gap / 2, y1)) if False else None
        # bright slit between two door halves
        o = outside(t)
        slit = o.crop((int(W / 2 - 300), y0, int(W / 2 + 300), y1))
        m = Image.new("L", slit.size, 0)
        ImageDraw.Draw(m).rectangle([300 - gap / 2, 0, 300 + gap / 2, y1 - y0], fill=255)
        img.paste(slit, (int(W / 2 - 300), y0), m)
        d = ImageDraw.Draw(img)
        d.rectangle([x0, y0, int(W / 2 - gap / 2), y1], fill=(54, 30, 24, 255))
        d.rectangle([int(W / 2 + gap / 2), y0, x1, y1], fill=(54, 30, 24, 255))
        a = to_arr(img)
        add_glow(a, glow_sprite(260, (255, 70, 50), 1.5), W / 2, (y0 + y1) / 2, 0.35)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        h, fx, fy, _ = hero(0, 0, phone=0, back=True, scale=1.25)
        hd = np.asarray(h, np.float32).copy(); hd[..., :3] *= 0.35
        img.alpha_composite(Image.fromarray(hd.astype(np.uint8), "RGBA"), (int(W / 2 - 330 - fx), int(1900 - fy + 60)))
        # final: zoom into the slit, her eye looks straight in
        z = 1.0 + 0.04 * t / D + 2.2 * ss(t, t4 - 0.2, t4 + 1.0)
        fl = 0.8 if t4 + 1.0 <= t < t4 + 1.08 else 0.0
        a = finish(img, t, vig=VIG_H, push=z, cx=W / 2, cy=850, flash=fl, flash_col=(255, 30, 20))
        if t > D - 0.45:
            a *= 0.0
        return a
    return f


# ----------------------------------------------------------------- part 2
def make_recap(D, caps):
    L = lane()
    hf = house_front()
    hdr = series_header("MYANMAR", "PART 2")
    def f(t):
        img = L.sky.copy()
        img.alpha_composite(L.far, (-150, GY - 400)); img.alpha_composite(L.mid, (-150, GY - 470))
        img.alpha_composite(hf, (0, GY + 210 - hf.height))
        img.alpha_composite(L.road.crop((0, 0, W, H)), (0, 60))
        img.alpha_composite(coffin_ground().resize((420, 156)), (330, GY + 140))
        put_ghost(img, 760, GY + 330, scale=0.62, t=t, carry=False, eyes=1.0)
        fog(img, t, 0.35, GY - 100, GY + 500)
        a = finish(img, t, vig=VIG_H, push=1.0 + 0.08 * t / D, cy=1150)
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        for im, (x, y), al in header_layers(hdr, t):
            if al > 0.01:
                out.alpha_composite(with_alpha(im, al), (int(x), int(y)))
        return to_arr(out)
    return f


def _knocks(caps):
    t0 = caps[0][1]
    return [t0 + 0.05, t0 + 0.55, t0 + 1.05]


def make_knock(D, caps):
    bg = interior()
    dl = door_layer()
    ks = _knocks(caps)
    def f(t):
        img = bg.copy()
        sh = sum(math.exp(-(t - k) * 14) for k in ks if t >= k)
        img.alpha_composite(dl, (DOOR[0] + int(6 * sh * math.sin(t * 90)), DOOR[1]))
        # red light leaking under the door
        a = to_arr(img)
        add_glow(a, glow_sprite(300, (255, 50, 40), 1.4), W / 2, DOOR[3] + 10, 0.5 + 0.3 * sh)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        h, fx, fy, _ = hero(0, 0, phone=0, scale=1.1)
        back_off = 160 * ss(t, ks[0], ks[2] + 0.4)
        img.alpha_composite(h, (int(W / 2 + 160 + back_off * 0.3 - fx), int(1900 + 40 - fy)))
        return finish(img, t, vig=VIG_H, push=1.0 + 0.05 * t / D, shake=min(1.0, sh) * 0.5)
    return f


def make_hide(D, caps):
    bg = interior()
    dl = door_layer()
    t2, t3 = caps[1][1], caps[2][1]
    cg = glow_sprite(380, (255, 180, 90), 1.6)
    def f(t):
        img = bg.copy()
        img.alpha_composite(dl, (DOOR[0], DOOR[1]))
        # shadow of her robe crossing the light under the door
        a = to_arr(img)
        add_glow(a, glow_sprite(300, (255, 50, 40), 1.4), W / 2, DOOR[3] + 10, 0.6)
        if t > t3:
            sx = W / 2 + 260 * math.sin((t - t3) * 1.4)
            yy = DOOR[3]
            a[yy - 30:yy + 30, max(0, int(sx - 90)):int(sx + 90)] *= 0.15
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        # Min crouched at the right with a candle, holding his breath
        h, fx, fy, _ = hero(0, 0, phone=0, scale=0.95)
        hc = h.resize((h.width, int(h.height * 0.78)))
        img.alpha_composite(hc, (int(860 - fx), int(1760 - fy * 0.78)))
        d = ImageDraw.Draw(img)
        lit = t > t2 - 0.2
        d.rectangle([700, 1660, 730, 1740], fill=(220, 210, 190, 255))
        a = to_arr(img)
        if lit:
            fl = 0.85 + 0.15 * math.sin(t * 17) * math.sin(t * 5)
            if t > t3:
                fl *= 0.7 + 0.3 * math.sin((t - t3) * 9)
            add_glow(a, cg, 715, 1650, 1.0 * fl)
            add_glow(a, glow_sprite(30, (255, 230, 170), 1.2), 715, 1650, 1.4 * fl)
        return finish(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"), t, vig=VIG_H, push=1.0 + 0.08 * t / D, cy=1300)
    return f


def make_dawn(D, caps):
    L = lane()
    hf = house_front()
    t2 = caps[1][1]
    st = D5.stupa_layer()
    def f(t):
        k = ss(t, 0.4, caps[0][2])
        y = np.linspace(0, 1, H)[:, None]
        top = np.array([40, 30, 70]); bot = np.array([255, 150, 130])
        sky = top * (1 - y) + bot * y
        sk = np.broadcast_to(sky[:, None, :], (H, W, 3)) * (0.35 + 0.65 * k)
        img = Image.fromarray(np.clip(sk, 0, 255).astype(np.uint8)).convert("RGBA")
        s2 = st.resize((st.width // 2, st.height // 2))
        img.alpha_composite(s2, (720, GY - 360 - 20))
        img.alpha_composite(L.mid, (-150, GY - 470))
        img.alpha_composite(L.road)
        # the empty doorstep (seen from the open door)
        d = ImageDraw.Draw(img)
        d.rectangle([380, GY + 260, 700, GY + 320], fill=(90, 80, 80, 255))
        fog(img, t, 0.3, GY - 100, GY + 500, col=(255, 190, 170))
        # birds
        for i in range(5):
            bx = (200 + i * 140 + t * 60) % W; by = 500 + 40 * math.sin(i + t)
            d.line([(bx - 18, by), (bx, by + 8), (bx + 18, by)], fill=(30, 20, 30, 255), width=4)
        # door frame sliding open
        op = ss(t, 0.0, 1.4)
        d.rectangle([0, 0, int(260 - 200 * op), H], fill=(40, 22, 18, 255))
        d.rectangle([int(820 + 200 * op), 0, W, H], fill=(40, 22, 18, 255))
        return finish(img, t, vig=VIG, push=1.06 - 0.04 * t / D)
    return f


def make_twist(D, caps):
    t2 = caps[1][1]
    dl = door_layer()
    def f(t):
        if t < t2 - 0.2:     # ribbon tied on the door handle, blowing
            img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            big = dl.resize((dl.width * 3, dl.height * 3))
            img.alpha_composite(big, (-big.width + 520, -900))
            d = ImageDraw.Draw(img)
            hx, hy = 400, 640
            d.ellipse([hx - 30, hy - 30, hx + 30, hy + 30], fill=(170, 140, 70, 255))
            for k in range(2):
                pts = [(hx + 10 + i * 36, hy + 20 + i * 70 + 26 * math.sin(t * 5 + i * 0.8 + k)) for i in range(10)]
                d.line(pts, fill=YEL + (255,) if k == 0 else (230, 170, 20, 255), width=30 - 8 * k, joint="curve")
            a = to_arr(img)
            add_glow(a, glow_sprite(400, (255, 220, 160), 1.6), 700, 400, 0.5)
            return finish(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"), t, push=1.0 + 0.06 * t / D)
        # Min's back: five pale finger marks... then she is right behind him
        img = interior()
        h, fx, fy, _ = hero(0, 0, phone=0, back=True, scale=2.2)
        img.alpha_composite(h, (int(W / 2 - fx), int(2400 - fy)))
        d = ImageDraw.Draw(img)
        bx, by = W / 2 + 40, 1260
        for i in range(4):
            d.rounded_rectangle([bx - 90 + i * 45, by - 120 + abs(i - 1.5) * 12, bx - 66 + i * 45, by + 10], 12, fill=(150, 170, 165, 200))
        d.rounded_rectangle([bx - 150, by - 10, bx - 120, by + 70], 12, fill=(150, 170, 165, 200))
        jt = D - 1.1
        if t > jt:
            put_ghost(img, W / 2 + 40, 2700, scale=2.4, t=t, carry=False, eyes=1.0, aura=0.7)
        fl = 0.85 if jt <= t < jt + 0.08 else 0.0
        a = finish(img, t, vig=VIG_H, push=1.0 + 0.05 * (t - t2) + (0.6 if t > jt else 0), cy=700, shake=0.8 if t > jt else 0, flash=fl, flash_col=(255, 30, 20))
        return a
    return f


def make_explain(D, caps):
    L = lane()
    title = text_img("MA PHAE WAH", font(LORA, 110, "Bold"), fill=(255, 220, 90, 255), glow=(200, 60, 20, 220), pad=20)
    sub = text_img("the yellow-ribbon lady", font(INTER_SB, 50), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("Guardian of cemeteries", pf, fill=(110, 20, 24, 235), h=80),
             pill("Carries a coffin at midnight", pf, fill=(110, 20, 24, 235), h=80),
             pill("Where it lands, someone falls sick", pf, fill=(110, 20, 24, 235), h=80)]
    ts = [caps[1][1], caps[2][1], caps[3][1]]
    def f(t):
        img = L.frame(t, cam=-30 + 20 * t / D, wall=False)
        put_ghost(img, 540, GY + 500, scale=0.85, t=t, carry=True, eyes=1.0, aura=0.5)
        fog(img, t, 0.35, GY - 100, GY + 600)
        a = finish(img, t, vig=VIG_H, push=1.0)
        out = Image.fromarray(np.clip(a * 0.85, 0, 255).astype(np.uint8)).convert("RGBA")
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 150))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 300))
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.2, tt + 0.3)
            if k > 0:
                out.alpha_composite(with_alpha(c, k), (int(W / 2 - c.width / 2), int(410 + i * 100 + 14 * (1 - k))))
        return to_arr(out)
    return f


def make_outro(D, caps):
    L = lane()
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("have survived?", font(LORA, 100, "Bold"), fill=(255, 210, 60, 255), glow=(200, 40, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Open the door", (120, 25, 25, 235)), ("Hold your breath", (60, 40, 40, 235)), ("Light a candle", (140, 100, 20, 235)), ("RUN!", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    def f(t):
        img = L.frame(t, cam=0, wall=True)
        fog(img, t, 0.4, GY - 300, GY + 600)
        a = finish(img, t, vig=VIG_H) * 0.55
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
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
