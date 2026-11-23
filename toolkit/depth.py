"""2.5D 'cinematic' helpers: make flat shapes look 3D and give scenes real depth.

inflate_shade(mask, base, ...)  -> RGBA: a flat silhouette shaded like a rounded 3D object (key light + rim light)
dof(img, radius)                -> blur a layer by its distance from the focus plane
god_rays(frame, light_xy, occluder_alpha, color) -> light beams through fog/trees from a light source
bokeh_particles(...)            -> floating dust/ash/embers with depth-blur
parallax offsets: move each layer by camera_dx * depth_factor (far = 0.1, mid = 0.4, near = 1.0, foreground = 1.6)
"""
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import distance_transform_edt, gaussian_filter


def inflate_shade(mask, base, light=(-0.55, -0.65, 0.55), rim=(255, 60, 60), rim_dir=(0.8, -0.2),
                  rim_strength=0.9, radius=70, ambient=0.28, spec=0.25, toon=None):
    """mask: PIL 'L' or float array 0..1. base: (r,g,b). Returns RGBA PIL image the size of the mask."""
    m = np.asarray(mask, np.float32)
    if m.max() > 1.5:
        m = m / 255.0
    inside = m > 0.5
    d = gaussian_filter(distance_transform_edt(inside).astype(np.float32), max(1.5, radius * 0.05))
    u = np.clip(d / radius, 0, 1)
    h = np.sqrt(1 - (1 - u) ** 2) * radius           # round dome profile
    h = gaussian_filter(h, max(2.0, radius * 0.04))
    gy, gx = np.gradient(h)
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    diff = np.clip((n * L).sum(2), 0, 1)
    H = (L + np.array([0, 0, 1.0])); H /= np.linalg.norm(H)
    specular = np.clip((n * H).sum(2), 0, 1) ** 24 * spec
    rd = np.array(rim_dir, np.float32); rd /= np.linalg.norm(rd)
    rimv = (1 - n[..., 2]) ** 2.2 * np.clip(n[..., 0] * rd[0] + n[..., 1] * rd[1], 0, 1)
    if toon is None:
        import os; toon = os.environ.get("STYLE") == "toon"
    if toon:   # 2.2D: flat colour bands (cartoon shading) instead of smooth 3D
        diff = np.where(diff > 0.55, 1.0, np.where(diff > 0.2, 0.6, 0.3))
        rimv = (rimv > 0.12).astype(np.float32) * 0.8
        specular = (specular > spec * 0.5).astype(np.float32) * spec * 0.6
        u = np.ones_like(u)
    ao = 0.75 + 0.25 * u                               # darker near the outline
    col = np.array(base, np.float32)[None, None] * (ambient + (1 - ambient) * diff)[..., None] * ao[..., None]
    col += np.array(rim, np.float32)[None, None] * (rimv * rim_strength)[..., None]
    col += 255 * specular[..., None]
    if toon:   # dark ink outline
        from scipy.ndimage import binary_dilation
        ring = binary_dilation(inside, iterations=3) & ~binary_dilation(~inside, iterations=0) & (d < 2.5)
        col[ring] = (12, 6, 8)
    rgba = np.dstack([np.clip(col, 0, 255), m * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def dof(img, radius):
    if radius <= 0.3:
        return img
    return img.filter(ImageFilter.GaussianBlur(radius))


def god_rays(frame_rgb, light_xy, occluder_alpha, color=(255, 70, 50), strength=0.9, steps=28, reach=0.45):
    """frame_rgb: float32 HxWx3 (modified copy returned). occluder_alpha: float HxW 0..1 (1 = blocks light)."""
    H, W = occluder_alpha.shape
    lx, ly = light_xy
    yy, xx = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((xx - lx) ** 2 + (yy - ly) ** 2) / (2 * (min(W, H) * 0.18) ** 2))).astype(np.float32)
    src = glow * (1 - occluder_alpha)
    acc = np.zeros_like(src)
    img = Image.fromarray((src * 255).astype(np.uint8))
    for i in range(steps):
        s = 1 + reach * i / steps
        w2, h2 = int(W * s), int(H * s)
        z = img.resize((w2, h2), Image.BILINEAR)
        ox, oy = int(lx * s - lx), int(ly * s - ly)
        acc += np.asarray(z.crop((ox, oy, ox + W, oy + H)), np.float32) / 255 * (1 - i / steps)
    acc /= steps * 0.5
    out = frame_rgb + acc[..., None] * np.array(color, np.float32)[None, None] * strength
    return out


def bokeh_particles(img, n, seed, t=0.0, color=(255, 120, 90), size=(3, 18), blur=(0, 6), area=None, drift=(10, -25)):
    """Draw floating particles; bigger ones are 'closer' and blurrier (depth). img: RGBA PIL, modified in place."""
    from PIL import ImageDraw
    rnd = np.random.default_rng(seed)
    W, H = img.size
    x0, y0, x1, y1 = area or (0, 0, W, H)
    for k in range(n):
        depth = rnd.random()
        r = size[0] + (size[1] - size[0]) * depth ** 2
        x = (rnd.uniform(x0, x1) + drift[0] * t * (0.3 + depth)) % W
        y = (rnd.uniform(y0, y1) + drift[1] * t * (0.3 + depth)) % H
        a = int(255 * (0.25 + 0.6 * rnd.random()) * (1 - 0.4 * depth))
        b = blur[0] + (blur[1] - blur[0]) * depth ** 2
        pad = int(r + 3 * b + 4)
        spr = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
        ImageDraw.Draw(spr).ellipse([pad - r, pad - r, pad + r, pad + r], fill=tuple(color) + (a,))
        if b > 0.3:
            spr = spr.filter(ImageFilter.GaussianBlur(b))
        img.alpha_composite(spr, (int(x - pad), int(y - pad)))
