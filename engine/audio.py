#!/usr/bin/env python3
"""Synthesise music bed + SFX for the reel. Usage: python3 audio.py sfx.json out.wav [duration]"""
import json, sys, math, os
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100
rng = np.random.default_rng(3)

def tt(d): return np.arange(int(d * SR)) / SR
def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-t / d)
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x)
def chirp(f0, f1, d, curve=1.0):
    t = tt(d); k = (t / d) ** curve
    f = f0 * (f1 / f0) ** k
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def norm(x, peak=1.0):
    m = np.max(np.abs(x)) or 1; return x / m * peak
def sweep_noise(d, f0, f1, q=0.6):
    """noise through a sweeping one-pole bandpass-ish (lp - lp)"""
    n = int(d * SR); x = rng.standard_normal(n)
    f = f0 * (f1 / f0) ** (np.arange(n) / n)
    a1 = np.exp(-2 * np.pi * f / SR); a2 = np.exp(-2 * np.pi * f * q / SR)
    y1 = np.zeros(n); y2 = np.zeros(n); s1 = s2 = 0.0
    for i in range(n):
        s1 = a1[i] * s1 + (1 - a1[i]) * x[i]; s2 = a2[i] * s2 + (1 - a2[i]) * x[i]
        y1[i] = s1; y2[i] = s2
    return y1 - y2

# ------------------------------------------------------------- sfx
def s_whoosh(d=0.55, f0=300, f1=4000, amp=0.5):
    x = sweep_noise(d, f0, f1); n = len(x); t = np.arange(n) / n
    return norm(x * np.sin(np.pi * t) ** 1.5, amp)
def s_swish(): return s_whoosh(0.28, 900, 6000, 0.35)
def s_zoom():
    x = s_whoosh(0.95, 200, 5000, 0.45)
    t = tt(0.95); x += 0.12 * chirp(220, 880, 0.95, 1.6) * (t / 0.95) ** 2 * np.exp(-(t - 0.95) ** 2)
    return x
def s_plop():
    d = 0.22; t = tt(d)
    x = chirp(230, 85, d, 0.5) * np.exp(-t / 0.06)
    return norm(x, 0.8)
def s_pop(f0=520, f1=1100, amp=0.42):
    d = 0.09; t = tt(d)
    return norm(chirp(f0, f1, d, 0.6) * np.exp(-t / 0.025), amp)
def s_tick(): return s_pop(900, 1500, 0.16)
def s_chop():
    d = 0.35; t = tt(d)
    thud = chirp(140, 55, d, 0.4) * np.exp(-t / 0.07)
    crunch = bp(rng.standard_normal(len(t)), 1800, 6000) * np.exp(-t / 0.03)
    knock = np.sin(2 * np.pi * 620 * t) * np.exp(-t / 0.02)
    return norm(0.9 * thud + 0.55 * norm(crunch) + 0.3 * knock, 0.95)
def s_crack():
    d = 0.6; n = int(d * SR); x = np.zeros(n)
    for k in range(9):
        p = int(rng.uniform(0, 0.35) * SR); L = int(0.03 * SR)
        x[p:p + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (0.006 * SR)) * rng.uniform(0.4, 1)
    x = bp(x, 1200, 7000)
    t = tt(d); x = norm(x, 0.6) + 0.25 * np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.05)
    return x
def s_fizz(d=1.6, amp=0.28):
    n = int(d * SR); t = np.arange(n) / SR
    base = hp(rng.standard_normal(n), 4000) * 0.25
    crack = np.zeros(n); idx = rng.choice(n, int(d * 260), replace=False); crack[idx] = rng.uniform(-1, 1, len(idx))
    crack = bp(crack, 2500, 9000)
    e = np.sin(np.pi * t / d) ** 0.8
    return norm((base + norm(crack)) * e, amp)
def s_fizz_soft(): return s_fizz(1.8, 0.16)
def s_rise():
    d = 1.3; t = tt(d)
    x = 0.5 * chirp(300, 900, d, 1.2) + 0.3 * chirp(450, 1350, d, 1.2)
    x *= np.sin(np.pi * t / d) ** 1.2
    return norm(x + 0.6 * s_fizz(d, 0.5), 0.3)
