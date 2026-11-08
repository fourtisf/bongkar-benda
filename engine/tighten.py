#!/usr/bin/env python3
"""Pendekkan jeda panjang DI DALAM tiap kalimat (bagian sunyi > CAP detik dipangkas jadi CAP), kecepatan bicara tidak diubah.
Aman dijalankan berulang. python3 tighten.py [cap=0.30]  ->  vo/lNN.wav + lines.json diperbarui"""
import json, os, sys
import numpy as np
import scipy.io.wavfile as wf
HERE = os.getcwd()   # jalankan dari folder episode
CAP = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30
meta = json.load(open(os.path.join(HERE, 'vo', 'lines.json'))); saved = 0
for m in meta:
    p = os.path.join(HERE, m['file']); sr, x = wf.read(p); x = x.astype(np.float32) / 32768
    e = np.sqrt(np.convolve(x ** 2, np.ones(441) / 441, mode='same')); quiet = e < 0.012
    keep, i, last, xf = [], 0, 0, int(0.01 * sr)
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if i > 0 and j < len(quiet) and (j - i) / sr > CAP:
                a = i + int(CAP * sr / 2); b = j - int(CAP * sr / 2)        # buang bagian tengah jeda
                keep.append(x[last:a]); last = b
            i = j
        else: i += 1
    keep.append(x[last:])
    y = keep[0]
    for seg in keep[1:]:                                                    # sambung dengan crossfade 10 ms
        n = min(xf, len(y), len(seg)); w = np.linspace(0, 1, n)
        y = np.concatenate([y[:len(y) - n], y[len(y) - n:] * (1 - w) + seg[:n] * w, seg[n:]])
    saved += (len(x) - len(y)) / sr
    wf.write(p, sr, (np.clip(y, -1, 1) * 32767).astype(np.int16)); m['dur'] = round(len(y) / sr, 3)
json.dump(meta, open(os.path.join(HERE, 'vo', 'lines.json'), 'w'), indent=1)
print(f'jeda dipendekkan, hemat {saved:.1f} dtk')
