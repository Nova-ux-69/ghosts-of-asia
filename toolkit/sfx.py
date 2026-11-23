"""Scary sound effects for Ghosts of Asia (numpy only). All return mono float arrays at SR.

Use in an episode's sound script:  import sys; sys.path.insert(0, TOOLKIT); from sfx import *
Typical scare: riser(2.5) -> silence(0.4) -> braam() + sub_drop() + glitch(), with heartbeat_accel() under the build-up.
"""
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

SR = 24000
_rng = np.random.default_rng(11)


def _t(d): return np.arange(int(d * SR)) / SR
def _env(n, a, r):
    e = np.ones(n); ai, ri = int(a * SR), int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e
def _bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], btype="band", fs=SR, output="sos"), x)
def _lp(x, f): return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)


def braam(dur=3.0, g=1.0):
    """Trailer-style brass hit: detuned saws around low A, fast attack, long decay."""
    t = _t(dur); s = np.zeros_like(t)
    for f in (55, 55.6, 82.4, 110.2, 164.2):
        ph = 2 * np.pi * f * t
        s += 2 * ((ph / (2 * np.pi)) % 1) - 1
    s = _lp(s, 900) * np.minimum(1, t / 0.02) * np.exp(-t * 1.1)
    return s / np.abs(s).max() * 0.55 * g


def sub_drop(dur=2.0, g=1.0):
    """Deep falling boom you feel more than hear."""
    t = _t(dur)
    return np.sin(2 * np.pi * np.cumsum(30 + 90 * np.exp(-t * 4)) / SR) * np.exp(-t * 1.8) * 0.7 * g


def riser(dur=2.5, g=1.0):
    """Rising noise + pitch sweep that builds tension and stops dead (put the scare right after)."""
    t = _t(dur); u = t / dur
    noise = _bp(_rng.standard_normal(len(t)), 600, 6000) * u ** 2
    sweep = np.sin(2 * np.pi * np.cumsum(200 + 1600 * u ** 2) / SR) * u ** 3
    return (0.25 * noise + 0.18 * sweep) * g


def pulse_beat(dur=8.0, bpm_start=70, bpm_end=140, g=1.0):
    """Low tribal/drum pulse that speeds up (the 'beat' under a build-up)."""
    n = int(dur * SR); out = np.zeros(n); t0 = 0.0
    while t0 < dur:
        u = t0 / dur; bpm = bpm_start + (bpm_end - bpm_start) * u
        k = int(t0 * SR); m = min(int(0.35 * SR), n - k)
        tt = np.arange(m) / SR
        hit = np.sin(2 * np.pi * (48 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9)
        hit += _bp(_rng.standard_normal(m), 80, 400) * np.exp(-tt * 25) * 0.4
        out[k:k + m] += hit * (0.5 + 0.5 * u)
        t0 += 60 / bpm
    return out * 0.45 * g


def heartbeat_accel(dur=6.0, start_period=0.95, end_period=0.42, g=1.0):
    n = int(dur * SR); out = np.zeros(n); t0 = 0.0
    while t0 < dur - 0.3:
        u = t0 / dur; per = start_period + (end_period - start_period) * u
        for off, a in ((0, 1.0), (0.22, 0.7)):
            k = int((t0 + off) * SR); m = min(int(0.25 * SR), n - k)
            if m <= 0: continue
            tt = np.arange(m) / SR
            out[k:k + m] += np.sin(2 * np.pi * (55 - 20 * tt / 0.25) * tt) * np.exp(-tt * 18) * 0.45 * a
        t0 += per
    return out * g


def reverse_whisper(dur=1.6, g=1.0):
    """Breathy whisper-like noise, played backwards (sucks in toward the scare)."""
    t = _t(dur)
    s = _bp(_rng.standard_normal(len(t)), 1500, 5500) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t) ** 2)
    s = s * _env(len(t), 0.05, 0.6)
    return s[::-1] * 0.22 * g


def glitch(dur=0.5, g=1.0):
    """Digital stutter/static burst for a flicker or a teleporting ghost."""
    n = int(dur * SR); out = np.zeros(n); k = 0
    while k < n:
        m = int(_rng.uniform(0.015, 0.06) * SR)
        if _rng.random() < 0.6:
            out[k:k + m] = _rng.standard_normal(min(m, n - k)) * _rng.uniform(0.2, 0.6)
        k += m
    return _bp(out, 300, 8000) * 0.5 * g


def dissonant_strings(dur=5.0, g=1.0):
    """High screeching cluster (like violins scraping) for a reveal."""
    t = _t(dur); s = np.zeros_like(t)
    for f in (1661, 1760, 1865, 1976):
        s += np.sin(2 * np.pi * f * t + 3 * np.sin(2 * np.pi * 6.3 * t))
    return s * np.minimum(1, t / 0.08) * np.exp(-t * 0.7) * 0.05 * g


def silence(dur):
    return np.zeros(int(dur * SR))


def dog_howl(dur=4.0, pitch=520, distance=0.6, g=1.0, seed=None):
    """A lonely dog howling far away: rises in pitch, holds with a wobble, then falls and fades.
    distance 0 = close, 1 = very far (darker, quieter, more echo). Layer 1-3 howls with different pitch/seed for a pack."""
    rng = np.random.default_rng(seed)
    t = _t(dur); u = t / dur
    contour = pitch * (0.62 + 0.38 * np.minimum(1, u / 0.18) ** 0.6 - 0.22 * np.clip((u - 0.72) / 0.28, 0, 1) ** 1.5)
    contour *= 1 + 0.018 * np.sin(2 * np.pi * (5.2 + rng.uniform(-0.6, 0.6)) * t) * np.minimum(1, u / 0.3)
    ph = 2 * np.pi * np.cumsum(contour) / SR
    s = np.sin(ph) + 0.45 * np.sin(2 * ph + 0.3) + 0.18 * np.sin(3 * ph + 1.1) + 0.06 * np.sin(4 * ph)
    s += 0.05 * _bp(rng.standard_normal(len(t)), 300, 2500)          # breath
    s = _bp(s, 250, 3200 - 2000 * distance)
    env = np.minimum(1, u / 0.12) * np.clip((1 - u) / 0.25, 0, 1) ** 1.3
    s *= env
    # echo off buildings / trees: a few decaying delayed copies
    out = s.copy()
    for k, (dly, a) in enumerate(((0.19, 0.45), (0.37, 0.3), (0.61, 0.2), (0.9, 0.12))):
        n = int(dly * SR * (0.6 + distance)); out[n:] += s[:-n] * a * (0.4 + distance)
    out = out / (np.abs(out).max() + 1e-9)
    return out * (0.5 - 0.3 * distance) * g


def dog_pack(dur=7.0, distance=0.7, g=1.0):
    """2-3 dogs howling one after another in the distance (classic 'something is coming' sound)."""
    out = np.zeros(int(dur * SR))
    for i, (st, p, ln) in enumerate(((0.0, 520, 4.2), (1.3, 610, 3.6), (2.6, 470, 4.0))):
        h = dog_howl(min(ln, dur - st), p, distance + 0.08 * i, seed=i)
        a = int(st * SR); out[a:a + len(h)] += h * (1 - 0.2 * i)
    return out / (np.abs(out).max() + 1e-9) * (0.5 - 0.3 * distance) * g