def s_sting():
    d = 0.4; t = tt(d)
    f = 1700 + 90 * np.sin(2 * np.pi * 30 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.005, 0.12)
    return norm(x, 0.22)
def s_blink():
    d = 0.18; t = tt(d); return norm(chirp(600, 300, d) * np.exp(-t / 0.05), 0.2)
def s_plip():
    d = 0.16; t = tt(d)
    return norm(chirp(520, 1500, d, 0.35) * np.exp(-t / 0.035), 0.32)
def s_zap(up=True):
    d = 0.45; t = tt(d)
    f = (120 * (3 ** (t / d))) if up else (360 * (1 / 3) ** (t / d))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sq = np.tanh(4 * np.sin(ph)) * (0.6 + 0.4 * np.sin(2 * np.pi * 40 * t))
    nz = bp(rng.standard_normal(len(t)), 2000, 8000) * 0.3
    x = (lp(sq, 3000) + nz) * env_ad(len(t), 0.01, 0.16)
    return norm(x, 0.3)
def s_bell(f=1320, amp=0.3, dec=0.6):
    d = 1.4; t = tt(d)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (dec * dd)) for r, a, dd in ((1, 1, 1), (2.76, 0.5, 0.5), (5.4, 0.25, 0.3)))
    return norm(x * env_ad(len(t), 0.002, 10), amp)
def s_ding(): return s_bell(1320, 0.3)
def s_ding_soft(): return s_bell(990, 0.18)
def s_card():
    x = s_swish() * 0.6; p = s_pop(400, 800, 0.4)
    out = np.zeros(max(len(x), len(p) + int(0.12 * SR))); out[:len(x)] += x; out[int(0.12 * SR):int(0.12 * SR) + len(p)] += p
    return out
def s_boing():
    d = 0.6; t = tt(d)
    f = 260 + 90 * np.sin(2 * np.pi * 9 * t) * np.exp(-t / 0.25)
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(len(t), 0.005, 0.18), 0.35)
def s_shine():
    out = np.zeros(int(1.6 * SR))
    for i, f in enumerate((1568, 2093, 2637, 3136)):
        b = s_bell(f, 0.14, 0.35); o = int(i * 0.07 * SR); out[o:o + len(b)] += b[:len(out) - o]
    return out

def s_clunk():
    d = 0.5; t = tt(d)
    thud = chirp(90, 45, d, 0.4) * np.exp(-t / 0.08)
    click = bp(rng.standard_normal(len(t)), 1500, 5000) * np.exp(-t / 0.01)
    hum = 0.12 * np.sin(2 * np.pi * 110 * t) * np.exp(-t / 0.4)
    return norm(thud + 0.5 * click + hum, 0.7)
def s_heart():
    out = np.zeros(int(0.6 * SR))
    for off, g in ((0, 1.0), (0.17, 0.7)):
        d = 0.18; t = tt(d); b = chirp(70, 40, d, 0.5) * np.exp(-t / 0.05) * g; i = int(off * SR); out[i:i + len(b)] += b
    return norm(lp(out, 300), 0.8)
def s_blink(): return s_pop(1300, 1900, 0.08)
def s_stamp():
    d = 0.3; t = tt(d)
    return norm(chirp(160, 60, d, 0.4) * np.exp(-t / 0.05) + 0.6 * bp(rng.standard_normal(len(t)), 800, 3000) * np.exp(-t / 0.02), 0.7)

def s_beep(f=880, d=0.14, amp=0.35):
    t = tt(d); return norm(np.sin(2 * np.pi * f * t) * env_ad(len(t), 0.003, 0.08), amp)
def s_go():
    t = tt(0.45); x = np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1760 * t)
    return norm(x * env_ad(len(t), 0.003, 0.2), 0.4)
def s_buzzer():
    t = tt(0.55); x = np.tanh(3 * np.sin(2 * np.pi * 150 * t)) * env_ad(len(t), 0.01, 0.35)
    return norm(lp(x, 2500), 0.45)
def s_clock(): return s_pop(2200, 1800, 0.18)

