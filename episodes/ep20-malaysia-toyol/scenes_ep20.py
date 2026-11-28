"""Ep20 Malaysia / the Toyol - scenes (2.1D survival). Each make_<id>(D, caps) returns f(t) -> float RGB (H, W, 3)."""
from art_ep20 import *

if os.environ.get("NO_UI"):                       # covers: no shop pill under the cover header
    def put_ui(*a, **k):
        pass

UI_Y = 200


def chips_at(out, chips, ts, t, y0, gap=110):
    for i, (c, tt) in enumerate(zip(chips, ts)):
        k = ss(t, tt - 0.15, tt + 0.3)
        if k > 0:
            cc = c if c.width <= W - 40 else c.resize((W - 40, int(c.height * (W - 40) / c.width)), Image.LANCZOS)
            out.alpha_composite(with_alpha(cc, k), (int(W / 2 - cc.width / 2), int(y0 + i * gap + 20 * (1 - k))))


def stop_motion(u, steps):
    return math.floor(max(0.0, min(1.0, u)) * steps) / steps


def jump(t, jt, mode="grin", inv=False, scale=1.3, y=880, tilt=0.0, x=540, bg=(6, 1, 2)):
    img = tface_full(t, jt, mode=mode, inv=inv, scale=scale, y=y, tilt=tilt, x=x, bg=bg)
    fl = 0.85 if t < jt + 0.08 else 0.0
    return finish(img, t, VIG_H, push=1.0 + 0.4 * ss(t, jt, jt + 0.18), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))


def sepia(img, k=1.0):
    a = to_arr(img)
    lum = a.mean(2, keepdims=True)
    s = lum * np.array([1.15, 0.92, 0.7], np.float32)
    return to_img(a * (1 - k) + s * k)


def wet_prints(img, pts, k):
    """Small wet footprints (a child's) across the counter top."""
    if k <= 0:
        return img
    d = ImageDraw.Draw(img)
    n = int(len(pts) * min(1, k))
    for i, (x, y) in enumerate(pts[:n]):
        sg = 1 if i % 2 else -1
        d.ellipse([x - 11, y - 6 + sg * 8, x + 11, y + 6 + sg * 8], fill=(30, 22, 16, 200))
        for j in range(4):
            d.ellipse([x + 12 + j * 3, y - 9 + j * 5 + sg * 8, x + 17 + j * 3, y - 5 + j * 5 + sg * 8], fill=(30, 22, 16, 200))
    return img


PRINTS = [(470 + i * 24, 1272 + (i % 2) * 6) for i in range(9)]


def mirror_toyol(where="shelf", k=1.0):
    """A tiny toyol in the convex mirror's reflection (the viewer sees it first)."""
    def fn(ref, t):
        if k <= 0:
            return ref
        x, y = (60, 120) if where == "shelf" else (130, 150)
        return put_toyol(ref, x, y, 0.2, t, pose="squat" if where == "shelf" else "stand", eyes=k, alpha=k)
    return fn


def notes(img, x, y, n, sc=1.0):
    """A small stack of ringgit notes on the counter (n = how many)."""
    d = ImageDraw.Draw(img)
    for i in range(n):
        c = [(190, 80, 90), (90, 120, 200), (200, 110, 60)][i % 3]
        yy = y - i * 5 * sc
        d.polygon([(x - 60 * sc, yy), (x + 56 * sc, yy - 4 * sc), (x + 62 * sc, yy + 22 * sc), (x - 56 * sc, yy + 26 * sc)], fill=c + (255,), outline=(30, 20, 20, 255))
    return img


