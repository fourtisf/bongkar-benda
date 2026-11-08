#!/usr/bin/env bash
# Render episode (CRF 26). Suara yang sudah ada di vo/ dipakai; tambah --voice untuk membuat ulang suara (butuh GEMINI_API_KEY di .env root proyek).
set -e
cd "$(dirname "$0")"
NAME=$(basename "$PWD")
[ "$1" = "--voice" ] && ./voice.sh
python3 episode.py timeline timeline.json
python3 ../../engine/audio.py timeline.json audio.wav
MUSIC=0 python3 ../../engine/audio.py timeline.json audio_nomusic.wav
python3 episode.py video raw.mp4
for v in "" "_tanpa-musik"; do
  A=audio.wav; [ -n "$v" ] && A=audio_nomusic.wav
  ffmpeg -y -loglevel error -i raw.mp4 -i $A -af "loudnorm=I=-14:TP=-1.5:LRA=11" \
    -c:v libx264 -preset slow -crf 26 -tune animation -x264-params aq-mode=3 -pix_fmt yuv420p -profile:v high \
    -c:a aac -b:a 128k -ar 44100 -shortest -movflags +faststart ../../videos/bongkar-benda-${NAME}${v}.mp4
done
rm -f raw.mp4 audio.wav audio_nomusic.wav timeline.json
echo "Selesai: videos/bongkar-benda-${NAME}.mp4"
