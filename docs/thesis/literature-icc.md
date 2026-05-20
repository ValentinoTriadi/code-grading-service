# Studi Literatur — Konsistensi & ICC

Kerangka bagian Tinjauan Pustaka untuk pembahasan **konsistensi sistem** dan **Intraclass Correlation Coefficient (ICC)**. File ini bukan tulisan jadi — anggap sebagai outline + catatan isi yang masih perlu kamu kembangkan jadi paragraf prosa.

> **Prinsip penulisan:** definisikan dulu semua dimensi → baru pilih konfigurasinya → baru hitung → baru interpretasi. Jangan campur "pengenalan" dan "justifikasi pilihan" di paragraf yang sama; pembaca akan kesfulitan mengikuti penalaran.

---

## 2.X.1 Konsistensi sebagai Aspek Reliabilitas

**Yang perlu kamu tulis:**

- Definisi konsistensi sebagai *run-to-run reliability* — yaitu seberapa stabil hasil sistem ketika diberi input identik berulang kali.
- Mengapa konsistensi krusial untuk sistem penilaian otomatis berbasis LLM: keputusan produksi (deployment) menuntut skor yang dapat direproduksi; sistem yang akurat tetapi berfluktuasi sulit dipercaya pengguna.
- **Bedakan dengan akurasi**: akurasi membandingkan output sistem dengan referensi eksternal (skor manusia), sedangkan konsistensi membandingkan output sistem dengan dirinya sendiri pada panggilan berbeda. Keduanya independen — sistem bisa konsisten tetapi salah, atau akurat secara rata-rata tetapi tidak stabil per panggilan.

**Sitasi yang relevan:** literatur reliability klasik (Cronbach, 1951; Shrout & Fleiss, 1979) untuk konsep dasar; literatur evaluasi LLM modern bila tersedia.

---

## 2.X.2 Pemilihan Metrik Konsistensi

**Yang perlu kamu tulis:**

Sebut beberapa alternatif metrik yang lazim, lalu jelaskan mengapa belum cukup untuk konteks ini:

| Metrik | Kelemahan untuk kasus ini |
|---|---|
| Pearson r | Hanya mengukur korelasi linier; mengabaikan offset sistematis (bias). |
| Cohen's κ | Dirancang untuk dua rater pada data kategorikal, bukan kontinu. |
| Krippendorff α | Generalisasi yang fleksibel, tetapi terlalu umum untuk pertanyaan single-rater. |
| Cronbach α | Cocok untuk reliabilitas internal kuesioner (banyak item), bukan single-skor diulang. |

Kemudian justifikasi singkat memilih ICC: dirancang spesifik untuk multiple ratings pada subjek yang sama, mendukung mode absolute agreement, dan punya formula khusus untuk single-rater.

---

## 2.X.3 Pengenalan ICC (Intraclass Correlation Coefficient)

**Yang perlu kamu tulis:**

- Asal-usul historis: dirumuskan oleh Shrout & Fleiss (1979), diperluas dan diklasifikasikan ulang oleh McGraw & Wong (1996).
- Konsep dasar: ICC adalah **rasio antara variansi sistematis (between-subject)** terhadap **total variansi**.

  ```
  ICC = σ²(between) / [σ²(between) + σ²(within)]
  ```

  Semakin besar variansi between-subject relatif terhadap noise within-subject, semakin tinggi ICC — artinya pengukuran membedakan subjek dengan baik.
- Rentang nilai: nominal 0–1; secara teknis bisa negatif untuk formula tertentu, tetapi dalam praktek diinterpretasikan sebagai 0.

---

## 2.X.4 Klasifikasi ICC

> Tulis bagian ini untuk **mendefinisikan** semua dimensi pilihan ICC. Pemilihan konfigurasi konkret untuk eksperimen ditunda ke 2.X.5 supaya alur argumentasi tidak meloncat.
T

### a. Model — bagaimana rater dipilih

| Model | Definisi | Kapan dipakai |
|---|---|---|
| One-Way Random | Rater berbeda untuk setiap subjek; rater dipandang sebagai sampel random. | Penilai tidak konsisten antar subjek. |
| Two-Way Random | Semua subjek dinilai oleh rater yang sama; rater adalah sampel random dari populasi rater. | Hasilnya ingin digeneralisasi ke rater lain di luar studi. |
| Two-Way Mixed | Semua subjek dinilai oleh rater yang sama; rater adalah objek tetap, bukan sampel. | Rater yang dipakai adalah satu-satunya yang akan dinilai. |

**Sitasi:** McGraw & Wong (1996); Liljequist dkk. (2019).

### b. Bentuk pengukuran — single vs average

- **ICC(·,1)** — single rater: generalisasi ke pengukuran satu rater.
- **ICC(·,k)** — average rater: generalisasi ke rata-rata k rater.

Pilihan tergantung *bagaimana skor akan dipakai* di praktek. Kalau deployment hanya pakai 1 panggilan LLM, gunakan ICC(·,1). Kalau deployment me-rata-rata k panggilan, gunakan ICC(·,k).

### c. Tipe agreement — absolute vs consistency

