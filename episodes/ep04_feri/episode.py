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

# ------------------------------------------------------------ laut diorama (premium: kilau matahari, berkas cahaya bawah air, dasar laut berpasir)
def strata_face(cv, plane, pv, u0, u1, a, dk=0.0):
    face = poly([fpt(plane, pv, u0, BED_Z), fpt(plane, pv, u1, BED_Z), fpt(plane, pv, u1, SOIL_Z), fpt(plane, pv, u0, SOIL_Z)])
    cv.save(); cv.clipPath(face, doAntiAlias=True); n = 30
    for k, (z0, z1, c) in enumerate(SOIL):
        us = [lerp(u0, u1, i / n) for i in range(n + 1)]
        top = [fpt(plane, pv, u, z0 + (wav(u, k) if k else 0)) for u in us]; bot = [fpt(plane, pv, u, z1 + wav(u, k + 1)) for u in us[::-1]]
        cv.drawPath(poly(top + bot), P(shader=lg(*fpt(plane, pv, u0, z0), *fpt(plane, pv, u0, max(z1, SOIL_Z)), [col(tone(c, dk + 0.05), a), col(tone(c, dk - 0.06), a)])))
        if k: cv.drawPath(poly(top, False), P(col(tone(c, -0.35), 0.35 * a), stroke=1.4))
    cv.restore(); cv.drawPath(face, P(col('#8C6A4A', 0.5 * a), stroke=1.5))
def seabed_top(cv, t, x0, x1, y0, y1, a):
    quad(cv, WORLD, [(x0, y0, BED_Z), (x1, y0, BED_Z), (x1, y1, BED_Z), (x0, y1, BED_Z)], '#E2C9A0', a, grad=((x0, y1, BED_Z), (x1, y0, BED_Z), '#EAD5B0', '#CDB089'))
    for k in range(int((y1 - y0) / 0.9)):                                 # riak pasir
        y = y0 + 0.5 + k * 0.9
        pts = [P3(x, y + 0.12 * math.sin(x * 1.3 + k), BED_Z + 0.01) for x in [x0 + i * 0.5 for i in range(int((x1 - x0) / 0.5) + 1)]]
        cv.drawPath(poly(pts, False), P(col('#B8996F', 0.5 * a), stroke=1.6))
    rnd = random.Random(11)
    for k in range(9):                                                    # batu
        x, y = rnd.uniform(x0 + 1, x1 - 1), rnd.uniform(y0 + 1, y1 - 1); r = rnd.uniform(0.3, 0.7)
        box(cv, WORLD, x, y, BED_Z, r, r * 0.8, r * 0.45, '#9C8466', a, top=0.25)
def water_face(cv, t, plane, pv, u0, u1, a, dk=0.0, hole=None, level=SEA_Z):
    q = poly([fpt(plane, pv, u0, level), fpt(plane, pv, u1, level), fpt(plane, pv, u1, BED_Z), fpt(plane, pv, u0, BED_Z)])
    if hole is not None: q = skia.Op(q, hole, skia.PathOp.kDifference_PathOp)
    cv.drawPath(q, P(shader=lg(*fpt(plane, pv, u0, level), *fpt(plane, pv, u0, BED_Z), [col(tone('#6A86B6', dk), 0.72 * a), col(tone('#2B4170', dk), 0.82 * a), col(tone('#1A2A4C', dk), 0.9 * a)], [0, 0.55, 1])))
    cv.save(); cv.clipPath(q, doAntiAlias=True)                           # berkas cahaya matahari di dalam air
    for k in range(6):
        uc = lerp(u0, u1, (k + 0.5) / 6) + 0.8 * math.sin(t * 0.5 + k * 1.7); w = 0.6 + 0.3 * math.sin(k * 2.1)
        ray = poly([fpt(plane, pv, uc - w, level), fpt(plane, pv, uc + w, level), fpt(plane, pv, uc + w + 1.6, BED_Z), fpt(plane, pv, uc - w + 0.6, BED_Z)])
        cv.drawPath(ray, P(col(WHITE, 0.07 * a * (0.6 + 0.4 * math.sin(t * 1.3 + k))), blur=10))
    cv.restore()
    ln = poly([fpt(plane, pv, lerp(u0, u1, i / 60), level + 0.06 * math.sin(i * 0.9 + t * 3)) for i in range(61)], False)
    cv.save()
    if hole is not None: cv.clipPath(hole, skia.ClipOp.kDifference, True)
    cv.drawPath(ln, P(col(WHITE, 0.75 * a), stroke=3)); cv.restore()
def sea_top(cv, t, x0, x1, y0, y1, a, alpha=1.0):
    quad(cv, WORLD, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], '#4A6496', a * alpha, grad=((x0, y1, 0), (x1, y0, 0), '#7690BE', '#3A5487'))
    cv.save(); cv.clipPath(WORLD.path([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)]), doAntiAlias=True)
    for k in range(4):                                                    # kilau matahari: pita terang diagonal
        xc = x0 + (x1 - x0) * (0.2 + 0.2 * k) + 1.5 * math.sin(t * 0.4 + k)
        band = WORLD.path([(xc - 0.6, y0, 0), (xc + 0.6, y0, 0), (xc + 2.6, y1, 0), (xc + 1.4, y1, 0)])
        cv.drawPath(band, P(col(WHITE, 0.08 * a * alpha), blur=14))
    cv.restore()
    rnd = random.Random(5)
    for k in range(int((x1 - x0) * (y1 - y0) / 9)):
        x = x0 + (rnd.uniform(0, 1) * (x1 - x0) + t * 0.35) % (x1 - x0); y = rnd.uniform(y0 + 0.4, y1 - 0.4); L = rnd.uniform(0.4, 1.0)
        if x + L > x1: continue
        p0, p1 = P3(x, y, 0.01), P3(x + L, y, 0.01)
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, a * alpha * 0.5 * (0.5 + 0.5 * math.sin(t * 2.2 + k))), stroke=2.2))
def sea_bed(cv, t, x0, x1, y0, y1, a):
    seabed_top(cv, t, x0, x1, y0, y1, a)
    strata_face(cv, 'y', y1, x0, x1, a); strata_face(cv, 'x', x1, y0, y1, a, dk=-0.1)
def text_on_y(cv, txt, x0, yp, zb, size, c, a, font_name=XB):
    """teks menempel di bidang y = yp (sepanjang sumbu x, tegak ke atas z)"""
    s_, c30 = WORLD.s, math.cos(math.radians(30))
    ox, oy = P3(x0, yp, zb)
    cv.save(); cv.concat(skia.Matrix.MakeAll(c30 * s_, 0, ox, 0.5 * s_, s_, oy, 0, 0, 1))
    f = font(font_name, size); cv.drawString(txt, 0, 0, f, P(col(c, a))); cv.restore()

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
BULK = [-6.5, -2.6, 1.4, 5.3]
CDECK = 0.3
TANK = -1.7
COMP = [(-10.0, -6.5, 'mesin'), (-6.5, -2.6, 'udara'), (-2.6, 1.4, 'udara'), (1.4, 5.3, 'udara'), (5.3, 9.6, 'udara')]
GLASS, GLASS_HI = '#22345C', '#5A73A3'

class Pose:
    def __init__(self, dz=0.0, trim=0.0): self.dz, self.trim = dz, trim
    def z(self, x, z): return z + self.dz + self.trim * x
def sp(pose, x, y, z): return P3(x, y, pose.z(x, z))
def profile_path(pose, y=0.0):
    return poly([sp(pose, x, y, zbot(x)) for x in STA] + [sp(pose, x, y, zdeck(x)) for x in STA[::-1]])

def propeller(cv, pose, a, t):
    x, z = -9.75, -1.65
    box(cv, WORLD, -10.5, -0.12, pose.z(-10.5, -2.0), 0.45, 0.24, 1.3, NAVY2, a, top=0.2)          # kemudi
    p = sp(pose, x, 0.15, z)
    for k in range(4):
        ang = t * 9 + k * math.pi / 2; dx, dy = math.cos(ang), math.sin(ang)
        tip = (p[0] + dx * 26, p[1] + dy * 26); cv.drawLine(p[0], p[1], tip[0], tip[1], P(col('#C9A35A', a), stroke=9))
    cv.drawCircle(p[0], p[1], 7, P(col('#8E7440', a)))
