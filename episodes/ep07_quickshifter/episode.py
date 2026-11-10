#!/usr/bin/env python3
"""Bongkar Benda #07: 'Gigi motor, kok nggak patah?' (quick shifter, request penonton)
Motor sport fiktif 3D di jalan yang bergerak + girboks yang dibelah (poros utama & poros bawah, roda gigi, cincin pengunci 'dog', garpu, drum pemindah, kopling).
Hook: ganti gigi tanpa kopling, gas dibuka; kalau tanpa quick shifter gigi dipaksa pindah saat menahan tenaga -> beradu & patah -> REWIND -> busi padam
sesaat, gigi masuk mulus. Alasan 1: sensor di batang pemindah gigi. Alasan 2: komputer memutus pengapian sesaat (hitungan milidetik), gigi lepas
tekanan. Alasan 3: gigi lama lepas, gigi berikutnya masuk, tanpa kopling. Asal-usul: balap motor. Penutup: motor sport 250 cc di Indonesia.
Sumber: content/EP07_quickshifter.md. python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, YELLOW, RED, WHITE, text_c, mono, card, chip, label, check, logo_mark)
from iso import Iso, tone, quad, box, shadow, poly, sparks
import geo3d as g
from geo3d import add, sub, mul, dot, nrm, p3, obox, ocyl, gear3d, extrude, face

bb.DUR = 48.443
bb.TITLE = ('Gigi motor,', 'kok nggak patah?'); bb.TITLE_OUT = 4.3
bb.GROUPS = [(0.0, 7.42, 'A'), (7.42, 13.817, 'B'), (13.817, 21.229, 'C'), (21.229, 28.142, 'D'), (28.142, 33.566, 'E'),
             (33.566, 38.858, 'F'), (38.858, 43.243, 'G'), (43.243, 48.443, 'J')]
bb.PHRASES = [(0.15, 'Motor ini ganti gigi [tanpa tarik kopling],'), (3.02, '[gasnya] tetap dibuka.'), (4.48, 'Kok giginya nggak [patah]?'), (6.19, 'Ini [alasannya].'),
              (7.42, '[Pertama],'), (8.33, 'ada [sensor] di batang pemindah gigi.'), (10.4, 'Begitu kakimu [menginjak tuas],'), (12.3, 'sensor [langsung tahu].'),
              (13.817, '[Kedua],'), (14.67, 'komputer motor [memutus pengapian] sesaat,'), (17.19, 'cuma [hitungan milidetik].'), (18.4, 'Jadi gigi nggak lagi [menahan tenaga mesin].'),
              (21.229, '[Ketiga],'), (22.03, 'di momen itu,'), (22.96, 'gigi lama [lepas]'), (23.78, 'dan gigi berikutnya [langsung masuk].'), (25.74, 'Pindah gigi jadi [mulus] tanpa kopling.'),
              (28.142, 'Teknologi ini'), (29.18, 'awalnya dibuat untuk [balap motor],'), (30.91, 'supaya ganti gigi [lebih cepat]'), (32.2, 'dari pakai kopling.'),
              (33.566, 'Sekarang, di [Indonesia],'), (35.52, 'motor sport [250 cc] pun'), (37.05, 'sudah ada yang [memakainya].'),
              (38.858, 'Ini [request] dari kalian.'), (40.36, 'Benda apa lagi yang mau kamu [bongkar]?'), (41.98, 'Tulis di [komentar]!'),
              (43.243, 'Follow [Bongkar Benda],'), (44.66, 'biar makin paham [cara kerja benda] di sekitarmu.')]

WORLD = Iso(0, 0, 50); g.ISO = WORLD
NAVY, NAVY2 = '#2A3F6B', '#1A2A4C'
STEEL, STEEL_D = '#B9C0CC', '#5A6B8C'
GEAR_C, GEAR_C2 = '#C9CED8', '#AEB6C4'
def P3(x, y, z): return WORLD.p(x, y, z)
def cam(cv, wx, wy, zoom, sx=540, sy=760): cv.translate(sx, sy); cv.scale(zoom, zoom); cv.translate(-wx, -wy)
def scr(p, f, zoom, sx, sy): return (sx + (p[0] - f[0]) * zoom, sy + (p[1] - f[1]) * zoom)
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
def hud(cv, gear, ign, a, x=870, y=330, glow=0.0):
    """panel kecil: angka gigi + lampu pengapian"""
    if a <= 0: return
    card(cv, skia.Rect(x - 120, y - 70, x + 120, y + 70), a, rad=26)
    mono(cv, 'GIGI', x - 60, y - 38, 18, MUTED, a, sp=3); text_c(cv, str(gear), x - 60, y + 14, 72, mixc(INK, ORANGE, glow), a)
    mono(cv, 'BUSI', x + 55, y - 38, 18, MUTED, a, sp=3)
    c_ = mixc('#C9CED8', YELLOW, ign); cv.drawCircle(x + 55, y + 12, 26, P(col(c_, a)))
    if ign > 0.5:
        for k in range(6):
            ang = k * math.pi / 3; cv.drawLine(x + 55 + 30 * math.cos(ang), y + 12 + 30 * math.sin(ang), x + 55 + 40 * math.cos(ang), y + 12 + 40 * math.sin(ang), P(col(ORANGE, a), stroke=4))
    else:
        cv.drawLine(x + 35, y - 8, x + 75, y + 32, P(col(RED, a), stroke=5))

# ------------------------------------------------------------ motor sport fiktif (profil diekstrusi) + pengendara
BODY = [(2.0, 1.25), (2.18, 1.6), (1.95, 1.92), (1.45, 2.05), (1.05, 2.12), (0.55, 2.16), (0.05, 1.96), (-0.55, 1.9), (-1.3, 2.05), (-1.9, 2.12),
        (-2.0, 1.96), (-1.4, 1.7), (-0.6, 1.5), (-0.1, 1.02), (0.5, 0.74), (1.3, 0.8), (1.75, 1.0)]
SCREEN = [(1.95, 1.92), (1.45, 2.05), (1.32, 2.32), (1.8, 2.26)]
SEAT = [(0.05, 1.96), (-0.55, 1.9), (-0.6, 2.02), (0.02, 2.08)]
def bike(cv, t, a, x0=0.0, paint=(ORANGE, NAVY), lever=0.0, sensor_glow=0.0, foot=0.0, rider=True, spin=None, wire=0.0, ecu_glow=0.0):
    if a <= 0: return
    sp_ = t * 14 if spin is None else spin
    def X(x, y, z): return (x0 + x, y, z)
    shadow(cv, WORLD, x0 - 2.0, -0.6, 0.0, 4.2, 1.2, a, blur=12, k=0.3)
    for wx in (-1.45, 1.45):                                              # roda
        ocyl(cv, X(wx, 0, 0.62), (0, 1, 0), 0.62, 0.15, '#2C3446', a, n=28, spin=sp_, cap_col='#3E4A60', spokes=5, hub=0.62)
        rim = [p3(q) for q in g.ring(X(wx, 0.151, 0.62), (0, 1, 0), 0.4, 28)]; cv.drawPath(poly(rim), P(col(ORANGE, a), stroke=3))
        disc = [p3(q) for q in g.ring(X(wx, 0.16, 0.62), (0, 1, 0), 0.28, 20)]; cv.drawPath(poly(disc), P(col('#C9CED8', a), stroke=2.5))
    for yy in (-0.2, 0.2):                                                # garpu depan & lengan ayun
        p0, p1 = P3(*X(1.45, yy, 0.62)), P3(*X(1.72, yy, 1.8)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#C9A35A' if yy > 0 else '#8E7440', a), stroke=7))
    p0, p1 = P3(*X(-1.45, 0.25, 0.62)), P3(*X(-0.15, 0.25, 0.95)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=10))
    box(cv, WORLD, x0 + 0.0, -0.32, 0.5, 1.1, 0.64, 0.62, '#3E4A60', a, top=0.25, left=0.05, right=-0.15)     # mesin
    cov = [p3(q) for q in g.ring(X(0.55, 0.33, 0.82), (0, 1, 0), 0.24, 20)]; cv.drawPath(poly(cov), P(col('#8E9AAF', a))); cv.drawPath(poly(cov), P(col(NAVY2, a), stroke=1.5))
    p0, p1 = P3(*X(0.15, 0.2, 0.55)), P3(*X(-1.2, 0.2, 0.62)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#2C3446', a), stroke=4))    # rantai
    front = g.p3                                                          # bodi & fairing
    sh = lg(*P3(*X(0, 0.38, 2.2)), *P3(*X(0, 0.38, 0.8)), [col(paint[0], a), col(paint[0], a), col(paint[1], a), col(paint[1], a)], [0, 0.5, 0.52, 1])
    bp = extrude(cv, [(x0 + x, z) for x, z in BODY], -0.38, 0.38, lambda nm: tone(paint[0], 0.05) if nm[2] > 0.35 else tone(paint[1], -0.1), paint[0], a, front_shader=sh)
    if bp is not None:
        cv.save(); cv.clipPath(bp, doAntiAlias=True)
        st = poly([P3(*X(x, 0.381, z)) for x, z in ((2.1, 1.5), (-1.9, 2.0), (-1.9, 1.92), (2.1, 1.4))]); cv.drawPath(st, P(col(WHITE, 0.9 * a)))
        cv.restore()
        cv.drawPath(bp, P(col(tone(paint[1], -0.3), 0.6 * a), stroke=1.5))
    cv.drawPath(poly([P3(*X(x, 0.39, z)) for x, z in SCREEN]), P(col('#5A73A3', 0.85 * a)))
    cv.drawPath(poly([P3(*X(x, 0.39, z)) for x, z in SEAT]), P(col('#2C3446', a)))
    hl = P3(*X(2.12, 0.2, 1.5)); cv.drawCircle(hl[0], hl[1], 7, P(col('#FFE3A8', a)))
    peg = X(-0.1, 0.48, 0.92); ocyl(cv, peg, (0, 1, 0), 0.05, 0.1, '#8E9AAF', a, n=10, hub=0)
    piv = X(0.12, 0.5, 0.95); ang = math.radians(-8 - 14 * lever)               # tuas pemindah gigi + batang + sensor
    toe = add(piv, (0.32 * math.cos(ang), 0.0, 0.32 * math.sin(ang)))
    q0, q1 = P3(*piv), P3(*toe); cv.drawLine(q0[0], q0[1], q1[0], q1[1], P(col('#5A6B8C', a), stroke=6)); cv.drawCircle(q1[0], q1[1], 4, P(col('#8E9AAF', a)))
    rod0 = add(piv, (0.12 * math.cos(ang), 0.0, 0.12 * math.sin(ang))); rod1 = X(0.42, 0.42, 1.12)
    r0, r1 = P3(*rod0), P3(*rod1); cv.drawLine(r0[0], r0[1], r1[0], r1[1], P(col('#8E9AAF', a), stroke=4))
    sc = mul(add(rod0, rod1), 0.5); ocyl(cv, sc, nrm(sub(rod1, rod0)), 0.055, 0.06, ORANGE, a, n=12, glow=sensor_glow, hub=0)
    if sensor_glow > 0: s_ = P3(*sc); cv.drawCircle(s_[0], s_[1], 18, P(col(ORANGE, 0.5 * sensor_glow * a), blur=8))
    ecu = X(-0.95, 0.39, 1.62)                                            # kotak komputer (ECU) di bawah jok
    obox(cv, ecu, (1, 0, 0), (0, 1, 0), (0, 0, 1), 0.22, 0.02, 0.13, NAVY2, a, glow=ecu_glow)
    led = P3(*add(ecu, (0.12, 0.03, 0.05))); cv.drawCircle(led[0], led[1], 3, P(col(ORANGE if ecu_glow > 0.3 else '#5A6B8C', a)))
    if wire > 0:                                                          # kabel sinyal sensor -> ECU, pulsa berjalan
        pts = [P3(*q) for q in (sc, X(0.2, 0.42, 1.25), X(-0.4, 0.4, 1.45), add(ecu, (0.2, 0.02, -0.08)))]
        pth = poly(pts, False); cv.drawPath(pth, P(col(NAVY2, a), stroke=2.5))
        m = skia.PathMeasure(pth, False); L = m.getLength(); u = (t * 1.6) % 1.0; seg = skia.Path(); m.getSegment(L * u, L * min(1, u + 0.18), seg, True)
        cv.drawPath(seg, P(col(ORANGE, wire * a), stroke=7, blur=3)); cv.drawPath(seg, P(col(WHITE, wire * a), stroke=2))
    if rider:                                                             # pengendara: tungkai jauh -> badan -> tungkai dekat
        def L_(pts_, c, w):
            pp = [P3(*X(*q)) for q in pts_]; cv.drawPath(poly(pp, False), P(col(c, a), stroke=w))
        L_([(-0.1, -0.33, 1.98), (0.5, -0.42, 1.55), (0.05, -0.48, 1.0)], tone(NAVY2, -0.1), 15)
        L_([(0.6, -0.32, 2.55), (1.0, -0.36, 2.25), (1.4, -0.33, 2.08)], tone(NAVY2, -0.1), 10)
        L_([(-0.15, 0, 2.05), (0.65, 0, 2.62)], NAVY, 30)
        L_([(-0.05, 0.05, 2.15), (0.6, 0.05, 2.6)], ORANGE, 5)
        hp = P3(*X(0.98, 0, 2.86)); cv.drawCircle(hp[0], hp[1], 17, P(shader=rg(hp[0] - 6, hp[1] - 6, 24, [col(tone(paint[0], 0.2), a), col(tone(paint[0], -0.15), a)])))
        vis = skia.Path(); vis.addArc(skia.Rect(hp[0] - 13, hp[1] - 9, hp[0] + 15, hp[1] + 9), -40, 110); cv.drawPath(vis, P(col(NAVY2, a), stroke=7))
        ft = 0.06 * foot
        L_([(-0.1, 0.33, 1.98), (0.5, 0.42, 1.55), (0.06, 0.48, 1.0 + ft), (0.3, 0.5, 0.94 + ft)], NAVY, 15)
        L_([(0.06, 0.49, 1.0 + ft), (0.3, 0.5, 0.94 + ft)], '#2C3446', 11)
        L_([(0.6, 0.32, 2.55), (1.0, 0.36, 2.25), (1.4, 0.33, 2.08)], NAVY, 10)
        gl = P3(*X(1.42, 0.34, 2.07)); cv.drawCircle(gl[0], gl[1], 6, P(col('#2C3446', a)))
def road(cv, t, a, speed=9.0, x0=-30, x1=30):
    quad(cv, WORLD, [(x0, -9, -0.01), (x1, -9, -0.01), (x1, 9, -0.01), (x0, 9, -0.01)], '#EDE4D6', a)
    quad(cv, WORLD, [(x0, -2.4, 0), (x1, -2.4, 0), (x1, 2.4, 0), (x0, 2.4, 0)], '#4A5368', a, grad=((x0, 2.4, 0), (x0, -2.4, 0), '#545E74', '#3F475B'))
    off = (t * speed) % 3.0
    x = x0 - off
    while x < x1:
        quad(cv, WORLD, [(x, -0.08, 0.002), (x + 1.6, -0.08, 0.002), (x + 1.6, 0.08, 0.002), (x, 0.08, 0.002)], '#F2EEE8', 0.85 * a); x += 3.0
    off2 = (t * speed) % 1.2; x = x0 - off2; k = 0
    while x < x1:                                                         # kerb oranye-putih
        for yy in (2.4, -2.9):
            quad(cv, WORLD, [(x, yy, 0.003), (x + 0.6, yy, 0.003), (x + 0.6, yy + 0.5, 0.003), (x, yy + 0.5, 0.003)], ORANGE if (k + int((t * speed) // 1.2)) % 2 else '#F6F2EC', a)
        x += 0.6; k += 1
    rnd = random.Random(3)
    for j in range(10):                                                   # pohon & tiang lampu yang lewat
        xx = ((rnd.uniform(0, 60) - t * speed) % 60) - 30; yy = rnd.choice((-5.5, -6.5, 4.5, 5.5))
        if not (x0 < xx < x1): continue
        if j % 3 == 0:
            q0, q1 = P3(xx, yy, 0), P3(xx, yy, 2.6); cv.drawLine(q0[0], q0[1], q1[0], q1[1], P(col(NAVY, a), stroke=4)); cv.drawCircle(q1[0], q1[1], 7, P(col('#FFE3A8', a)))
        else:
            box(cv, WORLD, xx - 0.1, yy - 0.1, 0, 0.2, 0.2, 1.0, '#8C6A4A', a, top=0.2); p = P3(xx, yy, 2.0); r = 46
            cv.drawCircle(p[0], p[1], r, P(shader=rg(p[0] - 15, p[1] - 18, r * 1.5, [col('#F4C27A', a), col(ORANGE_D, a)])))
def speedlines(cv, t, a, cx=540, cy=900):
    if a <= 0: return
    rnd = random.Random(9)
    for k in range(16):
        y = cy - 420 + rnd.uniform(0, 840); L = rnd.uniform(80, 220); x = (rnd.uniform(0, 1400) - t * 1800) % 1400 - 160
        cv.drawLine(x, y, x + L, y + L * 0.5, P(col(WHITE, 0.45 * a), stroke=3))

# ------------------------------------------------------------ girboks yang dibelah
ZM, ZC_, YS = 2.2, 3.7, 0.0                                              # poros utama (z = ZM), poros bawah/atas (z = ZC_)
GEARS = [(-2.5, 0.56, 0.94), (-1.3, 0.66, 0.84), (0.1, 0.74, 0.76), (1.6, 0.81, 0.69)]   # (x, r di poros utama, r di poros atas): gigi 1..4
GH = 0.2
DOG3, DOG4, DOGN = 0.52, 1.18, 0.85                                      # posisi cincin pengunci: masuk gigi 3, gigi 4, netral
def dogring_x(state): return state
def gearbox(cv, t, a, dog=DOG3, load=0.0, crash=0.0, broken=0.0, drum=0.0, spin=None, glow34=0.0, clutch_x=0.0, labels=None, ign=1.0):
    """state: dog = posisi x cincin pengunci; load = tekanan tenaga di gigi yang terkunci; crash = beradu (percikan); broken = taring patah terlempar"""
    if a <= 0: return
    sp_ = t * 5 if spin is None else spin
    box(cv, WORLD, -4.6, -1.5, -0.2, 7.4, 3.4, 0.2, '#D9CFBF', a, top=0.15)                       # lantai rumah girboks
    face(cv, [(-4.6, -1.5, 0), (2.8, -1.5, 0), (2.8, -1.5, 5.2), (-4.6, -1.5, 5.2)], (0, 1, 0), '#EDE6DA', a)   # dinding belakang (menghadap +y)
    for zz in (0.8, 2.2, 3.7):
        for xx in (-4.2, 2.4):
            b_ = P3(xx, -1.49, zz); cv.drawCircle(b_[0], b_[1], 6, P(col('#B9AE9F', a)))
    cut = poly([P3(-4.6, -1.5, 5.2), P3(2.8, -1.5, 5.2), P3(2.8, 1.9, 5.2)], False); cv.drawPath(cut, P(col(NAVY2, a), stroke=8))
    items = []
    def shaft(z, xa, xb):
        def fn(cv): ocyl(cv, ((xa + xb) / 2, YS, z), (1, 0, 0), 0.14, (xb - xa) / 2, STEEL, a, n=14, hub=0)
        items.append((-99 + z * 0.01, fn))
    shaft(ZM, -4.3, 2.6); shaft(ZC_, -3.0, 2.4)
    for i, (x, r1, r2) in enumerate(GEARS):
        n1, n2 = max(10, int(r1 * 26)), max(10, int(r2 * 26))
        pk = 0
        gl = 0.0
        if i == 2: pk = 4; gl = glow34 if dog < DOGN else 0.0
        if i == 3: pk = 4; gl = glow34 if dog > DOGN else 0.0
        def gm(cv, x=x, r1=r1, n1=n1, pk=pk, gl=gl, i=i):
            gear3d(cv, (x, YS, ZM), (1, 0, 0), r1, GH, n1, GEAR_C, a, spin=sp_ * (0.9 if i < 2 else 1.0), glow=gl, pockets=pk, pocket_side=(1 if i == 2 else -1))
        def gc(cv, x=x, r1=r1, r2=r2, n2=n2):
            gear3d(cv, (x, YS, ZC_), (1, 0, 0), r2, GH, n2, GEAR_C2, a, spin=-sp_ * r1 / r2 + math.pi / n2)
        items.append((x + ZM, gm)); items.append((x + ZC_, gc))
    cr = 0.95                                                              # kopling di ujung kiri poros utama
    def clutch(cv):
        ocyl(cv, (-3.85, YS, ZM), (1, 0, 0), cr, 0.32, '#8E9AAF', a, n=28, cap_col='#C9CED8', spin=sp_, spokes=6, hub=0.4)
        for k in range(8):
            xk = -4.12 + k * 0.075; rr_ = [p3(q) for q in g.ring((xk, YS, ZM), (1, 0, 0), cr * 1.01, 28)]
            cv.drawPath(poly(rr_), P(col(ORANGE_D if k % 2 else '#5A6B8C', 0.55 * a), stroke=1.4))
        if clutch_x > 0:
            c_ = P3(-3.53, YS, ZM); s_ = 60 * clutch_x
            cv.drawLine(c_[0] - s_, c_[1] - s_, c_[0] + s_, c_[1] + s_, P(col(RED, clutch_x * a), stroke=12)); cv.drawLine(c_[0] - s_, c_[1] + s_, c_[0] + s_, c_[1] - s_, P(col(RED, clutch_x * a), stroke=12))
    items.append((-3.85 + ZM, clutch))
    def dogring(cv):                                                      # cincin pengunci dengan taring di kedua sisi
        jit = 0.03 * math.sin(t * 70) * crash
        c = (dog + jit, YS, ZM)
        ocyl(cv, c, (1, 0, 0), 0.5, 0.13, ORANGE if glow34 > 0 else '#D9962E', a, n=24, cap_col=tone(ORANGE, 0.15), hub=0.45, glow=0.0)
        grv = [p3(q) for q in g.ring(c, (1, 0, 0), 0.505, 24)]; cv.drawPath(poly(grv), P(col(ORANGE_D, a), stroke=3))
        e1, e2 = g.basis((1, 0, 0))
        for side in (-1, 1):
            for m_ in range(4):
                if broken > 0 and side == -1 and m_ == 1: continue
                th = sp_ + m_ * math.tau / 4 + 0.4 + 0.21
                dc = add(add(c, mul((1, 0, 0), side * 0.2)), add(mul(e1, 0.39 * math.cos(th)), mul(e2, 0.39 * math.sin(th))))
                u_ = (1, 0, 0); v_ = nrm(add(mul(e1, -math.sin(th)), mul(e2, math.cos(th)))); w_ = nrm(add(mul(e1, math.cos(th)), mul(e2, math.sin(th))))
                obox(cv, dc, u_, v_, w_, 0.08, 0.1, 0.06, '#F2B25A', a)
    items.append((dog + ZM + 0.01, dogring))
    def drumfork(cv):                                                     # drum pemindah (alur) + garpu ke cincin
        dc = (-0.6, 1.2, 1.0)
        ocyl(cv, dc, (1, 0, 0), 0.34, 1.9, '#9AA3B2', a, n=20, hub=0)
        for k in range(3):                                                # alur zig-zag pada drum, berputar
            pts = []
            for j in range(40):
                xx = -2.4 + 3.6 * j / 39; th = drum + k * 2.1 + 0.6 * math.sin(xx * 1.6 + k)
                pts.append(p3((xx, 1.2 + 0.345 * math.cos(th), 1.0 + 0.345 * math.sin(th))))
            cv.drawPath(poly(pts, False), P(col(NAVY2, 0.7 * a), stroke=2.5))
        fx = dog; f0 = p3((fx, 1.2, 1.32)); f1 = p3((fx, 0.42, ZM - 0.32)); f2 = p3((fx, 0.0, ZM - 0.52))
        cv.drawLine(f0[0], f0[1], f1[0], f1[1], P(col(NAVY, a), stroke=10)); cv.drawLine(f1[0], f1[1], f2[0], f2[1], P(col(NAVY, a), stroke=8))
        cv.drawCircle(f0[0], f0[1], 8, P(col(ORANGE, a)))
    items.append((-0.6 + 1.2 + 1.0 + 3.0, drumfork))
    for _, fn in sorted(items, key=lambda it: it[0]): fn(cv)
    if load > 0:                                                          # tekanan tenaga mesin di taring yang terkunci
        tx = (dog - 0.2) if dog < DOGN else (dog + 0.2)
        for k in range(3):
            th = sp_ + k * 2.1; e1, e2 = g.basis((1, 0, 0)); pc = p3(add((tx, YS, ZM), add(mul(e1, 0.4 * math.cos(th)), mul(e2, 0.4 * math.sin(th)))))
            cv.drawCircle(pc[0], pc[1], 14, P(col(ORANGE, 0.6 * load * a), blur=6)); cv.drawCircle(pc[0], pc[1], 5, P(col(YELLOW, load * a)))
    if crash > 0:
        cp = p3((dog - 0.25, YS + 0.3, ZM + 0.2)); sparks(cv, cp[0], cp[1], t, 17, crash * a, n=22, spread=120, up=False)
    if broken > 0:                                                        # taring patah terlempar
        bp_ = p3((dog - 0.3 + 1.2 * broken, YS + 0.6 + 1.5 * broken, ZM + 1.6 * broken - 2.6 * broken * broken))
        cv.save(); cv.translate(*bp_); cv.rotate(broken * 720); cv.drawRect(skia.Rect(-8, -6, 8, 6), P(col('#F2B25A', a))); cv.drawRect(skia.Rect(-8, -6, 8, 6), P(col(NAVY2, a), stroke=1.5)); cv.restore()
        cc = p3((0.1 + GH, YS + 0.2, ZM + 0.25))
        for k in range(4):
            ang = k * 1.3 + 0.4; cv.drawLine(cc[0], cc[1], cc[0] + 30 * math.cos(ang), cc[1] + 30 * math.sin(ang), P(col(RED, a * clamp(broken * 3)), stroke=3))

GB_F = (-0.9, 0.0, 2.7)
GBZ = 2.25
def gb_cam(cv, zoom=GBZ, sx=540, sy=900):
    f = P3(*GB_F); cam(cv, f[0], f[1], zoom, sx, sy); return f

# ------------------------------------------------------------ A: HOOK (0 - 7.42)
T_DIVE, T_FORCE, T_CRACK, T_RW, T_BACK, T_QS = 3.3, 3.75, 4.35, 4.95, 5.75, 5.85
def gA(cv, t):
    gb = eio(prog(t, T_DIVE, T_DIVE + 0.45))                               # 0 = motor, 1 = girboks
    if gb < 1:
        zoom = lerp(2.9, 2.5, eio(prog(t, 0.0, 2.6))) * lerp(1, 3.5, ei(gb)); f = P3(0.4, 0.0, 1.35 + 0.2 * gb); sx, sy = 540, 960
        cv.save(); cam(cv, f[0], f[1], zoom, sx, sy); layer(cv, 1 - gb)
        road(cv, t, 1.0, speed=11); lev = bump(prog(t, 1.4, 2.0))
        bike(cv, t, 1.0, lever=lev, foot=lev, sensor_glow=0.0)
        cv.restore(); cv.restore()
        speedlines(cv, t, (1 - gb) * 0.9)
        ka = eo(prog(t, 0.6, 0.9)) * (1 - prog(t, 2.9, 3.2))
        if ka > 0:
            p = scr(P3(1.42, 0.34, 2.12), f, zoom, sx, sy); label(cv, 'KOPLING NGGAK DITARIK', p[0], p[1], 760, 640, ka, sub='tangan kiri santai')
        ga_ = eo(prog(t, 3.02, 3.2)) * (1 - gb)
        if ga_ > 0: chip(cv, 'GAS TETAP DIBUKA', 540, 1340, ga_, size=28, bg=ORANGE)
    if gb > 0:
        rwb = prog(t, T_RW, T_BACK)
        if t < T_RW:
            dog = lerp(DOG3, DOG3 + 0.12, eo(prog(t, T_FORCE, T_CRACK))); crash = prog(t, T_FORCE, T_FORCE + 0.1) * (1 - prog(t, T_CRACK + 0.3, T_CRACK + 0.6)); broken = prog(t, T_CRACK, T_CRACK + 0.55)
            load = 1.0; ign = 1.0; glow = 0.0
        elif t < T_QS:
            k = 1 - eio(rwb); dog = lerp(DOG3, DOG3 + 0.12, k); crash = 0.0; broken = 0.55 * k if k > 0.05 else 0.0; load = 1.0; ign = 1.0; glow = 0.0
        else:
            ign = 0.0 if T_QS < t < T_QS + 0.35 else 1.0
            dog = lerp(DOG3, DOG4, eio(prog(t, T_QS + 0.05, T_QS + 0.3))); crash = 0.0; broken = 0.0; load = 0.0 if t < T_QS + 0.35 else 1.0
            glow = eo(prog(t, T_QS + 0.25, T_QS + 0.5)) * (1 - 0.5 * prog(t, 6.8, 7.3))
        shk = 12 * math.sin(t * 60) * bump(prog(t, T_CRACK, T_CRACK + 0.35))
        cv.save(); layer(cv, gb); cv.translate(shk, 0)
        f = gb_cam(cv, zoom=lerp(3.4, GBZ, eio(prog(t, T_DIVE, T_DIVE + 0.6))), sy=lerp(1000, 900, gb))
        gearbox(cv, t, 1.0, dog=dog, load=load, crash=crash, broken=broken, drum=0.0 if t < T_QS else 0.8 * eio(prog(t, T_QS, T_QS + 0.3)), glow34=glow, ign=ign)
        cv.restore(); cv.restore()
        fl = bump(prog(t, T_CRACK, T_CRACK + 0.3))
        if fl > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.25 * fl)))
        if T_FORCE - 0.2 < t < T_RW + 0.1: chip(cv, 'KALAU TANPA QUICK SHIFTER?', 540, 560, eo(prog(t, T_FORCE - 0.2, T_FORCE)) * (1 - prog(t, T_RW - 0.1, T_RW + 0.1)), size=28, bg=RED)
        if T_CRACK < t < T_RW + 0.1: text_c(cv, 'KRAK!', 360, 1180, 64, RED, eo(prog(t, T_CRACK, T_CRACK + 0.1)) * (1 - prog(t, T_RW - 0.05, T_RW + 0.1)), halo=1.0)
        if t > T_QS:
            hud(cv, 4 if t > T_QS + 0.25 else 3, ign, gb * eo(prog(t, T_QS, T_QS + 0.2)), x=870, y=330, glow=glow)
            p = scr(P3(DOG4, 0.4, ZM + 0.5), P3(*GB_F), GBZ, 540, 900); la = eo(prog(t, T_QS + 0.3, T_QS + 0.6)) * (1 - prog(t, 7.1, 7.42))
            label(cv, 'GIGI MASUK MULUS', p[0], p[1], 290, 1180, la, sub='busi padam sesaat')
            check(cv, 460, 1115, 24, prog(t, T_QS + 0.4, T_QS + 0.8), la)
    rewind_fx(cv, t, T_RW, T_BACK)
    for k, (num, txt) in enumerate((('1', 'SENSOR'), ('2', 'BUSI PADAM'), ('3', 'GIGI MASUK'))):
        q = prog(t, 6.3 + 0.15 * k, 6.6 + 0.15 * k)
        if q > 0:
            x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
            cv.save(); cv.translate(x, 1335); cv.scale(s_, s_); cv.translate(-x, -1335)
            card(cv, skia.Rect(x - 155, 1305, x + 155, 1365), aa, rad=30, lift=8)
            cv.drawCircle(x - 120, 1335, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 120, 1335, 24, WHITE, aa)
            text_c(cv, txt, x + 14, 1335, 24, INK, aa)
            cv.restore()

# ------------------------------------------------------------ B: sensor di batang pemindah gigi (7.42 - 13.817)
def gB(cv, t):
    a0 = eo(prog(t, 7.42, 7.8))
    zoom = lerp(3.3, 3.6, eio(prog(t, 7.42, 13.817))); f = P3(0.2, 0.45, 1.25); sx, sy = 560, 880
    lev = bump(prog(t, 10.4, 11.2)) + bump(prog(t, 12.3, 12.9))
    sg = eo(prog(t, 8.33, 8.7)) * 0.6 + lev * 0.6
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    road(cv, t, a0, speed=11); bike(cv, t, a0, lever=lev, foot=lev, sensor_glow=clamp(sg), wire=eo(prog(t, 12.3, 12.6)), ecu_glow=eo(prog(t, 12.5, 12.8)))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 8.33, 8.7))
    if la > 0: p = S((0.28, 0.46, 1.04)); label(cv, 'SENSOR', p[0], p[1], 820, 560, a0 * la, sub='di batang pemindah gigi')
    ta = eo(prog(t, 10.4, 10.7))
    if ta > 0:
        p = S((0.42, 0.5, 0.88)); label(cv, 'TUAS GIGI', p[0], p[1], 300, 1150, a0 * ta, dot=NAVY, sub='diinjak kaki')
        p2 = S((0.44, 0.5, 0.7)); arrow(cv, (p2[0], p2[1] + 70), (p2[0], p2[1] - 10), ORANGE, a0 * bump(prog(t, 10.3, 11.3)) * 1.2, w=9, head=22)
    ea = eo(prog(t, 12.3, 12.6))
    if ea > 0:
        p = S((-0.95, 0.4, 1.62)); label(cv, 'KOMPUTER MOTOR', p[0], p[1], 300, 520, a0 * ea, sub='menerima sinyal')
        chip(cv, 'SENSOR LANGSUNG TAHU', 540, 1340, a0 * eo(prog(t, 12.4, 12.7)), size=28, bg=ORANGE); check(cv, 790, 1340, 22, prog(t, 12.5, 12.9), a0 * ea)
    sp_ = eo(prog(t, 8.0, 8.3)) * (1 - prog(t, 13.5, 13.817))
    speedlines(cv, t, 0.5 * sp_)

# ------------------------------------------------------------ C: komputer memutus pengapian sesaat; gigi lepas dari tekanan (13.817 - 21.229)
T_CUT0, T_CUT1 = 14.9, 15.55
def spark_on(t):
    if T_CUT0 < t < T_CUT1: return 0.0
    ph = (t * 3.2) % 1.0
    return 1.0 if ph < 0.18 else 0.0
def engine_scene(cv, t, a):
    """mesin dibelah: silinder, piston naik-turun, busi di atas, komputer (ECU) dengan kabel"""
    box(cv, WORLD, -3.0, -2.0, -0.2, 6.0, 4.0, 0.2, '#D9CFBF', a, top=0.15)
    box(cv, WORLD, -1.4, -1.2, 0.0, 2.8, 1.2, 4.2, '#5A6B8C', a, top=0.3, left=0.05, right=-0.15)   # blok mesin (separuh belakang)
    face(cv, [(-1.4, 0.0, 0.0), (1.4, 0.0, 0.0), (1.4, 0.0, 4.2), (-1.4, 0.0, 4.2)], (0, 1, 0), '#3E4A60', a)
    face(cv, [(-0.75, 0.01, 1.4), (0.75, 0.01, 1.4), (0.75, 0.01, 3.7), (-0.75, 0.01, 3.7)], (0, 1, 0), '#C9CED8', a)    # dinding silinder
    ph = t * 3.2 * math.tau; pz = 2.15 + 0.55 * math.cos(ph)
    comb = spark_on(t) > 0 or (((t * 3.2) % 1.0) < 0.35 and not (T_CUT0 < t < T_CUT1 + 0.1))
    if comb:
        face(cv, [(-0.75, 0.02, pz + 0.55), (0.75, 0.02, pz + 0.55), (0.75, 0.02, 3.7), (-0.75, 0.02, 3.7)], (0, 1, 0), '#FFB066', a * 0.9)
    obox(cv, (0.0, -0.35, pz + 0.27), (1, 0, 0), (0, 1, 0), (0, 0, 1), 0.72, 0.35, 0.28, '#D9DEE7', a)   # piston
    cr = (0.0, -0.2, 0.75); ca = ph; pin = add(cr, (0.45 * math.sin(ca), 0.0, 0.45 * math.cos(ca)))
    q0, q1 = P3(*pin), P3(0.0, 0.02, pz); cv.drawLine(q0[0], q0[1], q1[0], q1[1], P(col('#8E9AAF', a), stroke=12))
    ocyl(cv, cr, (0, 1, 0), 0.6, 0.15, '#8E9AAF', a, n=24, spin=ca, hub=0.3)
    ocyl(cv, (0.0, -0.4, 4.45), (0, 0, 1), 0.12, 0.28, '#F2EEE8', a, n=12, hub=0)    # busi
    ocyl(cv, (0.0, -0.4, 4.1), (0, 0, 1), 0.17, 0.1, '#8E9AAF', a, n=6, hub=0)
    s = spark_on(t)
    if s > 0:
        sp = P3(0.0, 0.02, 3.62); cv.drawCircle(sp[0], sp[1], 26, P(col(YELLOW, 0.8 * a), blur=8))
        for k in range(8):
            ang = k * math.pi / 4; cv.drawLine(sp[0], sp[1], sp[0] + 30 * math.cos(ang), sp[1] + 30 * math.sin(ang), P(col(WHITE, a), stroke=3))
    obox(cv, (2.3, 0.6, 3.6), (1, 0, 0), (0, 1, 0), (0, 0, 1), 0.55, 0.32, 0.35, NAVY2, a)       # ECU
    pts = [P3(*q) for q in ((1.9, 0.6, 3.75), (1.2, 0.2, 4.7), (0.3, -0.4, 4.8), (0.0, -0.4, 4.73))]
    cv.drawPath(poly(pts, False), P(col(NAVY2, a), stroke=4))
    if T_CUT0 - 0.2 < t < T_CUT1:
        pth = poly(pts, False); m = skia.PathMeasure(pth, False); L = m.getLength(); u = prog(t, T_CUT0 - 0.2, T_CUT0); seg = skia.Path(); m.getSegment(L * max(0, u - 0.25), L * u, seg, True)
        cv.drawPath(seg, P(col(ORANGE, a), stroke=9, blur=3))
def gC(cv, t):
    a0 = eo(prog(t, 13.817, 14.2)); part2 = eio(prog(t, 18.2, 18.6))
    if part2 < 1:
        aa = a0 * (1 - part2)
        zoom = lerp(2.3, 2.45, eio(prog(t, 13.817, 18.4))); f = P3(0.6, 0.0, 2.5); sx, sy = 520, 900
        cv.save(); cam(cv, f[0], f[1], zoom, sx, sy); engine_scene(cv, t, aa); cv.restore()
        S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
        la = eo(prog(t, 14.0, 14.4))
        if la > 0: p = S((2.3, 0.9, 3.9)); label(cv, 'KOMPUTER MOTOR', p[0], p[1], 820, 470, aa * la, sub='mengatur pengapian')
        ba = eo(prog(t, 14.67, 15.0))
        if ba > 0: p = S((0.0, -0.4, 4.6)); label(cv, 'BUSI', p[0], p[1], 300, 470, aa * ba, dot=NAVY, sub='percikan api')
        if T_CUT0 < t < T_CUT1 + 0.3: chip(cv, 'PENGAPIAN DIPUTUS', 540, 1340, aa * eo(prog(t, T_CUT0, T_CUT0 + 0.15)) * (1 - prog(t, T_CUT1, T_CUT1 + 0.3)), size=28, bg=RED)
        hud(cv, 3, 0.0 if T_CUT0 < t < T_CUT1 else 1.0, aa * eo(prog(t, 14.3, 14.6)), x=870, y=330)
        ma = eo(prog(t, 17.19, 17.5))
        if ma > 0:                                                        # garis waktu percikan + celah sesaat
            r = skia.Rect(150, 1200, 930, 1300); card(cv, r, aa * ma, rad=26)
            for k in range(14):
                x = r.left() + 40 + k * 52; gap = 7 <= k <= 8
                if not gap: cv.drawLine(x, r.bottom() - 25, x, r.top() + 25, P(col(ORANGE, aa * ma), stroke=6))
            cv.drawRoundRect(skia.Rect(r.left() + 40 + 6.5 * 52, r.top() + 18, r.left() + 40 + 8.5 * 52, r.bottom() - 18), 10, 10, P(col(RED, 0.18 * aa * ma)))
            text_c(cv, '≈ MILIDETIK', r.left() + 40 + 7.5 * 52, r.top() - 22, 26, RED, aa * ma, halo=1.0)
    if part2 > 0:
        aa = a0 * part2; unload = eo(prog(t, 18.9, 19.6))
        cv.save(); gb_cam(cv, zoom=lerp(2.5, 2.65, eio(prog(t, 18.4, 21.229))), sx=600, sy=900)
        gearbox(cv, t, aa, dog=DOG3, load=1 - unload)
        cv.restore()
        hud(cv, 3, 0.0, aa, x=870, y=330)
        pa = eo(prog(t, 18.5, 18.8))
        if pa > 0:
            p = scr(P3(DOG3 - 0.2, 0.3, ZM + 0.4), P3(*GB_F), lerp(2.5, 2.65, eio(prog(t, 18.4, 21.229))), 600, 900)
            label(cv, 'TARING PENGUNCI', p[0], p[1], 300, 500, aa * pa, sub='tadinya ditekan tenaga mesin')
        ua = eo(prog(t, 19.6, 19.9))
        if ua > 0: chip(cv, 'TEKANAN HILANG', 540, 1340, aa * ua, size=30, bg=ORANGE); check(cv, 735, 1340, 22, prog(t, 19.7, 20.1), aa * ua)

# ------------------------------------------------------------ D: gigi lama lepas, gigi berikutnya masuk, mulus tanpa kopling (21.229 - 28.142)
def gD(cv, t):
    a0 = eo(prog(t, 21.229, 21.6))
    out = eio(prog(t, 22.96, 23.4)); inn = eio(prog(t, 23.78, 24.2))
    dog = lerp(lerp(DOG3, DOGN, out), DOG4, inn)
    glow = eo(prog(t, 24.1, 24.4)) * (0.7 + 0.3 * math.sin(t * 5))
    zoom = lerp(2.3, 2.42, eio(prog(t, 21.229, 28.142)))
    cv.save(); f = gb_cam(cv, zoom=zoom, sx=560, sy=900)
    gearbox(cv, t, a0, dog=dog, load=1.0 if (t < 22.96 or t > 24.3) else 0.0, drum=0.8 * inn + 0.4 * out, glow34=glow, clutch_x=eo(prog(t, 25.74, 26.0)))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, 560, 900)
    hud(cv, 4 if inn > 0.5 else 3, 0.0 if 22.9 < t < 24.25 else 1.0, a0, x=870, y=330, glow=glow)
    oa = eo(prog(t, 22.96, 23.3)) * (1 - prog(t, 23.7, 23.9))
    if oa > 0: p = S((GEARS[2][0], 0.5, ZM + 0.6)); label(cv, 'GIGI 3 LEPAS', p[0], p[1], 280, 560, a0 * oa, dot=NAVY)
    ia = eo(prog(t, 23.78, 24.1))
    if ia > 0: p = S((GEARS[3][0], 0.5, ZM + 0.7)); label(cv, 'GIGI 4 MASUK', p[0], p[1], 280, 560, a0 * ia * (1 - prog(t, 25.5, 25.74)))
    da = eo(prog(t, 22.03, 22.4)) * (1 - prog(t, 22.9, 23.1))
    if da > 0: p = S((-0.6, 1.5, 1.2)); label(cv, 'DRUM & GARPU', p[0], p[1], 800, 1180, a0 * da, dot=NAVY, sub='menggeser cincin pengunci')
    ka = eo(prog(t, 25.74, 26.0))
    if ka > 0:
        p = S((-3.85, 0.0, ZM + 1.0)); label(cv, 'KOPLING', p[0], p[1], 300, 520, a0 * ka, dot=RED, sub='nggak dipakai')
        chip(cv, 'MULUS TANPA KOPLING', 540, 1340, a0 * eo(prog(t, 25.85, 26.15)), size=30, bg=ORANGE); check(cv, 790, 1340, 22, prog(t, 25.95, 26.35), a0 * ka)

# ------------------------------------------------------------ E: awalnya dibuat untuk balap motor (28.142 - 33.566)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def race_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'SIRKUIT BALAP', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    trk = skia.Path(); trk.moveTo(r.left(), 900); trk.cubicTo(400, 760, 720, 980, r.right(), 820)              # lintasan melengkung
    cv.drawPath(trk, P(col('#B8A07C', a), stroke=150)); cv.drawPath(trk, P(col(SEPIA_INK, 0.5 * a), stroke=3, effect=skia.DashPathEffect.Make([30, 22], -t * 200)))
    for k in range(18):
        x = r.left() + k * 52; cv.drawRect(skia.Rect(x, 1000 + 0.12 * (x - 540) * 0, x + 26, 1018), P(col(ORANGE_D if k % 2 else '#FBF3E2', a)))
    bx, by = 520 + 30 * math.sin(t * 1.5), 830                            # motor balap miring di tikungan (siluet)
    cv.save(); cv.translate(bx, by); cv.rotate(-5)
    for wx in (-88, 92):
        cv.drawCircle(wx, 42, 40, P(col(SEPIA_INK, a))); cv.drawCircle(wx, 42, 24, P(col('#D9BF92', a))); cv.drawCircle(wx, 42, 8, P(col(SEPIA_INK, a)))
    bodyp = poly([(-128, 4), (-96, -34), (-30, -46), (28, -40), (74, -60), (128, -38), (138, 0), (96, 18), (20, 24), (-60, 22)])
    cv.drawPath(bodyp, P(col('#C98A4A', a))); cv.drawPath(bodyp, ink(1, 3.5))
    cv.drawLine(-110, -6, 120, -18, P(col('#FBF3E2', a), stroke=6))
    cv.drawPath(poly([(96, -48), (128, -76), (140, -44)]), P(col('#E6D3AE', a))); cv.drawPath(poly([(96, -48), (128, -76), (140, -44)]), ink(1, 2.5))
    rid = poly([(-70, -44), (-10, -86), (52, -96), (70, -66), (20, -48)]); cv.drawPath(rid, P(col(SEPIA_INK, a)))
    cv.drawCircle(62, -104, 24, P(col('#C98A4A', a))); cv.drawCircle(62, -104, 24, ink(1, 3)); cv.drawLine(66, -112, 86, -104, P(col(SEPIA_INK, a), stroke=6))
    cv.drawLine(-40, 30, -60, 70, ink(1, 8))                               # lutut menyentuh aspal
    cv.restore()
    fx0, fy0 = 230, 360                                                    # bendera finish kotak-kotak
    cv.drawLine(fx0, fy0, fx0, fy0 + 230, ink(1, 6))
    for i in range(4):
        for j in range(3):
            wv = 6 * math.sin(t * 5 + i * 0.8)
            cv.drawRect(skia.Rect(fx0 + i * 34, fy0 + j * 30 + wv, fx0 + (i + 1) * 34, fy0 + (j + 1) * 30 + wv), P(col(SEPIA_INK if (i + j) % 2 else '#FBF3E2', a)))
    sx_, sy_ = 790, 480                                                    # stopwatch
    cv.drawCircle(sx_, sy_, 86, P(col('#FBF3E2', a))); cv.drawCircle(sx_, sy_, 86, ink(1, 7)); cv.drawRect(skia.Rect(sx_ - 16, sy_ - 116, sx_ + 16, sy_ - 92), P(col(SEPIA_INK, a)))
    for k in range(12):
        ang = k * math.tau / 12; cv.drawLine(sx_ + 66 * math.cos(ang), sy_ + 66 * math.sin(ang), sx_ + 78 * math.cos(ang), sy_ + 78 * math.sin(ang), ink(1, 3))
    ang = -math.pi / 2 + t * 4.0; cv.drawLine(sx_, sy_, sx_ + 60 * math.cos(ang), sy_ + 60 * math.sin(ang), P(col(ORANGE_D, a), stroke=6)); cv.drawCircle(sx_, sy_, 8, P(col(SEPIA_INK, a)))
    for k in range(5):                                                    # garis kecepatan
        y = 760 + k * 22; cv.drawLine(bx - 280 - k * 30, y, bx - 160 - k * 30, y + 10, ink(0.5, 3))
    cv.restore()
def gE(cv, t):
    a0 = eo(prog(t, 28.142, 28.5))
    zz = 1.14 + 0.03 * eio(prog(t, 28.142, 33.566))
    cv.save(); cv.translate(540, 770); cv.scale(zz, zz); cv.translate(-540, -700)
    race_card(cv, t, a0)
    cv.restore()
    ba = eo(prog(t, 29.18, 29.5))
    if ba > 0: chip(cv, 'AWALNYA UNTUK BALAP', 540, 330, a0 * ba, size=28, bg=INK)
    sa = eo(prog(t, 30.91, 31.25))
    if sa > 0:                                                            # waktu ganti gigi: kopling vs quick shifter (tanpa angka)
        r = skia.Rect(170, 1040, 910, 1250); card(cv, r, a0 * sa, rad=28)
        mono(cv, 'WAKTU GANTI GIGI', 540, r.top() + 36, 20, MUTED, a0 * sa, sp=3)
        for i, (nm, frac, c) in enumerate((('PAKAI KOPLING', 0.9, NAVY), ('QUICK SHIFTER', 0.32, ORANGE))):
            y = r.top() + 92 + i * 66; grow = eo(prog(t, 31.0 + 0.3 * i, 31.6 + 0.3 * i))
            text_c(cv, nm, 330, y, 22, c, a0 * sa)
            cv.drawRoundRect(skia.Rect(450, y - 16, 870, y + 16), 16, 16, P(col('#EEE6DA', a0 * sa)))
            cv.drawRoundRect(skia.Rect(450, y - 16, 450 + 420 * frac * grow, y + 16), 16, 16, P(col(c, a0 * sa)))
        if t > 32.2: chip(cv, 'LEBIH CEPAT', 540, 1340, a0 * eo(prog(t, 32.2, 32.5)), size=30, bg=ORANGE)

# ------------------------------------------------------------ F: di Indonesia, motor sport 250 cc pun sudah ada yang memakainya (33.566 - 38.858)
def gF(cv, t):
    a0 = eo(prog(t, 33.566, 33.95))
    zoom = lerp(1.45, 1.55, eio(prog(t, 33.566, 38.858))); f = P3(0.5, 0.2, 1.4); sx, sy = 560, 900
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    road(cv, t, a0, speed=10)
    for k, (dx, dy, paint) in enumerate(((-4.4, -1.2, (NAVY, ORANGE)), (0.4, 1.2, (ORANGE, NAVY)), (4.6, -1.0, ('#F6F2EC', ORANGE_D)))):
        cv.save(); o = P3(0, dy, 0); cv.translate(o[0], o[1])
        bike(cv, t + k * 0.3, a0, x0=dx + 0.25 * math.sin(t * 1.2 + k), paint=paint, rider=True)
        cv.restore()
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    ia = eo(prog(t, 33.92, 34.25))
    if ia > 0: chip(cv, 'DI INDONESIA', 540, 330, a0 * ia, size=28, bg=INK)
    ca = eo(prog(t, 35.52, 35.85))
    if ca > 0: chip(cv, 'MOTOR SPORT 250 cc', 540, 1340, a0 * ca, size=30, bg=ORANGE)
    qa = eo(prog(t, 37.05, 37.4))
    if qa > 0:
        p = S((0.4 + 0.3, 1.2 + 0.5, 1.1)); label(cv, 'QUICK SHIFTER', p[0], p[1], 800, 560, a0 * qa, sub='sudah ada yang pakai')
        check(cv, 960, 495, 24, prog(t, 37.15, 37.55), a0 * qa)

# ------------------------------------------------------------ G: request dari kalian + komentar (38.858 - 43.243)
CMTS = [('ABS dong!', 280, 790, 40.5, ORANGE), ('motor matic!!', 760, 920, 40.75, INK), ('kopling gimana?', 320, 1050, 41.0, ORANGE_D), ('KRL pls', 760, 1180, 41.25, NAVY)]
def gG(cv, t):
    a0 = eo(prog(t, 38.858, 39.15))
    logo_mark(cv, 540, 420, 80 * lerp(0.6, 1, bo(prog(t, 38.858, 39.25))), a0, t)
    ra = eo(prog(t, 39.0, 39.35))
    if ra > 0:
        s_ = lerp(1.4, 1.0, eo(prog(t, 39.0, 39.35))); cv.save(); cv.translate(540, 580); cv.rotate(-4); cv.scale(s_, s_)
        rr = skia.Rect(-250, -44, 250, 44); cv.drawRoundRect(rr, 22, 22, P(col(ORANGE, a0 * ra))); text_c(cv, 'REQUEST DARI KALIAN', 0, 0, 34, WHITE, a0 * ra); cv.restore()
        check(cv, 820, 560, 26, prog(t, 39.2, 39.6), a0 * ra)
    text_c(cv, 'BONGKAR APA LAGI?', 540, 690, 56, INK, a0 * eo(prog(t, 40.36, 40.6)))
    for txt, x, y, t0, c in CMTS:
        q = prog(t, t0, t0 + 0.3)
        if q <= 0: continue
        aa = a0 * clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
        r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, aa, rad=42, lift=10)
        cv.drawCircle(r.left() + 42, 0, 24, P(col(c, aa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, aa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, aa)))
        cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, aa)))
        cv.restore()
    ca = eo(prog(t, 41.98, 42.25))
    if ca > 0: chip(cv, 'TULIS DI KOMENTAR', 540, 1340, a0 * ca, size=30, bg=ORANGE)

def gJ(cv, t):
    tt = t - 43.243; a = eo(prog(tt, 0.0, 0.4)); p_ = bo(prog(tt, 0.0, 0.6))
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
    ev = [(0.0, 'whoosh'), (0.05, 'grind'), (1.3, 'grind'), (1.45, 'tick'), (1.7, 'clunk'), (3.02, 'zoom'), (3.3, 'whoosh'), (3.75, 'buzzer'), (3.8, 'grind'), (3.85, 'fizz'),
          (4.35, 'crack'), (4.37, 'chop'), (4.4, 'rumble'), (4.95, 'rewind'), (5.85, 'zap2'), (6.0, 'clunk'), (6.05, 'shine'), (6.15, 'ding'), (6.3, 'pop'), (6.45, 'pop'), (6.6, 'pop'),
          (7.42, 'whoosh'), (7.6, 'grind'), (8.33, 'pop'), (8.4, 'zap'), (10.4, 'tick'), (10.7, 'clunk'), (12.3, 'beep'), (12.45, 'zap'), (12.55, 'ding'),
          (13.817, 'whoosh'), (14.0, 'pop'), (14.2, 'tick'), (14.5, 'tick'), (14.67, 'pop'), (14.9, 'stamp'), (15.55, 'tick'), (15.85, 'tick'), (17.19, 'card'), (17.3, 'beep'),
          (18.2, 'swish'), (18.5, 'pop'), (19.6, 'shine'), (19.7, 'ding'),
          (21.229, 'whoosh'), (22.03, 'pop'), (22.96, 'swish'), (23.0, 'clunk'), (23.78, 'clunk'), (23.85, 'ding'), (25.74, 'buzzer'), (25.85, 'stamp'), (25.95, 'ding'),
          (28.142, 'whoosh'), (28.2, 'card'), (29.18, 'pop'), (30.91, 'card'), (31.0, 'rise'), (32.2, 'ding'),
          (33.566, 'whoosh'), (33.6, 'grind'), (33.92, 'pop'), (35.52, 'pop'), (35.6, 'grind'), (37.05, 'pop'), (37.15, 'ding'),
          (38.858, 'whoosh'), (39.0, 'stamp'), (39.2, 'shine'), (40.36, 'pop'), (40.5, 'pop'), (40.75, 'pop'), (41.0, 'pop'), (41.25, 'pop'), (41.98, 'pop'),
          (43.243, 'whoosh'), (43.39, 'boing'), (43.74, 'shine'), (43.99, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
