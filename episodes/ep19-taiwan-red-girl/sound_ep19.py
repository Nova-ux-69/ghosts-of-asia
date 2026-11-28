"""Ep19 Taiwan / the little girl in red (2.1D survival) sound - sfx2 kit (Nova 2026-11-27) with a new Taiwanese colour:
an erhu-like bowed line in the Chinese gong pentatonic, a temple muyu woodblock as the ticking clock, a small
shrine bell, evening mountain cicadas that STOP dead, wind through the tree ferns, stone steps, the home-video tape
whirr, a child's voice counting "one... two... three... four", Grandpa's voice in the fog that isn't Grandpa, a child
whispering "Mei... come and play with me", and a full string of firecrackers (crackle + big bangs) for the escape;
breathing/whispering choir bed under everything (sfx.bed). Part 1 scares: sfx2 braam/taiko/metal + tape-stops;
Part 2: the violin/choir/boom kit + metal hits. Utility functions are shared with ep16/ep17."""
import json, sys, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt
PART = sys.argv[1]; SR = 24000
T = json.load(open(f"{PART}/timing.json"))
st = {}; acc = 0
for s in T: st[s["id"]] = acc; acc += s["dur"]
TOT = acc; N = int(TOT * SR) + SR
rng = np.random.default_rng(191 if PART == "p1" else 192)
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
import sfx2 as sfx   # NEW sound kit (Nova 2026-11-27)
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


# ---------------------------------------------------------------- ep13 sounds
MIYAKO = [293.7, 311.1, 392.0, 440.0, 466.2, 587.3, 622.3, 784.0]      # D Eb G A Bb D' Eb' G' (miyako-bushi)
def koto_line(t0, t1, g=1.0, per=1.1, seed=0):
    r = np.random.default_rng(seed); t = t0; k = 4
    while t < t1:
        k = int(np.clip(k + r.choice([-2, -1, -1, 1, 2]), 0, len(MIYAKO) - 1))
        add(plk(MIYAKO[k], g), t, r.uniform(-.5, .5)); t += per * r.choice([1, 1, 1.5, .5])
def tine(f, g=1.0, dur=2.4):
    n = int(dur * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*f*x) * np.exp(-x*2.2) + .35*np.sin(2*np.pi*f*3.98*x) * np.exp(-x*6) + .15*np.sin(2*np.pi*f*7.1*x)*np.exp(-x*12)
    s *= np.minimum(1, x / .002)
    return verb(s * .05 * g, .55)
def music_box(t0, t1, g=1.0, seed=0, slow=1.0):
    """A slightly detuned music box playing a little lullaby in miyako-bushi, slowing down like it's running out."""
    tune = [5, 4, 3, 4, 5, 5, 5, -1, 4, 3, 2, 3, 4, -1, 2, 3, 4, 5, 3, 2, 1, -1]
    t = t0; i = 0; per = .42
    while t < t1:
        k = tune[i % len(tune)]
        if k >= 0:
            add(tine(MIYAKO[k] * 2 * (1 + .004 * np.sin(i)), g), t, .2 * np.sin(i))
        t += per; per *= 1.0 + .012 * slow; i += 1
def higurashi(t0, t1, g=1.0, seed=0):
    """Evening cicadas: bursts of fast 'kana-kana-kana' trills that fall in pitch, from several trees."""
    r = np.random.default_rng(seed)
    for v in range(3):
        t = t0 + r.uniform(0, 1.5)
        while t < t1 - .5:
            dur = min(r.uniform(2.0, 3.2), t1 - t)
            n = int(dur * SR); x = np.arange(n) / SR
            f0 = r.uniform(4200, 5200)
            f = f0 * (1 - .12 * x / dur)
            car = np.sin(2*np.pi*np.cumsum(f)/SR) + .3*np.sin(2*np.pi*np.cumsum(f*1.5)/SR)
            am = np.clip(np.sin(2*np.pi*(14 - 4*x/dur)*x), 0, 1) ** 2
            e = np.exp(-x * 1.1) * np.minimum(1, x / .05)
            add(car * am * e * .022 * g, t, r.uniform(-.8, .8)); t += dur + r.uniform(1.0, 2.5)
def crow(g=1.0, n_=2):
    o = np.zeros(int(1.6 * SR))
    for k in range(n_):
        n = int(.32 * SR); x = np.arange(n) / SR
        f = 560 - 160 * x / .32
        src = sum(np.sign(np.sin(h * 2*np.pi*np.cumsum(f)/SR)) / h for h in (1, 2, 3))
        s = (bp(src, 700, 2400) + bp(rng.standard_normal(n), 900, 3000) * .6) * np.sin(np.pi * x / .32) ** .6
        i = int(k * .45 * SR); o[i:i + n] += s
    return verb(o * .07 * g, .5)
def wood_knock(g=1.0):
    n = int(.35 * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*(170 - 40*x)*x) * np.exp(-x*30) * .8 + bp(rng.standard_normal(n), 400, 2500) * np.exp(-x*70) * .6
    s += np.sin(2*np.pi*95*x) * np.exp(-x*18) * .4
    return verb(s * .7 * g, .35)
def tap(g=1.0):
    n = int(.2 * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 1800, 6000) * np.exp(-x*90) * .6 + np.sin(2*np.pi*(320 - 80*x)*x) * np.exp(-x*45) * .4
    return verb(s * .4 * g, .45)
def door_creak(dur=1.8, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 110 + 90 * np.sin(np.pi * x / dur) + 25 * np.sin(2*np.pi*3*x)
    s = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)) * (.5 + .5*np.sin(2*np.pi*23*x)) ** 2
    return verb(bp(s, 250, 3000) * env(n, .08, .3) * .09 * g, .4)
def bulb_buzz(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); x = np.arange(n) / SR
    s = (np.sin(2*np.pi*100*x) + .5*np.sin(2*np.pi*200*x) + .25*np.sign(np.sin(2*np.pi*100*x))) * .012
    cr = (rng.random(n) > .9996).astype(float); cr = lfilter([1], [1, -.97], cr) * bp(rng.standard_normal(n), 2000, 8000) * .3
    add((s * (.7 + .3 * (np.sin(2*np.pi*.9*x) > -.6)) + cr) * g, t0, .1)
