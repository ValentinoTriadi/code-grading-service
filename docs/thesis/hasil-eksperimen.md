# Hasil Eksperimen

*Draft subbab Hasil & Pembahasan — Run 13 (final). Mencakup seluruh trajektori iteratif (Run 1–11 + Phase 2 re-run), analisis ANOVA, dan pengukuran konsistensi ICC.*

---

## Dataset

Eksperimen dijalankan pada dataset yang terdiri dari **144 submisi kode mahasiswa** untuk **6 soal pemrograman** dalam berbagai bahasa, beserta skor manusia (*ground truth*) yang ditetapkan oleh asisten pengajar pada skala 0–100.

**Tabel 1. Dataset soal**

| Soal | Bahasa | Topik | Tingkat | n submisi |
|------|--------|-------|---------|-----------|
| P1 | Python | Sum Array (termasuk kasus sudut) | Mudah | 28 |
| P2 | Java | Palindrome Check (normalize + compare) | Mudah–sedang | 20 |
| P3 | TypeScript | LRU Cache dengan O(1) eviction | Sedang | 25 |
| P4 | C++ | Dijkstra SSSP dengan `long long` | Sedang–sulit | 25 |
| P5 | Java | Binary Search Tree (insert/delete/inorder) | Sulit | 23 |
| P6 | Go | Concurrent Worker Pool (*concurrency*) | Sulit | 23 |

Distribusi skor manusia **condong ke kanan** (mean 84,0; median 90,0; std dev 17,7): 73% submisi mendapat skor ≥ 85. Ekor panjang ke bawah berasal hampir seluruhnya dari P1 dan P6. Soal P6 merupakan soal paling menantang — kriteria *Concurrency Safety* (35 poin) adalah titik kehilangan poin terbesar dengan rata-rata pengurangan −8,0 poin dan deviasi standar 27,2.

---

## Desain Eksperimen

Eksperimen menguji desain **faktorial penuh 2³**: tiga faktor *prompt engineering* masing-masing dengan dua level (aktif/nonaktif) menghasilkan **8 skenario** (S1–S8). Ketiga faktor tersebut adalah `structured_rubric` (rubrik terstruktur per-subkriteria dengan *scoring band*), `chain-of-thought` (instruksi penalaran `<THINKING>` bertahap), dan `few_shot` (contoh penilaian per-soal). S8 adalah konfigurasi *all-on* yang mengaktifkan ketiga faktor.

**Tabel 2. Delapan skenario faktorial penuh 2³**

| ID | Label | Rubrik | CoT | Few-shot |
|----|-------|:------:|:---:|:--------:|
| S1 | baseline | ✗ | ✗ | ✗ |
| S2 | rubric-only | ✓ | ✗ | ✗ |
| S3 | cot-only | ✗ | ✓ | ✗ |
| S4 | fewshot-only | ✗ | ✗ | ✓ |
| S5 | rubric+cot | ✓ | ✓ | ✗ |
| S6 | rubric+fewshot | ✓ | ✗ | ✓ |
| S7 | cot+fewshot | ✗ | ✓ | ✓ |
| **S8** | **all-on** | **✓** | **✓** | **✓** |

Pemenang ditentukan melalui **composite picker** dua tahap: (1) *gate deployability* — skenario dengan parse rate < 90% terdiskualifikasi; (2) komposit z-score `2·z_MAE + 1·z_(1−r)` di antara skenario yang lolos, dengan MAE diberi bobot 2× Pearson karena akurasi absolut lebih penting daripada sekadar keselarasan urutan.

---

## Trajektori Iteratif — Run 1 s/d 11

Sebelum mencapai konfigurasi final, eksperimen melewati **11 run** yang mencakup tiga iterasi perbaikan prompt (*Fix A, B, C*) dan eksplorasi beberapa model. Tabel berikut merangkum metrik utama tiap run.

**Tabel 3. Trajektori metrik lintas run (pemenang per run, Fase 1 & 2)**

