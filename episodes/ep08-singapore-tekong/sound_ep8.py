"""Ep08 Singapore / Tekong sound: dogs howling, night crickets, scares from toolkit/sfx.py."""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt
PART = sys.argv[1]; SR = 24000
T = json.load(open(f"{PART}/timing.json"))
st = {}; acc = 0
for s in T: st[s["id"]] = acc; acc += s["dur"]
TOT = acc; N = int(TOT * SR) + SR
rng = np.random.default_rng(81 if PART == "p1" else 82)
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


import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
import sfx
def footsteps(t0, t1, per, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        n = int(.18 * SR); x = np.arange(n) / SR
        s = (np.sin(2*np.pi*(90 - 40*x/.18)*x) * np.exp(-x*28) * .5 + bp(rng.standard_normal(n), 600, 3000) * np.exp(-x*50) * .25)
        add(s * g, t, pan + rng.uniform(-.05, .05)); t += per * rng.uniform(.93, 1.07)
def thud(g=1.0):
    n = int(1.2 * SR); x = np.arange(n) / SR
    return (np.sin(2*np.pi*(48 + 30*np.exp(-x*12))*x) * np.exp(-x*5) * .8 + bp(rng.standard_normal(n), 150, 900) * np.exp(-x*25) * .4) * g
def slam(g=1.0):
    return verb(thud(1.0) + np.pad(slap(.8), (0, int(1.0 * SR))), .3)[:int(2.0 * SR)] * g
def beep(g=1.0):
    o = np.zeros(int(.8 * SR))
    for k in range(2):
        n = int(.12 * SR); x = np.arange(n) / SR
        o[int(k * .25 * SR):int(k * .25 * SR) + n] += np.sin(2*np.pi*1320*x) * env(n, .005, .03) * .12
    return o * g
def engine(dur, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    s = lp(rng.standard_normal(n), .01) * 3 + np.sin(2*np.pi*(42 + 6*x/dur)*x) * .4
    return s * np.exp(-x * 1.3 / dur * 2) * env(n, .05, .8) * .35 * g
def crickets(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*4300*x) * (np.sin(2*np.pi*22*x) > .6) * (np.sin(2*np.pi*.7*x) > -.2) * .012
    s2 = np.sin(2*np.pi*3700*x) * (np.sin(2*np.pi*19*x + 1) > .7) * (np.sin(2*np.pi*.53*x + 2) > 0) * .01
    add(s * g, t0, -.5); add(s2 * g, t0, .5)
def big_bell(g=1.0):
    n = int(6 * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*x) * np.exp(-x*d) for f, a, d in ((196, 1, .5), (392.4, .5, .8), (466, .35, 1.1), (588, .25, 1.4), (980, .12, 2.2)))
    return verb(s * np.minimum(1, x / .005) * .12 * g, .5)
def match(g=1.0):
    n = int(1.2 * SR); x = np.arange(n) / SR
    return (bp(rng.standard_normal(n), 1500, 7000) * np.exp(-x*12) * .4 + bp(rng.standard_normal(n), 200, 900) * np.exp(-x*2) * .08) * g
def breath(t0, t1, g=1.0, per=1.1):
    t = t0
    while t < t1:
        n = int(.5 * SR); x = np.arange(n) / SR
        add(bp(rng.standard_normal(n), 400, 2500) * np.sin(np.pi*x/.5) ** 2 * .06 * g, t); t += per
def scare(t, g=1.0):
    add(sfx.braam(3.0, g), t); add(sfx.sub_drop(2.0, g), t); add(sfx.glitch(.5, g * .9), t, .2); add(sfx.dissonant_strings(4.0, g * .7), t + .05)
def howls(t0, t1, every=16, dist=.75, g=1.0, seed=0):
    r = np.random.default_rng(seed); t = t0
    while t < t1 - 3:
        add(sfx.dog_howl(r.uniform(3.2, 4.4), r.uniform(450, 620), dist, seed=int(r.integers(99)), g=g), t, r.uniform(-.7, .7)); t += every * r.uniform(.85, 1.15)
SAUNG = [293.7, 329.6, 370.0, 440.0, 493.9, 587.3, 659.3]
def melody2(t0, t1, g=1.0, per=.6, seed=0):
    r = np.random.default_rng(seed); t = t0; k = 3
    while t < t1:
        k = int(np.clip(k + r.choice([-2, -1, 1, 1, 2]), 0, len(SAUNG) - 1))
        add(plk(SAUNG[k], g), t, r.uniform(-.5, .5)); t += per * r.choice([1, 1, 2, .5])


def thunder(g=1.0):
    n = int(5 * SR); x = np.arange(n) / SR
    s = lp(rng.standard_normal(n), .01) * 6 * (np.exp(-x * .9) * (1 + .6 * np.sin(2*np.pi*1.3*x) ** 2))
    s += bp(rng.standard_normal(n), 80, 400) * np.exp(-x * 3) * .6
    return s * env(n, .05, 1.0) * .35 * g
def static(dur, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1200, 5000) * (.5 + .5 * (np.sin(2*np.pi*7*x) > 0)) * env(n, .02, .1) * .08 * g
def whistle(g=1.0):
    n = int(1.0 * SR); x = np.arange(n) / SR
    f = 2600 + 90 * np.sin(2*np.pi*38*x)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * env(n, .02, .2) * .07 * g
def squelch(t0, t1, per, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        n = int(.22 * SR); x = np.arange(n) / SR
        s = np.sin(2*np.pi*(80 - 30*x/.22)*x) * np.exp(-x*22) * .5 + bp(rng.standard_normal(n), 300, 1800) * np.exp(-x*18) * .3
        add(s * g, t, pan + rng.uniform(-.05, .05)); t += per * rng.uniform(.93, 1.07)
def door_creak(dur=1.6, g=1.0):
    return creak(dur, 1.6 * g)

LV = dict(hook=.8, ferry=.3, rule=.3, fall=.55, voice=.8, answer=.8, cliff=.9, recap=.6, run=.9, lights=.3, bunk=.7, twist=.85, explain=.3, outro=.25)
WIND = dict(hook=.5, ferry=.6, rule=.3, fall=.4, voice=.5, answer=.5, cliff=.3, recap=.4, run=.5, lights=.3, bunk=0, twist=0, explain=0, outro=.2)
RAINV = dict(hook=1, ferry=1, rule=1, fall=1, voice=1, answer=1, cliff=.8, recap=1, run=1.1, lights=.8, bunk=.25, twist=.25, explain=.2, outro=.6)
def curve(Dd, a):
    c = np.zeros(N)
    for s in T: c[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = Dd[s["id"]]
    c[int(TOT * SR):] = c[int(TOT * SR) - 1]
    return lp(c, a)
lvl, wl, rl = curve(LV, .0006), curve(WIND, .0004), curve(RAINV, .0006)
drone = ((np.sin(2*np.pi*46.2*tt) + .5*np.sin(2*np.pi*69.3*tt) + .3*np.sin(2*np.pi*98*tt + np.sin(2*np.pi*.2*tt))) * .05
         + lp(rng.standard_normal(N), .008) * .22) * lvl
wmod = .6 + .4 * np.sin(2*np.pi*.09*tt) * np.sin(2*np.pi*.23*tt + 1)
windL = bp(rng.standard_normal(N), 250, 1400) * .07 * wmod; windR = bp(rng.standard_normal(N), 260, 1500) * .07 * wmod[::-1]
rainL = bp(rng.standard_normal(N), 900, 9000) * .06 * (.85 + .15 * np.sin(2*np.pi*.13*tt)); rainR = bp(rng.standard_normal(N), 900, 9000) * .06
drops = np.zeros(N); idx = rng.integers(0, N, int(TOT * 40)); drops[idx] = rng.uniform(.1, .4, len(idx)); drops = bp(drops, 2000, 8000) * .5
L += drone + windL * wl + (rainL + drops) * rl; R += drone + windR * wl + (rainR + drops) * rl
SIL = []
if PART == "p1":
    add(thunder(1.0), st["hook"] + .1)
    add(sfx.dog_pack(7.0, .65, 1.0), st["hook"] + 1.0)
    add(sfx.reverse_whisper(1.6, 1.0), cap("hook", 1) + 1.2, -.5)
    add(sfx.sub_drop(2.0, .8), cap("hook", 1) + 2.4)
    add(engine(6.0, .8), st["ferry"] + .2, -.3)
    add(sfx.dog_howl(4.0, 520, .8, seed=5), st["ferry"] + 4.5, .6)
    add(whistle(1.0), st["rule"] + .3, .3)
    squelch(st["rule"] + 1.0, st["rule"] + DUR["rule"], .5, .6)
    add(static(1.2, 1.0), cap("rule", 2) - .3, -.4)
    squelch(st["fall"], cap("fall", 2), .7, .6)
    add(beep(.8), cap("fall", 1) + .3)
    add(sfx.heartbeat_accel(DUR["fall"] - 3, .95, .6, .8), cap("fall", 2) - .5)
    add(sfx.dog_howl(4.2, 560, .7, seed=6), cap("fall", 2) + .5, -.6)
    add(sfx.reverse_whisper(1.6, 1.2), st["voice"] + .3, -.7)
    add(sfx.reverse_whisper(1.6, 1.0), st["voice"] + 1.6, .7)
    add(sfx.reverse_whisper(1.6, 1.0), st["voice"] + 3.0, -.4)
    add(sfx.dissonant_strings(5.0, .6), st["voice"] + .5)
    add(sfx.pulse_beat(DUR["answer"], 70, 120, .7), st["answer"])
    add(sfx.riser(1.6, .8), cap("answer", 2) - 1.4)
    scare(cap("answer", 2) + .2, .8)
    squelch(st["cliff"] + .3, cap("cliff", 1), .9, .8, -.4)
    add(sfx.glitch(.5, 1.0), cap("cliff", 1) + .3); add(beep(1.0), cap("cliff", 1))
    SIL.append((cap("cliff", 1) + .35, cap("cliff", 1) + 1.2))   # torch dies: silence
    add(sfx.heartbeat_accel(DUR["cliff"] - 5, .8, .45, 1.0), cap("cliff", 2) - .4)
    add(sfx.reverse_whisper(1.6, 1.3), cap("cliff", 2) + .2, .8)
    t4 = cap("cliff", 3)
    add(sfx.riser(1.6, 1.0), t4 - .5)
    SIL.append((t4 + 1.0, t4 + 1.1))
    scare(t4 + 1.1, 1.15)
else:
    add(thunder(.9), st["recap"] + .05); add(sfx.reverse_whisper(1.6, 1.0), st["recap"] + 1.2, .6)
    add(sfx.sub_drop(2.0, .7), cap("recap", 1))
    squelch(st["run"], st["run"] + DUR["run"], .28, 1.0)
    breath(st["run"], st["run"] + DUR["run"], 1.3, .55)
    squelch(cap("run", 1) + .3, st["run"] + DUR["run"], .3, .6, -.6)        # footsteps behind, matching
    add(sfx.heartbeat_accel(DUR["run"], .6, .38, 1.0), st["run"])
    for c in (.3, 1.3, 2.3):
        add(sfx.braam(2.0, .8), cap("run", 1) + c); add(sfx.glitch(.4, .8), cap("run", 1) + c, -.3)
    add(whistle(.8), cap("lights", 1) - .5, .4)
    add(pad(DUR["lights"], (146.8, 220, 293.7), .02), st["lights"])
    add(sfx.sub_drop(2.0, .7), cap("lights", 2) + .3)
    add(sfx.dog_howl(4.0, 520, .85, seed=8), st["bunk"] + .5, -.6)
    for k, tt in enumerate((1.4, 2.0, 2.6)):
        add(plk([440, 440, 349.2][k], .9), cap("bunk", 1) + tt)
    add(sfx.dissonant_strings(5.0, .6), cap("bunk", 2) - .2)
    add(door_creak(2.0, 1.0), st["twist"] + .2, .5)
    add(sfx.heartbeat_accel(DUR["twist"] - 1.5, .9, .45, 1.0), st["twist"] + .3)
    add(sfx.reverse_whisper(1.6, 1.2), cap("twist", 1) - .2, .5)
    jt = st["twist"] + DUR["twist"] - 1.1
    add(sfx.riser(1.6, 1.0), jt - 1.7)
    SIL.append((jt - .1, jt))
    scare(jt, 1.15)
    melody2(st["explain"] + .4, st["explain"] + DUR["explain"] - .5, .5, .7, seed=3)
    add(pad(DUR["explain"] + .4, (146.8, 185, 220), .02), st["explain"])
    add(sfx.dog_howl(4.0, 500, .85, seed=9), st["explain"] + 8.0, .6)
    melody2(st["outro"] + .2, st["outro"] + DUR["outro"] - 1.0, .45, .55, seed=5)
    add(pad(DUR["outro"], (146.8, 185, 220, 293.7), .02), st["outro"])
    add(sfx.dog_howl(4.0, 540, .85, seed=11), st["outro"] + 3.8, -.5)
for a, b in SIL:
    m = np.ones(N); m[int(a * SR):int(b * SR)] = 0.0; m = lp(m, .02); L *= m; R *= m
duck = np.ones(N)
for s in T:
    for c in s["caps"]: duck[int((st[s["id"]] + c[1]) * SR):int((st[s["id"]] + c[2]) * SR)] = .55
duck = lp(duck, .0008); L *= duck; R *= duck
vo = np.concatenate([sf.read(f"{PART}/vo/{s['id']}.wav")[0] for s in T]); vo = vo / np.abs(vo).max() * .85
L[:len(vo)] += vo; R[:len(vo)] += vo
mix = np.stack([L, R], 1)[:int(TOT * SR)]; mix /= max(1.0, np.abs(mix).max() / .97)
sf.write(f"{PART}/mix.wav", mix.astype(np.float32), SR); print(PART, "ok", round(TOT, 2))
