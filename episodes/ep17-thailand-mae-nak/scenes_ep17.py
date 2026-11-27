"""Ep17 Thailand / Mae Nak - scenes (2.1D survival). Each make_<id>(D, caps) returns f(t) -> float RGB (H, W, 3)."""
from art_ep17 import *

if os.environ.get("NO_UI"):                       # covers: no night/temple pill under the cover header
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


def jump(t, jt, mode="smile", inv=False, scale=1.3, y=880, tilt=0.0, x=540, bg=(6, 1, 2)):
    img = nface_full(t, jt, mode=mode, inv=inv, scale=scale, y=y, tilt=tilt, x=x, bg=bg)
    fl = 0.85 if t < jt + 0.08 else 0.0
    return finish(img, t, VIG_H, push=1.0 + 0.4 * ss(t, jt, jt + 0.18), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))


def stop_motion(u, steps):
    return math.floor(max(0.0, min(1.0, u)) * steps) / steps


def porch_scene(HS, t, pest, lime_state, arm_u, ghost=0.0, nak_x=820):
    """Nak kneeling on the porch at the mortar. lime_state: (x, y) of the lime or None. arm_u 0..1: her right arm
    reaching from the shoulder down through the plank gap to the lime on the ground (0 = not reaching)."""
    def porch(img, t_):
        img = HS.mortar_img(img, pest if arm_u <= 0 else 0.0)
        img, shp = put_nak(img, nak_x, HS.floor + 2, 0.42, t_, pose="kneel", ghost=ghost, eyes=ghost)
        porch.sh = shp
        return img

    def under(img, t_):
        if lime_state is not None:
            img = put_lime(img, lime_state[0], lime_state[1], 12, glow=0.5)
        if arm_u > 0:
            sx, sy = porch.sh
            gx, gy = HS.gap
            long_arm(img, (sx - 4, sy + 6), (gx, gy - 6), t_, width=16, fingers=0.0)
            lx, ly = HS.lime
            hx, hy = gx + (lx - gx) * arm_u, gy + (ly - 20 - gy) * arm_u
            long_arm(img, (gx, gy), (hx, hy), t_, width=18, bend=0.3)
        return img
    return porch, under


# ============================================================ PART 1
def make_hook(D, caps):
    HS = house()
    hdr = series_header("THAILAND", "PART 1")
    t2 = caps[1][1]
    jt = D - 0.7
    r0, r1, r2 = 1.0, 2.1, 2.6                                   # lime rolls, reaches the gap, lands
    reach_end = caps[1][2] - 0.2

    def f(t):
        if t >= jt:
            return jump(t, jt, scale=1.35, tilt=-10, x=600)
        mx, my = HS.mortar
        gx, gy = HS.gap
        lx, ly = HS.lime
        if t < r0:
            lime = (mx + 40, my - 12)
        elif t < r1:
            u = ss(t, r0, r1); lime = (mx + 40 + (gx - mx - 40) * u, my - 12)
        elif t < r2:
            u = (t - r1) / (r2 - r1); lime = (gx + (lx - gx) * u, gy + (ly - gy) * u * u)
        else:
            lime = (lx, ly)
        arm_u = stop_motion(ss(t, t2 + 0.3, reach_end), 5) if t > t2 + 0.3 else 0.0
        pest = abs(math.sin(t * 5)) if t < r1 else 0.0
        porch, under = porch_scene(HS, t, pest, lime, arm_u, ghost=ss(t, t2, t2 + 1.0))
        img = HS.frame(t, porch=[porch], extras=[under])
        zk = ss(t, t2, jt)
        cut = any(abs(t - (t2 + 0.3 + k * (reach_end - t2 - 0.3) / 5)) < 0.035 for k in range(1, 5))
        a = finish(img, t, VIG_H, push=1.06 + 0.04 * t / D + 0.35 * zk, cx=600 + 120 * zk, cy=1000 + 300 * zk,
                   flash=0.25 if cut else 0.0, flash_col=(255, 40, 30))
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_setup(D, caps):
    K = klong()
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        cam = -200 + 260 * t / D

        def boat(img, t_, o):
            bob = 5 * math.sin(t_ * 1.6)
            x = 330 + 80 * t_ / D
            b = boat_sprite(560)
            img.alpha_composite(b, (int(x - 40), int(1290 + bob)))
            im, fx, fy = mak(0.0, oar=True, scale=0.42, look=-0.2)
            return put_sprite(img, im, x + 300, 1374 + bob, fx, fy)

        def watcher(img, t_, o):                           # the viewer sees her first: a woman with a baby on the far bank
            k = ss(t_, t3 + 0.4, t3 + 1.4)
            if k <= 0:
                return img
            img, _ = put_nak(img, 870 + 0.1 * cam, 1000, 0.085, t_, pose="baby", ghost=0.0, eyes=0.8 * k, alpha=k)
            return img
        img = K.frame(t, cam, water_extras=[watcher, boat])
        zk = ss(t, t3 + 0.6, D)
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.05 * t / D + 0.6 * zk, cx=540 + 330 * zk, cy=1150 - 160 * zk))
        put_ui(out, clock_at(100, 105, t / D), "2 KM", t, ss(t, t2 - 0.2, t2 + 0.3), y=UI_Y)
        return to_arr(out)
    return f


