"""Ep13 Japan / Hanako-san - scenes (2.1D survival). Each make_<id>(D, caps) returns f(t) -> float RGB (H, W, 3)."""
from art_ep13 import *

# story clock (seconds left on the dare stopwatch) per scene: (start, end)
CLOCK = {"hall": (162, 141), "knock": (118, 104), "mistake": (98, 86), "cliff": (78, 61),
         "recap": (44, 40), "chalk": (36, 27), "stairs": (16, 0)}


def clock(sid, t, D):
    a, b = CLOCK[sid]
    return a + (b - a) * min(1.0, t / D)


def fist(knock=0.0, open_hand=False):
    """Yui's right hand + navy sleeve coming in from the lower right. knock 0..1 = how far forward (toward the door)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hx, hy = 690 - 60 * knock, 1080 - 20 * knock
    def sleeve(d, s):
        d.polygon(P_((W + 60, 1500), (W + 60, 1900), (hx + 210, 1330), (hx + 120, 1180), s=s), fill=255)
    def arm(d, s):
        d.line([((hx + 170) * s, 1260 * s), (hx * s, hy * s)], fill=255, width=int(96 * s))
        if open_hand:
            d.ellipse([(hx - 80) * s, (hy - 70) * s, (hx + 60) * s, (hy + 70) * s], fill=255)
            for k in range(4):
                d.line([((hx - 40) * s, (hy - 40 + k * 26) * s), ((hx - 150) * s, (hy - 60 + k * 30) * s)], fill=255, width=int(26 * s))
        else:
            d.rounded_rectangle([(hx - 90) * s, (hy - 70) * s, (hx + 50) * s, (hy + 70) * s], int(40 * s), fill=255)
    lay.alpha_composite(shade(arm, (W, H), SKIN, 40, rim=(255, 120, 90)))
    lay.alpha_composite(shade(sleeve, (W, H), NAVY, 50))
    if not open_hand:
        d = ImageDraw.Draw(lay)
        for k in range(3):
            d.line([(hx - 86, hy - 40 + k * 34), (hx - 40, hy - 40 + k * 34)], fill=(140, 90, 66, 255), width=4)
    return lay


_FI = {}


def fist_c(knock, open_hand=False):
    k = (round(knock, 1), open_hand)
    if k not in _FI:
        _FI[k] = fist(knock, open_hand)
    return _FI[k]


def knock_curve(t, t0, n=3, per=0.55):
    """0..1 forward motion for n knocks starting at t0."""
    for i in range(n):
        a = t0 + i * per
        if a <= t < a + per:
            u = (t - a) / per
            return math.sin(math.pi * min(1, u / 0.5)) if u < 0.5 else 0.0
    return 0.0


# ============================================================ PART 1
def make_hook(D, caps):
    DF = doorfront()
    hdr = series_header("JAPAN", "PART 1")
    t0 = 1.2
    cut = caps[1][1] - 0.1

    def f(t):
        kn = knock_curve(t, t0, 3, 0.62)
        if t < cut:
            img = DF.frame(t, occupied=0, glow=0.35)
            img.alpha_composite(fist_c(kn))
            hit = any(t0 + i * 0.62 + 0.14 <= t < t0 + i * 0.62 + 0.22 for i in range(3))
            a = finish(img, t, VIG_H, push=1.12 + 0.1 * t / cut, cx=560, cy=1000, shake=0.35 if hit else 0.0)
        else:
            tt = t - cut
            def gap(img, t_):
                # under the door: two small red shoes step into the light
                k = ss(tt, 0.15, 0.5)
                return red_shoes(img, 540, 1752, 1.15, k, step=int(tt / 0.4))
            img = DF.frame(t, occupied=1 if tt > 0.1 else 0, gap=gap, glow=1.0)
            fl = 0.55 if tt < 0.07 else 0.0
            a = finish(img, t, VIG_H, push=1.25 + 0.2 * ss(tt, 0, 0.4), cx=540, cy=1500, shake=0.6 * (1 - ss(tt, 0, 0.6)),
                       flash=fl, flash_col=(255, 30, 20))
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def friends(img, t, P):
    """Two friends by the bikes (silhouettes with phone lights), small, in the yard."""
    for x, ph in ((780, 0.0), (900, 0.4)):
        h, fx, fy, pp = yui(ph, scale=0.42)
        dark = tint(h, (0.25, 0.18, 0.18))
        img.alpha_composite(dark, (int(x - fx + P(1.0)), int(1640 - fy)))
        img = glow_on(img, gsp(40, (255, 240, 210)), x - fx + pp[0] + P(1.0), 1640 - fy + pp[1], 0.8)
    return img


def make_dare(D, caps):
    S = school(0)
    t3 = caps[2][1]
    bw = S.bath_win

    def f(t):
        def win(lay, tt):
            if 3.4 < tt < 6.2:                                     # only the viewer sees her: a small girl in the red window
                k = ss(tt, 3.4, 3.7) * (1 - ss(tt, 5.8, 6.2))
                g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                g = put_hanako(g, (bw[0] + bw[2]) / 2, bw[3] - 2, 0.1, tt, eyes=1.0, aura=0.3, sway=False)
                lay.alpha_composite(with_alpha(g, k))
            return lay
        def yard(img, tt, P):
            h, fx, fy, _ = yui(0.0, back=True, scale=0.62)
            img.alpha_composite(h, (int(560 - fx + P(0.9)), int(1760 - fy)))
            return friends(img, tt, P)
        img = S.frame(t, cam=-30 + 60 * t / D, extra_win=win, extra_yard=yard)
        fog(img, t, 0.25, 1150, 1500, speed=10, col=(160, 50, 40))
        push = 1.0 + 0.35 * ss(t, 1.0, 6.0)
        cxx = 540 + (bw[0] - 380) * ss(t, 1.0, 6.0); cyy = 1100 - 180 * ss(t, 1.0, 6.0)
        if t > t3 - 0.3:
            push = 1.06; cxx = 540; cyy = 1150
        out = to_img(finish(img, t, VIG_H, push=push, cx=cxx, cy=cyy))
        if t > t3 - 0.2:
            put_timer(out, 180, t, ss(t, t3 - 0.2, t3 + 0.3), floor="1F")
        return to_arr(out)
    return f


def make_rule(D, caps):
    B = bathroom()
    f1 = font(INTER_SB, 44)
    chips = [pill("1. KNOCK 3 TIMES ON STALL 3", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("2. \"HANAKO-SAN, ARE YOU THERE?\"", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("3. IF SHE ANSWERS... NEVER OPEN", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [caps[0][1] + 1.2, caps[1][1], caps[2][1]]
    x3, y3 = B.P.p(B.SF, 1.1, 3.3)

    def f(t):
        def gh(img, tt):
            # a faint small girl standing in front of stall 3 (memory / legend)
            k = 0.55 * ss(tt, 2.0, 4.0)
            if k > 0:
                g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                g = put_hanako(g, x3 - 70, y3, B.P.scale_at(3.3, 1.15, 930), tt, eyes=1.0, aura=0.4, sway=False)
                img.alpha_composite(with_alpha(g, k))
            return img
        img = B.frame(t, bulb=0.9, extras=[(3.3, gh)], gap_glow=0.9)
        a = to_arr(img)
        lum = a.mean(2, keepdims=True)                                     # faded memory (sepia-red)
        a = a * 0.4 + lum * np.array([1.3, 0.8, 0.6]) * 0.6
        a *= 0.92 + 0.08 * math.sin(t * 40)
        img = to_img(a)
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.15, tt + 0.3)
            if k > 0:
                cc = c if c.width <= W - 40 else c.resize((W - 40, int(c.height * (W - 40) / c.width)), Image.LANCZOS)
                img.alpha_composite(with_alpha(cc, k), (int(W / 2 - cc.width / 2), int(250 + i * 120 + 20 * (1 - k))))
        return finish(img, t, vig=VIG_H, push=1.0 + 0.08 * t / D, cx=640, cy=1000)
    return f


def make_hall(D, caps):
    C = corridor()
    P = C.P
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        z = 1.5 + 0.6 * t / D
        def y_(img, tt):
            sc = P.scale_at(z, 1.6, 836)
            h, fx, fy, _ = yui((tt * 1.1) % 1, back=True, scale=sc)
            x, yy = P.p(-0.35, C.FL, z)
            img.alpha_composite(h, (int(x - fx), int(yy - fy)))
            return img
        ex = []
        if t2 - 0.3 < t < t2 + 1.6:
            # a small red skirt dashes across the far end of the hall in jerky stop-motion jumps
            u = ss(t, t2 - 0.3, t2 + 1.6)
            sx = 0.58 - 0.7 * (int(u * 6) / 6)
            def hn(img, tt, sx=sx):
                xx, yy = P.p(sx, C.FL, 4.2)
                return put_hanako(img, xx, yy, P.scale_at(4.2, 1.15, 930), tt, eyes=1.0, aura=0.6, step=int(tt * 8), sway=False)
            ex.append((4.2, hn))
        ex.append((z, y_))
        # the light flickers once she has passed
        lt = 1.0 if t < t2 + 1.6 else (0.25 if math.sin(t * 37) > 0.2 else 0.9)
        img = C.frame(t, light=lt, extras=ex)
        fog(img, t, 0.12, 700, 1700, speed=6, col=(140, 60, 50))
        zk = ss(t, t2 - 0.4, t2 + 0.2) * (1 - ss(t, t3, t3 + 0.6))
        push = 1.08 + 0.1 * t / D + 0.35 * zk
        out = to_img(finish(img, t, VIG_H, push=push, cx=540 + 60 * zk, cy=950 + 60 * zk))
        put_timer(out, clock("hall", t, D), t, floor="3F")
        return to_arr(out)
    return f


def make_knock(D, caps):
    B = bathroom(); DF = doorfront(); P = B.P
    t1, t2, t3 = caps[0][1] + 1.0, caps[1][1], caps[2][1]
    ans = caps[2][1] + 1.3                     # "Yes. I'm here."

    def f(t):
        if t < t1:
            z = 1.3 + 1.2 * ss(t, 0, t1)
            def y_(img, tt):
                h, fx, fy, _ = yui((tt * 1.1) % 1, back=True, scale=P.scale_at(z, 1.6, 836))
                x, yy = P.p(0.2, B.FL, z)
                img.alpha_composite(h, (int(x - fx), int(yy - fy)))
                return img
            img = B.frame(t, extras=[(z, y_)], gap_glow=0.8)
            out = to_img(finish(img, t, VIG_H, push=1.1 + 0.15 * t / t1, cx=640, cy=1000))
        else:
            tt = t - t1
            kn = knock_curve(t, t1 + 0.15, 3, 0.55)
            def gap(img, t_):
                if t_ > ans:
                    return red_shoes(img, 540, 1752, 1.15, ss(t_, ans, ans + 0.3), step=0)
                return img
            img = DF.frame(t, occupied=1 if t > ans else 0, gap=gap, glow=0.4 + 0.6 * ss(t, ans - 0.2, ans + 0.2))
            img.alpha_composite(fist_c(kn if t < t2 + 0.5 else 0.0))
            hit = any(t1 + 0.15 + i * 0.55 + 0.12 <= t < t1 + 0.15 + i * 0.55 + 0.2 for i in range(3))
            push = 1.08 + 0.05 * tt + 0.25 * ss(t, ans, ans + 0.4)
            out = to_img(finish(img, t, VIG_H, push=push, cx=560, cy=1000 + 600 * ss(t, ans, ans + 0.4), shake=0.3 if hit else 0))
        put_timer(out, clock("knock", t, D), t)
        return to_arr(out)
    return f


def mirror_bg():
    """The cracked mirror above the sinks, seen straight on (Yui's reflection goes in it)."""
    a = vgrad((40, 30, 32), (60, 44, 44), (30, 22, 24), ym=0.5)
    img = to_img(a); d = ImageDraw.Draw(img)
    d.rectangle([40, 140, W - 40, 1500], fill=(70, 60, 60, 255))
    d.rectangle([70, 170, W - 70, 1470], fill=(26, 20, 24, 255))
    return img


_MB = None


def make_mistake(D, caps):
    global _MB
    DF = doorfront()
    t1, t2, t3 = caps[1][1], caps[2][1], caps[2][1] + 1.7
    if _MB is None:
        _MB = mirror_bg()
    MB = _MB
    cracks = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(cracks)
    rng = np.random.default_rng(5)
    for k in range(9):
        a = rng.uniform(0, 2 * math.pi); r = rng.uniform(300, 700)
        cd.line([(760, 420), (760 + 120 * math.cos(a), 420 + 120 * math.sin(a)), (760 + r * math.cos(a + 0.1), 420 + r * math.sin(a + 0.1))],
                fill=(200, 190, 190, 200), width=3)

    def f(t):
        if t < t2 - 0.1:
            u = ss(t, t1 - 0.2, t1 + 1.6)
            img = DF.frame(t, open_u=u, occupied=1)
            if u < 0.05:
                img.alpha_composite(fist_c(0.0, open_hand=True))
            out = to_img(finish(img, t, VIG_H, push=1.08 + 0.12 * ss(t, t1, t2), cx=560, cy=1100))
            put_timer(out, clock("mistake", t, D), t)
            return to_arr(out)
        # the mirror: Yui's reflection... and a little girl right behind her shoulder
        tt = t - (t2 - 0.1)
        img = MB.copy()
        inner = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        k = ss(t, t3 - 0.9, t3)
        if k > 0:
            inner = put_hface(inner, 800, 600, 0.55, t, eyes=k, tilt=-18, aura=0.5 * k, alpha=k)
        fc = yui_face(look=0.6 * ss(t, t3, t3 + 0.3), mouth=0.3 + 0.4 * ss(t, t3, t3 + 0.3))
        fc = fc.resize((int(fc.width * 0.85), int(fc.height * 0.85)), Image.LANCZOS)
        inner.alpha_composite(fc, (-40, 420))
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([70, 170, W - 70, 1470], fill=255)
        ia = np.asarray(inner, np.float32).copy(); ia[..., 3] *= np.asarray(m, np.float32) / 255
        img.alpha_composite(tint(Image.fromarray(ia.astype(np.uint8), "RGBA"), (0.85, 0.75, 0.75)))
        img.alpha_composite(cracks)
        a = to_arr(img); add_glow(a, gsp(500, (255, 180, 130)), 540, 60, 0.4)
        img = to_img(a)
        fl = 0.7 if t3 <= t < t3 + 0.08 else 0.0
        sh = 0.8 * (1 - ss(t, t3, t3 + 0.7)) if t > t3 else 0.0
        push = 1.04 + 0.05 * tt + (0.3 * ss(t, t3, t3 + 0.2) if t > t3 else 0)
        out = to_img(finish(img, t, VIG_H, push=push, cx=720 if t > t3 else 540, cy=640 if t > t3 else 820, shake=sh, flash=fl, flash_col=(255, 30, 20)))
        put_timer(out, clock("mistake", t, D), t)
        return to_arr(out)
    return f


def make_cliff(D, caps):
    C = corridor(); U = underdesk(); P = C.P
    t1, t2 = caps[1][1], caps[2][1]
    jt = caps[2][2] + 0.15

    def f(t):
        if t >= jt:
            img = Image.new("RGBA", (W, H), (8, 2, 3, 255))
            img = put_hface(img, 540, 1060, 1.5, t, eyes=1.0, mouth=0.5, tilt=180, aura=0.8)        # upside down, from above
            fl = 0.85 if t < jt + 0.08 else 0.0
            a = finish(img, t, vig=VIG_H, push=1.0 + 0.6 * ss(t, jt, jt + 0.25), cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
            if t > D - 0.45:
                a *= 0.0
            return a
        if t < t1 - 0.15:
            # the lights die; Yui runs toward us down the dark corridor
            z = 3.0 - 1.9 * ss(t, 0.4, t1 - 0.15)
            def y_(img, tt):
                h, fx, fy, _ = yui((tt * 2.0) % 1, run=1.0, scale=P.scale_at(z, 1.6, 836), phone=False)
                x, yy = P.p(0.0, C.FL, z)
                img.alpha_composite(h, (int(x - fx), int(yy - fy)))
                return img
            lt = 0.6 if (t < 0.6 and math.sin(t * 50) > 0) else 0.08
            img = C.frame(t, light=lt, extras=[(z, y_)])
            img = to_img(to_arr(img) * (0.45 if lt < 0.5 else 0.8))
            out = to_img(finish(img, t, VIG_H, push=1.06, cx=540, cy=950, shake=0.25))
            put_timer(out, clock("cliff", t, D), t)
            return to_arr(out)
        # under the desk: small red shoes walk in, tap... tap... tap... and stop right beside her
        tt = t - (t1 - 0.15)
        steps_ = int(max(0, t - t1) / 0.7)
        u = min(1.0, steps_ / 6)
        side = -2.1 + 3.0 * u; z = 7.0 - 5.7 * u
        def sh(img, t_):
            x, y = U.floor_xy(side, z)
            return shoes_legs(img, x, y, U.P.scale_at(z, 0.45, 300), step=steps_)
        img = U.frame(t, extras=[(z, sh)])
        push = 1.03 + 0.04 * math.sin(t * 1.3) + 0.2 * ss(t, t2, jt)
        out = to_img(finish(img, t, VIG_H, push=push, cx=540 + 200 * ss(t, t2, jt), cy=1000))
        put_timer(out, clock("cliff", t, D), t)
        return to_arr(out)
    return f


# ============================================================ PART 2
def make_recap(D, caps):
    U = underdesk()
    hdr = series_header("JAPAN", "PART 2")

    def f(t):
        def sh(img, t_):
            x, y = U.floor_xy(0.9, 1.3)
            return shoes_legs(img, x, y, U.P.scale_at(1.3, 0.45, 300), step=0)
        img = U.frame(t, extras=[(1.3, sh)])
        h, fx, fy = yui_crouch(1.2, look=1.0)
        tr = 3 * math.sin(t * 31)
        img.alpha_composite(h, (int(150 - fx + tr), int(1900 - fy)))
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.06 * t / D, cx=560, cy=1100))
        put_header(out, hdr, t)
        put_timer(out, clock("recap", t, D), t, y=1180)
        return to_arr(out)
    return f