def chalk(dur=1.5, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    strokes = np.clip(np.sin(2*np.pi*3.2*x + 2*np.sin(2*np.pi*.7*x)), 0, 1) ** .5
    s = bp(rng.standard_normal(n), 2500, 7000) * strokes * .25
    sq = np.sin(2*np.pi*np.cumsum(2900 + 300*np.sin(2*np.pi*5*x))/SR) * (np.sin(2*np.pi*1.1*x) > .85) * .08
    return (s + sq) * env(n, .02, .1) * g
def clunk(g=1.0):
    n = int(.8 * SR); x = np.arange(n) / SR
    return verb((np.sin(2*np.pi*(80 - 20*x)*x) * np.exp(-x*14) + bp(rng.standard_normal(n), 300, 3000) * np.exp(-x*60) * .5) * .6 * g, .5)
def hum(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); x = np.arange(n) / SR
    add((np.sin(2*np.pi*50*x) * .02 + np.sin(2*np.pi*150*x) * .006) * g, t0)


# ============================================================ ep14: new sounds
def sunshower(t0, t1, g=1.0):
    """Rain from a clear sky: soft hiss on leaves + random drips/ticks on bamboo leaves."""
    n = int((t1 - t0) * SR); x = np.arange(n) / SR
    e = np.minimum(1, x / 1.5) * np.minimum(1, (x[-1] - x) / 1.0 + 1e-3)
    hiss = bp(rng.standard_normal(n), 1500, 9000) * .05 + bp(rng.standard_normal(n), 300, 1500) * .025
    ticks = (rng.random(n) > .9985).astype(float)
    ticks = lfilter([1], [1, -.9], ticks) * bp(rng.standard_normal(n), 2500, 8000) * .25
    add((hiss + ticks) * e * g, t0, -.2); add((bp(rng.standard_normal(n), 1500, 9000) * .045) * e * g, t0, .3)
def bamboo_tok(g=1.0, f=None):
    """Two bamboo culms knocking together in the wind: a hollow woody resonance."""
    f = f or rng.uniform(380, 720); n = int(.5 * SR); x = np.arange(n) / SR
    s = (np.sin(2*np.pi*f*x) + .4*np.sin(2*np.pi*f*2.7*x)) * np.exp(-x*22) + bp(rng.standard_normal(n), 800, 3000) * np.exp(-x*90) * .3
    return verb(s * .18 * g, .45)
def bamboo_knocks(t0, t1, every=1.4, g=1.0):
    t = t0
    while t < t1:
        k = rng.integers(1, 3)
        for j in range(k): add(bamboo_tok(g * rng.uniform(.5, 1.0)), t + j * .12, rng.uniform(-.8, .8))
        t += every * rng.uniform(.6, 1.5)
def bamboo_groan(g=1.0, dur=1.6):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 70 + 30 * np.sin(np.pi * x / dur)
    s = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)) * (.5 + .5*np.sin(2*np.pi*17*x)) ** 3
    return verb(bp(s, 200, 1800) * env(n, .2, .4) * .08 * g, .5)
def tuko(g=1.0, n_=5):
    """Tokay gecko: a rising croak, then 'to-KO' repeated, slowing down."""
    out = []
    for k in range(n_):
        for f0, d in ((260, .16), (180, .22)):
            m = int(d * SR); x = np.arange(m) / SR
            s = np.sign(np.sin(2*np.pi*(f0 - 40*x/d)*x)) * (.5 + .5*np.sin(2*np.pi*90*x))
            out.append(bp(s, 150, 1600) * np.sin(np.pi*x/d) ** .5 * .12)
            out.append(np.zeros(int(.06 * SR)))
        out.append(np.zeros(int((.5 + .12 * k) * SR)))
    return verb(np.concatenate(out) * g, .35)
def jeepney(dur=6.0, g=1.0):
    """A diesel jeepney pulling away: knocking diesel idle rising then fading into the distance + a short horn."""
    n = int(dur * SR); x = np.arange(n) / SR
    rpm = 14 + 10 * np.minimum(1, x / 2.0)
    ph = 2 * np.pi * np.cumsum(rpm) / SR
    knock_ = (np.sin(ph) > .7).astype(float)
    s = lp(knock_, .05) * .5 + lp(rng.standard_normal(n), .02) * .4 + np.sin(ph * 3) * .15
    s *= np.exp(-x * .45) * env(n, .05, 1.0)
    hn = int(.5 * SR); hx = np.arange(hn) / SR
    horn = (np.sign(np.sin(2*np.pi*420*hx)) + np.sign(np.sin(2*np.pi*530*hx))) * .05 * env(hn, .01, .05)
    s[int(.9 * SR):int(.9 * SR) + hn] += bp(horn, 300, 3000)
    return s * g
def hoof(g=1.0, wood=False):
    n = int(.35 * SR); x = np.arange(n) / SR
    if wood:
        s = (np.sin(2*np.pi*(180 - 60*x)*x) * np.exp(-x*28) + bp(rng.standard_normal(n), 500, 2500) * np.exp(-x*70) * .6) * .8
        return verb(s * g, .35)
    s = np.sin(2*np.pi*(90 - 40*x)*x) * np.exp(-x*30) * .7 + bp(rng.standard_normal(n), 200, 1200) * np.exp(-x*50) * .4
    return s * g
def hooves(t0, t1, per=.55, g=1.0, wood=False, pan=0.0, gallop=False):
    t = t0
    while t < t1:
        if gallop:
            for j, dt in enumerate((0, .09, .2)):
                add(hoof(g * (.7 + .15 * j), wood), t + dt, pan)
        else:
            add(hoof(g, wood), t, pan)
        t += per
def snort(g=1.0):
    n = int(.7 * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 250, 2200) * (np.exp(-x*6) * (1 + .6*np.sin(2*np.pi*28*x))) * .4
    return verb(s * g, .3)
TL = {}
def tik_laugh(g=1.0):
    """The Tikbalang laugh: a slowed, pitched-down whinny (FM, falling, fast tremolo) under a deep 'heh heh heh'."""
    if "x" not in TL:
        n = int(1.8 * SR); x = np.arange(n) / SR
        f = 820 - 420 * (x / 1.8) ** .7
        vib = 1 + .08 * np.sin(2*np.pi*22*x)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        whin = (np.sin(ph) + .5*np.sin(2*ph) + .3*np.sin(3*ph)) * (.6 + .4*np.sin(2*np.pi*11*x)) * env(n, .03, .6)
        whin = bp(whin, 250, 4000) * .25
        try:
            from kokoro_onnx import Kokoro
            tk = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit", "models")
            k = Kokoro(os.path.join(tk, "kokoro.onnx"), os.path.join(tk, "voices.bin"))
            a, sr = k.create("Heh heh heh... heh heh heh.", voice="am_adam", speed=0.85, lang="en-us")
            a = np.asarray(a, float)
            if sr != SR: a = resample(a, int(len(a) * SR / sr))
            low = resample(a, int(len(a) * 1.6))
            low = bp(low, 80, 4000); low /= np.abs(low).max() + 1e-9
            v = np.zeros(max(len(low), n)); v[:len(low)] += low * .5; v[:n] += whin
        except Exception as e:
            print("laugh voice failed", e); v = whin
        TL["x"] = verb(v * .45, .8)
    return TL["x"] * g
KUL = [392.0, 440.0, 523.3, 587.3, 659.3, 784.0]
def gongchime(f, g=1.0, dur=1.6):
    n = int(dur * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*m*x) * np.exp(-x*dd) for m, a, dd in ((1, 1, 3.2), (2.02, .35, 5), (2.98, .2, 7), (4.1, .1, 9)))
    s += bp(rng.standard_normal(n), 2000, 6000) * np.exp(-x*150) * .2
    return verb(s * .06 * g, .45)
