"""SPECIAL EPISODE - South Korea / Cheonyeo Gwishin. MIXED STYLE (Nova's choice, 2026-11-25):
  C) dark painted exteriors: a Seoul high school under a blood moon, apartment towers, ginkgo trees, the school gate
  A) cinematic red silhouettes: the 4th-floor corridor, red moonlight through the windows, a backlit ghost with red rim
  B) CCTV footage: grainy monochrome security cameras with timestamps; the ghost is closer every time it cuts back
Ghost: the cheonyeo gwishin - a young woman in a white mourning hanbok (sobok), very long black hair down over the
face, too-long arms, floats; no gore. Hero: Ji-ho, a high-school boy in uniform with a backpack.
Each make_<id>(D, caps) returns f(t) -> float RGB array (H, W, 3)."""
import os, sys, math, random
os.environ["STYLE"] = "flat21"
_EP = os.path.dirname(os.path.abspath(__file__)); _TK = os.path.join(_EP, "..", "..", "toolkit")
sys.path.insert(0, _TK)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from art_v import W, H, FPS, font, text_img, with_alpha, ease, glow_sprite, add_glow, fog_texture, vignette, INTER_SB, INTER_M, LORA
from depth import bokeh_particles, inflate_shade
from scenes_v import series_header, header_layers, pill

KR = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
RED = np.array([255, 30, 22], np.float32)
VIG = vignette(0.85)
VIG_H = vignette(1.05)
GR = [np.random.default_rng(i).normal(0, 5, (H, W, 1)).astype(np.float32) for i in range(6)]
FOGT = fog_texture(W + 800, H, 121)


def krfont(size):
    for idx in (1, 0, 2, 3):          # the .ttc holds JP/KR/SC/TC faces; any of them has Hangul
        try:
            f = ImageFont.truetype(KR, size, index=idx)
            if f.getlength("한") > 0:
                return f
        except Exception:
            pass
    return font(INTER_SB, size)


def ss(t, a, b):
    return ease((t - a) / max(1e-3, b - a))


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


def fog(img, t, k, y0, y1, speed=18, col=(150, 30, 26), off=0):
    o = int((t * speed + off) % 800)
    f = FOGT[:, o:o + W]
    yy = np.arange(H)[:, None]
    band = np.clip(np.minimum((yy - y0) / 150, (y1 - yy) / 150), 0, 1)
    a = f * band * k
    lay = np.dstack([np.full((H, W), col[0], np.float32), np.full((H, W), col[1], np.float32),
                     np.full((H, W), col[2], np.float32), a * 255]).astype(np.uint8)
    img.alpha_composite(Image.fromarray(lay, "RGBA"))


_GLOW = {}


def gsp(r, col=(255, 60, 40), p=1.6):
    k = (int(r), col, p)
    if k not in _GLOW:
        _GLOW[k] = glow_sprite(int(r), col, p)
    return _GLOW[k]


def noise(h, w, scale, seed, blur=0):
    r = np.random.default_rng(seed)
    small = (r.random((h // scale + 2, w // scale + 2)) * 255).astype(np.uint8)
    im = Image.fromarray(small).resize((w + 2 * scale, h + 2 * scale), Image.BICUBIC).crop((0, 0, w, h))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, np.float32) / 255
    return (a - a.min()) / (a.max() - a.min() + 1e-6)


def mask_of(size, fn, blur=0):
    m = Image.new("L", size, 0)
    fn(ImageDraw.Draw(m))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return m


def solid(size, col, m):
    im = Image.new("RGBA", size, tuple(col) + (255,))
    im.putalpha(m)
    return im


# ============================================================ flag (Taegukgi) + UI
_FLAG = None


def _rect_poly(cx, cy, along, across, ang):
    """A rectangle centred at (cx, cy): 'along' is its size along direction ang, 'across' perpendicular."""
    ux, uy = math.cos(ang), math.sin(ang); vx, vy = -uy, ux
    pts = []
    for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        pts.append((cx + ux * along / 2 * a + vx * across / 2 * b, cy + uy * along / 2 * a + vy * across / 2 * b))
    return pts


def flag_base():
    """South Korea: white field, red-over-blue taegeuk tilted along the diagonal, four black trigrams
    (geon top-left, gam top-right, ri bottom-left, gon bottom-right). Drawn at 4x then reduced."""
    global _FLAG
    if _FLAG is None:
        s = 4; w, h = 300 * s, 200 * s
        im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        # taegeuk, built horizontally then rotated so the red head sits upper-left
        R = h / 4
        tg = Image.new("RGBA", (int(2 * R + 4), int(2 * R + 4)), (0, 0, 0, 0)); d = ImageDraw.Draw(tg)
        c = R + 2
        red, blue = (205, 46, 58, 255), (0, 71, 160, 255)
        d.ellipse([c - R, c - R, c + R, c + R], fill=blue)
        d.pieslice([c - R, c - R, c + R, c + R], 180, 360, fill=red)
        d.ellipse([c - R, c - R / 2, c, c + R / 2], fill=red)
        d.ellipse([c, c - R / 2, c + R, c + R / 2], fill=blue)
        ang = math.degrees(math.atan2(2, 3))
        tg = tg.rotate(-ang, Image.BICUBIC)
        im.alpha_composite(tg, (int(w / 2 - tg.width / 2), int(h / 2 - tg.height / 2)))
        d = ImageDraw.Draw(im)
        bar_l, bar_w, gap = h / 4, h / 24, h / 48
        dist = R + h / 8 + (3 * bar_w + 2 * gap) / 2
        diag = math.atan2(h, w)
        # (direction angle, pattern innermost->outermost; 1 = solid, 0 = broken)
        specs = [(math.pi + diag, (1, 1, 1)),        # geon, top-left
                 (-diag, (0, 1, 0)),                 # gam, top-right
                 (math.pi - diag, (1, 0, 1)),        # ri, bottom-left
                 (diag, (0, 0, 0))]                  # gon, bottom-right
        for a, pat in specs:
            ux, uy = math.cos(a), math.sin(a)
            for k, solid_ in enumerate(pat):
                off = dist - (bar_w + gap) + k * (bar_w + gap)
                cx, cy = w / 2 + ux * off, h / 2 + uy * off
                if solid_:
                    d.polygon(_rect_poly(cx, cy, bar_l, bar_w, a + math.pi / 2), fill=(0, 0, 0, 255))
                else:
                    seg = (bar_l - gap) / 2
                    for sgn in (-1, 1):
                        px, py = cx + (-uy) * sgn * (seg / 2 + gap / 2), cy + ux * sgn * (seg / 2 + gap / 2)
                        d.polygon(_rect_poly(px, py, seg, bar_w, a + math.pi / 2), fill=(0, 0, 0, 255))
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
        lum = 1.0 + 0.14 * math.cos(ph)
        col = a[:, x].copy(); col[:, :3] *= lum
        out[12 + dy:12 + dy + h, x] = col
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
    im2 = Image.new("RGBA", (w + 14, h + 24), (0, 0, 0, 0)); im2.alpha_composite(im, (14, 0))
    ImageDraw.Draw(im2).rectangle([0, 0, 7, h + 23], fill=(200, 190, 170, 255))
    sc = width / im2.width
    return im2.resize((width, int(im2.height * sc)), Image.LANCZOS)


_SPECIAL = None


def special_badge():
    global _SPECIAL
    if _SPECIAL is None:
        _SPECIAL = pill("SPECIAL EPISODE", font(INTER_SB, 40), outline=(255, 214, 120, 255), fill=(40, 26, 10, 235),
                        color=(255, 214, 120, 255), h=74)
    return _SPECIAL


def put_header(out, hdr, t, flag=True):
    for im, (x, y), al in header_layers(hdr, t):
        if al > 0.01:
            out.alpha_composite(with_alpha(im, al), (int(x), int(y)))
    sb = special_badge()
    out.alpha_composite(with_alpha(sb, ease((t + 1.0) / 0.5)), (int(W / 2 - sb.width / 2), 530))
    if flag:
        fw = flag_wave(t)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 40))


_CLK = {}


