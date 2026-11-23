"""Ep06 China / Jiangshi sound: river + mountain wind bed, guzheng-style pentatonic plucks (Karplus-Strong),
a Taoist hand bell, a temple gong for stings, heavy two-footed hops on wooden boards, paper flutter, held-breath
heartbeat with a muffled low-pass, dawn birds."""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt
PART = sys.argv[1]; SR = 24000
T = json.load(open(f"{PART}/timing.json"))
st = {}; acc = 0
for s in T: st[s["id"]] = acc; acc += s["dur"]
TOT = acc; N = int(TOT * SR) + SR
rng = np.random.default_rng(61 if PART == "p1" else 62)
L = np.zeros(N); R = np.zeros(N); tt = np.arange(N) / SR
C = {s["id"]: s["caps"] for s in T}; DUR = {s["id"]: s["dur"] for s in T}
def cap(sid, i, j=1): return st[sid] + C[sid][i][j]
def add(sig, t0, pan=0.0, g=1.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    sig = sig[:N - i]
    L[i:i + len(sig)] += sig * g * np.sqrt((1 - pan) / 2); R[i:i + len(sig)] += sig * g * np.sqrt((1 + pan) / 2)
def lp(x, a): return lfilter([a], [1, -(1 - a)], x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def env(n, a, r):
    e = np.ones(n); ai, ri = int(a * SR), int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def verb(s, wet=.4):
    o = np.zeros(len(s) + int(1.6 * SR)); o[:len(s)] += s
    for dl, a in ((.07,.5),(.13,.42),(.21,.34),(.33,.27),(.5,.2),(.74,.13),(1.05,.08)):
        i = int(dl * SR); o[i:i+len(s)] += lp(s, .25) * a * wet
    return o
def pluck(f, dur=2.2, g=1.0):
    """Karplus-Strong string, guzheng-ish with a little pitch bend."""
    n = int(dur * SR); p = int(SR / f)
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = .5 * (buf[i % p] + buf[(i + 1) % p]) * .996
    return verb(out * .12 * g, .5)
PENTA = [293.7, 329.6, 392.0, 440.0, 523.3, 587.3, 659.3]
_pl = {}
def plk(f, g=1.0):
    if f not in _pl: _pl[f] = pluck(f)
    return _pl[f] * g
def melody(t0, t1, g=1.0, per=.55, seed=0):
    r = np.random.default_rng(seed); t = t0; k = 3
    while t < t1:
        k = int(np.clip(k + r.choice([-2, -1, 1, 1, 2]), 0, len(PENTA) - 1))
        add(plk(PENTA[k], g), t, r.uniform(-.5, .5)); t += per * r.choice([1, 1, 2, .5])
def bell(g=1.0):
    """Small Taoist hand bell: inharmonic partials + clapper tick, rung twice."""
    n = int(1.8 * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*x) * np.exp(-x * d) for f, a, d in ((1870, 1, 3), (2810, .6, 4.5), (4460, .35, 7), (5980, .2, 9)))
    s += bp(rng.standard_normal(n), 3000, 8000) * np.exp(-x * 120) * .5
    o = np.zeros(n + int(.28 * SR)); o[:n] += s; o[int(.28 * SR):] += s * .7
    return verb(o * .06 * g, .35)
def gong(g=1.0, dur=5.0):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 82 * (1 + .04 * np.exp(-x * 2))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = (np.sin(ph) + .5 * np.sin(2.76 * ph) + .3 * np.sin(5.4 * ph) + .2 * np.sin(8.9 * ph)) * np.exp(-x * .8)
    s *= np.minimum(1, x / .01)
    s += lp(rng.standard_normal(n), .05) * np.exp(-x * 9) * .6
    return s * .2 * g
def boom(g=1.0, dur=3.0):
    n = int(dur * SR); x = np.arange(n) / SR
    return (np.sin(2*np.pi*(38 + 80*np.exp(-x*7))*x) * np.exp(-x*2.4) * .6 + lp(rng.standard_normal(n), .06) * np.exp(-x*8) * .35) * g
def hop(g=1.0):
    """Two stiff feet landing together on wooden boards: low thud + wood knock + robe swish."""
    n = int(.45 * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*(70 - 30*x/.45)*x) * np.exp(-x*16) * .6
    s += bp(rng.standard_normal(n), 400, 1600) * np.exp(-x*45) * .35
    s += np.sin(2*np.pi*220*x) * np.exp(-x*30) * .12
    s += bp(rng.standard_normal(n), 1500, 5000) * np.exp(-((x - .03) / .04) ** 2) * .05
    return s * g
def hops(t0, t1, per, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        add(hop(g), t, pan); t += per
def heart(a, b, g=1.0):
    t0, per = a, .9
    while t0 < b - .2:
        for dt, k in ((0, 1), (.22, .7)):
            n = int(.25 * SR); x = np.arange(n) / SR
            add(np.sin(2*np.pi*(55 - 20*x/.25)*x) * np.exp(-x*18) * .35 * k * g, t0 + dt)
        t0 += per; per = max(.45, per * .94)
def flutter(dur=1.4, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    am = (np.abs(np.sin(2*np.pi*13*x + 3*np.sin(2*np.pi*2*x))) ** 3)
    return bp(rng.standard_normal(n), 1200, 6000) * am * env(n, .05, .6) * .14 * g
def whoosh(dur=1.6, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    return bp(rng.standard_normal(n), 200, 1800) * np.sin(np.pi * x / dur) ** 2 * .25 * g
def knock(g=1.0):
    o = np.zeros(int(1.2 * SR))
    for k in range(3):
        n = int(.12 * SR); x = np.arange(n) / SR
        s = (np.sin(2*np.pi*140*x) * .6 + bp(rng.standard_normal(n), 300, 2000) * .5) * np.exp(-x*40)
        i = int(k * .32 * SR); o[i:i+n] += s
    return o * .5 * g
def creak(dur=1.3, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 180 + 120 * np.sin(np.pi * x / dur)
    s = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)) * (.5 + .5*np.sin(2*np.pi*31*x))
    return bp(s, 300, 2500) * env(n, .1, .3) * .05 * g
def slap(g=1.0):
    n = int(.2 * SR); x = np.arange(n) / SR
    return bp(rng.standard_normal(n), 500, 6000) * np.exp(-x*40) * .6 * g
def birds(t0, t1, g=1.0):
    t = t0
    while t < t1:
        n = int(.16 * SR); x = np.arange(n) / SR
        f = rng.uniform(2600, 4400) * (1 + .25 * np.sin(2*np.pi*16*x))
        add(np.sin(2*np.pi*np.cumsum(f)/SR) * np.sin(np.pi*x/.16) ** 2 * .025 * g, t, rng.uniform(-.8, .8)); t += rng.uniform(.3, 1.2)
def pad(dur, freqs, g):
    n = int(dur * SR); t = np.arange(n) / SR
    p = sum(np.sin(2*np.pi*f*t) * (.6 + .4*np.sin(2*np.pi*.11*t + i)) for i, f in enumerate(freqs))
    return lp(p, .15) * env(n, 1.0, 1.0) * g

LV = dict(hook=.7, inn=.3, warn=.25, paper=.55, wake=.85, cliff=.9, recap=.6, breath=.8, bell=.7, dawn=.25,
          explain=.3, outro=.3)
WIND = dict(hook=.8, inn=.3, warn=.15, paper=.6, wake=.5, cliff=.4, recap=.5, breath=.2, bell=.3, dawn=.4, explain=0, outro=0)
RIVER = dict(hook=0, inn=.8, warn=.2, paper=.2, wake=0, cliff=0, recap=0, breath=0, bell=0, dawn=.7, explain=0, outro=0)
def curve(D, a):
    c = np.zeros(N)
    for s in T: c[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = D[s["id"]]
    c[int(TOT * SR):] = c[int(TOT * SR) - 1]
    return lp(c, a)
lvl, wl, rv = curve(LV, .0006), curve(WIND, .0004), curve(RIVER, .0004)
drone = ((np.sin(2*np.pi*55*tt) + .5*np.sin(2*np.pi*82.4*tt) + .3*np.sin(2*np.pi*110*tt + np.sin(2*np.pi*.2*tt))) * .045
         + lp(rng.standard_normal(N), .008) * .2) * lvl
wmod = .6 + .4 * np.sin(2*np.pi*.09*tt) * np.sin(2*np.pi*.23*tt + 1)
windL = bp(rng.standard_normal(N), 250, 1400) * .08 * wmod; windR = bp(rng.standard_normal(N), 260, 1500) * .08 * wmod[::-1]
riv = lambda: bp(rng.standard_normal(N), 600, 4000) * .03 * (.8 + .2 * lp(rng.standard_normal(N), .0005) * 30)
L += drone + windL * wl + riv() * rv; R += drone + windR * wl + riv() * rv
if PART == "p1":
    add(gong(.8), st["hook"] + .05); add(bell(.8), st["hook"] + .9, .4)
    hops(cap("hook", 0) + 1.0, st["hook"] + DUR["hook"] - .3, .75, .45, .3)
    add(boom(.8), cap("hook", 1) - .05); add(whoosh(1.5, .7), cap("hook", 1) - .6)
    melody(st["inn"] + .3, cap("inn", 1) - .2, .8, .6, seed=1)
    add(knock(1.0), cap("inn", 1) + .5, .3); add(bell(.9), cap("inn", 1) + 2.2, .3); add(bell(.6), cap("inn", 1) + 3.4, .2)
    add(pad(DUR["warn"], (146.8, 220, 293.7), .02), st["warn"])
    add(plk(PENTA[2], .8), cap("warn", 1)); add(plk(PENTA[0], .8), cap("warn", 2) - .1)
    add(boom(.5), cap("warn", 2) + .4)
    add(creak(1.4, 1.0), st["paper"] + .3, -.3)
    heart(cap("paper", 1), cap("paper", 2), .8)
    add(whoosh(2.0, 1.0), cap("paper", 2) - .1, .3); add(flutter(1.8, 1.2), cap("paper", 2) + .1, .5)
    add(gong(.7, 4), cap("wake", 0) + .3)
    add(whoosh(.8, .6), cap("wake", 1) + .2)
    add(hop(1.6), cap("wake", 2) + .5); add(boom(.9), cap("wake", 2) + .5)
    hops(st["cliff"] + .2, cap("cliff", 1) - .2, .65, 1.1, .2)
    heart(st["cliff"], cap("cliff", 2) - .3, 1.0)
    add(boom(.7), cap("cliff", 1) - .05)
    add(gong(1.0), cap("cliff", 2) - .1); add(bell(.7), cap("cliff", 2) + 1.0, .4)
else:
    add(gong(.6), st["recap"] + .05)
    hops(cap("recap", 1) - .5, st["recap"] + DUR["recap"] - .2, .65, .9, -.2)
    add(plk(PENTA[4], .8), cap("breath", 1))
    hb0, hb1 = cap("breath", 2) - .2, cap("bell", 1) + .3
    # muffle: everything else drops while she holds her breath
    m = np.ones(N); m[int(hb0 * SR):int(hb1 * SR)] = .35; m = lp(m, .0008); L *= m; R *= m
    heart(hb0, hb1, 1.2)
    add(whoosh(1.2, .4), cap("breath", 2) + 1.6, -.6); add(whoosh(1.2, .4), cap("breath", 2) + 3.0, .6)
    add(bell(1.2), cap("bell", 1) - .1, .5); add(bell(.9), cap("bell", 1) + .5, .4)
    add(creak(.6, 1.5), cap("bell", 1) + 1.0, .3)
    add(slap(1.0), cap("bell", 1) + 2.4); add(gong(1.0), cap("bell", 1) + 2.45)
    add(boom(.6), cap("bell", 2))
    add(whoosh(1.2, .5), cap("bell", 2) + 1.0)          # her long exhale
    birds(st["dawn"] + .5, st["dawn"] + DUR["dawn"] - .3, .8)
    for k in range(5): add(bell(.35), st["dawn"] + .8 + k * 1.6, .2)
    hops(st["dawn"] + .4, st["dawn"] + DUR["dawn"] - .5, .8, .25, .1)
    melody(st["explain"] + .3, st["explain"] + DUR["explain"] - .5, .55, .7, seed=3)
    add(pad(DUR["explain"] + .4, (146.8, 174.6, 220), .02), st["explain"])
    add(bell(.4), cap("explain", 1) + .3, -.2); add(bell(.4), cap("explain", 2) + .3, .2)
    melody(st["outro"] + .2, st["outro"] + DUR["outro"] - 1.0, .5, .55, seed=5)
    add(pad(DUR["outro"], (146.8, 185, 220, 293.7), .02), st["outro"])
duck = np.ones(N)
for s in T:
    for c in s["caps"]: duck[int((st[s["id"]] + c[1]) * SR):int((st[s["id"]] + c[2]) * SR)] = .6
duck = lp(duck, .0008); L *= duck; R *= duck
vo = np.concatenate([sf.read(f"{PART}/vo/{s['id']}.wav")[0] for s in T]); vo = vo / np.abs(vo).max() * .85
L[:len(vo)] += vo; R[:len(vo)] += vo
mix = np.stack([L, R], 1)[:int(TOT * SR)]; mix /= max(1.0, np.abs(mix).max() / .97)
sf.write(f"{PART}/mix.wav", mix.astype(np.float32), SR); print(PART, "ok", round(TOT, 2))
