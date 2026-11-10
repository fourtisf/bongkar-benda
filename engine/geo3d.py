"""Alat 3D kecil untuk Bongkar Benda: vektor, muka bernormal dengan backface culling, balok & silinder & roda gigi berorientasi bebas.
Proyeksi memakai ISO (Iso dari iso.py); episode mengisinya: geo3d.ISO = WORLD. Sumbu dunia: x kanan-bawah, y kiri-bawah, z atas;
penonton melihat dari arah (1, 1, 1): muka bernormal +x, +y, +z terlihat. (Dipakai mulai EP07; EP06 memakai salinan lokal.)"""
import math
import skia
from bb import P, col, WHITE, ORANGE
from iso import tone
from iso import poly

ISO = None
VIEW = (1.0, 1.0, 1.0)
def p3(p): return ISO.p(*p)
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def nrm(a): l = math.sqrt(dot(a, a)) or 1.0; return (a[0] / l, a[1] / l, a[2] / l)
def crs(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
LIGHT = nrm((-0.4, 0.3, 1.0))
def shade(c, n, k0=-0.12, k1=0.42): return tone(c, k0 + k1 * dot(n, LIGHT))
def visible(n): return dot(n, VIEW) > 1e-6
def face(cv, pts, n, c, a, glow=0.0, edge=None, flat=False):
    if a <= 0 or not visible(n): return None
    pth = poly([p3(p) for p in pts]); cv.drawPath(pth, P(col(c if flat else shade(c, n), a)))
    if edge: cv.drawPath(pth, P(col(edge, 0.6 * a), stroke=1.2))
    if glow > 0: cv.drawPath(pth, P(col(ORANGE, 0.75 * glow * a)))
    return pth
def obox(cv, c, u, v, w, hu, hv, hw, col_, a, glow=0.0, cols=None, edge=None):
    """balok berorientasi: sumbu u, v, w (ortonormal), setengah-ukuran hu, hv, hw; cols = warna per muka ('u','-u','v','-v','w','-w')"""
    for n, ctr, e1, e2, key in ((u, mul(u, hu), mul(v, hv), mul(w, hw), 'u'), (mul(u, -1), mul(u, -hu), mul(v, hv), mul(w, hw), '-u'),
                                (v, mul(v, hv), mul(u, hu), mul(w, hw), 'v'), (mul(v, -1), mul(v, -hv), mul(u, hu), mul(w, hw), '-v'),
                                (w, mul(w, hw), mul(u, hu), mul(v, hv), 'w'), (mul(w, -1), mul(w, -hw), mul(u, hu), mul(v, hv), '-w')):
        fc = add(c, ctr); pts = [sub(sub(fc, e1), e2), sub(add(fc, e1), e2), add(add(fc, e1), e2), add(sub(fc, e1), e2)]
        face(cv, pts, n, (cols or {}).get(key, col_), a, glow, edge)
def basis(ax):
    t = (0, 0, 1) if abs(ax[2]) < 0.9 else (1, 0, 0)
    e1 = nrm(crs(ax, t)); e2 = crs(ax, e1); return e1, e2
def ring(c, ax, r, n=24, a0=0.0):
    e1, e2 = basis(ax)
    return [add(c, add(mul(e1, r * math.cos(a0 + math.tau * i / n)), mul(e2, r * math.sin(a0 + math.tau * i / n)))) for i in range(n)]
def ocyl(cv, c, ax, r, h, col_, a, n=20, spin=None, glow=0.0, cap_col=None, spokes=3, hub=0.55):
    """silinder berorientasi (pusat c, sumbu ax, jari-jari r, setengah-panjang h); spin = sudut jari-jari"""
    if a <= 0: return
    e1, e2 = basis(ax)
    d = [add(mul(e1, math.cos(math.tau * i / n)), mul(e2, math.sin(math.tau * i / n))) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n; nm = nrm(add(d[i], d[j]))
        pts = [add(add(c, mul(ax, -h)), mul(d[i], r)), add(add(c, mul(ax, h)), mul(d[i], r)), add(add(c, mul(ax, h)), mul(d[j], r)), add(add(c, mul(ax, -h)), mul(d[j], r))]
        face(cv, pts, nm, col_, a, glow)
    for sgn in (1, -1):
        nm = mul(ax, sgn)
        if not visible(nm): continue
        cc = add(c, mul(ax, sgn * h)); pts = [add(cc, mul(di, r)) for di in d]
        face(cv, pts, nm, cap_col or tone(col_, 0.1), a, glow)
        if hub:
            inner = [add(cc, mul(di, r * hub)) for di in d]; cv.drawPath(poly([p3(p) for p in inner]), P(col(tone(cap_col or col_, -0.25), a), stroke=1.5))
        if spin is not None:
            for k in range(spokes):
                th = spin + k * math.tau / spokes; dd = add(mul(e1, math.cos(th)), mul(e2, math.sin(th)))
                p0, p1 = p3(add(cc, mul(dd, r * 0.18))), p3(add(cc, mul(dd, r * 0.8)))
                cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(tone(cap_col or col_, -0.35), a), stroke=max(1.5, r * 12)))