def clock_ui(time_str, warn=False, k=1.0, y=70):
    key = (time_str, warn)
    if key not in _CLK:
        f1 = font(INTER_SB, 34); f2 = font(INTER_SB, 54)
        lab = "GATE LOCKS 11:00"
        w1 = f1.getlength(lab); w2 = f2.getlength(time_str)
        bw = int(w1 + w2 + 110); bh = 92
        im = Image.new("RGBA", (bw * 2, bh * 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle([2, 2, bw * 2 - 3, bh * 2 - 3], bh, fill=(20, 6, 8, 225),
                                             outline=(255, 70, 60, 255) if warn else (200, 170, 120, 255), width=5)
        im = im.resize((bw, bh), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.text((34, bh / 2), lab, font=f1, fill=(230, 215, 200, 255), anchor="lm")
        d.text((bw - 34, bh / 2), time_str, font=f2, fill=(255, 90, 70, 255) if warn else (250, 240, 228, 255), anchor="rm")
        _CLK[key] = im
    im = _CLK[key]
    return im, (int(W / 2 - im.width / 2), y), k


def put(out, item):
    im, (x, y), k = item
    if k > 0.01:
        out.alpha_composite(with_alpha(im, k), (int(x), int(y)))


# ============================================================ characters (silhouette sprites with red rim)
def rim_sprite(m, body=(72, 26, 28), rim=(255, 60, 40), glow=(200, 20, 16), rim_w=5, glow_r=22, glow_k=0.55, radius=55):
    """m: PIL 'L' mask. Shaded dark body with a red rim light (flat21 inflate_shade) + soft red outer glow."""
    sh = inflate_shade(m, body, rim=rim, radius=radius)
    a = np.asarray(m, np.float32) / 255
    out_g = np.asarray(m.filter(ImageFilter.GaussianBlur(glow_r)), np.float32) / 255 * (1 - a) * glow_k
    rgb = np.asarray(sh, np.float32)[..., :3]
    rgb = rgb * a[..., None] + np.array(glow, np.float32) * (1 - a[..., None])
    alpha = np.clip(a + out_g, 0, 1)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8), "RGBA")


def _old_rim_sprite(m, body=(4, 1, 2), rim=(255, 60, 40), glow=(200, 20, 16), rim_w=5, glow_r=22, glow_k=0.55):
    inner = m.filter(ImageFilter.MinFilter(rim_w * 2 + 1))
    a = np.asarray(m, np.float32) / 255
    ring = np.clip(a - np.asarray(inner, np.float32) / 255, 0, 1)
    ring = np.asarray(Image.fromarray((ring * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255
    out_g = np.asarray(m.filter(ImageFilter.GaussianBlur(glow_r)), np.float32) / 255 * (1 - a) * glow_k
    rgb = np.zeros(a.shape + (3,), np.float32)
    rgb[:] = body
    rgb = rgb * (1 - ring[..., None]) + np.array(rim, np.float32) * ring[..., None]
    rgb = rgb * a[..., None] + np.array(glow, np.float32) * (1 - a[..., None])
    alpha = np.clip(a + out_g, 0, 1)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8), "RGBA")


def ghost_mask(size=(760, 1320), sway=0.0, arms=0.0, seed=5):
    """The cheonyeo gwishin: sobok jacket + bell skirt with a torn hem, very long hair, long thin arms.
    Height ~1200 px, feet hidden (she floats). sway shifts the hem/hair; arms 0..1 raises the arms forward."""
    w, h = size; cx = w / 2; top = 40; s = 3.0
    r = random.Random(seed)
    def fn(d):
        d.ellipse([cx - 22 * s, top, cx + 24 * s, top + 58 * s], fill=255)
        d.polygon([(cx - 9 * s, top + 50 * s), (cx + 11 * s, top + 50 * s), (cx + 40 * s, top + 82 * s), (cx - 38 * s, top + 84 * s)], fill=255)
        d.polygon([(cx - 40 * s, top + 82 * s), (cx + 42 * s, top + 80 * s), (cx + 38 * s, top + 128 * s), (cx - 36 * s, top + 130 * s)], fill=255)
        hem = []
        n = 16
        for i in range(n + 1):
            tt = i / n
            hem.append((cx - 92 * s + sway * s + tt * 186 * s, top + (380 + r.uniform(-16, 10) + (9 if i % 2 else 0)) * s))
        d.polygon([(cx - 34 * s, top + 122 * s), (cx + 36 * s, top + 122 * s), (cx + 72 * s + sway * 0.5 * s, top + 250 * s)]
                  + hem[::-1] + [(cx - 70 * s + sway * 0.5 * s, top + 250 * s)], fill=255)
        for side in (-1, 1):
            ex = cx + side * (58 - 10 * arms) * s; ey = top + (170 - 60 * arms) * s
            hx = cx + side * (64 - 30 * arms) * s; hy = top + (262 - 150 * arms) * s
            pts = [(cx + side * 40 * s, top + 86 * s), (ex, ey), (hx, hy)]
            d.line(pts, fill=255, width=int(9 * s), joint="curve")
            for k in range(4):
                d.line([(hx, hy), (hx + side * (k - 1.5) * 3 * s, hy + (22 + k * 3) * s)], fill=255, width=int(3 * s))
        for i in range(60):
            x0 = cx + r.uniform(-21, 23) * s; y0 = top + r.uniform(4, 22) * s
            ln = r.uniform(170, 300) * s; spread = r.uniform(-1, 1)
            pts = [(x0 + spread * 36 * s * (k / 11) + math.sin(k / 11 * 6 + i) * 5 * s + sway * s * (k / 11) ** 1.5, y0 + ln * k / 11) for k in range(12)]
            d.line(pts, fill=255, width=max(2, int(r.uniform(2, 5) * s)), joint="curve")
    return mask_of(size, fn)


_GS = {}


def ghost_sil(phase=0, arms=0.0):
    """Red-rim silhouette ghost (style A) with one red eye glinting through the hair. 8 sway phases cached."""
    key = (phase % 8, round(arms, 1))
    if key not in _GS:
        sway = 10 * math.sin(phase % 8 / 8 * 2 * math.pi)
        m = ghost_mask(sway=sway, arms=key[1])
        spr = rim_sprite(m, body=(50, 16, 18), rim=(255, 50, 36), radius=45)
        a = to_arr(spr); al = np.asarray(spr.split()[3], np.float32)
        add_glow(a, gsp(26, (255, 40, 30), 1.4), 760 / 2 - 22, 40 + 92, 1.2)
        add_glow(a, gsp(6, (255, 220, 200), 1.0), 760 / 2 - 22, 40 + 92, 1.0)
        _GS[key] = Image.fromarray(np.dstack([np.clip(a, 0, 255), al]).astype(np.uint8), "RGBA")
    return _GS[key]


_GP = {}


def ghost_pale(phase=0, grey=False, arms=0.0):
    """White-sobok ghost (explain card + CCTV): bone-white clothes with soft shading, black hair over the face."""
    key = (phase % 8, grey, round(arms, 1))
    if key not in _GP:
        sway = 10 * math.sin(phase % 8 / 8 * 2 * math.pi)
        size = (760, 1320)
        m = ghost_mask(size, sway=sway, arms=key[2])
        a = np.asarray(m, np.float32) / 255
        # shading: lighter centre, darker edges, folds
        inner = np.asarray(m.filter(ImageFilter.GaussianBlur(28)), np.float32) / 255
        yy, xx = np.mgrid[0:size[1], 0:size[0]]
        folds = 0.92 + 0.08 * np.sin(xx / 23.0 + yy / 400.0)
        lum = (0.55 + 0.45 * inner) * folds
        base = np.array([222, 216, 210], np.float32)
        rgb = lum[..., None] * base
        # hair: draw strands only (dark) over the head and down the front
        hm = Image.new("L", size, 0); d = ImageDraw.Draw(hm)
        cx, top, s = size[0] / 2, 40, 3.0
        r = random.Random(11)
        d.ellipse([cx - 23 * s, top - 2, cx + 25 * s, top + 44 * s], fill=255)
        for i in range(70):
            x0 = cx + r.uniform(-22, 23) * s; y0 = top + r.uniform(6, 26) * s
            ln = r.uniform(120, 300) * s; spread = r.uniform(-0.9, 0.9)
            pts = [(x0 + spread * 32 * s * (k / 11) + math.sin(k / 11 * 6 + i) * 4 * s + sway * s * (k / 11) ** 1.5, y0 + ln * k / 11) for k in range(12)]
            d.line(pts, fill=255, width=max(2, int(r.uniform(2, 4.5) * s)), joint="curve")
        hmm = np.asarray(hm, np.float32)[..., None] / 255
        rgb = rgb * (1 - hmm) + np.array([8, 6, 8], np.float32) * hmm
        al = np.clip(a + hmm[..., 0] * (a > -1), 0, 1)
        if grey:
            g = rgb.mean(2, keepdims=True); rgb = np.repeat(g, 3, 2)
        else:
            # one red eye through the hair
            add_glow(rgb, gsp(20, (255, 40, 30), 1.4), cx - 22, top + 92, 1.0)
        _GP[key] = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al * 255]).astype(np.uint8), "RGBA")
    return _GP[key]


def student_mask(phase=0.0, run=0.0, look_back=0.0, size=(600, 1120)):
    """Ji-ho, front/back silhouette: short hair, uniform blazer, backpack straps, swinging arms and legs.
    Height ~1050 px with feet at the bottom."""
    w, h = size; cx = w / 2; fy = h - 20
    amp = 0.35 + 0.35 * run
    lg = math.sin(phase) * amp; ar = -lg * 1.1
    lean = 0.10 * run
    def fn(d):
        hip = (cx, fy - 470)
        for sgn in (1, -1):
            a = lg * sgn
            knee = (hip[0] + sgn * 10 + math.sin(a) * 230, hip[1] + math.cos(a) * 230)
            foot = (knee[0] + math.sin(a - 0.25 * run * sgn) * 215, knee[1] + 215)
            d.line([(hip[0] + sgn * 42, hip[1]), knee, foot], fill=255, width=86, joint="curve")
            d.ellipse([foot[0] - 62, foot[1] - 32, foot[0] + 62, foot[1] + 16], fill=255)
        sh_y = fy - 870
        sx = lean * 120
        d.polygon([(cx - 135 + sx, sh_y), (cx + 135 + sx, sh_y), (cx + 118, fy - 430), (cx - 118, fy - 430)], fill=255)
        d.rounded_rectangle([cx - 105 + sx, sh_y - 10, cx + 105 + sx, sh_y + 120], 50, fill=255)
        for sgn in (1, -1):
            a = ar * sgn
            sh = (cx + sgn * 122 + sx, sh_y + 34)
            el = (sh[0] + math.sin(a) * 180 + sgn * 18, sh[1] + math.cos(a) * 180)
            hd = (el[0] + math.sin(a + 0.4 * run * sgn) * 170, el[1] + math.cos(a * 0.8) * 160)
            d.line([sh, el, hd], fill=255, width=64, joint="curve")
            d.ellipse([hd[0] - 34, hd[1] - 34, hd[0] + 34, hd[1] + 34], fill=255)
        hx = cx + sx * 1.3 + look_back * 18
        d.rectangle([hx - 26, sh_y - 70, hx + 26, sh_y + 10], fill=255)
        d.ellipse([hx - 72, sh_y - 220, hx + 72, sh_y - 50], fill=255)
        d.chord([hx - 80, sh_y - 236, hx + 80, sh_y - 110], 180, 360, fill=255)
        if look_back > 0.3:
            # turned head: a nose bump on the profile
            d.polygon([(hx + 66, sh_y - 150), (hx + 92, sh_y - 128), (hx + 66, sh_y - 118)], fill=255)
    return mask_of(size, fn)


_ST = {}


def student_sil(phase_i, run=0.0, look_back=0.0, rim=(255, 60, 40)):
    key = (phase_i % 8, round(run, 1), round(look_back, 1), rim)
    if key not in _ST:
        m = student_mask(phase_i % 8 / 8 * 2 * math.pi, run, look_back)
        _ST[key] = rim_sprite(m, rim=rim, glow_k=0.35, glow_r=16, radius=60)
    return _ST[key]


def student_grey(phase_i, run=0.0):
    key = ("g", phase_i % 8, round(run, 1))
    if key not in _ST:
        m = student_mask(phase_i % 8 / 8 * 2 * math.pi, run, 0)
        a = np.asarray(m, np.float32) / 255
        inner = np.asarray(m.filter(ImageFilter.GaussianBlur(20)), np.float32) / 255
        lum = 40 + 40 * inner
        _ST[key] = Image.fromarray(np.dstack([lum, lum, lum, a * 255]).astype(np.uint8), "RGBA")
    return _ST[key]


def guard_mask(size=(600, 1120), push=0.0):
    w, h = size; cx = w / 2; fy = h - 20
    def fn(d):
        for sgn in (1, -1):
            d.line([(cx + sgn * 40, fy - 480), (cx + sgn * 60, fy - 240), (cx + sgn * 70, fy)], fill=255, width=70, joint="curve")
            d.ellipse([cx + sgn * 70 - 55, fy - 30, cx + sgn * 70 + 55, fy + 10], fill=255)
        d.polygon([(cx - 140, fy - 860), (cx + 140, fy - 860), (cx + 130, fy - 440), (cx - 130, fy - 440)], fill=255)
        d.ellipse([cx - 70, fy - 1040, cx + 70, fy - 870], fill=255)
        d.polygon([(cx - 95, fy - 990), (cx + 95, fy - 990), (cx + 130, fy - 960), (cx - 80, fy - 960)], fill=255)  # cap
        d.chord([cx - 76, fy - 1070, cx + 76, fy - 950], 180, 360, fill=255)
        d.line([(cx - 130, fy - 830), (cx - 230 - 60 * push, fy - 640), (cx - 330 - 120 * push, fy - 600)], fill=255, width=54, joint="curve")
        d.line([(cx + 130, fy - 830), (cx + 200, fy - 640), (cx + 230, fy - 560)], fill=255, width=54, joint="curve")
        d.rectangle([cx + 215, fy - 600, cx + 250, fy - 520], fill=255)    # flashlight
    return mask_of(size, fn)


_GD = {}


def guard_sil(push=0.0):
    k = round(push, 1)
    if k not in _GD:
        _GD[k] = rim_sprite(guard_mask(push=k), rim=(255, 120, 70), glow_k=0.25)
    return _GD[k]


def paste_scaled(img, spr, x, y_bottom, height, alpha=1.0, flip=False):
    sc = height / spr.height
    im = spr.resize((max(1, int(spr.width * sc)), max(1, int(height))), Image.BILINEAR)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if alpha < 1:
        im = with_alpha(im, alpha)
    img.alpha_composite(im, (int(x - im.width / 2), int(y_bottom - im.height)))


def paste_scaled_top(img, spr, x, y_top, height, alpha=1.0):
    paste_scaled(img, spr, x, y_top + height, height, alpha)


# ============================================================ C) painted exterior: Seoul school under a blood moon
WW = W + 400     # parallax layers are wider than the frame