def hull_whole(cv, pose, a, part, t=0.0):
    """sisi dekat lambung utuh (y = +wb), bergradasi; part='bawah' (di bawah garis air) atau 'atas'"""
    if part == 'bawah': propeller(cv, pose, a, t)
    for xa, xb in zip(STA[:-1], STA[1:]):
        rows = []
        for x in (xa, xb):
            zb_, zt = pose.z(x, zbot(x)), pose.z(x, zdeck(x)); w = wb(x); zw = clamp(0.0, zb_, zt)
            rows.append((x, w, zb_, zw, zt))
        (x0, w0, b0, m0, t0), (x1, w1, b1, m1, t1) = rows
        k = 0.06 if xa > 5 else 0.0
        if part == 'bawah' and (m0 > b0 or m1 > b1):
            q = poly([P3(x0, w0 * 0.9, b0), P3(x1, w1 * 0.9, b1), P3(x1, w1, m1), P3(x0, w0, m0)])
            cv.drawPath(q, P(shader=lg(*P3(x0, w0, m0), *P3(x0, w0, b0), [col(tone(NAVY2, k + 0.05), a), col(tone('#0E1830', k), a)])))
        if part == 'atas' and (t0 > m0 or t1 > m1):
            q = poly([P3(x0, w0, m0), P3(x1, w1, m1), P3(x1, w1, t1), P3(x0, w0, t0)])
            cv.drawPath(q, P(shader=lg(*P3(x0, w0, t0), *P3(x0, w0, m0), [col(tone(NAVY, k + 0.12), a), col(tone(NAVY, k - 0.08), a)])))
            for zl, h, c in ((0.78, 0.2, ORANGE), (1.12, 0.06, '#F4F0EA')):
                s0, s1 = pose.z(x0, zl), pose.z(x1, zl)
                if t0 > s0 + h and m0 < s0: cv.drawPath(poly([P3(x0, w0, s0), P3(x1, w1, s1), P3(x1, w1, s1 + h), P3(x0, w0, s0 + h)]), P(col(c, a)))
    if part == 'atas':
        for x in [lerp(-9.0, 6.6, i / 22) for i in range(23)]:              # jendela bulat lambung
            p = sp(pose, x, wb(x) + 0.01, 0.42)
            cv.drawCircle(p[0], p[1], 4.2, P(col('#F4F0EA', 0.9 * a))); cv.drawCircle(p[0], p[1], 2.4, P(col(GLASS, a)))
        text_on_y(cv, 'BONGKAR BENDA', -4.2, 2.21, pose.z(-1.0, 0.18), 0.42, '#F4F0EA', 0.95 * a)
        p = sp(pose, 8.9, wb(8.9) + 0.02, 0.85); cv.drawRect(skia.Rect(p[0] - 5, p[1] - 3, p[0] + 9, p[1] + 9), P(col('#0E1830', a)))  # jangkar
        top = [sp(pose, x, wb(x), zdeck(x)) for x in STA] + [sp(pose, x, -wb(x), zdeck(x)) for x in STA[::-1]]
        cv.drawPath(poly(top), P(shader=lg(*sp(pose, XS, 0, 1.4), *sp(pose, XB_, 0, 1.4), [col('#DDD7CD', a), col('#CFC8BD', a)])))
        rail = [sp(pose, x, wb(x), zdeck(x) + 0.28) for x in STA]; cv.drawPath(poly(rail, False), P(col('#F4F0EA', a), stroke=2))
        for x in STA[::2]:
            p0, p1 = sp(pose, x, wb(x), zdeck(x)), sp(pose, x, wb(x), zdeck(x) + 0.28); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#F4F0EA', 0.8 * a), stroke=1.2))
def window_band(cv, pose, x0, x1, yp, z0, z1, a, lights=0.0):
    q = poly([sp(pose, x0, yp, z0), sp(pose, x1, yp, z0), sp(pose, x1, yp, z1), sp(pose, x0, yp, z1)])
    cv.drawPath(q, P(shader=lg(*sp(pose, x0, yp, z1), *sp(pose, x0, yp, z0), [col(mixc(GLASS_HI, '#FFC98A', lights), a), col(mixc(GLASS, '#E0600A', lights * 0.6), a)])))
    cv.save(); cv.clipPath(q, doAntiAlias=True)
    for k in range(int(x1 - x0) + 2):                                      # pantulan kaca diagonal
        xx = x0 + k * 1.1 + 0.3
        st = poly([sp(pose, xx, yp, z0), sp(pose, xx + 0.25, yp, z0), sp(pose, xx + 0.55, yp, z1), sp(pose, xx + 0.3, yp, z1)])
        cv.drawPath(st, P(col(WHITE, 0.16 * a)))
    for k in range(int((x1 - x0) / 0.6) + 1):                              # tiang jendela
        p0, p1 = sp(pose, x0 + k * 0.6, yp, z0), sp(pose, x0 + k * 0.6, yp, z1); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#F4F0EA', 0.7 * a), stroke=1.4))
    cv.restore()
def superstructure(cv, pose, a, cut=False, t=0.0, lights=0.0):
    W = '#F6F2EC'
    decks = [(-7.0, 5.6, 1.95, 1.4, 1.5), (-5.4, 4.0, 1.75, 2.9, 1.3), (1.8, 4.6, 1.6, 4.2, 0.9)]
    if cut:
        for x0, x1, hw, z0, h in decks:                                    # interior terbuka: dinding belakang, lantai, kursi, atap
            q = poly([sp(pose, x0, -hw, z0), sp(pose, x1, -hw, z0), sp(pose, x1, -hw, z0 + h), sp(pose, x0, -hw, z0 + h)])
            cv.drawPath(q, P(shader=lg(*sp(pose, x0, -hw, z0 + h), *sp(pose, x0, -hw, z0), [col('#F1ECE4', a), col('#DCD4C8', a)])))
            window_band(cv, pose, x0 + 0.4, x1 - 0.4, -hw + 0.01, z0 + 0.5, z0 + h - 0.35, a * 0.9, lights)
            quad(cv, WORLD, [(x0, -hw, pose.z(x0, z0)), (x1, -hw, pose.z(x1, z0)), (x1, 0, pose.z(x1, z0)), (x0, 0, pose.z(x0, z0))], '#C9C2B6', a)
            if h > 1.0:
                for row in range(int((x1 - x0 - 1.0) / 0.8)):
                    xr = x0 + 0.6 + row * 0.8
                    box(cv, WORLD, xr, -hw + 0.35, pose.z(xr, z0), 0.35, hw - 0.5, 0.32, NAVY, a, top=0.3)
            else:
                box(cv, WORLD, x0 + 0.4, -hw + 0.3, pose.z(x0, z0), x1 - x0 - 0.8, 0.5, 0.45, NAVY2, a, top=0.3)   # konsol anjungan
            for (pa, pb) in (((x0, 0, z0), (x1, 0, z0)), ((x0, 0, z0 + h), (x1, 0, z0 + h)), ((x0, 0, z0), (x0, 0, z0 + h)), ((x1, 0, z0), (x1, 0, z0 + h))):
                p0, p1 = sp(pose, *pa), sp(pose, *pb); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=5))
            quad(cv, WORLD, [(x0, -hw, pose.z(x0, z0 + h)), (x1, -hw, pose.z(x1, z0 + h)), (x1, 0, pose.z(x1, z0 + h)), (x0, 0, pose.z(x0, z0 + h))], tone(W, -0.02), a * 0.0)
        box(cv, WORLD, -4.9, -0.7, pose.z(-4.2, 4.2), 1.4, 0.7, 2.2, ORANGE, a, top=0.25); box(cv, WORLD, -4.9, -0.7, pose.z(-4.2, 6.4), 1.4, 0.7, 0.3, NAVY2, a)
        return
    for x0, x1, hw, z0, h in decks:
        box(cv, WORLD, x0, -hw, pose.z((x0 + x1) / 2, z0), x1 - x0, 2 * hw, h, W, a, top=0.18, left=0.0, right=-0.12)
        window_band(cv, pose, x0 + 0.3, x1 - 0.3, hw + 0.01, z0 + 0.45, z0 + h - 0.35, a, lights)
        rail = [sp(pose, x0, hw, z0 + h + 0.22), sp(pose, x1, hw, z0 + h + 0.22)]; cv.drawLine(rail[0][0], rail[0][1], rail[1][0], rail[1][1], P(col(W, a), stroke=2))
    q = poly([sp(pose, 4.6, 1.6, 4.55), sp(pose, 4.6, -1.6, 4.55), sp(pose, 4.6, -1.6, 4.95), sp(pose, 4.6, 1.6, 4.95)])                         # kaca depan anjungan
    cv.drawPath(q, P(col(GLASS, a)))
    box(cv, WORLD, 2.4, -2.3, pose.z(3.0, 4.35), 1.6, 4.6, 0.12, W, a, top=0.2)                                                              # sayap anjungan
    for x in (-4.0, -1.6, 0.8):                                                                                                              # sekoci
        box(cv, WORLD, x, 1.78, pose.z(x, 3.0), 1.3, 0.38, 0.38, ORANGE, a, top=0.3)
        p0, p1 = sp(pose, x + 0.2, 1.75, 3.6), sp(pose, x + 0.2, 1.95, 3.1); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=2))
    box(cv, WORLD, -4.9, -0.7, pose.z(-4.2, 4.2), 1.4, 1.4, 2.2, ORANGE, a, top=0.25, right=-0.18)                                           # cerobong
    box(cv, WORLD, -4.9, -0.7, pose.z(-4.2, 5.55), 1.4, 1.4, 0.18, '#F6F2EC', a); box(cv, WORLD, -4.95, -0.75, pose.z(-4.2, 6.4), 1.5, 1.5, 0.3, NAVY2, a)
    m0, m1 = sp(pose, 3.1, 0, 5.1), sp(pose, 3.1, 0, 6.7); cv.drawLine(m0[0], m0[1], m1[0], m1[1], P(col(NAVY2, a), stroke=4))               # tiang + radar berputar
    ra = t * 3.0; r0 = sp(pose, 3.1 - 0.7 * math.cos(ra), -0.7 * math.sin(ra), 6.5); r1 = sp(pose, 3.1 + 0.7 * math.cos(ra), 0.7 * math.sin(ra), 6.5)
    cv.drawLine(r0[0], r0[1], r1[0], r1[1], P(col(NAVY2, a), stroke=4))
