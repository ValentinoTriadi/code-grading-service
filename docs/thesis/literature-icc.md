# Studi Literatur — Konsistensi & ICC

Bagian Tinjauan Pustaka untuk pembahasan **konsistensi sistem** dan **Intraclass Correlation Coefficient (ICC)**. Alur penyajian mengikuti prinsip: definisikan dulu seluruh dimensi → baru pilih konfigurasinya → baru hitung → baru interpretasi, agar penalaran mudah diikuti dan "pengenalan" tidak bercampur dengan "justifikasi pilihan".

---

## 2.X.1 Konsistensi sebagai Aspek Reliabilitas

Konsistensi adalah aspek reliabilitas yang merujuk pada *run-to-run reliability*, yaitu seberapa stabil keluaran sebuah sistem ketika diberi input yang identik secara berulang. Untuk sistem penilaian otomatis berbasis *Large Language Model* (LLM), konsistensi merupakan syarat krusial menuju penerapan (*deployment*): keputusan produksi menuntut skor yang dapat direproduksi, sebab sistem yang akurat secara rata-rata namun berfluktuasi pada setiap pemanggilan sulit dipercaya dan diaudit oleh pengguna.

Konsistensi perlu dibedakan secara tegas dari akurasi. Akurasi membandingkan keluaran sistem terhadap referensi eksternal — dalam konteks ini, skor penilai manusia — sedangkan konsistensi membandingkan keluaran sistem terhadap dirinya sendiri pada pemanggilan yang berbeda. Kedua properti ini saling independen: sebuah sistem dapat konsisten namun keliru (selalu memberi skor sama tetapi salah), atau akurat secara rata-rata namun tidak stabil pada tiap pemanggilan. Konsep reliabilitas semacam ini berakar pada literatur klasik teori pengukuran (Cronbach, 1951; Shrout & Fleiss, 1979).

---

## 2.X.2 Pemilihan Metrik Konsistensi

Sejumlah koefisien kesepakatan (*agreement*) lazim digunakan untuk mengukur reliabilitas, namun masing-masing memiliki keterbatasan untuk pertanyaan konsistensi *single-rater* pada data kontinu seperti pada penelitian ini:

| Metrik | Kelemahan untuk kasus ini |
|---|---|
| Pearson r | Hanya mengukur korelasi linier; mengabaikan offset sistematis (bias). Dua pengukuran yang selalu berselisih konstan tetap menghasilkan r = 1. |
| Cohen's κ | Dirancang untuk dua rater pada data kategorikal, bukan skor kontinu. |
| Krippendorff α | Generalisasi yang fleksibel, tetapi terlalu umum untuk pertanyaan single-rater. |
| Cronbach α | Cocok untuk reliabilitas internal kuesioner (banyak item), bukan satu skor yang diukur ulang. |

ICC dipilih karena dirancang khusus untuk *multiple ratings* terhadap subjek yang sama, mendukung mode *absolute agreement* yang peka terhadap offset sistematis, dan memiliki bentuk formula khusus untuk kasus *single-rater*. Berbeda dari Pearson r, ICC menghitung kesepakatan pada nilai absolut, bukan sekadar pola — properti yang esensial ketika skor yang dilaporkan harus dapat direproduksi pada angkanya, bukan hanya pada urutannya.

---

## 2.X.3 Pengenalan ICC (Intraclass Correlation Coefficient)

*Intraclass Correlation Coefficient* (ICC) adalah koefisien yang mengukur reliabilitas pengukuran sebagai **rasio antara variansi yang menjadi perhatian (variansi antar-subjek) terhadap variansi total** (Liljequist dkk., 2019):

```
ICC = σ²(between) / [σ²(between) + σ²(within)]
```

