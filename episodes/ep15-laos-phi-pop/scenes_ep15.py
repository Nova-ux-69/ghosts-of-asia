"""Ep15 Laos / Phi Pop - scenes (2.1D survival). Each make_<id>(D, caps) returns f(t) -> float RGB (H, W, 3)."""
from art_ep15 import *

if os.environ.get("NO_UI"):                       # covers: no clock pill under the cover header
    def put_clock(*a, **k):
        pass

UI_Y = 200
_SH = {}


def shadow(neck, turn, reach=0.0, scale=0.85, child=False):
    """Cached Phi Pop shadow mask, resized. Returns (mask, eyes in mask px)."""
    k = (round(neck, 2), round(turn, 2), round(reach, 2), round(scale, 2), child)
    if k not in _SH:
        if len(_SH) > 300:
            _SH.clear()
        m, e = pop_shadow_mask(neck, turn, reach, child=child)
        if scale != 1.0:
            m = m.resize((int(m.width * scale), int(m.height * scale)), Image.LANCZOS)
            e = [(x * scale, y * scale) for x, y in e]
        _SH[k] = (m, e)
    return _SH[k]


def shadow_eyes(img, m, e, sx, sy, cam, t, k=1.0, sc=0.5):
    """Red eyes on a wall shadow placed with Room.frame(shadow=(m, sx, sy, ..))."""
    if k <= 0:
        return img
    x0 = sx - m.width / 2 - cam; y0 = sy - m.height
    kk = k * (0.7 + 0.3 * math.sin(t * 6) ** 2)
    for ex, ey in e:
        eye(img, x0 + ex, y0 + ey, kk, sc)
    return img


def chips_at(out, chips, ts, t, y0, gap=110):
    for i, (c, tt) in enumerate(zip(chips, ts)):
        k = ss(t, tt - 0.15, tt + 0.3)
        if k > 0:
            cc = c if c.width <= W - 40 else c.resize((W - 40, int(c.height * (W - 40) / c.width)), Image.LANCZOS)
            out.alpha_composite(with_alpha(cc, k), (int(W / 2 - cc.width / 2), int(y0 + i * gap + 20 * (1 - k))))


def put_sprite(img, spr, x, y, fx, fy):
    img.alpha_composite(spr, (int(x - fx), int(y - fy)))
    return img


def sil(mask, col=(10, 3, 4), rim=(255, 60, 40), rim_k=0.8):
    """A dark silhouette with a thin red rim from an L mask."""
    a = np.asarray(mask, np.float32) / 255
    from scipy.ndimage import gaussian_filter
    edge = np.clip(a - gaussian_filter(a, 3), 0, 1) * 3
    rgb = np.array(col, np.float32)[None, None] * (1 - edge[..., None]) + np.array(rim, np.float32)[None, None] * edge[..., None] * rim_k
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), "RGBA")


_SIL = {}


def sil_c(key, mask_fn):
    if key not in _SIL:
        _SIL[key] = sil(mask_fn())
    return _SIL[key]


