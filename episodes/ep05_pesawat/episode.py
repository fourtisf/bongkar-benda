#!/usr/bin/env python3
"""Bongkar Benda #05: 'Pesawat, kok nggak kesetrum petir?'
Langit badai + pesawat isometrik detail (utuh / kabin dibelah: kursi & penumpang, bagasi, kargo). Hook: petir menyambar; kalau arusnya masuk kabin,
penumpang kesetrum -> REWIND -> arus mengalir di kulit luar, penumpang aman. Alasan 1: kulit logam menghantarkan listrik di luar (sangkar Faraday).
Alasan 2: petir menyambar di ujung (moncong) dan keluar di ujung lain (ekor). Alasan 3: sistem bahan bakar dirancang supaya uapnya tidak tersulut.
Sejarah: Michael Faraday 1836, ruangan berlapis logam. Penutup: pesawat komersial disambar petir ~sekali setahun. Sumber: content/EP05_pesawat.md
python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, YELLOW, RED, WHITE, text_c, mono, card, chip, label, check, logo_mark, logo_cube, logo_disc)
from iso import Iso, tone, quad, box, shadow, poly, ring_pts, sparks

bb.DUR = 48.814
bb.TITLE = ('Pesawat,', 'kok nggak kesetrum petir?'); bb.TITLE_OUT = 4.4
bb.GROUPS = [(0.0, 6.586, 'A'), (6.586, 13.145, 'B'), (13.145, 20.535, 'C'), (20.535, 26.715, 'D'), (26.715, 35.542, 'E'),
             (35.542, 40.222, 'F'), (40.222, 43.614, 'G'), (43.614, 48.814, 'J')]
bb.PHRASES = [(0.15, 'Pesawat ini disambar [petir].'), (2.35, 'Penumpangnya [kesetrum] nggak?'), (3.71, '[Tenang], nggak.'), (5.32, 'Ini [alasannya].'),
              (6.586, '[Pertama],'), (7.74, 'kulit pesawat [menghantarkan listrik].'), (9.94, 'Arus petir mengalir di [bagian luar],'), (11.55, '[nggak masuk] ke kabin.'),
              (13.145, '[Kedua],'), (14.25, 'petir biasanya menyambar di [ujung],'), (15.99, 'seperti [moncong],'), (17.1, 'lalu [keluar] lewat ujung lain,'), (18.86, 'biasanya [ekor].'),
              (20.535, '[Ketiga],'), (21.48, 'sistem bahan bakarnya [dirancang]'), (23.1, 'supaya percikan petir'), (24.32, '[nggak bisa menyulut] uap bahan bakar.'),
              (26.715, 'Prinsip ini dibuktikan [Michael Faraday].'), (29.27, 'Tahun [1836],'), (31.01, 'dia [menyetrum] ruangan berlapis logam,'), (33.15, 'dan di dalamnya [nggak ada listrik].'),
              (35.542, 'Rata-rata, [pesawat komersial]'), (38.15, 'disambar petir sekitar'), (39.03, '[sekali setahun].'),
              (40.222, 'Benda apa yang mau kamu [bongkar] berikutnya?'), (42.37, 'Tulis di [komentar]!'),
              (43.614, 'Follow [Bongkar Benda],'), (45.01, 'biar makin paham [cara kerja benda] di sekitarmu.')]

WORLD = Iso(0, 0, 50)
NAVY, NAVY2 = '#2A3F6B', '#1A2A4C'
SKIN, SKIN_D = '#F6F2EC', '#D9D3C9'
GLASS, GLASS_HI = '#22345C', '#5A73A3'
BOLT = '#FFF4D6'

def P3(x, y, z): return WORLD.p(x, y, z)
def cam(cv, wx, wy, zoom, sx=540, sy=760): cv.translate(sx, sy); cv.scale(zoom, zoom); cv.translate(-wx, -wy)
def scr(p, f, zoom, sx, sy): return (sx + (p[0] - f[0]) * zoom, sy + (p[1] - f[1]) * zoom)
def rad(d): return math.radians(d)
def arrow(cv, p0, p1, c, a, w=9, head=20):
    if a <= 0: return
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); hx, hy = p1[0] - math.cos(ang) * head * 0.8, p1[1] - math.sin(ang) * head * 0.8
    pth = skia.Path(); pth.moveTo(*p1)
    pth.lineTo(p1[0] - head * math.cos(ang - 0.45), p1[1] - head * math.sin(ang - 0.45)); pth.lineTo(p1[0] - head * math.cos(ang + 0.45), p1[1] - head * math.sin(ang + 0.45)); pth.close()
    cv.drawLine(p0[0], p0[1], hx, hy, P(col(WHITE, a), stroke=w + 7)); cv.drawPath(pth, P(col(WHITE, a), stroke=7))
    cv.drawLine(p0[0], p0[1], hx, hy, P(col(c, a), stroke=w)); cv.drawPath(pth, P(col(c, a)))
def text_on_y(cv, txt, x0, yp, zb, size, c, a, font_name=XB):
    s_, c30 = WORLD.s, math.cos(math.radians(30)); ox, oy = P3(x0, yp, zb)
    cv.save(); cv.concat(skia.Matrix.MakeAll(c30 * s_, 0, ox, 0.5 * s_, s_, oy, 0, 0, 1)); cv.drawString(txt, 0, 0, font(font_name, size), P(col(c, a))); cv.restore()

# ------------------------------------------------------------ langit badai (latar penuh)
def storm_sky(cv, t, a, flash=0.0, top_cream=0.0):
    if a <= 0: return
    cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(shader=lg(0, 0, 0, 1920, [col('#1A2A4C', a), col('#2E4472', a), col('#4C6596', a), col('#7387B0', a)], [0, 0.35, 0.75, 1])))
    rnd = random.Random(2)
    for layer_i, (yb, sc, al, sp) in enumerate(((520, 1.3, 0.35, 12), (900, 1.0, 0.45, 22), (1500, 1.5, 0.55, 34))):   # lapisan awan bergerak
        for k in range(7):
            x = (rnd.uniform(-200, 1280) - t * sp) % 1500 - 210; y = yb + rnd.uniform(-90, 90); r = rnd.uniform(70, 150) * sc
            for j in range(4):
                cx, cy, rr = x + (j - 1.5) * r * 0.55, y + (0.25 if j % 2 else -0.1) * r * 0.5, r * (0.55 + 0.15 * (j % 2))
                cv.drawCircle(cx, cy + rr * 0.15, rr, P(col('#14213D', al * 0.6 * a), blur=18))
                cv.drawCircle(cx, cy, rr, P(shader=rg(cx - rr * 0.3, cy - rr * 0.5, rr * 1.4, [col(mixc('#8C9CC0', '#FFFFFF', 0.25 + flash * 0.6), al * a), col(mixc('#3A5080', '#C9D3E8', flash * 0.5), al * a)])))
    for k in range(60):                                                   # hujan: garis miring
        x = (rnd.uniform(0, 1200) + t * 700) % 1200 - 60; y = (rnd.uniform(0, 1920) + t * 1400 * rnd.uniform(0.8, 1.2)) % 1920
        cv.drawLine(x, y, x - 14, y + 46, P(col(WHITE, 0.16 * a), stroke=2))
    if flash > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(WHITE, 0.55 * flash * a)))
    if top_cream > 0: cv.drawRect(skia.Rect(0, 0, 1080, 620), P(shader=lg(0, 380, 0, 640, [col(bb.BG0, top_cream), col(bb.BG0, 0)])))
def bolt(cv, p0, p1, t, a, seed=1, w=7, branches=2):
    """kilat bercabang dari p0 ke p1 (koordinat layar), berkedip"""
    if a <= 0: return
    rnd = random.Random(seed + int(t * 24)); n = 9; pts = [p0]
    for i in range(1, n):
        u = i / n; jx = rnd.uniform(-1, 1) * 38 * (1 - abs(0.5 - u)); pts.append((lerp(p0[0], p1[0], u) + jx, lerp(p0[1], p1[1], u) + rnd.uniform(-10, 10)))
    pts.append(p1)
    pth = poly(pts, False)
    cv.drawPath(pth, P(col(ORANGE, 0.55 * a), stroke=w * 4, blur=16)); cv.drawPath(pth, P(col(YELLOW, 0.8 * a), stroke=w * 1.8, blur=4)); cv.drawPath(pth, P(col(BOLT, a), stroke=w))
    for b_ in range(branches):
        i = rnd.randint(2, n - 3); bx, by = pts[i]; ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + rnd.choice((-1, 1)) * rnd.uniform(0.5, 1.0)
        q = [(bx, by)]
        for j in range(3): q.append((q[-1][0] + math.cos(ang) * 40 + rnd.uniform(-12, 12), q[-1][1] + math.sin(ang) * 40 + rnd.uniform(-12, 12)))
        cv.drawPath(poly(q, False), P(col(BOLT, 0.8 * a), stroke=w * 0.5))
def flow(cv, pts, t, a, c=ORANGE, speed=1.4, n=4, seg=0.12, w=8, phase=0.0):
    """denyut arus mengalir di sepanjang lintasan (titik layar)"""
    if a <= 0 or len(pts) < 2: return
    pth = poly(pts, False); m = skia.PathMeasure(pth, False); L = m.getLength()
    cv.drawPath(pth, P(col(c, 0.35 * a), stroke=w * 0.6, blur=3))
    for k in range(n):
        u = (t * speed / max(L / 600, 0.3) + k / n + phase) % 1.0; s0, s1 = L * u, L * min(1.0, u + seg)
        sg = skia.Path(); m.getSegment(s0, s1, sg, True)
        cv.drawPath(sg, P(col(c, 0.8 * a), stroke=w * 2.6, blur=8)); cv.drawPath(sg, P(col(BOLT, a), stroke=w * 0.7))

# ------------------------------------------------------------ pesawat
def fr(x):
    if x > 6.4: return 1.3 * math.sqrt(max(0.0, 1 - ((x - 6.4) / 2.9) ** 2)) ** 0.8
    if x < -5.4: return lerp(1.3, 0.32, (-5.4 - x) / 4.2)
    return 1.3
def fzc(x): return 0.0 if x > -5.4 else lerp(0.0, 0.75, (-5.4 - x) / 4.2)
XT, XN = -9.6, 9.3
FST = [lerp(XT, XN, i / 48) for i in range(49)]
FLOOR = -0.38
def fpt(x, th, r_add=0.0): r = fr(x) + r_add; return P3(x, r * math.cos(th), fzc(x) + r * math.sin(th))
def skin_col(thd):
    if thd < -12: return NAVY
    return SKIN
def fuselage(cv, a, d0=-45, d1=135, t=0.0):
    n = 18
    for xa, xb in zip(FST[:-1], FST[1:]):
        for i in range(n):
            ta, tb = lerp(d0, d1, i / n), lerp(d0, d1, (i + 1) / n); tm = (ta + tb) / 2
            c = skin_col(tm); k = 0.16 * math.sin(rad(tm)) + 0.07 * math.cos(rad(tm)) - 0.06
            if 4 < tm < 13: c = ORANGE
            q = poly([fpt(xa, rad(ta)), fpt(xb, rad(ta)), fpt(xb, rad(tb)), fpt(xa, rad(tb))]); cv.drawPath(q, P(col(tone(c, k), a)))
    for x in [lerp(-4.8, 5.6, i / 20) for i in range(21)]:                # jendela kabin
        p = fpt(x, rad(36), 0.005); cv.drawRoundRect(skia.Rect(p[0] - 3.5, p[1] - 5.5, p[0] + 3.5, p[1] + 5.5), 3, 3, P(col(GLASS, a)))
    for x in (6.3, -4.9):                                                 # pintu
        q = poly([fpt(x - 0.25, rad(8)), fpt(x + 0.25, rad(8)), fpt(x + 0.25, rad(62)), fpt(x - 0.25, rad(62))]); cv.drawPath(q, P(col(SKIN_D, a), stroke=1.6))
    for xa_, xb_ in ((7.55, 8.05), (8.1, 8.45)):                          # kaca kokpit
        q = poly([fpt(xa_, rad(30)), fpt(xb_, rad(30)), fpt(xb_, rad(62)), fpt(xa_, rad(62))]); cv.drawPath(q, P(col(GLASS, a)))
    text_on_y(cv, 'BONGKAR BENDA AIR', -3.4, 1.29, 0.2, 0.36, NAVY, 0.9 * a)
def fuselage_inner(cv, a):
    """separuh belakang kabin (dibelah di y=0): dinding dalam, lantai, kursi, bagasi atas, kargo"""
    n = 14
    for xa, xb in zip(FST[:-1], FST[1:]):
        for i in range(n):
            ta, tb = lerp(120, 270, i / n), lerp(120, 270, (i + 1) / n); tm = (ta + tb) / 2
            k = lerp(-0.25, 0.05, (tm - 120) / 150)
            q = poly([fpt(xa, rad(ta), -0.06), fpt(xb, rad(ta), -0.06), fpt(xb, rad(tb), -0.06), fpt(xa, rad(tb), -0.06)])
            cv.drawPath(q, P(col(tone('#EDE7DD', k), a)))
    for x in [lerp(-4.8, 5.6, i / 20) for i in range(21)]:                # jendela dari dalam
        p = fpt(x, rad(160), -0.07); cv.drawRoundRect(skia.Rect(p[0] - 4, p[1] - 6, p[0] + 4, p[1] + 6), 3, 3, P(col('#9FB0CC', a)))
    quad(cv, WORLD, [(-6.0, -1.15, -1.05), (6.4, -1.15, -1.05), (6.4, 0, -1.05), (-6.0, 0, -1.05)], '#B8AE9F', a)          # lantai kargo
    for x in (-5.0, -3.6, -2.0, 1.0, 2.6, 4.2):                           # koper di kargo
        box(cv, WORLD, x, -0.95, -1.05, 0.9, 0.7, 0.45, (ORANGE, NAVY, '#C9A35A')[int(x * 3) % 3], a, top=0.25)
    quad(cv, WORLD, [(-6.2, -1.25, FLOOR), (6.6, -1.25, FLOOR), (6.6, 0, FLOOR), (-6.2, 0, FLOOR)], '#C9C2B6', a)          # lantai kabin
    for x in [lerp(-4.9, 5.4, i / 13) for i in range(14)]:                 # bagasi atas
        box(cv, WORLD, x, -1.05, 0.72, 0.68, 0.45, 0.34, '#F1ECE4', a, top=0.15)
def cabin_people(cv, t, a, shock=0.0, calm=1.0):
    rows = [lerp(-4.8, 5.2, i / 12) for i in range(13)]
    for xr in rows:
        for j, y in enumerate((-0.95, -0.62, -0.29)):
            jit = shock * 3.5 * math.sin(t * 60 + xr * 7 + j * 3)
            box(cv, WORLD, xr, y - 0.13, FLOOR, 0.42, 0.26, 0.3, NAVY, a, top=0.3)                  # dudukan
            box(cv, WORLD, xr - 0.06, y - 0.13, FLOOR + 0.3, 0.1, 0.26, 0.45, NAVY2, a, top=0.3)    # sandaran
            body = mixc(('#F6F2EC', ORANGE, '#5A6B8C')[(int(xr * 5) + j) % 3], RED, shock * 0.7)
            box(cv, WORLD, xr + 0.08, y - 0.1, FLOOR + 0.3, 0.2, 0.2, 0.32, body, a, top=0.2)
            p = P3(xr + 0.18, y, FLOOR + 0.82); p = (p[0] + jit, p[1] - abs(jit) * 0.5)
            cv.drawCircle(p[0], p[1], 5.5, P(col(mixc('#E8C9A0', RED, shock * 0.6), a)))
            if shock > 0.3:                                                # rambut berdiri
                for k in range(3): cv.drawLine(p[0] - 3 + k * 3, p[1] - 5, p[0] - 5 + k * 5, p[1] - 11, P(col(INK, a * shock), stroke=1.4))
def wing(cv, side, a, fuel=0.0, t=0.0, cut=0.0):
    sgn = 1 if side == 'near' else -1
    rl, rt, tt_, tl = (2.6, 1.1 * sgn, -0.55), (-1.6, 1.1 * sgn, -0.65), (-5.6, 10.0 * sgn, -0.05), (-4.1, 10.0 * sgn, 0.0)
    th_r, th_t = 0.26, 0.09
    if side == 'near':                                                    # sisi depan (tebal sayap)
        cv.drawPath(WORLD.path([rl, tl, (tl[0], tl[1], tl[2] - th_t), (rl[0], rl[1], rl[2] - th_r)]), P(col(tone(SKIN_D, -0.05), a)))
    top = WORLD.path([rl, rt, tt_, tl]); cv.drawPath(top, P(shader=lg(*P3(*rl), *P3(*tl), [col(tone(SKIN, 0.02), a), col(tone(SKIN_D, 0.02), a)])))
    for k in range(1, 4):                                                  # garis panel
        u = k / 4; pa, pb = P3(lerp(rl[0], tl[0], u), lerp(rl[1], tl[1], u), lerp(rl[2], tl[2], u)), P3(lerp(rt[0], tt_[0], u), lerp(rt[1], tt_[1], u), lerp(rt[2], tt_[2], u))
        cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col(SKIN_D, 0.8 * a), stroke=1.4))
    flap = WORLD.path([(rt[0] + 0.9, rt[1], rt[2] + 0.02), rt, tt_, (tt_[0] + 0.5, tt_[1], tt_[2] + 0.02)]); cv.drawPath(flap, P(col(tone(SKIN_D, -0.08), a)))
    wl = WORLD.path([tl, (tt_[0] + 0.4, tt_[1], tt_[2]), (tt_[0] - 0.3, tt_[1], tt_[2] + 1.0), (tl[0] - 0.6, tl[1], tl[2] + 1.0)]); cv.drawPath(wl, P(col(ORANGE, a)))   # winglet
    if fuel > 0 and side == 'near':                                       # potongan tangki bahan bakar di sayap
        u0, u1 = 0.12, 0.62
        def wp(u, v): return (lerp(lerp(rl[0], tl[0], u), lerp(rt[0], tt_[0], u), v), lerp(lerp(rl[1], tl[1], u), lerp(rt[1], tt_[1], u), v), lerp(lerp(rl[2], tl[2], u), lerp(rt[2], tt_[2], u), v) + 0.002)
        hole = WORLD.path([wp(u0, 0.15), wp(u1, 0.15), wp(u1, 0.75), wp(u0, 0.75)])
        cv.drawPath(hole, P(col('#5B4A35', fuel * a)))
        ins = WORLD.path([wp(u0 + 0.02, 0.2), wp(u1 - 0.02, 0.2), wp(u1 - 0.02, 0.7), wp(u0 + 0.02, 0.7)])
        cv.drawPath(ins, P(shader=lg(*P3(*wp(u0, 0.2)), *P3(*wp(u1, 0.7)), [col('#F2C46A', fuel * a), col('#D9962E', fuel * a)])))
        cv.save(); cv.clipPath(ins, doAntiAlias=True)
        for k in range(6):
            uu = lerp(u0, u1, (k + 0.5) / 6); pa, pb = P3(*wp(uu, 0.2)), P3(*wp(uu, 0.7)); cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col('#8C6A3A', fuel * a), stroke=3))
        for k in range(3):
            uu = lerp(u0, u1, ((t * 0.15 + k / 3) % 1.0)); pa = P3(*wp(uu, 0.45)); cv.drawLine(pa[0] - 14, pa[1], pa[0] + 14, pa[1] - 5, P(col(WHITE, 0.4 * fuel * a), stroke=3))
        cv.restore()
        cv.drawPath(hole, P(col(NAVY2, fuel * a), stroke=4))
        return hole
def engine(cv, side, a, t):
    sgn = 1 if side == 'near' else -1; y = 4.3 * sgn; cz = -1.35; r = 0.56
    box(cv, WORLD, 1.2, y - 0.08, cz + 0.3, 1.4, 0.16, 0.55, SKIN_D, a, top=0.2)                   # pilon
    n = 16
    for i in range(n):
        ta, tb = rad(lerp(-45, 135, i / n)), rad(lerp(-45, 135, (i + 1) / n)); k = 0.18 * math.sin((ta + tb) / 2) - 0.05
        q = poly([P3(0.4, y + r * math.cos(ta), cz + r * math.sin(ta)), P3(3.3, y + r * math.cos(ta), cz + r * math.sin(ta)), P3(3.3, y + r * math.cos(tb), cz + r * math.sin(tb)), P3(0.4, y + r * math.cos(tb), cz + r * math.sin(tb))])
        cv.drawPath(q, P(col(tone(NAVY if i < 4 else SKIN, k), a)))
    face = poly(ring_pts(WORLD, 3.3, y, cz, r, axis='x', n=28)); cv.drawPath(face, P(col('#2C3446', a)))
    inner = poly(ring_pts(WORLD, 3.31, y, cz, r * 0.82, axis='x', n=28)); cv.drawPath(inner, P(col('#3E4A60', a)))
    for k in range(10):                                                   # kipas berputar
        th = t * 14 + k * math.tau / 10; p0, p1 = P3(3.32, y + 0.1 * math.cos(th), cz + 0.1 * math.sin(th)), P3(3.32, y + r * 0.8 * math.cos(th + 0.3), cz + r * 0.8 * math.sin(th + 0.3))
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#9FB0CC', 0.8 * a), stroke=3))
    cv.drawPath(face, P(col(ORANGE, a), stroke=3))
def tail(cv, a, which):
    if which == 'fin':
        fin = WORLD.path([(-6.0, 0.02, 1.0), (-9.2, 0.02, 1.0), (-9.85, 0.02, 4.7), (-8.6, 0.02, 4.7)])
        cv.drawPath(fin, P(shader=lg(*P3(-6.0, 0, 1.0), *P3(-9.0, 0, 4.7), [col(ORANGE, a), col(ORANGE_D, a)])))
        cv.drawPath(fin, P(col(tone(ORANGE_D, -0.2), a), stroke=2))
        p = P3(-8.4, 0.02, 3.0); logo_disc(cv, p[0], p[1], 34, a); logo_cube(cv, p[0], p[1] - 2, 18, 3, a)
        rud = WORLD.path([(-9.2, 0.03, 1.0), (-9.85, 0.03, 4.7)], close=False); cv.drawPath(rud, P(col(NAVY2, 0.5 * a), stroke=2))
    else:
        sgn = 1 if which == 'near' else -1
        st = WORLD.path([(-7.0, 0.45 * sgn, 0.85), (-8.6, 0.45 * sgn, 0.92), (-9.6, 3.9 * sgn, 1.08), (-8.7, 3.9 * sgn, 1.1)])
        cv.drawPath(st, P(col(tone(SKIN, -0.02 if sgn > 0 else -0.08), a))); cv.drawPath(st, P(col(SKIN_D, a), stroke=1.5))
def plane(cv, t, a, cut=0.0, shock=0.0, fuel=0.0, cut_wing=False):
    """urutan: sayap/mesin/sirip belakang -> badan -> sirip tegak -> sayap/mesin depan"""
    if a <= 0: return None
    wing(cv, 'far', a); engine(cv, 'far', a, t); tail(cv, a, 'far')
    if cut > 0:
        fuselage_inner(cv, a * cut); cabin_people(cv, t, a * cut, shock=shock)
        sec_top = [P3(x, 0, fzc(x) + fr(x)) for x in FST]; sec_bot = [P3(x, 0, fzc(x) - fr(x)) for x in FST]
        cv.drawPath(poly(sec_top, False), P(col('#8E9AAF', a * cut), stroke=9)); cv.drawPath(poly(sec_bot, False), P(col('#8E9AAF', a * cut), stroke=9))
        cv.drawPath(poly(sec_top, False), P(col(WHITE, 0.5 * a * cut), stroke=2))
    if cut < 1:
        fuselage(cv, a * (1 - cut), t=t)
    else:
        fuselage(cv, a, d0=-45, d1=-5, t=t)                               # sisa kulit bawah depan (tepi potongan) tetap terlihat tipis
    tail(cv, a, 'fin'); tail(cv, a, 'near')
    hole = None
    if not cut_wing:
        hole = wing(cv, 'near', a * (1 - 0.0), fuel=fuel, t=t); engine(cv, 'near', a, t)
    return hole
def skin_path_top(f=None):
    return [P3(x, 0, fzc(x) + fr(x)) for x in FST[::-1]]
def skin_path_side():
    return [fpt(x, rad(60)) for x in FST[::-1]]

# ------------------------------------------------------------ A: HOOK — disambar petir; kalau arus masuk kabin: kesetrum; REWIND; arus di kulit luar (0 - 6.586)
T_S1, T_CUT, T_RW, T_BACK, T_S2 = 0.55, 0.95, 3.55, 4.3, 4.38
def gA(cv, t):
    flash = max(bump(prog(t, T_S1, T_S1 + 0.25)), bump(prog(t, T_S2, T_S2 + 0.25)))
    storm_sky(cv, t, 1.0, flash, top_cream=1 - eio(prog(t, bb.TITLE_OUT - 0.4, bb.TITLE_OUT)))
    u = eio(prog(t, 0.0, 1.2))
    zoom = lerp(0.62, 0.92, u) * (1 + 0.04 * eio(prog(t, 4.3, 6.586))); fw = (lerp(0.5, 1.5, u), 0.0, lerp(1.5, 0.3, u)); f = P3(*fw)
    bobz = 8 * math.sin(t * 1.6); shk = 10 * math.sin(t * 55) * bump(prog(t, T_S1, T_S1 + 0.4)) + 8 * math.sin(t * 55) * bump(prog(t, T_S2, T_S2 + 0.3))
    sx, sy = 540 + shk, 1000 + bobz
    rewind_back = prog(t, T_RW, T_BACK)
    cut = eio(prog(t, T_CUT, T_CUT + 0.35)) * (1 - eio(prog(t, T_RW, T_RW + 0.3))) + eio(prog(t, T_S2 + 0.1, T_S2 + 0.45))
    cut = clamp(cut)
    shock = eo(prog(t, 1.35, 1.6)) * (1 - prog(t, T_RW - 0.1, T_RW + 0.1))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    plane(cv, t, 1.0, cut=cut, shock=shock, cut_wing=cut > 0.5)
    S = lambda w_: P3(*w_)
    nose = S((XN, 0, 0.1)); tailp = S((-9.8, 0, 4.6))
    if T_S1 - 0.02 < t < T_S1 + 0.5: bolt(cv, (nose[0] - 380, nose[1] - 900), nose, t, bump(prog(t, T_S1 - 0.02, T_S1 + 0.5)) * 1.4, seed=3, w=9)
    if T_S2 - 0.02 < t < T_S2 + 0.5: bolt(cv, (nose[0] - 380, nose[1] - 900), nose, t, bump(prog(t, T_S2 - 0.02, T_S2 + 0.5)) * 1.4, seed=5, w=9)
    if 1.2 < t < T_RW:                                                    # pengandaian: arus merah menembus kabin ke penumpang
        ra = eo(prog(t, 1.2, 1.4)) * (1 - prog(t, T_RW - 0.15, T_RW))
        rnd = random.Random(int(t * 14))
        for k in range(7):
            x0 = lerp(7.0, -3.5, k / 6) + rnd.uniform(-0.4, 0.4); p0 = S((x0, 0, fr(x0)))
            p1 = S((x0 - 0.5, -0.6, FLOOR + 0.8)); bolt(cv, p0, p1, t, ra * 0.9, seed=k * 7, w=3.5, branches=1)
        cv.drawRect(skia.Rect(-4000, -4000, 4000, 4000), P(col(RED, 0.10 * ra)))
    if t > T_S2 + 0.05:                                                   # arus aman di kulit luar, keluar di ekor
        fa = eo(prog(t, T_S2 + 0.05, T_S2 + 0.3)) * (1 - 0.6 * prog(t, 6.0, 6.5))
        flow(cv, skin_path_top(), t, fa, speed=1.6, n=5); flow(cv, [P3(x, 0, fzc(x) - fr(x)) for x in FST[::-1]], t, fa, speed=1.6, n=5, phase=0.3)
        if t < T_S2 + 1.2: bolt(cv, tailp, (tailp[0] - 260, tailp[1] + 520), t, bump(prog(t, T_S2 + 0.35, T_S2 + 1.2)), seed=9, w=6)
    cv.restore()
    rw = prog(t, T_RW, T_BACK + 0.05)
    if 0 < rw < 1:
        ra = clamp(bump(rw) * 1.3)
        cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(bb.BG0, 0.12 * ra)))
        for k in range(14):
            yy = (k * 151 + t * 2400) % 1920; cv.drawRect(skia.Rect(0, yy, 1080, yy + 5), P(col(WHITE, 0.35 * ra)))
        r = skia.Rect(400, 520, 680, 600); cv.drawRoundRect(r, 40, 40, P(col(INK, ra)))
        for k in range(2):
            x0_ = 470 + k * 44; tri = skia.Path(); tri.moveTo(x0_, 560); tri.lineTo(x0_ + 38, 536); tri.lineTo(x0_ + 38, 584); tri.close(); cv.drawPath(tri, P(col(WHITE, ra)))
        f_ = font(MONO, 26); cv.drawString('ULANG', 570, bl(f_, 560), f_, P(col(WHITE, ra)))
    if 1.0 < t < T_RW: chip(cv, 'KALAU ARUSNYA MASUK KABIN?', 540, 560, eo(prog(t, 1.0, 1.2)) * (1 - prog(t, T_RW - 0.15, T_RW)), size=28, bg=RED)
    if 2.35 < t < T_RW: text_c(cv, 'KESETRUM!', 540, 1180, 56, RED, eo(prog(t, 2.35, 2.5)) * (1 - prog(t, T_RW - 0.15, T_RW)), halo=1.0)
    if t > T_S2 + 0.3:
        p = scr(P3(1.0, 0, fr(1.0)), f, zoom, sx, sy); la = eo(prog(t, T_S2 + 0.3, T_S2 + 0.65)) * (1 - prog(t, 6.3, 6.586))
        label(cv, 'ARUS DI KULIT LUAR', p[0], p[1], 300, 640, la, sub='penumpang aman')
        check(cv, 505, 575, 24, prog(t, T_S2 + 0.4, T_S2 + 0.8), la)
    for k, (num, txt) in enumerate((('1', 'KULIT LOGAM'), ('2', 'MASUK-KELUAR'), ('3', 'TANGKI AMAN'))):
        q = prog(t, 5.4 + 0.15 * k, 5.7 + 0.15 * k)
        if q > 0:
            x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
            cv.save(); cv.translate(x, 1335); cv.scale(s_, s_); cv.translate(-x, -1335)
            card(cv, skia.Rect(x - 158, 1305, x + 158, 1365), aa, rad=30, lift=8)
            cv.drawCircle(x - 123, 1335, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 123, 1335, 24, WHITE, aa)
            text_c(cv, txt, x + 14, 1335, 23, INK, aa)
            cv.restore()

# ------------------------------------------------------------ B: kulit logam menghantarkan listrik; arus di luar, tidak masuk kabin (6.586 - 13.145)
def gB(cv, t):
    a0 = eo(prog(t, 6.586, 6.95))
    storm_sky(cv, t, a0, 0.6 * bump(prog(t, 7.6, 7.9)))
    zoom = lerp(1.08, 1.2, eio(prog(t, 6.586, 13.145))); fw = (0.8, -0.4, 0.2); f = P3(*fw); sx, sy = 560, 980
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    plane(cv, t, a0, cut=1.0, cut_wing=True)
    fa = eo(prog(t, 7.74, 8.1))
    flow(cv, skin_path_top(), t, a0 * fa, speed=1.3, n=6); flow(cv, [P3(x, 0, fzc(x) - fr(x)) for x in FST[::-1]], t, a0 * fa, speed=1.3, n=6, phase=0.4)
    for x in (5.0, 1.0, -3.0):                                            # arus juga melingkari kulit (bukan lewat kabin)
        ring = [fpt(x, rad(d)) for d in range(90, 271, 8)]
        flow(cv, ring, t, a0 * eo(prog(t, 9.94, 10.3)), speed=0.8, n=2, seg=0.2, w=6)
    nose = P3(XN, 0, 0.1)
    if 7.6 < t < 8.2: bolt(cv, (nose[0] - 300, nose[1] - 800), nose, t, a0 * bump(prog(t, 7.6, 8.2)), seed=11, w=8)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 7.74, 8.1))
    if la > 0: p = S((-1.5, 0, fr(-1.5))); label(cv, 'KULIT LOGAM', p[0], p[1], 280, 560, a0 * la, sub='menghantarkan listrik')
    ka = eo(prog(t, 11.55, 11.9))
    if ka > 0:
        p = S((0.5, -0.6, 0.6)); label(cv, 'KABIN', p[0], p[1], 800, 1150, a0 * ka, dot=NAVY, sub='tanpa listrik petir')
        chip(cv, 'NGGAK MASUK KE KABIN', 540, 1340, a0 * eo(prog(t, 11.6, 11.9)), size=28, bg=ORANGE); check(cv, 800, 1340, 22, prog(t, 11.7, 12.1), a0 * ka)
    sa = eo(prog(t, 9.94, 10.3)) * (1 - prog(t, 11.3, 11.6))
    if sa > 0: chip(cv, 'ARUS DI BAGIAN LUAR', 540, 330, a0 * sa, size=28, bg=NAVY)

# ------------------------------------------------------------ C: menyambar di ujung (moncong), keluar di ujung lain (ekor) (13.145 - 20.535)
def gC(cv, t):
    a0 = eo(prog(t, 13.145, 13.5))
    fl = max(bump(prog(t, 15.99, 16.25)), 0.7 * bump(prog(t, 18.86, 19.1)))
    storm_sky(cv, t, a0, fl)
    zoom = lerp(0.76, 0.82, eio(prog(t, 13.145, 20.535))); fw = (0.0, 0.3, 0.9); f = P3(*fw); sx, sy = 540, 880
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    plane(cv, t, a0, cut=0.0)
    nose = P3(XN, 0, 0.1); tailp = P3(-9.8, 0, 4.6); tipn = P3(-4.6, 10.0, 0.6)
    ea = eo(prog(t, 14.25, 14.6))                                         # titik-titik ujung yang paling sering disambar
    for i, w_ in enumerate(((XN, 0, 0.1), (-4.6, 10.0, 0.6), (-4.6, -10.0, 0.6), (-9.8, 0, 4.6))):
        p = P3(*w_); pr = 1 + 0.25 * math.sin(t * 6 + i)
        cv.drawCircle(p[0], p[1], 34 * pr, P(col(ORANGE, 0.5 * ea * a0), stroke=5)); cv.drawCircle(p[0], p[1], 12, P(col(ORANGE, ea * a0 * (1 - prog(t, 15.8, 16.0)))))
    if 15.95 < t < 16.7: bolt(cv, (nose[0] - 350, nose[1] - 900), nose, t, a0 * bump(prog(t, 15.95, 16.7)) * 1.4, seed=13, w=9)
    pa = eo(prog(t, 16.2, 16.6))
    if pa > 0: flow(cv, skin_path_side(), t, a0 * pa * (1 - 0.5 * prog(t, 20.0, 20.5)), speed=1.4, n=5)
    if 18.8 < t < 19.8: bolt(cv, tailp, (tailp[0] - 300, tailp[1] + 640), t, a0 * bump(prog(t, 18.8, 19.8)) * 1.3, seed=15, w=8)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    if ea > 0: chip(cv, 'TITIK UJUNG', 540, 330, a0 * ea * (1 - prog(t, 15.8, 16.1)), size=28, bg=NAVY)
    ma = eo(prog(t, 15.99, 16.3))
    if ma > 0: p = S((XN, 0, 0.1)); label(cv, 'MASUK: MONCONG', p[0], p[1], 760, 1160, a0 * ma, sub='titik sambar pertama')
    ka = eo(prog(t, 18.86, 19.2))
    if ka > 0: p = S((-9.8, 0, 4.6)); label(cv, 'KELUAR: EKOR', p[0], p[1], 300, 420, a0 * ka, sub='arus pergi lagi')

# ------------------------------------------------------------ D: sistem bahan bakar dirancang supaya uapnya tidak tersulut (20.535 - 26.715)
def gD(cv, t):
    a0 = eo(prog(t, 20.535, 20.9))
    storm_sky(cv, t, a0, 0.5 * bump(prog(t, 23.1, 23.35)))
    zoom = lerp(1.3, 1.4, eio(prog(t, 20.535, 26.715))); fw = (-1.6, 4.6, -0.6); f = P3(*fw); sx, sy = 560, 900
    fu = eo(prog(t, 21.48, 21.9))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    hole = plane(cv, t, a0, cut=0.0, fuel=fu)
    sa = prog(t, 23.1, 26.715)
    if sa > 0 and hole is not None:                                       # percikan di kulit sayap memantul, tidak tembus ke tangki
        b0 = hole.getBounds()
        for k in range(4):
            q = ((t - 23.1) * 1.2 + k / 4) % 1.0; px = lerp(b0.left(), b0.right(), (k + 0.5) / 4); py = b0.top() - 40
            sparks(cv, px, py, t + k, 40 + k, a0 * eo(prog(t, 23.1, 23.4)) * (1 - prog(t, 26.2, 26.7)), n=10, spread=70, up=True)
        sh = eo(prog(t, 24.32, 24.7))
        if sh > 0: cv.drawPath(hole, P(col(ORANGE, 0.9 * sh * a0), stroke=10)); cv.drawPath(hole, P(col(ORANGE, 0.5 * sh * a0), stroke=26, blur=12))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 21.48, 21.85))
    if la > 0 and hole is not None:
        b = hole.getBounds(); p = scr((b.centerX(), b.centerY()), f, zoom, sx, sy); label(cv, 'TANGKI BAHAN BAKAR', p[0], p[1], 300, 420, a0 * la, sub='di dalam sayap')
    ca = eo(prog(t, 24.32, 24.7))
    if ca > 0:
        chip(cv, 'UAP NGGAK TERSULUT', 540, 1340, a0 * ca, size=28, bg=ORANGE); check(cv, 770, 1340, 22, prog(t, 24.4, 24.8), a0 * ca)
    pa = eo(prog(t, 23.1, 23.4)) * (1 - prog(t, 24.1, 24.3))
    if pa > 0: chip(cv, 'PERCIKAN PETIR', 540, 1340, a0 * pa, size=28, bg=RED)

# ------------------------------------------------------------ E: Michael Faraday 1836: ruangan berlapis logam disetrum, di dalamnya tidak ada listrik (26.715 - 35.542)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def faraday_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'LONDON · 1836', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    cv.drawRect(skia.Rect(r.left(), 980, r.right(), r.bottom()), P(col('#D9BF92', a)))
    for k in range(9): cv.drawLine(r.left() + k * 110, 980, r.left() + k * 110 - 60, r.bottom(), ink(0.3, 2))
    rx0, ry0, rx1, ry1 = 330, 520, 760, 980                                # ruangan berlapis logam (foil)
    cv.drawRect(skia.Rect(rx0, ry0, rx1, ry1), P(shader=lg(rx0, ry0, rx1, ry1, [col('#C9C2B6', a), col('#9C9488', a)])))
    for k in range(1, 8): cv.drawLine(rx0 + k * (rx1 - rx0) / 8, ry0, rx0 + k * (rx1 - rx0) / 8, ry1, ink(0.35, 2))
    for k in range(1, 6): cv.drawLine(rx0, ry0 + k * (ry1 - ry0) / 6, rx1, ry0 + k * (ry1 - ry0) / 6, ink(0.35, 2))
    cv.drawRect(skia.Rect(rx0, ry0, rx1, ry1), ink(1, 4))
    cv.drawRect(skia.Rect(rx0 + 40, ry0 + 60, rx1 - 40, ry1 - 30), P(col('#F6EEDC', 0.85 * a)))  # bagian dalam (dibelah)
    ex, ey = 600, 900                                                     # elektroskop: daun emas tetap menutup
    cv.drawRoundRect(skia.Rect(ex - 40, ey - 90, ex + 40, ey), 16, 16, P(col('#FBF3E2', a))); cv.drawRoundRect(skia.Rect(ex - 40, ey - 90, ex + 40, ey), 16, 16, ink(1, 3))
    cv.drawLine(ex, ey - 130, ex, ey - 60, ink(1, 4)); cv.drawCircle(ex, ey - 134, 9, P(col('#C9A35A', a)))
    cv.drawLine(ex, ey - 60, ex - 4, ey - 22, P(col('#C9A35A', a), stroke=4)); cv.drawLine(ex, ey - 60, ex + 4, ey - 22, P(col('#C9A35A', a), stroke=4))
    hx, hy = 470, 960                                                     # Faraday di dalam ruangan
    cv.drawRoundRect(skia.Rect(hx - 24, hy - 110, hx + 24, hy - 20), 12, 12, P(col('#3E2E22', a)))
    cv.drawRect(skia.Rect(hx - 18, hy - 22, hx - 5, hy), P(col('#3E2E22', a))); cv.drawRect(skia.Rect(hx + 5, hy - 22, hx + 18, hy), P(col('#3E2E22', a)))
    cv.drawCircle(hx, hy - 134, 22, P(col('#E8C9A0', a))); cv.drawCircle(hx, hy - 134, 22, ink(1, 2.5))
    cv.drawArc(skia.Rect(hx - 24, hy - 160, hx + 24, hy - 116), 180, 180, False, P(col('#B9B2A8', a)))
    cv.drawLine(hx + 20, hy - 96, hx + 70, hy - 120 + 3 * math.sin(t * 3), P(col('#3E2E22', a), stroke=10))
    gx, gy = 220, 760                                                     # mesin listrik statis (roda) + percikan ke dinding luar
    cv.drawCircle(gx, gy, 70, P(col('#C9A577', a))); cv.drawCircle(gx, gy, 70, ink(1, 4))
    for k in range(6):
        th = t * 3 + k * math.pi / 3; cv.drawLine(gx, gy, gx + 64 * math.cos(th), gy + 64 * math.sin(th), ink(0.7, 3))
    cv.drawRect(skia.Rect(gx - 12, gy, gx + 12, 980), P(col('#B58A57', a))); cv.drawCircle(gx + 90, gy - 70, 14, P(col('#C9A35A', a)))
    if int(t * 6) % 2 == 0:
        bolt(cv, (gx + 100, gy - 70), (rx0, ry0 + 120 + 60 * math.sin(t * 5)), t, a * 0.9, seed=21, w=4, branches=2)
    cv.restore()
def gE(cv, t):
    a0 = eo(prog(t, 26.715, 27.1))
    zz = 1.14 + 0.03 * eio(prog(t, 26.715, 35.542))
    cv.save(); cv.translate(540, 770); cv.scale(zz, zz); cv.translate(-540, -700)
    faraday_card(cv, t, a0)
    cv.restore()
    S = lambda x, y: (540 + (x - 540) * zz, 770 + (y - 700) * zz)
    na = eo(prog(t, 27.2, 27.6))
    if na > 0: p = S(470, 826); label(cv, 'MICHAEL FARADAY', p[0], p[1], 290, 480, a0 * na, size=26, sub='ilmuwan Inggris')
    ra = eo(prog(t, 31.01, 31.4))
    if ra > 0: p = S(700, 560); label(cv, 'RUANGAN BERLAPIS LOGAM', p[0], p[1], 770, 480, a0 * ra, size=24, sub='disetrum dari luar')
    ea = eo(prog(t, 33.15, 33.5))
    if ea > 0:
        p = S(600, 860); label(cv, 'DI DALAM: AMAN', p[0], p[1], 760, 1240, a0 * ea, size=26, sub='daun elektroskop diam')
        chip(cv, 'SANGKAR FARADAY', 300, 1240, a0 * eo(prog(t, 33.3, 33.6)), size=26, bg=ORANGE)

# ------------------------------------------------------------ F: pesawat komersial disambar petir sekitar sekali setahun (35.542 - 40.222)
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MEI', 'JUN', 'JUL', 'AGU', 'SEP', 'OKT', 'NOV', 'DES']
def gF(cv, t):
    a0 = eo(prog(t, 35.542, 35.9))
    u = eio(prog(t, 35.8, 39.6)); strike = bump(prog(t, 38.1, 38.45))
    storm_sky(cv, t, a0 * 0.85, strike * 0.6)
    cx, cy, R = 540, 980, 380                                             # lintasan setahun (busur)
    arc = skia.Path(); arc.addArc(skia.Rect(cx - R, cy - R, cx + R, cy + R), 200, 140)
    cv.drawPath(arc, P(col(WHITE, 0.35 * a0), stroke=6, effect=skia.DashPathEffect.Make([14, 12], -t * 30)))
    for i, mth in enumerate(MONTHS):
        th = rad(200 + 140 * (i + 0.5) / 12); px, py = cx + R * math.cos(th), cy + R * math.sin(th)
        on = u >= (i + 0.5) / 12
        cv.drawCircle(px, py, 9, P(col(ORANGE if on else WHITE, (0.95 if on else 0.5) * a0)))
        text_c(cv, mth, cx + (R + 46) * math.cos(th), cy + (R + 46) * math.sin(th), 22, WHITE, 0.8 * a0, f=B)
    th = rad(200 + 140 * u); px, py = cx + R * math.cos(th), cy + R * math.sin(th)    # pesawat kecil menyusuri busur
    cv.save(); cv.translate(px, py); cv.rotate(math.degrees(th) + 90); cv.scale(0.16, 0.16); o = P3(0, 0, 0); cv.translate(-o[0], -o[1])
    plane(cv, t, a0, cut=0.0)
    cv.restore()
    if strike > 0:
        thk = rad(200 + 140 * (7.5 / 12)); bx, by = cx + R * math.cos(thk), cy + R * math.sin(thk)
        bolt(cv, (bx - 120, by - 420), (bx, by), t, a0 * strike * 1.4, seed=31, w=7)
    if u > 0.62:
        thk = rad(200 + 140 * (7.5 / 12)); bx, by = cx + R * math.cos(thk), cy + R * math.sin(thk)
        cv.drawCircle(bx, by, 26, P(col(YELLOW, a0), stroke=5)); text_c(cv, 'ZAP!', bx, by - 60, 30, YELLOW, a0 * eo(prog(t, 38.2, 38.4)), halo=0.0)
    ca = eo(prog(t, 35.8, 36.2))
    if ca > 0:
        card(cv, skia.Rect(250, 1060, 830, 1260), a0 * ca, rad=30)
        mono(cv, 'PESAWAT KOMERSIAL', 540, 1100, 22, MUTED, a0 * ca, sp=3)
        ba = eo(prog(t, 38.15, 38.45)); sc = 1 + 0.15 * bump(prog(t, 39.03, 39.4))
        cv.save(); cv.translate(540, 1170); cv.scale(sc, sc); cv.translate(-540, -1170)
        text_c(cv, '≈ 1× SETAHUN', 540, 1170, 72, ORANGE, a0 * ba); cv.restore()
        text_c(cv, 'disambar petir', 540, 1225, 28, INK2, a0 * ca, f=B)

# ------------------------------------------------------------ G & J
CMTS = [('bendungan!', 280, 760, 40.6, ORANGE), ('kapal selam dong', 760, 900, 40.85, INK), ('kereta cepat pls', 310, 1040, 41.1, ORANGE_D), ('tower crane!!', 760, 1180, 41.35, NAVY)]
def gG(cv, t):
    a0 = eo(prog(t, 40.222, 40.5))
    logo_mark(cv, 540, 430, 80 * lerp(0.6, 1, bo(prog(t, 40.222, 40.6))), a0, t)
    text_c(cv, 'BONGKAR APA LAGI?', 540, 590, 64, INK, a0 * eo(prog(t, 40.3, 40.6)))
    for txt, x, y, t0, c in CMTS:
        q = prog(t, t0, t0 + 0.3)
        if q <= 0: continue
        aa = a0 * clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
        r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, aa, rad=42, lift=10)
        cv.drawCircle(r.left() + 42, 0, 24, P(col(c, aa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, aa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, aa)))
        cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, aa)))
        cv.restore()
    ca = eo(prog(t, 42.37, 42.65))
    if ca > 0: chip(cv, 'TULIS DI KOMENTAR', 540, 1340, a0 * ca, size=30, bg=ORANGE)
def gJ(cv, t):
    tt = t - 43.614; a = eo(prog(tt, 0.0, 0.4)); p_ = bo(prog(tt, 0.0, 0.6))
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
    ev = [(0.0, 'whoosh'), (0.1, 'rumble'), (0.55, 'zap2'), (0.57, 'crack'), (0.6, 'rumble'), (0.95, 'swish'), (1.2, 'zap'), (1.3, 'buzzer'), (1.6, 'fizz'), (2.35, 'buzzer'),
          (3.55, 'rewind'), (4.38, 'zap2'), (4.4, 'crack'), (4.5, 'shine'), (4.7, 'ding'), (4.8, 'stamp'), (5.4, 'pop'), (5.55, 'pop'), (5.7, 'pop'),
          (6.586, 'whoosh'), (7.6, 'zap2'), (7.65, 'crack'), (7.74, 'pop'), (8.0, 'fizz_soft'), (9.94, 'swish'), (10.0, 'pop'), (11.55, 'ding'), (11.65, 'stamp'),
          (13.145, 'whoosh'), (14.25, 'tick'), (14.35, 'tick'), (14.45, 'tick'), (14.55, 'tick'), (15.95, 'zap2'), (15.97, 'crack'), (16.0, 'rumble'), (16.3, 'fizz_soft'),
          (18.8, 'zap'), (18.86, 'crack'), (19.0, 'pop'),
          (20.535, 'whoosh'), (21.48, 'card'), (21.6, 'pop'), (23.1, 'fizz'), (23.15, 'buzzer'), (24.32, 'shine'), (24.4, 'ding'), (24.5, 'stamp'),
          (26.715, 'whoosh'), (26.75, 'card'), (27.2, 'pop'), (29.27, 'tick'), (31.01, 'zap'), (31.05, 'pop'), (32.0, 'zap'), (33.15, 'pop'), (33.3, 'ding'),
          (35.542, 'whoosh'), (35.8, 'card'), (36.2, 'tick'), (37.0, 'tick'), (38.1, 'zap2'), (38.15, 'crack'), (39.03, 'stamp'), (39.1, 'ding'),
          (40.222, 'whoosh'), (40.3, 'shine'), (40.6, 'pop'), (40.85, 'pop'), (41.1, 'pop'), (41.35, 'pop'), (42.37, 'pop'),
          (43.614, 'whoosh'), (43.76, 'boing'), (44.1, 'shine'), (44.36, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
