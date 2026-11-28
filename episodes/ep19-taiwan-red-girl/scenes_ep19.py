"""Ep19 Taiwan / the little girl in red (mo-sin-a) - scenes (2.1D survival). Each make_<id>(D, caps) returns
f(t) -> float RGB (H, W, 3)."""
from art_ep19 import *

if os.environ.get("NO_UI"):                       # covers: no trail pill under the cover header
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


def jump(t, jt, mode="smile", inv=False, scale=1.3, y=880, tilt=0.0, x=540, bg=(6, 1, 2)):
    img = gface_full(t, jt, mode=mode, inv=inv, scale=scale, y=y, tilt=tilt, x=x, bg=bg)
    fl = 0.85 if t < jt + 0.08 else 0.0
    return finish(img, t, VIG_H, push=1.0 + 0.4 * ss(t, jt, jt + 0.18), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))


def put_hiker(img, kind, x, y, sc, phase=0.0, run=0.0, alpha=1.0, dark=0.0, incense=False):
    spr, fx, fy = hiker(kind, phase, 1.0, run, incense)
    g = spr.resize((max(1, int(spr.width * sc)), max(1, int(spr.height * sc))), Image.LANCZOS)
    if dark > 0:
        g = tint(g, (1 - dark, 1 - dark, 1 - dark))
    return put_sprite(img, g, x, y, fx * sc, fy * sc, alpha)


def put_mei(img, x, y, sc, pose="stand", alpha=1.0, **kw):
    spr, fx, fy = mei(pose, scale=1.0, **kw)
    g = spr.resize((max(1, int(spr.width * sc)), max(1, int(spr.height * sc))), Image.LANCZOS)
    return put_sprite(img, g, x, y, fx * sc, fy * sc, alpha)


FAM = [("grandpa", 0.50, -0.35), ("mum", 0.40, 0.4), ("boy", 0.30, -0.4)]   # the family in the home video
GIRL_U, GIRL_SIDE = 0.18, 0.3


def family_video(TR, t, climb=0.0, girl_front=0.0, girl_on=True, tilt=-18, walk=True):
    """The family climbing the steps as filmed by Mei, the girl in red at the back of the line (closest to us).
    Returns (img, positions [(x, head_y)] for grandpa, mum, boy, girl)."""
    pos = []

    def fam(img, t_):
        nonlocal pos
        pos = []
        for i, (k, u, side) in enumerate(FAM):
            x, y, sc = TR.P.at(u + climb, side)
            img = put_hiker(img, k, x, y, sc, phase=(t_ * 1.3 + i * .3) % 1 if walk else 0.0)
            pos.append((x, y - 900 * sc * KINDS[k]["size"] - 70 * sc))
        x, y, sc = TR.P.at(GIRL_U + climb, GIRL_SIDE)
        if girl_on:
            if girl_front > 0.5:
                img = put_girl(img, x, y, sc * 0.9, t_, pose="stand", tilt=tilt, eyes=1.0)
            else:
                img = put_girl(img, x, y, sc * 0.9, t_, pose="back", phase=(t_ * 1.3) % 1 if walk else 0.0, eyes=0.0)
        pos.append((x, y - 880 * sc * 0.9 - 60 * sc))
        return img
    img = TR.frame(t, path_extras=[fam], fogk=0.3)
    return img, pos


