#!/usr/bin/env python3
"""Bongkar Benda #08: 'Gedung pencakar langit, kok nggak roboh kena gempa?'
Diorama kota isometrik: gedung tinggi (lantai bertumpuk, kaca), tanah yang dibelah (lapisan lunak/keras, tiang pondasi), gempa (tanah bergetar, gelombang).
Hook: gempa; kalau gedungnya kaku, retak di bawah lalu roboh -> REWIND -> gedung bergoyang lentur, bola peredam berayun. Alasan 1: pondasi sampai lapisan keras.
Alasan 2: dirancang lentur (bergoyang, bukan patah). Alasan 3: peredam: Taipei 101, bola baja 660 ton berayun melawan goyangan.
Sejarah: Kiyoshi Muto, Gedung Kasumigaseki 1968. Penutup: Padang, gedung di atas bantalan karet (base isolation). Sumber: content/EP08_gedung.md
python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, YELLOW, RED, WHITE, text_c, mono, card, chip, label, check, logo_mark)
from iso import Iso, tone, quad, box, shadow, poly
import geo3d as g
from geo3d import add, sub, mul, dot, nrm, p3, obox, ocyl, face

bb.DUR = 46.467
bb.TITLE = ('Gedung tinggi,', 'kok nggak roboh?'); bb.TITLE_OUT = 4.4
bb.GROUPS = [(0.0, 7.088, 'A'), (7.088, 11.998, 'B'), (11.998, 17.631, 'C'), (17.631, 25.796, 'D'), (25.796, 33.27, 'E'),
             (33.27, 37.976, 'F'), (37.976, 41.267, 'G'), (41.267, 46.467, 'J')]
bb.PHRASES = [(0.15, 'Tanah [berguncang],'), (1.46, 'gedung setinggi [ratusan meter]'), (3.38, 'ini ikut [bergoyang].'), (4.46, 'Kok nggak [roboh]?'), (5.65, 'Ini [alasannya].'),
              (7.088, '[Pertama],'), (7.93, 'pondasinya [tertanam dalam],'), (9.71, 'sampai ke [lapisan tanah yang keras].'),
              (11.998, '[Kedua],'), (12.72, 'gedungnya dirancang [lentur].'), (14.4, 'Saat [gempa],'), (15.35, 'ia [bergoyang],'), (16.4, 'bukan [patah].'),
              (17.631, '[Ketiga],'), (18.42, 'ada [peredam].'), (19.49, 'Di [Taipei 101],'), (20.62, 'bola baja seberat [660 ton]'), (23.32, 'berayun [melawan goyangan] gedung.'),
              (25.796, 'Ide gedung lentur dipelopori [Kiyoshi Muto].'), (28.5, 'Tahun [1968],'), (30.24, 'dia membangun [gedung pencakar langit]'), (31.95, 'pertama di [Jepang].'),
              (33.27, 'Di [Padang],'), (34.17, 'bahkan ada gedung yang berdiri'), (35.8, 'di atas [bantalan karet] peredam gempa.'),
              (37.976, 'Benda apa yang mau kamu [bongkar] berikutnya?'), (40.01, 'Tulis di [komentar]!'),
              (41.267, 'Follow [Bongkar Benda],'), (42.65, 'biar makin paham [cara kerja benda] di sekitarmu.')]

WORLD = Iso(0, 0, 50); g.ISO = WORLD
NAVY, NAVY2 = '#2A3F6B', '#1A2A4C'
GLASS, GLASS_HI = '#2E4672', '#6F88B8'
CONC, CONC_E = '#EFE7DB', '#C5B8A6'
SOIL = [(0.0, -1.0, '#E4C6A2'), (-1.0, -3.0, '#D6AE84'), (-3.0, -5.2, '#C79B71'), (-5.2, -40, '#8C6A4A')]   # lapisan terbawah = tanah keras
HW, FH, NF = 1.8, 0.5, 36
H = FH * NF
def P3(x, y, z): return WORLD.p(x, y, z)
def cam(cv, wx, wy, zoom, sx=540, sy=760): cv.translate(sx, sy); cv.scale(zoom, zoom); cv.translate(-wx, -wy)
def scr(p, f, zoom, sx, sy): return (sx + (p[0] - f[0]) * zoom, sy + (p[1] - f[1]) * zoom)
def wav(u, k): return 0.07 * math.sin(1.25 * u + 1.7 * k) + 0.045 * math.sin(2.9 * u + 0.6 * k)
def arrow(cv, p0, p1, c, a, w=9, head=20):
    if a <= 0: return
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); hx, hy = p1[0] - math.cos(ang) * head * 0.8, p1[1] - math.sin(ang) * head * 0.8
    pth = skia.Path(); pth.moveTo(*p1)
    pth.lineTo(p1[0] - head * math.cos(ang - 0.45), p1[1] - head * math.sin(ang - 0.45)); pth.lineTo(p1[0] - head * math.cos(ang + 0.45), p1[1] - head * math.sin(ang + 0.45)); pth.close()
    cv.drawLine(p0[0], p0[1], hx, hy, P(col(WHITE, a), stroke=w + 7)); cv.drawPath(pth, P(col(WHITE, a), stroke=7))
    cv.drawLine(p0[0], p0[1], hx, hy, P(col(c, a), stroke=w)); cv.drawPath(pth, P(col(c, a)))
def rewind_fx(cv, t, t0, t1):
    rw = prog(t, t0, t1 + 0.05)
    if not (0 < rw < 1): return
    ra = clamp(bump(rw) * 1.3)
    cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(bb.BG0, 0.12 * ra)))
    for k in range(14):
        yy = (k * 151 + t * 2400) % 1920; cv.drawRect(skia.Rect(0, yy, 1080, yy + 5), P(col(WHITE, 0.35 * ra)))
    r = skia.Rect(400, 520, 680, 600); cv.drawRoundRect(r, 40, 40, P(col(INK, ra)))
    for k in range(2):
        x0_ = 470 + k * 44; tri = skia.Path(); tri.moveTo(x0_, 560); tri.lineTo(x0_ + 38, 536); tri.lineTo(x0_ + 38, 584); tri.close(); cv.drawPath(tri, P(col(WHITE, ra)))
    f_ = font(MONO, 26); cv.drawString('ULANG', 570, bl(f_, 560), f_, P(col(WHITE, ra)))
def seismo(cv, t, a, amp, x=870, y=330):
    """kartu seismograf kecil: garis getaran bergerak"""
    if a <= 0: return
    r = skia.Rect(x - 140, y - 64, x + 140, y + 64); card(cv, r, a, rad=24)
    mono(cv, 'GEMPA', x - 108, y - 40, 18, MUTED, a, sp=3, align=0)
    pts = []
    for i in range(80):
        xx = r.left() + 18 + i * (r.width() - 36) / 79; tt = t * 6 - i * 0.18
        yy = y + 14 + amp * 34 * math.sin(tt * 3.1) * math.sin(tt * 0.9 + 1) * (0.6 + 0.4 * math.sin(i * 0.7))
        pts.append((xx, yy))
    cv.drawPath(poly(pts, False), P(col(RED if amp > 0.5 else ORANGE, a), stroke=3))

# ------------------------------------------------------------ tanah (dibelah), kota, gedung
def ground_block(cv, t, a, x0=-12, x1=12, y0=-10, y1=10, zb=-8.0, gx=0.0, piles=False, pile_glow=0.0, hard_glow=0.0):
    """balok tanah: muka kiri = bidang y = y1, muka kanan = bidang x = x1 (berlapis); gx = geser gempa"""
    def fp(plane, pv, u, z): return P3(u + gx, pv, z) if plane == 'y' else P3(pv + gx, u, z)
    for plane, pv, u0, u1, dk in (('y', y1, x0, x1, 0.0), ('x', x1, y0, y1, -0.1)):
        face_ = poly([fp(plane, pv, u0, 0), fp(plane, pv, u1, 0), fp(plane, pv, u1, zb), fp(plane, pv, u0, zb)])
        cv.save(); cv.clipPath(face_, doAntiAlias=True)
        for k, (z0, z1, c) in enumerate(SOIL):
            us = [lerp(u0, u1, i / 30) for i in range(31)]
            top = [fp(plane, pv, u, z0 + (wav(u, k) if k else 0)) for u in us]; bot = [fp(plane, pv, u, max(z1, zb - 1) + wav(u, k + 1)) for u in us[::-1]]
            cc = c if k < 3 else mixc(c, ORANGE, 0.35 * hard_glow)
            cv.drawPath(poly(top + bot), P(shader=lg(*fp(plane, pv, u0, z0), *fp(plane, pv, u0, max(z1, zb)), [col(tone(cc, dk + 0.05), a), col(tone(cc, dk - 0.07), a)])))
            if k: cv.drawPath(poly(top, False), P(col(tone(c, -0.35), 0.4 * a), stroke=1.4))
        if piles and plane == 'y':                                         # tiang pondasi terlihat di muka potong (di bawah gedung)
            for xx in (-1.4, -0.47, 0.47, 1.4):
                q = poly([fp('y', pv, xx - 0.22, -0.6), fp('y', pv, xx + 0.22, -0.6), fp('y', pv, xx + 0.22, -6.4), fp('y', pv, xx - 0.22, -6.4)])
                cv.drawPath(q, P(shader=lg(*fp('y', pv, xx - 0.22, -2), *fp('y', pv, xx + 0.22, -2), [col('#B9AE9F', a), col('#8E8476', a)])))
                if pile_glow > 0: cv.drawPath(q, P(col(ORANGE, 0.75 * pile_glow * a)))
            q = poly([fp('y', pv, -2.2, 0), fp('y', pv, 2.2, 0), fp('y', pv, 2.2, -0.7), fp('y', pv, -2.2, -0.7)]); cv.drawPath(q, P(col('#D9D0C2', a))); cv.drawPath(q, P(col(CONC_E, a), stroke=2))
        cv.restore(); cv.drawPath(face_, P(col('#6B5A4A', 0.5 * a), stroke=1.5))
    quad(cv, WORLD, [(x0 + gx, y0, 0), (x1 + gx, y0, 0), (x1 + gx, y1, 0), (x0 + gx, y1, 0)], '#EDE4D6', a, grad=((x0 + gx, y1, 0), (x1 + gx, y0, 0), '#F2EADD', '#E3D7C5'))
    for k in range(-5, 6):                                                # jalan & ubin
        p0, p1 = P3(x0 + gx, k * 2.0, 0.002), P3(x1 + gx, k * 2.0, 0.002); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#D9CCBA', 0.5 * a), stroke=1.2))
    quad(cv, WORLD, [(x0 + gx, 4.0, 0.003), (x1 + gx, 4.0, 0.003), (x1 + gx, 6.2, 0.003), (x0 + gx, 6.2, 0.003)], '#4A5368', a)
    x = x0 + 0.5
    while x < x1 - 1:
        quad(cv, WORLD, [(x + gx, 5.05, 0.004), (x + 1.0 + gx, 5.05, 0.004), (x + 1.0 + gx, 5.15, 0.004), (x + gx, 5.15, 0.004)], '#F2EEE8', 0.85 * a); x += 2.0
def small_buildings(cv, t, a, gx=0.0, jit=0.0):
    rnd = random.Random(4)
    for (x, y, w, d, h, c) in ((-9.5, -6.5, 3.0, 2.6, 5.5, '#F1E6D8'), (-5.8, -8.2, 2.6, 2.4, 7.5, '#FAF6F0'), (4.6, -8.5, 2.8, 2.6, 6.2, '#EBDDCB'), (8.2, -6.8, 2.6, 2.6, 4.8, '#F5ECE1'),
                               (-10.2, 0.8, 2.6, 2.6, 3.6, '#F5ECE1'), (8.6, 0.6, 2.6, 2.4, 3.2, '#F1E6D8')):
        jx = jit * 0.15 * math.sin(t * 22 + x)
        box(cv, WORLD, x + gx + jx, y, 0, w, d, h, c, a, top=0.3, left=0.02, right=-0.14)
        for row in range(int((h - 0.5) / 0.7)):
            z = 0.55 + row * 0.7
            for cc in range(int((w - 0.3) / 0.55)):
                xx = x + 0.3 + cc * 0.55 + gx + jx; on = rnd.random() < 0.3
                quad(cv, WORLD, [(xx, y + d, z), (xx + 0.3, y + d, z), (xx + 0.3, y + d, z + 0.42), (xx, y + d, z + 0.42)], '#FFC98A' if on else NAVY, 0.85 * a)
    for (x, y) in ((-6.5, 2.8), (-3.6, 3.2), (3.8, 3.0), (6.8, 2.6), (-8.0, -2.0), (6.6, -3.2)):
        p = P3(x + gx, y, 1.6); box(cv, WORLD, x - 0.1 + gx, y - 0.1, 0, 0.2, 0.2, 0.9, '#8C6A4A', a, top=0.2)
        cv.drawCircle(p[0], p[1], 40, P(shader=rg(p[0] - 12, p[1] - 15, 60, [col('#F4C27A', a), col(ORANGE_D, a)])))

def bend(z, sway): return sway * (z / H) ** 1.6
def tower(cv, t, a, sway=0.0, gx=0.0, rot=0.0, crack=0.0, cut=0.0, ball=None, glow_core=0.0, glow_frame=0.0, tint=0.0, top_only=False):
    """gedung tinggi: lantai bertumpuk (geser 'sway' membentuk lengkung), rot = roboh kaku di tepi kanan bawah; cut = separuh depan dibuang"""
    if a <= 0: return
    c_, s_ = math.cos(rot), math.sin(rot); xe = HW
    def T(x, y, z):
        xr, zr = x - xe, z
        return (xe + xr * c_ + zr * s_ + gx, y, -xr * s_ + zr * c_)
    u, v, w = (c_, 0.0, -s_), (0.0, 1.0, 0.0), (s_, 0.0, c_)
    body_c = mixc(CONC, '#F2B5A0', tint)
    i0 = 0 if not top_only else NF - 20
    for i in range(i0, NF):
        z0 = i * FH; dx = bend(z0 + FH / 2, sway)
        if cut <= 0.01:
            cc = T(dx, 0, z0 + FH / 2)
            obox(cv, cc, u, v, w, HW, HW, FH / 2, body_c, a, cols={'w': '#E6DFD3'})
            for (axis, fn) in (('v', lambda a_, b_: T(dx + a_, HW + 0.005, z0 + b_)), ('u', lambda a_, b_: T(dx + HW + 0.005, a_, z0 + b_))):
                n_ = v if axis == 'v' else u
                if dot(n_, (1, 1, 1)) <= 0: continue
                q = [fn(-HW + 0.08, 0.12), fn(HW - 0.08, 0.12), fn(HW - 0.08, FH - 0.04), fn(-HW + 0.08, FH - 0.04)]
                pth = poly([p3(p) for p in q]); gl = lg(*p3(q[3]), *p3(q[0]), [col(tone(GLASS_HI, 0.0 if axis == 'v' else -0.15), a), col(tone(GLASS, 0.0 if axis == 'v' else -0.2), a)])
                cv.drawPath(pth, P(shader=gl))
                for k in range(1, 6):
                    m0, m1 = p3(fn(-HW + k * 0.6, 0.12)), p3(fn(-HW + k * 0.6, FH - 0.04)); cv.drawLine(m0[0], m0[1], m1[0], m1[1], P(col(CONC, 0.7 * a), stroke=1.2))
                if i % 3 == 0:
                    s0, s1 = p3(fn(-HW + 0.3, 0.2)), p3(fn(-HW + 1.2, FH - 0.1)); cv.drawLine(s0[0], s0[1], s1[0], s1[1], P(col(WHITE, 0.18 * a), stroke=6))
        else:
            ac = a
            q = [T(dx - HW, -HW + 0.01, z0), T(dx + HW, -HW + 0.01, z0), T(dx + HW, -HW + 0.01, z0 + FH), T(dx - HW, -HW + 0.01, z0 + FH)]   # dinding belakang (dari dalam)
            face(cv, q, (0, 1, 0), '#E9E2D7', ac)
            qg = [T(dx - HW + 0.1, -HW + 0.02, z0 + 0.14), T(dx + HW - 0.1, -HW + 0.02, z0 + 0.14), T(dx + HW - 0.1, -HW + 0.02, z0 + FH - 0.05), T(dx - HW + 0.1, -HW + 0.02, z0 + FH - 0.05)]
            cv.drawPath(poly([p3(p) for p in qg]), P(col('#9FB0CC', 0.75 * ac)))
            obox(cv, T(dx + HW - 0.05, -HW / 2, z0 + FH / 2), u, v, w, 0.05, HW / 2, FH / 2, body_c, ac)        # sisi kanan separuh belakang
            open_ = ball is not None and i >= NF - 6
            if not (open_ and i > NF - 6): obox(cv, T(dx, -HW / 2, z0 + 0.03), u, v, w, HW, HW / 2, 0.03, '#D6CDBF', ac)   # pelat lantai
            if not open_: obox(cv, T(dx, -0.3, z0 + FH / 2), u, v, w, 0.55, 0.3, FH / 2, mixc('#CFC6B8', ORANGE, glow_core), ac)    # inti beton
            for xc in (-HW + 0.15, HW - 0.15):                                                                  # kolom di bidang potong
                cc = T(dx + xc, -0.08, z0 + FH / 2); obox(cv, cc, u, v, w, 0.1, 0.08, FH / 2, mixc(NAVY, ORANGE, glow_frame), ac)
            e0, e1 = p3(T(dx - HW, 0.0, z0 + 0.03)), p3(T(dx + HW, 0.0, z0 + 0.03)); cv.drawLine(e0[0], e0[1], e1[0], e1[1], P(col(mixc(NAVY2, ORANGE, glow_frame), ac), stroke=5))
    zt = NF * FH; dx = bend(zt, sway)                                          # atap: mahkota + antena
    obox(cv, T(dx, 0 if cut <= 0.01 else -HW / 2, zt + 0.2), u, v, w, HW - 0.2, HW - 0.2 if cut <= 0.01 else HW / 2 - 0.1, 0.2, NAVY, a)
    p0, p1 = p3(T(dx, 0, zt + 0.4)), p3(T(dx + 0.05, 0, zt + 2.2)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=4))
    cv.drawCircle(p1[0], p1[1], 5, P(col(RED if int(t * 2) % 2 else ORANGE, a)))
    if cut > 0.01 and ball is not None:                                        # bola peredam di ruang lantai atas (digambar terakhir)
        ac = a; bx, br = ball; zb_ = (NF - 5) * FH + 0.75; dxb = bend(zb_, sway)
        bc = T(dxb + bx, -0.3, zb_); top_ = T(bend(NF * FH, sway), -0.3, NF * FH)
        for dy in (-0.3, 0.3):
            p0, p1 = p3(add(top_, (0, dy, 0))), p3(add(bc, (0, dy * 0.5, br * 0.7))); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, ac), stroke=3))
        for sd in (-1, 1):                                                     # peredam hidrolik ke lantai
            p0, p1 = p3(T(dxb + sd * 1.55, -0.3, zb_ - 0.55)), p3(bc)
            cv.drawLine(p0[0], p0[1], lerp(p0[0], p1[0], 0.55), lerp(p0[1], p1[1], 0.55), P(col(ORANGE, ac), stroke=9))
            cv.drawLine(lerp(p0[0], p1[0], 0.45), lerp(p0[1], p1[1], 0.45), p1[0], p1[1], P(col('#C9CED8', ac), stroke=4))
        pc = p3(bc); R = br * 50
        cv.drawCircle(pc[0], pc[1] + R * 0.3, R, P(col(NAVY2, 0.25 * ac), blur=10))
        cv.drawCircle(pc[0], pc[1], R, P(shader=rg(pc[0] - R * 0.35, pc[1] - R * 0.4, R * 1.5, [col('#F6F2EC', ac), col('#C9A35A', ac), col('#6B5A3A', ac)], [0, 0.45, 1])))
        cv.drawCircle(pc[0] - R * 0.35, pc[1] - R * 0.35, R * 0.18, P(col(WHITE, 0.7 * ac)))
    if crack > 0:                                                              # retak di lantai bawah
        for k, (x0, z0) in enumerate(((-1.0, 0.3), (0.2, 0.9), (1.1, 0.2))):
            rnd = random.Random(60 + k); pts = [T(x0, HW + 0.01, z0)]; zz = z0
            for _ in range(5):
                zz += rnd.uniform(0.25, 0.5); pts.append(T(x0 + rnd.uniform(-0.4, 0.4), HW + 0.01, zz))
            pth = poly([p3(p) for p in pts], False); m = skia.PathMeasure(pth, False); seg = skia.Path(); m.getSegment(0, m.getLength() * crack, seg, True)
            cv.drawPath(seg, P(col('#5A1A12', 0.6 * a), stroke=7)); cv.drawPath(seg, P(col(RED, a), stroke=3.5))
def quake_rings(cv, t, a, cx=0.0, cy=0.0):
    if a <= 0: return
    for k in range(4):
        q = ((t * 0.7) + k / 4) % 1.0; r = 2 + 12 * q
        pts = [P3(cx + r * math.cos(th), cy + r * math.sin(th), 0.01) for th in [math.tau * i / 60 for i in range(60)]]
        cv.drawPath(poly(pts), P(col(ORANGE, 0.5 * a * (1 - q)), stroke=4))
def quake_gx(t, amp): return amp * (0.6 * math.sin(t * 19) + 0.4 * math.sin(t * 31 + 1.3))

# ------------------------------------------------------------ A: HOOK — gempa; kalau kaku: retak & roboh -> REWIND -> bergoyang lentur + bola peredam (0 - 7.088)
T_RIG, T_CR, T_FALL, T_HIT, T_RW, T_BACK = 1.4, 1.8, 2.5, 3.5, 3.7, 4.5
def gA(cv, t):
    amp = 0.35 * eo(prog(t, 0.0, 0.4)) * (1 - 0.7 * prog(t, 5.6, 6.8))
    gx = quake_gx(t, amp)
    falling = T_FALL < t < T_BACK
    if t < T_HIT: rot = math.radians(78) * ei(prog(t, T_FALL, T_HIT))
    elif t < T_RW: rot = math.radians(78)
    else: rot = math.radians(78) * (1 - eio(prog(t, T_RW, T_BACK)))
    rigid = T_RIG < t < T_BACK
    sway = 0.0 if rigid else 1.1 * math.sin(t * 3.2) * eo(prog(t, 0.0, 0.6)) * (1 - 0.5 * prog(t, 6.0, 6.9))
    cut = eio(prog(t, T_BACK + 0.2, T_BACK + 0.6))
    bx = -0.9 * math.sin(t * 3.2 - 0.6) * cut
    u0 = eio(prog(t, 0.0, 2.0)); zin = eio(prog(t, T_BACK + 0.2, 5.4))
    fw = (lerp(0.0, 1.0, u0 * (1 - zin)), 0.0, lerp(lerp(14.0, 8.5, u0), 15.8, zin)); zoom = lerp(lerp(1.6, 0.98, u0), 2.1, zin)
    hit = prog(t, T_HIT, T_HIT + 0.45); shk = 14 * math.sin(t * 60) * (1 - hit) if T_HIT < t < T_HIT + 0.45 else 0.0
    f = P3(*fw); sx, sy = 540 + shk + gx * 30 * (1 - zin), 940
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    ground_block(cv, t, 1.0, gx=gx); quake_rings(cv, t, eo(prog(t, 0.1, 0.5)) * (1 - prog(t, 5.8, 6.6)))
    small_buildings(cv, t, 1.0, gx=gx, jit=amp)
    tower(cv, t, 1.0, sway=sway, gx=gx, rot=rot if falling or t < T_HIT else rot, crack=eo(prog(t, T_CR, T_FALL)) * (1 - prog(t, T_RW, T_RW + 0.3)), cut=cut,
          ball=(bx, 0.85), tint=prog(t, T_RIG, T_RIG + 0.2) * (1 - prog(t, T_RW, T_BACK)))
    if T_HIT - 0.02 < t < T_HIT + 0.8:                                         # debu
        q = prog(t, T_HIT - 0.02, T_HIT + 0.8); rnd = random.Random(5)
        for k in range(24):
            ang = rnd.uniform(math.pi, math.tau); L = 60 + 220 * eo(q); c0 = P3(rnd.uniform(3, 16), rnd.uniform(-2, 2), 0.3)
            cv.drawCircle(c0[0] + math.cos(ang) * L * 0.5, c0[1] + math.sin(ang) * L * 0.3, 30 + 50 * q, P(col('#D9C7AE', 0.5 * (1 - q)), blur=12))
    cv.restore()
    fl = bump(prog(t, T_HIT, T_HIT + 0.3))
    if fl > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.25 * fl)))
    if T_RIG - 0.1 < t < T_RW + 0.1: chip(cv, 'KALAU GEDUNGNYA KAKU?', 540, 560, eo(prog(t, T_RIG - 0.1, T_RIG + 0.1)) * (1 - prog(t, T_RW - 0.1, T_RW + 0.1)), size=30, bg=RED)
    if T_HIT < t < T_RW + 0.1: text_c(cv, 'ROBOH!', 540, 1200, 64, RED, eo(prog(t, T_HIT, T_HIT + 0.12)) * (1 - prog(t, T_RW - 0.05, T_RW + 0.1)), halo=1.0)
    rewind_fx(cv, t, T_RW, T_BACK)
    seismo(cv, t, eo(prog(t, 4.4, 4.7)), amp * 2.2)
    if t > T_BACK + 0.4:
        bc = (bend((NF - 5) * FH + 0.75, sway) + bx, -0.3, (NF - 5) * FH + 0.75); p = scr(P3(*bc), f, zoom, sx, sy); la = eo(prog(t, T_BACK + 0.5, T_BACK + 0.85)) * (1 - prog(t, 6.8, 7.088))
        label(cv, 'BERGOYANG, BUKAN ROBOH', p[0], p[1], 300, 1150, la, sub='bola peredam melawan goyangan')
        check(cv, 470, 1085, 24, prog(t, T_BACK + 0.6, T_BACK + 1.0), la)
    for k, (num, txt) in enumerate((('1', 'PONDASI DALAM'), ('2', 'LENTUR'), ('3', 'PEREDAM'))):
        q = prog(t, 5.7 + 0.15 * k, 6.0 + 0.15 * k)
        if q > 0:
            x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
            cv.save(); cv.translate(x, 1335); cv.scale(s_, s_); cv.translate(-x, -1335)
            card(cv, skia.Rect(x - 158, 1305, x + 158, 1365), aa, rad=30, lift=8)
            cv.drawCircle(x - 123, 1335, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 123, 1335, 24, WHITE, aa)
            text_c(cv, txt, x + 14, 1335, 23, INK, aa)
            cv.restore()

# ------------------------------------------------------------ B: pondasi tertanam dalam sampai lapisan tanah keras (7.088 - 11.998)
def gB(cv, t):
    a0 = eo(prog(t, 7.088, 7.45)); u = eio(prog(t, 7.2, 9.6))
    fw = (0.0, 6.0, lerp(1.5, -3.6, u)); zoom = lerp(1.2, 1.45, u); f = P3(*fw); sx, sy = 540, 900
    pg = eo(prog(t, 7.93, 8.4)); hg = eo(prog(t, 9.71, 10.1)) * (0.7 + 0.3 * math.sin(t * 5))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    ground_block(cv, t, a0, x0=-8, x1=8, y0=-8, y1=4.0, zb=-8.0, piles=True, pile_glow=pg * 0.6, hard_glow=hg)
    small_buildings(cv, t, a0)
    tower(cv, t, a0, sway=0.15 * math.sin(t * 3))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 7.93, 8.3))
    if la > 0: p = S((1.4, 4.0, -3.5)); label(cv, 'TIANG PONDASI', p[0], p[1], 820, 560, a0 * la, sub='ditanam dalam')
    sa = eo(prog(t, 8.4, 8.8))
    if sa > 0: p = S((-6.0, 4.0, -1.8)); label(cv, 'TANAH LUNAK', p[0], p[1], 270, 600, a0 * sa, dot=NAVY)
    ha = eo(prog(t, 9.71, 10.05))
    if ha > 0:
        p = S((-4.0, 4.0, -6.5)); label(cv, 'LAPISAN KERAS', p[0], p[1], 270, 1190, a0 * ha, sub='tempat tiang bertumpu')
        chip(cv, 'BERTUMPU DI TANAH KERAS', 540, 1340, a0 * eo(prog(t, 9.9, 10.2)), size=28, bg=ORANGE)

# ------------------------------------------------------------ C: dirancang lentur; saat gempa bergoyang, bukan patah (11.998 - 17.631)
def gC(cv, t):
    a0 = eo(prog(t, 11.998, 12.4))
    quake = prog(t, 14.4, 14.7) * (1 - 0.6 * prog(t, 17.0, 17.6))
    amp = 0.3 * quake; gx = quake_gx(t, amp)
    sway = (0.3 + 1.6 * quake) * math.sin(t * 3.0)
    fw = (0.8, 0.0, 8.6); zoom = lerp(1.0, 1.06, eio(prog(t, 11.998, 17.631))); f = P3(*fw); sx, sy = 560, 900
    gf = eo(prog(t, 12.72, 13.1)) * (0.7 + 0.3 * math.sin(t * 5))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    ground_block(cv, t, a0, gx=gx); quake_rings(cv, t, quake)
    small_buildings(cv, t, a0, gx=gx, jit=amp)
    tower(cv, t, a0, sway=sway, gx=gx, cut=1.0, glow_frame=gf, glow_core=0.4 * gf)
    pa = eo(prog(t, 16.4, 16.7))
    if pa > 0:                                                                 # gedung kaku bayangan: patah (merah putus-putus)
        gh = [P3(-6.0 + gx, 0, 0), P3(-6.0 + gx, 0, 8.0), P3(-6.6 + gx, 0, 8.4), P3(-4.0 + gx, 0, 14.0)]
        cv.drawPath(poly(gh, False), P(col(RED, 0.85 * a0 * pa), stroke=6, effect=skia.DashPathEffect.Make([14, 10], 0)))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 12.72, 13.1))
    if la > 0: p = S((bend(10, sway) + HW - 0.15, -0.08, 10.0)); label(cv, 'RANGKA LENTUR', p[0], p[1], 830, 600, a0 * la, sub='baja & beton bertulang')
    seismo(cv, t, a0 * eo(prog(t, 14.4, 14.7)), amp * 2.4, x=270, y=330)
    if t > 15.35:
        top = S((bend(H, sway), 0, H + 0.6)); arrow(cv, (top[0] - 120, top[1] - 30), (top[0] + 120, top[1] - 30), ORANGE, a0 * eo(prog(t, 15.35, 15.6)) * (0.7 + 0.3 * abs(math.sin(t * 3))), w=8, head=20)
        arrow(cv, (top[0] + 120, top[1] - 60), (top[0] - 120, top[1] - 60), ORANGE, a0 * eo(prog(t, 15.35, 15.6)) * (0.7 + 0.3 * abs(math.cos(t * 3))), w=8, head=20)
    if pa > 0:
        p = S((-6.4, 0, 8.3)); s_ = 34
        cv.drawLine(p[0] - s_, p[1] - s_, p[0] + s_, p[1] + s_, P(col(RED, a0 * pa), stroke=10)); cv.drawLine(p[0] - s_, p[1] + s_, p[0] + s_, p[1] - s_, P(col(RED, a0 * pa), stroke=10))
        chip(cv, 'BERGOYANG, BUKAN PATAH', 540, 1340, a0 * pa, size=28, bg=ORANGE); check(cv, 805, 1340, 22, prog(t, 16.5, 16.9), a0 * pa)

# ------------------------------------------------------------ D: peredam: Taipei 101, bola baja 660 ton berayun melawan goyangan (17.631 - 25.796)
def gD(cv, t):
    a0 = eo(prog(t, 17.631, 18.0))
    sway = 0.9 * math.sin(t * 2.6); bx = -0.75 * math.sin(t * 2.6 - 0.5) * eo(prog(t, 18.42, 18.8))
    calm = eo(prog(t, 23.32, 24.2)); sway *= (1 - 0.55 * calm)
    fw = (0.0, -0.5, 16.2); zoom = lerp(2.25, 2.4, eio(prog(t, 17.631, 25.796))); f = P3(*fw); sx, sy = 540, 900
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    tower(cv, t, a0, sway=sway, cut=1.0, ball=(bx, 0.85), top_only=True)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    bc = (bend((NF - 5) * FH + 0.75, sway) + bx, -0.3, (NF - 5) * FH + 0.75)
    pa = eo(prog(t, 18.42, 18.8))
    if pa > 0: p = S(add(bc, (0, 0, -0.8))); label(cv, 'PEREDAM', p[0], p[1], 290, 1180, a0 * pa * (1 - prog(t, 20.4, 20.62)), sub='di lantai paling atas')
    ta = eo(prog(t, 19.49, 19.8))
    if ta > 0: chip(cv, 'TAIPEI 101', 540, 330, a0 * ta, size=30, bg=INK)
    wa = eo(prog(t, 20.62, 21.0))
    if wa > 0:
        p = S(bc); label(cv, 'BOLA BAJA 660 TON', p[0], p[1], 300, 1180, a0 * wa, sub='diameter ±5,5 m')
    ma = eo(prog(t, 23.32, 23.6))
    if ma > 0:                                                                 # arah berlawanan
        top = S((bend(H, sway), 0, H + 0.5)); bp_ = S(bc)
        d1 = 1 if math.cos(t * 2.6) > 0 else -1
        arrow(cv, (top[0], top[1] - 40), (top[0] + 110 * d1, top[1] - 40), NAVY, a0 * ma, w=8, head=20)
        arrow(cv, (bp_[0], bp_[1] + 70), (bp_[0] - 110 * d1, bp_[1] + 70), ORANGE, a0 * ma, w=8, head=20)
        chip(cv, 'MELAWAN GOYANGAN', 540, 1340, a0 * ma, size=30, bg=ORANGE); check(cv, 765, 1340, 22, prog(t, 23.45, 23.85), a0 * ma)

# ------------------------------------------------------------ E: Kiyoshi Muto, Gedung Kasumigaseki 1968 (25.796 - 33.27)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def muto_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'TOKYO · 1968', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    cv.drawRect(skia.Rect(r.left(), 1000, r.right(), r.bottom()), P(col('#D9BF92', a)))
    rnd = random.Random(3)
    for k in range(9):                                                         # kota rendah
        x = r.left() + 20 + k * 98; h = rnd.uniform(70, 170)
        cv.drawRect(skia.Rect(x, 1000 - h, x + 80, 1000), P(col('#E2CFA8', a))); cv.drawRect(skia.Rect(x, 1000 - h, x + 80, 1000), ink(0.6, 2))
    sw = 6 * math.sin(t * 2.4)                                                 # Gedung Kasumigaseki: tinggi, rangka baja lentur
    gx0, gx1, gtop = 470, 610, 380
    pts = [(gx0, 1000), (gx1, 1000), (gx1 + sw, gtop), (gx0 + sw, gtop)]
    cv.drawPath(poly(pts), P(col('#FBF3E2', a))); cv.drawPath(poly(pts), ink(1, 4))
    for k in range(1, 30):
        yy = 1000 - k * (1000 - gtop) / 30; s_ = sw * (k / 30) ** 1.6
        cv.drawLine(gx0 + s_, yy, gx1 + s_, yy, ink(0.55, 1.5))
    for k in range(1, 5):
        xx = gx0 + k * (gx1 - gx0) / 5; cv.drawLine(xx, 1000, xx + sw, gtop, ink(0.45, 1.5))
    hx, hy = 300, 1000                                                         # Kiyoshi Muto: jas & kacamata
    cv.drawRoundRect(skia.Rect(hx - 28, hy - 120, hx + 28, hy - 20), 14, 14, P(col('#3E2E22', a)))
    cv.drawRect(skia.Rect(hx - 20, hy - 22, hx - 6, hy), P(col('#3E2E22', a))); cv.drawRect(skia.Rect(hx + 6, hy - 22, hx + 20, hy), P(col('#3E2E22', a)))
    cv.drawCircle(hx, hy - 146, 24, P(col('#E8C9A0', a))); cv.drawCircle(hx, hy - 146, 24, ink(1, 2.5))
    cv.drawArc(skia.Rect(hx - 26, hy - 174, hx + 26, hy - 128), 180, 180, False, P(col('#2A1F17', a)))
    for gx_ in (-9, 9): cv.drawCircle(hx + gx_, hy - 146, 7, ink(1, 2))
    cv.drawLine(hx + 24, hy - 100, hx + 92, hy - 130 + 4 * math.sin(t * 3), P(col('#3E2E22', a), stroke=10))
    cv.restore()
def gE(cv, t):
    a0 = eo(prog(t, 25.796, 26.2))
    zz = 1.14 + 0.03 * eio(prog(t, 25.796, 33.27))
    cv.save(); cv.translate(540, 770); cv.scale(zz, zz); cv.translate(-540, -700)
    muto_card(cv, t, a0)
    cv.restore()
    S = lambda x, y: (540 + (x - 540) * zz, 770 + (y - 700) * zz)
    na = eo(prog(t, 26.6, 26.95))
    if na > 0: p = S(300, 854); label(cv, 'KIYOSHI MUTO', p[0], p[1], 300, 1240, a0 * na, size=26, sub='insinyur struktur Jepang')
    ga = eo(prog(t, 30.24, 30.6))
    if ga > 0: p = S(620, 520); label(cv, 'GEDUNG KASUMIGASEKI', p[0], p[1], 780, 400, a0 * ga, size=24, sub='±147 m, 36 lantai')
    ja = eo(prog(t, 31.95, 32.25))
    if ja > 0: chip(cv, 'PERTAMA DI JEPANG', 540, 1340, a0 * ja, size=30, bg=ORANGE)

# ------------------------------------------------------------ F: Padang: gedung di atas bantalan karet peredam gempa (33.27 - 37.976)
def gF(cv, t):
    a0 = eo(prog(t, 33.27, 33.65))
    amp = 0.45 * eo(prog(t, 33.4, 33.8)); gx = quake_gx(t, amp); bxo = gx * 0.18
    fw = (0.3, 0.6, 2.4); zoom = lerp(1.75, 1.85, eio(prog(t, 33.27, 37.976))); f = P3(*fw); sx, sy = 540, 900
    iso_g = eo(prog(t, 35.8, 36.1)) * (0.7 + 0.3 * math.sin(t * 6))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    ground_block(cv, t, a0, x0=-7, x1=7, y0=-6, y1=6, zb=-4.0, gx=gx)
    for (x, y) in ((-2.0, -2.0), (0.0, -2.0), (2.0, -2.0), (-2.0, 0.0), (0.0, 0.0), (2.0, 0.0), (-2.0, 2.0), (0.0, 2.0), (2.0, 2.0)):   # bantalan karet berlapis
        for k in range(7):
            zz = 0.1 + k * 0.17; sh = lerp(gx, bxo, (zz + 0.05) / 1.25)
            ocyl(cv, (x + sh, y, zz), (0, 0, 1), 0.55, 0.08, ('#2C3446' if k % 2 == 0 else '#C9CED8'), a0, n=20, hub=0, glow=iso_g * (1 if k % 2 == 0 else 0))
    box(cv, WORLD, -2.8 + bxo, -2.8, 1.25, 5.6, 5.6, 0.25, '#D9D0C2', a0, top=0.2)
    for i in range(8):                                                         # gedung menengah
        z0 = 1.5 + i * 0.6
        box(cv, WORLD, -2.5 + bxo, -2.5, z0, 5.0, 5.0, 0.6, '#F1E6D8', a0, top=0.22, left=0.02, right=-0.14)
        for cc in range(7):
            xx = -2.3 + cc * 0.68 + bxo; quad(cv, WORLD, [(xx, 2.5, z0 + 0.12), (xx + 0.45, 2.5, z0 + 0.12), (xx + 0.45, 2.5, z0 + 0.5), (xx, 2.5, z0 + 0.5)], GLASS, 0.85 * a0)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    pa = eo(prog(t, 33.4, 33.7))
    if pa > 0: chip(cv, 'PADANG', 540, 330, a0 * pa, size=30, bg=INK)
    ia = eo(prog(t, 35.8, 36.1))
    if ia > 0:
        p = S((2.0 + gx * 0.5, 2.0, 0.6)); label(cv, 'BANTALAN KARET', p[0], p[1], 820, 1180, a0 * ia, sub='karet & pelat baja berlapis')
        chip(cv, 'GETARAN TEREDAM', 540, 1340, a0 * eo(prog(t, 36.0, 36.3)), size=30, bg=ORANGE)
    seismo(cv, t, a0 * eo(prog(t, 33.6, 33.9)), amp * 2.0, x=270, y=470)

# ------------------------------------------------------------ G & J
CMTS = [('motor matic!', 280, 760, 38.4, ORANGE), ('jembatan dong', 760, 900, 38.65, INK), ('KRL pls', 330, 1040, 38.9, ORANGE_D), ('bendungan!!', 760, 1180, 39.15, NAVY)]
def gG(cv, t):
    a0 = eo(prog(t, 37.976, 38.3))
    logo_mark(cv, 540, 430, 80 * lerp(0.6, 1, bo(prog(t, 37.976, 38.4))), a0, t)
    text_c(cv, 'BONGKAR APA LAGI?', 540, 590, 64, INK, a0 * eo(prog(t, 38.05, 38.35)))
    for txt, x, y, t0, c in CMTS:
        q = prog(t, t0, t0 + 0.3)
        if q <= 0: continue
        aa = a0 * clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
        r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, aa, rad=42, lift=10)
        cv.drawCircle(r.left() + 42, 0, 24, P(col(c, aa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, aa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, aa)))
        cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, aa)))
        cv.restore()
    ca = eo(prog(t, 40.01, 40.3))
    if ca > 0: chip(cv, 'TULIS DI KOMENTAR', 540, 1340, a0 * ca, size=30, bg=ORANGE)
def gJ(cv, t):
    tt = t - 41.267; a = eo(prog(tt, 0.0, 0.4)); p_ = bo(prog(tt, 0.0, 0.6))
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
    ev = [(0.0, 'rumble'), (0.05, 'whoosh'), (0.9, 'rumble'), (1.4, 'buzzer'), (1.8, 'crack'), (2.0, 'crack'), (2.5, 'rumble'), (2.6, 'whoosh'), (3.5, 'clunk'), (3.52, 'rumble'),
          (3.7, 'rewind'), (4.5, 'shine'), (4.6, 'swish'), (4.9, 'zap'), (5.0, 'ding'), (5.7, 'pop'), (5.85, 'pop'), (6.0, 'pop'),
          (7.088, 'whoosh'), (7.3, 'swish'), (7.93, 'clunk'), (8.0, 'pop'), (8.4, 'pop'), (9.71, 'rise'), (10.0, 'ding'), (10.1, 'stamp'),
          (11.998, 'whoosh'), (12.72, 'zap'), (12.8, 'pop'), (14.4, 'rumble'), (14.5, 'buzzer'), (15.35, 'swish'), (16.4, 'crack'), (16.5, 'ding'), (16.6, 'stamp'),
          (17.631, 'whoosh'), (18.42, 'pop'), (19.49, 'card'), (20.62, 'clunk'), (20.7, 'pop'), (21.5, 'swish'), (22.6, 'swish'), (23.32, 'shine'), (23.45, 'ding'),
          (25.796, 'whoosh'), (25.85, 'card'), (26.6, 'pop'), (28.5, 'tick'), (30.24, 'pop'), (31.95, 'stamp'), (32.0, 'ding_soft'),
          (33.27, 'whoosh'), (33.4, 'rumble'), (33.5, 'pop'), (35.8, 'zap'), (36.0, 'ding'), (36.1, 'stamp'),
          (37.976, 'whoosh'), (38.05, 'shine'), (38.4, 'pop'), (38.65, 'pop'), (38.9, 'pop'), (39.15, 'pop'), (40.01, 'pop'),
          (41.267, 'whoosh'), (41.41, 'boing'), (41.76, 'shine'), (42.01, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
