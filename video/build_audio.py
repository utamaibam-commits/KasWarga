"""Susun audio final: voiceover + SFX buatan numpy + musik latar sederhana (aman lisensi)."""
import os
import wave

import numpy as np

import timeline as TL

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
rng = np.random.default_rng(7)
T = TL.total()
N = int(T * SR) + SR


def env(n, a=0.005, d=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a)
    if d:
        e *= np.exp(-t / d)
    return e


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode='same')


def noise(n):
    return rng.standard_normal(n)


def sfx(kind):
    if kind == 'thump':
        n = int(.45 * SR); t = np.arange(n) / SR
        f = 150 * np.exp(-t * 18) + 45
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .002, .16) * 1.0
    if kind == 'stamp':
        n = int(.18 * SR)
        return (lowpass(noise(n), 6) * env(n, .001, .03) * .8 + np.sin(2 * np.pi * 90 * np.arange(n) / SR) * env(n, .001, .06) * .6)
    if kind == 'pop':
        n = int(.12 * SR); t = np.arange(n) / SR
        f = 900 * np.exp(-t * 30) + 300
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .035) * .7
    if kind == 'tick':
        n = int(.04 * SR)
        return np.sin(2 * np.pi * 2200 * np.arange(n) / SR) * env(n, .0005, .008) * .6
    if kind == 'knock':
        n = int(.16 * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 180 * t) + .5 * np.sin(2 * np.pi * 420 * t)) * env(n, .001, .03) * .8 + lowpass(noise(n), 10) * env(n, .001, .01) * .4
    if kind == 'ding':
        n = int(1.0 * SR); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1318 * t) + .6 * np.sin(2 * np.pi * 1976 * t) + .3 * np.sin(2 * np.pi * 2637 * t)) * env(n, .002, .28) * .45
    if kind == 'sparkle':
        out = np.zeros(int(.7 * SR))
        for i, f in enumerate([1568, 2093, 2637, 3136, 4186]):
            s = int(i * .06 * SR); n = int(.3 * SR); t = np.arange(n) / SR
            out[s:s + n] += np.sin(2 * np.pi * f * t) * env(n, .001, .08) * .3
        return out
    if kind == 'err':
        n = int(.3 * SR); t = np.arange(n) / SR
        return np.sign(np.sin(2 * np.pi * 110 * t)) * env(n, .002, .12) * .35
    if kind in ('whoosh', 'rip'):
        n = int((.45 if kind == 'whoosh' else .32) * SR)
        x = noise(n)
        if kind == 'whoosh':
            out = np.zeros(n)
            for i in range(0, n, 512):  # sapuan lowpass naik
                k = int(40 - 36 * i / n)
                out[i:i + 512] = lowpass(x, k)[i:i + 512]
            e = np.sin(np.pi * np.arange(n) / n) ** 2
            return out * e * 1.4
        # sobekan kertas: noise kasar terputus-putus
        grains = (rng.random(n // 220 + 1) > .35).repeat(220)[:n]
        return lowpass(x, 3) * grains * env(n, .005, .12) * .9
    if kind == 'scribble':
        n = int(.7 * SR); t = np.arange(n) / SR
        am = .5 + .5 * np.sin(2 * np.pi * 11 * t) ** 2
        return lowpass(noise(n), 4) * am * env(n, .01, .5) * .5
    if kind == 'tada':
        out = np.zeros(int(1.4 * SR))
        for i, f in enumerate([523, 659, 784, 1047]):
            s = int(i * .07 * SR); n = len(out) - s; t = np.arange(n) / SR
            out[s:] += (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * env(n, .003, .5) * .22
        return out
    raise ValueError(kind)


def read_vo(p):
    with wave.open(p) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        sr = w.getframerate()
    idx = np.arange(int(len(x) * SR / sr)) * sr / SR
    return np.interp(idx, np.arange(len(x)), x)


vo = np.zeros(N)
for s in TL.scenes():
    x = read_vo(os.path.join(HERE, 'build', 'vo_s%d.wav' % s['k']))
    a = int(s['vo'] * SR)
    vo[a:a + len(x)] += x

fx = np.zeros(N)
for t, kind, g in TL.sfx():
    x = sfx(kind) * g
    a = int(t * SR)
    fx[a:a + len(x)] += x[:max(0, N - a)]

# musik latar: 118 BPM, pluck akor + bass + kick + shaker
bpm = 118
beat = 60 / bpm
mus = np.zeros(N)
chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
bass = [130.8, 110.0, 87.3, 98.0]
nb = int(T / beat) + 2
for i in range(nb):
    t0 = int(i * beat * SR)
    bar = (i // 4) % 4
    # kick tiap ketukan
    k = sfx('thump')[:int(.25 * SR)] * .35
    mus[t0:t0 + len(k)] += k[:max(0, N - t0)]
    # shaker di setengah ketukan
    h0 = int((i + .5) * beat * SR)
    n = int(.05 * SR)
    sh = (noise(n) - lowpass(noise(n), 3)) * env(n, .001, .015) * .12
    mus[h0:h0 + n] += sh[:max(0, N - h0)]
    # bass
    n = int(beat * .9 * SR); tt = np.arange(n) / SR
    b = np.sin(2 * np.pi * bass[bar] * tt) * env(n, .005, .3) * .22
    mus[t0:t0 + n] += b[:max(0, N - t0)]
    # pluck akor di ketukan 2 & 4 (dan offbeat)
    for off in ((.0, .5) if i % 2 else (.5,)):
        p0 = int((i + off) * beat * SR)
        n = int(.35 * SR); tt = np.arange(n) / SR
        pl = sum(np.sin(2 * np.pi * f * 2 * tt) * (.6 + .4 * np.sin(2 * np.pi * f * 4 * tt)) for f in chords[bar]) * env(n, .002, .09) * .07
        mus[p0:p0 + n] += pl[:max(0, N - p0)]

# ducking musik saat ada suara
v_env = lowpass(np.abs(vo), int(.08 * SR))
duck = 1 - .55 * np.clip(v_env / .05, 0, 1)
fade = np.ones(N)
fe = int(T * SR)
fade[fe - int(1.2 * SR):fe] = np.linspace(1, 0, int(1.2 * SR))
fade[fe:] = 0
fade[:int(.3 * SR)] = np.linspace(0, 1, int(.3 * SR))
mix = vo * 1.0 + fx * 0.42 + mus * duck * fade * 0.55
peak = np.max(np.abs(mix))
mix = mix / max(peak / 0.95, 1)
mix = mix[:fe]
out = os.path.join(HERE, 'build', 'mix.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('audio', round(T, 2), 'dtk, peak', round(peak, 2))