| Run | Model | Intervensi | Pemenang | MAE ↓ | Parse % | ICC P2 | Catatan |
|-----|-------|-----------|----------|------:|--------:|-------:|---------|
| 1 | Flash | Pilot; rubrik nonstruktur per-soal | S7 | 17,80 | 99,3% | 0,881 | Baseline awal |
| 2 | Flash | Rubrik default untuk nonstruktur | S7 | 18,51 | 99,3% | 0,896 | **Anomali: S7 > S8 ditemukan** |
| 3 | Flash | **Fix A** — "Do not invent defects" | S3 | 16,52 | 97,9% | 0,911 | Halusinasi P2 hilang |
| 4 | Flash | **Fix B** — rubrik *scoring band* | S5 | 10,84 | 98,6% | 0,759 | **MAE anjlok; S8 > S7** |
| 5 | Flash | **Fix C** — few-shot per-soal | **S8** | **11,17** | 99,3% | 0,715 | Semua *smoking-gun* pulih |
| 6 | Flash | Ubah temperature/token | S8 | 11,50 | 100% | 1,000 | P2 deterministik (catatan metodologis) |
| 7 | **Pro** | Model Gemini 2.5 Pro | S3 | 12,62 | 82,6% | 0,910 | Parse rate jatuh → tidak *deployable* |
| 8 | **3.5 Flash** | Model Gemini 3.5 Flash | S7 | 10,19 | 93,8% | 0,981 | MAE terendah; konsistensi sangat tinggi |
| 9 | Flash | *Picker* baru (gate + z-score 2:1) | S5 | 11,49 | 99,3% | 0,998 | Metodologi pemilihan diperketat |
| 10 | Flash | Konsolidasi + ANOVA (n=731) | S8 | 10,70 | 98,6% | 0,978 | Run antara |
| **11** | **Flash (temp=0)** | **Run final/kanonik** | **S8** | **10,97** | **98,6%** | **1,000** | **Angka yang dilaporkan** |

Pola utama: **MAE S8 turun dari 18,27 (Run 2) ke 10,97 (Run 11) — penurunan ~40%** — melalui tiga perbaikan bertahap. Pada saat yang sama terdapat *trade-off*: ICC konsistensi Fase 2 turun dari 0,896 (Run 2) ke 0,715 (Run 5). Hal ini akan dibahas lebih lanjut pada subbab analisis konsistensi.

### Tiga Perbaikan Inti (Fix A → B → C)

#### Fix A — Melawan Bias "Cari Bug" (Run 3)

Masalah yang ditemukan pada Run 2 adalah model yang dilengkapi CoT memperlakukan rubrik berbentuk *checklist failure-mode* sebagai daftar *to-do* — mencari-cari setiap cacat yang disebutkan dan mengadanya bila tidak ditemukan. Kasus paling mencolok: submisi `PalindromeC3` (skor manusia: 98) diberi skor 35 oleh S8 karena model "mengarang" klaim bahwa `sb.reverse()` bermutasi setelah dipanggil — sebuah klaim yang salah secara faktual.

**Perubahan:** (1) `system.txt` — tambah aturan *"Do not invent defects"* yang mewajibkan model mengutip baris kode spesifik sebagai bukti sebelum mengurangi nilai; (2) `cot_instruction.txt` — langkah 7 (*"Look back and re-check"*) diperketat menjadi *evidence test* eksplisit.

**Dampak:** Halusinasi `PalindromeC3` hilang total (skor 35 → 100). S8 MAE: 18,27 → 17,75.

#### Fix B — Scoring Band, Bukan Checklist (Run 4)

Walau aturan "jangan mengarang" sudah ditambahkan, *bentuk* rubrik yang masih berupa enumerasi failure-mode tetap memicu bias atensi. Rubrik perlu ditulis ulang menjadi **tabel *scoring band*** yang mendeskripsikan *bukti apa dalam kode* yang sesuai dengan setiap band skor, bukan *apa yang harus dicari*.

**Perubahan:** Keenam `rubric_structured` di `problems.json` ditulis ulang menjadi tabel 3–4 band per kriteria dengan jangkar skor eksplisit (mis. `45/45`, `32/45`, `18/45`, `0/45`).

**Dampak:** Semua skenario ber-rubrik (S2, S5, S6, S8) turun 3–8 poin MAE. S8: 17,75 → 12,24. **Gap S8–S7 berbalik**: S8 kini lebih baik 4,5 MAE. Sebagai *trade-off*, ICC konsistensi Fase 2 turun dari 0,911 ke 0,759 — band rubrik yang ketat memunculkan *band-boundary flicker* pada submisi di batas band.

#### Fix C — Few-Shot Sesuai Bentuk Rubrik (Run 5)

