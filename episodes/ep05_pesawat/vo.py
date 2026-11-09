import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi. Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Pesawat ini disambar petir. Penumpangnya kesetrum nggak? Tenang, nggak. Ini alasannya.',
    'Pertama, kulit pesawat menghantarkan listrik. Arus petir mengalir di bagian luar, nggak masuk ke kabin.',
    'Kedua, petir biasanya menyambar di ujung, seperti moncong, lalu keluar lewat ujung lain, biasanya ekor.',
    'Ketiga, sistem bahan bakarnya dirancang supaya percikan petir nggak bisa menyulut uap bahan bakar.',
    'Prinsip ini dibuktikan Michael Faraday. Tahun delapan belas tiga puluh enam, dia menyetrum ruangan berlapis logam, dan di dalamnya nggak ada listrik.',
    'Rata-rata, pesawat komersial disambar petir sekitar sekali setahun.',
    'Benda apa yang mau kamu bongkar berikutnya? Tulis di komentar!',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 6.586, 13.145, 20.535, 26.715, 35.542, 40.222, 43.614]
LINES = list(zip(ANCHORS, TEXTS))