def wrist_closeup(t, wrap=1.0, strings=3, snap=0.0, grandma=True, light=1.0):
    """Close-up: Noy's forearm across the frame, Grandma's old hands tying a white baci string round her wrist.
    snap 0..1: one string breaks, the two ends flying apart."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def arm(d, s):
        d.polygon(P_((-40, 1010), (560, 1040), (600, 1090), (600, 1200), (560, 1240), (-40, 1250), s=s), fill=255)
        d.ellipse([560 * s, 1010 * s, 790 * s, 1250 * s], fill=255)                     # her fist
    img.alpha_composite(shade_c("arm", arm, SKIN, 60))
    d = ImageDraw.Draw(img)
    for k in range(3):                                                                    # knuckle lines
        d.arc([650, 1040 + k * 52, 760, 1090 + k * 52], 270, 360, fill=(120, 80, 60, 255), width=4)
    # the strings: loops round the wrist
    for i in range(strings):
        x = 500 + i * 26
        if i == strings - 1 and snap > 0:
            dx = 80 * snap
            d.line([(x, 1035), (x + 6, 1120 - 30 * snap), (x - dx, 1120 + 60 * snap)], fill=STRING + (255,), width=8, joint="curve")
            d.line([(x + 4, 1250), (x + 10, 1170 + 30 * snap), (x + dx + 20, 1150 - 40 * snap)], fill=STRING + (255,), width=8, joint="curve")
            continue
        n = int(14 * min(1, wrap if i == 0 else 1))
        pts = [(x + 8 * math.sin(j * 0.6), 1030 + j * 16) for j in range(n + 1)]
        if len(pts) > 1:
            d.line(pts, fill=STRING + (255,), width=8, joint="curve")
        if i == 0 and wrap > 0.9:
            d.ellipse([x - 16, 1000, x + 16, 1030], fill=STRING + (255,))                   # the knot on top
            d.line([(x, 1010), (x - 30, 950)], fill=STRING + (255,), width=6)
            d.line([(x, 1010), (x + 26, 954)], fill=STRING + (255,), width=6)
    if grandma:
        img.alpha_composite(shade_c("gma", gma_hands, (150, 104, 80), 30))
        d = ImageDraw.Draw(img)
        for k in range(5):                                                                # wrinkles
            d.arc([430 + k * 30, 840 + (k % 2) * 20, 480 + k * 30, 880 + (k % 2) * 20], 200, 330, fill=(100, 66, 50, 255), width=3)
    if light != 1.0:
        img = tint(img, (light, light, light))
    return img


def gma_hands(d, s):
    """Grandma's two old hands coming in from the top right, pinching the string ends above the wrist."""
    # upper hand: forearm from the top right, a broad palm, fingers pinching down at the knot
    d.polygon(P_((W + 60, 520), (W + 60, 700), (720, 900), (650, 840), s=s), fill=255)
    d.ellipse([560 * s, 780 * s, 740 * s, 930 * s], fill=255)
    for k in range(4):
        x0 = 575 + k * 34
        d.line([(x0 * s, 880 * s), ((x0 - 22) * s, (960 - k * 6) * s), ((x0 - 30) * s, (990 - k * 8) * s)], fill=255, width=int(24 * s), joint="curve")
    d.line([(700 * s, 860 * s), (640 * s, 960 * s)], fill=255, width=int(26 * s))                      # thumb
    # lower hand: from the right, holding the other end
    d.polygon(P_((W + 60, 880), (W + 60, 1060), (820, 1010), (800, 900), s=s), fill=255)
    d.ellipse([700 * s, 900 * s, 860 * s, 1030 * s], fill=255)
    for k in range(3):
        y0 = 920 + k * 32
        d.line([(720 * s, y0 * s), (660 * s, (y0 + 10) * s), (630 * s, (y0 + 26) * s)], fill=255, width=int(24 * s), joint="curve")


_SHC = {}


def shade_c(key, fn, col, r):
    if key not in _SHC:
        _SHC[key] = shade(fn, (W, H), col, r)
    return _SHC[key]


def kface_full(t, t0, inv=False, scale=1.25, y=880):
    img = Image.new("RGBA", (W, H), (6, 1, 2, 255))
    return put_kface(img, 540, y + 120 * ss(t, t0, t0 + 0.15) * (1 if not inv else -1), scale, t, eyes=1.0, grin=1.0, aura=0.9, inv=inv)


