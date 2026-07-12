# Intraclass Correlation Coefficient (ICC)

Intraclass Correlation Coefficient (ICC) merupakan metrik yang menggambarkan rasio antara variansi sistematis (variansi antar-subjek) terhadap variansi total. Metrik ini lazim digunakan untuk mengukur seberapa *reliable* suatu sistem pengukuran. Secara intuitif, ICC dapat dipahami sebagai rasio sinyal terhadap derau: pembilangnya menyatakan seberapa besar perbedaan nyata antar-subjek (sinyal), sedangkan penyebutnya turut mencakup variasi yang tidak diinginkan ketika subjek yang sama diukur berulang kali (derau). Semakin besar variansi antar-subjek relatif terhadap derau, semakin tinggi nilai ICC, yang menandakan bahwa metode pengukuran mampu membedakan subjek satu dengan lainnya secara konsisten. Nilai ICC berkisar antara 0 hingga 1, dengan nilai yang lebih tinggi menunjukkan reliabilitas yang lebih baik (Liljequist dkk., 2019).

Dalam konteks evaluasi LLM, ICC telah digunakan oleh Jukiewicz dkk. untuk memeriksa sejauh mana perbedaan nilai tugas yang diberikan oleh LLM selama inferensi yang dilakukan berulang kali. Penggunaan semacam ini relevan karena keluaran LLM bersifat probabilistik: pemanggilan yang diulang terhadap masukan yang identik dapat menghasilkan skor yang berbeda, dan ICC menyediakan ukuran kuantitatif atas kestabilan tersebut. Berbeda dari koefisien korelasi Pearson yang hanya menangkap keselarasan pola dan mengabaikan pergeseran nilai yang sistematis, ICC dirancang khusus untuk menilai kesepakatan pada pengukuran berulang terhadap subjek yang sama (Shrout & Fleiss, 1979).

ICC tidak bersifat tunggal. Koefisien ini dapat diklasifikasikan ke dalam beberapa dimensi, dan kombinasi pilihan pada setiap dimensi menentukan formula serta makna ICC yang dihasilkan. Pemilihan konfigurasi harus disesuaikan dengan situasi pengukuran, sebab penerapan formula yang tidak sesuai dapat menghasilkan kesimpulan yang keliru (McGraw & Wong, 1996). Keempat dimensi tersebut diuraikan sebagai berikut.

## Model

Dimensi model menentukan bagaimana penilai (*rater*) diperlakukan secara statistik, dan dengan demikian menentukan sejauh mana kesimpulan reliabilitas dapat digeneralisasi. Terdapat tiga model.

Pada **One-Way Random**, setiap subjek dinilai oleh penilai yang berbeda, dan penilai-penilai tersebut dipandang sebagai sampel acak. Model ini sesuai ketika tidak ada penilai yang sama menilai seluruh subjek. Pada **Two-Way Random**, semua subjek dinilai oleh sekumpulan penilai yang sama, dan penilai dipandang sebagai sampel acak dari suatu populasi penilai; konsekuensinya, hasil reliabilitas dapat digeneralisasi ke penilai lain di luar studi. Pada **Two-Way Mixed**, semua subjek juga dinilai oleh penilai yang sama, tetapi penilai dipandang sebagai objek tetap, yaitu satu-satunya penilai yang menjadi perhatian, sehingga kesimpulan hanya berlaku bagi penilai tersebut. Perlu dicatat bahwa Liljequist dkk. (2019) menunjukkan model Two-Way Random dan Two-Way Mixed menghasilkan formula ICC yang identik secara matematis; perbedaan keduanya semata-mata terletak pada niat generalisasi, bukan pada perhitungannya.

## Bentuk Pengukuran

