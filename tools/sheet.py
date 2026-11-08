#!/usr/bin/env python3
"""Contact sheet QA dari video jadi (default 16 frame merata).  python3 tools/sheet.py video.mp4 sheet.png [n]"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
v, out = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 16
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v], capture_output=True, text=True).stdout)
tw, th, cols = 432, 768, 4; rows = (n + cols - 1) // cols; S = Image.new('RGB', (cols * tw, rows * th), 'black'); d = ImageDraw.Draw(S)
with tempfile.TemporaryDirectory() as tmp:
    for i in range(n):
        t = dur * (i + 0.5) / n; f = os.path.join(tmp, f'{i}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', v, '-frames:v', '1', f])
        im = Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS); S.paste(im, ((i % cols) * tw, (i // cols) * th))
        d.text(((i % cols) * tw + 8, (i // cols) * th + 8), f'{t:.1f}s', fill='red')
S.save(out); print(out)