def make_chalk(D, caps):
    BB = blackboard()
    t1 = caps[1][1]
    hit = caps[1][2] + 0.15

    def f(t):
        if t >= hit:
            img = Image.new("RGBA", (W, H), (8, 2, 3, 255))
            bg = BB.frame(t, write=(1, 1, 1))
            img.alpha_composite(dof(bg, 10))
            img = to_img(to_arr(img) * 0.4)
            img = put_hface(img, 540, 960, 1.35, t, eyes=1.0, mouth=0.7, tilt=-22, aura=0.8)
            fl = 0.85 if t < hit + 0.08 else 0.0
            return finish(img, t, VIG_H, push=1.0 + 0.4 * ss(t, hit, hit + 0.2), cx=540, cy=900, shake=1.0 * (1 - ss(t, hit, hit + 0.8)),
                          flash=fl, flash_col=(255, 30, 20))
        w1 = ss(t, t1 + 0.3, t1 + 1.8); w2 = ss(t, t1 + 1.9, t1 + 3.1); w3 = ss(t, t1 + 3.2, hit - 0.2)
        img = BB.frame(t, write=(w1, w2, w3))
        if t < t1:
            # peeking out from under the desk: the desk edge at the bottom of the frame
            d = ImageDraw.Draw(img)
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.1 * t / hit, cx=540, cy=820 + 60 * ss(t, t1, hit)))
        put_timer(out, clock("chalk", t, D), t, y=1560)
        return to_arr(out)
    return f


