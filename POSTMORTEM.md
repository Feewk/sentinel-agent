# Post-Mortem — Sentinel Agent Build (2026-11-23, satu hari, M0–M4 + submit)

Hasil akhir: BUIDL 51680 tersubmit 12 hari sebelum deadline, Beta #102 LOLOS
DENGAN CATATAN, 4/4 kontrak terverifikasi Sourcify (exact_match).

## Yang berjalan baik
- Rencana riset Epsilon (REACTIVE-BUILD-PLAN) akurat: urutan deploy terkunci,
  payload address(0), larangan >5 ETH ke faucet — nol kejutan arsitektur.
- Bukti berlapis: hash di chain → README → field organizer → verifikasi Beta
  independen (recompute rationaleHash) → Sourcify. Juri bisa verifikasi
  tanpa percaya kata kami.
- Protokol Dorong Vonis bekerja: vonis Beta #102 tiba sebagai handoff aktif,
  catatan ditutup di hari yang sama.

## Celah nyata → aturan build berikutnya
1. **Faucet adalah titik kritis tersembunyi.** 5 faucet gagal di Cloudflare
   Turnstile dari browser cloud (±25 percobaan); yang tembus justru klaim
   user dari browser sendiri (0,36 ETH). ATURAN: untuk build berikutnya,
   petakan jalur faucet SEBELUM milestone nol — utamakan faucet tanpa
   Turnstile (QuickNode/GetBlock dicoba sbg rute baru oleh koordinator),
   siapkan opsi klaim-user sebagai rencana A paralel, bukan fallback panik.
   Jaga buffer: sisa 0,09 ETH di akhir build itu terlalu tipis.
2. **Timeout kartu approval membunuh momentum dua kali** (cek RPC pertama
   13:48; verifikasi Sourcify 15:36 — retry baru jalan 16:31 setelah user
   gas). ATURAN: batch-kan aksi yang butuh approval dalam satu jendela saat
   user sedang aktif di chat; jangan sebar approval di jam user sepi.
3. **Kredensial konektor tidak menembus sandbox side chat.** Konektor Gemini
   mengembalikan 403 "not available to the sandbox" dari chat Theta —
   backend gemini tak teruji live, run produksi memakai backend operator.
   ATURAN: uji jalur kredensial di MENIT PERTAMA build (spike kecil), bukan
   saat integrasi; selalu desain decider/provider sebagai antarmuka pluggable
   dengan backend operator yang jujur + tercatat, supaya satu jalur buntu
   tidak menghentikan build. Utang "satu run live gemini" dicatat eksplisit
   di STATUS + vonis Beta, bukan disembunyikan.
4. **Form platform punya kejutan di menit terakhir** (DoraHacks: kontak
   wajib, URL video github.com/raw ditolak sebagai "link GitHub", field
   hash dibatasi 960 karakter, jawaban organizer tak bisa dilihat/diubah
   pasca-submit). ATURAN: recon form submission di HARI PERTAMA event
   (buka form, catat semua field wajib + batas karakter), bukan di hari
   submit; siapkan URL video dalam format yang diterima form (raw host
   langsung / YouTube) sejak awal.
5. **RPC publik goyah di tengah run** (poll agen putus beberapa kali; satu
   entri log.jsonl hilang dan di-backfill dari chain). ATURAN: chain adalah
   sumber kebenaran — log lokal selalu bisa direkonstruksi dari event;
   untuk run panjang pakai ≥2 endpoint RPC bergantian.
6. **Kejujuran adalah fitur, bukan beban.** Disclosure backend operator di
   README + deskripsi BUIDL diterima Beta sebagai bukti sah dan memperkuat
   (bukan melemahkan) penilaian Craft. ATURAN: tuliskan keterbatasan apa
   adanya di dokumen utama juri sejak draf pertama.

## Angka build
- Durasi efektif: ±2,5 jam kerja agen (13:47 serah terima → 16:00 submit)
- Biaya testnet: ±0,27 ETH Sepolia + ±4,25 lREACT terpakai dari modal awal
- Artefak: 4 kontrak terverifikasi · 12 hash bukti · video 2m50s · repo
  publik 6 commit di hari yang sama
