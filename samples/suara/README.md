# Contoh suara Gemini TTS

Semua dibuat dengan model `gemini-3.1-flash-tts-preview` + gaya brand (`engine/gemini_tts.py` → `STYLE`), kalimat yang sama:
"Bendungan ini menahan miliaran liter air. Tapi dindingnya justru dibuat melengkung. Kok bisa nggak jebol? ..."

| File | Voice | Karakter | Status |
|---|---|---|---|
| `suara_Puck.mp3` | **Puck** | cowok, cerah & energik | ✅ **dipilih untuk Bongkar Benda** (`BB_VOICE=Puck`, bawaan) |
| `suara_Sadaltager.mp3` | Sadaltager | cowok, berwibawa ala narator dokumenter | cadangan |
| `suara_Laomedeia.mp3` | Laomedeia | cewek, ceria | cadangan |

Ganti suara untuk satu episode: `BB_VOICE=Sadaltager ./voice.sh`. Buat contoh suara lain:
`python3 engine/gemini_tts.py sample <Voice> contoh.wav "kalimat"`.