class Exterior:
    def __init__(self):
        rng = np.random.default_rng(3)
        random.seed(3)
        yy = np.arange(H)[:, None].astype(np.float32)
        # --- sky
        top, mid, hor = np.array([5, 2, 3], np.float32), np.array([42, 4, 7], np.float32), np.array([110, 12, 14], np.float32)
        k1 = np.clip(yy / 900, 0, 1)[..., None]; k2 = np.clip((yy - 900) / 330, 0, 1)[..., None]
        sky = top * (1 - k1) + mid * k1
        sky = sky * (1 - k2) + hor * k2
        sky = np.broadcast_to(sky, (H, WW, 3)).copy()
        mx, my, mr = 200 + 760, 500, 135
        Y, X = np.mgrid[0:H, 0:WW]
        dd = np.sqrt((X - mx) ** 2 + (Y - my) ** 2).astype(np.float32)
        sky += (np.exp(-(dd / 420) ** 2) * 0.9 + np.exp(-(dd / 190) ** 2) * 0.6)[..., None] * np.array([150, 20, 14], np.float32)
        disk = np.clip((mr - dd) / 2.0, 0, 1)
        cr = noise(H, WW, 9, 9, 2) * 0.6 + noise(H, WW, 30, 10, 6) * 0.4
        limb = np.clip(1 - (dd / mr) ** 2, 0, 1) ** 0.25
        moon = (np.array([255, 160, 128], np.float32) * (0.75 + 0.25 * limb[..., None]) * (1 - 0.2 * cr[..., None]))
        sky = sky * (1 - disk[..., None]) + moon * disk[..., None]
        self.sky = Image.fromarray(np.clip(sky, 0, 255).astype(np.uint8)).convert("RGBA")
        # --- clouds (separate, drifting)
        cw = WW + 900
        n1 = noise(900, cw, 70, 12, 20); n2 = noise(900, cw, 20, 13, 3)
        cl = np.clip((n1 * 0.75 + n2 * 0.35 - 0.48) * 3.0, 0, 1)
        band = np.clip(np.minimum(np.arange(900)[:, None] / 200, (900 - np.arange(900)[:, None]) / 250), 0, 1)
        cl *= band
        ccol = np.dstack([np.full(cl.shape, 16), np.full(cl.shape, 3), np.full(cl.shape, 5)]).astype(np.float32)
        Yc, Xc = np.mgrid[0:900, 0:cw]
        lit = np.exp(-(((Xc - 960) ** 2 + (Yc - 500) ** 2) / 300 ** 2)).astype(np.float32)
        ccol += lit[..., None] * np.array([120, 22, 16], np.float32) * (1 - cl[..., None]) * 0.9
        self.clouds = Image.fromarray(np.dstack([np.clip(ccol, 0, 255), cl * 235]).astype(np.uint8), "RGBA")
        # --- far: Bukhansan-like rocky ridge, a tower on a hill, apartment towers
        far = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); d = ImageDraw.Draw(far)
        pts = [(0, 1100)]
        x = 0
        while x < WW:
            x += random.uniform(40, 110); pts.append((x, 1050 - 120 * math.sin(x / 260) ** 2 - random.uniform(0, 60) - (90 if 300 < x < 520 else 0)))
        pts += [(WW, H), (0, H)]
        d.polygon(pts, fill=(28, 5, 8, 255))
        tx = 420
        d.rectangle([tx - 7, 820, tx + 7, 960], fill=(28, 5, 8, 255))
        d.ellipse([tx - 26, 840, tx + 26, 872], fill=(28, 5, 8, 255))
        d.rectangle([tx - 2, 770, tx + 2, 822], fill=(28, 5, 8, 255))
        d.ellipse([tx - 4, 764, tx + 4, 772], fill=(255, 40, 30, 255))
        for i in range(9):
            bx = 830 + i * 72 + random.uniform(-10, 10); bw = random.uniform(56, 70); bt = 1180 - random.uniform(240, 420)
            d.rectangle([bx, bt, bx + bw, 1200], fill=(17, 3, 5, 255))
            for wy in range(int(bt) + 14, 1190, 18):
                for wx in range(int(bx) + 6, int(bx + bw) - 6, 12):
                    if random.random() < 0.05:
                        d.rectangle([wx, wy, wx + 6, wy + 5], fill=(110, 30, 22, 255))
        self.far = far.filter(ImageFilter.GaussianBlur(1.6))
        # --- school building
        sc = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sc)
        L0, R0, T0, B0 = 310, 1170, 800, 1250
        fac = noise(B0 - T0 + 140, R0 - L0, 18, 21, 2)
        fac_rgb = (np.array([30, 8, 10], np.float32) * (0.8 + 0.4 * fac[..., None]))
        d.rectangle([L0, T0 - 22, R0, B0], fill=(30, 8, 10, 255))
        d.rectangle([690, 680, 790, B0], fill=(30, 8, 10, 255))
        arr = np.asarray(sc, np.float32).copy()
        arr[T0 - 140:B0, L0:R0, :3] = np.where(arr[T0 - 140:B0, L0:R0, 3:] > 0, fac_rgb, arr[T0 - 140:B0, L0:R0, :3])
        sc = Image.fromarray(arr.astype(np.uint8), "RGBA"); d = ImageDraw.Draw(sc)
        for i in range(5):
            y = T0 + i * 112
            d.rectangle([L0, y - 4, R0, y + 4], fill=(44, 10, 12, 255))
        d.line([(L0, T0 - 22), (690, T0 - 22)], fill=(130, 24, 20, 255), width=3)
        d.line([(790, T0 - 22), (R0, T0 - 22)], fill=(150, 26, 22, 255), width=3)
        d.line([(690, 680), (790, 680)], fill=(160, 28, 22, 255), width=3)
        d.line([(R0, T0 - 22), (R0, B0)], fill=(110, 20, 18, 255), width=3)
        self.win = []
        for row in range(4):
            y0 = T0 + row * 112 + 26
            for wing, xs in (("L", range(335, 690 - 40, 58)), ("R", range(812, R0 - 30, 58))):
                for c, x0 in enumerate(xs):
                    dim = random.random() < 0.12
                    d.rectangle([x0, y0, x0 + 40, y0 + 62], fill=(52, 12, 12, 255) if dim else (11, 3, 5, 255))
                    d.line([(x0 + 20, y0), (x0 + 20, y0 + 62)], fill=(30, 8, 10, 255), width=3)
                    self.win.append((row, wing, c, x0, y0))
        for k in range(4):
            y0 = T0 + k * 112 + 20
            d.rectangle([724, y0, 756, y0 + 80], fill=(70, 14, 14, 255))
        d.ellipse([712, 700, 768, 756], fill=(60, 14, 14, 255), outline=(150, 30, 24, 255), width=3)
        d.line([(740, 728), (740, 708)], fill=(10, 2, 3, 255), width=4); d.line([(740, 728), (754, 734)], fill=(10, 2, 3, 255), width=4)
        d.rectangle([600, B0 - 120, 880, B0 - 104], fill=(40, 10, 12, 255))
        d.rectangle([660, B0 - 104, 820, B0], fill=(7, 2, 3, 255))
        d.rectangle([1000, 735, 1080, 778], fill=(22, 6, 8, 255))
        kf = krfont(30)
        d.text((740, 650), "한빛고등학교", font=kf, fill=(120, 30, 26, 255), anchor="mm")
        d.line([(250, 1250), (250, 820)], fill=(20, 5, 7, 255), width=5)
        d.polygon([(252, 826), (300, 836), (252, 850)], fill=(50, 12, 12, 255))
        self.school = sc
        # lit 4th-floor window (row 0, right wing, col 3) with and without the figure in it
        lw = [w_ for w_ in self.win if w_[0] == 0 and w_[1] == "R" and w_[2] == 3][0]
        self.lit_xy = (lw[3], lw[4])
        def lit_layer(fig):
            im = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); dd_ = ImageDraw.Draw(im)
            x0, y0 = self.lit_xy
            g = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); ImageDraw.Draw(g).rectangle([x0 - 10, y0 - 10, x0 + 50, y0 + 72], fill=(255, 40, 26, 200))
            im.alpha_composite(g.filter(ImageFilter.GaussianBlur(26)))
            dd_.rectangle([x0, y0, x0 + 40, y0 + 62], fill=(255, 70, 50, 255))
            if fig:
                dd_.ellipse([x0 + 12, y0 + 12, x0 + 28, y0 + 30], fill=(8, 1, 2, 255))
                dd_.polygon([(x0 + 8, y0 + 26), (x0 + 32, y0 + 26), (x0 + 36, y0 + 62), (x0 + 4, y0 + 62)], fill=(8, 1, 2, 255))
                for k in range(5):
                    dd_.line([(x0 + 13 + k * 3.5, y0 + 18), (x0 + 11 + k * 4, y0 + 50)], fill=(8, 1, 2, 255), width=2)
            dd_.line([(x0 + 20, y0), (x0 + 20, y0 + 62)], fill=(60, 10, 10, 255), width=3)
            return im
        self.lit_fig = lit_layer(True); self.lit_empty = lit_layer(False)
        # --- sports field
        fl = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); d = ImageDraw.Draw(fl)
        d.rectangle([0, 1250, WW, 1560], fill=(36, 9, 10, 255))
        a = np.asarray(fl, np.float32).copy()
        n = noise(310, WW, 6, 31)
        a[1250:1560, :, :3] *= (0.75 + 0.45 * n[..., None])
        fl = Image.fromarray(a.astype(np.uint8), "RGBA"); d = ImageDraw.Draw(fl)
        d.arc([150, 1270, WW - 150, 1640], 190, 350, fill=(80, 24, 22, 255), width=4)
        gx = 470
        d.line([(gx, 1350), (gx, 1300), (gx + 150, 1300), (gx + 150, 1350)], fill=(70, 18, 18, 255), width=6)
        pud = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); ImageDraw.Draw(pud).ellipse([880, 1420, 1100, 1450], fill=(170, 26, 20, 170))
        fl.alpha_composite(pud.filter(ImageFilter.GaussianBlur(3)))
        self.field = fl
        # --- near: wall, gate pillars, plaque, road, ginkgo, streetlamp
        nr = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); d = ImageDraw.Draw(nr)
        d.rectangle([0, 1600, WW, H], fill=(13, 4, 5, 255))
        a = np.asarray(nr, np.float32).copy()
        yy2 = np.arange(1600, H)[:, None]
        a[1600:H, :, :3] *= (0.8 + 0.3 * noise(H - 1600, WW, 4, 41)[..., None])
        nr = Image.fromarray(a.astype(np.uint8), "RGBA"); d = ImageDraw.Draw(nr)
        P1x, P2x = 200 + 250, 200 + 830
        for x in list(range(0, P1x - 40, 34)) + list(range(P2x + 40, WW, 34)):
            d.line([(x, 1470), (x, 1610)], fill=(4, 1, 2, 255), width=7)
            d.polygon([(x - 7, 1472), (x + 7, 1472), (x, 1452)], fill=(4, 1, 2, 255))
        d.rectangle([0, 1490, P1x - 40, 1500], fill=(4, 1, 2, 255)); d.rectangle([P2x + 40, 1490, WW, 1500], fill=(4, 1, 2, 255))
        d.rectangle([0, 1580, P1x - 40, 1615], fill=(6, 2, 3, 255)); d.rectangle([P2x + 40, 1580, WW, 1615], fill=(6, 2, 3, 255))
        for px in (P1x, P2x):
            d.rectangle([px - 40, 1360, px + 40, 1640], fill=(16, 5, 6, 255))
            d.rectangle([px - 50, 1346, px + 50, 1366], fill=(26, 7, 8, 255))
            d.line([(px + 40, 1366), (px + 40, 1640)], fill=(90, 18, 16, 255), width=2)
        d.rectangle([P1x - 30, 1400, P1x + 30, 1560], fill=(40, 22, 12, 255))
        kf2 = krfont(34)
        for i, ch in enumerate("한빛고"):
            d.text((P1x, 1425 + i * 44), ch, font=kf2, fill=(160, 120, 70, 255), anchor="mm")
        self.P = (P1x, P2x)
        # ginkgo tree, left foreground
        def branch(x, y, ang, ln, w, depth):
            if depth == 0 or ln < 8:
                if random.random() < 0.85:
                    for _ in range(3):
                        lx, ly = x + random.uniform(-12, 12), y + random.uniform(-12, 12)
                        a0 = random.uniform(0, 360)
                        d.pieslice([lx - 7, ly - 7, lx + 7, ly + 7], a0, a0 + 110, fill=(74, 42, 10, 255))
                return
            x2, y2 = x + math.cos(ang) * ln, y - math.sin(ang) * ln
            d.line([(x, y), (x2, y2)], fill=(3, 1, 1, 255), width=max(1, int(w)))
            for _ in range(2 if depth > 3 else 3):
                branch(x2, y2, ang + random.uniform(-0.65, 0.65), ln * random.uniform(0.66, 0.8), w * 0.68, depth - 1)
        d.polygon([(200 - 60, H), (200 + 70, H), (200 + 52, 1100), (200 + 30, 820), (200 + 8, 820), (200 - 20, 1100)], fill=(3, 1, 1, 255))
        branch(200 + 18, 860, 1.15, 210, 26, 8)
        branch(200 + 22, 1000, 0.45, 180, 18, 7)
        branch(200 + 14, 940, 2.2, 150, 16, 6)
        # streetlamp, right
        lx = 200 + 990
        d.line([(lx, H), (lx, 1080)], fill=(4, 1, 2, 255), width=14)
        d.line([(lx, 1085), (lx - 70, 1070)], fill=(4, 1, 2, 255), width=10)
        d.rectangle([lx - 105, 1062, lx - 55, 1082], fill=(4, 1, 2, 255))
        self.lamp_xy = (lx - 80, 1086)
        self.near = nr
        self.lamp_glow = gsp(260, (255, 80, 40), 1.8)
        self.lamp_core = gsp(40, (255, 210, 160), 1.2)

    def gate(self, open_=0.5):
        """Sliding iron gate between the pillars; open_ 0 = closed, 1 = fully open (slides behind the right pillar)."""
        P1, P2 = self.P
        im = Image.new("RGBA", (WW, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        gw = (P2 - 40) - (P1 + 40)
        x0 = P1 + 40 + gw * open_
        x1 = x0 + gw
        d.rectangle([x0, 1480, x1, 1492], fill=(6, 2, 3, 255)); d.rectangle([x0, 1600, x1, 1612], fill=(6, 2, 3, 255))
        x = x0
        while x <= x1:
            d.line([(x, 1470), (x, 1615)], fill=(6, 2, 3, 255), width=6)
            x += 30
        d.line([(x0, 1478), (x1, 1478)], fill=(110, 22, 18, 255), width=2)
        return im

    def frame(self, t, cam=0.0, lit="fig", lit_k=1.0, gate_open=0.45, chars_mid=None, chars_near=None, fog_k=0.35, leaves=True):
        img = self.sky.crop((int(200 - cam * 0.08), 0, int(200 - cam * 0.08) + W, H))
        co = int((t * 14) % 900)
        img.alpha_composite(self.clouds.crop((co + int(200 - cam * 0.12), 0, co + int(200 - cam * 0.12) + W, 900)), (0, 0))
        def lay(L, k):
            x = int(200 - cam * k)
            return L.crop((x, 0, x + W, H))
        img.alpha_composite(lay(self.far, 0.2))
        fog(img, t, 0.28 * fog_k / 0.35, 1000, 1260, speed=10, col=(130, 22, 20))
        img.alpha_composite(lay(self.school, 0.45))
        if lit and lit_k > 0:
            L = self.lit_fig if lit == "fig" else self.lit_empty
            img.alpha_composite(with_alpha(lay(L, 0.45), lit_k))
        img.alpha_composite(lay(self.field, 0.6))
        if chars_mid:
            chars_mid(img, t, lambda k: -cam * k)
        fog(img, t, fog_k, 1200, 1620, speed=22, col=(150, 28, 24), off=300)
        nl = lay(self.near, 1.0)
        img.alpha_composite(nl)
        img.alpha_composite(lay(self.gate(gate_open), 1.0))
        a = to_arr(img)
        lx, ly = self.lamp_xy[0] - 200 + cam, self.lamp_xy[1]
        fl = 0.9 + 0.1 * math.sin(t * 23) * math.sin(t * 7)
        add_glow(a, self.lamp_glow, lx, ly + 40, 0.55 * fl)
        add_glow(a, self.lamp_core, lx, ly, 1.0 * fl)
        img = to_img(a)
        if chars_near:
            chars_near(img, t, lambda k: -cam * k)
        if leaves:
            bokeh_particles(img, 26, 7, t, color=(150, 80, 20), size=(4, 14), blur=(0, 5), area=(0, 300, W, 1800), drift=(-18, 40))
        return img


_EXT = None


def ext():
    global _EXT
    if _EXT is None:
        _EXT = Exterior()
    return _EXT


# ============================================================ A) red-silhouette corridor (4th floor)
class Corridor:
    VP = (540, 900)
    FAR = (110, 150)

    def __init__(self, mirror=False):
        self.mirror = mirror
        vx, vy = self.VP; fw, fh = self.FAR
        self.fl, self.fr, self.ft, self.fb = vx - fw, vx + fw, vy - fh, vy + fh
        base = np.zeros((H, W, 3), np.float32) + np.array([3, 1, 2], np.float32)
        def m(fn, blur=0):
            return np.asarray(mask_of((W, H), fn, blur), np.float32)[..., None] / 255
        def over(a, mk, col, k=1.0):
            return a * (1 - mk * k) + np.array(col, np.float32) * mk * k
        fl, fr, ft, fb = self.fl, self.fr, self.ft, self.fb
        base = over(base, m(lambda d: d.polygon([(0, H), (W, H), (fr, fb), (fl, fb)], fill=255)), (16, 5, 6))
        base = over(base, m(lambda d: d.polygon([(0, 0), (W, 0), (fr, ft), (fl, ft)], fill=255)), (6, 2, 3))
        base = over(base, m(lambda d: d.polygon([(0, 0), (fl, ft), (fl, fb), (0, H)], fill=255)), (12, 4, 5))
        base = over(base, m(lambda d: d.polygon([(W, 0), (fr, ft), (fr, fb), (W, H)], fill=255)), (14, 4, 5))
        base = over(base, m(lambda d: d.rectangle([fl, ft, fr, fb], fill=255)), (4, 1, 2))
        # floor tiles (perspective lines + a few cross lines)
        for k in range(-8, 9):
            base = over(base, m(lambda d, k=k: d.line([(W / 2 + k * 160, H), (vx + k * fw / 8, fb)], fill=255, width=2)), (0, 0, 0), 0.5)
        for f in (0.08, 0.2, 0.35, 0.52, 0.7):
            y = H + (fb - H) * f ** 0.8
            base = over(base, m(lambda d, y=y: d.line([(0, y), (W, y)], fill=255, width=2)), (0, 0, 0), 0.4)
        # left wall: classroom doors + sliding windows + class plates sticking out
        glow = np.zeros_like(base)
        self.plates = []
        for f0, f1 in [(0.06, 0.2), (0.32, 0.42), (0.55, 0.62), (0.73, 0.77)]:
            q = [self.wp("L", f0, 0.22), self.wp("L", f1, 0.22), self.wp("L", f1, 1.0), self.wp("L", f0, 1.0)]
            base = over(base, m(lambda d, q=q: d.polygon(q, fill=255)), (5, 1, 2))
            qw = [self.wp("L", f1 + 0.01, 0.25), self.wp("L", f1 + 0.08, 0.25), self.wp("L", f1 + 0.08, 0.55), self.wp("L", f1 + 0.01, 0.55)]
            base = over(base, m(lambda d, q=qw: d.polygon(q, fill=255)), (9, 2, 3))
            p0 = self.wp("L", f0, 0.12); p1 = self.wp("L", f0, 0.19)
            self.plates.append((p0, p1, f0))
        # right wall: tall windows with red moonlight + floor pools + light shafts
        for f0, f1 in [(0.02, 0.17), (0.27, 0.39), (0.5, 0.58), (0.67, 0.72), (0.79, 0.82)]:
            q = [self.wp("R", f0, 0.2), self.wp("R", f1, 0.2), self.wp("R", f1, 0.62), self.wp("R", f0, 0.62)]
            glow += m(lambda d, q=q: d.polygon(q, fill=255), 2) * np.array([255, 60, 44], np.float32) * 0.85
            glow += m(lambda d, q=q: d.polygon(q, fill=255), 50) * np.array([255, 20, 14], np.float32) * 0.7
            mt = ((q[0][0] + q[1][0]) / 2, (q[0][1] + q[1][1]) / 2); mb = ((q[3][0] + q[2][0]) / 2, (q[3][1] + q[2][1]) / 2)
            ml = ((q[0][0] + q[3][0]) / 2, (q[0][1] + q[3][1]) / 2); mr = ((q[1][0] + q[2][0]) / 2, (q[1][1] + q[2][1]) / 2)
            bar = m(lambda d: (d.line([mt, mb], fill=255, width=max(3, int(14 * (1 - f0)))), d.line([ml, mr], fill=255, width=max(3, int(10 * (1 - f0))))))
            p0, p1 = self.wp("R", f0, 1.0), self.wp("R", f1, 1.0)
            sh = 520 * (1 - f0) ** 1.2
            pool = [(p0[0] - sh * 0.25, p0[1] - 14), (p1[0] - sh * 0.2, p1[1] - 4), (p1[0] - sh * 0.9, p1[1] - 2), (p0[0] - sh * 1.15, p0[1] - 40)]
            glow += m(lambda d, q=pool: d.polygon(q, fill=255), 20) * np.array([255, 26, 18], np.float32) * 0.32
            glow += m(lambda d, q=[q[0], q[1], pool[2], pool[3]]: d.polygon(q, fill=255), 40) * np.array([255, 26, 18], np.float32) * 0.1
            glow *= (1 - bar * 0.95)
        # far stairwell door with red light leaking
        door = [self.fl + 70, self.ft + 50, self.fr - 70, self.fb]
        glow += m(lambda d: d.rectangle(door, fill=255), 70) * np.array([255, 26, 18], np.float32) * 0.55
        glow += m(lambda d: d.rectangle(door, fill=255), 4) * np.array([255, 110, 80], np.float32) * 0.6
        # floor reflection of the windows (wet, polished)
        refl = np.flipud(glow)
        sh = int(2 * self.fb - H)
        refl = np.roll(refl, sh, axis=0)
        refl[:self.fb] = 0
        glow += refl * 0.22
        Yb = np.arange(H)[:, None, None]
        amb = np.exp(-((Yb - self.VP[1]) / 700.0) ** 2) * np.array([60, 10, 10], np.float32)
        self.base = base * 2.3 + amb
        self.glow = glow * 1.35
        # ceiling tubes (each can be switched on/off)
        self.tubes = []
        for f in (0.1, 0.33, 0.55, 0.72):
            y = self.ft * f ** 0.8 + 6; w = 150 * (1 - f) + 18
            tm = m(lambda d, y=y, w=w: d.rectangle([W / 2 - w, y - 5, W / 2 + w, y + 5], fill=255), 1)
            tg = m(lambda d, y=y, w=w: d.rectangle([W / 2 - w, y - 5, W / 2 + w, y + 5], fill=255), 90)
            fy = H + (self.fb - H) * f ** 0.8
            pool = m(lambda d, fy=fy, w=w: d.ellipse([W / 2 - w * 2.2, fy - 60 * (1 - f), W / 2 + w * 2.2, fy + 60 * (1 - f)], fill=255), 40)
            self.tubes.append(tm * np.array([255, 230, 225], np.float32) + tg * np.array([230, 190, 185], np.float32) * 0.9
                              + pool * np.array([200, 150, 150], np.float32) * 0.35)
        # signs: the floor sign "4층" and the class plates "3-1".. on the left wall, the green exit sign far away
        sg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sg)
        kf = krfont(34)
        for i, (p0, p1, f0) in enumerate(self.plates):
            sw = 80 * (1 - f0) + 18; sh_ = 40 * (1 - f0) + 10
            x = p0[0] + 10; y = p0[1]
            if mirror:
                x = W - x - sw
            d.rectangle([x, y, x + sw, y + sh_], fill=(20, 6, 7, 255), outline=(120, 26, 22, 255), width=2)
            if f0 < 0.5:
                d.text((x + sw / 2, y + sh_ / 2), f"3-{4 - i}", font=krfont(int(sh_ * 0.7)), fill=(200, 160, 150, 255), anchor="mm")
        ex = (self.fl + 110, self.ft + 18)
        if mirror:
            ex = (W - ex[0], ex[1])
        d.rectangle([ex[0] - 28, ex[1] - 10, ex[0] + 28, ex[1] + 10], fill=(20, 120, 60, 255))
        self.signs = sg
        self.exit_xy = ex
        if mirror:
            self.base = self.base[:, ::-1].copy(); self.glow = self.glow[:, ::-1].copy()
            self.tubes = [tb[:, ::-1].copy() for tb in self.tubes]

    def wp(self, side, f, v):
        fe = f ** 0.8
        x = (W + (self.fr - W) * fe) if side == "R" else (self.fl * fe)
        yt = self.ft * fe; yb = H + (self.fb - H) * fe
        return (x, yt + (yb - yt) * v)

    def depth_xy(self, f, x_off=0.0):
        """Floor point at depth f (0 near .. 1 far) on the centre line, plus the height of a 1.0 person there."""
        fe = f ** 0.8
        y = H + (self.fb - H) * fe
        wall_h = (H + (self.fb - H) * fe) - self.ft * fe
        return (W / 2 + x_off * (1 - fe), y, wall_h * 0.62)

    def frame(self, t, tubes=(0, 0, 0, 0), glow_k=1.0, flicker=0.0, chars=None, fog_k=0.45, red_k=1.0):
        fl = 1.0 - flicker * (0.5 + 0.5 * math.sin(t * 37) * math.sin(t * 13 + 1))
        a = self.base + self.glow * (glow_k * fl * red_k)
        for tb, on in zip(self.tubes, tubes):
            if on > 0.01:
                a = a + tb * on
        img = to_img(a)
        img.alpha_composite(self.signs)
        exy = self.exit_xy if not self.mirror else (W - self.exit_xy[0], self.exit_xy[1])
        fog(img, t, fog_k * 0.6, self.ft + 200, self.fb + 140, speed=12, col=(170, 30, 24), off=100)
        if chars:
            chars(img, t)
        fog(img, t, fog_k * 0.75, self.fb - 80, H, speed=26, col=(170, 26, 20), off=400)
        return img


_COR = {}


def corridor(mirror=False):
    if mirror not in _COR:
        _COR[mirror] = Corridor(mirror)
    return _COR[mirror]


# ============================================================ A) toilet stall, seen from inside
class Stall:
    def __init__(self):
        a = np.zeros((H, W, 3), np.float32) + np.array([4, 1, 2], np.float32)
        def m(fn, blur=0):
            return np.asarray(mask_of((W, H), fn, blur), np.float32)[..., None] / 255
        def over(a, mk, col, k=1.0):
            return a * (1 - mk * k) + np.array(col, np.float32) * mk * k
        DL, DR, DT, DB = 170, 910, 160, 1600
        self.D = (DL, DR, DT, DB)
        # side partitions
        a = over(a, m(lambda d: d.polygon([(0, 0), (DL, DT), (DL, DB + 40), (0, H)], fill=255)), (11, 3, 4))
        a = over(a, m(lambda d: d.polygon([(W, 0), (DR, DT), (DR, DB + 40), (W, H)], fill=255)), (9, 3, 4))
        # floor tiles in front (inside the stall)
        a = over(a, m(lambda d: d.polygon([(0, H), (W, H), (DR, DB + 40), (DL, DB + 40)], fill=255)), (14, 4, 5))
        for k in range(-5, 6):
            a = over(a, m(lambda d, k=k: d.line([(W / 2 + k * 260, H), (W / 2 + k * 70, DB + 40)], fill=255, width=2)), (0, 0, 0), 0.6)
        for y in (1700, 1790, 1900):
            a = over(a, m(lambda d, y=y: d.line([(0, y), (W, y)], fill=255, width=2)), (0, 0, 0), 0.5)
        # the door: dark panel with a lighter frame, scratches, hook, latch
        door = noise(DB - DT, DR - DL, 10, 51, 2)
        dpanel = np.array([20, 6, 8], np.float32) * (0.85 + 0.3 * door[..., None])
        a[DT:DB, DL:DR] = dpanel
        a = over(a, m(lambda d: d.rectangle([DL, DT, DR, DB], outline=255, width=8)), (34, 9, 10))
        a = over(a, m(lambda d: d.rounded_rectangle([DR - 120, 860, DR - 50, 920], 10, fill=255)), (40, 12, 12))
        a = over(a, m(lambda d: d.rectangle([DR - 104, 876, DR - 66, 904], fill=255)), (230, 30, 24))
        a = over(a, m(lambda d: d.line([(W / 2, 300), (W / 2, 360), (W / 2 + 40, 380)], fill=255, width=12, joint="curve")), (40, 12, 12))
        r = random.Random(4)
        sc = m(lambda d: [d.line([(x0 := r.uniform(DL + 60, DR - 60), y0 := r.uniform(500, 1400)), (x0 + r.uniform(-60, 60), y0 + r.uniform(-30, 30))], fill=255, width=2) for _ in range(40)])
        a = over(a, sc, (60, 20, 20), 0.6)
        sg = Image.new("L", (W, H), 0); dd = ImageDraw.Draw(sg)
        dd.text((W / 2 - 40, 1200), "살려줘", font=krfont(64), fill=255, anchor="mm")
        sgm = np.asarray(sg.filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255
        a = over(a, sgm, (90, 30, 28), 0.55)
        self.base = a * 2.0 + np.array([18, 3, 4], np.float32)
        # light under the door + spill on the floor + red edge light round the door
        g = m(lambda d: d.rectangle([DL - 10, DB, DR + 10, DB + 40], fill=255), 3) * np.array([255, 50, 36], np.float32)
        g += m(lambda d: d.polygon([(DL - 30, DB + 40), (DR + 30, DB + 40), (W + 200, H), (-200, H)], fill=255), 50) * np.array([255, 36, 24], np.float32) * 0.95
        g += m(lambda d: d.rectangle([DL - 4, DT - 4, DR + 4, DT + 4], fill=255), 6) * np.array([255, 40, 30], np.float32) * 0.5
        self.glow = g
        # Ji-ho's sneakers at the bottom of the frame
        # Ji-ho's sneakers, seen from above at the bottom of the frame (toes towards the door)
        sm = mask_of((W, 400), lambda d: (d.ellipse([300, 60, 470, 470], fill=255), d.ellipse([610, 60, 780, 470], fill=255)))
        shoes = rim_sprite(sm, body=(44, 16, 18), glow_k=0.2, radius=50)
        sd = ImageDraw.Draw(shoes)
        for cx_ in (385, 695):
            sd.ellipse([cx_ - 86, 56, cx_ + 86, 476], outline=(150, 70, 66, 255), width=6)
            for k in range(4):
                sd.line([(cx_ - 30, 220 + k * 34), (cx_ + 30, 236 + k * 34)], fill=(120, 50, 48, 255), width=5)
        self.shoes = shoes

    def frame(self, t, shadow_x=None, shadow_k=0.0, hair=0.0, hem=0.0, flicker=0.0, drip=True):
        DL, DR, DT, DB = self.D
        fl = 1.0 - flicker * (0.5 + 0.5 * math.sin(t * 41) * math.sin(t * 9))
        g = self.glow * fl
        if shadow_k > 0 and shadow_x is not None:
            xs = np.arange(W)[None, :, None]
            occ = np.exp(-((xs - shadow_x) / 150.0) ** 2) * shadow_k
            yy = np.arange(H)[:, None, None]
            occ = occ * (yy >= DB - 4)
            g = g * (1 - np.clip(occ, 0, 0.92))
        a = self.base + g
        img = to_img(a)
        if hem > 0:
            hm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(hm)
            pts = [(shadow_x - 160 + k * 20, DB + 6 + (8 if k % 2 else 0)) for k in range(17)]
            d.polygon([(shadow_x - 170, DB - 2)] + pts + [(shadow_x + 170, DB - 2)], fill=(210, 200, 195, int(230 * hem)))
            img.alpha_composite(hm.filter(ImageFilter.GaussianBlur(1.2)))
        if hair > 0:
            hm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(hm)
            r = random.Random(8)
            for i in range(70):
                x0 = r.uniform(DL + 120, DR - 120); ln = hair * r.uniform(0.6, 1.0) * 330
                pts = [(x0 + math.sin(k * 0.7 + i + t * 2) * 10 + (x0 - W / 2) * 0.25 * k / 10, DB + 20 + ln * k / 10) for k in range(11)]
                d.line(pts, fill=(2, 1, 1, 255), width=r.choice([3, 4, 5]), joint="curve")
            img.alpha_composite(hm)
        img.alpha_composite(self.shoes, (0, H - 330))
        if drip:
            ph = (t * 0.7) % 1.0
            d = ImageDraw.Draw(img)
            if ph < 0.7:
                y = 120 + (ph / 0.7) ** 2 * 1500
                d.ellipse([DL + 60, y, DL + 70, y + 18], fill=(180, 40, 34, 200))
        fog(img, t, 0.25, DB - 200, H, speed=10, col=(160, 24, 18))
        return img


_STALL = None


def stall():
    global _STALL
    if _STALL is None:
        _STALL = Stall()
    return _STALL


# ============================================================ B) CCTV (rendered at half resolution, monochrome)
HW, HH = 540, 960


class Cctv:
    def __init__(self):
        self.views = {"hall": self._hall(), "stalls": self._stalls(), "gate": self._gate()}
        r = np.random.default_rng(77)
        self.noise = [r.normal(0, 0.05, (HH, HW)).astype(np.float32) for _ in range(6)]
        self.scan = (1 - 0.16 * (np.arange(HH)[:, None] % 3 == 0)).astype(np.float32)
        self.vig = vignette(0.6, HW, HH)[..., 0]
        self.f = ImageFont.truetype(MONO, 34)
        self.fs = ImageFont.truetype(MONO, 28)

    def _canvas(self, col=0.06):
        return Image.new("L", (HW, HH), int(col * 255))

    def _hall(self):
        im = self._canvas(); d = ImageDraw.Draw(im)
        vx, vy, fw, fh = 330, 330, 34, 44
        fl, fr, ft, fb = vx - fw, vx + fw, vy - fh, vy + fh
        d.polygon([(0, HH), (HW, HH), (fr, fb), (fl, fb)], fill=60)
        d.polygon([(0, 0), (HW, 0), (fr, ft), (fl, ft)], fill=34)
        d.polygon([(0, 0), (fl, ft), (fl, fb), (0, HH)], fill=78)
        d.polygon([(HW, 0), (fr, ft), (fr, fb), (HW, HH)], fill=46)
        d.rectangle([fl, ft, fr, fb], fill=8)
        for f0, f1 in [(0.1, 0.24), (0.42, 0.52), (0.66, 0.72)]:
            def wp(f, v):
                fe = f ** 0.8; x = fl * fe; yt = ft * fe; yb = HH + (fb - HH) * fe
                return (x, yt + (yb - yt) * v)
            d.polygon([wp(f0, 0.25), wp(f1, 0.25), wp(f1, 1), wp(f0, 1)], fill=22)
        for f in (0.15, 0.45):
            y = ft * f ** 0.8 + 4; x = vx - 150 * (1 - f)
            d.rectangle([x - 60 * (1 - f) - 10, y - 3, x + 60 * (1 - f) + 10, y + 3], fill=235)
        a = np.asarray(im, np.float32) / 255
        g = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40)), np.float32) / 255
        a = np.clip(a + g * 0.25, 0, 1)
        sh = np.asarray(mask_of((HW, HH), lambda d: d.ellipse([20, 520, 440, 900], fill=255), 60), np.float32) / 255
        return np.clip(a + sh * 0.08, 0, 1)

    def _stalls(self):
        im = self._canvas(0.1); d = ImageDraw.Draw(im)
        d.polygon([(0, 560), (HW, 430), (HW, HH), (0, HH)], fill=70)
        for i in range(-6, 12):
            d.line([(i * 60, HH), (180 + i * 48, 430)], fill=52, width=1)
        for y in range(470, HH, 46):
            d.line([(0, y + 130 - (y - 430) * 0.25), (HW, y)], fill=52, width=1)
        d.polygon([(0, 80), (HW, 120), (HW, 430), (0, 560)], fill=54)
        for k in range(4):
            x0 = 30 + k * 128; x1 = x0 + 108
            yt0 = 150 + k * 6; yb0 = 545 - k * 30; yt1 = 154 + (k + 1) * 6 - 6; yb1 = 545 - (k + 1) * 30 + 10
            d.polygon([(x0, yt0), (x1, yt1), (x1, yb1), (x0, yb0)], fill=96 if k != 2 else 88)
            d.line([(x1 + 4, yt1 - 10), (x1 + 4, yb1 + 18)], fill=30, width=6)
            if k != 2:
                d.polygon([(x0 + 10, yt0 + 8), (x0 + 30, yt0 + 12), (x0 + 30, yb0 - 10), (x0 + 10, yb0 - 4)], fill=20)
            else:
                d.rectangle([x1 - 22, (yt1 + yb1) / 2 - 6, x1 - 12, (yt1 + yb1) / 2 + 6], fill=150)
        d.rectangle([200, 20, 330, 30], fill=230)
        a = np.asarray(im, np.float32) / 255
        g = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(50)), np.float32) / 255
        self.stall3 = ((30 + 2 * 128 + 54), 545 - 2 * 30)
        return np.clip(a * 0.95 + g * 0.2, 0, 1)

    def _gate(self):
        im = self._canvas(0.04); d = ImageDraw.Draw(im)
        d.polygon([(0, 380), (HW, 330), (HW, HH), (0, HH)], fill=40)
        d.polygon([(0, 380), (HW, 330), (HW, 300), (0, 340)], fill=18)
        d.polygon([(0, 640), (HW, 560), (HW, 600), (0, 690)], fill=58)
        for x in range(-40, HW + 40, 22):
            d.line([(x, 440 - x * 0.09), (x, 520 - x * 0.09)], fill=14, width=4)
        d.line([(0, 452), (HW, 404)], fill=14, width=4); d.line([(0, 515), (HW, 467)], fill=14, width=4)
        d.rectangle([150, 380, 178, 560], fill=24); d.rectangle([370, 360, 398, 540], fill=24)
        d.polygon([(180, 520), (370, 503), (380, 700), (160, 730)], fill=46)
        d.line([(470, HH), (470, 140)], fill=10, width=8)
        d.rectangle([440, 132, 480, 146], fill=10)
        a = np.asarray(im, np.float32) / 255
        pool = np.asarray(mask_of((HW, HH), lambda d: d.ellipse([280, 380, 600, 760], fill=255), 70), np.float32) / 255
        a = np.clip(a + pool * 0.35, 0, 1)
        self.gate_gap = (180, 370, 520)
        return a

    def frame(self, view, t, sprites=(), cam="CAM 04  4F HALL", clock=(22, 54, 10), glitch=0.0, playback=False, extra=None):
        a = self.views[view].copy()
        if view == "hall":
            a = np.clip(a * (0.92 + 0.08 * math.sin(t * 50) * (math.sin(t * 3) > 0.6)), 0, 1)
        img = Image.fromarray((a * 255).astype(np.uint8)).convert("RGBA")
        for spr, x, yb, h_, al in sprites:
            paste_scaled(img, spr, x, yb, h_, al)
        if extra:
            extra(img, t)
        g = np.asarray(img.convert("L"), np.float32) / 255
        g = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9)), np.float32) / 255
        g = g * 1.1 + self.noise[int(t * FPS) % 6]
        g = g * self.scan * self.vig
        band = np.exp(-(((np.arange(HH) - (t * 160) % (HH + 200) + 100)) / 14.0) ** 2)[:, None]
        g = np.clip(g + band * 0.12, 0, 1)
        if glitch > 0:
            r = np.random.default_rng(int(t * 97))
            for _ in range(int(3 + 8 * glitch)):
                y0 = int(r.integers(0, HH - 40)); hh = int(r.integers(6, 40))
                g[y0:y0 + hh] = np.roll(g[y0:y0 + hh], int(r.integers(-80, 80) * glitch), axis=1)
        big = Image.fromarray((g * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        A = np.asarray(big, np.float32)[..., None] * np.array([0.9, 1.0, 0.92], np.float32)
        ca = 3 + int(10 * glitch)
        A[..., 0] = np.roll(A[..., 0], ca, axis=1); A[..., 2] = np.roll(A[..., 2], -ca, axis=1)
        out = to_img(A); d = ImageDraw.Draw(out)
        if int(t * 2) % 2 == 0:
            d.ellipse([40, 54, 68, 82], fill=(235, 30, 30, 255))
        d.text((80, 48), "PLAY" if playback else "REC", font=self.f, fill=(235, 235, 235, 255))
        d.text((W - 40, 48), cam, font=self.f, fill=(235, 235, 235, 255), anchor="ra")
        hh, mm, s0 = clock
        tot = s0 + int(t)
        sec = tot % 60; mm2 = mm + tot // 60
        d.text((40, H - 100), "2026-11-24" if not playback else "◀◀ 2026-11-24", font=self.fs, fill=(235, 235, 235, 255))
        d.text((W - 40, H - 100), f"{hh:02d}:{mm2:02d}:{sec:02d}", font=self.f, fill=(235, 235, 235, 255), anchor="ra")
        return out


_CC = None


def cctv():
    global _CC
    if _CC is None:
        _CC = Cctv()
    return _CC


# ============================================================ the face (jump scare)
_FACE = None


def face_sprite():
    """Close-up of her face: pale, long black hair hanging over most of it, ONE red eye, a dark open mouth. No gore."""
    global _FACE
    if _FACE is None:
        w, h = 1080, 1500
        cx, cy = w / 2, 700
        yy, xx = np.mgrid[0:h, 0:w]
        dd = (((xx - cx) / 300) ** 2 + ((yy - cy) / 420) ** 2)
        face = np.clip((1 - dd) * 6, 0, 1)
        shade = np.clip(1 - dd, 0, 1) ** 0.35
        rgb = np.array([212, 206, 204], np.float32) * (0.45 + 0.55 * shade[..., None])
        rgb *= (1 - 0.25 * noise(h, w, 40, 71, 10)[..., None])
        def dark(fn, col, blur=0, k=1.0):
            nonlocal rgb
            mm = np.asarray(mask_of((w, h), fn, blur), np.float32)[..., None] / 255
            rgb = rgb * (1 - mm * k) + np.array(col, np.float32) * mm * k
        dark(lambda d: d.ellipse([cx - 190, cy - 110, cx - 20, cy + 40], fill=255), (60, 40, 44), 30, 0.85)
        dark(lambda d: d.ellipse([cx - 230, cy + 60, cx - 60, cy + 260], fill=255), (120, 100, 104), 50, 0.5)
        dark(lambda d: d.ellipse([cx + 35, cy - 90, cx + 175, cy + 10], fill=255), (40, 30, 32), 18, 0.8)
        dark(lambda d: d.ellipse([cx - 140, cy - 70, cx - 60, cy - 10], fill=255), (12, 6, 8), 3)
        dark(lambda d: d.ellipse([cx - 60, cy + 190, cx + 60, cy + 300], fill=255), (14, 6, 8), 6)
        dark(lambda d: d.line([(cx - 30, cy + 30), (cx - 10, cy + 120), (cx + 20, cy + 125)], fill=255, width=8), (150, 120, 118), 6, 0.5)
        add_glow(rgb, gsp(70, (255, 30, 20), 1.3), cx - 100, cy - 40, 1.4)
        add_glow(rgb, gsp(16, (255, 220, 200), 1.0), cx - 100, cy - 40, 1.0)
        hair = Image.new("L", (w, h), 0); d = ImageDraw.Draw(hair)
        r = random.Random(21)
        d.ellipse([cx - 330, cy - 520, cx + 330, cy - 200], fill=255)
        for i in range(260):
            # leave a gap over the left eye and mouth; the right half of the face stays covered
            x0 = cx + (r.uniform(-310, -175) if r.random() < 0.35 else r.uniform(10, 310))
            y0 = cy - r.uniform(300, 460)
            ln = r.uniform(700, 1100)
            pts = [(x0 + math.sin(k * 0.5 + i) * 10 + (x0 - cx) * 0.25 * k / 12, y0 + ln * k / 12) for k in range(13)]
            d.line(pts, fill=255, width=r.choice([4, 6, 8, 10]), joint="curve")
        for i in range(220):
            x0 = cx + r.choice([-1, 1]) * r.uniform(290, 540); y0 = cy - r.uniform(380, 520); ln = r.uniform(800, 1200)
            pts = [(x0 + math.sin(k * 0.45 + i) * 14 + (x0 - cx) * 0.12 * k / 12, y0 + ln * k / 12) for k in range(13)]
            d.line(pts, fill=255, width=r.choice([6, 9, 12, 16]), joint="curve")
        hm = np.asarray(hair.filter(ImageFilter.GaussianBlur(1)), np.float32)[..., None] / 255
        rgb = rgb * (1 - hm) + np.array([6, 4, 6], np.float32) * hm
        alpha = np.clip(face + hm[..., 0], 0, 1)
        _FACE = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8), "RGBA")
    return _FACE