def make_stairs(D, caps):
    S = stairs()
    t2, t3 = caps[1][1], caps[2][1]
    f1 = caps[0][1] + 2.0                     # 3F -> 2F

    def f(t):
        if t < f1:
            lab, fl = "3F", ss(t, f1 - 0.3, f1) * 0.5
        elif t < t2:
            lab, fl = "2F", 0.5 - 0.5 * ss(t, f1, f1 + 0.3)
            if t > t2 - 0.3:
                fl = ss(t, t2 - 0.3, t2) * 0.5
        else:
            lab, fl = "3F", 0.5 - 0.5 * ss(t, t2, t2 + 0.3)
        # she runs down the flight again and again (it loops)
        seg = 0 if t < f1 else (1 if t < t2 else 2)
        st0 = (0, f1, t2)[seg]; st1 = (f1, t2, D)[seg]
        u = ss(t, st0, st1)
        x = 120 + 860 * u
        def y_(img, tt):
            h, fx, fy, _ = yui((tt * 2.2) % 1, run=1.0, scale=0.62, phone=False)
            img.alpha_composite(h, (int(x - fx), int(S.surf(x) - fy + 6)))
            if t > t3:
                img = shoes_legs(img, 70, S.Y0, 0.42, step=0, k=ss(t, t3, t3 + 0.4))
            return img
        img = S.frame(t, lab, flip=fl, extras=[(1, y_)])
        out = to_img(finish(img, t, VIG_H, push=1.12, cx=x + 60, cy=S.surf(x) - 250, shake=0.2))
        if t < t3:
            put_timer(out, clock("stairs", t, t3), t, floor=lab)
        else:
            put_timer(out, 0, t, floor="3F")
        return to_arr(out)
    return f


