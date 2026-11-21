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
LV = dict(hook=.7, move=.25, warn=.35, rip=.45, night=.6, cliff=.9, recap=.6, door=.6, float=.8,
          reveal=1.0, morning=.2, explain=.4, outro=.35)
lvl = np.zeros(N)
for s in T: lvl[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = LV[s["id"]]
lvl[int(TOT * SR):] = lvl[int(TOT * SR) - 1]
lvl = lp(lvl, 0.0006)
d = ((np.sin(2*np.pi*55*tt) + .7*np.sin(2*np.pi*82.6*tt) + .4*np.sin(2*np.pi*110.3*tt)) * .05 + lp(rng.standard_normal(N), .01) * .25) * lvl
L += d; R += d
def chirp():
    n = int(.022 * SR); x = np.sin(2*np.pi*rng.uniform(4300, 5200)*np.arange(n)/SR) * np.hanning(n)
    o = np.zeros(int(.12 * SR))
    for k in range(3): o[int(k*.035*SR):int(k*.035*SR)+n] += x
    return o
CR = {"p1": ("move", "night", 1), "p2": None}[PART]
if CR:
    c0, c1 = st[CR[0]], cap(CR[1], CR[2]) + 0.3
    for _ in range(5):
        t0 = c0 + rng.uniform(0, 1); pan = rng.uniform(-.8, .8); g = rng.uniform(.02, .045)
        while t0 < c1 - .2: add(chirp(), t0, pan, g); t0 += rng.uniform(.45, .9)
for sid in ("hook", "night", "cliff", "recap", "door", "float", "reveal"):
    if sid not in st: continue
    n = int(DUR[sid] * SR)
    w = bp(rng.standard_normal(n), 250, 900) * .05 * (0.6 + .4*np.sin(np.linspace(0, 2*np.pi, n) - 1.5)) * env(n, 1.0, 0.8)
    add(w, st[sid], -.3); add(np.roll(w, 4000), st[sid], .3)
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
if PART == "p1":
    add(chime(.8), st["hook"] + .2, .3); add(hum(5.0, .6, seed=1), cap("hook", 0, 2) - .3, .4)
    add(pad(DUR["move"] + DUR["warn"], (146.8, 185, 220, 293.7), .02), st["move"])
    add(noise_burst(.35, 1500, 5000, .25), cap("rip", 1) + .1, 0); add(noise_burst(.3, 1200, 4500, .2), cap("rip", 1) + .6, .2)
    add(thump(.9), cap("rip", 1) + (C["rip"][1][2] - C["rip"][1][1]) * .6, 0)
    add(chime(.6), cap("night", 1), .5)
    add(hum(DUR["night"] - C["night"][2][1] + DUR["cliff"], .55, seed=2), cap("night", 2) - .3, .6)
    add(sting(.6, 4), cap("cliff", 1) - .05)
    add(sting(.8, 4), cap("cliff", 2) - .1)
else:
    add(hum(DUR["recap"] + 2, .5, seed=3), st["recap"] + .3, .5)
    add(noise_burst(1.2, 300, 1400, .12), st["door"] + .25, -.4)
    add(hum(DUR["door"] + DUR["float"], .6, base=415, seed=4), cap("door", 1) - .2, .3)
    heart(st["float"] + .3, st["reveal"] + C["reveal"][1][1])
    add(sting(1.0), cap("reveal", 1) - .05)
    birds(st["morning"] + .3, st["morning"] + DUR["morning"] - .5)
    add(pad(DUR["morning"], (174.6, 220, 261.6, 349.2), .02), st["morning"])
    add(chime(.6), cap("morning", 1), .2)
    add(pad(DUR["explain"] + .4, (110, 130.8, 164.8, 196.6), .025), st["explain"])
    add(pad(DUR["outro"], (110, 138.6, 164.8, 220), .022), st["outro"])
duck = np.ones(N)
for s in T:
    for c in s["caps"]: duck[int((st[s["id"]] + c[1]) * SR):int((st[s["id"]] + c[2]) * SR)] = .6
duck = lp(duck, .0008); L *= duck; R *= duck
vo = np.concatenate([sf.read(f"{PART}/vo/{s['id']}.wav")[0] for s in T]); vo = vo / np.abs(vo).max() * .85
L[:len(vo)] += vo; R[:len(vo)] += vo
mix = np.stack([L, R], 1)[:int(TOT * SR)]; mix /= max(1.0, np.abs(mix).max() / .97)
sf.write(f"{PART}/mix.wav", mix.astype(np.float32), SR); print(PART, "ok", round(TOT, 2))