def face_slam(out, k, flash=0.0, grey=False):
    """k 0..1: the face rushes from far into the lens."""
    sp = face_sprite()
    if grey:
        g = sp.convert("LA").convert("RGBA")
        sp = g
    sc = 0.3 + 0.75 * k ** 1.6
    im = sp.resize((int(sp.width * sc), int(sp.height * sc)), Image.BILINEAR)
    out.alpha_composite(im, (int(W / 2 - im.width / 2), int(H * 0.45 - im.height * 0.47)))
    return out


# ============================================================ scenes - PART 1
def make_hook(D, caps):
    E = ext()
    hdr = series_header("SOUTH KOREA", "PART 1")
    t3 = caps[2][1]
    def f(t):
        cam = -40 + 50 * t / D
        k = ss(t, t3 - 0.2, t3 + 0.4)
        img = E.frame(t, cam=cam, lit="fig", lit_k=0.85 + 0.15 * math.sin(t * 9))
        push = 1.0 + 0.06 * t / D + 0.5 * k
        lx, ly = E.lit_xy[0] - 200 - cam * 0.45 + 20, E.lit_xy[1] + 30
        shake = 0.3 * ss(t, t3, t3 + 0.2) * (1 - ss(t, t3 + 0.3, t3 + 1.2))
        a = finish(img, t, VIG_H, push=push, cx=W / 2 * (1 - k) + lx * k, cy=H * 0.5 * (1 - k) + ly * k, shake=shake,
                   flash=0.45 if t3 < t < t3 + 0.07 else 0.0, flash_col=(255, 40, 30))
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_school(D, caps):
    E = ext()
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        cam = 30 - 60 * t / D
        def near(img, tt, P):
            x = 560 + P(1.0) - 40 * tt / D
            ph = int(tt * 6)
            paste_scaled(img, student_sil(ph, 0.0), x, 1660, 330)
        img = E.frame(t, cam=cam, lit="empty", lit_k=0.6 + 0.4 * ss(t, t3, t3 + 0.6), chars_near=near)
        k = ss(t, t3 - 0.4, D)
        lx, ly = E.lit_xy[0] - 200 - cam * 0.45 + 20, E.lit_xy[1] + 30
        a = finish(img, t, VIG_H, push=1.0 + 0.9 * k ** 1.3, cx=W / 2 * (1 - k) + lx * k, cy=H * 0.55 * (1 - k) + ly * k)
        out = to_img(a)
        tm = "10:55" if t < t2 + 1.5 else "10:56"
        put(out, clock_ui(tm, k=ss(t, t2 - 0.2, t2 + 0.3)))
        return to_arr(out)
    return f


