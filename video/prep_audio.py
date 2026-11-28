"""Rapikan voiceover per scene (buang diam awal/akhir, percepat 1.10x) + tulis waktu beat.

Waktu beat diambil dari analisis jeda + transkrip bertimestamp (dalam detik audio asli),
lalu dikonversi ke waktu setelah dipercepat. Hasil: build/vo_sN.wav dan build/beats.json.
"""
import json
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, 'build')
os.makedirs(B, exist_ok=True)
SR = 24000
TEMPO = 1.10

# (awal bicara, akhir bicara, [awal tiap beat]) dalam detik audio asli
SCENES = {
    1: (0.03, 5.14, [0.03, 1.95, 3.11]),        # Jadi bendahara RT | capek, anjir | Tiap bulan nagih iuran satu-satu
    2: (0.02, 5.20, [0.02, 1.60, 2.78, 4.40]),  # Siapa udah bayar? | Siapa belum? | Buku tulis penuh coretan | bikin pusing
    3: (0.00, 4.90, [0.00, 1.65, 2.96, 3.94]),  # Makanya pakai | KasWarga | Centang sekali | langsung lunas
    4: (0.00, 4.49, [0.00, 1.04, 2.67]),        # Yang belum bayar? | Langsung ketahuan | Rekap kirim ke grup WA
    5: (0.00, 5.65, [0.00, 1.48, 3.73]),        # Arisan juga bisa | Kocok di HP | Anjay seru banget
    6: (0.02, 4.44, [0.02, 1.31, 2.75, 3.84]),  # Nggak pakai kuota | langganan | Sekali bayar | pakai terus
    7: (0.01, 2.85, [0.01, 1.37]),              # Buat para bendahara | cek link di bio sekarang
}

res = {}
for k, (a, b, beats) in SCENES.items():
    out = os.path.join(B, 'vo_s%d.wav' % k)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', os.path.join(HERE, 'vo', 's%d.wav' % k),
                    '-af', 'atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,atempo=%.2f' % (a, b + 0.06, TEMPO), '-ar', str(SR), out],
                   check=True)
    with wave.open(out) as w:
        dur = w.getnframes() / SR
    res[k] = {'beats': [round((t - a) / TEMPO, 3) for t in beats], 'dur': round(dur, 3)}
    print(k, res[k])
json.dump(res, open(os.path.join(B, 'beats.json'), 'w'), indent=1)
