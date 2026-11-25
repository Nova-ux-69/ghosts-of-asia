"""Ep11 Vietnam / the Ma Da (2.1D survival) sound: canal water lapping, bamboo creaks, drips, frogs and crickets,
a dan bau-style monochord (one string, slow pitch bends) in a Vietnamese pentatonic scale, a child's whisper "help me...",
a wet giggle, a splash + underwater muffle, a night heron squawk (false scare), a pagoda bell and roosters at dawn;
scares from toolkit/sfx.py (Part 1) and a different kit in Part 2 (violin screech, choir stab, boom, reverse scream)."""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt
PART = sys.argv[1]; SR = 24000
T = json.load(open(f"{PART}/timing.json"))
st = {}; acc = 0
for s in T: st[s["id"]] = acc; acc += s["dur"]
TOT = acc; N = int(TOT * SR) + SR
rng = np.random.default_rng(111 if PART == "p1" else 112)
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

# ---- NEW (Nova 2026-11-25): a signature sound for the Chudail + a different scare kit for Part 2
from scipy.signal import resample
LAUGH = {}
def ghost_laugh(g=1.0):
    """Her laugh: a soft female 'hee hee hee', slowed and pitched down, doubled an octave lower, drowned in reverb,
    with a reversed swell leading into it."""
    if "x" not in LAUGH:
        try:
            from kokoro_onnx import Kokoro
            tk = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit", "models")
            k = Kokoro(os.path.join(tk, "kokoro.onnx"), os.path.join(tk, "voices.bin"))
            a, sr = k.create("Hee hee hee... hee hee...", voice="af_nicole", speed=0.8, lang="en-us")
            a = np.asarray(a, float)
            if sr != SR:
                a = resample(a, int(len(a) * SR / sr))
            slow = resample(a, int(len(a) * 1.25))                    # lower + slower
            low = resample(a, int(len(a) * 2.0))[:len(slow)] * .45    # an octave under it
            v = slow + np.pad(low, (0, max(0, len(slow) - len(low))))
            v = bp(v, 120, 6000)
            v = v / (np.abs(v).max() + 1e-9)
            wet = verb(v * .3, .85)
            pre = verb(v[::-1] * .15, .85)[::-1][-int(1.2 * SR):]
            LAUGH["x"] = np.concatenate([pre * np.linspace(0, 1, len(pre)), wet])
        except Exception as e:
            print("laugh failed", e); LAUGH["x"] = np.zeros(SR)
    return LAUGH["x"] * g
def bone_crack(g=1.0, n=6):
    """Joints twisting (her backward feet): a burst of dry cracks over a low knock."""
    o = np.zeros(int(1.2 * SR)); t = 0.0
    for k in range(n):
        m = int(.04 * SR); x = np.arange(m) / SR
        c = bp(rng.standard_normal(m), 1200, 7000) * np.exp(-x * 260) * rng.uniform(.5, 1)
        c += np.sin(2 * np.pi * rng.uniform(140, 260) * x) * np.exp(-x * 120) * .5
        i = int(t * SR); o[i:i + m] += c; t += rng.uniform(.03, .13)
    return verb(o * .45 * g, .35)
def moan(dur=2.6, g=1.0):
    """A low, hollow female moan ('ooooh') that sinks in pitch, with an octave-down shadow under it."""
    n = int(dur * SR); x = np.arange(n) / SR
    f = (230 - 70 * x / dur) * (1 + .02 * np.sin(2 * np.pi * 4.6 * x))
    ph = 2 * np.pi * np.cumsum(f) / SR
    src = sum(np.sin(h * ph) / h ** 1.2 for h in range(1, 16)) + .5 * sum(np.sin(h * ph / 2) / h ** 1.2 for h in range(1, 10))
    v = bp(src, 260, 380) + bp(src, 700, 950) * .6 + bp(rng.standard_normal(n), 300, 2000) * .15
    v *= env(n, .5, .9)
    return verb(v / (np.abs(v).max() + 1e-9) * .12 * g, .85)
