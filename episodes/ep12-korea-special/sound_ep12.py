"""Ep12 SPECIAL South Korea / Cheonyeo Gwishin sound: fluorescent buzz and clunks, a hummed folk melody (Arirang, traditional),
school chime, ticking clock, CCTV hum and glitches, drips, a sliding iron gate, gayageum-like plucks, dogs; scares from toolkit/sfx.py."""
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



# ---------------------------------------------------------------- ep12 sounds
KPENTA = [293.7, 329.6, 392.0, 440.0, 493.9, 587.3, 659.3]          # D E G A B (Korean pentatonic feel)
def gayageum(t0, t1, g=1.0, per=.6, seed=0):
    """Plucked silk strings with a bent tail (nonghyeon), slow and sparse."""
    r = np.random.default_rng(seed); t = t0; k = 3
    while t < t1:
        k = int(np.clip(k + r.choice([-2, -1, 1, 1, 2]), 0, len(KPENTA) - 1))
        add(plk(KPENTA[k], g), t, r.uniform(-.5, .5))
        if r.random() < .3:
            add(plk(KPENTA[k] * 1.06, g * .35), t + .25, r.uniform(-.5, .5))
        t += per * r.choice([1, 1, 2, 1.5])
# Arirang (traditional folk song, public domain): the opening phrase, hummed.
ARIRANG = [(392, .9), (392, .45), (440, .45), (392, .9), (440, .45), (493.9, .45), (587.3, .9), (493.9, .45), (440, .45),
           (392, .9), (440, .45), (392, .45), (329.6, .9), (293.7, 1.6)]
def hum(g=1.0, speed=1.0, detune=1.0):
    """A girl humming 'mmm': glottal pulse train with vibrato through nasal formants, lots of room."""
    out = []
    for f, d in ARIRANG:
        n = int(d * 1.35 / speed * SR); x = np.arange(n) / SR
        ff = f * detune * (1 + .012 * np.sin(2 * np.pi * 5.2 * x)) * (1 - .015 * np.exp(-x * 9))
        ph = 2 * np.pi * np.cumsum(ff) / SR
        src = sum(np.sin(h * ph) / h ** 1.3 for h in range(1, 14))
        v = bp(src, 180, 380) * 1.0 + bp(src, 2200, 2900) * .25 + lp(src, .08) * .3
        v *= env(n, .06, .18)
        out.append(v)
    s = np.concatenate(out)
    s = s / (np.abs(s).max() + 1e-9)
    return verb(s * .1 * g, .7)
_HUM = {}
def humming(t0, g=1.0, pan=0.0, dist=0.0, cut_at=None):
    key = round(dist, 2)
    if key not in _HUM:
        h = hum(1.0, 1.0, 0.985)
        if dist > 0:
            h = lp(h, max(.05, .6 - .5 * dist))
        _HUM[key] = h
    h = _HUM[key].copy()
    if cut_at is not None:
        i = int((cut_at - t0) * SR)
        if 0 < i < len(h):
            h[i:] = 0; h[max(0, i - 200):i] *= np.linspace(1, 0, min(200, i))
    add(h * g, t0, pan)
def tick(g=1.0):
    n = int(.05 * SR); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * x) * .5 + bp(rng.standard_normal(n), 2000, 7000) * .5) * np.exp(-x * 160) * .12 * g
def ticking(t0, t1, g=1.0, per=1.0):
    t = t0; k = 0
    while t < t1:
        add(tick(g * (1 if k % 2 == 0 else .7)), t, .25 if k % 2 else -.25); t += per; k += 1
def chime(g=1.0):
    """School chime: the four-note Westminster quarters, played on soft bells."""
    notes = [329.6, 261.6, 293.7, 196.0]
    o = np.zeros(int(5.5 * SR))
    for k, f in enumerate(notes):
        n = int(2.4 * SR); x = np.arange(n) / SR
        s = sum(a * np.sin(2 * np.pi * f * m * x) * np.exp(-x * dd) for m, a, dd in ((1, 1, 1.4), (2.0, .4, 2.2), (2.76, .2, 3), (4.07, .1, 4)))
        i = int(k * .75 * SR); o[i:i + n] += s * np.minimum(1, x / .004)
    return verb(lp(o, .4) * .07 * g, .6)
