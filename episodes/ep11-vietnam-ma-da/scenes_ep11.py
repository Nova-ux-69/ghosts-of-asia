"""Ep11 Vietnam / the Ma Da - scenes (2.1D survival). Each make_<id>(D, caps) returns f(t) -> float RGB (H, W, 3)."""
from art_ep11 import *

C_ = None


def cn():
    return canal()


def on_bridge(img, x, t, phase=None, scale=0.42, back=False, torch=True, beam_k=0.9, down=0.25, run=0.0):
    C = cn()
    ph = (t * 1.4) % 1 if phase is None else phase
    h, fx, fy, tp = bao(ph, run=run, scale=scale, back=back, torch=torch)
    y = C.walk_y(x)
    img.alpha_composite(h, (int(x - fx), int(y - fy)))
    if torch and beam_k > 0 and run < 0.5:
        img = beam(img, x - fx + tp[0], y - fy + tp[1], beam_k, length=520, spread=150, down=down)
    return img


_WC = None


def water_closeup(t, y0=1240, zoom=2.6, cx=600):
    """Black water seen from close above: soft moving swells with red moon glints (computed at 1/4 res)."""
    global _WC
    w4, h4 = W // 4, H // 4
    if _WC is None:
        yy, xx = np.mgrid[0:h4, 0:w4].astype(np.float32)
        _WC = (yy, xx, fog_texture(w4, h4, 61), fog_texture(w4, h4, 62))
    yy, xx, n1, n2 = _WC
    g = yy / h4
    base = np.stack([22 - 12 * g, 5 - 3 * g, 7 - 4 * g], -1)
    v = np.sin(yy * 0.16 + 4 * n1 + t * 1.6 + np.sin(xx * 0.05 + t * 0.6) * 1.5)
    hl = np.clip((v - 0.55) * 2.6, 0, 1) * (0.35 + 0.65 * n2)
    v2 = np.sin(yy * 0.31 - 3 * n2 + t * 2.3 + xx * 0.02)
    hl2 = np.clip((v2 - 0.85) * 6, 0, 1) * np.exp(-((xx - w4 * 0.35) / 50) ** 2)
    a = base + hl[..., None] * np.array([120, 30, 24]) + hl2[..., None] * np.array([255, 120, 80]) * 0.8
    return to_img(a).resize((W, H), Image.BICUBIC)


# ============================================================ PART 1
def make_hook(D, caps):
    C = cn()
    hdr = series_header("VIETNAM", "PART 1")
    cut = caps[1][1] - 0.15

    def f(t):
        if t < cut:
            def wat(img, tt, P):
                # only the viewer sees her: the top of a head and two red eyes, just above the water
                return put_mada(img, 760, 1640, 0.7, tt, eyes=0.9, rise=0.12 + 0.1 * ss(tt, 0, cut), tilt=-8 * ss(tt, 1.5, cut), aura=0.4)
            img = C.frame(t, cam=-20 + 40 * t / cut, extra_water=wat)
            fog(img, t, 0.35, HZ - 140, HZ + 300, speed=14)
            a = finish(img, t, VIG_H, push=1.0 + 0.12 * t / cut, cx=720, cy=1300)
        else:
            tt = t - cut
            img = water_closeup(t, 1500, 2.2, 640)
            # a small pale hand rises out of the black water, fingers reaching up
            u = ss(tt, 0, 0.8)
            bx, by = 560, 1260 - 300 * u
            def hand(d, s):
                d.polygon(P_((bx - 62, 1300), (bx + 62, 1300), (bx + 50, by + 70), (bx - 50, by + 70), s=s), fill=255)
                d.ellipse([(bx - 66) * s, (by - 20) * s, (bx + 66) * s, (by + 110) * s], fill=255)
                for k in range(4):
                    a = -math.pi / 2 + (k - 1.5) * 0.3
                    d.line([(bx * s, (by + 10) * s), ((bx + math.cos(a) * 120) * s, (by + 10 + math.sin(a) * 120) * s)], fill=255, width=int(26 * s))
                d.line([((bx - 50) * s, (by + 50) * s), ((bx - 120) * s, (by - 4) * s)], fill=255, width=int(26 * s))
            hm = shade(hand, (W, H), PALE, 22, rim_strength=1.0)
            hm = Image.fromarray(np.asarray(hm)[:1300].copy(), "RGBA")
            img.alpha_composite(hm)
            d = ImageDraw.Draw(img)
            for k in range(5):
                ph = (t * 1.5 + k * 0.2) % 1
                d.ellipse([bx - 40 + k * 20 - 5, by + 120 + ph * 400 - 8, bx - 40 + k * 20 + 5, by + 120 + ph * 400 + 8], fill=(240, 210, 200, int(220 * (1 - ph))))
            ripple_rings(img, 560, 1300, 220, t, 1.0, n=4, speed=0.9)
            fog(img, t, 0.3, 1400, 1920, speed=30)
            fl = 0.5 if tt < 0.07 else 0.0
            a = finish(img, t, VIG_H, push=1.06 + 0.06 * tt, cx=560, cy=1200, flash=fl, flash_col=(255, 40, 30), shake=0.3 * (1 - ss(tt, 0, 0.5)))
        out = to_img(a)
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_bridge(D, caps):
    C = cn()
    t3 = caps[2][1]

    def f(t):
        x = 90 + 560 * t / D
        def wat(img, tt, P):
            if 3.2 < tt < 7.2:                                   # far out in the canal: a head comes up... and sinks
                r = math.sin(math.pi * (tt - 3.2) / 4.0)
                img = put_mada(img, 940, 1520, 0.32, tt, eyes=r, rise=0.14 * r, aura=0.3)
            return img
        def onb(img, tt, P):
            return on_bridge(img, x, tt, beam_k=0.9 if t < t3 else (0.9 if math.sin(t * 23) > -0.3 else 0.2))
        img = C.frame(t, cam=40 * t / D, extra_water=wat, extra_bridge=onb)
        fog(img, t, 0.3, HZ - 120, HZ + 260, speed=20)
        out = to_img(finish(img, t, VIG_H, push=1.12, cx=x + 120, cy=1200))
        if t > t3 - 0.2:
            ui = torch_ui(12 - 3 * ss(t, t3, D), t, "600 M", ss(t, t3 - 0.2, t3 + 0.3))
            out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
        return to_arr(out)
    return f


