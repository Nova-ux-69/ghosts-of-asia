"""Ep16 Indonesia / Kuntilanak - scenes (2.1D survival). Each make_<id>(D, caps) returns f(t) -> float RGB (H, W, 3)."""
from art_ep16 import *

if os.environ.get("NO_UI"):                       # covers: no laugh meter under the cover header
    def put_ui(*a, **k):
        pass

UI_Y = 200


def chips_at(out, chips, ts, t, y0, gap=110):
    for i, (c, tt) in enumerate(zip(chips, ts)):
        k = ss(t, tt - 0.15, tt + 0.3)
        if k > 0:
            cc = c if c.width <= W - 40 else c.resize((W - 40, int(c.height * (W - 40) / c.width)), Image.LANCZOS)
            out.alpha_composite(with_alpha(cc, k), (int(W / 2 - cc.width / 2), int(y0 + i * gap + 20 * (1 - k))))


def put_sprite(img, spr, x, y, fx, fy):
    img.alpha_composite(spr, (int(x - fx), int(y - fy)))
    return img


def jump(t, jt, inv=False, scale=1.3, y=880, tilt=0.0, x=540, bg=(6, 1, 2)):
    img = kface_full(t, jt, inv=inv, scale=scale, y=y, tilt=tilt, x=x, bg=bg)
    fl = 0.85 if t < jt + 0.08 else 0.0
    return finish(img, t, VIG_H, push=1.0 + 0.4 * ss(t, jt, jt + 0.18), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))


def stop_motion(u, steps):
    """Quantise 0..1 into jerky steps (she is suddenly closer)."""
    return math.floor(u * steps) / steps


# ============================================================ PART 1
def make_hook(D, caps):
    B = boardwalk()
    hdr = series_header("INDONESIA", "PART 1")
    t2 = caps[1][1]
    soft = t2 + 1.2
    jt = caps[1][2] - 0.6

    def f(t):
        if t >= jt:
            return jump(t, jt, scale=1.35, tilt=-12, x=600)
        if t < t2:
            z = 30.0
        else:
            z = 30.0 - 26.0 * stop_motion(ss(t, t2 - 0.1, jt - 0.3), 4)

        def her(img, t_):
            x, y, s = B.at(z, 0.0)
            return put_kunti(img, x, y + 6 * math.sin(t_ * 2), s * 0.95, t_, eyes=1.0, aura=0.5)
        img = B.frame(t, extras=[her], petals=0.5)
        cut = t2 <= t < t2 + 0.06 or (t2 > 0 and any(abs(t - (t2 + k * (jt - 0.3 - t2) / 4)) < 0.04 for k in range(1, 4)))
        a = finish(img, t, VIG_H, push=1.04 + 0.05 * t / D, cx=540, cy=900, flash=0.3 if cut else 0.0, flash_col=(255, 40, 30))
        out = to_img(a)
        put_header(out, hdr, t)
        near = 0.0 if t < soft else 1.0
        put_ui(out, near, "300 M", t, ss(t, 0.6, 1.0), y=640)
        return to_arr(out)
    return f


def make_setup(D, caps):
    R = riverfront()
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        cam = -60 + 140 * t / D

        def girl(img, t_, o):
            wipe = math.sin(t_ * 5) > 0 and t_ < t3
            im, fx, fy = putri(0.2 if wipe else 0.0, scale=0.56)
            return put_sprite(img, im, 1020 + o - 150, 1600, fx, fy)

        def watcher(img, t_, o):                                 # the viewer sees her first, up in the banyan
            k = ss(t_, t2 + 1.2, t2 + 2.0)
            if k <= 0:
                return img
            px, py = R.perch
            return put_kunti(img, px + o - 150, py, 0.24, t_, pose="perch", alpha=k, aura=0.4)
        img = R.frame(t, cam, extras=[girl], tree_extras=[watcher])
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.06 * t / D, cx=600, cy=1000))
        put_ui(out, 0.0, "300 M", t, ss(t, t3 - 0.2, t3 + 0.3), y=UI_Y)
        return to_arr(out)
    return f