# ============================================================ PART 1
def make_hook(D, caps):
    UB = under("bed")
    hdr = series_header("MALAYSIA", "PART 1")
    c1, c2 = caps[0], caps[1]
    nts = [c1[1] + 1.6, c1[1] + 2.6, c1[1] + 3.6]
    turn = c2[1] + 1.4
    jt = D - 0.7

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="grin", scale=1.35, tilt=-12, x=560)

        def floor(img, t_):
            x, y, s = UB.at(0.72, 0.15)
            d = ImageDraw.Draw(img)
            d.rectangle([x + 60 * s * 4, y - 120 * s * 4, x + 140 * s * 4, y], fill=(170, 30, 36, 255), outline=(60, 10, 12, 255), width=3)   # the coin tin
            d.ellipse([x + 60 * s * 4, y - 136 * s * 4, x + 140 * s * 4, y - 104 * s * 4], fill=(120, 20, 24, 255))
            for i in range(9):                                                 # coins being stacked
                cx_ = x - 80 * s * 4 + (i % 3) * 26 * s * 4
                d.ellipse([cx_ - 12 * s * 4, y - 6 * s * 4 - (i // 3) * 6 * s * 4, cx_ + 12 * s * 4, y + 4 * s * 4 - (i // 3) * 6 * s * 4], fill=(220, 180, 70, 255), outline=(110, 80, 30, 255))
            look = ss(t_, turn - 0.4, turn + 0.2)
            tl = -25 * look
            img = put_toyol(img, x - 10, y + 6, s * 2.4, t_, pose="squat", reach=0.5 + 0.5 * math.sin(t_ * 5) * (1 - look),
                            tilt=tl, eyes=0.35 + 0.65 * look, dark=0.35 * (1 - look), grin=1.0 if t_ > turn + 0.6 else 0.0)
            return img
        img = UB.frame(t, floor=[floor], red=1.5)
        x, y, s = UB.at(0.72, 0.15)
        for i, tt in enumerate(nts):
            img = big_text(img, ["SATU", "DUA", "TIGA"][i], 190, 760 + i * 150, ss(t, tt, tt + 0.25) * (1 - ss(t, c2[1] + 0.5, c2[1] + 1.0)), sc=0.8)
        zk = ss(t, turn, jt)
        hit = abs(t - turn) < 0.08
        a = finish(img, t, VIG_H, push=1.04 + 0.05 * t / D + 0.9 * zk, cx=x - 10, cy=1150 + (y - 330 - 1150) * zk,
                   flash=0.3 if hit else 0.0, flash_col=(255, 40, 30), shake=0.6 if hit else 0.0)
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_setup(D, caps):
    O = outside()
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        def inside(img, t_):                           # Aiman behind the counter, seen through the opening
            return put_aiman(img, 250 + 40 * math.sin(t_ * .5), 1500, 0.34, pose="count" if t_ > t2 else "stand")

        def watcher(img, t_):                          # the viewer sees it first: by the jar in the window across the road
            k = ss(t_, t3 + 0.6, t3 + 1.4)
            if k <= 0:
                return img
            jx, jy = O.jar
            return put_toyol(img, jx - 44, jy + 42, 0.12, t_, pose="squat", eyes=k, alpha=k, dark=0.5)
        img = O.frame(t, mid=[inside, watcher])
        zk = ss(t, t3 + 1.0, D)
        jx, jy = O.jar
        out = to_img(finish(img, t, VIG_H, push=1.06 + 0.06 * t / D + 1.0 * zk, cx=360 + (jx - 360) * zk, cy=1150 + (jy - 1150) * zk))
        put_ui(out, clock_at(0, 4, t / D), "RM 800", t, ss(t, t3 - 0.2, t3 + 0.3), y=UI_Y)
        return to_arr(out)
    return f


def make_rule(D, caps):
    SH = shop()
    f1 = font(INTER_SB, 42)
    oc, fc = (150, 230, 170, 255), (20, 50, 36, 230)
    chips = [pill("TOK WAN'S RULES", f1, outline=oc, fill=fc, color=(210, 255, 220, 255), h=86),
             pill("1. MONEY MISSING? IT'S A TOYOL", f1, outline=oc, fill=fc, color=(255, 240, 220, 255), h=92),
             pill("2. IT ONLY TAKES HALF", f1, outline=oc, fill=fc, color=(255, 240, 220, 255), h=92),
             pill("3. LET IT COUNT THE BEANS", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [0.4, caps[1][1] + 0.2, caps[1][1] + 2.4, caps[2][1] + 0.8]
    t2 = caps[1][1]
    tag = pill("EARLIER TONIGHT", font(INTER_M, 32), outline=(220, 200, 160, 255), fill=(40, 30, 20, 200), h=64)
    bg = {}

    def f(t):
        key = int(t * 10)
        if key not in bg:
            def people(img, t_):
                s_, fx, fy = tokwan()
                img = put_sprite(img, sc_spr(s_, 0.95), 300, 1700, fx * .95, fy * .95)
                return put_aiman(img, 650, 1660, 0.95, pose="stand", look=-0.5)
            k = ss(t, t2 + 0.6, t2 + 1.4) * (1 - ss(t, caps[2][1] + 1.0, caps[2][1] + 1.6))
            img = SH.frame(t, back=[people], mirror=[mirror_toyol("shelf", k)])
            img = sepia(img, 0.55)
            bg.clear(); bg[key] = finish(img, t, VIG_H, push=1.08 + 0.05 * t / D, cx=480, cy=1000)
        out = to_img(bg[key])
        out.alpha_composite(with_alpha(tag, ss(t, 0, 0.4) * (1 - ss(t, 2.0, 2.4))), (int(W / 2 - tag.width / 2), 700))
        chips_at(out, chips, ts, t, 230, 108)
        return to_arr(out)
    return f


def make_coins(D, caps):
    SH = shop()
    c2, c3 = caps[1][1], caps[2][1]

    def f(t):
        walk = ss(t, c2, c2 + 1.0) * (1 - ss(t, c3 - 0.6, c3 + 0.1))

        def him(img, t_):
            pose = "count" if walk < 0.2 else ("run" if 0.2 < walk < 0.95 else "stand")
            return put_aiman(img, 640 + 300 * walk, 1660, 0.95, pose=pose, phase=(t_ * 2) % 1,
                             gasp=0.7 * ss(t_, c3 + 0.3, c3 + 0.6), look=0.3 if t_ > c3 else 0.0)

        def ctr(img, t_):
            img = notes(img, 650, 1268, 8 if t_ < c3 else 4)
            return wet_prints(img, PRINTS, ss(t_, c2 + 0.5, c3))
        mk = ss(t, c2 + 0.3, c2 + 1.0)
        img = SH.frame(t, back=[him], counter=[ctr], mirror=[mirror_toyol("floor", mk)], clock_m=18 + int(t / D * 6))
        hit = abs(t - c3 - 0.4) < 0.09
        zk = ss(t, c3, D)
        out = to_img(finish(img, t, VIG_H, push=1.12 + 0.05 * t / D + 0.4 * zk, cx=640, cy=1150 - 80 * zk, shake=0.7 if hit else 0.0,
                            flash=0.25 if hit else 0.0, flash_col=(255, 40, 30)))
        half = t > c3 + 0.35
        put_ui(out, clock_at(18, 24, t / D), "RM 400" if half else "RM 800", t, 1.0, y=UI_Y, danger=half)
        return to_arr(out)
    return f


def make_beans(D, caps):
    SH = shop()
    c2, c3 = caps[1][1], caps[2][1]
    nts = [c2 + 0.1, c2 + 0.75, c2 + 1.4]

    def f(t):
        reveal = ss(t, c3 - 0.2, c3 + 0.8)
        

        def ctr(img, t_):
            img = notes(img, 650, 1268, 4)
            img = wet_prints(img, PRINTS, 1.0)
            bx, by = SH.bowl
            pick = 0.5 + 0.5 * math.sin(t_ * 6)
            img = put_toyol(img, bx + 150, by + 10, 0.55, t_, pose="squat", reach=pick, tilt=-20 * reach_turn(t_),
                            eyes=0.25 + 0.75 * reveal, dark=0.55 * (1 - reveal), grin=1.0 if t_ > c3 + 1.2 else 0.0)
            return img

        def reach_turn(t_):
            return ss(t_, c3 + 0.6, c3 + 1.3)
        img = SH.frame(t, counter=[ctr], beans=1.0 - 0.3 * ss(t, 0, D), flicker=1.0 if t < 1.2 else 0.0, clock_m=25)
        bx, by = SH.bowl
        for i, tt in enumerate(nts):
            img = big_text(img, ["SATU", "DUA", "TIGA"][i], bx - 10 + i * 100, by - 230 - i * 40, ss(t, tt, tt + 0.25) * (1 - ss(t, c3 - 0.2, c3 + 0.3)), sc=0.9)
        push = 2.0 - 0.45 * reveal
        out = to_img(finish(img, t, VIG_H, push=push + 0.04 * t / D, cx=bx + 90, cy=by - 120))
        put_ui(out, clock_at(25, 26, t / D), "RM 400", t, 1.0, y=UI_Y, danger=True)
        return to_arr(out)
    return f


def make_mistake(D, caps):
    SH = shop()
    c2, c3 = caps[1][1], caps[2][1]
    jt = D - 0.6
    rr = np.random.default_rng(12)
    flying = [(rr.uniform(-60, 60), rr.uniform(-900, -400), rr.uniform(600, 1100), rr.uniform(0, .3)) for _ in range(70)]

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="grin", scale=1.4, tilt=10, x=520)
        throw = ss(t, 0.9, 1.4)
        lights = 1.0 - ss(t, c3 + 0.2, c3 + 0.9)
        if c3 < t < c3 + 0.9 and int(t * 20) % 3 == 0:
            lights = 1.0

        def him(img, t_):
            return put_aiman(img, 560, 1660, 0.95, pose="throw" if 0.9 < t_ < 2.6 else "stand", gasp=0.6 * ss(t_, c2, c2 + 0.5), look=-0.4)

        def ctr(img, t_):
            img = notes(img, 650, 1268, 4)
            img = wet_prints(img, PRINTS, 1.0)
            turn = ss(t_, c2 + 0.2, c2 + 1.4)
            img = put_toyol(img, 230, 1262, 0.55, t_, pose="squat", tilt=-30 * turn, eyes=0.6 + 0.4 * turn, grin=1.0 if t_ > c2 + 1.0 else 0.0,
                            aura=0.4 * turn)
            if throw > 0:                                            # the beans flying out of the shutter
                d = ImageDraw.Draw(img)
                for dx, vy, vx, dl in flying:
                    tt_ = t_ - 1.0 - dl
                    if 0 < tt_ < 1.6:
                        px, py = 420 + dx + vx * tt_, 1150 + vy * tt_ + 900 * tt_ * tt_
                        d.ellipse([px - 7, py - 5, px + 7, py + 5], fill=(90, 150, 60, 255))
            return img
        img = SH.frame(t, back=[him], counter=[ctr], beans=0.0 if t > 1.0 else 1.0, light=max(0.05, lights), red=1.0, clock_m=27)
        if lights < 0.3:                                             # in the dark: just the red eyes on the counter
            pass
        zk = ss(t, c3 + 1.0, jt)
        out = to_img(finish(img, t, VIG_H, push=1.1 + 0.6 * zk, cx=420 - 150 * zk, cy=1050 + 100 * zk,
                            shake=0.5 if abs(t - 1.0) < 0.15 else 0.0))
        put_ui(out, clock_at(27, 28, t / D), "RM 400", t, 1.0 - 0.6 * (1 - lights), y=UI_Y, danger=True)
        return to_arr(out)
    return f


def make_cliff(D, caps):
    UC = under("counter")
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.1

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="grin", inv=True, scale=1.35, y=900)
        come = ss(t, t2 - 0.2, t2 + 2.2)
        u = 0.15 + 0.72 * stop_motion(come, 5)

        def feet(img, t_):
            if come <= 0:
                return img
            x, y, s = UC.at(u, 0.1)
            return put_toyol(img, x, y, s * 3.2, t_, pose="stand", eyes=1.0 if u < 0.6 else 0.0, alpha=ss(t_, t2 - 0.2, t2 + 0.2), dark=0.2)
        img = UC.frame(t, floor=[feet])
        zk = ss(t, t3, jt)
        hit = come > 0 and abs(t - (t2 + 2.2)) < 0.1
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.2 * zk, cx=540, cy=1250, shake=0.4 if hit else 0.0))
        put_ui(out, clock_at(29, 30, t / D), "RM 400", t, 1.0, y=UI_Y, danger=True)
        return to_arr(out)
    return f


# ============================================================ PART 2
def legs_front(img, t, alpha=1.0, UC=None):
    UC = UC or under("counter")
    x, y, s = UC.at(0.87, 0.1)
    return put_toyol(img, x, y, s * 3.2, t, pose="stand", eyes=0.0, alpha=alpha, dark=0.2)


def make_recap(D, caps):
    UC = under("counter")
    hdr = series_header("MALAYSIA", "PART 2")

    def f(t):
        img = UC.frame(t, floor=[lambda im, t_: legs_front(im, t_, UC=UC)])
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.05 * t / D, cx=540, cy=1150))
        put_header(out, hdr, t)
        put_ui(out, "22:30", "RM 400", t, ss(t, 2.0, 2.4), y=640, danger=True)
        return to_arr(out)
    return f


