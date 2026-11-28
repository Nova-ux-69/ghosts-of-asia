"""Ep18 White Lady of Balete Drive - FOUND FOOTAGE style: a taxi dashcam (CAM 1) and a night-vision cabin camera (CAM 2).
Worlds are drawn in 2.1D, then a camera layer adds wide-angle lens distortion, sensor noise, colour fringing,
scan lines, a REC / timestamp / GPS display and glitches. make_<id>(D, caps) -> f(t) -> float RGB (H, W, 3)."""
import os, sys, math
os.environ["STYLE"] = "flat21"
_EP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_EP, "..", "ep07b-myanmar-2p1d")); sys.path.insert(0, os.path.join(_EP, "..", "..", "toolkit"))
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from art_v import W, H, font, text_img, with_alpha, ease, glow_sprite, add_glow, fog_texture, INTER_SB, INTER_M, LORA
from depth import dof
import demo25_myanmar as D5
from scenes_v import series_header, header_layers, pill
from scenes_ep7b import ss, shade, to_arr

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def mono(sz, bold=False):
    return ImageFont.truetype(MONO_B if bold and os.path.exists(MONO_B) else MONO, sz)

HOR = 780          # horizon line of the dashcam
FOC = 900          # focal length in px
CAMH = 1.3         # camera height (m)
CX = W / 2

