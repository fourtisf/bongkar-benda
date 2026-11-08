#!/usr/bin/env python3
"""Bongkar Benda #01: 'Lift, kok nggak jatuh?'
Lubang lift isometrik yang dibelah (cutaway): kabel putus + kabin jatuh + rem darurat mencengkeram rel (hook), 4 tali baja + standar EN 81 >= 12x,
beban penyeimbang + puli berputar, pengatur kecepatan -> rem jepit + percikan, kartu vintage Elisha Otis 1854 (tali dipotong, ratchet menahan),
peredam kejut pegas di dasar lubang, ajakan komentar, outro logo. Fakta: EN 81-20 (faktor keamanan tali >= 12 untuk > 2 tali),
penyeimbang ~ kabin + 40-50% muatan, governor + safety gear pada rel pemandu, buffer di pit, demonstrasi Otis Mei 1854 (Crystal Palace, New York).
python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4  (jalankan dari folder ini)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'engine'))
import skia
import bb
from bb import (clamp, lerp, prog, eo, ei, eio, bo, bump, col, mixc, P, lg, rg, layer, font, XB, B, M, MONO, bl,
               INK, INK2, MUTED, ORANGE, ORANGE_D, TEAL, YELLOW, RED, SKY, WHITE, STEEL, STEEL_D, CONCRETE,
               text_c, mono, card, chip, label, check, wrench, logo_mark)
from iso import Iso, tone, quad, box, shadow, wheel, rope, spring, sparks, ring_pts, poly

bb.TITLE = ('Lift,', 'kok nggak jatuh?'); bb.TITLE_OUT = 5.6
bb.GROUPS = [(0.0, 5.85, 'A'), (5.85, 12.96, 'B'), (12.96, 17.0, 'C'), (17.0, 22.76, 'D'), (22.76, 30.34, 'E'),
             (30.34, 33.72, 'F'), (33.72, 36.6, 'G'), (36.6, 42.0, 'J')]
bb.PHRASES = [(0.15, 'Kalau [kabel lift putus],'), (1.6, 'kamu bakal [jatuh]?'), (2.65, '[Tenang],'), (3.44, 'hampir [nggak mungkin].'), (4.6, 'Ini [alasannya].'),
              (5.85, '[Pertama],'), (6.52, 'lift digantung [beberapa tali baja] sekaligus.'), (8.76, 'Dan menurut [standar Eropa],'),
              (10.01, 'tiap tali minimal [12 kali] lebih kuat dari bebannya.'),
              (12.96, '[Kedua],'), (13.59, 'ada [beban penyeimbang] di sisi lain.'), (15.18, 'Jadi mesinnya [nggak perlu kerja berat].'),
              (17.0, '[Ketiga],'), (17.63, '[rem darurat].'), (18.61, 'Kalau lift meluncur [kelewat cepat],'), (19.95, 'rem ini langsung [mencengkeram rel],'),
              (21.61, 'dan lift [berhenti].'),
              (22.76, 'Idenya dari [Elisha Otis].'), (24.43, 'Tahun [1854],'), (26.1, 'dia menyuruh orang [memotong tali] liftnya sendiri.'),
              (28.28, 'Liftnya cuma [turun sedikit],'), (29.23, 'lalu [tertahan].'),
              (30.34, 'Kalau semuanya [gagal] pun,'), (31.55, 'di dasar lubang lift masih ada [peredam kejut].'),
              (33.72, 'Benda apa yang mau kamu [bongkar] berikutnya?'), (35.39, 'Tulis di [komentar]!'),
              (36.6, 'Follow [Bongkar Benda],'), (37.95, 'biar makin paham [cara kerja benda] di sekitarmu.')]

# ------------------------------------------------------------ dunia: lubang lift yang dibelah
WORLD = Iso(0, 0, 50)
SH_X, SH_Y, Z_PIT, Z_TOP = 4.2, 3.2, -1.4, 12.0
CAB = (0.9, 1.0, 2.4, 1.8, 2.5)                  # x, y, lebar, dalam, tinggi
ROPE_X = [1.86, 2.02, 2.18, 2.34]; ROPE_YC, ROPE_YW = 1.9, 0.4; SHEAVE_Z, SHEAVE_R = 12.95, 0.75
CABIN_C = '#E9EDF3'

def P3(x, y, z): return WORLD.p(x, y, z)
def cam(cv, wx, wy, zoom, sx=540, sy=760):
    cv.translate(sx, sy); cv.scale(zoom, zoom); cv.translate(-wx, -wy)
def focus(x, y, z): return P3(x, y, z)

def shaft(cv, a=1.0, doors=True):
    box(cv, WORLD, -0.35, -0.35, Z_PIT - 0.2, 0.35, SH_Y + 0.35, Z_TOP - Z_PIT + 0.2, CONCRETE, a, top=0.3, left=0.12, right=-0.06, hi=False)
    box(cv, WORLD, 0.0, -0.35, Z_PIT - 0.2, SH_X, 0.35, Z_TOP - Z_PIT + 0.2, CONCRETE, a, top=0.3, left=0.02, right=-0.18, hi=False)
    box(cv, WORLD, 0.0, 0.0, Z_PIT - 0.25, SH_X, SH_Y, 0.05, '#C2CBD8', a, top=0.0, hi=False)
    for zf in (0.0, 4.0, 8.0):
        for (p0, p1) in (((0, 0, zf - 0.08), (SH_X, 0, zf - 0.08)), ((0, 0, zf - 0.08), (0, SH_Y, zf - 0.08))):
            (x0, y0), (x1, y1) = P3(*p0), P3(*p1); cv.drawLine(x0, y0, x1, y1, P(col('#AEB9CA', a), stroke=3))
        if doors:
            quad(cv, WORLD, [(0, 1.15, zf), (0, 2.45, zf), (0, 2.45, zf + 2.35), (0, 1.15, zf + 2.35)], '#9AA7BB', a, edge='#6B7A93', ew=2)
            quad(cv, WORLD, [(0, 1.25, zf), (0, 1.79, zf), (0, 1.79, zf + 2.25), (0, 1.25, zf + 2.25)], '#C9D2DF', a)
            quad(cv, WORLD, [(0, 1.81, zf), (0, 2.35, zf), (0, 2.35, zf + 2.25), (0, 1.81, zf + 2.25)], '#C9D2DF', a)
            x, y = P3(0, 1.8, zf + 2.75); f = font(XB, 22); s = str(int(zf / 4) + 1); cv.drawString(s, x - f.measureText(s) / 2, bl(f, y), f, P(col(INK2, 0.8 * a)))

def rails(cv, a, side):
    if side == 'back':
        box(cv, WORLD, 0.62, 1.75, Z_PIT, 0.16, 0.3, Z_TOP - Z_PIT, STEEL, a, hi=False)
        for x in (1.25, 2.87): box(cv, WORLD, x, 0.3, Z_PIT, 0.08, 0.2, Z_TOP - Z_PIT, STEEL, 0.8 * a, hi=False)
    else: box(cv, WORLD, 3.42, 1.75, Z_PIT, 0.16, 0.3, Z_TOP - Z_PIT, STEEL, a, hi=False)

def counterweight(cv, z, a=1.0, glow=0.0):
    if glow > 0:
        x0, y0 = P3(1.4, 0.4, z + 2.1); x1, y1 = P3(2.8, 0.4, z - 0.1)
        cv.drawRect(skia.Rect(min(x0, x1) - 20, y0 - 20, max(x0, x1) + 20, y1 + 20), P(col(TEAL, 0.45 * glow * a), blur=26))
    box(cv, WORLD, 1.4, 0.2, z, 1.4, 0.4, 2.0, '#5E6A80', a)
    for k in range(1, 6):
        (x0, y0), (x1, y1) = P3(1.4, 0.6, z + k * 0.33), P3(2.8, 0.6, z + k * 0.33); cv.drawLine(x0, y0, x1, y1, P(col('#3B4558', a), stroke=2))
        (x2, y2) = P3(2.8, 0.2, z + k * 0.33); cv.drawLine(x1, y1, x2, y2, P(col('#2B3343', a), stroke=2))

def person(cv, x, y, z, a=1.0, scared=0.0, t=0.0):
    fx, fy = P3(x, y, z); h = 82; sh = 3 * math.sin(t * 50) * scared
    cv.drawOval(skia.Rect(fx - 22, fy - 7, fx + 22, fy + 7), P(col('#1B2A44', 0.25 * a), blur=4))
    for s_ in (-1, 1): cv.drawRoundRect(skia.Rect(fx + s_ * 9 - 5 + sh, fy - h * 0.45, fx + s_ * 9 + 5 + sh, fy), 4, 4, P(col(INK2, a)))
    cv.drawRoundRect(skia.Rect(fx - 17 + sh, fy - h * 0.86, fx + 17 + sh, fy - h * 0.4), 12, 12, P(col(ORANGE, a)))
    arm = 22 * scared
    for s_ in (-1, 1): cv.drawLine(fx + s_ * 15 + sh, fy - h * 0.78, fx + s_ * (22 + arm * 0.4) + sh, fy - h * (0.55 + 0.45 * scared), P(col(ORANGE_D, a), stroke=8))
    cv.drawCircle(fx + sh, fy - h * 0.98, 13, P(col('#F2C9A0', a))); cv.drawCircle(fx + sh, fy - h * 1.03, 13.5, P(col(INK, a)), )
    cv.drawCircle(fx + sh, fy - h * 0.96, 11.5, P(col('#F2C9A0', a)))
    for s_ in (-1, 1): cv.drawCircle(fx + s_ * 4.5 + sh, fy - h * 0.97, 2.2 + 1.3 * scared, P(col(INK, a)))
    if scared > 0.3: cv.drawOval(skia.Rect(fx - 3 + sh, fy - h * 0.93, fx + 3 + sh, fy - h * 0.88), P(col(INK, a)))

def cabin(cv, z, a=1.0, t=0.0, brake=0.0, scared=0.0, glow_gear=0.0, gear_squeeze=0.0):
    x, y, w, d, h = CAB
    shadow(cv, WORLD, x + 0.1, y + 0.1, z - 0.02, w, d, a, blur=10, k=0.18)
    gear(cv, 0.52, z, a, t, glow_gear, gear_squeeze)
    quad(cv, WORLD, [(x, y, z), (x + w, y, z), (x + w, y, z + h), (x, y, z + h)], '#F1F4F8', a, grad=((x, y, z + h), (x, y, z), '#FFF4E4', '#E3E9F1'))
    quad(cv, WORLD, [(x, y, z), (x, y + d, z), (x, y + d, z + h), (x, y, z + h)], '#DCE3EC', a)
    (hx0, hy0), (hx1, hy1) = P3(x + 0.2, y, z + 1.0), P3(x + w - 0.2, y, z + 1.0); cv.drawLine(hx0, hy0, hx1, hy1, P(col(STEEL, a), stroke=4))
    quad(cv, WORLD, [(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z)], '#D8C2A0', a)
    person(cv, x + 1.35, y + 1.0, z, a, scared, t)
    for pts in ([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)], [(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)]):
        pth = WORLD.path(pts); cv.drawPath(pth, P(col('#DDEBFA', 0.22 * a)))
        cv.save(); cv.clipPath(pth, skia.ClipOp.kIntersect, True)
        (sx0, sy0), (sx1, sy1) = P3(*pts[3]), P3(*pts[1])
        cv.drawPath(pth, P(shader=lg(sx0, sy0, sx1, sy1, [col(WHITE, 0.0), col(WHITE, 0.35 * a), col(WHITE, 0.0)], [0.3, 0.5, 0.7])))
        cv.restore()
        cv.drawPath(pth, P(col('#7D8AA0', a), stroke=4))
    for pts in ([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + 0.22), (x, y + d, z + 0.22)], [(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + 0.22), (x + w, y, z + 0.22)]):
        quad(cv, WORLD, pts, ORANGE, a, edge=ORANGE_D)
    (dx0, dy0), (dx1, dy1) = P3(x + w / 2, y + d, z + 0.22), P3(x + w / 2, y + d, z + h); cv.drawLine(dx0, dy0, dx1, dy1, P(col('#7D8AA0', a), stroke=2.5))
    box(cv, WORLD, x, y, z + h, w, d, 0.12, '#B9C3D2', a)
    box(cv, WORLD, 1.6, 1.75, z + h + 0.12, 1.0, 0.3, 0.22, STEEL_D, a)
    gear(cv, 3.3, z, a, t, glow_gear, gear_squeeze)

def gear(cv, gx, z, a, t, glow_gear, squeeze):
    """rem jepit (safety gear) yang menjepit rel pemandu"""
    gc = mixc(ORANGE, YELLOW, glow_gear * (0.5 + 0.5 * math.sin(t * 30)))
    if glow_gear > 0:
        cx, cy = P3(gx + 0.19, 1.9, z + 0.25); cv.drawCircle(cx, cy, 34, P(col(YELLOW, 0.6 * glow_gear * a), blur=18))
    sq = 0.06 * squeeze
    box(cv, WORLD, gx, 1.62, z + 0.04, 0.38, 0.13 + sq, 0.42, gc, a)
    box(cv, WORLD, gx, 2.05 - sq, z + 0.04, 0.38, 0.13 + sq, 0.42, gc, a)

def ropes_to(cv, z_cab_top, z_cw_top, a=1.0, glow=None, snap=None, t=0.0):
    """tali baja: kabin (y=1.9) & penyeimbang (y=0.4). snap=(z_putus, recoil, jatuh) memutus tali kabin"""
    for k, xr in enumerate(ROPE_X):
        g = glow[k] if glow else 0.0
        c = mixc('#3B4658', ORANGE, g); w = 4.0 + 3 * g
        if g > 0:
            (x0, y0), (x1, y1) = P3(xr, ROPE_YC, SHEAVE_Z), P3(xr, ROPE_YC, z_cab_top)
            cv.drawLine(x0, y0, x1, y1, P(col(ORANGE, 0.5 * g * a), stroke=16, blur=10))
        rope(cv, WORLD, (xr, ROPE_YW, SHEAVE_Z), (xr, ROPE_YW, z_cw_top), a, w=3.5)
        if snap is None: rope(cv, WORLD, (xr, ROPE_YC, SHEAVE_Z), (xr, ROPE_YC, z_cab_top), a, c=c, w=w)
        else:
            zb, rec, drop = snap; ztop = zb + rec
            rope(cv, WORLD, (xr, ROPE_YC, SHEAVE_Z), (xr, ROPE_YC, ztop), a, c=c, w=w)
            x0, y0 = P3(xr, ROPE_YC, ztop)
            for f_ in (-1, 0, 1): cv.drawLine(x0, y0, x0 + f_ * 6, y0 + 12, P(col('#3B4658', a), stroke=2))
            zl = min(zb - drop, z_cab_top + 3.0)
            if zl > z_cab_top + 0.1:
                pa, pb = P3(xr, ROPE_YC, z_cab_top), P3(xr, ROPE_YC, zl)
                pth = skia.Path(); pth.moveTo(*pa); wob = 18 * math.sin(t * 22 + k)
                pth.quadTo((pa[0] + pb[0]) / 2 + wob, (pa[1] + pb[1]) / 2, pb[0] + wob * 0.6, pb[1])
                cv.drawPath(pth, P(col('#3B4658', a), stroke=4))
                for f_ in (-1, 0, 1): cv.drawLine(pb[0] + wob * 0.6, pb[1], pb[0] + wob * 0.6 + f_ * 6, pb[1] - 12, P(col('#3B4658', a), stroke=2))

def machine(cv, ang, a=1.0, glow_motor=0.0):
    box(cv, WORLD, 1.4, 0.62, Z_TOP, 2.4, 1.1, 0.22, '#7A879C', a)
    for yy in (0.5, 1.95): box(cv, WORLD, -0.2, yy - 0.12, Z_TOP - 0.25, SH_X + 0.4, 0.24, 0.25, '#6C7A90', a, hi=False)
    wheel(cv, WORLD, 1.75, 2.45, 1.15, SHEAVE_Z, SHEAVE_R, '#9AA6BA', a, ang=ang, spokes=6, groove=4)
    if glow_motor > 0:
        x, y = P3(3.1, 1.15, 12.8); cv.drawCircle(x, y, 70, P(col(TEAL, 0.5 * glow_motor * a), blur=26))
    box(cv, WORLD, 2.6, 0.78, Z_TOP + 0.22, 1.0, 0.75, 0.8, '#3E6FB5', a)
    wheel(cv, WORLD, 3.6, 3.75, 1.15, 12.62, 0.3, '#2F5A96', a, ang=ang * 2.5, spokes=4)
    for k in range(4):
        (x0, y0), (x1, y1) = P3(2.7 + k * 0.22, 1.53, Z_TOP + 0.35), P3(2.7 + k * 0.22, 1.53, Z_TOP + 0.9); cv.drawLine(x0, y0, x1, y1, P(col('#2A4E86', a), stroke=3))

def buffers(cv, comp=0.0, a=1.0):
    for (x, y, h, r, main_) in ((2.1, 0.4, 0.7, 0.18, False), (1.3, 2.45, 1.0, 0.22, True), (2.9, 2.45, 1.0, 0.22, True)):
        box(cv, WORLD, x - r - 0.1, y - r - 0.1, Z_PIT - 0.2, 2 * r + 0.2, 2 * r + 0.2, 0.2, '#6B7A93', a)
        top = Z_PIT + h * (1 - 0.3 * comp if main_ else 1)
        spring(cv, WORLD, x, y, Z_PIT, top, r, a, c='#E0600A' if main_ else '#6B7A93', turns=5)
        box(cv, WORLD, x - r - 0.05, y - r - 0.05, top, 2 * r + 0.1, 2 * r + 0.1, 0.08, '#4A5568', a)

def lift_scene(cv, t, cab_z, cw_z=7.0, ang=0.0, a=1.0, glow=None, snap=None, brake=0.0, scared=0.0, glow_gear=0.0, squeeze=0.0,
               buf=0.0, cw_glow=0.0, motor_glow=0.0, streak=0.0):
    shaft(cv, a)
    buffers(cv, buf, a)
    rails(cv, a, 'back')
    counterweight(cv, cw_z, a, cw_glow)
    if streak > 0:
        for k, xx in enumerate((0.7, 1.4, 2.6, 3.4)):
            (x0, y0), (x1, y1) = P3(xx, 2.9, cab_z + 2.9), P3(xx, 2.9, cab_z + 2.9 + 1.4 + 0.6 * (k % 2))
            cv.drawLine(x0, y0, x1, y1, P(col(INK, 0.35 * streak * a), stroke=4))
    cabin(cv, cab_z, a, t, brake, scared, glow_gear, squeeze)
    ropes_to(cv, cab_z + CAB[4] + 0.34, cw_z + 2.0, a, glow, snap, t)
    rails(cv, a, 'front')
    machine(cv, ang, a, motor_glow)

# ------------------------------------------------------------ A: HOOK — kabel putus, kabin jatuh, rem darurat (0 - 5.85)
T_SNAP, T_BRAKE, DB, Z0, G = 0.25, 1.75, 0.32, 7.6, 3.4
def fall_z(t):
    if t < T_SNAP + 0.1: return Z0
    if t < T_BRAKE: u = t - T_SNAP - 0.1; return Z0 - 0.5 * G * u * u
    vb = G * (T_BRAKE - T_SNAP - 0.1); zb = Z0 - 0.5 * G * (T_BRAKE - T_SNAP - 0.1) ** 2
    u = min(t - T_BRAKE, DB); return zb - (vb * u - 0.5 * vb / DB * u * u)
ZA, SYA = 2.5, 960
def gA(cv, t):
    z = fall_z(t); stop = prog(t, T_BRAKE, T_BRAKE + DB); falling = T_SNAP + 0.1 < t < T_BRAKE + DB
    jolt = 14 * math.sin(t * 70) * (1 - prog(t, T_BRAKE, T_BRAKE + 0.5)) if t > T_BRAKE else 0.0
    shk = 6 * math.sin(t * 55) * (1 - prog(t, T_SNAP, T_SNAP + 0.4)) if t > T_SNAP else 0.0
    fx, fy = focus(2.1, 1.9, lerp(Z0 + 1.6, z + 1.9, 0.75))
    zin = lerp(1.1, 1.0, eo(prog(t, 0.0, 0.8)))
    cv.save(); cam(cv, fx, fy, ZA * zin, 540, SYA + jolt + shk)
    snap = None
    if t >= T_SNAP: snap = (Z0 + CAB[4] + 2.6, 2.4 * eo(prog(t, T_SNAP, T_SNAP + 0.5)), Z0 - z)
    lift_scene(cv, t, z, cw_z=9.4, a=1.0, snap=snap, scared=prog(t, T_SNAP, T_SNAP + 0.2) * (1 - prog(t, 2.6, 3.0)), glow_gear=prog(t, T_BRAKE - 0.05, T_BRAKE + 0.1) * (1 - 0.6 * prog(t, 3.0, 4.0)),
               squeeze=prog(t, T_BRAKE - 0.05, T_BRAKE + 0.1), streak=clamp((Z0 - z) / 2) * (1 - stop) if falling else 0.0)
    if t > T_BRAKE - 0.05:
        sa = 1 - prog(t, T_BRAKE + 0.5, T_BRAKE + 1.3)
        x, y = P3(3.49, 1.9, z + 0.2); sparks(cv, x, y, t, 34, sa, n=14, spread=70)
    gx, gy = P3(3.49, 1.9, z + 0.25)
    cv.restore()
    ta = 1 - eio(prog(t, bb.TITLE_OUT - 0.4, bb.TITLE_OUT))
    if ta > 0: cv.drawRect(skia.Rect(0, 0, 1080, 560), P(shader=lg(0, 380, 0, 580, [col(bb.BG0, ta), col(bb.BG0, 0)])))
    fl = prog(t, T_SNAP, T_SNAP + 0.35)
    if 0 < fl < 1: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.28 * (1 - fl))))
    if falling: cv.drawRect(skia.Rect(0, 0, 1080, 1920), P(col(RED, 0.07 * (1 - stop))))
    sx, sy = 540 + (gx - fx) * ZA, SYA + (gy - fy) * ZA
    if t > T_SNAP + 0.1 and t < 2.65: chip(cv, 'KABEL PUTUS!', 540, 560, eo(prog(t, T_SNAP + 0.1, T_SNAP + 0.3)) * (1 - prog(t, 2.4, 2.65)), size=30, bg=RED)
    la = eo(prog(t, 2.65, 3.0))
    if la > 0:
        label(cv, 'REM DARURAT', sx, sy, 820, 700, la, sub='mencengkeram rel')
        check(cv, 960, 630, 26, prog(t, 2.75, 3.2))
    for k, (num, txt) in enumerate((('1', 'TALI BAJA'), ('2', 'PENYEIMBANG'), ('3', 'REM DARURAT'))):
        q = prog(t, 4.6 + 0.15 * k, 4.9 + 0.15 * k)
        if q > 0:
            x = 200 + k * 340; s_ = lerp(0.6, 1, bo(q)); aa = clamp(q * 3)
            cv.save(); cv.translate(x, 1335); cv.scale(s_, s_); cv.translate(-x, -1335)
            r = skia.Rect(x - 155, 1305, x + 155, 1365); card(cv, r, aa, rad=30, lift=8)
            cv.drawCircle(x - 120, 1335, 21, P(col(ORANGE, aa))); text_c(cv, num, x - 120, 1335, 24, WHITE, aa)
            text_c(cv, txt, x + 14, 1335, 24, INK, aa)
            cv.restore()

# ------------------------------------------------------------ B: beberapa tali baja; standar Eropa: >= 12x lebih kuat (5.85 - 12.96)
def gB(cv, t):
    a0 = eo(prog(t, 5.85, 6.2))
    zoom = lerp(2.7, 3.2, eio(prog(t, 5.85, 12.9)))
    fx, fy = focus(2.1, 1.2, 11.6)
    glow = [eo(prog(t, 6.6 + 0.3 * k, 6.9 + 0.3 * k)) * (0.6 + 0.4 * math.sin(t * 6 + k)) for k in range(4)]
    cv.save(); cam(cv, fx, fy, zoom, 540, 640)
    lift_scene(cv, t, 8.3, cw_z=3.0, ang=t * 0.6, a=a0, glow=glow)
    pts = [P3(xr, ROPE_YC, 11.0 - 0.0 * k) for k, xr in enumerate(ROPE_X)]
    cv.restore()
    for k, (px, py) in enumerate(pts):
        q = prog(t, 6.6 + 0.3 * k, 6.9 + 0.3 * k)
        if q > 0:
            sx, sy = 540 + (px - fx) * zoom, 640 + (py - fy) * zoom; s_ = lerp(0.5, 1, bo(q))
            bx, by = sx + (k - 1.5) * 70, sy - 170 - 20 * (k % 2)
            cv.drawLine(sx, sy, bx, by + 26 * s_, P(col(INK, 0.5 * a0 * clamp(q * 3)), stroke=2.5))
            cv.drawCircle(bx, by, 26 * s_, P(col(ORANGE, a0 * clamp(q * 3)))); text_c(cv, str(k + 1), bx, by, 28 * s_, WHITE, a0 * clamp(q * 3))
    if t > 7.9: chip(cv, '4 TALI BAJA SEKALIGUS', 540, 330, a0 * eo(prog(t, 7.9, 8.2)) * (1 - prog(t, 8.6, 8.9)), size=28, bg=INK)
    ca = eo(prog(t, 8.76, 9.2))
    if ca > 0:
        r = skia.Rect(90, 1010 + 30 * (1 - ca), 990, 1330 + 30 * (1 - ca)); card(cv, r, a0 * ca, rad=30)
        mono(cv, 'STANDAR EROPA · EN 81', r.left() + 44, r.top() + 46, 22, MUTED, a0 * ca, sp=3, align=0)
        lens_x, lens_y = r.left() + 130, r.top() + 180
        cv.drawCircle(lens_x, lens_y, 92, P(col('#E9EEF5', a0 * ca))); cv.drawCircle(lens_x, lens_y, 92, P(col(INK, a0 * ca), stroke=5))
        for k in range(7):
            ang = k * math.tau / 6; cx_ = lens_x + (0 if k == 6 else 50 * math.cos(ang + t * 0.3)); cy_ = lens_y + (0 if k == 6 else 50 * math.sin(ang + t * 0.3))
            cv.drawCircle(cx_, cy_, 24, P(shader=rg(cx_ - 8, cy_ - 8, 34, [col('#D7DEE8', a0 * ca), col('#7D8AA0', a0 * ca)])))
            for j in range(6):
                aj = j * math.tau / 6 + t; cv.drawCircle(cx_ + 13 * math.cos(aj), cy_ + 13 * math.sin(aj), 6, P(col('#5C6B84', 0.6 * a0 * ca), stroke=1.5))
        mono(cv, 'PENAMPANG TALI', lens_x, r.bottom() - 30, 16, MUTED, a0 * ca, sp=2)
        x0 = r.left() + 270; bw = r.right() - 50 - x0
        text_c(cv, 'BEBAN', x0 + 60, r.top() + 110, 24, MUTED, a0 * ca, f=B)
        cv.drawRoundRect(skia.Rect(x0 + 130, r.top() + 94, x0 + 130 + bw / 13 * 1.2, r.top() + 126), 10, 10, P(col(INK2, a0 * ca)))
        kk = eio(prog(t, 10.1, 11.4))
        text_c(cv, 'KEKUATAN', x0 + 72, r.top() + 176, 24, MUTED, a0 * ca, f=B)
        cv.drawRoundRect(skia.Rect(x0 + 150, r.top() + 158, x0 + 150 + (bw - 150) * kk, r.top() + 194), 12, 12, P(shader=lg(x0 + 150, 0, x0 + bw, 0, [col('#FFB066', a0 * ca), col(ORANGE, a0 * ca)])))
        v = 1 + 11 * kk
        f = font(XB, 104); s = f'≥ {int(round(v))}×'; w = f.measureText(s)
        cv.drawString(s, r.right() - 60 - w, bl(f, r.top() + 262) + 4, f, P(col(ORANGE_D, 0.3 * a0 * ca), blur=6))
        cv.drawString(s, r.right() - 60 - w, bl(f, r.top() + 262), f, P(col(ORANGE if kk > 0.98 else INK, a0 * ca)))
        text_c(cv, 'tiap tali', x0 + 80, r.top() + 262, 26, INK2, a0 * ca * prog(t, 10.6, 11.0), f=B)

# ------------------------------------------------------------ C: beban penyeimbang di sisi lain -> mesin nggak kerja berat (12.96 - 17.0)
def gC(cv, t):
    a0 = eo(prog(t, 12.96, 13.3)); u = eio(prog(t, 13.3, 16.6))
    cz = lerp(1.0, 6.2, u); wz = lerp(8.6, 3.4, u)
    fx, fy = focus(2.1, 1.3, 6.0)
    cv.save(); cam(cv, fx, fy, 1.45, 470, 860)
    lift_scene(cv, t, cz, cw_z=wz, ang=-u * 7.0, a=a0, cw_glow=eo(prog(t, 13.59, 14.0)), motor_glow=eo(prog(t, 15.18, 15.6)))
    cw = P3(2.1, 0.4, wz + 1.0); mo = P3(3.1, 1.15, 12.9)
    cv.restore()
    sc = lambda p: (470 + (p[0] - fx) * 1.45, 860 + (p[1] - fy) * 1.45)
    l1 = eo(prog(t, 13.65, 14.1))
    if l1 > 0: x, y = sc(cw); label(cv, 'BEBAN PENYEIMBANG', x, y, 800, 860, a0 * l1, dot=TEAL, size=26, sub='≈ kabin + 40–50% muatan')
    l2 = eo(prog(t, 15.2, 15.6))
    if l2 > 0: x, y = sc(mo); label(cv, 'MESIN', x, y, 850, 330, a0 * l2, dot=TEAL, size=26, sub='kerja lebih ringan')
    for k, (ax, lab_) in enumerate(((240, 'KABIN NAIK'), (700, 'PENYEIMBANG TURUN'))):
        aa = a0 * eo(prog(t, 13.4, 13.8)) * (1 - prog(t, 16.6, 16.9))
        if aa > 0:
            yb = 1345; d = -1 if k == 0 else 1; off = 10 * math.sin(t * 6)
            pth = skia.Path(); pth.moveTo(ax - 18, yb - d * 10 + off * d); pth.lineTo(ax, yb - d * 34 + off * d); pth.lineTo(ax + 18, yb - d * 10 + off * d)
            cv.drawPath(pth, P(col(TEAL if k else ORANGE, aa), stroke=7)); text_c(cv, lab_, ax + (130 if k == 0 else 150), yb - 20, 22, INK2, aa, f=B)

# ------------------------------------------------------------ D: rem darurat: kelewat cepat -> mencengkeram rel -> berhenti (17.0 - 22.76)
def speed_dial(cv, cx, cy, r, v, a, t, alarm=0.0):
    card(cv, skia.Rect(cx - r - 30, cy - r - 30, cx + r + 30, cy + r * 0.75 + 30), a, rad=30)
    p = skia.Path(); p.addArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), 150, 240)
    cv.drawPath(p, P(col('#E3E9F1', a), stroke=26))
    p2 = skia.Path(); p2.addArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), 150 + 240 * 0.72, 240 * 0.28)
    cv.drawPath(p2, P(col(RED, 0.85 * a), stroke=26))
    ang = math.radians(150 + 240 * clamp(v)); nx, ny = cx + math.cos(ang) * r * 0.85, cy + math.sin(ang) * r * 0.85
    cv.drawLine(cx, cy, nx, ny, P(col(INK, a), stroke=8)); cv.drawCircle(cx, cy, 14, P(col(INK, a)))
    mono(cv, 'KECEPATAN', cx, cy + r * 0.45, 18, MUTED, a, sp=3)
    if alarm > 0: text_c(cv, 'KELEWAT CEPAT!', cx, cy + r * 0.78, 26, RED, a * alarm * (0.6 + 0.4 * math.sin(t * 20)))
def governor_card(cv, cx, cy, s, a, t, spin, trip):
    card(cv, skia.Rect(cx - s, cy - s * 0.95, cx + s, cy + s * 0.95), a, rad=28)
    mono(cv, 'PENGATUR KECEPATAN', cx, cy - s * 0.72, 16, MUTED, a, sp=2)
    r = s * 0.48; cy2 = cy + s * 0.1
    cv.drawCircle(cx, cy2, r, P(col('#9AA6BA', a))); cv.drawCircle(cx, cy2, r, P(col('#4A5568', a), stroke=4))
    for k in range(2):
        ang = spin + k * math.pi; ext = r * (0.35 + 0.4 * trip)
        x, y = cx + math.cos(ang) * ext, cy2 + math.sin(ang) * ext
        cv.drawLine(cx, cy2, x, y, P(col(INK2, a), stroke=6)); cv.drawCircle(x, y, 14, P(col(ORANGE if trip > 0.5 else '#5C6B84', a)))
    cv.drawCircle(cx, cy2, 10, P(col(INK, a)))
def gD(cv, t):
    a0 = eo(prog(t, 17.0, 17.3))
    clamp_t = 19.95; stop_t = 21.0
    if t < clamp_t: speed = lerp(0.25, 1.0, eio(prog(t, 18.0, 19.6)))
    else: speed = lerp(1.0, 0.0, eio(prog(t, clamp_t, stop_t)))
    zt = 9.0 - 1.2 * (t - 17.0) - 2.2 * eio(prog(t, 18.0, 19.95)) * 1.0 - 0.8 * eio(prog(t, 19.95, 21.0))
    zt = max(zt, 2.0)
    zoom = lerp(2.25, 3.6, eio(prog(t, 19.7, 20.4)))
    fx, fy = focus(lerp(2.1, 3.45, eio(prog(t, 19.7, 20.4))), 1.9, zt + lerp(1.3, 0.25, eio(prog(t, 19.7, 20.4))))
    jolt = 10 * math.sin(t * 60) * bump(prog(t, clamp_t, clamp_t + 0.5))
    cv.save(); cam(cv, fx, fy, zoom, 540, 900 + jolt)
    eng = prog(t, clamp_t - 0.05, clamp_t + 0.15)
    lift_scene(cv, t, zt, cw_z=10.0 - (9.0 - zt) * 0.5, ang=-(9.0 - zt) * 1.3, a=a0, glow_gear=eng * (1 - 0.5 * prog(t, 21.6, 22.4)), squeeze=eng,
               streak=clamp(speed - 0.5) * 2 * (1 - eng))
    if eng > 0:
        x, y = P3(3.49, 1.9, zt + 0.2); sparks(cv, x, y, t, 24, (1 - prog(t, 20.8, 21.4)) * a0, n=18, spread=70)
    gpt = P3(3.49, 1.9, zt + 0.25)
    cv.restore()
    da = a0 * eo(prog(t, 17.2, 17.6)) * (1 - eio(prog(t, 19.6, 19.95)))
    if da > 0: speed_dial(cv, 800, 440, 120, speed, da, t, alarm=prog(t, 18.61, 18.8))
    ga = a0 * eo(prog(t, 18.9, 19.2)) * (1 - eio(prog(t, 19.7, 19.95)))
    if ga > 0: governor_card(cv, 250, 460, 150, ga, t, spin=t * (6 + 20 * speed), trip=prog(t, 19.2, 19.5))
    la = eo(prog(t, 20.1, 20.5))
    if la > 0:
        sx, sy = 540 + (gpt[0] - fx) * zoom, 900 + (gpt[1] - fy) * zoom
        label(cv, 'MENCENGKERAM REL', sx, sy, 560, 400, a0 * la, sub='rem jepit (safety gear)')
    ba = eo(prog(t, 21.61, 21.9))
    if ba > 0: chip(cv, 'BERHENTI', 540, 1335, a0 * ba, size=30, bg=TEAL)

# ------------------------------------------------------------ E: Elisha Otis 1854: tali dipotong, lift cuma turun sedikit lalu tertahan (22.76 - 30.34)
SEPIA, SEPIA_D, SEPIA_INK = '#F3E6CC', '#E2CFA8', '#6B4A2B'
def otis_card(cv, t, a):
    r = skia.Rect(110, 250, 970, 1150)
    card(cv, r, a, rad=24, fill=SEPIA, edge=SEPIA_D, shadow=0.3, lift=18)
    cv.drawRoundRect(r.makeInset(24, 24), 14, 14, P(col(SEPIA_INK, 0.45 * a), stroke=3))
    mono(cv, 'NEW YORK · 1854', 540, r.top() + 72, 26, SEPIA_INK, a, sp=6)
    ink = lambda al=1.0: P(col(SEPIA_INK, al * a))
    top_y, bot_y = r.top() + 140, r.bottom() - 120
    for x in (330, 750):                                                  # dua tiang kayu + gigi ratchet
        cv.drawRect(skia.Rect(x - 18, top_y, x + 18, bot_y), P(col('#C9A577', a))); cv.drawRect(skia.Rect(x - 18, top_y, x + 18, bot_y), ink(0.8)); cv.drawRect(skia.Rect(x - 18, top_y, x + 18, bot_y), P(col(SEPIA_INK, a), stroke=3))
        sd = 1 if x < 540 else -1; p = skia.Path(); p.moveTo(x + sd * 18, top_y + 20)
        for k in range(22): yy = top_y + 20 + k * 30; p.lineTo(x + sd * 34, yy + 10); p.lineTo(x + sd * 18, yy + 30)
        cv.drawPath(p, P(col(SEPIA_INK, a), stroke=3))
    cv.drawRect(skia.Rect(290, top_y - 24, 790, top_y + 8), P(col('#B58A57', a))); cv.drawRect(skia.Rect(290, top_y - 24, 790, top_y + 8), P(col(SEPIA_INK, a), stroke=3))
    cut = prog(t, 26.25, 26.45); drop = 34 * eio(prog(t, 26.45, 27.0))
    py = 760 + drop; apex = py - 230; yc = top_y + 70; rec = 46 * eo(cut)
    if cut <= 0: cv.drawLine(540, top_y + 8, 540, apex, P(col(SEPIA_INK, a), stroke=6))
    else:
        wob = 16 * math.sin(t * 24) * (1 - prog(t, 26.5, 27.6))
        cv.drawLine(540, top_y + 8, 540 + wob * 0.5, yc - rec, P(col(SEPIA_INK, a), stroke=6))
        cv.drawLine(540, apex, 540 - wob, yc + 14 + drop, P(col(SEPIA_INK, a), stroke=6))
        for e_, d_ in ((yc - rec, 1), (yc + 14 + drop, -1)):
            for f_ in (-1, 0, 1): cv.drawLine(540, e_, 540 + f_ * 7, e_ + d_ * 12, P(col(SEPIA_INK, a), stroke=2.5))
    ax_a = prog(t, 25.85, 26.15) * (1 - prog(t, 26.9, 27.2))
    if ax_a > 0:                                                          # kapak yang diayun dari kiri ke tali
        sw = lerp(-55, 0, eio(prog(t, 25.95, 26.28)))
        cv.save(); cv.translate(390, yc + 110); cv.rotate(sw)
        hx_, hy_ = 520 - 390, yc - (yc + 110)
        cv.drawLine(0, 0, hx_ * 0.92, hy_ * 0.92, P(col('#8B5A2B', ax_a * a), stroke=12))
        cv.save(); cv.translate(hx_, hy_); cv.rotate(math.degrees(math.atan2(hy_, hx_)) + 90)
        bl_ = skia.Path(); bl_.moveTo(-8, -10); bl_.lineTo(-8, 34); bl_.lineTo(30, 46); bl_.quadTo(44, 12, 30, -24); bl_.close()
        cv.drawPath(bl_, P(col('#8E9AAF', ax_a * a))); cv.drawPath(bl_, P(col(SEPIA_INK, ax_a * a), stroke=3)); cv.restore(); cv.restore()
    if 0 < cut < 1:
        for k in range(6): ang = k * math.tau / 6; cv.drawLine(540 + 10 * math.cos(ang), yc + 7 + 10 * math.sin(ang), 540 + 42 * math.cos(ang), yc + 7 + 42 * math.sin(ang), P(col(ORANGE_D, a * (1 - cut)), stroke=3))
    cv.drawLine(540, py - 230, 400, py - 30, P(col(SEPIA_INK, a), stroke=4)); cv.drawLine(540, py - 230, 680, py - 30, P(col(SEPIA_INK, a), stroke=4))
    cv.drawRect(skia.Rect(352, py - 30, 728, py + 4), P(col('#B58A57', a))); cv.drawRect(skia.Rect(352, py - 30, 728, py + 4), P(col(SEPIA_INK, a), stroke=3))
    for x in (380, 700): cv.drawLine(x, py - 30, x, py - 110, P(col(SEPIA_INK, a), stroke=4))
    cv.drawLine(380, py - 110, 700, py - 110, P(col(SEPIA_INK, a), stroke=4))
    held = prog(t, 26.9, 27.05)
    for sd, x in ((-1, 352), (1, 728)):                                   # pawl penahan
        ang = lerp(0, 35, held) * (-sd)
        cv.save(); cv.translate(x, py - 12); cv.rotate(ang); cv.drawRect(skia.Rect(-4 if sd > 0 else -26, -6, 26 if sd > 0 else 4, 6), P(col(SEPIA_INK, a))); cv.restore()
    hx = 590; hy = py - 30                                                # Otis: topi tinggi + mantel, tangan terangkat
    cv.drawRoundRect(skia.Rect(hx - 26, hy - 150, hx + 26, hy - 40), 14, 14, P(col('#3E2E22', a)))
    cv.drawRect(skia.Rect(hx - 20, hy - 42, hx - 6, hy), P(col('#3E2E22', a))); cv.drawRect(skia.Rect(hx + 6, hy - 42, hx + 20, hy), P(col('#3E2E22', a)))
    cv.drawLine(hx + 22, hy - 138, hx + 64, hy - 200 + 6 * math.sin(t * 3), P(col('#3E2E22', a), stroke=12))
    cv.drawCircle(hx, hy - 172, 22, P(col('#E8C9A0', a))); cv.drawCircle(hx, hy - 172, 22, P(col(SEPIA_INK, a), stroke=2.5))
    cv.drawRect(skia.Rect(hx - 20, hy - 238, hx + 20, hy - 188), P(col('#2A1F17', a))); cv.drawRect(skia.Rect(hx - 32, hy - 194, hx + 32, hy - 186), P(col('#2A1F17', a)))
    cv.drawRect(skia.Rect(420, hy - 70, 500, hy), P(col('#C9A577', a))); cv.drawRect(skia.Rect(420, hy - 70, 500, hy), P(col(SEPIA_INK, a), stroke=3))
    cv.drawLine(420, hy - 70, 500, hy, P(col(SEPIA_INK, 0.6 * a), stroke=2)); cv.drawLine(500, hy - 70, 420, hy, P(col(SEPIA_INK, 0.6 * a), stroke=2))
    for k in range(9):                                                    # penonton (siluet)
        x = 180 + k * 90; hh = 46 + 10 * ((k * 37) % 3)
        cv.drawCircle(x, bot_y + 40 - hh, 18, P(col(SEPIA_INK, 0.55 * a))); cv.drawRoundRect(skia.Rect(x - 28, bot_y + 52 - hh, x + 28, bot_y + 70), 18, 18, P(col(SEPIA_INK, 0.55 * a)))
    if held > 0.5 and t < 27.6:
        for sd, x in ((-1, 320), (1, 760)): text_c(cv, 'KLIK!', x + sd * 30, py - 60, 26, ORANGE_D, a * (1 - prog(t, 27.2, 27.6)))
def gE(cv, t):
    a0 = eo(prog(t, 22.76, 23.2))
    cv.save(); cv.translate(540, 770); cv.scale(1.14, 1.14); cv.translate(-540, -700)
    otis_card(cv, t, a0)
    cv.restore()
    na = eo(prog(t, 23.0, 23.4))
    if na > 0: label(cv, 'ELISHA OTIS', 620, 656, 850, 500, a0 * na, dot=ORANGE, size=26, sub='penemu rem lift pengaman')
    if t > 28.28:
        aa = eo(prog(t, 28.28, 28.6)); chip(cv, 'CUMA TURUN SEDIKIT', 540, 1355, a0 * aa * (1 - prog(t, 29.1, 29.3)), size=26, bg=INK)
    ta = eo(prog(t, 29.23, 29.5))
    if ta > 0: chip(cv, 'TERTAHAN!', 540, 1355, a0 * ta, size=30, bg=TEAL)

# ------------------------------------------------------------ F: peredam kejut di dasar lubang lift (30.34 - 33.72)
def gF(cv, t):
    a0 = eo(prog(t, 30.34, 30.7))
    u = eio(prog(t, 30.5, 31.8)); z = lerp(1.8, -0.4, u)
    comp = prog(t, 31.75, 32.2) * (1 - 0.3 * bump(prog(t, 32.2, 32.8)))
    if comp > 0: z = -0.4 - 0.3 * comp
    fx, fy = focus(2.1, 1.9, 0.0)
    cv.save(); cam(cv, fx, fy, 2.35, 540, 830)
    lift_scene(cv, t, z, cw_z=9.5, ang=0, a=a0, buf=comp)
    bp = P3(2.9, 2.45, -1.0)
    cv.restore()
    la = eo(prog(t, 31.6, 32.0))
    if la > 0: label(cv, 'PEREDAM KEJUT', 540 + (bp[0] - fx) * 2.35, 830 + (bp[1] - fy) * 2.35, 800, 440, a0 * la, sub='pegas / oli di dasar lubang')
    if t > 30.5: chip(cv, 'LAPISAN TERAKHIR', 540, 330, a0 * eo(prog(t, 30.5, 30.8)), size=26, bg=INK)

# ------------------------------------------------------------ G: bongkar apa lagi? tulis di komentar (33.72 - 36.6)
CMTS = [('eskalator!', 280, 760, 34.2, ORANGE), ('kereta cepat dong', 750, 900, 34.45, TEAL), ('kapal selam pls', 310, 1040, 34.7, SKY), ('bendungan!!', 760, 1180, 34.95, '#8B5CF6')]
def gG(cv, t):
    a0 = eo(prog(t, 33.72, 34.0))
    logo_mark(cv, 540, 430, 80 * lerp(0.6, 1, bo(prog(t, 33.72, 34.1))), a0, t)
    text_c(cv, 'BONGKAR APA LAGI?', 540, 590, 64, INK, a0 * eo(prog(t, 33.8, 34.1)))
    for txt, x, y, t0, c in CMTS:
        q = prog(t, t0, t0 + 0.3)
        if q <= 0: continue
        aa = a0 * clamp(q * 3); s_ = lerp(0.6, 1, bo(q)); f = font(XB, 32); w = f.measureText(txt) + 120
        cv.save(); cv.translate(x, y); cv.scale(s_, s_); cv.rotate(-3 if x < 540 else 3)
        r = skia.Rect(-w / 2, -42, w / 2, 42); card(cv, r, aa, rad=42, lift=10)
        cv.drawCircle(r.left() + 42, 0, 24, P(col(c, aa))); cv.drawCircle(r.left() + 42, -6, 9, P(col(WHITE, aa))); cv.drawOval(skia.Rect(r.left() + 28, 4, r.left() + 56, 22), P(col(WHITE, aa)))
        cv.drawString(txt, r.left() + 80, bl(f, 0), f, P(col(INK, aa)))
        cv.restore()
    ca = eo(prog(t, 35.39, 35.7))
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
    ev = [(0.0, 'whoosh'), (0.25, 'crack'), (0.27, 'chop'), (0.4, 'zap2'), (0.45, 'buzzer'), (1.72, 'stamp'), (1.75, 'fizz'), (2.65, 'ding'), (2.75, 'shine'),
          (4.6, 'pop'), (4.75, 'pop'), (4.9, 'pop'),
          (5.85, 'whoosh'), (6.6, 'tick'), (6.9, 'tick'), (7.2, 'tick'), (7.5, 'tick'), (7.9, 'pop'), (8.76, 'card'), (10.1, 'rise'), (11.4, 'ding'),
          (12.96, 'whoosh'), (13.3, 'swish'), (13.65, 'pop'), (15.2, 'pop'), (15.3, 'ding_soft'),
          (17.0, 'whoosh'), (17.2, 'pop'), (18.0, 'rise'), (18.61, 'beep'), (18.85, 'beep'), (18.9, 'pop'), (19.2, 'zap'), (19.95, 'clunk'), (19.97, 'stamp'), (20.0, 'fizz'),
          (20.1, 'pop'), (21.61, 'ding'),
          (22.76, 'whoosh'), (22.8, 'card'), (23.0, 'pop'), (26.25, 'chop'), (26.3, 'crack'), (26.95, 'clunk'), (27.0, 'tick'), (28.28, 'pop'), (29.23, 'ding'),
          (30.34, 'whoosh'), (30.5, 'pop'), (31.75, 'boing'), (31.8, 'clunk'), (31.6, 'pop'),
          (33.72, 'whoosh'), (33.8, 'shine'), (34.2, 'pop'), (34.45, 'pop'), (34.7, 'pop'), (34.95, 'pop'), (35.39, 'pop'),
          (36.6, 'whoosh'), (36.75, 'boing'), (37.1, 'shine'), (37.35, 'pop')]
    return sorted(ev)

if __name__ == '__main__': bb.main()