# ============================================================ PART 1
def make_hook(D, caps):
    TR = trail(False)
    hdr = series_header("TAIWAN", "PART 1")
    c1, c2 = caps[0], caps[1]
    nts = [c1[1] + 1.1, c1[1] + 1.7, c1[1] + 2.3, c1[2] - 0.6]
    turn = c2[1] + 1.7
    jt = D - 0.7

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="smile", scale=1.35, tilt=-14, x=560)
        climb = 0.012 * min(t, turn)
        img, pos = family_video(TR, t, climb, girl_front=1.0 if t > turn else 0.0, walk=t < turn)
        img = camcorder(img, t, stamp=f"16:21:{7 + int(t):02d}")
        for i, tt in enumerate(nts):
            x, y = pos[i]
            img = count_num(img, i + 1, x, y - 40, ss(t, tt, tt + 0.25) * (1 - 0.6 * ss(t, c2[1], c2[1] + 0.5)) if i < 3 else ss(t, tt, tt + 0.25), red=i == 3)
        gx, gy = pos[3]
        zk = ss(t, c2[1], jt)
        glitch_ = abs(t - turn) < 0.08
        a = finish(img, t, VIG_H, push=1.03 + 0.75 * zk, cx=gx + 0 * zk, cy=900 + (gy + 160 - 900) * zk,
                   flash=0.35 if glitch_ else 0.0, flash_col=(255, 40, 30), shake=0.6 if glitch_ else 0.0)
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_setup(D, caps):
    TR = trail(False)
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        u0 = 0.012 * t

        def fam(img, t_):
            for i, (k, u) in enumerate((("grandpa", 0.36), ("mum", 0.29), ("boy", 0.24), ("mei", 0.13))):
                x, y, sc = TR.P.at(u + u0)
                img = put_hiker(img, k, x + (40 if k == "boy" else -20 * (i % 2)), y, sc, phase=(t_ * 1.2 + i * .25) % 1)
            return img

        def watcher(img, t_):                         # the viewer sees her first: far up the steps between the ferns
            k = ss(t_, t3 + 0.2, t3 + 1.0)
            if k <= 0:
                return img
            x, y, sc = TR.P.at(0.86, 1.6)
            return put_girl(img, x, y, sc * 0.9, t_, tilt=-15, eyes=k, alpha=k)
        img = TR.frame(t, far_extras=[watcher], path_extras=[fam], fogk=0.3)
        zk = ss(t, t3 + 0.4, D)
        wx, wy, _ = TR.P.at(0.86, 1.6)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.04 * t / D + 0.9 * zk, cx=540 + (wx - 540) * zk, cy=1100 - (1100 - wy + 40) * zk))
        put_ui(out, clock_at(0, 5, t / D), "2.4 KM", t, ss(t, t2 - 0.2, t2 + 0.3), y=UI_Y)
        return to_arr(out)
    return f


