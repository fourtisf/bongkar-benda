#!/usr/bin/env python3
"""Bongkar Benda #02: 'Terowongan MRT, kok nggak ambruk?'
Potongan kota isometrik (jalan raya, gedung, mobil) dengan terowongan MRT di bawahnya. Hook: tanah retak di atas terowongan, cincin beton menahan.
Alasan 1: mesin bor EPB (kepala bor berputar, ruang tanah, ulir pembuang, tekanan seimbang; TBM MRT Jakarta Fase 1: 323 ton, diameter 6,7 m).
Alasan 2: lengan pemasang memasang segmen beton jadi cincin, mesin maju. Alasan 3: celah di luar cincin disuntik semen (grouting), jalan tetap rata.
Sejarah: Marc Brunel, perisai terowongan, Thames Tunnel London (mulai 1825). Penutup: terowongan MRT Jakarta Fase 2A sedalam 28 m. Sumber: content/EP02_mrt.md
python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, YELLOW, RED, WHITE, CREAM, CREAM_D, text_c, mono, card, chip, label, check, logo_mark)
from iso import Iso, tone, quad, box, shadow, poly

bb.TITLE = ('Terowongan MRT,', 'kok nggak ambruk?'); bb.TITLE_OUT = 5.2
bb.GROUPS = [(0.0, 5.5, 'A'), (5.5, 12.5, 'B'), (12.5, 17.1, 'C'), (17.1, 21.95, 'D'), (21.95, 28.8, 'E'),
             (28.8, 33.4, 'F'), (33.4, 36.6, 'G'), (36.6, 42.0, 'J')]
bb.PHRASES = [(0.15, 'Di atas [terowongan] ini'), (1.41, 'ada [jalan raya], [gedung],'), (2.4, 'dan [ribuan mobil].'), (3.89, 'Kok nggak [ambruk]?'), (4.66, 'Ini [alasannya].'),
              (5.5, '[Pertama],'), (6.23, 'mesin bor seberat'), (7.31, '[lebih dari 300 ton] ini'), (8.33, '[menahan tanah] di depannya.'),
              (9.7, 'Tanah galiannya [ditekan balik],'), (10.97, 'jadi dorongannya [seimbang].'),
              (12.5, '[Kedua],'), (13.05, 'sambil maju,'), (13.86, 'mesin ini langsung memasang [cincin beton]'), (15.43, 'jadi [dinding terowongan].'),
              (17.1, '[Ketiga],'), (17.86, 'celah di belakang cincin'), (18.95, '[disuntik semen].'), (19.69, 'Jadi tanah di atasnya'), (20.7, '[nggak ikut turun].'),
              (21.95, 'Idenya dari [Marc Brunel].'), (23.7, 'Tahun [1825],'), (25.04, 'dia menggali terowongan'), (26.09, 'di bawah [Sungai Thames]'), (27.12, 'pakai [perisai besi].'),
              (28.8, 'Di [Jakarta],'), (29.72, 'terowongan MRT terbaru'), (30.84, 'bahkan ada yang sedalam [28 meter].'),
              (33.4, 'Benda apa yang mau kamu [bongkar] berikutnya?'), (35.26, 'Tulis di [komentar]!'),
              (36.6, 'Follow [Bongkar Benda],'), (37.57, 'biar makin paham [cara kerja benda] di sekitarmu.')]

# ------------------------------------------------------------ dunia: potongan kota + tanah yang dibelah di bidang y=0 (sumbu terowongan)
WORLD = Iso(0, 0, 50)
X0, X1, YB, ZB = -15.0, 0.0, -4.2, -8.6          # balok tanah: x X0..X1, y YB..0 (separuh depan dibuang), z ZB..0 (jalan di z=0)
ZC, R, RO, RS = -4.7, 1.5, 1.74, 1.86            # sumbu terowongan (y=0, z=ZC); jari-jari dalam cincin, luar cincin, perisai TBM
LS, RW = 3.4, 0.55                               # panjang perisai TBM, lebar satu cincin
XBH = X1 - 0.75                                  # sekat (bulkhead) di belakang ruang tanah
SOIL = [(0.0, -0.3, '#3B4458'), (-0.3, -0.62, '#B9A994'), (-0.62, -2.3, '#E4C6A2'), (-2.3, -4.1, '#D6AE84'),
        (-4.1, -6.3, '#C79B71'), (-6.3, -20.0, '#B68A62')]
CONC, CONC_E = '#EEE6DC', '#BCAE9E'
NAVY, NAVY2 = '#2A3F6B', '#1A2A4C'
MUCK = '#9A6A45'

def P3(x, y, z): return WORLD.p(x, y, z)
def cam(cv, wx, wy, zoom, sx=540, sy=760): cv.translate(sx, sy); cv.scale(zoom, zoom); cv.translate(-wx, -wy)
def scr(p, f, zoom, sx, sy): return (sx + (p[0] - f[0]) * zoom, sy + (p[1] - f[1]) * zoom)
def wav(u, k): return 0.07 * math.sin(1.25 * u + 1.7 * k) + 0.045 * math.sin(2.9 * u + 0.6 * k)
def cyl(x, r, th, cz=ZC, cy=0.0): return P3(x, cy + r * math.cos(th), cz + r * math.sin(th))
def rad(d): return math.radians(d)

def fpt(plane, pv, u, z): return P3(u, pv, z) if plane == 'y' else P3(pv, u, z)
def face_path(plane, pv, u0, u1, z0, z1): return poly([fpt(plane, pv, u0, z0), fpt(plane, pv, u1, z0), fpt(plane, pv, u1, z1), fpt(plane, pv, u0, z1)])
def strata(cv, plane, pv, u0, u1, a, hole=None, dk=0.0, zb=ZB, zt=0.0):
    """lapisan tanah bergelombang di bidang potong. plane 'y' = muka kiri (u = x), 'x' = muka kanan (u = y)"""
    if a <= 0: return
    face = face_path(plane, pv, u0, u1, zt, zb)
    if hole is not None: face = skia.Op(face, hole, skia.PathOp.kDifference_PathOp)
    cv.save(); cv.clipPath(face, doAntiAlias=True); n = 30
    for k, (z0, z1, c) in enumerate(SOIL):
        if z0 < zb or z1 > zt: continue
        us = [lerp(u0, u1, i / n) for i in range(n + 1)]
        top = [fpt(plane, pv, u, z0 + (wav(u, k) if k > 1 else 0)) for u in us]
        bot = [fpt(plane, pv, u, z1 + (wav(u, k + 1) if k + 1 > 1 else 0)) for u in us[::-1]]
        cv.drawPath(poly(top + bot), P(shader=lg(*fpt(plane, pv, u0, z0), *fpt(plane, pv, u0, z1), [col(tone(c, dk + 0.05), a), col(tone(c, dk - 0.06), a)])))
        if k > 1:                                                         # garis lapisan halus (tanpa titik)
            ln = poly([fpt(plane, pv, u, z0 + wav(u, k)) for u in us], False)
            cv.drawPath(ln, P(col(tone(c, -0.35), 0.35 * a), stroke=1.4))
            for j in range(int(abs(u1 - u0) * 1.3)):                     # goresan tekstur pendek
                rnd = random.Random(k * 97 + j * 13 + int(pv * 7)); uu = lerp(u0, u1, rnd.random()); zz = lerp(z0, max(z1, zb), rnd.uniform(0.2, 0.9))
                p0, p1 = fpt(plane, pv, uu, zz), fpt(plane, pv, uu + 0.35 * (1 if plane == 'y' else 1), zz)
                cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(tone(c, -0.25), 0.3 * a), stroke=1.6))
    cv.restore()
    cv.drawPath(face, P(col(tone(SOIL[4][2], -0.45), 0.55 * a), stroke=1.6))

def band_hole(plane_y_segments):
    """lubang pita di muka kiri (bidang y=0): [(xa, xb, r), ...]"""
    out = None
    for xa, xb, r in plane_y_segments:
        pth = face_path('y', 0.0, xa, xb, ZC + r, ZC - r)
        out = pth if out is None else skia.Op(out, pth, skia.PathOp.kUnion_PathOp)
    return out
def half_disc(x, r, cz=ZC, d0=90, d1=270, n=48):
    return poly([cyl(x, r, rad(lerp(d0, d1, i / n)), cz) for i in range(n + 1)])

def lining(cv, xa, xb, a, r=R, ro=RO, d0=125.0, d1=270.0, joints=True, glow=0.0, j_off=0.0, edges=True):
    """dinding cincin beton separuh belakang (permukaan dalam) + potongan tebalnya di bidang y=0"""
    if a <= 0 or xb <= xa: return
    n = 16
    for i in range(n):
        da, db = lerp(d0, d1, i / n), lerp(d0, d1, (i + 1) / n); k = lerp(-0.30, 0.06, ((da + db) / 2 - 125) / 145)
        cv.drawPath(poly([cyl(xa, r, rad(da)), cyl(xb, r, rad(da)), cyl(xb, r, rad(db)), cyl(xa, r, rad(db))]), P(col(tone(CONC, k), a)))
    if joints:
        xj = xb - j_off
        while xj > xa + 0.01:
            cv.drawPath(poly([cyl(xj, r, rad(d)) for d in range(int(d0), int(d1) + 1, 5)], False), P(col(CONC_E, 0.85 * a), stroke=1.6)); xj -= RW
        for d in (165, 225):
            if d0 <= d <= d1: p0, p1 = cyl(xa, r, rad(d)), cyl(xb, r, rad(d)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(CONC_E, 0.6 * a), stroke=1.3))
    if edges: lining_edges(cv, xa, xb, a, r, ro, glow, j_off)
def lining_edges(cv, xa, xb, a, r=R, ro=RO, glow=0.0, j_off=0.0, top=True, bot=True):
    for z0, z1, on in ((ZC + r, ZC + ro, top), (ZC - ro, ZC - r, bot)):
        if not on: continue
        q = quad(cv, WORLD, [(xa, 0, z0), (xb, 0, z0), (xb, 0, z1), (xa, 0, z1)], tone(CONC, 0.1), a, edge=CONC_E)
        if glow > 0: cv.drawPath(q, P(col(ORANGE, 0.85 * glow * a), blur=10)); cv.drawPath(q, P(col(ORANGE, 0.9 * glow * a)))
        xj = xb - j_off
        while xj > xa + 0.01:
            p0, p1 = P3(xj, 0, z0), P3(xj, 0, z1); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(CONC_E, a), stroke=1.4)); xj -= RW

def street(cv, t, a, xa=X0, xb=X1, bounce=0.0, cars=True, buildings=True, ya=YB):
    """permukaan jalan (z=0), trotoar, gedung di belakang, mobil yang melaju"""
    quad(cv, WORLD, [(xa, ya + 0.8, 0), (xb, ya + 0.8, 0), (xb, 0, 0), (xa, 0, 0)], '#4A5368', a, grad=((xa, 0, 0), (xa, ya + 0.8, 0), '#545E74', '#3F475B'))
    x = xa + 0.3
    while x < xb - 0.3:                                                   # marka putus-putus
        quad(cv, WORLD, [(x, -1.78, 0.002), (min(x + 0.8, xb), -1.78, 0.002), (min(x + 0.8, xb), -1.62, 0.002), (x, -1.62, 0.002)], '#F2EEE8', 0.9 * a); x += 1.5
    box(cv, WORLD, xa, ya, 0, xb - xa, 0.8, 0.14, '#EADFD3', a, top=0.25, left=-0.05, right=-0.15)
    if buildings:
        for (bx, bw, bh, c, lit) in ((-13.4, 2.0, 7.2, '#F5ECE1', 4), (-10.6, 2.2, 6.5, '#F1E6D8', 3), (-7.9, 1.9, 9.5, '#FAF6F0', 7), (-5.3, 2.3, 5.2, '#EBDDCB', 2), (-2.4, 1.9, 7.6, '#F5ECE1', 5)):
            if bx + bw < xa or bx > xb: continue
            building(cv, bx, ya - 2.4, bw, 2.3, bh, c, a, lit)
    if cars:
        L = xb - xa
        cs = []
        for k, (y, v, c, ph) in enumerate(((-0.95, 2.2, ORANGE, 0.1), (-0.95, 2.2, '#F7F4EF', 0.55), (-2.45, -1.8, NAVY, 0.3), (-2.45, -1.8, '#F7F4EF', 0.8), (-0.95, 2.2, NAVY, 0.85))):
            cx = xa + ((ph * L + v * t) % (L + 1.4)) - 1.3
            cs.append((cx + y, cx, y, c, k))
        for _, cx, y, c, k in sorted(cs):
            car(cv, cx, y, c, a, bounce * math.sin(t * 40 + k * 2.1), xa, xb)
def building(cv, x, y, w, d, h, c, a, lit):
    shadow(cv, WORLD, x + 0.15, y + d - 0.05, 0.14, w, 0.6, a, blur=10, k=0.25)
    box(cv, WORLD, x, y, 0.14, w, d, h, c, a, top=0.3, left=0.02, right=-0.14)
    rnd = random.Random(int(x * 10))
    for row in range(int((h - 0.6) / 0.8)):
        z = 0.75 + row * 0.8
        for cc in range(int((w - 0.2) / 0.55)):
            xx = x + 0.2 + cc * 0.55; on = rnd.random() < lit / 20
            quad(cv, WORLD, [(xx, y + d, z), (xx + 0.32, y + d, z), (xx + 0.32, y + d, z + 0.45), (xx, y + d, z + 0.45)], '#FFC98A' if on else NAVY, (0.95 if on else 0.8) * a)
        for cc in range(int((d - 0.2) / 0.55)):
            yy = y + 0.2 + cc * 0.55
            quad(cv, WORLD, [(x + w, yy, z), (x + w, yy + 0.32, z), (x + w, yy + 0.32, z + 0.45), (x + w, yy, z + 0.45)], NAVY2, 0.75 * a)
    box(cv, WORLD, x - 0.05, y - 0.05, 0.14 + h, w + 0.1, d + 0.1, 0.18, tone(c, -0.1), a, top=0.2)
def car(cv, x, y, c, a, bz=0.0, xa=X0, xb=X1):
    if x + 1.25 < xa + 0.05 or x > xb - 0.05: return
    x0 = max(x, xa + 0.05); w = min(x + 1.25, xb - 0.05) - x0
    if w <= 0.05: return
    z = 0.02 + max(0.0, bz) * 0.12
    shadow(cv, WORLD, x0, y - 0.36, 0.01, w, 0.72, a, blur=5, k=0.35)
    box(cv, WORLD, x0, y - 0.36, z + 0.08, w, 0.72, 0.32, c, a, top=0.22)
    cx0 = max(x + 0.3, x0); cw = min(x + 0.92, x0 + w) - cx0
    if cw > 0.05: box(cv, WORLD, cx0, y - 0.31, z + 0.4, cw, 0.62, 0.25, '#5A6B8C' if c == NAVY else NAVY, a, top=0.35)

def bed(cv, xa, xb, a):
    box(cv, WORLD, xa, -0.95, ZC - 1.42, xb - xa, 1.9, 0.42, '#DCD2C6', a, top=0.15, left=-0.02, right=-0.12)
    for y in (-0.42, 0.42):
        p0, p1 = P3(xa, y, ZC - 0.98), P3(xb, y, ZC - 0.98); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#5A6B8C', a), stroke=3))
def train(cv, xf, a, xa=X0, xb=X1):
    """kereta MRT: badan putih, jendela navy, garis oranye; xf = ujung depan (x)"""
    LC, GAP = 3.3, 0.18
    for k in range(3):
        x1_ = xf - k * (LC + GAP); x0_ = x1_ - LC
        c0, c1 = max(x0_, xa + 0.02), min(x1_, xb - 0.02)
        if c1 - c0 < 0.05: continue
        box(cv, WORLD, c0, -0.72, ZC - 0.95, c1 - c0, 1.44, 1.82, '#F4F0EA', a, top=0.12, left=0.0, right=-0.12)
        quad(cv, WORLD, [(c0, 0.72, ZC - 0.38), (c1, 0.72, ZC - 0.38), (c1, 0.72, ZC - 0.24), (c0, 0.72, ZC - 0.24)], ORANGE, a)
        xw = x0_ + 0.25
        while xw + 0.5 < x1_:
            w0, w1 = max(xw, c0), min(xw + 0.5, c1)
            if w1 > w0: quad(cv, WORLD, [(w0, 0.72, ZC + 0.05), (w1, 0.72, ZC + 0.05), (w1, 0.72, ZC + 0.58), (w0, 0.72, ZC + 0.58)], NAVY, 0.9 * a)
            xw += 0.75
        if k == 0 and x1_ <= xb - 0.02:                                   # kaca depan
            quad(cv, WORLD, [(x1_, -0.5, ZC + 0.05), (x1_, 0.5, ZC + 0.05), (x1_, 0.5, ZC + 0.62), (x1_, -0.5, ZC + 0.62)], NAVY, a)
            quad(cv, WORLD, [(x1_, -0.62, ZC - 0.38), (x1_, 0.62, ZC - 0.38), (x1_, 0.62, ZC - 0.24), (x1_, -0.62, ZC - 0.24)], ORANGE, a)

def cracks(cv, t, u, a, retract=0.0):
    """retakan merah dari atap terowongan ke jalan (di muka potong y=0)"""
    if u <= 0 or a <= 0: return
    for k, x0 in enumerate((-6.4, -4.6, -3.1)):
        rnd = random.Random(31 + k); pts = [(x0, ZC + RO + 0.02)]; z = ZC + RO
        while z < -0.35:
            z = min(-0.35, z + rnd.uniform(0.35, 0.6)); pts.append((pts[-1][0] + rnd.uniform(-0.35, 0.35), z))
        sp = [P3(x, 0, zz) for x, zz in pts]; pth = poly(sp, False); fr = clamp(u * (1 - retract))
        if fr < 0.02: continue
        m = skia.PathMeasure(pth, False); seg = skia.Path(); m.getSegment(0, m.getLength() * fr, seg, True)
        cv.drawPath(seg, P(col('#5A1A12', 0.6 * a), stroke=7)); cv.drawPath(seg, P(col(RED, a), stroke=3.5))

# ------------------------------------------------------------ TBM (mesin bor terowongan)
def drum(cv, x0, x1, r, c, a, d0=-45, d1=135, n=24, cz=ZC):
    """pita samping silinder sumbu-x, hanya sudut d0..d1 (derajat; y = r cos, z = r sin)"""
    for i in range(n):
        da, db = rad(lerp(d0, d1, i / n)), rad(lerp(d0, d1, (i + 1) / n)); tm = (da + db) / 2
        k = 0.22 * math.sin(tm) + 0.08 * math.cos(tm) - 0.08
        cv.drawPath(poly([cyl(x0, r, da, cz), cyl(x0, r, db, cz), cyl(x1, r, db, cz), cyl(x1, r, da, cz)]), P(col(tone(c, k), a)))
def cutter_face(cv, x, r, ang, a, d0=0, d1=360, glow=0.0):
    """kepala bor di bidang x: dasar gelap (lubang masuk tanah), 6 jari oranye berputar + gigi pemotong, pelek & hub"""
    if a <= 0: return
    clip = poly([cyl(x, r, rad(lerp(d0, d1, i / 64))) for i in range(65)])
    cv.save(); cv.clipPath(clip, doAntiAlias=True)
    cv.drawPath(clip, P(col('#5B3D27', a)))
    for k in range(6):
        th = ang + math.tau * k / 6; w = 0.16
        pts = [cyl(x, 0.25, th - 0.5), cyl(x, r, th - w), cyl(x, r, th + w), cyl(x, 0.25, th + 0.5)]
        cv.drawPath(poly(pts), P(col(ORANGE, a))); cv.drawPath(poly(pts), P(col(ORANGE_D, a), stroke=1.5))
        for j in range(4):                                                # gigi pemotong
            rr = lerp(0.55, r - 0.18, j / 3); p0 = cyl(x, rr, th - 0.05 * (1 + j % 2)); p1 = cyl(x, rr, th + 0.05 * (1 + j % 2))
            cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=5))
    ring = skia.Op(clip, poly([cyl(x, r - 0.16, rad(lerp(d0, d1, i / 64))) for i in range(65)]), skia.PathOp.kDifference_PathOp)
    cv.drawPath(ring, P(col(ORANGE_D, a)))
    hub = poly([cyl(x, 0.32, rad(i * 360 / 32)) for i in range(32)]); cv.drawPath(hub, P(col(tone(ORANGE, 0.15), a))); cv.drawPath(hub, P(col(ORANGE_D, a), stroke=2))
    cv.restore()
    if glow > 0: cv.drawPath(clip, P(col(ORANGE, 0.5 * glow * a), blur=22))
def tbm_back(cv, a):
    """bagian TBM yang ada di belakang muka potong (digambar sebelum tanah)"""
    drum(cv, X1 - LS, X1, RS, NAVY, a)
def tbm_front(cv, t, ang, a, glow=0.0):
    """separuh depan TBM utuh + kepala bor penuh"""
    if a <= 0: return
    drum(cv, X1 - LS, X1, RS, NAVY, a, d0=-45, d1=90)
    drum(cv, X1 - 0.75, X1 - 0.55, RS + 0.012, ORANGE, a, d0=-45, d1=90, n=12)
    drum(cv, X1, X1 + 0.14, RS - 0.02, ORANGE_D, a, d0=-45, d1=135)
    cutter_face(cv, X1 + 0.14, RS - 0.02, ang, a, glow=glow)

def shield_cut(cv, a, inner=True, edges=True):
    """perisai TBM yang dibelah: permukaan dalam separuh belakang + potongan kulit baja di bidang y=0"""
    if inner:
        n = 14
        for i in range(n):
            da, db = lerp(125, 270, i / n), lerp(125, 270, (i + 1) / n); k = lerp(-0.25, 0.12, ((da + db) / 2 - 125) / 145)
            cv.drawPath(poly([cyl(X1 - LS, RS - 0.1, rad(da)), cyl(X1, RS - 0.1, rad(da)), cyl(X1, RS - 0.1, rad(db)), cyl(X1 - LS, RS - 0.1, rad(db))]), P(col(tone('#3A5182', k), a)))
        for xr in (X1 - 1.6, X1 - 2.5):
            cv.drawPath(poly([cyl(xr, RS - 0.1, rad(d)) for d in range(125, 271, 5)], False), P(col(NAVY2, 0.6 * a), stroke=2))
    if edges:
        for z0, z1 in ((ZC + RS - 0.13, ZC + RS), (ZC - RS, ZC - RS + 0.13)):
            quad(cv, WORLD, [(X1 - LS, 0, z0), (X1, 0, z0), (X1, 0, z1), (X1 - LS, 0, z1)], NAVY2, a)
        quad(cv, WORLD, [(X1 - 0.75, 0, ZC + RS - 0.13), (X1 - 0.55, 0, ZC + RS - 0.13), (X1 - 0.55, 0, ZC + RS), (X1 - 0.75, 0, ZC + RS)], ORANGE, a)

def chamber(cv, t, ang, fill, a):
    """bidang potong y=0: ruang tanah (antara kepala bor & sekat), sekat, ulir pembuang + ban berjalan"""
    if a <= 0: return
    zb0, zt0 = ZC - RS + 0.13, ZC + RS - 0.13
    quad(cv, WORLD, [(XBH, 0, zb0), (X1 - 0.02, 0, zb0), (X1 - 0.02, 0, zt0), (XBH, 0, zt0)], '#2C2420', 0.85 * a)
    zf = lerp(zb0, zt0, fill)
    if fill > 0:
        q = quad(cv, WORLD, [(XBH, 0, zb0), (X1 - 0.02, 0, zb0), (X1 - 0.02, 0, zf), (XBH, 0, zf)], MUCK, a,
                 grad=((XBH, 0, zf), (XBH, 0, zb0), '#B07C52', '#84583A'))
        cv.save(); cv.clipPath(q, doAntiAlias=True)
        for k in range(7):                                                # pusaran tanah yang diaduk kepala bor
            th = ang * 1.3 + k * 0.9; zz = lerp(zb0, zt0, (k + 0.5) / 7)
            p0, p1 = P3(XBH + 0.1 + 0.25 * (1 + math.sin(th)), 0, zz), P3(XBH + 0.35 + 0.25 * (1 + math.cos(th)), 0, zz + 0.18)
            cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#C9976A', 0.7 * a), stroke=3))
        cv.restore()
    quad(cv, WORLD, [(XBH - 0.14, 0, ZC - RS + 0.13), (XBH, 0, ZC - RS + 0.13), (XBH, 0, ZC + RS - 0.13), (XBH - 0.14, 0, ZC + RS - 0.13)], NAVY2, a)
    A_, B_ = (XBH + 0.15, ZC - RS + 0.45), (X1 - LS + 0.25, ZC + 0.35)        # ulir pembuang (tabung miring, dibelah)
    pa, pb = P3(A_[0], 0, A_[1]), P3(B_[0], 0, B_[1])
    cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col('#3B4458', a), stroke=26)); cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col('#6B5A4A', a), stroke=18))
    L = math.hypot(pb[0] - pa[0], pb[1] - pa[1]); ux, uy = (pb[0] - pa[0]) / L, (pb[1] - pa[1]) / L
    ph = (t * 1.6) % 1.0
    for j in range(int(L / 22) + 1):                                      # sirip ulir bergerak ke belakang
        s_ = (j + ph) * 22
        if s_ > L: break
        cx, cy = pa[0] + ux * s_, pa[1] + uy * s_
        cv.drawLine(cx - uy * 9 - ux * 5, cy + ux * 9 - uy * 5, cx + uy * 9 + ux * 5, cy - ux * 9 + uy * 5, P(col(ORANGE, 0.9 * a), stroke=3))
    cv.drawLine(pa[0], pa[1] - 11, pb[0], pb[1] - 11, P(col(WHITE, 0.25 * a), stroke=2))
    pc, pd = P3(X1 - LS + 0.2, 0, ZC + 0.05), P3(X1 - LS - 6.0, 0, ZC + 0.05)  # ban berjalan membawa tanah ke belakang
    cv.drawLine(pc[0], pc[1], pd[0], pd[1], P(col('#3B4458', a), stroke=5))
    for j in range(14):
        xx = X1 - LS + 0.1 - ((j * 0.45 + t * 1.2) % 6.0)
        q0, q1 = P3(xx, 0, ZC + 0.12), P3(xx - 0.22, 0, ZC + 0.12); cv.drawLine(q0[0], q0[1] - 3, q1[0], q1[1] - 3, P(col(MUCK, a), stroke=8))

def construction(cv, t, a, ang, fill=0.0, whole=1.0, rings=None, erector=None, jacks=None, glow=0.0, street_on=True):
    """dunia konstruksi: cincin di belakang, TBM di depan (whole: 1 = utuh, 0 = dibelah)"""
    tail = X1 - LS + 0.25
    if rings is None: lining(cv, X0, tail, a, edges=False, j_off=0.0)
    else: rings_draw(cv, t, rings, a, edges=False)
    shield_cut(cv, a, inner=True, edges=False)
    if whole > 0: tbm_back(cv, a * whole)
    hole = band_hole([(X0, tail, RO), (X1 - LS, X1, RS)])
    strata(cv, 'y', 0.0, X0, X1, a, hole)
    if rings is None: lining_edges(cv, X0, tail, a)
    else: rings_draw(cv, t, rings, a, inner=False)
    shield_cut(cv, a, inner=False, edges=True)
    chamber(cv, t, ang, fill, a)
    if erector: erector_draw(cv, *erector, a=a)
    if jacks is not None: jacks_draw(cv, jacks, a)
    strata(cv, 'x', X1, YB, 0.0, a, half_disc(X1, RS), dk=-0.1)
    cutter_face(cv, X1, RS - 0.02, ang, a * (1 - whole) if whole < 1 else 0, d0=90, d1=270)
    if whole > 0: tbm_front(cv, t, ang, a * whole, glow)
    if street_on: street(cv, t, a)

# ---- cincin yang dipasang segmen demi segmen (adegan C)
SEGS = [(210, 270), (150, 210), (125, 150)]                               # segmen yang terlihat di separuh belakang (bawah -> atas)
def rings_draw(cv, t, st, a, inner=True, edges=True):
    """st = (n_adv, [(k, placed_fraction_per_segment...)]); cincin k mulai di x = tail - RW * (n_adv - k)"""
    n_adv, rings = st; tail = X1 - LS + 0.25
    for k, segs in rings:
        xs = tail - RW * (n_adv - k); xe = xs + RW
        if xe < X0: continue
        xs = max(xs, X0)
        for (d0, d1), on in zip(SEGS, segs):
            if on <= 0: continue
            if inner:
                lining(cv, xs, xe, a * clamp(on * 3), d0=d0, d1=d1, joints=False, edges=False)
                cv.drawPath(poly([cyl(xs, R, rad(d)) for d in range(int(d0), int(d1) + 1, 5)], False), P(col(CONC_E, a), stroke=1.6))
                p0, p1 = cyl(xs, R, rad(d0)), cyl(xe, R, rad(d0)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(CONC_E, 0.8 * a), stroke=1.3))
        if not inner and edges:
            if segs[0] > 0: lining_edges(cv, xs, xe, a * clamp(segs[0] * 3), top=False)
            if len(segs) > 2 and segs[2] > 0: lining_edges(cv, xs, xe, a * clamp(segs[2] * 3), bot=False)
def seg_fly(cv, x, d0, d1, rr, a):
    """segmen beton yang sedang dibawa lengan pemasang"""
    n = 8
    for i in range(n):
        da, db = rad(lerp(d0, d1, i / n)), rad(lerp(d0, d1, (i + 1) / n))
        cv.drawPath(poly([cyl(x, rr, da), cyl(x + RW, rr, da), cyl(x + RW, rr, db), cyl(x, rr, db)]), P(col(tone(CONC, -0.05 + 0.1 * i / n), a)))
    face = poly([cyl(x + RW, rr, rad(lerp(d0, d1, i / n))) for i in range(n + 1)] + [cyl(x + RW, rr + 0.24, rad(lerp(d1, d0, i / n))) for i in range(n + 1)])
    cv.drawPath(face, P(col(tone(CONC, 0.12), a))); cv.drawPath(face, P(col(CONC_E, a), stroke=1.5))
def erector_draw(cv, ang_d, rr, carry, a=1.0):
    """lengan pemasang di ekor perisai: berputar di sumbu, membawa segmen (carry = (d0, d1) atau None)"""
    xe = X1 - LS + 0.75
    p0 = P3(xe, 0, ZC); p1 = cyl(xe, rr * 0.92, rad(ang_d))
    if carry: seg_fly(cv, X1 - LS + 0.25, carry[0], carry[1], rr, a)
    cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=14)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#5A6B8C', a), stroke=7))
    cv.drawCircle(p0[0], p0[1], 13, P(col(ORANGE, a))); cv.drawCircle(p1[0], p1[1], 9, P(col(ORANGE, a)))
def jacks_draw(cv, x_ring, a):
    """dongkrak pendorong: dari sekat perisai ke muka cincin terbaru"""
    xb_ = X1 - LS + 1.55
    for d in (150, 195, 240):
        p0, p1 = cyl(xb_, R + 0.08, rad(d)), cyl(x_ring, R + 0.08, rad(d))
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#C8CFDA', a), stroke=6)); cv.drawLine(p0[0], p0[1], lerp(p0[0], p1[0], 0.45), lerp(p0[1], p1[1], 0.45), P(col(NAVY2, a), stroke=10))
        cv.drawCircle(p1[0], p1[1], 6, P(col(ORANGE, a)))

# ------------------------------------------------------------ A: HOOK — kota di atas terowongan; tanah retak, cincin beton menahan (0 - 5.5)
T_CR, T_SAVE = 3.85, 4.45
def gA(cv, t):
    u = eio(prog(t, 0.0, 2.7))
    fw = (lerp(-5.2, -5.6, u), lerp(-2.0, -1.2, u), lerp(0.8, -3.2, u)); zoom = lerp(2.35, 1.42, u) * (1 + 0.02 * eio(prog(t, 2.7, 5.5)))
    shk = (9 * math.sin(t * 57) * (1 - prog(t, T_CR + 0.2, T_SAVE + 0.2))) if T_CR < t < T_SAVE + 0.2 else 0.0
    f = P3(*fw); sx, sy = 540 + shk, 1010
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    crack_u = eo(prog(t, T_CR, T_CR + 0.5)); retract = eio(prog(t, T_SAVE, T_SAVE + 0.6)); glow = eo(prog(t, T_SAVE - 0.1, T_SAVE + 0.2)) * (1 - 0.7 * prog(t, 4.6, 5.4))
    lining(cv, X0, X1, 1.0, edges=False, j_off=0.0)
    xf = lerp(X0 - 1.0, X1 + 3.2, prog(t, 0.0, 5.5))
    bed(cv, X0, X1, 1.0); train(cv, xf, 1.0)
    strata(cv, 'y', 0.0, X0, X1, 1.0, band_hole([(X0, X1, RO)]))
    lining_edges(cv, X0, X1, 1.0, glow=glow)
    if crack_u > 0:                                                       # bongkahan tanah jatuh dari atap terowongan
        for k in range(7):
            rnd = random.Random(70 + k); x = rnd.uniform(-7.0, -2.6); t0 = T_CR + 0.1 + 0.08 * k
            if t0 < t < T_SAVE + 0.4:
                zz = ZC + RO - 2.4 * (t - t0) ** 2 * 2.2
                if zz > ZC - 0.9: p = P3(x, 0.2, zz); cv.drawRect(skia.Rect(p[0] - 6, p[1] - 5, p[0] + 6, p[1] + 5), P(col(MUCK, 1 - retract)))
    cracks(cv, t, crack_u, 1.0, retract)
    strata(cv, 'x', X1, YB, 0.0, 1.0, half_disc(X1, RO), dk=-0.1)
    ann = skia.Op(half_disc(X1, RO), half_disc(X1, R), skia.PathOp.kDifference_PathOp)
    cv.drawPath(ann, P(col(tone(CONC, 0.04), 1.0))); cv.drawPath(ann, P(col(CONC_E, 1.0), stroke=1.5))
    if glow > 0: cv.drawPath(ann, P(col(ORANGE, 0.9 * glow))); cv.drawPath(ann, P(col(ORANGE, 0.6 * glow), blur=14))
    for d in (150, 210):
        p0, p1 = cyl(X1, R, rad(d)), cyl(X1, RO, rad(d)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(CONC_E, 1.0), stroke=1.5))
    street(cv, t, 1.0, bounce=prog(t, T_CR, T_CR + 0.1) * (1 - prog(t, T_SAVE, T_SAVE + 0.3)))
    cv.restore()
    ta = 1 - eio(prog(t, bb.TITLE_OUT - 0.4, bb.TITLE_OUT))
    if ta > 0: cv.drawRect(skia.Rect(0, 0, 1080, 560), P(shader=lg(0, 380, 0, 600, [col(bb.BG0, ta), col(bb.BG0, 0)])))
    fl = prog(t, T_CR, T_CR + 0.35)
    if 0 < fl < 1: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.25 * (1 - fl))))
    if T_CR < t < T_SAVE + 0.2: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.06 * (1 - prog(t, T_SAVE, T_SAVE + 0.2)))))
    if T_CR + 0.1 < t < T_SAVE + 0.3: chip(cv, 'AMBRUK?', 540, 560, eo(prog(t, T_CR + 0.1, T_CR + 0.3)) * (1 - prog(t, T_SAVE + 0.05, T_SAVE + 0.3)), size=32, bg=RED)
    if t > T_SAVE:
        p = scr(cyl(X1, (R + RO) / 2, rad(160)), f, zoom, sx, sy)
        la = eo(prog(t, T_SAVE, T_SAVE + 0.35)) * (1 - prog(t, 5.25, 5.5))
        label(cv, 'CINCIN BETON', p[0], p[1], 840, 640, la, sub='menahan tanah')
        check(cv, 985, 575, 26, prog(t, T_SAVE + 0.1, T_SAVE + 0.5), la)
    for k, (num, txt) in enumerate((('1', 'TAHAN TANAH'), ('2', 'CINCIN BETON'), ('3', 'SUNTIK SEMEN'))):
        q = prog(t, 4.7 + 0.15 * k, 5.0 + 0.15 * k)
        if q > 0:
            x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
            cv.save(); cv.translate(x, 1335); cv.scale(s_, s_); cv.translate(-x, -1335)
            card(cv, skia.Rect(x - 158, 1305, x + 158, 1365), aa, rad=30, lift=8)
            cv.drawCircle(x - 123, 1335, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 123, 1335, 24, WHITE, aa)
            text_c(cv, txt, x + 14, 1335, 24, INK, aa)
            cv.restore()

# ------------------------------------------------------------ B: mesin bor menahan tanah di depannya, tekanan seimbang (5.5 - 12.5)
def arrow(cv, p0, p1, c, a, w=9, head=20):
    if a <= 0: return
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); hx, hy = p1[0] - math.cos(ang) * head * 0.8, p1[1] - math.sin(ang) * head * 0.8
    pth = skia.Path(); pth.moveTo(*p1)
    pth.lineTo(p1[0] - head * math.cos(ang - 0.45), p1[1] - head * math.sin(ang - 0.45)); pth.lineTo(p1[0] - head * math.cos(ang + 0.45), p1[1] - head * math.sin(ang + 0.45)); pth.close()
    cv.drawLine(p0[0], p0[1], hx, hy, P(col(WHITE, a), stroke=w + 7)); cv.drawPath(pth, P(col(WHITE, a), stroke=7))
    cv.drawLine(p0[0], p0[1], hx, hy, P(col(c, a), stroke=w)); cv.drawPath(pth, P(col(c, a)))
def gB(cv, t):
    a0 = eo(prog(t, 5.5, 5.9)); ang = t * 1.4
    zoom = lerp(2.05, 2.35, eio(prog(t, 5.5, 12.5))); fw = (X1 - 1.6, -0.6, ZC + 0.5); f = P3(*fw); sx, sy = 470, 900
    whole = 1 - eio(prog(t, 6.3, 7.0)); fill = eio(prog(t, 9.7, 10.6))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    construction(cv, t, a0, ang, fill=max(0.25, fill) if whole < 1 else 0.25, whole=whole, glow=0.0)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 6.0, 6.4))
    if la > 0:
        p = S((X1, -0.9, ZC + 1.0)); label(cv, 'KEPALA BOR', p[0], p[1], 850, 640, a0 * la, sub='berputar & mengeruk')
    ca = eo(prog(t, 6.3, 6.7)) * (1 - prog(t, 9.3, 9.6))
    if ca > 0:                                                            # kartu fakta TBM MRT Jakarta
        r = skia.Rect(150, 250, 930, 500); card(cv, r, a0 * ca, rad=30)
        mono(cv, 'TBM MRT JAKARTA · FASE 1', r.left() + 44, r.top() + 50, 22, MUTED, a0 * ca, sp=3, align=0)
        n = int(lerp(0, 323, eo(prog(t, 7.31, 8.1))))
        text_c(cv, f'{n} TON', 400, r.top() + 150, 104, INK, a0 * ca)
        text_c(cv, 'diameter 6,7 m', 765, r.top() + 128, 30, INK2, a0 * ca, f=B)
        text_c(cv, 'panjang 43 m', 765, r.top() + 176, 30, INK2, a0 * ca, f=B)
    pa = eo(prog(t, 8.33, 8.7))
    if pa > 0:                                                            # tekanan tanah & air dari depan
        for k, (yy, zz) in enumerate(((-0.6, ZC + 1.0), (-0.9, ZC), (-0.6, ZC - 1.0))):
            q = eo(prog(t, 8.33 + 0.12 * k, 8.7 + 0.12 * k)); wob = 6 * math.sin(t * 5 + k)
            arrow(cv, S((X1 + 2.0, yy, zz)), S((X1 + 0.45 + 0.04 * wob, yy, zz)), NAVY, a0 * q * (1 - prog(t, 12.2, 12.5)), w=10, head=24)
        lb = eo(prog(t, 8.7, 9.0)); p = S((X1 + 2.0, -0.6, ZC + 1.6))
        if lb > 0: chip(cv, 'TEKANAN TANAH + AIR', 790, 1010, a0 * lb * (1 - prog(t, 9.5, 9.8)), size=24, bg=NAVY)
    qa = eo(prog(t, 9.7, 10.05))
    if qa > 0:                                                            # tanah galian ditekan balik
        lp_ = S((XBH + 0.3, 0, ZC + 0.4)); label(cv, 'RUANG TANAH', lp_[0], lp_[1], 250, 1150, a0 * qa, sub='tanah galian ditekan balik')
        for k, zz in enumerate((ZC + 0.8, ZC - 0.4)):
            q = eo(prog(t, 10.0 + 0.12 * k, 10.4 + 0.12 * k))
            arrow(cv, S((X1 - 0.35, 0, zz)), S((X1 + 0.75, -0.25, zz)), ORANGE, a0 * q * (1 - prog(t, 12.2, 12.5)), w=10, head=24)
    ga = eo(prog(t, 10.97, 11.3))
    if ga > 0:                                                            # pengukur tekanan: seimbang
        cx, cy = 540, 360; r_ = 92
        card(cv, skia.Rect(cx - 210, cy - 115, cx + 210, cy + 110), a0 * ga, rad=30)
        arc = skia.Path(); arc.addArc(skia.Rect(cx - r_, cy - r_ + 30, cx + r_, cy + r_ + 30), 200, 140)
        cv.drawPath(arc, P(col('#E8DED2', a0 * ga), stroke=22))
        mid = skia.Path(); mid.addArc(skia.Rect(cx - r_, cy - r_ + 30, cx + r_, cy + r_ + 30), 255, 30); cv.drawPath(mid, P(col(ORANGE, a0 * ga), stroke=22))
        nd = math.radians(270 + 5 * math.sin(t * 3) * (1 - prog(t, 11.3, 11.8)))
        cv.drawLine(cx, cy + 30, cx + 78 * math.cos(nd), cy + 30 + 78 * math.sin(nd), P(col(INK, a0 * ga), stroke=7)); cv.drawCircle(cx, cy + 30, 12, P(col(INK, a0 * ga)))
        mono(cv, 'TEKANAN DEPAN', cx, cy + 78, 20, MUTED, a0 * ga, sp=3)
        chip(cv, 'SEIMBANG', 540, 1340, a0 * eo(prog(t, 11.05, 11.35)), size=30, bg=ORANGE)
        check(cv, cx + 160, cy - 60, 22, prog(t, 11.15, 11.55), a0 * ga)

# ------------------------------------------------------------ C: sambil maju, memasang cincin beton (12.5 - 17.1)
RING_T = [(13.0, 13.4, 13.8), (14.7, 15.05, 15.4), (16.3, 16.6, 16.9)]   # waktu tiap segmen terpasang (bawah -> atas)
ADV_T = [(13.95, 14.5), (15.55, 16.1)]                                   # TBM maju satu cincin
def ring_state(t):
    n_adv = sum(eio(prog(t, a_, b_)) for a_, b_ in ADV_T)
    rings = [(k, (1, 1, 1)) for k in range(-26, 0)]
    for k, ts in enumerate(RING_T): rings.append((k, tuple(prog(t, s_, s_ + 0.05) for s_ in ts)))
    return n_adv, rings
def gC(cv, t):
    a0 = eo(prog(t, 12.5, 12.9)); ang = t * 1.4
    zoom = lerp(2.5, 2.7, eio(prog(t, 12.5, 17.1))); fw = (X1 - LS + 0.3, -0.5, ZC + 0.3); f = P3(*fw); sx, sy = 560, 900
    st = ring_state(t); n_adv = st[0]
    carry, ang_d, rr = None, 270.0, R * 0.55                               # lengan pemasang: ambil segmen di bawah, putar ke posisinya
    for k, ts in enumerate(RING_T):
        for s_i, ts_ in enumerate(ts):
            t0 = ts_ - 0.38
            if t0 <= t < ts_:
                u = eio(prog(t, t0, ts_ - 0.04)); d0, d1 = SEGS[s_i]; mid = (d0 + d1) / 2
                ang_d = lerp(270, mid, u); rr = lerp(R * 0.55, R, u); span = (d1 - d0) / 2
                carry = (ang_d - span, ang_d + span)
    x_ring = X1 - LS + 0.25 + RW - RW * (n_adv - max(k for k, segs in st[1] if all(s > 0 for s in segs)))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    construction(cv, t, a0, ang, fill=1.0, whole=0.0, rings=st, erector=(ang_d, rr, carry), jacks=x_ring)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    for k, (a_, b_) in enumerate(ADV_T):                                  # +1 CINCIN
        q = prog(t, b_ - 0.1, b_ + 0.5)
        if 0 < q < 1:
            p = S((X1 - LS - 0.3, 0, ZC + RO + 0.6)); text_c(cv, '+1 CINCIN', p[0], p[1] - 60 * eo(q), 34, ORANGE, a0 * bump(q) * 1.4, halo=1.0)
    la = eo(prog(t, 14.5, 14.9))
    if la > 0:
        p = S((X1 - LS - 0.6, 0, ZC - R - 0.1)); label(cv, 'CINCIN BETON', p[0], p[1], 300, 1150, a0 * la, sub='segmen demi segmen')
    lb = eo(prog(t, 13.1, 13.5))
    if lb > 0:
        p = S((X1 - LS + 0.75, 0, ZC)); label(cv, 'LENGAN PEMASANG', p[0], p[1], 760, 420, a0 * lb, sub='menaruh segmen beton')
    ca = eo(prog(t, 15.43, 15.75))
    if ca > 0: chip(cv, 'JADI DINDING TEROWONGAN', 540, 1340, a0 * ca, size=28, bg=INK)

# ------------------------------------------------------------ D: celah di luar cincin disuntik semen, jalan tetap rata (17.1 - 21.95)
SX0, SX1, SY0, SY1, SZB, SZC = -4.6, 0.0, -5.0, 5.0, -10.0, -5.6
SR, SRO, SRS = 1.75, 2.08, 2.55
def scyl(r, th, x=SX1): return P3(x, r * math.cos(th), SZC + r * math.sin(th))
def circle(r, x=SX1, n=72): return poly([scyl(r, math.tau * i / n, x) for i in range(n)])
def gD(cv, t):
    a0 = eo(prog(t, 17.1, 17.5))
    zoom = lerp(1.5, 1.6, eio(prog(t, 17.1, 21.95))); fw = (SX1 - 1.4, 0.2, SZC + 1.2); f = P3(*fw); sx, sy = 540, 860
    grout = eio(prog(t, 18.95, 20.0)); sag = eo(prog(t, 17.6, 18.2)) * (1 - eio(prog(t, 19.0, 19.7)))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    strata(cv, 'y', SY1, SX0, SX1, a0, None, zb=SZB)                     # muka kiri (tanah biasa)
    hole = circle(SRS)
    cv.save(); cv.clipPath(circle(SR), doAntiAlias=True)
    n = 24                                                                # bagian dalam terowongan yang menjauh
    for i in range(n):
        da, db = rad(lerp(135, 315, i / n)), rad(lerp(135, 315, (i + 1) / n))
        q = poly([scyl(SR, da), scyl(SR, db), scyl(SR, db, SX1 - 7), scyl(SR, da, SX1 - 7)])
        cv.drawPath(q, P(shader=lg(*scyl(SR, da), *scyl(SR, da, SX1 - 7), [col(tone(CONC, -0.05 - 0.1 * math.sin(da)), a0), col(tone(CONC, -0.55), a0)])))
    for j in range(1, 12):
        cv.drawPath(poly([scyl(SR, rad(d), SX1 - j * RW) for d in range(135, 316, 6)], False), P(col(CONC_E, a0 * (1 - j / 12)), stroke=1.5))
    cv.drawPath(circle(SR, SX1 - 7), P(col('#1A2030', a0), blur=6)); cv.restore()
    strata(cv, 'x', SX1, SY0, SY1, a0, hole, dk=-0.1, zb=SZB)            # muka kanan dengan potongan terowongan
    gap = skia.Op(circle(SRS), circle(SRO), skia.PathOp.kDifference_PathOp)
    cv.drawPath(gap, P(col('#3A2C22', a0)))                              # celah kosong di luar cincin
    if grout > 0:
        lvl = SZC - SRS + grout * 2 * SRS + 0.25 * math.sin(t * 4) * grout * (1 - grout)
        fillp = poly([P3(SX1, -SRS - 0.5, SZC - SRS - 0.2), P3(SX1, SRS + 0.5, SZC - SRS - 0.2), P3(SX1, SRS + 0.5, lvl), P3(SX1, -SRS - 0.5, lvl)])
        g = skia.Op(gap, fillp, skia.PathOp.kIntersect_PathOp)
        cv.drawPath(g, P(shader=lg(*scyl(SRS, rad(90)), *scyl(SRS, rad(270)), [col('#FFB066', a0), col(ORANGE_D, a0)])))
    ring = skia.Op(circle(SRO), circle(SR), skia.PathOp.kDifference_PathOp)
    cv.drawPath(ring, P(shader=lg(*scyl(SRO, rad(90)), *scyl(SRO, rad(270)), [col(tone(CONC, 0.12), a0), col(tone(CONC, -0.06), a0)])))
    cv.drawPath(ring, P(col(CONC_E, a0), stroke=1.6))
    for d in range(30, 390, 60):
        p0, p1 = scyl(SR, rad(d)), scyl(SRO, rad(d)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(CONC_E, a0), stroke=2))
    if 18.9 < t < 20.3:                                                   # nosel suntik di ekor
        for d in (230, 310, 90):
            p0, p1 = scyl(SRO - 0.05, rad(d)), scyl(SRS - 0.1, rad(d)); aa = a0 * bump(prog(t, 18.9, 20.3))
            cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(ORANGE, aa), stroke=7))
    quad(cv, WORLD, [(SX0, SY0, 0), (SX1, SY0, 0), (SX1, SY1, 0), (SX0, SY1, 0)], '#4A5368', a0, grad=((SX0, SY1, 0), (SX0, SY0, 0), '#545E74', '#3F475B'))
    for y in (-1.6, 1.6):
        quad(cv, WORLD, [(SX0 + 0.3, y - 0.07, 0.002), (SX1 - 0.3, y - 0.07, 0.002), (SX1 - 0.3, y + 0.07, 0.002), (SX0 + 0.3, y + 0.07, 0.002)], '#F2EEE8', 0.9 * a0)
    for k, (yc, v) in enumerate(((-3.0, 2.0), (0.4, -1.6))):
        car(cv, SX0 - 1.3 + ((t * v * 0.6 + k * 1.7) % 4.4) if v > 0 else SX1 - ((t * -v * 0.6 + k * 1.3) % 4.4), yc, (ORANGE, '#F7F4EF')[k], a0, 0.0, SX0, SX1)
    if sag > 0:                                                           # tanpa semen: tanah di atas ikut turun (garis putus merah)
        pts = [P3(SX1, y, -0.35 - 1.1 * sag * math.exp(-(y / 2.2) ** 2)) for y in [i * 0.25 - 4.0 for i in range(33)]]
        pth = poly(pts, False); dash = skia.DashPathEffect.Make([16, 10], t * 40)
        cv.drawPath(pth, P(col(RED, a0 * sag), stroke=5, effect=dash))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    if sag > 0.05:
        p = S((SX1, 0, -1.6)); arrow(cv, (p[0], p[1] - 40), (p[0], p[1] + 30), RED, a0 * sag, w=8, head=20)
        chip(cv, 'TANAH TURUN?', 540, 420, a0 * sag, size=28, bg=RED)
    la = eo(prog(t, 17.7, 18.1))
    if la > 0:
        p = S((SX1, -SRS * 0.71 - 0.05, SZC + SRS * 0.71)); label(cv, 'CELAH', p[0], p[1], 250, 560, a0 * la, sub='di luar cincin beton')
    lb = eo(prog(t, 19.0, 19.4))
    if lb > 0:
        p = S((SX1, SRS * 0.85, SZC - SRS * 0.5)); label(cv, 'SEMEN (GROUT)', p[0], p[1], 820, 1180, a0 * lb, sub='mengisi celah')
    ca = eo(prog(t, 20.7, 21.0))
    if ca > 0:
        chip(cv, 'TANAH NGGAK TURUN', 540, 420, a0 * ca, size=28, bg=ORANGE); check(cv, 760, 420, 22, prog(t, 20.8, 21.2), a0 * ca)

# ------------------------------------------------------------ E: Marc Brunel, perisai terowongan, London 1825 (21.95 - 28.8)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def brunel_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'LONDON · 1825', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    wy = 455                                                              # sungai Thames + perahu layar
    cv.drawRect(skia.Rect(r.left(), wy, r.right(), wy + 150), P(col('#E6D3AE', a)))
    for k in range(3):
        p = skia.Path(); yy = wy + 25 + k * 40; p.moveTo(r.left(), yy)
        for i in range(30): x = r.left() + i * 32; p.quadTo(x + 8, yy - 8 + 2 * math.sin(t * 2 + k), x + 16, yy); p.quadTo(x + 24, yy + 8, x + 32, yy)
        cv.drawPath(p, ink(0.5, 2.5))
    bx = 300 + 60 * math.sin(t * 0.4)
    hull = skia.Path(); hull.moveTo(bx - 70, wy - 4); hull.lineTo(bx + 70, wy - 4); hull.lineTo(bx + 48, wy + 22); hull.lineTo(bx - 48, wy + 22); hull.close()
    cv.drawPath(hull, P(col('#B58A57', a))); cv.drawPath(hull, ink())
    sail = skia.Path(); sail.moveTo(bx - 4, wy - 10); sail.lineTo(bx - 4, wy - 130); sail.lineTo(bx + 60, wy - 14); sail.close()
    cv.drawPath(sail, P(col('#FBF3E2', a))); cv.drawPath(sail, ink())
    cv.drawRect(skia.Rect(r.left(), wy + 150, r.right(), r.bottom()), P(col('#D9BF92', a)))   # dasar sungai & tanah
    for k in range(5): cv.drawLine(r.left(), wy + 190 + k * 70, r.right(), wy + 196 + k * 70, ink(0.25, 2))
    ty0, ty1 = 760, 1010                                                  # terowongan bata (dua lorong lengkung)
    for cx in (360, 620):
        arch = skia.Path(); arch.moveTo(cx - 110, ty1); arch.lineTo(cx - 110, ty0 + 90); arch.arcTo(skia.Rect(cx - 110, ty0 - 20, cx + 110, ty0 + 200), 180, 180, False); arch.lineTo(cx + 110, ty1); arch.close()
        cv.drawPath(arch, P(col('#C79A63', a))); cv.drawPath(arch, ink())
        inner = skia.Path(); inner.moveTo(cx - 80, ty1); inner.lineTo(cx - 80, ty0 + 95); inner.arcTo(skia.Rect(cx - 80, ty0 + 15, cx + 80, ty0 + 175), 180, 180, False); inner.lineTo(cx + 80, ty1); inner.close()
        cv.drawPath(inner, P(col('#8E6A45', a)))
        for k in range(5): cv.drawLine(cx - 110, ty0 + 110 + k * 30, cx - 80, ty0 + 110 + k * 30, ink(0.5, 2)); cv.drawLine(cx + 80, ty0 + 110 + k * 30, cx + 110, ty0 + 110 + k * 30, ink(0.5, 2))
        lamp = 0.6 + 0.4 * math.sin(t * 7 + cx); cv.drawCircle(cx, ty0 + 150, 28, P(col('#FFD08A', 0.5 * lamp * a), blur=14))
    sx0, sx1, sy0, sy1 = 760, 900, 700, 1020                              # perisai: rangka sel bertingkat di muka galian
    cv.drawRect(skia.Rect(sx0, sy0, sx1, sy1), P(col('#7E8693', a))); cv.drawRect(skia.Rect(sx0, sy0, sx1, sy1), ink(1, 4))
    for i in range(1, 3): cv.drawLine(sx0, sy0 + i * (sy1 - sy0) / 3, sx1, sy0 + i * (sy1 - sy0) / 3, ink(1, 4))
    cv.drawLine((sx0 + sx1) / 2, sy0, (sx0 + sx1) / 2, sy1, ink(1, 4))
    for row in range(3):
        for c_ in range(2):
            cx = sx0 + 35 + c_ * 70; cy = sy0 + 85 + row * (sy1 - sy0) / 3
            sw = math.sin(t * 6 + row * 1.7 + c_ * 2.3)
            cv.drawCircle(cx, cy - 34, 10, P(col(SEPIA_INK, a))); cv.drawRoundRect(skia.Rect(cx - 10, cy - 24, cx + 10, cy + 8), 6, 6, P(col(SEPIA_INK, a)))
            cv.drawLine(cx + 6, cy - 16, cx + 26 + 6 * sw, cy - 34 - 10 * sw, ink(1, 3))
    cv.drawRect(skia.Rect(sx1, sy0 - 10, r.right(), sy1 + 10), P(col('#C9A577', 0.6 * a)))
    hx, hy = 712, 1010                                                    # Brunel: topi tinggi, di dekat perisai
    cv.drawRoundRect(skia.Rect(hx - 22, hy - 120, hx + 22, hy - 30), 12, 12, P(col('#3E2E22', a)))
    cv.drawRect(skia.Rect(hx - 16, hy - 32, hx - 4, hy), P(col('#3E2E22', a))); cv.drawRect(skia.Rect(hx + 4, hy - 32, hx + 16, hy), P(col('#3E2E22', a)))
    cv.drawLine(hx + 18, hy - 106, hx + 58, hy - 120 + 4 * math.sin(t * 3), P(col('#3E2E22', a), stroke=10))
    cv.drawCircle(hx, hy - 140, 18, P(col('#E8C9A0', a))); cv.drawCircle(hx, hy - 140, 18, ink(1, 2.5))
    cv.drawRect(skia.Rect(hx - 16, hy - 196, hx + 16, hy - 154), P(col('#2A1F17', a))); cv.drawRect(skia.Rect(hx - 26, hy - 160, hx + 26, hy - 152), P(col('#2A1F17', a)))
    cv.restore()
def gE(cv, t):
    a0 = eo(prog(t, 21.95, 22.4))
    cv.save(); cv.translate(540, 770); cv.scale(1.14, 1.14); cv.translate(-540, -700)
    brunel_card(cv, t, a0)
    cv.restore()
    S = lambda x, y: (540 + (x - 540) * 1.14, 770 + (y - 700) * 1.14)
    na = eo(prog(t, 22.2, 22.6))
    if na > 0: p = S(712, 860); label(cv, 'MARC BRUNEL', p[0], p[1], 290, 1240, a0 * na, size=26, sub='insinyur Terowongan Thames')
    ra = eo(prog(t, 26.09, 26.45))
    if ra > 0: p = S(700, 520); label(cv, 'SUNGAI THAMES', p[0], p[1], 820, 300, a0 * ra, size=26)
    sa = eo(prog(t, 27.12, 27.45))
    if sa > 0:
        p = S(830, 860); label(cv, 'PERISAI BESI', p[0], p[1], 820, 1230, a0 * sa, size=26, sub='melindungi para penggali')

# ------------------------------------------------------------ F: di Jakarta, ada yang sedalam 28 meter (28.8 - 33.4)
FX0, FY0, FZB, FZT, FTY = -4.8, -7.4, -16.4, -14.0, -3.7                # 1 satuan = 2 m; pusat terowongan di 28 m
def fcyl(r, th): return P3(0, FTY + r * math.cos(th), FZT + r * math.sin(th))
def gF(cv, t):
    a0 = eo(prog(t, 28.8, 29.2)); u = eio(prog(t, 30.2, 31.9))
    zoom = lerp(1.16, 1.21, eio(prog(t, 28.8, 33.4))); fw = (-2.2, -3.4, -7.4); f = P3(*fw); sx, sy = 540, 790
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    hole = poly([fcyl(1.4, math.tau * i / 60) for i in range(60)])
    strata(cv, 'y', 0.0, FX0, 0.0, a0, None, zb=FZB)
    strata(cv, 'x', 0.0, FY0, 0.0, a0, hole, dk=-0.1, zb=FZB)
    cv.drawPath(hole, P(shader=rg(*fcyl(0, 0), 60, [col('#2A3348', a0), col('#141A28', a0)])))
    ann = skia.Op(hole, poly([fcyl(1.12, math.tau * i / 60) for i in range(60)]), skia.PathOp.kDifference_PathOp)
    cv.drawPath(ann, P(col(CONC, a0))); cv.drawPath(ann, P(col(CONC_E, a0), stroke=1.5))
    tr = poly([P3(0.01, FTY - 0.55, FZT - 0.55), P3(0.01, FTY + 0.55, FZT - 0.55), P3(0.01, FTY + 0.55, FZT + 0.45), P3(0.01, FTY - 0.55, FZT + 0.45)])
    cv.drawPath(tr, P(col('#F4F0EA', a0)))                               # muka depan kereta di dalam terowongan
    cv.drawPath(poly([P3(0.02, FTY - 0.42, FZT - 0.05), P3(0.02, FTY + 0.42, FZT - 0.05), P3(0.02, FTY + 0.42, FZT + 0.3), P3(0.02, FTY - 0.42, FZT + 0.3)]), P(col(NAVY, a0)))
    cv.drawPath(poly([P3(0.02, FTY - 0.55, FZT - 0.3), P3(0.02, FTY + 0.55, FZT - 0.3), P3(0.02, FTY + 0.55, FZT - 0.2), P3(0.02, FTY - 0.55, FZT - 0.2)]), P(col(ORANGE, a0)))
    quad(cv, WORLD, [(FX0, FY0, 0), (0, FY0, 0), (0, 0, 0), (FX0, 0, 0)], '#4A5368', a0, grad=((FX0, 0, 0), (FX0, FY0, 0), '#545E74', '#3F475B'))
    car(cv, FX0 - 1.2 + (t * 1.1) % 6.2, -1.2, ORANGE, a0, 0.0, FX0, 0.0); car(cv, -((t * 0.9 + 2.0) % 6.2), -3.4, '#F7F4EF', a0, 0.0, FX0, 0.0)
    for k in range(9):                                                    # gedung 9 lantai bayangan, dicerminkan ke bawah tanah
        z0 = -k * 1.55; z1 = z0 - 1.55; aa = a0 * clamp(u * 9 - k)
        if aa <= 0: continue
        q = quad(cv, WORLD, [(-4.2, 0, z0), (-0.7, 0, z0), (-0.7, 0, z1), (-4.2, 0, z1)], WHITE, 0.4 * aa)
        cv.drawPath(q, P(col(NAVY, 0.9 * aa), stroke=2.5, effect=skia.DashPathEffect.Make([10, 7], 0)))
        for j in range(5):
            xx = -4.0 + j * 0.65; quad(cv, WORLD, [(xx, 0, z0 - 0.45), (xx + 0.32, 0, z0 - 0.45), (xx + 0.32, 0, z0 - 1.05), (xx, 0, z0 - 1.05)], NAVY, 0.45 * aa)
    zz = lerp(0, FZT, u)                                                  # penggaris kedalaman di tepi depan + garis ke terowongan
    p0, p1 = P3(0, 0, 0), P3(0, 0, zz); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(ORANGE, a0), stroke=10))
    for k in range(0, 15):
        if -k < zz - 0.01: continue
        pa, pb = P3(0, 0, -k), P3(0, -0.45 if k % 5 else -0.8, -k)
        cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col(INK, a0), stroke=3 if k % 5 else 4))
    if u > 0.97:
        da = a0 * eo(prog(t, 31.9, 32.15)); pa, pb = P3(0, 0, FZT), fcyl(1.15, math.pi)
        cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col(ORANGE, da), stroke=4, effect=skia.DashPathEffect.Make([12, 8], 0)))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    ca = eo(prog(t, 29.3, 29.7))
    if ca > 0:                                                            # penghitung kedalaman
        card(cv, skia.Rect(680, 250, 1000, 440), a0 * ca, rad=30)
        mono(cv, 'KEDALAMAN', 840, 293, 22, MUTED, a0 * ca, sp=4)
        text_c(cv, f'{int(round(28 * u))} m', 840, 375, 92, ORANGE, a0 * ca)
    p = S((0, 0, 0)); text_c(cv, '0 m', p[0] + 75, p[1] + 25, 32, INK, a0 * eo(prog(t, 29.0, 29.3)), halo=1.0)
    ga = eo(prog(t, 32.1, 32.45))
    if ga > 0:
        p = S((-2.45, 0, -10.2)); label(cv, '≈ GEDUNG 9 LANTAI', p[0], p[1], 250, 300, a0 * ga, dot=INK, size=26, sub='kalau dibalik ke bawah')
    ta = eo(prog(t, 32.3, 32.6))
    if ta > 0: chip(cv, 'TERDALAM DI INDONESIA', 805, 495, a0 * ta, size=24, bg=INK)

# ------------------------------------------------------------ G: bongkar apa lagi? tulis di komentar (33.4 - 36.6)
CMTS = [('jembatan!', 280, 760, 33.9, ORANGE), ('pesawat dong', 760, 900, 34.15, INK), ('kereta cepat pls', 310, 1040, 34.4, ORANGE_D), ('bendungan!!', 760, 1180, 34.65, NAVY)]
def gG(cv, t):
    a0 = eo(prog(t, 33.4, 33.7))
    logo_mark(cv, 540, 430, 80 * lerp(0.6, 1, bo(prog(t, 33.4, 33.8))), a0, t)
    text_c(cv, 'BONGKAR APA LAGI?', 540, 590, 64, INK, a0 * eo(prog(t, 33.5, 33.8)))
    for txt, x, y, t0, c in CMTS:
        q = prog(t, t0, t0 + 0.3)
        if q <= 0: continue
        aa = a0 * clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
        r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, aa, rad=42, lift=10)
        cv.drawCircle(r.left() + 42, 0, 24, P(col(c, aa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, aa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, aa)))
        cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, aa)))
        cv.restore()
    ca = eo(prog(t, 35.26, 35.55))
    if ca > 0: chip(cv, 'TULIS DI KOMENTAR', 540, 1340, a0 * ca, size=30, bg=ORANGE)

# ------------------------------------------------------------ J: outro (36.6 - 42)
def gJ(cv, t):
    tt = t - 36.6; a = eo(prog(tt, 0.0, 0.4)); p_ = bo(prog(tt, 0.0, 0.6))
    cv.drawCircle(540, 720, 460, P(shader=rg(540, 720, 460, [col(ORANGE, 0.18 * a), col(ORANGE, 0)])))
    logo_mark(cv, 540, 720, 170 * p_, a, t, open_=0.4 + 0.6 * eo(prog(tt, 0.3, 0.9)))
    ta = eo(prog(tt, 0.4, 0.9))
    if ta > 0:
        layer(cv, ta); bb.tracked(cv, 'BONGKAR BENDA', 540, 990, font(XB, 68), P(col(INK)), 8)
        text_c(cv, 'cara kerja benda di sekitarmu', 540, 1058, 30, MUTED, 1.0, f=B); cv.restore()
    press = 1 - 0.08 * bump(prog(tt, 0.75, 1.0)); ba = prog(tt, 0.3, 0.7)
    if ba > 0:
        cv.save(); cv.translate(540, 1200); cv.scale(press, press); cv.translate(-540, -1200)
        chip(cv, 'Follow', 540, 1200, clamp(ba * 1.5), size=44, bg=ORANGE, pad=56); cv.restore()

bb.DRAWERS = [gA, gB, gC, gD, gE, gF, gG, gJ]

def build_sfx():
    ev = [(0.0, 'whoosh'), (0.3, 'grind'), (1.6, 'grind'), (3.85, 'rumble'), (3.87, 'crack'), (3.95, 'buzzer'), (4.45, 'stamp'), (4.5, 'shine'), (4.55, 'ding'),
          (4.7, 'pop'), (4.85, 'pop'), (5.0, 'pop'),
          (5.5, 'whoosh'), (5.7, 'grind'), (6.0, 'pop'), (6.3, 'swish'), (6.35, 'card'), (7.31, 'rise'), (8.1, 'tick'), (8.33, 'zap2'), (8.7, 'pop'),
          (9.0, 'grind'), (9.7, 'pop'), (10.0, 'zap'), (10.97, 'card'), (11.05, 'ding'),
          (12.5, 'whoosh'), (12.62, 'clunk'), (13.0, 'clunk'), (13.1, 'pop'), (13.4, 'clunk'), (13.8, 'clunk'), (13.95, 'grind'), (14.5, 'ding_soft'), (14.55, 'pop'),
          (14.7, 'clunk'), (15.05, 'clunk'), (15.4, 'clunk'), (15.43, 'pop'), (15.55, 'grind'), (16.1, 'ding_soft'), (16.3, 'clunk'), (16.6, 'clunk'), (16.9, 'clunk'),
          (17.1, 'whoosh'), (17.6, 'rumble'), (17.7, 'pop'), (17.75, 'buzzer'), (18.95, 'pour'), (19.0, 'pop'), (19.5, 'pour'), (20.7, 'ding'), (20.8, 'stamp'),
          (21.95, 'whoosh'), (22.0, 'card'), (22.2, 'pop'), (23.7, 'tick'), (26.09, 'pop'), (27.12, 'pop'), (27.17, 'ding_soft'),
          (28.8, 'whoosh'), (29.0, 'pop'), (30.2, 'rise'), (31.9, 'ding'), (32.1, 'pop'), (32.3, 'card'),
          (33.4, 'whoosh'), (33.5, 'shine'), (33.9, 'pop'), (34.15, 'pop'), (34.4, 'pop'), (34.65, 'pop'), (35.26, 'pop'),
          (36.6, 'whoosh'), (36.75, 'boing'), (37.1, 'shine'), (37.35, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