Dimensi bentuk pengukuran menentukan apakah reliabilitas yang dihitung berlaku untuk satu pengukuran tunggal atau untuk rata-rata beberapa pengukuran. Bentuk **Single Rater**, dinotasikan ICC(·,1), menyatakan reliabilitas dari satu kali pengukuran tunggal. Bentuk **Average Rater**, dinotasikan ICC(·,k), menyatakan reliabilitas dari rata-rata k pengukuran, dan umumnya menghasilkan nilai yang lebih tinggi karena proses perata-rataan menekan derau acak. Pemilihan bergantung pada bagaimana skor akan digunakan dalam praktik: bila keputusan akhir hanya didasarkan pada satu pengukuran, bentuk single rater yang tepat; bila keputusan didasarkan pada rata-rata sejumlah pengukuran, bentuk average rater yang relevan.

## Tipe Agreement

Dimensi tipe agreement menentukan aspek kesepakatan yang diukur. **Absolute Agreement** (A) menilai kesepakatan pada nilai absolut, sehingga peka terhadap bias atau pergeseran (*offset*) sistematis antar-pengukuran. **Consistency** (C) hanya menilai kesepakatan pada pola atau urutan relatif antar-subjek, dan mengabaikan offset sistematis. Perbedaan keduanya dapat diilustrasikan sebagai berikut: apabila satu pengukuran secara konsisten memberikan skor lima poin lebih tinggi daripada pengukuran lain untuk semua subjek, koefisien Consistency akan tetap tinggi karena pola peringkatnya sama, sedangkan koefisien Absolute Agreement akan menurun karena nilai absolutnya berbeda secara konstan (McGraw & Wong, 1996). Pemilihan di antara keduanya bergantung pada apakah kesepakatan nilai absolut merupakan syarat, atau cukup kesepakatan pada pola.

## Tujuan Pengukuran

Dimensi tujuan pengukuran menentukan jenis reliabilitas yang ingin disimpulkan. **Intrarater Reliability** mengukur konsistensi satu penilai yang sama ketika menilai subjek yang sama pada waktu yang berbeda; tujuan ini berkaitan dengan *self-consistency* atau *test-retest reliability*. **Interrater Reliability** mengukur kesepakatan antar penilai yang berbeda terhadap subjek yang sama. Dengan kata lain, intrarater menyoroti kestabilan internal satu penilai, sedangkan interrater menyoroti keselarasan antar penilai yang berbeda (Koo & Li, 2016).

## Interpretasi Nilai ICC

Setelah dihitung, nilai ICC perlu diterjemahkan menjadi kategori reliabilitas. Panduan yang paling sering disitasi adalah ambang yang diusulkan oleh Koo dan Li (2016), sebagaimana ditampilkan pada tabel berikut.

| Rentang nilai ICC | Tingkat reliabilitas |
|---|---|
| `< 0,5` | Buruk (*poor*) |
| `0,5 – 0,75` | Sedang (*moderate*) |
| `0,75 – 0,90` | Baik (*good*) |
| `≥ 0,90` | Sangat baik (*excellent*) |

Perlu ditekankan bahwa ambang tersebut bersifat konvensional dan harus dimaknai sesuai konteks penggunaan; nilai yang dianggap memadai bergantung pada kebutuhan penerapan sistem (Liljequist dkk., 2019). Selain itu, pelaporan yang baik tidak cukup hanya mencantumkan *point estimate*, melainkan juga menyertakan selang kepercayaan (*confidence interval*) 95%. Hal ini penting karena dua nilai ICC yang sama dapat memiliki tingkat ketidakpastian yang sangat berbeda — misalnya nilai 0,85 dengan selang `[0,60; 0,95]` jauh lebih tidak pasti dibanding nilai 0,85 dengan selang `[0,82; 0,88]`. Bahkan, Koo dan Li (2016) menganjurkan agar pengategorian reliabilitas didasarkan pada batas bawah selang kepercayaan, bukan pada *point estimate*, supaya klaim reliabilitas bersifat konservatif.

---

*Referensi yang dipakai pada bagian ini: Shrout & Fleiss (1979); McGraw & Wong (1996); Koo & Li (2016); Liljequist dkk. (2019); serta Jukiewicz dkk. (lengkapi metadata sitasi).*