def make_rule(D, caps):
    SH = shrine()
    f1 = font(INTER_SB, 42)
    oc, fc = (255, 200, 120, 255), (60, 30, 20, 230)
    chips = [pill("GRANDPA'S RULES", f1, outline=oc, fill=fc, color=(255, 220, 160, 255), h=86),
             pill("1. IF IT CALLS YOUR NAME, DON'T ANSWER", f1, outline=oc, fill=fc, color=(255, 240, 220, 255), h=92),
             pill("2. STAY WITH THE RIBBONS", f1, outline=oc, fill=fc, color=(255, 240, 220, 255), h=92),
             pill("3. IT HATES LOUD BANGS", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [0.3, caps[2][1] + 0.2, caps[2][1] + 1.9, caps[3][1]]
    t2 = caps[1][1]
    bg = {}

    def f(t):
        key = int(t * 10)
        if key not in bg:
            def fam(img, t_):
                img = put_hiker(img, "boy", 250, 1720, 0.62, 0.0)
                img = put_hiker(img, "mum", 120, 1800, 0.72, 0.0)
                img = put_hiker(img, "grandpa", 520, 1760, 0.74, 0.0, incense=True)
                img = incense_tips(img, 520, 1760, 0.74, t_)
                img = put_hiker(img, "mei", 930, 1860, 0.78, 0.0)
                return img

            def peeker(img, t_):                     # beside the shrine, in the ferns: a small red shape, watching
                k = ss(t_, t2 + 0.8, t2 + 1.6) * (1 - ss(t_, caps[2][1] - 0.2, caps[2][1] + 0.3))
                if k > 0:
                    img = put_girl(img, 990, 1230, 0.3, t_, tilt=-20, eyes=k, alpha=k, dark=0.3)
                return img
            img = SH.frame(t, extras=[peeker, fam])
            bg.clear(); bg[key] = finish(img, t, VIG_H, push=1.08 + 0.05 * t / D, cx=600, cy=1250) * 0.8
        out = to_img(bg[key])
        chips_at(out, chips, ts, t, 230, 112)
        return to_arr(out)
    return f


def make_count(D, caps):
    TR = trail(False)
    cut = caps[1][1] - 0.1
    c2, c3 = caps[1], caps[2]
    nts = [c2[1] + 0.8, c2[1] + 1.5, c2[1] + 2.2, c3[1] + 0.1]
    snap = D - 1.0

    def f(t):
        if t < cut:
            def sitter(img, t_):
                return put_mei(img, 540, 1640, 1.05, pose="sit", phone=1.0, look=0.0)
            img = TR.frame(t, path_extras=[sitter], fogk=0.35)
            a = to_arr(img)
            add_glow(a, gsp(160, (170, 200, 255)), 540, 1290, 0.35)
            out = to_img(finish(to_img(a), t, VIG_H, push=1.25 + 0.04 * t, cx=540, cy=1250))
            put_ui(out, clock_at(21, 22, t / D), "2.0 KM", t, 1.0, y=UI_Y)
            return to_arr(out)
        img, pos = family_video(TR, 3.0, 0.0, girl_front=1.0 if t > snap else 0.0, walk=False, tilt=-22)
        img = camcorder(img, t, stamp="16:21:13", play=False)
        d = ImageDraw.Draw(img)
        d.rectangle([66, 1560, 78, 1600], fill=(250, 250, 250, 255)); d.rectangle([90, 1560, 102, 1600], fill=(250, 250, 250, 255))   # pause
        for i, tt in enumerate(nts):
            x, y = pos[i]
            img = count_num(img, i + 1, x, y - 40, ss(t, tt, tt + 0.25), red=i == 3)
        gx, gy = pos[3]
        zk = ss(t, c3[1] + 0.6, D)
        hit = abs(t - snap) < 0.09
        out = to_img(finish(img, t, VIG_H, push=1.0 + 0.8 * zk, cx=gx, cy=900 + (gy + 160 - 900) * zk,
                            flash=0.3 if hit else 0.0, flash_col=(255, 40, 30), shake=0.7 if hit else 0.0))
        return to_arr(out)
    return f


def make_fog(D, caps):
    TR = trail(False)
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        fk = ss(t, 0.2, 2.6)
        cam = 260 * ss(t, t3, D)

        def fam(img, t_):                              # Grandpa, Mum and the boy fade up the steps into the fog
            al = 1 - ss(t_, 1.2, 3.2)
            if al <= 0:
                return img
            for i, (k, u) in enumerate((("grandpa", 0.6), ("mum", 0.55), ("boy", 0.5))):
                x, y, sc = TR.P.at(u + 0.02 * t_)
                img = put_hiker(img, k, x + 30 * (i - 1), y, sc, phase=(t_ * 1.2 + i * .3) % 1, alpha=al)
            return img

        def far_girl(img, t_):                         # on the bank: the girl, half in the fog (viewer sees her)
            k = ss(t_, t2 + 0.6, t2 + 1.3)
            if k <= 0:
                return img
            x, y, sc = TR.P.at(0.5, 1.5)
            return put_girl(img, x, y, sc * 0.9, t_, tilt=-15, eyes=k, alpha=k * 0.85)
        img = TR.frame(t, cam=cam, far_extras=[fam, far_girl], fogk=0.35 + 0.9 * fk, red=ss(t, t2, t2 + 1.2), veil=0.5 * fk)
        u = ss(t, 0.0, D)
        x, y, sc = TR.P.at(0.06 + 0.12 * u, 0.0 + 1.2 * ss(t, t3, D))
        img = put_hiker(img, "mei", x - cam * 0.5, y, sc, phase=(t * 1.2) % 1)
        out = to_img(finish(img, t, VIG_H, push=1.06 + 0.04 * t / D, cx=540 + cam * 0.3, cy=1150))
        put_ui(out, clock_at(30, 38, t / D), "1.8 KM", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_mistake(D, caps):
    FW = fogwood()
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 0.6

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="smile", scale=1.4, tilt=16, y=860)
        shrink = stop_motion(ss(t, t3 + 0.2, t3 + 1.4), 4)

        def sil(img, t_):                              # a figure in the fog: Grandpa's shape... shrinking into a child
            x, y, sc = FW.P.at(0.4); x += 80
            if shrink < 1:
                img = put_hiker(img, "grandpa", x, y, sc * (1 - 0.35 * shrink), alpha=0.85, dark=0.92)
            if shrink > 0:
                img = put_girl(img, x, y, sc * 0.9, t_, tilt=-25, eyes=1.0, alpha=shrink, dark=0.2)
            return img

        def her(img, t_):
            x, y, sc = FW.P.at(0.12)
            return put_hiker(img, "mei", x, y, sc, phase=0.0 if t_ > 1.2 else (t_ * 1.2) % 1)
        img = FW.frame(t, near_extras=[sil, her], fogk=0.8)
        zk = ss(t, t3, jt)
        hit = abs(t - t3) < 0.12
        x, y, sc = FW.P.at(0.4); x += 80
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.9 * zk, cx=540 + (x - 540) * zk, cy=1200 + (y - 260 - 1200) * zk,
                            shake=0.4 if hit else 0.0))
        put_ui(out, clock_at(40, 41, t / D), "LOST", t, 1.0, y=UI_Y, danger=t > t2)
        return to_arr(out)
    return f