# ============================================================ PART 1
def make_hook(D, caps):
    R = room()
    hdr = series_header("LAOS", "PART 1")
    t2 = caps[1][1]
    SX, SY = 700, 1420

    def f(t):
        neck = ss(t, t2 - 2.2, t2 - 0.1)
        turn = ss(t, t2 - 0.6, t2)
        m, e = shadow(round(neck * 20) / 20, round(turn * 10) / 10, 0.0, 0.85)
        cam = -30 + 30 * t / D

        def woman(img, t_):                                       # the woman herself, seated, back to us, in the foreground
            s_ = sil_c("seat", lambda: pop_shadow_mask(0, 0, 0)[0].resize((1170, 1690), Image.LANCZOS))
            img.alpha_composite(s_, (int(560 + 100 - cam - s_.width / 2), int(2120 - s_.height)))
            return img
        img = R.frame(t, cam, lamp=1.0, shadow=(m, SX, SY, 1.0), front=[woman])
        shadow_eyes(img, m, e, SX, SY, cam, t, ss(t, t2 - 0.4, t2), 0.5)
        hit = t2 - 0.05 <= t < t2 + 0.12
        zk = ss(t, t2 - 0.1, t2 + 1.2)
        a = finish(img, t, VIG_H, push=1.0 + 0.04 * t / D + 0.45 * zk, cx=600 + 60 * zk, cy=960 - 300 * zk,
                   shake=0.8 if hit else 0.0, flash=0.5 if t2 - 0.05 <= t < t2 + 0.05 else 0.0, flash_col=(255, 30, 20))
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_setup(D, caps):
    V = village()
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        cam = -40 + 80 * t / D

        def people(img, t_, o):
            px, py = V.porch
            im, fx, fy = noy(0.0, scale=0.36, carry=True)
            img = put_sprite(img, im, px + o + 30, py, fx, fy)
            # Grandma walks away along the yard toward the temple with a lantern
            u = ss(t_, 0.2, D)
            gx = 700 + 300 * u + o; gy = 1520 - 70 * u; sc = 0.3 - 0.12 * u
            img = put_kham(img, gx, gy, sc, t_, possessed=False, eyes=0, aura=0, dark=0.45)
            a = to_arr(img); add_glow(a, gsp(70, (255, 170, 80)), gx + 60 * sc, gy - 600 * sc, 0.8); add_glow(a, gsp(10, (255, 240, 200)), gx + 60 * sc, gy - 600 * sc, 1.0)
            return to_img(a)

        def watcher(img, t_, o):                                  # the viewer sees her first: far out in the paddies
            k = ss(t_, t3 + 0.6, t3 + 1.0) * (1 - ss(t_, D - 0.9, D - 0.5))
            if k <= 0:
                return img
            return put_kham(img, 930 + o, 1190, 0.17, t_, tilt=-20, eyes=1.0, aura=0.3, alpha=k, dark=0.3)
        img = V.frame(t, cam, extras=[people], mid_extras=[watcher])
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.06 * t / D, cx=560, cy=1000))
        if t > t3 - 0.2:
            put_clock(out, 3, "23:40", t, ss(t, t3 - 0.2, t3 + 0.3), y=UI_Y)
        return to_arr(out)
    return f


