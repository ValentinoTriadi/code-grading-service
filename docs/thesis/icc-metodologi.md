# Pengukuran Konsistensi dengan ICC(A,1) (Metodologi)

*Draft subbab Metodologi — versi ringkas: konfigurasi ICC yang dipakai, alasannya, dan cara perhitungannya.*

## Konfigurasi ICC yang Digunakan

Konsistensi sistem penilaian pada penelitian ini diukur menggunakan **ICC(A,1)**, yaitu ICC dengan model *Two-Way Mixed*, bentuk *Single Rater*, tipe *Absolute Agreement*, dan tujuan *Intrarater Reliability*. Pemilihan ini diturunkan secara eksplisit dari keempat dimensi ICC sebagaimana dirangkum pada tabel berikut.

| Dimensi | Pilihan | Alasan |
|---|---|---|
| Model | Two-Way Mixed | Konfigurasi prompt yang dievaluasi merupakan objek tetap yang akan diterapkan, bukan sampel acak dari populasi konfigurasi. |
| Bentuk Pengukuran | Single Rater (k=1) | Sistem yang diterapkan memakai satu kali pemanggilan, bukan rata-rata beberapa pemanggilan. |
| Tipe Agreement | Absolute (A) | Pergeseran nilai sistematis antar-pemanggilan tetap merupakan inkonsistensi yang harus terdeteksi; *consistency* (C) akan menyembunyikannya. |
| Tujuan | Intrarater | "Penilai" yang diukur adalah satu konfigurasi prompt yang sama, hanya berbeda pada waktu pemanggilan. |

Pertimbangan utama adalah bahwa pada pengukuran *self-consistency* LLM, skor yang dilaporkan harus dapat direproduksi pada nilai absolutnya, bukan sekadar pada urutannya. Karena itu *absolute agreement* dipilih, sebab setiap offset konstan antar-pemanggilan pun dihitung sebagai inkonsistensi. Konfigurasi ICC(A,1) ini ekuivalen dengan notasi ICC(2,1) menurut Shrout dan Fleiss (1979) dan setara dengan tipe `"ICC2"` pada pustaka `pingouin` (Python).

## Cara Perhitungan

Skor disusun sebagai matriks berukuran `n × k`, dengan `n` jumlah submission yang dinilai berulang dan `k` jumlah pengulangan pemanggilan terhadap masukan yang identik (pada penelitian ini k = 7). Elemen `xᵢⱼ` menyatakan skor pada submission ke-`i` untuk pemanggilan ke-`j`.

Perhitungan diawali dengan *repeated-measures ANOVA* yang memecah variansi total menjadi *sum of squares* (SS), lalu menormalkannya dengan derajat bebas menjadi *mean square* (MS):

```
MS_BS = SS_rows  / (n − 1)              # between subjects   — variansi antar-submission (sinyal)
MS_BM = SS_cols  / (k − 1)              # between measurements — bias antar-pemanggilan
MS_E  = SS_error / ((n − 1)(k − 1))     # residual            — derau within-submission
```

Nilai ICC(A,1) kemudian dihitung sebagai (McGraw & Wong, 1996; Liljequist dkk., 2019):

```
                       MS_BS − MS_E
ICC(A,1) = ─────────────────────────────────────────────────────
           MS_BS + (k − 1)·MS_E + (k / n)·(MS_BM − MS_E)
```

Penyebut formula menggabungkan tiga sumber variansi: `MS_BS` (sinyal, yaitu perbedaan nyata antar-submission), `(k − 1)·MS_E` (derau within-submission, yaitu inkonsistensi LLM terhadap dirinya sendiri lintas pemanggilan), dan `(k/n)·(MS_BM − MS_E)` (bias sistematis antar-pemanggilan). Suku terakhir inilah yang membedakan *absolute agreement* dari *consistency*, dan menjadi alasan ICC(A,1) mampu menangkap pergeseran nilai yang sistematis.

Sebagai pemeriksaan diagnostik, *consistency* ICC(C,1) — yang identik dengan formula di atas tanpa suku bias pada penyebut — turut dihitung. Selisih antara ICC(C,1) dan ICC(A,1) menjadi indikator besarnya bias sistematis; bila keduanya hampir sama, tidak terdapat pergeseran sistematis antar-pemanggilan (Liljequist dkk., 2019).

Nilai titik (*point estimate*) ICC(A,1) dihitung melalui implementasi pure-Python (`experiments/metrics.py:icc_a1`), sedangkan selang kepercayaan 95% diperoleh menggunakan pustaka `pingouin.intraclass_corr` (tipe `"ICC2"`), dengan aproksimasi normal Fisher-z sebagai cadangan apabila pustaka tersebut tidak tersedia. Nilai ICC dilaporkan beserta selang kepercayaan tersebut, dan ditafsirkan menurut ambang reliabilitas Koo dan Li (2016).
