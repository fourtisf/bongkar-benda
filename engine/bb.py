#!/usr/bin/env python3
"""Mesin video Bongkar Benda (skia-python, 1080x1920, 30 fps, tema terang + ilustrasi isometrik 3D).
Episode (episodes/epXX_nama/episode.py) mengisi bb.GROUPS, bb.PHRASES, bb.TITLE, bb.DRAWERS, bb.build_sfx lalu memanggil bb.main().
Jalankan dari folder episode:  python3 episode.py preview t1 t2 ... | timeline out.json | video out.mp4
Waktu animasi (DUR detik) diregangkan ke durasi suara (vo/lines.json) lewat build_warp(), sama seperti mesin Ruang Pikir."""
import skia, math, json, sys, os, subprocess
import numpy as np

W, H, FPS = 1080, 1920, 30
DUR = 42.0
ENGINE = os.path.dirname(os.path.abspath(__file__)); FD = os.path.join(ENGINE, 'fonts')
EP = os.getcwd()

# ------------------------------------------------------------ palet brand (lihat BRAND.md)
BG0, BG1 = '#F6F8FC', '#DCE4EF'
INK, INK2, MUTED = '#14213D', '#2C3E5F', '#6B7A93'
ORANGE, ORANGE_D, TEAL, YELLOW, RED, SKY, WHITE = '#FF7A1A', '#E0600A', '#12B3A3', '#FFC23C', '#EF4136', '#4F9DFF', '#FFFFFF'
STEEL, STEEL_D, CONCRETE = '#8E9AAF', '#4A5568', '#D3DAE5'

# ------------------------------------------------------------ util (sama dengan mesin Ruang Pikir)
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def prog(t, a, b): return clamp((t - a) / (b - a)) if b > a else (1.0 if t >= a else 0.0)
def eo(t): t = clamp(t); return 1 - (1 - t) ** 3
def ei(t): t = clamp(t); return t ** 3
def eio(t): t = clamp(t); return t * t * (3 - 2 * t)
def bo(t, s=1.70158): t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1
def bump(t): t = clamp(t); return math.sin(math.pi * t)
def col(h, a=1.0):
    h = h.lstrip('#'); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(clamp(a) * 255))