| Tipe | Definisi | Sensitif terhadap |
|---|---|---|
| **Absolute Agreement (A)** | Sepakat pada **nilai** absolutnya. | Bias sistematis antar rater/run (offset). |
| **Consistency (C)** | Sepakat pada **pola** (urutan / korelasi). | Tidak peka terhadap offset; hanya pola. |

Contoh: kalau Run 1 selalu memberikan skor 5 poin lebih tinggi dari Run 2 untuk semua submission, **Consistency** akan tinggi (pola sama), tetapi **Absolute Agreement** akan rendah (nilai berbeda secara konstan).

**Sitasi:** McGraw & Wong (1996).

### d. Tujuan pengukuran — intrarater vs interrater

| Tujuan | Definisi | Konteks |
|---|---|---|
| **Intrarater reliability** | Konsistensi **satu** penilai yang sama menilai **subjek yang sama** di **waktu berbeda**. | Test-retest reliability, *self-consistency*. |
| **Interrater reliability** | Agreement antar **penilai yang berbeda** terhadap **subjek yang sama**. | Multi-rater agreement. |

**Sitasi:** Koo & Li (2016).

---

## 2.X.5 Pemilihan Konfigurasi ICC untuk Eksperimen Ini

> Bagian ini adalah **inti argumentasi**. Setiap pilihan harus dibangun dari empat dimensi di Bab 2.X.4 dan diberi alasan eksplisit. Tabel di bawah lebih persuasif daripada paragraf.

| Dimensi | Pilihan | Alasan |
|---|---|---|
| **Model** | Two-Way Mixed | Konfigurasi prompt LLM adalah **objek tetap** yang akan di-deploy, bukan sampel random dari populasi konfigurasi. |
| **Bentuk pengukuran** | Single rater (k=1) | Yang akan di-deploy adalah **satu** konfigurasi pemanggilan, bukan rata-rata k panggilan. |
| **Tipe agreement** | Absolute (A) | Bias sistematis antar run (offset konstan) tetap merupakan bentuk inkonsistensi yang harus terdeteksi. Consistency (C) akan menyembunyikan ini. |
| **Tujuan** | Intrarater | "Penilai" yang diukur adalah **satu** konfigurasi prompt yang sama, hanya berbeda di waktu pemanggilan. |

**Kesimpulan eksplisit (wajib ditulis):**

> Pengukuran konsistensi pada eksperimen ini menggunakan **ICC(A,1)** — Two-Way Mixed Model, Absolute Agreement, Single-Rater Form, Intrarater Reliability. Notasi alternatif yang ekuivalen: ICC2,1 (Shrout & Fleiss, 1979) atau ICC(2,1) absolute (McGraw & Wong, 1996).

> **Catatan penulisan:** banyak pembaca skripsi yang bingung dengan banyaknya nama untuk hal yang sama. Tulis tabel ekuivalensi notasi di sini — atau di footnote — supaya `ICC(A,1)`, `Two-Way Mixed Absolute Single`, dan `ICC2,1` tidak terlihat seperti tiga metrik berbeda.

---

## 2.X.6 Komputasi ICC(A,1)

**Yang perlu kamu tulis:**

### a. Representasi data

Matriks `n × k`:

- `n` = jumlah submission yang dinilai berulang
- `k` = jumlah perulangan (pada eksperimen ini, k = 7)

| Submission | Run 1 | Run 2 | … | Run k |
|---|---|---|---|---|
| M₁  | x₁₁ | x₁₂ | … | x₁ₖ |
| M₂  | x₂₁ | x₂₂ | … | x₂ₖ |
| ⋮   | ⋮ | ⋮ | ⋮ | ⋮ |
| Mₙ  | xₙ₁ | xₙ₂ | … | xₙₖ |

**Asumsi statistik** yang perlu disebutkan:

- Independensi antar observasi (skor antar run tidak saling memengaruhi).
- Residual approximately normal — biasanya terpenuhi untuk skor 0–100 dengan banyak submission.
- Tidak ada interaksi systematic submission × run yang besar.

### b. Langkah perhitungan

> Pindahkan kontennya yang sudah kamu tulis di skripsi ke sini — semua formula dari Grand Mean hingga ICC(A,1) tetap relevan dan benar. Tidak perlu diubah.

1. Grand mean — `x̄_grand`
2. Row means — `x̄_i` per submission
3. Column means — `x̄_j` per run
4. Sum of Squares: `SS_rows`, `SS_cols`, `SS_total`, `SS_error`
5. Mean Squares: `MS_BS`, `MS_BM`, `MS_E`
6. Formula ICC(A,1):

   ```
                          MS_BS − MS_E
   ICC(A,1) = ─────────────────────────────────────────────────────
              MS_BS + (k − 1)·MS_E + (k / n)·(MS_BM − MS_E)
   ```

### c. Implementasi praktis

- Library yang direkomendasikan untuk verifikasi:
  - Python: `pingouin.intraclass_corr` — tipe `"ICC2"` (notasi pingouin) sama dengan `ICC(A,1)`.
  - R: `irr::icc(model="twoway", type="agreement", unit="single")`.