_BUJ = None


def bujeok_hand():
    """A hand holding a bujeok: yellow paper talisman with red cinnabar characters and seal patterns, in red light."""
    global _BUJ
    if _BUJ is None:
        w, h = 900, 1150
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        px0, py0, px1, py1 = 290, 60, 610, 960
        paper = noise(py1 - py0, px1 - px0, 30, 61, 4) * 0.6 + noise(py1 - py0, px1 - px0, 4, 62) * 0.4
        yy = np.linspace(0, 1, py1 - py0)[:, None]
        pa = np.dstack([180 + 45 * paper - 30 * yy, 118 + 32 * paper - 20 * yy, 36 + 12 * paper, np.full(paper.shape, 255)]).astype(np.uint8)
        im.paste(Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8), "RGBA"), (px0, py0))
        ink = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(ink)
        INK = (160, 14, 12, 255)
        cf = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", 120)
        d.text((450, 170), "勅", font=cf, fill=INK, anchor="mm"); d.text((450, 300), "令", font=cf, fill=INK, anchor="mm")
        d.ellipse([395, 390, 505, 500], outline=INK, width=12); d.ellipse([435, 430, 465, 460], fill=INK)
        pts = [(450, 510)]
        for k in range(8):
            pts.append((450 + (40 if k % 2 == 0 else -40), 540 + k * 40))
        d.line(pts, fill=INK, width=12, joint="curve")
        for k, cxk in enumerate((390, 450, 510)):
            d.ellipse([cxk - 18, 860 - 18, cxk + 18, 860 + 18], outline=INK, width=8)
        d.rectangle([px0 + 16, py0 + 16, px1 - 16, py1 - 16], outline=INK, width=7)
        im.alpha_composite(ink.filter(ImageFilter.GaussianBlur(0.8)))
        hm = mask_of((w, h), lambda d: (d.rounded_rectangle([250, 760, 650, 1150], 140, fill=255),
                                         [d.rounded_rectangle([262 + k * 90, 700 + abs(k - 1.5) * 18, 342 + k * 90, 900], 40, fill=255) for k in range(4)],
                                         d.rounded_rectangle([560, 820, 730, 900], 40, fill=255)))
        im.alpha_composite(rim_sprite(hm, body=(52, 18, 18), glow_k=0.15, radius=60))
        _BUJ = im
    return _BUJ