def make_cliff(D, caps):
    FW = fogwood(); HO = hollow()
    cut = caps[0][2] - 0.4
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.1

    def f(t):
        if t < cut:
            u = t / cut

            def runner(img, t_):
                x0, y0, s0 = FW.P.at(0.05)
                hx, hy = FW.hollow
                x = x0 + (hx - x0) * u; y = y0 + (hy + 100 - y0) * u; sc = s0 + (0.32 - s0) * u
                return put_hiker(img, "mei", x, y, sc, phase=(t_ * 2.4) % 1, run=1.0, alpha=1 - ss(u, 0.85, 1.0))
            img = FW.frame(t, near_extras=[runner], fogk=0.8)
            out = to_img(finish(img, t, VIG_H, push=1.1, cx=640, cy=1200, shake=0.35))
            put_ui(out, clock_at(42, 43, u), "LOST", t, 1.0, y=UI_Y, danger=True)
            return to_arr(out)
        if t >= jt:
            return jump(t, jt, mode="smile", inv=True, scale=1.35, y=900)
        come = ss(t, t2 - 0.3, t2 + 1.8)
        s_ = 1.0 + 2.0 * stop_motion(come, 4)

        def legs(img, t_):
            if come <= 0:
                return img
            return put_girl(img, 540, 1250 + 280 * (s_ - 1.0) / 2.0, s_, t_, eyes=0.0, alpha=ss(t_, t2 - 0.3, t2 + 0.1))
        img = HO.frame(t, outside_extras=[legs], fogk=0.7)
        zk = ss(t, t3, jt)
        out = to_img(finish(img, t, VIG_H, push=1.03 + 0.2 * zk, cx=540, cy=1250, shake=0.4 if abs(t - t2 - 1.8) < 0.1 else 0.0))
        put_ui(out, clock_at(44, 45, t / D), "LOST", t, 1.0, y=UI_Y, danger=True)
        return to_arr(out)
    return f


# ============================================================ PART 2
def legs_outside(img, t, alpha=1.0):
    return put_girl(img, 540, 1530, 3.0, t, eyes=0.0, alpha=alpha)


def make_recap(D, caps):
    HO = hollow()
    hdr = series_header("TAIWAN", "PART 2")

    def f(t):
        img = HO.frame(t, outside_extras=[legs_outside], fogk=0.7)
        out = to_img(finish(img, t, VIG_H, push=1.03 + 0.05 * t / D, cx=540, cy=1100))
        put_header(out, hdr, t)
        put_ui(out, "16:46", "LOST", t, ss(t, 2.0, 2.4), y=600, danger=True)
        return to_arr(out)
    return f


