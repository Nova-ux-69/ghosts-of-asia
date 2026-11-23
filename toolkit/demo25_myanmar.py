"""2.5D cinematic style test: a Myanmar cemetery at night, a stupa far away, a banyan tree, and the ghost.
Usage: python3 demo25_myanmar.py still out.png [t]
       python3 demo25_myanmar.py video out.mp4 [seconds]
"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from depth import inflate_shade, dof, god_rays, bokeh_particles
from art_v import fog_texture, caption_img, vignette

W, H = 1080, 1920
MOON = (300, 380)
LIGHT = (-0.55, -0.7, 0.5)          # moon is up-left
RIM = (255, 55, 40)                 # red rim from the right (a red glow behind the trees)
HORIZON = 1180


def smooth_mask(draw_fn, size, ss=2):
    """Draw at ss x, return a smooth 'L' mask at 1x."""
    w, h = size
    m = Image.new("L", (w * ss, h * ss), 0)
    draw_fn(ImageDraw.Draw(m), ss)
    return m.resize((w, h), Image.LANCZOS)


def shaded(draw_fn, size, base, radius, **kw):
    m = smooth_mask(draw_fn, size)
    return inflate_shade(m, base, light=kw.pop("light", LIGHT), rim=kw.pop("rim", RIM), radius=radius, **kw)


# ------------------------------------------------------------------ sky
def sky():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([4, 2, 3], np.float32); mid = np.array([38, 6, 8], np.float32); hor = np.array([110, 22, 18], np.float32)
    k1 = np.clip(y / 0.6, 0, 1) ** 1.6
    k2 = np.clip((y - 0.45) / 0.18, 0, 1)
    col = top * (1 - k1) + mid * k1
    col = col * (1 - k2) + hor * k2
    col = np.broadcast_to(col[:, None, :], (H, W, 3)).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - MOON[0]) ** 2 + (yy - MOON[1]) ** 2)
    col += (np.exp(-d / 260) * 120)[..., None] * np.array([1.0, 0.55, 0.45])
    col += (np.exp(-d / 70) * 90)[..., None] * np.array([1.0, 0.85, 0.8])
    moon = np.clip((95 - d) / 2, 0, 1)
    tex = fog_texture(W, H, 7)
    mcol = np.array([235, 215, 205], np.float32) * (0.85 + 0.15 * tex)[..., None]
    col = col * (1 - moon[..., None]) + mcol * moon[..., None]
    # thin clouds across the moon
    cl = fog_texture(W, H, 3) * np.exp(-((yy - 520) / 160) ** 2)
    col = col * (1 - 0.5 * cl[..., None]) + np.array([60, 15, 18]) * 0.5 * cl[..., None]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")


# ------------------------------------------------------------------ far: stupa + treeline
def stupa_layer():
    w, h = 520, 760
    def draw(d, s):
        cx = w * s / 2
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        # terraces
        for i, (hw, y0, y1) in enumerate(((230, 700, 760), (190, 640, 700), (155, 590, 640))):
            d.rectangle([cx - hw * s, y0 * s, cx + hw * s, y1 * s], fill=255)
        # bell
        d.polygon(P(*[(w / 2 + 140 * math.sin(a) * (1 - 0.15 * (1 - math.cos(a))), 590 - 190 * (1 - math.cos(a * 0.9)))
                      for a in np.linspace(-1.55, 1.55, 40)]), fill=255)
        d.ellipse([cx - 140 * s, 520 * s, cx + 140 * s, 600 * s], fill=255)
        # bands and spire
        d.polygon(P((w / 2 - 70, 420), (w / 2 + 70, 420), (w / 2 + 50, 330), (w / 2 - 50, 330)), fill=255)
        d.polygon(P((w / 2 - 48, 335), (w / 2 + 48, 335), (w / 2 + 6, 70), (w / 2 - 6, 70)), fill=255)
        d.ellipse([cx - 22 * s, 220 * s, cx + 22 * s, 250 * s], fill=255)
        d.ellipse([cx - 16 * s, 150 * s, cx + 16 * s, 175 * s], fill=255)
        # hti umbrella
        d.polygon(P((w / 2 - 26, 90), (w / 2 + 26, 90), (w / 2, 40)), fill=255)
        d.line([(cx, 0), (cx, 50 * s)], fill=255, width=int(4 * s))
    st = shaded(draw, (w, h), (150, 100, 50), 60, rim=(255, 120, 60), rim_strength=0.5, spec=0.5)
    # haze: mix towards the horizon red
    a = np.asarray(st, np.float32)
    a[..., :3] = a[..., :3] * 0.55 + np.array([110, 24, 20]) * 0.45
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def treeline(seed, y, amp, col, height):
    rng = np.random.default_rng(seed)
    m = Image.new("L", (W + 300, height), 0)
    d = ImageDraw.Draw(m)
    x = 0
    while x < W + 300:
        r = rng.uniform(30, 80) * amp
        d.ellipse([x - r, height - y - r * rng.uniform(1.0, 2.2), x + r, height - y + r], fill=255)
        if rng.random() < 0.25:  # sugar palm
            th = rng.uniform(150, 260) * amp
            d.line([(x, height), (x, height - y - th)], fill=255, width=int(5 * amp))
            for k in range(9):
                ang = -math.pi / 2 + (k - 4) * 0.38
                d.line([(x, height - y - th), (x + math.cos(ang) * 55 * amp, height - y - th + math.sin(ang) * 40 * amp + 20)], fill=255, width=int(6 * amp))
        x += r * rng.uniform(0.9, 1.4)
    d.rectangle([0, height - y, W + 300, height], fill=255)
    im = Image.new("RGBA", m.size, col + (0,)); im.putalpha(m)
    return im


# ------------------------------------------------------------------ mid: banyan tree
def banyan():
    w, h = 900, 1500
    rng = np.random.default_rng(11)
    def trunk(d, s):
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        d.polygon(P((470, 1500), (760, 1500), (690, 1380), (660, 1000), (690, 700), (760, 520), (700, 500), (620, 660), (560, 560), (470, 420),
                    (430, 450), (520, 640), (540, 900), (520, 1300)), fill=255)
        for x0, x1 in ((470, 330), (520, 400), (700, 860), (740, 900)):   # buttress roots
            d.polygon(P((x0, 1380), (x0 + 40, 1380), (x1, 1500), (x1 - 60, 1500)), fill=255)
        for i in range(14):  # hanging aerial roots
            x = rng.uniform(150, 880); y0 = rng.uniform(450, 620); L = rng.uniform(300, 800)
            d.line([(x * s, y0 * s), ((x + rng.uniform(-15, 15)) * s, (y0 + L) * s)], fill=255, width=int(rng.uniform(4, 9) * s))
    tr = shaded(trunk, (w, h), (70, 45, 38), 34, rim_strength=1.1)
    def canopy(d, s):
        for i in range(70):
            r = rng.uniform(60, 130); cx = float(np.clip(rng.normal(600, 170), r + 10, w - r - 10)); cy = float(np.clip(rng.normal(420, 90), r, 700))
            d.ellipse([(cx - r) * s, (cy - r * 0.8) * s, (cx + r) * s, (cy + r * 0.8) * s], fill=255)
    cn = shaded(canopy, (w, h), (40, 34, 28), 90, rim_strength=1.2, spec=0.05, ambient=0.18)
    a = np.asarray(cn, np.float32)
    leaf = fog_texture(w, h, 31); fine = np.random.default_rng(4).random((h, w)).astype(np.float32)
    a[..., :3] *= (0.55 + 0.6 * leaf + 0.25 * fine)[..., None]
    cn = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(tr); out.alpha_composite(cn)
    return out


# ------------------------------------------------------------------ graves
def grave(seed, scale=1.0, lean=0.0):
    w, h = int(220 * scale) + 40, int(320 * scale) + 40
    def draw(d, s):
        x0, x1, y0, y1 = 20 * s, (w - 20) * s, 20 * s, (h - 20) * s
        r = (x1 - x0) / 2
        d.rounded_rectangle([x0, y0 + r * 0.2, x1, y1], radius=int(r * 0.9), fill=255)
        d.rectangle([x0 - 10 * s, y1 - 30 * s * scale, x1 + 10 * s, y1], fill=255)
    g = shaded(draw, (w, h), (95, 88, 86), 26 * scale, rim_strength=0.8, spec=0.15)
    # carved line + moss noise
    a = np.asarray(g, np.float32)
    tex = fog_texture(w, h, seed)
    a[..., :3] *= (0.7 + 0.45 * tex)[..., None]
    g = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    return g.rotate(lean, resample=Image.BICUBIC, expand=True)


# ------------------------------------------------------------------ ghost
def ghost():
    w, h = 620, 1150
    cx = w / 2
    def hair_back(d, s):
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        d.ellipse([(cx - 105) * s, 80 * s, (cx + 105) * s, 330 * s], fill=255)
        d.polygon(P((cx - 105, 200), (cx - 150, 520), (cx - 175, 780), (cx - 120, 720), (cx - 95, 840), (cx - 40, 560), (cx + 40, 560),
                    (cx + 100, 860), (cx + 125, 710), (cx + 170, 800), (cx + 150, 520), (cx + 105, 200)), fill=255)
    def hair_front(d, s):
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        d.pieslice([(cx - 98) * s, 88 * s, (cx + 98) * s, 300 * s], 180, 360, fill=255)
        for sg in (-1, 1):   # side curtains that frame the face and fall in front of the shoulders
            d.polygon(P((cx + sg * 98, 190), (cx + sg * 40, 200), (cx + sg * 52, 330), (cx + sg * 70, 640), (cx + sg * 58, 760), (cx + sg * 95, 700), (cx + sg * 118, 520)), fill=255)
        for x, y1 in ((cx - 22, 330), (cx + 6, 375), (cx + 30, 300)):   # thin strands over the face
            d.polygon(P((x - 9, 190), (x + 9, 190), (x + 3, y1), (x - 2, y1)), fill=255)
    def face(d, s):
        d.ellipse([(cx - 62) * s, 170 * s, (cx + 62) * s, 345 * s], fill=255)
    def dress(d, s):
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        hem = [(cx + 250 - i * 500 / 14, 1120 - (40 if i % 2 else 0) - 30 * math.sin(i * 1.7)) for i in range(15)]
        d.polygon(P((cx - 20, 330), (cx + 20, 330), (cx + 95, 410), (cx + 150, 700), (cx + 250, 1120), *hem[1:-1], (cx - 250, 1120), (cx - 150, 700), (cx - 95, 410)), fill=255)
    def arms(d, s):
        P = lambda *pts: [(x * s, y * s) for x, y in pts]
        for sg in (-1, 1):
            d.polygon(P((cx + sg * 90, 410), (cx + sg * 125, 420), (cx + sg * 165, 760), (cx + sg * 150, 770)), fill=255)
            d.polygon(P((cx + sg * 150, 760), (cx + sg * 170, 760), (cx + sg * 178, 880), (cx + sg * 168, 900), (cx + sg * 155, 870)), fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = shaded(dress, (w, h), (196, 190, 194), 70, rim=(255, 60, 50), rim_strength=1.0, spec=0.18, ambient=0.35)
    # fade the hem into mist
    a = np.asarray(dr, np.float32)
    yy = np.arange(h)[:, None]
    a[..., 3] *= np.clip((1110 - yy) / 330, 0, 1) ** 0.8
    dr = Image.fromarray(a.astype(np.uint8), "RGBA")
    # cloth folds, stronger towards the hem
    a = np.asarray(dr, np.float32)
    xx = np.arange(w)[None, :]
    fold = 0.5 + 0.5 * np.sin((xx - cx) / 23 + np.sin(yy / 90) * 1.5)
    kf = 0.2 + np.clip((yy - 420) / 600, 0, 1) * 0.4
    a[..., :3] *= (1 - kf * fold)[..., None]
    out.alpha_composite(shaded(hair_back, (w, h), (16, 12, 12), 40, rim=(255, 50, 40), rim_strength=1.3, spec=0.3, ambient=0.2))
    out.alpha_composite(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA"))
    out.alpha_composite(shaded(arms, (w, h), (190, 196, 192), 14, rim_strength=0.9, ambient=0.4))
    out.alpha_composite(shaded(face, (w, h), (198, 204, 200), 40, rim_strength=0.6, ambient=0.4, spec=0.1))
    fd = ImageDraw.Draw(out)
    fd.ellipse([cx - 44, 232, cx - 12, 264], fill=(25, 10, 12, 255))       # dark eye sockets
    fd.ellipse([cx + 12, 232, cx + 44, 264], fill=(25, 10, 12, 255))
    fd.ellipse([cx - 8, 300, cx + 8, 318], fill=(30, 12, 14, 255))   # small open mouth
    out.alpha_composite(shaded(hair_front, (w, h), (18, 13, 13), 22, rim=(255, 50, 40), rim_strength=1.4, spec=0.35, ambient=0.2))
    return out


def eye_glow(img, x, y, k):
    spr = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(spr)
    d.ellipse([52, 54, 68, 66], fill=(255, 40, 30, int(255 * k)))
    g = spr.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(g, (int(x - 60), int(y - 60)))
    img.alpha_composite(g, (int(x - 60), int(y - 60)))
    img.alpha_composite(spr, (int(x - 60), int(y - 60)))


def foreground():
    m = Image.new("L", (W + 400, 700), 0)
    d = ImageDraw.Draw(m)
    rng = np.random.default_rng(5)
    for i in range(160):
        x = rng.uniform(0, W + 400); hgt = rng.uniform(120, 520)
        d.polygon([(x - 10, 700), (x + 10, 700), (x + rng.uniform(-60, 60), 700 - hgt)], fill=255)
    d.line([(0, 80), (220, 150), (420, 120), (520, 160)], fill=255, width=26)   # a branch at the top-left of this strip
    for x, y in ((160, 140), (300, 130), (450, 140)):
        d.ellipse([x - 40, y - 15, x + 40, y + 30], fill=255)
    im = Image.new("RGBA", m.size, (6, 3, 4, 0)); im.putalpha(m)
    return im


# ------------------------------------------------------------------ build all layers once
class Scene:
    def __init__(self):
        self.sky = sky()
        self.far_trees = dof(treeline(1, 40, 0.7, (40, 10, 12), 420), 3)
        st = stupa_layer(); self.stupa = dof(st.resize((st.width * 3 // 4, st.height * 3 // 4), Image.LANCZOS), 2.0)
        self.mid_trees = dof(treeline(2, 10, 1.1, (14, 5, 7), 520), 1.5)
        self.banyan = banyan()
        self.graves = [(grave(s, sc, ln), x, y, sc, bl) for s, sc, ln, x, y, bl in (
            (1, 0.55, -4, 140, 1300, 1.2), (2, 0.5, 3, 430, 1290, 1.2), (3, 0.7, 6, 760, 1360, 0.4),
            (4, 1.0, -7, 70, 1500, 0.0), (5, 1.25, 5, 640, 1640, 2.5))]
        self.ghost = ghost()
        self.fg = dof(foreground(), 9)
        self.fog = fog_texture(W + 600, H, 21)
        self.fog2 = fog_texture(W + 600, H, 22)
        self.vig = vignette(0.85)
        y = np.arange(H)[:, None]
        g = np.clip((y - HORIZON + 40) / 900, 0, 1)
        ground = np.zeros((H, W, 4), np.float32)
        ground[..., 0] = 40 - 30 * g; ground[..., 1] = 12 - 8 * g; ground[..., 2] = 12 - 8 * g
        ground[..., 3] = 255 * (y >= HORIZON - 10)
        tex = fog_texture(W, H, 9)
        ground[..., :3] *= (0.7 + 0.6 * tex)[..., None]
        self.ground = Image.fromarray(np.clip(ground, 0, 255).astype(np.uint8), "RGBA")

    def frame(self, t, cam=0.0, push=1.0, cap=None):
        img = self.sky.copy()
        P = lambda depth: int(-cam * depth)          # parallax
        img.alpha_composite(self.far_trees, (P(0.15) - 150, HORIZON - 420 + 20))
        img.alpha_composite(self.stupa, (P(0.2) + 20, HORIZON - 570 + 30))
        img.alpha_composite(self.mid_trees, (P(0.35) - 150, HORIZON - 520 + 40))
        img.alpha_composite(self.ground)
        bx, by = P(0.6) + 380, HORIZON - 1500 + 330
        img.alpha_composite(self.banyan, (bx, by))
        occ_im = Image.new("L", (W, H), 0)
        for lay, pos in ((self.far_trees, (P(0.15) - 150, HORIZON - 400)), (self.stupa, (P(0.2) + 20, HORIZON - 540)),
                         (self.mid_trees, (P(0.35) - 150, HORIZON - 480)), (self.banyan, (bx, by))):
            occ_im.paste(255, pos, lay.split()[3])
        occ_im.paste(255, (0, HORIZON, W, H))
        occ = np.asarray(occ_im, np.float32) / 255
        small = Image.fromarray((occ * 255).astype(np.uint8)).resize((W // 3, H // 3))
        base = np.asarray(img, np.float32)[..., :3]
        rays = god_rays(np.zeros((H // 3, W // 3, 3), np.float32), (MOON[0] / 3, MOON[1] / 3), np.asarray(small, np.float32) / 255,
                        color=(255, 90, 70), strength=0.55, reach=0.9)
        rays = np.asarray(Image.fromarray(np.clip(rays, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
        base = base + rays
        img = Image.fromarray(np.clip(np.dstack([base, np.full((H, W), 255.0)]), 0, 255).astype(np.uint8), "RGBA")
        for g, x, y, sc, bl in self.graves[:3]:
            img.alpha_composite(dof(g, bl), (P(0.6 + 0.3 * sc) + x, y - g.height))
        # fog band behind the ghost
        self._fog(img, t, 0.45, 1150, 1500, self.fog, 18, P(0.7))
        # ghost floats and sways
        fl = 18 * math.sin(t * 1.3)
        gh = self.ghost.rotate(1.5 * math.sin(t * 0.9), resample=Image.BICUBIC, center=(310, 200))
        glow = gh.split()[3].filter(ImageFilter.GaussianBlur(40))
        gl = Image.new("RGBA", gh.size, (255, 60, 50, 0)); gl.putalpha(glow.point(lambda v: int(v * 0.45)))
        gx, gy = P(0.8) + 230, int(500 + fl)
        img.alpha_composite(gl, (gx, gy)); img.alpha_composite(gh, (gx, gy))
        k = 0.6 + 0.4 * math.sin(t * 5) ** 2
        eye_glow(img, gx + 310 - 27, gy + 248, k); eye_glow(img, gx + 310 + 27, gy + 248, k)
        for g, x, y, sc, bl in self.graves[3:]:
            img.alpha_composite(dof(g, bl), (P(0.6 + 0.3 * sc) + x, y - g.height))
        self._fog(img, t, 0.35, 1400, 1920, self.fog2, -26, P(1.0))
        bokeh_particles(img, 45, 3, t, color=(255, 110, 80), size=(2, 14), blur=(0, 7), area=(0, 300, W, 1700))
        img.alpha_composite(self.fg, (P(1.6) - 200, H - 700 + 40))
        if push != 1.0:
            cw, ch = W / push, H / push
            img = img.resize((W, H), Image.BICUBIC, box=((W - cw) / 2, (H - ch) * 0.45, (W - cw) / 2 + cw, (H - ch) * 0.45 + ch))
        a = np.asarray(img, np.float32)[..., :3] * self.vig
        a += np.random.default_rng(int(t * 30)).normal(0, 5, (H, W, 1))
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        if cap:
            c = caption_img(cap)
            img.alpha_composite(c, ((W - c.width) // 2, 1320))
        return img.convert("RGB")

    def banyan_occ(self, bx, by):
        m = Image.new("L", (W, H), 0)
        m.paste(self.banyan.split()[3], (bx, by))
        st = Image.new("L", (W, H), 0)
        return np.maximum(np.asarray(m, np.float32) / 255, 0)

    def _fog(self, img, t, k, y0, y1, tex, speed, px):
        off = int((t * speed + px) % 600)
        f = tex[:, off:off + W]
        yy = np.arange(H)[:, None]
        band = np.clip(np.minimum((yy - y0) / 160, (y1 - yy) / 160), 0, 1)
        a = f * band * k
        layer = np.dstack([np.full((H, W), 150.0), np.full((H, W), 45.0), np.full((H, W), 42.0), a * 255]).astype(np.uint8)
        img.alpha_composite(Image.fromarray(layer, "RGBA"))


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    S = Scene()
    cap = "In Myanmar, they say she waits among the graves."
    if mode == "still":
        t = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
        S.frame(t, cam=0, push=1.0, cap=cap).save(out)
    else:
        dur = float(sys.argv[3]) if len(sys.argv) > 3 else 6
        n = int(dur * 30)
        tmp = out[:-4] + ".tmp.mp4"
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                              "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for i in range(n):
            t = i / 30; u = t / dur; e = u * u * (3 - 2 * u)
            p.stdin.write(S.frame(t, cam=-60 + 120 * e, push=1.0 + 0.09 * e, cap=cap if t > 1.0 else None).tobytes())
        p.stdin.close(); p.wait()
        os.replace(tmp, out)
