"""Ep14 Philippines / Tikbalang - scenes (2.1D survival). Each make_<id>(D, caps) returns f(t) -> float RGB (H, W, 3)."""
from art_ep14 import *

if os.environ.get("NO_UI"):                       # covers: no phone pill under the cover header
    def put_phone(*a, **k):
        pass

UI_Y = 200


def batt(sid, t, D):
    """Story clock: phone battery per scene (start, end)."""
    a, b = {"setup": (9, 9), "rain": (8, 8), "loop": (7, 5), "mistake": (5, 4), "cliff": (4, 3),
            "recap": (3, 3), "under": (3, 2), "chase": (2, 0)}[sid]
    return a + (b - a) * min(1.0, t / D)


def chips_at(out, chips, ts, t, y0, gap=110):
    for i, (c, tt) in enumerate(zip(chips, ts)):
        k = ss(t, tt - 0.15, tt + 0.3)
        if k > 0:
            cc = c if c.width <= W - 40 else c.resize((W - 40, int(c.height * (W - 40) / c.width)), Image.LANCZOS)
            out.alpha_composite(with_alpha(cc, k), (int(W / 2 - cc.width / 2), int(y0 + i * gap + 20 * (1 - k))))


def put_sprite(img, spr, x, y, fx, fy):
    img.alpha_composite(spr, (int(x - fx), int(y - fy)))
    return img


def torch(img, x, y, k=1.0, r=220):
    """Phone torch: a small bright point + a soft white-warm cone of light ahead."""
    a = to_arr(img)
    add_glow(a, gsp(r, (255, 220, 180)), x, y, 0.45 * k)
    add_glow(a, gsp(30, (255, 250, 230)), x, y, 1.0 * k)
    return to_img(a)


# ============================================================ PART 1
def make_hook(D, caps):
    B = balete()
    hdr = series_header("PHILIPPINES", "PART 1")
    t2 = caps[1][1]
    px, py = B.perch

    def f(t):
        hit = t2 - 0.05 <= t < t2 + 0.12
        ek = 0.35 + 0.65 * ss(t, t2 - 0.2, t2 + 0.1)
        def tk(img, tt, o):
            return put_tik(img, 560 + o, 1500, 0.72, tt, pose="squat", grin=0.9 * ss(tt, t2, t2 + 0.6), eyes=ek, aura=0.3 + 0.5 * ek, sway=False)
        img = B.frame(t, cam=-20 + 40 * t / D, extras=[(1, tk)])
        rain(img, t, 0.35)
        z = 1.0 + 0.05 * t / D + 0.5 * ss(t, t2 - 0.1, t2 + 1.4)
        a = finish(img, t, VIG_H, push=z, cx=540 + 20 * ss(t, t2 - 0.1, t2 + 1.4), cy=960 + 60 * ss(t, t2 - 0.1, t2 + 1.4),
                   shake=0.8 if hit else 0.0, flash=0.5 if t2 - 0.05 <= t < t2 + 0.05 else 0.0, flash_col=(255, 30, 20))
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_setup(D, caps):
    R = roadside(); P = R.P
    t3 = caps[2][1]

    def f(t):
        u = ss(t, 0.0, 5.5)
        z = 0.9 + 9.0 * u ** 1.3                                    # the jeepney pulls away toward the horizon
        def jeep(img, tt, o):
            if z > 9.5:
                return img
            x, y = P.p(0.2, 1.0, z)
            sc = 0.62 / z
            j = jeepney_rear(sc)
            a = 1.0 - ss(tt, 4.8, 5.6)
            img.alpha_composite(with_alpha(j, a), (int(x - j.width / 2 + o), int(y - j.height + 4)))
            ar = to_arr(img)
            for sx in (-1, 1):
                add_glow(ar, gsp(max(8, int(90 / z)), (255, 40, 30)), x + sx * 260 * sc + o, y - 0.34 * 640 * sc, 0.9 * a)
            return to_img(ar)
        def boy(img, tt, o):
            h, fx, fy, _ = paolo(0.0, back=True, scale=0.6)
            return put_sprite(img, h, 680 + o * 1.4, 1620, fx, fy)
        img = R.frame(t, cam=-20 + 40 * t / D, extras=[(3, jeep), (1, boy)])
        push = 1.04 + 0.08 * t / D
        out = to_img(finish(img, t, VIG_H, push=push, cx=520, cy=1050))
        if t > t3 - 0.2:
            put_phone(out, batt("setup", t, D), 2.0, t, ss(t, t3 - 0.2, t3 + 0.3), y=UI_Y)
        return to_arr(out)
    return f