def make_peek(D, caps):
    UC = under("counter")
    t2 = caps[1][1]
    jt = D - 0.8

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="scream", inv=True, scale=1.45, y=860)
        hand = ss(t, 0.3, 2.0)
        face = ss(t, t2 - 0.2, t2 + 1.2)

        def floor(img, t_):
            img = legs_front(img, t_, alpha=1 - 0.8 * face, UC=UC)
            if face > 0:
                img = put_tface(img, 540, 300 + 520 * face, 0.62, t_, mode="grin", inv=True, aura=0.4, alpha=min(1, face * 2))
            return img

        def edge(img, t_):
            if hand > 0:
                img = small_hand(img, 1200 - 520 * hand, 1220 + 30 * math.sin(t_ * 3), 3.0, ang=math.pi + 0.15, curl=0.2 + 0.6 * hand)
            return img
        img = UC.frame(t, floor=[floor], edge=[edge])
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.15 * face, cx=540, cy=1000, shake=0.3 if abs(t - 0.4) < 0.1 else 0.0))
        put_ui(out, "22:31", "RM 400", t, 1.0, y=UI_Y, danger=True)
        return to_arr(out)
    return f


def held_mirror(img, t, x, y, r, face=0.0, mode="still"):
    """The round shop mirror held up; face>0 shows the toyol's own face reflected in it."""
    ref = to_img(vgrad((30, 20, 20), (60, 30, 30), (20, 10, 10), ym=0.5, w=2 * r, h=2 * r))
    if face > 0:
        ref = put_tface(ref, r, r + 30, r / 380, t, mode=mode, aura=0.0, alpha=face)
    m = Image.new("L", ref.size, 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    ref.putalpha(m)
    img.alpha_composite(ref, (int(x - r), int(y - r)))
    d = ImageDraw.Draw(img)
    d.ellipse([x - r, y - r, x + r, y + r], outline=(200, 140, 40, 255), width=max(6, int(r / 12)))
    d.arc([x - r * .7, y - r * .7, x + r * .3, y + r * .3], 200, 260, fill=(255, 255, 255, 170), width=max(4, int(r / 16)))
    return img


def make_mirror(D, caps):
    SH = shop()
    c2, c3 = caps[1][1], caps[2][1]
    tag = pill("TOK WAN'S LAST RULE", font(INTER_SB, 40), outline=(150, 230, 170, 255), fill=(20, 50, 36, 230), color=(210, 255, 220, 255), h=86)
    rule = pill("SHOW IT ITS OWN FACE", font(INTER_SB, 50), outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=104)
    pov = c3 + 1.2

    def f(t):
        if t < pov:
            torn = t > c3 + 0.3

            def him(img, t_):
                if not torn:
                    return put_aiman(img, 420 + 100 * ss(t_, c3 - 0.4, c3 + 0.3), 1660, 0.95, pose="stand", look=0.5, gasp=0.4)
                img = put_aiman(img, 520, 1660, 0.95, pose="hold", gasp=0.6)
                return held_mirror(img, t_, 520, 760, 150)

            def ctr(img, t_):
                return put_toyol(img, 860, 1262, 0.55, t_, pose="stand", tilt=-15, eyes=1.0, aura=0.3, flip=True)
            img = SH.frame(t, back=[him], counter=[ctr], light=0.12, beans=0.0, wall_mirror=not torn)
            out = to_img(finish(img, t, VIG_H, push=1.1 + 0.08 * t / D, cx=500, cy=900))
            out.alpha_composite(with_alpha(tag, ss(t, 0.3, 0.7)), (int(W / 2 - tag.width / 2), 330))
            out.alpha_composite(with_alpha(rule, ss(t, c2, c2 + 0.3)), (int(W / 2 - rule.width / 2), 440))
            return to_arr(out)
        # POV: the toyol sees itself in the mirror - and screams
        k = ss(t, pov, pov + 0.3)
        scream = t > pov + 0.5
        img = SH.frame(t, back=[lambda im, t_: put_aiman(im, 540, 2400, 1.9, pose="hold", gasp=0.8)], light=0.1, beans=0.0, wall_mirror=False)
        img = held_mirror(img, t, 540, 900, 330, face=k, mode="scream" if scream else "still")
        hit = abs(t - pov - 0.5) < 0.1
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.15 * k, cx=540, cy=900, shake=1.0 if scream else 0.2,
                            flash=0.5 if hit else 0.0, flash_col=(255, 240, 220)))
        return to_arr(out)
    return f


