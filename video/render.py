"""Render video promosi KasWarga, gaya "Guntingan Kertas" (paper cut-out) 1080x1920 30 fps.

python3 render.py stills t1 t2 ...   -> build/still_<t>.png
python3 render.py full               -> build/video_noaudio.mp4 lalu KasWarga-Promo.mp4
"""
import math
import os
import random
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

import timeline as TL

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, 'build')
A = os.path.join(HERE, 'assets')
W, H, FPS = 1080, 1920, 30
FONT = '/usr/share/fonts/opentype/inter/Inter-%s.otf'
SC = TL.scenes()
TOTAL = TL.total()

INK = (22, 26, 51)
CREAM = (255, 248, 234)
WHITE = (255, 255, 255)
YEL = (255, 214, 64)
RED = (232, 52, 72)
GREEN = (24, 170, 90)
INDIGO = (67, 56, 202)
BG = {1: (255, 112, 84), 2: (255, 196, 58), 3: (79, 70, 229), 4: (20, 170, 160), 5: (250, 98, 160), 6: (30, 160, 90), 7: (67, 56, 202)}


def font(w, s):
    return ImageFont.truetype(FONT % w, s)


def clamp(x, a=0., b=1.):
    return max(a, min(b, x))


def spring(t):
    if t <= 0:
        return 0.
    return 1 - math.exp(-7 * t) * math.cos(12 * t)


def eout(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def shade(c, f):
    return tuple(int(clamp(v * f, 0, 255)) for v in c)


# ---------- sprite kertas ----------
def rough_poly(w, h, j=4, step=26, seed=0):
    r = random.Random(seed)
    pts = []
    for x in range(0, w, step):
        pts.append((x, r.uniform(0, j)))
    for y in range(0, h, step):
        pts.append((w - r.uniform(0, j), y))
    for x in range(w, 0, -step):
        pts.append((x, h - r.uniform(0, j)))
    for y in range(h, 0, -step):
        pts.append((r.uniform(0, j), y))
    return pts


def bake(rgba, sh=(10, 14), blur=10, op=0.38):
    """Tambahkan bayangan kertas (dipanggang ke sprite)."""
    pad = blur * 2 + max(sh)
    w, h = rgba.size
    out = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    a = rgba.split()[3]
    sha = Image.new('L', out.size, 0)
    sha.paste(a, (pad + sh[0], pad + sh[1]))
    sha = sha.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op))
    out.putalpha(sha)
    top = Image.new('RGBA', out.size, (0, 0, 0, 0))
    top.paste(rgba, (pad, pad))
    return Image.alpha_composite(out, top)


def grain(img, amt=10, seed=1):
    a = np.asarray(img).astype(np.int16)
    n = np.random.default_rng(seed).normal(0, amt, a.shape[:2])[..., None]
    a[..., :3] = np.clip(a[..., :3] + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8), img.mode)


def paper(w, h, col, seed=0, j=5):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon(rough_poly(w, h, j, seed=seed), fill=col + (255,))
    return grain(im, 7, seed)


def label(text, size=86, bg=WHITE, fg=INK, padx=34, pady=18, weight='ExtraBold', seed=0, hl=None):
    f = font(weight, size)
    bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    w, h = tw + padx * 2, th + pady * 2 + 6
    im = paper(w, h, bg, seed)
    d = ImageDraw.Draw(im)
    d.text((padx - bb[0], pady - bb[1] + 2), text, font=f, fill=fg)
    return bake(im)


def multi_label(lines, size=86, bg=WHITE, fg=INK, seed=0, gap=0):
    ims = [label(t, size, bg if not isinstance(t, tuple) else t[1], fg, seed=seed + i) for i, t in enumerate(lines)]
    return ims


# ---------- cache aset ----------
_C = {}


def C(key, fn):
    if key not in _C:
        _C[key] = fn()
    return _C[key]


