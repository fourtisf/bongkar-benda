import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi. Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Kereta ini terbalik di atas kepala. Penumpangnya kok nggak jatuh? Ini alasannya.',
    'Pertama, rodanya menjepit rel dari tiga sisi: atas, samping, dan bawah. Jadi keretanya nggak bisa lepas.',
    'Kedua, di puncak, kereta melaju kencang. Badanmu justru tertekan ke kursi, bukan jatuh.',
    'Ketiga, putarannya nggak bulat sempurna. Atasnya sempit, bawahnya lebar, supaya badanmu nggak tertekan berlebihan.',
    'Roda penjepit dari bawah ini dipatenkan John Miller, tahun sembilan belas sembilan belas.',
    'Dulu, putaran pertama di Coney Island bentuknya bulat, dan penumpangnya sampai sakit leher.',
    'Benda apa yang mau kamu bongkar berikutnya? Tulis di komentar!',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 6.275, 13.804, 19.771, 26.783, 31.321, 36.559, 39.931]
LINES = list(zip(ANCHORS, TEXTS))
