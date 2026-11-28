"""Ep18 White Lady (found footage) sound, built on the NEW kit toolkit/sfx2.py.
Car-camera audio: engine hum + tyre roar (changes with speed), cabin rattle, indicator ticks, the taximeter beeping,
a weak AM radio between stations, a woman's whisper "para po" (Kokoro voice, slowed, breathy, from the back seat),
camera mic clipping on scares, and the sfx2 bed (whispering choir) under everything."""
import json, sys, os, numpy as np, soundfile as sf
from scipy.signal import lfilter, butter, sosfilt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
import sfx2 as sfx
PART = sys.argv[1]; SR = sfx.SR
T = json.load(open(f"{PART}/timing.json"))
st = {}; acc = 0
for s in T: st[s["id"]] = acc; acc += s["dur"]
TOT = acc; N = int(TOT * SR) + SR
rng = np.random.default_rng(181 if PART == "p1" else 182)
L = np.zeros(N); R = np.zeros(N); tt = np.arange(N) / SR
C = {s["id"]: s["caps"] for s in T}; DUR = {s["id"]: s["dur"] for s in T}
def cap(sid, i): return st[sid] + C[sid][i][1]
def add(sig, t0, pan=0.0, g=1.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    sig = sig[:N - i]
    L[i:i + len(sig)] += sig * g * np.sqrt((1 - pan) / 2); R[i:i + len(sig)] += sig * g * np.sqrt((1 + pan) / 2)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype='band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, btype='low', fs=SR, output='sos'), x)
def seg_curve(vals, smooth=0.3):
    c = np.zeros(N)
    for s in T: c[int(st[s["id"]] * SR):int((st[s["id"]] + s["dur"]) * SR)] = vals.get(s["id"], 0)
    k = int(smooth * SR); ker = np.ones(k) / k
    return np.convolve(c, ker, mode="same")

# ---- car: engine + tyres, level by scene (0 = parked / playback)
CAR = dict(hook=.8, shift=1, rule=.7, shortcut=.6, lady=.8, again=.8, cliff=1.2, recap=.6, meter=1, voice=.8, empty=.5, twist=.2, explain=.5, outro=.4)
car = seg_curve(CAR)
eng = (np.sin(2 * np.pi * (38 + 10 * car) * tt) * 0.5 + np.sin(2 * np.pi * (76 + 20 * car) * tt) * 0.25)
eng = lp(eng + rng.standard_normal(N) * 0.3, 260) * 0.12 * car
tyre = bp(rng.standard_normal(N), 200, 1800) * 0.045 * car
rattle = bp(rng.standard_normal(N), 2000, 5000) * (rng.random(N) < 0.002) * 0.6 * car
L += eng + tyre + rattle; R += eng + tyre * 0.9 + rattle
bl, br = sfx.bed(N / SR, seed=18)
L += bl[:N] * 0.9; R += br[:N] * 0.9

def tick(g=1.0):
    n = int(.03 * SR); x = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1500, 5000) * np.exp(-x * 200) * .5 * g
def beep(f=2200, d=.09, g=1.0):
    n = int(d * SR); x = np.arange(n) / SR
    return np.sin(2 * np.pi * f * x) * np.minimum(1, np.minimum(x, d - x) / .005) * .12 * g
def radio(dur, g=1.0):
    n = int(dur * SR); x = np.arange(n) / SR
    s = bp(rng.standard_normal(n), 600, 3500) * (.5 + .5 * np.sin(2 * np.pi * .7 * x))
    s += np.sin(2 * np.pi * 440 * x + 3 * np.sin(2 * np.pi * 2 * x)) * .15 * (np.sin(2 * np.pi * .23 * x) > .6)   # a lost station
    return s * .06 * g
def clip_hit(g=1.0):
    """The cheap camera mic overloads: braam + distortion."""
    s = sfx.braam(2.5, 1.0); sd = sfx.sub_drop(1.8, .8); s[:len(sd)] += sd
    return np.tanh(s * 3) * .55 * g
_wh = None
def whisper():
    global _wh
    if _wh is None:
        from kokoro_onnx import Kokoro
        M = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit", "models")
        k = Kokoro(os.path.join(M, "kokoro.onnx"), os.path.join(M, "voices.bin"))
        a, sr = k.create("Pah-rah poh.", voice="af_nicole", speed=0.7, lang="en-us")
        a = np.interp(np.arange(0, len(a), sr / SR * 0.88), np.arange(len(a)), a)    # resample + pitch down a little
        breath = bp(rng.standard_normal(len(a)), 800, 6000) * np.abs(a).max() * .25
        a = bp(a, 250, 5000) + breath
        _wh = a / (np.abs(a).max() + 1e-9) * .5
    return _wh

