import json, sys, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt
PART = sys.argv[1]; SR = 24000
T = json.load(open(f"{PART}/timing.json"))
st = {}; acc = 0
for s in T: st[s["id"]] = acc; acc += s["dur"]
TOT = acc; N = int(TOT * SR) + SR
rng = np.random.default_rng(7 if PART == "p1" else 8)
L = np.zeros(N); R = np.zeros(N); tt = np.arange(N) / SR
C = {s["id"]: s["caps"] for s in T}; DUR = {s["id"]: s["dur"] for s in T}
def cap(sid, i, j=1): return st[sid] + C[sid][i][j]
def add(sig, t0, pan=0.0, g=1.0):
    i = int(t0 * SR)
    if i >= N: return
    sig = sig[:N - i]
    L[i:i + len(sig)] += sig * g * np.sqrt((1 - pan) / 2); R[i:i + len(sig)] += sig * g * np.sqrt((1 + pan) / 2)
def lp(x, a): return lfilter([a], [1, -(1 - a)], x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def env(n, a, r):
    e = np.ones(n); ai, ri = int(a * SR), int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
LV = dict(hook=.75, walk=.35, warn=.15, appear=.55, ask=.8, cliff=.9, recap=.6, answer=.75, mask=1.0,
          trick=.5, run=.5, explain=.35, outro=.3)
lvl = np.zeros(N)
for s in T: lvl[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = LV[s["id"]]
lvl[int(TOT * SR):] = lvl[int(TOT * SR) - 1]
lvl = lp(lvl, 0.0006)
# low drone + the electric hum of streetlights and vending machines (Japan's 50 Hz mains buzz)
d = ((np.sin(2*np.pi*49*tt) + .6*np.sin(2*np.pi*73.4*tt) + .35*np.sin(2*np.pi*98*tt)) * .05 + lp(rng.standard_normal(N), .01) * .22) * lvl
buzz = (np.sign(np.sin(2*np.pi*100*tt)) * .5 + np.sin(2*np.pi*200*tt)) * .006
street = np.zeros(N)
for sid in ("hook", "walk", "appear", "cliff", "recap", "trick", "run"):
    if sid in st: street[int(st[sid] * SR):int((st[sid] + DUR[sid]) * SR)] = 1
street = lp(street, .0008)
L += d + buzz * street * .8; R += d + buzz * street
def wail(dur, f0=600, g=1.0, reverb=True):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (1 + .18*np.sin(np.pi*t/dur) - .25*(t/dur)**2) + 10*np.sin(2*np.pi*5.5*t)
    ph = 2 * np.cumsum(np.pi * f / SR)
    s = sum(np.sin(k*ph)/(k**1.3) for k in range(1, 7)) + .15*bp(rng.standard_normal(n), 800, 3000)
    s *= (.6 + .4*np.abs(np.sin(np.pi*2.2*t))**.5) * env(n, .35, .9)
    s = bp(s, 350, 3200) * .12 * g
    if not reverb: return s
    o = np.zeros(n + int(1.5 * SR)); o[:n] += s
    for dl, a in ((.09,.5),(.17,.4),(.29,.32),(.41,.25),(.6,.18),(.83,.12),(1.1,.08)):
        i = int(dl * SR); o[i:i+n] += lp(s, .3) * a
    return o
def thump(g=1):
    n = int(.25 * SR); t = np.arange(n) / SR
    return np.sin(2*np.pi*(55 - 20*t/.25)*t) * np.exp(-t*18) * .35 * g
def heart(a, b):
    t0, per = a, .95
    while t0 < b - .2: add(thump(), t0); add(thump(.7), t0 + .22); t0 += per; per = max(.5, per * .93)
def sting(g=1.0, dur=4.5):
    n = int(dur * SR); t = np.arange(n) / SR
    boom = np.sin(2*np.pi*(40 + 90*np.exp(-t*6))*t) * np.exp(-t*2.2) * .6
    burst = lp(rng.standard_normal(n), .08) * np.exp(-t*7) * .4
    cl = sum(np.sin(2*np.pi*f*t + rng.uniform(0, 6)) for f in (1661, 1760, 1865, 1976, 880, 932)) * .035
    cl *= np.minimum(1, t/.05) * np.exp(-t*.9) * (.7 + .3*np.sin(2*np.pi*9*t))
    return (boom + burst + cl) * g
def pad(dur, freqs, g):
    n = int(dur * SR); t = np.arange(n) / SR
    p = sum(np.sin(2*np.pi*f*t) * (.6 + .4*np.sin(2*np.pi*.13*t + i)) for i, f in enumerate(freqs))
    return lp(p, .15) * env(n, 1.0, 1.0) * g

def hum(dur, g=1.0, base=440.0, seed=0):
    r = np.random.default_rng(seed)
    notes = [1, 1.189, 1.335, 1.189, 1, 0.891, 1, 1.189, 1.0]
    n = int(dur * SR); t = np.arange(n) / SR
    seg = dur / len(notes)
    idx = np.minimum((t / seg).astype(int), len(notes) - 1)
    f = base * np.array(notes)[idx]
    f = lp(f, 0.002) * (1 + 0.008 * np.sin(2 * np.pi * 5.2 * t))
    ph = 2 * np.cumsum(np.pi * f / SR)
    s = sum(np.sin(k * ph) / k ** 1.6 for k in range(1, 6))
    s = 0.6 * bp(s, 250, 450) + 0.4 * bp(s, 750, 1000) + 0.15 * s
    s *= env(n, 0.8, 1.2) * (0.75 + 0.25 * np.sin(2 * np.pi * (1 / seg) * t - 1.5) ** 2) * 0.1 * g
    o = np.zeros(n + int(1.5 * SR)); o[:n] += s
    for dl, a in ((.11, .45), (.23, .35), (.37, .26), (.55, .18), (.8, .1)):
        i = int(dl * SR); o[i:i + n] += lp(s, .3) * a
    return o
def chime(g=1.0):
    n = int(2.5 * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * (1.5 + k)) for k, f in enumerate((2093, 2637, 3136))) * .05 * g
def noise_burst(dur, lo, hi, g):
    n = int(dur * SR)
    return bp(rng.standard_normal(n), lo, hi) * env(n, .01, dur * .8) * g
def birds(t0, t1):
    t = t0
    while t < t1:
        n = int(.12 * SR); tt = np.arange(n) / SR
        f = rng.uniform(2800, 4200) * (1 + .3 * np.sin(2 * np.pi * 18 * tt))
        add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.hanning(n) * .03, t, rng.uniform(-.7, .7))
        t += rng.uniform(.15, .9)