def make_rule(D, caps):
    BP = bamboo(33)
    f1 = font(INTER_SB, 44)
    chips = [pill("LOLA'S RULES", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 220, 160, 255), h=86),
             pill("1. ASK PERMISSION TO PASS", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("2. LOST? SHIRT INSIDE OUT", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [0.3, caps[0][1] + 0.6, caps[1][1] + 0.8]

    def f(t):
        def boy(img, tt, o):
            z = 1.25 + 0.5 * tt / D
            h, fx, fy, pp = paolo((tt * 1.0) % 1, back=True, scale=BP.P.scale_at(z, 0.95, 815))
            x, y = BP.P.p(0.05, 1.0, z)
            img = put_sprite(img, h, x + o, y, fx, fy)
            return img
        img = BP.frame(t, cam=10 * math.sin(t * 0.5), extras=[(1.3, boy)], fogk=0.45)
        img = torch(img, 590, 1000, 0.7, r=260)
        a = to_arr(img)
        lum = a.mean(2, keepdims=True)                                             # a faded memory tint
        a = a * 0.55 + lum * np.array([1.4, 0.85, 0.65]) * 0.45
        img = to_img(a)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.08 * t / D, cx=540, cy=1000))
        chips_at(out, chips, ts, t, 260, 118)
        return to_arr(out)
    return f


