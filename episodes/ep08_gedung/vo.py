import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi. Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Tanah berguncang, gedung setinggi ratusan meter ini ikut bergoyang. Kok nggak roboh? Ini alasannya.',
    'Pertama, pondasinya tertanam dalam, sampai ke lapisan tanah yang keras.',
    'Kedua, gedungnya dirancang lentur. Saat gempa, ia bergoyang, bukan patah.',
    'Ketiga, ada peredam. Di Taipei seratus satu, bola baja seberat enam ratus enam puluh ton berayun melawan goyangan gedung.',
    'Ide gedung lentur dipelopori Kiyoshi Muto. Tahun sembilan belas enam puluh delapan, dia membangun gedung pencakar langit pertama di Jepang.',
    'Di Padang, bahkan ada gedung yang berdiri di atas bantalan karet peredam gempa.',
    'Benda apa yang mau kamu bongkar berikutnya? Tulis di komentar!',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 7.088, 11.998, 17.631, 25.796, 33.27, 37.976, 41.267]
LINES = list(zip(ANCHORS, TEXTS))