def buzz(t0, t1, g=1.0, offs=()):
    """Fluorescent tube hum (120 Hz + harmonics) that drops a step every time a tube dies."""
    n = int((t1 - t0) * SR); x = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * 120 * h * x) / h for h in range(1, 9))
    s = bp(s, 100, 3000) * (1 + .3 * (rng.random(n) > .995))
    lvl = np.ones(n)
    for k, o in enumerate(offs):
        lvl[int(o * SR):] = max(0, 1 - (k + 1) / len(offs))
    add(s * lp(lvl, .01) * .03 * g, t0)
def clunk(g=1.0):
    n = int(.6 * SR); x = np.arange(n) / SR
    return verb((np.sin(2 * np.pi * (90 - 40 * x) * x) * np.exp(-x * 18) * .6 + bp(rng.standard_normal(n), 800, 4000) * np.exp(-x * 70) * .4) * g * .5, .5)
def cctv_hum(t0, dur, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * 60 * h * x) / h for h in (1, 2, 3, 5)) * .02 + bp(rng.standard_normal(n), 3000, 9000) * .02
    add(s * env(n, .02, .05) * g, t0)
def drip(g=1.0):
    n = int(.5 * SR); x = np.arange(n) / SR
    f = 900 + 900 * np.exp(-x * 40)
    return verb(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 30) * .12 * g, .7)
def gate_roll(dur, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    am = .6 + .4 * np.abs(np.sin(2 * np.pi * 7 * x + 2 * np.sin(2 * np.pi * .9 * x)))
    s = bp(rng.standard_normal(n), 1400, 4200) * am * .25 + lp(rng.standard_normal(n), .01) * 1.5
    sq = np.sin(2 * np.pi * np.cumsum(2600 + 300 * np.sin(2 * np.pi * .7 * x)) / SR) * (np.sin(2 * np.pi * .5 * x) > .7) * .04
    return (s + sq) * env(n, .1, .2) * .4 * g
def clang(g=1.0):
    n = int(3 * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * x) * np.exp(-x * d) for f, a, d in ((310, 1, 1.5), (697, .7, 2), (1180, .5, 3), (1903, .35, 4), (2870, .2, 6)))
    s += bp(rng.standard_normal(n), 1000, 6000) * np.exp(-x * 40) * .6
    return verb(s * np.minimum(1, x / .002) * .12 * g, .5)
