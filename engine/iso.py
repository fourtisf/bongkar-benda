"""Primitif isometrik 3D untuk Bongkar Benda: proyeksi, balok berbayang, silinder/roda, tali, pegas, percikan.
Sumbu: x ke kanan-bawah, y ke kiri-bawah, z ke atas. Cahaya dari kiri atas: sisi atas paling terang, sisi kiri (y+) sedang, sisi kanan (x+) gelap."""
import math, random
import skia
from bb import P, col, mixc, lg, clamp, lerp, eo, WHITE, INK, ORANGE, YELLOW

C30 = math.cos(math.radians(30))
class Iso:
    def __init__(self, ox=0.0, oy=0.0, s=50.0): self.ox, self.oy, self.s = ox, oy, s
    def p(self, x, y, z): return (self.ox + (x - y) * C30 * self.s, self.oy + (x + y) * 0.5 * self.s - z * self.s)
    def path(self, pts, close=True):
        q = [self.p(*pt) for pt in pts]; pth = skia.Path(); pth.moveTo(*q[0])
        for r in q[1:]: pth.lineTo(*r)
        if close: pth.close()
        return pth

def tone(c, k):
    """k > 0 lebih terang, k < 0 lebih gelap"""
    return mixc(c, WHITE, k) if k >= 0 else mixc(c, '#0B1222', -k)

def quad(cv, iso, pts, c, a=1.0, edge=None, ew=1.5, grad=None):
    if a <= 0: return
    pth = iso.path(pts)
    if grad:
        (x0, y0), (x1, y1) = iso.p(*grad[0]), iso.p(*grad[1])
        cv.drawPath(pth, P(shader=lg(x0, y0, x1, y1, [col(grad[2], a), col(grad[3], a)])))
    else: cv.drawPath(pth, P(col(c, a)))
    if edge: cv.drawPath(pth, P(col(edge, 0.6 * a), stroke=ew))
    return pth

def box(cv, iso, x, y, z, w, d, h, c, a=1.0, top=0.28, left=0.0, right=-0.2, edge=True, faces='tlr', hi=True):
    """balok: sisi atas (z+h), kiri (bidang y+d), kanan (bidang x+w)"""
    if a <= 0: return
    e = tone(c, -0.35) if edge else None
    if 'l' in faces: quad(cv, iso, [(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)], tone(c, left), a, e)
    if 'r' in faces: quad(cv, iso, [(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)], tone(c, right), a, e)
    if 't' in faces:
        quad(cv, iso, [(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)], tone(c, top), a, e)
        if hi:
            p0, p1, p2 = iso.p(x, y + d, z + h), iso.p(x + w, y + d, z + h), iso.p(x + w, y, z + h)
            pth = skia.Path(); pth.moveTo(*p0); pth.lineTo(*p1); pth.lineTo(*p2)
            cv.drawPath(pth, P(col(WHITE, 0.55 * a), stroke=1.6))

def shadow(cv, iso, x, y, z, w, d, a=1.0, blur=14, k=0.25):
    pth = iso.path([(x, y, z), (x + w, y, z), (x + w, y + d, z), (x, y + d, z)])
    cv.drawPath(pth, P(col('#1B2A44', k * a), blur=blur))

def ring_pts(iso, cx, cy, cz, r, axis='x', n=40, a0=0.0):
    out = []
    for k in range(n):
        th = a0 + math.tau * k / n; u, v = r * math.cos(th), r * math.sin(th)
        if axis == 'x': out.append(iso.p(cx, cy + u, cz + v))
        elif axis == 'y': out.append(iso.p(cx + u, cy, cz + v))
        else: out.append(iso.p(cx + u, cy + v, cz))
    return out
def poly(pts, close=True):
    pth = skia.Path(); pth.moveTo(*pts[0])
    for q in pts[1:]: pth.lineTo(*q)
    if close: pth.close()
    return pth