def step(g=1.0, hard=False):
    n = int(.09 * SR); t = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 300 if hard else 200, 2600 if hard else 1800) * np.exp(-t * 55) * .5
    s += np.sin(2*np.pi*70*t) * np.exp(-t * 40) * .3
    return s * g
def steps(t0, t1, per, g, hard=False):
    t = t0; k = 0
    while t < t1:
        add(step(g * (1 if k % 2 else .8), hard), t, -.15 if k % 2 else .15); t += per * rng.uniform(.95, 1.05); k += 1
def crossing(t0, t1, g=.5):
    """Distant Japanese railway crossing bell: kan-kan-kan."""
    t = t0; k = 0
    while t < t1:
        n = int(.35 * SR); x = np.arange(n) / SR
        f = 760 if k % 2 else 740
        b = (np.sin(2*np.pi*f*x) + .4*np.sin(2*np.pi*f*2.76*x)) * np.exp(-x * 9)
        add(lp(b, .25) * .05 * g, t, .7); t += .42; k += 1
def tick(t0, t1, g=.6):
    t = t0
    while t < t1:
        n = int(.02 * SR); add(bp(rng.standard_normal(n), 2500, 6000) * np.hanning(n) * .08 * g, t, -.5); t += 1.0
def glitch(dur, g=1.0):
    n = int(dur * SR); s = np.zeros(n)
    for i in range(0, n, int(.03 * SR)):
        if rng.random() < .55:
            m = min(n - i, int(.03 * SR)); s[i:i+m] = bp(rng.standard_normal(m), 600, 5000)[:m] * rng.uniform(.3, 1)
    return s * .2 * g
