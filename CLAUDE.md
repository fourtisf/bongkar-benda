# Bongkar Benda — instruksi untuk Claude Code

Proyek video pendek "cara kerja benda raksasa" milik ALFA (terpisah dari Ruang Pikir). Baca `README.md` dan `BRAND.md`.

- Mesin: `engine/bb.py` + `engine/iso.py` (skia-python). Episode = folder di `episodes/` dengan `vo.py`, `episode.py`, `voice.sh`, `build.sh`. Contoh lengkap: `episodes/ep01_lift/`.
- Suara: Gemini TTS voice **Puck** (`BB_VOICE`), resep 1 request + dipotong di jeda (`engine/vo_full.py`) + `engine/tighten.py 0.22`. Cek transkripsi tiap baris (instruksi gaya tidak boleh terbaca); durasi video 40–55 dtk.
- API key: `GEMINI_API_KEY` di `.env` root (tidak di-commit) atau environment. Jangan pernah menulis key ke file yang di-commit.
- Visual: tema terang, isometrik 3D yang dibelah, judul hanya di adegan pertama, ilustrasi mengisi layar sampai ±y 1700 (jangan banyak ruang kosong), caption 56 px navy + kata kunci oranye di atas kartu putih transparan berpusat y 1495 (`CAP_Y`), chip/kartu adegan di atas y ±1370, satu ide per adegan, label penunjuk, outro logo + Follow. Hook bergerak sejak frame pertama.
- Fakta harus terverifikasi (standar teknis, sejarah terdokumentasi); tulis sumber di `content/EPxx_*.md`. Jangan meniru nama/logo/tata letak/naskah akun lain.
- QA sebelum menyerahkan: contact sheet ±12–16 frame, tidak ada teks bertabrakan, loudness ±−14 LUFS, cek campuran suara-musik.
- Model gambar Gemini butuh billing; tanpa billing gambar semuanya dengan kode.