def s_grind(d=1.3, amp=0.42):
    """gemuruh mesin bor terowongan: derau rendah + denyut gigi pemotong"""
    t = tt(d); x = lp(rng.standard_normal(len(t)), 380, 4) * (0.65 + 0.35 * np.sin(2 * np.pi * 13 * t))
    x += 0.35 * bp(rng.standard_normal(len(t)), 900, 2600) * (np.sin(2 * np.pi * 13 * t) > 0.6)
    return norm(x * np.minimum(1, t / 0.12) * np.minimum(1, (d - t) / 0.3), amp)
def s_rumble(d=1.1, amp=0.55):
    """tanah runtuh: gemuruh rendah yang meluruh + kerikil berjatuhan"""
    t = tt(d); x = lp(rng.standard_normal(len(t)), 160, 4) * np.exp(-t / 0.45)
    c = s_crack(); c = np.pad(c, (0, max(0, len(t) - len(c))))[:len(t)]
    x = norm(x) + 0.3 * norm(c)
    return norm(x, amp)
def s_pour(d=1.2, amp=0.22):
    """semen/grout mengalir: derau pita tengah bergelombang"""
    t = tt(d); x = bp(rng.standard_normal(len(t)), 250, 1400) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t + 2 * np.sin(2 * np.pi * 1.3 * t)))
    return norm(x * np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.4), amp)

def s_splash(d=1.2, amp=0.6):
    """benda besar jatuh ke air: dentum rendah + semburan derau yang meluruh"""
    t = tt(d); x = 0.8 * chirp(110, 45, d, 0.5) * np.exp(-t / 0.18)
    x += norm(bp(rng.standard_normal(len(t)), 500, 5000) * np.exp(-t / 0.35)) * 0.7
    return norm(x, amp)
def s_rewind(d=0.9, amp=0.35):
    """pita diputar mundur: nada naik-turun cepat bergetar"""
    t = tt(d); f = 500 + 900 * (t / d) ** 1.5
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * t)) + 0.25 * bp(rng.standard_normal(len(t)), 2000, 7000)
    return norm(x * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1), amp)

SFX = dict(beep=s_beep, go=s_go, buzzer=s_buzzer, clock=s_clock, clunk=s_clunk, heart=s_heart, stamp=s_stamp, blink=s_blink, whoosh=s_whoosh, swish=s_swish, zoom=s_zoom, plop=s_plop, pop=s_pop, tick=s_tick, chop=s_chop, crack=s_crack,
           fizz=s_fizz, fizz_soft=s_fizz_soft, rise=s_rise, sting=s_sting, plip=s_plip,
           zap=lambda: s_zap(True), zap2=lambda: s_zap(False), ding=s_ding, ding_soft=s_ding_soft, card=s_card,
           boing=s_boing, shine=s_shine, grind=s_grind, rumble=s_rumble, pour=s_pour, splash=s_splash, rewind=s_rewind)

# ------------------------------------------------------------- music
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def marimba(f, d=0.6):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.28) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.05)
    return x * np.minimum(t / 0.003, 1)
def pad(freqs, d):
    t = tt(d); x = np.zeros(len(t))
    for f in freqs:
        for det in (-0.12, 0.12):
            ff = f * 2 ** (det / 12)
            x += 2 * ((ff * t) % 1) - 1  # saw
    x = lp(x, 900)
    a = np.minimum(t / 0.5, 1) * np.minimum((d - t) / 0.6, 1)
    return x * a / len(freqs)
def kick():
    d = 0.35; t = tt(d); return chirp(110, 42, d, 0.35) * np.exp(-t / 0.11)
def snap():
    d = 0.18; t = tt(d); return bp(rng.standard_normal(len(t)), 900, 4000) * np.exp(-t / 0.04)
def hat():
    d = 0.06; t = tt(d); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / 0.012)