def make_peek(D, caps):
    HO = hollow()
    t2 = caps[1][1]
    jt = D - 0.8

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="scream", inv=True, scale=1.45, y=860)
        hand = ss(t, 0.3, 1.4)
        face = ss(t, t2 - 0.2, t2 + 1.2)

        def outside(img, t_):
            img = legs_outside(img, t_, alpha=1 - 0.7 * face)
            if face > 0:
                img = put_gface(img, 540, 380 + 340 * face, 0.55, t_, mode="still", inv=True, aura=0.4, alpha=min(1, face * 2))
            return img

        def edge(img, t_):
            if hand > 0:
                img = small_hand(img, 160 + 70 * hand, 980, 1.3, ang=0.15, curl=0.4 + 0.6 * hand)
            return img
        img = HO.frame(t, outside_extras=[outside], edge_extras=[edge], fogk=0.7)
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.15 * face, cx=540, cy=900, shake=0.3 if abs(t - 0.4) < 0.1 else 0.0))
        put_ui(out, "16:47", "LOST", t, 1.0, y=UI_Y, danger=True)
        return to_arr(out)
    return f


def firecrackers(img, x0, y0, x1, y1, n=14, lit=0.0, t=0.0):
    """A string of small red firecrackers (paper tubes on a braided fuse); lit 0..1 = how much has burned."""
    d = ImageDraw.Draw(img)
    for i in range(n):
        u = i / (n - 1)
        if u < lit:
            continue
        x = x0 + (x1 - x0) * u + 10 * math.sin(u * 9 + t); y = y0 + (y1 - y0) * u
        for sg in (-1, 1):
            d.rounded_rectangle([x + sg * 14 - 7, y - 16, x + sg * 14 + 7, y + 16], 4, fill=(200, 26, 26, 255), outline=(90, 10, 10, 255), width=2)
            d.rectangle([x + sg * 14 - 7, y - 6, x + sg * 14 + 7, y - 2], fill=(220, 180, 70, 255))
    d.line([(x0 + (x1 - x0) * lit, y0 + (y1 - y0) * lit), (x1, y1)], fill=(120, 90, 50, 255), width=4)
    return img


