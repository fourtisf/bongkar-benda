import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi (DUR 42). Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Kalau kabel lift putus, kamu bakal jatuh? Tenang, hampir nggak mungkin. Ini alasannya.',
    'Pertama, lift digantung beberapa tali baja sekaligus. Dan menurut standar Eropa, tiap tali minimal dua belas kali lebih kuat dari bebannya.',
    'Kedua, ada beban penyeimbang di sisi lain. Jadi mesinnya nggak perlu kerja berat.',
    'Ketiga, rem darurat. Kalau lift meluncur kelewat cepat, rem ini langsung mencengkeram rel, dan lift berhenti.',
    'Idenya dari Elisha Otis. Tahun delapan belas lima puluh empat, dia menyuruh orang memotong tali liftnya sendiri. Liftnya cuma turun sedikit, lalu tertahan.',
    'Kalau semuanya gagal pun, di dasar lubang lift masih ada peredam kejut.',
    'Benda apa yang mau kamu bongkar berikutnya? Tulis di komentar!',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 5.85, 12.96, 17.0, 22.76, 30.34, 33.72, 36.6]
LINES = list(zip(ANCHORS, TEXTS))