def make_rule(D, caps):
    K = klong()
    f1 = font(INTER_SB, 44)
    oc, fc = (255, 200, 120, 255), (70, 30, 20, 230)
    chips = [pill("THE OLD BOATMAN'S WARNING", f1, outline=oc, fill=fc, color=(255, 220, 160, 255), h=86),
             pill("1. WATCH HER ARMS", f1, outline=oc, fill=fc, color=(255, 240, 220, 255), h=92),
             pill("2. NEVER LET HER KNOW YOU SAW", f1, outline=oc, fill=fc, color=(255, 240, 220, 255), h=92),
             pill("3. RUN TO THE TEMPLE", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [0.3, caps[2][1] + 0.2, caps[2][1] + 1.6, caps[2][2] - 1.2]
    bg = {}

    def f(t):
        key = int(t * 10)
        if key not in bg:
            def boats(img, t_, o):
                bob = 5 * math.sin(t_ * 1.6)
                b = boat_sprite(560)
                img.alpha_composite(b, (60, int(1300 + bob)))
                im, fx, fy = mak(0.0, oar=True, scale=0.42, look=0.0, gasp=0.6 * ss(t_, caps[1][1], caps[1][1] + 0.5))
                img = put_sprite(img, im, 330, 1384 + bob, fx, fy)
                b2 = boat_sprite(440).transpose(Image.FLIP_LEFT_RIGHT)
                img.alpha_composite(b2, (560, int(1340 - bob)))
                bm = boatman_sprite()
                img.alpha_composite(bm, (700, int(1040 - bob)))
                return img
            img = K.frame(t, 60, water_extras=[boats])
            bg.clear(); bg[key] = finish(img, t, VIG_H, push=1.25 + 0.05 * t / D, cx=560, cy=1250) * 0.75
        out = to_img(bg[key])
        chips_at(out, chips, ts, t, 240, 118)
        return to_arr(out)
    return f


def make_home(D, caps):
    HS = house()
    t2, t3 = caps[1][1], caps[2][1]
    quiet = t2 + 0.4

    def f(t):
        def porch(img, t_):
            img, _ = put_nak(img, 820, HS.floor + 2, 0.4, t_, pose="baby", ghost=0.0)
            return img

        def wall(img, t_):                                 # her shadow on the wall... its arm is far too long
            k = ss(t_, t2 + 0.6, t2 + 1.6)
            if k <= 0:
                return img
            body, ax, ay, ee, shr = nak("stand", 0.0, 0.0)
            sh = tint(body, (0, 0, 0), alpha=0.6 * k).resize((int(body.width * 0.46), int(body.height * 0.46)))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            bx, by = 470 - ax * 0.46, HS.floor - ay * 0.46
            lay.alpha_composite(sh, (int(bx), int(by)))
            sx, sy = bx + shr[0] * 0.46, by + shr[1] * 0.46
            reach = ss(t_, t2 + 1.0, D)
            ImageDraw.Draw(lay).line([(sx - 50, sy + 10), (sx - 60 - 260 * reach, sy + 80 + 120 * reach)], fill=(0, 0, 0, int(150 * k)), width=14)
            m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([130, 540, 610, HS.floor], fill=255)
            la = np.asarray(lay).copy(); la[..., 3] = (la[..., 3].astype(np.float32) * np.asarray(m, np.float32) / 255).astype(np.uint8)
            img.alpha_composite(Image.fromarray(la, "RGBA"))
            return img

        def ground(img, t_):
            for i, x in enumerate((420, 600)):
                bark = abs(math.sin(t_ * 9 + i)) if t_ < quiet else 0.0
                dg = dog_sprite(bark)
                if t_ >= quiet:
                    dg = dg.transpose(Image.FLIP_LEFT_RIGHT)                  # they turn away and cower
                img.alpha_composite(dg.resize((150, 110)), (x - 75, HS.ground - 100 + (8 if t_ >= quiet else 0)))
            u = ss(t_, 0.0, t2)
            im, fx, fy = mak((t_ * 1.6) % 1 if u < 1 else 0.0, back=False, scale=0.52)
            return put_sprite(img, im, 1160 - 230 * u, HS.ground + 10, fx, fy)
        img = HS.frame(t, porch=[porch], wall_fx=[wall], extras=[ground])
        zk = ss(t, t3 - 0.3, D)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.04 * t / D + 0.3 * zk, cx=620 - 140 * zk, cy=900 - 140 * zk))
        put_ui(out, clock_at(118, 120, t / D), "800 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_lime(D, caps):
    HS = house()
    t2, t3 = caps[1][1], caps[2][1]
    r0, r1, r2 = t2 + 0.5, t2 + 1.6, t2 + 2.1

    def f(t):
        mx, my = HS.mortar
        gx, gy = HS.gap
        lx, ly = HS.lime
        if t < r0:
            lime = (mx + 40, my - 12)
        elif t < r1:
            u = ss(t, r0, r1); lime = (mx + 40 + (gx - mx - 40) * u, my - 12)
        elif t < r2:
            u = (t - r1) / (r2 - r1); lime = (gx + (lx - gx) * u, gy + (ly - gy) * u * u)
        else:
            lime = (lx, ly)
        arm_u = stop_motion(ss(t, t3 + 0.6, caps[2][2] + 0.2), 6) if t > t3 + 0.6 else 0.0
        porch, under = porch_scene(HS, t, abs(math.sin(t * 5)) if t < r1 else 0.0, lime, arm_u, ghost=0.0)

        def mak_(img, t_):
            im, fx, fy = mak(0.0, scale=0.5, look=ss(t_, r1, r2) - 0.4 * ss(t_, t3 + 0.8, D), gasp=0.5 * ss(t_, t3 + 1.5, D))
            img = put_sprite(img, im, 420, HS.ground + 6, fx, fy)
            return img
        img = HS.frame(t, porch=[porch], extras=[mak_, under])
        zk = ss(t, t3, D)
        cut = any(abs(t - (t3 + 0.6 + k * (caps[2][2] - 0.4 - t3) / 6)) < 0.035 for k in range(1, 6))
        out = to_img(finish(img, t, VIG_H, push=1.06 + 0.4 * ss(t, t2, r0) - 0.4 * ss(t, r2, t3) + 0.5 * zk,
                            cx=700 - 120 * zk, cy=920 + 380 * zk, flash=0.2 if cut else 0.0, flash_col=(255, 40, 30)))
        put_ui(out, clock_at(160, 162, t / D), "800 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_mistake(D, caps):
    HS = house()
    t3 = caps[2][1]
    jt = D - 0.6

    def f(t):
        if t >= jt:
            return jump(t, jt, inv=True, scale=1.4, y=820)
        porch, under = porch_scene(HS, t, 0.0, None, 1.0, ghost=1.0)
        drop = ss(t, t3 - 0.6, t3 + 0.6)

        def mak_(img, t_):
            im, fx, fy = mak(0.0, scale=0.5, look=0.6 - 0.8 * ss(t_, t3, t3 + 0.5), gasp=ss(t_, 0.2, 0.5))
            return put_sprite(img, im, 420, HS.ground + 6, fx, fy)

        def head(img, t_):                                     # her upside-down face comes down under the floor beside him
            if drop <= 0:
                return img
            y = HS.floor + 44 - 180 + 330 * ease(drop)
            if y - 90 > HS.floor + 30:
                ImageDraw.Draw(img).rectangle([540, HS.floor + 30, 600, y - 90], fill=(10, 8, 10, 255))   # hair hanging up to the gap
            return put_nface(img, 570, y, 0.32, t_, inv=True, aura=0.6)

        def lime_hand(img, t_):
            lx, ly = HS.lime
            img = put_lime(img, lx, ly - 4, 12, glow=0.3)
            return img
        img = HS.frame(t, porch=[porch], extras=[lime_hand, under, mak_, head], under_light=1.0 - 0.7 * ss(t, caps[1][1], caps[1][1] + 0.6))
        hit = 0.2 < t < 0.35
        out = to_img(finish(img, t, VIG_H, push=1.75 + 0.15 * t / D, cx=560, cy=1250, shake=0.5 if hit else 0.0,
                            flash=0.25 if hit else 0.0, flash_col=(255, 40, 30)))
        put_ui(out, clock_at(162, 163, t / D), "800 M", t, 1.0, y=UI_Y, danger=t > t3)
        return to_arr(out)
    return f


def make_cliff(D, caps):
    K = klong(); NB = natbush()
    t2, t3 = caps[1][1], caps[2][1]
    cut = caps[0][2] - 0.5
    jt = D - 1.1

    def f(t):
        if t < cut:
            u = t / cut
            cam = -250 + 420 * u

            def runner(img, t_, o):
                im, fx, fy = mak((t_ * 2.6) % 1, run=1.0, scale=0.48)
                return put_sprite(img, im, 260 + 520 * u, K.path_y + 6 * math.sin(t_ * 20), fx, fy)

            def follower(img, t_, o):                          # far behind, over the water: something pale, following
                gap = 420 - 160 * stop_motion(u, 4)
                img, _ = put_nak(img, 260 + 520 * u - gap, 1380, 0.3, t_, pose="float", ghost=1.0, aura=0.5)
                return img
            img = K.frame(t, cam, water_extras=[follower], bank_extras=[runner])
            out = to_img(finish(img, t, VIG_H, push=1.12, cx=540, cy=1300, shake=0.3))
            put_ui(out, clock_at(165, 168, u), "600 M", t, 1.0, y=UI_Y)
            return to_arr(out)
        if t >= jt:
            return jump(t, jt, scale=1.35, y=860)
        come = ss(t, t2 - 0.4, t2 + 1.6)
        s_ = 0.35 + 0.8 * stop_motion(come, 4)

        def her(img, t_):
            if come <= 0:
                return img
            img, _ = put_nak(img, 560, 1200 + 520 * (s_ - 0.35) / 0.8, s_, t_, pose="float", ghost=1.0, aura=0.5, alpha=ss(t_, t2 - 0.4, t2))
            return img
        img = NB.frame(t, extras=[her], sway=0.4)
        zk = ss(t, t3, jt)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.25 * zk, cx=540, cy=900, shake=0.4 if abs(t - t2 - 1.6) < 0.1 else 0.0))
        put_ui(out, clock_at(170, 171, t / D), "500 M", t, 1.0, y=UI_Y, danger=True)
        return to_arr(out)
    return f