def mixc(c1, c2, u):
    a = [int(c1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]; b_ = [int(c2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02X%02X%02X' % tuple(int(round(lerp(x, y, clamp(u)))) for x, y in zip(a, b_))
def P(c=None, stroke=0, blur=0, shader=None, effect=None):
    p = skia.Paint(AntiAlias=True)
    if c is not None: p.setColor(c)
    if shader is not None: p.setShader(shader)
    if stroke: p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if effect is not None: p.setPathEffect(effect)
    return p
def lg(x0, y0, x1, y1, cs, pos=None): return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], cs, pos)
def rg(x, y, r, cs, pos=None): return skia.GradientShader.MakeRadial(skia.Point(x, y), r, cs, pos)
def layer(cv, a, rect=None): cv.saveLayerAlpha(rect, int(clamp(a) * 255))
_tf = {}
def font(name, size):
    if name not in _tf: _tf[name] = skia.Typeface.MakeFromFile(os.path.join(FD, name))
    f = skia.Font(_tf[name], size); f.setEdging(skia.Font.Edging.kAntiAlias); f.setSubpixel(True); return f
XB, B, M, MONO = 'PlusJakartaSans-ExtraBold.ttf', 'PlusJakartaSans-Bold.ttf', 'PlusJakartaSans-Medium.ttf', 'JetBrainsMono-ExtraBold.ttf'
def bl(f, cy): m = f.getMetrics(); return cy - (m.fAscent + m.fDescent) / 2
def tracked(cv, s, cx, cy, f, paint, sp):
    w = sum(f.measureText(c) + sp for c in s) - sp; x = cx - w / 2; b_ = bl(f, cy)
    for c in s: cv.drawString(c, x, b_, f, paint); x += f.measureText(c) + sp
    return w
def parse(s):
    out, buf = [], ''
    for ch in s:
        if ch == '[':
            if buf: out.append((buf, False)); buf = ''
        elif ch == ']': out.append((buf, True)); buf = ''
        else: buf += ch
    if buf: out.append((buf, False))
    return out

# ------------------------------------------------------------ elemen UI brand
def text_c(cv, s, cx, cy, size, c=INK, a=1.0, f=XB, halo=0.0):
    ff = font(f, size); w = ff.measureText(s); y = bl(ff, cy)
    if halo > 0: cv.drawString(s, cx - w / 2, y, ff, P(col(WHITE, halo * a), blur=size * 0.18))
    cv.drawString(s, cx - w / 2, y, ff, P(col(c, a))); return w
def mono(cv, s, cx, cy, size, c=INK, a=1.0, sp=2.0, align=0.5):
    f = font(MONO, size); w = sum(f.measureText(ch) + sp for ch in s) - sp; x = cx - w * align; y = bl(f, cy)
    for ch in s: cv.drawString(ch, x, y, f, P(col(c, a))); x += f.measureText(ch) + sp
    return w
def card(cv, r, a=1.0, rad=26, fill=WHITE, edge='#C9D3E3', shadow=0.22, lift=14):
    """kartu putih membulat dengan bayangan lembut (gaya tema terang)"""
    if a <= 0: return
    rr = skia.RRect.MakeRectXY(r, rad, rad)
    cv.drawRRect(skia.RRect.MakeRectXY(r.makeOffset(0, lift), rad, rad), P(col('#2B3A55', shadow * a), blur=lift * 1.4))
    cv.drawRRect(rr, P(col(fill, a)))
    cv.drawRRect(rr, P(col(edge, 0.9 * a), stroke=2))
def chip(cv, text, x, y, a=1.0, size=26, fg=WHITE, bg=INK, f=XB, pad=24):
    if a <= 0: return 0
    ff = font(f, size); w = ff.measureText(text); h = size * 1.75
    r = skia.Rect.MakeXYWH(x - w / 2 - pad, y - h / 2, w + pad * 2, h)
    cv.drawRoundRect(r.makeOffset(0, 6), h / 2, h / 2, P(col('#2B3A55', 0.22 * a), blur=8))
    cv.drawRoundRect(r, h / 2, h / 2, P(col(bg, a)))
    cv.drawString(text, x - w / 2, bl(ff, y), ff, P(col(fg, a)))
    return w + pad * 2
def label(cv, text, tx, ty, lx, ly, a=1.0, c=INK, dot=ORANGE, size=26, sub=None):
    """label penunjuk: titik di target (tx,ty), garis ke kartu label di (lx,ly)"""
    if a <= 0: return
    u = eo(clamp(a * 1.4))
    ex, ey = lerp(tx, lx, u), lerp(ty, ly, u)
    cv.drawLine(tx, ty, ex, ey, P(col(INK, 0.75 * a), stroke=3))
    cv.drawCircle(tx, ty, 11, P(col(WHITE, a))); cv.drawCircle(tx, ty, 7, P(col(dot, a)))
    if u < 0.6: return
    aa = a * prog(u, 0.6, 1.0)
    f = font(XB, size); w = f.measureText(text); fs = font(B, size * 0.7); ws = fs.measureText(sub) if sub else 0
    bw = max(w, ws) + 44; bh = size * 1.8 + (size * 0.95 if sub else 0)
    r = skia.Rect.MakeXYWH(lx - bw / 2, ly - bh / 2, bw, bh)
    card(cv, r, aa, rad=18, lift=8)
    cv.drawRoundRect(skia.Rect(r.left(), r.top(), r.left() + 8, r.bottom()), 4, 4, P(col(dot, aa)))
    cy = ly - (size * 0.45 if sub else 0)
    cv.drawString(text, lx - w / 2 + 4, bl(f, cy), f, P(col(c, aa)))
    if sub: cv.drawString(sub, lx - ws / 2 + 4, bl(fs, cy + size * 0.95), fs, P(col(MUTED, aa)))
def check(cv, cx, cy, r, p_, a=1.0, c=TEAL):
    if p_ <= 0 or a <= 0: return
    cv.drawCircle(cx, cy, r, P(col(c, a * eo(p_))))
    pth = skia.Path(); pth.moveTo(cx - r * 0.45, cy + r * 0.02); pth.lineTo(cx - r * 0.1, cy + r * 0.38); pth.lineTo(cx + r * 0.5, cy - r * 0.35)
    m = skia.PathMeasure(pth, False); seg = skia.Path(); m.getSegment(0, m.getLength() * eo(prog(p_, 0.3, 1.0)), seg, True)
    cv.drawPath(seg, P(col(WHITE, a), stroke=r * 0.2))
def wrench(cv, x, y, s, c=ORANGE, a=1.0, rot=-40):
    """ikon kunci pas (brand)"""
    cv.save(); cv.translate(x, y); cv.rotate(rot)
    p = skia.Path(); p.addRoundRect(skia.Rect(-s * 0.13, -s * 0.15, s * 0.13, s * 0.75), s * 0.12, s * 0.12)
    h = skia.Path(); h.addCircle(0, -s * 0.38, s * 0.36); p = skia.Op(p, h, skia.PathOp.kUnion_PathOp)
    n = skia.Path(); n.addRect(skia.Rect(-s * 0.13, -s * 0.85, s * 0.13, -s * 0.36)); p = skia.Op(p, n, skia.PathOp.kDifference_PathOp)
    cv.drawPath(p, P(col(c, a))); cv.restore()
def logo_mark(cv, cx, cy, s, a=1.0, t=0.0, open_=1.0):
    """logo: kubus isometrik yang 'dibongkar' (tiga sisi terpisah) di dalam lencana oranye"""
    if a <= 0: return
    r = skia.Rect(cx - s, cy - s, cx + s, cy + s)
    cv.drawRoundRect(r.makeOffset(0, s * 0.1), s * 0.42, s * 0.42, P(col(ORANGE_D, 0.5 * a), blur=s * 0.12))
    cv.drawRoundRect(r, s * 0.42, s * 0.42, P(shader=lg(0, cy - s, 0, cy + s, [col('#FF9A45', a), col(ORANGE, a), col(ORANGE_D, a)], [0, 0.5, 1])))
    k = s * 0.42; c30 = math.cos(math.radians(30)); gap = s * 0.09 * open_
    def face(pts, c):
        p = skia.Path(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        p.close(); cv.drawPath(p, P(col(c, a)))
    top = [(cx, cy - k), (cx + k * c30, cy - k * 0.5), (cx, cy), (cx - k * c30, cy - k * 0.5)]
    face([(x, y - gap) for x, y in top], WHITE)
    face([(cx - k * c30 - gap * c30, cy - k * 0.5 + gap * 0.5), (cx - gap * c30, cy + gap * 0.5), (cx - gap * c30, cy + k + gap * 0.5), (cx - k * c30 - gap * c30, cy + k * 0.5 + gap * 0.5)], '#FFE2C8')
    face([(cx + gap * c30, cy + gap * 0.5), (cx + k * c30 + gap * c30, cy - k * 0.5 + gap * 0.5), (cx + k * c30 + gap * c30, cy + k * 0.5 + gap * 0.5), (cx + gap * c30, cy + k + gap * 0.5)], INK)

# ------------------------------------------------------------ latar, judul, caption, watermark
_bg = None
def bg_img():
    global _bg
    if _bg is None:
        s = skia.Surface(W, H); c = s.getCanvas()
        c.drawRect(skia.Rect(0, 0, W, H), P(shader=lg(0, 0, 0, H, [col('#EEF3FA'), col('#E3EAF4'), col('#C9D6E8'), col('#B7C7DD')], [0, 0.4, 0.78, 1])))
        c.drawRect(skia.Rect(0, 0, W, H), P(shader=rg(540, 820, 760, [col(WHITE, 0.7), col(WHITE, 0)])))
        p = skia.Path()                                                   # lantai grid isometrik tipis (garis, tanpa titik)
        for k in range(-14, 15):
            p.moveTo(540 + k * 90 - 1400 * 0.866, 1500 - 1400 * 0.5); p.lineTo(540 + k * 90 + 1400 * 0.866, 1500 + 1400 * 0.5)
            p.moveTo(540 + k * 90 + 1400 * 0.866, 1500 - 1400 * 0.5); p.lineTo(540 + k * 90 - 1400 * 0.866, 1500 + 1400 * 0.5)
        c.save(); c.clipRect(skia.Rect(0, 1100, W, H))
        c.drawPath(p, P(col('#9FB2CC', 0.45), stroke=1.6)); c.restore()
        c.drawRect(skia.Rect(0, 1100, W, H), P(shader=lg(0, 1100, 0, 1500, [col('#E3EAF4', 1), col('#E3EAF4', 0)])))
        _bg = s.makeImageSnapshot()
    return _bg
def draw_bg(cv, t): cv.drawImage(bg_img(), 0, 0)

TITLE = None            # ('Lift,', 'kok nggak jatuh?')
TITLE_OUT = 4.5         # judul hilang di detik animasi ini (hanya adegan pertama)
def draw_title(cv, t):
    if not TITLE: return
    a = eo(prog(t, 0.0, 0.3)) * (1 - eio(prog(t, TITLE_OUT - 0.4, TITLE_OUT)))
    if a <= 0: return
    dy = (1 - eo(prog(t, 0.0, 0.35))) * 20 - 12 * eio(prog(t, TITLE_OUT - 0.4, TITLE_OUT))
    layer(cv, a)
    fb = font(MONO, 22); tw = sum(fb.measureText(ch) + 3 for ch in 'BONGKAR BENDA') - 3; bw = tw + 92
    r = skia.Rect(540 - bw / 2, 128 + dy, 540 + bw / 2, 176 + dy)
    cv.drawRoundRect(r, 24, 24, P(col(INK))); wrench(cv, r.left() + 34, r.centerY() + 2, 26, ORANGE)
    x = r.left() + 62; y = bl(fb, r.centerY())
    for ch in 'BONGKAR BENDA': cv.drawString(ch, x, y, fb, P(col(WHITE))); x += fb.measureText(ch) + 3
    f1 = font(XB, 132); s1 = TITLE[0]; w1 = f1.measureText(s1)
    if w1 > 960: f1 = font(XB, 132 * 960 / w1); w1 = f1.measureText(s1)
    y1 = bl(f1, 268 + dy)
    for k in range(7, 0, -1): cv.drawString(s1, 540 - w1 / 2 + k * 0.6, y1 + k * 1.1, f1, P(col(mixc('#C3CEE0', '#9AA8C0', k / 7))))
    cv.drawString(s1, 540 - w1 / 2, y1, f1, P(col(INK)))
    f2 = font(XB, 78); s2 = TITLE[1]; w2 = f2.measureText(s2)
    if w2 > 980: f2 = font(XB, 78 * 980 / w2); w2 = f2.measureText(s2)
    y2 = bl(f2, 376 + dy)
    cv.drawString(s2, 540 - w2 / 2, y2 + 4, f2, P(col(ORANGE_D, 0.35), blur=6))
    cv.drawString(s2, 540 - w2 / 2, y2, f2, P(col(ORANGE)))
    u = eo(prog(t, 0.25, 0.75))
    if u > 0:                                                             # garis bawah coretan tangan
        p = skia.Path(); x0, x1 = 540 - w2 / 2 + 10, 540 + w2 / 2 - 10
        p.moveTo(x0, 420 + dy); p.quadTo((x0 + x1) / 2, 436 + dy, x1, 414 + dy)
        m = skia.PathMeasure(p, False); seg = skia.Path(); m.getSegment(0, m.getLength() * u, seg, True)
        cv.drawPath(seg, P(col(INK), stroke=8))
    cv.restore()

PHRASES = []            # [(t_mulai, 'teks dengan [kata kunci]')]
def _tokens(text):
    out, prev_space = [], False
    for seg, h in parse(text):
        for k, w in enumerate(seg.split(' ')):
            if w: out.append((w, h, k > 0 or prev_space))
        prev_space = seg.endswith(' ')
    return out
_LAYOUT = {}
def cap_layout(text, size=56, maxw=900):
    key = (text, size)
    if key not in _LAYOUT:
        f = font(XB, size); sp = f.measureText(' '); lines, cur, cw = [], [], 0
        for w, h, spc in _tokens(text):
            ww = f.measureText(w); gap = sp if (cur and spc) else 0
            if cur and spc and cw + gap + ww > maxw: lines.append((cur, cw)); cur, cw, gap = [], 0, 0
            cw += gap + ww; cur.append((w, h, ww, gap))
        if cur: lines.append((cur, cw))
        _LAYOUT[key] = lines
    return _LAYOUT[key]
CAP_Y = 1495           # pusat caption (di atas UI TikTok/Reels di bagian paling bawah)
def draw_captions(cv, t):
    size, lh = 56, 68; f = font(XB, size)
    for i, (s, txt) in enumerate(PHRASES):
        e = PHRASES[i + 1][0] - 0.2 if i + 1 < len(PHRASES) else DUR - 0.3
        if t < s or t > e + 0.17: continue
        aout = 1 - prog(t, e, e + 0.16); lines = cap_layout(txt, size)
        y0 = CAP_Y - (len(lines) - 1) * lh / 2; n = 0
        pa = eo(prog(t, s, s + 0.15)) * aout; mw = max(wt for _, wt in lines)
        pr = skia.Rect(540 - mw / 2 - 40, y0 - lh / 2 - 14, 540 + mw / 2 + 40, y0 + (len(lines) - 0.5) * lh + 14)
        cv.drawRoundRect(pr.makeOffset(0, 10), 30, 30, P(col('#2B3A55', 0.16 * pa), blur=16))
        cv.drawRoundRect(pr, 30, 30, P(col(WHITE, 0.88 * pa)))
        for li, (words, wtot) in enumerate(lines):
            x = 540 - wtot / 2; cy = y0 + li * lh
            for w, h, ww, gap in words:
                x += gap; p_ = prog(t, s + n * 0.035, s + n * 0.035 + 0.22); n += 1; a = eo(p_) * aout
                if a > 0:
                    y = bl(f, cy) + (1 - eo(p_)) * 14
                    cv.drawString(w, x, y, f, P(col(WHITE, 0.95 * a), blur=10))
                    cv.drawString(w, x, y + 3, f, P(col('#9AA8C0', 0.35 * a), blur=4))
                    cv.drawString(w, x, y, f, P(col(ORANGE if h else INK, a)))
                x += ww
def draw_watermark(cv, t):
    tracked(cv, 'BONGKAR BENDA', 540, 1650, font(MONO, 20), P(col(INK, 0.3 * eo(prog(t, .5, 1.2)))), 6)

# ------------------------------------------------------------ adegan: crossfade + kamera halus + memudar sebelum zona caption
GROUPS = []; DRAWERS = []; FADE2 = 0.45
_MASK = skia.Paint(Shader=lg(0, 120, 0, 1780, [col('#000000', 0), col('#000000', 1), col('#000000', 1), col('#000000', 0)],
                              [0, 40 / 1660, 1480 / 1660, 1]), BlendMode=skia.BlendMode.kDstIn)
def draw_groups(cv, t):
    n0 = cv.getSaveCount(); cv.saveLayer(None, None)
    for i, (s, e, _) in enumerate(GROUPS):
        fi = FADE2 if i > 0 else 0; fo = FADE2 if i < len(GROUPS) - 1 else 0
        if t < s or t > e + fo: continue
        ain = eo(prog(t, s, s + fi)) if fi else 1.0; aout = 1 - eio(prog(t, e, e + fo)) if fo else 1.0
        a = min(ain, aout); sc = (1.06 - 0.06 * ain if fi else 1.0) * (1 + 0.025 * eio(prog(t, s, e))) * (1 + 0.04 * eio(prog(t, e, e + fo)) if fo else 1)
        cv.save(); cv.translate(540, 760); cv.scale(sc, sc); cv.translate(-540, -760)
        if a < 1: layer(cv, a)
        DRAWERS[i](cv, t)
        if a < 1: cv.restore()
        cv.restore()
    if cv.getSaveCount() != n0 + 1: print(f'peringatan: save/restore tidak seimbang di t={t:.2f}', file=sys.stderr); cv.restoreToCount(n0 + 1)
    cv.drawRect(skia.Rect(0, 0, W, H), _MASK); cv.restore()

def draw_frame(cv, t):
    draw_bg(cv, t); draw_groups(cv, t); draw_watermark(cv, t); draw_title(cv, t); draw_captions(cv, t)
    fe = prog(t, DUR - 0.35, DUR)
    if fe > 0: cv.drawRect(skia.Rect(0, 0, W, H), P(col(BG0, fe)))

def build_sfx(): return []

# ------------------------------------------------------------ regangkan waktu animasi ke suara
def build_warp():
    meta = os.path.join(EP, 'vo', 'lines.json')
    A, O = [0.0], [0.0]
    lines = json.load(open(meta)) if os.path.exists(meta) else []
    anchors = [l['anchor'] for l in lines]
    for k, l in enumerate(lines):
        if l['anchor'] > A[-1]: O.append(O[-1] + (l['anchor'] - A[-1])); A.append(l['anchor'])
        nxt = anchors[k + 1] if k + 1 < len(anchors) else DUR
        need = l['dur'] + (0.9 if k + 1 == len(lines) else 0.35)
        O.append(O[-1] + max(nxt - l['anchor'], need)); A.append(nxt)
    if A[-1] < DUR: O.append(O[-1] + DUR - A[-1]); A.append(DUR)
    return np.array(A), np.array(O), lines
WA = WO = None
def anim_t(T): return float(np.interp(T, WO, WA))
def out_t(t): return float(np.interp(t, WA, WO))

def main(argv=None):
    global WA, WO
    argv = argv or sys.argv; mode = argv[1]
    WA, WO, lines = build_warp(); out_dur = float(WO[-1])
    if mode == 'preview':
        os.makedirs(os.path.join(EP, 'preview'), exist_ok=True); s = skia.Surface(W, H); cv = s.getCanvas()
        for ts in argv[2:]:
            t = float(ts); cv.clear(skia.ColorWHITE); draw_frame(cv, t); s.makeImageSnapshot().save(os.path.join(EP, 'preview', f't{t:05.2f}.png'), skia.kPNG)
    elif mode == 'timeline':
        tl = {'out_dur': out_dur, 'sfx': [(round(out_t(t), 4), k) for t, k in sys.modules['__main__'].build_sfx()],
              'voice': [(round(out_t(l['anchor']) + 0.04, 4), l['file']) for l in lines]}
        json.dump(tl, open(argv[2], 'w'), indent=1); print('out_dur', out_dur)
    elif mode == 'video':
        n = int(round(out_dur * FPS)); s = skia.Surface(W, H); cv = s.getCanvas()
        pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', argv[2]], stdin=subprocess.PIPE)
        for fi in range(n):
            cv.clear(skia.ColorWHITE); draw_frame(cv, anim_t(fi / FPS)); pr.stdin.write(s.makeImageSnapshot().tobytes())
            if fi % 200 == 0: print('frame', fi, '/', n, flush=True)
        pr.stdin.close(); pr.wait()