Dua contoh *few-shot* yang dipakai pada Run 1–4 adalah contoh penilaian soal *Two-Sum* (Python, 3 kriteria, gaya prosa) — tidak sesuai dengan sebagian besar soal yang memiliki 4 kriteria dalam gaya *band*. Model harus mengekstrapolasi dari contoh Python ke soal Go dengan kriteria *Concurrency Safety* — sumber kebisingan skor.

**Perubahan:** (1) `few_shot.json` — diganti menjadi 12 contoh per-soal (2 per P1–P6): satu submisi bermutu tinggi + satu submisi cacat, kode sintetis (anti data-leakage), dinilai dalam gaya band; (2) `prompt.py` — filter pool berdasarkan `problem_id` sebelum injeksi.

**Dampak:** S8 menjadi pemenang (MAE 11,17, parse rate 99,3%). Semua empat *smoking-gun* pulih, termasuk `sum_array_c1` (skor manusia 95, sebelumnya 5–37, kini 95). Parse rate non-CoT naik +10–20 pp.

### Tabel Pemulihan Smoking-Gun

**Tabel 4. Submisi "smoking-gun" — perjalanan kalibrasi**

| Submisi | Skor manusia | Run 2 S8 | Run 3 (Fix A) | Run 4 (Fix B) | Run 5 (Fix C) | Status |
|---------|:-----------:|:--------:|:-------------:|:-------------:|:-------------:|--------|
| `PalindromeC3` (palindrom benar) | 98 | 35 | **100** | 100 | 100 | ✅ Pulih di Fix A |
| `dijkstra_c2` (Dijkstra bersih) | 100 | 70 | 85 | **100** | 100 | ✅ Pulih di Fix B |
| `pool_h2` (worker pool benar) | 90 | 61 | 48 | **96** | 86 | ✅ Pulih di Fix B |
| `sum_array_c1` (sum benar) | 95 | 10 | 5 | 37 | **95** | ✅ Pulih di Fix C |

---

## Fase 1 — Akurasi & Deployability (Run Final, Temp=0)

Run 11 merupakan run final yang menjadi acuan pelaporan: Gemini 2.5 Flash, temperature 0 (deterministik), dengan konfigurasi prompt Fix A+B+C penuh. Dijalankan pada 8 skenario × 144 submisi.

### Hasil per Skenario

**Tabel 5. Hasil Fase 1 — seluruh skenario, diurutkan composite score**

| Rank | Skenario | Parse Rate | MAE | Pearson *r* | ICC(A,1) | Composite *z* |
|:---:|---|---:|---:|---:|---:|---:|
| 1 | **S8** (rubrik + CoT + few-shot) | **98,6%** | **10,97** | 0,724 | 0,687 | **−2,822** |
| 2 | S5 (rubrik + CoT) | 98,6% | 10,70 | 0,669 | 0,651 | −1,464 |
| 3 | S7 (CoT + few-shot) | 97,9% | 16,93 | 0,692 | 0,548 | +1,784 |
| 4 | S3 (CoT saja) | 95,8% | 15,72 | 0,638 | 0,545 | +2,502 |
| — | S4 (few-shot saja) | 31,9% | 9,89 | 0,720 | 0,704 | *gugur* |
| — | S6 (rubrik + few-shot) | 34,0% | 10,80 | 0,670 | 0,659 | *gugur* |
| — | S2 (rubrik saja) | 27,1% | 11,99 | 0,667 | 0,578 | *gugur* |
| — | S1 (baseline) | 0,0% | — | — | — | *gugur* |

*n=697 baris valid dari 1.152 teoritis (8 skenario × 144 submisi). Baris yang hilang akibat skenario tanpa CoT gagal di-parse.*

**Temuan kunci:** Semua empat skenario yang lolos gate 90% adalah skenario ber-CoT (S3, S5, S7, S8). Semua empat skenario tanpa CoT (S1, S2, S4, S6) gagal dengan parse rate 0–34%. Ini menunjukkan bahwa **CoT adalah penentu *deployability*** — tanpa instruksi penalaran bertahap, model cenderung menghasilkan respons dalam format bebas yang tidak dapat diekstrak menjadi skor terstruktur.

S8 terpilih sebagai pemenang meskipun MAE-nya (10,97) sedikit lebih tinggi daripada S5 (10,70), karena S8 memiliki Pearson *r* yang lebih baik (0,724 vs 0,669), menghasilkan composite *z* terendah (−2,822 vs −1,464). S8 juga merupakan satu-satunya konfigurasi yang mengaktifkan ketiga komponen sekaligus.