def make_flee(D, caps):
    O = outside()
    c2, c3 = caps[1][1], caps[2][1]

    def f(t):
        run = ss(t, 0.2, c2 + 2.4)
        u = stop_motion(run, 10)
        dawn = ss(t, c3, D)

        def runner(img, t_):
            if u >= 1.0:
                jx, jy = O.jar
                return put_toyol(img, jx - 44, jy + 42, 0.12, t_, pose="squat", eyes=1 - dawn, alpha=1 - dawn, dark=0.4)
            x = 300 + (880 - 300) * u; y = 1520 + (1330 - 1520) * u
            sc = 0.6 - 0.35 * u
            return put_toyol(img, x, y, sc, t_, pose="run", phase=(t_ * 3) % 1, eyes=1.0, grin=0.0 if u < .5 else 1.0)
        img = O.frame(t, mid=[], front=[runner], dawn=dawn, jar_glow=1.0 + 0.8 * ss(t, c2 + 2.4, c2 + 3.0), shop_light=0.2)
        zk = ss(t, c2 + 1.6, c3)
        jx, jy = O.jar
        out = to_img(finish(img, t, VIG_H, push=1.06 + 0.9 * zk * (1 - dawn), cx=540 + (jx - 540) * zk * (1 - dawn), cy=1200 + (jy - 1200) * zk * (1 - dawn)))
        put_ui(out, "06:58" if dawn > 0.5 else "22:33", "RM 400", t, 1 - ss(t, 0.5, 1.0), y=UI_Y)
        return to_arr(out)
    return f


