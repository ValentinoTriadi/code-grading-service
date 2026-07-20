# Analysis of Variance (ANOVA)

Analysis of Variance (ANOVA) merupakan metode statistik untuk menguji apakah perbedaan rata-rata antar kelompok lebih besar daripada yang diharapkan terjadi secara kebetulan. Caranya adalah dengan memecah variansi total dari data menjadi dua komponen: variansi antar-kelompok (*between-group*) dan variansi dalam-kelompok (*within-group*) (Fisher, 1925). Rasio antara kedua komponen tersebut, setelah dinormalisasi dengan derajat bebasnya, menghasilkan *F-statistic*:

```
F = MS_between / MS_within
```

Nilai `F` yang mendekati 1 menunjukkan variansi antar-kelompok tidak lebih besar daripada derau, sehingga tidak ada efek nyata; nilai `F` yang jauh lebih besar dari 1 menunjukkan faktor kelompok memberikan efek yang nyata. Signifikansi efek tersebut diuji melalui *p-value*, yaitu peluang mengamati nilai `F` sebesar itu (atau lebih ekstrem) apabila sebenarnya tidak ada efek sama sekali; *p-value* yang kecil menjadi bukti kuat adanya efek.

Dalam penelitian ini, ANOVA digunakan untuk **atribusi efek**, yaitu menentukan faktor *prompt engineering* mana — struktur rubrik, *chain-of-thought*, dan *few-shot* — yang berkontribusi terhadap akurasi penilaian beserta seberapa besar kontribusinya. Karena ketiga faktor tersebut dikombinasikan secara faktorial penuh (2³ = delapan skenario), ANOVA faktorial memungkinkan pengujian efek utama setiap faktor sekaligus interaksinya dalam satu kerangka — pertanyaan yang tidak dapat dijawab hanya dengan membandingkan dua skenario (Box, Hunter, & Hunter, 2005). Perlu dicatat bahwa ANOVA dan ICC sama-sama bertumpu pada dekomposisi variansi (*sum of squares*, *mean square*, derajat bebas), namun menjawab pertanyaan yang berbeda: ICC mengukur reliabilitas, sedangkan ANOVA mengatribusikan sumber variasi (Liljequist dkk., 2019).

ANOVA dapat diklasifikasikan ke dalam beberapa dimensi yang dipilih sesuai kebutuhan, sebagaimana diuraikan berikut.

## Jumlah Faktor

Dimensi ini menentukan berapa banyak faktor kategorikal yang dianalisis secara bersamaan. **One-Way ANOVA** menguji satu faktor dengan dua level atau lebih. **Two-Way ANOVA** menguji dua faktor sekaligus beserta interaksinya. **n-Way ANOVA** memperluasnya ke lebih dari dua faktor dengan seluruh interaksi orde tinggi. Penelitian ini menggunakan *three-way ANOVA* karena mengombinasikan tiga faktor (`rubric`, `cot`, `fewshot`) secara faktorial.

## Tipe Sum of Squares

Ketika terdapat lebih dari satu faktor, kontribusi tiap faktor dihitung dengan terlebih dahulu "mengeluarkan" pengaruh faktor lain, dan cara mengeluarkan inilah yang membedakan tipe *sum of squares* (SS). **Type I** bersifat sekuensial sehingga hasilnya bergantung pada urutan faktor. **Type II** menyesuaikan setiap efek utama terhadap efek utama lain, namun tanpa memperhitungkan interaksi. **Type III** menyesuaikan setiap efek terhadap semua efek lain termasuk interaksi. Pada desain yang seimbang (*balanced*), ketiga tipe menghasilkan nilai yang sama; namun pada desain tidak seimbang (*unbalanced*), ketiganya berbeda sehingga pemilihan tipe menjadi krusial. Untuk data tidak seimbang, Langsrud (2003) menganjurkan penggunaan Type II dibanding Type III karena Type II memiliki *statistical power* yang lebih baik untuk pengujian efek utama.

## Fixed Effects dan Random Effects

Dimensi ini menentukan bagaimana level faktor diperlakukan. Pada **fixed effects**, level faktor adalah level spesifik yang memang ingin diuji, bukan sampel dari suatu populasi level — misalnya `rubric` ∈ {aktif, nonaktif}, di mana peneliti tertarik tepat pada kedua level tersebut. Pada **random effects**, level faktor merupakan sampel acak dari populasi level yang lebih besar. Penelitian ini menggunakan *fixed effects*, sebab setiap level faktor adalah konfigurasi konkret yang dipertimbangkan untuk diterapkan.

## Balanced dan Unbalanced Design

Desain disebut **balanced** apabila jumlah observasi sama untuk setiap kombinasi level (sel), dan **unbalanced** apabila jumlahnya tidak sama. Pada penelitian ini desain bersifat *unbalanced*: skenario tanpa *chain-of-thought* menghasilkan jauh lebih sedikit keluaran yang dapat di-parse menjadi skor valid. Ketidakseimbangan ini bukan sekadar gangguan, melainkan sinyal yang substantif — sebab *parse rate* merupakan aspek utama dari *deployability*, sehingga akurasi (yang diuji melalui ANOVA) memang sepatutnya diukur hanya pada keluaran yang dapat diterapkan, yaitu yang berhasil di-parse. Konsekuensinya, analisis dilakukan pada data yang tidak seimbang, dan pemilihan Type II *sum of squares* menjadi pilihan yang tepat untuk kondisi ini (Langsrud, 2003).

## Ukuran Efek (Effect Size)

Nilai `F` dan *p-value* hanya menyatakan apakah suatu efek signifikan, bukan seberapa besar magnitudonya. Untuk itu digunakan ukuran efek *partial eta-squared* (η²p), yaitu proporsi variansi yang dapat diatribusikan kepada suatu faktor setelah memperhitungkan residual:

```
η²p = SS_effect / (SS_effect + SS_residual)
```

Magnitudo η²p ditafsirkan menurut ambang yang diusulkan Cohen (1988): nilai sekitar 0,01 tergolong kecil (*small*), 0,06 sedang (*medium*), dan 0,14 besar (*large*). Pelaporan ukuran efek penting karena pada ukuran sampel yang besar, sebuah efek dapat signifikan secara statistik namun sangat kecil secara praktis.

---

*Referensi yang dipakai pada bagian ini: Fisher (1925); Box, Hunter, & Hunter (2005); Langsrud (2003); Cohen (1988); serta Liljequist dkk. (2019).*