def rewind(dur=1.2, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 600 + 2400 * ((x * 5) % 1)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 + bp(rng.standard_normal(n), 2000, 8000) * .4
    return s * env(n, .02, .1) * .12 * g
def run_steps(t0, t1, g=1.0, per=.28, pan=0.0):
    t = t0
    while t < t1:
        n = int(.16 * SR); x = np.arange(n) / SR
        s = np.sin(2 * np.pi * (110 - 40 * x / .16) * x) * np.exp(-x * 30) * .5 + bp(rng.standard_normal(n), 1500, 6000) * np.exp(-x * 60) * .3
        add(verb(s * g, .4), t, pan + rng.uniform(-.1, .1)); t += per * rng.uniform(.95, 1.05)
def latch(g=1.0):
    n = int(.3 * SR); x = np.arange(n) / SR
    return (bp(rng.standard_normal(n), 1500, 7000) * np.exp(-x * 80) + np.sin(2 * np.pi * 1700 * x) * np.exp(-x * 60) * .5) * .3 * g
def jump(t, g=1.0):
    scare(t, g); add(shriek(1.0, .8 * g), t + .02)

LV = dict(hook=.8, school=.3, rule=.3, hall=.7, camera=.6, mistake=.8, cliff=.9,
          recap=.6, stall=.9, escape=.7, gate=.5, twist=.6, home=.7, explain=.3, outro=.25)
WIND = dict(hook=.8, school=.6, rule=0, hall=.1, camera=0, mistake=.1, cliff=0, recap=.4, stall=0, escape=.1, gate=.7, twist=.2, home=.2, explain=.5, outro=.4)
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
SIL = []
if PART == "p1":
    # hook: dogs, far humming, slam into the window on "don't look back"
    add(sfx.dog_pack(7.0, .7, 1.0), st["hook"] + .1)
    humming(st["hook"] + 1.0, .55, .5, dist=.6)
    h3 = cap("hook", 2)
    SIL.append((h3 - .35, h3))
    add(sfx.sub_drop(2.0, 1.0), h3); add(sfx.glitch(.4, .7), h3); add(sfx.braam(2.5, .7), h3); add(sfx.reverse_whisper(1.6, .8), h3 + .4, -.4)
    # school: chime, steps, the ticking clock from the moment the pill appears
    add(chime(1.0), st["school"] + .2, -.2)
    footsteps(st["school"] + .3, st["school"] + DUR["school"], .55, .6)
    ticking(cap("school", 1) - .2, st["school"] + DUR["school"], 1.0)
    gayageum(cap("school", 2), st["school"] + DUR["school"], .4, .6, seed=3)
    add(sfx.dog_howl(4.0, 520, .8, seed=21, g=.6), st["school"] + 4.0, .6)
    # rule: plucks, whisper, a far shape appears on "keep your eyes down"
    gayageum(st["rule"] + .3, cap("rule", 2), .5, .7, seed=5)
    add(sfx.reverse_whisper(1.6, .8), cap("rule", 2) - .2, .6)
    add(sfx.dissonant_strings(4.0, .45), cap("rule", 2))
    # hall: tubes die one by one, howls, then the humming at the end of the hall
    offs = [.8, 1.6, 2.4, 3.2]
    buzz(st["hall"], st["hall"] + 3.4, 1.0, offs)
    for o in offs: add(clunk(.9), st["hall"] + o, (o - 2) * .3)
    add(sfx.dog_pack(6.0, .75, .9), cap("hall", 1) - .2)
    hs = cap("hall", 2) - .3
    humming(hs, 1.0, .1, dist=.35)
    add(sfx.heartbeat_accel(st["hall"] + DUR["hall"] - hs + 1, .9, .6, .7), hs)
    # camera: CCTV hum, a glitch + hit at every cut, the beat speeds up
    cctv_hum(st["camera"], DUR["camera"], 1.0)
    c2, c3 = C["camera"][1][1], C["camera"][2][1]
    for k, ct in enumerate((c2 - .3, c2 + 1.6, c3 - .2, c3 + 1.0)):
        add(sfx.glitch(.35, .6 + .1 * k), st["camera"] + ct, .2); add(thud(.4 + .15 * k), st["camera"] + ct)
    add(sfx.pulse_beat(DUR["camera"], 80, 140, .6), st["camera"])
    humming(st["camera"] + .3, .35, -.3, dist=.5)
    # mistake: running, the talisman flutters down, her whisper, he looks back -> silence -> face
    run_steps(st["mistake"], cap("mistake", 2) + .3, .9, .27)
    add(flutter(1.2, 1.0), st["mistake"] + 1.2, -.4)
    add(whisper("Ji-ho...", g=1.1), cap("mistake", 1) + .1, .3)
    sc = cap("mistake", 2) + .5
    add(sfx.riser(1.2, .8), sc - 1.4)
    SIL.append((sc - .4, sc))
    jump(sc, 1.2)
    # cliff: latch, breath, drips; the humming comes close and STOPS on "right outside his door"
    add(latch(1.0), st["cliff"] + .2)
    breath(st["cliff"] + .6, cap("cliff", 2) + 1.0, .9, 1.3)
    tdp = st["cliff"]
    while tdp < st["cliff"] + DUR["cliff"] - 1.6:
        add(drip(1.0), tdp + 1.0, -.4); tdp += 1 / .7
    hs = st["cliff"] + .3
    stop = cap("cliff", 1) + 1.0
    humming(hs, 1.1, 0.0, dist=0.0, cut_at=stop)
    add(sfx.heartbeat_accel(st["cliff"] + DUR["cliff"] - stop, .9, .45, 1.1), stop + .3)
    add(sfx.dissonant_strings(5.0, .5), cap("cliff", 2))
    cut = st["cliff"] + DUR["cliff"] - 1.5
    cctv_hum(cut, 1.5, 1.2)
    add(sfx.riser(1.4, 1.0), cut - 1.3)
    SIL.append((cut - .35, cut))
    add(sfx.glitch(.3, .9), cut + .55)
    jump(cut + .62, 1.3)
else:
    add(sfx.sub_drop(2.0, .7), st["recap"] + .05)
    humming(st["recap"] + .3, .5, .4, dist=.5)
    add(sfx.dog_howl(4.2, 520, .7, seed=7), st["recap"] + 1.0, -.5)
    add(latch(.8), cap("recap", 1) - .1)
    # stall: drips on the words, hair slithering in, jolt at the end
    add(drip(1.3), cap("stall", 0) + .05, -.3); add(drip(1.3), cap("stall", 0) + .7, .3)
    sl0 = cap("stall", 1) - .3
    add(rustle(st["stall"] + DUR["stall"] - sl0, 1.6), sl0, 0.0)
    add(sfx.heartbeat_accel(st["stall"] + DUR["stall"] - sl0, .8, .4, 1.0), sl0)
    add(sfx.pulse_beat(DUR["stall"], 70, 130, .5), st["stall"])
    jt = st["stall"] + DUR["stall"] - .45
    add(sfx.riser(1.2, .8), jt - 1.3); SIL.append((jt - .3, jt))
    add(sfx.braam(2.0, .9), jt); add(sfx.glitch(.4, .8), jt); add(sfx.sub_drop(2.0, .8), jt)
    # escape: running, breath, a whoosh on every floor
    run_steps(st["escape"] + .3, st["escape"] + DUR["escape"], 1.0, .27)
    breath(st["escape"] + .3, st["escape"] + DUR["escape"], 1.0, .5)
    add(sfx.pulse_beat(DUR["escape"], 110, 170, .6), st["escape"])
    add(sfx.reverse_whisper(1.6, .8), cap("escape", 1), .5)
    for k, o in enumerate((0, 1.0, 1.9)):
        add(whoosh(.8, 1.0), cap("escape", 2) + o, (-.4, .4, 0)[k])
    # gate: the iron gate rolling shut, ticking, clang, then the humming stops dead
    g0, g1 = st["gate"] + .5, cap("gate", 1) + 1.6
    add(gate_roll(g1 - g0, 1.0), g0, .3)
    add(clang(1.0), g1, .3)
    ticking(st["gate"], g1, 1.1, .5)
    run_steps(st["gate"] + .3, cap("gate", 1) + 1.6, .9, .27)
    hs = st["gate"] + .5
    humming(hs, .7, -.3, dist=.4, cut_at=cap("gate", 2) + .9)
    add(sfx.dog_pack(6.0, .75, .8), st["gate"] + 1.0)
    SIL.append((cap("gate", 2) + .9, cap("gate", 2) + 1.4))
    add(sfx.dissonant_strings(4.0, .5), cap("gate", 2) + 1.4)
    # twist: CCTV playback, footsteps, then she walks out -> face
    cctv_hum(st["twist"], DUR["twist"], 1.0)
    add(rewind(1.2, 1.0), st["twist"] + .1)
    add(sfx.dissonant_strings(4.0, .5), cap("twist", 2) + .4)
    add(sfx.heartbeat_accel(DUR["twist"] - (cap("twist", 2) - st["twist"]), .9, .45, .9), cap("twist", 2))
    jt = st["twist"] + DUR["twist"] - .75
    add(sfx.riser(1.6, 1.0), jt - 1.9)
    SIL.append((jt - .4, jt - .15))
    add(sfx.glitch(.3, .9), jt - .15)
    jump(jt, 1.2)
    # the bad ending: Ji-ho hums HER song by the window (she hums with him, faintly), then he turns
    add(pad(DUR["home"], (110, 146.8, 155.6), .025), st["home"])
    add(sfx.dog_howl(4.0, 480, .85, seed=13, g=.6), st["home"] + .6, -.6)
    hj = cap("home", 1) - .4
    boy = hum(1.0, .92, 0.5)
    tturn = st["home"] + DUR["home"] - 2.4
    i = int((tturn - .35 - hj) * SR)
    if 0 < i < len(boy):
        boy[i:] = 0
    add(boy * 1.1, hj, .1)
    humming(hj + .15, .45, -.2, dist=.3, cut_at=tturn - .35)
    add(sfx.heartbeat_accel(tturn - hj, .9, .55, .8), hj)
    add(sfx.riser(1.4, .8), tturn - 1.5)
    SIL.append((tturn - .35, tturn))
    add(sfx.braam(3.0, 1.1), tturn); add(sfx.sub_drop(2.0, 1.0), tturn); add(sfx.dissonant_strings(4.0, .7), tturn + .05)
    add(sfx.reverse_whisper(1.6, .9), tturn + .6, .4)
    # explain + outro: gayageum, a soft pad, far dogs, the hum one last time
    gayageum(st["explain"] + .4, st["explain"] + DUR["explain"] - .5, .5, .65, seed=33)
    add(pad(DUR["explain"] + DUR["outro"], (146.8, 220, 293.7), .02), st["explain"])
    add(sfx.dog_howl(4.0, 500, .8, seed=9), st["explain"] + 6.0, .6)
    gayageum(st["outro"] + .2, st["outro"] + DUR["outro"] - 1.0, .45, .55, seed=35)
    humming(st["outro"] + 2.5, .35, -.5, dist=.6)
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