def vehicles(cv, pose, a):
    for x, L, c, kind in ((-6.0, 2.6, '#F4F0EA', 'truk'), (-3.0, 1.3, ORANGE, 'mobil'), (-1.4, 1.3, NAVY, 'mobil'), (0.3, 2.6, '#F4F0EA', 'bus'), (3.3, 1.3, '#F7F4EF', 'mobil')):
        z = pose.z(x + L / 2, CDECK); y = -0.45
        if kind == 'truk':
            box(cv, WORLD, x, y - 0.32, z, L * 0.72, 0.64, 0.74, c, a, top=0.15); box(cv, WORLD, x + L * 0.75, y - 0.3, z, L * 0.25, 0.6, 0.54, ORANGE, a, top=0.2)
        elif kind == 'bus':
            box(cv, WORLD, x, y - 0.32, z, L, 0.64, 0.72, ORANGE_D, a, top=0.15)
            quad(cv, WORLD, [(x + 0.2, y + 0.33, z + 0.38), (x + L - 0.2, y + 0.33, z + 0.38), (x + L - 0.2, y + 0.33, z + 0.6), (x + 0.2, y + 0.33, z + 0.6)], GLASS, a)
        else:
            box(cv, WORLD, x, y - 0.28, z, L, 0.56, 0.27, c, a, top=0.22); box(cv, WORLD, x + 0.28, y - 0.24, z + 0.27, L * 0.5, 0.48, 0.22, '#5A6B8C' if c == NAVY else NAVY, a, top=0.3)
def hull_cut(cv, t, pose, a, air_glow=0.0, bulk_glow=0.0, flood=None):
    """separuh belakang lambung (y<=0): dinding dalam berangka, lantai, sekat, ruang mesin, dek kendaraan, pelat baja tebal di bidang potong"""
    def wallq(x0, x1, z0f, z1f, c0, c1):
        for xa, xb in zip(STA[:-1], STA[1:]):
            if xb <= x0 or xa >= x1: continue
            xa_, xb_ = max(xa, x0), min(xb, x1)
            q = poly([sp(pose, xa_, -wb(xa_), z0f(xa_)), sp(pose, xb_, -wb(xb_), z0f(xb_)), sp(pose, xb_, -wb(xb_), z1f(xb_)), sp(pose, xa_, -wb(xa_), z1f(xa_))])
            cv.drawPath(q, P(shader=lg(*sp(pose, xa_, -wb(xa_), z1f(xa_)), *sp(pose, xa_, -wb(xa_), z0f(xa_)), [col(c0, a), col(c1, a)])))
        x = x0 + 0.35
        while x < x1 - 0.1:                                                # rangka (gading-gading)
            p0, p1 = sp(pose, x, -wb(x), z0f(x)), sp(pose, x, -wb(x), z1f(x)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#B8AE9F', 0.55 * a), stroke=2)); x += 0.7
    for i, (x0, x1, kind) in enumerate(COMP):
        if kind == 'udara': wallq(x0, x1, zbot, lambda x: CDECK, '#EFE8DD', '#D9CFBF')
        else: wallq(x0, x1, zbot, lambda x: CDECK, '#C5CBD6', '#9CA6B8')
        xa_, xb_ = max(x0, -9.6), min(x1, 7.4)
        if xb_ > xa_: quad(cv, WORLD, [(xa_, -wb(xa_), pose.z(xa_, TANK)), (xb_, -wb(xb_), pose.z(xb_, TANK)), (xb_, 0, pose.z(xb_, TANK)), (xa_, 0, pose.z(xa_, TANK))], '#D0C6B6', a)
        if kind == 'mesin':
            box(cv, WORLD, -9.0, -1.45, pose.z(-8.2, TANK), 2.0, 1.0, 0.9, NAVY, a, top=0.3)
            for k in range(4): box(cv, WORLD, -8.85 + k * 0.45, -1.3, pose.z(-8.2, TANK + 0.9), 0.32, 0.6, 0.32, ORANGE, a, top=0.3)
            p0, p1 = sp(pose, -8.0, -1.0, TANK + 1.2), sp(pose, -8.0, -1.0, CDECK); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(ORANGE_D, a), stroke=5))
            p0, p1 = sp(pose, -9.0, -0.9, -1.65), sp(pose, -9.75, -0.4, -1.65); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#8E7440', a), stroke=5))   # poros
        if flood and flood[0] == i and flood[1] > 0:
            zl = lerp(TANK, CDECK - 0.1, flood[1]) + 0.05 * math.sin(t * 6)
            q = poly([sp(pose, x0, 0, TANK), sp(pose, x1, 0, TANK), sp(pose, x1, 0, zl), sp(pose, x0, 0, zl)])
            cv.drawPath(q, P(shader=lg(*sp(pose, x0, 0, zl), *sp(pose, x0, 0, TANK), [col('#6A86B6', 0.88 * a), col('#22345C', 0.95 * a)])))
            ln = poly([sp(pose, x0, 0, zl), sp(pose, x0, -wb(x0), zl), sp(pose, x1, -wb(x1), zl), sp(pose, x1, 0, zl)]); cv.drawPath(ln, P(col('#7690BE', 0.85 * a)))
            for k in range(6):
                xx = lerp(x0 + 0.3, x1 - 0.3, k / 5); p0 = sp(pose, xx, 0, zl); cv.drawLine(p0[0] - 10, p0[1], p0[0] + 10, p0[1] - 3, P(col(WHITE, 0.7 * a), stroke=3))
        if i + 1 < len(COMP):
            xb = x1
            q = poly([sp(pose, xb, -wb(xb), zbot(xb)), sp(pose, xb, 0, zbot(xb)), sp(pose, xb, 0, CDECK), sp(pose, xb, -wb(xb), CDECK)])
            cv.drawPath(q, P(shader=lg(*sp(pose, xb, -wb(xb), CDECK), *sp(pose, xb, 0, zbot(xb)), [col('#D9D0C2', a), col('#BDB2A2', a)])))
            if bulk_glow > 0: cv.drawPath(q, P(col(ORANGE, 0.5 * bulk_glow * a)))
    quad(cv, WORLD, [(XS, -wb(XS), pose.z(XS, CDECK)), (9.6, -wb(9.6), pose.z(9.6, CDECK)), (9.6, 0, pose.z(9.6, CDECK)), (XS, 0, pose.z(XS, CDECK))], '#BFC5CF', a)
    for k in range(9):                                                     # marka jalur kendaraan
        x = -8.8 + k * 2.0; p0, p1 = sp(pose, x, -0.95, CDECK + 0.005), sp(pose, x + 1.0, -0.95, CDECK + 0.005); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(YELLOW, 0.8 * a), stroke=2))
    wallq(XS, 9.6, lambda x: CDECK, lambda x: 1.4, '#EAE4DA', '#D6CEC1')
    vehicles(cv, pose, a)
    if air_glow > 0:
        for i, (x0, x1, kind) in enumerate(COMP):
            if kind != 'udara' or (flood and flood[0] == i and flood[1] > 0.05): continue
            ph = 0.75 + 0.25 * math.sin(t * 4 + i)
            q = poly([sp(pose, x, 0, max(zbot(x), TANK)) for x in STA if x0 <= x <= x1] + [sp(pose, x1, 0, CDECK - 0.05), sp(pose, x0, 0, CDECK - 0.05)])
            cv.drawPath(q, P(shader=lg(*sp(pose, x0, 0, CDECK), *sp(pose, x0, 0, TANK), [col('#FFF1DE', 0.7 * air_glow * a), col(AIR, 0.85 * air_glow * a)])))
            cv.drawPath(q, P(col(ORANGE, 0.32 * air_glow * ph * a), blur=14))
            for k in range(3):                                             # kilau udara bergerak
                xx = lerp(x0, x1, ((t * 0.25 + k / 3 + i * 0.13) % 1.0)); p0, p1 = sp(pose, xx, 0, TANK + 0.3), sp(pose, xx + 0.5, 0, CDECK - 0.2)
                cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, 0.35 * air_glow * a), stroke=5))
    sec = [sp(pose, x, 0, zbot(x)) for x in STA]                             # pelat baja tebal di bidang potong
    cv.drawPath(poly(sec, False), P(col(NAVY2, a), stroke=13)); cv.drawPath(poly(sec, False), P(col(GLASS_HI, 0.55 * a), stroke=3))
    for zz in (TANK, CDECK, 1.4):
        xa_, xb_ = (-9.6, 7.4) if zz == TANK else (XS, 9.6 if zz == CDECK else XB_)
        p0, p1 = sp(pose, xa_, 0, zz), sp(pose, xb_, 0, zz); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=8))
    for xb in BULK:
        p0, p1 = sp(pose, xb, 0, zbot(xb)), sp(pose, xb, 0, CDECK)
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(ORANGE if bulk_glow > 0.3 else NAVY2, a), stroke=9 + 4 * bulk_glow))
    p0, p1 = sp(pose, XS, 0, zbot(XS)), sp(pose, XS, 0, 1.4); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=10))