def make_bang(D, caps):
    HO = hollow(); FW = fogwood()
    c2, c3 = caps[1][1], caps[2][1]
    rr = np.random.default_rng(5)
    bursts = [(rr.uniform(0.0, 1.0), rr.uniform(-1, 1), rr.uniform(0.6, 1.2)) for _ in range(26)]
    conf = [(rr.uniform(300, 1000), rr.uniform(1200, 1500), rr.uniform(-300, 300), rr.uniform(-900, -400), rr.uniform(0, 6)) for _ in range(70)]

    def f(t):
        if t < c2 - 0.1:                                       # inside: Mei pulls out the string, the lighter flame
            img = Image.new("RGBA", (W, H), (20, 12, 10, 255))
            img.alpha_composite(HO.ring.resize((int(W * 1.6), int(H * 1.6))).crop((300, 500, 300 + W, 500 + H)))
            img = put_mei(img, 560, 2060, 1.75, pose="sit", phone=-1, gasp=0.2, look=-0.4)
            img = firecrackers(img, 590, 1440, 760, 1900, n=10, t=t)
            fx, fy = 540, 1380
            flame = ss(t, c2 - 1.8, c2 - 1.5)
            a = to_arr(img)
            if flame > 0:
                add_glow(a, gsp(380, (255, 140, 60)), fx, fy, 0.55 * flame * (0.85 + 0.15 * math.sin(t * 30)))
                add_glow(a, gsp(30, (255, 230, 150)), fx, fy - 10, 1.0 * flame)
            out = to_img(finish(to_img(a), t, VIG_H, push=1.05 + 0.05 * t / c2, cx=560, cy=1050))
            put_ui(out, "16:48", "LOST", t, 1.0, y=UI_Y, danger=True)
            return to_arr(out)
        if t < c3:                                              # the burning string thrown out of the hollow
            u = ss(t, c2, c3)

            def outside(img, t_):
                img = put_girl(img, 760, 1460, 1.7, t_, eyes=0.0, alpha=0.9)
                img = firecrackers(img, 300, 1360, 760, 1430, n=12, lit=0.0, t=t_)
                a = to_arr(img)
                add_glow(a, gsp(40, (255, 200, 120)), 300 + 20 * math.sin(t_ * 40), 1360, 1.0)
                return to_img(a)
            img = HO.frame(t, outside_extras=[outside], fogk=0.7)
            out = to_img(finish(img, t, VIG_H, push=1.06, cx=540, cy=1200, shake=0.2))
            return to_arr(out)
        u = (t - c3) / (D - c3)
        bang_end = c3 + 1.8

        def girl_scream(img, t_):
            k = 1 - ss(t_, c3 + 0.9, c3 + 1.4)
            if k <= 0:
                return img
            if int(t_ * 30) % 3 == 0 and t_ > c3 + 0.9:
                return img
            img = put_girl(img, 560, 1380, 0.62, t_, tilt=-30 * k, smile=1.0, eyes=1.0, alpha=k, aura=0.6)
            return img

        def blasts(img, t_):
            a = to_arr(img)
            hx, hy = FW.hollow
            for i, (bu, bs, bk) in enumerate(bursts):
                tt = c3 + 0.05 + bu * 1.6
                k = math.exp(-max(0, t_ - tt) * 9) if t_ >= tt else 0.0
                if k > 0.02:
                    bx, by = hx - 260 + bu * 360 + bs * 40, hy + 220 + bs * 30
                    add_glow(a, gsp(200 * bk, (255, 190, 110)), bx, by, 1.4 * k)
                    add_glow(a, gsp(30 * bk, (255, 255, 230)), bx, by, 1.5 * k)
            img = to_img(a)
            d = ImageDraw.Draw(img)
            for x, y, vx, vy, ph in conf:                       # red paper bits flying
                tt = t_ - c3
                if 0 < tt < 4:
                    px, py = x + vx * tt * 0.6, y + vy * tt + 500 * tt * tt
                    s_ = 8 + 4 * math.sin(ph + tt * 9)
                    d.polygon([(px - s_, py), (px, py - s_ * .5), (px + s_, py), (px, py + s_ * .5)], fill=(210, 30, 30, 255))
            return img
        fk = 0.85 - 0.7 * ss(t, c3 + 0.6, D)
        img = FW.frame(t, far_extras=[girl_scream], near_extras=[blasts], fogk=fk, red=1 - ss(t, c3 + 1.0, D))
        sm = ss(t, c3, c3 + 0.3) * (1 - ss(t, bang_end, D))
        lay = Image.new("RGBA", (W, H), (200, 190, 180, int(90 * sm)))
        img.alpha_composite(lay)
        hit = (t - c3) % 0.21 < 0.05 and t < bang_end
        out = to_img(finish(img, t, VIG_H, push=1.06 + 0.04 * u, cx=640, cy=1200, shake=1.0 if t < bang_end else 0.2,
                            flash=0.3 if hit else 0.0, flash_col=(255, 230, 190)))
        put_ui(out, clock_at(48, 49, u), "1.2 KM", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def torch_beams(img, t, srcs, k=1.0):
    """Torch light cones coming up from below through the fog."""
    lay = Image.new("L", (W, H), 0); d = ImageDraw.Draw(lay)
    for i, (sx, sy, tx, ty) in enumerate(srcs):
        wob = 40 * math.sin(t * 2.1 + i * 2)
        tx += wob
        ang = math.atan2(ty - sy, tx - sx); ln = math.hypot(tx - sx, ty - sy) * 1.3
        spread = 0.09
        d.polygon([(sx, sy), (sx + math.cos(ang - spread) * ln, sy + math.sin(ang - spread) * ln),
                   (sx + math.cos(ang + spread) * ln, sy + math.sin(ang + spread) * ln)], fill=110)
    lay = lay.filter(ImageFilter.GaussianBlur(26))
    a = to_arr(img) + np.asarray(lay, np.float32)[..., None] / 255 * np.array([255, 235, 200], np.float32) * 0.75 * k
    return to_img(a)


def make_run(D, caps):
    TR = trail(True)
    t2 = caps[1][1]

    def f(t):
        u = ss(t, 0, D)

        def runner(img, t_):
            x, y, sc = TR.P.at(0.5 - 0.32 * u)
            return put_mei(img, x, y, sc * 1.05, pose="run", phase=(t_ * 2.6) % 1, gasp=0.4)
        img = TR.frame(t, path_extras=[runner], fogk=0.5, red=0.0)
        x, y, sc = TR.P.at(0.5 - 0.32 * u)
        img = torch_beams(img, t, [(150, 1980, x - 40, y - 300), (900, 1990, x + 60, y - 260)], k=0.6 + 0.4 * ss(t, t2 - 0.5, t2 + 0.5))
        k = ss(t, t2 - 0.3, t2 + 0.5)
        if k > 0:                                             # Grandpa in the foreground, torch up, calling
            img = put_hiker(img, "grandpa", 200, 2160, 1.2, 0.0, alpha=k, dark=0.35)
            a = to_arr(img); add_glow(a, gsp(60, (255, 240, 200)), 330, 1500, 1.0 * k); img = to_img(a)
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.06 * u, cx=540, cy=1150, shake=0.3))
        put_ui(out, clock_at(80, 86, u), f"{0.6 - 0.4 * u:.1f} KM", t, 1.0, y=UI_Y, night=True)
        return to_arr(out)
    return f


