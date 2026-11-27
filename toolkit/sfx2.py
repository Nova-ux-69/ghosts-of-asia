"""Sound kit #2 for Ghosts of Asia (Nova, 2026-11-27: "all videos sound the same, change to a new one").
Same function names as sfx.py, so an episode switches kits with:  import sfx2 as sfx
New character: taiko + metal impacts with tape-stops, a creepy child-hum, a detuned music box, a ticking clock pulse,
bowed-glass clusters, a low "aah" choir, wind that howls through trees (instead of dogs), plus bed() for a breathing,
whispering background under the whole video. All mono float arrays at SR unless noted."""
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

SR = 24000
_rng = np.random.default_rng(23)


def _t(d): return np.arange(int(d * SR)) / SR
def _env(n, a, r):
    e = np.ones(n); ai, ri = min(int(a * SR), n // 2), min(int(r * SR), n // 2)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def _bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)
def _lp(x, f): return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)
def _hp(x, f): return sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)
def _verb(s, wet=0.5, size=1.0):
    o = np.zeros(len(s) + int(2.2 * size * SR)); o[:len(s)] += s
    for dl, a in ((.05, .6), (.11, .5), (.19, .42), (.29, .35), (.43, .28), (.62, .2), (.88, .14), (1.25, .09), (1.7, .05)):
        i = int(dl * size * SR); o[i:i + len(s)] += _lp(s, 3500) * a * wet
    return o
def _norm(x, peak=1.0): return x / (np.abs(x).max() + 1e-9) * peak


def _formant_voice(f0, dur, vowel="aa", vib=5.0):
    """Very simple formant synth: glottal pulse train through 3 band-passes."""
    t = _t(dur)
    f = f0 * (1 + 0.012 * np.sin(2 * np.pi * vib * t))
    ph = np.cumsum(f) / SR
    src = (ph % 1.0) * 2 - 1
    src = src - _lp(src, 300) * 0.3
    F = {"aa": (750, 1150, 2600), "oo": (350, 800, 2400), "ee": (300, 2300, 3000), "mm": (250, 900, 2200)}[vowel]
    s = sum(_bp(src, f_ * 0.85, f_ * 1.15) * a for f_, a in zip(F, (1.0, 0.6, 0.3)))
    return s


# ---------------------------------------------------------------- impacts
def taiko(g=1.0):
    t = _t(1.6)
    s = np.sin(2 * np.pi * (70 * np.exp(-t * 3) + 42) * t) * np.exp(-t * 4)
    s += _bp(_rng.standard_normal(len(t)), 80, 600) * np.exp(-t * 18) * 0.6
    return _norm(_verb(s, 0.5), 0.9) * g


def metal_hit(g=1.0):
    t = _t(3.0)
    s = sum(a * np.sin(2 * np.pi * f * t + _rng.uniform(0, 6)) * np.exp(-t * d) for f, a, d in
            ((311, 1, 1.2), (467, .7, 1.6), (733, .5, 2.2), (1187, .35, 3), (1709, .25, 4), (2633, .15, 6)))
    s += _hp(_rng.standard_normal(len(t)), 3000) * np.exp(-t * 30) * 0.4
    return _norm(_verb(s, 0.6), 0.7) * g


def tape_stop(x, dur=0.5):
    """Slow a sound to a halt (like a tape machine stopping)."""
    n = len(x); m = int(dur * SR)
    rate = np.linspace(1, 0.05, m)
    pos = np.cumsum(rate); pos = pos[pos < n - 1]
    return np.interp(pos, np.arange(n), x) * np.linspace(1, 0, len(pos))


def braam(dur=3.0, g=1.0):
    """New scare hit: taiko + metal clang + low 808 dive, tail tape-stops."""
    n = int(dur * SR); o = np.zeros(n + SR)
    tk = taiko(1.0); mh = metal_hit(0.8)
    o[:len(tk)] += tk[:len(o)]; o[:len(mh[:len(o)])] += mh[:len(o)]
    t = _t(dur)
    boom = np.sin(2 * np.pi * np.cumsum(55 * np.exp(-t * 1.5) + 28) / SR) * np.exp(-t * 1.2) * 0.9
    o[:n] += boom
    o = o[:n] * _env(n, 0.002, min(0.6, dur / 2))
    return _norm(o, 0.95) * g