### Atribusi Faktor — 3-Way ANOVA

Untuk memahami kontribusi tiap komponen prompt terhadap pengurangan error penilaian, dijalankan *three-way ANOVA* Type II pada 697 baris valid dengan variabel dependen `|skor_manusia − skor_LLM|` dan faktor `rubric × cot × fewshot`. Type II dipilih karena desain tidak seimbang (*unbalanced*) akibat skenario tanpa CoT menghasilkan jauh lebih sedikit baris valid.

**Tabel 6. Hasil 3-way ANOVA pada |skor manusia − skor LLM| (n=697, Type II SS)**

| Faktor | F | p | η²p | Interpretasi |
|---|--:|--:|--:|---|
| rubric | 10,24 | 0,0014 ** | 0,015 | Signifikan, efek kecil |
| cot | 10,16 | 0,0015 ** | 0,015 | Signifikan, efek kecil |
| few-shot | 0,03 | 0,8519 ns | 0,000 | Tidak ada efek |
| rubric × cot | 10,10 | 0,0015 ** | 0,014 | Signifikan, efek kecil |
| rubric × few-shot | 0,14 | 0,7092 ns | 0,000 | Tidak ada efek |
| cot × few-shot | 0,87 | 0,3506 ns | 0,001 | Tidak ada efek |
| rubric × cot × few-shot | 0,02 | 0,8819 ns | 0,000 | Tidak ada efek |

*Signifikansi: \*\* p < 0,01; ns p ≥ 0,05. Ukuran efek η²p ditafsirkan menurut Cohen (1988): ≈0,01 kecil, ≈0,06 sedang.*

Tiga temuan utama:

1. **Rubrik dan CoT keduanya signifikan** sebagai efek utama (p < 0,01, η²p ≈ 0,015). Keduanya secara nyata mengurangi error penilaian.
2. **Interaksi rubrik × CoT juga signifikan** (F = 10,10, p = 0,0015): manfaat rubrik terstruktur dan CoT tidak bersifat aditif murni — keduanya saling memperkuat ketika digunakan bersamaan.
3. **Few-shot tidak memberikan efek yang terukur** pada akurasi (η²p = 0,000 untuk semua efek yang melibatkan few-shot). Meskipun S8 yang menyertakan few-shot terpilih sebagai pemenang, keunggulannya berasal dari kombinasi rubrik dan CoT, bukan dari komponen few-shot itu sendiri.

---

## Analisis Mendalam — Sumber Residual Error

### Stratifikasi MAE berdasarkan Kualitas Submisi

MAE keseluruhan S8 sebesar 10,97 **tidak terdistribusi merata** — error terkonsentrasi pada submisi berkualitas rendah dan sedang.

**Tabel 7. MAE terstratifikasi berdasarkan band skor manusia (S8, Run 5)**

| Band skor manusia | n | MAE | Bias rata-rata (LLM − manusia) |
|-------------------|---|----:|-------------------------------:|
| 95–100 | 55 | **5,78** | −4,55 |
| 85–94 | 54 | 11,74 | −6,81 |
| 70–84 | 21 | 15,33 | −4,10 |
| 50–69 | 10 | 24,70 | −18,10 |
| 30–49 | 3 | 25,33 | +25,33 |

**Framing utama:** LLM sudah mencapai MAE 5,78 pada kode bersih (skor ≥ 95), mendekati target. Sisa error terkonsentrasi pada kode rusak di mana LLM menerapkan rubrik secara ketat sementara asisten pengajar manusia memberikan *partial credit* yang lebih longgar.

### Asimetri Ketidaksepakatan

Dari 29 kasus error besar (|error| ≥ 20):
- **23 kasus: LLM lebih rendah** dari manusia — LLM mendeteksi bug nyata yang dimaafkan oleh TA
- **6 kasus: LLM lebih tinggi** dari manusia — LLM meleset menilai

Pola ini menunjukkan bahwa **sumber error dominan bukan halusinasi LLM** (masalah itu sudah diatasi oleh Fix A+B+C), melainkan **inkonsistensi penilaian manusia pada kode rusak**. LLM menerapkan rubrik secara konsisten; TA memberi *partial credit* secara subjektif.

**Tabel 8. Contoh kasus "LLM benar, manusia longgar"**