def music(D):
    bpm = 84; beat = 60 / bpm; bar = 4 * beat
    out = np.zeros(int((D + 2) * SR))
    def add(sig, at, g):
        i = int(at * SR); j = min(len(out), i + len(sig))
        if i < len(out): out[i:j] += sig[:j - i] * g
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]  # Am7 Fmaj7 Cmaj7 G7
    arps = [[0, 1, 2, 3, 2, 1, 3, 2], [0, 2, 1, 3, 2, 3, 1, 2]]
    nb = int(D / bar) + 1
    for b in range(nb):
        t0 = b * bar; ch = chords[b % 4]
        add(pad([midi(n) for n in ch], bar + 0.4), t0, 0.16)
        add(np.sin(2 * np.pi * midi(ch[0] - 12) * tt(bar * 0.9)) * np.exp(-tt(bar * 0.9) / 0.9), t0, 0.22)
        pat = arps[b % 2]
        for k in range(8):
            if b == 0 and k < 2: continue
            add(marimba(midi(ch[pat[k]] + 12), 0.9), t0 + k * beat / 2, 0.12 if k % 2 == 0 else 0.08)
        if b >= 1:
            for k in range(4):
                if k in (0, 2): add(kick(), t0 + k * beat, 0.42)
                if k in (1, 3): add(snap(), t0 + k * beat, 0.12)
            for k in range(8): add(hat(), t0 + k * beat / 2 + 0.01, 0.05 if k % 2 else 0.03)
    out = out[:int(D * SR)]
    t = np.arange(len(out)) / SR
    out *= np.minimum(t / 0.8, 1) * np.minimum((D - t) / 1.6, 1)
    return out


# ------------------------------------------------------------- EP22: lagu orisinal lo-fi pop ceria (lebih menonjol dari musik latar biasa)
def epiano(f, d):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 1.1) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.35) + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t / 0.15)
    x *= 1 + 0.12 * np.sin(2 * np.pi * 5.2 * t)
    return x * np.minimum(t / 0.006, 1) * np.minimum((d - t) / 0.05, 1)
def lead(f, d):
    t = tt(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(t / 0.2, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    x = np.sin(ph) * np.exp(-t / 0.6) + 0.3 * np.sin(2 * ph) * np.exp(-t / 0.22) + 0.08 * np.sin(3 * ph) * np.exp(-t / 0.08)
    return lp(x, 3200) * np.minimum(t / 0.004, 1) * np.minimum((d - t) / 0.04, 1)
def bassline(f, d):
    t = tt(d)
    x = np.tanh(1.6 * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t))) * np.exp(-t / 0.6)
    return lp(x, 500) * np.minimum(t / 0.004, 1) * np.minimum((d - t) / 0.03, 1)
def clap():
    d = 0.22; t = tt(d); n = rng.standard_normal(len(t)); env = np.zeros(len(t))
    for k, o in enumerate((0.0, 0.011, 0.022)):
        i = int(o * SR); env[i:] += np.exp(-(t[i:] - o) / (0.008 if k < 2 else 0.07))
    return bp(n, 1000, 5000) * env * 0.6
def chime(f, d=1.6):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t / 0.3)) * np.exp(-t / 0.7) * np.minimum(t / 0.002, 1)

def music(D):
    bpm = float(os.environ.get('BB_BPM', 108)); beat = 60 / bpm; bar = 4 * beat; sw = 0.03; TR = int(os.environ.get('BB_TR', 0))   # Bongkar Benda: C-G-Am-F, 108 BPM
    out = np.zeros(int((D + 3) * SR))
    def add(sig, at, g):
        i = int(at * SR); j = min(len(out), i + len(sig))
        if 0 <= i < len(out): out[i:j] += sig[:j - i] * g
    chords = [[55, 60, 64, 67], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]   # C  G  Am  F (ceria, ala video sains)
    roots = [36, 43, 45, 41]
    mel = [[(76, 0, .5), (79, .5, .5), (81, 1, .5), (79, 1.5, 1), (76, 2.5, .5), (74, 3, 1)],
           [(74, 0, .5), (76, .5, .5), (79, 1, 1), (76, 2, .5), (74, 2.5, .5), (72, 3, 1)],
           [(76, 0, .5), (79, .5, .5), (81, 1, .5), (84, 1.5, 1), (81, 2.5, .5), (79, 3, 1)],
           [(81, 0, .5), (79, .5, .5), (76, 1, 1), (74, 2, .5), (72, 2.5, 1.5)]]
    nb = int(D / bar) + 2
    for b in range(nb):
        t0 = b * bar; ch = chords[b % 4]; rt = roots[b % 4]
        for st, ln, g in ((0, 1.4, 0.11), (1.5, 0.45, 0.07), (2.5, 0.45, 0.07), (3.5, 0.45, 0.06)):
            for n in ch: add(epiano(midi(n + TR), ln * beat + 0.2), t0 + st * beat, g)
        for st, n, ln in ((0, rt, 1.2), (1.5, rt, 0.4), (2, rt + 12, 0.4), (3, rt + 7, 0.8)):
            add(bassline(midi(n + TR), ln * beat), t0 + st * beat, 0.30)
        for n, st, ln in mel[b % 4]:
            add(lead(midi(n + TR), ln * beat + 0.15), t0 + st * beat, 0.16)
        for k in range(4):
            if k in (0, 2): add(kick(), t0 + k * beat, 0.5)
            if k in (1, 3): add(clap(), t0 + k * beat, 0.22)
        add(kick(), t0 + 2.5 * beat, 0.3)
        for k in range(8): add(hat(), t0 + k * beat / 2 + (sw if k % 2 else 0), 0.07 if k % 2 else 0.045)
        if b % 4 == 0: add(chime(midi(84 + TR)), t0, 0.10)
    out = out[:int(D * SR)]
    t = np.arange(len(out)) / SR
    out *= np.minimum(t / 0.15, 1) * np.minimum((D - t) / 1.8, 1)
    return out