def sub_drop(dur=2.0, g=1.0):
    t = _t(dur)
    s = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 2.2) + 22) / SR)
    s = np.tanh(s * 2.5) * np.exp(-t * 1.6)
    return _norm(s, 0.9) * g


def riser(dur=2.5, g=1.0):
    """Reverse piano cluster + rising 'aah' choir."""
    t = _t(dur)
    pn = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 1.6) for f in (110, 116.5, 164.8, 233.1, 246.9))
    pn = pn[::-1]
    ch = sum(_formant_voice(f, dur, "aa") for f in (220, 233, 311))
    ch *= np.linspace(0, 1, len(t)) ** 2
    s = pn * 0.6 + ch * 0.5 * np.linspace(0.3, 1, len(t))
    return _norm(s * _env(len(t), 0.05, 0.02), 0.8) * g


def pulse_beat(dur=8.0, bpm_start=70, bpm_end=140, g=1.0):
    """Ticking clock + a low synth pulse that speeds up (instead of the old thump)."""
    n = int(dur * SR); o = np.zeros(n); t = 0.0
    while t < dur - 0.1:
        k = t / dur; per = 60 / (bpm_start + (bpm_end - bpm_start) * k)
        i = int(t * SR); m = int(0.03 * SR)
        x = np.arange(m) / SR
        tick = _bp(_rng.standard_normal(m), 2500, 6000) * np.exp(-x * 160) * 0.5
        o[i:i + m] += tick[:max(0, n - i)]
        m2 = int(0.25 * SR); x2 = np.arange(m2) / SR
        pul = np.sin(2 * np.pi * 55 * x2) * np.exp(-x2 * 12) * (0.3 + 0.5 * k)
        o[i:i + m2] += pul[:max(0, n - i)]
        t += per / 2
    return o * g


def heartbeat_accel(dur=6.0, start_period=0.95, end_period=0.42, g=1.0):
    """Muffled heartbeat heard from inside the body + a shaky breath on every 3rd beat."""
    n = int(dur * SR); o = np.zeros(n); t = 0.0; k = 0
    while t < dur - 0.3:
        per = start_period + (end_period - start_period) * (t / dur)
        for dt, a in ((0, 1.0), (0.16, 0.65)):
            i = int((t + dt) * SR); m = int(0.22 * SR); x = np.arange(m) / SR
            b = np.sin(2 * np.pi * (48 + 20 * np.exp(-x * 30)) * x) * np.exp(-x * 16) * a
            o[i:i + m] += b[:max(0, n - i)]
        if k % 3 == 2:
            i = int((t + 0.1) * SR); m = int(0.6 * SR); x = np.arange(m) / SR
            br = _bp(_rng.standard_normal(m), 500, 2500) * np.sin(np.pi * x / 0.6) ** 2 * 0.08
            o[i:i + m] += br[:max(0, n - i)]
        t += per; k += 1
    return _lp(o, 900) * 1.4 * g


def reverse_whisper(dur=1.6, g=1.0):
    """A child humming three wrong notes (formant 'mm'), a little detuned, with breath."""
    notes = (392, 370, 349.2)
    seg = dur / 3; out = []
    for f in notes:
        v = _formant_voice(f, seg, "mm", vib=6.5) * _env(int(seg * SR), 0.05, 0.12)
        out.append(v)
    s = np.concatenate(out)
    s += _bp(_rng.standard_normal(len(s)), 1500, 6000) * 0.03
    return _norm(_verb(s, 0.7, 1.3)[:int(dur * SR * 1.6)], 0.5) * g


def glitch(dur=0.5, g=1.0):
    """Radio static burst with vinyl crackle and a stutter."""
    n = int(dur * SR)
    s = _bp(_rng.standard_normal(n), 800, 6000) * 0.6
    cr = np.zeros(n); idx = _rng.integers(0, n, 60); cr[idx] = _rng.uniform(-1, 1, 60)
    s += _hp(cr, 2000) * 2
    blk = int(0.04 * SR)
    for i in range(0, n - 2 * blk, blk * 2):
        s[i + blk:i + 2 * blk] = s[i:i + blk] * 0.8
    return _norm(s * _env(n, 0.005, 0.05), 0.6) * g


