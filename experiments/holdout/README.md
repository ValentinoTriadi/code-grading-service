# Holdout Test Set — Cycle Entry Point (Praktikum 10, Olympia)

Data uji **terpisah** dari `experiments/dataset/`. Tujuannya sebagai **pengujian akhir**
(held-out) untuk eksperimen: setelah konfigurasi prompt terbaik ditentukan pada
`dataset/`, layanan diuji pada data ini yang **belum pernah dipakai** saat pengembangan.

- **Sumber:** kuis "Praktikum 10 - K1 & K2" di Olympia (`report.php?id=7422`), soal ke-3
  *Cycle* — cari *entry point* dari cycle pada linked list.
- **Kenapa Q3 (Cycle):** soal sulit (rata-rata auto-grader 1,50/2,50) yang masih punya
  ≥20 pengumpul, dan sebaran skornya paling kaya (7 level) sehingga informatif untuk
  membandingkan penilaian LLM/manual dengan auto-grader. (Q4 UI lebih sulit tapi 70%
  bernilai 0 → kurang bervariasi.)
- **Sampel:** 20 submisi dipilih merata sepanjang rentang skor Olympia.

## Skema (identik dengan `experiments/dataset/`)

| Berkas | Isi | Git |
|---|---|---|
| `problems.json` | 1 problem `H1` + `rubric_structured` (score band) & `rubric_unstructured` | **tracked** |
| `submissions.json` | 20 submisi anonim (`cycle_01..20`), kode inline, `olympia_score`, `human_score` = `null` | **tracked** |
| `code/cycle_NN.c` | kode submisi (anonim, tanpa NIM di nama file) | **tracked** |
| `grading_sheet.csv` | lembar penilaian manual selaras rubrik (4 kriteria, /100) | **tracked** |
| `raw/` | data mentah ber-PII: NIM, nama, email, semua submisi kuis, soal, skrip, `mapping_pii.csv` | **git-ignored** |

> `raw/mapping_pii.csv` memetakan `submission_id ↔ NIM ↔ nama`. Hanya ada di lokal
> (di-ignore) agar identitas mahasiswa tidak ter-commit.

## Alur penilaian manual (langkah kamu berikutnya)

1. Nilai tiap `code/cycle_NN.c` memakai rubrik di `problems.json` (skala **0–100**,
   kriteria: Correctness /45, Efficiency /25, Approach /15, Code Quality /15).
2. Isi `grading_sheet.csv` (skor per kriteria + total; kolom `olympia_ref(/100)` sebagai
   pembanding auto-grader).
3. Setelah terisi, jalankan pemindahan skor ke `submissions.json`
   (`human_score` + `human_score_breakdown`) — minta bantuan untuk skrip sinkronisasinya.
4. Data siap dipakai sebagai pengujian akhir eksperimen (LLM vs manusia, plus pembanding
   auto-grader Olympia).

## Rubrik

Ditulis dengan gaya *evidence-based scoring band* yang sama seperti `dataset/` (Fix B):
tiap band memetakan **bukti yang terlihat di kode → skor**, dikalibrasi terhadap pola
nyata pada 20 submisi (Floyd two-pointer bersih; penandaan `INFO` dengan sentinel;
array visited O(N); sampai versi yang tak kompilasi karena `next()` vs `NEXT`).

### Kebijakan: kode ter-comment (revisi manual, transparansi)

`cycle_08` adalah satu-satunya submisi yang algoritmanya **di-comment total** (hanya
`return NULL` yang aktif). Kebijakan penilaian manual: attempt yang terlihat di dalam
comment diberi **setengah kredit Correctness** (9 = ½ × band 18/45) karena idenya
mengarah benar tetapi tidak dieksekusi; **Efficiency tetap rendah** (niatnya O(N²), bukan
O(1) — `return NULL` yang no-op tidak dihitung sebagai "efisien"). Total manual cycle_08:
17 → **26**. Catatan ini didokumentasikan karena revisi menyentuh ground-truth held-out;
kebijakan half-credit berlaku seragam untuk kasus all-commented (di set ini hanya cycle_08).
