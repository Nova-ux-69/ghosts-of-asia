"""Ep07 Myanmar / Ma Phae Wah sound: hot still night bed (crickets, a distant tokay gecko calling "to-kay"),
a nasal hne-style reed melody that bends between notes, soft pat-waing-like tuned drums, a big monastery bell at
dawn, her dragging bare-foot shuffle on dust, the creak of a heavy coffin, plank-door knocks and a banging shutter.
Scares use toolkit/sfx.py: riser -> silence -> braam + sub_drop + glitch + dissonant strings."""
import json, os, sys, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
from sfx import braam, sub_drop, riser, pulse_beat, heartbeat_accel, reverse_whisper, glitch, dissonant_strings, dog_howl, dog_pack
PART = sys.argv[1]; SR = 24000
T = json.load(open(f"{PART}/timing.json"))
st = {}; acc = 0
for s in T: st[s["id"]] = acc; acc += s["dur"]
TOT = acc; N = int(TOT * SR) + SR
rng = np.random.default_rng(71 if PART == "p1" else 72)
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
SCALE = [261.6, 293.7, 329.6, 392.0, 440.0, 523.3, 587.3]
def hne(f0, f1, dur, g=1.0):
    """Nasal double-reed note that slides from f0 to f1, with vibrato."""
    n = int(dur * SR); x = np.arange(n) / SR
    f = f0 + (f1 - f0) * np.clip(x / min(.25, dur * .4), 0, 1) ** 2
    f = f * (1 + .012 * np.sin(2 * np.pi * 5.5 * x) * np.clip(x / .3, 0, 1))
    ph = np.cumsum(f) / SR
    saw = 2 * (ph % 1) - 1
    s = bp(saw, 700, 3200) + .3 * bp(saw, 1800, 4200)
    return s * env(n, .04, min(.2, dur * .3)) * .05 * g
def melody(t0, t1, g=1.0, per=.5, seed=0):
    r = np.random.default_rng(seed); t = t0; k = 3; prev = SCALE[k]
    while t < t1:
        k = int(np.clip(k + r.choice([-2, -1, -1, 1, 2]), 0, len(SCALE) - 1))
        d = per * r.choice([1, 1, 2, 3])
        add(verb(hne(prev, SCALE[k], d * .95, g), .45), t, r.uniform(-.3, .3)); prev = SCALE[k]; t += d
def drum(f=180, g=1.0):
    """Tuned barrel-drum stroke (pat waing-like)."""
    n = int(.6 * SR); x = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * (1 + .25 * np.exp(-x * 30)) * x) * np.exp(-x * 9)
    s += bp(rng.standard_normal(n), 300, 2500) * np.exp(-x * 60) * .3
    return s * .18 * g
def drums(t0, t1, g=1.0, seed=0):
    r = np.random.default_rng(seed); t = t0
    while t < t1:
        add(drum(r.choice([150, 180, 220, 260]), g), t, r.uniform(-.4, .4)); t += r.choice([.25, .25, .5, .75])
def monastery_bell(g=1.0, dur=6.0):
    n = int(dur * SR); x = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*x) * np.exp(-x * d) for f, a, d in ((196, 1, .5), (392, .5, .8), (470, .4, 1.0), (590, .3, 1.3), (880, .2, 2)))
    s *= np.minimum(1, x / .005)
    s += lp(rng.standard_normal(n), .08) * np.exp(-x * 20) * .3
    return verb(s * .14 * g, .5)
def boom(g=1.0, dur=3.0):
    n = int(dur * SR); x = np.arange(n) / SR
    return (np.sin(2*np.pi*(38 + 80*np.exp(-x*7))*x) * np.exp(-x*2.4) * .6 + lp(rng.standard_normal(n), .06) * np.exp(-x*8) * .35) * g
def shuffle(g=1.0):
    """A bare foot dragged slowly over dry dust."""
    n = int(.7 * SR); x = np.arange(n) / SR
    e = np.sin(np.pi * x / .7) ** 2
    return bp(rng.standard_normal(n), 500, 3500) * e * (.6 + .4 * np.sin(2*np.pi*17*x)) * .09 * g
def shuffles(t0, t1, per, g=1.0, pan=0.0):
    t = t0
    while t < t1:
        add(shuffle(g), t, pan); t += per