def wheel(cv, iso, x0, x1, cy, cz, r, c, a=1.0, ang=0.0, spokes=5, groove=0, groove_c=None, hub=0.22):
    """roda/puli dengan poros sepanjang sumbu x (x0..x1); muka depan di x1 menghadap kanan; jari-jari berputar sebesar ang"""
    if a <= 0: return
    back = ring_pts(iso, x0, cy, cz, r); front = ring_pts(iso, x1, cy, cz, r)
    cv.drawPath(poly(back), P(col(tone(c, -0.45), a)))
    n = len(back)
    for k in range(n):                                               # pita samping
        j = (k + 1) % n; th = math.tau * (k + 0.5) / n
        sh = 0.15 * math.cos(th) + 0.25 * math.sin(th)
        q = poly([back[k], back[j], front[j], front[k]])
        cv.drawPath(q, P(col(tone(c, -0.3 + sh), a)))
    if groove:
        for g in range(groove):
            xg = lerp(x0, x1, (g + 1) / (groove + 1)); rr = ring_pts(iso, xg, cy, cz, r * 1.001)
            cv.drawPath(poly(rr), P(col(groove_c or tone(c, -0.55), 0.8 * a), stroke=2))
    cv.drawPath(poly(front), P(col(tone(c, 0.12), a)))
    cv.drawPath(poly(front), P(col(tone(c, -0.4), a), stroke=2))
    inner = ring_pts(iso, x1, cy, cz, r * 0.78)
    cv.drawPath(poly(inner), P(col(tone(c, -0.12), a)))
    for k in range(spokes):
        th = ang + math.tau * k / spokes
        p0 = iso.p(x1, cy + r * hub * math.cos(th), cz + r * hub * math.sin(th)); p1 = iso.p(x1, cy + r * 0.78 * math.cos(th), cz + r * 0.78 * math.sin(th))
        cv.drawLine(p0[0], p0[1], p1[0], p1[1], P(col(tone(c, 0.2), a), stroke=max(3, iso.s * r * 0.16)))
    hb = ring_pts(iso, x1, cy, cz, r * hub)
    cv.drawPath(poly(hb), P(col(tone(c, 0.35), a))); cv.drawPath(poly(hb), P(col(tone(c, -0.4), a), stroke=1.5))

def rope(cv, iso, p0, p1, a=1.0, c='#3B4658', w=4.0, hi=True):
    if a <= 0: return
    (x0, y0), (x1, y1) = iso.p(*p0), iso.p(*p1)
    cv.drawLine(x0, y0, x1, y1, P(col(c, a), stroke=w))
    if hi: cv.drawLine(x0 - w * 0.25, y0, x1 - w * 0.25, y1, P(col(WHITE, 0.35 * a), stroke=w * 0.3))

def spring(cv, iso, x, y, z0, z1, r, a=1.0, c='#5C6B84', turns=6, w=5):
    """pegas spiral vertikal dari z0 ke z1"""
    if a <= 0: return
    pts = []
    n = turns * 16
    for k in range(n + 1):
        u = k / n; th = math.tau * turns * u
        pts.append(iso.p(x + r * math.cos(th), y + r * math.sin(th), lerp(z0, z1, u)))
    pth = poly(pts, close=False)
    cv.drawPath(pth, P(col(tone(c, -0.3), a), stroke=w + 2)); cv.drawPath(pth, P(col(tone(c, 0.25), a), stroke=w * 0.6))

def sparks(cv, x, y, t, seed, a=1.0, n=14, spread=140, up=True):
    """percikan api berupa garis pendek (tanpa titik)"""
    if a <= 0: return
    rnd = random.Random(seed)
    for k in range(n):
        ang = rnd.uniform(-math.pi * 0.95, -math.pi * 0.05) if up else rnd.uniform(0, math.tau)
        L = rnd.uniform(0.3, 1.0) * spread; ph = (t * rnd.uniform(2.5, 4.5) + rnd.random()) % 1.0
        d0, d1 = L * ph, L * min(1.0, ph + 0.25)
        x0, y0 = x + math.cos(ang) * d0, y + math.sin(ang) * d0 + 60 * ph * ph
        x1, y1 = x + math.cos(ang) * d1, y + math.sin(ang) * d1 + 60 * min(1, ph + 0.25) ** 2
        c = YELLOW if k % 3 else ORANGE
        cv.drawLine(x0, y0, x1, y1, P(col(c, a * (1 - ph)), stroke=4))
        cv.drawLine(x0, y0, x1, y1, P(col(WHITE, 0.7 * a * (1 - ph)), stroke=1.5))