def music_box(dur=5.0, g=1.0, detune=0.03):
    """A slow, out-of-tune music box lullaby."""
    mel = (659.3, 587.3, 523.3, 587.3, 659.3, 659.3, 659.3, 587.3, 587.3, 587.3)
    n = int(dur * SR); o = np.zeros(n); per = dur / len(mel)
    for k, f in enumerate(mel):
        f *= 1 + _rng.uniform(-detune, detune)
        i = int(k * per * SR); m = int(1.8 * SR); x = np.arange(m) / SR
        tine = (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * f * 4.2 * x) * np.exp(-x * 8)) * np.exp(-x * 2.5)
        o[i:i + m] += tine[:max(0, n - i)] * 0.3
    o *= np.linspace(1, 0.6, n)
    return _verb(o, 0.5)[:n] * g


def dissonant_strings(dur=5.0, g=1.0):
    """Bowed-glass cluster with slow tremolo + the music box underneath."""
    t = _t(dur)
    s = sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * 0.3 * t) * 0.4) for f in (880, 932.3, 1046.5, 1108.7)) * 0.12
    s *= (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t))
    s = s * _env(len(t), 0.8, 1.2) + music_box(dur, 0.6)
    return s * g


def silence(dur):
    return np.zeros(int(dur * SR))


def dog_howl(dur=4.0, pitch=520, distance=0.6, g=1.0, seed=None):
    """Kit 2 replaces dogs with WIND that howls through the trees (a long, crying gust)."""
    r = np.random.default_rng(seed)
    t = _t(dur); u = t / dur
    f = pitch * (0.9 + 0.25 * np.sin(np.pi * u) + 0.03 * np.sin(2 * np.pi * r.uniform(0.6, 1.2) * t))
    nz = r.standard_normal(len(t))
    s = np.zeros(len(t))
    blk = 2400
    for i in range(0, len(t) - blk, blk):           # band-pass noise that glides (a whistling gust)
        fc = f[i]
        s[i:i + blk] = _bp(nz[i:i + blk + 0][:blk], fc * 0.92, fc * 1.08)
    s = _lp(s, 2600 - 1400 * distance) * np.sin(np.pi * u) ** 1.5
    s += _bp(r.standard_normal(len(t)), 150, 700) * 0.15 * np.sin(np.pi * u)
    return _norm(s, 0.5 - 0.25 * distance) * g


def dog_pack(dur=7.0, distance=0.7, g=1.0):
    out = np.zeros(int(dur * SR))
    for i, (st, p, ln) in enumerate(((0.0, 480, 4.5), (1.6, 620, 4.0), (3.0, 420, 4.0))):
        h = dog_howl(min(ln, dur - st), p, distance + 0.05 * i, seed=i + 5)
        a = int(st * SR); out[a:a + len(h)] += h
    return _norm(out, 0.5 - 0.25 * distance) * g


def bed(dur, seed=0):
    """Stereo background for a whole video: low 'oo' choir drone, slow breathing, faint whispers, distant metal groans.
    Returns (L, R)."""
    r = np.random.default_rng(seed)
    n = int(dur * SR); t = np.arange(n) / SR
    ch = np.zeros(n)
    seg = int(6 * SR)
    for i in range(0, n, seg):
        m = min(seg + SR, n - i)
        v = sum(_formant_voice(f, m / SR, "oo", vib=4) for f in (98, 146.8, 155.6))
        m = min(m, len(v))
        ch[i:i + m] += v[:m] * _env(m, 1.5, 1.5)
    ch = _lp(ch, 1200) * 0.08
    br = _bp(r.standard_normal(n), 400, 1800) * (np.sin(2 * np.pi * t / 4.5) ** 8) * 0.03
    L = ch + br; R = ch * 0.9 + np.roll(br, int(0.3 * SR))
    k = 5.0
    while k < dur - 3:
        g_ = metal_hit(0.25)
        gr = tape_stop(g_, 1.8)
        i = int(k * SR); m = min(len(gr), n - i)
        (L if r.random() < 0.5 else R)[i:i + m] += gr[:m] * 0.4
        k += r.uniform(9, 14)
    return L, R