def wake(cv, t, pose, a):
    for k in range(4):                                                     # jejak ombak di belakang & buih haluan
        ph = (t * 0.6 + k / 4) % 1.0; L = 2 + 7 * ph
        for sd in (-1, 1):
            p0, p1 = P3(XS - 0.5 - L, sd * (1.6 + 1.6 * ph), 0.02), P3(XS - 0.5 - L - 1.2, sd * (1.9 + 1.6 * ph), 0.02)
            cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, 0.55 * (1 - ph) * a), stroke=3))
    for k in range(3):
        ph = (t * 1.3 + k / 3) % 1.0; p0 = sp(pose, XB_ - 0.3 - ph * 2.4, wb(XB_ - 1) + 0.3 + ph * 0.9, 0.02)
        cv.drawLine(p0[0], p0[1], p0[0] - 34, p0[1] - 9, P(col(WHITE, 0.8 * (1 - ph) * a), stroke=3.5))
    pts = [sp(pose, x, wb(x) + 0.06, 0.03 + 0.04 * math.sin(x * 3 + t * 5)) for x in STA]   # garis buih di garis air
    cv.drawPath(poly(pts, False), P(col(WHITE, 0.7 * a), stroke=3))
def ship(cv, t, pose, a, cut=0.0, air_glow=0.0, bulk_glow=0.0, flood=None, under=None, lights=0.0, wake_on=True):
    if cut > 0:
        if under: under()
        hull_cut(cv, t, pose, a, air_glow, bulk_glow, flood)
        superstructure(cv, pose, a, cut=True, t=t, lights=lights)
    if cut < 1:
        aw = a * (1 - cut)
        hull_whole(cv, pose, aw, 'bawah', t)
        if under and cut <= 0: under()
        if wake_on: wake(cv, t, pose, aw)
        hull_whole(cv, pose, aw, 'atas', t)
        superstructure(cv, pose, aw, cut=False, t=t, lights=lights)

def bubbles(cv, x, y, z0, z1, t, a, n=10, seed=3):
    rnd = random.Random(seed)
    for k in range(n):
        ph = (t * rnd.uniform(0.5, 0.9) + rnd.random()) % 1.0; xx = x + rnd.uniform(-1.2, 1.2) + 0.2 * math.sin(t * 5 + k); zz = lerp(z0, z1, ph)
        p = P3(xx, y + rnd.uniform(-0.5, 0.5), zz); r = rnd.uniform(4, 9)
        cv.drawCircle(p[0], p[1], r, P(col(WHITE, 0.8 * a * (1 - ph)), stroke=2))

SEA_A = (-15.0, 15.0, -7.0, 4.4)
SEA_C = (-15.0, 15.0, -7.0, 0.0)
def world(cv, t, a, pose, cut, sea, **kw):
    x0, x1, y0, y1 = sea
    sea_bed(cv, t, x0, x1, y0, y1, a)
    under = lambda: sea_top(cv, t, x0, x1, y0, y1, a, alpha=0.84)
    ship(cv, t, pose, a, cut=cut, under=under, wake_on=(cut < 1), **kw)
    hole = profile_path(pose, 0.0) if y1 <= 0.01 else None
    water_face(cv, t, 'y', y1, x0, x1, a, hole=hole); water_face(cv, t, 'x', x1, y0, y1, a, dk=-0.1)

# ------------------------------------------------------------ A: HOOK — kapal diremas jadi kubus baja, tenggelam; REWIND; dibelah garis cahaya, rongga udara menyala (0 - 6.72)
T_M0, T_M1, T_SINK, T_BED, T_RW, T_BACK, T_CUT = 0.35, 0.85, 0.9, 1.85, 2.05, 2.95, 3.25
SHIP_C = (0.3, 0.0, 0.6)
def steel_cube(cv, zc, a, s_=2.7):
    x, y = -s_ / 2 + 0.3, -s_ / 2
    box(cv, WORLD, x, y, zc - s_ / 2, s_, s_, s_, '#7D879A', a, top=0.38, left=0.06, right=-0.22)
    for k in range(3):                                                     # guratan baja remuk
        p0, p1 = P3(x + 0.3 + k * 0.8, y + s_, zc - s_ / 2 + 0.2), P3(x + 0.6 + k * 0.7, y + s_, zc + s_ / 2 - 0.2)
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#4A5568', 0.8 * a), stroke=2))
    p0, p1 = P3(x, y + s_, zc + s_ / 2), P3(x + s_, y + s_, zc + s_ / 2); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, 0.7 * a), stroke=2.5))
def cube_z(t):
    if t < T_SINK: return 1.0
    if t < T_BED: return lerp(1.0, BED_Z + 1.35, ei(prog(t, T_SINK, T_BED)))
    if t < T_RW: return BED_Z + 1.35
    return lerp(BED_Z + 1.35, 1.0, eio(prog(t, T_RW, T_RW + 0.6)))
def crush(t):
    if t < T_RW: return eio(prog(t, T_M0, T_M1))
    return 1 - eio(prog(t, T_RW + 0.5, T_BACK))