def gear3d(cv, c, ax, r, h, teeth, col_, a, spin=0.0, glow=0.0, depth=0.14, cap_col=None, holes=True, pockets=0, pocket_side=1, pocket_col='#1A2A4C'):
    """roda gigi berorientasi: gigi trapesium di tepi, lubang poros; pockets = jumlah lubang 'dog' di muka sisi pocket_side"""
    if a <= 0: return
    e1, e2 = basis(ax); n = teeth * 4
    def rr(k): return r if (k % 4) in (1, 2) else r * (1 - depth)
    d = [add(mul(e1, math.cos(spin + math.tau * k / n)), mul(e2, math.sin(spin + math.tau * k / n))) for k in range(n)]
    for k in range(n):
        j = (k + 1) % n; nm = nrm(add(d[k], d[j]))
        pts = [add(add(c, mul(ax, -h)), mul(d[k], rr(k))), add(add(c, mul(ax, h)), mul(d[k], rr(k))), add(add(c, mul(ax, h)), mul(d[j], rr(j))), add(add(c, mul(ax, -h)), mul(d[j], rr(j)))]
        face(cv, pts, nm, col_, a, glow)
    for sgn in (1, -1):
        nm = mul(ax, sgn)
        if not visible(nm): continue
        cc = add(c, mul(ax, sgn * h)); pts = [add(cc, mul(d[k], rr(k))) for k in range(n)]
        face(cv, pts, nm, cap_col or tone(col_, 0.08), a, glow)
        rim = [p3(add(cc, mul(d[k], r * (1 - depth) * 0.92))) for k in range(0, n, 2)]; cv.drawPath(poly(rim), P(col(tone(cap_col or col_, -0.2), 0.7 * a), stroke=1.4))
        if holes:
            for m_ in range(5):
                th = spin + m_ * math.tau / 5; hc = add(cc, add(mul(e1, r * 0.55 * math.cos(th)), mul(e2, r * 0.55 * math.sin(th))))
                hp = [p3(q) for q in ring(hc, ax, r * 0.13, 12)]; cv.drawPath(poly(hp), P(col(tone(cap_col or col_, -0.3), a)))
        if pockets and sgn == pocket_side:
            for m_ in range(pockets):
                th = spin + m_ * math.tau / pockets + 0.4; th2 = th + 0.42
                q = [add(cc, add(mul(e1, rad_ * math.cos(tt)), mul(e2, rad_ * math.sin(tt)))) for rad_, tt in ((r * 0.32, th), (r * 0.32, th2), (r * 0.46, th2), (r * 0.46, th))]
                cv.drawPath(poly([p3(p) for p in q]), P(col(pocket_col, a)))
        hub = [p3(q) for q in ring(cc, ax, r * 0.2, 16)]; cv.drawPath(poly(hub), P(col('#2C3446', a)))
def extrude(cv, prof, y0, y1, c_side, c_front, a, front_shader=None, edge=None):
    """profil 2D (x, z) diekstrusi sepanjang y dari y0 ke y1 (y1 = muka depan yang terlihat); c_side boleh fungsi(normal) -> warna"""
    if a <= 0: return None
    m = len(prof); cx = sum(p[0] for p in prof) / m; cz = sum(p[1] for p in prof) / m
    for i in range(m):
        (xa, za), (xb, zb) = prof[i], prof[(i + 1) % m]
        n2 = (zb - za, -(xb - xa)); mx, mz = (xa + xb) / 2 - cx, (za + zb) / 2 - cz
        if n2[0] * mx + n2[1] * mz < 0: n2 = (-n2[0], -n2[1])
        nm = nrm((n2[0], 0.0, n2[1]))
        face(cv, [(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], nm, c_side(nm) if callable(c_side) else c_side, a)
    pth = poly([p3((x, y1, z)) for x, z in prof])
    if front_shader is not None: cv.drawPath(pth, P(shader=front_shader))
    else: cv.drawPath(pth, P(col(c_front, a)))
    if edge: cv.drawPath(pth, P(col(edge, 0.7 * a), stroke=1.6))
    return pth