def make_twist(D, caps):
    RM = room(); TR = trail(False)
    c2, c3 = caps[1][1], caps[2][1]
    jt = D - 1.0
    vid = {}

    def video_inset(t):
        """The home video playing on Mei's phone (shown as an inset): the family on the steps... and no girl."""
        key = int(t * 6)
        if key not in vid:
            img, pos = family_video(TR, t, 0.004 * t, girl_on=False)
            img = camcorder(img, t, stamp=f"16:21:{7 + int(t) % 50:02d}")
            for i in range(3):
                tt = c2 + 0.7 + i * 0.6
                x, y = pos[i]
                img = count_num(img, i + 1, x, y - 40, ss(t, tt, tt + 0.25))
            crop = img.crop((90, 700, 990, 1600)).resize((540, 540), Image.LANCZOS)
            fr = Image.new("RGBA", (560, 560), (20, 20, 24, 255)); fr.alpha_composite(crop, (10, 10))
            vid.clear(); vid[key] = fr
        return vid[key]

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="smile", scale=1.45, y=900, tilt=-8, bg=(18, 10, 16))
        step = 0 if t < c3 + 0.4 else (1 if t < c3 + 1.4 else 2)

        def behind(img, t_):
            k = ss(t_, c2 + 1.2, c2 + 2.0)
            if k <= 0:
                return img
            if step == 0:
                return put_girl(img, RM.door[0], RM.door[1], 0.82, t_, tilt=-15, eyes=k, alpha=k, dark=0.35)
            if step == 1:
                return put_girl(img, 820, 1460, 1.05, t_, tilt=-20, eyes=1.0, dark=0.3)
            return put_girl(img, 790, 1600, 1.0, t_, tilt=-28, smile=1.0, eyes=1.0, dark=0.2)

        def mei_(img, t_):
            return put_mei(img, 470, 1900, 1.15, pose="sit", phone=1.0, look=-0.6 * ss(t_, c3 + 1.8, jt), gasp=0.5 * ss(t_, c3 + 2.2, jt))
        img = RM.frame(t, back_extras=[behind], front_extras=[mei_])
        a = to_arr(img); add_glow(a, gsp(220, (170, 200, 255)), 470, 1450, 0.4); img = to_img(a)
        if step >= 2:
            img = count_num(img, 4, 790, 640, ss(t, c3 + 1.6, c3 + 1.9), red=True, sc=1.2)
        zk = ss(t, c3 + 1.4, jt)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.35 * zk, cx=540 + 160 * zk, cy=1100 + 60 * zk,
                            shake=0.4 if abs(t - c3 - 0.4) < 0.08 or abs(t - c3 - 1.4) < 0.08 else 0.0))
        k = ss(t, 0.3, 0.8) * (1 - ss(t, c3 + 0.2, c3 + 0.6))
        if k > 0:
            out.alpha_composite(with_alpha(video_inset(t), k), (int(W / 2 - 280), 300))
        return to_arr(out)
    return f


