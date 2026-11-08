#!/usr/bin/env python3
"""Gemini TTS helper (Bongkar Benda). Key: GEMINI_API_KEY dari environment atau file .env di root proyek. Needs generativelanguage.googleapis.com allowed.
python3 engine/gemini_tts.py sample <voice> <out.wav> "<text>"   -> satu klip contoh suara
python3 gemini_tts.py script <voice>                          -> full script into vo/lXX.wav + vo/lines.json (split by pauses)
"""
import os, sys, json, base64, requests, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
# Kunci & pengaturan dibaca dari environment, atau dari .env di folder repo (tidak ikut git),
# atau ~/.config/ruangpikir/gemini.env. Yang sudah ada di environment tidak ditimpa.
def _load_env():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # engine/ -> root proyek
    for p in (os.path.join(root, '.env'), os.path.expanduser('~/.config/bongkarbenda/gemini.env')):
        if not os.path.exists(p): continue
        for line in open(p):
            line = line.strip()
            if line.startswith('export '): line = line[7:].strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                if v.strip(): os.environ.setdefault(k.strip(), v.strip().strip('"\''))
_load_env()
MODEL = os.environ.get('GEMINI_TTS_MODEL', 'gemini-3.1-flash-tts-preview')
VOICE = os.environ.get('BB_VOICE', 'Puck')      # suara brand Bongkar Benda
STYLE = ("Bacakan dalam bahasa Indonesia santai, jelas, dan antusias, seperti kreator konten edukasi yang sedang membongkar cara kerja "
         "benda raksasa ke temannya. Terdengar kagum dan penasaran di pertanyaan, yakin dan seru saat menjelaskan. Tempo agak cepat dan energik.")

PROXY_KEY = 'DISUNTIK-OLEH-PROXY'
def api_key():
    """Urutan: env GEMINI_API_KEY -> file .env di root proyek -> nilai pengganti.
    Di sesi Claude Code cloud key boleh disimpan sebagai network secret untuk host generativelanguage.googleapis.com
    (header x-goog-api-key): proxy mengganti nilai pengganti ini dengan key asli, jadi key tidak perlu ada di file mana pun."""
    return os.environ.get('GEMINI_API_KEY') or PROXY_KEY

def tts(text, voice, style=STYLE):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent'
    body = {'contents': [{'parts': [{'text': f'{style}\n\n{text}'}]}],
            'generationConfig': {'responseModalities': ['AUDIO'],
                                 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}}}}
    r = requests.post(url, headers={'x-goog-api-key': api_key()}, json=body, timeout=300,
                      verify=os.environ.get('REQUESTS_CA_BUNDLE') or True)
    if r.status_code != 200:
        if r.status_code in (400, 401, 403) and api_key() == PROXY_KEY:
            raise SystemExit('GEMINI_API_KEY belum tersedia: isi .env (salin .env.example) atau simpan key sebagai network secret '
                             'generativelanguage.googleapis.com (header x-goog-api-key) di environment Claude Code.')
        raise SystemExit(f'HTTP {r.status_code}: {r.text[:500]}')
    js = r.json()
    if 'candidates' not in js: raise SystemExit('no candidates: ' + str(js)[:200])
    part = js['candidates'][0]['content']['parts'][0]['inlineData']
    pcm = np.frombuffer(base64.b64decode(part['data']), dtype=np.int16).astype(np.float32) / 32768
    rate = 24000
    if 'rate=' in part.get('mimeType', ''): rate = int(part['mimeType'].split('rate=')[1].split(';')[0])
    return resample_poly(pcm, 44100, rate).astype(np.float32)

def save(path, x): wavfile.write(path, 44100, (np.clip(x, -1, 1) * 32767).astype(np.int16))

def split_by_pauses(x, n):
    """cut x into n pieces at the n-1 longest silences"""
    win = 441; e = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode='same'))
    quiet = e < 0.012
    gaps, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if i > 0 and j < len(quiet): gaps.append((j - i, i, j))
            i = j
        else: i += 1
    gaps = sorted(sorted(gaps, reverse=True)[:n - 1], key=lambda g: g[1])
    cuts = [0] + [(g[1] + g[2]) // 2 for g in gaps] + [len(x)]
    out = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        seg = x[a:b]; idx = np.where(np.abs(seg) > 0.01)[0]
        if len(idx): seg = seg[max(0, idx[0] - 441): idx[-1] + 3500]
        out.append(seg)
    return out

if __name__ == '__main__':
    if sys.argv[1] == 'sample':
        save(sys.argv[3], tts(sys.argv[4], sys.argv[2]))
    elif sys.argv[1] == 'script':
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from vo import LINES, OUT
        text = '\n\n'.join(t for _, t in LINES)
        x = tts(text + '\n', sys.argv[2], STYLE + ' Beri jeda sekitar satu detik di antara setiap baris.')
        save(os.path.join(OUT, 'full.wav'), x)
        segs = split_by_pauses(x, len(LINES))
        meta = []
        for i, ((anchor, t), s) in enumerate(zip(LINES, segs)):
            p = os.path.join(OUT, f'l{i:02d}.wav'); save(p, s)
            meta.append({'i': i, 'anchor': anchor, 'text': t, 'file': p, 'dur': round(len(s) / 44100, 3)})
            print(f'{i:2d} {len(s)/44100:5.2f}s {t}')
        json.dump(meta, open(os.path.join(OUT, 'lines.json'), 'w'), indent=1)
