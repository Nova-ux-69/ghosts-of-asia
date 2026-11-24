"""Ep10 India / the Chudail (2.1D survival) sound: desert wind, a two-stroke scooter that coughs and dies, silver anklets
(payal) on every step, a peacock scream (false scare), a tanpura drone and santoor-like plucks in a Bhairav-style scale,
a female whisper calling "Arjun...", a brass temple bell at dawn; scares from toolkit/sfx.py."""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt
PART = sys.argv[1]; SR = 24000
T = json.load(open(f"{PART}/timing.json"))
st = {}; acc = 0
for s in T: st[s["id"]] = acc; acc += s["dur"]
TOT = acc; N = int(TOT * SR) + SR
rng = np.random.default_rng(101 if PART == "p1" else 102)
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

def bark(g=1.0, pitch=1.0):
    """A dog bark: short noisy formant burst with a falling pitch."""
    n = int(.22 * SR); x = np.arange(n) / SR
    f = (520 - 380 * x / .22) * pitch
    v = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)) * .5 + rng.standard_normal(n) * .5
    return bp(v, 350, 2600) * np.exp(-x * 14) * np.minimum(1, x / .01) * .35 * g
def barking(t0, t1, g=1.0, n=3):
    for k in range(n):
        r = np.random.default_rng(40 + k); t = t0 + r.uniform(0, .4); pan = r.uniform(-.8, .8); p = r.uniform(.8, 1.25)
        while t < t1:
            for j in range(int(r.integers(1, 4))):
                add(bark(g * r.uniform(.6, 1.0), p), t + j * .19, pan)
            t += r.uniform(.7, 1.5)
def frogs(t0, t1, g=1.0):
    r = np.random.default_rng(5); t = t0
    while t < t1:
        n = int(.09 * SR); x = np.arange(n) / SR
        f = r.uniform(380, 640)
        s = np.sign(np.sin(2*np.pi*f*x)) * (np.sin(2*np.pi*55*x) > 0) * np.sin(np.pi * x / .09)
        add(bp(s, 300, 1800) * .02 * g, t, r.uniform(-.9, .9)); t += r.uniform(.15, .6)