# ============================================================ PART 2
def make_recap(D, caps):
    NB = natbush()
    hdr = series_header("THAILAND", "PART 2")

    def f(t):
        def her(img, t_):
            img, _ = put_nak(img, 560, 1720, 1.15, t_, pose="float", ghost=1.0, aura=0.5)
            return img
        img = NB.frame(t, extras=[her], sway=0.4)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.05 * t / D, cx=540, cy=1000))
        put_header(out, hdr, t)
        put_ui(out, "2:51", "500 M", t, ss(t, 2.0, 2.4), y=680, danger=True)
        return to_arr(out)
    return f


def make_bush(D, caps):
    NB = natbush()
    t2, t3 = caps[1][1], caps[2][1]
    back = t2 + 1.4
    jt = t3 - 0.05

    def f(t):
        if t >= jt:
            return jump(t, jt, mode="scream", scale=1.45, y=860)
        lean = ss(t, t2 - 0.6, t2 + 0.3) * (1 - ss(t, back, back + 0.6))

        def her(img, t_):
            if lean < 0.95:
                img, _ = put_nak(img, 560, 1720 - 300 * ss(t_, back, back + 0.6), 1.15 - 0.4 * ss(t_, back, back + 0.6), t_,
                                 pose="float", ghost=1.0, aura=0.5, alpha=1 - lean)
            if lean > 0:
                sniff = 8 * math.sin(t_ * 14) * (t_ < back)
                img = put_nface(img, 540, 980 + sniff, 0.5 + 0.25 * lean, t_, aura=0.5, alpha=lean)
            return img
        img = NB.frame(t, extras=[her], sway=0.4 + 1.5 * ss(t, back, back + 0.3))
        out = to_img(finish(img, t, VIG_H, push=1.05 + 0.12 * lean, cx=540, cy=980, shake=0.6 * ss(t, back, back + 0.2) * (1 - ss(t, back + 0.4, back + 0.8))))
        put_ui(out, "2:52", "500 M", t, 1.0, y=UI_Y, danger=True)
        return to_arr(out)
    return f