def gA(cv, t):
    u = eio(prog(t, 0.0, 1.7)); u2 = eio(prog(t, T_RW, T_BACK + 0.4))
    zoom = lerp(1.25, 0.92, u) if t < T_RW else lerp(0.92, 1.08, u2)
    fz = lerp(1.2, -2.4, u) if t < T_RW else lerp(-2.4, -0.2, u2)
    fw = (0.6, -0.6, fz); f = P3(*fw); bob = 0.07 * math.sin(t * 2.0)
    hit = prog(t, T_BED, T_BED + 0.45); shk = 12 * math.sin(t * 60) * (1 - hit) if T_BED < t < T_BED + 0.45 else 0.0
    sx, sy = 540 + shk, 990
    m = crush(t); cut = eio(prog(t, T_CUT, T_CUT + 0.45)); air = eo(prog(t, 3.6, 3.95)) * (1 - 0.4 * prog(t, 5.6, 6.5))
    sea = SEA_A if cut < 0.5 else SEA_C
    x0, x1, y0, y1 = sea
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    sea_bed(cv, t, x0, x1, y0, y1, 1.0)
    pose = Pose(dz=bob)
    if m <= 0.001:
        ship(cv, t, pose, 1.0, cut=cut, air_glow=air, under=lambda: sea_top(cv, t, x0, x1, y0, y1, 1.0, alpha=0.84), wake_on=(cut < 1))
    else:                                                                 # diremas: hanya kapal yang mengecil, laut tetap
        c = P3(*SHIP_C); k = 1 - 0.86 * m; sa = clamp(1.0 - m * 1.2)
        def squeezed(fn):
            cv.save(); cv.translate(*c); cv.scale(k, lerp(1, 0.75, m) * k + (1 - k) * 0.4); cv.translate(-c[0], -c[1]); fn(); cv.restore()
        if sa > 0: squeezed(lambda: hull_whole(cv, pose, sa, 'bawah', t))
        sea_top(cv, t, x0, x1, y0, y1, 1.0, alpha=0.84)
        if sa > 0:
            squeezed(lambda: hull_whole(cv, pose, sa, 'atas', t)); squeezed(lambda: superstructure(cv, pose, sa, cut=False, t=t))
    if m > 0.55: steel_cube(cv, cube_z(t), clamp((m - 0.55) * 4))
    if T_M0 + 0.1 < t < T_M1 + 0.25:                                      # percikan logam saat diremas
        p = P3(*SHIP_C); from iso import sparks as _sp; _sp(cv, p[0], p[1] - 40, t, 21, bump(prog(t, T_M0 + 0.1, T_M1 + 0.25)), n=24, spread=220, up=False)
    if T_SINK < t < T_BED + 0.8: bubbles(cv, 0.3, 0.0, cube_z(t), -0.2, t, prog(t, T_SINK, T_SINK + 0.2) * (1 - prog(t, T_BED + 0.3, T_BED + 0.8)), n=16)
    if T_BED < t < T_BED + 0.8:                                           # awan pasir di dasar laut
        q = prog(t, T_BED, T_BED + 0.8); rnd = random.Random(4)
        for k in range(16):
            ang = rnd.uniform(math.pi, math.tau); L = 50 + 110 * eo(q); c0 = P3(0.3 + rnd.uniform(-1.6, 1.6), rnd.uniform(-1.2, 1.2), BED_Z)
            cv.drawLine(c0[0], c0[1], c0[0] + math.cos(ang) * L, c0[1] + math.sin(ang) * L * 0.5, P(col('#EAD5B0', 0.85 * (1 - q)), stroke=6))
    if T_SINK - 0.05 < t < T_SINK + 0.7:                                  # semburan air
        q = prog(t, T_SINK - 0.05, T_SINK + 0.7); rnd = random.Random(8)
        c_ = P3(0.3, 0, 0); cv.drawCircle(c_[0], c_[1] - 40, 140 * eo(q), P(col(WHITE, 0.5 * (1 - q) ** 2), blur=26))
        for k in range(30):
            ang = rnd.uniform(-math.pi * 0.96, -math.pi * 0.04); L = rnd.uniform(80, 260) * eo(q); c0 = P3(0.3 + rnd.uniform(-1.4, 1.4), rnd.uniform(-1.4, 1.4), 0)
            cv.drawLine(c0[0] + math.cos(ang) * L * 0.35, c0[1] + math.sin(ang) * L * 0.45, c0[0] + math.cos(ang) * L, c0[1] + math.sin(ang) * L * 1.4 + 200 * q * q, P(col(WHITE, 0.95 * (1 - q)), stroke=7))
    hole = profile_path(pose, 0.0) if y1 <= 0.01 and m < 0.5 else None
    water_face(cv, t, 'y', y1, x0, x1, 1.0, hole=hole); water_face(cv, t, 'x', x1, y0, y1, 1.0, dk=-0.1)
    lc = prog(t, T_CUT - 0.05, T_CUT + 0.5)                                # garis cahaya yang membelah kapal
    if 0 < lc < 1:
        xs_ = lerp(XS - 0.5, XB_ + 0.5, eio(lc)); pa, pb = sp(pose, xs_, 0.02, -2.6), sp(pose, xs_, 0.02, 7.0)
        cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col(ORANGE, 0.8 * bump(lc)), stroke=26, blur=14)); cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col(WHITE, bump(lc)), stroke=6))
        trail = poly([sp(pose, x, 0.02, zbot(x)) for x in STA if x <= xs_] or [pa, pb], False)
        cv.drawPath(trail, P(col(ORANGE, 0.9 * bump(lc)), stroke=6, blur=4))
    cv.restore()
    ta = 1 - eio(prog(t, bb.TITLE_OUT - 0.4, bb.TITLE_OUT))
    if ta > 0: cv.drawRect(skia.Rect(0, 0, 1080, 560), P(shader=lg(0, 380, 0, 600, [col(bb.BG0, ta), col(bb.BG0, 0)])))
    fl = max(bump(prog(t, T_BED, T_BED + 0.3)), 0.6 * bump(prog(t, T_M0 + 0.2, T_M1)))
    if fl > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.2 * fl)))
    if T_M0 < t < T_RW + 0.1: chip(cv, 'KALAU BAJANYA PADAT?', 540, 560, eo(prog(t, T_M0, T_M0 + 0.15)) * (1 - prog(t, T_RW - 0.1, T_RW + 0.1)), size=30, bg=RED)
    if T_BED < t < T_RW + 0.1:
        p = scr(P3(0.3, 1.6, BED_Z + 3.2), f, zoom, sx, sy); text_c(cv, 'TENGGELAM!', p[0], p[1], 44, RED, eo(prog(t, T_BED, T_BED + 0.15)) * (1 - prog(t, T_RW - 0.05, T_RW + 0.1)), halo=1.0)
    rw = prog(t, T_RW, T_BACK + 0.1)
    if 0 < rw < 1:
        ra = clamp(bump(rw) * 1.3)
        cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(bb.BG0, 0.14 * ra)))
        for k in range(14):
            yy = (k * 151 + t * 2400) % 1920; cv.drawRect(skia.Rect(0, yy, 1080, yy + 5), P(col(WHITE, 0.35 * ra)))
        r = skia.Rect(400, 520, 680, 600); cv.drawRoundRect(r, 40, 40, P(col(INK, ra)))
        for k in range(2):
            x0_ = 470 + k * 44; tri = skia.Path(); tri.moveTo(x0_, 560); tri.lineTo(x0_ + 38, 536); tri.lineTo(x0_ + 38, 584); tri.close(); cv.drawPath(tri, P(col(WHITE, ra)))
        f_ = font(MONO, 26); cv.drawString('ULANG', 570, bl(f_, 560), f_, P(col(WHITE, ra)))
    if t > 3.6:
        p = scr(P3(-0.6, 0, -0.9), f, zoom, sx, sy); la = eo(prog(t, 3.7, 4.05)) * (1 - prog(t, 6.4, 6.72))
        label(cv, 'RONGGA UDARA', p[0], p[1], 300, 650, la, sub='lambungnya kosong')
        check(cv, 470, 585, 24, prog(t, 3.8, 4.2), la)
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
    zoom = lerp(1.14, 1.3, eio(prog(t, 6.72, 14.158))); fw = (0.0, -0.8, -0.2); f = P3(*fw); sx, sy = 560, 990
    air = max(eo(prog(t, 7.59, 8.0)) * 0.6, eo(prog(t, 8.88, 9.2)))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    world(cv, t, a0, Pose(dz=0.05 * math.sin(t * 2.0)), 1.0, SEA_C, air_glow=air)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    for i, (x0, x1, kind) in enumerate(COMP):
        if kind != 'udara': continue
        q = eo(prog(t, 8.88 + 0.12 * i, 9.2 + 0.12 * i)) * (1 - prog(t, 13.8, 14.1))
        if q > 0: p = S(((x0 + x1) / 2, 0, -0.75)); chip(cv, 'UDARA', p[0], p[1], a0 * q, size=22, bg=ORANGE, pad=16)
    la = eo(prog(t, 7.59, 7.95)) * (1 - prog(t, 9.8, 10.1))
    if la > 0: p = S((-4.6, 0, zbot(-4.6) + 0.05)); label(cv, 'LAMBUNG BAJA', p[0], p[1], 280, 1200, a0 * la, dot=NAVY, sub='tipis, isinya kosong')
    ba = eo(prog(t, 10.05, 10.4))
    if ba > 0:
        cx, cy = 540, 400; tilt = lerp(0, -11, eo(prog(t, 10.5, 11.3))) + 1.5 * math.sin(t * 3) * (1 - prog(t, 11.3, 11.9))
        card(cv, skia.Rect(cx - 330, cy - 165, cx + 330, cy + 150), a0 * ba, rad=32)
        mono(cv, 'DIRATA-RATA', cx, cy - 125, 22, MUTED, a0 * ba, sp=4)
        cv.save(); cv.translate(cx, cy + 10); cv.rotate(tilt)
        cv.drawLine(-230, 0, 230, 0, P(col(INK, a0 * ba), stroke=8))
        for sx_, lab, c in ((-230, 'KAPAL', NAVY), (230, 'AIR SEBESAR KAPAL', '#4A6496')):
            cv.save(); cv.translate(sx_, 0); cv.rotate(-tilt)
            cv.drawLine(0, 0, 0, 30, P(col(INK, a0 * ba), stroke=3)); cv.drawRoundRect(skia.Rect(-82, 30, 82, 46), 8, 8, P(col(INK, a0 * ba)))
            if lab == 'KAPAL':
                hull = skia.Path(); hull.moveTo(-64, -8); hull.lineTo(64, -8); hull.lineTo(48, 26); hull.lineTo(-50, 26); hull.close()
                cv.drawPath(hull, P(col(NAVY, a0 * ba))); cv.drawRect(skia.Rect(-40, -34, 34, -8), P(col('#F6F2EC', a0 * ba))); cv.drawRect(skia.Rect(-30, -42, -16, -24), P(col(ORANGE, a0 * ba)))
                cv.drawRect(skia.Rect(-36, -26, 30, -18), P(col(GLASS, a0 * ba)))
            else:
                cv.drawRoundRect(skia.Rect(-66, -44, 66, 26), 10, 10, P(shader=lg(0, -44, 0, 26, [col('#7690BE', a0 * ba), col('#2A3F6B', a0 * ba)])))
                cv.drawLine(-60, -30, -20, -30, P(col(WHITE, 0.5 * a0 * ba), stroke=3))
            text_c(cv, lab, 0, 86, 22 if len(lab) > 6 else 24, c, a0 * ba)
            cv.restore()
        cv.restore()
        tri = skia.Path(); tri.moveTo(cx, cy + 10); tri.lineTo(cx - 24, cy + 70); tri.lineTo(cx + 24, cy + 70); tri.close(); cv.drawPath(tri, P(col(INK, a0 * ba)))
    ca = eo(prog(t, 11.4, 11.7))
    if ca > 0: chip(cv, 'KAPAL LEBIH RINGAN', 540, 1340, a0 * ca, size=30, bg=ORANGE); check(cv, 775, 1340, 22, prog(t, 11.5, 11.9), a0 * ca)

