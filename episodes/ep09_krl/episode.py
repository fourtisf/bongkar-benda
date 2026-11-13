#!/usr/bin/env python3
"""Bongkar Benda #09: 'KRL, kok nggak keluar rel pas belok?'
Diorama rel isometrik + potongan depan roda kereta (dibelah di bidang poros).
Hook: KRL melaju ke tikungan; kalau rodanya datar -> anjlok di tikungan -> REWIND -> belok mulus, roda menyala oranye.
Alasan 1: roda miring seperti kerucut; saat belok, roda luar menggelinding di bagian yang lebih besar -> belok sendiri.
Alasan 2: bibir roda (flens) di sisi dalam = pengaman terakhir. Alasan 3: di tikungan rel luar lebih tinggi (peninggian rel).
Sejarah: kereta listrik pertama Indonesia 1925, Tanjung Priok - Jatinegara. Kini ±1 juta penumpang KRL Jabodetabek/hari.
Sumber: content/EP09_krl.md.  python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, YELLOW, RED, WHITE, text_c, mono, card, chip, label, check, logo_mark)
from iso import Iso, tone, quad, box, poly, sparks
import geo3d as g
from geo3d import add, sub, mul, dot, nrm, crs, p3, obox, ocyl

bb.DUR = 53.971
bb.TITLE = ('KRL,', 'kok nggak keluar rel?'); bb.TITLE_OUT = 4.4
AN = [0.0, 7.312, 11.947, 19.383, 25.554, 32.608, 39.066, 44.11, 48.771, 53.971]
bb.GROUPS = [(AN[i], AN[i + 1], k) for i, k in enumerate('ABCDEFGHJ')]
bb.PHRASES = [(0.15, 'Kereta nggak punya [setir],'), (1.87, 'dan rodanya [nyatu sama poros].'), (3.97, 'Kok bisa [belok] tanpa [keluar rel]?'), (5.81, 'Ini [alasannya].'),
              (7.35, '[Pertama],'), (7.98, 'roda kereta itu [nggak datar].'), (9.78, 'Bentuknya [miring],'), (10.91, 'kayak [kerucut].'),
              (11.99, 'Saat [belok],'), (12.98, 'roda luar menggelinding di bagian yang [lebih besar],'), (15.59, 'jadi menempuh [jarak lebih jauh].'), (17.41, 'Keretanya pun [belok sendiri].'),
              (19.42, '[Kedua],'), (20.0, 'ada [bibir roda] di sisi dalam.'), (21.83, 'Ini [pengaman terakhir]'), (23.24, 'kalau rodanya [bergeser terlalu jauh].'),
              (25.59, '[Ketiga],'), (26.23, 'di [tikungan],'), (27.18, 'rel bagian luar dibuat [lebih tinggi].'), (29.3, 'Kereta jadi [sedikit miring],'), (30.77, 'melawan [dorongan ke luar].'),
              (32.65, 'Kereta listrik [pertama] di Indonesia'), (34.75, 'melaju tahun [1925],'), (36.86, 'dari [Tanjung Priok] ke [Jatinegara].'),
              (39.11, 'Sekarang, sekitar [sejuta orang]'), (40.96, 'naik KRL Jabodetabek [setiap hari].'),
              (44.15, '[Kirim] ke teman yang tiap hari naik KRL.'), (46.37, 'Benda apa yang mau kamu [bongkar] berikutnya?'),
              (48.81, 'Follow [Bongkar Benda],'), (50.05, 'biar makin paham [cara kerja benda] di sekitarmu.')]

WORLD = Iso(0, 0, 50); g.ISO = WORLD
NAVY, NAVY2 = '#2A3F6B', '#1A2A4C'
BODY, ROOF = '#F7F2EA', '#DCD5CA'
STEEL_W, STEEL_T, SECT, SECT_E = '#9AA6BA', '#C9CFD9', '#E7EAF0', '#5B6782'
RAIL_C, SLEEP_C, BAL_C, BAL_D, SOIL_C = '#8E9AAF', '#D9D0C2', '#B3A797', '#8C8070', '#D6AE84'
VV = (1.0, 1.0, 1.0)
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
def xmark(cv, x, y, s, a, c=RED, w=10):
    if a <= 0: return
    cv.drawLine(x - s, y - s, x + s, y + s, P(col(WHITE, a), stroke=w + 6)); cv.drawLine(x - s, y + s, x + s, y - s, P(col(WHITE, a), stroke=w + 6))
    cv.drawLine(x - s, y - s, x + s, y + s, P(col(c, a), stroke=w)); cv.drawLine(x - s, y + s, x + s, y - s, P(col(c, a), stroke=w))
def cards3(cv, t, t0, items, y=1335):
    for k, (num, txt) in enumerate(items):
        q = prog(t, t0 + 0.15 * k, t0 + 0.3 + 0.15 * k)
        if q <= 0: continue
        x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.translate(-x, -y)
        card(cv, skia.Rect(x - 158, y - 30, x + 158, y + 30), aa, rad=30, lift=8)
        cv.drawCircle(x - 123, y, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 123, y, 24, WHITE, aa)
        text_c(cv, txt, x + 14, y, 23, INK, aa)
        cv.restore()

# ------------------------------------------------------------ mesh 3D sederhana: muka diurutkan menurut kedalaman (pandangan dari (1,1,1))
class Mesh:
    def __init__(self, zoom=1.0): self.f = []; self.sw = 1.3 / max(zoom, 0.1)
    def add(self, pts, n, c, a=1.0, glow=0.0, flat=False, bias=0.0, edge=None, gc=ORANGE):
        if a <= 0.003 or dot(n, VV) <= 1e-6: return
        k = sum(p[0] + p[1] + p[2] for p in pts) / len(pts) + bias
        self.f.append((k, pts, n, c, a, glow, flat, edge, gc))
    def draw(self, cv):
        self.f.sort(key=lambda q: q[0])
        for k, pts, n, c, a, glow, flat, edge, gc in self.f:
            pth = poly([p3(p) for p in pts]); cc = c if flat else g.shade(c, n)
            if glow > 0: cc = mixc(cc, gc, 0.8 * clamp(glow))
            cv.drawPath(pth, P(col(cc, a)))
            if a > 0.98: cv.drawPath(pth, P(col(cc, a), stroke=self.sw))
            if edge: cv.drawPath(pth, P(col(edge, 0.85 * a), stroke=self.sw * 2.4))
        self.f = []
def half_range(ax, keep):
    """rentang sudut lathe yang dot(arah, keep) <= 0 (separuh di belakang bidang potong)"""
    e1, e2 = g.basis(ax); phi = math.atan2(dot(e2, keep), dot(e1, keep))
    return (phi + math.pi / 2, phi + 3 * math.pi / 2)
def lathe(M, c, ax, prof, colf, a=1.0, n=40, rng=(0.0, math.tau), glowf=None, gc=ORANGE, off=(0.0, 0.0, 0.0), bias=0.0):
    """benda putar: profil [(s, r)] sepanjang sumbu ax dari pusat c (profil berjalan dengan s naik di tepi luar)"""
    e1, e2 = g.basis(ax); th0, th1 = rng; m = max(4, int(round(n * (th1 - th0) / math.tau)))
    ths = [th0 + (th1 - th0) * j / m for j in range(m + 1)]
    dirs = [add(mul(e1, math.cos(q)), mul(e2, math.sin(q))) for q in ths]
    b = add(c, off)
    for i in range(len(prof) - 1):
        (s0, r0), (s1, r1) = prof[i], prof[i + 1]
        Ns, Nr = -(r1 - r0), (s1 - s0); L = math.hypot(Ns, Nr)
        if L < 1e-9: continue
        Ns, Nr = Ns / L, Nr / L; gl = glowf(i) if glowf else 0.0
        for j in range(m):
            dm = nrm(add(dirs[j], dirs[j + 1])); nn = add(mul(ax, Ns), mul(dm, Nr))
            cc = colf(i, 0.5 * (ths[j] + ths[j + 1])) if callable(colf) else colf
            pts = [add(b, add(mul(ax, s0), mul(dirs[j], r0))), add(b, add(mul(ax, s1), mul(dirs[j], r1))),
                   add(b, add(mul(ax, s1), mul(dirs[j + 1], r1))), add(b, add(mul(ax, s0), mul(dirs[j + 1], r0)))]
            M.add(pts, nn, cc, a, gl, gc=gc, bias=bias)
def prism(M, prof, o, eu, ez, et, t0, t1, colf, a=1.0, segs=1, cap1=True, capc=None, cap_edge=None, glowf=None, bias=0.0, cap_bias=0.3):
    """profil 2D [(u, z)] diekstrusi sepanjang et dari t0 ke t1; muka ujung t1 (normal +et) = potongan"""
    m = len(prof); area = sum(prof[i][0] * prof[(i + 1) % m][1] - prof[(i + 1) % m][0] * prof[i][1] for i in range(m)); sg = 1 if area > 0 else -1
    W = lambda u, z, t_: add(o, add(mul(eu, u), add(mul(ez, z), mul(et, t_))))
    for i in range(m):
        (u0, z0), (u1, z1) = prof[i], prof[(i + 1) % m]
        nn = nrm(add(mul(eu, (z1 - z0) * sg), mul(ez, -(u1 - u0) * sg)))
        if dot(nn, VV) <= 1e-6: continue
        cc = colf(i) if callable(colf) else colf; gl = glowf(i) if glowf else 0.0
        for k in range(segs):
            ta, tb = lerp(t0, t1, k / segs), lerp(t0, t1, (k + 1) / segs)
            M.add([W(u0, z0, ta), W(u1, z1, ta), W(u1, z1, tb), W(u0, z0, tb)], nn, cc, a, gl, bias=bias)
    if cap1: M.add([W(u, z, t1) for u, z in prof], et, capc or (colf(0) if callable(colf) else colf), a, flat=True, bias=bias + cap_bias, edge=cap_edge)

# ------------------------------------------------------------ bingkai potongan depan: rel ke arah penonton (TT), poros mendatar (AA)
BETA = math.radians(22)                                                      # 3/4: muka roda & potongan sama-sama terlihat
TT = (math.cos(BETA), math.sin(BETA), 0.0); AA = (math.sin(BETA), -math.cos(BETA), 0.0); ZZ = (0.0, 0.0, 1.0)
def Wp(a_, t_, z_): return (AA[0] * a_ + TT[0] * t_, AA[1] * a_ + TT[1] * t_, z_)
SL, RW = 0.45, 0.465                                                         # kemiringan tapak (dibesar-besarkan) & jari-jari roda
def r_tread(s): return RW + 0.005 - (clamp(s, -0.10, 0.10) + 0.10) * SL
WPROF = [(-0.155, 0.0), (-0.155, RW + 0.085), (-0.125, RW + 0.085), (-0.11, RW + 0.02), (-0.10, RW + 0.005), (0.10, r_tread(0.10)),
         (0.10, r_tread(0.10) - 0.03), (0.05, r_tread(0.10) - 0.06), (0.05, 0.17), (0.09, 0.15), (0.09, 0.0)]
FLANGE_SEG, TREAD_SEG = (1, 2, 3), 4
FLANGE_POLY = [(-0.155, RW - 0.005), (-0.155, RW + 0.085), (-0.125, RW + 0.085), (-0.11, RW + 0.02), (-0.10, RW + 0.005), (-0.10, RW - 0.005)]
AXP = [(-0.8, 0.0), (-0.8, 0.06), (-0.75, 0.06), (-0.75, 0.085), (0.75, 0.085), (0.75, 0.06), (0.8, 0.06), (0.8, 0.0)]
RAILP = [(-0.07, -0.16), (0.07, -0.16), (0.07, -0.145), (0.014, -0.13), (0.011, -0.05), (0.0375, -0.042), (0.0375, 0.0), (-0.0375, 0.0),
         (-0.0375, -0.042), (-0.011, -0.05), (-0.014, -0.13), (-0.07, -0.145)]
def R2f(psi):
    c, s_ = math.cos(psi), math.sin(psi)
    def R2(a_, z_): x_ = a_ + 0.6; return (-0.6 + x_ * c - z_ * s_, x_ * s_ + z_ * c)
    return R2
_rp = random.Random(11); PEBBLES = []
while len(PEBBLES) < 34:
    pa, pz = _rp.uniform(-1.62, 1.62), _rp.uniform(-0.93, -0.44)
    if abs(pa) < 1.75 - (pz + 0.98) / 0.58 * 0.45: PEBBLES.append((pa, pz, _rp.uniform(0.035, 0.06), _rp.random()))
def track_sec(M, a=1.0, L=8.0, scroll=0.0, psi=0.0, front=0.0, slide=0.0, rail_glow=(0.0, 0.0), segs=28):
    """tanah, balas, bantalan, rel dilihat dari depan, dibelah di t = 0; front = alfa separuh depan (t 0..3) yang bergeser 'slide' ke penonton"""
    R2 = R2f(psi)
    parts = [(-L, 0.0, a, 0.0, 0.0)]
    if front > 0.003: parts.append((0.0, 3.0, a * front, slide, 6.0))
    for (t0, t1, aa, sl, bs) in parts:
        o = mul(TT, sl); n_ = max(2, int(segs * (t1 - t0) / L))
        prism(M, [(-5.0, -4.0), (5.0, -4.0), (5.0, -0.98), (-5.0, -0.98)], o, AA, ZZ, TT, t0, t1, SOIL_C, aa, segs=n_, capc='#D9B48C', bias=bs)
        bal = [(-1.75, -0.98), (1.75, -0.98), R2(1.3, -0.40), R2(-1.3, -0.40)]
        prism(M, bal, o, AA, ZZ, TT, t0, t1, BAL_C, aa, segs=n_, capc='#C2B6A6', bias=bs)
        k0 = int(math.floor((t0 - scroll) / 0.62)) - 1
        for k in range(k0, k0 + int((t1 - t0) / 0.62) + 3):
            tk = k * 0.62 + scroll % 0.62
            ta, tb = max(tk - 0.24, t0), min(tk, t1)
            if tb <= ta + 0.01: continue
            slp = [R2(-1.15, -0.40), R2(1.15, -0.40), R2(1.15, -0.17), R2(-1.15, -0.17)]
            prism(M, slp, o, AA, ZZ, TT, ta, tb, SLEEP_C, aa, capc='#E6DED2', cap_edge='#A3978A', bias=bs + 0.2)
        for side, gl in ((1, rail_glow[0]), (-1, rail_glow[1])):
            rp = [R2(side * 0.6 + u, z) for u, z in RAILP]
            prism(M, rp, o, AA, ZZ, TT, t0, t1, lambda i: '#D3D9E2' if i in (5, 6, 7) else RAIL_C, aa, segs=n_, capc=mixc(SECT, ORANGE, 0.6 * gl), cap_edge=SECT_E,
                  glowf=(lambda i, gl=gl: gl), bias=bs + 0.25)
def ws_draw(M, a=1.0, d=0.0, psi=0.0, front=0.0, slide=0.0, tglow=0.0, fglow=0.0, spin=0.0, n=40, cut=True):
    """sepasang roda + poros di atas rel; d = geser ke kanan (+AA, sisi luar); psi = miring bersama rel (peninggian)"""
    R2 = R2f(psi)
    r1, r2 = r_tread(-d), r_tread(d)
    A1, Z1 = R2(0.6 + d, r1); A2, Z2 = R2(-0.6 + d, r2)
    c1, c2 = Wp(A1, 0, Z1), Wp(A2, 0, Z2)
    ax = nrm(sub(c1, c2)); up = nrm(crs(ax, TT))
    def colw(i, th):
        if i == TREAD_SEG: return STEEL_T if ((th - spin) % (math.tau / 10)) > 0.12 else '#7C879B'
        return STEEL_W
    glowf = lambda i: tglow if i == TREAD_SEG else (fglow if i in FLANGE_SEG else 0.0)
    for cc, axw in ((c1, ax), (c2, mul(ax, -1))):
        rk = half_range(axw, TT) if cut else (0.0, math.tau)
        lathe(M, cc, axw, WPROF, colw, a, n, rk, glowf)
        if cut:
            if front > 0.003: lathe(M, cc, axw, WPROF, colw, a * front, n, (rk[0] + math.pi, rk[1] + math.pi), glowf, off=mul(TT, slide), bias=6.0)
            pts = [add(cc, add(mul(axw, s), mul(up, r))) for s, r in WPROF] + [add(cc, add(mul(axw, s), mul(up, -r))) for s, r in WPROF[::-1]]
            M.add(pts, TT, SECT, a, flat=True, bias=0.45, edge=SECT_E)
    mid = mul(add(c1, c2), 0.5)
    rk = half_range(ax, TT) if cut else (0.0, math.tau)
    lathe(M, mid, ax, AXP, '#7C879B', a, 24, rk)
    if cut:
        if front > 0.003: lathe(M, mid, ax, AXP, '#7C879B', a * front, 24, (rk[0] + math.pi, rk[1] + math.pi), off=mul(TT, slide), bias=6.0)
        pts = [add(mid, add(mul(ax, s), mul(up, r))) for s, r in AXP] + [add(mid, add(mul(ax, s), mul(up, -r))) for s, r in AXP[::-1]]
        M.add(pts, TT, '#D5DAE3', a, flat=True, bias=0.4, edge=SECT_E)
    return c1, c2, ax, up, r1, r2
def sec_pt(c, ax, up, s, r): return add(c, add(mul(ax, s), mul(up, r)))
def pebbles(cv, a, psi=0.0):
    if a <= 0: return
    for pa, pz, pr, ph in PEBBLES:
        p = p3(Wp(pa, 0, pz)); rr = pr * 50
        cv.drawCircle(p[0], p[1], rr * 1.15, P(col(BAL_D, 0.55 * a)))
        cv.drawCircle(p[0] - rr * 0.25, p[1] - rr * 0.3, rr * 0.45, P(col(WHITE, 0.25 * a)))

# ------------------------------------------------------------ diorama rel atas (hook, stasiun): lintasan, KRL, tiang listrik
RCH, LH1 = 9.0, 34.0; ARCH = math.pi / 2 * RCH
def hpath(s):
    if s < LH1: return (-LH1 + s, -RCH, 0.0)
    s2 = s - LH1
    if s2 < ARCH: an = -math.pi / 2 + s2 / RCH; return (RCH * math.cos(an), RCH * math.sin(an), s2 / RCH)
    return (RCH, s2 - ARCH, math.pi / 2)
def spath(s): return (-LH1 + s, -RCH, 0.0)                                     # lurus terus (kereta yang anjlok)
def tpath(s): return (s - 30.0, 0.0, 0.0)                                       # stasiun: lurus sepanjang x
def track_top(cv, a, s0, s1, path, ds=0.5):
    n = max(2, int((s1 - s0) / ds)); ss = [s0 + (s1 - s0) * k / n for k in range(n + 1)]
    def off(s, o, z): x, y, h = path(s); return P3(x - math.sin(h) * o, y + math.cos(h) * o, z)
    cv.drawPath(poly([off(s, 1.85, 0.0) for s in ss] + [off(s, -1.85, 0.0) for s in ss[::-1]]), P(col('#B9AE9F', a)))
    cv.drawPath(poly([off(s, 1.3, 0.16) for s in ss] + [off(s, -1.3, 0.16) for s in ss[::-1]]), P(col('#CDC3B4', a)))
    for k in range(int(math.ceil(s0 / 0.7)), int(s1 / 0.7) + 1):
        s = k * 0.7; q = [off(s - 0.13, 1.0, 0.18), off(s + 0.13, 1.0, 0.18), off(s + 0.13, -1.0, 0.18), off(s - 0.13, -1.0, 0.18)]
        cv.drawPath(poly(q), P(col('#E8E0D3', a))); cv.drawPath(poly(q), P(col('#9E9282', 0.55 * a), stroke=1.2))
    for o in (0.45, -0.45):
        cv.drawPath(poly([off(s, o, 0.2) for s in ss], False), P(col('#4A5568', a), stroke=5.5))
        cv.drawPath(poly([off(s, o, 0.28) for s in ss], False), P(col('#E4E9F0', a), stroke=2.6))
def tcar(cv, base, u, v, w, a, lead=False, wglow=0.0, panto=0.0, doors=0.0):
    """satu gerbong KRL fiktif (krem, garis oranye, jendela navy); base = titik rel di bawah pusat gerbong"""
    if a <= 0: return
    L, Wd, z0, z1 = 2.9, 1.1, 0.55, 3.05
    def Pt(cu, cv_, cw): return add(base, add(mul(u, cu), add(mul(v, cv_), mul(w, cw))))
    def qd(pts, c, aa=1.0): cv.drawPath(poly([p3(p) for p in pts]), P(col(c, a * aa)))
    vis = lambda n_: dot(n_, VV) > 1e-6
    for bu in (-1.95, 1.95):
        obox(cv, Pt(bu, 0, 0.42), u, v, w, 0.8, 0.72, 0.2, '#2C3446', a)
        for sg in (1, -1):
            if not vis(mul(v, sg)): continue
            for wu in (-0.45, 0.45): ocyl(cv, Pt(bu + wu, sg * 0.74, 0.36), mul(v, sg), 0.3, 0.04, '#3B4658', a, n=14, hub=0.4, glow=wglow)
    obox(cv, Pt(0, 0, (z0 + z1) / 2), u, v, w, L, Wd, (z1 - z0) / 2, BODY, a, cols={'w': ROOF})
    for sg in (1, -1):
        if not vis(mul(v, sg)): continue
        o = sg * (Wd + 0.004)
        qd([Pt(-L + 0.02, o, 1.02), Pt(L - 0.02, o, 1.02), Pt(L - 0.02, o, 1.25), Pt(-L + 0.02, o, 1.25)], ORANGE)
        for (u0, u1) in ((-2.75, -2.32), (-1.5, -0.4), (0.4, 1.5), (2.32, 2.75)):
            qd([Pt(u0, o, 1.62), Pt(u1, o, 1.62), Pt(u1, o, 2.5), Pt(u0, o, 2.5)], NAVY)
            qd([Pt(u0 + 0.05, o, 2.3), Pt(u0 + 0.3, o, 2.5), Pt(u0 + 0.45, o, 2.5), Pt(u0 + 0.2, o, 2.3)], WHITE, 0.22)
        for du in (-1.95, 0.0, 1.95):
            qd([Pt(du - 0.32, o, 0.62), Pt(du + 0.32, o, 0.62), Pt(du + 0.32, o, 2.72), Pt(du - 0.32, o, 2.72)], '#E6DED2')
            if doors > 0.01: qd([Pt(du - 0.28 * doors, o, 0.64), Pt(du + 0.28 * doors, o, 0.64), Pt(du + 0.28 * doors, o, 2.68), Pt(du - 0.28 * doors, o, 2.68)], '#3A4560')
            for sd in (-1, 1):
                w0, w1 = du + sd * 0.04, du + sd * 0.27
                qd([Pt(w0, o, 1.75), Pt(w1, o, 1.75), Pt(w1, o, 2.55), Pt(w0, o, 2.55)], NAVY, 1 - doors)
    if lead and vis(u):
        o = L + 0.004
        qd([Pt(o, -Wd + 0.12, 1.85), Pt(o, Wd - 0.12, 1.85), Pt(o, Wd - 0.12, 2.78), Pt(o, -Wd + 0.12, 2.78)], NAVY)
        qd([Pt(o, -Wd + 0.2, 2.5), Pt(o, -Wd + 0.6, 2.78), Pt(o, -Wd + 0.85, 2.78), Pt(o, -Wd + 0.45, 2.5)], WHITE, 0.22)
        qd([Pt(o, -Wd, 0.8), Pt(o, Wd, 0.8), Pt(o, Wd, 1.35), Pt(o, -Wd, 1.35)], ORANGE)
        for sg in (1, -1): hl = p3(Pt(o, sg * 0.72, 1.6)); cv.drawCircle(hl[0], hl[1], 7, P(col('#FFF2C8', a))); cv.drawCircle(hl[0], hl[1], 16, P(col('#FFE2A0', 0.35 * a), blur=8))
    obox(cv, Pt(-1.2, 0, z1 + 0.16), u, v, w, 0.95, 0.62, 0.16, '#CFC6B8', a)
    if panto > 0:
        pa_, pm_, pt_ = p3(Pt(1.0, 0, z1 + 0.05)), p3(Pt(1.55, 0, z1 + 0.62 * panto)), p3(Pt(1.0, 0, z1 + 1.25 * panto))
        cv.drawPath(poly([pa_, pm_, pt_], False), P(col(NAVY2, a), stroke=3))
        l0, l1 = p3(Pt(1.0, -0.55, z1 + 1.25 * panto)), p3(Pt(1.0, 0.55, z1 + 1.25 * panto)); cv.drawLine(l0[0], l0[1], l1[0], l1[1], P(col(NAVY2, a), stroke=4))
def car_pose(path, sc, dev=0.0, yaw=0.0, roll=0.0, drop=0.0):
    x, y, h = path(sc); h += yaw
    u, v = (math.cos(h), math.sin(h), 0.0), (-math.sin(h), math.cos(h), 0.0)
    base = add((x, y, 0.0), mul(v, -dev))
    if roll <= 0: return add(base, (0, 0, -drop)), u, v, ZZ
    Wd = 1.1; piv = add(base, mul(v, -Wd))                                     # terguling ke sisi luar (-v) di tepi bawah luar
    w2 = add(mul(ZZ, math.cos(roll)), mul(v, -math.sin(roll))); v2 = add(mul(v, math.cos(roll)), mul(ZZ, math.sin(roll)))
    return add(piv, add(mul(v2, Wd), (0, 0, -drop))), u, v2, w2
def scenery(cv, t, a):
    objs = []
    for (x, y, w_, d_, h_, c) in ((-8.0, -2.5, 3.0, 3.0, 2.6, '#F1E6D8'), (-3.0, 1.0, 2.6, 2.8, 3.6, '#FAF6F0'), (-12.0, 2.0, 3.2, 2.6, 2.2, '#EBDDCB'),
                                  (2.0, 4.5, 2.6, 2.4, 2.8, '#F5ECE1'), (14.0, -12.0, 3.0, 3.0, 3.0, '#F1E6D8'), (-6.0, -16.0, 3.0, 2.6, 2.6, '#F5ECE1'),
                                  (15.0, 3.0, 2.8, 2.8, 2.4, '#EBDDCB'), (-16.0, 6.0, 3.0, 3.0, 3.2, '#FAF6F0')):
        objs.append((x + y, ('house', x, y, w_, d_, h_, c)))
    for (x, y) in ((-4.5, -5.0), (0.5, -1.5), (-9.5, 4.5), (4.5, 8.0), (12.0, -6.0), (16.5, -2.0), (-1.0, -14.0), (6.0, -15.0), (-14.0, -3.0), (13.0, 9.0)):
        objs.append((x + y, ('tree', x, y)))
    return objs
def draw_obj(cv, ob, a):
    if ob[0] == 'house':
        _, x, y, w_, d_, h_, c = ob
        box(cv, WORLD, x, y, 0, w_, d_, h_, c, a, top=0.3, left=0.02, right=-0.14)
        quad(cv, WORLD, [(x - 0.15, y - 0.15, h_), (x + w_ + 0.15, y - 0.15, h_), (x + w_ + 0.15, y + d_ + 0.15, h_), (x - 0.15, y + d_ + 0.15, h_)], '#E08A4C', a)
        for k in range(int((w_ - 0.4) / 0.7)):
            xx = x + 0.4 + k * 0.7; quad(cv, WORLD, [(xx, y + d_, 0.9), (xx + 0.4, y + d_, 0.9), (xx + 0.4, y + d_, 1.5), (xx, y + d_, 1.5)], NAVY, 0.85 * a)
    else:
        _, x, y = ob; p = P3(x, y, 1.7); box(cv, WORLD, x - 0.12, y - 0.12, 0, 0.24, 0.24, 1.0, '#8C6A4A', a, top=0.2)
        cv.drawCircle(p[0], p[1], 46, P(shader=rg(p[0] - 14, p[1] - 17, 70, [col('#F4C27A', a), col(ORANGE_D, a)])))
def ground(cv, a, x0=-40, x1=40, y0=-40, y1=40):
    quad(cv, WORLD, [(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], '#EDE4D6', a, grad=((x0, y1, 0), (x1, y0, 0), '#F3EBDF', '#E2D6C4'))
def poles(path, s0, s1, step=6.5, side=-1):
    out = []
    for k in range(int(math.ceil(s0 / step)), int(s1 / step) + 1):
        x, y, h = path(k * step); v = (-math.sin(h), math.cos(h), 0.0); b = add((x, y, 0.0), mul(v, side * 2.3))
        out.append((b[0] + b[1], ('pole', b, add((x, y, 0.0), mul(v, side * 0.1)))))
    return out
def draw_pole(cv, ob, a):
    _, b, tip = ob
    p0, p1 = P3(b[0], b[1], 0), P3(b[0], b[1], 4.9); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY2, a), stroke=5))
    p2 = P3(tip[0], tip[1], 4.75); cv.drawLine(p1[0], p1[1], p2[0], p2[1], P(col(NAVY2, a), stroke=3.5))
def wire(cv, a, path, s0, s1):
    n = int((s1 - s0) / 0.6); pts = []
    for k in range(n + 1):
        s = s0 + (s1 - s0) * k / n; x, y, h = path(s); pts.append(P3(x, y, 4.4))
    cv.drawPath(poly(pts, False), P(col(NAVY2, 0.8 * a), stroke=2))

# ------------------------------------------------------------ A: HOOK — KRL ke tikungan; kalau rodanya datar -> anjlok -> REWIND -> belok mulus (0 - 7.312)
T_RIG, T_DER, T_HIT, T_RW, T_BACK = 1.05, 1.65, 2.45, 2.9, 3.7
V0 = 7.0
def head_s(t):
    """posisi kepala kereta & progres anjlok (q) untuk waktu animasi t"""
    if t >= T_BACK: return LH1 - 3.15 + V0 * (t - T_BACK), 0.0
    if t >= T_RW: te = lerp(T_HIT, 1.2, eio(prog(t, T_RW, T_BACK)))
    else: te = t
    if te < T_DER: return LH1 + V0 * (te - T_DER), 0.0
    tau = min(te - T_DER, 0.8); return LH1 + V0 * tau - 4.375 * tau * tau, ei(tau / 0.8)
def train(cv, t, a, sh, q, wglow=0.0, path=hpath, n=3, objs=None, doors=0.0, panto=1.0):
    out = []
    for i in range(n):
        sc = sh - 2.9 - i * 6.3
        if q > 0:
            k = (1.0, 0.5, 0.18)[i]
            base, u, v, w = car_pose(spath, sc, dev=2.0 * q * k, yaw=-0.5 * q * k, roll=1.38 * q * (1.0, 0.3, 0.06)[i], drop=0.15 * q * k)
        else: base, u, v, w = car_pose(path, sc)
        out.append((base[0] + base[1], ('car', base, u, v, w, i == 0, wglow, panto * (1 - q) if i == 0 else 0.0, doors)))
    return out
def draw_scene(cv, t, a, objs):
    for _, ob in sorted(objs, key=lambda o: o[0]):
        if ob[0] == 'car': tcar(cv, ob[1], ob[2], ob[3], ob[4], a, lead=ob[5], wglow=ob[6], panto=ob[7], doors=ob[8])
        elif ob[0] == 'pole': draw_pole(cv, ob, a)
        else: draw_obj(cv, ob, a)
def gA(cv, t):
    sh, q = head_s(t)
    zin = eio(prog(t, T_BACK + 0.3, 5.6))
    pan = eio(prog(t, 0.0, 1.5)); fw = P3(lerp(lerp(-4.0, 2.5, pan), 6.5, zin), lerp(lerp(-8.6, -6.0, pan), -3.5, zin), 1.0); zoom = lerp(lerp(0.86, 0.95, eio(prog(t, 0, 2.4))), 1.12, zin)
    hit = prog(t, T_HIT, T_HIT + 0.45); shk = 14 * math.sin(t * 60) * (1 - hit) if T_HIT < t < T_HIT + 0.45 else 0.0
    sx, sy = 540 + shk, lerp(1090, 960, zin)
    wg = eo(prog(t, 4.6, 5.0)) * (0.7 + 0.3 * math.sin(t * 6))
    cv.save(); cam(cv, fw[0], fw[1], zoom, sx, sy)
    ground(cv, 1.0); track_top(cv, 1.0, 0.0, LH1 + ARCH + 22, hpath)
    objs = scenery(cv, t, 1.0) + poles(hpath, 0.0, LH1 + ARCH + 22) + train(cv, t, 1.0, sh, q, wglow=wg)
    draw_scene(cv, t, 1.0, objs)
    wire(cv, 1.0, hpath, 0.0, LH1 + ARCH + 22)
    if T_DER < t < T_RW:                                                       # percikan di roda depan
        base, u, v, w = car_pose(spath, sh - 2.9, dev=2.0 * q, yaw=-0.5 * q, roll=1.38 * q, drop=0.15 * q)
        for bu in (1.95, -1.95):
            p = p3(add(base, add(mul(u, bu), mul(v, -1.0)))); sparks(cv, p[0], p[1], t, 7 + int(bu), 1.0 - prog(t, T_HIT + 0.2, T_RW), n=16, spread=120)
    if T_HIT - 0.02 < t < T_HIT + 0.9:                                          # debu
        qq = prog(t, T_HIT - 0.02, T_HIT + 0.9); rnd = random.Random(5)
        base, u, v, w = car_pose(spath, sh - 2.9, dev=2.0, yaw=-0.5, roll=1.38, drop=0.15)
        for k in range(22):
            ang = rnd.uniform(math.pi, math.tau); L = 50 + 200 * eo(qq); c0 = p3(add(base, add(mul(u, rnd.uniform(-3, 3)), mul(v, rnd.uniform(-2.5, 0.5)))))
            cv.drawCircle(c0[0] + math.cos(ang) * L * 0.5, c0[1] + math.sin(ang) * L * 0.3, 30 + 50 * qq, P(col('#D9C7AE', 0.55 * (1 - qq)), blur=12))
    cv.restore()
    S = lambda w_: scr(P3(*w_), fw, zoom, sx, sy)
    fl = bump(prog(t, T_HIT, T_HIT + 0.3))
    if fl > 0: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.25 * fl)))
    la = eo(prog(t, 0.25, 0.55)) * (1 - prog(t, T_RIG - 0.15, T_RIG + 0.05))
    if la > 0:
        base, u, v, w = car_pose(hpath, sh - 2.9); p = S(add(base, add(mul(u, 2.9), (0, 0, 2.3)))); label(cv, 'NGGAK PUNYA SETIR', p[0], p[1], 300, 1180, la, sub='rodanya nyatu sama poros')
    if T_RIG - 0.1 < t < T_RW + 0.1: chip(cv, 'KALAU RODANYA DATAR?', 540, 560, eo(prog(t, T_RIG - 0.1, T_RIG + 0.1)) * (1 - prog(t, T_RW - 0.1, T_RW + 0.1)), size=30, bg=RED)
    if T_HIT < t < T_RW + 0.1: text_c(cv, 'ANJLOK!', 540, 1200, 64, RED, eo(prog(t, T_HIT, T_HIT + 0.12)) * (1 - prog(t, T_RW - 0.05, T_RW + 0.1)), halo=1.0)
    rewind_fx(cv, t, T_RW, T_BACK)
    if t > 4.5:
        base, u, v, w = car_pose(hpath, sh - 2.9); p = S(add(base, add(mul(u, 1.95), add(mul(v, 0.8), (0, 0, 0.35)))))
        ra = eo(prog(t, 4.6, 4.95)) * (1 - prog(t, 7.0, 7.312))
        label(cv, 'RAHASIANYA DI RODA', p[0], p[1], 760, 1170, ra, sub='belok tanpa keluar rel'); check(cv, 920, 1100, 24, prog(t, 4.75, 5.1), ra)
    cards3(cv, t, 5.81, (('1', 'RODA KERUCUT'), ('2', 'BIBIR RODA'), ('3', 'REL MIRING')))

# ------------------------------------------------------------ B: roda kereta nggak datar, miring seperti kerucut (7.312 - 11.947)
def gB(cv, t):
    a0 = eo(prog(t, 7.312, 7.7))
    cutq = eio(prog(t, 7.98, 8.7))
    zin = eio(prog(t, 9.55, 10.25)) * (1 - eio(prog(t, 10.75, 11.45)))
    zout = eio(prog(t, 10.75, 11.45)); fa, fz, zoom = lerp(0.0, 0.66, zin), lerp(0.3, 0.42, zin), lerp(lerp(7.0, 5.6, zout), 11.0, zin)
    f = P3(*Wp(fa, 0, fz)); sx, sy = 540, 900
    tg = eo(prog(t, 9.78, 10.1)) * (0.75 + 0.25 * math.sin(t * 6))
    M = Mesh(zoom)
    track_sec(M, a0, scroll=t * 2.4, front=1 - cutq, slide=2.6 * cutq)
    c1, c2, ax, up, r1, r2 = ws_draw(M, a0, front=1 - cutq, slide=2.6 * cutq, spin=t * 7.0, tglow=tg)
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    M.draw(cv); pebbles(cv, a0 * cutq)
    sw = 1.0 / zoom
    fa_ = eo(prog(t, 8.55, 8.85)) * (1 - prog(t, 9.6, 9.85))                   # 'nggak datar': garis datar merah putus-putus vs tapak miring
    if fa_ > 0:
        for sg in (1, -1):
            p0, p1 = p3(sec_pt(c1, ax, up, -0.10, sg * (RW + 0.005))), p3(sec_pt(c1, ax, up, 0.13, sg * (RW + 0.005)))
            cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(RED, a0 * fa_), stroke=7 * sw, effect=skia.DashPathEffect.Make([16 * sw, 10 * sw], 0)))
    ca = eo(prog(t, 10.91, 11.3))
    if ca > 0:                                                                 # kerucut: perpanjangan tapak sampai ke puncak
        for cc, axw in ((c1, ax), (c2, mul(ax, -1))):
            s_ap = -0.10 + (RW + 0.005) / SL
            top0, bot0 = p3(sec_pt(cc, axw, up, -0.10, RW + 0.005)), p3(sec_pt(cc, axw, up, -0.10, -(RW + 0.005)))
            apx = p3(sec_pt(cc, axw, up, s_ap, 0.0))
            u_ = eo(prog(t, 10.91, 11.35)); ex = lambda p: (lerp(p[0], apx[0], u_), lerp(p[1], apx[1], u_))
            tri = poly([top0, ex(top0), ex(bot0), bot0]); cv.drawPath(tri, P(col(ORANGE, 0.16 * a0 * ca)))
            for pp in (top0, bot0):
                e_ = ex(pp); cv.drawLine(pp[0], pp[1], e_[0], e_[1], P(col(ORANGE, a0 * ca), stroke=5 * sw, effect=skia.DashPathEffect.Make([14 * sw, 9 * sw], 0)))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    la = eo(prog(t, 7.45, 7.8)) * (1 - prog(t, 8.5, 8.8))
    if la > 0: p = S(sec_pt(c1, ax, up, 0.0, RW)); label(cv, 'RODA KERETA', p[0], p[1], 820, 560, a0 * la, sub='dibelah di tengah')
    if fa_ > 0:
        p = S(sec_pt(c1, ax, up, 0.14, RW + 0.005)); xmark(cv, p[0] + 34, p[1] - 30, 22, a0 * fa_)
        chip(cv, 'NGGAK DATAR', 540, 1340, a0 * fa_, size=30, bg=RED)
    ma = eo(prog(t, 9.85, 10.2)) * (1 - prog(t, 10.75, 11.0))
    if ma > 0:
        p = S(sec_pt(c1, ax, up, 0.0, r_tread(0.0))); label(cv, 'PERMUKAAN MIRING', p[0], p[1], 300, 520, a0 * ma, sub='tapak roda (dibesar-besarkan)')
        chip(cv, 'MIRING', 540, 1340, a0 * ma, size=30, bg=ORANGE)
    if ca > 0:
        p = S(sec_pt(c1, ax, up, 0.6, 0.0)); label(cv, 'KAYAK KERUCUT', p[0], p[1], 780, 520, a0 * eo(prog(t, 11.05, 11.4)), sub='dua kerucut beradu alas')
        chip(cv, 'KERUCUT', 540, 1340, a0 * eo(prog(t, 11.1, 11.4)), size=30, bg=ORANGE); check(cv, 650, 1340, 22, prog(t, 11.2, 11.6), a0)

# ------------------------------------------------------------ C: saat belok, roda luar di bagian lebih besar -> jarak lebih jauh -> belok sendiri (11.947 - 19.383)
RCC = 3.0
def ring_vis(cv, cc, axw, s, r, c, a, w, rngk=None):
    e1, e2 = g.basis(axw); pts, segs = [], []
    th0, th1 = rngk or (0.0, math.tau)
    for k in range(61):
        th = th0 + (th1 - th0) * k / 60; d = add(mul(e1, math.cos(th)), mul(e2, math.sin(th)))
        if dot(d, VV) > 0: pts.append(p3(add(cc, add(mul(axw, s), mul(d, r)))))
        elif pts: segs.append(pts); pts = []
    if pts: segs.append(pts)
    for sp in segs:
        if len(sp) > 1: cv.drawPath(poly(sp, False), P(col(WHITE, a), stroke=w * 1.9)); cv.drawPath(poly(sp, False), P(col(c, a), stroke=w))
def topview(cv, t, a):
    """lintasan melengkung dilihat dari atas + sepasang roda berjalan; jejak rel luar (oranye) vs dalam (navy)"""
    phi0 = math.radians(-12); ph = phi0 + math.radians(31) * max(0.0, t - 15.45)
    f = P3(RCC * 0.7071, RCC * 0.7071, 0.0); zoom = 3.1; sx, sy = 540, 760
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy); ground(cv, a, -12, 14, -12, 14)
    phs = [math.radians(-50 + 2 * k) for k in range(96)]
    ring = lambda r_, z_: [P3(r_ * math.cos(q), r_ * math.sin(q), z_) for q in phs]
    cv.drawPath(poly(ring(RCC + 1.85, 0) + ring(RCC - 1.85, 0)[::-1]), P(col('#B9AE9F', a)))
    cv.drawPath(poly(ring(RCC + 1.3, 0.16) + ring(RCC - 1.3, 0.16)[::-1]), P(col('#CDC3B4', a)))
    for k in range(-20, 62):
        q0 = math.radians(k * 2.5); dq = 0.022
        qq = [P3(r_ * math.cos(q0 + s_ * dq), r_ * math.sin(q0 + s_ * dq), 0.18) for r_, s_ in ((RCC - 1.0, -1), (RCC - 1.0, 1), (RCC + 1.0, 1), (RCC + 1.0, -1))]
        cv.drawPath(poly(qq), P(col('#E8E0D3', a))); cv.drawPath(poly(qq), P(col('#9E9282', 0.55 * a), stroke=0.8))
    for r_ in (RCC + 0.6, RCC - 0.6):
        cv.drawPath(poly(ring(r_, 0.12), False), P(col('#4A5568', a), stroke=4)); cv.drawPath(poly(ring(r_, 0.2), False), P(col('#E4E9F0', a), stroke=2))
    tr = eo(prog(t, 15.6, 15.9))
    if tr > 0 and ph > phi0:
        for r_, c in ((RCC + 0.6, ORANGE), (RCC - 0.6, NAVY)):
            n = max(2, int((ph - phi0) / math.radians(1.5))); pts = [P3(r_ * math.cos(phi0 + (ph - phi0) * k / n), r_ * math.sin(phi0 + (ph - phi0) * k / n), 0.22) for k in range(n + 1)]
            cv.drawPath(poly(pts, False), P(col(WHITE, a * tr), stroke=9)); cv.drawPath(poly(pts, False), P(col(c, a * tr), stroke=5.5))
    M = Mesh(zoom); d = 0.05
    rad = (math.cos(ph), math.sin(ph), 0.0)
    c1 = add(mul(rad, RCC + 0.6 + d), (0, 0, r_tread(-d))); c2 = add(mul(rad, RCC - 0.6 + d), (0, 0, r_tread(d)))
    ax = nrm(sub(c1, c2)); spin = -t * 6
    def colw(i, th):
        if i == 7 and ((th - spin) % (math.tau / 5)) < 0.35: return '#6F7A8F'
        return STEEL_T if i == TREAD_SEG else STEEL_W
    for cc, axw in ((c1, ax), (c2, mul(ax, -1))): lathe(M, cc, axw, WPROF, colw, a, 32)
    lathe(M, mul(add(c1, c2), 0.5), ax, AXP, '#7C879B', a, 16)
    M.draw(cv)
    ring_vis(cv, c1, ax, -d, r_tread(-d), ORANGE, a * tr, 4.5); ring_vis(cv, c2, mul(ax, -1), d, r_tread(d), NAVY, a * tr, 4.5)
    ga = eo(prog(t, 17.41, 17.8))
    if ga > 0:                                                                 # panah arah belok di depan roda
        pts = [P3(RCC * math.cos(ph + math.radians(14 + 1.5 * k)), RCC * math.sin(ph + math.radians(14 + 1.5 * k)), 0.35) for k in range(int(22 * ga) + 2)]
        cv.drawPath(poly(pts, False), P(col(WHITE, a * ga), stroke=14)); cv.drawPath(poly(pts, False), P(col(ORANGE, a * ga), stroke=8))
        if len(pts) > 2: arrow(cv, pts[-3], pts[-1], ORANGE, a * ga, w=8, head=18)
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    return S, ph
def gC(cv, t):
    a0 = eo(prog(t, 11.947, 12.35))
    ph2 = eio(prog(t, 15.3, 15.8))
    if ph2 < 1:
        aa = a0 * (1 - ph2)
        d = 0.055 * eio(prog(t, 12.1, 12.9))
        zoom = lerp(7.6, 8.4, eio(prog(t, 11.947, 15.3))); f = P3(*Wp(0.05, 0, 0.32)); sx, sy = 540, 860
        M = Mesh(zoom); track_sec(M, 1.0, scroll=t * 2.4)
        c1, c2, ax, up, r1, r2 = ws_draw(M, 1.0, d=d, spin=t * 7.0)
        layer(cv, aa)
        cv.save(); cam(cv, f[0], f[1], zoom, sx, sy); M.draw(cv); pebbles(cv, 1.0)
        sw = 1.0 / zoom; ra = eo(prog(t, 12.98, 13.4))
        if ra > 0:
            rk1, rk2 = half_range(ax, TT), half_range(mul(ax, -1), TT)
            ring_vis(cv, c1, ax, -d, r1, ORANGE, ra, 9 * sw, rk1); ring_vis(cv, c2, mul(ax, -1), d, r2, NAVY, ra, 9 * sw, rk2)
            for cc, axw, s, r, c in ((c1, ax, -d, r1, ORANGE), (c2, mul(ax, -1), d, r2, NAVY)):
                p0, p1 = p3(sec_pt(cc, axw, up, s, 0.0)), p3(sec_pt(cc, axw, up, s, -r))
                cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(WHITE, ra), stroke=14 * sw)); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(c, ra), stroke=8 * sw))
                cv.drawCircle(p1[0], p1[1], 12 * sw, P(col(WHITE, ra))); cv.drawCircle(p1[0], p1[1], 8 * sw, P(col(c, ra)))
        cv.restore()
        S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
        ka = eo(prog(t, 12.05, 12.35))
        if ka > 0:
            chip(cv, 'SAAT BELOK', 540, 330, ka, size=30, bg=INK)
            pc = S(Wp(0.0, 0, 1.25)); arrow(cv, (pc[0] - 90, pc[1]), (pc[0] + 110, pc[1]), NAVY, ka * (0.75 + 0.25 * math.sin(t * 6)), w=9, head=22)
            text_c(cv, 'TERDORONG KE LUAR', pc[0] + 10, pc[1] - 46, 24, NAVY, ka, halo=1.0)
        if ra > 0:
            p = S(sec_pt(c1, ax, up, -d, -r1 * 0.55)); label(cv, 'RODA LUAR', p[0], p[1], 830, 1170, ra, sub='bagian lebih besar')
            p = S(sec_pt(c2, mul(ax, -1), up, d, -r2 * 0.55)); label(cv, 'RODA DALAM', p[0], p[1], 250, 1170, ra, dot=NAVY, sub='bagian lebih kecil')
        cv.restore()
    if ph2 > 0:
        layer(cv, a0 * ph2)
        S, ph = topview(cv, t, 1.0)
        la = eo(prog(t, 15.9, 16.3))
        if la > 0:
            pm = S(((RCC + 0.6) * math.cos(math.radians(8)), (RCC + 0.6) * math.sin(math.radians(8)), 0.2))
            label(cv, 'LEBIH JAUH', pm[0], pm[1], 820, 1180, la, sub='jejak roda luar')
            pn = S(((RCC - 0.6) * math.cos(math.radians(2)), (RCC - 0.6) * math.sin(math.radians(2)), 0.2))
            label(cv, 'LEBIH PENDEK', pn[0], pn[1], 800, 400, la, dot=NAVY, sub='jejak roda dalam')
        ba = eo(prog(t, 17.41, 17.75))
        if ba > 0: chip(cv, 'BELOK SENDIRI', 540, 1340, ba, size=30, bg=ORANGE); check(cv, 712, 1340, 22, prog(t, 17.55, 17.95), ba)
        cv.restore()

# ------------------------------------------------------------ D: bibir roda di sisi dalam = pengaman terakhir (19.383 - 25.554)
GAP = 0.0625
def gD(cv, t):
    a0 = eo(prog(t, 19.383, 19.75))
    sh = eio(prog(t, 23.3, 23.75)) * (1 - 0.15 * eio(prog(t, 24.3, 24.8)))
    d = -0.01 + (GAP + 0.01) * sh
    zoom = lerp(12.5, 13.2, eio(prog(t, 19.383, 25.554))); f = P3(*Wp(0.56, 0, 0.36)); sx, sy = 540, 860
    fg = eo(prog(t, 20.0, 20.35)) * (0.75 + 0.25 * math.sin(t * 6))
    hitp = prog(t, 23.72, 24.1)
    M = Mesh(zoom); track_sec(M, a0, scroll=t * 2.4, rail_glow=(0.6 * bump(hitp), 0.0))
    c1, c2, ax, up, r1, r2 = ws_draw(M, a0, d=d, fglow=fg, spin=t * 7.0)
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy); M.draw(cv); pebbles(cv, a0)
    sw = 1.0 / zoom
    if fg > 0:                                                                 # bibir roda di potongan: oranye
        for sg in (1, -1):
            pts = [p3(sec_pt(c1, ax, up, s, sg * r)) for s, r in FLANGE_POLY]; cv.drawPath(poly(pts), P(col(ORANGE, 0.85 * a0 * fg / (0.75 + 0.25 * math.sin(t * 6)) if fg else 0)))
    ga = eo(prog(t, 21.0, 21.3)) * (1 - prog(t, 23.25, 23.45))
    if ga > 0:                                                                 # celah antara bibir roda dan rel
        y_ = -0.02; p0, p1 = p3(Wp(0.6 - 0.0375, 0, y_)), p3(Wp(0.6 - 0.0375 - GAP - d + 0.0, 0, y_))
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(NAVY, a0 * ga), stroke=4 * sw))
        for pp in (p0, p1): cv.drawLine(pp[0], pp[1] - 14 * sw, pp[0], pp[1] + 14 * sw, P(col(NAVY, a0 * ga), stroke=4 * sw))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    if t > 23.7 and t < 24.4:
        p = S(Wp(0.6 - 0.0375, 0, 0.02)); sparks(cv, p[0], p[1], t, 31, a0 * (1 - prog(t, 24.0, 24.4)), n=14, spread=110)
    la = eo(prog(t, 20.0, 20.35))
    if la > 0: p = S(sec_pt(c1, ax, up, -0.14, -(RW + 0.045))); label(cv, 'BIBIR RODA', p[0], p[1], 280, 1180, a0 * la, sub='di sisi dalam roda')
    if ga > 0: p = S(Wp(0.6 - 0.0375 - GAP / 2, 0, -0.02)); text_c(cv, 'CELAH', p[0], p[1] + 60, 26, NAVY, a0 * ga, halo=1.0)
    pa = eo(prog(t, 21.83, 22.15))
    if pa > 0: chip(cv, 'PENGAMAN TERAKHIR', 540, 1340, a0 * pa, size=30, bg=INK)
    if t > 23.24:
        pc = S(Wp(0.62, 0, 1.0)); aa = a0 * eo(prog(t, 23.24, 23.45)) * (1 - prog(t, 23.9, 24.2))
        arrow(cv, (pc[0] - 120, pc[1]), (pc[0] + 120, pc[1]), NAVY, aa, w=10, head=24)
    ha = eo(prog(t, 23.8, 24.1))
    if ha > 0:
        p = S(Wp(0.6 - 0.0375, 0, 0.02)); label(cv, 'TERTAHAN REL', p[0], p[1], 800, 520, a0 * ha, sub='roda nggak lolos keluar')
        check(cv, 878, 1340, 22, prog(t, 23.9, 24.3), a0 * ha)

# ------------------------------------------------------------ E: di tikungan rel luar lebih tinggi -> kereta sedikit miring melawan dorongan ke luar (25.554 - 32.608)
def rrect_pts(a0, z0, a1, z1, rt, rb, n=6):
    pts = []
    for (cx, cz, r, st) in ((a1 - rb, z0 + rb, rb, -90), (a1 - rt, z1 - rt, rt, 0), (a0 + rt, z1 - rt, rt, 90), (a0 + rb, z0 + rb, rb, 180)):
        for k in range(n + 1):
            an = math.radians(st + 90 * k / n); pts.append((cx + r * math.cos(an), cz + r * math.sin(an)))
    return pts
CAR_OUT = rrect_pts(-1.45, 1.12, 1.45, 4.0, 0.42, 0.12)
CAR_IN = rrect_pts(-1.33, 1.34, 1.33, 3.86, 0.32, 0.02)
SKIN, HAIR = '#E8C9A0', '#2A1F17'
def person(cv, R2, ax_, z_floor, ang, shirt, a, seated=0, face=1, arm_to=None, h=1.62):
    """orang dilihat dari depan potongan (koordinat a, z), berdiri di z_floor, condong 'ang' (rad, + ke kanan)"""
    def Q(da, dz):
        x_ = ax_ + da * math.cos(ang) + dz * math.sin(ang); z = z_floor - da * math.sin(ang) + dz * math.cos(ang)
        return p3(Wp(*(lambda q: (q[0], 0, q[1]))(R2(x_, z))))
    s = 50.0
    if seated:
        hip, knee, foot = Q(0, 0.45), Q(face * 0.42, 0.47), Q(face * 0.48, 0.0)
        cv.drawPath(poly([hip, knee, foot], False), P(col(NAVY2, a), stroke=0.15 * s))
        torso_top = Q(-face * 0.04, 1.05); cv.drawLine(hip[0], hip[1], torso_top[0], torso_top[1], P(col(shirt, a), stroke=0.3 * s))
        hd = Q(-face * 0.02, 1.27)
    else:
        for lx in (-0.1, 0.1): f0, f1 = Q(lx, 0.0), Q(lx, 0.8); cv.drawLine(f0[0], f0[1], f1[0], f1[1], P(col(NAVY2, a), stroke=0.14 * s))
        t0, t1 = Q(0, 0.82), Q(0, 1.32); cv.drawLine(t0[0], t0[1], t1[0], t1[1], P(col(shirt, a), stroke=0.36 * s))
        if arm_to is not None:
            sh_ = Q(0.14 * (1 if arm_to[0] > ax_ else -1), 1.3); cv.drawLine(sh_[0], sh_[1], arm_to[1][0], arm_to[1][1], P(col(shirt, a), stroke=0.1 * s))
        hd = Q(0, h - 0.13)
    cv.drawCircle(hd[0], hd[1], 0.15 * s, P(col(SKIN, a))); cv.drawArc(skia.Rect(hd[0] - 0.155 * s, hd[1] - 0.16 * s, hd[0] + 0.155 * s, hd[1] + 0.12 * s), 180, 180, False, P(col(HAIR, a)))
def gE(cv, t):
    a0 = eo(prog(t, 25.554, 25.95))
    push = eo(prog(t, 26.23, 26.7))
    hq = eio(prog(t, 27.3, 28.7)); TH = math.radians(13.0); psi = TH * hq
    th_e = TH * push * (1 + 0.06 * math.sin(t * 5))                            # arah tali pegangan (dunia)
    R2 = R2f(psi)
    zoom = lerp(3.55, 3.7, eio(prog(t, 25.554, 32.608))); f = P3(*Wp(0.0, 0, 1.75)); sx, sy = 540, 880
    rg_ = eo(prog(t, 27.18, 27.5)) * (0.7 + 0.3 * math.sin(t * 6)) * (1 - 0.6 * prog(t, 29.3, 29.8))
    M = Mesh(zoom); track_sec(M, a0, scroll=t * 2.4, psi=psi, rail_glow=(rg_, 0.0))
    c1, c2, ax, up, r1, r2 = ws_draw(M, a0, psi=psi, spin=t * 7.0, n=28)
    Wr = lambda a_, z_: Wp(*(lambda q: (q[0], 0, q[1]))(R2(a_, z_)))
    eA, eZ = nrm(sub(Wr(1, 0), Wr(0, 0))), nrm(sub(Wr(0, 1), Wr(0, 0)))
    o0 = Wr(0, 0)
    for sd in (1, -1):                                                         # rangka bogie
        prism(M, [(sd * 0.92, 0.42), (sd * 1.04, 0.42), (sd * 1.04, 0.98), (sd * 0.92, 0.98)], o0, eA, eZ, TT, -2.2, 0.0, '#2C3446', a0, segs=3, capc='#3B4658')
    prism(M, [(-1.04, 0.86), (1.04, 0.86), (1.04, 1.0), (-1.04, 1.0)], o0, eA, eZ, TT, -2.2, 0.0, '#2C3446', a0, segs=3, capc='#3B4658')
    prism(M, CAR_OUT, o0, eA, eZ, TT, -9.0, 0.0, lambda i: ROOF if 7 <= i <= 19 else BODY, a0, segs=9, cap1=False)
    prism(M, [(-0.75, 4.0), (0.25, 4.0), (0.25, 4.28), (-0.75, 4.28)], o0, eA, eZ, TT, -3.5, -1.2, '#CFC6B8', a0, segs=2)
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy); M.draw(cv); pebbles(cv, a0)
    sw = 1.0 / zoom
    Q2 = lambda a_, z_: p3(Wr(a_, z_))
    for sd in (1, -1):                                                         # pegas suspensi
        for k in range(5):
            p0, p1 = Q2(sd * 0.8 - 0.1, 1.0 + k * 0.024), Q2(sd * 0.8 + 0.1, 1.012 + k * 0.024); cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col('#4A5568', a0), stroke=3 * sw))
    outer = poly([Q2(*p) for p in CAR_OUT]); inner = poly([Q2(*p) for p in CAR_IN])
    cv.save(); cv.clipPath(inner, doAntiAlias=True)
    fl0, fl1 = Q2(0, 1.34), Q2(0, 3.86)
    cv.drawPath(inner, P(shader=lg(fl0[0], fl0[1], fl1[0], fl1[1], [col('#D8CDBE', a0), col('#EFE6DA', a0)])))
    for sd in (1, -1):                                                         # bangku memanjang (tampak menjauh)
        a_in, a_out = sd * 0.86, sd * 1.33
        q = [p3(add(Wr(a_in, 1.76), mul(TT, tt_))) for tt_ in (0, -7)] + [p3(add(Wr(a_out, 1.76), mul(TT, tt_))) for tt_ in (-7, 0)]
        cv.drawPath(poly(q), P(col('#F6C597', 0.9 * a0)))
        q = [p3(add(Wr(sd * 1.2, 2.45), mul(TT, tt_))) for tt_ in (0, -7)] + [p3(add(Wr(a_out, 2.45), mul(TT, tt_))) for tt_ in (-7, 0)]
        cv.drawPath(poly(q), P(col('#F0A868', 0.55 * a0)))
    for tt_ in (-1.2, -0.6):                                                   # tali pegangan di belakang (lebih jauh, lebih pudar)
        for sd in (1, -1):
            top_ = add(Wr(sd * 0.62, 3.5), mul(TT, tt_)); bot = add(top_, (0, 0, 0))
            p0 = p3(top_); L_ = 0.42 * 50
            cv.drawLine(p0[0], p0[1], p0[0] + L_ * math.sin(th_e) * 1.22, p0[1] + L_ * math.cos(th_e), P(col(NAVY, 0.35 * a0), stroke=3 * sw))
    for sd in (1, -1):                                                         # dudukan + penumpang duduk
        cv.drawPath(poly([Q2(sd * 0.86, 1.34), Q2(sd * 1.33, 1.34), Q2(sd * 1.33, 1.76), Q2(sd * 0.86, 1.76)]), P(col(ORANGE, a0)))
        cv.drawPath(poly([Q2(sd * 1.22, 1.76), Q2(sd * 1.33, 1.76), Q2(sd * 1.33, 2.45), Q2(sd * 1.22, 2.45)]), P(col(ORANGE_D, a0)))
    lean = math.radians(9) * push * (1 - hq)
    person(cv, R2, -1.02, 1.76, lean * 0.5, '#C9CED8', a0, seated=1, face=1)
    person(cv, R2, 1.02, 1.76, lean * 0.5, '#F2B5A0', a0, seated=1, face=-1)
    straps = []
    for sd in (1, -1):                                                         # tali pegangan di bidang potong: tergantung searah gravitasi efektif
        b0 = Q2(sd * 0.62, 3.5); L_ = 0.42 * 50
        sa = th_e
        e = (b0[0] + L_ * math.sin(sa) * 1.22, b0[1] + L_ * math.cos(sa))
        straps.append(e)
    person(cv, R2, -0.42, 1.34, lean, NAVY, a0, arm_to=(-0.62, straps[1]))
    person(cv, R2, 0.42, 1.34, lean, ORANGE, a0, arm_to=(0.62, straps[0]))
    for sd, e in zip((1, -1), straps):
        b0 = Q2(sd * 0.62, 3.5)
        cv.drawLine(b0[0], b0[1], e[0], e[1], P(col(NAVY, a0), stroke=3.5 * sw))
        cv.drawCircle(e[0], e[1] + 5, 8, P(col(ORANGE, a0), stroke=4 * sw))
        cv.drawCircle(b0[0], b0[1], 6, P(col('#8E9AAF', a0)))
    cv.restore()
    ring = skia.Op(outer, inner, skia.PathOp.kDifference_PathOp)
    cv.drawPath(ring, P(col('#F3EEE6', a0))); cv.drawPath(ring, P(col(NAVY, a0), stroke=2.5 * sw))
    so = poly([Q2(1.45, 1.6), Q2(1.45, 1.86), Q2(1.33, 1.86), Q2(1.33, 1.6)]); cv.drawPath(so, P(col(ORANGE, a0)))
    so = poly([Q2(-1.45, 1.6), Q2(-1.45, 1.86), Q2(-1.33, 1.86), Q2(-1.33, 1.6)]); cv.drawPath(so, P(col(ORANGE, a0)))
    aa = eo(prog(t, 29.3, 29.7))
    if aa > 0 and psi > 0.01:                                                  # sudut miring di bantalan
        piv = Q2(-0.6, -0.17); L_ = 1.85 * 61
        e0 = (piv[0] + L_, piv[1]); e1 = Q2(1.25, -0.17)
        cv.drawLine(piv[0], piv[1], e0[0], e0[1], P(col(NAVY, a0 * aa), stroke=3 * sw, effect=skia.DashPathEffect.Make([10 * sw, 7 * sw], 0)))
        r_ = L_ * 0.8; ang = math.degrees(math.atan2(e1[1] - piv[1], e1[0] - piv[0]))
        cv.drawArc(skia.Rect(piv[0] - r_, piv[1] - r_, piv[0] + r_, piv[1] + r_), ang, -ang, False, P(col(ORANGE, a0 * aa), stroke=6 * sw))
    cv.restore()
    S = lambda w_: scr(P3(*w_), f, zoom, sx, sy)
    ca = eo(prog(t, 26.23, 26.55))
    if ca > 0: chip(cv, 'DI TIKUNGAN', 540, 300, a0 * ca, size=30, bg=INK)
    pa = eo(prog(t, 26.4, 26.8)) * (1 - 0.0 * prog(t, 30.7, 31))
    if pa > 0:
        pc = S(Wr(0.3, 2.6)); arrow(cv, (pc[0] + 60, pc[1] - 270), (pc[0] + 330, pc[1] - 270), NAVY, a0 * pa * (0.75 + 0.25 * math.sin(t * 6)), w=10, head=24)
        text_c(cv, 'DORONGAN KE LUAR', pc[0] + 190, pc[1] - 320, 26, NAVY, a0 * pa, halo=1.0)
    ra = eo(prog(t, 27.18, 27.5)) * (1 - prog(t, 29.2, 29.4))
    if ra > 0: p = S(Wr(0.6, 0.0)); label(cv, 'REL LUAR LEBIH TINGGI', p[0], p[1], 760, 1180, a0 * ra, sub='peninggian rel di tikungan')
    ma = eo(prog(t, 29.3, 29.65)) * (1 - prog(t, 30.6, 30.8))
    if ma > 0: chip(cv, 'KERETA SEDIKIT MIRING', 540, 1340, a0 * ma, size=30, bg=ORANGE)
    wa = eo(prog(t, 30.77, 31.1))
    if wa > 0:
        pc = S(Wr(-0.3, 2.6)); arrow(cv, (pc[0] - 40, pc[1] - 200), (pc[0] - 300, pc[1] - 200), ORANGE, a0 * wa, w=10, head=24)
        chip(cv, 'MELAWAN DORONGAN', 540, 1340, a0 * wa, size=30, bg=ORANGE); check(cv, 772, 1340, 22, prog(t, 30.9, 31.3), a0 * wa)

# ------------------------------------------------------------ F: kereta listrik pertama, Batavia 1925, Tanjung Priok - Jatinegara (32.608 - 39.066)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def history_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1180)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'BATAVIA · 1925', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0, w=3: P(col(SEPIA_INK, al * a), stroke=w)
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(r.makeInset(26, 26), 12, 12), True)
    gy = 870
    cv.drawRect(skia.Rect(r.left(), gy, r.right(), r.bottom()), P(col('#D9BF92', a)))
    rnd = random.Random(8)
    for k in range(8):                                                         # kota lama
        x = r.left() + 30 + k * 110; h = rnd.uniform(90, 190)
        cv.drawRect(skia.Rect(x, gy - 40 - h, x + 90, gy - 40), P(col('#E8D7B5', a))); cv.drawRect(skia.Rect(x, gy - 40 - h, x + 90, gy - 40), ink(0.5, 2))
        tri = poly([(x - 6, gy - 40 - h), (x + 45, gy - 75 - h), (x + 96, gy - 40 - h)]); cv.drawPath(tri, P(col('#D9BF92', a))); cv.drawPath(tri, ink(0.5, 2))
    cv.drawLine(r.left(), gy - 6, r.right(), gy - 6, ink(1, 4)); cv.drawLine(r.left(), gy + 6, r.right(), gy + 6, ink(0.7, 3))
    for k in range(30): x = r.left() + k * 32; cv.drawLine(x, gy - 2, x + 10, gy + 14, ink(0.5, 3))
    wy = 520; cv.drawLine(r.left(), wy, r.right(), wy, ink(0.9, 2.5))           # kabel listrik atas
    for x in (220, 540, 860): cv.drawLine(x, gy - 6, x, wy - 20, ink(0.9, 5)); cv.drawLine(x, wy - 10, x + 40, wy - 10, ink(0.9, 3))
    lx = lerp(180, 330, eio(prog(t, 32.6, 39.0)))                              # lokomotif listrik + kereta (ilustrasi)
    def wagon(x0, w_, loco=False):
        body = skia.Rect(x0, gy - 175, x0 + w_, gy - 40)
        cv.drawRoundRect(body, 10, 10, P(col('#8C6A4A' if loco else '#B08A60', a))); cv.drawRoundRect(body, 10, 10, ink(1, 4))
        cv.drawRect(skia.Rect(x0 - 6, gy - 192, x0 + w_ + 6, gy - 175), P(col(SEPIA_INK, a)))
        n_ = 3 if loco else 4
        for k in range(n_):
            wx = x0 + 22 + k * (w_ - 44) / n_; cv.drawRect(skia.Rect(wx, gy - 150, wx + (w_ - 44) / n_ - 16, gy - 105), P(col(SEPIA, a))); cv.drawRect(skia.Rect(wx, gy - 150, wx + (w_ - 44) / n_ - 16, gy - 105), ink(0.8, 2))
        for wx in ((x0 + 40, x0 + 100, x0 + w_ - 100, x0 + w_ - 40) if loco else (x0 + 45, x0 + w_ - 45)):
            cv.drawCircle(wx, gy - 26, 22, P(col('#4A3626', a))); cv.drawCircle(wx, gy - 26, 22, ink(1, 3))
            sp_ = t * 8; cv.drawLine(wx, gy - 26, wx + 18 * math.cos(sp_), gy - 26 + 18 * math.sin(sp_), P(col(SEPIA, a), stroke=3))
    wagon(lx - 560, 260); wagon(lx - 290, 260); wagon(lx, 300, loco=True)
    pb, pt_ = (lx + 150, gy - 192), (lx + 150, wy)                              # pantograf
    cv.drawPath(poly([pb, (lx + 110, gy - 260), pt_], False), ink(1, 4)); cv.drawLine(lx + 115, wy, lx + 185, wy, ink(1, 5))
    sparks(cv, lx + 150, wy + 4, t, 41, 0.8 * a, n=8, spread=50)
    cv.restore()
    return lx
def gF(cv, t):
    a0 = eo(prog(t, 32.608, 33.0))
    zz = 1.0 + 0.02 * eio(prog(t, 32.608, 39.066))
    cv.save(); cv.translate(540, 715); cv.scale(zz, zz); cv.translate(-540, -715)
    lx = history_card(cv, t, a0)
    ra = eo(prog(t, 36.86, 37.2))                                              # peta rute di kartu
    if ra > 0:
        y = 1060; x0, x1 = 230, 850
        cv.drawLine(x0, y, x1, y, P(col(SEPIA_INK, a0 * ra), stroke=6))
        u = eio(prog(t, 37.0, 38.6)); cv.drawLine(x0, y, lerp(x0, x1, u), y, P(col(ORANGE, a0 * ra), stroke=10))
        for x, nm, t0 in ((x0, 'TANJUNG PRIOK', 36.86), (x1, 'JATINEGARA', 37.96)):
            qa = a0 * eo(prog(t, t0, t0 + 0.3)); cv.drawCircle(x, y, 18, P(col(WHITE, qa))); cv.drawCircle(x, y, 18, P(col(SEPIA_INK, qa), stroke=6))
            text_c(cv, nm, x, y - 46, 26, SEPIA_INK, qa)
        text_c(cv, '(dulu Meester Cornelis)', x1, y + 46, 20, SEPIA_INK, a0 * eo(prog(t, 38.1, 38.4)), f=B)
    cv.restore()
    la = eo(prog(t, 33.0, 33.35))
    if la > 0: label(cv, 'KERETA LISTRIK PERTAMA', 540 + (lx + 150 - 540) * zz, 715 + (870 - 230 - 715) * zz, 600, 1300, a0 * la * (1 - prog(t, 34.6, 34.75)), sub='ilustrasi')
    ya = eo(prog(t, 34.75, 35.05))
    if ya > 0:
        s_ = lerp(1.6, 1.0, bo(prog(t, 34.75, 35.1))); cv.save(); cv.translate(540, 1300); cv.scale(s_, s_); cv.translate(-540, -1300)
        chip(cv, 'TAHUN 1925', 540, 1300, a0 * ya, size=34, bg=ORANGE); cv.restore()

# ------------------------------------------------------------ G: sekarang ±1 juta orang naik KRL Jabodetabek setiap hari (39.066 - 44.11)
_rq = random.Random(21)
PEOPLE = [(_rq.uniform(-11, 11), _rq.uniform(2.4, 4.9), _rq.choice([NAVY, ORANGE, '#C9CED8', '#F2B5A0', ORANGE_D, '#7C879B']), _rq.uniform(0, 1), _rq.uniform(0.85, 1.1)) for _ in range(52)]
DOORS_X = [c + d for c in (-6.3, 0.0, 6.3) for d in (-1.95, 0.0, 1.95)]
def gG(cv, t):
    a0 = eo(prog(t, 39.066, 39.45))
    f = P3(0.5, 1.2, 1.5); zoom = lerp(0.95, 1.02, eio(prog(t, 39.066, 44.11))); sx, sy = 540, 930
    cv.save(); cam(cv, f[0], f[1], zoom, sx, sy)
    ground(cv, a0); track_top(cv, a0, 0.0, 60.0, tpath)
    objs = train(cv, t, a0, 30.0 + 2.9 + 6.3, 0.0, path=tpath, doors=eo(prog(t, 39.3, 39.8)))
    draw_scene(cv, t, a0, objs); wire(cv, a0, tpath, 0.0, 60.0)
    box(cv, WORLD, -13, 1.75, 0, 26, 3.6, 1.05, '#E9DFD0', a0, top=0.18, left=0.02, right=-0.12)
    quad(cv, WORLD, [(-13, 1.9, 1.051), (13, 1.9, 1.051), (13, 2.15, 1.051), (-13, 2.15, 1.051)], ORANGE, a0)
    walk = prog(t, 39.6, 43.6)
    figs = []
    for (x0, y0, c, ph, hs) in PEOPLE:
        dx = min(DOORS_X, key=lambda dd: abs(dd - x0))
        u = clamp(walk * 1.6 - ph * 0.6)
        if u >= 1: continue
        x = lerp(x0, dx, eio(u)); y = lerp(y0, 1.75, eio(u)); figs.append((x + y, x, y, c, u, hs, ph))
    for _, x, y, c, u, hs, ph in sorted(figs):
        aa = a0 * (1 - prog(u, 0.85, 1.0)); bob = 2.5 * abs(math.sin(t * 9 + ph * 6)) if 0 < u < 1 else 0
        p = P3(x, y, 1.05); h = 1.55 * hs * 50
        cv.drawOval(skia.Rect(p[0] - 12, p[1] - 5, p[0] + 12, p[1] + 5), P(col('#2B3A55', 0.18 * aa)))
        cv.drawRoundRect(skia.Rect(p[0] - 10, p[1] - h * 0.5 - bob, p[0] + 10, p[1]), 6, 6, P(col(NAVY2, aa)))
        cv.drawRoundRect(skia.Rect(p[0] - 13, p[1] - h * 0.86 - bob, p[0] + 13, p[1] - h * 0.42 - bob), 9, 9, P(col(c, aa)))
        cv.drawCircle(p[0], p[1] - h * 0.95 - bob, 10, P(col(SKIN, aa))); cv.drawArc(skia.Rect(p[0] - 10.5, p[1] - h * 0.95 - 11 - bob, p[0] + 10.5, p[1] - h * 0.95 + 8 - bob), 180, 180, False, P(col(HAIR, aa)))
    cv.restore()
    ca = eo(prog(t, 39.2, 39.55))
    if ca > 0:
        r = skia.Rect(250, 250, 830, 450); card(cv, r, a0 * ca, rad=28)
        v = int(round(1000000 * eio(prog(t, 39.98, 41.3)) / 1000.0)) * 1000
        s = '±' + f'{v:,}'.replace(',', '.'); mono(cv, s, 540, 330, 66, ORANGE, a0 * ca, sp=2)
        text_c(cv, 'penumpang KRL per hari', 540, 405, 28, MUTED, a0 * ca, f=B)
    ka = eo(prog(t, 40.96, 41.3))
    if ka > 0: chip(cv, 'KRL JABODETABEK · SETIAP HARI', 540, 1340, a0 * ka, size=28, bg=INK)

# ------------------------------------------------------------ H: kirim ke teman anak KRL + komentar (44.11 - 48.771)
CMTS = [('eskalator dong', 290, 760, 46.6, ORANGE), ('tol layang!', 770, 900, 46.85, INK), ('kapal selam', 320, 1040, 47.1, ORANGE_D), ('bendungan!!', 760, 1180, 47.35, NAVY)]
def phone(cv, t, a):
    r = skia.Rect(330, 300, 750, 1080); card(cv, r, a, rad=48, fill=INK, edge=INK, shadow=0.3, lift=16)
    sc = r.makeInset(16, 16); cv.drawRoundRect(sc, 36, 36, P(col(bb.BG0, a)))
    cv.save(); cv.clipRRect(skia.RRect.MakeRectXY(sc, 36, 36), True)
    cv.drawRect(sc, P(shader=lg(0, sc.top(), 0, sc.bottom(), [col('#FFF6EC', a), col('#F6D9BE', a)])))
    cx, cy = 520, 700                                                          # mini adegan: rel melengkung + gerbong
    pth = skia.Path(); pth.moveTo(360, 560); pth.quadTo(700, 640, 560, 900)
    cv.drawPath(pth, P(col('#B9AE9F', a), stroke=40)); cv.drawPath(pth, P(col('#4A5568', a), stroke=4))
    cv.save(); cv.translate(470, 640); cv.rotate(22 + 6 * math.sin(t * 3))
    cv.drawRoundRect(skia.Rect(-80, -26, 80, 26), 10, 10, P(col(BODY, a))); cv.drawRect(skia.Rect(-78, 2, 78, 10), P(col(ORANGE, a)))
    for k in range(4): cv.drawRect(skia.Rect(-68 + k * 38, -18, -42 + k * 38, -2), P(col(NAVY, a)))
    cv.restore()
    text_c(cv, 'KRL, kok nggak', 520, 420, 34, INK, a); text_c(cv, 'keluar rel?', 520, 462, 34, ORANGE, a)
    cv.restore()
    sx_, sy_ = 690, 860                                                        # tombol bagikan
    pz = 1 + 0.18 * bump(prog(t, 44.35, 44.7))
    cv.save(); cv.translate(sx_, sy_); cv.scale(pz, pz)
    cv.drawCircle(0, 0, 34, P(col(WHITE, a))); pl = poly([(-16, 4), (16, -12), (4, 16), (0, 6)]); cv.drawPath(pl, P(col(ORANGE, a)))
    cv.restore()
    return (sx_, sy_)
def gH(cv, t):
    a0 = eo(prog(t, 44.11, 44.45)); sw2 = eio(prog(t, 46.1, 46.5))
    if sw2 < 1:
        aa = a0 * (1 - sw2); layer(cv, aa)
        src = phone(cv, t, 1.0)
        for k, (fx, fy, nm, c) in enumerate(((190, 1160, 'teman', ORANGE), (540, 1215, 'anak KRL', NAVY), (890, 1160, 'sahabat', ORANGE_D))):
            q = prog(t, 44.45 + 0.15 * k, 45.05 + 0.15 * k)
            if q > 0:
                x = lerp(src[0], fx, eio(q)); y = lerp(src[1], fy, eio(q)) - 160 * bump(q)
                if q < 1:
                    pl = poly([(x - 18, y + 4), (x + 18, y - 12), (x + 4, y + 18), (x, y + 7)]); cv.drawPath(pl, P(col(ORANGE, 1.0)))
            fa = eo(prog(t, 44.9 + 0.15 * k, 45.2 + 0.15 * k))
            if fa > 0:
                s_ = lerp(0.6, 1, bo(prog(t, 44.9 + 0.15 * k, 45.3 + 0.15 * k)))
                cv.save(); cv.translate(fx, fy); cv.scale(s_, s_)
                cv.drawCircle(0, 6, 54, P(col('#2B3A55', 0.2 * fa), blur=10)); cv.drawCircle(0, 0, 52, P(col(c, fa)))
                cv.drawCircle(0, -12, 18, P(col(WHITE, fa))); cv.drawOval(skia.Rect(-28, 10, 28, 40), P(col(WHITE, fa)))
                cv.restore(); text_c(cv, nm, fx, fy + 80, 26, INK, fa, f=B)
        ka = eo(prog(t, 44.3, 44.6))
        if ka > 0: chip(cv, 'KIRIM KE TEMAN ANAK KRL', 540, 1340, ka, size=30, bg=ORANGE)
        cv.restore()
    if sw2 > 0:
        aa = a0 * sw2; layer(cv, aa)
        logo_mark(cv, 540, 430, 80 * lerp(0.6, 1, bo(prog(t, 46.1, 46.5))), 1.0, t)
        text_c(cv, 'BONGKAR APA LAGI?', 540, 590, 64, INK, eo(prog(t, 46.2, 46.5)))
        for txt, x, y, t0, c in CMTS:
            q = prog(t, t0, t0 + 0.3)
            if q <= 0: continue
            qa = clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
            cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
            r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, qa, rad=42, lift=10)
            cv.drawCircle(r.left() + 42, 0, 24, P(col(c, qa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, qa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, qa)))
            cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, qa)))
            cv.restore()
        ca = eo(prog(t, 47.0, 47.3))
        if ca > 0: chip(cv, 'TULIS DI KOMENTAR', 540, 1340, ca, size=30, bg=ORANGE)
        cv.restore()
def gJ(cv, t):
    tt = t - 48.771; a = eo(prog(tt, 0.0, 0.4)); p_ = bo(prog(tt, 0.0, 0.6))
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

bb.DRAWERS = [gA, gB, gC, gD, gE, gF, gG, gH, gJ]

def build_sfx():
    ev = [(0.0, 'rumble'), (0.05, 'whoosh'), (0.3, 'pop'), (1.05, 'buzzer'), (1.65, 'grind'), (1.9, 'crack'), (2.2, 'rumble'), (2.45, 'clunk'), (2.47, 'crack'),
          (2.9, 'rewind'), (3.7, 'shine'), (3.8, 'rumble'), (4.6, 'zap'), (4.75, 'ding'), (5.81, 'pop'), (5.96, 'pop'), (6.11, 'pop'),
          (7.312, 'whoosh'), (7.45, 'pop'), (7.98, 'chop'), (8.1, 'swish'), (8.55, 'buzzer'), (9.78, 'zap'), (9.85, 'pop'), (10.91, 'shine'), (11.2, 'ding'),
          (11.947, 'whoosh'), (12.05, 'swish'), (12.98, 'pop'), (13.2, 'pop'), (15.3, 'whoosh'), (15.6, 'rise'), (15.9, 'pop'), (17.41, 'ding'), (17.5, 'stamp'),
          (19.383, 'whoosh'), (20.0, 'zap'), (20.1, 'pop'), (21.0, 'tick'), (21.83, 'card'), (23.3, 'swish'), (23.72, 'clunk'), (23.75, 'crack'), (23.9, 'ding'),
          (25.554, 'whoosh'), (26.23, 'swish'), (26.4, 'pop'), (27.18, 'rise'), (27.3, 'pop'), (29.3, 'pop'), (30.77, 'shine'), (30.9, 'ding'), (31.0, 'stamp'),
          (32.608, 'whoosh'), (32.7, 'card'), (33.0, 'pop'), (34.75, 'stamp'), (36.86, 'pop'), (37.96, 'pop'), (38.1, 'ding_soft'),
          (39.066, 'whoosh'), (39.2, 'card'), (39.98, 'rise'), (41.3, 'ding'), (40.96, 'pop'), (41.35, 'stamp'),
          (44.11, 'whoosh'), (44.35, 'pop'), (44.5, 'swish'), (44.65, 'swish'), (44.8, 'swish'), (45.0, 'pop'), (45.15, 'pop'), (45.3, 'pop'),
          (46.1, 'whoosh'), (46.25, 'shine'), (46.6, 'pop'), (46.85, 'pop'), (47.1, 'pop'), (47.35, 'pop'), (47.0, 'pop'),
          (48.771, 'whoosh'), (48.91, 'boing'), (49.26, 'shine'), (49.51, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