def make_run(D, caps):
    K = klong()
    t2 = caps[1][1]

    def f(t):
        u = t / D
        cam = -260 + 560 * u
        mx = 620 + 30 * math.sin(t * 1.3)

        def runner(img, t_, o):
            im, fx, fy = mak((t_ * 2.8) % 1, run=1.0, scale=0.5)
            return put_sprite(img, im, mx, K.path_y + 6 * math.sin(t_ * 22), fx, fy)

        def her(img, t_, o):
            k = ss(t_, t2 - 0.6, t2 + 0.2)
            if k <= 0:
                return img
            img, sh = put_nak(img, 150, 1360 + 10 * math.sin(t_ * 2), 0.34, t_, pose="float", ghost=1.0, aura=0.6, alpha=k)
            gap = 420 - 330 * stop_motion(ss(t_, t2, D), 5)
            if k > 0.5:
                long_arm(img, (sh[0] - 20, sh[1] + 10), (mx - gap, K.path_y - 230), t_, width=16, bend=-0.5)
            return img
        img = K.frame(t, cam, water_extras=[her], bank_extras=[runner])
        out = to_img(finish(img, t, VIG_H, push=1.1 + 0.08 * u, cx=520, cy=1300, shake=0.35))
        dist = int(450 - 400 * u)
        put_ui(out, clock_at(173, 178, u), f"{dist // 10 * 10} M", t, 1.0, y=UI_Y, danger=True)
        return to_arr(out)
    return f