# ------------------------------------------------------------ C: peragaan Archimedes: model kapal masuk tangki penuh, air tumpah = berat kapal (14.158 - 21.131)
TX0, TX1, TY0, TY1, TZ1 = -7.0, 3.0, -3.0, 1.6, 4.6                       # tangki kaca (air sampai bibir)
BX0, BX1, BY0, BY1, BZ1 = 4.6, 7.6, -1.6, 1.4, 3.2                        # gelas ukur
def glass_box(cv, x0, x1, y0, y1, z0, z1, a, back=True):
    if back:
        for pts in ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)]):
            q = WORLD.path(pts); cv.drawPath(q, P(col(WHITE, 0.35 * a))); cv.drawPath(q, P(col('#9FB0CC', 0.7 * a), stroke=2))
        quad(cv, WORLD, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], '#E9EEF5', 0.6 * a)
    else:
        for pts in ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]):
            q = WORLD.path(pts); cv.drawPath(q, P(col(WHITE, 0.12 * a))); cv.drawPath(q, P(col('#9FB0CC', 0.9 * a), stroke=2.5))
        for (xx, yy) in ((x0 + 0.6, y1), (x1, y0 + 0.5)):
            p0, p1 = P3(xx, yy, z0 + 0.4), P3(xx + (0.5 if yy == y1 else 0), yy + (0 if yy == y1 else 0.5), z1 - 0.4)
            cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, 0.6 * a), stroke=5))
        rim = WORLD.path([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]); cv.drawPath(rim, P(col('#9FB0CC', a), stroke=3))
def water_box(cv, t, x0, x1, y0, y1, z0, z1, a):
    if z1 <= z0 + 0.01: return
    quad(cv, WORLD, [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], '#9DB2D6', 0.35 * a)
    for pts, dk in (([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], 0.0), ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], -0.1)):
        q = WORLD.path(pts); cv.drawPath(q, P(shader=lg(*P3(x0, y1, z1), *P3(x0, y1, z0), [col(tone('#8FA6CF', dk), 0.32 * a), col(tone('#4A6496', dk), 0.5 * a)])))
    ln = WORLD.path([(x0, y1, z1), (x1, y1, z1), (x1, y0, z1)], close=False); cv.drawPath(ln, P(col(WHITE, 0.8 * a), stroke=3))
def scale_bar(cv, cx, cy, lab, frac, c, a):
    card(cv, skia.Rect(cx - 130, cy - 150, cx + 130, cy + 110), a, rad=26)
    mono(cv, lab, cx, cy - 118, 20, MUTED, a, sp=3)
    r = skia.Rect(cx - 34, cy - 85, cx + 34, cy + 75); cv.drawRoundRect(r, 14, 14, P(col('#EEE6DA', a)))
    h = (r.height() - 8) * clamp(frac); cv.drawRoundRect(skia.Rect(r.left() + 4, r.bottom() - 4 - h, r.right() - 4, r.bottom() - 4), 10, 10, P(col(c, a)))
def gC(cv, t):
    a0 = eo(prog(t, 14.158, 14.55))
    zoom = lerp(0.98, 1.04, eio(prog(t, 14.158, 21.131))); fw = (0.0, -0.6, 3.4); f = P3(*fw); sx, sy = 540, 980
    low = eio(prog(t, 15.2, 16.9)); spill = eio(prog(t, 15.5, 17.2))
    mz = lerp(TZ1 + 3.4, TZ1, low) + 0.03 * math.sin(t * 2) * low       # garis air model kapal
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    box(cv, WORLD, -8.4, -4.4, -1.0, 17.2, 7.2, 1.0, '#E8DFD2', a0, top=0.18, left=0.02, right=-0.12)    # meja
    box(cv, WORLD, TX0 - 0.3, TY0 - 0.3, 0.0, TX1 - TX0 + 0.6, TY1 - TY0 + 0.6, 0.3, NAVY, a0, top=0.25)   # timbangan tangki
    box(cv, WORLD, BX0 - 0.3, BY0 - 0.3, 0.0, BX1 - BX0 + 0.6, BY1 - BY0 + 0.6, 0.3, NAVY, a0, top=0.25)   # timbangan gelas
    glass_box(cv, TX0, TX1, TY0, TY1, 0.3, TZ1 + 0.3, a0, back=True); glass_box(cv, BX0, BX1, BY0, BY1, 0.3, BZ1, a0, back=True)
    water_box(cv, t, BX0, BX1, BY0, BY1, 0.3, 0.3 + (BZ1 - 0.9) * spill, a0)
    k = 0.3; c = P3(-2.0, -0.7, mz)                                       # model kapal (skala 0,3) diturunkan tali derek
    hz = P3(-2.0, -0.7, mz + 1.6 * k * 3.0)
    if t < 17.0: cv.drawLine(hz[0], hz[1] - 600, hz[0], hz[1], P(col(NAVY2, a0), stroke=3)); cv.drawCircle(hz[0], hz[1], 8, P(col(ORANGE, a0), stroke=4))
    cv.save(); cv.translate(*c); cv.scale(k, k); o = P3(0, 0, 0); cv.translate(-o[0], -o[1])
    pose = Pose(dz=0.0); hull_whole(cv, pose, a0, 'bawah', t); hull_whole(cv, pose, a0, 'atas', t); superstructure(cv, pose, a0, cut=False, t=t)
    cv.restore()
    water_box(cv, t, TX0, TX1, TY0, TY1, 0.3, TZ1 + 0.05 * spill * (1 - spill) + 0.3, a0)
    if 15.5 < t < 17.6:                                                   # air tumpah lewat corong
        sp0 = P3(TX1, TY1 - 1.0, TZ1 + 0.3); sp1 = P3(BX0 + 0.8, BY1 - 1.2, 0.3 + (BZ1 - 0.9) * spill + 0.1)
        aa = a0 * bump(prog(t, 15.5, 17.6)) * 1.3
        pth = skia.Path(); pth.moveTo(*sp0); pth.quadTo(sp0[0] + 60, sp0[1] - 10, sp1[0], sp1[1])
        cv.drawPath(pth, P(col('#6A86B6', clamp(aa)), stroke=14)); cv.drawPath(pth, P(col(WHITE, 0.6 * clamp(aa)), stroke=3, effect=skia.DashPathEffect.Make([12, 10], -t * 80)))
    box(cv, WORLD, TX1, TY1 - 1.3, TZ1, 0.9, 0.6, 0.18, '#9FB0CC', a0, top=0.2)      # corong
    glass_box(cv, TX0, TX1, TY0, TY1, 0.3, TZ1 + 0.3, a0, back=False); glass_box(cv, BX0, BX1, BY0, BY1, 0.3, BZ1, a0, back=False)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    ua = eo(prog(t, 17.31, 17.7))
    if ua > 0:                                                            # air mendorong ke atas
        for kx in (-4.6, -3.3, -2.0, -0.7, 0.6):
            q = (t * 0.9 + kx * 0.2) % 1.0
            arrow(cv, S((kx, -0.5, TZ1 - 2.4 + 0.3 * q)), S((kx, -0.5, TZ1 - 0.8 + 0.3 * q)), ORANGE, a0 * ua * (0.7 + 0.3 * bump(q)), w=8, head=20)
        chip(cv, 'AIR MENDORONG KE ATAS', 540, 330, a0 * ua * (1 - prog(t, 19.2, 19.5)), size=26, bg=ORANGE)
    la = eo(prog(t, 15.2, 15.55)) * (1 - prog(t, 17.0, 17.3))
    if la > 0: chip(cv, 'KAPAL MENYINGKIRKAN AIR', 540, 330, a0 * la, size=26, bg=NAVY)
    sa = eo(prog(t, 15.6, 16.0))
    if sa > 0:
        p = S((BX0 + 1.5, BY1, BZ1 + 0.3)); text_c(cv, 'AIR TUMPAH', p[0], p[1] - 30, 26, NAVY, a0 * sa, halo=1.0)
    wa = eo(prog(t, 19.4, 19.75))
    if wa > 0:                                                            # dua batang sama tinggi
        scale_bar(cv, 330, 420, 'BERAT KAPAL', 0.8, NAVY, a0 * wa); scale_bar(cv, 750, 420, 'AIR TUMPAH', 0.8 * eo(prog(t, 19.5, 20.1)), '#4A6496', a0 * wa)
        text_c(cv, '=', 540, 410, 80, ORANGE, a0 * wa * eo(prog(t, 20.0, 20.3)))
        chip(cv, 'SAMA KUAT', 540, 1345, a0 * eo(prog(t, 20.0, 20.3)), size=30, bg=INK); check(cv, 700, 1345, 22, prog(t, 20.1, 20.5), a0 * wa)