Konsep ini pertama diperkenalkan oleh Fisher pada paruh awal abad ke-20, kemudian diformalkan dalam kerangka analisis variansi (ANOVA) oleh Bartko (1966), diklasifikasikan ke dalam enam bentuk klasik oleh Shrout dan Fleiss (1979), dan direklasifikasi secara sistematis menurut {model × bentuk × tipe} oleh McGraw dan Wong (1996). Secara intuitif, ICC dapat dipahami sebagai *rasio sinyal terhadap derau*: pembilangnya adalah variansi "sinyal" — seberapa berbeda satu subjek dari subjek lain — sedangkan penyebutnya mencakup pula "derau", yaitu variasi yang tidak diinginkan dalam pengukuran berulang terhadap subjek yang sama. Semakin besar variansi antar-subjek relatif terhadap derau, semakin tinggi ICC, yang menandakan metode pengukuran mampu membedakan subjek dengan andal.

Nilai ICC berkisar secara nominal antara 0 dan 1. Secara teknis nilai dapat negatif untuk formula tertentu (misalnya ketika `MS_BS < MS_E` akibat ukuran sampel yang kecil), namun nilai semacam itu hanyalah estimasi yang kurang beruntung dan dalam praktik diinterpretasikan sebagai 0 (Liljequist dkk., 2019).

---

## 2.X.4 Klasifikasi ICC

Bagian ini **mendefinisikan** seluruh dimensi pilihan ICC. Pemilihan konfigurasi konkret untuk eksperimen ditunda ke 2.X.5 agar alur argumentasi tidak meloncat. McGraw dan Wong (1996) menyusun ICC ke dalam empat dimensi yang saling ortogonal: model, bentuk pengukuran, tipe agreement, dan tujuan pengukuran.

### a. Model — bagaimana rater dipilih

| Model | Definisi | Kapan dipakai |
|---|---|---|
| One-Way Random | Rater berbeda untuk setiap subjek; rater dipandang sebagai sampel random. | Penilai tidak konsisten antar subjek. |
| Two-Way Random | Semua subjek dinilai oleh rater yang sama; rater adalah sampel random dari populasi rater. | Hasilnya ingin digeneralisasi ke rater lain di luar studi. |
| Two-Way Mixed | Semua subjek dinilai oleh rater yang sama; rater adalah objek tetap, bukan sampel. | Rater yang dipakai adalah satu-satunya yang akan dinilai. |

**Sitasi:** McGraw & Wong (1996); Liljequist dkk. (2019).

Perlu dicatat bahwa Liljequist dkk. (2019) menunjukkan, dalam konteks studi reliabilitas, **Two-Way Random dan Two-Way Mixed menghasilkan formula ICC yang identik secara matematis**; perbedaan keduanya semata-mata terletak pada *niat generalisasi* (apakah rater dipandang sebagai sampel acak atau objek tetap), bukan pada perhitungannya.

### b. Bentuk pengukuran — single vs average

- **ICC(·,1)** — single rater: generalisasi ke pengukuran satu rater.
- **ICC(·,k)** — average rater: generalisasi ke rata-rata k rater.

Pilihan bergantung pada *bagaimana skor akan dipakai* dalam praktik. Bila deployment hanya memakai satu pemanggilan LLM, gunakan ICC(·,1); bila deployment merata-ratakan k pemanggilan, gunakan ICC(·,k).

### c. Tipe agreement — absolute vs consistency

| Tipe | Definisi | Sensitif terhadap |
|---|---|---|
| **Absolute Agreement (A)** | Sepakat pada **nilai** absolutnya. | Bias sistematis antar rater/run (offset). |
| **Consistency (C)** | Sepakat pada **pola** (urutan / korelasi). | Tidak peka terhadap offset; hanya pola. |

Contoh: jika Run 1 selalu memberikan skor 5 poin lebih tinggi dari Run 2 untuk semua submission, **Consistency** akan tinggi (pola sama), tetapi **Absolute Agreement** akan rendah (nilai berbeda secara konstan).

**Sitasi:** McGraw & Wong (1996).

### d. Tujuan pengukuran — intrarater vs interrater