def make_rule(D, caps):
    bg = room_bg()
    ba = grandma()
    lampg = gsp(420, (255, 170, 80))
    f1 = font(INTER_SB, 44)
    chips = [pill("1. THE DROWNED NEED A REPLACEMENT", f1, outline=(255, 200, 120, 255), fill=(70, 30, 20, 230), color=(255, 240, 220, 255), h=92),
             pill("2. NEVER TOUCH THE WATER AT NIGHT", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92),
             pill("3. IF IT CALLS FOR HELP... DON'T", f1, outline=(255, 120, 90, 255), fill=(120, 20, 20, 235), color=(255, 240, 220, 255), h=92)]
    ts = [caps[1][1], caps[2][1], caps[2][1] + 1.6]

    def f(t):
        img = bg.copy()
        img.alpha_composite(ba)
        a = to_arr(img)
        fl = 0.8 + 0.2 * math.sin(t * 13) * math.sin(t * 5)
        add_glow(a, lampg, 240, 1060, 1.0 * fl)
        add_glow(a, gsp(70, (255, 40, 30)), 670, 560, 0.8)
        add_glow(a, gsp(70, (255, 40, 30)), 980, 560, 0.8)
        lum = a.mean(2, keepdims=True)                        # faded memory
        a = a * 0.45 + lum * np.array([1.25, 0.85, 0.6]) * 0.55
        a *= 0.92 + 0.08 * math.sin(t * 40)
        img = to_img(a)
        for i, (c, tt) in enumerate(zip(chips, ts)):
            k = ss(t, tt - 0.15, tt + 0.3)
            if k > 0:
                cc = c if c.width <= W - 40 else c.resize((W - 40, int(c.height * (W - 40) / c.width)), Image.LANCZOS)
                img.alpha_composite(with_alpha(cc, k), (int(W / 2 - cc.width / 2), int(250 + i * 120 + 20 * (1 - k))))
        return finish(img, t, vig=VIG_H, push=1.0 + 0.06 * t / D, cx=600, cy=1000)
    return f


def make_water(D, caps):
    C = cn()
    t2, t3 = caps[1][1], caps[2][1]
    sw = swimmer(0.42)

    def f(t):
        x = 400 + 60 * t / D
        def wat(img, tt, P):
            # the long pale shape under the surface, sliding under the bridge toward him
            u = ss(tt, t2 - 1.0, D)
            sx = 1150 - 700 * u
            sy = 1600 + 30 * math.sin(tt * 1.3)
            img.alpha_composite(sw, (int(sx - 60), int(sy - sw.height / 2)))
            if tt > t3:
                k = ss(tt, t3, t3 + 0.6) * 0.7
                eye(img, sx + 70, sy - 26, k, 0.32); eye(img, sx + 70, sy + 26, k, 0.32)
            return img
        def onb(img, tt, P):
            return on_bridge(img, x, tt, phase=(tt * 0.7) % 1, beam_k=0.75 if math.sin(tt * 19) > -0.5 else 0.25)
        img = C.frame(t, cam=0, extra_water=wat, extra_bridge=onb)
        fog(img, t, 0.3, HZ - 100, HZ + 300, speed=12)
        push = 1.08 + 0.18 * ss(t, t3 - 0.2, D)
        cxx = x + 200 * ss(t, t3 - 0.2, D)
        cyy = 1300 + 200 * ss(t, t3 - 0.2, D)
        out = to_img(finish(img, t, VIG_H, push=push, cx=cxx, cy=cyy))
        ui = torch_ui(8, t, "450 M")
        out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
        return to_arr(out)
    return f


