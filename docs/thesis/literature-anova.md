# Studi Literatur — Atribusi Efek & ANOVA

Kerangka bagian Tinjauan Pustaka untuk pembahasan **atribusi efek prompt-engineering** terhadap akurasi grading, dengan metrik utama **Analysis of Variance (ANOVA)**. File ini bukan tulisan jadi — anggap sebagai outline + catatan isi yang masih perlu kamu kembangkan jadi paragraf prosa.

> **Prinsip penulisan:** ANOVA dan ICC sama-sama bertumpu pada dekomposisi variansi (SS, MS, df), tetapi *menjawab pertanyaan yang berbeda*. Tulis bagian ini setelah ICC (lihat [`literature-icc.md`](literature-icc.md)) supaya mesin matematikanya sudah familiar dan kamu tinggal mem-fokuskan pembaca ke perbedaan tujuan.

---

## 2.Y.1 Atribusi Efek sebagai Aspek Desain Eksperimen

**Yang perlu kamu tulis:**

- Definisi *atribusi efek*: pertanyaan "**faktor mana** yang menyebabkan perbedaan hasil, dan **seberapa besar** kontribusinya?". Pertanyaan ini muncul ketika eksperimen punya banyak komponen yang bisa dimanipulasi (struktur rubrik, chain-of-thought, few-shot) dan kamu ingin tahu komponen mana yang load-bearing.
- Konteks eksperimen ini: delapan skenario adalah hasil **full factorial 2³** dari tiga faktor biner. Membandingkan dua skenario saja (misal S8 vs S7) hanya menjawab "apakah few-shot membantu *ketika rubric+CoT aktif*", bukan "apakah few-shot membantu *secara umum*". Untuk pertanyaan kedua, butuh atribusi formal.
- **Bedakan dengan akurasi (Pearson, MAE) dan konsistensi (ICC):**
  - Akurasi: seberapa dekat skor LLM ke skor manusia.
  - Konsistensi: seberapa stabil skor LLM lintas panggilan.
  - **Atribusi efek**: dari mana akurasi/konsistensi itu datang.

**Sitasi yang relevan:** Fisher (1935) untuk dasar desain eksperimen; Box, Hunter & Hunter (2005) untuk full factorial design dalam konteks rekayasa.

---

## 2.Y.2 Pemilihan Metrik Atribusi

**Yang perlu kamu tulis:**

Sebut beberapa alternatif metrik atribusi, lalu jelaskan mengapa belum cukup untuk konteks ini:

| Metrik | Kelemahan untuk kasus ini |
|---|---|
| Two-sample t-test | Hanya dua grup pada satu waktu; banyak perbandingan inflasi error α. |
| Pairwise comparison + Bonferroni | Bisa, tapi tidak mengukur **interaksi** antar faktor. |
| Linear regression (OLS) | Bisa estimasi koefisien, tetapi tidak ringkas mendekomposisi variansi per faktor + interaksi. |
| Effect size individual (Cohen's d) | Mengukur magnitude tetapi bukan signifikansi sumber variansi. |

Justifikasi singkat memilih ANOVA: ia adalah **kerangka terstandar** untuk *eksperimen faktorial* — satu prosedur mendekomposisi variansi total menjadi efek utama + interaksi + residual, sekaligus memberikan F-statistic dan p-value per sumber.

> **Catatan penulisan:** ANOVA bisa dilihat sebagai *kasus khusus* dari regression linear dengan dummy variables — tulis ini di footnote agar pembaca yang familiar dengan regression tidak merasa kamu memakai metrik eksotis.

---

## 2.Y.3 Pengenalan ANOVA

**Yang perlu kamu tulis:**

- Asal-usul historis: dirumuskan oleh Ronald Fisher pada tahun 1920-an dalam konteks pertanian (membandingkan hasil panen di plot dengan perlakuan berbeda). Buku *Statistical Methods for Research Workers* (Fisher, 1925) adalah referensi awal.
- Konsep inti: ANOVA memecah **total variansi** observasi menjadi **variansi antar-grup** (signal) dan **variansi dalam-grup** (noise), lalu menguji apakah signal cukup besar dibanding noise untuk dianggap *bukan kebetulan*.

  ```
  Total Variance = Between-Group Variance + Within-Group Variance
  ```

- **F-statistic** adalah rasio dari kedua variansi tersebut, setelah dinormalisasi dengan derajat bebas (degrees of freedom):

  ```
  F = MS_between / MS_within
  ```

  - `F ≈ 1` → variansi antar-grup tidak lebih besar dari noise → tidak ada efek nyata.
  - `F >> 1` → variansi antar-grup mendominasi → faktor grup memberikan efek nyata.

- **p-value**: probabilitas mengamati F sebesar (atau lebih ekstrem dari) hasil eksperimen *jika tidak ada efek sama sekali*. p kecil → bukti kuat ada efek.

---

## 2.Y.4 Klasifikasi ANOVA

> Tulis bagian ini untuk **mendefinisikan** semua dimensi pilihan ANOVA. Pemilihan konfigurasi konkret untuk eksperimen ditunda ke 2.Y.5.

### a. Jumlah faktor — one-way, two-way, n-way

| Jenis | Definisi | Contoh |
|---|---|---|
| One-Way ANOVA | Satu faktor kategorikal dengan dua atau lebih level. | Apakah skor LLM berbeda untuk *cot=off* vs *cot=on*? |
| Two-Way ANOVA | Dua faktor kategorikal, plus interaksi antar keduanya. | Efek `rubric` × `cot` terhadap error. |
| n-Way ANOVA | Lebih dari dua faktor + semua interaksi orde tinggi. | Eksperimen ini: 3-way `rubric × cot × fewshot`. |

### b. Tipe Sum of Squares — Type I, Type II, Type III

Ketika ada lebih dari satu faktor, kontribusi setiap faktor dihitung dengan "mengeluarkan" pengaruh faktor lain terlebih dahulu. Cara mengeluarkan inilah yang membedakan tipe SS:

| Tipe | Cara hitung | Kapan dipakai |
|---|---|---|
| **Type I** | Sequential — SS faktor A dulu, lalu SS faktor B *given A*, lalu interaksi. **Tergantung urutan**. | Hanya kalau ada urutan teoritis natural antar faktor. |
| **Type II** | Setiap efek utama disesuaikan terhadap semua efek utama lain (tetapi tanpa interaksi). | Desain seimbang dan tidak ada interaksi signifikan. |
| **Type III** | Setiap efek disesuaikan terhadap semua efek lain *termasuk interaksi*. | Standar ketika ada interaksi signifikan; sering default di SPSS. |

**Catatan:** pada desain *balanced* (jumlah observasi sama per sel), Type I = Type II = Type III. Pada desain *unbalanced*, ketiganya berbeda.

### c. Fixed effects vs random effects

| Jenis | Definisi | Konteks |
|---|---|---|
| **Fixed effects** | Level faktor adalah yang spesifik kamu inginkan, bukan sampel dari populasi level. | Level `rubric` ∈ {on, off} — kamu tertarik tepat pada kedua level ini, bukan generalisasi ke level lain. |
| **Random effects** | Level faktor adalah sampel acak dari populasi. | Misal "submission" sebagai faktor — tiap submission adalah sampel acak dari populasi submission. |
| **Mixed-effects** | Campuran fixed dan random. | Sering dipakai untuk repeated-measures. |

### d. Balanced vs unbalanced design

- **Balanced** — sama jumlah observasi per sel (per kombinasi level). ANOVA paling kuat & sederhana di sini.
- **Unbalanced** — jumlah observasi tidak sama. Pemilihan Type SS jadi krusial.

---

## 2.Y.5 Pemilihan Konfigurasi ANOVA untuk Eksperimen Ini

> Bagian ini **inti argumentasi**. Setiap pilihan dibangun dari empat dimensi di 2.Y.4 dan diberi alasan eksplisit.

| Dimensi | Pilihan | Alasan |
|---|---|---|
| **Jumlah faktor** | Three-Way ANOVA | Eksperimen mengkombinasi 3 faktor prompt-engineering (`rubric`, `cot`, `fewshot`) secara faktorial penuh. |
| **Tipe SS** | **Type II** | Desain seimbang (144 observasi per skenario); Type II memberi statistical power lebih baik untuk efek utama dibanding Type III. |
| **Tipe efek** | **Fixed effects** | Level setiap faktor (on/off) adalah konfigurasi konkret yang akan di-deploy, bukan sampel acak. |
| **Balanced?** | Ya | 8 skenario × 144 submission = 1152 baris setara. |

**Dependent variable**: `|human_score − llm_score|` (absolute error). Memakai absolute error daripada signed error karena hipotesis adalah "faktor X mengurangi *besar* error", bukan "X menggeser error ke arah tertentu".

**Kesimpulan eksplisit:**

> Pengukuran atribusi efek pada eksperimen ini menggunakan **Three-Way Fixed-Effects ANOVA Type II Sum of Squares** terhadap absolute grading error, dengan tiga faktor biner: `structured_rubric`, `chain_of_thought`, dan `few_shot`. Tujuh sumber variansi diuji: tiga efek utama, tiga interaksi 2-arah, dan satu interaksi 3-arah.

**Implementasi:** `statsmodels.formula.api.ols("abs_error ~ C(rubric) * C(cot) * C(fewshot)", data=df).fit()` lalu `statsmodels.stats.anova.anova_lm(model, typ=2)`. Lihat `experiments/analysis.py:compute_phase1_anova`.

---

## 2.Y.6 Komputasi ANOVA

### a. Representasi data

Dataframe dengan satu baris per observasi:

| abs_error | rubric | cot | fewshot |
|---|---|---|---|
| 12.0 | 1 | 1 | 1 |
| 18.5 | 0 | 1 | 1 |
| 22.0 | 0 | 0 | 0 |
| … | … | … | … |

- `abs_error`: dependent variable kontinu, range [0, 100].
- `rubric`, `cot`, `fewshot`: faktor biner (0/1), masing-masing dikode dengan `C(...)` di statsmodels supaya diperlakukan sebagai kategorikal, bukan numerik.

Untuk eksperimen ini: ~763 baris (hanya `schema_valid=True` yang masuk).

**Asumsi statistik:**

- **Independensi observasi.** Setiap (submission, scenario) menghasilkan satu baris yang tidak berinteraksi dengan baris lain.
- **Normalitas residual.** Errornya kira-kira normal. Karena `abs_error` punya batas bawah 0, distribusi mungkin right-skewed; uji robustness (Welch ANOVA atau Kruskal-Wallis) bisa dilampirkan kalau reviewer menanyakan.
- **Homogenitas variansi (homoscedasticity).** Variansi `abs_error` mirip di semua kombinasi level faktor. Bisa diuji dengan Levene's test.

### b. Langkah perhitungan — One-Way ANOVA (kasus paling sederhana)

> Tulis langkah ini lebih dulu untuk pembaca yang belum familiar. Three-way adalah generalisasi langsung.

Diberikan satu faktor dengan `g` level dan total `N` observasi:

#### Langkah 1 — Grand mean

```
x̄_grand = (1/N) · Σᵢ xᵢ
```

#### Langkah 2 — Group means

```
x̄ⱼ = (1/nⱼ) · Σᵢ∈grup_j  xᵢ          untuk setiap level j ∈ {1, …, g}
```

#### Langkah 3 — Sum of Squares

```
SS_Between = Σⱼ nⱼ · (x̄ⱼ − x̄_grand)²       # variansi antar grup (signal)
SS_Within  = Σⱼ Σᵢ∈grup_j (xᵢ − x̄ⱼ)²        # variansi dalam grup (noise)
SS_Total   = SS_Between + SS_Within
```

#### Langkah 4 — Degrees of freedom

```
df_Between = g − 1
df_Within  = N − g
df_Total   = N − 1
```

#### Langkah 5 — Mean Squares

```
MS_Between = SS_Between / df_Between
MS_Within  = SS_Within  / df_Within
```

#### Langkah 6 — F-statistic dan p-value

```
F = MS_Between / MS_Within
p = P(F_{df_Between, df_Within} ≥ F_observed)     # F-distribution tail
```

Kalau `p < α` (biasanya 0.05), tolak hipotesis nol bahwa semua grup means sama.

### c. Contoh perhitungan terverifikasi (one-way, worked example)

**Setup:** Satu faktor `cot` dengan dua level. 5 observasi per level. Dependent: `abs_error`.

| obs | cot=off | cot=on |
|---|---:|---:|
| 1 | 18 | 12 |
| 2 | 22 | 11 |
| 3 | 17 | 13 |
| 4 | 19 | 10 |
| 5 | 24 | 14 |
| **mean** | **20** | **12** |

**Langkah 1 — Grand mean:**

```
x̄_grand = (18+22+17+19+24 + 12+11+13+10+14) / 10 = 160 / 10 = 16
```

**Langkah 2 — Group means:** `x̄_off = 20, x̄_on = 12` (sudah dihitung di tabel).

**Langkah 3 — Sum of Squares:**

```
SS_Between = 5·(20 − 16)² + 5·(12 − 16)²
           = 5·16 + 5·16
           = 160

SS_Within  = [(18−20)² + (22−20)² + (17−20)² + (19−20)² + (24−20)²]   # cot=off
           + [(12−12)² + (11−12)² + (13−12)² + (10−12)² + (14−12)²]   # cot=on
           = [4+4+9+1+16] + [0+1+1+4+4]
           = 34 + 10
           = 44

SS_Total   = 160 + 44 = 204
```

**Langkah 4 — Degrees of freedom:**

```
df_Between = 2 − 1 = 1
df_Within  = 10 − 2 = 8
```

**Langkah 5 — Mean Squares:**

```
MS_Between = 160 / 1 = 160
MS_Within  = 44 / 8  = 5.5
```

**Langkah 6 — F-statistic dan p-value:**

```
F = 160 / 5.5 ≈ 29.1
p = P(F_{1, 8} ≥ 29.1) ≈ 0.00065
```

**Interpretasi:** `p ≈ 0.00065 < 0.05`. Tolak hipotesis nol. Perbedaan rata-rata antara `cot=off` (20) dan `cot=on` (12) **secara statistik signifikan** — CoT memang mengurangi error grading pada data toy ini.

### d. Generalisasi ke Three-Way ANOVA

Pada 3-way ANOVA, total SS dipecah menjadi **8 sumber**:

```
SS_Total = SS_A + SS_B + SS_C
         + SS_AB + SS_AC + SS_BC
         + SS_ABC
         + SS_Residual
```

Dengan A=`rubric`, B=`cot`, C=`fewshot`:

| Sumber | Pertanyaan yang dijawab |
|---|---|
| **A** (main effect rubric) | Apakah rata-rata error berbeda antara rubric=on vs rubric=off, *rata-rata di semua kombinasi cot dan fewshot*? |
| **B** (main effect cot) | Apakah rata-rata error berbeda antara cot=on vs cot=off? |
| **C** (main effect fewshot) | Apakah rata-rata error berbeda antara fewshot=on vs fewshot=off? |
| **A:B** (interaksi rubric × cot) | Apakah efek rubric *berbeda* tergantung apakah cot aktif? |
| **A:C** (interaksi rubric × fewshot) | Apakah efek rubric berbeda tergantung apakah fewshot aktif? |
| **B:C** (interaksi cot × fewshot) | Apakah efek cot berbeda tergantung apakah fewshot aktif? |
| **A:B:C** (interaksi 3-arah) | Apakah pola (rubric × cot) sendiri berbeda tergantung fewshot? |
| **Residual** | Sisa variansi yang tidak bisa dijelaskan oleh kombinasi faktor. |

Setiap sumber dapat F-statistic dan p-value tersendiri. Output `statsmodels.anova_lm` adalah tabel 8 baris (7 sumber + residual).

### e. Implementasi praktis

- Library yang direkomendasikan:
  - Python: `statsmodels.formula.api.ols` + `statsmodels.stats.anova.anova_lm(typ=2)`.
  - R: `aov(abs_error ~ rubric * cot * fewshot, data=df)` lalu `summary(...)`; untuk Type II: `car::Anova(model, type=2)`.
- Pada penelitian ini, lihat `experiments/analysis.py:compute_phase1_anova` (line ~121).

---

## 2.Y.7 Interpretasi Hasil

### a. Threshold p-value konvensional

| p-value | Interpretasi |
|---|---|
| `< 0.001` | Bukti sangat kuat ada efek |
| `< 0.01`  | Bukti kuat |
| `< 0.05`  | Threshold konvensional "signifikan" |
| `< 0.1`   | Bukti lemah/sugestif |
| `≥ 0.1`   | Tidak ada bukti efek pada data ini |

**Catatan penulisan:**

- *Statistical significance ≠ practical importance.* Dengan N besar (>1000 baris di Phase 1), efek kecil pun jadi signifikan secara statistik. Wajib laporkan **effect size** bersama p.

### b. Effect size — partial η² (eta-squared)

Effect size mengukur **besarnya** kontribusi setiap sumber variansi:

```
η²_A = SS_A / SS_Total                              # eta-squared
η²_partial_A = SS_A / (SS_A + SS_Residual)          # partial eta-squared
```

Rule of thumb (Cohen, 1988):

| Partial η² | Interpretasi |
|---|---|
| `< 0.01` | Trivial |
| `0.01 – 0.06` | Small |
| `0.06 – 0.14` | Medium |
| `≥ 0.14` | Large |

Effect size membantu membedakan "p kecil karena efek besar" dari "p kecil karena N besar tetapi efek kecil".

### c. Pemeriksaan asumsi

Kalau reviewer ketat, lampirkan:

- **Residual plot** untuk cek homoscedasticity (residual vs fitted).
- **Q-Q plot** residual untuk cek normalitas.
- **Levene's test** untuk homogenitas variansi.
- Kalau asumsi banyak yang gagal: pakai **Welch ANOVA** (tidak asumsi equal variance) atau **Kruskal-Wallis** (non-parametrik).

---

## 2.Y.8 ANOVA vs ICC — Perbandingan Eksplisit

> Ini bagian yang **wajib ada** karena dua metrik dipakai berdampingan di eksperimen ini. Banyak pembaca skripsi yang akan bingung kenapa keduanya muncul; tulis perbandingan eksplisit supaya tidak terlihat redundan.

| Aspek | ANOVA | ICC |
|---|---|---|
| **Pertanyaan inti** | Faktor mana yang menyebabkan mean shift? | Berapa proporsi variansi yang dijelaskan oleh signal vs noise? |
| **Output** | F-statistic + p-value per sumber | Rasio 0–1 + 95% CI |
| **Jenis inference** | Hypothesis testing | Effect-size / reliability |
| **Dipakai di Phase berapa?** | Phase 1 (8 skenario × 144 submission) | Phase 2 (28 submission × 7 replikasi) |
| **Apa yang divariasikan?** | Faktor prompt (rubric, cot, fewshot) — *between-scenario* | Replikasi (waktu pemanggilan) — *within-scenario* |
| **Subjek yang dibandingkan** | Mean error antar grup | Skor LLM yang sama pada submission yang sama |
| **Asumsi tentang LLM** | LLM diperlakukan sebagai **single rater** yang skornya bisa berbeda lintas konfigurasi | LLM diperlakukan sebagai **single rater** yang skornya bisa berbeda lintas panggilan |

**Mekanisme matematis serupa:**

Kedua metrik berakar pada dekomposisi variansi (`SS`, `MS`, `df`). Yang berbeda hanyalah:

1. **Apa yang dipecah:** ANOVA memecah variansi *antar skenario*; ICC memecah variansi *antar submission* dan *antar replikasi*.
2. **Apa yang dilaporkan:** ANOVA melaporkan rasio + p-value (signifikansi); ICC melaporkan rasio langsung sebagai interpretasi reliabilitas.

**Mengapa keduanya dibutuhkan?**

- ANOVA saja tidak cukup: ia bisa bilang "rubric+cot signifikan menurunkan error", tetapi tidak menjawab "kalau aku pakai konfigurasi terbaik dan run ulang, akan dapat skor yang sama?"
- ICC saja tidak cukup: ia bisa bilang "konfigurasi S8 konsisten lintas 7 replikasi", tetapi tidak menjawab "konsistensi itu datang dari *faktor mana*?"

Keduanya **saling melengkapi**: ANOVA mendiagnosis *driver* akurasi, ICC mengukur *stabilitas* hasil terbaik.

> **Catatan penulisan skripsi:** sertakan paragraf eksplisit di metodologi yang mengatakan "Phase 1 dievaluasi dengan 3-way ANOVA untuk atribusi efek prompt, sementara Phase 2 dievaluasi dengan ICC(A,1) untuk stabilitas replikasi pada konfigurasi pemenang. Keduanya bertumpu pada dekomposisi variansi yang sama tetapi menjawab pertanyaan berbeda — atribusi vs reliabilitas." Pernyataan eksplisit semacam ini menyelamatkan pembaca dari kebingungan saat metrik dipertukarkan.

---

## 2.Y.9 Penerapan ANOVA pada Riset Sebelumnya (Opsional)

> Bagian ini opsional, tetapi memperkuat argumen kalau ANOVA adalah pilihan standar di literatur, bukan ad-hoc.

**Yang bisa kamu tulis:**

- ANOVA dalam *automated essay scoring* (AES) untuk menguji apakah feature engineering tertentu meningkatkan korelasi mesin-manusia.
- ANOVA dalam evaluasi prompt-engineering untuk LLM — riset belakangan ini sering memakai ANOVA atau regression dummy untuk mengatribusi efek setiap komponen prompt (chain-of-thought, few-shot, system message, dst).
- ANOVA sebagai standar di bidang lain yang bisa jadi analogi: psikologi eksperimental (manipulasi multi-faktor), uji klinis (treatment × dosis), agronomi (pupuk × varietas).

Identifikasi gap: apakah literatur eksisting mengukur efek faktor prompt-engineering secara terpisah (one factor at a time)? Eksperimen kamu mengisi gap ini dengan desain faktorial penuh + ANOVA, yang dapat menangkap **interaksi** yang akan terlewat dalam evaluasi one-at-a-time.

---

## Daftar Referensi Inti

| Sitasi | Untuk apa |
|---|---|
| Fisher, R. A. (1925) — *Statistical Methods for Research Workers* | Formulasi orisinal ANOVA. |
| Fisher, R. A. (1935) — *The Design of Experiments* | Dasar desain faktorial. |
| Box, G. E. P., Hunter, J. S., & Hunter, W. G. (2005) — *Statistics for Experimenters* | Referensi modern untuk full factorial design. |
| Cohen, J. (1988) — *Statistical Power Analysis for the Behavioral Sciences* | Effect size & power analysis (η², partial η²). |
| Tabachnick, B. G., & Fidell, L. S. (2013) — *Using Multivariate Statistics* | Diskusi Type I/II/III SS dan kapan dipakai. |
| Field, A. (2018) — *Discovering Statistics Using IBM SPSS Statistics* | Penjelasan praktis ANOVA + interaksi untuk skripsi. |

---

## Rekomendasi Gaya Penulisan untuk Bagian Ini

1. **Tulis 2.Y setelah 2.X (ICC) selesai.** Pembaca akan ingat mesin matematika dekomposisi variansi → 2.Y bisa lebih ringkas di bagian formula dan fokus ke perbedaan tujuan.
2. **Pisahkan "definisi" dari "pemilihan".** 2.Y.4 = definisi murni; 2.Y.5 = justifikasi pilihan. Sama polanya dengan ICC.
3. **Tabel ANOVA-vs-ICC di 2.Y.8 adalah halaman *referensi cepat*.** Pembaca skripsi yang skim akan baca tabel itu dulu sebelum prosa.
4. **Selalu pasangkan F dengan p dan effect size.** "F=29.1, p<0.001, partial η²=0.78" jauh lebih informatif dari "F=29.1, p<0.001" saja.
5. **Notasi konsisten dengan literature-icc.md.** Pakai `MS_Between`, `MS_Within` di sini (mirror `MS_BS`, `MS_E` di ICC) supaya pembaca melihat parallelism eksplisit.

---

## Cross-reference

- Implementasi dan komputasi: lihat `experiments/analysis.py:compute_phase1_anova` dan `experiments/analysis.py:format_phase1_anova`.
- Definisi 8 skenario faktorial: lihat `experiments/scenarios.py` dan `docs/design/experiment-plan.md` § Phase 1 — Accuracy.
- Metrik komplementer (konsistensi): lihat `docs/thesis/literature-icc.md`.
- Output ANOVA pada run aktual: lihat `experiments/results/*/summary.txt` (tabel "3-way ANOVA on |human − LLM|").
