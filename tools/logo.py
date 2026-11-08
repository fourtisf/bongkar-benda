#!/usr/bin/env python3
"""Logo profil Bongkar Benda (TikTok / Instagram / YouTube): kubus isometrik yang 'dibongkar' (tiga sisi terpisah)
di atas lingkaran oranye. Gambar logo (logo_disc, logo_cube) ada di engine/bb.py, sama dengan logo_mark() di outro video.
python3 tools/logo.py [folder_keluaran]      -> brand/ (default)
  profil_bongkar-benda.png        1080x1080, latar penuh (platform memotongnya jadi lingkaran) <- pakai ini
  profil_bongkar-benda_pop.png    varian dengan garis "pop" (lebih ramai, kurang jelas di ukuran sangat kecil)
  profil_bongkar-benda_navy.png   varian latar navy
  logo_bongkar-benda.png          lencana bulat transparan bercincin putih (untuk thumbnail/cover/watermark)
  cek_profil.png                  QA: potongan lingkaran + ukuran kecil (110/64/40 px) di latar terang & gelap"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'engine'))
import skia
from bb import col, P, font, logo_cube, logo_disc, C30, INK, WHITE, B   # gambar logo ada di mesin (sama dengan outro video)

S = 1080

def pops(cv, cx, cy, k):
    """garis "pop" di ujung luar tiap celah kubus (varian _pop)"""
    for (ex, ey), (dx, dy) in (((cx - k * C30, cy - k * 0.5), (-C30, -0.5)), ((cx + k * C30, cy - k * 0.5), (C30, -0.5)), ((cx, cy + k), (0, 1))):
        segs = [(0.24, 0.40, 0, 0)] + [(0.20, 0.33, -dy * sd, dx * sd) for sd in (-1, 1)]
        for a0, a1, nx, ny in segs:
            x0, y0 = ex + dx * k * a0 + nx * k * 0.12, ey + dy * k * a0 + ny * k * 0.12
            ln = skia.Path(); ln.moveTo(x0, y0)
            ln.lineTo(x0 + (dx + nx * 0.45) * k * (a1 - a0), y0 + (dy + ny * 0.45) * k * (a1 - a0))
            cv.drawPath(ln, P(col(WHITE, 0.95), stroke=k * 0.045))

def profile(navy=False, pop=False):
    """foto profil persegi berlatar penuh; kubus (heksagon ±62% diameter) aman di potongan lingkaran"""
    s = skia.Surface(S, S); cv = s.getCanvas(); c = S / 2
    logo_disc(cv, c, c, c, navy=navy, rect=skia.Rect(0, 0, S, S))
    k, gap = (250, 46) if pop else (280, 46)
    cy = c - gap * 0.25 + 6
    logo_cube(cv, c, cy, k, gap, navy=navy)
    if pop: pops(cv, c, cy, k)
    return s.makeImageSnapshot()

def badge():
    """lencana bulat transparan dengan cincin putih"""
    s = skia.Surface(S, S); cv = s.getCanvas(); cv.clear(skia.Color(0, 0, 0, 0))
    c = S / 2; r = S / 2 - 40
    cv.drawCircle(c, c + 14, r, P(col(INK, 0.35), blur=18))
    cv.drawCircle(c, c, r, P(col(WHITE)))
    logo_disc(cv, c, c, r - 22)
    logo_cube(cv, c, c - 42 * 0.25 + 6, 255, 42)
    return s.makeImageSnapshot()

def circle_crop(img, size):
    s = skia.Surface(size, size); cv = s.getCanvas(); cv.clear(skia.Color(0, 0, 0, 0))
    p = skia.Path(); p.addCircle(size / 2, size / 2, size / 2); cv.clipPath(p, doAntiAlias=True)
    cv.drawImageRect(img, skia.Rect(0, 0, size, size), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    return s.makeImageSnapshot()

def qa_sheet(imgs, names):
    """tiap varian: lingkaran besar + 110/64/40 px, di latar putih (TikTok) dan gelap (mode gelap)"""
    rowh, Wd = 360, 1500
    s = skia.Surface(Wd, rowh * len(imgs) + 40); cv = s.getCanvas(); cv.clear(skia.Color(255, 255, 255))
    for i, (img, nm) in enumerate(zip(imgs, names)):
        y = 20 + i * rowh
        cv.drawRect(skia.Rect(750, y, Wd, y + rowh - 20), P(col('#121212')))
        for x0 in (0, 750):
            cv.drawImage(circle_crop(img, 300), x0 + 20, y + 10)
            x = x0 + 360
            for sz in (110, 64, 40):
                cv.drawImage(circle_crop(img, sz), x, y + 140 - sz / 2); x += sz + 30
            cv.drawString(nm, x0 + 360, y + 300, font(B, 26), P(col('#888888')))
    return s.makeImageSnapshot()

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(root, 'brand')
    os.makedirs(out, exist_ok=True)
    v = {'profil_bongkar-benda.png': profile(), 'profil_bongkar-benda_pop.png': profile(pop=True),
         'profil_bongkar-benda_navy.png': profile(navy=True), 'logo_bongkar-benda.png': badge()}
    for name, img in v.items(): img.save(os.path.join(out, name), skia.kPNG)
    qa_sheet(list(v.values()), ['utama (oranye)', 'pop', 'navy', 'lencana transparan']).save(os.path.join(out, 'cek_profil.png'), skia.kPNG)
    print('Selesai:', out)
