# Bongkar Benda — instruksi untuk Claude Code

Proyek video pendek "cara kerja benda raksasa" milik ALFA (terpisah dari Ruang Pikir, repo `fourtisf/ruangpikir`). Target akun TikTok/IG: @bongkarbenda (cek ketersediaan). Baca juga `README.md` dan `BRAND.md`. ALFA menulis dalam bahasa Indonesia santai; balas dalam bahasa Indonesia.

## Kalau ALFA minta "ide konten"
1. Pakai dan lengkapi `content/IDE_KONTEN.md` (tandai [x] yang sudah jadi). Usulkan 4–6 ide bernomor. Tiap ide berisi: judul layar "Benda, kok [hal ajaib]?", hook 0–3 dtk (kalimat + visual yang bergerak), visual 3D isometrik yang dibelah, fakta/sumber terverifikasi, dan alasan kenapa berpotensi viral. Beri satu rekomendasi.
2. Pola yang menang di genre ini (akun sejenis, Nov 2026): **objek/bangunan raksasa** yang dilihat semua orang tapi tak dipahami cara kerjanya (jembatan 1,8 jt, terowongan 1,4 jt, pesawat 997 rb, gedung 940 rb, kapal 641 rb views) jauh mengalahkan sains kecil sehari-hari (bau hujan, layar sentuh, file terhapus: 13–25 rb). Visual "dibelah" yang memperlihatkan isi sangat memuaskan. Judul 2–4 kata. Video bersambung (part 2) anjlok, jadi buat 1 video tuntas. Tokoh tidak wajib; objeknya bintangnya.
3. Utamakan objek yang dekat dengan penonton Indonesia (lift mal, KRL/MRT, kereta cepat Whoosh, jalan tol layang, bendungan, kapal feri, eskalator). Jangan meniru topik, naskah, nama, logo, atau tata letak akun lain.

## Kalau ALFA minta "buat video [topik]"
1. Riset fakta dulu (standar teknis, sumber resmi, sejarah terdokumentasi) dan catat di `content/EPxx_nama.md`. Angka hanya kalau terverifikasi; kisaran ditulis "≈".
2. Salin folder episode terakhir (`episodes/ep01_lift/`) jadi `episodes/epXX_nama/`, lalu tulis `vo.py` (7–9 kalimat, ±45 dtk): hook bahaya/kejutan → "Ini alasannya" (daftar 1-2-3) → satu adegan per alasan → cerita sejarah singkat (orang + tahun) → ajakan komentar "Benda apa yang mau kamu bongkar berikutnya?" → "Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu."
3. Jalankan `./voice.sh` (Gemini TTS voice **Puck**, 1 request, dipotong di jeda, `tighten.py 0.22`), lalu `python3 tools/transcribe.py episodes/epXX_nama`. Kalimat harus persis dan instruksi gaya tidak boleh terbaca. Kata pembuka yang kurang jelas (mis. "Ngerasa") ganti dengan yang jelas ("Kamu ngerasa").
4. Hitung `ANCHORS` sebanding durasi suara, cari jeda tiap baris untuk `PHRASES` (lihat episode 01), atur `GROUPS`, lalu gambar adegan di `episode.py` dengan `engine/iso.py` (balok, roda, tali, pegas, percikan) dan UI `engine/bb.py` (label penunjuk, kartu, chip, check).
5. Preview frame (`python3 episode.py preview t1 t2 ...`), perbaiki tabrakan, lalu `./build.sh` → `videos/bongkar-benda-epXX_nama.mp4` + `_tanpa-musik`.
6. QA wajib: `python3 tools/sheet.py video.mp4 sheet.png` (16 frame: tidak ada teks bertabrakan, **layar terisi penuh**), loudness ±−14 LUFS, `python3 tools/mixcheck.py video.mp4` (narasi jelas di atas musik).
7. Tulis copywriting di `content/EPxx_nama.md` (teks cover, caption TikTok & IG, komentar pin, judul Shorts), update `content/IDE_KONTEN.md`, commit, push, lalu kirim video ke ALFA.

## Aturan teknis
- Mesin: `engine/bb.py` + `engine/iso.py` (skia-python). Episode = folder di `episodes/` berisi `vo.py`, `episode.py`, `voice.sh`, `build.sh`. Contoh lengkap: `episodes/ep01_lift/`.
- Suara: Gemini TTS voice **Puck** (`BB_VOICE`), model `gemini-3.1-flash-tts-preview`, resep 1 request + dipotong di jeda (`engine/vo_full.py`) + `engine/tighten.py 0.22`. Durasi video 40–55 dtk. Contoh suara lain di `samples/suara/`.
- Visual: tema terang, isometrik 3D yang dibelah, judul hanya di adegan pertama, ilustrasi mengisi layar sampai ±y 1700 (jangan banyak ruang kosong), caption 56 px navy + kata kunci oranye di atas kartu putih transparan berpusat y 1495 (`CAP_Y`), chip/kartu adegan di atas y ±1370, satu ide per adegan, label penunjuk, outro logo + Follow. Hook bergerak sejak frame pertama. Tanpa titik-titik bokeh.
- Musik: lagu instrumental orisinal di `engine/audio.py` (C–G–Am–F, 108 BPM; `BB_BPM`/`BB_TR` untuk variasi). Jangan pakai lagu berhak cipta; sarankan lagu trending lewat aplikasi pada versi `_tanpa-musik` (suara asli 100%, lagu 10–15%).
- Model gambar Gemini butuh billing (Free Tier limit 0); tanpa billing semua digambar dengan kode.

## API key / rahasia
- `GEMINI_API_KEY` dibaca dari environment variable, file `.env` di root (tidak di-commit), atau network secret Claude Code untuk host `generativelanguage.googleapis.com` (header `x-goog-api-key`; `engine/gemini_tts.py` lalu memakai nilai pengganti dan proxy menyuntikkan key).
- Jangan pernah menulis key di file yang di-commit atau di chat. Sebelum commit: `git diff --cached | grep -E "AIza[0-9A-Za-z_-]{20,}"` harus kosong.
- Kuota gratis TTS terbatas (±3 request/menit). Kalau 429, tunggu atau ganti `GEMINI_TTS_MODEL`.