def voice_fx(x):
    import os
    if os.environ.get('VO_ENGINE', 'gemini') != 'espeak':
        x = hp(x, 70) + 0.18 * bp(hp(x, 70), 2500, 6000)
        env = np.sqrt(np.convolve(x ** 2, np.ones(441) / 441, mode='same') + 1e-9)
        x = x * np.minimum(1.0, (0.14 / env) ** 0.35)
        return norm(x, 0.9)
    x = hp(x, 85)
    x = x + 0.45 * bp(x, 2200, 5200) + 0.25 * bp(x, 180, 320)      # presence + body
    air = hp(x, 3500); x = x + 0.12 * np.tanh(3 * air)               # a bit of air/brightness
    # simple compressor
    env = np.sqrt(np.convolve(x ** 2, np.ones(441) / 441, mode='same') + 1e-9)
    g = np.minimum(1.0, (0.12 / env) ** 0.5); x = x * g
    # small room
    y = x.copy()
    for d, a in ((0.023, 0.16), (0.037, 0.11), (0.053, 0.08), (0.071, 0.05)):
        k = int(d * SR); y[k:] += a * lp(x, 4000)[:-k]
    return norm(y, 0.9)

def smooth_env(x, win):
    return np.convolve(np.abs(x), np.ones(win) / win, mode='same')

if __name__ == '__main__':
    tl = json.load(open(sys.argv[1])); out_path = sys.argv[2]
    D = tl['out_dur']
    mus = music(D)
    if os.environ.get('MUSIC', '1') == '0': mus = mus * 0.0   # versi tanpa musik latar (untuk lagu TikTok/IG)
    n = len(mus)
    fx = np.zeros(n + 4 * SR); vo = np.zeros(n + 4 * SR)
    cache = {}
    for at, kind in tl['sfx']:
        if kind not in cache: cache[kind] = SFX[kind]()
        s = cache[kind] * (0.45 if kind == 'tick' else 1.0)
        i = int(at * SR); fx[i:i + len(s)] += s
    for at, path in tl.get('voice', []):
        sr, v = wavfile.read(path); v = v.astype(np.float64) / 32768.0
        v = voice_fx(v); i = int(at * SR); vo[i:i + len(v)] += v
    fx = fx[:n]; vo = vo[:n]
    venv = np.clip(smooth_env(vo, 4410) / 0.06, 0, 1)
    venv = np.convolve(venv, np.ones(8820) / 8820, mode='same')       # smooth ducking ramps
    fenv = np.clip(smooth_env(fx, 2205) / 0.08, 0, 1)
    m_gain = 0.85 * (1 - 0.3 * fenv) * (1 - 0.58 * np.clip(venv, 0, 1))   # EP22: lagu lebih menonjol, tetap turun saat ada suara
    f_gain = 0.9 * (1 - 0.35 * np.clip(venv, 0, 1))
    mix = mus * m_gain + fx * f_gain + vo * 1.0
    mix = np.tanh(mix * 1.1) / 1.1
    st = np.stack([mix, mix], axis=1)
    wavfile.write(out_path, SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))
    print('ok', len(mix) / SR)