# ============================================================ flag + header
def ph_flag(w=170):
    h = w // 2; s = 3
    im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w * s, h * s // 2], fill=(0, 56, 168, 255))
    d.rectangle([0, h * s // 2, w * s, h * s], fill=(206, 17, 38, 255))
    tw = h * s * 0.866
    d.polygon([(0, 0), (tw, h * s / 2), (0, h * s)], fill=(255, 255, 255, 255))
    cx, cy, r = tw * 0.36, h * s / 2, h * s * 0.11
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(252, 209, 22, 255))
    for k in range(8):
        a = k * math.pi / 4
        d.line([(cx + math.cos(a) * r * 1.2, cy + math.sin(a) * r * 1.2), (cx + math.cos(a) * r * 2.0, cy + math.sin(a) * r * 2.0)], fill=(252, 209, 22, 255), width=int(r * 0.35))
    for (sx, sy) in ((tw * 0.1, h * s * 0.12), (tw * 0.1, h * s * 0.88), (tw * 0.82, h * s * 0.5)):
        d.ellipse([sx - r * 0.35, sy - r * 0.35, sx + r * 0.35, sy + r * 0.35], fill=(252, 209, 22, 255))
    return im.resize((w, h), Image.LANCZOS)


FLAG = ph_flag(170)


def header(img, t, part):
    hdr = series_header("PHILIPPINES", part)
    for im, (x, y), al in header_layers(hdr, t):
        if al > 0.01:
            img.alpha_composite(with_alpha(im, al), (int(x), int(y)))
    img.alpha_composite(FLAG, (int(W / 2 - FLAG.width / 2), 70))


# ============================================================ camera layer
_mx = None
def _maps():
    global _mx
    if _mx is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (W / 2)
        r2 = nx * nx + ny * ny
        k = 1 + 0.10 * r2 + 0.02 * r2 * r2                  # barrel distortion (wide dashcam lens)
        sx = W / 2 + nx * (W / 2) / k * 1.06; sy = H / 2 + ny * (W / 2) / k * 1.06
        _mx = (sx.astype(np.float32), sy.astype(np.float32))
    return _mx


VIG = None
def _vig():
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        VIG = np.clip(1.15 - d ** 2.2, 0.15, 1.0)[..., None].astype(np.float32)
    return VIG


NOISE = [np.random.default_rng(i).normal(0, 1, (H // 2, W // 2, 1)).astype(np.float32) for i in range(8)]
SCAN = (1 - 0.08 * ((np.arange(H) % 4) < 2))[:, None, None].astype(np.float32)


def osd(img, t, cam, clock0, speed=None, gps=True, rec=True, extra=None):
    d = ImageDraw.Draw(img)
    f = mono(34, True); f2 = mono(30)
    sec = clock0 + t
    hh, mm, s_ = int(sec // 3600) % 24, int(sec // 60) % 60, int(sec) % 60
    stamp = f"2026-11-28  {hh:02d}:{mm:02d}:{s_:02d}"
    d.text((W - 40, 40), stamp, font=f, fill=(240, 240, 230, 235), anchor="ra")
    if rec and int(t * 2) % 2 == 0:
        d.ellipse([40, 46, 68, 74], fill=(255, 30, 30, 255))
    d.text((84, 40), "REC", font=f, fill=(240, 240, 230, 235))
    d.text((40, 1250), cam, font=f2, fill=(240, 240, 230, 215))
    if speed is not None:
        d.text((W - 40, 1250), f"{int(speed):3d} km/h", font=f2, fill=(240, 240, 230, 215), anchor="ra")
    if gps:
        d.text((40, 96), "N14.6172  E121.0268", font=mono(26), fill=(220, 220, 210, 190))
    if extra:
        d.text((W - 40, 96), extra, font=mono(26), fill=(255, 210, 120, 220), anchor="ra")


def camera(img, t, kind="dash", glitch=0.0, clock0=2 * 3600 + 45 * 60 + 10, speed=None, cam=None, extra=None, rec=True):
    """img: RGBA/RGB PIL frame of the world. Returns float array with the found-footage look and OSD."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    mx, my = _maps()
    a = cv2.remap(a, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if kind == "nv":    # night vision: luminance -> green phosphor, bloom
        lum = a @ np.array([0.3, 0.59, 0.11], np.float32)
        lum = np.clip(lum * 1.15 + 6, 0, 255)
        bl = cv2.GaussianBlur(lum, (0, 0), 14)
        lum = np.clip(lum * 0.9 + 0.3 * bl, 0, 255)
        a = np.stack([lum * 0.45, lum * 1.0, lum * 0.5], -1)
        nz = 22
    else:               # cheap dashcam sensor: cool cast, crushed blacks, sodium highlights
        a = a * np.array([0.92, 0.98, 1.08], np.float32)
        a = np.clip((a - 8) * 1.08, 0, 255)
        nz = 11
    n = cv2.resize(NOISE[int(t * 30) % 8], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    a = a + n * nz
    a[..., 0] = np.roll(a[..., 0], 3, axis=1)             # colour fringing
    a[..., 2] = np.roll(a[..., 2], -3, axis=1)
    a = a * SCAN * _vig()
    if glitch > 0:
        rng = np.random.default_rng(int(t * 30))
        for _ in range(int(3 + 10 * glitch)):
            y0 = int(rng.uniform(0, H - 60)); hh = int(rng.uniform(8, 60 * glitch + 10))
            a[y0:y0 + hh] = np.roll(a[y0:y0 + hh], int(rng.uniform(-80, 80) * glitch), axis=1)
        if rng.random() < glitch * 0.5:
            a = a * 0.4 + rng.normal(0, 60, (H, 1, 1)).astype(np.float32)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    osd(out, t, cam or ("CAM 1  FRONT" if kind == "dash" else "CAM 2  CABIN  IR"), clock0, speed, extra=extra, rec=rec)
    return to_arr(out)


def static(t, k=1.0):
    rng = np.random.default_rng(int(t * 30) + 7)
    a = rng.uniform(0, 255, (H // 4, W // 4, 1)).astype(np.float32)
    a = cv2.resize(a, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    a = np.repeat(a, 3, axis=2) * k * SCAN
    return a


# ============================================================ the road (CAM 1)
_SPR = {}
def sprites():
    if not _SPR:
        _SPR["tree"] = D5.banyan()                       # balete = strangler fig, same family as the banyan
        def pole(d, s):
            d.rectangle([40 * s, 0, 56 * s, 1000 * s], fill=255)
            d.line([(48 * s, 10 * s), (180 * s, 0)], fill=255, width=int(12 * s))
        _SPR["lamp"] = shade(pole, (220, 1000), (60, 56, 58), 8)
        _SPR["lady"] = D5.ghost()
        _SPR["glow"] = glow_sprite(300, (255, 170, 80), 1.7)
        _SPR["hl"] = glow_sprite(700, (255, 245, 220), 1.4)
        # road sign + barrier
        sg = Image.new("RGBA", (560, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(sg)
        d.rounded_rectangle([0, 0, 559, 199], 16, fill=(20, 110, 60, 255), outline=(240, 240, 240, 255), width=8)
        d.text((280, 100), "BALETE DR.", font=font(INTER_SB, 92), fill=(245, 245, 245, 255), anchor="mm")
        _SPR["sign"] = sg
        br = Image.new("RGBA", (900, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(br)
        for k in range(9):
            d.polygon([(k * 100, 40), (k * 100 + 50, 40), (k * 100 + 100, 140), (k * 100 + 50, 140)], fill=(240, 120, 20, 255))
        d.rectangle([0, 40, 899, 140], outline=(240, 240, 240, 255), width=6)
        d.rectangle([30, 140, 50, 260], fill=(200, 200, 200, 255)); d.rectangle([850, 140, 870, 260], fill=(200, 200, 200, 255))
        d.text((450, 205), "ROAD CLOSED", font=font(INTER_SB, 48), fill=(255, 230, 60, 255), anchor="mm")
        _SPR["barrier"] = br
        y = np.linspace(0, 1, H)[:, None]
        sky = np.array([4, 4, 8]) * (1 - y) + np.array([60, 36, 30]) * np.clip(y / (HOR / H), 0, 1) ** 3
        _SPR["sky"] = Image.fromarray(np.clip(np.broadcast_to(sky[:, None, :], (H, W, 3)), 0, 255).astype(np.uint8)).convert("RGBA")
    return _SPR


def proj(X, Y, z):
    """World (X right, Y up, z forward, metres) -> screen."""
    return CX + FOC * X / z, HOR + FOC * (CAMH - Y) / z


def put_world(img, spr, X, z, height_m, anchor_bottom=True, blur=0.0, dark=1.0):
    if z < 1.2:
        return
    x, y = proj(X, 0, z)
    hpx = FOC * height_m / z
    sc = hpx / spr.height
    w, h = max(1, int(spr.width * sc)), max(1, int(spr.height * sc))
    if w > 4000 or h > 6000:
        return
    s = spr.resize((w, h), Image.BILINEAR)
    if dark < 1:
        a = np.asarray(s, np.float32).copy(); a[..., :3] *= dark; s = Image.fromarray(a.astype(np.uint8), "RGBA")
    if blur > 0.3:
        s = s.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(s, (int(x - w / 2), int(y - h)))


def road(t, dist, lady_z=None, lady_wave=0.0, sign_z=None, barrier_z=None, balete=True, lamps_on=1.0, steer=0.0, flick=1.0):
    """dist: metres travelled. Returns RGBA PIL frame of the road ahead at night."""
    S = sprites()
    img = S["sky"].copy()
    d = ImageDraw.Draw(img)
    # city glow + far skyline
    rng = np.random.default_rng(3)
    for k in range(40):
        x = rng.uniform(0, W); hh = rng.uniform(20, 120)
        d.rectangle([x, HOR - hh, x + rng.uniform(30, 90), HOR], fill=(14, 12, 16, 255))
    # road surface
    zs = np.linspace(2.0, 160, 160)
    for i in range(len(zs) - 1):
        z0, z1 = zs[i], zs[i + 1]
        xl0, y0 = proj(-3.8 + steer, 0, z0); xr0, _ = proj(3.8 + steer, 0, z0)
        xl1, y1 = proj(-3.8 + steer, 0, z1); xr1, _ = proj(3.8 + steer, 0, z1)
        sh = int(14 + 22 * math.exp(-z0 / 14) * flick)
        d.polygon([(xl0, y0), (xr0, y0), (xr1, y1), (xl1, y1)], fill=(sh, sh - 2, sh + 2, 255))
        # verges
        xa, _ = proj(-14 + steer, 0, z0); xb, _ = proj(-14 + steer, 0, z1)
        d.polygon([(xa, y0), (xl0, y0), (xl1, y1), (xb, y1)], fill=(14, 16, 12, 255))
        xa, _ = proj(14 + steer, 0, z0); xb, _ = proj(14 + steer, 0, z1)
        d.polygon([(xr0, y0), (xa, y0), (xb, y1), (xr1, y1)], fill=(14, 16, 12, 255))
    # centre dashes and kerb lines
    off = dist % 9.0
    for k in range(18):
        z0 = 2 + k * 9 - off
        if z0 < 2:
            continue
        a0 = proj(-0.08 + steer, 0, z0); a1 = proj(-0.08 + steer, 0, z0 + 3)
        b0 = proj(0.08 + steer, 0, z0); b1 = proj(0.08 + steer, 0, z0 + 3)
        c = int(150 * min(1, 30 / z0) * flick) + 30
        d.polygon([a0, b0, b1, a1], fill=(c, c, c - 20, 255))
    # objects far -> near
    objs = []
    for side in (-1, 1):
        for k in range(12):
            z = (k * 22 + (11 if side > 0 else 0)) - dist % 22 + 3
            if balete:
                objs.append((z, "tree", side * (5.2 + (k % 3) * 0.8), 20 + (k % 4) * 3))
        for k in range(5):
            z = k * 45 + 20 - dist % 45 + 3
            objs.append((z, "lamp", side * 4.6, 7.5))
    if lady_z is not None:
        objs.append((lady_z, "lady", 3.6, 1.75))
        objs.append((lady_z + 1.5, "tree", 6.5, 30))           # the biggest balete
    if sign_z is not None:
        objs.append((sign_z, "sign", 4.4, 2.6))
    if barrier_z is not None:
        objs.append((barrier_z, "barrier", 0.0, 1.4))
    glow_pts = []
    for z, kind, X, hm in sorted(objs, key=lambda o: -o[0]):
        if z < 1.5 or z > 170:
            continue
        if kind == "tree":
            put_world(img, S["tree"], X + steer, z, hm, dark=0.55 + 0.45 * math.exp(-z / 25) * flick)
        elif kind == "lamp":
            put_world(img, S["lamp"], X + steer, z, hm)
            lx, ly = proj(X + steer + (-0.8 if X > 0 else 0.8) * 0, hm * 0.98, z)
            glow_pts.append((lx + (FOC * 1.0 / z) * (-1 if X > 0 else 1) * 0.0, ly, z))
        elif kind == "lady":
            put_world(img, S["lady"], X + steer, z, hm, dark=0.7 + 0.3 * flick)
            if lady_wave > 0:   # a raised arm waving slowly
                x, y = proj(X + steer, 1.45, z)
                L = FOC * 0.55 / z; a = -1.9 + 0.35 * math.sin(t * 3.0)
                d2 = ImageDraw.Draw(img)
                d2.line([(x - FOC * 0.12 / z, y), (x - FOC * 0.12 / z + math.cos(a) * L, y + math.sin(a) * L)], fill=(200, 205, 200, int(255 * lady_wave)), width=max(2, int(FOC * 0.07 / z)))
        elif kind == "sign":
            x, y = proj(X + steer, 2.6, z); sc = FOC * 0.9 / z / 200
            s = S["sign"].resize((max(1, int(560 * sc)), max(1, int(200 * sc))), Image.BILINEAR)
            img.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2)))
        elif kind == "barrier":
            put_world(img, S["barrier"], X + steer, z, hm)
    a = to_arr(img)
    for lx, ly, z in glow_pts:
        add_glow(a, S["glow"], lx, ly, min(1.2, 9 / z) * lamps_on)
    # headlights on the road
    add_glow(a, S["hl"], CX, HOR + 470, 0.22 * flick)
    add_glow(a, S["hl"], CX, HOR + 260, 0.10 * flick)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    # car bonnet at the bottom with a dull reflection
    d = ImageDraw.Draw(img)
    d.ellipse([-900, 1700, W + 900, 2900], fill=(8, 8, 10, 255))
    d.arc([-900, 1700, W + 900, 2900], 235, 305, fill=(55, 55, 65, 255), width=5)
    return img


# ============================================================ the cabin (CAM 2, night vision)
_CAB = {}
def cabin_base():
    if "bg" not in _CAB:
        img = Image.new("RGBA", (W, H), (20, 20, 22, 255)); d = ImageDraw.Draw(img)
        d.polygon([(120, 380), (960, 380), (1020, 760), (60, 760)], fill=(105, 105, 112, 255))      # rear window (lit by the street)
        def seat(d_, s):
            d_.rounded_rectangle([60 * s, 760 * s, 1020 * s, 1250 * s], int(60 * s), fill=255)
        _CAB["seat"] = shade(seat, (W, H), (90, 86, 84), 60)
        def rests(d_, s):
            for x in (230, 850):
                d_.rounded_rectangle([(x - 90) * s, 640 * s, (x + 90) * s, 800 * s], int(40 * s), fill=255)
        _CAB["rests"] = shade(rests, (W, H), (100, 96, 94), 30)
        def driver(d_, s):      # Joel: back of head and shoulder in the right foreground
            d_.ellipse([800 * s, 980 * s, 1140 * s, 1380 * s], fill=255)
            d_.rounded_rectangle([640 * s, 1300 * s, 1300 * s, 2000 * s], int(160 * s), fill=255)
        _CAB["driver"] = shade(driver, (W, H), (70, 66, 64), 120)
        _CAB["bg"] = img
        ld = D5.ghost()
        a = np.asarray(ld.crop((0, 0, ld.width, 760)), np.float32).copy()   # head + upper body, seated
        hair = (a[..., :3].max(-1) < 60) & (a[..., 3] > 0)
        a[hair, :3] = np.array([58, 58, 64], np.float32) + a[hair, :3] * 0.6     # hair catches a little IR light
        face = (a[..., :3].mean(-1) > 150) & (np.arange(760)[:, None] < 360)
        a[face, :3] = np.minimum(255, a[face, :3] * 1.15)
        _CAB["lady"] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    return _CAB


def cabin(t, lady=0.0, lady_lean=0.0, flower=False, window_lights=True, lady_scale=1.0, eyes=1.0):
    C = cabin_base()
    img = C["bg"].copy()
    if window_lights:   # street lights sliding across the rear window
        a = to_arr(img)
        for k in range(3):
            x = (k * 420 + t * 600) % 1400 - 200
            add_glow(a, glow_sprite(160, (255, 200, 140), 1.6), x, 560, 0.5)
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        d = ImageDraw.Draw(img)
        d.polygon([(0, 0), (W, 0), (W, 380), (0, 380)], fill=(20, 20, 22, 255))
        d.polygon([(0, 380), (120, 380), (60, 760), (0, 760)], fill=(20, 20, 22, 255))
        d.polygon([(960, 380), (W, 380), (W, 760), (1020, 760)], fill=(20, 20, 22, 255))
    img.alpha_composite(C["rests"]); img.alpha_composite(C["seat"])
    if flower:   # a small white flower on the wet seat
        d = ImageDraw.Draw(img)
        for k in range(5):
            a_ = k * 2 * math.pi / 5
            d.ellipse([470 + math.cos(a_) * 22 - 18, 1000 + math.sin(a_) * 22 - 14, 470 + math.cos(a_) * 22 + 18, 1000 + math.sin(a_) * 22 + 14], fill=(245, 245, 240, 255))
        d.ellipse([458, 988, 482, 1012], fill=(230, 220, 160, 255))
        d.ellipse([380, 1030, 600, 1090], outline=(120, 130, 140, 180), width=3)
    if lady > 0:
        ld = C["lady"]
        sc = 1.3 * lady_scale * (1 + 0.35 * lady_lean)
        s = ld.resize((int(ld.width * sc), int(ld.height * sc)), Image.LANCZOS)
        x = 540 - s.width / 2 + 60 * lady_lean; y = 1060 - s.height * 0.95 + 120 * lady_lean
        img.alpha_composite(with_alpha(s, lady), (int(x), int(y)))
        if eyes > 0:   # IR eye-shine
            for dx in (-27, 27):
                ex, ey = x + (310 + dx) * sc, y + 248 * sc
                a = to_arr(img); add_glow(a, glow_sprite(int(9 * sc) + 4, (255, 255, 255), 1.0), ex, ey, 2.2 * eyes * lady)
                img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    img.alpha_composite(C["driver"])
    return img



def zoom_to(a, x, y, z):
    """Digital zoom of the recorded frame (like scrubbing found footage)."""
    if z <= 1.001:
        return a
    cw, ch = W / z, H / z
    x0 = min(max(0, x - cw / 2), W - cw); y0 = min(max(0, y - ch / 2), H - ch)
    return cv2.resize(np.ascontiguousarray(a[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]), (W, H))

# ============================================================ scenes - part 1
def make_hook(D, caps):
    t2 = caps[1][1]
    def f(t):
        if t < 0.8 or (t2 - 0.15 < t < t2 + 0.1):
            a = static(t)
        else:
            img = road(t, 14 * t, lady_z=40 - 4 * t, lady_wave=0.0)
            a = camera(img, t, "dash", glitch=0.25 * (math.sin(t * 7) > 0.92), speed=38, extra="FILE 0247.MP4")
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        lbl = text_img("RECOVERED FOOTAGE", font(INTER_SB, 54), fill=(255, 60, 50, 255), pad=10)
        if 0.8 < t < 4.0 and int(t * 3) % 2 == 0:
            out.alpha_composite(lbl, (int(W / 2 - lbl.width / 2), 520))
        header(out, t, "PART 1")
        return to_arr(out)
    return f


def make_shift(D, caps):
    def f(t):
        img = road(t, 40 + 16 * t, balete=False)
        return camera(img, t, "dash", speed=46, clock0=2 * 3600 + 45 * 60 + 1)
    return f


def make_rule(D, caps):
    t2, t3 = caps[1][1], caps[2][1]
    def f(t):
        img = cabin(t, lady=0.0)
        a = camera(img, t, "nv", clock0=2 * 3600 + 45 * 60 + 9)
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        rules = ["DRIVERS' RULES:", "1. 12AM-3AM: NO BALETE DRIVE", "2. NEVER PICK UP A LADY IN WHITE"]
        d = ImageDraw.Draw(out)
        y = 430
        for i, (r, tt) in enumerate(zip(rules, (0.2, t2, t3))):
            k = ss(t, tt, tt + 0.3)
            if k > 0:
                box = text_img(r, mono(44, True), fill=(255, 80, 70, int(255 * k)) if i else (255, 230, 200, int(255 * k)), pad=12)
                out.alpha_composite(box, (int(W / 2 - box.width / 2), y)); y += 90
        return to_arr(out)
    return f


def make_shortcut(D, caps):
    t2 = caps[1][1]
    def f(t):
        if t < t2:
            img = road(t, 80 + 8 * t, barrier_z=max(6, 22 - 6 * t), balete=False)
            return camera(img, t, "dash", speed=max(5, 30 - 12 * t), clock0=2 * 3600 + 46 * 60)
        u = t - t2
        img = road(t, 100 + 10 * u, sign_z=max(3, 14 - 8 * u), steer=-1.5 * math.sin(min(1, u / 1.5) * math.pi / 2) + 1.5)
        return camera(img, t, "dash", speed=24, clock0=2 * 3600 + 46 * 60, extra="BALETE DR.")
    return f


def make_lady(D, caps):
    t2 = caps[1][1]
    def f(t):
        z = 34 - 3.6 * t
        flick = 0.6 + 0.4 * (math.sin(t * 23) > -0.7)
        img = road(t, 200 + 3.6 * t, lady_z=z, lady_wave=1.0, flick=flick)
        a = camera(img, t, "dash", speed=41, glitch=0.15 if z < 9 else 0, clock0=2 * 3600 + 47 * 60 + 2, extra="BALETE DR.")
        lx, ly = proj(3.6, 1.0, z)
        return zoom_to(a, lx, ly, 1 + 1.6 * ss(t, 0.6, 3.5))
    return f


def make_again(D, caps):
    def f(t):
        z = 30 - 3.6 * t
        img = road(t, 200 + 3.6 * t, lady_z=z, lady_wave=1.0, flick=0.7 + 0.3 * (math.sin(t * 31) > -0.4))
        g = 0.6 if t < 0.25 else (0.3 if 2.0 < t < 2.2 else 0.0)
        a = camera(img, t, "dash", speed=41, glitch=g, clock0=2 * 3600 + 47 * 60 + 2, extra="BALETE DR.")   # same clock = a loop
        lx, ly = proj(3.6, 1.0, z)
        return zoom_to(a, lx, ly, 2.0 + 0.6 * ss(t, 0.3, D))
    return f


def make_cliff(D, caps):
    t2, t3, t4 = caps[1][1], caps[2][1], caps[3][1]
    def f(t):
        if t < t2 - 0.1:
            img = road(t, 400 + 20 * t, flick=0.8)
            return camera(img, t, "dash", speed=62 + 8 * t, clock0=2 * 3600 + 49 * 60 + 30, extra="BALETE DR.")
        if t < t2 + 0.35:
            return static(t, 0.8)
        lady = ss(t, t3 - 0.2, t3 + 0.9)
        lean = ss(t, t4 + 0.4, t4 + 1.4)
        img = cabin(t, lady=lady, lady_lean=lean)
        g = 0.5 if t3 - 0.1 < t < t3 + 0.15 else 0.0
        a = camera(img, t, "nv", glitch=g, clock0=2 * 3600 + 49 * 60 + 33)
        # final: digital zoom on her face, freeze + flash
        if t > t4 + 0.4:
            z = 1 + 1.6 * ss(t, t4 + 0.4, t4 + 1.4)
            cw, ch = W / z, H / z; x0 = W / 2 - cw / 2; y0 = 640 - ch / 2
            a = cv2.resize(a[int(max(0, y0)):int(max(0, y0) + ch), int(x0):int(x0 + cw)], (W, H))
        if t4 + 1.4 <= t < t4 + 1.5:
            a = a * 0.2 + np.array([255, 255, 255], np.float32) * 0.8
        if t > D - 0.45:
            a = a * 0
        return a
    return f


# ============================================================ scenes - part 2
def make_recap(D, caps):
    def f(t):
        img = cabin(t, lady=1.0, lady_lean=0.3)
        a = camera(img, t, "nv", glitch=0.2 * (math.sin(t * 9) > 0.8), clock0=2 * 3600 + 49 * 60 + 36, cam="CAM 2  CABIN  IR  [REPLAY]")
        out = Image.fromarray(np.clip(a * 0.85, 0, 255).astype(np.uint8)).convert("RGBA")
        header(out, t, "PART 2")
        return to_arr(out)
    return f


def meter_ui(fare, k=1.0):
    im = Image.new("RGBA", (520, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 519, 189], 18, fill=(10, 10, 10, int(230 * k)), outline=(255, 60, 50, int(255 * k)), width=5)
    d.text((26, 18), "TAXIMETER", font=mono(30, True), fill=(255, 120, 100, int(255 * k)))
    d.text((494, 120), f"P {fare:6.2f}", font=mono(70, True), fill=(255, 70, 60, int(255 * k)), anchor="rm")
    return im


def make_meter(D, caps):
    t2 = caps[1][1]
    def f(t):
        img = road(t, 600 + 16 * t, flick=0.9)
        a = camera(img, t, "dash", speed=48, clock0=2 * 3600 + 49 * 60 + 40, extra="BALETE DR.")
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        fare = 40.0 + (0 if t < t2 else 13.5 * int((t - t2) * 3))
        k = 1.0
        out.alpha_composite(meter_ui(fare, k), (W - 560, 1040))
        return to_arr(out)
    return f


def make_voice(D, caps):
    t2 = caps[1][1]
    def f(t):
        lean = 0.3 + 0.7 * ss(t, 0.5, t2)
        img = cabin(t, lady=1.0, lady_lean=lean, lady_scale=1.0)
        g = 0.35 if t2 - 0.1 < t < t2 + 0.2 else 0.05
        return camera(img, t, "nv", glitch=g, clock0=2 * 3600 + 49 * 60 + 47)
    return f


def make_empty(D, caps):
    def f(t):
        img = cabin(t, lady=0.0, flower=True)
        a = camera(img, t, "nv", clock0=2 * 3600 + 49 * 60 + 55)
        z = 1 + 0.5 * ss(t, caps[1][1], D)
        if z > 1.001:
            cw, ch = W / z, H / z; x0 = 470 - cw / 2; y0 = 1000 - ch / 2
            x0 = min(max(0, x0), W - cw); y0 = min(max(0, y0), H - ch)
            a = cv2.resize(a[int(y0):int(y0 + ch), int(x0):int(x0 + cw)], (W, H))
        return a
    return f


def make_twist(D, caps):
    t2 = caps[1][1]
    jt = D - 1.0
    def f(t):
        # a playback screen: the clip scrubs forward, then freezes on the last frame
        scrub = min(1.0, t / (t2 + 1.5))
        img = cabin(t * 3, lady=0.0 if t < jt else 1.0, flower=t < jt, window_lights=True)
        a = camera(img, t, "nv", clock0=2 * 3600 + 49 * 60 + int(10 + 50 * scrub), cam="PLAYBACK  FILE 0247.MP4", rec=False)
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        d = ImageDraw.Draw(out)
        d.rectangle([60, 1200, W - 60, 1212], fill=(80, 80, 80, 255))
        d.rectangle([60, 1200, 60 + (W - 120) * scrub, 1212], fill=(255, 60, 50, 255))
        d.text((W / 2, 1150), "|| LAST FRAME" if scrub >= 1 else ">> PLAYING", font=mono(36, True), fill=(240, 240, 230, 255), anchor="mm")
        a = to_arr(out)
        if t > jt:   # she is right at the lens
            c = cabin_base()["lady"]
            sc = 2.6
            s = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
            face = cabin(t, lady=0.0, window_lights=False); face.alpha_composite(s, (int(W / 2 - s.width / 2), int(-120)))
            fa = camera(face, t, "nv", glitch=0.5, cam="PLAYBACK  FILE 0247.MP4", rec=False)
            a = fa
        if jt <= t < jt + 0.08:
            a = a * 0.2 + np.array([255, 255, 255], np.float32) * 0.8
        return a
    return f


def make_explain(D, caps):
    title = text_img("THE WHITE LADY", font(LORA, 100, "Bold"), fill=(250, 245, 240, 255), glow=(30, 80, 160, 220), pad=20)
    sub = text_img("of Balete Drive, Quezon City", font(INTER_SB, 48), fill=(255, 214, 120, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("Told by taxi drivers since the 1950s", pf, fill=(20, 40, 90, 235), h=80),
             pill("Asks for a ride, then vanishes", pf, fill=(20, 40, 90, 235), h=80),
             pill("Avoided from 12 to 3 a.m.", pf, fill=(110, 20, 24, 235), h=80)]
    ts = [caps[1][1] - 0.5, caps[1][1] + 3.5, caps[2][1] + 3.0]
    def f(t):
        img = road(t, 900 + 6 * t, lady_z=30, lady_wave=0.0, flick=0.85)
        a = camera(img, t, "dash", speed=20, clock0=2 * 3600 + 50 * 60, extra="BALETE DR.") * 0.55
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        out.alpha_composite(with_alpha(FLAG, ss(t, 0, 0.5)), (int(W / 2 - FLAG.width / 2), 170))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 280))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 420))
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.2, tt + 0.3)
            if k > 0:
                out.alpha_composite(with_alpha(c, k), (int(W / 2 - c.width / 2), int(520 + i * 100 + 14 * (1 - k))))
        return to_arr(out)
    return f


def make_outro(D, caps):
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("stop for her?", font(LORA, 100, "Bold"), fill=(255, 210, 60, 255), glow=(30, 80, 160, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Stop the car", (20, 40, 90, 235)), ("Keep driving", (60, 60, 60, 235)), ("Look in the mirror", (140, 100, 20, 235)), ("PRAY", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    def f(t):
        img = road(t, 1000 + 8 * t, flick=0.8)
        a = camera(img, t, "dash", speed=30) * 0.45
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        out.alpha_composite(FLAG, (int(W / 2 - FLAG.width / 2), 180))
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
