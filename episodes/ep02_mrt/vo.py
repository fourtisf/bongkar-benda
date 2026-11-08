import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi (DUR 42). Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Di atas terowongan ini ada jalan raya, gedung, dan ribuan mobil. Kok nggak ambruk? Ini alasannya.',
    'Pertama, mesin bor seberat lebih dari tiga ratus ton ini menahan tanah di depannya. Tanah galiannya ditekan balik, jadi dorongannya seimbang.',
    'Kedua, sambil maju, mesin ini langsung memasang cincin beton jadi dinding terowongan.',
    'Ketiga, celah di belakang cincin disuntik semen. Jadi tanah di atasnya nggak ikut turun.',
    'Idenya dari Marc Brunel. Tahun delapan belas dua puluh lima, dia menggali terowongan di bawah Sungai Thames pakai perisai besi.',
    'Di Jakarta, terowongan MRT terbaru bahkan ada yang sedalam dua puluh delapan meter.',
    'Benda apa yang mau kamu bongkar berikutnya? Tulis di komentar!',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 5.5, 12.5, 17.1, 21.95, 28.8, 33.4, 36.6]
LINES = list(zip(ANCHORS, TEXTS))
