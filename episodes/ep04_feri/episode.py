#!/usr/bin/env python3
"""Bongkar Benda #04: 'Kapal feri, kok nggak tenggelam?'
Diorama laut isometrik yang dibelah dengan kapal feri ro-ro (lambung bisa utuh atau dibelah: ruang udara, sekat kedap air, ruang mesin, dek kendaraan).
Hook: kalau bajanya dipadatkan, balok baja tenggelam ke dasar laut -> REWIND -> kapal dibelah, rongga udara menyala. Alasan 1: lambung berongga, rata-rata
lebih ringan dari air (timbangan). Alasan 2: kapal menyingkirkan air, air mendorong balik ke atas sama kuat dengan berat kapal (Archimedes).
Alasan 3: sekat kedap air, satu ruang bocor kapal tetap mengapung. Sejarah: Samuel Plimsoll, garis muat wajib 1876. Penutup: Merak-Bakauheni, puluhan feri.
Sumber: content/EP04_feri.md. python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, YELLOW, RED, WHITE, text_c, mono, card, chip, label, check, logo_mark)
from iso import Iso, tone, quad, box, shadow, poly, ring_pts

bb.DUR = 47.447
bb.TITLE = ('Kapal feri,', 'kok nggak tenggelam?'); bb.TITLE_OUT = 4.6
bb.GROUPS = [(0.0, 6.72, 'A'), (6.72, 14.158, 'B'), (14.158, 21.131, 'C'), (21.131, 26.98, 'D'), (26.98, 34.068, 'E'),
             (34.068, 38.692, 'F'), (38.692, 42.247, 'G'), (42.247, 47.447, 'J')]
bb.PHRASES = [(0.15, 'Kapal ini dari [baja],'), (2.01, 'beratnya [ribuan ton].'), (3.7, 'Kok bisa [ngapung]?'), (4.76, 'Ini [alasannya].'),
              (6.72, '[Pertama],'), (7.59, 'lambungnya [berongga],'), (8.88, 'isinya [udara].'), (10.05, 'Jadi kalau dirata-rata,'), (11.4, 'kapal ini [lebih ringan] dari air.'),
              (14.158, '[Kedua],'), (15.2, 'kapal [menyingkirkan] banyak air.'), (17.31, 'Air itu [mendorong balik] ke atas,'), (19.4, 'sama kuat dengan [berat kapal].'),
              (21.131, '[Ketiga],'), (21.95, 'lambungnya dibagi [sekat kedap air].'), (24.6, 'Kalau satu ruang [bocor],'), (25.34, 'kapal [tetap mengapung].'),
              (26.98, 'Sejak tahun [1876],'), (29.01, 'berkat [Samuel Plimsoll],'), (30.51, 'kapal wajib punya [garis muat]:'), (32.2, 'batas [aman] muatan.'),
              (34.068, 'Di [Merak] sampai [Bakauheni],'), (35.7, '[puluhan kapal feri] bolak-balik siang dan malam.'),
              (38.692, 'Benda apa yang mau kamu [bongkar] berikutnya?'), (40.92, 'Tulis di [komentar]!'),
              (42.247, 'Follow [Bongkar Benda],'), (43.58, 'biar makin paham [cara kerja benda] di sekitarmu.')]

WORLD = Iso(0, 0, 50)
NAVY, NAVY2 = '#2A3F6B', '#1A2A4C'
SEA_Z, BED_Z, SOIL_Z = 0.0, -6.0, -10.5
SOIL = [(BED_Z, BED_Z - 0.6, '#E6CFA8'), (BED_Z - 0.6, BED_Z - 2.2, '#D9B88C'), (BED_Z - 2.2, BED_Z - 3.6, '#C99E73'), (BED_Z - 3.6, -40, '#B88B63')]
WALL, WALL_D = '#ECE5DA', '#CFC5B6'
AIR = '#FFE3C2'

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

# ------------------------------------------------------------ laut diorama
def strata_face(cv, plane, pv, u0, u1, a, dk=0.0):
    face = poly([fpt(plane, pv, u0, BED_Z), fpt(plane, pv, u1, BED_Z), fpt(plane, pv, u1, SOIL_Z), fpt(plane, pv, u0, SOIL_Z)])
    cv.save(); cv.clipPath(face, doAntiAlias=True); n = 30
    for k, (z0, z1, c) in enumerate(SOIL):
        us = [lerp(u0, u1, i / n) for i in range(n + 1)]
        top = [fpt(plane, pv, u, z0 + (wav(u, k) if k else 0)) for u in us]; bot = [fpt(plane, pv, u, z1 + wav(u, k + 1)) for u in us[::-1]]
        cv.drawPath(poly(top + bot), P(shader=lg(*fpt(plane, pv, u0, z0), *fpt(plane, pv, u0, max(z1, SOIL_Z)), [col(tone(c, dk + 0.05), a), col(tone(c, dk - 0.06), a)])))
        if k: cv.drawPath(poly(top, False), P(col(tone(c, -0.35), 0.35 * a), stroke=1.4))
    cv.restore(); cv.drawPath(face, P(col('#8C6A4A', 0.5 * a), stroke=1.5))
def water_face(cv, plane, pv, u0, u1, a, dk=0.0, hole=None, level=SEA_Z):
    q = poly([fpt(plane, pv, u0, level), fpt(plane, pv, u1, level), fpt(plane, pv, u1, BED_Z), fpt(plane, pv, u0, BED_Z)])
    if hole is not None: q = skia.Op(q, hole, skia.PathOp.kDifference_PathOp)
    cv.drawPath(q, P(shader=lg(*fpt(plane, pv, u0, level), *fpt(plane, pv, u0, BED_Z), [col(tone('#5B76A6', dk), 0.78 * a), col(tone('#22345C', dk), 0.9 * a)])))
    ln = poly([fpt(plane, pv, lerp(u0, u1, i / 40), level) for i in range(41)], False)
    cv.save()
    if hole is not None: cv.clipPath(hole, skia.ClipOp.kDifference, True)
    cv.drawPath(ln, P(col(WHITE, 0.6 * a), stroke=2.5)); cv.restore()
def sea_top(cv, t, x0, x1, y0, y1, a, alpha=1.0):
    quad(cv, WORLD, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], '#4A6496', a * alpha, grad=((x0, y1, 0), (x1, y0, 0), '#6681B0', '#3A5487'))
    rnd = random.Random(5)
    for k in range(int((x1 - x0) * (y1 - y0) / 10)):
        x = x0 + (rnd.uniform(0, 1) * (x1 - x0) + t * 0.35) % (x1 - x0); y = rnd.uniform(y0 + 0.4, y1 - 0.4); L = rnd.uniform(0.4, 1.0)
        if x + L > x1: continue
        p0, p1 = P3(x, y, 0.01), P3(x + L, y, 0.01); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, a * 0.45 * (0.5 + 0.5 * math.sin(t * 2.2 + k))), stroke=2))
def sea_bed(cv, x0, x1, y0, y1, a):
    strata_face(cv, 'y', y1, x0, x1, a); strata_face(cv, 'x', x1, y0, y1, a, dk=-0.1)
    quad(cv, WORLD, [(x0, y0, BED_Z), (x1, y0, BED_Z), (x1, y1, BED_Z), (x0, y1, BED_Z)], '#E6CFA8', 0.0)

# ------------------------------------------------------------ kapal feri: profil samping + lebar badan
XS, XB_ = -10.0, 10.6
def zbot(x):
    if x < -9.6: return lerp(-1.5, -2.2, (x + 10) / 0.4)
    if x > 7.4: return -2.2 + ((x - 7.4) / 3.2) ** 2 * 3.6
    return -2.2
def zdeck(x): return 1.4 + (0.3 * ((x - 6.0) / 4.6) ** 2 if x > 6.0 else 0.0)
def wb(x):
    if x > 5.0: return 2.2 * (1 - 0.85 * ((x - 5.0) / 5.6) ** 2)
    if x < -9.0: return 2.1
    return 2.2
STA = [lerp(XS, XB_, i / 44) for i in range(45)]
BULK = [-6.5, -2.6, 1.4, 5.3]                                    # sekat kedap air (x)
CDECK = 0.3                                                       # dek kendaraan
TANK = -1.7                                                       # atas tangki dasar ganda
COMP = [(-10.0, -6.5, 'mesin'), (-6.5, -2.6, 'udara'), (-2.6, 1.4, 'udara'), (1.4, 5.3, 'udara'), (5.3, 9.6, 'udara')]

class Pose:
    def __init__(self, dz=0.0, trim=0.0): self.dz, self.trim = dz, trim
    def z(self, x, z): return z + self.dz + self.trim * x
def sp(pose, x, y, z): return P3(x, y, pose.z(x, z))
def profile_path(pose, y=0.0, zcap=None):
    pts = [sp(pose, x, y, zbot(x)) for x in STA] + [sp(pose, x, y, zdeck(x)) for x in STA[::-1]]
    return poly(pts)
def hull_whole(cv, pose, a, part):
    """sisi dekat lambung utuh (y = +wb). part='bawah' (di bawah garis air) atau 'atas'"""
    for xa, xb in zip(STA[:-1], STA[1:]):
        rows = []
        for x in (xa, xb):
            zb_, zt = pose.z(x, zbot(x)), pose.z(x, zdeck(x)); w = wb(x)
            zw = clamp(0.0, zb_, zt)
            rows.append((x, w, zb_, zw, zt))
        (x0, w0, b0, m0, t0), (x1, w1, b1, m1, t1) = rows
        k = 0.06 * (1 if xa > 5 else 0)
        if part == 'bawah' and (m0 > b0 or m1 > b1):
            cv.drawPath(poly([P3(x0, w0 * 0.9, b0), P3(x1, w1 * 0.9, b1), P3(x1, w1, m1), P3(x0, w0, m0)]), P(col(tone(NAVY2, k), a)))
        if part == 'atas' and (t0 > m0 or t1 > m1):
            cv.drawPath(poly([P3(x0, w0, m0), P3(x1, w1, m1), P3(x1, w1, t1), P3(x0, w0, t0)]), P(col(tone(NAVY, k - 0.02), a)))
            s0, s1 = pose.z(x0, 0.75), pose.z(x1, 0.75)
            if t0 > s0 + 0.2:
                cv.drawPath(poly([P3(x0, w0, max(m0, s0)), P3(x1, w1, max(m1, s1)), P3(x1, w1, max(m1, s1 + 0.2)), P3(x0, w0, max(m0, s0 + 0.2))]), P(col(ORANGE, a)))
    if part == 'atas':
        top = [sp(pose, x, wb(x), zdeck(x)) for x in STA] + [sp(pose, x, -wb(x), zdeck(x)) for x in STA[::-1]]
        cv.drawPath(poly(top), P(col('#D9D3C9', a))); cv.drawPath(poly(top), P(col(tone('#D9D3C9', -0.3), a), stroke=1.5))
def superstructure(cv, pose, a, cut=False, t=0.0, lights=0.0):
    y0 = -1.9; y1 = 0.0 if cut else 1.9
    def bx(x, y, z, w, d, h, c, top=0.2):
        if cut:
            d = min(d, -y)
            if d <= 0: return
        box(cv, WORLD, x, y, pose.z(x + w / 2, z), w, d, h, c, a, top=top, left=0.02, right=-0.12)
    bx(-7.0, y0, 1.4, 12.5, y1 - y0, 1.5, '#F4F0EA'); bx(-5.2, y0 + 0.2, 2.9, 9.0, y1 - y0 - (0 if cut else 0.4), 1.3, '#F4F0EA')
    bx(1.6, y0 + 0.3, 4.2, 2.6, y1 - y0 - (0 if cut else 0.6), 0.9, '#F4F0EA')
    win = '#FFC98A' if lights > 0.5 else NAVY
    if not cut:                                                           # jendela di sisi dekat
        for zr, xa, xb_ in ((1.85, -6.6, 5.2), (3.3, -4.8, 3.5)):
            x = xa
            while x < xb_:
                quad(cv, WORLD, [(x, 1.9 if zr < 3 else 1.7, pose.z(x, zr)), (x + 0.45, 1.9 if zr < 3 else 1.7, pose.z(x, zr)), (x + 0.45, 1.9 if zr < 3 else 1.7, pose.z(x, zr + 0.5)), (x, 1.9 if zr < 3 else 1.7, pose.z(x, zr + 0.5))], win, a)
                x += 0.75
        quad(cv, WORLD, [(4.2, 1.6, pose.z(4.2, 4.5)), (4.2, -1.6, pose.z(4.2, 4.5)), (4.2, -1.6, pose.z(4.2, 4.9)), (4.2, 1.6, pose.z(4.2, 4.9))], NAVY, a)
        for x in (-3.8, -0.6, 2.6):                                       # sekoci oranye
            box(cv, WORLD, x, 1.75, pose.z(x, 3.05), 1.1, 0.35, 0.35, ORANGE, a, top=0.25)
    fx = -4.6; bx(fx, -0.6, 4.2, 1.2, 1.2, 2.0, ORANGE, top=0.25); bx(fx, -0.6, 6.2, 1.2, 1.2, 0.35, NAVY2)
def vehicles(cv, pose, a, cut=False):
    items = [(-5.8, -0.42, 2.4, '#F4F0EA', 'truk'), (-2.9, -0.42, 1.2, ORANGE, 'mobil'), (-1.3, -0.42, 1.2, NAVY, 'mobil'), (0.4, -0.42, 2.4, '#F4F0EA', 'truk'), (3.3, -0.42, 1.2, '#F7F4EF', 'mobil')]
    if not cut: return
    for x, y, L, c, kind in items:
        z = pose.z(x + L / 2, CDECK)
        if kind == 'truk':
            box(cv, WORLD, x, y - 0.3, z, L * 0.72, 0.6, 0.72, c, a, top=0.15); box(cv, WORLD, x + L * 0.75, y - 0.28, z, L * 0.25, 0.56, 0.52, ORANGE, a, top=0.2)
        else:
            box(cv, WORLD, x, y - 0.26, z, L, 0.52, 0.26, c, a, top=0.22); box(cv, WORLD, x + 0.25, y - 0.22, z + 0.26, L * 0.5, 0.44, 0.2, '#5A6B8C' if c == NAVY else NAVY, a, top=0.3)
def hull_cut(cv, t, pose, a, air_glow=0.0, bulk_glow=0.0, flood=None):
    """separuh belakang lambung (y<=0) dengan isi: dinding dalam, lantai, sekat, ruang mesin, dek kendaraan"""
    def wallq(x0, x1, z0f, z1f, c):                                       # dinding dalam sisi jauh (y = -wb), menghadap +y
        for xa, xb in zip(STA[:-1], STA[1:]):
            if xb <= x0 or xa >= x1: continue
            xa_, xb_ = max(xa, x0), min(xb, x1)
            cv.drawPath(poly([sp(pose, xa_, -wb(xa_), z0f(xa_)), sp(pose, xb_, -wb(xb_), z0f(xb_)), sp(pose, xb_, -wb(xb_), z1f(xb_)), sp(pose, xa_, -wb(xa_), z1f(xa_))]), P(col(c, a)))
    for i, (x0, x1, kind) in enumerate(COMP):
        wallq(x0, x1, zbot, lambda x: CDECK, tone(WALL, -0.12) if kind == 'udara' else '#B9C0CC')
        for zf, c in ((TANK, '#D6CDBF'), ):                               # lantai tangki
            xa_, xb_ = max(x0, -9.6), min(x1, 7.4)
            if xb_ > xa_: quad(cv, WORLD, [(xa_, -wb(xa_), pose.z(xa_, zf)), (xb_, -wb(xb_), pose.z(xb_, zf)), (xb_, 0, pose.z(xb_, zf)), (xa_, 0, pose.z(xa_, zf))], c, a)
        if kind == 'mesin':
            box(cv, WORLD, -9.0, -1.5, pose.z(-8.2, TANK), 1.8, 1.1, 1.1, NAVY, a, top=0.3); box(cv, WORLD, -8.7, -1.3, pose.z(-8.2, TANK + 1.1), 1.2, 0.7, 0.45, '#5A6B8C', a)
        if flood and flood[0] == i and flood[1] > 0:                      # ruang yang bocor terisi air
            zl = lerp(zbot(x0 + 0.5), CDECK - 0.1, flood[1])
            xa_, xb_ = x0, x1
            q = poly([sp(pose, xa_, 0, max(zbot(xa_), TANK)), sp(pose, xb_, 0, max(zbot(xb_), TANK)), sp(pose, xb_, 0, zl), sp(pose, xa_, 0, zl)])
            cv.drawPath(q, P(shader=lg(*sp(pose, xa_, 0, zl), *sp(pose, xa_, 0, TANK), [col('#5B76A6', 0.85 * a), col('#22345C', 0.95 * a)])))
            ln = poly([sp(pose, xa_, 0, zl), sp(pose, xa_, -wb(xa_), zl), sp(pose, xb_, -wb(xb_), zl), sp(pose, xb_, 0, zl)])
            cv.drawPath(ln, P(col('#6681B0', 0.8 * a)))
        if i + 1 < len(COMP):                                             # sekat di ujung depan ruang ini
            xb = x1
            q = poly([sp(pose, xb, -wb(xb), zbot(xb)), sp(pose, xb, 0, zbot(xb)), sp(pose, xb, 0, CDECK), sp(pose, xb, -wb(xb), CDECK)])
            cv.drawPath(q, P(col(tone(WALL_D, -0.05), a)))
            if bulk_glow > 0: cv.drawPath(q, P(col(ORANGE, 0.55 * bulk_glow * a)))
    quad(cv, WORLD, [(XS, -wb(XS), pose.z(XS, CDECK)), (9.6, -wb(9.6), pose.z(9.6, CDECK)), (9.6, 0, pose.z(9.6, CDECK)), (XS, 0, pose.z(XS, CDECK))], '#C9CED8', a)
    wallq(XS, 9.6, lambda x: CDECK, lambda x: 1.4, tone(WALL, -0.05))
    vehicles(cv, pose, a, cut=True)
    if air_glow > 0:                                                      # rongga udara menyala (bidang potong)
        for i, (x0, x1, kind) in enumerate(COMP):
            if kind != 'udara' or (flood and flood[0] == i and flood[1] > 0.05): continue
            ph = 0.75 + 0.25 * math.sin(t * 4 + i)
            q = poly([sp(pose, x, 0, max(zbot(x), TANK)) for x in STA if x0 <= x <= x1] + [sp(pose, x1, 0, CDECK - 0.05), sp(pose, x0, 0, CDECK - 0.05)])
            cv.drawPath(q, P(col(AIR, 0.75 * air_glow * a))); cv.drawPath(q, P(col(ORANGE, 0.35 * air_glow * ph * a), blur=12))
    sec = []                                                              # potongan pelat baja di bidang y=0
    for x in STA: sec.append(sp(pose, x, 0, zbot(x)))
    cv.drawPath(poly(sec, False), P(col(NAVY2, a), stroke=9))
    for zz in (TANK, CDECK, 1.4):
        xa_, xb_ = (-9.6, 7.4) if zz == TANK else (XS, 9.6 if zz == CDECK else XB_)
        p0, p1 = sp(pose, xa_, 0, zz), sp(pose, xb_, 0, zz); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=6))
    for xb in BULK:
        p0, p1 = sp(pose, xb, 0, zbot(xb)), sp(pose, xb, 0, CDECK)
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(ORANGE if bulk_glow > 0.3 else NAVY2, a), stroke=7 + 4 * bulk_glow))
    p0, p1 = sp(pose, XS, 0, zbot(XS)), sp(pose, XS, 0, 1.4); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=8))
def ship(cv, t, pose, a, cut=0.0, air_glow=0.0, bulk_glow=0.0, flood=None, under=None, lights=0.0, sea=None):
    """cut: 0 = utuh, 1 = dibelah. under(): gambar permukaan laut di antara bagian bawah & atas"""
    if cut > 0:
        if under: under()
        hull_cut(cv, t, pose, a, air_glow, bulk_glow, flood)
        superstructure(cv, pose, a, cut=True, t=t, lights=lights)
    if cut < 1:
        aw = a * (1 - cut)
        hull_whole(cv, pose, aw, 'bawah')
        if under and cut <= 0: under()
        hull_whole(cv, pose, aw, 'atas')
        superstructure(cv, pose, aw, cut=False, t=t, lights=lights)
    for k in range(3):                                                    # buih haluan
        ph = (t * 1.3 + k / 3) % 1.0; p0 = sp(pose, XB_ - 0.2 - ph * 2.2, wb(XB_ - 1) + 0.3 + ph * 0.8, 0.02)
        cv.drawLine(p0[0], p0[1], p0[0] - 30, p0[1] - 8, P(col(WHITE, 0.7 * (1 - ph) * a), stroke=3))

def bubbles(cv, x, y, z0, z1, t, a, n=10, seed=3):
    rnd = random.Random(seed)
    for k in range(n):
        ph = (t * rnd.uniform(0.5, 0.9) + rnd.random()) % 1.0; xx = x + rnd.uniform(-1.2, 1.2) + 0.2 * math.sin(t * 5 + k); zz = lerp(z0, z1, ph)
        p = P3(xx, y + rnd.uniform(-0.5, 0.5), zz); r = rnd.uniform(4, 9)
        cv.drawCircle(p[0], p[1], r, P(col(WHITE, 0.8 * a * (1 - ph)), stroke=2))

SEA_A = (-17.0, 17.0, -9.0, 4.6)                                         # laut utuh (muka depan di y=4.6)
SEA_C = (-17.0, 17.0, -9.0, 0.0)                                         # laut dibelah di y=0
def world(cv, t, a, pose, cut, sea, **kw):
    x0, x1, y0, y1 = sea
    sea_bed(cv, x0, x1, y0, y1, a)
    under = lambda: sea_top(cv, t, x0, x1, y0, y1, a, alpha=0.82)
    ship(cv, t, pose, a, cut=cut, under=under, **kw)
    hole = profile_path(pose, 0.0) if y1 <= 0.01 else None
    water_face(cv, 'y', y1, x0, x1, a, hole=hole); water_face(cv, 'x', x1, y0, y1, a, dk=-0.1)

# ------------------------------------------------------------ A: HOOK — kalau bajanya padat: tenggelam; REWIND; kapal dibelah, rongga udara menyala (0 - 6.72)
T_M0, T_M1, T_SINK, T_BED, T_RW, T_BACK, T_CUT = 0.35, 0.85, 0.9, 1.85, 2.05, 2.95, 3.3
def steel_block(cv, m, zc, a):
    """balok baja padat: ukuran dari badan kapal mengecil jadi kubus (m: 0..1)"""
    sx_, sy_, sz_ = lerp(20.6, 2.6, m), lerp(2.2, 2.6, m), lerp(3.6, 2.6, m)
    x = lerp(XS, -1.3, m); y = lerp(-2.2, -1.3, m)
    box(cv, WORLD, x, y, zc - sz_ / 2, sx_, sy_, sz_, '#7D879A', a, top=0.35, left=0.05, right=-0.2)
    p0, p1 = P3(x, y + sy_, zc + sz_ / 2), P3(x + sx_, y + sy_, zc + sz_ / 2)
    cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, 0.6 * a), stroke=2))
def block_z(t):
    if t < T_SINK: return -0.4
    if t < T_BED: return lerp(-0.4, BED_Z + 1.3, ei(prog(t, T_SINK, T_BED)))
    if t < T_RW: return BED_Z + 1.3
    return lerp(BED_Z + 1.3, -0.4, eio(prog(t, T_RW, T_RW + 0.6)))
def morph(t):
    if t < T_RW: return eio(prog(t, T_M0, T_M1))
    return 1 - eio(prog(t, T_RW + 0.55, T_BACK))
def gA(cv, t):
    u = eio(prog(t, 0.0, 1.6)); u2 = eio(prog(t, T_RW, T_BACK + 0.4))
    zoom = lerp(1.15, 0.86, u) if t < T_RW else lerp(0.86, 1.06, u2)
    fz = lerp(0.6, -2.0, u) if t < T_RW else lerp(-2.0, -0.3, u2)
    fw = (0.5, -1.0, fz); f = P3(*fw); bob = 0.06 * math.sin(t * 2.0)
    hit = prog(t, T_BED, T_BED + 0.45); shk = 10 * math.sin(t * 60) * (1 - hit) if T_BED < t < T_BED + 0.45 else 0.0
    sx, sy = 540 + shk, 1000
    m = morph(t); cut = eio(prog(t, T_CUT, T_CUT + 0.5)); air = eo(prog(t, 3.7, 4.0)) * (1 - 0.4 * prog(t, 5.6, 6.5))
    sea = SEA_A if cut < 0.5 else SEA_C
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    x0, x1, y0, y1 = sea
    sea_bed(cv, x0, x1, y0, y1, 1.0)
    pose = Pose(dz=bob)
    if m < 1:
        under = lambda: sea_top(cv, t, x0, x1, y0, y1, 1.0, alpha=0.82)
        ship(cv, t, pose, 1.0 - m, cut=cut, air_glow=air, under=under)
    else: sea_top(cv, t, x0, x1, y0, y1, 1.0, alpha=0.82)
    if m > 0: steel_block(cv, m, block_z(t), clamp(m * 2))
    if T_SINK < t < T_BED + 0.8: bubbles(cv, 0.0, -1.3, block_z(t), -0.2, t, prog(t, T_SINK, T_SINK + 0.2) * (1 - prog(t, T_BED + 0.3, T_BED + 0.8)), n=12)
    if T_BED < t < T_BED + 0.7:                                           # debu pasir di dasar laut
        q = prog(t, T_BED, T_BED + 0.7); rnd = random.Random(4)
        for k in range(12):
            ang = rnd.uniform(math.pi, math.tau); L = 40 + 80 * eo(q); c0 = P3(rnd.uniform(-1.5, 1.5), -1.3, BED_Z)
            cv.drawLine(c0[0], c0[1], c0[0] + math.cos(ang) * L, c0[1] + math.sin(ang) * L * 0.5, P(col('#E6CFA8', 0.8 * (1 - q)), stroke=5))
    if T_SINK - 0.05 < t < T_SINK + 0.6:                                  # cipratan saat balok masuk air
        q = prog(t, T_SINK - 0.05, T_SINK + 0.6); rnd = random.Random(8)
        for k in range(20):
            ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05); L = rnd.uniform(60, 170) * eo(q); c0 = P3(rnd.uniform(-1.2, 1.2), rnd.uniform(-1.5, 0), 0)
            cv.drawLine(c0[0] + math.cos(ang) * L * 0.35, c0[1] + math.sin(ang) * L * 0.4, c0[0] + math.cos(ang) * L, c0[1] + math.sin(ang) * L * 1.3 + 150 * q * q, P(col(WHITE, 0.9 * (1 - q)), stroke=6))
    hole = profile_path(pose, 0.0) if y1 <= 0.01 and m < 0.5 else None
    water_face(cv, 'y', y1, x0, x1, 1.0, hole=hole); water_face(cv, 'x', x1, y0, y1, 1.0, dk=-0.1)
    cv.restore()
    ta = 1 - eio(prog(t, bb.TITLE_OUT - 0.4, bb.TITLE_OUT))
    if ta > 0: cv.drawRect(skia.Rect(0, 0, 1080, 560), P(shader=lg(0, 380, 0, 600, [col(bb.BG0, ta), col(bb.BG0, 0)])))
    fl = bump(prog(t, T_BED, T_BED + 0.3))
    if fl > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.2 * fl)))
    if T_M0 < t < T_RW + 0.1: chip(cv, 'KALAU BAJANYA PADAT?', 540, 560, eo(prog(t, T_M0, T_M0 + 0.15)) * (1 - prog(t, T_RW - 0.1, T_RW + 0.1)), size=30, bg=RED)
    if T_BED < t < T_RW + 0.1:
        p = scr(P3(-0.5, 1.3, BED_Z + 2.8), f, zoom, sx, sy); text_c(cv, 'TENGGELAM!', p[0], p[1], 40, RED, eo(prog(t, T_BED, T_BED + 0.15)) * (1 - prog(t, T_RW - 0.05, T_RW + 0.1)), halo=1.0)
    rw = prog(t, T_RW, T_BACK + 0.1)
    if 0 < rw < 1:                                                        # REWIND
        ra = clamp(bump(rw) * 1.3)
        cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(bb.BG0, 0.14 * ra)))
        for k in range(14):
            yy = (k * 151 + t * 2400) % 1920; cv.drawRect(skia.Rect(0, yy, 1080, yy + 5), P(col(WHITE, 0.35 * ra)))
        r = skia.Rect(400, 520, 680, 600); cv.drawRoundRect(r, 40, 40, P(col(INK, ra)))
        for k in range(2):
            x0_ = 470 + k * 44; tri = skia.Path(); tri.moveTo(x0_, 560); tri.lineTo(x0_ + 38, 536); tri.lineTo(x0_ + 38, 584); tri.close(); cv.drawPath(tri, P(col(WHITE, ra)))
        f_ = font(MONO, 26); cv.drawString('ULANG', 570, bl(f_, 560), f_, P(col(WHITE, ra)))
    if t > 3.7:
        p = scr(P3(-0.6, 0, -0.9), f, zoom, sx, sy); la = eo(prog(t, 3.75, 4.1)) * (1 - prog(t, 6.4, 6.72))
        label(cv, 'RONGGA UDARA', p[0], p[1], 300, 640, la, sub='lambungnya kosong')
        check(cv, 470, 575, 24, prog(t, 3.85, 4.25), la)
    for k, (num, txt) in enumerate((('1', 'RONGGA UDARA'), ('2', 'GAYA APUNG'), ('3', 'SEKAT'))):
        q = prog(t, 4.85 + 0.15 * k, 5.15 + 0.15 * k)
        if q > 0:
            x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
            cv.save(); cv.translate(x, 1335); cv.scale(s_, s_); cv.translate(-x, -1335)
            card(cv, skia.Rect(x - 158, 1305, x + 158, 1365), aa, rad=30, lift=8)
            cv.drawCircle(x - 123, 1335, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 123, 1335, 24, WHITE, aa)
            text_c(cv, txt, x + 14, 1335, 24, INK, aa)
            cv.restore()

# ------------------------------------------------------------ B: lambung berongga berisi udara; rata-rata lebih ringan dari air (6.72 - 14.158)
def gB(cv, t):
    a0 = eo(prog(t, 6.72, 7.1))
    zoom = lerp(1.12, 1.25, eio(prog(t, 6.72, 14.158))); fw = (0.0, -1.0, -0.4); f = P3(*fw); sx, sy = 560, 980
    air = max(eo(prog(t, 7.59, 8.0)) * 0.6, eo(prog(t, 8.88, 9.2)))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    world(cv, t, a0, Pose(dz=0.05 * math.sin(t * 2.0)), 1.0, SEA_C, air_glow=air)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    for i, (x0, x1, kind) in enumerate(COMP):                             # label UDARA di tiap ruang
        if kind != 'udara': continue
        q = eo(prog(t, 8.88 + 0.12 * i, 9.2 + 0.12 * i)) * (1 - prog(t, 13.8, 14.1))
        if q > 0: p = S(((x0 + x1) / 2, 0, -0.75)); chip(cv, 'UDARA', p[0], p[1], a0 * q, size=22, bg=ORANGE, pad=16)
    la = eo(prog(t, 7.59, 7.95)) * (1 - prog(t, 9.8, 10.1))
    if la > 0: p = S((-4.6, 0, zbot(-4.6) + 0.05)); label(cv, 'LAMBUNG BAJA', p[0], p[1], 280, 1180, a0 * la, dot=NAVY, sub='tipis, isinya kosong')
    ba = eo(prog(t, 10.05, 10.4))
    if ba > 0:                                                            # timbangan: kapal (rata-rata) vs air sebesar kapal
        cx, cy = 540, 400; tilt = lerp(0, -11, eo(prog(t, 10.5, 11.3))) + 1.5 * math.sin(t * 3) * (1 - prog(t, 11.3, 11.9))
        card(cv, skia.Rect(cx - 330, cy - 160, cx + 330, cy + 150), a0 * ba, rad=32)
        mono(cv, 'DI RATA-RATA', cx, cy - 122, 22, MUTED, a0 * ba, sp=4)
        cv.save(); cv.translate(cx, cy + 10); cv.rotate(tilt)
        cv.drawLine(-230, 0, 230, 0, P(col(INK, a0 * ba), stroke=8))
        for sx_, lab, c in ((-230, 'KAPAL', NAVY), (230, 'AIR', '#4A6496')):
            cv.save(); cv.translate(sx_, 0); cv.rotate(-tilt)
            cv.drawLine(0, 0, 0, 30, P(col(INK, a0 * ba), stroke=3)); cv.drawRoundRect(skia.Rect(-80, 30, 80, 46), 8, 8, P(col(INK, a0 * ba)))
            r = skia.Rect(-62, -38, 62, 26)
            if lab == 'KAPAL':
                hull = skia.Path(); hull.moveTo(-60, -10); hull.lineTo(60, -10); hull.lineTo(46, 26); hull.lineTo(-48, 26); hull.close()
                cv.drawPath(hull, P(col(NAVY, a0 * ba))); cv.drawRect(skia.Rect(-34, -34, 30, -10), P(col('#F4F0EA', a0 * ba))); cv.drawRect(skia.Rect(-26, -40, -14, -24), P(col(ORANGE, a0 * ba)))
            else:
                cv.drawRoundRect(r, 10, 10, P(shader=lg(0, -38, 0, 26, [col('#6681B0', a0 * ba), col('#2A3F6B', a0 * ba)])))
            text_c(cv, lab, 0, 84, 24, c, a0 * ba)
            cv.restore()
        cv.restore()
        tri = skia.Path(); tri.moveTo(cx, cy + 10); tri.lineTo(cx - 24, cy + 70); tri.lineTo(cx + 24, cy + 70); tri.close(); cv.drawPath(tri, P(col(INK, a0 * ba)))
    ca = eo(prog(t, 11.4, 11.7))
    if ca > 0: chip(cv, 'KAPAL LEBIH RINGAN', 540, 1340, a0 * ca, size=30, bg=ORANGE); check(cv, 775, 1340, 22, prog(t, 11.5, 11.9), a0 * ca)

# ------------------------------------------------------------ C: kapal menyingkirkan air; air mendorong ke atas sama kuat dengan berat kapal (14.158 - 21.131)
def gC(cv, t):
    a0 = eo(prog(t, 14.158, 14.55))
    zoom = lerp(0.98, 1.06, eio(prog(t, 14.158, 21.131))); fw = (0.0, -1.0, -0.2); f = P3(*fw); sx, sy = 540, 960
    low = eio(prog(t, 15.2, 16.9)); dz = lerp(2.6, 0.0, low) + 0.04 * math.sin(t * 2) * low
    lvl = 0.0
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    world(cv, t, a0, Pose(dz=dz), 1.0, SEA_C, air_glow=0.35)
    ga = eo(prog(t, 15.4, 15.8)) * (1 - prog(t, 18.8, 19.3))             # air yang tersingkir: bayangan setinggi bagian lambung yang tercelup
    if ga > 0:
        hgt = 2.2 * low
        box(cv, WORLD, -4.0, 3.2, 0.4, 6.0, 1.8, hgt, '#6681B0', 0.7 * ga * a0, top=0.2)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    if ga > 0.05:
        p = S((-1.0, 5.0, 0.2)); text_c(cv, 'AIR YANG TERSINGKIR', p[0], p[1] + 40, 26, NAVY, a0 * ga, halo=1.0)
    ua = eo(prog(t, 17.31, 17.7))
    if ua > 0:                                                            # dorongan air ke atas di dasar lambung
        for k, x in enumerate((-7.5, -4.5, -1.5, 1.5, 4.5)):
            q = (t * 0.9 + k * 0.17) % 1.0; zb_ = zbot(x) + dz
            arrow(cv, S((x, -0.2, zb_ - 1.5 + 0.4 * q)), S((x, -0.2, zb_ - 0.15 + 0.4 * q)), ORANGE, a0 * ua * (0.7 + 0.3 * bump(q)), w=9, head=22)
        chip(cv, 'DORONGAN AIR', 300, 1240, a0 * ua * (1 - prog(t, 19.2, 19.5)), size=26, bg=ORANGE)
    wa = eo(prog(t, 19.4, 19.75))
    if wa > 0:                                                            # berat (turun) = dorongan (naik)
        c0 = S((0.0, 0, 3.6 + dz)); c1 = S((0.0, 0, 0.9 + dz)); u0 = S((0.0, 0, -5.3 + dz)); u1 = S((0.0, 0, -2.5 + dz))
        arrow(cv, c0, c1, NAVY, a0 * wa, w=14, head=30); arrow(cv, u0, u1, ORANGE, a0 * wa, w=14, head=30)
        text_c(cv, 'BERAT KAPAL', c0[0] + 150, c0[1] + 30, 28, NAVY, a0 * wa, halo=1.0)
        text_c(cv, 'DORONGAN AIR', u0[0] + 160, u0[1] - 20, 28, ORANGE_D, a0 * wa, halo=1.0)
        chip(cv, 'SAMA KUAT', 540, 1340, a0 * eo(prog(t, 19.6, 19.9)), size=30, bg=INK); check(cv, 700, 1340, 22, prog(t, 19.7, 20.1), a0 * wa)
    la = eo(prog(t, 15.2, 15.55)) * (1 - prog(t, 17.0, 17.3))
    if la > 0: chip(cv, 'HUKUM ARCHIMEDES', 540, 330, a0 * la, size=28, bg=NAVY)

# ------------------------------------------------------------ D: sekat kedap air; satu ruang bocor, kapal tetap mengapung (21.131 - 26.98)
FLOOD_I = 3
def gD(cv, t):
    a0 = eo(prog(t, 21.131, 21.5))
    zoom = lerp(1.12, 1.2, eio(prog(t, 21.131, 26.98))); fw = (0.6, -1.0, -0.6); f = P3(*fw); sx, sy = 540, 980
    bg = eo(prog(t, 21.95, 22.3)) * (1 - 0.5 * prog(t, 24.4, 24.8)) + 0.5 * eo(prog(t, 25.34, 25.6))
    fl = eio(prog(t, 24.6, 25.5)); trim = -0.012 * fl
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    world(cv, t, a0, Pose(dz=0.04 * math.sin(t * 2) - 0.12 * fl, trim=trim), 1.0, SEA_C, air_glow=0.5 * (1 - fl * 0.2), bulk_glow=bg, flood=(FLOOD_I, fl))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 21.95, 22.3)) * (1 - prog(t, 24.3, 24.6))
    if la > 0: p = S((BULK[1], 0, -0.9)); label(cv, 'SEKAT KEDAP AIR', p[0], p[1], 300, 520, a0 * la, sub='membagi lambung jadi ruang-ruang')
    ba = prog(t, 24.6, 26.98)
    if ba > 0:                                                            # bocor di dasar satu ruang
        x0, x1, _ = COMP[FLOOD_I]; p = S(((x0 + x1) / 2, 0, zbot(3.0) + 0.1))
        for k in range(5):
            ang = -math.pi / 2 + (k - 2) * 0.3; L = 30 + 20 * math.sin(t * 20 + k)
            cv.drawLine(p[0], p[1], p[0] + math.cos(ang) * L, p[1] + math.sin(ang) * L, P(col(WHITE, 0.8 * a0 * (1 - prog(t, 25.6, 26.2))), stroke=4))
        chip(cv, 'BOCOR!', 540, 330, a0 * eo(prog(t, 24.6, 24.8)) * (1 - prog(t, 25.3, 25.5)), size=30, bg=RED)
    ca = eo(prog(t, 25.34, 25.65))
    if ca > 0:
        chip(cv, 'TETAP MENGAPUNG', 540, 1340, a0 * ca, size=30, bg=ORANGE); check(cv, 750, 1340, 22, prog(t, 25.45, 25.85), a0 * ca)
        p = S((-2.0, 0, -0.9)); text_c(cv, 'KERING', p[0], p[1], 26, ORANGE_D, a0 * ca, halo=1.0); p = S((7.0, 0, -0.6)); text_c(cv, 'KERING', p[0], p[1], 26, ORANGE_D, a0 * ca, halo=1.0)

# ------------------------------------------------------------ E: Samuel Plimsoll, garis muat wajib sejak 1876 (26.98 - 34.068)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def plimsoll_card(cv, t, a, lvl):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'INGGRIS · 1876', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    hx0, hx1, hy0, hy1 = 150, 930, 430, 1000                              # sisi lambung kapal kayu-besi (tampak samping, dekat)
    cv.drawRect(skia.Rect(hx0, hy0, hx1, hy1), P(col('#8C6A4A', a)))
    for k in range(10): cv.drawLine(hx0, hy0 + 30 + k * 58, hx1, hy0 + 30 + k * 58, ink(0.35, 2))
    for k in range(14): cv.drawCircle(hx0 + 40 + k * 60, hy0 + 18, 5, ink(0.6, 2))
    cx, cy = 600, 700                                                     # tanda Plimsoll: lingkaran + garis + tangga garis muat
    cv.drawCircle(cx, cy, 70, P(col('#F3E6CC', a), stroke=8)); cv.drawLine(cx - 110, cy, cx + 110, cy, P(col('#F3E6CC', a), stroke=8))
    f_ = font(XB, 40); cv.drawString('L', cx - 120, cy - 30, f_, P(col('#F3E6CC', a))); cv.drawString('R', cx + 92, cy - 30, f_, P(col('#F3E6CC', a)))
    cv.drawLine(cx + 190, cy - 110, cx + 190, cy + 60, P(col('#F3E6CC', a), stroke=7))
    for k, lab in enumerate(('TF', 'F', 'T', 'S', 'W')):
        yy = cy - 100 + k * 40; cv.drawLine(cx + 190, yy, cx + 270, yy, P(col('#F3E6CC', a), stroke=6))
        cv.drawString(lab, cx + 280, yy + 12, font(XB, 28), P(col('#F3E6CC', a)))
    wy = lerp(hy0 + 40, hy1, 1 - lvl)                                     # muka air
    cv.drawRect(skia.Rect(r.left(), wy, r.right(), r.bottom()), P(col('#B89A72', 0.62 * a)))
    p = skia.Path(); p.moveTo(r.left(), wy)
    for i in range(30): x = r.left() + i * 32; p.quadTo(x + 8, wy - 7 + 2 * math.sin(t * 3 + i), x + 16, wy); p.quadTo(x + 24, wy + 7, x + 32, wy)
    cv.drawPath(p, P(col(WHITE, 0.9 * a), stroke=4))
    mx, my = 790, 345                                                     # potret medali Samuel Plimsoll
    cv.drawOval(skia.Rect(mx - 78, my - 92, mx + 78, my + 92), P(col('#FBF3E2', a))); cv.drawOval(skia.Rect(mx - 78, my - 92, mx + 78, my + 92), ink(1, 5))
    cv.save(); cv.clipPath(poly([(mx + 72 * math.cos(math.tau * i / 40), my + 86 * math.sin(math.tau * i / 40)) for i in range(40)]), doAntiAlias=True)
    cv.drawRoundRect(skia.Rect(mx - 60, my + 20, mx + 60, my + 120), 30, 30, P(col('#3E2E22', a)))
    cv.drawCircle(mx, my - 18, 34, P(col('#E8C9A0', a))); cv.drawCircle(mx, my - 18, 34, ink(1, 2.5))
    beard = skia.Path(); beard.moveTo(mx - 32, my - 14); beard.quadTo(mx, my + 52, mx + 32, my - 14); beard.close(); cv.drawPath(beard, P(col('#8A8A8A', a)))
    cv.drawArc(skia.Rect(mx - 34, my - 56, mx + 34, my - 6), 180, 180, False, P(col('#6B5A4A', a)))
    cv.restore()
    cv.restore()
def gE(cv, t):
    a0 = eo(prog(t, 26.98, 27.4))
    lvl = lerp(0.62, 0.5, eo(prog(t, 30.6, 31.2)))
    over = eo(prog(t, 31.2, 31.5)) * (1 - eio(prog(t, 31.9, 32.3)))      # kelebihan muatan dulu, lalu kembali ke batas aman
    lvl = lerp(lvl, 0.78, over)
    cv.save(); cv.translate(540, 770); cv.scale(1.14, 1.14); cv.translate(-540, -700)
    plimsoll_card(cv, t, a0, lvl)
    cv.restore()
    S = lambda x, y: (540 + (x - 540) * 1.14, 770 + (y - 700) * 1.14)
    na = eo(prog(t, 29.01, 29.4))
    if na > 0: p = S(790, 437); label(cv, 'SAMUEL PLIMSOLL', p[0], p[1], 760, 600, a0 * na, size=26, sub='anggota parlemen Inggris')
    ga = eo(prog(t, 30.51, 30.9))
    if ga > 0: p = S(600, 700); label(cv, 'GARIS MUAT', p[0], p[1], 300, 1240, a0 * ga, size=26, sub='tanda di lambung kapal')
    if over > 0.05: chip(cv, 'KELEBIHAN MUATAN', 540, 1340, a0 * over, size=28, bg=RED)
    sa = eo(prog(t, 32.2, 32.5))
    if sa > 0: chip(cv, 'BATAS AMAN', 540, 1340, a0 * sa, size=30, bg=ORANGE); check(cv, 690, 1340, 22, prog(t, 32.3, 32.7), a0 * sa)

# ------------------------------------------------------------ F: Merak - Bakauheni, puluhan feri bolak-balik siang dan malam (34.068 - 38.692)
def land(cv, pts, a, h=0.8):
    top = [P3(x, y, h) for x, y in pts]; cv.drawPath(poly(top), P(col('#EADFCB', a)))
    for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
        if (xb - xa) - (yb - ya) > 0 or True:
            q = poly([P3(xa, ya, h), P3(xb, yb, h), P3(xb, yb, 0), P3(xa, ya, 0)]); cv.drawPath(q, P(col('#C9B391', 0.9 * a)))
    cv.drawPath(poly(top), P(col('#B79D78', a), stroke=2))
def mini_ferry(cv, x, y, d, a, lights):
    L = 2.2
    box(cv, WORLD, x - L / 2, y - 0.4, 0, L, 0.8, 0.35, NAVY, a, top=0.3)
    box(cv, WORLD, x - L * 0.3, y - 0.3, 0.35, L * 0.55, 0.6, 0.3, '#F4F0EA', a, top=0.2)
    box(cv, WORLD, x - L * 0.2, y - 0.1, 0.65, 0.25, 0.2, 0.3, ORANGE, a)
    if lights > 0:
        p = P3(x, y + 0.3, 0.5); cv.drawCircle(p[0], p[1], 10, P(col('#FFC98A', 0.8 * lights * a), blur=6))
def gF(cv, t):
    a0 = eo(prog(t, 34.068, 34.5)); night = eio(prog(t, 36.6, 37.6))
    zoom = lerp(0.86, 0.94, eio(prog(t, 34.068, 38.692))); fw = (0.2, 1.0, 0.0); f = P3(*fw); sx, sy = 540, 820
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    x0, x1, y0, y1 = -18.0, 18.0, -14.0, 14.0
    sea_bed(cv, x0, x1, y0, y1, a0); sea_top(cv, t, x0, x1, y0, y1, a0)
    land(cv, [(-18, 6), (-6, 6), (-3, 9), (-4, 14), (-18, 14)], a0)       # Jawa (Merak) kiri-bawah
    land(cv, [(6, -14), (18, -14), (18, -4), (7, -4), (4, -8)], a0)       # Sumatra (Bakauheni) kanan-atas
    for (px_, py_) in ((-5.0, 7.0), (5.5, -5.5)):                         # dermaga
        box(cv, WORLD, px_ - 0.6, py_ - 1.2, 0, 1.2, 2.4, 0.9, '#D6CDBF', a0, top=0.25)
    for k in range(7):                                                    # feri bolak-balik di lintasan
        ph = (t * 0.06 + k / 7) % 1.0; d = 1 if k % 2 else -1; u = ph if d > 0 else 1 - ph
        x = lerp(-3.8, 4.2, u) + (k % 3 - 1) * 1.2; y = lerp(6.4, -4.6, u) + (k % 3 - 1) * 1.6
        mini_ferry(cv, x, y, d, a0, night)
    for k in range(3):
        p0, p1 = P3(-4.0 + (k - 1) * 1.2, 6.2 + (k - 1) * 1.6, 0.02), P3(4.4 + (k - 1) * 1.2, -4.4 + (k - 1) * 1.6, 0.02)
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, 0.4 * a0), stroke=3, effect=skia.DashPathEffect.Make([14, 12], -t * 30)))
    cv.restore()
    if night > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(shader=lg(0, 0, 0, 1920, [col(NAVY2, 0.42 * night), col(NAVY2, 0.18 * night)])))
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    for (wx, wy_, nm, lx, ly, t0) in ((-8.0, 9.0, 'MERAK', 270, 1180, 34.2), (9.0, -8.0, 'BAKAUHENI', 800, 420, 34.9)):
        q = eo(prog(t, t0, t0 + 0.35))
        if q > 0: p = S((wx, wy_, 0.8)); label(cv, nm, p[0], p[1], lx, ly, a0 * q, size=28, sub='Banten' if nm == 'MERAK' else 'Lampung')
    ca = eo(prog(t, 35.7, 36.0))
    if ca > 0: chip(cv, 'PULUHAN KAPAL FERI', 540, 1340, a0 * ca, size=30, bg=ORANGE)
    na = eo(prog(t, 37.0, 37.3))
    if na > 0: chip(cv, 'SIANG & MALAM', 540, 330, a0 * na, size=28, bg=INK)

# ------------------------------------------------------------ G & J
CMTS = [('pesawat!', 280, 760, 39.1, ORANGE), ('bendungan dong', 760, 900, 39.35, INK), ('kapal selam pls', 310, 1040, 39.6, ORANGE_D), ('tower crane!!', 760, 1180, 39.85, NAVY)]
def gG(cv, t):
    a0 = eo(prog(t, 38.692, 39.0))
    logo_mark(cv, 540, 430, 80 * lerp(0.6, 1, bo(prog(t, 38.692, 39.1))), a0, t)
    text_c(cv, 'BONGKAR APA LAGI?', 540, 590, 64, INK, a0 * eo(prog(t, 38.8, 39.1)))
    for txt, x, y, t0, c in CMTS:
        q = prog(t, t0, t0 + 0.3)
        if q <= 0: continue
        aa = a0 * clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
        r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, aa, rad=42, lift=10)
        cv.drawCircle(r.left() + 42, 0, 24, P(col(c, aa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, aa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, aa)))
        cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, aa)))
        cv.restore()
    ca = eo(prog(t, 40.92, 41.2))
    if ca > 0: chip(cv, 'TULIS DI KOMENTAR', 540, 1340, a0 * ca, size=30, bg=ORANGE)
def gJ(cv, t):
    tt = t - 42.247; a = eo(prog(tt, 0.0, 0.4)); p_ = bo(prog(tt, 0.0, 0.6))
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
    ev = [(0.0, 'whoosh'), (0.35, 'buzzer'), (0.4, 'clunk'), (0.85, 'stamp'), (0.9, 'splash'), (1.0, 'whoosh'), (1.85, 'clunk'), (1.87, 'rumble'),
          (2.05, 'rewind'), (2.95, 'shine'), (3.3, 'swish'), (3.7, 'zap'), (3.75, 'pop'), (3.9, 'ding'), (4.85, 'pop'), (5.0, 'pop'), (5.15, 'pop'),
          (6.72, 'whoosh'), (7.59, 'pop'), (8.88, 'shine'), (8.95, 'pop'), (9.1, 'pop'), (9.2, 'pop'), (10.05, 'card'), (10.5, 'swish'), (11.3, 'clunk'), (11.4, 'ding'),
          (14.158, 'whoosh'), (15.2, 'swish'), (15.4, 'pour'), (16.9, 'splash'), (17.31, 'rise'), (17.5, 'pop'), (19.4, 'stamp'), (19.6, 'pop'), (19.7, 'ding'),
          (21.131, 'whoosh'), (21.95, 'zap'), (22.0, 'pop'), (24.6, 'crack'), (24.65, 'buzzer'), (24.7, 'pour'), (25.34, 'ding'), (25.45, 'stamp'),
          (26.98, 'whoosh'), (27.0, 'card'), (29.01, 'pop'), (30.51, 'pop'), (30.6, 'swish'), (31.2, 'buzzer'), (32.2, 'ding'), (32.3, 'stamp'),
          (34.068, 'whoosh'), (34.2, 'pop'), (34.9, 'pop'), (35.7, 'pop'), (35.75, 'ding_soft'), (36.6, 'swish'), (37.0, 'pop'),
          (38.692, 'whoosh'), (38.8, 'shine'), (39.1, 'pop'), (39.35, 'pop'), (39.6, 'pop'), (39.85, 'pop'), (40.92, 'pop'),
          (42.247, 'whoosh'), (42.4, 'boing'), (42.75, 'shine'), (43.0, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