def make_rule(D, caps):
    C = corridor()
    t2, t3 = caps[1][1], caps[2][1]
    sign_f = krfont(150); sign_e = font(INTER_SB, 64)
    sign = Image.new("RGBA", (520, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(sign)
    d.rounded_rectangle([4, 4, 516, 256], 26, fill=(26, 6, 8, 235), outline=(255, 60, 44, 255), width=6)
    d.text((170, 130), "4층", font=sign_f, fill=(255, 90, 70, 255), anchor="mm")
    d.text((400, 130), "4F", font=sign_e, fill=(240, 200, 190, 255), anchor="mm")
    sign_g = sign.filter(ImageFilter.GaussianBlur(14))
    bgcache = {}
    def bg():
        if "b" not in bgcache:
            bgcache["b"] = C.frame(0, tubes=(0.5, 0.5, 0.4, 0.4), fog_k=0.3).filter(ImageFilter.GaussianBlur(9))
        return bgcache["b"]
    bj = bujeok_hand()
    def f(t):
        img = bg().copy()
        a = to_arr(img) * (0.75 + 0.25 * (1 - ss(t, t3, t3 + 0.5)) + 0.05 * math.sin(t * 13))
        img = to_img(a)
        k1 = 1 - ss(t, t2 - 0.3, t2 + 0.2)
        if k1 > 0:
            img.alpha_composite(with_alpha(sign_g, k1), (280, 560)); img.alpha_composite(with_alpha(sign_g, k1), (280, 560))
            img.alpha_composite(with_alpha(sign, k1), (280, 560))
        k2 = ss(t, t2 - 0.2, t2 + 0.5)
        if k2 > 0:
            y = 1950 - 1300 * k2 + 20 * math.sin(t * 2)
            img.alpha_composite(with_alpha(bj, k2), (int(W / 2 - bj.width / 2), int(y)))
            # in the far blurred hallway: a pale shape (the viewer sees her first)
            gp = ghost_pale(int(t * 4))
            paste_scaled(img, gp.filter(ImageFilter.GaussianBlur(5)), 820, 1060, 300, 0.55 * ss(t, t3, t3 + 1.2))
        fog(img, t, 0.3, 1200, H, speed=20)
        a = finish(img, t, VIG_H, push=1.0 + 0.05 * t / D, cy=H * 0.5)
        return a
    return f


def make_hall(D, caps):
    C = corridor()
    t2, t3 = caps[1][1], caps[2][1]
    offs = [0.8, 1.6, 2.4, 3.2]
    def f(t):
        tubes = tuple(0.0 if t > o else (0.85 + 0.15 * math.sin(t * 60) * (t > o - 0.4)) for o in offs)
        def chars(img, tt):
            fx, fy, ph = C.depth_xy(0.86)
            k = ss(tt, t3 - 0.6, t3 + 0.4)
            if k > 0:
                paste_scaled(img, ghost_sil(int(tt * 5)), fx + 10, fy - 40, ph * 1.08, k)
            fx2, fy2, ph2 = C.depth_xy(0.14 + 0.12 * tt / D, x_off=-330)
            paste_scaled(img, student_sil(int(tt * 7), 0.0), fx2, fy2, ph2 * 0.8)
        img = C.frame(t, tubes=tubes, glow_k=0.35 + 0.65 * ss(t, 2.8, 4.0), chars=chars)
        a = finish(img, t, VIG_H, push=1.0 + 0.12 * ss(t, t3 - 0.5, D), cx=W / 2, cy=880)
        return a
    return f


def make_camera(D, caps):
    CC = cctv()
    t2, t3 = caps[1][1], caps[2][1]
    cuts = [0.0, t2 - 0.3, t2 + 1.6, t3 - 0.2, t3 + 1.0, D]
    gpos = [None, (330, 360, 70), (320, 470, 140), (300, 620, 230), (270, 860, 420)]
    def f(t):
        i = max(k for k in range(len(cuts) - 1) if t >= cuts[k])
        tt = t - cuts[i]
        sprites = []
        hx = 260 + 10 * math.sin(t); hy = 760 + 90 * t / D
        sprites.append((student_grey(int(t * 8)), hx, hy, 300 + 60 * t / D, 1.0))
        if gpos[i] is not None:
            gx, gy, gh = gpos[i]
            sprites.insert(0, (ghost_pale(int(t * 5), grey=True), gx, gy, gh, 1.0))
        gl = 1.0 if tt < 0.12 and i > 0 else 0.0
        return to_arr(CC.frame("hall", t, sprites, glitch=gl, clock=(22, 55, 31)))
    return f


def make_mistake(D, caps):
    C = corridor(True)
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        def chars(img, tt):
            fg_ = 0.55 - 0.3 * ss(tt, 0, t3)
            gx, gy, gh = C.depth_xy(fg_, x_off=80)
            paste_scaled(img, ghost_sil(int(tt * 6), arms=0.6 * ss(tt, t2, t3)), gx, gy - 40, gh * 1.1)
            hx, hy, hh = C.depth_xy(0.12, x_off=-420)
            lb = ss(tt, t3 - 0.1, t3 + 0.3)
            paste_scaled(img, student_sil(int(tt * 12), 1.0, look_back=lb), hx, hy + 60, hh * 0.95)
            # the talisman falls and lands on the floor
            if tt > 1.2:
                p = min(1, (tt - 1.2) / 0.6)
                x = 300 + 60 * p; y = 1200 + 520 * p ** 2
                tal = Image.new("RGBA", (60, 120), (190, 130, 40, 255))
                ImageDraw.Draw(tal).line([(30, 15), (20, 60), (40, 100)], fill=(170, 16, 14, 255), width=6)
                tal = tal.rotate(40 * p + 10 * math.sin(tt * 9), expand=True)
                img.alpha_composite(tal, (int(x), int(y)))
        img = C.frame(t, tubes=(0, 0, 0, 0), glow_k=1.0, flicker=0.3, chars=chars, fog_k=0.5)
        sc = t > t3 + 0.5
        if sc:
            out = to_img(to_arr(img) * 0.5)
            k = ss(t, t3 + 0.5, t3 + 0.85)
            face_slam(out, k)
            a = finish(out, t, VIG_H, shake=0.6 * (1 - ss(t, t3 + 0.5, D)), flash=0.5 if t < t3 + 0.58 else 0.0, flash_col=(255, 30, 20))
            return a
        return finish(img, t, VIG_H, push=1.0 + 0.04 * t / D, shake=0.15 * ss(t, t2, t2 + 0.2))
    return f


def make_cliff(D, caps):
    S_ = stall(); CC = cctv()
    t2, t3 = caps[1][1], caps[2][1]
    cut = D - 1.5
    def f(t):
        if t < cut:
            if t < t2:
                sx = -200 + (W / 2 + 200) * ss(t, 0.8, t2 + 0.2)
            else:
                sx = W / 2
            sk = 0.85 * ss(t, 0.6, 1.2)
            img = S_.frame(t, shadow_x=sx, shadow_k=sk, hem=ss(t, t2 + 0.6, t3) * 0.9, flicker=0.2 + 0.5 * ss(t, t3, cut))
            push = 1.0 + 0.1 * ss(t, t2, cut)
            return finish(img, t, VIG_H, push=push, cy=H * 0.6, shake=0.05)
        tt = t - cut
        x3, y3 = CC.stall3
        out = CC.frame("stalls", t, [(ghost_pale(int(t * 5), grey=True), x3 - 40, y3 + 70, 260, 1.0)],
                       cam="CAM 07  4F TOILET", glitch=1.0 if 0.55 < tt < 0.75 else 0.0, clock=(22, 57, 2))
        if tt > 0.62:
            k = ss(tt, 0.62, 0.95)
            out = face_slam(out, k)
            a = finish(out, t, VIG_H, shake=0.7, flash=0.6 if tt < 0.7 else 0.0, flash_col=(255, 30, 20))
            if tt > D - cut - 0.18:
                a *= 0
            return a
        return to_arr(out)
    return f


# ============================================================ scenes - PART 2
def make_recap(D, caps):
    E = ext(); S_ = stall()
    hdr = series_header("SOUTH KOREA", "PART 2")
    t2 = caps[1][1]
    def f(t):
        if t < t2 - 0.2:
            cam = -30 + 40 * t / D
            img = E.frame(t, cam=cam, lit="fig")
            lx, ly = E.lit_xy[0] - 200 - cam * 0.45 + 20, E.lit_xy[1] + 30
            k = ss(t, 0.8, t2)
            a = finish(img, t, VIG_H, push=1.0 + 0.6 * k, cx=W / 2 * (1 - k) + lx * k, cy=H * 0.5 * (1 - k) + ly * k)
        else:
            img = S_.frame(t, shadow_x=W / 2, shadow_k=0.85, hem=0.9, flicker=0.3)
            a = finish(img, t, VIG_H, push=1.05 + 0.05 * (t - t2), cy=H * 0.6)
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_stall(D, caps):
    S_ = stall()
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        hair = ss(t, t2 - 0.3, D - 0.4) ** 1.2
        img = S_.frame(t, shadow_x=W / 2, shadow_k=0.9, hem=0.9, hair=hair, flicker=0.25 + 0.4 * ss(t, t3, D))
        jolt = t > D - 0.45
        return finish(img, t, VIG_H, push=1.03 + 0.18 * ss(t, t2, D), cy=H * 0.72, shake=0.5 if jolt else 0.04,
                      flash=0.35 if D - 0.45 < t < D - 0.38 else 0.0, flash_col=(255, 30, 20))
    return f


_FLOOR = {}


def floor_pill(n):
    if n not in _FLOOR:
        _FLOOR[n] = pill(f"{n}F", font(INTER_SB, 72), outline=(255, 90, 70, 255), fill=(90, 10, 12, 235), h=118)
    return _FLOOR[n]


def make_escape(D, caps):
    t2, t3 = caps[1][1], caps[2][1]
    words = [t3, t3 + 1.0, t3 + 1.9]
    def f(t):
        fl_i = 0 if t < words[1] else (1 if t < words[2] else 2)
        C = corridor(fl_i % 2 == 1)
        def chars(img, tt):
            if tt < t3:
                gx, gy, gh = C.depth_xy(0.3 + 0.25 * ss(tt, t2, t3), x_off=160)
                paste_scaled(img, ghost_sil(int(tt * 5), arms=0.3), gx, gy - 60, gh * 1.1, 1 - 0.6 * ss(tt, t2 + 1.5, t3))
            hx, hy, hh = C.depth_xy(0.35 - 0.25 * ss(tt, t2, t3 + 2.6), x_off=-80)
            paste_scaled(img, student_sil(int(tt * 12), 1.0), hx, hy, hh)
        img = C.frame(t, tubes=(0, 0, 0, 0), glow_k=0.9 - 0.15 * fl_i, chars=chars, fog_k=0.5, flicker=0.15)
        a = finish(img, t, VIG_H, push=1.03 + 0.03 * math.sin(t * 2), shake=0.12 + 0.1 * ss(t, t3, D))
        out = to_img(a)
        if t >= words[0] - 0.1:
            n = 4 - fl_i - (1 if t >= words[0] else 0) + 1
            n = [3, 2, 1][fl_i] if t >= words[0] else 4
            n = 4 if t < words[0] else (3 if t < words[1] else 2)
            fp = floor_pill(n)
            out.alpha_composite(fp, (int(W / 2 - fp.width / 2), 140))
        else:
            fp = floor_pill(4)
            out.alpha_composite(with_alpha(fp, ss(t, 0.2, 0.6)), (int(W / 2 - fp.width / 2), 140))
        return to_arr(out)
    return f


def make_gate(D, caps):
    E = ext()
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        cam = 0
        open_ = 0.45 * (1 - ss(t, 0.5, t2 + 1.6))
        def near(img, tt, P):
            P1, P2 = E.P
            gx = P2 - 200 + 40
            push = ss(tt, 0.5, t2 + 1.6)
            paste_scaled(img, guard_sil(push), gx + 60, 1650, 420)
            hp = ss(tt, 0.3, t2 + 1.4); out_ = ss(tt, t2 + 1.4, t3)
            hx = 520 + 60 * hp - 700 * out_; hy = 1450 + 470 * hp + 300 * out_; hh = 260 + 520 * hp
            if out_ < 0.99:
                paste_scaled(img, student_sil(int(tt * 12), 1.0), hx, hy, hh)
        def mid(img, tt, P):
            k = ss(tt, t3 - 0.2, t3 + 0.8)
            if k > 0:
                paste_scaled(img, ghost_pale(int(tt * 4)), 700 + P(0.6), 1450, 190, k)
        img = E.frame(t, cam=cam, lit="empty", lit_k=1 - ss(t, t3, t3 + 0.6), chars_near=near, chars_mid=mid, gate_open=open_)
        a = to_arr(img)
        bx = E.P[1] - 200 + 40 + 60 + 230 * 0.4
        add_glow(a, gsp(300, (255, 220, 160), 2.2), bx - 160, 1250, 0.35)
        img = to_img(a)
        k = ss(t, t3 - 0.3, D)
        a = finish(img, t, VIG_H, push=1.12 + 0.6 * k, cx=W / 2 * (1 - k) + 700 * k, cy=1300 * (1 - k) + 1360 * k)
        out = to_img(a)
        tm = "10:59" if t < t2 + 1.5 else "11:00"
        put(out, clock_ui(tm, warn=True, k=1 - ss(t, t3 - 0.3, t3 + 0.2)))
        return to_arr(out)
    return f


def make_twist(D, caps):
    CC = cctv()
    t2, t3 = caps[1][1], caps[2][1]
    g0, g1, g2 = CC.gate_gap
    def f(t):
        sprites = []
        hp = ss(t, t2 - 0.6, t2 + 1.4)
        if t2 - 0.6 < t < t2 + 1.6:
            sprites.append((student_grey(int(t * 12), 1.0), 300 - 40 * hp, 560 + 420 * hp, 160 + 260 * hp, 1.0))
        gp = ss(t, t3 + 0.6, D - 1.2)
        if t > t3 + 0.4:
            sprites.append((ghost_pale(int(t * 4), grey=True), 290 - 20 * gp, 520 + 260 * gp, 170 + 150 * gp, 1.0))
        out = CC.frame("gate", t, sprites, cam="CAM 01  MAIN GATE", playback=True, clock=(22, 59, 41),
                       glitch=1.0 if D - 0.9 < t < D - 0.7 else 0.0)
        if t > D - 0.75:
            k = ss(t, D - 0.75, D - 0.45)
            out = face_slam(out, k)
            a = finish(out, t, VIG_H, shake=0.6, flash=0.55 if t < D - 0.68 else 0.0, flash_col=(255, 30, 20))
            if t > D - 0.12:
                a *= 0
            return a
        return to_arr(out)
    return f


# ============================================================ the bad ending: Ji-ho's bedroom
class Bedroom:
    def __init__(self):
        E = ext()
        a = np.zeros((H, W, 3), np.float32) + np.array([22, 6, 8], np.float32)
        yy = np.arange(H)[:, None, None]
        a *= (0.6 + 0.4 * np.exp(-((yy - 800) / 900.0) ** 2))
        img = to_img(a)
        WX0, WY0, WX1, WY1 = 150, 260, 930, 1280
        # the view: the blood moon over Seoul apartment towers
        view = E.sky.crop((560, 160, 1400, 1260)).resize((WX1 - WX0, WY1 - WY0), Image.BICUBIC)
        far = E.far.crop((560, 160, 1400, 1260)).resize((WX1 - WX0, WY1 - WY0), Image.BICUBIC)
        view.alpha_composite(far)
        d = ImageDraw.Draw(view)
        r = random.Random(17)
        for i in range(5):
            bx = 40 + i * 160 + r.uniform(-20, 20); bt = 520 + r.uniform(-80, 120)
            d.rectangle([bx, bt, bx + 120, 1100], fill=(14, 3, 5, 255))
            for wy in range(int(bt) + 20, 1080, 34):
                for wx in range(int(bx) + 12, int(bx) + 108, 24):
                    if r.random() < 0.07:
                        d.rectangle([wx, wy, wx + 12, wy + 10], fill=(150, 36, 26, 255))
        img.alpha_composite(view, (WX0, WY0))
        d = ImageDraw.Draw(img)
        d.rectangle([WX0, WY0, WX1, WY1], outline=(8, 2, 3, 255), width=28)
        d.rectangle([(WX0 + WX1) / 2 - 12, WY0, (WX0 + WX1) / 2 + 12, WY1], fill=(8, 2, 3, 255))
        d.rectangle([WX0 - 40, WY1, WX1 + 40, WY1 + 40], fill=(30, 9, 10, 255))
        # curtain on the right with folds
        cur = np.zeros((H, 260, 4), np.float32)
        xx = np.arange(260)[None, :]
        fold = 0.6 + 0.4 * np.sin(xx / 18.0) ** 2
        cur[..., 0] = 60 * fold; cur[..., 1] = 14 * fold; cur[..., 2] = 16 * fold; cur[..., 3] = 255
        cur[:, :, :3] *= (0.5 + 0.5 * np.exp(-((np.arange(260)[None, :] - 40) / 120.0) ** 2))[..., None]
        img.alpha_composite(Image.fromarray(cur.astype(np.uint8), "RGBA").crop((0, 180, 260, 1700)), (880, 180))
        # desk with books on the left, floor
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1700, W, H], fill=(16, 5, 6, 255))
        d.rectangle([0, 1420, 260, 1450], fill=(12, 3, 4, 255)); d.rectangle([20, 1450, 50, 1720], fill=(10, 3, 4, 255))
        for k in range(5):
            d.rectangle([40 + k * 34, 1300 + (k % 2) * 20, 68 + k * 34, 1420], fill=(18 + k * 4, 5, 6, 255))
        a = to_arr(img)
        # red moonlight spilling on the floor + glow round the window
        sp = np.asarray(mask_of((W, H), lambda d: d.polygon([(WX0, WY1 + 40), (WX1, WY1 + 40), (W + 200, H), (-100, H)], fill=255), 60), np.float32)[..., None] / 255
        a += sp * np.array([150, 18, 14], np.float32) * 0.55
        add_glow(a, gsp(600, (200, 30, 20), 2.0), (WX0 + WX1) / 2, 700, 0.35)
        self.bg = to_img(a)
        self.WIN = (WX0, WY0, WX1, WY1)
        # Ji-ho from behind, sitting on a chair, facing the window
        def jiho(turn):
            def fn(d):
                cx, sy = 540, 1150
                d.polygon([(cx - 150, sy), (cx + 150, sy), (cx + 135, sy + 470), (cx - 135, sy + 470)], fill=255)
                d.rounded_rectangle([cx - 150, sy - 12, cx + 150, sy + 120], 60, fill=255)
                d.rectangle([cx - 30, sy - 80, cx + 30, sy + 10], fill=255)
                hx = cx + 14 * turn
                d.ellipse([hx - 80, sy - 270, hx + 80, sy - 70], fill=255)
                d.chord([hx - 88, sy - 288, hx + 88, sy - 140], 180, 360, fill=255)
                if turn > 0.3:
                    d.polygon([(hx - 74, sy - 190), (hx - 104, sy - 166), (hx - 74, sy - 152)], fill=255)
                d.rounded_rectangle([cx - 190, sy + 280, cx + 190, sy + 720], 40, fill=255)     # chair back
                d.rectangle([cx - 170, sy + 700, cx - 140, H], fill=255); d.rectangle([cx + 140, sy + 700, cx + 170, H], fill=255)
            return rim_sprite(mask_of((W, H), fn), glow_k=0.25, radius=60)
        self.jiho = [jiho(0.0), jiho(1.0)]


