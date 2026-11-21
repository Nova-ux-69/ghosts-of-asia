#!/usr/bin/env bash
# One-time setup in a fresh session: Python packages + narrator voice model.
set -e
TK="$(cd "$(dirname "$0")" && pwd)"
pip install --break-system-packages -q kokoro-onnx soundfile scipy pillow numpy
mkdir -p "$TK/models"
[ -f "$TK/models/kokoro.onnx" ] || curl -sSL -o "$TK/models/kokoro.onnx" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
[ -f "$TK/models/voices.bin" ] || curl -sSL -o "$TK/models/voices.bin" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
which ffmpeg >/dev/null || (apt-get install -y -qq ffmpeg >/dev/null 2>&1 || true)
fc-list | grep -qi "Lora" || echo "WARNING: Lora font missing (expected /usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf)"
echo "setup ok"
