#!/usr/bin/env python3
"""Bongkar Benda #06: 'Roller coaster, kok nggak jatuh pas terbalik?'
Diorama taman hiburan isometrik dengan putaran (loop) berbentuk tetes (klotoid: sempit di atas, lebar di bawah), kereta 3D berorientasi bebas
(bisa terbalik) + penumpang. Hook: kereta terbalik di puncak; kalau rodanya cuma di atas rel, kereta lepas & jatuh -> REWIND -> roda bawah menyala.
Alasan 1: roda menjepit rel dari atas, samping, bawah (close-up). Alasan 2: di puncak kereta melaju kencang, badan tertekan ke kursi.
Alasan 3: putaran tidak bulat (perbandingan lingkaran vs tetes, gaya di dasar). Sejarah: John Miller, paten roda bawah 1919.
Penutup: putaran pertama di Coney Island (1895) bulat, penumpang sakit leher. Sumber: content/EP06_rollercoaster.md
python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, YELLOW, RED, WHITE, text_c, mono, card, chip, label, check, logo_mark)
from iso import Iso, tone, quad, box, shadow, poly, ring_pts

bb.DUR = 45.131
bb.TITLE = ('Roller coaster,', 'kok nggak jatuh?'); bb.TITLE_OUT = 4.4
bb.GROUPS = [(0.0, 6.275, 'A'), (6.275, 13.804, 'B'), (13.804, 19.771, 'C'), (19.771, 26.783, 'D'), (26.783, 31.321, 'E'),
             (31.321, 36.559, 'F'), (36.559, 39.931, 'G'), (39.931, 45.131, 'J')]
bb.PHRASES = [(0.15, 'Kereta ini [terbalik]'), (1.3, 'di atas kepala.'), (2.9, 'Penumpangnya kok nggak [jatuh]?'), (4.46, 'Ini [alasannya].'),
              (6.275, '[Pertama],'), (7.23, 'rodanya [menjepit rel] dari tiga sisi:'), (9.3, '[atas], [samping], dan [bawah].'), (11.57, 'Jadi keretanya [nggak bisa lepas].'),
              (13.804, '[Kedua],'), (14.74, 'di [puncak],'), (15.33, 'kereta [melaju kencang].'), (16.56, 'Badanmu justru [tertekan ke kursi],'), (18.44, 'bukan [jatuh].'),
              (19.771, '[Ketiga],'), (20.62, 'putarannya nggak [bulat sempurna].'), (22.17, 'Atasnya [sempit],'), (23.21, 'bawahnya [lebar],'), (24.25, 'supaya badanmu nggak [tertekan berlebihan].'),
              (26.783, 'Roda penjepit dari bawah ini'), (28.1, 'dipatenkan [John Miller],'), (29.52, 'tahun [1919].'),
              (31.321, 'Dulu, putaran pertama di [Coney Island]'), (33.3, 'bentuknya [bulat],'), (34.3, 'dan penumpangnya sampai [sakit leher].'),
              (36.559, 'Benda apa yang mau kamu [bongkar] berikutnya?'), (38.63, 'Tulis di [komentar]!'),
              (39.931, 'Follow [Bongkar Benda],'), (41.15, 'biar makin paham [cara kerja benda] di sekitarmu.')]

WORLD = Iso(0, 0, 50)
NAVY, NAVY2 = '#2A3F6B', '#1A2A4C'
RAIL, CREAMW = '#D9DEE7', '#F6F2EC'

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

# ------------------------------------------------------------ alat 3D kecil: vektor, muka bernormal (backface culling), balok & silinder berorientasi
VIEW = (1.0, 1.0, 1.0)
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def nrm(a): l = math.sqrt(dot(a, a)) or 1.0; return (a[0] / l, a[1] / l, a[2] / l)
def crs(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
LIGHT = nrm((-0.4, 0.3, 1.0))
def shade(c, n, k0=-0.12, k1=0.42): return tone(c, k0 + k1 * dot(n, LIGHT))
def face(cv, pts, n, c, a, glow=0.0, edge=None):
    if a <= 0 or dot(n, VIEW) <= 1e-6: return
    pth = poly([P3(*p) for p in pts]); cv.drawPath(pth, P(col(shade(c, n), a)))
    if edge: cv.drawPath(pth, P(col(edge, 0.6 * a), stroke=1.2))
    if glow > 0: cv.drawPath(pth, P(col(ORANGE, 0.75 * glow * a)))
def obox(cv, c, u, v, w, hu, hv, hw, col_, a, glow=0.0, cols=None):
    """balok berorientasi: sumbu u, v, w (ortonormal), setengah-ukuran hu, hv, hw"""
    for n, ctr, e1, e2, key in ((u, mul(u, hu), mul(v, hv), mul(w, hw), 'u'), (mul(u, -1), mul(u, -hu), mul(v, hv), mul(w, hw), '-u'),
                                (v, mul(v, hv), mul(u, hu), mul(w, hw), 'v'), (mul(v, -1), mul(v, -hv), mul(u, hu), mul(w, hw), '-v'),
                                (w, mul(w, hw), mul(u, hu), mul(v, hv), 'w'), (mul(w, -1), mul(w, -hw), mul(u, hu), mul(v, hv), '-w')):
        fc = add(c, ctr); pts = [sub(sub(fc, e1), e2), sub(add(fc, e1), e2), add(add(fc, e1), e2), add(sub(fc, e1), e2)]
        face(cv, pts, n, (cols or {}).get(key, col_), a, glow)
def basis(ax):
    t = (0, 0, 1) if abs(ax[2]) < 0.9 else (1, 0, 0)
    e1 = nrm(crs(ax, t)); e2 = crs(ax, e1); return e1, e2
def ocyl(cv, c, ax, r, h, col_, a, n=20, spin=None, glow=0.0, cap_col=None):
    """silinder berorientasi (pusat c, sumbu ax, jari-jari r, setengah-panjang h); spin = sudut jari-jari roda"""
    if a <= 0: return
    e1, e2 = basis(ax)
    d = [add(mul(e1, math.cos(math.tau * i / n)), mul(e2, math.sin(math.tau * i / n))) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n; nm = nrm(add(d[i], d[j]))
        pts = [add(add(c, mul(ax, -h)), mul(d[i], r)), add(add(c, mul(ax, h)), mul(d[i], r)), add(add(c, mul(ax, h)), mul(d[j], r)), add(add(c, mul(ax, -h)), mul(d[j], r))]
        face(cv, pts, nm, col_, a, glow)
    for sgn in (1, -1):
        nm = mul(ax, sgn)
        if dot(nm, VIEW) <= 0: continue
        cc = add(c, mul(ax, sgn * h)); pts = [add(cc, mul(di, r)) for di in d]
        face(cv, pts, nm, cap_col or tone(col_, 0.1), a, glow)
        inner = [add(cc, mul(di, r * 0.55)) for di in d]; cv.drawPath(poly([P3(*p) for p in inner]), P(col(tone(cap_col or col_, -0.25), a), stroke=1.5))
        if spin is not None:
            for k in range(3):
                th = spin + k * math.tau / 3; dd = add(mul(e1, math.cos(th)), mul(e2, math.sin(th)))
                p0, p1 = P3(*add(cc, mul(dd, r * 0.18))), P3(*add(cc, mul(dd, r * 0.8))); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(tone(cap_col or col_, -0.35), a), stroke=max(1.5, r * 12)))

# ------------------------------------------------------------ lintasan: lurus -> putaran tetes (klotoid) -> lurus
CX, Z0, LW, LH, YD = 0.0, 1.9, 4.4, 10.4, 0.7
RL = 0.36                                                             # jarak rel dari sumbu (lateral y)
def loop_pt(phi, shape=1.0):
    k = 1 - 0.40 * shape * (1 - math.cos(phi)) / 2
    return (CX + LW * math.sin(phi) * k, -YD + 2 * YD * phi / math.tau, Z0 + LH * (1 - math.cos(phi)) / 2)
RAW = [(lerp(-19, CX, i / 80), -YD, Z0) for i in range(80)] + [loop_pt(math.tau * i / 300) for i in range(300)] + [(lerp(CX, 19, i / 80), YD, Z0) for i in range(81)]
SL = [0.0]
for a_, b_ in zip(RAW[:-1], RAW[1:]): SL.append(SL[-1] + math.sqrt(dot(sub(b_, a_), sub(b_, a_))))
LTOT = SL[-1]; S_LOOP0 = SL[80]; S_TOP = SL[80 + 150]; S_LOOP1 = SL[380]
def at(s):
    s = clamp(s, 0.0, LTOT); lo, hi = 0, len(SL) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if SL[m] <= s: lo = m
        else: hi = m
    u = (s - SL[lo]) / max(SL[hi] - SL[lo], 1e-9); p = add(RAW[lo], mul(sub(RAW[hi], RAW[lo]), u))
    i0, i1 = max(lo - 2, 0), min(hi + 2, len(RAW) - 1); d = sub(RAW[i1], RAW[i0])
    T = nrm((d[0], 0.0, d[2])); N = (-T[2], 0.0, T[0])
    return p, T, N
YAX = (0.0, 1.0, 0.0)

def track_items(items, a, glow=0.0, ghost_circle=0.0, seg_from=0, seg_to=None):
    """potong lintasan per segmen jadi item (kedalaman, fungsi gambar) supaya bisa diurutkan bersama kereta & tiang"""
    n = len(RAW) - 1; seg_to = seg_to or n; step = 2
    for i in range(seg_from, seg_to, step):
        j = min(i + step, n)
        pa, Ta, Na = at(SL[i]); pb, Tb, Nb = at(SL[j]); mid = mul(add(pa, pb), 0.5)
        def fn(cv, pa=pa, pb=pb, Na=Na, Nb=Nb, i=i):
            sa, sb = P3(*sub(pa, mul(Na, 0.34))), P3(*sub(pb, mul(Nb, 0.34)))
            cv.drawLine(sa[0], sa[1], sb[0], sb[1], P(col(ORANGE_D, a), stroke=16)); cv.drawLine(sa[0], sa[1], sb[0], sb[1], P(col(ORANGE, a), stroke=11))
            if glow > 0: cv.drawLine(sa[0], sa[1], sb[0], sb[1], P(col(ORANGE, 0.6 * glow * a), stroke=30, blur=10))
            if i % 6 == 0:
                for sg in (-1, 1):
                    r_ = P3(*add(pa, mul(YAX, sg * RL))); cv.drawLine(sa[0], sa[1], r_[0], r_[1], P(col(NAVY, a), stroke=4))
            for sg in (-1, 1):
                ra, rb = P3(*add(pa, mul(YAX, sg * RL))), P3(*add(pb, mul(YAX, sg * RL)))
                cv.drawLine(ra[0], ra[1], rb[0], rb[1], P(col(tone(RAIL, -0.25), a), stroke=7)); cv.drawLine(ra[0], ra[1] - 1.5, rb[0], rb[1] - 1.5, P(col(WHITE, 0.9 * a), stroke=2.5))
        items.append((dot(mid, VIEW), fn))

def support_items(items, a):
    for x, y in ((-15, -YD), (-11, -YD), (-7, -YD), (-3.4, -YD), (3.6, YD), (7.5, YD), (11.5, YD), (15.5, YD)):
        def fn(cv, x=x, y=y): box(cv, WORLD, x - 0.2, y - 0.2, 0, 0.4, 0.4, Z0 - 0.5, NAVY, a, top=0.3, left=0.05, right=-0.2); box(cv, WORLD, x - 0.4, y - 0.4, 0, 0.8, 0.8, 0.18, '#C9C2B6', a)
        items.append((x + y + Z0 * 0.3, fn))
    for phi in (math.pi * 0.5, math.pi * 1.5):                             # kaki penyangga sisi putaran
        p = loop_pt(phi); x, y, z = p
        def fn(cv, x=x, y=y, z=z):
            for dy in (-1.4, 1.4):
                p0, p1 = P3(x, y + dy, 0), P3(x, y, z - 0.35)
                cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=12)); cv.drawLine(p0[0] - 2, p0[1], p1[0] - 2, p1[1], P(col('#5A6B8C', a), stroke=4))
            for dy in (-1.4, 1.4): box(cv, WORLD, x - 0.35, y + dy - 0.35, 0, 0.7, 0.7, 0.2, '#C9C2B6', a)
        items.append((x + y + 0.2, fn))

SHIRTS = [ORANGE, '#F6F2EC', '#5A6B8C', ORANGE_D, '#E8C9A0', NAVY]
def car_items(items, s, a, k=0, fall=None, upstop=1.0, wheel_glow=None, t=0.0, scared=0.0, press=0.0, detail=False, arms=1.0):
    """satu gerbong di posisi lintasan s (atau jatuh: fall = (pusat, u, w))"""
    if fall is None:
        p, T, N = at(s); u, w = T, N
    else:
        p, u, w = fall
    v = YAX
    base = p
    body_c = add(base, mul(w, 0.52))
    def body(cv):
        obox(cv, body_c, u, v, w, 0.8, 0.5, 0.22, CREAMW, a, cols={'u': NAVY if k == 0 else CREAMW, 'w': '#E6DFD3'})
        for sg in (-1, 1):                                                  # garis oranye di sisi gerbong
            pa, pb = P3(*add(add(body_c, mul(u, -0.78)), mul(v, sg * 0.505))), P3(*add(add(body_c, mul(u, 0.78)), mul(v, sg * 0.505)))
            if dot(mul(v, sg), VIEW) > 0: cv.drawLine(pa[0], pa[1], pb[0], pb[1], P(col(ORANGE, a), stroke=4))
    items.append((dot(body_c, VIEW), body))
    for row, ro in enumerate((0.36, -0.36)):                              # 2 baris x 2 kursi
        for si, sv in enumerate((-0.24, 0.24)):
            idx = (k * 4 + row * 2 + si) % len(SHIRTS)
            seat_c = add(add(add(base, mul(w, 0.92)), mul(u, ro - 0.2)), mul(v, sv))
            tor_c = add(add(add(base, mul(w, 0.92)), mul(u, ro)), mul(v, sv))
            head = add(add(add(base, mul(w, 1.32 - 0.06 * press)), mul(u, ro)), mul(v, sv))
            def rider(cv, seat_c=seat_c, tor_c=tor_c, head=head, idx=idx, sv=sv, ro=ro):
                obox(cv, seat_c, u, v, w, 0.05, 0.18, 0.3, NAVY, a)
                obox(cv, tor_c, u, v, w, 0.12, 0.13, 0.2, SHIRTS[idx], a)
                ph = P3(*head); jit = scared * 3 * math.sin(t * 50 + idx)
                cv.drawCircle(ph[0] + jit, ph[1], 6.8, P(col('#E8C9A0', a))); cv.drawCircle(ph[0] + jit, ph[1], 6.8, P(col(tone('#E8C9A0', -0.3), a), stroke=1.2))
                hair = P3(*add(head, mul(w, 0.06))); cv.drawCircle(hair[0] + jit, hair[1], 5.5, P(col(('#2A1F17', '#5A4030', '#2A1F17')[idx % 3], a)))
                cv.drawCircle(ph[0] + jit, ph[1] + 1.5, 5.6, P(col('#E8C9A0', a)))
                for sg in (-1, 1):                                          # tangan terangkat (atau memegang palang)
                    sh = add(add(tor_c, mul(w, 0.16)), mul(v, sg * 0.12))
                    hand = add(add(add(sh, mul(w, 0.42 * arms + 0.05)), mul(v, sg * 0.1 * arms)), mul(u, 0.12 * (1 - arms)))
                    p0, p1 = P3(*sh), P3(*hand); cv.drawLine(p0[0], p0[1], p1[0] + jit, p1[1], P(col('#E8C9A0', a), stroke=3.2))
                bar0, bar1 = P3(*add(add(tor_c, mul(u, 0.2)), mul(v, -0.12))), P3(*add(add(tor_c, mul(u, 0.2)), mul(v, 0.12)))
                cv.drawLine(bar0[0], bar0[1], bar1[0], bar1[1], P(col(ORANGE, a), stroke=3))
            items.append((dot(head, VIEW) - 0.01, rider))
    for bu in (0.48, -0.48):                                               # roda: atas, samping, bawah di kedua rel
        for sg in (-1, 1):
            rail = add(add(base, mul(u, bu)), mul(v, sg * RL))
            wg = (wheel_glow or {})
            parts = [('atas', add(rail, mul(w, 0.18)), v, 0.12), ('samping', add(rail, mul(v, sg * 0.19)), w, 0.1), ('bawah', add(rail, mul(w, -0.18)), v, 0.11)]
            for name, wc, ax, r in parts:
                aa = a * (upstop if name == 'bawah' else 1.0)
                if aa <= 0: continue
                def wheel(cv, wc=wc, ax=ax, r=r, aa=aa, name=name):
                    if detail: ocyl(cv, wc, ax, r, 0.05, '#3E4A60', aa, n=16, spin=t * 12, glow=wg.get(name, 0.0), cap_col='#5A6B8C')
                    else:
                        p_ = P3(*wc); cv.drawCircle(p_[0], p_[1], r * 50, P(col('#3E4A60', aa)))
                        if wg.get(name, 0) > 0: cv.drawCircle(p_[0], p_[1], r * 50, P(col(ORANGE, wg[name] * aa)))
                items.append((dot(wc, VIEW) + (0.02 if name == 'bawah' else 0), wheel))
            if detail:
                arm = add(base, mul(u, bu)); a0_ = P3(*add(arm, mul(w, 0.3))); a1_ = P3(*add(rail, mul(w, -0.18)))
                def frame(cv, arm=arm, rail=rail, sg=sg):
                    for e0, e1 in ((add(arm, mul(w, 0.3)), add(rail, mul(w, 0.18))), (add(rail, mul(v, sg * 0.19)), add(rail, mul(w, -0.18))), (add(arm, mul(w, 0.3)), add(rail, mul(v, sg * 0.19)))):
                        p0, p1 = P3(*e0), P3(*e1); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=6))
                items.append((dot(rail, VIEW) - 0.05, frame))
TRAIN_GAP = 1.78
def train_items(items, s_front, a, **kw):
    for k in range(3): car_items(items, s_front - k * TRAIN_GAP, a, k=k, **kw)

# ------------------------------------------------------------ diorama taman hiburan
def plaza(cv, t, a, x0=-20, x1=20, y0=-8, y1=8):
    box(cv, WORLD, x0, y0, -0.9, x1 - x0, y1 - y0, 0.9, '#E9DFD0', a, top=0.0, left=-0.03, right=-0.14, faces='lr')
    quad(cv, WORLD, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], '#F2E9DC', a, grad=((x0, y1, 0), (x1, y0, 0), '#F6EEE2', '#E8DCCB'))
    for k in range(int(x1 - x0) // 2 + 1):                                # ubin
        p0, p1 = P3(x0 + k * 2, y0, 0.001), P3(x0 + k * 2, y1, 0.001); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#D9CCBA', 0.6 * a), stroke=1.2))
    for k in range(int(y1 - y0) // 2 + 1):
        p0, p1 = P3(x0, y0 + k * 2, 0.001), P3(x1, y0 + k * 2, 0.001); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#D9CCBA', 0.6 * a), stroke=1.2))
    sh = poly([P3(CX + 5.2 * math.cos(th), 3.2 * math.sin(th), 0.002) for th in [math.tau * i / 40 for i in range(40)]])
    cv.drawPath(sh, P(col('#8C7A64', 0.22 * a), blur=18))
def scenery_items(items, t, a):
    rnd = random.Random(7)
    trees = [(-17.5, 5.5), (-13, 6.2), (-9.5, 5.6), (-16, -5.8), (-13, -6.2), (6.5, -6.0), (10.5, -6.5), (14.5, -5.5), (9, 6.0), (13.5, 6.4), (17.5, 5.2), (-2.5, 6.6), (2.8, -6.6)]
    for (x, y) in trees:
        hgt = rnd.uniform(1.6, 2.4); c = rnd.choice(('#F2A65A', '#E8894A', '#F4C27A', ORANGE_D))
        def fn(cv, x=x, y=y, hgt=hgt, c=c):
            box(cv, WORLD, x - 0.12, y - 0.12, 0, 0.24, 0.24, hgt * 0.5, '#8C6A4A', a, top=0.2)
            p = P3(x, y, hgt); r = 0.95 * 50
            cv.drawCircle(p[0], p[1] + 6, r, P(col('#3E2E22', 0.18 * a), blur=8))
            cv.drawCircle(p[0], p[1], r, P(shader=rg(p[0] - r * 0.35, p[1] - r * 0.4, r * 1.5, [col(tone(c, 0.25), a), col(tone(c, -0.15), a)])))
            sp_ = P3(x, y, 0.002); cv.drawOval(skia.Rect(sp_[0] - 34, sp_[1] - 12, sp_[0] + 34, sp_[1] + 12), P(col('#8C7A64', 0.2 * a), blur=4))
        items.append((x + y, fn))
    for (x, y) in ((-8, 3.5), (-1, 4.8), (6, 3.6), (12, 4.2), (-12, -3.8), (2, -4.6), (9, -3.9)):   # lampu taman
        def fn(cv, x=x, y=y):
            p0, p1 = P3(x, y, 0), P3(x, y, 2.2); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY, a), stroke=4))
            cv.drawCircle(p1[0], p1[1], 7, P(col('#FFE3A8', a))); cv.drawCircle(p1[0], p1[1], 16, P(col('#FFE3A8', 0.35 * a), blur=6))
        items.append((x + y, fn))
    def station(cv):                                                      # stasiun di awal lintasan
        box(cv, WORLD, -19.6, -2.6, 0, 4.2, 4.0, 0.6, '#D6CDBF', a, top=0.25)
        for x in (-19.3, -15.8):
            for y in (-2.3, 1.0):
                box(cv, WORLD, x, y, 0.6, 0.18, 0.18, 2.4, NAVY, a, top=0.25)
        box(cv, WORLD, -19.9, -2.9, 3.0, 4.8, 4.6, 0.25, ORANGE, a, top=0.3, left=0.05, right=-0.15)
        box(cv, WORLD, -19.6, -2.6, 3.25, 4.2, 4.0, 0.4, ORANGE_D, a, top=0.3)
    items.append((-18.0, station))

def world(cv, t, a, extra=None, track_glow=0.0, supports=True, scenery=True):
    plaza(cv, t, a)
    items = []
    track_items(items, a, track_glow)
    if supports: support_items(items, a)
    if scenery: scenery_items(items, t, a)
    if extra: extra(items)
    for _, fn in sorted(items, key=lambda it: it[0]): fn(cv)

# ------------------------------------------------------------ A: HOOK — terbalik di puncak; kalau roda cuma di atas rel: jatuh; REWIND; roda bawah menyala (0 - 6.275)
T_TOP, T_DET, T_HIT, T_RW, T_BACK, T_ZIN = 1.3, 1.4, 2.3, 2.45, 3.3, 3.35
V_HOOK = 10.0
GF = 30.0
def hook_front(t):
    if t < T_TOP: return S_TOP - V_HOOK * (T_TOP - t)
    if t < 4.5: return S_TOP
    return S_TOP + V_HOOK * 0.45 * (t - 4.5) ** 1.3
def fall_state(k, tau):
    """gerbong k jatuh tau detik setelah lepas di puncak"""
    p0, T, N = at(S_TOP - k * TRAIN_GAP)
    vel = mul(T, V_HOOK * 0.6); pz = add(p0, add(mul(vel, tau), (0, 0, -0.5 * GF * tau * tau)))
    pz = (pz[0], pz[1], max(pz[2], 0.25))
    ang = 1.8 * tau * (1 if k % 2 else -1)
    u = nrm(add(mul(T, math.cos(ang)), mul(N, math.sin(ang)))); w = nrm(add(mul(N, math.cos(ang)), mul(T, -math.sin(ang))))
    return pz, u, w
def gA(cv, t):
    falling = T_DET < t < T_BACK
    if t < T_HIT: tau = max(0.0, t - T_DET)
    elif t < T_RW: tau = T_HIT - T_DET
    else: tau = (T_HIT - T_DET) * (1 - eio(prog(t, T_RW, T_BACK)))
    up_a = 1.0 if not (T_DET - 0.15 < t < T_BACK) else (1 - prog(t, T_DET - 0.15, T_DET)) if t < T_HIT else eo(prog(t, T_RW + 0.4, T_BACK))
    zoom_in = eio(prog(t, T_ZIN, 4.2)) * (1 - eio(prog(t, 4.6, 5.6)))
    u0 = eio(prog(t, 0.0, 1.15))
    fp, _, _ = at(hook_front(t))
    topc = add(at(S_TOP - TRAIN_GAP)[0], (0, 0, 0.3))
    wide = (CX + 0.5, 0.0, Z0 + LH * 0.5 - 0.8)
    fw = tuple(lerp(lerp(fp[i], wide[i], u0), topc[i], zoom_in) for i in range(3))
    zoom = lerp(lerp(2.1, 1.12, u0), 4.0, zoom_in) * (1 + 0.03 * eio(prog(t, 5.0, 6.2)))
    hit = prog(t, T_HIT, T_HIT + 0.4); shk = 12 * math.sin(t * 60) * (1 - hit) if T_HIT < t < T_HIT + 0.4 else 0.0
    f = P3(*fw); sx, sy = 540 + shk, lerp(820, 900, zoom_in)
    glow = eo(prog(t, T_BACK + 0.1, T_BACK + 0.45)) * (1 - 0.5 * prog(t, 5.6, 6.2))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    def extra(items):
        if falling and t > T_DET:
            for k in range(3): car_items(items, 0, 1.0, k=k, fall=fall_state(k, tau), upstop=0.0, t=t, scared=1.0, arms=0.2)
        else:
            train_items(items, hook_front(t), 1.0, upstop=up_a, t=t, wheel_glow={'bawah': glow}, detail=zoom > 2.0, scared=0.0, arms=1.0)
    world(cv, t, 1.0, extra)
    if T_HIT - 0.02 < t < T_HIT + 0.6:                                     # debu tumbukan
        q = prog(t, T_HIT - 0.02, T_HIT + 0.6); rnd = random.Random(5)
        for k in range(18):
            ang = rnd.uniform(math.pi, math.tau); L = 40 + 140 * eo(q); c0 = P3(-2.5 + rnd.uniform(-2, 2), rnd.uniform(-1, 1), 0.2)
            cv.drawLine(c0[0], c0[1], c0[0] + math.cos(ang) * L, c0[1] + math.sin(ang) * L * 0.6, P(col('#D9C7AE', 0.8 * (1 - q)), stroke=7))
    cv.restore()
    fl = max(bump(prog(t, T_HIT, T_HIT + 0.3)), 0.5 * bump(prog(t, T_DET - 0.1, T_DET + 0.25)))
    if fl > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.22 * fl)))
    if T_DET - 0.15 < t < T_RW + 0.1: chip(cv, 'KALAU RODANYA CUMA DI ATAS REL?', 540, 560, eo(prog(t, T_DET - 0.15, T_DET)) * (1 - prog(t, T_RW - 0.1, T_RW + 0.1)), size=26, bg=RED)
    if T_HIT < t < T_RW + 0.1: text_c(cv, 'JATUH!', 540, 1220, 60, RED, eo(prog(t, T_HIT, T_HIT + 0.12)) * (1 - prog(t, T_RW - 0.05, T_RW + 0.1)), halo=1.0)
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
    if t > T_BACK + 0.1:
        p_, T_, N_ = at(S_TOP - TRAIN_GAP); wc = add(add(p_, mul(YAX, RL)), mul(N_, -0.18)); p = scr(P3(*wc), f, zoom, sx, sy)
        la = eo(prog(t, T_BACK + 0.15, T_BACK + 0.5)) * (1 - prog(t, 5.9, 6.275))
        label(cv, 'RODA BAWAH', p[0], p[1], 800, 640, la, sub='mengunci kereta ke rel')
        check(cv, 965, 575, 24, prog(t, T_BACK + 0.25, T_BACK + 0.65), la)
    for k, (num, txt) in enumerate((('1', 'RODA MENJEPIT'), ('2', 'KECEPATAN'), ('3', 'BENTUK TETES'))):
        q = prog(t, 4.7 + 0.15 * k, 5.0 + 0.15 * k)
        if q > 0:
            x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
            cv.save(); cv.translate(x, 1335); cv.scale(s_, s_); cv.translate(-x, -1335)
            card(cv, skia.Rect(x - 158, 1305, x + 158, 1365), aa, rad=30, lift=8)
            cv.drawCircle(x - 123, 1335, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 123, 1335, 24, WHITE, aa)
            text_c(cv, txt, x + 14, 1335, 22, INK, aa)
            cv.restore()

# ------------------------------------------------------------ B: roda menjepit rel dari atas, samping, bawah; nggak bisa lepas (6.275 - 13.804)
S_B = SL[40]
def gB(cv, t):
    a0 = eo(prog(t, 6.275, 6.65))
    sB = S_B + 0.35 * (t - 6.275)
    lift = 0.05 * eo(prog(t, 11.57, 11.8)) * (1 - prog(t, 12.6, 13.0)) * (0.6 + 0.4 * math.sin(t * 30))
    p_, T_, N_ = at(sB - TRAIN_GAP * 0)
    tgt = add(add(add(p_, mul(T_, 0.48)), mul(YAX, RL)), (0, 0, 0.2))
    zoom = lerp(5.0, 5.6, eio(prog(t, 6.275, 13.804))); f = P3(*tgt); sx, sy = 520, 900
    wg = {'atas': eo(prog(t, 9.3, 9.6)), 'samping': eo(prog(t, 10.1, 10.4)), 'bawah': eo(prog(t, 10.78, 11.1)) + 0.6 * eo(prog(t, 11.6, 11.9))}
    for k_ in wg: wg[k_] = clamp(wg[k_]) * (0.75 + 0.25 * math.sin(t * 5))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    def extra(items):
        for k in range(2):
            s = sB - k * TRAIN_GAP; p, T, N = at(s)
            car_items(items, 0, a0, k=k, fall=(add(p, (0, 0, lift)), T, N), t=t, detail=True, wheel_glow=wg, arms=0.0)
    world(cv, t, a0, extra, scenery=False)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    p, T, N = at(sB); rail = add(add(add(p, mul(T, 0.48)), mul(YAX, RL)), (0, 0, lift))
    for name, off, lx, ly, t0, sub_ in (('RODA ATAS', mul(N, 0.18), 300, 480, 9.3, 'menggelinding di atas rel'), ('RODA SAMPING', mul(YAX, 0.19), 820, 760, 10.1, 'menahan ke kiri-kanan'),
                                        ('RODA BAWAH', mul(N, -0.18), 300, 1180, 10.78, 'mengunci dari bawah')):
        q = eo(prog(t, t0, t0 + 0.35))
        if q > 0: pp = S(add(rail, off)); label(cv, name, pp[0], pp[1], lx, ly, a0 * q, sub=sub_)
    ra = eo(prog(t, 7.23, 7.6)) * (1 - prog(t, 9.1, 9.4))
    if ra > 0: pp = S(add(add(p, mul(T, 1.4)), mul(YAX, RL))); label(cv, 'REL BAJA', pp[0], pp[1], 820, 500, a0 * ra, dot=NAVY, sub='bentuk pipa')
    la = eo(prog(t, 11.57, 11.85))
    if la > 0:
        pp = S(add(add(p, mul(N, 1.6)), mul(T, 0.2))); arrow(cv, (pp[0], pp[1] + 10), (pp[0], pp[1] - 150), RED, a0 * la * (1 - prog(t, 12.6, 13.0)), w=10, head=26)
        text_c(cv, 'TARIK?', pp[0] + 90, pp[1] - 110, 30, RED, a0 * la * (1 - prog(t, 12.6, 13.0)), halo=1.0)
        chip(cv, 'NGGAK BISA LEPAS', 540, 1340, a0 * eo(prog(t, 11.7, 12.0)), size=30, bg=ORANGE); check(cv, 760, 1340, 22, prog(t, 11.8, 12.2), a0 * la)
    ca = eo(prog(t, 7.23, 7.6)) * (1 - prog(t, 11.4, 11.6))
    if ca > 0: chip(cv, 'JEPIT DARI 3 SISI', 540, 1340, a0 * ca, size=28, bg=INK)

# ------------------------------------------------------------ C: di puncak kereta melaju kencang; badan tertekan ke kursi, bukan jatuh (13.804 - 19.771)
def c_front(t):
    """lambat di puncak (gerak lambat), gerbong tengah tepat di puncak saat 'tertekan ke kursi'"""
    u = prog(t, 13.804, 19.771); w = u - 0.13 * math.sin(math.tau * (u - 0.5))
    return S_TOP + TRAIN_GAP + lerp(-5.5, 5.5, w)
def gC(cv, t):
    a0 = eo(prog(t, 13.804, 14.2))
    sf = c_front(t)
    topc = add(at(S_TOP)[0], (0, 0, -1.7))
    zoom = lerp(3.0, 3.25, eio(prog(t, 13.804, 19.771))); f = P3(*topc); sx, sy = 540, 760
    press = eo(prog(t, 16.56, 16.9))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    world(cv, t, a0, lambda items: train_items(items, sf, a0, t=t, press=press, arms=1.0))
    sa = eo(prog(t, 15.33, 15.6))
    if sa > 0:                                                            # garis kecepatan di belakang kereta
        for k in range(6):
            s0 = sf - 2 * TRAIN_GAP - 0.8 - k * 0.15; p0, T0, N0 = at(s0); p1, _, _ = at(s0 - 2.2 - 0.4 * (k % 3))
            off = mul(N0, 0.35 + 0.25 * k); q0, q1 = P3(*add(p0, off)), P3(*add(p1, off))
            cv.drawLine(q0[0], q0[1], q1[0], q1[1], P(col(ORANGE if k % 2 else NAVY, 0.55 * sa * a0), stroke=5))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    if press > 0:                                                         # panah: tertekan ke kursi (keluar dari pusat putaran)
        for k in range(3):
            p, T, N = at(sf - k * TRAIN_GAP); hd = S(add(p, mul(N, 1.35))); st = S(add(p, mul(N, 0.6)))
            arrow(cv, hd, st, ORANGE, a0 * press * (0.8 + 0.2 * math.sin(t * 6 + k)), w=9, head=22)
        chip(cv, 'TERTEKAN KE KURSI', 540, 330, a0 * press * (1 - prog(t, 19.4, 19.7)), size=28, bg=ORANGE)
    ka = eo(prog(t, 15.33, 15.6)) * (1 - prog(t, 16.4, 16.6))
    if ka > 0: chip(cv, 'MELAJU KENCANG', 540, 330, a0 * ka, size=28, bg=NAVY)
    ja = eo(prog(t, 18.44, 18.7))
    if ja > 0:
        p, T, N = at(sf - TRAIN_GAP); hd = S(add(p, mul(N, 1.5))); dn = (hd[0], hd[1] + 200)
        cv.drawLine(hd[0], hd[1] + 20, dn[0], dn[1], P(col(RED, 0.8 * a0 * ja), stroke=6, effect=skia.DashPathEffect.Make([14, 10], 0)))
        s_ = 34; c0 = (dn[0], dn[1] + 10)
        cv.drawLine(c0[0] - s_, c0[1] - s_, c0[0] + s_, c0[1] + s_, P(col(RED, a0 * ja), stroke=10)); cv.drawLine(c0[0] - s_, c0[1] + s_, c0[0] + s_, c0[1] - s_, P(col(RED, a0 * ja), stroke=10))
        chip(cv, 'BUKAN JATUH', 540, 1340, a0 * ja, size=30, bg=INK); check(cv, 715, 1340, 22, prog(t, 18.55, 18.95), a0 * ja)

# ------------------------------------------------------------ D: putaran nggak bulat sempurna; atas sempit, bawah lebar (19.771 - 26.783)
def gD(cv, t):
    a0 = eo(prog(t, 19.771, 20.15))
    wide = (CX + 0.4, 0.0, Z0 + LH * 0.5 - 0.6); zoom = lerp(1.18, 1.24, eio(prog(t, 19.771, 26.783))); f = P3(*wide); sx, sy = 560, 880
    tg = eo(prog(t, 20.62, 21.0)) * (0.7 + 0.3 * math.sin(t * 4))
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    world(cv, t, a0, lambda items: train_items(items, S_LOOP0 - 8 + 5.5 * (t - 19.771), a0, t=t), track_glow=tg)
    ca = eo(prog(t, 20.62, 21.0))
    if ca > 0:                                                            # lingkaran sempurna (bayangan merah putus-putus) setinggi putaran
        rr = LH / 2; cz = Z0 + rr
        pts = [P3(CX + rr * math.sin(th), 0.0, cz - rr * math.cos(th)) for th in [math.tau * i / 80 for i in range(81)]]
        cv.drawPath(poly(pts, False), P(col(RED, 0.85 * a0 * ca), stroke=5, effect=skia.DashPathEffect.Make([16, 11], -t * 30)))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    if ca > 0:
        p = S((CX + LH / 2, 0.0, Z0 + LH / 2)); text_c(cv, 'BULAT', p[0] + 70, p[1], 30, RED, a0 * ca, halo=1.0)
    ta = eo(prog(t, 22.17, 22.5))
    if ta > 0:
        p = S(loop_pt(math.pi * 0.86)); label(cv, 'ATAS: SEMPIT', p[0], p[1], 290, 420, a0 * ta, sub='lengkung tajam')
    ba = eo(prog(t, 23.21, 23.55))
    if ba > 0:
        p = S(loop_pt(math.pi * 0.2)); label(cv, 'BAWAH: LEBAR', p[0], p[1], 820, 1130, a0 * ba, sub='lengkung landai')
    ga = eo(prog(t, 24.25, 24.6))
    if ga > 0:                                                            # tekanan di dasar putaran: lingkaran vs tetes
        r = skia.Rect(150, 250, 930, 470); card(cv, r, a0 * ga, rad=30)
        mono(cv, 'TEKANAN DI BAGIAN BAWAH', 540, r.top() + 40, 20, MUTED, a0 * ga, sp=3)
        for i, (nm, frac, c, txt) in enumerate((('BULAT', 0.92, RED, 'bisa ±5× berat badan'), ('TETES', 0.5 * eo(prog(t, 24.5, 25.2)) + 0.05, ORANGE, 'jauh lebih ringan'))):
            y = r.top() + 100 + i * 70
            text_c(cv, nm, 250, y, 26, c, a0 * ga)
            cv.drawRoundRect(skia.Rect(330, y - 16, 860, y + 16), 16, 16, P(col('#EEE6DA', a0 * ga)))
            cv.drawRoundRect(skia.Rect(330, y - 16, 330 + 530 * frac, y + 16), 16, 16, P(col(c, a0 * ga)))
            text_c(cv, txt, 600, y + 34, 18, MUTED, a0 * ga, f=B)
        chip(cv, 'BADAN NGGAK TERTEKAN BERLEBIHAN', 540, 1340, a0 * eo(prog(t, 24.5, 24.8)), size=24, bg=ORANGE)

# ------------------------------------------------------------ E: John Miller mematenkan roda bawah, 1919 (26.783 - 31.321)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def miller_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'AMERIKA · 1919', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    for k in range(26): cv.drawLine(r.left(), r.top() + 120 + k * 40, r.right(), r.top() + 120 + k * 40, ink(0.08, 1.5))      # kertas gambar paten
    cx, cy = 600, 720                                                     # gambar paten: rel (lingkaran) + roda atas, samping, bawah
    cv.drawCircle(cx, cy, 70, P(col('#E6D3AE', a))); cv.drawCircle(cx, cy, 70, ink(1, 5))
    cv.drawRect(skia.Rect(cx - 22, cy + 70, cx + 22, cy + 230), P(col('#E6D3AE', a))); cv.drawRect(skia.Rect(cx - 22, cy + 70, cx + 22, cy + 230), ink(1, 4))
    for (wx, wy, rr, nm) in ((cx, cy - 150, 78, 'A'), (cx + 160, cy, 64, 'B'), (cx, cy + 150 + 0, 0, '')):
        if rr: cv.drawCircle(wx, wy, rr, P(col('#FBF3E2', a))); cv.drawCircle(wx, wy, rr, ink(1, 5)); cv.drawCircle(wx, wy, rr * 0.25, ink(1, 4))
    glow = bump(prog(t, 29.4, 30.6)) * 1.2 + 0.4 * prog(t, 30.6, 31.0)
    bx, by = cx - 150, cy + 120                                           # roda bawah (di sisi bawah rel, diagonal supaya tidak menabrak tiang)
    cv.drawCircle(bx, by, 60, P(col(mixc('#FBF3E2', '#FFB066', clamp(glow)), a))); cv.drawCircle(bx, by, 60, P(col(ORANGE_D if glow > 0.2 else SEPIA_INK, a), stroke=6)); cv.drawCircle(bx, by, 15, ink(1, 4))
    cv.drawLine(bx + 42, by - 42, cx - 50, cy + 50, ink(1, 4))
    f_ = font(XB, 30)
    for (lx, ly, s_) in ((cx - 10, cy - 250, 'A'), (cx + 240, cy + 10, 'B'), (bx - 92, by + 70, 'C')): cv.drawString(s_, lx, ly, f_, P(col(SEPIA_INK, a)))
    sa = eo(prog(t, 29.52, 29.75))                                        # cap PATEN
    if sa > 0:
        cv.save(); cv.translate(800, 1000); cv.rotate(-12); s2 = lerp(1.6, 1.0, eo(prog(t, 29.52, 29.75))); cv.scale(s2, s2)
        rr_ = skia.Rect(-120, -46, 120, 46); cv.drawRoundRect(rr_, 12, 12, P(col(ORANGE_D, 0.9 * sa * a), stroke=6))
        text_c(cv, 'PATEN 1919', 0, 0, 34, ORANGE_D, 0.9 * sa * a); cv.restore()
    hx, hy = 260, 1000                                                    # John Miller: jas & kumis
    cv.drawRoundRect(skia.Rect(hx - 28, hy - 120, hx + 28, hy - 20), 14, 14, P(col('#3E2E22', a)))
    cv.drawRect(skia.Rect(hx - 20, hy - 22, hx - 6, hy + 20), P(col('#3E2E22', a))); cv.drawRect(skia.Rect(hx + 6, hy - 22, hx + 20, hy + 20), P(col('#3E2E22', a)))
    cv.drawCircle(hx, hy - 146, 24, P(col('#E8C9A0', a))); cv.drawCircle(hx, hy - 146, 24, ink(1, 2.5))
    cv.drawArc(skia.Rect(hx - 26, hy - 174, hx + 26, hy - 128), 180, 180, False, P(col('#5A4030', a)))
    cv.drawLine(hx - 12, hy - 138, hx + 12, hy - 138, P(col('#5A4030', a), stroke=4))
    cv.drawLine(hx + 24, hy - 100, hx + 90, hy - 130 + 4 * math.sin(t * 3), P(col('#3E2E22', a), stroke=10))
    cv.drawRect(skia.Rect(hx + 80, hy - 160, hx + 140, hy - 110), P(col('#FBF3E2', a))); cv.drawRect(skia.Rect(hx + 80, hy - 160, hx + 140, hy - 110), ink(1, 2))
    cv.restore()
def gE(cv, t):
    a0 = eo(prog(t, 26.783, 27.15))
    zz = 1.14 + 0.03 * eio(prog(t, 26.783, 31.321))
    cv.save(); cv.translate(540, 770); cv.scale(zz, zz); cv.translate(-540, -700)
    miller_card(cv, t, a0)
    cv.restore()
    S = lambda x, y: (540 + (x - 540) * zz, 770 + (y - 700) * zz)
    na = eo(prog(t, 28.1, 28.45))
    if na > 0: p = S(260, 854); label(cv, 'JOHN MILLER', p[0], p[1], 300, 380, a0 * na, size=26, sub='perancang roller coaster')
    ra = eo(prog(t, 29.52, 29.85))
    if ra > 0: p = S(450, 840); label(cv, 'RODA BAWAH', p[0], p[1], 770, 1240, a0 * ra, size=26, sub='kereta terkunci ke rel')

# ------------------------------------------------------------ F: putaran pertama di Coney Island (1895) bulat, penumpang sakit leher (31.321 - 36.559)
def coney_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'CONEY ISLAND · 1895', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    cv.drawRect(skia.Rect(r.left(), 990, r.right(), r.bottom()), P(col('#E6D3AE', a)))
    for k in range(4):                                                    # ombak laut di kejauhan
        p = skia.Path(); yy = 1010 + k * 30; p.moveTo(r.left(), yy)
        for i in range(30): x = r.left() + i * 32; p.quadTo(x + 8, yy - 6 + 2 * math.sin(t * 2 + k), x + 16, yy); p.quadTo(x + 24, yy + 6, x + 32, yy)
        cv.drawPath(p, ink(0.35, 2))
    cx, cy, R = 540, 700, 220                                              # putaran BULAT dari kayu + rangka
    for k in range(12):
        th = math.tau * k / 12; cv.drawLine(cx + R * math.cos(th), cy + R * math.sin(th), cx + R * 1.12 * math.cos(th), cy + R * 1.12 * math.sin(th), ink(0.7, 4))
    for x in (cx - 260, cx + 260):
        cv.drawLine(x, 990, cx + (x - cx) * 0.4, cy - 60, ink(0.8, 6)); cv.drawLine(x, 990, cx + (x - cx) * 0.9, cy + 120, ink(0.8, 6))
    cv.drawLine(cx - 470, 940, cx, cy + R, ink(1, 8)); cv.drawLine(cx, cy + R, cx + 430, 960, ink(1, 8))
    cv.drawCircle(cx, cy, R, P(col('#B58A57', a), stroke=14)); cv.drawCircle(cx, cy, R, ink(1, 3))
    rd = bump(prog(t, 33.3, 34.0)) * 1.2 + 0.5 * prog(t, 34.0, 34.6)
    if rd > 0: cv.drawCircle(cx, cy, R, P(col(RED, 0.8 * clamp(rd) * a), stroke=8))
    th = math.pi / 2 - t * 2.4                                             # gerbong kayu berputar + penumpang
    car_x, car_y = cx + (R - 10) * math.cos(th), cy + (R - 10) * math.sin(th)
    cv.save(); cv.translate(car_x, car_y); cv.rotate(math.degrees(th) + 90)
    cv.drawRoundRect(skia.Rect(-46, -18, 46, 18), 6, 6, P(col('#8C6A4A', a))); cv.drawRoundRect(skia.Rect(-46, -18, 46, 18), 6, 6, ink(1, 3))
    for k in (-18, 18): cv.drawCircle(k, -36, 12, P(col('#E8C9A0', a))); cv.drawCircle(k, -36, 12, ink(1, 2))
    cv.restore()
    sa = eo(prog(t, 34.3, 34.6))
    if sa > 0:                                                            # penumpang sakit leher (bintang pusing)
        px, py = 820, 880
        cv.drawRoundRect(skia.Rect(px - 30, py - 100, px + 30, py), 14, 14, P(col('#3E2E22', a * sa)))
        cv.save(); cv.translate(px, py - 128); cv.rotate(-22 + 6 * math.sin(t * 4)); cv.drawCircle(0, 0, 26, P(col('#E8C9A0', a * sa))); cv.drawCircle(0, 0, 26, ink(sa, 2.5)); cv.restore()
        cv.drawLine(px + 24, py - 92, px + 6, py - 112, P(col('#3E2E22', a * sa), stroke=10))
        for k in range(3):
            ang = t * 3 + k * math.tau / 3; sx_, sy_ = px + 48 * math.cos(ang), py - 170 + 14 * math.sin(ang)
            st = poly([(sx_ + 9 * math.cos(math.pi / 2 + j * math.tau / 10) * (1 if j % 2 == 0 else 0.45), sy_ - 9 * math.sin(math.pi / 2 + j * math.tau / 10) * (1 if j % 2 == 0 else 0.45)) for j in range(10)])
            cv.drawPath(st, P(col(ORANGE_D, a * sa)))
    cv.restore()
def gF(cv, t):
    a0 = eo(prog(t, 31.321, 31.7))
    zz = 1.14 + 0.03 * eio(prog(t, 31.321, 36.559))
    cv.save(); cv.translate(540, 770); cv.scale(zz, zz); cv.translate(-540, -700)
    coney_card(cv, t, a0)
    cv.restore()
    S = lambda x, y: (540 + (x - 540) * zz, 770 + (y - 700) * zz)
    ba = eo(prog(t, 33.3, 33.6))
    if ba > 0: p = S(760, 700); label(cv, 'PUTARAN BULAT', p[0], p[1], 800, 420, a0 * ba, size=26, dot=RED, sub='lengkungnya sama di semua sisi')
    sa = eo(prog(t, 34.3, 34.6))
    if sa > 0: chip(cv, 'SAKIT LEHER!', 540, 1340, a0 * sa, size=30, bg=RED)

# ------------------------------------------------------------ G & J
CMTS = [('kereta KRL!', 280, 760, 37.0, ORANGE), ('bianglala dong', 760, 900, 37.25, INK), ('gedung tahan gempa', 330, 1040, 37.5, ORANGE_D), ('bendungan!!', 760, 1180, 37.75, NAVY)]
def gG(cv, t):
    a0 = eo(prog(t, 36.559, 36.85))
    logo_mark(cv, 540, 430, 80 * lerp(0.6, 1, bo(prog(t, 36.559, 36.95))), a0, t)
    text_c(cv, 'BONGKAR APA LAGI?', 540, 590, 64, INK, a0 * eo(prog(t, 36.65, 36.95)))
    for txt, x, y, t0, c in CMTS:
        q = prog(t, t0, t0 + 0.3)
        if q <= 0: continue
        aa = a0 * clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
        r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, aa, rad=42, lift=10)
        cv.drawCircle(r.left() + 42, 0, 24, P(col(c, aa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, aa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, aa)))
        cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, aa)))
        cv.restore()
    ca = eo(prog(t, 38.63, 38.9))
    if ca > 0: chip(cv, 'TULIS DI KOMENTAR', 540, 1340, a0 * ca, size=30, bg=ORANGE)
def gJ(cv, t):
    tt = t - 39.931; a = eo(prog(tt, 0.0, 0.4)); p_ = bo(prog(tt, 0.0, 0.6))
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
    ev = [(0.0, 'whoosh'), (0.05, 'grind'), (0.9, 'swish'), (1.3, 'pop'), (1.25, 'buzzer'), (1.4, 'crack'), (1.45, 'whoosh'), (2.3, 'clunk'), (2.32, 'rumble'),
          (2.45, 'rewind'), (3.3, 'shine'), (3.4, 'zap'), (3.5, 'ding'), (3.6, 'stamp'), (4.7, 'pop'), (4.85, 'pop'), (5.0, 'pop'), (5.6, 'grind'),
          (6.275, 'whoosh'), (6.5, 'tick'), (6.9, 'tick'), (7.23, 'pop'), (9.3, 'ding_soft'), (10.1, 'ding_soft'), (10.78, 'ding'), (11.57, 'clunk'), (11.7, 'stamp'),
          (13.804, 'whoosh'), (14.2, 'grind'), (15.33, 'swish'), (15.4, 'pop'), (16.56, 'zap'), (16.6, 'pop'), (18.44, 'buzzer'), (18.55, 'ding'),
          (19.771, 'whoosh'), (20.62, 'swish'), (20.7, 'pop'), (22.17, 'pop'), (23.21, 'pop'), (24.25, 'card'), (24.5, 'rise'), (25.2, 'ding'),
          (26.783, 'whoosh'), (26.85, 'card'), (28.1, 'pop'), (29.52, 'stamp'), (29.6, 'ding_soft'),
          (31.321, 'whoosh'), (31.4, 'card'), (32.0, 'tick'), (33.3, 'buzzer'), (34.3, 'boing'), (34.4, 'pop'),
          (36.559, 'whoosh'), (36.65, 'shine'), (37.0, 'pop'), (37.25, 'pop'), (37.5, 'pop'), (37.75, 'pop'), (38.63, 'pop'),
          (39.931, 'whoosh'), (40.08, 'boing'), (40.43, 'shine'), (40.68, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