def make_voice(D, caps):
    C = cn()
    t1 = caps[1][1]

    def f(t):
        if t < t1 - 0.1:
            img = Image.new("RGBA", (W, H), (8, 2, 3, 255))
            bg = C.frame(t, fg=False, flies=False)
            img.alpha_composite(dof(bg, 9))
            img = to_img(to_arr(img) * 0.6)
            fc = bao_face(0.1, look=1.0)
            img.alpha_composite(fc, (40, 560))
            a = to_arr(img)
            add_glow(a, gsp(560, (255, 225, 180)), 560, 1900, 0.55 * (0.8 + 0.2 * math.sin(t * 25)))      # torch light from below
            return finish(to_img(a), t, VIG_H, push=1.02 + 0.05 * t / t1, cx=540, cy=1100)
        # POV looking down from the walkway: black water, rings, bubbles, a pale face just under the surface
        tt = t - t1
        img = water_closeup(t, 1450, 2.4, 520)
        ff = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ff = put_face(ff, 560, 1150, 0.8, t, eyes=0.6, aura=0.0)
        img.alpha_composite(tint(ff, (0.6, 0.38, 0.36), 0.32, blur=5))
        ripple_rings(img, 560, 1150, 300, t, 1.0, n=4, speed=0.5)
        d = ImageDraw.Draw(img)
        for i in range(7):
            ph = (t * 0.9 + i * 0.29) % 1
            bxp, byp = 520 + 60 * math.sin(i * 2.1), 1180 - 30 * ph
            d.ellipse([bxp - 9 * ph - 3, byp - 9 * ph - 3, bxp + 9 * ph + 3, byp + 9 * ph + 3], outline=(255, 140, 110, int(200 * (1 - ph))), width=3)
        def pole(d_, s):
            d_.line([(-20 * s, 480 * s), ((W + 20) * s, 420 * s)], fill=255, width=int(70 * s))
        img.alpha_composite(texmul(shade(pole, (W, H), BAMBOO, 30, rim_strength=1.1), lambda xx, yy: 1 - 0.4 * ((xx % 260) < 8)))
        a = to_arr(img)
        add_glow(a, gsp(500, (255, 225, 180)), 560, 1150, 0.35 * (0.8 + 0.2 * math.sin(t * 25)))
        out = to_img(finish(to_img(a), t, VIG_H, push=1.0 + 0.12 * ss(tt, 0, D - t1), cx=560, cy=1100))
        ui = torch_ui(5, t, "450 M")
        out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
        return to_arr(out)
    return f


_UND = None


def make_mistake(D, caps):
    t1, t2 = caps[1][1], caps[2][1]
    figs = []
    for x, sc, tl in ((260, 0.5, 6), (560, 0.62, -4), (850, 0.48, 9)):
        body = mada(tl, 0.0)[0]
        g = body.resize((int(body.width * sc), int(body.height * sc)), Image.LANCZOS)
        figs.append((tint(g, (0.62, 0.42, 0.4), 0.85, blur=2), x, sc, tl))

    def arm_shot(t, grab):
        img = water_closeup(t, 1450, 2.4, 520)
        ripple_rings(img, 600, 1180, 220, t, 1.0, n=3, speed=0.8)
        def pole(d_, s):
            d_.line([(-20 * s, 300 * s), ((W + 20) * s, 250 * s)], fill=255, width=int(80 * s))
        img.alpha_composite(texmul(shade(pole, (W, H), BAMBOO, 30, rim_strength=1.1), lambda xx, yy: 1 - 0.4 * ((xx % 260) < 8)))
        # Bao's arm reaching down from the walkway: ochre sleeve top-left, forearm, open hand over the water
        hx, hy = 600, 1130 - 30 * grab
        def sleeve(d, s):
            d.polygon(P_((-60, 120), (200, -40), (360, 330), (140, 470), s=s), fill=255)
        def arm(d, s):
            d.line([(230 * s, 380 * s), (hx * s, hy * s)], fill=255, width=int(118 * s))
            d.ellipse([(hx - 78) * s, (hy - 60) * s, (hx + 78) * s, (hy + 90) * s], fill=255)
            for k in range(4):
                a = math.pi / 2 + 0.5 - k * 0.32 - 0.5 * grab
                d.line([((hx + 10) * s, (hy + 40) * s), ((hx + 10 + math.cos(a) * 120) * s, (hy + 40 + math.sin(a) * 120) * s)], fill=255, width=int(30 * s))
            d.line([((hx - 50) * s, (hy + 10) * s), ((hx - 110) * s, (hy + 90) * s)], fill=255, width=int(32 * s))
        img.alpha_composite(shade(arm, (W, H), SKIN, 40, rim_strength=0.8))
        img.alpha_composite(shade(sleeve, (W, H), SHIRT, 60))
        if grab > 0:
            # a long pale hand bursts up and wraps round his wrist
            gx, gy = 640, 1120
            u = min(1.0, grab)
            def ghand(d, s):
                d.polygon(P_((gx + 40, 2000), (gx + 150, 2000), (gx + 70, gy + 90), (gx - 10, gy + 60), s=s), fill=255)
                d.ellipse([(gx - 70) * s, (gy - 30) * s, (gx + 70) * s, (gy + 90) * s], fill=255)
                for k in range(4):
                    a0 = -0.4 - k * 0.42
                    pts = [(gx - 30, gy + 10 + k * 18)]
                    for j in range(1, 5):
                        aa = a0 - j * 0.55 * u
                        px, py = pts[-1]
                        pts.append((px + math.cos(aa) * 52, py + math.sin(aa) * 52))
                    d.line([(px * s, py * s) for px, py in pts], fill=255, width=int(20 * s), joint="curve")
            gh = shade(ghand, (W, H), PALE, 16, rim_strength=1.1)
            img.alpha_composite(gh)
            d = ImageDraw.Draw(img)
            for k in range(6):
                ph = (t * 1.4 + k * 0.23) % 1
                d.ellipse([600 + k * 18 - 5, 1200 + ph * 300 - 8, 600 + k * 18 + 5, 1200 + ph * 300 + 8], fill=(240, 210, 200, int(220 * (1 - ph))))
        return img

    def f(t):
        if t < t1 - 0.1:
            img = arm_shot(t, 0)
            a = to_arr(img); add_glow(a, gsp(400, (255, 225, 180)), 700, 1200, 0.45)
            out = to_img(finish(to_img(a), t, VIG_H, push=1.02 + 0.06 * t / t1, cx=560, cy=1000))
            ui = torch_ui(4, t, "450 M"); out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
            return to_arr(out)
        if t < t2 - 0.1:
            tt = t - (t1 - 0.1)
            g = ss(tt, 0.0, 0.25)
            img = arm_shot(t, g)
            fl = 0.6 if tt < 0.08 else 0.0
            out = to_img(finish(img, t, VIG_H, push=1.08 + 0.05 * tt, cx=620, cy=1150, flash=fl, flash_col=(255, 255, 255), shake=0.8 * (1 - ss(tt, 0, 0.8))))
            ui = torch_ui(4, t, "450 M"); out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
            return to_arr(out)
        # under the water: the torch sinks, still shining... and lights up the drowned standing on the bottom
        tt = t - (t2 - 0.1)
        y = np.linspace(0, 1, H)[:, None, None]
        a = np.broadcast_to(np.array([40, 8, 10]) * (1 - y) + np.array([6, 1, 2]) * y, (H, W, 3)).astype(np.float32).copy()
        img = to_img(a)
        ty_ = 260 + 900 * ss(tt, 0, D - t2 + 0.1)
        tx_ = 560 + 40 * math.sin(tt * 1.4)
        for g, x, sc, tl in figs:
            light = max(0.0, 1 - abs(ty_ + 500 - 1250) / 900)
            fy = 1950
            gg = with_alpha(g, 0.25 + 0.75 * light)
            img.alpha_composite(gg, (int(x - 380 * sc), int(fy - g.height)))
        for g, x, sc, tl in figs:
            k = ss(ty_, 700, 1100)
            body, e1, e2, _ = mada(tl, 0.0)
            for ex, ey in (e1, e2):
                eye(img, x - 380 * sc + ex * sc, 1950 - g.height + ey * sc, k * 0.9, sc * 0.7)
        # the torch
        ang = 20 * math.sin(tt * 0.9) - 60
        tor = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); td = ImageDraw.Draw(tor)
        td.rounded_rectangle([40, 88, 140, 112], 6, fill=(60, 56, 60, 255)); td.polygon([(140, 82), (166, 74), (166, 126), (140, 118)], fill=(90, 86, 90, 255))
        tor = tor.rotate(ang, resample=Image.BICUBIC)
        img.alpha_composite(tor, (int(tx_ - 100), int(ty_ - 100)))
        a = to_arr(img)
        lm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(lm).polygon([(tx_, ty_), (tx_ - 420, ty_ + 1300), (tx_ + 420, ty_ + 1300)], fill=255)
        lm = np.asarray(lm.filter(ImageFilter.GaussianBlur(40)), np.float32) / 255
        a += lm[..., None] * np.array([150, 120, 90]) * 0.5
        add_glow(a, gsp(120, (255, 235, 200)), tx_ + 40, ty_ + 40, 0.9)
        img = to_img(a)
        bokeh_particles(img, 30, 17, t, color=(255, 170, 140), size=(2, 9), blur=(0, 3), drift=(0, -60))
        out = to_img(finish(img, t, VIG_H, push=1.04 + 0.06 * tt / (D - t2), cx=560, cy=900 + 300 * ss(tt, 0, D - t2)))
        ui = torch_ui(0, t, "450 M", lost=True); out.alpha_composite(ui, (int(W / 2 - ui.width / 2), 170))
        return to_arr(out)
    return f