def shriek(dur=1.2, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 1250 + 500 * np.sin(np.pi * x / dur) + 60 * np.sin(2*np.pi*9*x)
    s = sum(np.sin(2*np.pi*np.cumsum(f * k)/SR) / k for k in (1, 1.013, 1.5, 2.02))
    s += bp(rng.standard_normal(n), 2000, 7000) * .6
    return verb(s * env(n, .03, .5) * .12 * g, .5)
def rustle(dur=1.5, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    am = np.abs(np.sin(2*np.pi*6*x + 2*np.sin(2*np.pi*1.3*x))) ** 2
    return bp(rng.standard_normal(n), 2500, 9000) * am * env(n, .2, .4) * .08 * g


# ---------------------------------------------------------------- ep10 sounds
BHAIRAV = [293.7, 311.1, 370.0, 392.0, 440.0, 466.2, 554.4, 587.3, 622.3]     # D Bhairav: Sa re(b) Ga ma Pa dha(b) Ni Sa'
def santoor(t0, t1, g=1.0, per=.5, seed=0):
    r = np.random.default_rng(seed); t = t0; k = 4
    while t < t1:
        k = int(np.clip(k + r.choice([-2, -1, -1, 1, 1, 2]), 0, len(BHAIRAV) - 1))
        for rep in range(int(r.choice([1, 1, 2]))):
            add(plk(BHAIRAV[k], g * (1 - .3 * rep)), t + rep * .09, r.uniform(-.5, .5))
        t += per * r.choice([1, 1, 2, .5])
def tanpura(t0, dur, g=1.0):
    """Pa - Sa' - Sa' - Sa (low), plucked in a loop, buzzy (jawari) and long."""
    n = int(dur * SR); out = np.zeros(n + SR * 3); t = 0.0; seq = [110.0, 146.8, 146.8, 73.4]; i = 0
    while t < dur:
        f = seq[i % 4]; m = int(2.8 * SR); x = np.arange(m) / SR
        s = sum(np.sin(2 * np.pi * f * h * x + h) / h ** .7 for h in range(1, 12)) * np.exp(-x * .9)
        s *= 1 + .3 * np.sin(2 * np.pi * 3.1 * x)
        a = int(t * SR); out[a:a + m] += s * .02
        t += .72; i += 1
    add(lp(out, .3)[:n] * env(n, .6, 1.0) * g, t0)
def payal(g=1.0, n=7):
    """Silver anklet: a cluster of tiny bells jingling."""
    m = int(.5 * SR); x = np.arange(m) / SR; o = np.zeros(m)
    for k in range(n):
        f = rng.uniform(4200, 7600); d0 = rng.uniform(0, .06); i = int(d0 * SR)
        o[i:] += np.sin(2 * np.pi * f * x[:m - i]) * np.exp(-x[:m - i] * rng.uniform(25, 45)) * rng.uniform(.4, 1)
    o += bp(rng.standard_normal(m), 5000, 10000) * np.exp(-x * 60) * .3
    return verb(o * .05 * g, .3)
def sand_step(g=1.0):
    n = int(.25 * SR); x = np.arange(n) / SR
    return (bp(rng.standard_normal(n), 300, 2500) * np.exp(-x * 22) * .35 + np.sin(2 * np.pi * 70 * x) * np.exp(-x * 30) * .25) * g
def stone_step(g=1.0):
    n = int(.3 * SR); x = np.arange(n) / SR
    return verb((np.sin(2 * np.pi * (110 - 40 * x / .3) * x) * np.exp(-x * 30) * .5 + bp(rng.standard_normal(n), 800, 4000) * np.exp(-x * 60) * .3) * g, .6)
def walking(t0, t1, per, g=1.0, stone=False, jingle=True, pan=0.0):
    t = t0
    while t < t1:
        add((stone_step if stone else sand_step)(g * .8), t, pan)
        if jingle:
            add(payal(g), t + .01, pan + rng.uniform(-.1, .1))
        t += per
def scooter(t0, t1, g=1.0, cough_at=None):
    """Two-stroke putter: pulses at ~28 Hz on a noisy low hum; optional cough-and-die at cough_at."""
    n = int((t1 - t0) * SR); x = np.arange(n) / SR
    f = 28 + 3 * np.sin(2 * np.pi * .4 * x)
    pulse = (np.sin(2 * np.pi * np.cumsum(f) / SR) > .6).astype(float)
    s = lp(pulse, .2) * .5 + lp(rng.standard_normal(n), .05) * .5
    s = bp(s, 60, 1800)
    if cough_at is not None:
        c = cough_at - t0
        gate = np.ones(n)
        for k, (a, b) in enumerate(((c - 1.6, c - 1.35), (c - 1.0, c - .7), (c - .45, c - .3))):
            gate[int(max(0, a) * SR):int(max(0, b) * SR)] = 0
        gate[int(c * SR):] = 0
        gate = lp(gate, .02)
        s *= gate
    add(s * .35 * g * env(n, .3, .2), t0)
def peacock_scream(g=1.0):
    """'may-AWW' - two loud nasal cries."""
    o = np.zeros(int(1.6 * SR))
    for k, (st_, d) in enumerate(((0.0, .45), (.55, .6))):
        n = int(d * SR); x = np.arange(n) / SR
        f = 700 + 500 * np.sin(np.pi * x / d) ** .5 * (1 if k else .8)
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = sum(np.sin(h * ph) / h for h in range(1, 9)) * env(n, .02, .15)
        s = bp(s, 500, 5000)
        i = int(st_ * SR); o[i:i + n] += s
    return verb(o * .22 * g, .5)
def brass_bell(g=1.0):
    n = int(5 * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * x) * np.exp(-x * d) for f, a, d in ((523, 1, .7), (1043, .6, 1.0), (1312, .45, 1.4), (1790, .3, 2.0), (2650, .2, 3.0), (3400, .12, 4)))
    s += bp(rng.standard_normal(n), 2000, 7000) * np.exp(-x * 80) * .5
    return verb(s * np.minimum(1, x / .003) * .09 * g, .5)
def glass_clink(g=1.0):
    n = int(.4 * SR); x = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 30) for f in (3100, 4700, 6200)) * .04 * g
WH = {}
def whisper(text="Arjun...", voice="af_nicole", g=1.0):
    if text not in WH:
        try:
            from kokoro_onnx import Kokoro
            tk = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit", "models")
            k = Kokoro(os.path.join(tk, "kokoro.onnx"), os.path.join(tk, "voices.bin"))
            try:
                a, sr = k.create(text, voice=voice, speed=0.7, lang="en-us")
            except Exception:
                a, sr = k.create(text, voice="bf_emma", speed=0.7, lang="en-gb")
            a = np.asarray(a, float)
            breathy = bp(rng.standard_normal(len(a)), 1500, 7000) * np.abs(a) * 3.0      # airy whisper texture
            v = bp(a, 250, 6000) * .5 + breathy
            v = v / (np.abs(v).max() + 1e-9)
            WH[text] = verb(v * .25, .6)
        except Exception as e:
            print("whisper failed", e); WH[text] = np.zeros(SR)
    return WH[text] * g