def make_temple(D, caps):
    TG = temple(False)
    t2, t3 = caps[1][1], caps[2][1]
    fall = caps[0][2]

    def f(t):
        arrive = ss(t, t2 - 0.6, t2 + 0.4)

        def outside(lay, t_):
            if arrive <= 0:
                return lay
            sc = 0.3 + 0.25 * stop_motion(arrive, 3)
            lay, _ = put_nak(lay, 540, 1500, sc, t_, pose="baby", ghost=1.0, aura=0.6, alpha=min(1, arrive * 2))
            return lay

        def inside(img, t_):
            u = ss(t_, 0.0, fall)
            if t_ < fall:
                im, fx, fy = mak((t_ * 2.8) % 1, run=1.0, scale=0.3 + 0.35 * u)
                return put_sprite(img, im, 540 - 200 * u, 1500 + 330 * u, fx, fy)
            im, fx, fy = mak_crouch(0.62, look=0.4, cover=0.0)
            return put_sprite(img, im, 300, 1900, fx, fy)
        glow = 0.6 * ss(t, t2 + 0.2, t2 + 0.6) * (0.7 + 0.3 * math.sin(t * 6))
        img = TG.frame(t, outside=[outside], inside=[inside], line_glow=glow)
        zk = ss(t, t3 - 0.4, D)
        hit = fall - 0.05 < t < fall + 0.12
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.45 * zk, cx=540, cy=1000 + 150 * zk, shake=0.6 if hit else 0.0))
        put_ui(out, clock_at(180, 181, t / D), "0 M", t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_twist(D, caps):
    TG = temple(True)
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.0

    def f(t):
        if t >= jt:
            return jump(t, jt, scale=1.45, y=900, tilt=-6, bg=(40, 14, 16))
        walk = ss(t, 0.2, t2 - 0.2)

        def outside(lay, t_):                                   # far away on the canal path... someone is watching
            k = ss(t_, t2 + 0.5, t2 + 1.5)
            if k > 0:
                lay, _ = put_nak(lay, 690, 1300, 0.13, t_, pose="baby", ghost=1.0, alpha=k, eyes=k)
            return lay

        def inside(img, t_):
            im, fx, fy = mak_crouch(0.62, look=0.3 * ss(t_, 0, t2), cover=0.0)
            img = put_sprite(img, im, 230, 1900, fx, fy)
            lu = ss(t_, t3 - 0.2, t3 + 0.6)
            bs, bx, by = boy_sprite(round(lu, 1))
            sc = 0.45 + 0.4 * walk
            bs2 = bs.resize((int(bs.width * sc), int(bs.height * sc)), Image.LANCZOS)
            return put_sprite(img, bs2, 560 - 60 * walk, 1520 + 300 * walk, bx * sc, by * sc)
        img = TG.frame(t, outside=[outside], inside=[inside])
        zk = ss(t, t3, jt)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 1.0 * zk, cx=540 + 40 * zk, cy=1300 - 120 * zk))
        put_ui(out, "5:52", "0 M", t, 1.0 - ss(t, t3, t3 + 0.4), y=UI_Y)
        return to_arr(out)
    return f