def make_escape(D, caps):
    S = school(1)
    t2, t3 = caps[1][1], caps[2][1]
    bw = S.bath_win

    def f(t):
        u = ss(t, 0.0, D)
        def win(lay, tt):
            if tt > t3:
                k = ss(tt, t3, t3 + 0.5)
                g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                g = put_hanako(g, (bw[0] + bw[2]) / 2, bw[3] - 2, 0.1, tt, eyes=1.0, wave=0.5 + 0.5 * math.sin(tt * 5), aura=0.4, sway=False)
                lay.alpha_composite(with_alpha(g, k))
            return lay
        def yard(img, tt, P):
            # Hanako at the dark entrance, watching her go (gone from there once she's in the window)
            k = 1 - ss(tt, t3 - 0.2, t3 + 0.2)
            if k > 0:
                g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                g = put_hanako(g, 655 + P(0.35), GY, 0.17, tt, eyes=1.0, aura=0.5, sway=False)
                img.alpha_composite(with_alpha(g, k))
            sc = 0.3 + 0.65 * u
            h, fx, fy, _ = yui((tt * 1.0) % 1, scale=sc, phone=False)
            img.alpha_composite(h, (int(470 - fx + P(0.9)), int(GY + 40 + 560 * u - fy)))
            for x in (820, 900):                                       # her friends' phone lights by the gate
                img = glow_on(img, gsp(50, (255, 240, 210)), x + P(1.0), 1560, 0.7 + 0.2 * math.sin(tt * 3 + x))
            return img
        img = S.frame(t, cam=20 * math.sin(t * 0.3), extra_win=win, extra_yard=yard, bikes=True)
        fog(img, t, 0.3, 1200, 1700, speed=12, col=(120, 40, 36))
        push = 1.08 + 0.05 * u
        cyy = 1200 if t < t3 else 1200 - 250 * ss(t, t3 + 0.6, t3 + 2.0)
        cxx = 540 if t < t3 else 540 + 300 * ss(t, t3 + 0.6, t3 + 2.0)
        pz = push + (0.5 * ss(t, t3 + 0.6, t3 + 2.0) if t > t3 else 0)
        return finish(img, t, VIG_H, push=pz, cx=cxx, cy=cyy)
    return f