_gc = {}
def kulintang(t0, t1, g=1.0, per=.42, seed=0):
    """A slow, minor-ish kulintang gong-chime line (interlocking repeated notes)."""
    r = np.random.default_rng(seed); t = t0; k = 2
    while t < t1:
        k = int(np.clip(k + r.choice([-1, -1, 0, 1, 2, -2]), 0, len(KUL) - 1))
        f = KUL[k]
        if f not in _gc: _gc[f] = gongchime(f)
        reps = r.choice([1, 2, 3])
        for j in range(reps):
            add(_gc[f] * g * (1 - .2 * j), t, r.uniform(-.4, .4)); t += per * .5
        t += per * r.choice([1, 1, 2])
def agung(g=1.0):
    """The big hanging gong of the kulintang ensemble: a deep, slowly beating boom."""
    n = int(4.0 * SR); x = np.arange(n) / SR
    s = (np.sin(2*np.pi*73*x) + .6*np.sin(2*np.pi*74.2*x) + .3*np.sin(2*np.pi*146*x)) * np.exp(-x*.9)
    s += lp(rng.standard_normal(n), .05) * np.exp(-x*12) * .4
    return s * .22 * g
def chapel_bell(g=1.0):
    n = int(4.0 * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*x) * np.exp(-x*d) for f, a, d in ((523, 1, .9), (1046, .5, 1.4), (1256, .4, 1.8), (1690, .25, 2.5), (262, .5, .7)))
    return verb(s * .07 * g, .5)


# ---------------------------------------------------------------- ep15 sounds
KHENE = [146.8, 164.8, 196.0, 220.0, 246.9, 293.7, 329.6]     # D E G A B d e (Lao lai yai-like pentatonic)
def reed(f, dur, g=1.0, breath_=1.0):
    """A free-reed pipe: odd-heavy harmonics, a breathy attack, slight vibrato from the player's breath."""
    n = int(dur * SR); x = np.arange(n) / SR
    ph = 2 * np.pi * f * x * (1 + .003 * np.sin(2 * np.pi * 4.5 * x))
    s = np.sin(ph) + .55 * np.sin(3 * ph) + .3 * np.sin(5 * ph) + .2 * np.sin(2 * ph) + .12 * np.sin(7 * ph)
    s += bp(rng.standard_normal(n), 800, 4000) * .08 * breath_
    return lp(s, .3) * env(n, .08, .25) * .03 * g
def khene_drone(t0, t1, g=1.0):
    """The khene's constant drone pair (the low D and A) breathing in and out."""
    d = t1 - t0
    n = int(d * SR); x = np.arange(n) / SR
    pulse = .65 + .35 * np.sin(2 * np.pi * x / 2.4) ** 2
    s = (reed(73.4 * 2, d, 1.0) + reed(110.0 * 2, d, .7))[:n] * pulse
    add(s * g, t0, -.1)
def khene_line(t0, t1, g=1.0, per=.5, seed=0):
    r = np.random.default_rng(seed); t = t0; k = 3
    while t < t1 - .3:
        k = int(np.clip(k + r.choice([-2, -1, 1, 1, 2]), 0, len(KHENE) - 1))
        dur = per * r.choice([1, 1, 2, .5])
        add(reed(KHENE[k] * 2, dur + .1, g * 1.3) + reed(KHENE[k] * 3, dur + .1, g * .5), t, r.uniform(-.3, .3)); t += dur
def temple_drum(g=1.0):
    """A big temple drum: a deep skin boom with a slap and a long low tail."""
    n = int(3.5 * SR); x = np.arange(n) / SR
    s = np.sin(2 * np.pi * (52 + 40 * np.exp(-x * 9)) * x) * np.exp(-x * 1.6) * .9
    s += bp(rng.standard_normal(n), 120, 900) * np.exp(-x * 18) * .5
    return verb(s * .5 * g, .6)
def string_snap(g=1.0):
    """A cotton string snapping: a dry pluck that bends down, plus a tiny crack."""
    n = int(.6 * SR); x = np.arange(n) / SR
    f = 900 * np.exp(-x * 6) + 200
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 14) * .5
    s += bp(rng.standard_normal(n), 2000, 8000) * np.exp(-x * 120) * .8
    return verb(s * .4 * g, .25)
def sniff(g=1.0, n_=3):
    """Short, hungry sniffs (filtered noise inhales)."""
    o = np.zeros(int(1.4 * SR)); t = 0
    for k in range(n_):
        m = int(.16 * SR); x = np.arange(m) / SR
        s = bp(rng.standard_normal(m), 600, 3500) * np.sin(np.pi * x / .16) ** 2 * .3
        i = int(t * SR); o[i:i + m] += s; t += rng.uniform(.2, .3)
    return o * g