LV = dict(hook=.8, road=.25, rule=.15, tree=.5, woman=.8, mistake=.8, cliff=.9, recap=.6, steps=.85, escape=.6, bell=.4, twist=.25, explain=.3, outro=.25)
WIND = dict(hook=.9, road=.8, rule=0, tree=.6, woman=.6, mistake=.6, cliff=.15, recap=.2, steps=.15, escape=.7, bell=.4, twist=.1, explain=.4, outro=.3)
NIGHT = dict(hook=.4, road=0, rule=0, tree=.6, woman=.4, mistake=.2, cliff=0, recap=0, steps=0, escape=.2, bell=.2, twist=0, explain=.4, outro=.3)
def curve(Dd, a):
    c = np.zeros(N)
    for s in T: c[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = Dd[s["id"]]
    c[int(TOT * SR):] = c[int(TOT * SR) - 1]
    return lp(c, a)
lvl, wl = curve(LV, .0006), curve(WIND, .0004)
drone = ((np.sin(2*np.pi*36.7*tt) + .5*np.sin(2*np.pi*55*tt) + .3*np.sin(2*np.pi*77.8*tt + np.sin(2*np.pi*.17*tt))) * .05
         + lp(rng.standard_normal(N), .008) * .22) * lvl
wmod = .6 + .4 * np.sin(2*np.pi*.07*tt) * np.sin(2*np.pi*.19*tt + 1)
windL = bp(rng.standard_normal(N), 200, 1700) * .1 * wmod; windR = bp(rng.standard_normal(N), 220, 1800) * .1 * wmod[::-1]
L += drone + windL * wl; R += drone + windR * wl
for s in T:
    if NIGHT[s["id"]] > 0:
        crickets(st[s["id"]], st[s["id"]] + s["dur"], NIGHT[s["id"]] * .8)
SIL = []
if PART == "p1":
    add(sfx.dog_pack(7.0, .7, 1.1), st["hook"] + .1)
    cut = cap("hook", 1) - .15
    add(sfx.sub_drop(2.0, .9), cut); add(sfx.glitch(.4, .6), cut)
    walking(cut + .05, st["hook"] + DUR["hook"], .385, .9)
    add(sfx.reverse_whisper(1.6, .8), st["hook"] + 1.6, .5)
    scooter(st["road"], cap("tree", 0) + 2.9, .9, cough_at=cap("tree", 0) + 2.4)
    santoor(st["road"] + .5, st["road"] + DUR["road"] - .4, .45, .6, seed=3)
    add(sfx.reverse_whisper(1.6, .7), st["road"] + 3.1, -.6)
    add(sfx.dog_howl(4.0, 520, .8, seed=21, g=.6), st["road"] + 5.0, .6)
    for k in range(4): add(beep(.8), cap("road", 2) - .1 + k * .7, .2)
    tanpura(st["rule"], DUR["rule"], 1.0)
    for k in range(4): add(plk(BHAIRAV[[4, 3, 2, 1][k]], .7), st["rule"] + .6 + k * 2.2)
    add(sfx.reverse_whisper(1.6, .8), cap("rule", 2) - .4, -.3)
    die = cap("tree", 0) + 2.4
    add(slap(.5), die + .05, .3)
    pk = st["tree"] + C["tree"][0][2] + .1
    SIL.append((pk - .35, pk))
    add(peacock_scream(1.2), pk, -.3); add(flutter(1.4, 1.2), pk, -.2); add(sfx.braam(1.6, .45), pk); add(whoosh(1.0, 1.0), pk + .1, .4)
    add(sfx.dog_pack(6.0, .75, 1.0), cap("tree", 1) - .2)
    add(sfx.heartbeat_accel(DUR["tree"] - (cap("tree", 1) - st["tree"]) + 1, .9, .6, .7), cap("tree", 1))
    walking(st["woman"] + .3, cap("woman", 1) - .2, .7, .8, pan=.4)
    add(whisper("Arjun...", g=.9), cap("woman", 1) + .1, .5)
    add(sfx.pulse_beat(DUR["woman"] - 3, 70, 110, .5), st["woman"] + 1.5)
    fc = cap("woman", 2) - .15
    add(sfx.riser(1.2, .7), fc - 1.2); SIL.append((fc - .3, fc))
    add(sfx.sub_drop(2.0, .9), fc); add(sfx.dissonant_strings(4.0, .6), fc); add(payal(1.0), fc + .3)
    add(sfx.heartbeat_accel(DUR["mistake"], .7, .5, .8), st["mistake"])
    lo = cap("mistake", 1)
    add(sfx.riser(1.0, .5), lo - 1.0)
    add(whoosh(.6, .8), lo - .05); add(glass_clink(1.0), lo)
    SIL.append((lo + .05, lo + .7))
    add(sfx.braam(2.5, .7), lo + .75); add(sfx.reverse_whisper(1.6, .9), lo + 1.0, .3)
    fp = cap("mistake", 2) - .1
    for k in range(7): add(sand_step(.9), fp + k * .32, (-.2 if k % 2 else .2)); add(payal(.5), fp + k * .32 + .01)
    add(sfx.dissonant_strings(4.0, .5), fp + 1.0)
    walking(st["cliff"], st["cliff"] + 1.6, .24, 1.0, stone=True, jingle=False)
    breath(st["cliff"] + 1.6, cap("cliff", 1), .9, 1.2)
    c1 = cap("cliff", 1)
    t_ = c1 - .3
    jt = st["cliff"] + C["cliff"][2][2] + .15
    while t_ < jt - 1.0:
        add(stone_step(1.0), t_); add(payal(1.1), t_ + .01); t_ += .55
    m0, m1 = c1 + .5, st["cliff"] + DUR["cliff"]
    m = np.ones(N); m[int(m0 * SR):int(m1 * SR)] = .5; m = lp(m, .0008); L *= m; R *= m
    add(sfx.heartbeat_accel(jt - m0, .9, .45, 1.1), m0)
    add(sfx.pulse_beat(jt - c1, 80, 150, .6), c1)
    add(sfx.dissonant_strings(5.0, .5), cap("cliff", 2))
    add(sfx.riser(1.6, 1.0), jt - 1.75)
    SIL.append((jt - .4, jt))
    scare(jt, 1.2)
else:
    add(sfx.sub_drop(2.0, .7), st["recap"] + .05)
    walking(st["recap"] + .4, st["recap"] + DUR["recap"], .7, .8, stone=True)
    add(sfx.dog_howl(4.2, 520, .7, seed=7), st["recap"] + 1.0, -.5)
    cut = cap("steps", 1) - .2
    walking(st["steps"], cut - .1, .7, 1.0, stone=True)
    add(whisper("Arjun...", g=1.0), st["steps"] + .4, -.3)
    add(sfx.pulse_beat(cut - st["steps"], 80, 140, .6), st["steps"])
    SIL.append((cut, cut + .5))
    add(sfx.dissonant_strings(4.0, .6), cut + .5)
    add(sfx.heartbeat_accel(st["steps"] + DUR["steps"] - cut, .8, .45, 1.0), cut + .5)
    hit = st["steps"] + C["steps"][1][2] + .2
    add(sfx.braam(2.0, .8), hit); add(sfx.glitch(.4, .8), hit); add(sfx.sub_drop(2.0, .7), hit)
    tanpura(st["escape"], cap("escape", 2) - st["escape"], .9)
    add(brass_bell(.25), cap("escape", 1) + .3, .3)
    rn = cap("escape", 2) - .1
    walking(rn, st["escape"] + DUR["escape"], .26, 1.0, jingle=False)
    breath(rn, st["bell"] + cap("bell", 1) - st["bell"], 1.0, .5)
    add(sfx.pulse_beat(st["escape"] + DUR["escape"] - rn + DUR["bell"] * .5, 110, 160, .6), rn)
    walking(st["bell"], cap("bell", 1) - .1, .26, .9, jingle=False)
    for k in range(5): add(whisper("Arjun...", g=.8 - .1 * k), st["bell"] + .2 + k * .65, (-.8, .7, -.4, .9, -.1)[k])
    ring = cap("bell", 1) + 1.2
    SIL.append((ring - .3, ring))
    for k in range(3): add(brass_bell(1.2 - .3 * k), ring + k * 1.1, -.2)
    add(sfx.reverse_whisper(1.6, .9), ring + .1, -.6)
    birds(ring + 1.2, st["bell"] + DUR["bell"] + DUR["twist"] - 1.2, 1.0)
    add(pad(st["bell"] + DUR["bell"] - ring, (146.8, 220, 293.7), .02), ring)
    add(pad(DUR["twist"], (146.8, 185, 220), .018), st["twist"])
    add(sfx.dissonant_strings(4.0, .45), cap("twist", 2) - .2)
    add(payal(.9), cap("twist", 2) + .4); add(sfx.sub_drop(2.0, .6), cap("twist", 2) - .1)
    add(sfx.heartbeat_accel(DUR["twist"] - (cap("twist", 2) - st["twist"]), .9, .45, .9), cap("twist", 2))
    jt = st["twist"] + DUR["twist"] - 1.0
    add(sfx.riser(1.6, 1.0), jt - 1.7)
    SIL.append((jt - .35, jt))
    scare(jt, 1.15)
    tanpura(st["explain"], DUR["explain"] + DUR["outro"], 1.0)
    santoor(st["explain"] + .4, st["explain"] + DUR["explain"] - .5, .5, .65, seed=33)
    add(sfx.dog_howl(4.0, 500, .8, seed=9), st["explain"] + 6.0, .6)
    santoor(st["outro"] + .2, st["outro"] + DUR["outro"] - 1.0, .45, .55, seed=35)
    add(sfx.dog_howl(4.0, 540, .85, seed=11), st["outro"] + 3.5, -.5)
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