def bg_scene(k):
    def mk():
        col = BG[k]
        im = Image.new('RGBA', (W, H), col + (255,))
        r = random.Random(k * 11)
        # lapisan kertas sobek di atas & bawah
        for i, (y0, f) in enumerate(((-60, 1.12), (H - 520, 0.86), (H - 300, 0.78))):
            hh = 600 if i == 0 else 700
            pts = []
            for x in range(-40, W + 80, 60):
                yy = (hh - 120 + r.uniform(-40, 40)) if i == 0 else r.uniform(0, 60)
                pts.append((x, yy))
            poly = ([(-40, 0)] + pts + [(W + 80, 0)]) if i == 0 else ([(-40, hh)] + pts + [(W + 80, hh)])
            lay = Image.new('RGBA', (W + 120, hh), (0, 0, 0, 0))
            ImageDraw.Draw(lay).polygon([(x + 40, y) for x, y in poly], fill=shade(col, f) + (255,))
            lay = bake(grain(lay, 6, k + i), (0, 10 if i else -6), 14, .25)
            im.alpha_composite(lay, (-40 - 30, y0 - 30))
        im = grain(im, 9, k)
        return im.convert('RGB')
    return C('bg%d' % k, mk)


def tear_sheet(k):
    """Lembar kertas warna scene sebelumnya dengan tepi bawah sobek (untuk transisi)."""
    def mk():
        col = BG[k]
        r = random.Random(99 + k)
        hh = H + 220
        im = Image.new('RGBA', (W, hh), (0, 0, 0, 0))
        pts = [(0, 0), (W, 0)]
        for x in range(W, -40, -36):
            pts.append((x, H + 120 + r.uniform(-50, 50)))
        ImageDraw.Draw(im).polygon(pts, fill=col + (255,))
        # sisi sobek putih (serat kertas)
        edge = Image.new('RGBA', (W, hh), (0, 0, 0, 0))
        pts2 = [(x, y + 14 + r.uniform(0, 10)) for x, y in pts[2:]]
        ImageDraw.Draw(edge).polygon([(W, H)] + pts2 + [(0, H)], fill=CREAM + (255,))
        edge.alpha_composite(im)
        return bake(grain(edge, 8, k), (0, 18), 16, .35)
    return C('tear%d' % k, mk)


