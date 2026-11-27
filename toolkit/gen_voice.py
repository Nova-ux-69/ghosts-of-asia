import json, os, sys, numpy as np, soundfile as sf
sys.path.insert(0, os.getcwd())
_TK = os.path.dirname(os.path.abspath(__file__))
from kokoro_onnx import Kokoro
from script_v import PARTS
try:
    from script_v import SAY          # optional: {word: how the narrator should say it}; captions keep the spelling
except ImportError:
    SAY = {}
k = Kokoro(os.path.join(_TK, "models", "kokoro.onnx"), os.path.join(_TK, "models", "voices.bin")); SR = 24000; GAP = 0.35
for part, scenes in PARTS.items():
    os.makedirs(f"{part}/vo", exist_ok=True); timing = []
    for sid, lines, hold, slow in scenes:
        parts = [np.zeros(int(0.25 * SR))]; caps = []; t = 0.25
        for ln in lines:
            spoken = ln
            for w_, s_ in SAY.items():
                spoken = spoken.replace(w_, s_)
            a, sr = k.create(spoken, voice=os.environ.get("VOICE", "am_puck"), speed=(0.86 if slow else 0.95) * float(os.environ.get("VSPEED", "1")), lang=os.environ.get("VLANG", "en-us"))
            d = len(a) / SR; caps.append([ln, round(t, 3), round(t + d, 3)])
            parts += [a, np.zeros(int(GAP * SR))]; t += d + GAP
        parts.append(np.zeros(int(hold * SR)))
        audio = np.concatenate(parts).astype(np.float32)
        sf.write(f"{part}/vo/{sid}.wav", audio, SR)
        timing.append({"id": sid, "dur": len(audio) / SR, "caps": caps})
    json.dump(timing, open(f"{part}/timing.json", "w"), indent=1)
    print(part, [(x["id"], round(x["dur"], 1)) for x in timing], "total", round(sum(x["dur"] for x in timing), 1))
