import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi (DUR 42). Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Tengah jembatan ini nggak punya tiang sama sekali. Kok nggak ambruk ke laut? Ini alasannya.',
    'Pertama, kabel-kabel baja ini menarik jalan ke arah menara. Beratnya dibagi ke banyak kabel sekaligus.',
    'Kedua, menara meneruskan semua beban itu ke bawah, sampai ke pondasi di dasar laut.',
    'Ketiga, kabel di kiri dan kanan menara saling mengimbangi. Jadi menaranya tetap tegak.',
    'Idenya sudah digambar Fausto Veranzio tahun lima belas sembilan puluh lima: jembatan yang digantung rantai besi.',
    'Suramadu sendiri panjangnya lebih dari lima kilometer. Dan di bawahnya, kapal masih bisa lewat.',
    'Benda apa yang mau kamu bongkar berikutnya? Tulis di komentar!',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 6.715, 13.903, 19.476, 25.034, 31.188, 37.214, 40.495]
LINES = list(zip(ANCHORS, TEXTS))