_BED = None


def bedroom():
    global _BED
    if _BED is None:
        _BED = Bedroom()
    return _BED


_SNL = None


def never_left():
    global _SNL
    if _SNL is None:
        a = text_img("SHE NEVER", font(LORA, 120, "Bold"), fill=(255, 230, 215, 255), glow=(220, 20, 16, 255), pad=24)
        b = text_img("LEFT HIM.", font(LORA, 120, "Bold"), fill=(255, 120, 95, 255), glow=(220, 20, 16, 255), pad=24)
        im = Image.new("RGBA", (max(a.width, b.width), a.height + b.height - 40), (0, 0, 0, 0))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([30, 30, im.width - 30, im.height - 30], 60, fill=(0, 0, 0, 215))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(26)))
        im.alpha_composite(a, ((im.width - a.width) // 2, 0)); im.alpha_composite(b, ((im.width - b.width) // 2, a.height - 40))
        _SNL = im
    return _SNL


def make_home(D, caps):
    B = bedroom()
    t2, t3 = caps[1][1], caps[2][1]
    turn_t = D - 2.4
    def f(t):
        img = B.bg.copy()
        k = ss(t, t2 - 0.4, t2 + 1.6)
        if k > 0:
            sw = 4 * math.sin(t * 0.9)
            paste_scaled(img, ghost_sil(int(t * 3), arms=0.5), 560 + sw, H + 30, 1380, k)
        turned = t > turn_t
        img.alpha_composite(B.jiho[1 if turned else 0])
        if turned:
            a = to_arr(img)
            add_glow(a, gsp(30, (255, 40, 30), 1.3), 540 + 14 - 50, 1150 - 175, 1.3 * ss(t, turn_t, turn_t + 0.25))
            add_glow(a, gsp(8, (255, 220, 200), 1.0), 540 + 14 - 50, 1150 - 175, 1.0)
            img = to_img(a)
        fog(img, t, 0.3, 1400, H, speed=8)
        push = 1.0 + 0.12 * t / D + 0.25 * ss(t, turn_t, turn_t + 0.6)
        a = finish(img, t, VIG_H, push=push, cy=1000 - 80 * ss(t, turn_t, turn_t + 0.6),
                   flash=0.45 if turn_t < t < turn_t + 0.07 else 0.0, flash_col=(255, 30, 20), shake=0.3 * ss(t, turn_t, turn_t + 0.1) * (1 - ss(t, turn_t + 0.3, turn_t + 1.0)))
        if turned:
            out = to_img(a)
            sn = never_left()
            kk = ss(t, turn_t + 0.5, turn_t + 1.0)
            out.alpha_composite(with_alpha(sn, kk), (int(W / 2 - sn.width / 2), 330))
            return to_arr(out)
        return a
    return f


def make_explain(D, caps):
    E = ext()
    title = text_img("CHEONYEO GWISHIN", font(LORA, 96, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("처녀귀신  ·  Korea's maiden ghost", krfont(40), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("Died young and unmarried", pf, fill=(110, 20, 24, 235), h=80),
             pill("Full of HAN: deep sorrow", pf, fill=(110, 20, 24, 235), h=80),
             pill("White mourning hanbok (sobok)", pf, fill=(110, 20, 24, 235), h=80),
             pill("Hair down: only wives tied it up", pf, fill=(110, 20, 24, 235), h=80)]
    ts = [caps[0][1] + 1.2, caps[0][1] + 2.6, caps[0][1] + 4.2, caps[1][1] + 0.3]
    def f(t):
        def mid(img, tt, P):
            paste_scaled(img, ghost_pale(int(tt * 4)), 760 + P(0.6), 1560, 700)
        img = E.frame(t, cam=-20 + 20 * t / D, lit="empty", chars_mid=mid, fog_k=0.4)
        a = finish(img, t, vig=VIG_H)
        out = to_img(a * 0.72)
        fw = flag_wave(t, 150)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 70))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 170))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 320))
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.2, tt + 0.3)
            if k > 0:
                cc = c if c.width <= W - 40 else c.resize((W - 40, int(c.height * (W - 40) / c.width)), Image.LANCZOS)
                out.alpha_composite(with_alpha(cc, k), (int(W / 2 - cc.width / 2), int(430 + i * 96 + 14 * (1 - k))))
        return to_arr(out)
    return f


def make_outro(D, caps):
    E = ext()
    q = text_img("Would YOU have", font(LORA, 96, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("looked back?", font(LORA, 104, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Look back", (120, 25, 25, 235)), ("Eyes down", (60, 40, 40, 235)), ("Grab the talisman", (140, 70, 20, 235)), ("RUN!", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    def f(t):
        img = E.frame(t, cam=0, lit="fig", lit_k=0.9)
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
