# KasWarga — Kas RT, Iuran & Arisan

Web app 1 file untuk bendahara RT/RW, arisan, kas kelas, dan komunitas. Jalan **100% offline**, data tersimpan di perangkat pengguna (localStorage), tanpa akun dan tanpa server.

## Fitur
- **Iuran**: bulanan & sekali bayar, centang lunas sekali ketuk, bayar sebagian, bayar beberapa bulan sekaligus, tandai semua lunas.
- **Siapa belum bayar**: daftar otomatis per bulan + tunggakan per warga.
- **Kirim ke WhatsApp**: rekap sudah/belum bayar ke grup, pengingat personal, bukti bayar, laporan kas, hasil arisan (teks bisa diedit dulu).
- **Arisan**: setoran per putaran, kocok pemenang acak (atau pilih manual), riwayat pemenang, mulai periode baru.
- **Buku Kas**: pemasukan lain & pengeluaran per kategori; iuran otomatis masuk kas.
- **Laporan**: bulanan & tahunan, rekap per bulan, tabel status iuran 12 bulan, cetak / simpan PDF.
- **Data Warga**: tambah banyak sekaligus (tempel dari grup WA), urut nama/alamat, warga nonaktif.
- Backup/restore JSON, data contoh, tema gelap, tab Bantuan (Android, iPhone, Laptop).

## Struktur
- `app/KasWarga.html` — sumber utama (satu file, bisa juga dibuka langsung).
- `scripts/build-web.py` — membangun versi PWA ke `docs/` (butuh Pillow).
- `docs/` — yang disajikan GitHub Pages (index, manifest, service worker, ikon).

## Build & terbitkan
```bash
python3 scripts/build-web.py
```
GitHub Pages: Settings → Pages → Deploy from a branch → `main` / `/docs`.
Link aplikasi: https://utamaibam-commits.github.io/KasWarga/
