# Hasil Pengujian Holdout — Penilaian Kode Otomatis berbasis LLM

**Soal:** H1 "Cycle Entry Point" (cari entry-point dari cycle pada linked list) —
kuis *Praktikum 10* (Olympia). 20 submisi mahasiswa, dipilih merata sepanjang
rentang skor auto-grader.
**Konfigurasi:** skenario **S8 (all-on)** — rubrik terstruktur + chain-of-thought +
few-shot; model **Gemini 2.5 Flash**, temperature **0** (deterministik), 1 replikat.
**Referensi (ground truth):** penilaian manual **buta** (independen dari skor
Gemini/Olympia) memakai rubrik 4-kriteria (Correctness/45, Efficiency/25,
Approach/15, Code Quality/15).

> **TL;DR.** Pada data holdout yang belum pernah dipakai saat pengembangan, penilaian
> LLM mencapai **agreement "good"** dengan penilai manusia (**ICC(A,1) = 0,79**,
> Pearson 0,80, MAE 14,1/100) dan **generalisasi baik** — bahkan sedikit lebih tinggi
> dari dev set. Selisih terkonsentrasi pada **satu kriteria (Correctness)** dan
> **satu failure-mode yang terkarakterisasi**: LLM memverifikasi lewat satu contoh
> yang dipilih sendiri sehingga bug yang bergantung-input (mis. infinite loop) lolos.

---

## 1. Hasil utama

Ground truth = penilaian manusia (re-grade buta), n = 20, parse rate 100%.

| Pasangan | MAE (/100) | Pearson |
|---|---|---|
| **LLM vs manusia** | **14,10** | **0,798** |
| Olympia (auto-grader) vs manusia | 14,85 | 0,947 |
| LLM vs Olympia | 17,65 | 0,781 |

- **ICC(A,1) LLM↔manusia = 0,789** (95% CI [0,550 – 0,910]) — kategori *good agreement*
  (Koo & Li, 2016: 0,75–0,90).
- LLM **sedikit lebih dekat** ke manusia dibanding auto-grader Olympia dalam MAE
  (14,10 vs 14,85), tetapi **kalah di korelasi** (0,798 vs 0,947): Olympia
  mengurutkan submisi lebih konsisten karena *menjalankan* kode, namun punya offset
  absolut besar (memberi 0 pada kode non-kompilasi/TLE meski ada partial merit).

## 2. Generalisasi: dev vs holdout

Konfigurasi juara dipilih pada dev set (`dataset/`), lalu diuji sekali di holdout.

| Metrik | Dev (`dataset/`, n=142) | **Holdout (n=20)** |
|---|---|---|
| ICC(A,1) | 0,687 | **0,789** |
| Pearson | 0,724 | **0,798** |
| MAE | 10,97 | 14,10 |

Agreement (ICC/Pearson) **tidak turun** di holdout — malah naik — menunjukkan pemilihan
konfigurasi tidak overfit ke dev set. MAE sedikit lebih tinggi karena n kecil membuat
beberapa outlier mendominasi (lihat §4).

## 3. Rincian per kriteria

Seluruh ketidaksepakatan terkonsentrasi di **Correctness**; tiga kriteria lain
menunjukkan agreement sangat baik.

| Kriteria | MAE |
|---|---|
| Efficiency | 2,00 |
| Code Quality | 2,40 |
| Approach | 2,75 |
| **Correctness** | **9,25** |

Correctness adalah kriteria yang menuntut penalaran atas *perilaku eksekusi* kode —
justru titik terlemah LLM (lihat §5).

## 4. Distribusi selisih

| |selisih total| | jumlah |
|---|---|
| ≤ 5 poin | 7/20 (35%) |
| ≤ 10 poin | 11/20 (55%) |
| ≤ 15 poin | 12/20 (60%) |
| ≤ 20 poin | 13/20 (65%) |

**Median selisih = 9,0 poin** — jauh di bawah MAE 14,1, artinya MAE ditarik naik oleh
sedikit outlier. Tanpa outlier terbesar (cycle_01), **MAE = 12,16**.

## 5. Analisis per-submisi

| Submisi | Manusia | Olympia | LLM | \|LLM−man\| | \|Oly−man\| |
|---|--:|--:|--:|--:|--:|
| cycle_03 | 12 | 0 | 8 | 4 | 12 |
| cycle_06 | 12 | 10 | 16 | 4 | 2 |
| cycle_01 | 17 | 0 | 68 | **51** | 17 |
| cycle_02 | 17 | 0 | 8 | 9 | 17 |
| cycle_04 | 17 | 0 | 40 | **23** | 17 |
| cycle_07 | 22 | 10 | 3 | 19 | 12 |
| cycle_05 | 26 | 10 | 17 | 9 | 16 |
| cycle_08 | 26 | 10 | 3 | **23** | 16 |
| cycle_09 | 35 | 10 | 12 | **23** | 25 |
| cycle_10 | 35 | 10 | 8 | **27** | 25 |
| cycle_17 | 58 | 90 | 35 | **23** | 32 |
| cycle_11 | 59 | 50 | 67 | 8 | 9 |
| cycle_12 | 63 | 60 | 35 | **28** | 3 |
| cycle_13 | 63 | 60 | 49 | 14 | 3 |
| cycle_14 | 63 | 80 | 59 | 4 | 17 |
| cycle_16 | 63 | 90 | 72 | 9 | 27 |
| cycle_15 | 76 | 90 | 76 | 0 | 14 |
| cycle_18 | 76 | 90 | 76 | 0 | 14 |
| cycle_19 | 81 | 100 | 77 | 4 | 19 |
| cycle_20 | 100 | 100 | 100 | 0 | 0 |