def make_explain(D, caps):
    SH = shrine()
    title = text_img("MAE NAK", font(LORA, 120, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("of Phra Khanong - Thailand's most famous ghost", font(INTER_SB, 34), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 36)
    c1, c2 = (110, 20, 24, 235), (90, 40, 10, 235)
    chips = [pill("A young wife by the Phra Khanong canal", pf, fill=c1, h=78),
             pill("She died giving birth while Mak was at war", pf, fill=c1, h=78),
             pill("...but she was waiting when he came home", pf, fill=c1, h=78),
             pill("She dropped a lime - her arm stretched down", pf, fill=c1, h=78),
             pill("Ghosts fear nat leaves + temple ground", pf, fill=c1, h=78),
             pill("Today: her shrine at Wat Mahabut, Bangkok", pf, fill=c2, outline=(255, 200, 110, 255), h=78),
             pill("People bring dresses + toys for her baby", pf, fill=c2, outline=(255, 200, 110, 255), h=78)]
    ts = [caps[0][1] + 1.0, caps[1][1], caps[1][1] + 2.0, caps[1][2] - 0.8, caps[1][2] + 0.1, caps[2][1] + 0.2, caps[2][1] + 2.4]
    bg = {}

    def f(t):
        key = int(t * 6)
        if key not in bg:
            img = SH.frame(t)
            bg.clear(); bg[key] = finish(img, t, VIG_H, push=1.05 + 0.04 * t / D, cx=540, cy=1000) * 0.5
        out = to_img(bg[key])
        fw = flag_wave(t, 170)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 60))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 190))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 352))
        chips_at(out, chips, ts, t, 440, 92)
        return to_arr(out)
    return f


def make_outro(D, caps):
    HS = house()
    q = text_img("Would YOU have", font(LORA, 96, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("run... or stayed?", font(LORA, 92, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Run to the temple", (150, 30, 30, 235)), ("Stay with Nak", (60, 40, 40, 235)), ("Hide in the nat", (60, 90, 60, 235)), ("Pick up the lime", (90, 120, 40, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)
    bg = {}

    def f(t):
        key = int(t * 8)
        if key not in bg:
            def porch(img, t_):
                img, _ = put_nak(img, 820, HS.floor + 2, 0.5, t_, pose="baby", ghost=1.0, aura=0.5)
                return img
            img = HS.frame(t, porch=[porch])
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
