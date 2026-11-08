#!/usr/bin/env python3
"""Suara episode Bongkar Benda: voice Puck (BB_VOICE), model gemini-3.1-flash-tts-preview, instruksi gaya brand,
semua kalimat dalam 1 request, lalu dipotong di jeda terpanjang. Jalankan dari folder episode (berisi vo.py).
python3 vo_full.py [--split-only]   ->  vo/full.wav, vo/lNN.wav, vo/lines.json"""
import os, sys, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.getcwd())
os.environ.setdefault('GEMINI_TTS_MODEL', 'gemini-3.1-flash-tts-preview')
import gemini_tts as g
g.MODEL = os.environ['GEMINI_TTS_MODEL']
from vo import LINES, OUT, HERE
STYLE = g.STYLE
def split_lines(x, texts, sr=44100):
    """potong di jeda: pilih len(texts)-1 jeda yang panjang DAN membuat durasi tiap potongan sebanding dengan panjang
    kalimatnya (jeda di dalam kalimat, mis. setelah "Hasilnya?", sering sama panjang dengan jeda antarkalimat)"""
    e = np.sqrt(np.convolve(x ** 2, np.ones(441) / 441, mode='same')); quiet = e < 0.012
    gaps, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if i > 0 and j < len(quiet) and j - i > 0.12 * sr: gaps.append(((i + j) // 2, (j - i) / sr))
            i = j
        else: i += 1
    n, T = len(texts), len(x); ch = np.array([len(t) for t in texts], float); E = ch / ch.sum() * T
    m = len(gaps); NEG = -1e9
    best = np.full((n, m), NEG); prev = np.zeros((n, m), int)
    cost = lambda a, b_, k: -abs(np.log(max(b_ - a, 1) / E[k]))
    for j in range(m): best[1, j] = cost(0, gaps[j][0], 0) + 2 * gaps[j][1]
    for k in range(2, n):
        for j in range(m):
            for i in range(j):
                if best[k - 1, i] <= NEG: continue
                v = best[k - 1, i] + cost(gaps[i][0], gaps[j][0], k - 1) + 2 * gaps[j][1]
                if v > best[k, j]: best[k, j], prev[k, j] = v, i
    j = int(np.argmax([best[n - 1, jj] + cost(gaps[jj][0], T, n - 1) for jj in range(m)]))
    cuts = []
    for k in range(n - 1, 0, -1): cuts.append(gaps[j][0]); j = prev[k, j]
    cuts = [0] + cuts[::-1] + [T]; out = []
    for a, b_ in zip(cuts[:-1], cuts[1:]):
        seg = x[a:b_]; idx = np.where(np.abs(seg) > 0.01)[0]
        if len(idx): seg = seg[max(0, idx[0] - 441): idx[-1] + 3500]
        out.append(seg)
    return out

if '--split-only' in sys.argv:          # potong ulang vo/full.wav tanpa request TTS baru
    import scipy.io.wavfile as wf
    _, x = wf.read(os.path.join(OUT, 'full.wav')); x = x.astype(np.float32) / 32768
else:
    text = '\n\n'.join(t for _, t in LINES)
    x = None
    for attempt in range(5):
        try:
            x = g.tts(text + '\n', g.VOICE, STYLE + ' Beri jeda sekitar satu detik di antara setiap baris.'); break
        except SystemExit as e:
            print('ulang:', str(e)[:200], flush=True); time.sleep(30 + 20 * attempt)
    if x is None: sys.exit('gagal membuat suara')
    g.save(os.path.join(OUT, 'full.wav'), x)
segs = split_lines(x, [t for _, t in LINES])
meta = []
for i, ((anchor, t), s) in enumerate(zip(LINES, segs)):
    s = s.copy(); fi, fo = min(220, len(s) // 4), min(1300, len(s) // 4)   # fade 5 ms / 30 ms: tanpa bunyi klik
    s[:fi] *= np.linspace(0, 1, fi); s[len(s) - fo:] *= np.linspace(1, 0, fo)
    p = os.path.join(OUT, f'l{i:02d}.wav'); g.save(p, s)
    meta.append({'i': i, 'anchor': anchor, 'text': t, 'file': os.path.relpath(p, HERE), 'dur': round(len(s) / 44100, 3)})
    print(f'{i:2d} {len(s) / 44100:5.2f}s ({len(t) / max(len(s) / 44100, 0.01):4.1f} kar/dtk) {t}')
json.dump(meta, open(os.path.join(OUT, 'lines.json'), 'w'), indent=1)
print('total', round(len(x) / 44100, 2), 's, model', g.MODEL)