def make_rule(D, caps):
    R = room()
    f1 = font(INTER_SB, 44)
    chips = [pill("GRANDMA'S RULES", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 220, 160, 255), h=86),
             pill("1. KEEP THE WHITE STRINGS TIED", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("2. NEVER LET IN ANYONE HUNGRY", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [0.3, caps[1][1] + 0.6, caps[2][1] + 0.3]
    bg_cache = {}

    def f(t):
        key = int(t * 8)
        if key not in bg_cache:
            sk = ss(t, caps[1][1] + 1.2, caps[1][1] + 2.5)
            m, e = shadow(0.0, 0.0, 0.0, 0.85)
            b = R.frame(t, 0, lamp=1.0, shadow=(m, 760, 1420, 0.8 * sk))
            b = b.filter(ImageFilter.GaussianBlur(6))
            a = to_arr(b); lum = a.mean(2, keepdims=True)
            a = a * 0.55 + lum * np.array([1.4, 0.85, 0.65]) * 0.45                       # a faded memory tint
            bg_cache.clear(); bg_cache[key] = to_img(a * 0.8)
        img = bg_cache[key].copy()
        wr = wrist_closeup(t, wrap=ss(t, 0.4, 2.8), strings=1 + (t > 1.6) + (t > 2.4), grandma=True)
        img.alpha_composite(wr, (0, 60))
        out = to_img(finish(img, t, VIG_H, push=1.03 + 0.06 * t / D, cx=560, cy=1100))
        chips_at(out, chips, ts, t, 230, 118)
        return to_arr(out)
    return f


def make_visitor(D, caps):
    R = room()
    t2, t3 = caps[1][1], caps[2][1]
    knocks = [caps[0][1] + 1.0 + k * 0.32 for k in range(3)]
    SX, SY = 820, 1420

    def f(t):
        neck = ss(t, t2 + 1.0, t3 + 1.2)
        reach = ss(t, t2 + 2.0, D - 0.3)
        turn = 0.5 * ss(t, t3 + 0.6, D)
        m, e = shadow(round(neck * 20) / 20, round(turn * 10) / 10, round(reach * 10) / 10, 0.85)
        sk = ss(t, t2 + 0.3, t2 + 1.2)
        ks = max([1 - ss(t, k, k + 0.15) if t >= k else 0 for k in knocks])
        cam = 0

        def girl(img, t_):
            im, fx, fy = noy(0.0, back=True, scale=1.05)
            return put_sprite(img, im, 470 + 100, 1900, fx, fy)
        img = R.frame(t, cam, lamp=1.0 - 0.15 * ks, shadow=(m, SX, SY, sk), door_shake=ks, door_light=1.0, door_fig=1.0, front=[girl])
        shadow_eyes(img, m, e, SX, SY, cam, t, ss(t, t3 + 0.3, t3 + 0.9) * sk, 0.45)
        zk = ss(t, t3 - 0.3, D)
        a = finish(img, t, VIG_H, push=1.03 + 0.04 * t / D + 0.25 * zk, cx=540 + 260 * zk, cy=1000 - 250 * zk, shake=0.5 * ks)
        out = to_img(a)
        put_clock(out, 3, "00:00", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_gone(D, caps):
    R = room()
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        lift = ss(t, t2 + 0.3, t2 + 1.4)
        sh = ss(t, t3 - 0.3, t3 + 0.4)
        lamp = 0.8 + 0.2 * (math.sin(t * 7) > -0.6)

        def girl(img, t_):
            im, fx, fy = noy(0.0, back=True, scale=1.0, lift=lift)
            return put_sprite(img, im, 680 + 100, 1880, fx, fy)
        img = R.frame(t, 80, lamp=lamp, shutter=sh, net=dict(empty=True, lift=lift), front=[girl])
        zk = ss(t, t3 - 0.2, D)
        a = finish(img, t, VIG_H, push=1.04 + 0.05 * t / D + 0.35 * zk, cx=600 + 160 * zk, cy=1100 + 200 * zk,
                   flash=0.25 * (t3 - 0.05 < t < t3 + 0.05), flash_col=(255, 40, 30))
        out = to_img(a)
        put_clock(out, 3, "00:20", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_mistake(D, caps):
    V = village()
    t2, t3 = caps[1][1], caps[2][1]
    cuts = [0.0, 2.4, t2 - 0.1]
    zs = [0.13, 0.19, 0.27]

    def f(t):
        if t >= t3 - 0.1:
            # insert: the string catches on a nail and snaps
            u = ss(t, t3, t3 + 0.4)
            img = Image.new("RGBA", (W, H), (20, 6, 6, 255))
            a = to_arr(img); add_glow(a, gsp(500, (150, 30, 24)), 540, 1100, 0.6); img = to_img(a)
            d = ImageDraw.Draw(img)
            d.rectangle([0, 760, W, 840], fill=(80, 44, 30, 255))                     # the ladder rail
            d.polygon([(760, 840), (776, 840), (770, 960)], fill=(170, 160, 150, 255))   # a bent nail
            img.alpha_composite(wrist_closeup(t, wrap=1.0, strings=3, snap=u, grandma=False), (40, -60))
            hit = t3 <= t < t3 + 0.1
            out = to_img(finish(img, t, VIG_H, push=1.05 + 0.1 * u, cx=560, cy=1060, shake=0.9 if t < t3 + 0.4 else 0.1,
                                flash=0.6 if hit else 0.0, flash_col=(255, 40, 30)))
            put_clock(out, 3 if t < t3 + 0.1 else 2, "01:10", t, 1.0, y=UI_Y)
            return to_arr(out)
        i = max(k for k, c in enumerate(cuts) if t >= c)
        u = ss(t, 0.3, t3 - 0.3)

        def people(img, t_, o):
            x0, y0, x1, y1 = V.ladder
            im, fx, fy = noy(0.0, back=True, scale=0.36, lift=0.6)
            return put_sprite(img, im, x0 + (x1 - x0) * u + o + 20, y0 + (y1 - y0) * u + 120, fx, fy)

        def her(img, t_, o):                                         # out in the field: closer at every cut
            z = zs[i]
            return put_kham(img, 520 + 260 * i + o, 1200 + 90 * i, z, t_, tilt=-20 + 6 * i, eyes=1.0, aura=0.4, dark=0.25)
        img = V.frame(t, 120, extras=[her, people], window=0.6)
        cut_flash = 0.3 if (t - cuts[i]) < 0.06 and i > 0 else 0.0
        out = to_img(finish(img, t, VIG_H, push=1.15 + 0.08 * t / D, cx=620, cy=1150, flash=cut_flash, flash_col=(255, 40, 30)))
        put_clock(out, 3, "01:10", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def outside_sil(xc, alpha=1.0, eye_y=None):
    """An L-mask (barn width) of a tall figure standing outside the slats, centred at xc (barn coords)."""
    m = Image.new("L", (W + 200, H), 0); d = ImageDraw.Draw(m)
    a = int(255 * alpha)
    d.ellipse([xc - 70, 380, xc + 70, 560], fill=a)                                  # head, tilted
    d.polygon([(xc - 30, 540), (xc + 30, 540), (xc + 160, 700), (xc + 150, 1460), (xc - 150, 1460), (xc - 160, 700)], fill=a)
    for sg in (-1, 1):
        d.line([(xc + sg * 150, 700), (xc + sg * 190, 1300)], fill=a, width=40)
    return m


def make_cliff(D, caps):
    V = village(); B = barn()
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.1
    cut = 2.5

    def f(t):
        if t < cut:
            u = ss(t, 0.0, cut - 0.2)

            def people(img, t_, o):
                im, fx, fy = noy((t_ * 2.4) % 1, run=1.0, scale=0.34)
                x0, y0, x1, y1 = V.ladder
                bx, by = V.barn_door
                return put_sprite(img, im, x1 + (bx - x1) * u + o, 1500 - 40 * math.sin(u * math.pi), fx, fy)

            def her(img, t_, o):
                return put_kham(img, 760 + o, 1340, 0.32, t_, tilt=-24, eyes=1.0, aura=0.4, dark=0.3)
            img = V.frame(t, 140, extras=[her, people], window=0.4)
            return finish(img, t, VIG_H, push=1.1 + 0.05 * u, cx=700, cy=1150, shake=0.25)
        if t >= jt:
            img = kface_full(t, jt)
            fl = 0.85 if t < jt + 0.08 else 0.0
            return finish(img, t, VIG_H, push=1.0 + 0.4 * ss(t, jt, jt + 0.18), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
        tt = t - cut
        xc = 1100 - 520 * ss(t, cut, t2 + 1.4)                                    # she walks along outside, then stops behind Noy

        def occ(t_):
            return outside_sil(xc + 20 * math.sin(t_ * 1.5) * (t_ > t2 + 1.4))

        def girl(img, t_):
            im, fx, fy, w = noy_crouch(1.0, look=0.4 * ss(t_, t3, t3 + 0.6))
            return put_sprite(img, im, 560 + 100, 1650, fx, fy)

        def peek(img, t_):                                                         # an eye in the gap, right by her head
            k = ss(t_, t2 + 1.8, t2 + 2.3)
            if k > 0:
                g = min(B.gaps, key=lambda gx: abs(gx - 640))
                eye(img, g, 1040, k, 0.35)
            return img
        img = B.frame(t, 0, occl=occ, extras=[girl, peek])
        push = 1.04 + 0.2 * ss(t, t2, jt)
        out = to_img(finish(img, t, VIG_H, push=push, cx=560, cy=1200))
        put_clock(out, 2, "02:30", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


# ============================================================ PART 2
def make_recap(D, caps):
    B = barn()
    hdr = series_header("LAOS", "PART 2")

    def f(t):
        def occ(t_):
            return outside_sil(580 + 20 * math.sin(t_ * 1.5))

        def girl(img, t_):
            im, fx, fy, w = noy_crouch(1.0, look=0.3)
            return put_sprite(img, im, 560 + 100, 1650, fx, fy)
        img = B.frame(t, 0, occl=occ, extras=[girl])
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.05 * t / D, cx=540, cy=1100))
        put_header(out, hdr, t)
        put_clock(out, 2, "02:40", t, ss(t, 2.0, 2.4), y=560)
        return to_arr(out)
    return f


def make_snap(D, caps):
    B = barn()
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 0.9
    hx0, hy0, hx1, hy1 = B.hole

    def f(t):
        if t >= jt:
            img = kface_full(t, jt, inv=True, scale=1.35, y=760)
            fl = 0.85 if t < jt + 0.08 else 0.0
            return finish(img, t, VIG_H, push=1.0 + 0.5 * ss(t, jt, jt + 0.2), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
        snapped = t >= t2
        n_str = 2 if not snapped else 1
        up = ss(t, t3 - 0.2, t3 + 0.8)

        def occ(t_):
            return outside_sil(400)

        def girl(img, t_):
            im, fx, fy, w = noy_crouch(1.0, look=1.0 * up, strings=n_str, arm_out=1.0 * (1 - up))
            return put_sprite(img, im, 560 + 100, 1650, fx, fy)

        def fingers(img, t_):                                                     # long pale fingers slide through the gaps
            k = ss(t_, 0.3, t2) * (1 - ss(t_, t2 + 0.6, t2 + 1.4))
            if k <= 0:
                return img
            d = ImageDraw.Draw(img)
            g = [gx for gx in B.gaps if 300 < gx < 560][:3]
            for j, gx in enumerate(g):
                for f_ in range(2):
                    y = 1080 + j * 50 + f_ * 22
                    d.line([(gx, y), (gx + 40 + 90 * k, y + 30 * k), (gx + 50 + 160 * k, y + 70 * k)], fill=GHOST + (255,), width=10, joint="curve")
            return img

        img = B.frame(t, 0, occl=occ, back=[fingers], extras=[girl], hole_extra=None)
        # the face in the hole goes on top of the cropped frame (hole at barn x - 100)
        if t > t3 + 0.3:
            k = ss(t, t3 + 0.3, jt - 0.3)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            put_kface(lay, (hx0 + hx1) / 2 - 100, hy1 - 30 + 140 * (1 - k), 0.30, t, eyes=k, grin=1.0, aura=0.0, inv=True)
            mm = Image.new("L", (W, H), 0); ImageDraw.Draw(mm).ellipse([hx0 - 100, hy0, hx1 - 100, hy1], fill=255)
            al = np.minimum(np.asarray(lay.split()[3]), np.asarray(mm)).astype(np.uint8)
            lay.putalpha(Image.fromarray(al))
            img.alpha_composite(lay)
        hit = t2 <= t < t2 + 0.1
        push = 1.08 + 0.1 * ss(t, 0, t2) + 0.25 * up
        out = to_img(finish(img, t, VIG_H, push=push, cx=560 + 120 * up, cy=1150 - 900 * up, shake=0.8 if t2 <= t < t2 + 0.4 else 0.0,
                            flash=0.5 if hit else 0.0, flash_col=(255, 40, 30)))
        put_clock(out, n_str, "03:50", t, 1.0 - up * 0.0, y=UI_Y + 360 * up)
        return to_arr(out)
    return f


def make_found(D, caps):
    B = barn()
    t2 = caps[1][1]
    beats = [t2 + 0.1 + k * 0.95 for k in range(8)]

    def f(t):
        bk = max([1 - ss(t, b, b + 0.25) if t >= b else 0 for b in beats])
        dawn = ss(t, t2, D) * 0.7

        def kid(img, t_):
            im, ax, ay = tou("sleep", 1.15)
            sx, sy = B.sack_top
            return put_sprite(img, im, sx + 40, sy + 40, ax, ay)

        def girl(img, t_):
            im, fx, fy, w = noy_crouch(1.0, look=0.2)
            return put_sprite(img, im, 560 + 100 - 120 * ss(t_, 0, 1.0), 1650, fx, fy)
        img = B.frame(t, 120 * ss(t, 0.3, 2.5), extras=[kid, girl], dawn=dawn, light=1.0 + 0.5 * bk)
        a = to_arr(img)
        if t > t2:
            add_glow(a, gsp(420, (255, 160, 90)), 540, 900, 0.35 * bk)
        out = to_img(finish(to_img(a), t, VIG_H, push=1.06 + 0.1 * ss(t, 0.3, 3.0), cx=640, cy=1250, shake=0.35 * bk))
        put_clock(out, 1, "DAWN" if t > t2 else "05:28", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_run(D, caps):
    DK = dike_set(); G = gate()
    t2, t3, t4 = caps[1][1], caps[2][1], caps[3][1]
    cut = t3 - 0.1

    def f(t):
        if t < cut:
            u = t / cut
            cam = 900 + 900 * u
            nx = 620 + cam                                                   # Noy runs right; the camera follows

            def runners(img, t_, o):
                im, fx, fy = noy((t_ * 2.6) % 1, run=1.0, scale=0.62, carry=True)
                img = put_sprite(img, im, nx + o, DK.dike_y + 6 * math.sin(t_ * 20), fx, fy)
                if t_ > 0.8:
                    gap = 700 - 460 * ss(t_, 0.8, cut)
                    gap = gap - (gap % 70)                                   # stop-motion: she jumps closer
                    step = int(t_ * 7)
                    img = put_kham(img, nx - gap + o, DK.dike_y + 4, 0.72, t_, pose="side", step=step, eyes=1.0, aura=0.5)
                return img
            img = DK.frame(t, cam, extras=[runners], dawn=0.25 * u, drum=0.6 + 0.4 * (math.sin(t * 6.6) > 0.6))
            return finish(img, t, VIG_H, push=1.06, cx=540, cy=900, shake=0.3)
        tt = t - cut
        boom = t3 + 0.3
        bk = 1 - ss(t, boom, boom + 0.5) if t >= boom else 0
        fallk = ss(t, t4 - 0.2, t4 + 0.6)
        leave = ss(t, t4 + 0.8, D - 0.2)

        def scene(img, t_):
            im, fx, fy = noy(0.0, back=True, scale=0.3, carry=True)
            img = put_sprite(img, im, 540, 1220 - 40 * ss(t_ - cut, 0, 1.2), fx, fy)
            if fallk < 0.5:
                img = put_kham(img, 540, 1880, 0.62, t_, tilt=-18, eyes=1.0, aura=0.5 + 0.4 * bk)
            else:
                img = put_kham(img, 540, 1880, 0.62, t_, pose="kneel", possessed=True, eyes=1.0 - leave, aura=0.4 * (1 - leave))
            if leave > 0:                                                        # the Phi Pop leaves her body and flies off
                m, e = shadow(0.6, 1.0, 0.0, 0.55)
                s_ = sil(m)
                s_ = with_alpha(s_, 0.95 * (1 - ss(leave, 0.7, 1.0)))
                x = 540 + 380 * leave; y = 1600 - 1250 * leave
                img.alpha_composite(s_, (int(x - s_.width / 2), int(y - s_.height)))
                for ex, ey in e:
                    eye(img, x - s_.width / 2 + ex, y - s_.height + ey, 1.0 - leave, 0.4)
            return img
        img = G.frame(t, extras=[scene], drum=bk)
        return finish(img, t, VIG_H, push=1.04 + 0.04 * tt / 4, cx=540, cy=1100, shake=0.7 * bk,
                      flash=0.35 * bk * (t < boom + 0.12), flash_col=(255, 210, 150))
    return f


def make_twist(D, caps):
    G = gate(); R = room()
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.0
    SX, SY = 560, 1420

    def f(t):
        if t < t2 - 0.1:
            def scene(img, t_):
                im, fx, fy = noy(0.0, scale=0.34, carry=True)
                img = put_sprite(img, im, 700, 1300, fx, fy)
                return put_kham(img, 430, 1800, 0.55, t_, pose="kneel", possessed=False, eyes=0, aura=0)
            img = G.frame(t, extras=[scene], drum=0.3)
            return finish(img, t, VIG_H, push=1.04 + 0.04 * t / t2, cx=540, cy=1200)
        if t >= jt:
            img = Image.new("RGBA", (W, H), (60, 8, 8, 255))
            m, e = shadow(1.0, 1.0, 0.0, 2.6, child=True)
            s_ = sil(m, col=(4, 1, 2), rim=(255, 70, 50))
            x, y = 540, 2600 + 200 * (1 - ss(t, jt, jt + 0.15))
            img.alpha_composite(s_, (int(x - s_.width / 2), int(y - s_.height)))
            for ex, ey in e:
                eye(img, x - s_.width / 2 + ex, y - s_.height + ey, 1.0, 1.4)
            fl = 0.85 if t < jt + 0.08 else 0.0
            return finish(img, t, VIG_H, push=1.0 + 0.3 * ss(t, jt, jt + 0.18), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
        neck = ss(t, t3 + 0.6, jt - 0.2)
        turn = ss(t, jt - 1.0, jt - 0.2)
        m, e = shadow(round(neck * 20) / 20, round(turn * 10) / 10, 0.0, 0.85, child=True)

        def boy(img, t_):
            im, ax, ay = tou("sit", 1.5)
            bob = 6 * math.sin(t_ * 9) * (t_ > t2)
            return put_sprite(img, im, 360 + 100, 1760 + bob, ax, ay)
        img = R.frame(t, 0, lamp=0.4, dawn=0.6, shutter=1.0, shadow=(m, SX, SY, 1.0), front=[boy])
        shadow_eyes(img, m, e, SX, SY, 0, t, turn, 0.5)
        zk = ss(t, t3, jt)
        return finish(img, t, VIG_H, push=1.04 + 0.3 * zk, cx=540 + 40 * zk, cy=1150 - 350 * zk)
    return f


def make_explain(D, caps):
    R = room()
    title = text_img("PHI POP", font(LORA, 120, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("The hungry spirit of Lao folklore", font(INTER_SB, 38), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 38)
    chips = [pill("Hides inside a living person", pf, fill=(110, 20, 24, 235), h=80),
             pill("Said to get in through careless magic", pf, fill=(110, 20, 24, 235), h=80),
             pill("A spirit doctor (mor phi) drives it out", pf, fill=(110, 20, 24, 235), h=80),
             pill("White baci strings: a Lao blessing", pf, fill=(90, 40, 10, 235), outline=(255, 200, 110, 255), h=80)]
    ts = [caps[1][1], caps[2][1], caps[2][1] + 2.6, caps[2][1] + 4.6]
    bg = {}

    def f(t):
        key = int(t * 6)
        if key not in bg:
            m, e = shadow(0.8, 1.0, 0.3, 0.85)
            img = R.frame(t, 0, lamp=1.0, shadow=(m, 720, 1420, 1.0))
            shadow_eyes(img, m, e, 720, 1420, 0, t, 1.0, 0.45)
            bg.clear(); bg[key] = finish(img, t, VIG_H, push=1.05 + 0.04 * t / D, cx=640, cy=1000) * 0.6
        out = to_img(bg[key])
        fw = flag_wave(t, 170)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 60))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 190))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 352))
        chips_at(out, chips, ts, t, 450, 96)
        return to_arr(out)
    return f


def make_outro(D, caps):
    R = room()
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("open the door?", font(LORA, 92, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Open it", (150, 30, 30, 235)), ("Stay quiet", (60, 40, 40, 235)), ("Check the strings", (140, 90, 40, 235)), ("RUN", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    knocks = [1.2 + k * 0.3 for k in range(3)] + [5.0 + k * 0.3 for k in range(3)]

    def f(t):
        ks = max([1 - ss(t, k, k + 0.15) if t >= k else 0 for k in knocks])
        img = R.frame(t, 0, lamp=0.9 - 0.2 * ks, door_shake=ks, door_light=1.0, door_fig=1.0)
        a = finish(img, t, vig=VIG_H, push=1.02, cx=540, cy=1000, shake=0.3 * ks) * 0.5
        out = to_img(a)
        fw = flag_wave(t, 170)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 130))
        out.alpha_composite(with_alpha(q, ss(t, 0, 0.6)), (int(W / 2 - q.width / 2), 300))
        out.alpha_composite(with_alpha(q2, ss(t, 0.2, 0.8)), (int(W / 2 - q2.width / 2), 420))
        yy, k = 620, 0
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