def hair_over(L, t, x0=600, x1=800, fingers=0.0):
    """Wet black hair clumps sliding over the stern beam into the boat (L px inside), with weed and drips;
    fingers 0..1 = long pale fingers curling over the beam."""
    def fn(img, tt):
        if L <= 2 and fingers <= 0:
            return img
        if L > 2:
            def hm(d, s):
                for k in range(6):
                    xk = x0 + k * (x1 - x0) / 5
                    lk = L * (0.75 + 0.25 * math.sin(k * 1.7 + 1))
                    d.polygon(P_((xk - 30, 1250), (xk + 30, 1250), (xk + 26, 1420), (xk + 14 + 6 * math.sin(k), 1440 + lk), (xk - 4, 1450 + lk), (xk - 26, 1420), s=s), fill=255)
                d.ellipse([(x0 - 40) * s, 1180 * s, (x1 + 40) * s, 1330 * s], fill=255)
            hh = shade(hm, (W, H), (16, 13, 14), 14, rim_strength=1.6)
            img.alpha_composite(hh)
            d = ImageDraw.Draw(img)
            for k in range(4):
                xk = x0 + 20 + k * 55
                pts = [(xk + 9 * math.sin(j + k), 1240 + j * (L + 200) / 9) for j in range(10)]
                d.line(pts, fill=WEED + (255,), width=6)
            for k in range(5):
                ph = (tt * 1.6 + k * 0.31) % 1
                xk = x0 + k * (x1 - x0) / 4
                yk = 1440 + L * 0.9 + ph * 200
                d.ellipse([xk - 6, yk - 9, xk + 6, yk + 9], fill=(240, 200, 190, int(220 * (1 - ph))))
        if fingers > 0:
            def fg(d, s):
                for k in range(4):
                    fx = 470 + k * 34
                    u = fingers
                    d.line([(fx * s, 1405 * s), ((fx + 6) * s, (1405 + 40 * u) * s), ((fx + 2) * s, (1405 + 90 * u) * s)], fill=255, width=int(20 * s), joint="curve")
                d.ellipse([440 * s, 1380 * s, 600 * s, 1430 * s], fill=255)
            img.alpha_composite(shade(fg, (W, H), PALE, 10, rim_strength=1.0))
        return img
    return fn


