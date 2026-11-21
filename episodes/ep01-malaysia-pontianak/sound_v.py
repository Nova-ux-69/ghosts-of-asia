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
LV = dict(hook=.7, village=.35, walk=.35, silence=.6, cry=.7, cliff=.9, recap=.6, grandma=.25, softer=.9,
          reveal=1.0, explain=.4, ending=.8, outro=.35)
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
if "village" in st:
    c0, c1 = st["village"], cap("silence", 0) + 0.3
    for _ in range(5):
        t0 = c0 + rng.uniform(0, 1); pan = rng.uniform(-.8, .8); g = rng.uniform(.02, .045)
        while t0 < c1 - .2: add(chirp(), t0, pan, g); t0 += rng.uniform(.45, .9)
for sid in ("silence", "cry", "cliff", "recap", "softer", "reveal", "ending", "hook"):
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
if PART == "p1":
    add(wail(2.0, 600, reverb=True), cap("hook", 0, 2) - 0.4, 0.5, 0.7)
    add(wail(2.6, 620), cap("cry", 0, 2) - .6, .6, 1.0)
    add(wail(2.2, 580), cap("cry", 1, 2) - .3, .6, .8)
    heart(cap("cliff", 1), st["cliff"] + DUR["cliff"])
    add(sting(.55), cap("cliff", 1) + 0.05)
    add(wail(1.6, 540, reverb=False), cap("cliff", 1, 2) + 0.1, -.5, .3)
    add(sting(.8, 4), cap("cliff", 2) - 0.1)
else:
    add(wail(2.4, 620), st["recap"] + 0.3, .6, .8)
    add(wail(2.0, 590), cap("recap", 1) + 0.2, .6, .6)
    add(pad(DUR["grandma"], (146.8, 174.6, 220, 261.6), .025), st["grandma"])
    add(wail(1.8, 560, reverb=False), cap("softer", 0, 2) - .2, -.5, .45)
    add(wail(1.6, 540, reverb=False), cap("softer", 1, 2) - .1, -.4, .25)
    heart(st["softer"] + .4, st["reveal"])
    add(sting(1.0), st["reveal"] + .05)
    add(pad(DUR["explain"] + .4, (110, 130.8, 164.8, 196.6), .025), st["explain"])
    add(sting(.7, 4.5), cap("ending", 1) + .1)
    add(pad(DUR["outro"], (110, 138.6, 164.8, 220), .022), st["outro"])
duck = np.ones(N)
for s in T:
    for c in s["caps"]: duck[int((st[s["id"]] + c[1]) * SR):int((st[s["id"]] + c[2]) * SR)] = .6
duck = lp(duck, .0008); L *= duck; R *= duck
vo = np.concatenate([sf.read(f"{PART}/vo/{s['id']}.wav")[0] for s in T]); vo = vo / np.abs(vo).max() * .85
L[:len(vo)] += vo; R[:len(vo)] += vo
mix = np.stack([L, R], 1)[:int(TOT * SR)]; mix /= max(1.0, np.abs(mix).max() / .97)
sf.write(f"{PART}/mix.wav", mix.astype(np.float32), SR); print(PART, "ok", round(TOT, 2))