| Tujuan | Definisi | Konteks |
|---|---|---|
| **Intrarater reliability** | Konsistensi **satu** penilai yang sama menilai **subjek yang sama** di **waktu berbeda**. | Test-retest reliability, *self-consistency*. |
| **Interrater reliability** | Agreement antar **penilai yang berbeda** terhadap **subjek yang sama**. | Multi-rater agreement. |

**Sitasi:** Koo & Li (2016).

---

## 2.X.5 Pemilihan Konfigurasi ICC untuk Eksperimen Ini

Bagian ini adalah inti argumentasi: setiap pilihan dibangun dari empat dimensi pada 2.X.4 dan diberi alasan eksplisit.

| Dimensi | Pilihan | Alasan |
|---|---|---|
| **Model** | Two-Way Mixed | Konfigurasi prompt LLM adalah **objek tetap** yang akan di-deploy, bukan sampel random dari populasi konfigurasi. |
| **Bentuk pengukuran** | Single rater (k=1) | Yang akan di-deploy adalah **satu** konfigurasi pemanggilan, bukan rata-rata k panggilan. |
| **Tipe agreement** | Absolute (A) | Bias sistematis antar run (offset konstan) tetap merupakan bentuk inkonsistensi yang harus terdeteksi. Consistency (C) akan menyembunyikannya. |
| **Tujuan** | Intrarater | "Penilai" yang diukur adalah **satu** konfigurasi prompt yang sama, hanya berbeda di waktu pemanggilan. |

Berdasarkan empat pilihan di atas, pengukuran konsistensi pada eksperimen ini menggunakan **ICC(A,1)** — Two-Way Mixed Model, Absolute Agreement, Single-Rater Form, Intrarater Reliability. Untuk menghindari kebingungan akibat banyaknya nama bagi konfigurasi yang sama, berikut tabel ekuivalensi notasi:

| Notasi | Sumber |
|---|---|
| ICC(A,1) | McGraw & Wong (1996) — *absolute agreement, single* |
| ICC(2,1) | Shrout & Fleiss (1979) — bentuk klasik ke-2, single |
| Two-Way Mixed, Absolute, Single | deskripsi {model × tipe × bentuk} |
| `"ICC2"` | notasi paket `pingouin` (Python) |

Pemilihan ICC(A,1) sebagai metrik utama didasari pertimbangan bahwa pada pengukuran *self-consistency* LLM, setiap pergeseran nilai antar-pemanggilan — termasuk offset yang konstan — merupakan bentuk inkonsistensi yang tidak dapat ditoleransi, karena skor yang dilaporkan ke pengguna harus dapat direproduksi pada nilai absolutnya, bukan sekadar pada urutannya. Konsekuensinya, *consistency agreement* (ICC(C,1)) tidak memadai sebagai metrik utama sebab ia secara desain mengabaikan offset tersebut.

Meskipun demikian, Liljequist dkk. (2019) menganjurkan agar ketiga koefisien single-score — ICC(1), ICC(A,1), dan ICC(C,1) — dihitung dan dibandingkan, alih-alih mengunci satu model di awal. Penelitian ini mengadopsi rekomendasi tersebut bukan untuk mengubah metrik utama, melainkan sebagai **prosedur diagnostik** (lihat 2.X.6d): ICC(A,1) tetap dilaporkan sebagai metrik konsistensi utama, sementara perbandingannya dengan ICC(C,1) beserta uji-F digunakan untuk memastikan apakah inkonsistensi yang terdeteksi berasal dari derau acak atau dari bias sistematis antar-pemanggilan.

---

## 2.X.6 Komputasi ICC(A,1)

### a. Representasi data

Data konsistensi disusun sebagai matriks berukuran `n × k`, dengan baris mewakili subjek dan kolom mewakili pengukuran berulang:

- `n` = jumlah submission yang dinilai berulang
- `k` = jumlah perulangan (pada eksperimen ini, k = 7)