def make_cliff(D, caps):
    B = boat_inside()
    t1, t2 = caps[1][1], caps[2][1]
    jt = caps[2][2] + 0.15

    def f(t):
        if t >= jt:
            img = Image.new("RGBA", (W, H), (8, 2, 3, 255))
            img = put_face(img, 540, 920, 1.5, t, eyes=1.0, mouth=0.5, tilt=-10, aura=0.8)
            fl = 0.85 if t < jt + 0.08 else 0.0
            a = finish(img, t, vig=VIG_H, push=1.0 + 0.6 * ss(t, jt, jt + 0.25), cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
            if t > D - 0.45:
                a *= 0.0
            return a
        beat = int(max(0, t - (t1 - 0.2)) / 0.6) if t > t1 - 0.2 else -1
        L = 0 if beat < 0 else min(300, 40 + beat * 50)
        rise = ss(t, t2 - 0.2, jt - 0.3)
        def behind(img, tt):
            if rise > 0:
                img = put_face(img, 760, 1460 - 160 * rise, 0.36, tt, eyes=rise, aura=0.4)
            return img
        def front(img, tt):
            if t < 1.4:
                h, fx, fy = bao_crouch(1.6, 0)
                img.alpha_composite(h, (int(330 - fx - 300 * (1 - ss(tt, 0, 1.4))), int(1880 - fy)))
            else:
                h, fx, fy = bao_crouch(1.6, look=ss(tt, t1, t1 + 0.6))
                img.alpha_composite(h, (int(330 - fx), int(1880 - fy)))
            return img
        img = B.frame(t, behind_beam=behind, front=front, hair=hair_over(L, t, fingers=ss(t, t2 - 0.6, t2 + 0.4)))
        fog(img, t, 0.2, 1300, 1700, col=(120, 30, 30))
        push = 1.04 + 0.04 * math.sin(t * 1.3) + 0.2 * ss(t, t2, jt)
        cxx = 540 + 90 * ss(t, t1, jt); cyy = 1150 + 150 * ss(t, t1, jt)
        return finish(img, t, vig=VIG_H, push=push, cx=cxx, cy=cyy, shake=0.25 * (1 - ss(t, 0, 1.4)))
    return f


# ============================================================ PART 2
def make_recap(D, caps):
    B = boat_inside()
    hdr = series_header("VIETNAM", "PART 2")

    def f(t):
        def behind(img, tt):
            return put_face(img, 760, 1320 - 40 * ss(tt, 0, D), 0.36, tt, eyes=1.0, aura=0.4)
        def front(img, tt):
            h, fx, fy = bao_crouch(1.6, look=1.0)
            img.alpha_composite(h, (int(330 - fx), int(1880 - fy)))
            return img
        img = B.frame(t, behind_beam=behind, front=front, hair=hair_over(300, t, fingers=1.0))
        fog(img, t, 0.2, 1300, 1700, col=(120, 30, 30))
        out = to_img(finish(img, t, vig=VIG_H, push=1.04 + 0.06 * t / D, cx=560, cy=1150))
        put_header(out, hdr, t)
        return to_arr(out)
    return f


def make_boat(D, caps):
    B = boat_inside()
    t1 = caps[1][1]
    hit = caps[1][2] + 0.15

    def f(t):
        if t < t1 - 0.1:
            # the boat tips; cold black water spreads across the planks toward him
            rotv = 9 * math.sin(t * 2.2) * math.exp(-t * 0.25) + (6 * (1 - ss(t, 0, 0.3)))
            def behind(img, tt):
                return put_mada(img, 700, 1440, 0.5, tt, eyes=1.0, rise=0.55, reach=0.8, rings=False, aura=0.5)
            def front(img, tt):
                h, fx, fy = bao_crouch(1.6, look=1.0)
                img.alpha_composite(h, (int(300 - fx), int(1880 - fy)))
                return img
            img = B.frame(t, behind_beam=behind, front=front, water_floor=ss(t, 0.3, t1), hair=None)
            return finish(img, t, vig=VIG_H, push=1.1, cx=520, cy=1300, rotate=rotv, shake=0.4 * (1 - ss(t, 0, 0.6)))
        tt = t - (t1 - 0.1)
        img = Image.new("RGBA", (W, H), (6, 2, 3, 255))
        bg = B.frame(t, outside=True)
        img.alpha_composite(dof(bg, 10))
        img = to_img(to_arr(img) * 0.45)
        k = ss(tt, 0.3, 2.0)
        if k > 0:
            img = put_face(img, 820, 760 + 40 * (1 - k), 0.9, t, eyes=k, aura=0.5 * k, alpha=k, tilt=-14)
        fc = bao_face(0.4, look=0.0, wet=True)
        img.alpha_composite(fc, (-200, 620))
        fl = 0.85 if hit <= t < hit + 0.08 else 0.0
        return finish(img, t, VIG_H, push=1.02 + 0.06 * tt + (0.3 * ss(t, hit, hit + 0.2) if t > hit else 0), cx=640, cy=900,
                      flash=fl, flash_col=(255, 30, 20), shake=(1.0 * (1 - ss(t, hit, hit + 0.7)) if t > hit else 0))
    return f


def make_eyes(D, caps):
    C = cn()
    bw, (ex, ey), wl = boat_bow()
    t1, t2 = caps[1][1], caps[2][1]

    def f(t):
        bx, by = 360, 1660 - wl                      # boat sprite position (waterline at y=1500), bow eye at ~(535, 1410)
        def mid(img, tt, P):
            img.alpha_composite(bw, (bx, by))
            g = 0.5 + 0.5 * ss(tt, 0.2, 1.2)
            img = glow_on(img, gsp(170, (255, 230, 190)), bx + ex, by + ey, 0.6 * g * (0.85 + 0.15 * math.sin(tt * 7)))
            # she reaches for the boat... stops at the painted eye... and backs off in jerky steps, sinking
            if tt < t1:
                x = 120 + 140 * ss(tt, 0, t1); rise = 0.6; reach = 0.8
            else:
                beat = int((tt - t1) / 0.5)
                x = 260 - 60 * beat; rise = max(0.08, 0.6 - 0.09 * beat); reach = 0.2
            img = put_mada(img, x, 1790, 0.62, tt, eyes=1.0, rise=rise, reach=reach, aura=0.5)
            if tt > t2 - 0.1:                              # Bao leaps from the boat to the bank and runs
                u = ss(tt, t2 - 0.1, t2 + 0.9)
                h, fx, fy, _ = bao((tt * 1.9) % 1, run=1.0, scale=0.5, torch=False)
                jx = 720 + 300 * u; jy = 1460 - 260 * math.sin(math.pi * min(1, u * 1.2)) + 40 * u
                img.alpha_composite(h, (int(jx - fx), int(jy - fy)))
            return img
        img = C.frame(t, bridge=False, extra_mid=mid)
        fog(img, t, 0.3, HZ - 80, HZ + 400, speed=16)
        push = 1.04 + 0.06 * ss(t, 0, t1) * (1 - ss(t, t2 - 0.3, t2 + 0.3))
        cxx = 420 + 360 * ss(t, t2 - 0.3, t2 + 0.6)
        return finish(img, t, VIG_H, push=push, cx=cxx, cy=1560 - 200 * ss(t, t2 - 0.3, t2 + 0.6))
    return f


def path_strip():
    """Muddy canal-bank path (tileable, period 600) with grass tufts."""
    w = W + 1200
    m = Image.new("RGBA", (w, 560), (0, 0, 0, 0)); d = ImageDraw.Draw(m)
    d.rectangle([0, 60, w, 560], fill=(40, 16, 12, 255))
    rng = np.random.default_rng(12)
    for rep in range(w // 600 + 1):
        for _ in range(26):
            x = rep * 600 + rng.uniform(0, 600); hg = rng.uniform(40, 140)
            d.polygon([(x - 6, 70), (x + 6, 70), (x + rng.uniform(-30, 30), 70 - hg)], fill=(26, 10, 8, 255))
        for _ in range(3):
            x = rep * 600 + rng.uniform(0, 600); y = rng.uniform(200, 460)
            d.ellipse([x - 70, y - 12, x + 70, y + 12], fill=(90, 26, 22, 255))
    return texmul(m, lambda xx, yy: 0.8 + 0.2 * np.sin(xx / 13 + yy / 7) ** 2)


_PS = None


def make_shrine(D, caps):
    global _PS
    C = cn()
    if _PS is None:
        _PS = path_strip()
    PS = _PS
    sh, (ix, iy) = shrine()
    t1, t2 = caps[1][1], caps[2][1]
    hk = 0.35                                          # false scare: a night heron bursts out of the nipa

    def f(t):
        if t < t1 - 0.1:
            cam = 420 * t
            def front(img, tt, P):
                img.alpha_composite(PS, (-(int(cam) % 600) - 100, 1400))
                d = ImageDraw.Draw(img)
                for k in range(8):                            # wet footprints behind him (on the path)
                    fx_ = (k * 150 - cam) % 1200 - 60
                    if fx_ < 500:
                        d.ellipse([fx_ - 22, 1700 + (k % 2) * 40, fx_ + 22, 1712 + (k % 2) * 40], fill=(120, 40, 34, 255))
                h, fx, fy, _ = bao((tt * 1.9) % 1, run=1.0, scale=0.85, torch=False)
                img.alpha_composite(h, (int(640 - fx), int(1720 - fy + 6 * abs(math.sin(tt * 11)))))
                beat = int(tt / 0.6)
                img = put_mada(img, 60 + beat * 55 % 220, 1760, 0.5, tt, eyes=1.0, rise=1.0, rings=False, aura=0.6)
                if hk <= tt < hk + 1.3:
                    u = ss(tt, hk, hk + 1.3)
                    hr = heron(math.sin(tt * 26))
                    hr = hr.resize((int(hr.width * (1.6 + 1.6 * u)), int(hr.height * (1.6 + 1.6 * u))), Image.LANCZOS)
                    img.alpha_composite(hr, (int(-200 + 900 * u), int(900 - 500 * u)))
                return img
            img = C.frame(t, cam=cam * 0.1, bridge=False, extra_front=front, fg=False)
            fog(img, t, 0.3, HZ - 100, HZ + 300, speed=70)
            sh_ = 0.8 * (1 - ss(t, hk, hk + 0.6)) if t > hk else 0
            return finish(img, t, VIG_H, push=1.04 + 0.05 * ss(t, hk, hk + 0.15), cx=540, cy=1250, shake=0.15 + sh_)
        # the little shrine: he lights the incense; the footsteps stop; the sky turns grey
        tt = t - (t1 - 0.1)
        dawn = ss(t, t2, D)
        night = to_arr(C.frame(t, bridge=False, fg=False, flies=dawn < 0.5, lights=1 - dawn))
        y = np.linspace(0, 1, H)[:, None, None]
        dsky = np.broadcast_to(np.array([110, 92, 100]) * (1 - y) + np.array([200, 150, 140]) * y, (H, W, 3))
        img = to_img(night * (1 - 0.7 * dawn) + dsky * 0.7 * dawn)
        S2 = sh.resize((int(sh.width * 1.35), int(sh.height * 1.35)), Image.LANCZOS)
        sx, sy = 120, 1880 - S2.height
        img.alpha_composite(S2, (sx, sy))
        lit = ss(t, t1 + 1.2, t1 + 1.8)
        d = ImageDraw.Draw(img)
        bxi, byi = sx + ix * 1.35, sy + iy * 1.35
        for k in range(3):
            x0 = bxi - 30 + k * 30
            d.line([(x0, byi + 20), (x0 + 6 * (k - 1), byi - 90)], fill=(170, 60, 40, 255), width=5)
            if lit > 0:
                d.ellipse([x0 + 6 * (k - 1) - 7, byi - 97, x0 + 6 * (k - 1) + 7, byi - 83], fill=(255, 120, 60, int(255 * lit)))
        if lit > 0:
            sm = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sm)
            for k in range(3):
                pts = [(bxi - 30 + k * 30 + 26 * math.sin(j * 0.6 + t * 1.5 + k), byi - 100 - j * 30) for j in range(14)]
                sd.line(pts, fill=(220, 200, 190, int(110 * lit)), width=8, joint="curve")
            img.alpha_composite(sm.filter(ImageFilter.GaussianBlur(5)))
        # Bao (back view) at the shrine, the lighter flame in his hand
        h, fx, fy, _ = bao(0.0, 0, back=True, scale=1.0, torch=False)
        img.alpha_composite(h, (int(800 - fx), int(1960 - fy)))
        if t1 + 0.4 < t < t1 + 2.2:
            img = glow_on(img, gsp(90, (255, 200, 120)), bxi + 40, byi - 80, 0.9 * (0.8 + 0.2 * math.sin(t * 30)))
        if lit > 0:
            img = glow_on(img, gsp(160, (255, 110, 60)), bxi, byi - 90, 0.6 * lit)
        # the Ma Da far back on the path - fades away once the incense burns
        k = 1 - ss(t, t2 - 0.4, t2 + 1.0)
        if k > 0:
            gh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gh = put_mada(gh, 930, 1480, 0.32, t, eyes=1.0, rise=1.0, rings=False, aura=0.4)
            img.alpha_composite(with_alpha(gh, k))
        fog(img, t, 0.35, 1200, 1900, speed=20, col=(200, 120, 110) if dawn > 0.5 else (140, 40, 40))
        return finish(img, t, VIG if dawn > 0.5 else VIG_H, push=1.02 + 0.05 * tt / (D - t1), cx=540, cy=1200)
    return f


def make_twist(D, caps):
    t1, t2 = caps[1][1], caps[2][1]
    jt = D - 1.0
    bg = home_bg()
    bs = basin_sprite()

    def f(t):
        if t < t1 - 0.1:
            img = bg.copy()
            img.alpha_composite(bs, (250, 1180))
            h, fx, fy, _ = bao(0.0, 0, back=True, scale=1.5, torch=False)
            img.alpha_composite(h, (int(560 - fx), int(2250 - fy)))
            d = ImageDraw.Draw(img)
            for k in range(8):                                   # splashes
                ph = (t * 1.7 + k * 0.17) % 1
                x = 470 + k * 30; y = 1240 - 120 * math.sin(math.pi * ph)
                d.ellipse([x - 6, y - 9, x + 6, y + 9], fill=(230, 220, 220, int(200 * (1 - ph))))
            a = to_arr(img); add_glow(a, gsp(500, (255, 200, 170)), 790, 520, 0.5)
            return finish(to_img(a), t, VIG, push=1.02 + 0.06 * t / t1, cx=560, cy=1000)
        if t < t2 - 0.1:
            # his wrist: a ring of wet river weed is tied around it
            tt = t - (t1 - 0.1)
            img = to_img(to_arr(dof(bg, 12)) * 0.6)
            def arm(d, s):
                d.line([(-40 * s, 1080 * s), (720 * s, 960 * s)], fill=255, width=int(150 * s))
                d.ellipse([660 * s, 880 * s, 900 * s, 1060 * s], fill=255)
                for k in range(4):
                    d.line([(860 * s, (900 + k * 40) * s), (1010 * s, (890 + k * 46) * s)], fill=255, width=int(34 * s))
            img.alpha_composite(shade(arm, (W, H), SKIN, 60, rim=(255, 170, 130)))
            d = ImageDraw.Draw(img)
            wx = 520
            for j in range(3):
                pts = [(wx - 6 + 14 * j + 10 * math.sin(i * 1.3 + j), 900 + i * 18) for i in range(11)]
                d.line(pts, fill=WEED + (255,), width=16, joint="curve")
            for k in range(7):
                px, py = wx - 10 + k * 6, 1060 + (k % 3) * 18
                d.line([(px, 1040), (px - 10 + 4 * k, 1100 + 26 * (k % 3) + 10 * math.sin(t * 2 + k))], fill=(48, 70, 36, 255), width=8)
            for k in range(4):
                ph = (t * 1.2 + k * 0.27) % 1
                d.ellipse([wx + k * 20 - 6, 1120 + ph * 260 - 9, wx + k * 20 + 6, 1120 + ph * 260 + 9], fill=(230, 210, 200, int(220 * (1 - ph))))
            return finish(img, t, VIG_H, push=1.05 + 0.12 * ss(tt, 0, t2 - t1), cx=540, cy=1000)
        if t < jt:
            # looking down into the basin: his reflection... and someone behind him in the water
            tt = t - (t2 - 0.1)
            img = Image.new("RGBA", (W, H), (30, 8, 8, 255))
            d = ImageDraw.Draw(img)
            d.ellipse([-120, 260, 1200, 1780], fill=(196, 28, 30, 255))
            d.ellipse([-40, 330, 1120, 1700], fill=(20, 6, 8, 255))
            inner = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            fc = bao_face(0.2, look=0.0, wet=True)
            fc = fc.resize((int(fc.width * 0.7), int(fc.height * 0.7)), Image.LANCZOS)
            inner.alpha_composite(tint(fc, (0.75, 0.6, 0.55), 0.85), (200, 520))
            k = ss(tt, 1.2, jt - t2)
            if k > 0:
                inner = put_face(inner, 760, 820, 0.55, t, eyes=k, alpha=k * 0.9, aura=0.3 * k)
            arr = np.asarray(inner, np.float32)
            off = (6 * np.sin(np.arange(H) * 0.05 + t * 3)).astype(int)
            arr = arr[np.arange(H)[:, None], np.clip(np.arange(W)[None, :] + off[:, None], 0, W - 1)]
            m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([-40, 330, 1120, 1700], fill=255)
            arr[..., 3] *= np.asarray(m, np.float32) / 255
            img.alpha_composite(Image.fromarray(arr.astype(np.uint8), "RGBA"))
            ripple_rings(img, 540, 1000, 420, t, 0.6, n=3, speed=0.4, col=(255, 160, 140))
            return finish(img, t, VIG_H, push=1.05 + 0.15 * ss(tt, 0, jt - t2), cx=600, cy=900)
        img = Image.new("RGBA", (W, H), (8, 2, 3, 255))
        img = put_face(img, 540, 900, 1.5, t, eyes=1.0, mouth=0.6, tilt=8, aura=0.8)
        fl = 0.85 if t < jt + 0.08 else 0.0
        return finish(img, t, VIG_H, push=1.0 + 0.5 * ss(t, jt, jt + 0.2), cx=540, cy=900, shake=1.0, flash=fl, flash_col=(255, 30, 20))
    return f


def make_explain(D, caps):
    C = cn()
    title = text_img("THE MA DA", font(LORA, 116, "Bold"), fill=(255, 225, 200, 255), glow=(200, 30, 20, 230), pad=20)
    sub = text_img("Vietnam's water ghost of the drowned", font(INTER_SB, 38), fill=(250, 240, 225, 255), pad=10)
    pf = font(INTER_SB, 40)
    chips = [pill("The soul of someone who drowned", pf, fill=(110, 20, 24, 235), h=80),
             pill("River weed for hair, ice-cold hands", pf, fill=(110, 20, 24, 235), h=80),
             pill("Reborn only if someone takes its place", pf, fill=(110, 20, 24, 235), h=80),
             pill("So it pulls swimmers down", pf, fill=(110, 20, 24, 235), h=80)]
    ts = [caps[1][1], caps[1][1] + 1.8, caps[2][1], caps[2][1] + 2.6]

    def f(t):
        def wat(img, tt, P):
            return put_mada(img, 720, 1620, 0.62, tt, eyes=1.0, rise=0.75, aura=0.5)
        img = C.frame(t, cam=-20 + 30 * t / D, extra_water=wat)
        fog(img, t, 0.35, HZ - 100, HZ + 500)
        a = finish(img, t, vig=VIG_H, push=1.0 + 0.05 * t / D, cx=600, cy=1200)
        out = to_img(a * 0.8)
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
    C = cn()
    q = text_img("Would YOU", font(LORA, 100, "Bold"), fill=(250, 240, 225, 255), pad=20)
    q2 = text_img("have reached in?", font(LORA, 96, "Bold"), fill=(255, 120, 90, 255), glow=(200, 30, 20, 220), pad=20)
    pf = font(INTER_SB, 44)
    opts = [("Reach in", (120, 25, 25, 235)), ("Walk away", (60, 40, 40, 235)), ("Call Grandma", (140, 70, 20, 235)), ("RUN!", (150, 30, 30, 235))]
    chips = [pill(n, pf, fill=c, h=90) for n, c in opts]
    cm = text_img("Which country next? Comment below!", font(INTER_SB, 44), fill=(255, 214, 120, 255), pad=12)
    fol = text_img("Follow for more  GHOSTS OF ASIA", font(INTER_M, 36), fill=(230, 220, 215, 255), pad=10)

    def f(t):
        def wat(img, tt, P):
            return put_mada(img, 820, 1540, 0.36, tt, eyes=1.0, rise=0.35, aura=0.4)
        img = C.frame(t, extra_water=wat)
        fog(img, t, 0.4, HZ - 200, HZ + 600)
        a = finish(img, t, vig=VIG_H, push=1.02, cx=600, cy=1200) * 0.55
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
