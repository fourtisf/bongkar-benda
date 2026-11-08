#!/usr/bin/env python3
"""Logo profil Bongkar Benda (TikTok / Instagram / YouTube): kubus isometrik yang 'dibongkar' (tiga sisi terpisah)
di atas lingkaran oranye, motif yang sama dengan logo_mark() di engine/bb.py (outro video).
python3 tools/logo.py [folder_keluaran]      -> brand/ (default)
  profil_bongkar-benda.png        1080x1080, latar penuh (platform memotongnya jadi lingkaran) <- pakai ini
  profil_bongkar-benda_pop.png    varian dengan garis "pop" (lebih ramai, kurang jelas di ukuran sangat kecil)
  profil_bongkar-benda_navy.png   varian latar navy
  logo_bongkar-benda.png          lencana bulat transparan bercincin putih (untuk thumbnail/cover/watermark)
  cek_profil.png                  QA: potongan lingkaran + ukuran kecil (110/64/40 px) di latar terang & gelap"""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'engine'))
import skia
from bb import col, P, lg, rg, font, ORANGE, ORANGE_D, INK, WHITE, B

C30 = math.cos(math.radians(30))
S = 1080

def poly(pts):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    p.close(); return p

def cube(cv, cx, cy, k, gap, navy=False, pops=False):
    """kubus isometrik terbongkar: atas putih, kiri krem, kanan navy (di latar navy: kanan oranye)"""
    top = [(cx, cy - k), (cx + k * C30, cy - k * 0.5), (cx, cy), (cx - k * C30, cy - k * 0.5)]
    left = [(cx - k * C30, cy - k * 0.5), (cx, cy), (cx, cy + k), (cx - k * C30, cy + k * 0.5)]
    right = [(cx, cy), (cx + k * C30, cy - k * 0.5), (cx + k * C30, cy + k * 0.5), (cx, cy + k)]
    mv = lambda pts, dx, dy: [(x + dx, y + dy) for x, y in pts]
    faces = [  # (titik, gradasi, arah gradasi, kilau tepi)
        (mv(top, 0, -gap), [WHITE, '#EEF2F8'], (cx, cy - k, cx, cy), 0.9),
        (mv(left, -gap * C30, gap * 0.5), ['#FFE9D4', '#FFD3AC'], (cx - k * C30, cy - k * 0.5, cx, cy + k), 0.9),
        (mv(right, gap * C30, gap * 0.5), [ORANGE, ORANGE_D] if navy else [INK, '#22345C'], (cx + k * C30, cy - k * 0.5, cx, cy + k), 0.35),
    ]
    shade, sa = ('#050A18', 0.55) if navy else (INK, 0.30)
    for pts, *_ in faces:                                                     # bayangan lembut tiap sisi
        cv.drawPath(poly(mv(pts, 0, k * 0.07)), P(col(shade, sa), blur=k * 0.07))
    for pts, cs, (x0, y0, x1, y1), hla in faces:
        p = poly(pts); cv.drawPath(p, P(shader=lg(x0, y0, x1, y1, [col(cs[0]), col(cs[1])])))
        cv.save(); cv.clipPath(p, doAntiAlias=True)                           # kilau tipis di tepi atas sisi
        hl = skia.Path(); hl.moveTo(*pts[0]); hl.lineTo(*pts[1])
        cv.drawPath(hl, P(col(WHITE, hla), stroke=k * 0.04)); cv.restore()
    if pops:                                                                  # garis "pop" di ujung luar tiap celah
        for (ex, ey), (dx, dy) in (((cx - k * C30, cy - k * 0.5), (-C30, -0.5)), ((cx + k * C30, cy - k * 0.5), (C30, -0.5)), ((cx, cy + k), (0, 1))):
            segs = [(0.24, 0.40, 0, 0)]
            for sd in (-1, 1): segs.append((0.20, 0.33, -dy * sd, dx * sd))
            for a0, a1, nx, ny in segs:
                x0, y0 = ex + dx * k * a0 + nx * k * 0.12, ey + dy * k * a0 + ny * k * 0.12
                ln = skia.Path(); ln.moveTo(x0, y0)
                ln.lineTo(x0 + (dx + nx * 0.45) * k * (a1 - a0), y0 + (dy + ny * 0.45) * k * (a1 - a0))
                cv.drawPath(ln, P(col(WHITE, 0.95), stroke=k * 0.045))

def bg_disc(cv, cx, cy, r, navy=False, full=False):
    cs = [col('#2A3F6B'), col('#1A2A4C'), col(INK)] if navy else [col('#FFA352'), col(ORANGE), col(ORANGE_D)]
    sh = rg(cx - r * 0.35, cy - r * 0.45, r * 1.55, cs, [0, 0.55, 1])        # cahaya dari kiri atas
    if full: cv.drawRect(skia.Rect(0, 0, S, S), P(shader=sh))
    else: cv.drawCircle(cx, cy, r, P(shader=sh))

def profile(navy=False, pops=False):
    """foto profil persegi berlatar penuh; kubus (heksagon ±62% diameter) aman di potongan lingkaran"""
    s = skia.Surface(S, S); cv = s.getCanvas()
    bg_disc(cv, S / 2, S / 2, S / 2, navy, full=True)
    k, gap = (250, 46) if pops else (280, 46)
    cube(cv, S / 2, S / 2 - gap * 0.25 + 6, k, gap, navy, pops)
    return s.makeImageSnapshot()

def badge():
    """lencana bulat transparan dengan cincin putih"""
    s = skia.Surface(S, S); cv = s.getCanvas(); cv.clear(skia.Color(0, 0, 0, 0))
    c = S / 2; r = S / 2 - 40
    cv.drawCircle(c, c + 14, r, P(col(INK, 0.35), blur=18))
    cv.drawCircle(c, c, r, P(col(WHITE)))
    bg_disc(cv, c, c, r - 22)
    cube(cv, c, c - 42 * 0.25 + 6, 255, 42)
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
    v = {'profil_bongkar-benda.png': profile(), 'profil_bongkar-benda_pop.png': profile(pops=True),
         'profil_bongkar-benda_navy.png': profile(navy=True), 'logo_bongkar-benda.png': badge()}
    for name, img in v.items(): img.save(os.path.join(out, name), skia.kPNG)
    qa_sheet(list(v.values()), ['utama (oranye)', 'pop', 'navy', 'lencana transparan']).save(os.path.join(out, 'cek_profil.png'), skia.kPNG)
    print('Selesai:', out)