def gecko(g=1.0):
    """Tokay gecko: a rattle, then 'to-KAY' twice."""
    o = np.zeros(int(2.4 * SR))
    for k in range(2):
        for j, (f, d) in enumerate(((520, .12), (380, .22))):
            n = int(d * SR); x = np.arange(n) / SR
            s = np.sign(np.sin(2*np.pi*f*x)) * np.sin(np.pi*x/d) ** 2
            s = bp(s, 300, 2200) * .12
            i = int((.4 + k * .9 + j * .2) * SR); o[i:i+n] += s
    n = int(.3 * SR); x = np.arange(n) / SR
    o[:n] += bp(rng.standard_normal(n), 1500, 4000) * (np.sin(2*np.pi*40*x) > 0) * .05
    return o * g
def crickets(t0, t1, g=1.0):
    n = int((t1 - t0) * SR); x = np.arange(n) / SR
    if n <= 0: return
    s = np.sin(2*np.pi*4300*x) * (np.sin(2*np.pi*30*x) > .3) * (np.sin(2*np.pi*.7*x) > -.2)
    s2 = np.sin(2*np.pi*5100*x) * (np.sin(2*np.pi*26*x + 1) > .4) * (np.sin(2*np.pi*.5*x + 2) > 0)
    add((s + s2 * .7) * .01 * g * env(n, .5, .5), t0, .2)
def knock(g=1.0):
    n = int(.25 * SR); x = np.arange(n) / SR
    return (np.sin(2*np.pi*110*x) * .7 + bp(rng.standard_normal(n), 200, 1800) * .6) * np.exp(-x*28) * .6 * g
def bang(g=1.0):
    n = int(.8 * SR); x = np.arange(n) / SR
    return (np.sin(2*np.pi*(90 + 60*np.exp(-x*20))*x) * .7 + bp(rng.standard_normal(n), 150, 3000) * .8) * np.exp(-x*10) * .7 * g
def creak(dur=1.3, g=1.0, f0=160):
    n = int(dur * SR); x = np.arange(n) / SR
    f = f0 + 110 * np.sin(np.pi * x / dur)
    s = np.sign(np.sin(2*np.pi*np.cumsum(f)/SR)) * (.5 + .5*np.sin(2*np.pi*27*x))
    return bp(s, 250, 2400) * env(n, .1, .3) * .05 * g
def thud(g=1.0):
    n = int(1.0 * SR); x = np.arange(n) / SR
    return (np.sin(2*np.pi*(55 + 40*np.exp(-x*12))*x) * np.exp(-x*6) * .8 + bp(rng.standard_normal(n), 120, 900) * np.exp(-x*25) * .5) * g