| Submisi | Skor manusia | Skor LLM S8 | Masalah yang terdeteksi LLM |
|---------|:-----------:|:-----------:|---|
| `pool_e5` | 60 | 3 | Deadlock di setiap input — loop baca hasil berjalan sebelum pekerjaan dikirim. TA memberi 15/15 Efisiensi. |
| `pool_g3` | 70 | 22 | Worker berhenti selamanya — `close(jobs)` tidak pernah dipanggil. `wg.Wait()` menggantung. TA memberi 15/15 Efisiensi. |
| `BstH1` | 85 | 35 | Dua dari lima method BST adalah stub. Field `root` statis (berbagi antar-instans). TA memberi 35/40 Correctness. |
| `lru_f3` | 85 | 43 | `pop()` menghapus kunci paling baru, bukan paling lama — eviction policy terbalik. |

---

## Analisis per Soal (S8 Run Final)

**Tabel 9. Kinerja S8 per soal**

| Soal | n | MAE | Bias rata-rata | Catatan |
|------|---|----:|---------------:|---------|
| P1 Sum Array (Python) | 28 | 14,86 | −4,43 | Terburuk; banyak submisi trivial/rusak |
| P2 Palindrome (Java) | 20 | 6,50 | −4,30 | Hampir target; terkalibrasi baik setelah Fix A |
| **P3 LRU Cache (TypeScript)** | **25** | **10,04** | **−0,44** | **Bias hampir nol — terkalibrasi terbaik** |
| P4 Dijkstra (C++) | 25 | 9,50 | −4,50 | Bersih setelah Fix A+B |
| P5 BST (Java) | 23 | 11,65 | −9,22 | Skor konsisten rendah; pola *partial credit* manusia pada stub |
| P6 Worker Pool (Go) | 23 | 13,22 | −11,65 | Bias terbesar; LLM mendeteksi deadlock yang dimaafkan manusia |

---

## Perbandingan Model

Selain Gemini 2.5 Flash sebagai model utama, dua model lain diuji untuk referensi.

**Tabel 10. Perbandingan tiga model (konfigurasi terbaik masing-masing)**

| Metrik | Flash (Run 11) | Pro (Run 7) | 3.5 Flash (Run 8) |
|--------|---------------:|------------:|------------------:|
| Skenario pemenang | S8 (all-on) | S3 (cot-only) | S7 (cot+fewshot) |
| MAE (pemenang) | 10,97 | 12,62 | **10,19** |
| Parse rate (pemenang) | 98,6% | 82,6% | 93,8% |
| ICC Fase 1 (human↔LLM) | 0,687 | 0,607 | 0,637 |
| ICC Fase 2 (konsistensi) | 1,000\* | 0,910 | 0,981 |

*\* ICC = 1,000 pada Flash Run 11 adalah artefak determinisme (temp=0), bukan pengukuran konsistensi genuina.*

**Pro** lebih konsisten (ICC P2 0,910) tetapi parse rate 82,6% menjadikannya tidak *deployable* — 17% respons gagal menghasilkan JSON yang dapat di-parse. Skenario pemenangnya adalah S3 (cot-only, tanpa rubrik terstruktur), menunjukkan bahwa model yang lebih besar tidak mendapat manfaat yang sama dari rubrik dalam format ini. **3.5 Flash** mencapai MAE terbaik (10,19) dengan konsistensi sangat tinggi (0,981), meskipun dengan parse rate lebih rendah dari Flash 2.5 (93,8%). Untuk keseimbangan antara akurasi, *deployability*, dan konsistensi, **Flash 2.5 tetap pilihan terbaik** untuk produksi.

---

## Fase 2 — Konsistensi (ICC)

### Kondisi Pengujian

Fase 2 mengukur konsistensi intrarater dari konfigurasi terpilih (S8) pada kondisi paling menantang. **Soal P6** (*Worker Pool*, Go) dipilih sebagai *worst case* karena memiliki distribusi skor paling beragam dan kompleksitas teknis tertinggi. Sistem dijalankan **7 kali** (k=7) terhadap **19 submisi** P6 yang sama, menghasilkan matriks 19 × 7 = 133 penilaian.

Dua kondisi temperatur diuji:
- **temp=0**: kondisi produksi deterministik — sebagai *baseline*
- **temp=0.7**: kondisi uji ketahanan stokastik — untuk mengukur konsistensi genuina

### Hasil