def sister_legs(img, t, k=1.0, shake=0.0):
    """The little sister sitting on the edge of the bed: her legs in pink dotted pyjama trousers come down past the bed
    edge right in front of us, bare heels on the floor."""
    if k <= 0:
        return img
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    X = (250, 640)

    def legs(d, s):
        for x in X:
            d.polygon(P_((x, 640), (x + 170, 640), (x + 150, 1100), (x + 136, 1560), (x + 34, 1560), (x + 16, 1100), s=s), fill=255)

    def feet(d, s):
        for x in X:
            d.ellipse([(x + 20) * s, 1530 * s, (x + 150) * s, 1680 * s], fill=255)
    lay.alpha_composite(shade(feet, (W, H), (150, 108, 84), 30))
    lay.alpha_composite(shade(legs, (W, H), (196, 120, 150), 60, rim=(255, 120, 120)))
    d = ImageDraw.Draw(lay)
    r = np.random.default_rng(4)
    for x in X:
        for _ in range(26):
            px, py = x + r.uniform(40, 130), r.uniform(700, 1500)
            d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(250, 230, 236, 220))
        d.rectangle([x + 30, 1520, x + 140, 1548], fill=(160, 80, 110, 255))
    dy = int(8 * math.sin(t * 30) * shake)
    img.alpha_composite(with_alpha(lay, k), (0, dy))
    return img