- Keuntungan library: keluaran sudah termasuk **95% confidence interval** dan p-value.
- Pada penelitian ini implementasi pure-Python ada di `experiments/metrics.py:icc_a1` (untuk minimal-deps), divalidasi terhadap pingouin.

---

## 2.X.7 Interpretasi Koefisien

**Yang perlu kamu tulis:**

Threshold standar dari **Koo & Li (2016)** — sangat sering disitasi sebagai panduan baku:

| Rentang | Interpretasi |
|---|---|
| `< 0.5` | Poor reliability |
| `0.5 – 0.75` | Moderate reliability |
| `0.75 – 0.90` | Good reliability |
| `≥ 0.90` | Excellent reliability |

**Catatan penulisan:**

- Wajib lapor **95% CI bersama point estimate**. Point estimate `0.85` dengan CI `[0.6, 0.95]` sangat berbeda interpretasinya dengan `0.85` dengan CI `[0.82, 0.88]`.
- Pertimbangkan untuk menyebut **batas keberterimaan** sistem: misal "kami menargetkan ICC ≥ 0.75" dan jelaskan alasannya (deployment threshold, perbandingan dengan inter-grader human reliability, dsb).

---

## 2.X.8 Penerapan ICC pada Riset Sebelumnya (Opsional)

> Bagian ini opsional tetapi memperkuat argumen kamu — menunjukkan bahwa pilihan ICC bukan ad-hoc.

**Yang bisa kamu tulis:**

- ICC dalam evaluasi sistem **automated essay scoring** (AES) — banyak studi memakai ICC untuk membandingkan skor mesin dengan grader manusia.
- ICC dalam evaluasi konsistensi LLM untuk task NLP scoring (lebih baru, mungkin masih sedikit literaturnya — fakta ini sendiri bisa jadi *gap* yang riset kamu isi).
- ICC sebagai standar di bidang lain yang dapat dijadikan analogi: medical imaging reliability, psychometric test-retest reliability.

Beri 2–3 paragraf yang merangkum hasil riset terdahulu, lalu identifikasi gap yang diisi penelitian ini.

---

## Daftar Referensi Inti

| Sitasi | Untuk apa |
|---|---|
| Shrout, P. E., & Fleiss, J. L. (1979) | Formulasi orisinal ICC + 6 bentuk klasik (ICC(1,1), ICC(2,1), ICC(3,1), dst). |
| McGraw, K. O., & Wong, S. P. (1996) | Reklasifikasi ICC ke {Model × Form × Type}: ICC(A,1) vs ICC(C,1) dst. |
| Koo, T. K., & Li, M. Y. (2016) | Panduan praktis pemilihan model + threshold interpretasi yang paling sering disitasi. |
| Liljequist, D., Elfving, B., & Skavberg Roaldsen, K. (2019) | Sudah kamu pakai — taksonomi 3 model ICC. |
| Hallgren, K. A. (2012) | "Computing Inter-Rater Reliability for Observational Data" — panduan praktis di software, contoh hitungan. |
| Bartko, J. J. (1966) | ICC awal pada konteks variance components. |
| Cronbach, L. J. (1951) | Latar belakang reliability theory secara umum. |

---

## Rekomendasi Gaya Penulisan untuk Bagian Ini

1. **Pisahkan "definisi" dari "pemilihan".** Tulis 2.X.4 sebagai pure definisi, lalu 2.X.5 sebagai justifikasi pilihan. Kalau dicampur, kalimat "kami pakai Two-Way Mixed karena cocok" akan terasa hand-wavy bagi pembaca yang belum tahu apa itu Two-Way Mixed.
2. **Tabel > paragraf** untuk perbandingan multi-dimensi (model, form, type, purpose).
3. **Notasi konsisten.** Pilih satu konvensi subscript di awal (misal `MS_BS` italic vs `MS_{BS}` LaTeX) dan pakai terus. Skripsi jelek tampilannya kalau notasi formula tidak seragam antar bagian.
4. **Tabel ekuivalensi notasi** di akhir 2.X.5: petakan `ICC(A,1)` ↔ `ICC2,1` (Shrout & Fleiss) ↔ `Two-Way Mixed Absolute Single` (McGraw & Wong) ↔ `pingouin "ICC2"`. Ini menyelamatkan pembaca dari kebingungan sitasi-vs-notasi.
5. **Ulang kesimpulan di akhir** bagian 2.X. Kalimat penutup tipe "Berdasarkan empat pilihan di atas, eksperimen ini menggunakan ICC(A,1) Two-Way Mixed Absolute Agreement Single-Rater Intrarater" memudahkan pembaca yang skim.

---

## Cross-reference

- Implementasi dan komputasi: lihat `experiments/metrics.py:icc_a1` dan `experiments/analysis.py:compute_icc`.
- Desain eksperimen + jumlah replikasi (k=7) + ukuran sampel (n=20–28): lihat `docs/design/experiment-plan.md` § Phase 2 — Consistency.
- Threshold yang dipakai untuk *go/no-go* deployment: lihat `docs/design/experiment-plan.md` § Selection criterion.
