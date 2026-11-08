import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi. Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Kapal ini dari baja, beratnya ribuan ton. Kok bisa ngapung? Ini alasannya.',
    'Pertama, lambungnya berongga, isinya udara. Jadi kalau dirata-rata, kapal ini lebih ringan dari air.',
    'Kedua, kapal menyingkirkan banyak air. Air itu mendorong balik ke atas, sama kuat dengan berat kapal.',
    'Ketiga, lambungnya dibagi sekat kedap air. Kalau satu ruang bocor, kapal tetap mengapung.',
    'Sejak tahun delapan belas tujuh puluh enam, berkat Samuel Plimsoll, kapal wajib punya garis muat: batas aman muatan.',
    'Di Merak sampai Bakauheni, puluhan kapal feri bolak-balik siang dan malam.',
    'Benda apa yang mau kamu bongkar berikutnya? Tulis di komentar!',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 6.72, 14.158, 21.131, 26.98, 34.068, 38.692, 42.247]
LINES = list(zip(ANCHORS, TEXTS))