def make_explain(D, caps):
    SH = shrine()
    title = text_img("MO-SIN-A", font(LORA, 116, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    cj = text_img("魔神仔", ImageFont.truetype(CJK, 64), fill=(255, 200, 120, 255), pad=10)
    sub = text_img("Taiwan's mountain spirit", font(INTER_SB, 36), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 36)
    c1, c2 = (110, 20, 24, 235), (90, 40, 10, 235)
    chips = [pill("A spirit of Taiwan's mountains + forests", pf, fill=c1, h=78),
             pill("Often small... like a child", pf, fill=c1, h=78),
             pill("It leads people lost, deep into the hills", pf, fill=c1, h=78),
             pill("Usually children and the elderly", pf, fill=c1, h=78),
             pill("It hates loud noise: firecrackers!", pf, fill=c1, h=78),
             pill("1990s: a hiking video on Taiwanese TV", pf, fill=c2, outline=(255, 200, 110, 255), h=78),
             pill("A girl in red nobody had seen that day", pf, fill=c2, outline=(255, 200, 110, 255), h=78)]
    ts = [caps[0][1] + 0.8, caps[0][2] - 1.6, caps[1][1] + 0.6, caps[1][1] + 3.0, caps[1][2] - 1.4, caps[2][1] + 0.6, caps[2][1] + 4.0]
    bg = {}

    def f(t):
        key = int(t * 6)
        if key not in bg:
            def her(img, t_):
                return put_girl(img, 990, 1230, 0.3, t_, tilt=-20, eyes=0.8, dark=0.3)
            img = SH.frame(t, extras=[her])
            bg.clear(); bg[key] = finish(img, t, VIG_H, push=1.05 + 0.04 * t / D, cx=600, cy=1100) * 0.5
        out = to_img(bg[key])
        fw = flag_wave(t, 170)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 50))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 180))
        row = Image.new("RGBA", (cj.width + sub.width, max(cj.height, sub.height)), (0, 0, 0, 0))
        row.alpha_composite(cj, (0, 0)); row.alpha_composite(sub, (cj.width, (cj.height - sub.height) // 2))
        out.alpha_composite(with_alpha(row, ss(t, 0.5, 1.1)), (int(W / 2 - row.width / 2), 330))
        chips_at(out, chips, ts, t, 450, 92)
        return to_arr(out)
    return f


def make_outro(D, caps):
    TR = trail(False)
    q = text_img("Would YOU have", font(LORA, 96, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("answered?", font(LORA, 104, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 42)
    opts = [("Answer Grandpa", (150, 30, 30, 235)), ("Stay silent", (60, 40, 40, 235)), ("Follow the ribbons", (110, 60, 30, 235)), ("Firecrackers!", (160, 40, 20, 235))]
    chips = [pill(n, pf, fill=c, h=88) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    bg = {}

    def f(t):
        key = int(t * 8)
        if key not in bg:
            def her(img, t_):
                x, y, sc = TR.P.at(0.7)
                return put_girl(img, x, y, sc * 0.9, t_, tilt=-18, eyes=1.0)
            img = TR.frame(t, path_extras=[her], fogk=0.4)
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
