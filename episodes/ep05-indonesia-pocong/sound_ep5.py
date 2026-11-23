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

LV = dict(hook=.75, village=.35, warn=.15, shortcut=.5, thump=.8, cliff=.9, recap=.6, turn=1.0, bow=.6,
          untie=.7, morning=.25, explain=.35, outro=.3)
lvl = np.zeros(N)
for s in T: lvl[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = LV[s["id"]]
lvl[int(TOT * SR):] = lvl[int(TOT * SR) - 1]
lvl = lp(lvl, 0.0006)
# low drone + monsoon bed: rain hiss (stereo, decorrelated) whose level follows the story
d = ((np.sin(2*np.pi*49*tt) + .6*np.sin(2*np.pi*73.4*tt) + .35*np.sin(2*np.pi*98*tt)) * .05 + lp(rng.standard_normal(N), .01) * .22) * lvl
RAINLV = dict(hook=.5, village=.15, warn=.35, shortcut=.8, thump=.9, cliff=.5, recap=.7, turn=.6, bow=.4, untie=.15,
              morning=0, explain=0, outro=0)
rl = np.zeros(N)
for s in T: rl[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = RAINLV[s["id"]]
if "shortcut" in st: rl[int(st["shortcut"] * SR):int((st["shortcut"] + 1.0) * SR)] = .2
rl = lp(rl, .0004)
rainL = (bp(rng.standard_normal(N), 900, 7000) * .06 + lp(rng.standard_normal(N), .05) * .05)
rainR = (bp(rng.standard_normal(N), 900, 7000) * .06 + lp(rng.standard_normal(N), .05) * .05)
L += d + rainL * rl; R += d + rainR * rl
def thunder(g=1.0, dur=4.0, near=False):
    n = int(dur * SR); x = np.arange(n) / SR
    crack = bp(rng.standard_normal(n), 800, 5000) * np.exp(-x * 25) * (.6 if near else .1)
    roll = lp(rng.standard_normal(n), .004) * 6 * (np.exp(-x * .9) * (1 - np.exp(-x * 8))) * (.7 + .3 * np.sin(2*np.pi*1.3*x))
    return (crack + roll) * .5 * g
def hop(g=1.0):
    """Soft, heavy cloth-wrapped thud: low thump + muffled cloth swish."""
    n = int(.4 * SR); x = np.arange(n) / SR
    s = np.sin(2*np.pi*(62 - 25*x/.4)*x) * np.exp(-x*14) * .55
    s += lp(rng.standard_normal(n), .06) * np.exp(-x*20) * .5
    s += bp(rng.standard_normal(n), 300, 1500) * np.exp(-((x - .02) / .03) ** 2) * .12
    return s * g
def hops(t0, t1, per, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        add(hop(g), t, pan); t += per
def sigh(dur=2.0, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 400, 2500) * np.sin(np.pi * x / dur) ** 2 * .12
    return s * g
def birds(t0, t1, g=1.0):
    t = t0
    while t < t1:
        n = int(.18 * SR); x = np.arange(n) / SR
        f = rng.uniform(2800, 4200) * (1 + .3 * np.sin(2*np.pi*14*x))
        s = np.sin(2*np.pi*np.cumsum(f)/SR) * np.sin(np.pi*x/.18) ** 2 * .03 * g
        add(s, t, rng.uniform(-.8, .8)); t += rng.uniform(.25, 1.1)
def sparkle(dur, g=1.0):
    n = int(dur * SR); s = np.zeros(n)
    for _ in range(int(dur * 30)):
        i = rng.integers(0, max(1, n - 2000)); m = 1500; x = np.arange(m) / SR
        s[i:i+m] += np.sin(2*np.pi*rng.uniform(2500, 5000)*x) * np.exp(-x*50) * .03
    return s * g
if PART == "p1":
    add(thunder(.8), st["hook"] + .15, -.3)
    add(sting(.45, 3), st["hook"] + .05)
    hops(cap("hook", 0) + 2.2, st["hook"] + DUR["hook"] - .4, .62, .7, .2)
    add(sting(.6, 3.5), cap("hook", 1) - .05); add(thunder(1.0, near=True), cap("hook", 1) - .05, .3)
    steps(st["village"] + .3, st["village"] + DUR["village"] - .3, .55, .4)
    add(thunder(.5, 5), st["village"] + 3.0, .5); add(thunder(.6, 5), cap("village", 1) + 1.2, -.4)
    add(pad(DUR["warn"], (174.6, 220, 261.6, 349.2), .02), st["warn"])
    add(chime(.6), cap("warn", 1) + .2, -.2)
    add(thunder(.4), cap("warn", 1) + 3.4, .2)
    add(thunder(.8, near=True), cap("shortcut", 0) + 1.0, -.3)
    steps(cap("shortcut", 1) - .3, st["shortcut"] + DUR["shortcut"], .3, .55, hard=True)
    add(wail(DUR["thump"], 420, .35), st["thump"] + .3, -.4)
    tb = C["thump"][1][2] - C["thump"][1][1]
    for k in range(3):
        add(hop(1.4), cap("thump", 1) + tb * k / 3 + .05, -.3)
    heart(cap("thump", 1), st["thump"] + DUR["thump"])
    add(thunder(1.2, near=True), cap("thump", 2) + .2); add(sting(.9), cap("thump", 2) + .15)
    hops(cap("thump", 2) + .2, st["thump"] + DUR["thump"], .7, .8, -.3)
    hops(st["cliff"] + .2, cap("cliff", 0) + 2.0, .8, 1.0, .3)
    heart(cap("cliff", 0), cap("cliff", 2) - .2)
    ws = sf.read("p1/whisper.wav")[0]
    ws = np.interp(np.arange(0, len(ws), 24000 / 24000), np.arange(len(ws)), ws)
    add(ws * .5, cap("cliff", 1) + .9, .5); add(lp(ws, .3) * .25, cap("cliff", 1) + 1.05, -.5)
    add(sting(.6, 4), cap("cliff", 1) - .05)
    add(sting(.85, 4), cap("cliff", 2) - .1)
else:
    add(wail(5.0, 440, .4), st["recap"] + .4, .5)
    hops(cap("recap", 1) - .6, st["recap"] + DUR["recap"], .66, .8, -.3)
    add(sting(.45, 3), cap("recap", 1) - .05)
    heart(st["turn"] + .3, st["turn"] + DUR["turn"] - .3)
    add(noise_burst(.8, 300, 1500, .08), cap("turn", 0) + .3)
    add(pad(DUR["turn"] - 2, (98, 103.8, 146.8), .03), cap("turn", 1))
    add(sting(1.1, 3.0), cap("turn", 2) - .05); add(thunder(.9, near=True), cap("turn", 2))
    add(noise_burst(1.2, 200, 1200, .1), cap("bow", 1) + .3)
    add(pad(DUR["bow"], (220, 261.6, 329.6), .018), st["bow"])
    add(noise_burst(.4, 500, 3000, .12), cap("untie", 0) + 1.6); add(noise_burst(.5, 400, 2600, .1), cap("untie", 0) + 2.4)
    add(sigh(2.4, 1.6), cap("untie", 1) + .4)
    add(sparkle(3.0, 1.0), cap("untie", 1) + .6)
    add(pad(DUR["untie"] - 3, (261.6, 329.6, 392, 523.3), .02), cap("untie", 1) + .3)
    birds(st["morning"] + .3, st["morning"] + DUR["morning"] - .3, 1.0)
    add(pad(DUR["morning"] + .4, (196, 246.9, 293.7, 392), .02), st["morning"])
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