Submisi "bersih" (cycle_15/18/19/20) dinilai nyaris identik; selisih menumpuk pada
kode *partial-credit menengah* dengan bug alur-kontrol.

## 6. Temuan inti — failure-mode LLM-grader

**Outlier terbesar (cycle_01: manusia 17, LLM 68, selisih 51)** merangkum kelemahan
utama. Kode memakai pendekatan *visited-array*, tetapi `++idx` dan `Q = next(Q)`
diletakkan **di dalam inner loop** sehingga bookkeeping rusak dan pada list bercycle
kode **tidak berhenti** (`idx` membengkak → overflow `list[100000]`).

Penilai manusia memberi **Correctness 0** (algoritma tak dapat ditelusuri ke solusi
benar — infinite loop). LLM memberi **Correctness 45/45**. Analisis jejak `<THINKING>`
Gemini menunjukkan mekanismenya:

1. LLM **mengikuti instruksi trace** (CoT stage 4) dan menelusuri contoh `A→B→C→B`.
2. Pada input mungil itu, kode buggy **kebetulan mengembalikan jawaban benar (B)**;
   bug baru menggigit pada input lain (list lebih panjang / entry tak cepat ketemu).
3. LLM menyimpulkan *"It does work for A→B→C→B"* → Correctness penuh.

> **Karakterisasi:** LLM-grader memverifikasi kebenaran lewat **satu contoh yang
> dipilih sendiri dan non-adversarial**, sehingga bug yang *bergantung-input* lolos.
> Ia tidak bernalar generik atas struktur kontrol ("idx naik di inner loop → rusak")
> seperti manusia. Pola serupa terlihat pada cycle_04 ("works for cyclic lists",
> padahal crash di acyclic) dan cycle_06 (trace satu kasus "berhasil", padahal hang
> bila entry ≠ head).

Kontras dengan **Olympia** yang *menjalankan* kode: Olympia memberi cycle_01 = 0
(cocok dengan manusia). Inilah dikotomi **membaca vs menjalankan** kode — auto-grader
berbasis eksekusi menangkap bug bergantung-input yang lolos dari pembaca berbasis LLM.

## 7. Keterbatasan & ancaman validitas

- **Provenance referensi.** Label manusia versi awal dibuat dengan bantuan AI; untuk
  eksperimen ini seluruh 20 submisi **dinilai ulang secara buta** (independen dari skor
  model) memakai rubrik. Penilai tunggal (penulis) — idealnya ≥2 penilai independen
  (asisten/dosen) untuk sekaligus mengukur reliabilitas antar-manusia.
- **Kebutaan parsial.** Re-grade final dilakukan setelah penulis pernah melihat sebagian
  keluaran Gemini; upaya mitigasi: penilaian mengacu **hanya** pada rubrik + kode, dan
  independensi terlihat dari banyaknya submisi yang berbeda jauh dari skor LLM.
- **Rubrik.** Wording rubrik Correctness sempat disempurnakan lalu **dikembalikan ke
  versi asli** agar tidak menyetel terhadap holdout; band 0/45 dinyatakan berdasar
  konsep algoritma (kompilasi bukan faktor eksplisit). Pengembangan rubrik lebih lanjut
  sebaiknya di dev set.
- **n kecil (20)** membuat CI lebar ([0,55–0,91]) dan MAE sensitif terhadap outlier.
- **Satu soal (H1).** Generalisasi ke tipe soal lain belum diuji.

## 8. Arah lanjutan (future work)

1. **Verifikasi multi-input / adversarial** di prompt: alih-alih "at least one
   representative example", minta LLM menelusuri **beberapa** input (list panjang,
   entry bukan-head) dan mengecek terminasi & batas array — dikembangkan di dev set.
2. **Pipeline hibrida eksekusi + LLM:** jalankan kode terhadap test-case (seperti
   Olympia) untuk menangkap bug bergantung-input, lalu gunakan LLM untuk penilaian
   kualitatif (Approach, Code Quality) dan umpan balik naratif.
3. **Penilai manusia jamak** untuk baseline reliabilitas antar-manusia sebagai batas
   atas yang realistis bagi agreement LLM.

---

*Angka dihitung dari `experiments/holdout/results/phase1.jsonl` (Gemini 2.5 Flash,
temp 0, 20/20 parse valid) terhadap `submissions.json` (human_score re-grade buta).
Reproduksi: `set -a && source .env.experiment && set +a && uv run python -m
experiments.runner phase1`. Median latency 23,7 s/penilaian; median 4.937 token keluaran.*
