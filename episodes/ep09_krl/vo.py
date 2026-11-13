import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi. Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Kereta nggak punya setir, dan rodanya nyatu sama poros. Kok bisa belok tanpa keluar rel? Ini alasannya.',
    'Pertama, roda kereta itu nggak datar. Bentuknya miring, kayak kerucut.',
    'Saat belok, roda luar menggelinding di bagian yang lebih besar, jadi menempuh jarak lebih jauh. Keretanya pun belok sendiri.',
    'Kedua, ada bibir roda di sisi dalam. Ini pengaman terakhir kalau rodanya bergeser terlalu jauh.',
    'Ketiga, di tikungan, rel bagian luar dibuat lebih tinggi. Kereta jadi sedikit miring, melawan dorongan ke luar.',
    'Kereta listrik pertama di Indonesia melaju tahun sembilan belas dua puluh lima, dari Tanjung Priok ke Jatinegara.',
    'Sekarang, sekitar sejuta orang naik KRL Jabodetabek setiap hari.',
    'Kirim ke teman yang tiap hari naik KRL. Benda apa yang mau kamu bongkar berikutnya?',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 7.312, 11.947, 19.383, 25.554, 32.608, 39.066, 44.11, 48.771]
LINES = list(zip(ANCHORS, TEXTS))
