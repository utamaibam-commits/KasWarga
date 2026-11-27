"""Bangun versi link (web app / PWA) KasWarga ke folder docs/ untuk GitHub Pages.

Jalankan dari root repo:  python3 scripts/build-web.py
Sumber tetap satu: app/KasWarga.html. Ikon dibuat dengan Pillow.
"""
import json
import os

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(ROOT, 'app', 'KasWarga.html')
OUT = os.path.join(ROOT, 'docs')
VERSION = 'kaswarga-v1.0'
INDIGO = (67, 56, 202)
GOLD = (251, 191, 36)

os.makedirs(os.path.join(OUT, 'icons'), exist_ok=True)


def icon(size, pad=0.0, rounded=False):
    S = size * 4
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if rounded:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=S // 4, fill=INDIGO)
    else:
        d.rectangle([0, 0, S, S], fill=INDIGO)
    k = S / 64
    c = S / 2
    sc = 1 - pad

    def P(pts):
        return [(c + (x * k - c) * sc, c + (y * k - c) * sc) for x, y in pts]

    w = int(5 * k * sc)
    for pts, col in (([(14, 30), (32, 15), (50, 30)], 'white'), ([(20, 28), (20, 48), (44, 48), (44, 28)], 'white'),
                     ([(26, 38), (31, 43), (39, 34)], GOLD)):
        pp = P(pts)
        d.line(pp, fill=col, width=w, joint='curve')
        for p in (pp[0], pp[-1]):
            d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)
    return im.resize((size, size), Image.LANCZOS)


icon(192).save(os.path.join(OUT, 'icons', 'icon-192.png'))
icon(512).save(os.path.join(OUT, 'icons', 'icon-512.png'))
icon(512, pad=0.2).save(os.path.join(OUT, 'icons', 'maskable-512.png'))
icon(180).convert('RGB').save(os.path.join(OUT, 'icons', 'apple-touch-icon.png'))
icon(64, rounded=True).save(os.path.join(OUT, 'icons', 'favicon-64.png'))

html = open(SRC, encoding='utf-8').read()
start = html.index('<link rel="apple-touch-icon"')
end = html.index('>', start) + 1
html = html[:start] + (
    '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n'
    '<link rel="manifest" href="manifest.webmanifest">'
) + html[end:]
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)

manifest = {
    'name': 'KasWarga — Kas RT, Iuran & Arisan',
    'short_name': 'KasWarga',
    'description': 'Catat iuran warga, kas RT, dan arisan. Jalan offline, data hanya di perangkat Anda.',
    'lang': 'id',
    'start_url': './',
    'scope': './',
    'display': 'standalone',
    'orientation': 'any',
    'background_color': '#4338ca',
    'theme_color': '#4338ca',
    'icons': [
        {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
        {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
        {'src': 'icons/maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
    ],
}
json.dump(manifest, open(os.path.join(OUT, 'manifest.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

sw = """// Service worker KasWarga: simpan aplikasi di perangkat agar jalan tanpa internet.
const CACHE = '%s';
const FILES = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png',
  './icons/maskable-512.png', './icons/apple-touch-icon.png', './icons/favicon-64.png'];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});
// Cache dulu (instan & offline), lalu perbarui diam-diam bila ada internet.
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.open(CACHE).then(async (c) => {
    const hit = await c.match(req, {ignoreSearch: true});
    const net = fetch(req).then((res) => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => null);
    if (hit) { e.waitUntil(net); return hit; }
    const res = await net;
    return res || (req.mode === 'navigate' ? c.match('./index.html') : Response.error());
  }));
});
""" % VERSION
open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8').write(sw)
open(os.path.join(OUT, '.nojekyll'), 'w').close()
print('ok -> docs/')
