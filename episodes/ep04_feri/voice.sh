#!/usr/bin/env bash
# Suara episode (voice Puck, gemini-3.1-flash-tts-preview, 1 request, dipotong di jeda). Cek transkripsinya setelah selesai.
set -e
cd "$(dirname "$0")"
python3 ../../engine/vo_full.py
python3 ../../engine/tighten.py 0.22