def violin_screech(dur=1.2, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 1500 + 1100 * (x / dur) ** .5
    ph = 2 * np.pi * np.cumsum(f * (1 + .01 * np.sin(2 * np.pi * 9 * x))) / SR
    saw = sum(np.sin(h * ph) / h for h in range(1, 12)) + .7 * sum(np.sin(h * ph * 1.059) / h for h in range(1, 8))
    s = bp(saw + bp(rng.standard_normal(n), 2000, 9000) * .4, 900, 9000)
    return verb(s * env(n, .01, .5) * .09 * g, .5)
def metal_scrape(dur=3.0, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 1800, 6500) * (.5 + .5 * np.abs(np.sin(2 * np.pi * (3 + 4 * x / dur) * x)))
    s += sum(np.sin(2 * np.pi * f * x) * .15 for f in (2213, 3371, 4789)) * (.6 + .4 * np.sin(2 * np.pi * .7 * x))
    return verb(s * env(n, .4, .8) * .08 * g, .6)
def boom(g=1.0):
    n = int(3 * SR); x = np.arange(n) / SR
    s = np.sin(2 * np.pi * (55 - 20 * x / 3) * x) * np.exp(-x * 1.6) + lp(rng.standard_normal(n), .02) * np.exp(-x * 6) * 2
    return verb(s * .5 * g, .7)
def choir_stab(g=1.0):
    """A dissonant 'aah' cluster hit (minor second + tritone), short and loud."""
    n = int(2.2 * SR); x = np.arange(n) / SR; o = np.zeros(n)
    for f in (220, 233.1, 311.1, 329.6, 466.2):
        ph = 2 * np.pi * f * x * (1 + .006 * np.sin(2 * np.pi * 5 * x + f))
        src = sum(np.sin(h * ph) / h ** 1.3 for h in range(1, 10))
        o += bp(src, 600, 1300) + bp(src, 1000, 2600) * .5
    return verb(o * np.exp(-x * 1.5) * np.minimum(1, x / .01) * .05 * g, .8)
def reverse_scream(g=1.0, dur=1.4):
    s = shriek(dur, 1.0)[::-1]
    return s * np.linspace(0, 1, len(s)) ** 2 * g


# ---------------------------------------------------------------- ep11 sounds
VN = [293.7, 349.2, 392.0, 440.0, 523.3, 587.3, 698.5]       # D F G A C D' F' (Vietnamese-style pentatonic)
def danbau(f0, dur=2.4, bend=0.0, g=1.0):
    """Dan bau-like single string: soft harmonic tone with a slow pitch bend (bend in semitones) and vibrato."""
    n = int(dur * SR); x = np.arange(n) / SR
    b = 2 ** (bend * np.clip((x - .35) / .8, 0, 1) / 12)
    f = f0 * b * (1 + .012 * np.sin(2 * np.pi * 5.2 * x) * np.clip((x - .5), 0, 1))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + .35 * np.sin(2 * ph) + .12 * np.sin(3 * ph)
    s *= np.minimum(1, x / .015) * np.exp(-x * .9)
    return verb(s * .07 * g, .6)
def danbau_line(t0, t1, g=1.0, per=1.3, seed=0):
    r = np.random.default_rng(seed); t = t0; k = 3
    while t < t1 - .5:
        k = int(np.clip(k + r.choice([-2, -1, 1, 1, 2]), 0, len(VN) - 1))
        add(danbau(VN[k], 2.4, r.choice([0, 0, 2, -2, 3]), g), t, r.uniform(-.4, .4)); t += per * r.choice([1, 1, 1.5, .75])
def lapping(t0, t1, g=1.0):
    """Gentle water against bamboo legs and hulls: soft lowpassed noise with slow irregular swells."""
    n = int((t1 - t0) * SR); x = np.arange(n) / SR
    am = np.clip(np.sin(2 * np.pi * .45 * x + 2 * np.sin(2 * np.pi * .13 * x)), 0, 1) ** 2
    s = bp(rng.standard_normal(n), 150, 1200) * am * .12
    s += bp(rng.standard_normal(n), 1500, 4000) * am ** 3 * .03
    add(s * g, t0, -.2); add(np.roll(s, SR // 3) * g * .8, t0, .3)
def drip(g=1.0, f=None):
    n = int(.35 * SR); x = np.arange(n) / SR
    f = f or rng.uniform(900, 1500)
    s = np.sin(2 * np.pi * (f + 900 * np.exp(-x * 40)) * x) * np.exp(-x * 28)
    return verb(s * .12 * g, .45)
def drips(t0, t1, per=.7, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        add(drip(g), t, pan + rng.uniform(-.3, .3)); t += per * rng.uniform(.7, 1.3)
def splash(g=1.0, dur=1.2):
    n = int(dur * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 300, 6000) * np.exp(-x * 5) * np.minimum(1, x / .01)
    s += np.sin(2 * np.pi * (90 - 40 * x) * x) * np.exp(-x * 9) * .5
    return verb(s * .35 * g, .4)
def bubbles(t0, t1, g=1.0):
    t = t0
    while t < t1:
        n = int(.08 * SR); x = np.arange(n) / SR
        f = rng.uniform(300, 900) * (1 + 2 * x / .08)
        add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * x / .08) * .05 * g, t, rng.uniform(-.5, .5)); t += rng.uniform(.04, .25)
def bamboo_creak(g=1.0):
    return creak(rng.uniform(.6, 1.2), 1.6 * g)
def heron_squawk(g=1.0):
    """'KWOK!' - a harsh nasal bark, twice."""
    o = np.zeros(int(1.0 * SR))
    for k, st_ in enumerate((0.0, .32)):
        n = int(.22 * SR); x = np.arange(n) / SR
        f = 520 - 200 * x / .22
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = bp(sum(np.sin(h * ph) / h for h in range(1, 12)) + rng.standard_normal(n) * .4, 400, 4000) * env(n, .01, .08)
        i = int(st_ * SR); o[i:i + n] += s
    return verb(o * .3 * g, .45)
def rooster(g=1.0):
    n = int(1.6 * SR); x = np.arange(n) / SR
    f = np.interp(x, [0, .2, .4, .9, 1.6], [500, 760, 700, 820, 560])
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = bp(sum(np.sin(h * ph) / h for h in range(1, 8)), 400, 4000) * env(n, .03, .4)
    return verb(s * .03 * g, .5)
def flick(g=1.0):
    n = int(.5 * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 2000, 8000) * np.exp(-x * 60) * .5 + bp(rng.standard_normal(n), 300, 1500) * np.exp(-x * 4) * .08
    return s * g
def muffle(a, b):
    """Underwater: lowpass everything between a and b (plus a little before/after)."""
    global L, R
    i, j = int(a * SR), int(b * SR)
    for ch in (L, R):
        seg = ch[i:j].copy()
        ch[i:j] = lfilter([.06], [1, -.94], seg) * 2.2
GIG = {}
def giggle(g=1.0):
    """A wet little-girl giggle, slowed, with an octave-down shadow and long reverb."""
    if "x" not in GIG:
        try:
            from kokoro_onnx import Kokoro
            tk = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit", "models")
            k = Kokoro(os.path.join(tk, "kokoro.onnx"), os.path.join(tk, "voices.bin"))
            a, sr = k.create("Hee hee hee hee...", voice="af_sky", speed=0.9, lang="en-us")
            a = np.asarray(a, float)
            if sr != SR: a = resample(a, int(len(a) * SR / sr))
            slow = resample(a, int(len(a) * 1.15)); low = resample(a, int(len(a) * 1.9))[:len(slow)] * .35
            v = slow + np.pad(low, (0, max(0, len(slow) - len(low))))
            v = bp(v, 150, 6500); v = v / (np.abs(v).max() + 1e-9)
            pre = verb(v[::-1] * .15, .85)[::-1][-int(1.0 * SR):]
            GIG["x"] = np.concatenate([pre * np.linspace(0, 1, len(pre)), verb(v * .3, .85)])
        except Exception as e:
            print("giggle failed", e); GIG["x"] = np.zeros(SR)
    return GIG["x"] * g

LV = dict(hook=.8, bridge=.3, rule=.15, water=.7, voice=.8, mistake=.85, cliff=.9, recap=.6, boat=.85, eyes=.6, shrine=.5, twist=.25, explain=.3, outro=.25)
WIND = dict(hook=.5, bridge=.5, rule=0, water=.4, voice=.3, mistake=.2, cliff=.15, recap=.15, boat=.15, eyes=.4, shrine=.5, twist=.05, explain=.35, outro=.3)
NIGHT = dict(hook=.5, bridge=.6, rule=0, water=.3, voice=0, mistake=0, cliff=.2, recap=.2, boat=0, eyes=.4, shrine=.3, twist=0, explain=.4, outro=.4)
WATER = dict(hook=.9, bridge=.8, rule=0, water=.9, voice=1.0, mistake=1.0, cliff=.9, recap=.9, boat=1.0, eyes=.9, shrine=.4, twist=0, explain=.7, outro=.7)
def curve(Dd, a):
    c = np.zeros(N)
    for s in T: c[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = Dd[s["id"]]
    c[int(TOT * SR):] = c[int(TOT * SR) - 1]
    return lp(c, a)
lvl, wl = curve(LV, .0006), curve(WIND, .0004)
drone = ((np.sin(2*np.pi*36.7*tt) + .5*np.sin(2*np.pi*55*tt) + .3*np.sin(2*np.pi*73.4*tt + np.sin(2*np.pi*.17*tt))) * .05
         + lp(rng.standard_normal(N), .008) * .22) * lvl
wmod = .6 + .4 * np.sin(2*np.pi*.07*tt) * np.sin(2*np.pi*.19*tt + 1)
windL = bp(rng.standard_normal(N), 200, 1500) * .07 * wmod; windR = bp(rng.standard_normal(N), 220, 1600) * .07 * wmod[::-1]
L += drone + windL * wl; R += drone + windR * wl
for s in T:
    a0, a1 = st[s["id"]], st[s["id"]] + s["dur"]
    if NIGHT[s["id"]] > 0:
        crickets(a0, a1, NIGHT[s["id"]] * .8); frogs(a0, a1, NIGHT[s["id"]] * 1.2)
    if WATER[s["id"]] > 0:
        lapping(a0, a1, WATER[s["id"]])
SIL = []
if PART == "p1":
    add(sfx.dog_pack(7.0, .7, 1.0), st["hook"] + .1)
    danbau_line(st["hook"] + .3, cap("hook", 1) - .2, .8, 1.1, seed=1)
    add(sfx.reverse_whisper(1.6, .8), st["hook"] + 2.2, .5)
    cut = cap("hook", 1) - .15
    SIL.append((cut - .3, cut))
    add(splash(.9), cut); add(sfx.sub_drop(2.0, .9), cut); add(sfx.glitch(.4, .6), cut); add(whisper("help me...", voice="af_sky", g=.7), cut + .2, .2)
    drips(cut + .2, st["hook"] + DUR["hook"], .35, .9)
    t_ = st["bridge"] + .2
    while t_ < st["bridge"] + DUR["bridge"]:
        add(sand_step(.5), t_, -.1); t_ += .62
        if rng.random() < .45: add(bamboo_creak(.8), t_ - .1, rng.uniform(-.5, .5))
    danbau_line(st["bridge"] + .6, st["bridge"] + DUR["bridge"] - .3, .5, 1.4, seed=3)
    add(sfx.dog_howl(4.0, 520, .8, seed=21, g=.6), st["bridge"] + 2.0, .6)
    add(splash(.25), st["bridge"] + 3.4, .7)
    for k in range(4): add(beep(.8), cap("bridge", 2) - .1 + k * .7, .2)
    add(pad(DUR["rule"], (146.8, 220, 293.7), .02), st["rule"])
    for k in range(4): add(danbau(VN[[4, 3, 1, 0][k]], 2.4, [0, -2, 0, 2][k], .9), st["rule"] + .6 + k * 2.2)
    add(sfx.reverse_whisper(1.6, .8), cap("rule", 2) - .4, -.3)
    add(sfx.dog_pack(4.0, .7, .9), st["water"])
    SIL.append((cap("water", 0, 2) - .5, cap("water", 0, 2) - .1))           # the dogs stop dead
    t_ = st["water"] + .3
    while t_ < st["water"] + DUR["water"]:
        add(sand_step(.4), t_, -.1); add(bamboo_creak(.7), t_ + .1, .3); t_ += 1.1
    add(sfx.pulse_beat(DUR["water"] - 2, 70, 110, .5), st["water"] + 2)
    add(sfx.heartbeat_accel(DUR["water"] + DUR["voice"], .95, .5, .7), cap("water", 1))
    add(moan(2.8, .6), cap("water", 1) + .3, .5); add(sfx.dissonant_strings(4.0, .45), cap("water", 2))
    bubbles(cap("water", 1), st["water"] + DUR["water"], .8)
    add(whisper("help me... help me...", voice="af_sky", g=1.0), cap("voice", 0) + 1.0, .3)
    bubbles(cap("voice", 1) - .2, st["voice"] + DUR["voice"], 1.0)
    add(sfx.riser(1.2, .6), st["mistake"] + .6)
    g1 = cap("mistake", 1) - .1
    SIL.append((g1 - .35, g1))
    add(splash(1.2), g1); add(sfx.braam(2.0, .7), g1); add(sfx.sub_drop(2.0, .8), g1); add(giggle(.6), g1 + .4, .3)
    add(sfx.heartbeat_accel(DUR["mistake"] - (g1 - st["mistake"]), .7, .45, .9), g1 + .3)
    s2 = cap("mistake", 2) - .1
    add(splash(.8), s2 + .05)
    bubbles(s2, st["mistake"] + DUR["mistake"], 1.4)
    add(sfx.dissonant_strings(4.0, .6), s2 + .5); add(choir_stab(.5), s2 + 1.6)
    muffle(s2 + .1, st["mistake"] + DUR["mistake"] - .05)
    t0c = st["cliff"]
    add(splash(.6), t0c + .1); t_ = t0c
    for k in range(4): add(stone_step(.6), t0c + .1 + k * .22, -.3)
    drips(t0c + 1.2, t0c + DUR["cliff"] - 1.2, .5, 1.1, .2)
    c1 = cap("cliff", 1)
    beat_t = c1 - .2
    while beat_t < cap("cliff", 2):
        add(slap(.3), beat_t, .4); add(drip(.9, 1100), beat_t + .05, .4); beat_t += .6
    add(giggle(.5), cap("cliff", 1, 2) - .2, .5)
    m0, m1 = c1 + .5, st["cliff"] + DUR["cliff"]
    m = np.ones(N); m[int(m0 * SR):int(m1 * SR)] = .5; m = lp(m, .0008); L *= m; R *= m
    jt = st["cliff"] + C["cliff"][2][2] + .15
    add(sfx.heartbeat_accel(jt - m0, .9, .45, 1.1), m0)
    add(sfx.pulse_beat(jt - c1, 80, 150, .6), c1)
    add(sfx.dissonant_strings(5.0, .5), cap("cliff", 2))
    add(sfx.riser(1.6, 1.0), jt - 1.75)
    SIL.append((jt - .4, jt))
    scare(jt, 1.2); add(splash(1.0), jt + .02)
else:
    add(sfx.sub_drop(2.0, .7), st["recap"] + .05)
    drips(st["recap"] + .3, st["recap"] + DUR["recap"], .45, 1.0, .3)
    add(sfx.dog_howl(4.2, 520, .7, seed=7), st["recap"] + 1.0, -.5)
    add(bamboo_creak(1.2), st["boat"] + .05, .2); add(thud(.8), st["boat"] + .05); add(splash(.7), st["boat"] + .1, .4)
    for k in range(3): add(bamboo_creak(1.0), st["boat"] + .8 + k * .9, (-.3, .4, -.1)[k])
    add(sfx.pulse_beat(DUR["boat"], 80, 140, .6), st["boat"])
    gc = cap("boat", 1) - .1
    SIL.append((gc - .4, gc))
    add(giggle(1.1), gc + .1, .7)
    hit = st["boat"] + C["boat"][1][2] + .15
    SIL.append((hit - .15, hit))
    add(violin_screech(1.2, 1.1), hit); add(boom(1.0), hit); add(splash(.8), hit + .05)
    add(pad(cap("eyes", 2) - st["eyes"], (146.8, 174.6, 220), .02), st["eyes"])
    add(sfx.heartbeat_accel(cap("eyes", 2) - st["eyes"], .8, .5, .8), st["eyes"])
    add(glass_clink(1.2), st["eyes"] + 1.0); add(metal_scrape(3.0, .6), cap("eyes", 1) - .2, -.3)
    for k in range(6): add(splash(.25), cap("eyes", 1) + k * .5, -.5)
    jp = cap("eyes", 2) - .1
    add(whoosh(.8, 1.0), jp); add(thud(.7), jp + .9)
    walking(jp + 1.0, st["eyes"] + DUR["eyes"], .26, .9, jingle=False)
    add(heron_squawk(1.3), st["shrine"] + .35, -.4); add(flutter(1.4, 1.2), st["shrine"] + .35, -.2); add(sfx.braam(1.4, .4), st["shrine"] + .35)
    walking(st["shrine"], cap("shrine", 1) - .1, .26, 1.0, jingle=False)
    t_ = st["shrine"] + .2
    while t_ < cap("shrine", 2) - .1:
        add(splash(.12), t_, -.6); t_ += .6
    breath(st["shrine"], cap("shrine", 1), 1.0, .5)
    add(sfx.pulse_beat(cap("shrine", 2) - st["shrine"], 110, 160, .6), st["shrine"])
    add(flick(1.0), cap("shrine", 1) + .4); add(flick(1.0), cap("shrine", 1) + .9)
    dw = cap("shrine", 2)
    SIL.append((dw - .3, dw))
    for k in range(3): add(big_bell(1.0 - .25 * k), dw + k * 1.6, -.2)
    add(rooster(1.0), dw + 1.4, .6); add(rooster(.7), dw + 3.0, -.7)
    birds(dw + 1.0, st["twist"] + DUR["twist"] - 1.5, 1.0)
    add(pad(DUR["twist"], (146.8, 185, 220), .018), st["twist"])
    for k in range(6): add(splash(.18), st["twist"] + .4 + k * .55, .1)
    drips(cap("twist", 1), st["twist"] + DUR["twist"] - 1.2, .55, 1.0)
    add(metal_scrape(4.0, .6), cap("twist", 2) - .2, .3)
    add(sfx.heartbeat_accel(DUR["twist"] - (cap("twist", 2) - st["twist"]), .9, .45, .9), cap("twist", 2))
    add(giggle(.6), cap("twist", 2) + 1.2, .4)
    jt = st["twist"] + DUR["twist"] - 1.0
    rs = reverse_scream(1.0, 1.4)
    add(rs, jt - len(rs) / SR)
    SIL.append((jt - .12, jt - .02))
    add(choir_stab(1.2), jt); add(boom(1.2), jt); add(violin_screech(1.0, .9), jt + .02); add(splash(.9), jt)
    add(pad(DUR["explain"] + DUR["outro"], (146.8, 220, 293.7), .02), st["explain"])
    danbau_line(st["explain"] + .4, st["explain"] + DUR["explain"] - .5, .6, 1.3, seed=33)
    add(sfx.dog_howl(4.0, 500, .8, seed=9), st["explain"] + 6.0, .6)
    danbau_line(st["outro"] + .2, st["outro"] + DUR["outro"] - 1.0, .55, 1.2, seed=35)
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