def phone(name):
    def mk():
        sc = Image.open(os.path.join(A, name + '.png')).convert('RGB').resize((520, 1126), Image.LANCZOS)
        fw, fh = 560, 1166
        fr = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        d = ImageDraw.Draw(fr)
        d.rounded_rectangle((0, 0, fw - 1, fh - 1), 66, fill=INK + (255,))
        m = Image.new('L', sc.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, sc.size[0] - 1, sc.size[1] - 1), 48, fill=255)
        fr.paste(sc, (20, 20), m)
        # bingkai kertas putih (foto yang digunting)
        pw, ph = fw + 44, fh + 44
        p = paper(pw, ph, WHITE, 5, 6)
        p.alpha_composite(fr, (22, 22))
        # selotip
        tp = Image.new('RGBA', (170, 54), (255, 240, 180, 190))
        tp = tp.rotate(-8, expand=True, resample=Image.BICUBIC)
        p.alpha_composite(tp, (pw // 2 - 90, -8 if False else 0))
        return bake(p, (14, 20), 16, .4)
    return C('ph' + name, mk)


def house(col, roof, seed):
    def mk():
        w, h = 190, 230
        im = Image.new('RGBA', (w, h + 90), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.polygon([(-6, 100), (w // 2, 0), (w + 6, 100)], fill=roof + (255,))
        d.polygon(rough_poly(w - 30, h - 20, 4, seed=seed), fill=col + (255,))
        body = paper(w - 30, h - 20, col, seed)
        im.alpha_composite(body, (15, 95))
        d = ImageDraw.Draw(im)
        d.rectangle((w // 2 - 26, h - 5, w // 2 + 26, h + 74), fill=shade(col, .55) + (255,))
        d.rectangle((32, 130, 72, 170), fill=CREAM + (255,))
        d.rectangle((w - 72, 130, w - 32, 170), fill=CREAM + (255,))
        return bake(grain(im, 6, seed))
    return C('house%d' % seed, mk)


def notebook():
    def mk():
        w, h = 720, 820
        p = paper(w, h, CREAM, 3, 6)
        d = ImageDraw.Draw(p)
        for y in range(120, h - 30, 62):
            d.line((40, y, w - 40, y), fill=(160, 190, 230, 255), width=3)
        d.line((110, 20, 110, h - 20), fill=(240, 120, 120, 255), width=3)
        f = font('SemiBold', 40)
        names = ['Pak Budi', 'Bu Sri', 'Pak Joko', 'Bu Dewi', 'Pak Rudi', 'Bu Yanti', 'Pak Agus', 'Bu Nur', 'Pak Dedi', 'Bu Ratna', 'Pak Irfan']
        for i, n in enumerate(names):
            d.text((130, 70 + i * 62), n, font=f, fill=(60, 70, 120, 255))
        return p
    return C('nb', mk)


def scribbles(seed=4):
    r = random.Random(seed)
    lines = []
    for i in range(11):
        y = 100 + i * 62
        kind = r.choice('vxs?')
        lines.append((kind, y, r.uniform(-1, 1)))
    return lines


def icon_check(sz, col=WHITE, bg=GREEN):
    def mk():
        im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.ellipse((0, 0, sz - 1, sz - 1), fill=bg + (255,))
        s = sz / 100
        d.line([(28 * s, 52 * s), (44 * s, 68 * s), (73 * s, 36 * s)], fill=col + (255,), width=int(11 * s), joint='curve')
        return bake(grain(im, 6, sz))
    return C('chk%d%s' % (sz, bg), mk)


def wa_bubble():
    def mk():
        w, h = 560, 300
        p = paper(w, h, WHITE, 8, 5)
        d = ImageDraw.Draw(p)
        d.ellipse((30, 28, 92, 90), fill=(22, 163, 74, 255))
        d.arc((46, 44, 76, 74), 40, 330, fill=WHITE + (255,), width=5)
        d.text((108, 36), 'Grup Warga RT 05', font=font('ExtraBold', 36), fill=(21, 128, 61, 255))
        d.text((34, 110), 'Rekap Iuran Kas', font=font('ExtraBold', 40), fill=INK)
        d.text((34, 166), 'Sudah bayar (9)', font=font('SemiBold', 34), fill=(21, 128, 61, 255))
        d.text((34, 214), 'Belum bayar (7)', font=font('Bold', 34), fill=(190, 18, 60, 255))
        return bake(p)
    return C('wa', mk)


def logo(size=150):
    def mk():
        im = paper(size, size, INDIGO, 21, 5)
        d = ImageDraw.Draw(im)
        s = size / 24
        d.line([(3 * s, 11 * s), (12 * s, 4 * s), (21 * s, 11 * s)], fill=WHITE + (255,), width=int(2.2 * s), joint='curve')
        d.line([(5.5 * s, 9.5 * s), (5.5 * s, 20 * s), (18.5 * s, 20 * s), (18.5 * s, 9.5 * s)], fill=WHITE + (255,), width=int(2.2 * s), joint='curve')
        d.line([(9 * s, 14.5 * s), (11.2 * s, 16.7 * s), (15.5 * s, 12 * s)], fill=YEL + (255,), width=int(2.4 * s), joint='curve')
        return bake(im)
    return C('logo%d' % size, mk)


def tag(text, icon):
    def mk():
        f = font('ExtraBold', 70)
        tw = f.getbbox(text)[2]
        w, h = tw + 190, 150
        p = paper(w, h, CREAM, len(text), 6)
        d = ImageDraw.Draw(p)
        d.ellipse((30, 30, 120, 120), fill=GREEN + (255,))
        if icon == 'wifi':
            for i, rr in enumerate((36, 24, 12)):
                d.arc((75 - rr, 82 - rr, 75 + rr, 82 + rr), 220, 320, fill=WHITE + (255,), width=6)
            d.line((48, 48, 104, 104), fill=WHITE + (255,), width=7)
        elif icon == 'card':
            d.rounded_rectangle((46, 52, 104, 98), 6, outline=WHITE + (255,), width=6)
            d.line((46, 66, 104, 66), fill=WHITE + (255,), width=6)
            d.line((36, 40, 114, 110), fill=WHITE + (255,), width=7)
        else:
            d.line([(52, 76), (68, 92), (98, 60)], fill=WHITE + (255,), width=10, joint='curve')
        d.text((150, 34), text, font=f, fill=INK)
        return bake(p)
    return C('tag' + text, mk)


# ---------- komposit ----------
def put(canvas, spr, cx, cy, scale=1., rot=0., alpha=1.):
    if scale <= 0.01 or alpha <= 0.01:
        return
    im = spr
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    if abs(scale - 1) > 0.002:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    a = im.split()[3]
    if alpha < 1:
        a = a.point(lambda v: int(v * alpha))
    canvas.paste(im.convert('RGB'), (int(cx - im.width / 2), int(cy - im.height / 2)), a)


def drop(t, t0, rot0=-12, dur=1.0):
    """Kertas jatuh & mendarat: kembalikan (dy, scale, rot, alpha)."""
    u = (t - t0)
    if u < 0:
        return None
    s = spring(u / dur * 1.3)
    return (1 - s) * -160, 1.0 + (1 - eout(u * 4)) * 0.25, rot0 * (1 - s), clamp(u * 8)


def slam(t, t0):
    u = t - t0
    if u < 0:
        return None
    s = spring(u * 1.25)
    return 1.9 - 0.9 * s, clamp(u * 10)


class Fx:
    def __init__(self):
        self.punch = 0.
        self.shake = 0.


def hit(fx, t, t0, amt=0.05, sh=14):
    u = t - t0
    if 0 <= u < 0.5:
        e = math.exp(-u * 9)
        fx.punch = max(fx.punch, amt * e)
        fx.shake = max(fx.shake, sh * e)


def confetti(c, t, t0, n=46, seed=3):
    u = t - t0
    if u < 0:
        return
    r = random.Random(seed)
    d = ImageDraw.Draw(c)
    cols = [YEL, RED, GREEN, (90, 200, 255), WHITE, (255, 140, 60)]
    for i in range(n):
        x0 = r.uniform(0, W)
        vy = r.uniform(380, 700)
        delay = r.uniform(0, .5)
        uu = u - delay
        if uu < 0:
            continue
        y = -60 + vy * uu + 120 * uu * uu
        if y > H + 60:
            continue
        x = x0 + math.sin(uu * r.uniform(2, 5) + i) * 50
        ang = uu * r.uniform(3, 8) + i
        w, h = r.uniform(18, 34), r.uniform(10, 20) * abs(math.cos(ang))
        ca, sa = math.cos(ang * .7), math.sin(ang * .7)
        pts = [(x + ca * dx - sa * dy, y + sa * dx + ca * dy) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
        d.polygon(pts, fill=cols[i % len(cols)])


def ring(c, t, t0, cx, cy, col=WHITE, maxr=420, w=14):
    u = t - t0
    if not 0 <= u < 0.5:
        return
    r = maxr * eout(u * 2)
    a = 1 - u * 2
    ov = Image.new('L', (W, H), 0)
    ImageDraw.Draw(ov).ellipse((cx - r, cy - r, cx + r, cy + r), outline=int(255 * a), width=w)
    c.paste(col, (0, 0), ov)


# ---------- scene ----------
def scene_draw(k, t, s, c, fx):
    b = s['beats']
    if k == 1:
        cols = [((255, 214, 64), (60, 80, 200)), ((90, 200, 255), (232, 52, 72)), (CREAM, (30, 160, 90)), ((255, 160, 200), (60, 80, 200)), ((255, 214, 64), (232, 52, 72))]
        for i, (cc, rf) in enumerate(cols):
            u = t - (b[0] + i * .07)
            if u < 0:
                continue
            y = 1330 + (1 - spring(u * 1.2)) * 420
            put(c, house(cc, rf, 10 + i), 115 + i * 212, y, 1.0, (i % 2 * 2 - 1) * 2)
        d1 = drop(t, b[0])
        if d1:
            put(c, C('l1a', lambda: label('JADI BENDAHARA RT', 82)), 540, 360 + d1[0], d1[1], -3 + d1[2], d1[3])
        sl = slam(t, b[1])
        if sl:
            hit(fx, t, b[1], .06, 18)
            ring(c, t, b[1], 540, 560, WHITE)
            put(c, C('l1b', lambda: label('CAPEK, ANJIR!', 124, YEL, INK)), 540, 560, sl[0], 4, sl[1])
        d3 = drop(t, b[2], 10)
        if d3:
            put(c, C('l1c', lambda: label('nagih iuran satu-satu...', 64, INK, WHITE, weight='Bold')), 540, 770 + d3[0], d3[1], 2 + d3[2], d3[3])
            for i in range(4):
                u = t - (b[2] + i * .32)
                if u >= 0:
                    sp = slam(t, b[2] + i * .32)
                    put(c, C('tok', lambda: label('TOK! TOK!', 44, WHITE, RED)), 115 + (i + (i > 1)) * 212, 1090 + (i % 2) * 40, sp[0] * .9, (i % 2 * 2 - 1) * 10, sp[1])
    elif k == 2:
        nb = notebook()
        d0 = drop(t, s['beats'][0] - .2, 8, 1.2)
        if d0:
            nbc = nb.copy()
            dd = ImageDraw.Draw(nbc)
            prog = clamp((t - b[2]) / 1.3)
            for i, (kind, y, j) in enumerate(scribbles()):
                if prog * 11 <= i:
                    break
                col = (220, 40, 60, 255) if kind in 'xs?' else (20, 140, 70, 255)
                x0 = 420
                if kind == 'v':
                    dd.line([(x0, y + 22), (x0 + 22, y + 44), (x0 + 60, y)], fill=col, width=7)
                elif kind == 'x':
                    dd.line([(x0, y), (x0 + 50, y + 46)], fill=col, width=7)
                    dd.line([(x0 + 50, y), (x0, y + 46)], fill=col, width=7)
                elif kind == 's':
                    dd.line([(120, y + 26), (380, y + 18 + j * 8)], fill=col, width=8)
                    dd.line([(x0 - 10, y + 10), (x0 + 200, y + 30 + j * 10), (x0 + 40, y + 40)], fill=col, width=6)
                else:
                    dd.text((x0, y - 8), '???', font=font('Black', 50), fill=col)
            put(c, bake(nbc), 540, 1120 + d0[0], d0[1], -4 + d0[2], d0[3])
        for i, (txt, yy, bi, rot) in enumerate((('SIAPA UDAH BAYAR?', 330, 0, -3), ('SIAPA BELUM?', 490, 1, 3))):
            dd_ = drop(t, b[bi], -10 if i else 10)
            if dd_:
                put(c, C('l2%d' % i, lambda txt=txt, i=i: label(txt, 84 if i == 0 else 100, WHITE if i == 0 else INK, INK if i == 0 else YEL)), 540, yy + dd_[0], dd_[1], rot + dd_[2], dd_[3])
        # tanda tanya beterbangan
        for i in range(5):
            u = t - (b[0] + .1 + i * .18)
            if u < 0:
                continue
            x = [130, 950, 180, 900, 540][i]
            y = [700, 640, 1580, 1560, 1700][i] - u * 30
            put(c, C('q%d' % (i % 2), lambda i=i: label('?', 110, [INK, WHITE][i % 2], [YEL, RED][i % 2], 26, 6)), x, y, spring(u * 1.3), math.sin(u * 3 + i) * 15)
        sl = slam(t, b[3])
        if sl:
            hit(fx, t, b[3], .07, 22)
            put(c, C('pusing', lambda: label('PUSING!', 150, RED, WHITE)), 560, 1180, sl[0], -8, sl[1])
    elif k in (3, 4):
        if k == 3:
            d0 = drop(t, b[0])
            if d0:
                put(c, C('l3a', lambda: label('MAKANYA PAKAI...', 76)), 540, 300 + d0[0], d0[1], -2 + d0[2], d0[3])
            sl = slam(t, b[1])
            if sl:
                hit(fx, t, b[1], .05, 12)
                ring(c, t, b[1], 540, 470, YEL)
                put(c, logo(120), 190, 470, sl[0], -6, sl[1])
                put(c, C('lw', lambda: label('KasWarga', 120, YEL, INK)), 600, 470, sl[0], 3, sl[1])
            u = t - (b[1] + .05)
            if u >= 0:
                y = 1180 + (1 - spring(u * 1.1)) * 1100
                ph = 'beranda' if t < b[2] else 'iuran-list'
                put(c, phone(ph), 540, y, .92, -3 + (1 - spring(u)) * 10)
            sl2 = slam(t, b[2])
            if sl2:
                hit(fx, t, b[2], .05, 14)
                put(c, icon_check(230), 860, 980, sl2[0], -10, sl2[1])
                put(c, C('l3c', lambda: label('CENTANG SEKALI', 74, WHITE, INK)), 380, 640, sl2[0] * .9 + .1, -4, sl2[1])
            sl3 = slam(t, b[3])
            if sl3:
                put(c, C('l3d', lambda: label('LANGSUNG LUNAS!', 92, GREEN, WHITE)), 540, 1600, sl3[0], 3, sl3[1])
        else:
            d0 = drop(t, b[0] - .1)
            if d0:
                put(c, C('l4a', lambda: label('YANG BELUM BAYAR?', 84)), 540, 330 + d0[0], d0[1], 3 + d0[2], d0[3])
            u = t - b[0]
            if u >= -.2:
                y = 1150 + (1 - spring((u + .2) * 1.1)) * 1100
                if t < b[2]:
                    put(c, phone('iuran-belum'), 540, y, .9, 2)
                else:
                    uu = t - b[2]
                    put(c, phone('wa-msg'), 540 - (1 - spring(uu * 1.2)) * 900, 1150, .9, -2 + (1 - spring(uu)) * 8)
            sl = slam(t, b[1])
            if sl and t < b[2]:
                hit(fx, t, b[1], .05, 14)
                # lingkaran spidol merah di daftar "Belum"
                prog = clamp((t - b[1]) / .45)
                ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(ov).arc((290, 760, 890, 1450), -100, -100 + 380 * prog, fill=RED + (255,), width=16)
                c.paste(ov.convert('RGB'), (0, 0), ov.split()[3])
                put(c, C('l4b', lambda: label('LANGSUNG KETAHUAN!', 76, RED, WHITE)), 540, 520, min(sl[0], 1.4), -3, sl[1])
            sl2 = slam(t, b[2] + .25)
            if sl2:
                put(c, C('l4c', lambda: label('KIRIM KE GRUP WA', 88, (22, 163, 74), WHITE)), 540, 520, sl2[0], -3, sl2[1])
                put(c, wa_bubble(), 640, 1560 - (1 - spring((t - b[2] - .25) * 1.2)) * 200, sl2[0] * .5 + .5, 4, sl2[1])
    elif k == 5:
        d0 = drop(t, b[0])
        if d0:
            put(c, C('l5a', lambda: label('ARISAN JUGA BISA!', 88)), 540, 330 + d0[0], d0[1], -3 + d0[2], d0[3])
        names = ['Bu Siti', 'Bu Dewi', 'Bu Yanti', 'Bu Nur', 'Bu Ratna', 'Bu Wati', 'Bu Lilis', 'Bu Tuti']
        u = t - b[0] - .1
        if u >= 0:
            # kartu kocokan
            cur = 'Siap dikocok'
            if t >= b[1]:
                tt, gap, i = b[1], .06, 0
                while tt + gap < t and tt < b[2]:
                    tt += gap
                    gap *= 1.09
                    i += 1
                cur = names[(i * 3) % len(names)] if t < b[2] else 'Bu Erna'
            win = t >= b[2]
            key = 'drum' + cur + str(win)

            def mk(cur=cur, win=win):
                p = paper(820, 380, YEL if win else CREAM, 31, 6)
                d = ImageDraw.Draw(p)
                d.text((410, 70), 'PEMENANG' if win else 'KOCOKAN ARISAN', font=font('Bold', 38), fill=(140, 90, 20, 255) if win else (120, 120, 150, 255), anchor='mm')
                f = font('Black', 110)
                d.text((410, 210), cur, font=f, fill=RED if win else INK, anchor='mm')
                return bake(p)
            jit = (math.sin(t * 90) * 6) if (b[1] <= t < b[2]) else 0
            sc = 1.0 if not win else spring((t - b[2]) * 1.4) * .15 + .95
            put(c, C(key, mk), 540 + jit, 1050 + (1 - spring(u * 1.2)) * 900, sc, -3)
        sl = slam(t, b[1])
        if sl:
            put(c, C('l5b', lambda: label('KOCOK LANGSUNG DI HP', 70, INK, YEL)), 540, 520, sl[0] * .6 + .4, 3, sl[1])
        if t >= b[2]:
            hit(fx, t, b[2], .07, 20)
            ring(c, t, b[2], 540, 1050, YEL, 600)
            sl2 = slam(t, b[2] + .35)
            if sl2:
                put(c, C('l5c', lambda: label('ANJAY, SERU!', 130, RED, WHITE)), 540, 1450, sl2[0], -6, sl2[1])
            confetti(c, t, b[2])
    elif k == 6:
        items = [('Tanpa kuota', 'wifi'), ('Tanpa langganan', 'card'), ('Sekali bayar', 'ok')]
        for i, (txt, ic) in enumerate(items):
            sl = slam(t, b[i])
            if sl:
                hit(fx, t, b[i], .04, 12)
                put(c, tag(txt, ic), 540 + (i - 1) * 30, 560 + i * 250, sl[0], (-1) ** i * 4, sl[1])
        sl = slam(t, b[3])
        if sl:
            hit(fx, t, b[3], .06, 16)
            put(c, C('l6', lambda: label('PAKAI TERUS!', 130, YEL, INK)), 540, 1360, sl[0], -5, sl[1])
        d0 = drop(t, b[0] - .25)
        if d0:
            put(c, C('l6a', lambda: label('100% OFFLINE', 70, INK, WHITE)), 540, 330 + d0[0], d0[1], 3 + d0[2], d0[3])
    elif k == 7:
        u = t - b[0]
        sl = slam(t, b[0] - .1)
        if sl:
            put(c, logo(170), 540, 420, sl[0], -4, sl[1])
            put(c, C('l7n', lambda: label('KasWarga', 110, YEL, INK)), 540, 610, sl[0] * .5 + .5, 3, sl[1])
        d0 = drop(t, b[0] + .1)
        if d0:
            put(c, C('l7a', lambda: label('Kas RT, Iuran & Arisan', 60, WHITE, INK, weight='Bold')), 540, 760 + d0[0], d0[1], -2 + d0[2], d0[3])
        sl2 = slam(t, b[1])
        if sl2:
            hit(fx, t, b[1], .06, 16)
            ring(c, t, b[1], 540, 1040, YEL, 520)
            put(c, C('l7b', lambda: label('CEK LINK DI BIO', 118, YEL, INK)), 540, 1040, sl2[0], -4, sl2[1])
            bob = math.sin((t - b[1]) * 7) * 18
            # panah ke atas
            ar = C('arrow', lambda: bake(_arrow()))
            put(c, ar, 540, 1250 + bob, sl2[0] * .5 + .5, 0, sl2[1])
            sl3 = slam(t, b[1] + .6)
            if sl3:
                put(c, C('l7c', lambda: label('lynk.id/ibam2178', 80, WHITE, INDIGO)), 540, 1440, sl3[0], 2, sl3[1])
        confetti(c, t, b[1] + .3, 36, 8)


def _arrow():
    im = Image.new('RGBA', (160, 170), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(80, 0), (160, 80), (110, 80), (110, 170), (50, 170), (50, 80), (0, 80)], fill=WHITE + (255,))
    return grain(im, 6, 2)


def frame(i):
    t = i / FPS
    s = next(x for x in SC if x['start'] <= t < x['start'] + x['dur'] + 1e-6) if t < TOTAL else SC[-1]
    k = s['k']
    lt = t - s['start']
    c = bg_scene(k).copy()
    fx = Fx()
    scene_draw(k, lt, s, c, fx)
    # watermark
    put(c, C('wm', lambda: label('@klisacom', 34, INK, WHITE, 18, 8, 'Bold')), 160, 175, 1, -2, .9)
    # kamera
    if fx.punch > 0.001 or fx.shake > 0.5:
        z = 1 + fx.punch
        sx = math.sin(t * 83) * fx.shake
        sy = math.cos(t * 71) * fx.shake
        cw, ch = W / z, H / z
        x0 = clamp((W - cw) / 2 + sx, 0, W - cw)
        y0 = clamp((H - ch) / 2 + sy, 0, H - ch)
        c = c.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    # transisi: lembar kertas scene sebelumnya tersobek ke atas
    if k > 1 and lt < .42:
        p = eout(lt / .42)
        sh = tear_sheet(k - 1)
        y = -p * (sh.height + 40)
        c.paste(sh.convert('RGB'), (int(-(sh.width - W) / 2), int(y) - 30), sh.split()[3])
    return c


def render_raw(i):
    return frame(i).tobytes()


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'stills':
        for a in sys.argv[2:]:
            frame(int(float(a) * FPS)).save(os.path.join(B, 'still_%s.png' % a))
        print('ok')
    elif mode == 'full':
        n = int(TOTAL * FPS)
        out = os.path.join(B, 'video_noaudio.mp4')
        p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS),
                              '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        with Pool(4) as pool:
            for j, buf in enumerate(pool.imap(render_raw, range(n), chunksize=4)):
                p.stdin.write(buf)
                if j % 150 == 0:
                    print('frame', j, '/', n, flush=True)
        p.stdin.close()
        p.wait()
        final = os.path.join(HERE, 'KasWarga-Promo-TikTok.mp4')
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', out, '-i', os.path.join(B, 'mix.wav'), '-c:v', 'copy', '-c:a', 'aac', '-ar', '44100',
                        '-b:a', '192k', '-shortest', '-movflags', '+faststart', final], check=True)
        print('done', final)