| Submission | Run 1 | Run 2 | … | Run k |
|---|---|---|---|---|
| M₁  | x₁₁ | x₁₂ | … | x₁ₖ |
| M₂  | x₂₁ | x₂₂ | … | x₂ₖ |
| ⋮   | ⋮ | ⋮ | ⋮ | ⋮ |
| Mₙ  | xₙ₁ | xₙ₂ | … | xₙₖ |

Elemen `xᵢⱼ` adalah skor yang diberikan pada submission ke-`i` pada pemanggilan ke-`j`. Dari matriks ini dihitung rata-rata baris `x̄ᵢ` (rata-rata skor tiap submission), rata-rata kolom `x̄ⱼ` (rata-rata skor tiap pemanggilan), dan grand mean `x̄`. Perhitungan ICC mengasumsikan beberapa hal yang perlu disebutkan secara eksplisit:

- Independensi antar observasi (skor antar run tidak saling memengaruhi).
- Residual mendekati normal — umumnya terpenuhi untuk skor 0–100 dengan banyak submission.
- Tidak ada interaksi sistematis submission × run yang besar.

### b. Langkah perhitungan

Diberikan matriks `n × k` (baris = submission, kolom = replikasi), perhitungan ICC(A,1) memecah variansi total menjadi tiga sumber dan menggabungkannya menjadi rasio sinyal-terhadap-derau.

#### Langkah 1 — Grand mean

Rata-rata seluruh sel pada matriks:

```
x̄_grand = (1 / (n · k)) · Σᵢ Σⱼ xᵢⱼ
```

Nilai ini menjadi *baseline* untuk seluruh dekomposisi variansi berikutnya.

#### Langkah 2 — Row means (rata-rata per submission)

```
x̄ᵢ = (1 / k) · Σⱼ xᵢⱼ           untuk setiap submission i
```

Spread antar `x̄ᵢ` mewakili *signal* yang ingin ditangkap: seberapa berbeda satu submission dari yang lain. Bila LLM membedakan dengan baik, row means tersebar lebar.

#### Langkah 3 — Column means (rata-rata per replikasi)

```
x̄ⱼ = (1 / n) · Σᵢ xᵢⱼ           untuk setiap replikasi j
```

Bila ada bias sistematis antar run (misal Run 5 sistematis 2 poin lebih tinggi dari Run 1), column means akan bergeser. Inilah komponen *absolute agreement* yang tidak ditangkap oleh `ICC(C,1)`.

#### Langkah 4 — Sum of Squares (dekomposisi variansi)

Tiga komponen utama, ditambah residual:

```
SS_rows  = k · Σᵢ (x̄ᵢ − x̄_grand)²              # variansi antar submission (signal)
SS_cols  = n · Σⱼ (x̄ⱼ − x̄_grand)²              # variansi antar replikasi (rater bias)
SS_total = Σᵢ Σⱼ (xᵢⱼ − x̄_grand)²              # variansi total semua sel
SS_error = SS_total − SS_rows − SS_cols          # sisa = noise within-submission
```

Identitas `SS_total = SS_rows + SS_cols + SS_error` berlaku ketika asumsi independensi terpenuhi (lihat 2.X.6a).

#### Langkah 5 — Mean Squares (normalisasi dengan derajat bebas)

```
MS_BS = SS_rows  / (n − 1)                       # mean square between subjects
MS_BM = SS_cols  / (k − 1)                       # mean square between measurements (raters)
MS_E  = SS_error / ((n − 1) · (k − 1))           # mean square error / residual
```

Ketiga mean square ini adalah estimator dari komponen variansi yang mendasari model. Mengikuti relasi *expected mean square* untuk model dua arah (Liljequist dkk., 2019), `MS_BS` mengestimasi `k·σ²_r + σ²_v`, `MS_BM` mengestimasi `n·σ²_c + σ²_v`, dan `MS_E` mengestimasi `σ²_v`, dengan `σ²_r` variansi skor sejati antar-submission (sinyal), `σ²_c` variansi bias sistematis antar-pemanggilan, dan `σ²_v` variansi derau acak. Intuisinya:

- `MS_BS` tinggi → submission benar-benar berbeda satu sama lain.
- `MS_E` tinggi → submission yang sama dinilai berbeda lintas replikasi (LLM tidak konsisten dengan dirinya sendiri).
- `MS_BM` tinggi → ada bias replikasi yang sistematis.

*(Catatan pemetaan notasi: `MS_BS`, `MS_BM`, `MS_E` di sini setara dengan `MSBS`, `MSBM`, `MSE` pada Liljequist dkk. (2019) dan McGraw & Wong (1996).)*

#### Langkah 6 — Formula ICC(A,1)

```
                       MS_BS − MS_E
ICC(A,1) = ─────────────────────────────────────────────────────
           MS_BS + (k − 1)·MS_E + (k / n)·(MS_BM − MS_E)
```

Tiga komponen di penyebut mewakili tiga sumber derau yang berbeda — dan inilah yang membedakan **Absolute Agreement** dari **Consistency**:

| Komponen | Apa yang ditangkap |
|---|---|
| `MS_BS` (numerator) | Variansi *signal* — perbedaan antar submission. |
| `(k − 1) · MS_E` | Noise within-submission lintas replikasi — **inkonsistensi LLM ke dirinya sendiri**. |
| `(k / n) · (MS_BM − MS_E)` | Bias sistematis antar replikasi (offset konstan antar run). Inilah yang dihilangkan oleh `ICC(C,1)`. |

Catatan: nilai `MS_BM − MS_E` dapat negatif bila bias antar replikasi sangat kecil. Penyebut tetap valid karena `MS_BS` yang besar akan mendominasi.

### c. Diagnostik bias antar-pemanggilan (ICC(C,1) dan uji-F)

Sebagaimana dianjurkan pada 2.X.5, ICC(A,1) dilaporkan sebagai metrik utama, namun ICC(C,1) dihitung sebagai pembanding diagnostik. Bentuk *consistency* memiliki formula yang sama dengan ICC(A,1) tanpa suku bias pada penyebut:

```
                       MS_BS − MS_E
ICC(C,1) = ───────────────────────────────
           MS_BS + (k − 1)·MS_E
```

Liljequist dkk. (2019) menunjukkan bahwa `ICC(C,1) ≥ ICC(A,1)` selalu berlaku, dan **selisih keduanya merupakan indikator besarnya bias sistematis** antar-pemanggilan. Apabila `ICC(A,1) ≈ ICC(C,1)`, dapat disimpulkan tidak ada pergeseran sistematis antar-run; sebaliknya, `ICC(C,1)` yang jauh lebih besar menandakan adanya bias. Untuk mengonfirmasi secara formal, digunakan uji-F atas variansi antar-pemanggilan:

```
F = MS_BM / MS_E
```

Nilai `F` yang mendekati 1 dengan p-value tinggi menunjukkan tidak ada perbedaan sistematis yang signifikan antar-pemanggilan, sehingga ICC(A,1) valid dilaporkan sebagai estimasi konsistensi yang utuh.

### d. Contoh perhitungan terverifikasi (worked example)

Untuk memudahkan validasi pembaca dan implementasi, di bawah ini contoh komputasi penuh dengan matriks kecil yang dapat dihitung manual.

**Setup:** `n = 3` submission, `k = 4` replikasi. Skor LLM:

|         | Rep 1 | Rep 2 | Rep 3 | Rep 4 |
|---------|------:|------:|------:|------:|
| Sub A   | 90    | 92    | 88    | 90    |
| Sub B   | 75    | 72    | 78    | 75    |
| Sub C   | 60    | 58    | 62    | 60    |

LLM ini cukup konsisten — variasi per submission kecil (~2 poin) sementara variasi antar submission besar (30 poin).

**Langkah 1 — Grand mean:**

```
x̄_grand = (90+92+88+90 + 75+72+78+75 + 60+58+62+60) / 12 = 900 / 12 = 75
```

