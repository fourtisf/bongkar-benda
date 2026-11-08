#!/usr/bin/env python3
"""Pendengar AI untuk video jadi: narasi jelas di atas musik? ada klik/distorsi? nilai musik + transkrip.
python3 tools/mixcheck.py videos/bongkar-benda-ep01_lift.mp4"""
import base64, os, sys, subprocess, requests
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'engine')); import gemini_tts as g
wav = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-vn', '-ac', '1', '-ar', '16000', '-f', 'wav', '-'], capture_output=True).stdout
q = ('Ini audio video pendek berbahasa Indonesia: narasi + lagu instrumental latar + efek suara. Jawab ringkas: 1) Apakah narasi selalu jelas '
     'di atas musik (sebut detik kalau tertutup)? 2) Ada bunyi klik, distorsi, atau nada sumbang? 3) Nilai musik sebagai latar 0-10 dan suasananya. 4) Transkrip narasi.')
r = requests.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent', headers={'x-goog-api-key': g.api_key()},
                  json={'contents': [{'parts': [{'inline_data': {'mime_type': 'audio/wav', 'data': base64.b64encode(wav).decode()}}, {'text': q}]}]},
                  timeout=300, verify=os.environ.get('REQUESTS_CA_BUNDLE') or True)
js = r.json(); print(js['candidates'][0]['content']['parts'][0]['text'] if 'candidates' in js else f'HTTP {r.status_code} {str(js)[:300]}')