# ------------------------------------------------------------ D: sekat kedap air; satu ruang bocor, kapal tetap mengapung (21.131 - 26.98)
FLOOD_I = 3
def gD(cv, t):
    a0 = eo(prog(t, 21.131, 21.5))
    zoom = lerp(1.16, 1.24, eio(prog(t, 21.131, 26.98))); fw = (0.8, -0.8, -0.4); f = P3(*fw); sx, sy = 540, 990
    bg = eo(prog(t, 21.95, 22.3)) * (1 - 0.5 * prog(t, 24.4, 24.8)) + 0.5 * eo(prog(t, 25.34, 25.6))
    fl = eio(prog(t, 24.6, 25.5)); trim = -0.012 * fl
    alarm = (0.5 + 0.5 * math.sin(t * 14)) * prog(t, 24.6, 24.8) * (1 - prog(t, 25.3, 25.6))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    world(cv, t, a0, Pose(dz=0.04 * math.sin(t * 2) - 0.12 * fl, trim=trim), 1.0, SEA_C, air_glow=0.5 * (1 - fl * 0.2), bulk_glow=bg, flood=(FLOOD_I, fl))
    cv.restore()
    if alarm > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.12 * alarm)))
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 21.95, 22.3)) * (1 - prog(t, 24.3, 24.6))
    if la > 0: p = S((BULK[1], 0, -0.9)); label(cv, 'SEKAT KEDAP AIR', p[0], p[1], 300, 520, a0 * la, sub='membagi lambung jadi ruang-ruang')
    ba = prog(t, 24.6, 26.98)
    if ba > 0:
        x0, x1, _ = COMP[FLOOD_I]; p = S(((x0 + x1) / 2, 0, zbot(3.0) + 0.1))
        for k in range(7):
            ang = -math.pi / 2 + (k - 3) * 0.25; L = 40 + 25 * math.sin(t * 20 + k)
            cv.drawLine(p[0], p[1], p[0] + math.cos(ang) * L, p[1] + math.sin(ang) * L, P(col(WHITE, 0.85 * a0 * (1 - prog(t, 25.6, 26.2))), stroke=5))
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
    hx0, hx1, hy0, hy1 = 136, 944, 440, 1124                              # lambung baja berpaku keling (tampak samping dekat)
    cv.drawRect(skia.Rect(hx0, hy0, hx1, hy1), P(shader=lg(0, hy0, 0, hy1, [col('#5A4634', a), col('#3E2E22', a)])))
    for k in range(6):
        yy = hy0 + 20 + k * 110; cv.drawLine(hx0, yy, hx1, yy, ink(0.5, 2))
        for j in range(26): cv.drawCircle(hx0 + 20 + j * 32, yy + 10, 3.2, P(col('#8C7258', a)))
    for j in range(6): cv.drawLine(hx0 + 60 + j * 150, hy0, hx0 + 60 + j * 150, hy1, ink(0.35, 2))
    cx, cy = 560, 720                                                     # tanda Plimsoll (cat putih)
    cv.drawCircle(cx, cy, 72, P(col('#F6EEDC', a), stroke=9)); cv.drawLine(cx - 115, cy, cx + 115, cy, P(col('#F6EEDC', a), stroke=9))
    f_ = font(XB, 42); cv.drawString('L', cx - 126, cy - 30, f_, P(col('#F6EEDC', a))); cv.drawString('R', cx + 96, cy - 30, f_, P(col('#F6EEDC', a)))
    cv.drawLine(cx + 195, cy - 115, cx + 195, cy + 60, P(col('#F6EEDC', a), stroke=7))
    for k, lab in enumerate(('TF', 'F', 'T', 'S', 'W')):
        yy = cy - 105 + k * 40; cv.drawLine(cx + 195, yy, cx + 275, yy, P(col('#F6EEDC', a), stroke=6)); cv.drawString(lab, cx + 285, yy + 12, font(XB, 28), P(col('#F6EEDC', a)))
    wy = lerp(hy0 + 60, hy1, 1 - lvl)
    cv.drawRect(skia.Rect(r.left(), wy, r.right(), r.bottom()), P(shader=lg(0, wy, 0, r.bottom(), [col('#9C8A6E', 0.72 * a), col('#6E5E48', 0.85 * a)])))
    for k in range(3):
        p = skia.Path(); yy = wy + k * 26; p.moveTo(r.left(), yy)
        for i in range(30): x = r.left() + i * 32; p.quadTo(x + 8, yy - 7 + 2 * math.sin(t * 3 + i + k), x + 16, yy); p.quadTo(x + 24, yy + 7, x + 32, yy)
        cv.drawPath(p, P(col('#F6EEDC', (0.9 if k == 0 else 0.35) * a), stroke=4 if k == 0 else 2))
    mx, my = 805, 360                                                     # potret medali Samuel Plimsoll
    cv.drawOval(skia.Rect(mx - 80, my - 94, mx + 80, my + 94), P(col('#C9A35A', a))); cv.drawOval(skia.Rect(mx - 72, my - 86, mx + 72, my + 86), P(col('#FBF3E2', a)))
    cv.save(); cv.clipPath(poly([(mx + 70 * math.cos(math.tau * i / 40), my + 84 * math.sin(math.tau * i / 40)) for i in range(40)]), doAntiAlias=True)
    cv.drawRoundRect(skia.Rect(mx - 62, my + 22, mx + 62, my + 122), 30, 30, P(col('#3E2E22', a)))
    cv.drawCircle(mx, my - 18, 34, P(col('#E8C9A0', a))); cv.drawCircle(mx, my - 18, 34, ink(1, 2.5))
    beard = skia.Path(); beard.moveTo(mx - 32, my - 14); beard.quadTo(mx, my + 54, mx + 32, my - 14); beard.close(); cv.drawPath(beard, P(col('#8A8A8A', a)))
    cv.drawArc(skia.Rect(mx - 34, my - 56, mx + 34, my - 6), 180, 180, False, P(col('#6B5A4A', a)))
    cv.restore()
    vg = skia.Rect(r.left(), r.top(), r.right(), r.bottom())               # vinyet
    cv.drawRect(vg, P(shader=rg(540, 700, 620, [col('#000000', 0), col('#3E2E22', 0.28 * a)], [0.6, 1.0])))
    cv.restore()
def gE(cv, t):
    a0 = eo(prog(t, 26.98, 27.4))
    lvl = lerp(0.62, 0.5, eo(prog(t, 30.6, 31.2)))
    over = eo(prog(t, 31.2, 31.5)) * (1 - eio(prog(t, 31.9, 32.3)))
    lvl = lerp(lvl, 0.78, over)
    zz = 1.14 + 0.03 * eio(prog(t, 26.98, 34.068))
    cv.save(); cv.translate(540, 770); cv.scale(zz, zz); cv.translate(-540, -700)
    plimsoll_card(cv, t, a0, lvl)
    cv.restore()
    S = lambda x, y: (540 + (x - 540) * zz, 770 + (y - 700) * zz)
    na = eo(prog(t, 29.01, 29.4))
    if na > 0: p = S(805, 455); label(cv, 'SAMUEL PLIMSOLL', p[0], p[1], 760, 610, a0 * na, size=26, sub='anggota parlemen Inggris')
    ga = eo(prog(t, 30.51, 30.9))
    if ga > 0: p = S(560, 720); label(cv, 'GARIS MUAT', p[0], p[1], 300, 1240, a0 * ga, size=26, sub='tanda di lambung kapal')
    if over > 0.05: chip(cv, 'KELEBIHAN MUATAN', 540, 1340, a0 * over, size=28, bg=RED)
    sa = eo(prog(t, 32.2, 32.5))
    if sa > 0: chip(cv, 'BATAS AMAN', 540, 1340, a0 * sa, size=30, bg=ORANGE); check(cv, 690, 1340, 22, prog(t, 32.3, 32.7), a0 * sa)