def fl_buzz(t0, dur=1.0, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    gate = (rng.random(n // 600 + 1) < .55).repeat(600)[:n]
    s = (np.sign(np.sin(2*np.pi*100*x)) * .5 + bp(rng.standard_normal(n), 2000, 6000) * .3) * gate * .09 * g
    add(s, t0, .3)
if PART == "p1":
    add(sting(.45, 3), st["hook"] + .05); add(wail(4.0, 520, .5), cap("hook", 0, 2) - 1.2, .5)
    add(sting(.5, 3.5), cap("hook", 1) - .05)
    steps(st["walk"] + .3, st["walk"] + DUR["walk"] - .2, .55, .5)
    crossing(st["walk"] + 1.0, st["walk"] + DUR["walk"] - .5, .6)
    tick(st["warn"] + .3, st["warn"] + DUR["warn"] - .3)
    add(pad(DUR["warn"], (196, 246.9, 293.7, 392), .02), st["warn"])
    add(chime(.7), cap("warn", 1) + .2, -.2)
    steps(st["appear"] + .2, st["appear"] + C["appear"][0][2], .55, .5)
    fl_buzz(cap("appear", 1) + .8, 1.0, 1.0); add(thump(1.0), cap("appear", 1) + 1.7)
    add(wail(DUR["appear"] - C["appear"][2][1] + 1, 470, .45), cap("appear", 2) - .2, .6)
    heart(st["ask"] + .2, cap("ask", 2) + .2)
    add(hum(4.0, .45, base=392, seed=5), st["ask"] + .5, .4)
    add(sting(1.0), cap("ask", 2) - .05)
    heart(st["cliff"] + .1, cap("cliff", 2) - .2)
    add(sting(.6, 4), cap("cliff", 1) - .05)
    add(sting(.85, 4), cap("cliff", 2) - .1)
else:
    add(wail(5.0, 500, .45), st["recap"] + .4, .5)
    add(sting(.45, 3), cap("recap", 1) - .05)
    heart(st["answer"] + .1, st["answer"] + DUR["answer"])
    add(thump(1.2), cap("answer", 1) + .5)
    heart(st["mask"] + .1, cap("mask", 2))
    add(hum(DUR["mask"] - 1.5, .55, base=370, seed=6), st["mask"] + .3, -.3)
    add(sting(1.1, 3.0), cap("mask", 2) - .05)
    add(glitch(1.2, 1.0), st["trick"] + C["trick"][1][1] + (C["trick"][1][2] - C["trick"][1][1]) * .55, 0)
    add(chime(.6), st["trick"] + C["trick"][1][1] + (C["trick"][1][2] - C["trick"][1][1]) * .55 + .3, .2)
    steps(cap("run", 1) - .4, st["run"] + DUR["run"] - .3, .3, .55, hard=True)
    add(pad(DUR["run"], (220, 277.2, 329.6, 440), .02), st["run"])
    add(pad(DUR["explain"] + .4, (110, 130.8, 164.8, 196.6), .025), st["explain"])
    add(chime(.5), cap("explain", 1) + .3, -.2); add(chime(.5), cap("explain", 2) + .3, .2)
    add(pad(DUR["outro"], (110, 138.6, 164.8, 220), .022), st["outro"])
    # dead silence for the black cut after "How about... now?"
    c0 = int((st["mask"] + C["mask"][2][2] + .15) * SR); c1 = int((st["mask"] + DUR["mask"]) * SR)
    gate = np.ones(N); gate[c0 + int(.9 * SR):c1] = .15; gate = lp(gate, .002); L *= gate; R *= gate
duck = np.ones(N)
for s in T:
    for c in s["caps"]: duck[int((st[s["id"]] + c[1]) * SR):int((st[s["id"]] + c[2]) * SR)] = .6
duck = lp(duck, .0008); L *= duck; R *= duck
vo = np.concatenate([sf.read(f"{PART}/vo/{s['id']}.wav")[0] for s in T]); vo = vo / np.abs(vo).max() * .85
L[:len(vo)] += vo; R[:len(vo)] += vo
mix = np.stack([L, R], 1)[:int(TOT * SR)]; mix /= max(1.0, np.abs(mix).max() / .97)
sf.write(f"{PART}/mix.wav", mix.astype(np.float32), SR); print(PART, "ok", round(TOT, 2))
