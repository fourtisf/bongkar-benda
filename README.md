# Bongkar Benda

Video pendek 9:16 (TikTok/Reels/Shorts, 40–55 detik) yang **membongkar cara kerja benda & bangunan raksasa**: ilustrasi isometrik 3D yang dibelah, semua bagian bergerak, narasi Gemini TTS (voice **Puck**), lagu instrumental orisinal.

## Struktur
| Folder | Isi |
|---|---|
| `engine/` | Mesin video bersama: `bb.py` (tema terang, judul, caption, kamera, render), `iso.py` (balok/roda/tali/pegas isometrik), `audio.py` (SFX + lagu orisinal + ducking), `gemini_tts.py`, `vo_full.py`, `tighten.py`, `fonts/` |
| `episodes/epXX_nama/` | `vo.py` (naskah + anchor), `episode.py` (adegan), `voice.sh`, `build.sh`, `vo/` (suara) |
| `videos/` | Hasil render: `bongkar-benda-epXX_nama.mp4` + versi `_tanpa-musik` |
| `content/` | Copywriting per episode + bank ide |
| `samples/suara/` | Contoh suara Gemini (Puck = dipilih, Sadaltager, Laomedeia) |
| `tools/` | QA: `transcribe.py` (cek suara per baris), `mixcheck.py` (pendengar AI untuk video jadi), `sheet.py` (contact sheet) |

## Pakai
```bash
cp .env.example .env && chmod 600 .env     # isi GEMINI_API_KEY (key yang sama dengan Ruang Pikir boleh)
pip install -r requirements.txt             # + ffmpeg
cd episodes/ep01_lift
./build.sh            # render dengan suara yang sudah ada
./build.sh --voice    # buat ulang suara (1 request TTS), lalu render
python3 episode.py preview 0.5 3 12   # cek frame (waktu animasi) -> preview/
```
Episode baru: salin folder episode terakhir, ganti `vo.py` (naskah), jalankan `./voice.sh`, cek transkripsi, atur `ANCHORS`/`PHRASES`/`GROUPS` ke jeda suara, gambar adegan di `episode.py`.

## API key Gemini (aman, tidak pernah di-commit)
Key yang sama dengan Ruang Pikir boleh dipakai. Pilih salah satu:
1. **Laptop / VPS:** `cp .env.example .env && chmod 600 .env`, lalu isi `GEMINI_API_KEY=...`. File `.env` ada di `.gitignore`, jadi tidak ikut ter-push.
2. **Claude Code cloud (disarankan):** simpan key sebagai *network secret* di pengaturan environment untuk host `generativelanguage.googleapis.com`, header `x-goog-api-key`. Proxy menyuntikkan key ke setiap request, jadi tidak perlu `.env` sama sekali (`engine/gemini_tts.py` otomatis memakai nilai pengganti).
3. Atau environment variable `GEMINI_API_KEY`.

Jangan pernah menulis key di file yang di-commit (termasuk repo private): key di riwayat git sulit dihapus dan bisa dibekukan Google kalau bocor.

## Catatan
- Model gambar Gemini (`gemini-3-pro-image`, dll.) **butuh billing** (Free Tier limit 0). Episode 01 digambar 100% dengan kode.