SIL = []
if PART == "p1":
    add(sfx.glitch(.8, .9), st["hook"]); add(radio(DUR["hook"] + DUR["shift"], .9), st["hook"] + .8, -.3)
    add(sfx.dog_howl(4.5, 480, .6, seed=3), st["hook"] + 2.5, .5)             # kit-2 'howl' = wind through the trees
    for k in range(10): add(tick(.7), st["shortcut"] + .3 + k * .45, .5)    # indicator: turning onto Balete Drive
    add(sfx.music_box(DUR["rule"], .25), st["rule"] + .3, -.2)
    add(sfx.reverse_whisper(1.8, .6), cap("rule", 2) + .3, .6)
    add(sfx.pulse_beat(DUR["lady"] + DUR["again"], 66, 120, .8), st["lady"])
    add(sfx.dissonant_strings(5, .5), cap("lady", 0) + .4)
    add(sfx.glitch(.5, 1.0), st["again"]); add(sfx.sub_drop(1.5, .7), st["again"] + .05)
    add(sfx.reverse_whisper(1.8, .9), cap("again", 1) - .3, .5)
    add(sfx.riser(1.6, .8), cap("cliff", 1) - 1.5)
    add(sfx.glitch(.5, 1.0), cap("cliff", 1) - .1)
    SIL.append((cap("cliff", 1) + .2, cap("cliff", 1) + .9))               # the cabin camera clicks on: dead quiet
    add(sfx.heartbeat_accel(DUR["cliff"] - 4, .85, .45, 1.0), cap("cliff", 2) - .6)
    add(sfx.reverse_whisper(1.8, 1.1), cap("cliff", 2) + .3, .7)
    t4 = cap("cliff", 3)
    add(sfx.riser(1.8, 1.0), t4 - .4)
    SIL.append((t4 + 1.3, t4 + 1.4))
    add(clip_hit(1.2), t4 + 1.4)
else:
    add(sfx.glitch(.6, .8), st["recap"]); add(sfx.dissonant_strings(5, .45), st["recap"] + .3)
    add(sfx.heartbeat_accel(DUR["meter"] + DUR["voice"], .9, .5, .9), st["meter"])
    t2 = cap("meter", 1)
    for k in range(int((DUR["meter"] - (t2 - st["meter"])) * 3)):
        add(beep(2400, .07, .9), t2 + k / 3, .4)                            # the meter running by itself
    add(sfx.pulse_beat(DUR["voice"], 80, 130, .7), st["voice"])
    add(whisper(), cap("voice", 0) + 1.6, .8, 1.4)                          # 'para po' from the back seat, right ear
    add(sfx.reverse_whisper(1.8, .8), cap("voice", 1) - .4, .6)
    add(sfx.glitch(.5, 1.0), cap("voice", 1) - .05)
    SIL.append((cap("voice", 1) + .4, st["empty"] + .2))                    # he looks in the mirror: silence
    add(sfx.music_box(DUR["empty"], .4), st["empty"] + .3)
    add(sfx.dog_howl(4.0, 520, .7, seed=7), st["empty"] + 2.0, -.5)
    for k in range(int(DUR["twist"] * 2)):
        add(tick(.5), st["twist"] + k * .5, 0)                               # playback clicks
    jt = st["twist"] + DUR["twist"] - 1.0
    add(sfx.riser(1.8, 1.0), jt - 1.9)
    SIL.append((jt - .12, jt))
    add(clip_hit(1.25), jt)
    add(sfx.music_box(DUR["explain"], .35), st["explain"] + .5)
    add(sfx.dog_howl(4.5, 500, .8, seed=9), st["explain"] + 9.0, .5)
    add(sfx.music_box(DUR["outro"], .3), st["outro"] + .2)

for a, b in SIL:
    m = np.ones(N); m[int(a * SR):int(b * SR)] = 0.0
    m = np.convolve(m, np.ones(480) / 480, mode="same"); L *= m; R *= m
duck = np.ones(N)
for s in T:
    for c in s["caps"]: duck[int((st[s["id"]] + c[1]) * SR):int((st[s["id"]] + c[2]) * SR)] = .55
duck = np.convolve(duck, np.ones(SR // 5) / (SR // 5), mode="same"); L *= duck; R *= duck
vo = np.concatenate([sf.read(f"{PART}/vo/{s['id']}.wav")[0] for s in T]); vo = vo / np.abs(vo).max() * .85
L[:len(vo)] += vo; R[:len(vo)] += vo
mix = np.stack([L, R], 1)[:int(TOT * SR)]; mix /= max(1.0, np.abs(mix).max() / .97)
sf.write(f"{PART}/mix.wav", mix.astype(np.float32), SR); print(PART, "ok", round(TOT, 2))