def make_rain(D, caps):
    BP = bamboo(21)
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        def tk(img, tt, o):
            if tt < t3 - 0.6:
                return img
            k = ss(tt, t3 - 0.6, t3 + 0.2)
            x, y = BP.P.p(-0.42, 1.0, 4.0)
            return put_tik(img, x + o, y, BP.P.scale_at(4.0, 3.0, 1550), tt, dark=0.55, eyes=k, aura=0.35 * k, alpha=k)
        def boy(img, tt, o):
            z = 0.95
            h, fx, fy, _ = paolo((tt * 1.0) % 1, back=True, scale=BP.P.scale_at(z, 0.95, 815))
            x, y = BP.P.p(0.06, 1.0, z)
            return put_sprite(img, h, x + o, y, fx, fy)
        rk = ss(t, 0.3, 1.8)
        img = BP.frame(t, cam=-30 + 60 * t / D, extras=[(4.0, tk), (0.95, boy)], rain_k=rk)
        img = torch(img, 760, 1130, 0.8, r=260)
        zk = ss(t, t3 - 0.2, t3 + 1.4)
        push = 1.04 + 0.06 * t / D + 0.5 * zk
        out = to_img(finish(img, t, VIG_H, push=push, cx=540 - 140 * zk, cy=900 + 40 * zk))
        if t < t2 + 0.4 and t > 0.4:
            pass
        put_phone(out, batt("rain", t, D), 1.6 - 0.4 * min(1, t / D), t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_loop(D, caps):
    BP = bamboo(21)
    cuts = [0.0, caps[1][1] - 0.1, caps[1][1] + 1.0, caps[2][1] - 0.1]
    tz = [6.0, 4.2, 3.0, 2.2]                                       # each time we cut back, it is closer

    def f(t):
        i = max(k for k, c in enumerate(cuts) if t >= c)
        tt = t - cuts[i]
        dur = (cuts[i + 1] if i + 1 < len(cuts) else D) - cuts[i]
        u = min(1.0, tt / max(0.5, dur))
        def sign(img, t_, o):
            z = 3.2 - 1.9 * u
            s_, fx, fy = sign_c(round(BP.P.scale_at(z, 1.2, 640), 2))
            x, y = BP.P.p(0.62, 1.0, z)
            return put_sprite(img, s_, x + o, y, fx, fy)
        def tk(img, t_, o):
            z = tz[i]
            sd = (-0.75, 0.9, -0.62, 0.7)[i]
            x, y = BP.P.p(sd, 1.0, z)
            return put_tik(img, x + o, y, BP.P.scale_at(z, 3.0, 1550), t_, dark=0.5, eyes=1.0, aura=0.4, sway=False, step=i)
        img = BP.frame(t, cam=(i % 2 * 2 - 1) * 30, extras=[(max(1.4, 3.2 - 1.9 * u), sign), (tz[i], tk)], rain_k=0.5)
        img = torch(img, 540, 1150, 0.6, r=240)
        cut_flash = 0.35 if tt < 0.06 and i > 0 else 0.0
        out = to_img(finish(img, t, VIG_H, push=1.03 + 0.08 * u, cx=560, cy=1000, flash=cut_flash, flash_col=(255, 40, 30)))
        put_phone(out, batt("loop", t, D), 1.2, t, 1.0, y=UI_Y)
        if i >= 1:
            again = text_img(["AGAIN.", "AGAIN.", "AGAIN."][min(2, i - 1)] if i < 3 else "1.2 KM. ALWAYS.", font(LORA, 72, "Bold"),
                             fill=(255, 200, 170, 255), glow=(200, 30, 20, 230), pad=16)
            out.alpha_composite(with_alpha(again, ss(tt, 0, 0.2) * (1 - ss(tt, 1.0, 1.3))), (int(W / 2 - again.width / 2), 360))
        return to_arr(out)
    return f


def make_mistake(D, caps):
    BP = bamboo(47)
    t2, t3 = caps[1][1], caps[2][1]

    def f(t):
        sh = ss(t, 0.6, 1.0) * (1 - ss(t, 3.2, 3.8))
        def boy(img, tt, o):
            z = 0.8
            h, fx, fy, _ = paolo(0.0, back=False, scale=BP.P.scale_at(z, 0.95, 815), shout=sh, phone=True)
            x, y = BP.P.p(0.0, 1.0, z)
            return put_sprite(img, h, x + o, y, fx, fy)
        ex = [(0.8, boy)]
        if t > t3 - 0.2:
            u = ss(t, t3 - 0.2, D - 0.3)
            z = 8.0 - 5.6 * (int(u * 7) / 7)                       # stop-motion: it gallops closer in jumps
            def tk(img, tt, o, z=z):
                x, y = BP.P.p(-0.15, 1.0, z)
                return put_tik(img, x + o, y, BP.P.scale_at(z, 3.0, 1550), tt, dark=0.4, eyes=1.0, aura=0.6, step=int(tt * 9), reach=0.6, sway=False)
            ex.append((z, tk))
        img = BP.frame(t, cam=0, extras=ex, rain_k=0.4)
        lk = 1.0 - 0.3 * ss(t, t2, t2 + 0.3)
        shake = 0.6 * (t2 - 0.05 < t < t2 + 0.6) + 0.35 * (t > t3)
        push = 1.08 + 0.15 * ss(t, 0, 3.0) - 0.1 * ss(t, t3 - 0.4, t3 + 0.4)
        out = to_img(finish(img, t, VIG_H, push=push, cx=540, cy=900 + 120 * ss(t, 0, 3.0) * (1 - ss(t, t3 - 0.4, t3 + 0.4)), shake=shake) * lk)
        put_phone(out, batt("mistake", t, D), 1.2, t, 1.0, y=UI_Y)
        return to_arr(out)
    return f


def make_cliff(D, caps):
    BR = bridge(); UB = underbridge()
    t2, t3 = caps[1][1], caps[2][1]
    jt = D - 1.1

    def f(t):
        if t < t2 - 0.1:
            # side view: Paolo dives under the bridge
            u = ss(t, 0.0, 2.4)
            def boy(img, tt, o):
                if u < 0.85:
                    h, fx, fy, _ = paolo((tt * 2.2) % 1, run=1.0, scale=0.34, phone=False)
                    x = 120 + 300 * u; y = 1060 + 120 * ss(tt, 1.6, 2.4)
                    return put_sprite(img, h, x + o, y, fx, fy)
                c, fx, fy = paolo_crouch(0.28)
                return put_sprite(img, c, 420 + o, 1210, fx, fy)
            img = BR.frame(t, cam=-20 + 30 * t / D, extras=[(1, boy)])
            return finish(img, t, VIG_H, push=1.05 + 0.1 * u, cx=480, cy=1050)
        if t >= jt:
            img = Image.new("RGBA", (W, H), (6, 1, 2, 255))
            img = put_tface(img, 540, 860 + 140 * ss(t, jt, jt + 0.15), 1.15, t, eyes=1.0, grin=1.0, inv=True, aura=0.9)
            fl = 0.85 if t < jt + 0.08 else 0.0
            return finish(img, t, VIG_H, push=1.0 + 0.4 * ss(t, jt, jt + 0.18), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
        tt = t - t2
        # under the bridge: the hooves walk over the planks, then stop right above him
        hx = 900 - 420 * ss(tt, 0, 2.4)
        step = int(tt / 0.45) % 2
        hooves = [(hx - 70 + 20 * step, 46), (hx + 70 - 20 * step, 46)]
        stopped = tt > 2.4
        def boy(img, t_):
            c, fx, fy = paolo_crouch(0.9, look=0.3)
            return put_sprite(img, c, 280, 1560, fx, fy)
        img = UB.frame(t, hooves=hooves, dust=0.4 + 0.6 * stopped, extras=[(1, boy)], light=1.0 - 0.3 * stopped)
        if t > t3 + 1.0:                                       # long pale fingers curl over the edge of the planks
            k = ss(t, t3 + 1.0, jt - 0.1)
            d = ImageDraw.Draw(img)
            for j in range(4):
                x = 600 + j * 34
                d.line([(x, 420), (x + 6, 420 + 120 * k), (x - 10, 460 + 150 * k)], fill=BONE + (255,), width=12, joint="curve")
        push = 1.05 + 0.15 * ss(tt, 2.4, 5.0)
        return finish(img, t, VIG_H, push=push, cx=520, cy=760, shake=0.25 * (not stopped) * (step == 0))
    return f


# ============================================================ PART 2
def make_recap(D, caps):
    UB = underbridge()
    hdr = series_header("PHILIPPINES", "PART 2")

    def f(t):
        hx = 520
        def boy(img, t_):
            c, fx, fy = paolo_crouch(0.9, look=0.3)
            return put_sprite(img, c, 280, 1560, fx, fy)
        img = UB.frame(t, hooves=[(hx - 60, 46), (hx + 60, 46)], dust=0.6, extras=[(1, boy)], light=0.8)
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.06 * t / D, cx=520, cy=900))
        put_header(out, hdr, t)
        put_phone(out, batt("recap", t, D), 1.2, t, ss(t, 2.0, 2.4), y=1150)
        return to_arr(out)
    return f


