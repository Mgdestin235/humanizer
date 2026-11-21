#!/usr/bin/env python3
"""Génère une musique instrumentale originale (libre de droits) pour le montage.

La musique est synthétisée par ce script : aucun extrait protégé n'est utilisé.
Elle sert de musique provisoire. Pour la remplacer, mettez votre fichier dans
config.json (champ "music.file") ou donnez-le à build.py avec --music.

Usage : python3 music.py sortie.wav [durée_en_secondes]
"""
import sys
import wave
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def tone(freq, dur, harm=6, power=1.4, detune=(0.0,)):
    """Son riche en harmoniques, doux (scie filtrée)."""
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for d in detune:
        f = freq * 2 ** (d / 1200)
        for h in range(1, harm + 1):
            if f * h > 9000:
                break
            out += np.sin(2 * np.pi * f * h * t + h) / h ** power
    return out / len(detune)


def env(n, a, r, curve=2.0):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na) ** curve
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e


def add(buf, sig, start):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[: j - i]


def reverb(x, secs=2.2, wet=0.28):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * secs / 4.5))
    ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
    size = 1 << (len(x) + n).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    y *= np.abs(x).max() / (np.abs(y).max() + 1e-9)
    return x * (1 - wet) + y * wet


def render(total):
    n = int(total * SR)
    bpm = 96
    beat = 60 / bpm
    bar = beat * 4
    # Do - Sol - La mineur - Fa : progression lumineuse, 2 mesures par accord
    prog = [(48, [0, 4, 7]), (55, [0, 4, 7]), (57, [0, 3, 7]), (53, [0, 4, 7])]
    pad = np.zeros(n)
    bass = np.zeros(n)
    pluck = np.zeros(n)
    kick = np.zeros(n)
    hat = np.zeros(n)

    nchords = int(total / (2 * bar)) + 2
    for c in range(nchords):
        root, ints = prog[c % 4]
        t0 = c * 2 * bar
        d = 2 * bar + 1.6
        for k in ints + [12]:
            s = tone(midi(root + 12 + k), d, harm=7, power=1.3, detune=(-7, 0, 7))
            add(pad, s * env(len(s), 1.4, 1.6) * 0.22, t0)
        b = np.sin(2 * np.pi * midi(root - 12) * np.arange(int(d * SR)) / SR)
        add(bass, b * env(len(b), 0.15, 0.8) * 0.5, t0)

        # arpège de notes courtes (croches), de plus en plus présent
        pattern = [0, 1, 2, 1, 3, 2, 1, 2]
        notes = [root + 24 + k for k in ints] + [root + 36]
        for i in range(16):
            ts = t0 + i * beat / 2
            if ts < 3.0 or ts >= total:
                continue
            nn = notes[pattern[i % 8] % len(notes)]
            s = tone(midi(nn), 1.1, harm=5, power=1.6)
            s *= np.exp(-np.arange(len(s)) / SR * 4.2) * env(len(s), 0.004, 0.05)
            add(pluck, s * (0.5 if i % 2 else 0.7) * 0.24, ts)

    # pulsation douce (grosse caisse feutrée) à partir de ~8 s
    for i in range(int(total / beat)):
        ts = i * beat
        if ts < 8.0:
            continue
        m = int(0.35 * SR)
        tt = np.arange(m) / SR
        f = 48 + 70 * np.exp(-tt * 30)
        k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
        add(kick, k * 0.55, ts)
    # petit « shaker » sur les contretemps à partir de ~14 s
    for i in range(int(total / (beat / 2))):
        ts = i * beat / 2
        if ts < 14.0 or i % 2 == 0:
            continue
        m = int(0.06 * SR)
        nz = rng.standard_normal(m)
        nz = np.diff(np.concatenate([[0], nz]))  # passe-haut simple
        add(hat, nz * np.exp(-np.arange(m) / SR * 55) * 0.05, ts)

    # écho ping-pong sur l'arpège
    dl = int(beat * 0.75 * SR)
    L, R = pluck.copy(), pluck.copy()
    for k in range(1, 5):
        g = 0.42 ** k
        sh = dl * k
        (R if k % 2 else L)[sh:] += pluck[: n - sh] * g
    L, R = reverb(L + pad * 0.9), reverb(R + pad * 0.9)
    L += bass + kick + hat
    R += bass + kick + hat

    # dynamique : montée douce au début, baisse dans la dernière seconde du plan final
    x = np.arange(n) / SR
    swell = np.clip(x / 2.5, 0, 1) ** 1.5
    fade = np.clip((total - x) / 3.2, 0, 1) ** 1.2
    g = swell * fade
    st = np.stack([L * g, R * g], 1)
    st /= np.abs(st).max()
    return (st * 0.89 * 32767).astype(np.int16)


if __name__ == "__main__":
    out = sys.argv[1]
    total = float(sys.argv[2]) if len(sys.argv) > 2 else 62.0
    data = render(total)
    with wave.open(out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print("musique écrite :", out, f"{total:.1f}s")