**Langkah 2 — Row means:**

```
x̄_A = (90+92+88+90) / 4 = 90
x̄_B = (75+72+78+75) / 4 = 75
x̄_C = (60+58+62+60) / 4 = 60
```

**Langkah 3 — Column means:**

```
x̄_1 = (90+75+60) / 3 = 75
x̄_2 = (92+72+58) / 3 = 74
x̄_3 = (88+78+62) / 3 = 76
x̄_4 = (90+75+60) / 3 = 75
```

Column means hampir sama (74–76) → bias sistematis antar replikasi sangat kecil.

**Langkah 4 — Sum of Squares:**

```
SS_rows  = 4 · [(90−75)² + (75−75)² + (60−75)²]
         = 4 · [225 + 0 + 225] = 1800

SS_cols  = 3 · [(75−75)² + (74−75)² + (76−75)² + (75−75)²]
         = 3 · [0 + 1 + 1 + 0] = 6

SS_total = Σ (xᵢⱼ − 75)²
         = 908 + 18 + 908       # row A, B, C
         = 1834

SS_error = 1834 − 1800 − 6 = 28
```

**Langkah 5 — Mean Squares:**

```
MS_BS = 1800 / (3 − 1)            = 900
MS_BM =    6 / (4 − 1)            =   2
MS_E  =   28 / ((3 − 1)·(4 − 1))  =   28 / 6 ≈ 4.67
```

**Langkah 6 — ICC(A,1):**

```
numerator   = 900 − 4.67 = 895.33

denominator = 900 + (4 − 1) · 4.67 + (4 / 3) · (2 − 4.67)
            = 900 + 14.00 + 1.333 · (−2.67)
            = 900 + 14.00 − 3.56
            = 910.44

ICC(A,1)    = 895.33 / 910.44 ≈ 0.983
```

**Interpretasi:** `0.983 → excellent` menurut threshold Koo & Li (lihat 2.X.7). LLM hampir sempurna dalam memberikan skor identik lintas replikasi untuk setiap submission.

Sebagai pembanding dengan angka riil yang dapat disitasi, Liljequist dkk. (2019) memberikan contoh klinis dengan `n = 10` subjek dan `k = 3` pengukuran berulang, menghasilkan `MS_BS = 212{,}61`, `MS_BM = 39{,}15`, dan `MS_E = 24{,}45`. Substitusi menghasilkan `ICC(A,1) = 188{,}16 / 265{,}92 ≈ 0{,}708` dan `ICC(C,1) ≈ 0{,}720`, dengan `F = 39{,}15 / 24{,}45 ≈ 1{,}601` (p = 0,229). Karena `ICC(A,1) ≈ ICC(C,1)` dan uji-F tidak signifikan, bias sistematis antar-pengukuran dapat diabaikan — sebuah contoh konkret bahwa selisih kecil antara kedua koefisien menandakan absennya bias.

### e. Implementasi praktis

- Library yang direkomendasikan untuk verifikasi:
  - Python: `pingouin.intraclass_corr` — tipe `"ICC2"` (notasi pingouin) sama dengan `ICC(A,1)`.
  - R: `irr::icc(model="twoway", type="agreement", unit="single")`.
- Keuntungan library: keluaran sudah termasuk **95% confidence interval** dan p-value.
- Pada penelitian ini implementasi pure-Python ada di `experiments/metrics.py:icc_a1` (untuk minimal-deps), divalidasi terhadap pingouin.

---

## 2.X.7 Interpretasi Koefisien

Untuk menerjemahkan nilai ICC menjadi kategori reliabilitas, penelitian ini memakai ambang standar dari **Koo & Li (2016)** — panduan yang paling sering disitasi:

| Rentang | Interpretasi |
|---|---|
| `< 0.5` | Poor reliability |
| `0.5 – 0.75` | Moderate reliability |
| `0.75 – 0.90` | Good reliability |
| `≥ 0.90` | Excellent reliability |