def make_twist(D, caps):
    UB = under("bed")
    c2, c3 = caps[1][1], caps[2][1]
    jt = D - 1.0
    half = pill("HALF... GONE", font(INTER_SB, 64), outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=120)

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="grin", scale=1.45, y=900, tilt=-8, bg=(14, 8, 16))
        morning = 1.0 - ss(t, c3 - 0.3, c3 + 0.6)
        nts = [c3 + 2.0, c3 + 2.9]

        def floor(img, t_):
            x, y, s = UB.at(0.25, -0.3)
            look = ss(t_, c3 + 3.4, jt - 0.3)
            if t_ > c3:
                img = put_toyol(img, x, y, s * 3.0, t_, pose="squat", reach=0.5 + 0.5 * math.sin(t_ * 5) * (1 - look), tilt=-25 * look,
                                eyes=0.4 + 0.6 * look, dark=0.4 * (1 - look), alpha=ss(t_, c3 + 0.2, c3 + 1.0), grin=1.0 if look > .6 else 0.0)
            return img

        def edge(img, t_):
            return sister_legs(img, t_, morning, shake=1.0 if 0.4 < t_ < c2 else 0.0)

        def tin(img, t_):
            k = ss(t_, c2 - 0.3, c2)
            if k <= 0 or morning <= 0:
                return img
            x, y, s = UB.at(0.85, 0.05)
            y = y - 500 * (1 - k)
            d = ImageDraw.Draw(img)
            d.rectangle([x - 80, y - 190, x + 80, y], fill=(170, 30, 36, 255), outline=(60, 10, 12, 255), width=5)
            d.rectangle([x - 80, y - 130, x + 80, y - 80], fill=(230, 210, 120, 255))
            d.ellipse([x - 80, y - 210, x + 80, y - 170], fill=(120, 20, 24, 255))
            for i in range(3):
                d.ellipse([x + 100 + i * 40, y - 14, x + 140 + i * 40, y + 6], fill=(220, 180, 70, 255), outline=(110, 80, 30, 255))
            return img
        img = UB.frame(t, floor=[floor], edge=[tin, edge], red=1.0 - 0.6 * morning)
        if morning > 0:                                       # morning light from the window
            a = to_arr(img); add_glow(a, gsp(500, (255, 220, 180)), 790, 660, 0.5 * morning); img = to_img(a)
        x, y, s = UB.at(0.25, -0.3)
        for i, tt in enumerate(nts):
            img = big_text(img, ["SATU", "DUA"][i], x - 40 + i * 110, y - 300 - i * 30, ss(t, tt, tt + 0.25), red=True, sc=0.8)
        zk = ss(t, c3 + 1.0, jt)
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.9 * zk, cx=540 + (x - 540) * zk, cy=1150 + (y - 200 - 1150) * zk))
        out.alpha_composite(with_alpha(half, ss(t, c2, c2 + 0.3) * (1 - ss(t, c3 - 0.3, c3))), (int(W / 2 - half.width / 2), 400))
        return to_arr(out)
    return f


