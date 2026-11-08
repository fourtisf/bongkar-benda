#!/usr/bin/env python3
"""Bongkar Benda #03: 'Jembatan Suramadu, kok nggak ambruk?'
Diorama laut isometrik yang dibelah (air + dasar laut) dengan jembatan cable-stayed: dua menara H, kabel kipas, dek, mobil, kapal.
Hook: bentang tengah tanpa tiang, dek melengkung (AMBRUK?), kabel menyala & dek lurus lagi. Alasan 1: kabel menarik dek ke menara, beban truk dibagi ke
banyak kabel. Alasan 2: menara meneruskan beban ke pondasi di dasar laut (gaya tekan). Alasan 3: kabel kiri & kanan saling mengimbangi, menara tegak.
Sejarah: Fausto Veranzio, Machinae Novae (1595), jembatan digantung rantai besi. Penutup: Suramadu 5.438 m, ruang bebas kapal 35 m. Sumber: content/EP03_suramadu.md
python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, YELLOW, RED, WHITE, text_c, mono, card, chip, label, check, logo_mark)
from iso import Iso, tone, quad, box, shadow, poly, ring_pts

SH = -1.976                                                    # hook baru 1,976 dtk lebih pendek: adegan B..J digeser
bb.DUR = 47.67 + SH
bb.TITLE = ('Jembatan Suramadu,', 'kok nggak ambruk?'); bb.TITLE_OUT = 5.0
_G = [(8.69, 15.88, 'B'), (15.88, 21.45, 'C'), (21.45, 27.01, 'D'), (27.01, 33.16, 'E'), (33.16, 39.19, 'F'), (39.19, 42.47, 'G'), (42.47, 47.67, 'J')]
bb.GROUPS = [(0.0, 8.69 + SH, 'A')] + [(round(a_ + SH, 3), round(b_ + SH, 3), k) for a_, b_, k in _G]
_PH0 = [(0.15, 'Tengah [jembatan] ini'), (1.88, 'nggak punya [tiang] sama sekali.'), (3.7, 'Kok nggak [ambruk] ke laut?'), (5.16, 'Ini [alasannya].')]
_PH = [(8.69, '[Pertama],'), (9.59, '[kabel-kabel baja] ini'), (11.18, '[menarik] jalan ke arah menara.'), (12.69, 'Beratnya dibagi ke [banyak kabel] sekaligus.'),
              (15.88, '[Kedua],'), (16.61, 'menara meneruskan semua beban itu [ke bawah],'), (19.33, 'sampai ke [pondasi] di dasar laut.'),
              (21.45, '[Ketiga],'), (22.26, 'kabel di kiri dan kanan menara [saling mengimbangi].'), (25.21, 'Jadi menaranya [tetap tegak].'),
              (27.01, 'Idenya sudah digambar'), (28.3, '[Fausto Veranzio]'), (29.5, 'tahun [1595]:'), (30.83, 'jembatan yang [digantung rantai besi].'),
              (33.16, '[Suramadu] sendiri'), (34.33, 'panjangnya [lebih dari 5 km].'), (36.45, 'Dan di bawahnya,'), (37.51, '[kapal] masih bisa lewat.'),
              (39.19, 'Benda apa yang mau kamu [bongkar] berikutnya?'), (41.25, 'Tulis di [komentar]!'),
              (42.47, 'Follow [Bongkar Benda],'), (43.61, 'biar makin paham [cara kerja benda] di sekitarmu.')]
bb.PHRASES = _PH0 + [(round(t_ + SH, 3), txt) for t_, txt in _PH]

# ------------------------------------------------------------ dunia: laut yang dibelah + jembatan kabel
WORLD = Iso(0, 0, 50)
PX, DZ, DT, DW, LY, PH = 14.0, 7.0, 0.7, 1.7, 2.05, 22.5      # menara di x = +-PX; dek atas z=DZ; lebar dek +-DW; kaki menara y=+-LY; puncak PH
SPAN_END = 34.0                                               # ujung bentang samping (pilar ujung)
CK = [(2.4 + 1.45 * k, 15.6 + 0.88 * k) for k in range(8)]    # kabel: (jarak angkur dek dari menara, tinggi angkur di menara)
SEA_Z, BED_Z, SOIL_Z = 0.0, -6.0, -12.0
SOIL = [(BED_Z, BED_Z - 0.6, '#E6CFA8'), (BED_Z - 0.6, BED_Z - 2.6, '#D9B88C'), (BED_Z - 2.6, BED_Z - 4.4, '#C99E73'), (BED_Z - 4.4, -40, '#B88B63')]
NAVY, NAVY2 = '#2A3F6B', '#1A2A4C'
CONC, CONC_E = '#F1EADF', '#C5B8A6'
CABLE = '#6A7894'

def P3(x, y, z): return WORLD.p(x, y, z)
def cam(cv, wx, wy, zoom, sx=540, sy=760): cv.translate(sx, sy); cv.scale(zoom, zoom); cv.translate(-wx, -wy)
def scr(p, f, zoom, sx, sy): return (sx + (p[0] - f[0]) * zoom, sy + (p[1] - f[1]) * zoom)
def wav(u, k): return 0.07 * math.sin(1.25 * u + 1.7 * k) + 0.045 * math.sin(2.9 * u + 0.6 * k)
def fpt(plane, pv, u, z): return P3(u, pv, z) if plane == 'y' else P3(pv, u, z)

def arrow(cv, p0, p1, c, a, w=9, head=20):
    if a <= 0: return
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); hx, hy = p1[0] - math.cos(ang) * head * 0.8, p1[1] - math.sin(ang) * head * 0.8
    pth = skia.Path(); pth.moveTo(*p1)
    pth.lineTo(p1[0] - head * math.cos(ang - 0.45), p1[1] - head * math.sin(ang - 0.45)); pth.lineTo(p1[0] - head * math.cos(ang + 0.45), p1[1] - head * math.sin(ang + 0.45)); pth.close()
    cv.drawLine(p0[0], p0[1], hx, hy, P(col(WHITE, a), stroke=w + 7)); cv.drawPath(pth, P(col(WHITE, a), stroke=7))
    cv.drawLine(p0[0], p0[1], hx, hy, P(col(c, a), stroke=w)); cv.drawPath(pth, P(col(c, a)))

# ---- laut diorama: permukaan air, muka depan (air tembus pandang + lapisan dasar laut)
def strata_face(cv, plane, pv, u0, u1, a, dk=0.0):
    face = poly([fpt(plane, pv, u0, BED_Z), fpt(plane, pv, u1, BED_Z), fpt(plane, pv, u1, SOIL_Z), fpt(plane, pv, u0, SOIL_Z)])
    cv.save(); cv.clipPath(face, doAntiAlias=True); n = 30
    for k, (z0, z1, c) in enumerate(SOIL):
        us = [lerp(u0, u1, i / n) for i in range(n + 1)]
        top = [fpt(plane, pv, u, z0 + (wav(u, k) if k else 0)) for u in us]
        bot = [fpt(plane, pv, u, z1 + wav(u, k + 1)) for u in us[::-1]]
        cv.drawPath(poly(top + bot), P(shader=lg(*fpt(plane, pv, u0, z0), *fpt(plane, pv, u0, max(z1, SOIL_Z)), [col(tone(c, dk + 0.05), a), col(tone(c, dk - 0.06), a)])))
        if k: cv.drawPath(poly(top, False), P(col(tone(c, -0.35), 0.35 * a), stroke=1.4))
    cv.restore()
    cv.drawPath(face, P(col('#8C6A4A', 0.5 * a), stroke=1.5))
def water_face(cv, plane, pv, u0, u1, a, dk=0.0):
    q = poly([fpt(plane, pv, u0, SEA_Z), fpt(plane, pv, u1, SEA_Z), fpt(plane, pv, u1, BED_Z), fpt(plane, pv, u0, BED_Z)])
    cv.drawPath(q, P(shader=lg(*fpt(plane, pv, u0, SEA_Z), *fpt(plane, pv, u0, BED_Z), [col(tone('#5B76A6', dk), 0.82 * a), col(tone('#22345C', dk), 0.92 * a)])))
    ln = poly([fpt(plane, pv, lerp(u0, u1, i / 40), SEA_Z) for i in range(41)], False)
    cv.drawPath(ln, P(col(WHITE, 0.6 * a), stroke=2.5))
def sea_top(cv, t, x0, x1, y0, y1, a):
    quad(cv, WORLD, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], '#4A6496', a, grad=((x0, y1, 0), (x1, y0, 0), '#6681B0', '#3A5487'))
    rnd = random.Random(5)
    for k in range(int((x1 - x0) * (y1 - y0) / 14)):                    # riak air bergerak pelan (garis, tanpa titik)
        x = x0 + (rnd.uniform(0, 1) * (x1 - x0) + t * 0.35) % (x1 - x0); y = rnd.uniform(y0 + 0.5, y1 - 0.5); L = rnd.uniform(0.5, 1.2)
        if x + L > x1: continue
        al = a * 0.45 * (0.5 + 0.5 * math.sin(t * 2.2 + k))
        p0, p1 = P3(x, y, 0.01), P3(x + L, y, 0.01); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, al), stroke=2))
def sea_block(cv, t, x0, x1, y0, y1, a, top=True):
    """balok laut: muka kiri = bidang y=y1, muka kanan = bidang x=x1"""
    if top: sea_top(cv, t, x0, x1, y0, y1, a)
    strata_face(cv, 'y', y1, x0, x1, a); strata_face(cv, 'x', x1, y0, y1, a, dk=-0.1)
def sea_fronts(cv, x0, x1, y0, y1, a):
    water_face(cv, 'y', y1, x0, x1, a); water_face(cv, 'x', x1, y0, y1, a, dk=-0.1)

# ---- silinder tegak (tiang pondasi)
def vcyl(cv, x, y, z0, z1, r, c, a, n=20):
    for i in range(n):
        ta, tb = math.radians(lerp(-45, 135, i / n)), math.radians(lerp(-45, 135, (i + 1) / n)); tm = (ta + tb) / 2
        k = 0.18 * math.cos(tm + 0.8) - 0.05
        cv.drawPath(poly([P3(x + r * math.cos(ta), y + r * math.sin(ta), z0), P3(x + r * math.cos(tb), y + r * math.sin(tb), z0),
                          P3(x + r * math.cos(tb), y + r * math.sin(tb), z1), P3(x + r * math.cos(ta), y + r * math.sin(ta), z1)]), P(col(tone(c, k), a)))
    cv.drawPath(poly(ring_pts(WORLD, x, y, z1, r, axis='z', n=24)), P(col(tone(c, 0.25), a)))

# ---- jembatan
_HINGE = [0.0]                                                 # sudut runtuh (derajat), hanya untuk hook
def deck_dz(x, sag):
    dz = -sag * max(0.0, 1 - (x / PX) ** 2) if abs(x) < PX else 0.0
    if _HINGE[0] and abs(x) < PX: dz -= (PX - abs(x)) * math.tan(math.radians(_HINGE[0]))
    return dz
def pylon(cv, px, a, side, tilt=0.0, glow=0.0, comp=0.0, t=0.0):
    """menara H: kaki di y=+-LY. side='far' (kaki y<0 + balok silang) atau 'near' (kaki y>0)"""
    legs = [(-LY,)] if side == 'far' else [(LY,)]
    for (ly,) in legs:
        sh = tilt * 0.0
        box(cv, WORLD, px - 0.45, ly - 0.4, 0.6, 0.9, 0.8, PH - 0.6, CONC, a, top=0.3, left=0.02, right=-0.16)
        if comp > 0:                                                      # denyut gaya tekan turun di kaki menara
            for j in range(3):
                u = (t * 0.6 + j / 3) % 1.0; zz = lerp(PH - 1.0, 0.8, u)
                p0, p1 = P3(px + 0.45, ly + 0.4, zz + 1.6), P3(px + 0.45, ly + 0.4, zz)
                arrow(cv, p0, p1, NAVY, a * comp * bump(u) * 1.2, w=8, head=18)
    if side == 'far':
        for zb, h in ((DZ - DT - 0.7, 0.7), (PH - 3.4, 0.8), (PH - 0.7, 0.7)):
            box(cv, WORLD, px - 0.4, -LY + 0.4, zb, 0.8, 2 * LY - 0.8, h, CONC, a, top=0.3, left=0.0, right=-0.16)
        if glow > 0:
            p = P3(px, 0, PH - 0.4); cv.drawCircle(p[0], p[1], 40, P(col(ORANGE, 0.5 * glow * a), blur=20))
def pile_cap(cv, px, a, piles=False, y_cut=None):
    if piles:
        for yy in (-2.2, -0.75, 0.75, 2.2):
            for xx in (-1.5, 0.0, 1.5):
                if y_cut is not None and yy > y_cut + 0.5: continue
                vcyl(cv, px + xx, yy, SOIL_Z + 1.0, -0.9, 0.38, '#B9AE9F', a)
    box(cv, WORLD, px - 2.4, -3.0, -0.9, 4.8, 6.0, 1.5, '#DCD2C5', a, top=0.25, left=0.0, right=-0.14)
def end_pier(cv, x, a):
    box(cv, WORLD, x - 0.5, -1.4, -0.4, 1.0, 2.8, DZ - DT + 0.4, CONC, a, top=0.3, left=0.02, right=-0.16)
def deck(cv, t, a, x0, x1, sag=0.0, crack=0.0):
    """dek dipotong per segmen supaya bisa melengkung (sag) di bentang tengah"""
    n = int((x1 - x0) / 0.8) + 1
    xs = [lerp(x0, x1, i / n) for i in range(n + 1)]
    for xa, xb in zip(xs[:-1], xs[1:]):
        za, zb_ = DZ + deck_dz(xa, sag), DZ + deck_dz(xb, sag)
        quad(cv, WORLD, [(xa, DW, za), (xb, DW, zb_), (xb, DW, zb_ - DT), (xa, DW, za - DT)], NAVY, a)                 # muka samping
        quad(cv, WORLD, [(xa, DW, za - 0.24), (xb, DW, zb_ - 0.24), (xb, DW, zb_ - 0.32), (xa, DW, za - 0.32)], ORANGE, a)
        quad(cv, WORLD, [(xa, -DW, za), (xb, -DW, zb_), (xb, DW, zb_), (xa, DW, za)], '#4A5368', a)                     # aspal
    for i, (xa, xb) in enumerate(zip(xs[:-1], xs[1:])):
        if i % 2: continue
        za, zb_ = DZ + deck_dz(xa, sag) + 0.004, DZ + deck_dz(xb, sag) + 0.004
        quad(cv, WORLD, [(xa, -0.06, za), (xb, -0.06, zb_), (xb, 0.06, zb_), (xa, 0.06, za)], '#F2EEE8', 0.85 * a)
    for yy in (-DW + 0.05, DW - 0.05):                                    # pagar tepi
        pts = [P3(x, yy, DZ + deck_dz(x, sag) + 0.28) for x in xs]; cv.drawPath(poly(pts, False), P(col('#C9CFD9', a), stroke=2))
    xe = x1; ze = DZ + deck_dz(xe, sag)
    quad(cv, WORLD, [(xe, -DW, ze), (xe, DW, ze), (xe, DW, ze - DT), (xe, -DW, ze - DT)], tone(NAVY, -0.2), a)
    if crack > 0:
        for k, x in enumerate((-2.0, 0.6, 2.8)):
            rnd = random.Random(40 + k); pts = [(x, DZ - DT)]
            for _ in range(4): pts.append((pts[-1][0] + rnd.uniform(-0.3, 0.3), pts[-1][1] + DT / 4))
            sp = [P3(px_, DW + 0.01, pz + deck_dz(px_, sag)) for px_, pz in pts]
            cv.drawPath(poly(sp, False), P(col(RED, crack * a), stroke=4))
def cables(cv, t, a, px, plane, sag=0.0, glow=None, sides=('main', 'back'), side_a=None, cab_a=1.0):
    """kabel kipas dari menara px; plane y: -LY (belakang) atau +LY (depan); glow[(sisi,k)] 0..1"""
    for sd in sides:
        sgn = -1 if (sd == 'main') == (px > 0) else 1                     # bentang tengah ke arah x=0
        aa = a * cab_a * (side_a if (side_a is not None and sd == 'back') else 1.0)
        if aa <= 0: continue
        for k, (d, hz) in enumerate(CK):
            xd = px + sgn * d; zd = DZ + deck_dz(xd, sag)
            yd = plane * DW / LY
            p0, p1 = P3(px, plane, hz), P3(xd, yd, zd)
            g = glow.get((sd, k), 0.0) if glow else 0.0
            if g > 0: cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(ORANGE, 0.55 * g * aa), stroke=10, blur=6))
            cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(mixc(CABLE, ORANGE, g), aa), stroke=2.6 + 2.4 * g))
def bridge(cv, t, a, sag=0.0, crack=0.0, glow=None, cars=True, x0=-SPAN_END - 2, x1=SPAN_END + 2, truck=None, side_a=None, pylons=(-PX, PX),
           comp=0.0, piles=False, y_cut=None, extra=None, cab_a=1.0):
    """urutan gambar: belakang -> depan (kabel & kaki belakang, dek, mobil, kaki & kabel depan)"""
    for px in pylons: pile_cap(cv, px, a, piles, y_cut)
    for x in (-SPAN_END, SPAN_END):
        if x0 <= x <= x1: end_pier(cv, x, a)
    for px in pylons:
        cables(cv, t, a, px, -LY, sag, glow, side_a=side_a, cab_a=cab_a); pylon(cv, px, a, 'far', comp=comp, t=t)
    deck(cv, t, a, x0, x1, sag, crack)
    if cars: traffic(cv, t, a, x0, x1, sag)
    if truck is not None: truck_draw(cv, truck, 0.85, a, sag)
    if extra: extra()
    for px in pylons:
        pylon(cv, px, a, 'near', comp=comp, t=t); cables(cv, t, a, px, LY, sag, glow, side_a=side_a, cab_a=cab_a)

def car3(cv, x, y, z, c, a, L=1.15):
    shadow(cv, WORLD, x, y - 0.3, z, L, 0.6, a, blur=4, k=0.3)
    box(cv, WORLD, x, y - 0.3, z + 0.06, L, 0.6, 0.28, c, a, top=0.22)
    box(cv, WORLD, x + 0.28, y - 0.26, z + 0.34, L * 0.5, 0.52, 0.22, '#5A6B8C' if c == NAVY else NAVY, a, top=0.35)
def traffic(cv, t, a, x0, x1, sag):
    L = x1 - x0; items = []
    for k, (y, v, c, ph) in enumerate(((-0.85, 3.2, ORANGE, 0.05), (-0.85, 3.2, '#F7F4EF', 0.3), (-0.85, 3.2, NAVY, 0.62), (-0.85, 3.2, '#F7F4EF', 0.84),
                                      (0.85, -2.8, '#F7F4EF', 0.18), (0.85, -2.8, ORANGE, 0.45), (0.85, -2.8, NAVY, 0.72))):
        x = x0 + ((ph * L + v * t) % L)
        if x + 1.15 > x1: continue
        items.append((x + y, x, y, c))
    for _, x, y, c in sorted(items): car3(cv, x, y, DZ + deck_dz(x + 0.6, sag), c, a)
def truck_draw(cv, x, y, a, sag):
    z = DZ + deck_dz(x + 1.2, sag)
    shadow(cv, WORLD, x, y - 0.38, z, 2.6, 0.76, a, blur=5, k=0.35)
    box(cv, WORLD, x, y - 0.38, z + 0.1, 1.9, 0.76, 0.9, '#F4F0EA', a, top=0.15)
    box(cv, WORLD, x + 1.95, y - 0.36, z + 0.1, 0.7, 0.72, 0.7, ORANGE, a, top=0.22)
    quad(cv, WORLD, [(x + 2.65, y - 0.26, z + 0.45), (x + 2.65, y + 0.26, z + 0.45), (x + 2.65, y + 0.26, z + 0.72), (x + 2.65, y - 0.26, z + 0.72)], NAVY, a)

def ship(cv, t, x, y, a):
    """kapal kargo melaju di sepanjang sumbu y (lambung navy, anjungan putih, cerobong oranye)"""
    shadow(cv, WORLD, x - 1.0, y - 3.4, 0.0, 2.0, 6.8, a, blur=10, k=0.25)
    box(cv, WORLD, x - 1.0, y - 3.2, -0.3, 2.0, 6.4, 1.4, NAVY, a, top=0.35, left=0.05, right=-0.15)
    quad(cv, WORLD, [(x - 1.0, y + 3.2, 0.55), (x + 1.0, y + 3.2, 0.55), (x + 1.0, y + 3.2, 0.7), (x - 1.0, y + 3.2, 0.7)], ORANGE, a)
    for k, c in enumerate((ORANGE, '#F4F0EA', NAVY2, ORANGE_D)):
        box(cv, WORLD, x - 0.75, y - 2.6 + k * 1.05, 1.1, 1.5, 0.95, 0.75, c, a, top=0.25)
    box(cv, WORLD, x - 0.8, y + 1.7, 1.1, 1.6, 1.2, 2.1, '#F4F0EA', a, top=0.2)
    quad(cv, WORLD, [(x - 0.8, y + 2.9, 2.5), (x + 0.8, y + 2.9, 2.5), (x + 0.8, y + 2.9, 2.85), (x - 0.8, y + 2.9, 2.85)], NAVY, a)
    box(cv, WORLD, x - 0.25, y + 2.0, 3.2, 0.5, 0.5, 1.0, ORANGE, a, top=0.25)
    for k in range(3):                                                    # buih di haluan
        ph = (t * 1.5 + k / 3) % 1.0; p0 = P3(x - 1.2 - ph, y + 3.3 - ph * 1.5, 0.02); p1 = P3(x + 1.2 + ph, y + 3.3 - ph * 1.5, 0.02)
        cv.drawLine(p0[0], p0[1], p0[0] + 18, p0[1] - 6, P(col(WHITE, 0.6 * (1 - ph) * a), stroke=3)); cv.drawLine(p1[0], p1[1], p1[0] - 18, p1[1] - 6, P(col(WHITE, 0.6 * (1 - ph) * a), stroke=3))

def scene(cv, t, a, sea=(-46.0, 46.0, -16.0, 12.0), ship_y=None, ship_x=-3.0, **kw):
    """laut diorama + jembatan + kapal; kapal digambar sebelum/sesudah dek tergantung posisinya"""
    x0, x1, y0, y1 = sea
    sea_block(cv, t, x0, x1, y0, y1, a)
    if ship_y is not None and ship_y < 0.3: ship(cv, t, ship_x, ship_y, a)
    bridge(cv, t, a, **kw)
    if ship_y is not None and ship_y >= 0.3: ship(cv, t, ship_x, ship_y, a)
    sea_fronts(cv, x0, x1, y0, y1, a)

# ------------------------------------------------------------ A: HOOK — tanpa tiang; kalau tanpa kabel dek jatuh ke laut; REWIND; kabel menyala (0 - 6.715)
T_CUT, T_FALL, T_HIT, T_RW, T_BACK = 0.55, 0.75, 1.4, 1.95, 2.95
HMAX = math.degrees(math.atan((DZ + 0.4) / PX))
def hinge(t):
    if t < T_FALL: return 0.0
    if t < T_HIT: return HMAX * ei(prog(t, T_FALL, T_HIT))
    if t < T_RW: return HMAX * (1 + 0.02 * math.sin((t - T_HIT) * 30) * (1 - prog(t, T_HIT, T_RW)))
    return HMAX * (1 - eio(prog(t, T_RW, T_BACK)))
def gA(cv, t):
    u = eio(prog(t, 0.0, 3.0))
    fw = (lerp(0.0, 1.5, u), 0.0, lerp(6.0, 8.0, u)); zoom = lerp(1.0, 0.66, u) * (1 + 0.05 * eio(prog(t, 3.4, 6.7)))
    impact = prog(t, T_HIT, T_HIT + 0.5)
    shk = 14 * math.sin(t * 55) * (1 - impact) if T_HIT < t < T_HIT + 0.5 else 0.0
    f = P3(*fw); sx, sy = 540 + shk, 980 + 0.6 * shk
    cab_a = 1.0 if t < T_CUT else (1 - prog(t, T_CUT, T_CUT + 0.15) if t < T_RW else eo(prog(t, T_BACK - 0.35, T_BACK)))
    glow = {}
    for sd in ('main', 'back'):
        for k in range(8):
            glow[(sd, k)] = eo(prog(t, T_BACK - 0.3 + 0.04 * k, T_BACK - 0.05 + 0.04 * k)) * (1 - 0.7 * prog(t, 4.6, 5.6))
    _HINGE[0] = hinge(t)
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    scene(cv, t, 1.0, sea=(-21.0, 25.0, -11.0, 6.0), ship_y=lerp(-9.5, -4.5, prog(t, 0.0, 6.7)), glow=glow, x0=-21.0, x1=25.0, cab_a=cab_a)
    _HINGE[0] = 0.0
    if T_CUT - 0.05 < t < T_CUT + 0.5:                                   # kabel "dilepas": kilat merah putus-putus
        ga = bump(prog(t, T_CUT - 0.05, T_CUT + 0.5))
        for px in (-PX, PX):
            for d, hz in CK:
                for sgn in (-1, 1):
                    p0, p1 = P3(px, LY, hz), P3(px + sgn * d, DW, DZ)
                    cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(RED, 0.8 * ga), stroke=3, effect=skia.DashPathEffect.Make([10, 8], t * 60)))
    if T_HIT - 0.05 < t < T_HIT + 0.9:                                   # cipratan besar di tengah + riak melingkar
        q = prog(t, T_HIT - 0.05, T_HIT + 0.9); rnd = random.Random(9)
        c_ = P3(0, 0, 0); cv.drawCircle(c_[0], c_[1] - 40, 160 * eo(q), P(col(WHITE, 0.55 * (1 - q) ** 2), blur=30))
        for k in range(34):
            ang = rnd.uniform(-math.pi * 0.97, -math.pi * 0.03); L = rnd.uniform(90, 300) * eo(q); c0 = P3(rnd.uniform(-1.8, 1.8), rnd.uniform(-1.8, 1.8), 0)
            x1_, y1_ = c0[0] + math.cos(ang) * L, c0[1] + math.sin(ang) * L * 1.4 + 220 * q * q
            cv.drawLine(c0[0] + math.cos(ang) * L * 0.35, c0[1] + math.sin(ang) * L * 0.45, x1_, y1_, P(col(WHITE, 0.95 * (1 - q)), stroke=7))
        for k in range(3):
            rq = clamp(q * 1.4 - k * 0.2)
            if 0 < rq < 1: cv.drawPath(poly(ring_pts(WORLD, 0, 0, 0.02, 1.5 + 9 * rq, axis='z', n=48)), P(col(WHITE, 0.7 * (1 - rq)), stroke=4))
    gh = eo(prog(t, 0.12, 0.3)) * (1 - prog(t, T_FALL, T_FALL + 0.25))   # tiang bayangan + silang merah
    if gh > 0:
        for yy in (-1.2, 1.2):
            qd = quad(cv, WORLD, [(-0.5, yy, 0), (0.5, yy, 0), (0.5, yy, DZ - DT), (-0.5, yy, DZ - DT)], WHITE, 0.25 * gh)
            cv.drawPath(qd, P(col(NAVY, 0.8 * gh), stroke=3, effect=skia.DashPathEffect.Make([12, 8], 0)))
        p = P3(0, 0, (DZ - DT) / 2); s_ = 70 * eo(prog(t, 0.15, 0.35))
        cv.drawLine(p[0] - s_, p[1] - s_, p[0] + s_, p[1] + s_, P(col(RED, gh), stroke=12)); cv.drawLine(p[0] - s_, p[1] + s_, p[0] + s_, p[1] - s_, P(col(RED, gh), stroke=12))
    cv.restore()
    ta = 1 - eio(prog(t, bb.TITLE_OUT - 0.4, bb.TITLE_OUT))
    if ta > 0: cv.drawRect(skia.Rect(0, 0, 1080, 560), P(shader=lg(0, 380, 0, 600, [col(bb.BG0, ta), col(bb.BG0, 0)])))
    fl = max(bump(prog(t, T_CUT, T_CUT + 0.3)), bump(prog(t, T_HIT, T_HIT + 0.35)))
    if fl > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.22 * fl)))
    if 0.12 < t < T_CUT + 0.05: chip(cv, 'TANPA TIANG', 540, 560, eo(prog(t, 0.12, 0.3)) * (1 - prog(t, T_CUT - 0.1, T_CUT + 0.05)), size=30, bg=INK)
    if T_CUT < t < T_RW + 0.1: chip(cv, 'KALAU TANPA KABEL?', 540, 560, eo(prog(t, T_CUT, T_CUT + 0.15)) * (1 - prog(t, T_RW - 0.1, T_RW + 0.1)), size=30, bg=RED)
    rw = prog(t, T_RW, T_BACK + 0.1)
    if 0 < rw < 1:                                                        # efek REWIND: garis pindai + ikon mundur
        ra = bump(rw) * 1.3
        cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(bb.BG0, 0.14 * clamp(ra))))
        for k in range(14):
            yy = (k * 151 + t * 2400) % 1920; cv.drawRect(skia.Rect(0, yy, 1080, yy + 5), P(col(WHITE, 0.35 * clamp(ra))))
        r = skia.Rect(400, 520, 680, 600); cv.drawRoundRect(r, 40, 40, P(col(INK, clamp(ra))))
        for k in range(2):
            x0_ = 470 + k * 44; tri = skia.Path(); tri.moveTo(x0_, 560); tri.lineTo(x0_ + 38, 536); tri.lineTo(x0_ + 38, 584); tri.close(); cv.drawPath(tri, P(col(WHITE, clamp(ra))))
        f_ = font(MONO, 26); cv.drawString('ULANG', 570, bl(f_, 560), f_, P(col(WHITE, clamp(ra))))
    if t > T_BACK:
        p = scr(P3(PX - CK[5][0] * 0.5, LY, lerp(CK[5][1], DZ, 0.5)), f, zoom, sx, sy)
        la = eo(prog(t, T_BACK + 0.05, T_BACK + 0.4)) * (1 - prog(t, 6.4, 6.7))
        label(cv, 'KABEL BAJA', p[0], p[1], 830, 600, la, sub='menahan jalan')
        check(cv, 975, 535, 26, prog(t, T_BACK + 0.15, T_BACK + 0.55), la)
    ca = eo(prog(t, 3.7, 4.0)) * (1 - prog(t, 5.0, 5.2))
    if ca > 0: chip(cv, 'KOK BISA?', 540, 1340, ca, size=32, bg=ORANGE)
    for k, (num, txt) in enumerate((('1', 'KABEL BAJA'), ('2', 'MENARA'), ('3', 'SEIMBANG'))):
        q = prog(t, 5.25 + 0.15 * k, 5.55 + 0.15 * k)
        if q > 0:
            x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
            cv.save(); cv.translate(x, 1335); cv.scale(s_, s_); cv.translate(-x, -1335)
            card(cv, skia.Rect(x - 155, 1305, x + 155, 1365), aa, rad=30, lift=8)
            cv.drawCircle(x - 120, 1335, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 120, 1335, 24, WHITE, aa)
            text_c(cv, txt, x + 14, 1335, 24, INK, aa)
            cv.restore()

# ------------------------------------------------------------ B: kabel baja menarik jalan ke menara; beban dibagi ke banyak kabel (8.69 - 15.88)
def gB(cv, t):
    a0 = eo(prog(t, 8.69, 9.1))
    zoom = lerp(1.05, 1.18, eio(prog(t, 8.69, 15.88))); fw = (PX - 5.5, 0.0, 12.2); f = P3(*fw); sx, sy = 560, 880
    tx = lerp(-1.0, 11.5, prog(t, 9.0, 15.6))                             # truk melaju ke arah menara kanan
    glow = {}
    for k, (d, hz) in enumerate(CK):
        xd = PX - d
        near = math.exp(-((tx + 1.3 - xd) / 2.2) ** 2) * eo(prog(t, 9.6, 10.0))
        wave = eo(prog(t, 12.69 + 0.07 * (7 - k), 12.69 + 0.07 * (7 - k) + 0.3)) * 0.85
        glow[('main', k)] = clamp(max(near, wave))
        glow[('back', k)] = clamp(wave * 0.7)
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    scene(cv, t, a0, glow=glow, truck=tx, pylons=(PX,), x0=-6.0, x1=SPAN_END + 2)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 9.59, 9.95))
    if la > 0:
        p = S((PX - CK[6][0] * 0.45, LY, lerp(CK[6][1], DZ, 0.45))); label(cv, 'KABEL BAJA', p[0], p[1], 280, 520, a0 * la, sub='menarik dek ke menara')
    ma = eo(prog(t, 11.18, 11.5)) * (1 - prog(t, 15.4, 15.8))
    if ma > 0:                                                            # panah tarik di kabel yang menyala, menuju puncak menara
        for k in (2, 4, 6):
            if glow[('main', k)] < 0.2: continue
            d, hz = CK[k]; pa, pb = S((PX - d, LY, DZ)), S((PX, LY, hz)); q = (t * 0.8 + k * 0.13) % 1.0
            p0 = (lerp(pa[0], pb[0], 0.15 + 0.5 * q), lerp(pa[1], pb[1], 0.15 + 0.5 * q)); p1 = (lerp(pa[0], pb[0], 0.32 + 0.5 * q), lerp(pa[1], pb[1], 0.32 + 0.5 * q))
            arrow(cv, p0, p1, ORANGE, a0 * ma * glow[('main', k)] * bump(q) * 1.3, w=8, head=18)
        chip(cv, 'TARIK', 860, 360, a0 * ma * (1 - prog(t, 12.5, 12.8)), size=28, bg=ORANGE)
    wa = eo(prog(t, 12.69, 13.0))
    if wa > 0:                                                            # berat truk dibagi ke beberapa kabel
        pt = S((tx + 1.3, 0.85, DZ + 1.1)); pd = S((tx + 1.3, 0.85, DZ + 3.4))
        arrow(cv, pd, pt, NAVY, a0 * wa, w=10, head=22)
        for k, (d, hz) in enumerate(CK):
            xd = PX - d
            if abs(xd - (tx + 1.3)) < 4.5:
                pa = S((xd, DW, DZ)); cv.drawLine(pt[0], pt[1], pa[0], pa[1], P(col(ORANGE, 0.8 * a0 * wa * eo(prog(t, 12.9 + 0.05 * k, 13.2 + 0.05 * k))), stroke=4, effect=skia.DashPathEffect.Make([10, 7], -t * 40)))
                cv.drawCircle(pa[0], pa[1], 9, P(col(ORANGE, a0 * wa)))
        text_c(cv, 'BERAT', pd[0], pd[1] - 30, 26, NAVY, a0 * wa, halo=1.0)
        chip(cv, 'DIBAGI KE BANYAK KABEL', 540, 1340, a0 * eo(prog(t, 13.3, 13.6)), size=28, bg=INK)

# ------------------------------------------------------------ C: menara meneruskan beban ke pondasi di dasar laut (15.88 - 21.45)
def gC(cv, t):
    a0 = eo(prog(t, 15.88, 16.3))
    u = eio(prog(t, 15.9, 18.6))
    fw = (PX, 0.0, lerp(11.0, -2.6, u)); zoom = lerp(0.8, 1.12, u); f = P3(*fw); sx, sy = 540, 860
    comp = eo(prog(t, 16.61, 17.0))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    x0, x1, y0, y1 = PX - 9.0, PX + 9.0, -14.0, 0.0                       # laut & dasar laut dibelah tepat di garis tengah menara
    sea_block(cv, t, x0, x1, y0, y1, a0)
    cv.save(); cv.clipPath(poly([P3(x0, y1, SEA_Z), P3(x1, y1, SEA_Z), P3(x1, y1, SOIL_Z), P3(x0, y1, SOIL_Z)]), doAntiAlias=True)
    cv.restore()
    bridge(cv, t, a0, pylons=(PX,), x0=PX - 9.0, x1=PX + 9.0, comp=comp, piles=True, y_cut=0.0, cars=True)
    water_face(cv, 'y', y1, x0, x1, a0 * 0.85); water_face(cv, 'x', x1, y0, y1, a0, dk=-0.1)
    for xx in (-1.5, 0.0, 1.5):                                            # tiang pondasi yang terpotong di bidang depan
        vcyl(cv, PX + xx, 0.75, SOIL_Z + 1.0, -0.9, 0.38, '#B9AE9F', a0)
    if comp > 0:                                                          # gaya tekan turun ke tiang & tanah
        for xx in (-1.5, 0.0, 1.5):
            for j in range(2):
                q = (t * 0.7 + j / 2 + xx * 0.1) % 1.0; zz = lerp(-1.2, SOIL_Z + 1.6, q)
                arrow(cv, P3(PX + xx, 1.2, zz + 1.4), P3(PX + xx, 1.2, zz), NAVY, a0 * comp * bump(q) * eo(prog(t, 19.33, 19.7)), w=8, head=18)
        pg = eo(prog(t, 19.33, 19.8))
        if pg > 0:
            cv.drawPath(poly([P3(PX - 2.6, 1.5, SOIL_Z + 0.6), P3(PX + 2.6, 1.5, SOIL_Z + 0.6), P3(PX + 2.6, 1.5, BED_Z), P3(PX - 2.6, 1.5, BED_Z)]), P(col(ORANGE, 0.22 * pg * a0), blur=18))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 16.61, 17.0))
    if la > 0:
        p = S((PX + 0.45, LY + 0.4, lerp(DZ + 4, 1.0, u))); label(cv, 'MENARA', p[0], p[1], 260, 420, a0 * la * (1 - prog(t, 19.0, 19.3)), dot=NAVY, sub='menekan ke bawah')
    pa = eo(prog(t, 19.33, 19.7))
    if pa > 0:
        p = S((PX + 1.5, 0.75, SOIL_Z + 3.0)); label(cv, 'PONDASI', p[0], p[1], 830, 1190, a0 * pa, dot=NAVY, sub='tertanam di dasar laut')
    ca = eo(prog(t, 17.4, 17.7)) * (1 - prog(t, 19.1, 19.4))
    if ca > 0: chip(cv, 'GAYA TEKAN', 540, 300, a0 * ca, size=28, bg=NAVY)

# ------------------------------------------------------------ D: kabel kiri & kanan saling mengimbangi, menara tetap tegak (21.45 - 27.01)
def gD(cv, t):
    a0 = eo(prog(t, 21.45, 21.85))
    zoom = lerp(0.98, 1.05, eio(prog(t, 21.45, 27.01))); fw = (PX, 0.0, 14.5); f = P3(*fw); sx, sy = 540, 860
    gh = eo(prog(t, 22.9, 23.3)) * (1 - eio(prog(t, 24.2, 24.7)))          # andai satu sisi hilang: menara miring (bayangan merah)
    side_a = 1 - 0.85 * gh
    glow = {}
    for k in range(8):
        pl = 0.5 + 0.5 * math.sin(t * 5 + k * 0.4)
        glow[('main', k)] = eo(prog(t, 22.26, 22.6)) * (0.55 + 0.45 * pl)
        glow[('back', k)] = eo(prog(t, 22.26, 22.6)) * (0.55 + 0.45 * pl) * side_a
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    scene(cv, t, a0, glow=glow, pylons=(PX,), x0=PX - 15.0, x1=SPAN_END + 2, side_a=side_a)
    if gh > 0:
        cv.save(); pv = P3(PX, 0, DZ - DT); cv.translate(*pv); cv.rotate(-12 * gh); cv.translate(-pv[0], -pv[1])
        q = poly([P3(PX - 0.45, LY + 0.4, DZ - DT), P3(PX + 0.45, LY + 0.4, DZ - DT), P3(PX + 0.45, LY + 0.4, PH), P3(PX - 0.45, LY + 0.4, PH)])
        cv.drawPath(q, P(col(RED, 0.18 * gh))); cv.drawPath(q, P(col(RED, 0.9 * gh), stroke=4, effect=skia.DashPathEffect.Make([14, 9], 0)))
        cv.restore()
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    top = S((PX, 0, PH - 1.0))
    fa = eo(prog(t, 22.26, 22.6))
    if fa > 0:                                                            # dua tarikan sama besar di puncak menara
        L = 150 * (0.92 + 0.08 * math.sin(t * 5)); dl = S((PX - 6, 0, PH - 3.0)); dr = S((PX + 6, 0, PH - 3.0))
        def unit(p): dx, dy = p[0] - top[0], p[1] - top[1]; n = math.hypot(dx, dy); return dx / n, dy / n
        ul, ur = unit(dl), unit(dr)
        arrow(cv, (top[0] + ul[0] * 30, top[1] + ul[1] * 30), (top[0] + ul[0] * (30 + L), top[1] + ul[1] * (30 + L)), ORANGE, a0 * fa, w=11, head=26)
        arrow(cv, (top[0] + ur[0] * 30, top[1] + ur[1] * 30), (top[0] + ur[0] * (30 + L * side_a), top[1] + ur[1] * (30 + L * side_a)), ORANGE, a0 * fa * clamp(side_a * 1.5), w=11, head=26)
        text_c(cv, 'TARIK', top[0] + ul[0] * (L + 95), top[1] + ul[1] * (L + 95) - 26, 26, ORANGE_D, a0 * fa, halo=1.0)
        text_c(cv, 'TARIK', top[0] + ur[0] * (L + 95), top[1] + ur[1] * (L + 95) - 26, 26, ORANGE_D, a0 * fa * side_a, halo=1.0)
    if gh > 0.05: chip(cv, 'SATU SISI SAJA? MIRING!', 540, 300, a0 * gh, size=26, bg=RED)
    ba = eo(prog(t, 24.6, 25.0))
    if ba > 0:                                                            # timbangan seimbang (ikon)
        cx, cy = 540, 300; tilt = 6 * math.sin(t * 3) * (1 - prog(t, 25.0, 25.6))
        card(cv, skia.Rect(cx - 170, cy - 60, cx + 170, cy + 60), a0 * ba, rad=30)
        cv.save(); cv.translate(cx, cy + 8); cv.rotate(tilt)
        cv.drawLine(-110, 0, 110, 0, P(col(INK, a0 * ba), stroke=7))
        for sx_ in (-110, 110): cv.drawRoundRect(skia.Rect(sx_ - 34, 6, sx_ + 34, 26), 8, 8, P(col(ORANGE, a0 * ba)))
        cv.restore()
        tri = skia.Path(); tri.moveTo(cx, cy + 8); tri.lineTo(cx - 20, cy + 44); tri.lineTo(cx + 20, cy + 44); tri.close(); cv.drawPath(tri, P(col(INK, a0 * ba)))
    pa = eo(prog(t, 25.21, 25.5))
    if pa > 0:                                                            # garis tegak lurus + TETAP TEGAK
        p0, p1 = S((PX + 0.0, LY + 0.4, PH + 1.2)), S((PX + 0.0, LY + 0.4, DZ + 0.2))
        cv.drawLine(p0[0] + 40, p0[1], p1[0] + 40, p1[1], P(col(INK, a0 * pa), stroke=3, effect=skia.DashPathEffect.Make([12, 8], 0)))
        cv.drawCircle(p1[0] + 40, p1[1], 10, P(col(INK, a0 * pa)))
        chip(cv, 'TETAP TEGAK', 540, 1340, a0 * pa, size=30, bg=ORANGE); check(cv, 735, 1340, 22, prog(t, 25.3, 25.7), a0 * pa)

# ------------------------------------------------------------ E: Fausto Veranzio, Machinae Novae 1595: jembatan digantung rantai besi (27.01 - 33.16)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def veranzio_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'MACHINAE NOVAE · 1595', 540, r.top() + 72, 24, SEPIA_INK, a, sp=5)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    wy = 860                                                              # sungai
    cv.drawRect(skia.Rect(r.left(), wy, r.right(), r.bottom()), P(col('#E6D3AE', a)))
    for k in range(4):
        p = skia.Path(); yy = wy + 30 + k * 45; p.moveTo(r.left(), yy)
        for i in range(30): x = r.left() + i * 32; p.quadTo(x + 8, yy - 7 + 2 * math.sin(t * 2 + k), x + 16, yy); p.quadTo(x + 24, yy + 7, x + 32, yy)
        cv.drawPath(p, ink(0.45, 2.5))
    for bx in (150, 830):                                                 # tepian
        bank = skia.Path(); sd = 1 if bx < 540 else -1
        bank.moveTo(bx - sd * 60, wy - 60); bank.lineTo(bx + sd * 120, wy - 60); bank.lineTo(bx + sd * 90, wy + 40); bank.lineTo(bx - sd * 60, wy + 40); bank.close()
        cv.drawPath(bank, P(col('#C9A577', a))); cv.drawPath(bank, ink())
    tw = [(300, 380), (780, 380)]                                          # dua menara kayu-batu
    for x, ytop in tw:
        cv.drawRect(skia.Rect(x - 26, ytop, x + 26, wy - 30), P(col('#B58A57', a))); cv.drawRect(skia.Rect(x - 26, ytop, x + 26, wy - 30), ink())
        for k in range(8): cv.drawLine(x - 26, ytop + 40 + k * 50, x + 26, ytop + 40 + k * 50, ink(0.5, 2))
        cv.drawRect(skia.Rect(x - 36, ytop - 20, x + 36, ytop), P(col('#A07548', a))); cv.drawRect(skia.Rect(x - 36, ytop - 20, x + 36, ytop), ink())
    dy = 700; cv.drawRect(skia.Rect(150, dy, 930, dy + 26), P(col('#C9A577', a))); cv.drawRect(skia.Rect(150, dy, 930, dy + 26), ink())
    for k in range(18): cv.drawLine(160 + k * 44, dy, 160 + k * 44, dy + 26, ink(0.5, 2))
    sw = 1.5 * math.sin(t * 1.6)
    for x, ytop in tw:                                                    # rantai besi miring dari puncak menara ke dek
        for k in range(5):
            for sd in (-1, 1):
                xe = x + sd * (60 + k * 50); ye = dy + sw
                n = int(math.hypot(xe - x, ye - ytop - 10) / 16)
                for j in range(n):
                    u0 = j / n; px_, py_ = lerp(x, xe, u0), lerp(ytop + 10, ye, u0); ang = math.degrees(math.atan2(ye - ytop - 10, xe - x))
                    cv.save(); cv.translate(px_, py_); cv.rotate(ang)
                    cv.drawRoundRect(skia.Rect(-8, -4 if j % 2 else -2, 8, 4 if j % 2 else 2), 4, 4, ink(0.85, 2)); cv.restore()
    hx, hy = 540, 702                                                     # Veranzio: berjanggut, kerah lebar, topi
    cv.drawRoundRect(skia.Rect(hx - 26, hy - 120, hx + 26, hy - 20), 14, 14, P(col('#3E2E22', a)))
    cv.drawOval(skia.Rect(hx - 34, hy - 136, hx + 34, hy - 114), P(col('#FBF3E2', a))); cv.drawOval(skia.Rect(hx - 34, hy - 136, hx + 34, hy - 114), ink(1, 2))
    cv.drawCircle(hx, hy - 158, 22, P(col('#E8C9A0', a))); cv.drawCircle(hx, hy - 158, 22, ink(1, 2.5))
    beard = skia.Path(); beard.moveTo(hx - 18, hy - 152); beard.quadTo(hx, hy - 110, hx + 18, hy - 152); beard.close(); cv.drawPath(beard, P(col('#5A4030', a)))
    cv.drawOval(skia.Rect(hx - 26, hy - 192, hx + 26, hy - 170), P(col('#2A1F17', a)))
    cv.drawLine(hx + 22, hy - 100, hx + 70, hy - 130 + 4 * math.sin(t * 3), P(col('#3E2E22', a), stroke=10))
    cv.drawRect(skia.Rect(hx + 62, hy - 160, hx + 110, hy - 120), P(col('#FBF3E2', a))); cv.drawRect(skia.Rect(hx + 62, hy - 160, hx + 110, hy - 120), ink(1, 2))
    cv.restore()
def gE(cv, t):
    a0 = eo(prog(t, 27.01, 27.45))
    cv.save(); cv.translate(540, 770); cv.scale(1.14, 1.14); cv.translate(-540, -700)
    veranzio_card(cv, t, a0)
    cv.restore()
    S = lambda x, y: (540 + (x - 540) * 1.14, 770 + (y - 700) * 1.14)
    na = eo(prog(t, 28.3, 28.65))
    if na > 0: p = S(540, 530); label(cv, 'FAUSTO VERANZIO', p[0], p[1], 300, 1240, a0 * na, size=26, sub='penemu, penulis Machinae Novae')
    ra = eo(prog(t, 30.83, 31.2))
    if ra > 0: p = S(380, 560); label(cv, 'RANTAI BESI', p[0], p[1], 820, 1240, a0 * ra, size=26, sub='menggantung jalan')

# ------------------------------------------------------------ F: Suramadu lebih dari 5 km; kapal masih bisa lewat di bawahnya (33.16 - 39.19)
def viaduct(cv, a, x0, x1, step=4.0):
    x = x0
    while x < x1 - 0.01:
        xb = min(x + step, x1)
        box(cv, WORLD, x + step / 2 - 0.35, -0.9, -0.3, 0.7, 1.8, DZ - DT + 0.3, CONC, a, top=0.3, right=-0.16)
        quad(cv, WORLD, [(x, DW, DZ), (xb, DW, DZ), (xb, DW, DZ - DT), (x, DW, DZ - DT)], NAVY, a)
        quad(cv, WORLD, [(x, DW, DZ - 0.24), (xb, DW, DZ - 0.24), (xb, DW, DZ - 0.32), (x, DW, DZ - 0.32)], ORANGE, a)
        quad(cv, WORLD, [(x, -DW, DZ), (xb, -DW, DZ), (xb, DW, DZ), (x, DW, DZ)], '#4A5368', a)
        x = xb
def gF(cv, t):
    a0 = eo(prog(t, 33.16, 33.6)); u = eio(prog(t, 36.2, 37.4))
    fw = (lerp(0.0, -1.0, u), 0.0, lerp(5.0, 4.5, u)); zoom = lerp(0.36, 0.9, u) * (1 + 0.03 * eio(prog(t, 33.16, 36.2))); f = P3(*fw); sx, sy = 540, 900
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    xr = 110.0 if u < 0.999 else 40.0
    sea_block(cv, t, -xr, xr, -24.0, 14.0, a0)
    sy_ = lerp(-16, 9, prog(t, 35.6, 39.19))
    if sy_ < 0.3: ship(cv, t, -3.0, sy_, a0)
    viaduct(cv, a0, -xr, -SPAN_END - 2); bridge(cv, t, a0); viaduct(cv, a0, SPAN_END + 2, xr)
    if sy_ >= 0.3: ship(cv, t, -3.0, sy_, a0)
    sea_fronts(cv, -xr, xr, -24.0, 14.0, a0)
    ra = eo(prog(t, 37.51, 37.9))
    if ra > 0:                                                            # penggaris ruang bebas kapal
        zz = lerp(0, DZ - DT, eo(prog(t, 37.51, 38.4))); p0, p1 = P3(3.0, DW + 1.0, 0), P3(3.0, DW + 1.0, zz)
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(ORANGE, a0 * ra), stroke=8))
        for k in range(8):
            if k * (DZ - DT) / 7 > zz + 0.01: continue
            pa = P3(3.0, DW + 1.0, k * (DZ - DT) / 7); cv.drawLine(pa[0], pa[1], pa[0] + 18, pa[1], P(col(INK, a0 * ra), stroke=3))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    ca = eo(prog(t, 33.4, 33.8)) * (1 - prog(t, 36.0, 36.4))
    if ca > 0:                                                            # kartu panjang jembatan
        r = skia.Rect(170, 250, 910, 470); card(cv, r, a0 * ca, rad=30)
        mono(cv, 'SURAMADU · SURABAYA – MADURA', 540, r.top() + 48, 22, MUTED, a0 * ca, sp=3)
        n = int(lerp(0, 5438, eo(prog(t, 34.33, 35.6))))
        text_c(cv, f'{n:,}'.replace(',', '.') + ' m', 540, r.top() + 140, 96, INK, a0 * ca)
    la = eo(prog(t, 34.6, 35.0)) * (1 - prog(t, 36.0, 36.3))
    if la > 0:                                                            # garis ukur di atas jembatan, menjulur ke luar layar
        pa, pb = S((-xr, 0, DZ + 9)), S((xr, 0, DZ + 9))
        cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col(ORANGE, a0 * la), stroke=6))
        chip(cv, 'LEBIH DARI 5 KM', 540, 1340, a0 * la, size=28, bg=ORANGE)
    if ra > 0:
        p = S((3.0, DW + 1.0, (DZ - DT) / 2)); text_c(cv, '35 m', p[0] + 110, p[1], 60, ORANGE, a0 * ra, halo=1.0)
        lb = eo(prog(t, 37.9, 38.2)); pk = S((-3.0, sy_, 2.5))
        if lb > 0: label(cv, 'RUANG KAPAL', pk[0], pk[1], 270, 480, a0 * lb, dot=NAVY, sub='di bawah bentang tengah')

# ------------------------------------------------------------ G: bongkar apa lagi? tulis di komentar (39.19 - 42.47)
CMTS = [('pesawat!', 280, 760, 39.6, ORANGE), ('bendungan dong', 760, 900, 39.85, INK), ('kereta cepat pls', 310, 1040, 40.1, ORANGE_D), ('tower crane!!', 760, 1180, 40.35, NAVY)]
def gG(cv, t):
    a0 = eo(prog(t, 39.19, 39.5))
    logo_mark(cv, 540, 430, 80 * lerp(0.6, 1, bo(prog(t, 39.19, 39.6))), a0, t)
    text_c(cv, 'BONGKAR APA LAGI?', 540, 590, 64, INK, a0 * eo(prog(t, 39.3, 39.6)))
    for txt, x, y, t0, c in CMTS:
        q = prog(t, t0, t0 + 0.3)
        if q <= 0: continue
        aa = a0 * clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
        r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, aa, rad=42, lift=10)
        cv.drawCircle(r.left() + 42, 0, 24, P(col(c, aa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, aa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, aa)))
        cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, aa)))
        cv.restore()
    ca = eo(prog(t, 41.25, 41.55))
    if ca > 0: chip(cv, 'TULIS DI KOMENTAR', 540, 1340, a0 * ca, size=30, bg=ORANGE)

# ------------------------------------------------------------ J: outro (42.47 - 47.67)
def gJ(cv, t):
    tt = t - 42.47; a = eo(prog(tt, 0.0, 0.4)); p_ = bo(prog(tt, 0.0, 0.6))
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

def _shift(fn): return lambda cv, t: fn(cv, t - SH)
bb.DRAWERS = [gA] + [_shift(g) for g in (gB, gC, gD, gE, gF, gG, gJ)]

def build_sfx():
    hook = [(0.0, 'whoosh'), (0.15, 'pop'), (0.2, 'buzzer'), (0.55, 'zap2'), (0.6, 'buzzer'), (0.75, 'crack'), (0.8, 'rumble'), (1.4, 'splash'), (1.45, 'rumble'),
            (1.95, 'rewind'), (2.65, 'zap'), (2.7, 'shine'), (3.0, 'stamp'), (3.05, 'ding'), (3.7, 'swish'), (3.75, 'pop'), (5.25, 'pop'), (5.4, 'pop'), (5.55, 'pop')]
    rest = [(8.69, 'whoosh'), (9.0, 'grind'), (9.59, 'pop'), (10.0, 'tick'), (11.18, 'zap2'), (11.3, 'pop'), (12.69, 'rise'), (13.0, 'ding_soft'), (13.3, 'pop'),
          (15.88, 'whoosh'), (16.61, 'clunk'), (16.7, 'pop'), (17.4, 'pop'), (18.0, 'swish'), (19.33, 'clunk'), (19.4, 'pop'), (19.5, 'ding_soft'),
          (21.45, 'whoosh'), (22.26, 'zap'), (22.3, 'pop'), (22.9, 'buzzer'), (24.2, 'swish'), (24.6, 'card'), (25.21, 'ding'), (25.3, 'stamp'),
          (27.01, 'whoosh'), (27.05, 'card'), (28.3, 'pop'), (29.5, 'tick'), (30.83, 'pop'), (30.9, 'ding_soft'),
          (33.16, 'whoosh'), (33.4, 'card'), (34.33, 'rise'), (34.6, 'pop'), (35.6, 'ding'), (36.2, 'zoom'), (37.51, 'rise'), (37.9, 'pop'), (38.4, 'ding'),
          (39.19, 'whoosh'), (39.3, 'shine'), (39.6, 'pop'), (39.85, 'pop'), (40.1, 'pop'), (40.35, 'pop'), (41.25, 'pop'),
          (42.47, 'whoosh'), (42.62, 'boing'), (42.97, 'shine'), (43.22, 'pop')]
    ev = hook + [(round(t_ + SH, 3), k) for t_, k in rest]
    return sorted(ev)

if __name__ == '__main__': bb.main()
