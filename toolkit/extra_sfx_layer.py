"""Add a darker sound layer under an existing mix: low drone, distant dog howls, reverse whispers. usage: extra_sfx.py in.mp4 out.wav seed"""
import sys, subprocess, numpy as np, soundfile as sf
sys.path.insert(0, "/home/claude/ghosts-of-asia/toolkit")
import sfx
SR = sfx.SR
inp, out, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", inp, "-vn", "-ac", "2", "-ar", str(SR), "/tmp/orig.wav"], check=True)
a, _ = sf.read("/tmp/orig.wav")
N = len(a); t = np.arange(N) / SR; rng = np.random.default_rng(seed)
lay = np.zeros(N)
lay += (np.sin(2*np.pi*41*t) + 0.5*np.sin(2*np.pi*61.7*t + np.sin(2*np.pi*0.13*t))) * 0.035 * (0.7 + 0.3*np.sin(2*np.pi*0.05*t))
def put(x, s):
    i = int(s * SR); x = x[:max(0, N - i)]; lay[i:i + len(x)] += x
s = 2.0
while s < N / SR - 5:
    put(sfx.dog_howl(rng.uniform(3.4, 4.4), rng.uniform(440, 600), 0.8, seed=int(rng.integers(99)), g=0.5), s); s += rng.uniform(14, 19)
s = 6.0
while s < N / SR - 4:
    put(sfx.reverse_whisper(1.6, 0.35), s); s += rng.uniform(11, 16)
L = a[:, 0] + lay; R = a[:, 1] + lay[::-1] * 0 + lay
m = np.stack([L, R], 1); m /= max(1.0, np.abs(m).max() / 0.97)
sf.write(out, m.astype(np.float32), SR)