def make_explain(D, caps):
    SH = shop()
    title = text_img("TOYOL", font(LORA, 130, "Bold"), fill=(220, 255, 220, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("Malaysia's money-stealing child spirit", font(INTER_SB, 38), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 36)
    c1, c2 = (110, 20, 24, 235), (20, 70, 50, 235)
    chips = [pill("A small child spirit of Malay folklore", pf, fill=c1, h=78),
             pill("Kept in a jar, fed milk + sweets", pf, fill=c1, h=78),
             pill("It steals money for its owner", pf, fill=c1, h=78),
             pill("They say it only takes half", pf, fill=c1, h=78),
             pill("Green beans or rice: it MUST count them", pf, fill=c2, outline=(150, 230, 170, 255), h=78),
             pill("2006: a fisherman in Pahang found a bottle", pf, fill=c1, h=78),
             pill("said to hold a toyol... now in a museum", pf, fill=c1, h=78)]
    ts = [caps[0][1] + 0.8, caps[0][1] + 4.0, caps[1][1] + 0.3, caps[1][1] + 1.8, caps[1][1] + 3.4, caps[2][1] + 0.4, caps[2][1] + 3.2]
    bg = {}

    def f(t):
        key = int(t * 6)
        if key not in bg:
            def ctr(img, t_):
                return put_toyol(img, 300, 1262, 0.5, t_, pose="squat", reach=0.5 + 0.5 * math.sin(t_ * 4), eyes=0.8)
            img = SH.frame(t, counter=[ctr], beans=0.8)
            bg.clear(); bg[key] = finish(img, t, VIG_H, push=1.15 + 0.04 * t / D, cx=450, cy=1100) * 0.45
        out = to_img(bg[key])
        fw = flag_wave(t, 190)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 50))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 190))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 350))
        chips_at(out, chips, ts, t, 450, 92)
        return to_arr(out)
    return f


def make_outro(D, caps):
    O = outside()
    q = text_img("Would YOU have", font(LORA, 96, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("let it count?", font(LORA, 104, "Bold"), fill=(170, 255, 170, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 42)
    opts = [("Let it count", (20, 80, 50, 235)), ("Grab the bowl", (110, 30, 30, 235)), ("Use the mirror", (100, 70, 30, 235)), ("RUN!", (160, 40, 20, 235))]
    chips = [pill(n, pf, fill=c, h=88) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    bg = {}

    def f(t):
        key = int(t * 8)
        if key not in bg:
            def her(img, t_):
                jx, jy = O.jar
                return put_toyol(img, jx - 44, jy + 42, 0.12, t_, pose="squat", eyes=1.0, dark=0.4)
            img = O.frame(t, mid=[her], shop_light=0.6)
            bg.clear(); bg[key] = finish(img, t, vig=VIG_H, push=1.05, cx=700, cy=1000) * 0.5
        out = to_img(bg[key])
        fw = flag_wave(t, 190)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 120))
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