def sniffs(t0, t1, every=1.4, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        add(sniff(g, int(rng.integers(2, 4))), t, pan + rng.uniform(-.2, .2)); t += every * rng.uniform(.8, 1.2)
def scratch(dur=1.4, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    am = np.abs(np.sin(2 * np.pi * 7 * x)) ** 4
    return bp(rng.standard_normal(n), 1500, 6000) * am * env(n, .1, .3) * .2 * g
def chant(t0, dur, g=1.0):
    """Far-off low voices holding a note (the temple at night): a soft vowel drone with slow swells."""
    n = int(dur * SR); x = np.arange(n) / SR
    f = 98 * (1 + .004 * np.sin(2 * np.pi * .3 * x))
    ph = 2 * np.pi * np.cumsum(f) / SR
    src = sum(np.sin(h * ph) / h for h in range(1, 14))
    v = bp(src, 300, 700) + bp(src, 900, 1300) * .4
    v *= (.6 + .4 * np.sin(2 * np.pi * .12 * x) ** 2) * env(n, 1.5, 1.5)
    add(lp(v, .2) * .02 * g, t0, -.4)



# ---------------------------------------------------------------- ep16 sounds
SLENDRO = [293.7, 337.0, 386.6, 443.5, 509.0, 586.0, 674.0]       # ~5-tone equal slendro (+ upper notes)
def saron(f, g=1.0, dur=1.8):
    """A bronze metallophone key: an inharmonic bell tone with a mallet tick."""
    n = int(dur * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*m*x) * np.exp(-x*d) for m, a, d in ((1, 1, 2.2), (2.76, .35, 5), (5.4, .12, 9), (1.003, .6, 2.0)))
    s += bp(rng.standard_normal(n), 2500, 7000) * np.exp(-x * 200) * .25
    return verb(s * .05 * g, .55)
_sr = {}
def gamelan(t0, t1, g=1.0, per=.55, seed=0, low=False):
    """A slow, sad slendro line, each note sometimes echoed an octave down (the gender's soft answer)."""
    r = np.random.default_rng(seed); t = t0; k = 3
    while t < t1 - .2:
        k = int(np.clip(k + r.choice([-2, -1, -1, 1, 2]), 0, len(SLENDRO) - 1))
        f = SLENDRO[k] / (2 if low else 1)
        if f not in _sr: _sr[f] = saron(f)
        add(_sr[f] * g, t, r.uniform(-.4, .4))
        if r.random() < .35:
            f2 = f / 2
            if f2 not in _sr: _sr[f2] = saron(f2, 1.3, 2.6)
            add(_sr[f2] * g * .6, t + per * .5, r.uniform(-.3, .3))
        t += per * r.choice([1, 1, 2, 1.5])
def gong_ageng(g=1.0):
    """The big gamelan gong: a deep shimmering boom with slow beating."""
    n = int(6.0 * SR); x = np.arange(n) / SR
    s = (np.sin(2*np.pi*55*x) + .7*np.sin(2*np.pi*55.9*x) + .35*np.sin(2*np.pi*110.6*x) + .15*np.sin(2*np.pi*167*x)) * np.exp(-x*.55)
    s += lp(rng.standard_normal(n), .04) * np.exp(-x*14) * .5
    return s * .26 * g
LAUGHS = {}
def _kokoro(text, voice, speed):
    from kokoro_onnx import Kokoro
    tk = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit", "models")
    k = Kokoro(os.path.join(tk, "kokoro.onnx"), os.path.join(tk, "voices.bin"))
    a, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
    a = np.asarray(a, float)
    if sr != SR: a = resample(a, int(len(a) * SR / sr))
    return a
def kunti_laugh(near=False, g=1.0):
    """HER LAUGH. far: a high, shrill 'hihihi-hiii' pitched up, filtered thin and drowned in a long distant echo
    (loud but far away). near: the same laugh whispered - breathy, dry, very close (put it hard in one ear)."""
    key = near
    if key not in LAUGHS:
        try:
            a = _kokoro("Hi hi hi hi hi... hiiii hi hi hi...", "af_bella", 1.05)
            up = resample(a, int(len(a) / 1.18))                          # pitched up: shrill
            up = up / (np.abs(up).max() + 1e-9)
            if near:
                breathy = bp(rng.standard_normal(len(up)), 1500, 8000) * np.abs(lp(up, .05)) * 6.0
                v = bp(up, 300, 6000) * .35 + breathy
                v = v / (np.abs(v).max() + 1e-9)
                LAUGHS[key] = np.concatenate([v * .55, np.zeros(int(.4 * SR))])
            else:
                v = bp(up, 600, 4500)
                o = np.zeros(len(v) + int(2.6 * SR))
                for dl, a_ in ((0, .55), (.23, .4), (.47, .3), (.8, .22), (1.2, .15), (1.7, .1)):
                    i = int(dl * SR); o[i:i + len(v)] += lp(v, .35) * a_
                LAUGHS[key] = verb(o * .7, .9)
        except Exception as e:
            print("laugh failed", e); LAUGHS[key] = np.zeros(SR)
    return LAUGHS[key] * g
def baby_cry(dur=4.0, g=1.0):
    """A baby crying far off: wah-wah cries (falling pitch, nasal formants) with small gasps between, in reverb."""
    o = np.zeros(int(dur * SR)); t = 0.1; r = np.random.default_rng(66)
    while t < dur - .9:
        cd = r.uniform(.55, .9); n = int(cd * SR); x = np.arange(n) / SR
        f0 = r.uniform(430, 520) * (1 + .12 * np.sin(np.pi * x / cd) - .18 * x / cd) * (1 + .02 * np.sin(2*np.pi*7*x))
        ph = 2 * np.pi * np.cumsum(f0) / SR
        src = sum(np.sin(h * ph) / h ** .9 for h in range(1, 12))
        v = bp(src, 900, 1700) + bp(src, 2400, 3600) * .6
        v *= env(n, .05, .2) * (.7 + .3 * np.sin(2*np.pi*3*x))
        i = int(t * SR); o[i:i + n] += v[:len(o) - i]
        t += cd + r.uniform(.25, .45)
    return verb(lp(o, .5) * .05 * g, .8)
def plank_step(g=1.0):
    """A step on a hollow plank walk over water: a woody knock with a low boom under it."""
    n = int(.3 * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*(110 - 40*x/.3)*x) * np.exp(-x*20) * .6 + np.sin(2*np.pi*240*x) * np.exp(-x*35) * .25
    s += bp(rng.standard_normal(n), 500, 2500) * np.exp(-x*60) * .3
    return s * g
def planks(t0, t1, per, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        add(plank_step(g * rng.uniform(.8, 1.0)), t, pan + rng.uniform(-.05, .05)); t += per * rng.uniform(.93, 1.07)
def kentongan_hit(g=1.0):
    """The kentongan: a hollow wooden slit drum - a loud, hollow 'TOK' with a woody ring."""
    n = int(1.2 * SR); x = np.arange(n) / SR
    s = (np.sin(2*np.pi*330*x) * .8 + np.sin(2*np.pi*660*x) * .3 + np.sin(2*np.pi*170*x) * .5) * np.exp(-x*16)
    s += bp(rng.standard_normal(n), 800, 4000) * np.exp(-x*90) * .7
    return verb(s * .5 * g, .6)
def shimmer(dur=3.0, g=1.0):
    """Petals falling: a faint high sparkle."""
    o = np.zeros(int(dur * SR)); t = 0
    while t < dur - .5:
        f = rng.uniform(2400, 4200); n = int(.5 * SR); x = np.arange(n) / SR
        i = int(t * SR); o[i:i + n] += np.sin(2*np.pi*f*x) * np.exp(-x*9) * .02
        t += rng.uniform(.08, .3)
    return verb(o * g, .7)
def bolt(g=1.0):
    n = int(.7 * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 1500, 6000) * env(n, .02, .1) * (x < .45) * .15
    s += np.sin(2*np.pi*900*x) * np.exp(-(x - .5).clip(0) * 40) * (x > .5) * .2
    return verb(s * g, .2)
def door_open(g=1.0):
    return np.concatenate([creak(1.0, 1.4), np.zeros(int(.2 * SR))]) * g


LV = dict(hook=.8, setup=.3, rule=.3, count=.5, fog=.6, mistake=.8, cliff=.9, recap=.6, peek=.85, bang=.6, run=.7, twist=.5, explain=.3, outro=.3)
WIND = dict(hook=.2, setup=.35, rule=.2, count=.25, fog=.6, mistake=.4, cliff=.35, recap=.2, peek=.15, bang=.3, run=.4, twist=.05, explain=.2, outro=.15)
def curve(Dd, a):
    c = np.zeros(N)
    for s in T: c[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = Dd[s["id"]]
    c[int(TOT * SR):] = c[int(TOT * SR) - 1]
    return lp(c, a)
lvl, wl = curve(LV, .0006), curve(WIND, .0004)
drone = ((np.sin(2*np.pi*36.7*tt) + .5*np.sin(2*np.pi*55*tt) + .3*np.sin(2*np.pi*77.8*tt + np.sin(2*np.pi*.17*tt))) * .05
         + lp(rng.standard_normal(N), .008) * .22) * lvl
wmod = .6 + .4 * np.sin(2*np.pi*.07*tt) * np.sin(2*np.pi*.19*tt + 1)
windL = bp(rng.standard_normal(N), 200, 1500) * .07 * wmod; windR = bp(rng.standard_normal(N), 220, 1600) * .07 * wmod[::-1]
L += drone + windL * wl; R += drone + windR * wl
def creaks(t0, t1, every=1.3, g=1.0):
    t = t0
    while t < t1:
        add(creak(rng.uniform(.6, 1.2), g), t, rng.uniform(-.6, .6)); t += every * rng.uniform(.7, 1.4)
SIL = []
def knocks3(t0, per, g=1.0, contact=.14):
    for i in range(3): add(wood_knock(g), t0 + i * per + contact, .1)
def dust(t0, t1, g=1.0):
    n = int((t1 - t0) * SR)
    gr = (rng.random(n) > .996).astype(float)
    add(lfilter([1], [1, -.6], gr) * bp(rng.standard_normal(n), 3000, 9000) * .12 * g, t0, -.1)
def die_beep(g=1.0):
    n = int(.9 * SR); x = np.arange(n) / SR
    f = 1200 * np.exp(-x * 2.2)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * env(n, .01, .3) * .08 * g



def knocks(t0, g=1.0):
    for i in range(3): add(wood_knock(g), t0 + i * .32, -.35)





# ---------------------------------------------------------------- ep17 sounds (Thailand)
THAI = [270.0 * 2 ** (k / 7) for k in range(-3, 11)]               # Thai 7-step equal scale
def ranat(f, g=1.0, dur=1.0):
    """Ranat ek: a hard-mallet wooden bar - bright attack, woody partials, short ring."""
    n = int(dur * SR); x = np.arange(n) / SR
    s = (np.sin(2*np.pi*f*x) * np.exp(-x*7) + .45 * np.sin(2*np.pi*f*3.93*x) * np.exp(-x*22) + .2 * np.sin(2*np.pi*f*9.2*x) * np.exp(-x*45))
    s += bp(rng.standard_normal(n), 2000, 7000) * np.exp(-x*200) * .4
    return verb(s * .06 * g, .3)
_rn = {}
def rn(k, g=1.0):
    k = int(np.clip(k, 0, len(THAI) - 1))
    if k not in _rn: _rn[k] = ranat(THAI[k])
    return _rn[k] * g
def ranat_line(t0, t1, g=1.0, per=.22, seed=0):
    """Running piphat-style line: pairs of notes (octave-ish doubling) wandering in the Thai scale."""
    r = np.random.default_rng(seed); t = t0; k = 5
    while t < t1:
        k = int(np.clip(k + r.choice([-2, -1, -1, 1, 1, 2]), 0, len(THAI) - 8))
        add(rn(k, g), t, -.3); add(rn(k + 7, g * .5), t + .01, .3)
        t += per * r.choice([1, 1, 1, 2])
def ching(g=1.0, closed=False):
    n = int((.25 if closed else 2.2) * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*x + rng.uniform(0, 6)) for f, a in ((3180, 1), (4710, .7), (6930, .5), (8100, .3)))
    s *= np.exp(-x * (30 if closed else 2.2))
    s += bp(rng.standard_normal(n), 4000, 10000) * np.exp(-x*60) * .5
    return s * .025 * g
def chings(t0, t1, per=1.6, g=1.0):
    t = t0; k = 0
    while t < t1:
        add(ching(g, closed=k % 2 == 1), t, .4 if k % 2 else -.4); t += per / 2; k += 1
def khong(f, g=1.0):
    n = int(2.4 * SR); x = np.arange(n) / SR
    s = (np.sin(2*np.pi*f*x) + .35 * np.sin(2*np.pi*f*2.71*x) * np.exp(-x*3)) * np.exp(-x*1.6)
    return verb(s * np.minimum(1, x / .004) * .05 * g, .4)
def khong_line(t0, t1, g=1.0, per=.6, seed=0):
    r = np.random.default_rng(seed); t = t0; k = 3
    while t < t1:
        k = int(np.clip(k + r.choice([-1, 1, 2, -2]), 0, 7))
        add(khong(THAI[k] / 2, g), t, r.uniform(-.4, .4)); t += per * r.choice([1, 1, 2])
LULL = [5, 4, 3, 4, 5, 5, 3, 2, 1, 2, 3, 1]
def lullaby(t0, t1, g=1.0, per=.9):
    """A woman humming a slow lullaby (formant 'mm' voice), wavering, a little out of tune."""
    t = t0; i = 0
    while t < t1 - .3:
        f = THAI[LULL[i % len(LULL)] + 3] * 1.0 * (1 + rng.uniform(-.012, .012))
        d = per * (1.6 if i % 4 == 3 else 1.0)
        v = sfx._formant_voice(f, d + .15, "mm", vib=4.5)
        v = v * env(len(v), .12, .25)
        add(verb(v * .02 * g, .6), t, -.2); t += d; i += 1
def pestle(g=1.0):
    """A wooden pestle into a clay mortar (krok): dull thud + clay knock."""
    n = int(.4 * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*(110 - 40*x/.4)*x) * np.exp(-x*22) * .7 + bp(rng.standard_normal(n), 400, 1800) * np.exp(-x*60) * .5
    return s * .5 * g
def pounding(t0, t1, per=.63, g=1.0):
    t = t0
    while t < t1:
        add(pestle(g), t, .45); t += per * rng.uniform(.96, 1.04)
def roll(dur=1.1, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    bumps = (np.sin(2*np.pi*16*x) > .85).astype(float)
    s = bp(rng.standard_normal(n), 300, 2500) * (.3 + bumps) * .12
    return s * env(n, .05, .1) * g
def lime_drop(g=1.0):
    n = int(.5 * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*(180 - 80*x/.5)*x) * np.exp(-x*25) * .5 + bp(rng.standard_normal(n), 300, 1500) * np.exp(-x*50) * .3
    o = np.zeros(int(.9 * SR)); o[:n] += s; o[int(.22*SR):int(.22*SR)+n] += s * .35        # a little bounce
    return o * g
def stretch(dur=2.5, g=1.0):
    """Her arm stretching: wet creaks, bone clicks, a low groan rising."""
    n = int(dur * SR); x = np.arange(n) / SR
    f = 55 + 40 * x / dur
    gr = np.sin(2*np.pi*np.cumsum(f)/SR) * (.6 + .4*np.sin(2*np.pi*3*x)) * env(n, .3, .3) * .25
    o = gr + np.pad(creak(dur, 1.4), (0, 0))[:n]
    o = o[:n]
    t = .1
    while t < dur - .3:
        bc = bone_crack(.8, 2); i = int(t * SR); m = min(len(bc), n - i); o[i:i+m] += bc[:m]; t += rng.uniform(.25, .5)
    return o * g
def oar(g=1.0):
    n = int(1.0 * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 300, 2400) * np.sin(np.pi * np.clip(x / .6, 0, 1)) ** 2 * .2
    s += lp(rng.standard_normal(n), .02) * np.exp(-x*6) * .3
    return s * g
def strokes(t0, t1, per=1.7, g=1.0):
    t = t0
    while t < t1:
        add(oar(g), t, .3); add(bamboo_creak(.35), t + .3, .3); t += per
def dirt_steps(t0, t1, per, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        n = int(.16 * SR); x = np.arange(n) / SR
        s = np.sin(2*np.pi*(80 - 30*x/.16)*x) * np.exp(-x*30) * .5 + bp(rng.standard_normal(n), 300, 2500) * np.exp(-x*35) * .35
        add(s * g, t, pan + rng.uniform(-.05, .05)); t += per * rng.uniform(.94, 1.06)
def scare1(t, g=1.0):
    """Part 1 scare (sfx2): braam + sub drop + taiko + metal hit + glitch, with a tape-stopped tail."""
    add(sfx.braam(3.0, g), t); add(sfx.sub_drop(2.0, g), t); add(sfx.taiko(g * .9), t); add(sfx.glitch(.5, g * .8), t, .2)
    add(sfx.tape_stop(sfx.metal_hit(g * .9), 1.6), t + .05, -.2)
def scare2(t, g=1.0):
    add(choir_stab(1.2 * g), t); add(boom(1.2 * g), t); add(violin_screech(1.0, .9 * g), t + .02); add(sfx.metal_hit(.6 * g), t + .05, .3)


# ============================================================ ep19: new sounds
GONG = [293.7, 329.6, 370.0, 440.0, 493.9, 587.3, 659.3, 740.0]     # D gong pentatonic (D E F# A B)
def cicadas(t0, t1, g=1.0, pan=0.3):
    """Evening mountain cicadas: a bright buzzing pulse (AM ~45 Hz) swelling in long waves."""
    n = int((t1 - t0) * SR)
    if n <= 0: return
    x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 4200, 7500) * (0.55 + 0.45 * np.sin(2*np.pi*46*x)) * (0.6 + 0.4 * np.sin(2*np.pi*x/3.7))
    s2 = bp(rng.standard_normal(n), 3000, 5200) * (0.5 + 0.5 * np.sin(2*np.pi*31*x + 1)) * (0.5 + 0.5 * np.sin(2*np.pi*x/5.3 + 2))
    e = env(n, .4, .3)
    add((s * .05 + s2 * .035) * e * g, t0, pan); add((s2 * .04) * e * g, t0, -pan)
def muyu(g=1.0, f=820):
    """A temple muyu woodblock: a hollow wooden 'tok'."""
    n = int(.25 * SR); x = np.arange(n) / SR
    s = (np.sin(2*np.pi*f*x) + .5 * np.sin(2*np.pi*f*2.4*x)) * np.exp(-x * 38) + bp(rng.standard_normal(n), 800, 3000) * np.exp(-x * 160) * .4
    return s * .5 * g
def muyu_line(t0, t1, per=.6, g=1.0):
    t = t0
    while t < t1:
        add(muyu(g), t, -.2); t += per
def erhu(f, dur=1.6, g=1.0, bend=0.0):
    """An erhu-like bowed note: a bright sawtooth with slow vibrato, a nasal body resonance, a soft bow attack."""
    n = int(dur * SR); x = np.arange(n) / SR
    ff = f * (1 + bend * np.clip(x / dur, 0, 1) ** 2) * (1 + .012 * np.sin(2*np.pi*5.5*x) * np.clip(x / .4, 0, 1))
    ph = 2 * np.pi * np.cumsum(ff) / SR
    saw = sum(np.sin(h * ph) / h for h in range(1, 14))
    s = bp(saw, 400, 3800) * .7 + bp(saw, 900, 1400) * .6 + bp(rng.standard_normal(n), 2000, 6000) * .03
    return verb(s * env(n, .18, .45) * .12 * g, .5)
def erhu_line(t0, t1, g=1.0, per=1.4, seed=0, low=False):
    r = np.random.default_rng(seed); t = t0; k = 3
    while t < t1 - .6:
        k = int(np.clip(k + r.choice([-2, -1, 1, 2]), 0, len(GONG) - 1))
        d_ = per * r.choice([1, 1, 1.5, 2])
        f = GONG[k] / (2 if low else 1)
        add(erhu(f, min(d_, t1 - t) + .2, g, bend=r.choice([0, 0, -.06, .06])), t, r.uniform(-.3, .3)); t += d_
def tape_whirr(dur, g=1.0):
    """The home video playing: tape hiss, a motor whirr and a faint 15.7 kHz-ish line hum (filtered down)."""
    n = int(dur * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 2000, 9000) * .03 + np.sin(2*np.pi*120*x) * .012 * (1 + .3 * np.sin(2*np.pi*.8*x)) + bp(rng.standard_normal(n), 200, 600) * .02
    return s * env(n, .05, .05) * g
def fuse(dur=1.5, g=1.0):
    """A burning fuse: sizzling hiss with tiny crackles."""
    n = int(dur * SR)
    s = bp(rng.standard_normal(n), 3000, 9000) * .18 * (0.7 + 0.3 * rng.random(n))
    for k in range(int(dur * 25)):
        i = int(rng.uniform(0, n - 200)); s[i:i + 60] += rng.standard_normal(60) * .4
    return s * env(n, .05, .1) * g
def pop(g=1.0):
    """One small firecracker: a sharp crack with a short low body and a little room."""
    n = int(.22 * SR); x = np.arange(n) / SR
    s = rng.standard_normal(n) * np.exp(-x * 90) * .9 + np.sin(2*np.pi*90*x) * np.exp(-x * 40) * .6
    return verb(bp(s, 60, 9000) * g, .25)
def string_bangs(t0, dur=1.8, g=1.0):
    """A whole string of firecrackers going off: a fast irregular crackle with louder bangs, panning across."""
    t = t0; k = 0
    while t < t0 + dur:
        add(pop(g * rng.uniform(.5, 1.0) * (1.6 if k % 7 == 0 else 1.0)), t, rng.uniform(-.7, .7)); t += rng.uniform(.03, .09); k += 1
    add(sfx.sub_drop(1.2, .7 * g), t0); add(sfx.taiko(.8 * g), t0)
CH = {}
def child(text, g=1.0, near=False, pitch=1.28, voice="af_sky", speed=.85):
    """A little girl's voice: a soft voice pitched up; near = breathy, dry and close; else = faint with an echo."""
    key = (text, near, pitch)
    if key not in CH:
        try:
            a = _kokoro(text, voice, speed)
            up = resample(a, int(len(a) / pitch)); up = up / (np.abs(up).max() + 1e-9)
            if near:
                breathy = bp(rng.standard_normal(len(up)), 1500, 8000) * np.abs(lp(up, .05)) * 5.0
                v = bp(up, 300, 6000) * .45 + breathy
                CH[key] = v / (np.abs(v).max() + 1e-9) * .5
            else:
                v = bp(up, 500, 5000)
                o = np.zeros(len(v) + int(1.8 * SR))
                for dl, a_ in ((0, .6), (.19, .35), (.41, .22), (.7, .14), (1.1, .08)):
                    i = int(dl * SR); o[i:i + len(v)] += lp(v, .4) * a_
                CH[key] = verb(o * .6, .7)
        except Exception as e:
            print("child voice failed", e); CH[key] = np.zeros(SR)
    return CH[key] * g
CALL = {}
def call(text, g=1.0, voice="am_michael", fake=False):
    """Someone calling far away in the fog, with a long echo. fake = the same call, but slowed and wrong (too low,
    smeared) - the thing pretending to be Grandpa."""
    key = (text, fake)
    if key not in CALL:
        try:
            a = _kokoro(text, voice, .9)
            if fake:
                a = resample(a, int(len(a) * 1.12))
            v = bp(a / (np.abs(a).max() + 1e-9), 300, 3500)
            o = np.zeros(len(v) + int(2.5 * SR))
            for dl, a_ in ((0, .55), (.3, .35), (.62, .24), (1.0, .15), (1.5, .09)):
                i = int(dl * SR); o[i:i + len(v)] += lp(v, .3) * a_
            CALL[key] = verb(o * .7, .9)
        except Exception as e:
            print("call failed", e); CALL[key] = np.zeros(SR)
    return CALL[key] * g
def small_steps(t0, t1, n_, g=1.0, pan=0.0):
    """Small, light footsteps on leaves and earth (a child), n_ steps evenly between t0 and t1."""
    for k in range(n_):
        m = int(.18 * SR); x = np.arange(m) / SR
        s = bp(rng.standard_normal(m), 600, 5000) * np.exp(-x * 30) * .35 + np.sin(2*np.pi*140*x) * np.exp(-x * 45) * .3
        add(s * g, t0 + (t1 - t0) * k / max(1, n_ - 1), pan + rng.uniform(-.05, .05))
def stone_steps(t0, t1, per, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        add(stone_step(g * rng.uniform(.8, 1.0)), t, pan + rng.uniform(-.1, .1)); t += per * rng.uniform(.94, 1.06)
def end(sid): return st[sid] + DUR[sid]


SIL = []
if PART == "p1":
    # hook: the home video - tape whirr, cicadas, steps; a child counts under the narration; she turns; face
    h0 = st["hook"]; c1a, c1b = cap("hook", 0), cap("hook", 0, 2); c2a = cap("hook", 1)
    add(tape_whirr(DUR["hook"] - .7, .9), h0)
    cicadas(h0, end("hook") - .8, .9)
    stone_steps(h0 + .1, c2a + 1.7, .55, .6, .1)
    add(erhu(GONG[3], 2.5, .8, bend=-.05), h0 + .2)
    for i, dt in enumerate((1.1, 1.7, 2.3)):
        add(child(["one...", "two...", "three..."][i], .35, near=False), c1a + dt - .05, .4)
    add(child("four.", .9, near=True), c1b - .65, .7)
    add(sfx.sub_drop(1.5, .5), c1b - .6)
    turn = c2a + 1.7
    add(sfx.glitch(.4, .7), turn, .2); add(sfx.taiko(.5), turn)
    add(sfx.dissonant_strings(3.0, .5), turn)
    jt = end("hook") - .7
    add(sfx.riser(1.3, .8), jt - 1.35); SIL.append((jt - .3, jt - .02))
    scare1(jt, 1.2)
    # setup: mountain afternoon - cicadas, wind in the ferns, four people on stone steps, an erhu; the far watcher
    s0 = st["setup"]
    cicadas(s0, end("setup"), 1.0)
    stone_steps(s0 + .2, end("setup"), .5, .7, -.1)
    erhu_line(s0 + .4, cap("setup", 2) - .2, .9, 1.3, seed=2)
    add(sfx.dog_howl(4.0, 520, .7, seed=21, g=.4), s0 + 3.0, .6)
    add(sfx.music_box(end("setup") - cap("setup", 2), .45), cap("setup", 2) + .2)
    add(sfx.reverse_whisper(1.6, .6), cap("setup", 2) + .4, .7)
    # rule: the Earth God shrine - a small bell, muyu ticking, incense; the girl peeks; the three rules
    r0 = st["rule"]
    add(bell(.8), r0 + .3); add(bell(.5), r0 + 4.0)
    muyu_line(r0 + .6, end("rule") - .3, .62, .7)
    add(pad(DUR["rule"], (146.8, 220, 293.7), .02), r0)
    cicadas(r0, cap("rule", 1) + .8, .6)
    add(sfx.reverse_whisper(1.6, .7), cap("rule", 1) + .8, .7)
    add(child("hee hee...", .4), cap("rule", 1) + 1.0, .8)
    add(sfx.heartbeat_accel(end("rule") - cap("rule", 2), .95, .6, .6), cap("rule", 2))
    add(sfx.taiko(.45), cap("rule", 3))
    # count: Mei on the step, tapping the phone; the tape whirrs; a child voice counts with her... four
    k0 = st["count"]; c2a = cap("count", 1); c3a = cap("count", 2)
    cicadas(k0, c3a, .5)
    add(beep(.4), k0 + 1.4)
    add(tape_whirr(end("count") - c2a + .2, 1.0), c2a - .2)
    for i, dt in enumerate((.8, 1.5, 2.2)):
        add(child(["one...", "two...", "three..."][i], .3), c2a + dt - .05, -.3)
    add(child("four.", .8, near=True), c3a + .05, .7)
    add(sfx.sub_drop(1.8, .7), c3a + .1); add(sfx.dissonant_strings(4.0, .5), c3a + .1)
    add(sfx.heartbeat_accel(end("count") - c3a, .9, .5, .7), c3a)
    snap = end("count") - 1.0
    add(sfx.glitch(.4, .8), snap, .2); add(sfx.taiko(.8), snap); add(sfx.metal_hit(.5), snap + .02, -.3)
    # fog: the wind comes up, the cicadas fade out, Grandpa's voice fading uphill, the ribbons turn red
    f0 = st["fog"]
    cicadas(f0, f0 + 2.5, .7)
    add(sfx.dog_howl(4.5, 480, .5, seed=5, g=.7), f0 + .3, -.5); add(sfx.dog_howl(4.0, 560, .6, seed=6, g=.5), f0 + 3.5, .5)
    add(call("Mei... stay close...", .35), f0 + 1.0, -.4)
    add(pad(DUR["fog"], (146.8, 155.6, 220), .025), f0)
    erhu_line(cap("fog", 1), end("fog"), .7, 1.6, seed=4, low=True)
    add(sfx.music_box(3.0, .35), cap("fog", 2))
    stone_steps(f0 + .2, end("fog"), .6, .5)
    # mistake: "Mei! Mei, over here!" - a voice that isn't Grandpa; she answers; the forest goes silent; face
    m0 = st["mistake"]; t2 = cap("mistake", 1); t3 = cap("mistake", 2)
    add(sfx.dog_howl(4.0, 500, .7, seed=8, g=.5), m0, .4)
    add(call("Mei! Mei, over here!", .55, fake=True), m0 + .3, -.3)
    add(pad(t3 - m0, (146.8, 155.6, 207.7), .02), m0)
    add(sfx.heartbeat_accel(t3 - m0, .9, .6, .6), m0)
    SIL.append((t3 + .1, t3 + 1.3))
    add(child("hee hee hee...", .6), t3 + 1.3, .5)
    add(sfx.dissonant_strings(3.0, .5), t3 + 1.3)
    jt = end("mistake") - .6
    add(sfx.riser(1.0, .8), jt - 1.05); SIL.append((jt - .25, jt - .02))
    scare1(jt, 1.3); add(shriek(1.0, .6), jt + .05)
    # cliff: running, breath, into the hollow (muffled); small light steps come... and stop. hum. face
    c0 = st["cliff"]; cut = c0 + C["cliff"][0][2] - .4; t2 = cap("cliff", 1)
    dirt_steps(c0, cut, .24, 1.0)
    add(sfx.pulse_beat(cut - c0 + .5, 120, 160, .6), c0); add(rustle(1.5, 1.0), cut - .2, .1)
    breath(cut + .2, end("cliff") - 1.3, .8, 1.0)
    small_steps(t2 - .3, t2 + 1.8, 5, .9, .1)
    SIL.append((t2 + 1.9, t2 + 2.4))
    add(sfx.music_box(end("cliff") - t2 - 2.4, .5), t2 + 2.4)
    add(child("Mm mm mm... mm mm...", .35, near=True), t2 + 2.6, .4)
    jt = end("cliff") - 1.1
    add(sfx.heartbeat_accel(jt - t2, .9, .45, 1.1), t2)
    add(sfx.riser(1.5, 1.0), jt - 1.65); SIL.append((jt - .4, jt))
    scare1(jt, 1.3); add(shriek(1.0, .7), jt + .1)
    howls(st["rule"], end("fog"), every=16, dist=.8, g=.35, seed=7)
else:
    # recap: inside the hollow - breath, heartbeat, the wind outside, the music box
    r0 = st["recap"]
    add(muyu(.8), r0 + .1)
    breath(r0 + .3, end("recap"), .7, 1.1)
    add(sfx.heartbeat_accel(DUR["recap"], .95, .8, .6), r0)
    add(sfx.music_box(DUR["recap"], .35), r0 + .4)
    add(sfx.dog_howl(4.0, 500, .6, seed=3, g=.5), r0 + 1.5, -.5)
    # peek: fingers scratch the bark; her face comes down: "Mei... come and play with me"; face
    p0 = st["peek"]; t2 = cap("peek", 1); jt = end("peek") - .8
    add(scratch(1.4, .9), p0 + .3, -.5)
    add(child("Mei... come and play with me.", .9, near=True), t2 + .1, .2)
    add(sfx.dissonant_strings(3.0, .5), t2)
    add(sfx.riser(1.0, .8), jt - 1.05); SIL.append((jt - .2, jt - .02))
    scare2(jt, 1.2); add(reverse_scream(1.3, 1.4), jt)
    # bang: rustle, the lighter, the fuse... BANG - a whole string of firecrackers; her scream; the fog tears open
    b0 = st["bang"]; c2 = cap("bang", 1); c3 = cap("bang", 2)
    add(rustle(1.2, .7), b0 + .6, .2)
    add(sfx.heartbeat_accel(c3 - b0, .9, .45, .9), b0)
    erhu_line(b0 + .4, c2 - .4, .6, 1.0, seed=12)
    add(flick(1.0), c2 - 1.8, .2); add(fuse(c3 - c2 + 1.8, .8), c2 - 1.7, .2)
    add(sfx.riser(1.2, .7), c3 - 1.25); SIL.append((c3 - .15, c3 - .02))
    string_bangs(c3, 1.9, 1.1)
    add(shriek(1.6, 1.1), c3 + .3, -.2); add(reverse_scream(1.0, 1.0), c3 + .2)
    add(sfx.dog_howl(3.0, 600, .4, seed=13, g=.5), c3 + 1.8, .4)
    add(pad(end("bang") - c3 - 1.9, (146.8, 220, 293.7), .02), c3 + 1.9)
    add(erhu(GONG[4], 2.5, .8), c3 + 2.2)
    # run: running down the stone steps, breath; torches, voices calling "Mei!" from below - the right direction
    u0 = st["run"]
    stone_steps(u0, end("run"), .26, 1.0)
    add(sfx.pulse_beat(DUR["run"], 120, 150, .55), u0)
    breath(u0 + .2, end("run"), .7, .5)
    muyu_line(u0 + .2, end("run"), .3, .5)
    add(call("Mei! Mei!", .5), cap("run", 1) - .2, -.3)
    add(call("Mei! Where are you?", .4, voice="af_nicole"), cap("run", 1) + 1.2, .4)
    add(erhu(GONG[5], 2.5, .7), cap("run", 1) + .2)
    # twist: night in the apartment - a desk fan, a scooter outside, the phone playing the video (counting)... "four."
    w0 = st["twist"]; c2 = cap("twist", 1); c3 = cap("twist", 2); jt = end("twist") - 1.0
    n = int((jt - w0) * SR); xx = np.arange(n) / SR
    add(bp(rng.standard_normal(n), 100, 900) * .03 * (1 + .2 * np.sin(2*np.pi*3*xx)), w0)                 # desk fan
    add(engine(3.0, .3), w0 + .8, -.6)
    add(beep(.35), w0 + 1.5)
    add(bp(tape_whirr(c3 + .4 - w0, 1.0), 400, 4000) * 1.4, w0 + .3, -.1)
    for i in range(3):
        add(bp(child(["one...", "two...", "three..."][i], .6), 500, 3500), c2 + .7 + i * .6 - .05, -.1)
    add(sfx.music_box(c3 - c2, .3), c2 + .5)
    SIL.append((c3 + .25, c3 + .55))
    add(sfx.heartbeat_accel(jt - c3, .9, .45, .9), c3)
    add(child("four.", 1.3, near=True), c3 + 1.5, .85)
    add(sfx.sub_drop(1.5, .8), c3 + 1.5)
    add(sfx.riser(1.0, .7), jt - 1.05); SIL.append((jt - .12, jt - .02))
    scare2(jt, 1.25); add(child("hee hee...", .6, near=True), jt + .25, .6)
    # explain + outro: erhu + muyu + a temple bell; wind howls; the counting once more, far away
    e0 = st["explain"]
    add(bell(.7), e0 + .1)
    add(pad(DUR["explain"] + DUR["outro"], (146.8, 220, 293.7), .02), e0)
    erhu_line(e0 + .5, end("explain") - .5, .7, 1.4, seed=33)
    muyu_line(e0 + .5, end("explain") - .5, 1.2, .45)
    melody(e0 + .5, end("explain") - .5, .5, .55, seed=34)
    add(sfx.dog_howl(4.0, 500, .8, seed=9, g=.5), e0 + 8.0, .6)
    o0 = st["outro"]
    erhu_line(o0 + .2, end("outro") - .8, .6, 1.2, seed=35)
    add(child("one... two... three... four.", .25), o0 + 2.5, .5)
    add(sfx.dog_howl(4.0, 540, .85, seed=11, g=.5), o0 + 1.0, -.5)
    howls(st["recap"], end("run"), every=16, dist=.8, g=.35, seed=8)
_bL, _bR = sfx.bed(N / SR + 1, seed=19 if PART == "p1" else 20)
L += _bL[:N] * 1.0; R += _bR[:N] * 1.0
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