Dua catatan penting dalam pelaporan. Pertama, *point estimate* wajib dilaporkan bersama **95% confidence interval (CI)**, sebab keduanya membawa informasi yang sangat berbeda: nilai `0.85` dengan CI `[0.6, 0.95]` jauh lebih tidak pasti dibanding `0.85` dengan CI `[0.82, 0.88]`. Koo & Li (2016) bahkan menganjurkan kategorisasi berdasarkan **batas bawah CI**, bukan point estimate, agar klaim reliabilitas bersifat konservatif. Kedua, perlu ditetapkan **batas keberterimaan** sistem secara eksplisit (misalnya menargetkan ICC ≥ 0.75) beserta alasannya — apakah berdasarkan ambang deployment, perbandingan terhadap reliabilitas antar-penilai manusia, atau pertimbangan lain.

---

## 2.X.8 Penerapan ICC pada Riset Sebelumnya

ICC telah lama menjadi standar dalam evaluasi reliabilitas di berbagai bidang. Pada *automated essay scoring* (AES), ICC banyak dipakai untuk membandingkan skor mesin dengan penilai manusia; di luar pemrosesan bahasa, ICC menjadi tolok ukur baku untuk *test-retest reliability* psikometri serta reliabilitas pengukuran pada *medical imaging* — konteks-konteks yang dapat dijadikan analogi bagi pengukuran konsistensi sistem penilaian.

Dalam konteks evaluasi LLM, ICC mulai digunakan untuk memeriksa stabilitas keluaran model pada inferensi berulang. Jukiewicz dkk. menggunakan ICC untuk memeriksa sejauh mana perbedaan nilai tugas yang diberikan oleh LLM selama inferensi berulang kali — penerapan yang sejalan langsung dengan pertanyaan konsistensi pada penelitian ini. Relatif sedikitnya literatur yang mengukur konsistensi LLM-as-judge secara kuantitatif dengan ICC justru menandai *gap* yang berusaha diisi oleh penelitian ini.

> *Lengkapi entri sitasi Jukiewicz dkk. (tahun, judul, venue) pada daftar pustaka.*

---

## Daftar Referensi Inti

| Sitasi | Untuk apa |
|---|---|
| Shrout, P. E., & Fleiss, J. L. (1979) | Formulasi orisinal ICC + 6 bentuk klasik (ICC(1,1), ICC(2,1), ICC(3,1), dst). |
| McGraw, K. O., & Wong, S. P. (1996) | Reklasifikasi ICC ke {Model × Form × Type}: ICC(A,1) vs ICC(C,1) dst. |
| Koo, T. K., & Li, M. Y. (2016) | Panduan praktis pemilihan model + threshold interpretasi yang paling sering disitasi. |
| Liljequist, D., Elfving, B., & Skavberg Roaldsen, K. (2019) | Re-analisis ICC single-score; relasi EMS, formula ICC(1)/ICC(A,1)/ICC(C,1), uji-F bias, contoh klinis terverifikasi. |
| Hallgren, K. A. (2012) | "Computing Inter-Rater Reliability for Observational Data" — panduan praktis di software, contoh hitungan. |
| Bartko, J. J. (1966) | ICC awal pada konteks variance components. |
| Cronbach, L. J. (1951) | Latar belakang reliability theory secara umum. |
| Jukiewicz dkk. | Penerapan ICC untuk konsistensi nilai LLM pada inferensi berulang *(lengkapi metadata)*. |

---

## Cross-reference

- Implementasi dan komputasi: lihat `experiments/metrics.py:icc_a1` dan `experiments/analysis.py:compute_icc`.
- Desain eksperimen + jumlah replikasi (k=7) + ukuran sampel: lihat `docs/design/experiment-plan.md` § Phase 2 — Consistency.
- Threshold yang dipakai untuk *go/no-go* deployment: lihat `docs/design/experiment-plan.md` § Selection criterion.
