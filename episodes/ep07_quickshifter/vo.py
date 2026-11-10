import os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'vo')
# anchor = waktu animasi. Angka & tahun ditulis dengan huruf supaya dibaca benar oleh TTS.
TEXTS = [
    'Motor ini ganti gigi tanpa tarik kopling, gasnya tetap dibuka. Kok giginya nggak patah? Ini alasannya.',
    'Pertama, ada sensor di batang pemindah gigi. Begitu kakimu menginjak tuas, sensor langsung tahu.',
    'Kedua, komputer motor memutus pengapian sesaat, cuma hitungan milidetik. Jadi gigi nggak lagi menahan tenaga mesin.',
    'Ketiga, di momen itu, gigi lama lepas dan gigi berikutnya langsung masuk. Pindah gigi jadi mulus tanpa kopling.',
    'Teknologi ini awalnya dibuat untuk balap motor, supaya ganti gigi lebih cepat dari pakai kopling.',
    'Sekarang, di Indonesia, motor sport dua ratus lima puluh cc pun sudah ada yang memakainya.',
    'Ini request dari kalian. Benda apa lagi yang mau kamu bongkar? Tulis di komentar!',
    'Follow Bongkar Benda, biar makin paham cara kerja benda di sekitarmu.',
]
ANCHORS = [0.15, 7.42, 13.817, 21.229, 28.142, 33.566, 38.858, 43.243]
LINES = list(zip(ANCHORS, TEXTS))