# ------------------------------------------------------------ F: Merak - Bakauheni, puluhan feri bolak-balik siang dan malam (34.068 - 38.692)
def land(cv, pts, a, h=1.0):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
        cv.drawPath(poly([P3(xa, ya, h), P3(xb, yb, h), P3(xb, yb, 0), P3(xa, ya, 0)]), P(col('#C9B391', a)))
    top = [P3(x, y, h) for x, y in pts]; cv.drawPath(poly(top), P(shader=lg(*P3(pts[0][0], pts[0][1], h), *P3(pts[2][0], pts[2][1], h), [col('#F0E4CF', a), col('#E2D2B6', a)])))
    cv.drawPath(poly(top), P(col('#B79D78', a), stroke=2))
def port(cv, x, y, a, night, t, sd=1):
    box(cv, WORLD, x - 1.0, y - 1.8, 0, 2.0, 3.6, 1.0, '#D6CDBF', a, top=0.25)
    box(cv, WORLD, x - 0.6, y - 0.9 * sd, 1.0, 1.2, 1.0, 1.2, '#F6F2EC', a, top=0.2)
    box(cv, WORLD, x + 0.3 * sd, y + 1.1 * sd, 1.0, 0.25, 0.25, 2.6, NAVY, a)                           # derek
    p0, p1 = P3(x + 0.42 * sd, y + 1.22 * sd, 3.6), P3(x - 1.6 * sd, y + 1.22 * sd, 3.6); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY, a), stroke=4))
    lx, ly = x - 0.6 * sd, y - 1.4 * sd                                                                  # mercusuar
    box(cv, WORLD, lx, ly, 1.0, 0.35, 0.35, 2.2, '#F6F2EC', a); box(cv, WORLD, lx, ly, 3.2, 0.35, 0.35, 0.3, ORANGE, a)
    if night > 0:
        p = P3(lx + 0.17, ly + 0.17, 3.35); ang = t * 2.5
        beam = skia.Path(); beam.moveTo(*p); beam.lineTo(p[0] + 260 * math.cos(ang - 0.12), p[1] + 130 * math.sin(ang - 0.12)); beam.lineTo(p[0] + 260 * math.cos(ang + 0.12), p[1] + 130 * math.sin(ang + 0.12)); beam.close()
        cv.drawPath(beam, P(col('#FFE3A8', 0.35 * night * a), blur=8)); cv.drawCircle(p[0], p[1], 12, P(col('#FFE3A8', night * a), blur=5))
def mini_ferry(cv, t, x, y, d, a, lights):
    L = 3.0
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1.0; p0, p1 = P3(x - d * (L / 2 + 0.5 + ph * 3), y - 0.5 - ph * 0.8, 0.02), P3(x - d * (L / 2 + 0.5 + ph * 3), y + 0.5 + ph * 0.8, 0.02)
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, 0.5 * (1 - ph) * a), stroke=2.5))
    box(cv, WORLD, x - L / 2, y - 0.55, 0, L, 1.1, 0.45, NAVY, a, top=0.3)
    box(cv, WORLD, x - L * 0.32, y - 0.42, 0.45, L * 0.6, 0.84, 0.4, '#F6F2EC', a, top=0.2)
    quad(cv, WORLD, [(x - L * 0.3, y + 0.43, 0.6), (x + L * 0.26, y + 0.43, 0.6), (x + L * 0.26, y + 0.43, 0.75), (x - L * 0.3, y + 0.43, 0.75)], '#FFC98A' if lights > 0.5 else GLASS, a)
    box(cv, WORLD, x - L * 0.22, y - 0.15, 0.85, 0.32, 0.3, 0.4, ORANGE, a)
    if lights > 0: p = P3(x, y + 0.45, 0.7); cv.drawCircle(p[0], p[1], 18, P(col('#FFC98A', 0.5 * lights * a), blur=10))
def gF(cv, t):
    a0 = eo(prog(t, 34.068, 34.5)); night = eio(prog(t, 36.6, 37.6))
    zoom = lerp(0.84, 0.92, eio(prog(t, 34.068, 38.692))); fw = (0.2, 1.0, 0.0); f = P3(*fw); sx, sy = 540, 840
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    x0, x1, y0, y1 = -15.0, 15.0, -12.0, 13.0
    sea_bed(cv, t, x0, x1, y0, y1, a0); sea_top(cv, t, x0, x1, y0, y1, a0)
    land(cv, [(-15, 6.5), (-6.5, 6.5), (-4, 9), (-5, 13), (-15, 13)], a0)
    land(cv, [(5.5, -12), (15, -12), (15, -3.8), (7, -3.8), (4.5, -7.5)], a0)
    port(cv, -5.6, 7.4, a0, night, t, sd=1); port(cv, 6.2, -5.4, a0, night, t, sd=-1)
    for k in range(3):
        p0, p1 = P3(-4.2 + (k - 1) * 1.4, 6.0 + (k - 1) * 1.8, 0.02), P3(4.8 + (k - 1) * 1.4, -4.2 + (k - 1) * 1.8, 0.02)
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, 0.4 * a0), stroke=3, effect=skia.DashPathEffect.Make([14, 12], -t * 30)))
    fs = []
    for k in range(6):
        ph = (t * 0.05 + k / 6) % 1.0; d = 1 if k % 2 else -1; u = ph if d > 0 else 1 - ph
        x = lerp(-3.6, 4.4, u) + (k % 3 - 1) * 1.4; y = lerp(5.6, -3.8, u) + (k % 3 - 1) * 1.8
        fs.append((x + y, x, y, d))
    for _, x, y, d in sorted(fs): mini_ferry(cv, t, x, y, d, a0, night)
    cv.restore()
    if night > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(shader=lg(0, 0, 0, 1920, [col(NAVY2, 0.42 * night), col(NAVY2, 0.15 * night)])))
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    for (wx, wy_, nm, lx, ly, t0) in ((-9.0, 9.5, 'MERAK', 270, 1180, 34.2), (9.5, -8.0, 'BAKAUHENI', 800, 420, 34.9)):
        q = eo(prog(t, t0, t0 + 0.35))
        if q > 0: p = S((wx, wy_, 1.0)); label(cv, nm, p[0], p[1], lx, ly, a0 * q, size=28, sub='Banten' if nm == 'MERAK' else 'Lampung')
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
    ev = [(0.0, 'whoosh'), (0.35, 'buzzer'), (0.45, 'crack'), (0.5, 'chop'), (0.7, 'fizz'), (0.85, 'stamp'), (0.9, 'splash'), (1.0, 'whoosh'), (1.85, 'clunk'), (1.87, 'rumble'),
          (2.05, 'rewind'), (2.95, 'shine'), (3.2, 'zap'), (3.3, 'swish'), (3.7, 'zap'), (3.75, 'pop'), (3.9, 'ding'), (4.85, 'pop'), (5.0, 'pop'), (5.15, 'pop'),
          (6.72, 'whoosh'), (7.59, 'pop'), (8.88, 'shine'), (8.95, 'pop'), (9.1, 'pop'), (9.2, 'pop'), (10.05, 'card'), (10.5, 'swish'), (11.3, 'clunk'), (11.4, 'ding'),
          (14.158, 'whoosh'), (15.2, 'swish'), (15.5, 'pour'), (16.3, 'pour'), (16.9, 'plop'), (17.31, 'rise'), (17.5, 'pop'), (19.4, 'card'), (19.6, 'rise'), (20.0, 'stamp'), (20.1, 'ding'),
          (21.131, 'whoosh'), (21.95, 'zap'), (22.0, 'pop'), (24.6, 'crack'), (24.65, 'buzzer'), (24.7, 'pour'), (25.34, 'ding'), (25.45, 'stamp'),
          (26.98, 'whoosh'), (27.0, 'card'), (29.01, 'pop'), (30.51, 'pop'), (30.6, 'swish'), (31.2, 'buzzer'), (32.2, 'ding'), (32.3, 'stamp'),
          (34.068, 'whoosh'), (34.2, 'pop'), (34.9, 'pop'), (35.7, 'pop'), (35.75, 'ding_soft'), (36.6, 'swish'), (37.0, 'pop'),
          (38.692, 'whoosh'), (38.8, 'shine'), (39.1, 'pop'), (39.35, 'pop'), (39.6, 'pop'), (39.85, 'pop'), (40.92, 'pop'),
          (42.247, 'whoosh'), (42.4, 'boing'), (42.75, 'shine'), (43.0, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
