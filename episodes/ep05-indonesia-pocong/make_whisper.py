# Makes p1/whisper.wav: the narrator-free whisper "Bayu..." (soft female voice, filtered, quiet).
import os, sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
from kokoro_onnx import Kokoro
TK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit")
k = Kokoro(os.path.join(TK, "models", "kokoro.onnx"), os.path.join(TK, "models", "voices.bin"))
a, sr = k.create("Bah-yoo...", voice="af_nicole", speed=0.6, lang="en-us")
a = sosfilt(butter(2, [700, 6000], btype="band", fs=sr, output="sos"), a)
a = a / np.abs(a).max() * 0.5
sf.write("p1/whisper.wav", a.astype(np.float32), sr); print("whisper", len(a) / sr)
