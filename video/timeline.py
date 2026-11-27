"""Timeline bersama untuk audio & render: waktu mulai scene, beat, dan daftar SFX."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BEATS = {int(k): v for k, v in json.load(open(os.path.join(HERE, 'build', 'beats.json'))).items()}
LEAD = 0.30
TAIL = {1: 0.45, 2: 0.45, 3: 0.55, 4: 0.55, 5: 1.10, 6: 0.55, 7: 1.60}
FPS = 30


def scenes():
    out, t = [], 0.0
    for k in range(1, 8):
        d = BEATS[k]['dur']
        dur = LEAD + d + TAIL[k]
        out.append({'k': k, 'start': t, 'dur': dur, 'vo': t + LEAD, 'beats': [LEAD + b for b in BEATS[k]['beats']]})
        t += dur
    return out


def total():
    s = scenes()[-1]
    return s['start'] + s['dur']


def sfx():
    """Daftar (waktu absolut, jenis, gain)."""
    ev = []
    for s in scenes():
        t0, b, k = s['start'], s['beats'], s['k']
        if k > 1:
            ev.append((t0, 'rip', 0.9))
        if k == 1:
            ev += [(t0 + b[0], 'whoosh', .7), (t0 + b[0] + .15, 'pop', .6), (t0 + b[1], 'thump', 1.0), (t0 + b[1] + .02, 'stamp', .8)]
            ev += [(t0 + b[2] + i * 0.32, 'knock', .8) for i in range(4)]
        elif k == 2:
            ev += [(t0 + b[0], 'pop', .7), (t0 + b[1], 'pop', .7), (t0 + b[2], 'scribble', .8), (t0 + b[3], 'thump', 1.0), (t0 + b[3], 'err', .5)]
        elif k == 3:
            ev += [(t0 + b[0], 'whoosh', .6), (t0 + b[1], 'thump', 1.0), (t0 + b[1] + .05, 'sparkle', .7), (t0 + b[2], 'stamp', .9),
                   (t0 + b[2] + .05, 'ding', .8), (t0 + b[3], 'pop', .7)]
        elif k == 4:
            ev += [(t0 + b[0], 'whoosh', .6), (t0 + b[1], 'scribble', .7), (t0 + b[1] + .1, 'thump', .8), (t0 + b[2], 'whoosh', .8),
                   (t0 + b[2] + .35, 'pop', .8)]
        elif k == 5:
            ev += [(t0 + b[0], 'pop', .7)]
            t = t0 + b[1]
            gap = 0.06
            while t < t0 + b[2]:
                ev.append((t, 'tick', .45))
                t += gap
                gap *= 1.09
            ev += [(t0 + b[2], 'thump', 1.0), (t0 + b[2], 'tada', .9)]
        elif k == 6:
            ev += [(t0 + b[i], 'stamp', .9) for i in range(3)] + [(t0 + b[3], 'ding', .8)]
        elif k == 7:
            ev += [(t0 + b[0], 'whoosh', .6), (t0 + b[1], 'thump', 1.0), (t0 + b[1] + .05, 'sparkle', .8), (t0 + b[1] + .6, 'pop', .6)]
    return ev
