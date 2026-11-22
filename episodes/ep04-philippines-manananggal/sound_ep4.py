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
def step(g=1.0, hard=False):
    n = int(.09 * SR); t = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 300 if hard else 200, 2600 if hard else 1800) * np.exp(-t * 55) * .5
    s += np.sin(2*np.pi*70*t) * np.exp(-t * 40) * .3
    return s * g
def steps(t0, t1, per, g, hard=False):
    t = t0; k = 0
    while t < t1:
        add(step(g * (1 if k % 2 else .8), hard), t, -.15 if k % 2 else .15); t += per * rng.uniform(.95, 1.05); k += 1
def glitch(dur, g=1.0):
    n = int(dur * SR); s = np.zeros(n)
    for i in range(0, n, int(.03 * SR)):
        if rng.random() < .55:
            m = min(n - i, int(.03 * SR)); s[i:i+m] = bp(rng.standard_normal(m), 600, 5000)[:m] * rng.uniform(.3, 1)
    return s * .2 * g
LV = dict(hook=.75, village=.35, warn=.15, open=.45, legs=.7, cliff=.9, recap=.6, face=1.0, lola=.55,
          salt=.8, dawn=.4, explain=.35, outro=.3)
lvl = np.zeros(N)
for s in T: lvl[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = LV[s["id"]]
lvl[int(TOT * SR):] = lvl[int(TOT * SR) - 1]
lvl = lp(lvl, 0.0006)
# low drone + a tropical night bed: pulsing crickets/cicadas and slow frog croaks
d = ((np.sin(2*np.pi*55*tt) + .6*np.sin(2*np.pi*82.4*tt) + .35*np.sin(2*np.pi*110*tt)) * .05 + lp(rng.standard_normal(N), .01) * .22) * lvl
crick = bp(rng.standard_normal(N), 4200, 5200) * (.5 + .5 * np.sign(np.sin(2*np.pi*22*tt))) * (.6 + .4*np.sin(2*np.pi*.4*tt)) * .05
night = np.zeros(N)
for sid in ("hook", "village", "open", "legs", "cliff", "recap", "face", "salt"):
    if sid in st: night[int(st[sid] * SR):int((st[sid] + DUR[sid]) * SR)] = 1
if "dawn" in st: night[int(st["dawn"] * SR):int((st["dawn"] + DUR["dawn"] * .5) * SR)] = .5
night = lp(night, .0008)
L += d + crick * night * .9; R += d + np.roll(crick, 900) * night
def frog(g=1.0):
    n = int(.22 * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*(180 + 60*np.sin(2*np.pi*30*x))*x) * (np.sin(np.pi*x/.22) ** 2) * (.5 + .5*np.sign(np.sin(2*np.pi*28*x)))
    return lp(s, .2) * .06 * g
def frogs(t0, t1, g=1.0):
    t = t0
    while t < t1:
        add(frog(g * rng.uniform(.6, 1)), t, rng.uniform(-.8, .8)); t += rng.uniform(.5, 1.6)
def flap(g=1.0):
    n = int(.45 * SR); x = np.arange(n) / SR
    s = lp(rng.standard_normal(n), .05) * np.exp(-((x - .12) / .07) ** 2) * 1.4
    s += np.sin(2*np.pi*45*x) * np.exp(-((x - .12) / .05) ** 2) * .5
    return s * .5 * g
def flaps(t0, t1, per=.75, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        add(flap(g), t, pan); t += per
def shriek(dur=1.6, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 900 + 500 * np.sin(np.pi * x / dur) + 40 * np.sin(2*np.pi*13*x)
    ph = 2 * np.cumsum(np.pi * f / SR)
    s = sum(np.sin(k*ph) / k for k in range(1, 5)) + .4 * bp(rng.standard_normal(n), 1500, 5000)
    s = bp(s, 500, 5000) * env(n, .05, .6) * .14 * g
    o = np.zeros(n + int(1.2 * SR)); o[:n] += s
    for dl, a in ((.12, .5), (.25, .35), (.4, .22), (.6, .12)):
        i = int(dl * SR); o[i:i + n] += lp(s, .3) * a
    return o
def sparkle(dur, g=1.0):
    n = int(dur * SR); s = np.zeros(n)
    for _ in range(int(dur * 40)):
        i = rng.integers(0, max(1, n - 2000)); m = 1500; x = np.arange(m) / SR
        s[i:i+m] += np.sin(2*np.pi*rng.uniform(3000, 6000)*x) * np.exp(-x*60) * .03
    return s * g
def rooster(g=1.0):
    n = int(1.6 * SR); x = np.arange(n) / SR
    f = np.interp(x, [0, .15, .35, .6, 1.2, 1.6], [500, 760, 700, 820, 640, 420])
    ph = 2 * np.cumsum(np.pi * f / SR)
    s = sum(np.sin(k*ph) / k**1.2 for k in range(1, 6)) * env(n, .03, .4) * (.7 + .3*np.sign(np.sin(2*np.pi*24*x)))
    return lp(bp(s, 400, 3500), .5) * .05 * g
if PART == "p1":
    add(sting(.45, 3), st["hook"] + .05); flaps(st["hook"] + .6, st["hook"] + 4.8, .55, .8, .3)
    add(sting(.5, 3.5), cap("hook", 1) - .05)
    frogs(st["village"] + .3, st["village"] + DUR["village"] - .3, .8)
    steps(st["village"] + .3, st["village"] + DUR["village"] - .3, .55, .45)
    add(noise_burst(.5, 600, 2500, .08), cap("village", 1) + .6, .2)
    add(pad(DUR["warn"], (196, 246.9, 293.7, 392), .02), st["warn"])
    add(chime(.7), cap("warn", 1) + .2, -.2)
    add(noise_burst(.9, 500, 2200, .1), cap("open", 1) + .3, -.2)
    frogs(st["open"] + 1, st["open"] + DUR["open"], .7)
    add(wail(DUR["legs"], 430, .4), st["legs"] + .3, .4)
    heart(cap("legs", 1) - .2, st["legs"] + DUR["legs"])
    add(sting(.9), cap("legs", 2) - .05)
    flaps(cap("cliff", 0) + .4, cap("cliff", 0) + 3.4, .8, 1.3, 0)
    heart(cap("cliff", 1) - .3, cap("cliff", 2) - .2)
    add(sting(.6, 4), cap("cliff", 1) - .05)
    add(sting(.85, 4), cap("cliff", 2) - .1)
else:
    add(wail(5.0, 460, .45), st["recap"] + .4, .5)
    flaps(cap("recap", 1) - .2, cap("recap", 1) + 2.0, .6, 1.0)
    add(sting(.45, 3), cap("recap", 1) - .05)
    heart(st["face"] + .3, st["face"] + DUR["face"] - .3)
    flaps(st["face"] + .5, st["face"] + DUR["face"] - .5, .9, .7, .2)
    add(wail(4.0, 380, .5), cap("face", 1) - .2, -.3)
    add(sting(1.1, 3.0), cap("face", 2) - .05)
    add(thump(1.2), cap("lola", 0) + 1.3)
    add(sting(.7, 2.5), cap("lola", 1) + (C["lola"][1][2] - C["lola"][1][1]) * .75 - .05)
    steps(st["salt"] + .2, st["salt"] + 3.2, .3, .55, hard=True)
    add(sparkle(2.5, 1.0), cap("salt", 0) + 1.6)
    add(shriek(1.8, 1.0), cap("salt", 1) - .1, .3)
    add(sting(.6, 3), cap("salt", 1) - .05)
    flaps(st["dawn"] + .2, cap("dawn", 1), .5, .5)
    add(rooster(1.0), cap("dawn", 1) + .8, -.5)
    add(pad(DUR["dawn"] + .4, (261.6, 329.6, 392, 523.3), .02), st["dawn"])
    add(pad(DUR["explain"] + .4, (110, 130.8, 164.8, 196.6), .025), st["explain"])
    add(chime(.5), cap("explain", 1) + .3, -.2); add(chime(.5), cap("explain", 2) + .3, .2)
    add(pad(DUR["outro"], (110, 138.6, 164.8, 220), .022), st["outro"])
duck = np.ones(N)
for s in T:
    for c in s["caps"]: duck[int((st[s["id"]] + c[1]) * SR):int((st[s["id"]] + c[2]) * SR)] = .6
duck = lp(duck, .0008); L *= duck; R *= duck
vo = np.concatenate([sf.read(f"{PART}/vo/{s['id']}.wav")[0] for s in T]); vo = vo / np.abs(vo).max() * .85
L[:len(vo)] += vo; R[:len(vo)] += vo
mix = np.stack([L, R], 1)[:int(TOT * SR)]; mix /= max(1.0, np.abs(mix).max() / .97)
sf.write(f"{PART}/mix.wav", mix.astype(np.float32), SR); print(PART, "ok", round(TOT, 2))