def make_rule(D, caps):
    B = boardwalk()
    f1 = font(INTER_SB, 44)
    chips = [pill("GRANDMA'S RULES", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 220, 160, 255), h=86),
             pill("1. SMELL FRANGIPANI? NEVER LOOK UP", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("2. LOUD LAUGH = SHE'S FAR", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("3. SOFT LAUGH = SHE'S NEAR", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [0.3, caps[1][1] + 0.3, caps[2][1] + 0.3, caps[2][1] + 2.4]
    rnd = np.random.default_rng(5)
    big = [(rnd.uniform(80, W - 80), rnd.uniform(700, 1800), rnd.uniform(70, 130), rnd.uniform(0, 360), rnd.uniform(20, 50)) for _ in range(9)]
    bg = {}

    def f(t):
        key = int(t * 6)
        if key not in bg:
            b = B.frame(t, petals=0.0).filter(ImageFilter.GaussianBlur(7))
            a = to_arr(b); lum = a.mean(2, keepdims=True)
            a = a * 0.5 + lum * np.array([1.4, 0.85, 0.65]) * 0.5                       # a faded memory tint
            bg.clear(); bg[key] = to_img(a * 0.75)
        img = bg[key].copy()
        for x, y, sz, r0, vy in big:                                                # big frangipani flowers drifting down
            fl = flower(sz, r0 + 30 * t)
            if sz > 110:
                fl = fl.filter(ImageFilter.GaussianBlur(4))
            yy = (y + vy * t) % (H + 200) - 100
            img.alpha_composite(fl, (int(x + 20 * math.sin(t + x) - fl.width / 2), int(yy - fl.height / 2)))
        out = to_img(finish(img, t, VIG_H, push=1.03 + 0.05 * t / D, cx=540, cy=1000))
        chips_at(out, chips, ts, t, 230, 118)
        return to_arr(out)
    return f


def make_smell(D, caps):
    B = boardwalk()
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        z = 3.2 + 1.6 * t / D                                                      # Putri walks away from us

        def scene(img, t_):
            px, py, s = B.at(z, 0.15)
            im, fx, fy = putri((t_ * 1.6) % 1, back=True, scale=s * 1.05)
            img = put_sprite(img, im, px, py, fx, fy)
            k = ss(t_, t3 - 0.3, t3 + 0.6)                                           # she hangs in the far banyan
            if k > 0:
                tx, ty = B.tree_top
                img = put_kunti(img, tx - 60, ty + 120, 0.16, t_, pose="perch", alpha=k, aura=0.6)
            return img
        img = B.frame(t, extras=[scene], petals=ss(t, t2 - 0.5, t2 + 1.0))
        zk = ss(t, t3, D)
        out = to_img(finish(img, t, VIG_H, push=1.06 + 0.08 * t / D + 0.5 * zk, cx=540 - 40 * zk, cy=1000 - 230 * zk))
        put_ui(out, 0.1, "150 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_laugh(D, caps):
    B = boardwalk(flip=True)
    t2, t3 = caps[1][1], caps[2][1]
    soft = t3 + 1.3

    def f(t):
        z = 4.4 - 0.9 * t / D                                                      # Putri walks toward us

        def scene(img, t_):
            if t_ < soft:
                x, y, s = B.at(26.0, -0.2)
                img = put_kunti(img, x, y, s * 0.95, t_, aura=0.5, alpha=ss(t_, 0.6, 1.4))
            px, py, s = B.at(z, 0.0)
            look = 0.0
            im, fx, fy = putri((t_ * 1.6) % 1 if t_ < soft else 0.0, scale=s * 1.05, look=look)
            img = put_sprite(img, im, px, py, fx, fy)
            if t_ >= soft:                                                         # right behind her shoulder now
                k = ss(t_, soft, soft + 0.05)
                img_k = put_kunti(Image.new("RGBA", (W, H), (0, 0, 0, 0)), px + 150, py + 40, s * 1.15, t_, aura=0.6, eyes=1.0)
                img.alpha_composite(with_alpha(img_k, k))
                im, fx, fy = putri(0.0, scale=s * 1.05, look=look)                  # Putri stays in front
                img = put_sprite(img, im, px, py, fx, fy)
            return img
        img = B.frame(t, extras=[scene], petals=0.4)
        hit = soft <= t < soft + 0.1
        zk = ss(t, soft, D)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.04 * t / D + 0.3 * zk, cx=560 + 60 * zk, cy=1000 - 150 * zk,
                            shake=0.6 if hit else 0.0, flash=0.4 if hit else 0.0, flash_col=(255, 40, 30)))
        near = 0.05 if t < t3 + 0.6 else (0.5 if t < soft else 1.0)
        put_ui(out, near, "120 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_mistake(D, caps):
    U = banyan_up(); R = riverfront()
    t2 = caps[1][1]
    up = t2 + 1.2                                                                 # "...and looked up."
    jt = caps[1][2] - 0.05

    def f(t):
        if t >= jt:
            return jump(t, jt, inv=False, scale=1.45, y=820)
        if t < up:
            # at the foot of the banyan: roots like curtains, she stops
            RD = ronda()

            def girl(img, t_, o):
                im, fx, fy = putri((t_ * 1.5) % 1 if t_ < t2 else 0.0, scale=0.7, look=1.0 * ss(t_, t2 + 0.5, up))
                return put_sprite(img, im, 520 + 60 * ss(t_, 0, t2), RD.walk_y + 10, fx, fy)
            img = RD.frame(t, 480 + 30 * t / up, extras=[girl])
            zk = ss(t, t2, up)
            out = to_img(finish(img, t, VIG_H, push=1.1 + 0.2 * zk, cx=540, cy=1100 - 250 * zk))
            put_ui(out, 1.0, "100 M", t, 1.0, y=UI_Y)
            return to_arr(out)
        # POV: looking up into the banyan. She is crouched on a branch... and her head turns down to us.
        k = ss(t, up, up + 0.4)

        def her(img, t_):
            px, py = U.perch
            drop = 200 * ss(t_, jt - 0.6, jt)
            return put_kunti(img, px + 120 * ss(t_, jt - 0.6, jt), py + drop, 0.62 + 0.5 * ss(t_, jt - 0.6, jt), t_, pose="perch", aura=0.7)
        img = U.frame(t, extras=[her])
        a = finish(img, t, VIG_H, push=1.05 + 0.15 * ss(t, up, jt), cx=420, cy=800, rotate=6 * (1 - k))
        out = to_img(a)
        put_ui(out, 1.0, "100 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_cliff(D, caps):
    RD = ronda(); UH = under_house()
    t2, t3 = caps[1][1], caps[2][1]
    cut = caps[0][2] - 0.8
    jt = D - 1.1

    def f(t):
        if t < cut:
            u = t / cut
            cam = -150 + 260 * u

            def runner(img, t_, o):
                im, fx, fy = putri((t_ * 2.6) % 1, run=1.0, scale=0.5)
                return put_sprite(img, im, 200 + 700 * u + o, RD.walk_y + 6 * math.sin(t_ * 20), fx, fy)

            def flyer(img, t_, o):                                              # she follows, gliding over the roofs
                gap = 520 - 160 * stop_motion(u, 4)
                return put_kunti(img, 200 + 700 * u + o - gap, 1150 + 30 * math.sin(t_ * 3), 0.34, t_, rot=-70, aura=0.6)
            img = RD.frame(t, cam, extras=[runner, flyer], lights=0.0)
            return finish(img, t, VIG_H, push=1.08, cx=540, cy=1100, shake=0.3)
        if t >= jt:
            return jump(t, jt, inv=True, scale=1.35, y=820)
        drop = ss(t, t2 + 0.3, t2 + 1.2)
        (gx0, gy0), (gx1, gy1) = UH.gap

        def hanging(img, t_):
            if drop <= 0:
                return img
            sway = 0.5 * math.sin(t_ * 1.2)
            y = -900 + 1142 * ease(drop)
            return put_kunti(img, 640 + 10 * math.sin(t_ * 0.8), y, 0.62, t_, pose="hang", sway=sway, aura=0.6, eyes=ss(t_, t3, t3 + 0.6))

        def girl(img, t_):
            im, fx, fy = putri_crouch(1.0, look=0.6 * ss(t_, t2 + 1.0, t2 + 1.6), cover=ss(t_, t2 + 0.8, t2 + 1.3))
            return put_sprite(img, im, 380, 1760, fx, fy)
        img = UH.frame(t, extras=[hanging, girl])
        push = 1.04 + 0.22 * ss(t, t2, jt)
        out = to_img(finish(img, t, VIG_H, push=push, cx=520, cy=1150, shake=0.5 if t2 + 1.0 < t < t2 + 1.25 else 0.0,
                            flash=0.3 if t2 + 1.0 < t < t2 + 1.08 else 0.0, flash_col=(255, 40, 30)))
        put_ui(out, 1.0, "80 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


# ============================================================ PART 2
def make_recap(D, caps):
    UH = under_house()
    hdr = series_header("INDONESIA", "PART 2")

    def f(t):
        def hanging(img, t_):
            return put_kunti(img, 640 + 10 * math.sin(t_ * 0.8), 242, 0.62, t_, pose="hang", sway=0.5 * math.sin(t_ * 1.2), aura=0.6)

        def girl(img, t_):
            im, fx, fy = putri_crouch(1.0, look=0.6, cover=1.0)
            return put_sprite(img, im, 380, 1760, fx, fy)
        img = UH.frame(t, extras=[hanging, girl])
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.05 * t / D, cx=540, cy=1100))
        put_header(out, hdr, t)
        put_ui(out, 1.0, "80 M", t, ss(t, 2.0, 2.4), y=640)
        return to_arr(out)
    return f


def make_hair(D, caps):
    UH = under_house()
    t2 = caps[1][1]
    jt = D - 0.9

    def f(t):
        if t >= jt:
            return jump(t, jt, scale=1.5, y=860, tilt=80, x=700)
        slide = ss(t, 0.4, caps[0][2])

        def hanging(img, t_):
            return put_kunti(img, 640 - 120 * slide, 242 + 160 * slide, 0.62 + 0.1 * slide, t_, pose="hang", sway=0.5 * math.sin(t_ * 1.2) - 0.8 * slide, aura=0.6)

        def girl(img, t_):
            im, fx, fy = putri_crouch(1.0, look=-0.4 * ss(t_, t2, t2 + 0.8), cover=1.0)
            return put_sprite(img, im, 380, 1760, fx, fy)

        def strands(img, t_):                                                     # black hair sliding over her shoulder
            if slide <= 0:
                return img
            d = ImageDraw.Draw(img)
            rnd = np.random.default_rng(3)
            hx, hy = 640 - 120 * slide, 242 + 160 * slide + 0.72 * 960
            for k in range(12):
                x0 = hx - 50 + k * 9
                ex = 470 + k * 6 + rnd.uniform(-10, 10); ey = hy + (1380 - hy) * slide + rnd.uniform(-30, 30)
                pts = [(x0 + (ex - x0) * u + 14 * math.sin(u * 7 + k + t_ * 2), hy + (ey - hy) * u) for u in np.linspace(0, 1, 9)]
                d.line(pts, fill=(10, 8, 10, 255), width=int(rnd.uniform(4, 8)), joint="curve")
            return img
        img = UH.frame(t, extras=[hanging, girl, strands])
        zk = ss(t, t2, jt)
        out = to_img(finish(img, t, VIG_H, push=1.15 + 0.45 * zk, cx=420 + 40 * zk, cy=1250 - 100 * zk))
        put_ui(out, 1.0, "80 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_bang(D, caps):
    RD = ronda()
    t2 = caps[1][1]
    hits = [t2 + 1.8 + k * 0.55 for k in range(4)] + [t2 + 3.9 + k * 0.5 for k in range(3)]
    run_end = t2 + 1.4

    def f(t):
        hk = max([1 - ss(t, h, h + 0.22) if t >= h else 0 for h in hits])
        if t < run_end:
            u = ss(t, 0.2, run_end)
            x = 1000 - 680 * u; run = 1.0
        else:
            x = 320; run = 0.0
        nh = sum(t >= h for h in hits)
        strike = 1.0 if t < run_end else (1.0 - hk if nh else 1.0)

        def girl(img, t_, o):
            im, fx, fy = putri((t_ * 2.6) % 1 if run else 0.0, run=run, scale=0.62, strike=strike if not run else -1.0)
            return put_sprite(img, im, x + o - 150 - 40, RD.walk_y + 10, fx, fy)

        def her(img, t_, o):                                                       # on the branch: recoils at every bang
            px, py = RD.perch
            rec = min(1.0, 0.25 * nh)
            return put_kunti(img, px + o - 150 + 40 * hk * math.sin(t_ * 70), py - 60 * rec, 0.34, t_, pose="perch", aura=0.5 + 0.5 * hk, sway=0.9 * hk)
        img = RD.frame(t, -150, extras=[girl], tree_extras=[her], lights=0.0)
        a = finish(img, t, VIG_H, push=1.05 + 0.2 * ss(t, run_end - 0.6, run_end + 0.6), cx=480, cy=1120, shake=0.8 * hk, flash=0.25 * hk, flash_col=(255, 220, 170))
        out = to_img(a)
        put_ui(out, 1.0 - 0.15 * nh, "80 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_escape(D, caps):
    RD = ronda(); B = boardwalk()
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        if t < t3 - 0.1:
            lights = ss(t, 0.2, caps[0][2] + 0.4)
            fly = ss(t, t2, t3 - 0.2)

            def girl(img, t_, o):
                im, fx, fy = putri(0.0, scale=0.62, strike=0.4)
                return put_sprite(img, im, 320 + o - 150 - 40, RD.walk_y + 10, fx, fy)

            def her(img, t_, o):
                px, py = RD.perch
                if fly <= 0:
                    return put_kunti(img, px + o - 150, py, 0.34, t_, pose="perch", aura=0.6)
                return put_kunti(img, px + o - 150 + 400 * fly, py - 700 * fly, 0.34 * (1 - 0.7 * fly), t_, rot=-40 * fly, aura=0.6, alpha=1 - ss(fly, 0.8, 1.0))
            img = RD.frame(t, -150 + 60 * t / t3, extras=[girl], tree_extras=[her], lights=lights)
            out = to_img(finish(img, t, VIG_H, push=1.05, cx=540, cy=1100))
            put_ui(out, 1.0 - 0.9 * ss(t, t2, t3), "80 M", t, 1.0, y=UI_Y)
            return to_arr(out)
        # running home along the boardwalk toward us
        u = ss(t, t3, D)

        def scene(img, t_):
            px, py, s = B.at(5.0 - 3.2 * u, 0.0)
            im, fx, fy = putri((t_ * 2.6) % 1, run=1.0, scale=s * 1.05)
            return put_sprite(img, im, px, py, fx, fy)
        img = B.frame(t, extras=[scene], petals=0.0, glow_lit=1.5)
        out = to_img(finish(img, t, VIG_H, push=1.05, cx=540, cy=1000, shake=0.2))
        put_ui(out, 0.0, "0 M" if u > 0.8 else "20 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_twist(D, caps):
    BR = bedroom()
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.0

    def f(t):
        if t >= jt:
            return jump(t, jt, scale=1.45, y=900, tilt=-6, bg=(30, 6, 6))
        px, py = BR.pillow

        def flowerk(img, t_):
            fl = flower(120, 20)
            img.alpha_composite(fl, (int(px - fl.width / 2 + 30), int(py - fl.height / 2)))
            return img

        def girl(img, t_):
            if t_ < t2:                                                            # at the door, sliding the bolt, back to us
                im, fx, fy = putri(0.0, back=True, scale=1.3, apron=False)
                return put_sprite(img, im, 260, 1960, fx, fy)
            return img

        def her(img, t_):                                                          # behind the curtain... a pale shape
            k = ss(t_, t3 - 0.2, t3 + 0.8)
            if k <= 0:
                return img
            return put_kunti(img, 930, 1390, 0.5, t_, alpha=k * 0.9, aura=0.6, dark=0.2)
        img = BR.frame(t, lamp=1.0 - 0.6 * ss(t, t3, jt), extras=[flowerk, her, girl])
        if t < t2:
            out = to_img(finish(img, t, VIG_H, push=1.06 + 0.04 * t / t2, cx=400, cy=1100))
        else:
            zk = ss(t, t2, t3 + 0.5)
            zk2 = ss(t, t3, jt)
            out = to_img(finish(img, t, VIG_H, push=1.2 + 0.8 * zk - 0.5 * zk2, cx=px + 30 + 200 * zk2, cy=py - 150 * zk2))
        return to_arr(out)
    return f


def make_explain(D, caps):
    B = boardwalk()
    title = text_img("KUNTILANAK", font(LORA, 112, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("The woman in white of Indonesian folklore", font(INTER_SB, 36), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 36)
    chips = [pill("Long white gown, long black hair", pf, fill=(110, 20, 24, 235), h=78),
             pill("Said to be a woman who died while pregnant", pf, fill=(110, 20, 24, 235), h=78),
             pill("Sign she is near: the smell of frangipani", pf, fill=(110, 20, 24, 235), h=78),
             pill("Soft laugh = near.  Loud laugh = far.", pf, fill=(110, 20, 24, 235), h=78),
             pill("Legend: 1771, Pontianak's founder fired cannons", pf, fill=(90, 40, 10, 235), outline=(255, 200, 110, 255), h=78),
             pill("to drive the ghosts away. The city has her name.", pf, fill=(90, 40, 10, 235), outline=(255, 200, 110, 255), h=78)]
    ts = [caps[1][1], caps[1][1] + 2.0, caps[1][2] - 0.6, caps[2][1] - 0.2, caps[2][1] + 1.2, caps[2][1] + 1.5]
    bg = {}

    def f(t):
        key = int(t * 6)
        if key not in bg:
            def her(img, t_):
                x, y, s = B.at(7.0, 0.0)
                return put_kunti(img, x, y, s, t_, aura=0.6)
            img = B.frame(t, extras=[her], petals=0.6)
            bg.clear(); bg[key] = finish(img, t, VIG_H, push=1.05 + 0.04 * t / D, cx=540, cy=1000) * 0.5
        out = to_img(bg[key])
        fw = flag_wave(t, 170)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 60))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 190))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 348))
        chips_at(out, chips, ts, t, 440, 92)
        return to_arr(out)
    return f


def make_outro(D, caps):
    R = riverfront()
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("have looked up?", font(LORA, 92, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Look up", (150, 30, 30, 235)), ("Keep walking", (60, 40, 40, 235)), ("Bang the drum", (140, 90, 40, 235)), ("RUN", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    bg = {}

    def f(t):
        key = int(t * 8)
        if key not in bg:
            def watcher(img, t_, o):
                px, py = R.perch
                return put_kunti(img, px + o - 150, py, 0.26, t_, pose="perch", aura=0.5)
            img = R.frame(t, 40 * t / D, tree_extras=[watcher])
            bg.clear(); bg[key] = finish(img, t, vig=VIG_H, push=1.02, cx=540, cy=1000) * 0.5
        out = to_img(bg[key])
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