**Tabel 11. Hasil Fase 2 — konsistensi S8 pada P6 (n=19 submisi × k=7 replikasi)**

| Kondisi | ICC(A,1) | 95% CI | Interpretasi (Koo & Li 2016) |
|---|:---:|:---:|---|
| temp=0 (produksi) | **1,000** | — | Deterministik — 7 replikasi byte-identik |
| temp=0.7 (uji ketahanan) | **0,882** | [0,714; 0,954] | **Baik (*good*)** |

Nilai ICC = 1,000 pada temp=0 adalah konfirmasi perilaku deterministik (*greedy decoding*), bukan temuan reliabilitas. Ketujuh replikasi menghasilkan teks yang byte-identik sehingga ICC secara matematis bernilai 1,000.

Hasil substantif adalah pada **temp=0.7**: ICC(A,1) = 0,882, dengan selang kepercayaan 95% [0,714; 0,954]. Mengikuti anjuran Koo dan Li (2016) untuk mengategorikan berdasarkan batas bawah selang kepercayaan (0,714), konfigurasi S8 tergolong **sedang hingga baik**. *Point estimate* 0,882 masuk kategori **baik (*good*)** dan mendekati ambang *excellent* (≥ 0,90).

Dari 19 submisi, **18 di antaranya menunjukkan variasi skor** antar-pemanggilan pada temp=0.7 — hanya 1 submisi yang menghasilkan skor identik di semua 7 replikasi. Ini mengonfirmasi bahwa ICC = 0,882 adalah ukuran konsistensi genuina, bukan artefak.

### Trade-off Akurasi ↔ Konsistensi

Sepanjang trajektori Run 2–5, peningkatan akurasi (MAE turun) disertai penurunan ICC konsistensi:

**Tabel 12. Trade-off akurasi ↔ konsistensi (S8, Fase 2)**

| Run | MAE S8 | ICC Fase 2 | Keterangan |
|-----|-------:|-----------:|------------|
| 2 | 19,37 | 0,896 | Sebelum perbaikan; rubrik *checklist* |
| 3 | 17,75 | 0,911 | Fix A — aturan bukti |
| 4 | 12,24 | 0,759 | Fix B — rubrik *band*; flicker batas band |
| 5 | 11,17 | 0,715 | Fix C — few-shot per-soal |
| **11 (final)** | **10,97** | **1,000\*** | **Temp=0 deterministik** |
| **13 (re-run P2 @ 0.7)** | — | **0,882** | **Konsistensi genuina pada temp=0.7** |

*\* Artefak determinisme.*

Pola ini dapat dijelaskan: rubrik *scoring band* yang ketat meningkatkan akurasi karena mendorong model memilih band yang tepat, namun submisi di *batas band* membuat model memilih band yang berbeda antar-pemanggilan (*band-boundary flicker*). Ini adalah *trade-off* yang dapat diterima dalam konteks *TA-assist* di mana LLM menghasilkan draf yang disetujui manusia.

---

## Ringkasan Temuan

1. **Konfigurasi terbaik adalah S8** (rubrik terstruktur + CoT + few-shot): parse rate 98,6%, MAE 10,97 poin, Pearson *r* = 0,724.

2. **CoT adalah penentu *deployability***. Semua skenario tanpa CoT terdiskualifikasi (parse rate 0–34%), terlepas dari akurasinya pada parses yang berhasil.

3. **Rubrik dan CoT berkontribusi nyata terhadap akurasi** (p < 0,01, ANOVA), dengan interaksi signifikan (rubrik × CoT). Few-shot tidak memberikan efek yang terukur secara statistik (η²p = 0,000).

4. **MAE LLM pada kode bersih sudah 5,78** (skor ≥ 95). Sisa MAE keseluruhan (10,97) didominasi oleh perbedaan filosofi penilaian pada kode rusak: LLM menerapkan rubrik ketat, manusia memberi *partial credit* longgar.

5. **Konsistensi S8 tergolong baik**: ICC(A,1) = 0,882 [0,714; 0,954] pada kondisi stokastik (temp=0.7), yang merupakan kondisi uji lebih ketat daripada kondisi produksi (temp=0).

---

*Referensi yang dipakai: Koo & Li (2016) untuk interpretasi ICC; Langsrud (2003) untuk Type II ANOVA pada data unbalanced; Cohen (1988) untuk ambang η²p; Liljequist dkk. (2019) untuk formula ICC(A,1).*