def whoosh(dur=1.6, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    return bp(rng.standard_normal(n), 200, 1800) * np.sin(np.pi * x / dur) ** 2 * .25 * g
def sputter(t0, t1, g=1.0):
    t = t0
    while t < t1:
        n = int(.05 * SR); add(bp(rng.standard_normal(n), 800, 5000) * np.exp(-np.arange(n) / SR * 60) * .1 * g, t, -.2)
        t += rng.uniform(.05, .25)
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
def scare(t, g=1.0):
    """The big hit: about 3 dB above the narration."""
    add(braam(3.0, 1.0 * g), t); add(sub_drop(2.0, 1.0 * g), t); add(glitch(.5, .9 * g), t, .3)
    add(dissonant_strings(4.0, .7 * g), t + .05)
def pre_scare(t, rise=2.2, gap=.4):
    add(riser(rise, .8), t - gap - rise)
    hush.append((t - gap, t))

hush = []
LV = dict(hook=.8, town=.35, warn=.3, look=.6, call=.8, cliff=.9, recap=.6, pray=.5, door=.8, empty=.4, dawn=.4, explain=.3, outro=.3)
WIND = dict(hook=.7, town=.4, warn=.1, look=.2, call=.4, cliff=.6, recap=.6, pray=.1, door=.3, empty=.5, dawn=.3, explain=0, outro=0)
def curve(D, a):
    c = np.zeros(N)
    for s in T: c[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = D[s["id"]]
    c[int(TOT * SR):] = c[int(TOT * SR) - 1]
    return lp(c, a)
lvl, wl = curve(LV, .0006), curve(WIND, .0004)
drone = ((np.sin(2*np.pi*49*tt) + .5*np.sin(2*np.pi*73.4*tt) + .35*np.sin(2*np.pi*103.8*tt + np.sin(2*np.pi*.17*tt))) * .05
         + lp(rng.standard_normal(N), .008) * .22) * lvl
wmod = .6 + .4 * np.sin(2*np.pi*.08*tt) * np.sin(2*np.pi*.21*tt + 1)
windL = bp(rng.standard_normal(N), 220, 1300) * .08 * wmod; windR = bp(rng.standard_normal(N), 240, 1400) * .08 * wmod[::-1]
L += drone + windL * wl; R += drone + windR * wl
if PART == "p1":
    D_ = DUR["hook"]; t2 = cap("hook", 1); stop_t = t2 - .4; jump = t2 + 1.6
    add(boom(.7), st["hook"] + .05); add(reverse_whisper(1.6, .8), st["hook"] + .3, -.3)
    shuffles(st["hook"] + .4, stop_t, 1.0, 1.0, .1)
    add(heartbeat_accel(jump - st["hook"] - 1.0, .95, .45, .8), st["hook"] + 1.0)
    add(reverse_whisper(1.6, 1.0), t2 + .1, .3)
    pre_scare(jump, 1.8, .35); scare(jump, 1.0)
    crickets(st["town"], st["town"] + DUR["town"], 1.0)
    add(gecko(1.0), st["town"] + 1.0, -.5)
    melody(st["town"] + .4, st["town"] + DUR["town"] - .5, .6, .55, seed=2)
    add(creak(.9, 1.2, 220), cap("town", 1) + .3, .3); add(knock(.8), cap("town", 1) + 1.1, .3)
    add(pad(DUR["warn"], (130.8, 196, 261.6), .02), st["warn"])
    sputter(st["warn"] + .2, st["warn"] + DUR["warn"], .5)
    add(reverse_whisper(1.6, .9), cap("warn", 1) + .3, .5); add(whoosh(1.4, .5), cap("warn", 1) + .4, .6)
    lk = st["look"]
    crickets(lk, cap("look", 1) - .3, .7)
    add(heartbeat_accel(DUR["look"] - .5, .95, .5, .9), lk + .3)
    hush.append((cap("look", 1) - .35, cap("look", 1) - .05))
    shuffles(cap("look", 1), cap("look", 2) - .1, .75, 1.6, .4)
    add(creak(1.4, 1.3, 140), cap("look", 2) + .4, .3)
    add(pulse_beat(DUR["look"] - (cap("look", 3) - lk) + .3, 70, 110, .6), cap("look", 3) - .2)
    shuffles(cap("look", 3), lk + DUR["look"], 1.0, .7, .2)
    add(boom(.6), cap("look", 3) - .1)
    c0 = st["call"]; jump2 = cap("call", 2, 2) + .25
    hush.append((cap("call", 1) - .1, cap("call", 1) + 1.2))
    add(reverse_whisper(1.6, 1.0), cap("call", 1) + 1.0, -.4)
    add(heartbeat_accel(jump2 - cap("call", 2), .8, .4, 1.0), cap("call", 2))
    add(creak(1.6, 1.0, 90), cap("call", 2) + .1, 0)                 # the neck turning
    pre_scare(jump2, 1.5, .4); scare(jump2, 1.0)
    cl = st["cliff"]
    add(pulse_beat(cap("cliff", 1) - cl, 80, 140, .8), cl)
    for k, c in enumerate((0.0, 1.3, 2.5, 3.5)):
        add(glitch(.3, .6), cl + c, .2 * (k % 2 * 2 - 1)); add(boom(.5 + .1 * k), cl + c)
    add(creak(2.6, 1.4, 120), cap("cliff", 1) + .3, .2)
    add(thud(1.0), cap("cliff", 2) - .35)
    jump3 = cap("cliff", 2, 2) + .25
    add(heartbeat_accel(jump3 - cap("cliff", 1), .9, .42, 1.0), cap("cliff", 1))
    add(reverse_whisper(1.6, .8), cap("cliff", 2) + .2, .3)
    pre_scare(jump3, 1.6, .35); scare(jump3, 1.1)
    # dogs (PLAYBOOK 2b): a pack at the start, far single howls under the build-ups, cut before each scare
    add(dog_pack(7.0, .7, 1.0), .2, -.4)
    add(dog_howl(4.0, 500, .75, .9, seed=3), st["town"] + 5.5, .5)
    add(dog_howl(3.5, 560, .7, .9, seed=4), st["look"] + 1.0, -.6)
    add(dog_howl(3.5, 470, .8, .8, seed=5), st["cliff"] + 1.0, .6)
else:
    add(boom(.6), st["recap"] + .05)
    add(creak(2.8, 1.2, 120), cap("recap", 1) + .3, .2); add(thud(.7), cap("recap", 1) + 3.0)
    shuffles(st["recap"] + .3, cap("recap", 1), 1.0, .8, .1)
    pr = st["pray"]
    add(whoosh(.8, .5), pr + .8, -.2)
    add(pad(DUR["pray"], (130.8, 155.6, 196), .025), pr)
    add(reverse_whisper(1.6, .8), cap("pray", 1) + .2, -.5)
    add(heartbeat_accel(DUR["pray"] - (cap("pray", 2) - pr), .9, .5, 1.0), cap("pray", 2))
    add(whoosh(3.0, .8), cap("pray", 2) + .3, .5)
    out_t = cap("pray", 2, 2) - .3
    sputter(out_t - 1.2, out_t, 1.2); add(whoosh(.5, .6), out_t, -.2)
    dr = st["door"]
    kn = [cap("door", 0) + C["door"][0][2] * .5 + k * .45 for k in range(3)]
    kn = [dr + C["door"][0][1] + C["door"][0][2] * .5 + k * .45 for k in range(3)]
    for k in kn: add(knock(1.3), k, .1)
    hush.append((cap("door", 1) - .1, cap("door", 1) + 1.5))
    jump = cap("door", 2, 2) + .05
    add(heartbeat_accel(jump - cap("door", 2), .9, .45, 1.0), cap("door", 2))
    add(creak(1.6, .8, 200), cap("door", 2) + .3, .4)
    pre_scare(jump, 2.0, .35)
    add(bang(1.3), jump - .02); scare(jump, 1.0)
    add(reverse_whisper(1.6, .9), st["empty"] + .2, .4)
    dw = st["dawn"]
    add(monastery_bell(1.2), dw + .2); add(monastery_bell(.8), dw + 3.2)
    birds(dw + .5, cap("dawn", 2) - .3, .9)
    melody(cap("dawn", 1), cap("dawn", 2) - .3, .45, .6, seed=4)
    # the twist: night again, another lamp goes out across the road
    add(dog_howl(3.5, 520, .75, .9, seed=8), cap("dawn", 2) + .1, .5)
    shuffles(cap("dawn", 2) + .2, cap("dawn", 2, 2) - .6, 1.0, .6, -.3)
    add(heartbeat_accel(cap("dawn", 2, 2) - cap("dawn", 2), .9, .5, .7), cap("dawn", 2))
    add(boom(1.0), cap("dawn", 2, 2) - .6); add(reverse_whisper(1.6, 1.0), cap("dawn", 2, 2) - .4, -.3)
    add(dog_pack(6.0, .7, .9), .3, .4)
    add(dog_howl(4.0, 540, .75, .9, seed=6), st["pray"] + .5, -.5)
    ex = st["explain"]
    melody(ex + .3, ex + DUR["explain"] - .5, .45, .6, seed=6)
    drums(ex + .3, ex + DUR["explain"] - .5, .5, seed=7)
    add(pad(DUR["explain"] + .4, (130.8, 196, 261.6), .02), ex)
    ou = st["outro"]
    melody(ou + .2, ou + DUR["outro"] - 1.0, .5, .5, seed=8)
    drums(ou + .2, ou + DUR["outro"] - 1.0, .6, seed=9)
    add(pad(DUR["outro"], (130.8, 164.8, 196, 261.6), .02), ou)
# pre-scare silence: everything (except the voice) drops out
hm = np.ones(N)
for a, b in hush: hm[int(a * SR):int(b * SR)] = .03
hm = lp(hm, .004); L *= hm; R *= hm
# duck the music under the voice (but the scare hits stay loud: they sit after the lines)
duck = np.ones(N)
for s in T:
    for c in s["caps"]: duck[int((st[s["id"]] + c[1]) * SR):int((st[s["id"]] + c[2]) * SR)] = .55
duck = lp(duck, .0008); L *= duck; R *= duck
vo = np.concatenate([sf.read(f"{PART}/vo/{s['id']}.wav")[0] for s in T]); vo = vo / np.abs(vo).max() * .8
L[:len(vo)] += vo; R[:len(vo)] += vo
mix = np.stack([L, R], 1)[:int(TOT * SR)]; mix /= max(1.0, np.abs(mix).max() / .97)
sf.write(f"{PART}/mix.wav", mix.astype(np.float32), SR); print(PART, "ok", round(TOT, 2), "peak", round(float(np.abs(mix).max()), 3))
