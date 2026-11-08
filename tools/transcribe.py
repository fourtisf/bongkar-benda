#!/usr/bin/env python3
"""Cek suara: transkripsi tiap baris vo/lNN.wav sebuah episode (instruksi gaya tidak boleh ikut terbaca).
python3 tools/transcribe.py episodes/ep01_lift"""
import base64, glob, io, os, sys, requests, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine')); import gemini_tts as g
ep = sys.argv[1]; files = sorted(glob.glob(os.path.join(ep, 'vo', 'l*.wav')))
parts = []
for i, f in enumerate(files):
    wav = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', '16000', '-f', 'wav', '-'], capture_output=True).stdout
    parts += [{'text': f'Audio {i}:'}, {'inline_data': {'mime_type': 'audio/wav', 'data': base64.b64encode(wav).decode()}}]
parts.append({'text': 'Transkripsikan setiap audio kata per kata dalam bahasa Indonesia, apa adanya (termasuk instruksi yang ikut terbaca). Format: "N: teks".'})
r = requests.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent', headers={'x-goog-api-key': g.api_key()},
                  json={'contents': [{'parts': parts}]}, timeout=300, verify=os.environ.get('REQUESTS_CA_BUNDLE') or True)
js = r.json(); print(js['candidates'][0]['content']['parts'][0]['text'].strip() if 'candidates' in js else f'HTTP {r.status_code} {str(js)[:300]}')