def make_under(D, caps):
    UB = underbridge()
    t2 = caps[1][1]
    jt = D - 0.9

    def f(t):
        def boy(img, t_):
            c, fx, fy = paolo_crouch(0.9, look=0.4)
            return put_sprite(img, c, 280, 1560, fx, fy)
        if t >= jt:
            img = Image.new("RGBA", (W, H), (6, 1, 2, 255))
            img = put_tface(img, 540, 820, 1.3, t, eyes=1.0, grin=1.0, inv=True, aura=0.9)
            fl = 0.85 if t < jt + 0.08 else 0.0
            return finish(img, t, VIG_H, push=1.0 + 0.5 * ss(t, jt, jt + 0.2), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
        def face(img, t_):
            if t_ < t2:
                return img
            k = ss(t_, t2, jt - 0.4)
            return put_tface(img, 760, -380 + 900 * k, 0.75, t_, eyes=ss(t_, t2 + 1.0, t2 + 1.6), grin=ss(t_, t2 + 2.2, jt - 0.4), inv=True, aura=0.6)
        img = UB.frame(t, hooves=[(460, 46), (580, 46)], dust=1.0 * (1 - ss(t, t2, t2 + 1.0)), extras=[(2, face), (1, boy)], light=0.75)
        push = 1.04 + 0.12 * ss(t, t2, jt)
        return finish(img, t, VIG_H, push=push, cx=620, cy=800)
    return f


def make_chase(D, caps):
    BP = bamboo(47)
    t2, t3 = caps[1][1], caps[2][1]
    dead = caps[0][1] + 1.6

    def f(t):
        if t < t2 - 0.1:
            # running: shaky camera rushing down the path, torch beam swinging, then the phone dies
            def boy(img, tt, o):
                h, fx, fy, _ = paolo((tt * 2.4) % 1, run=1.0, back=True, scale=BP.P.scale_at(0.9, 0.95, 815), phone=False)
                x, y = BP.P.p(0.05, 1.0, 0.9)
                return put_sprite(img, h, x + o, y + 12 * math.sin(tt * 30), fx, fy)
            img = BP.frame(t, cam=40 * math.sin(t * 7), extras=[(0.9, boy)], rain_k=0.6)
            lt = 1.0 if t < dead else 0.45
            if t < dead:
                img = torch(img, 540 + 200 * math.sin(t * 9), 1100, 0.9, r=300)
            out = to_img(finish(img, t, VIG_H, push=1.1 + 0.15 * ((t * 1.5) % 1), cx=540, cy=1000, shake=0.6) * lt)
            put_phone(out, max(0, batt("chase", t, D) * (t < dead)), None if t > dead else 1.2, t, 1.0, y=UI_Y)
            return to_arr(out)
        # it is squatting in the middle of the path: knees above its head
        tt = t - t2
        def tk(img, t_, o):
            x, y = BP.P.p(0.0, 1.0, 1.5)
            return put_tik(img, x + o, y, BP.P.scale_at(1.5, 3.0, 1550), t_, pose="squat", eyes=1.0, aura=0.7, grin=ss(t_, t3, t3 + 1.0), sway=False)
        img = BP.frame(t, cam=0, extras=[(1.5, tk)], rain_k=0.5, light=0.6)
        hit = tt < 0.12
        push = 1.0 + 0.35 * ss(tt, 0, 0.2) - 0.25 * ss(tt, 0.2, 1.4) + 0.12 * ss(t, t3, D)
        out = to_img(finish(img, t, VIG_H, push=push, cx=540, cy=900, shake=0.9 if hit else 0.0, flash=0.6 if hit else 0.0, flash_col=(255, 30, 20)))
        put_phone(out, 0, None, t, 0.8, y=UI_Y)
        return to_arr(out)
    return f


def make_escape(D, caps):
    BP = bamboo(21); HS = house(0.0)
    t2, t3, t4 = caps[1][1], caps[2][1], caps[3][1]
    tag = pill("SHIRT INSIDE OUT", font(INTER_SB, 48), outline=(255, 210, 120, 255), fill=(110, 60, 10, 235), color=(255, 240, 210, 255), h=96)
    tabi = text_img("\"Tabi po...\"", font(LORA, 84, "Bold"), fill=(255, 226, 190, 255), glow=(200, 40, 20, 220), pad=18)

    def f(t):
        if t < t4 - 0.1:
            # mid shot: Paolo on the path, the creature looming behind; the shirt flip; it backs away into the bamboo
            flip = ss(t, t2 - 0.1, t2 + 0.35)
            inside = flip > 0.5
            sq = abs(math.cos(flip * math.pi))                          # the flip squash
            back_k = ss(t, t3 + 0.6, t4 - 0.3)
            def tk(img, tt, o):
                z = 2.2 + 4.5 * back_k
                x, y = BP.P.p(-0.42, 1.0, z)
                return put_tik(img, x + o, y, BP.P.scale_at(z, 3.0, 1550), tt, eyes=1.0 - 0.6 * back_k, aura=0.5, dark=0.3, alpha=1 - 0.8 * back_k, sway=False)
            def boy(img, tt, o):
                h, fx, fy, _ = paolo(0.0, scale=1.2, inside=inside, phone=False)
                if sq < 0.999:
                    h = h.resize((max(1, int(h.width * max(0.05, sq))), h.height), Image.LANCZOS); fx = h.width / 2
                return put_sprite(img, h, 560 + o, 1880, fx, fy)
            img = BP.frame(t, cam=0, extras=[(2.2 + 4.5 * back_k, tk), (0.5, boy)], rain_k=0.6 * (1 - ss(t, t3 + 1.0, t4)), light=0.8 + 0.2 * back_k)
            out = to_img(finish(img, t, VIG_H, push=1.03 + 0.04 * t / D, cx=540, cy=1000, flash=0.4 * (1 - ss(t, t2 + 0.15, t2 + 0.4)) * (t > t2), flash_col=(255, 220, 150)))
            if t > t2 + 0.2:
                out.alpha_composite(with_alpha(tag, ss(t, t2 + 0.2, t2 + 0.5)), (int(W / 2 - tag.width / 2), 230))
            if t > t3:
                out.alpha_composite(with_alpha(tabi, ss(t, t3, t3 + 0.4) * (1 - ss(t, t4 - 0.6, t4 - 0.2))), (int(W / 2 - tabi.width / 2), 360))
            return to_arr(out)
        # Lola's house: lights + the parol star, the rain has stopped
        tt = t - t4
        def boy(img, t_, o):
            h, fx, fy, _ = paolo((t_ * 1.2) % 1, back=True, scale=0.5, inside=True, phone=False)
            return put_sprite(img, h, 540 + o, 1700 - 150 * ss(tt, 0, 3.5), fx, fy)
        img = HS.frame(t, cam=-20 + 20 * tt / 4, extras=[(1, boy)], lights=ss(tt, 0, 0.6), star=ss(tt, 0.3, 1.0))
        return finish(img, t, VIG_H, push=1.08 - 0.05 * ss(tt, 0, 3.5), cx=540, cy=1000, flash=0.25 * (1 - ss(tt, 0, 0.3)), flash_col=(255, 200, 150))
    return f


def make_twist(D, caps):
    HD = house(1.0); WN = window()
    t2 = caps[1][1]
    jt = D - 1.0

    def f(t):
        if t < t2 - 0.1:
            img = HD.frame(t, cam=10 * t, lights=0, star=0)
            return finish(img, t, VIG, push=1.05 + 0.25 * ss(t, 0.5, t2), cx=540, cy=1400)
        if t >= jt:
            def face(img, t_):
                return put_tface(img, 540, 700, 1.0, t_, eyes=1.0, grin=1.0, aura=0.9)
            img = WN.frame(t, face=face)
            fl = 0.85 if t < jt + 0.08 else 0.0
            return finish(img, t, VIG_H, push=1.0 + 0.35 * ss(t, jt, jt + 0.18), cx=540, cy=760, shake=1.0, flash=fl, flash_col=(255, 30, 20))
        img = WN.frame(t)
        u = ss(t, t2, jt)
        return finish(img, t, VIG, push=1.1 + 0.35 * u, cx=540, cy=1250 - 300 * u)
    return f


def make_explain(D, caps):
    B = balete()
    title = text_img("TIKBALANG", font(LORA, 116, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("The horse-headed trickster of the Philippines", font(INTER_SB, 36), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("Tall and bony: head and hooves of a horse", pf, fill=(110, 20, 24, 235), h=80),
             pill("Squats with its knees above its head", pf, fill=(110, 20, 24, 235), h=80),
             pill("Leads travelers in circles", pf, fill=(110, 20, 24, 235), h=80),
             pill("Shirt inside out breaks the trick", pf, fill=(110, 20, 24, 235), h=80),
             pill("Sun shower = a tikbalang wedding", pf, fill=(90, 40, 10, 235), outline=(255, 200, 110, 255), h=80)]
    ts = [caps[1][1], caps[1][1] + 2.0, caps[2][1], caps[2][1] + 2.4, caps[2][1] + 4.2]
    px, py = B.perch

    def f(t):
        def tk(img, tt, o):
            return put_tik(img, 560 + o, 1560, 0.62, tt, pose="squat", eyes=1.0, aura=0.5, sway=False)
        img = B.frame(t, cam=-10 + 20 * t / D, extras=[(1, tk)])
        a = finish(img, t, vig=VIG_H, push=1.05 + 0.05 * t / D, cx=640, cy=1000)
        out = to_img(a * 0.72)
        fw = flag_wave(t, 170)
        out.alpha_composite(fw, (int(W / 2 - fw.width / 2), 60))
        out.alpha_composite(with_alpha(title, ss(t, 0.1, 0.7)), (int(W / 2 - title.width / 2), 190))
        out.alpha_composite(with_alpha(sub, ss(t, 0.5, 1.1)), (int(W / 2 - sub.width / 2), 350))
        chips_at(out, chips, ts, t, 440, 94)
        return to_arr(out)
    return f


def make_outro(D, caps):
    BP = bamboo(33)
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("find your way out?", font(LORA, 88, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Shirt inside out", (140, 70, 20, 235)), ("Ask permission", (60, 40, 40, 235)), ("Hide", (90, 30, 30, 235)), ("RUN", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)

    def f(t):
        z = max(2.0, 7.0 - 1.4 * int(t / 2.0))                       # it gets closer every 2 s (stop-motion)
        def tk(img, tt, o):
            x, y = BP.P.p(0.0, 1.0, z)
            return put_tik(img, x + o, y, BP.P.scale_at(z, 3.0, 1550), tt, eyes=1.0, aura=0.6, tilt=-10, sway=False, dark=0.3)
        img = BP.frame(t, cam=0, extras=[(z, tk)], rain_k=0.3)
        a = finish(img, t, vig=VIG_H, push=1.02, cx=540, cy=1000) * 0.55
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