def make_twist(D, caps):
    PH = phone()
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.0

    def f(t):
        if t >= jt:
            img = Image.new("RGBA", (W, H), (8, 2, 3, 255))
            img = put_hface(img, 540, 960, 1.5, t, eyes=1.0, mouth=0.6, tilt=8, aura=0.8)
            fl = 0.85 if t < jt + 0.08 else 0.0
            return finish(img, t, VIG_H, push=1.0 + 0.5 * ss(t, jt, jt + 0.2), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
        g = ss(t, t3 - 0.1, t3 + 0.4)
        img = PH.frame(t, ghost=g, wave=0.5 + 0.5 * math.sin(t * 6))
        push = 1.02 + 0.08 * ss(t, 0, t2) + 0.5 * ss(t, t3 + 0.8, jt)
        cyy = 960 + 0 * t
        return finish(img, t, VIG_H, push=push, cx=560, cy=900 * ss(t, t3 + 0.8, jt) + 960 * (1 - ss(t, t3 + 0.8, jt)))
    return f


def make_explain(D, caps):
    B = bathroom()
    x3, y3 = B.P.p(B.SF, 1.1, 3.3)
    title = text_img("HANAKO-SAN", font(LORA, 112, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("Hanako of the toilet: Japan's school ghost", font(INTER_SB, 36), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("The ghost of a little girl in school toilets", pf, fill=(110, 20, 24, 235), h=80),
             pill("Third stall, often on the third floor", pf, fill=(110, 20, 24, 235), h=80),
             pill("Knock 3 times: \"Hanako-san, are you there?\"", pf, fill=(110, 20, 24, 235), h=80),
             pill("Bob haircut, red skirt", pf, fill=(110, 20, 24, 235), h=80)]
    ts = [caps[0][1] + 2.4, caps[1][1], caps[2][1], caps[2][1] + 2.2]

    def f(t):
        def gh(img, tt):
            return put_hanako(img, x3 - 70, y3, B.P.scale_at(3.3, 1.15, 930), tt, eyes=1.0, aura=0.5, tilt=-10 * ss(tt, 4, 6))
        img = B.frame(t, extras=[(3.3, gh)], gap_glow=1.0)
        a = finish(img, t, vig=VIG_H, push=1.05 + 0.05 * t / D, cx=640, cy=1100)
        out = to_img(a * 0.75)
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
    C = corridor(); P = C.P
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("knock 3 times?", font(LORA, 96, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Knock!", (120, 25, 25, 235)), ("Walk away", (60, 40, 40, 235)), ("Bring a friend", (140, 70, 20, 235)), ("NEVER", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)

    def f(t):
        # she gets closer every few seconds (stop-motion), down the corridor
        z = max(2.4, 6.0 - 1.2 * int(t / 2.2))
        def hn(img, tt):
            xx, yy = P.p(0.0, C.FL, z)
            return put_hanako(img, xx, yy, P.scale_at(z, 1.15, 930), tt, eyes=1.0, aura=0.6, tilt=-14, sway=False)
        img = C.frame(t, light=0.6, extras=[(z, hn)])
        a = finish(img, t, vig=VIG_H, push=1.02, cx=540, cy=1000) * 0.55
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
