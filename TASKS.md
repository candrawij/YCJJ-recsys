# 📋 Daftar Task & Rencana Pengembangan: YuruCamp Data Science

Dokumen ini berisi rincian **task terstruktur (action items)** untuk masing-masing dari 3 pendekatan yang telah dipisahkan. Setiap task dirancang mengikuti siklus kerja Data Science profesional untuk membantu Anda mengasah kemampuan praktis.

---

## 🏕️ PENDEKATAN 1: `01_camp_area_recommender`
> **Fokus:** Sistem Rekomendasi Destinasi Kemah, Segmentasi Karakteristik Alam, dan Generator Checklist Bawaan (Packing List).

### Fase 1: Data Preprocessing & Enrichment
- [ ] **Task 1.1 — Penanganan Missing Value Lanjutan:**
  - Evaluasi kolom `Fasilitas` (kosong ~58%) dan `Maps` (kosong ~54%).
  - Lakukan imputasi berbasis nama tempat / daerah atau tambahkan penanda status data (`is_verified`).
- [ ] **Task 1.2 — Ekstraksi Entitas Lokasi & Koordinat:**
  - Standarisasi kolom `Lokasi` (misal memisahkan Kabupaten/Kota dengan Kecamatan, contoh: "Bantul", "Karanganyar", "Wonosobo").
  - *(Opsional/Pengayaan)* Tambahkan koordinat Latitude & Longitude (bisa manual dari Google Maps) untuk visualisasi peta spasial.
- [ ] **Task 1.3 — Advanced Text Mining / NLP:**
  - Kembangkan ekstraksi fitur teks dengan **TF-IDF Vectorizer** pada gabungan kolom `Spot_Menarik` dan `Info_Tambahan`.
  - Ekstraksi keyword otomatis untuk mendeteksi bahaya medan (misal: "jurang", "panas", "angin kencang", "aliran sungai").

### Fase 2: Modeling & Evaluasi Clustering
- [ ] **Task 2.1 — Optimasi Parameter K-Means:**
  - Hitung **Silhouette Score** dan **Davies-Bouldin Index** untuk menguji apakah $k=3$ atau $k=4$ yang paling optimal secara matematis.
- [ ] **Task 2.2 — Eksperimen Model Alternatif:**
  - Coba algoritma **Hierarchical Clustering (Agglomerative)** dan buat visualisasi dendrogram.
  - Coba algoritma **DBSCAN** untuk mendeteksi spot camping dengan karakteristik anomali/ekstrem (outlier).
- [ ] **Task 2.3 — Profiling Karakter Klaster:**
  - Buat tabel ringkasan rata-rata fasilitas dan rentang HTM untuk tiap klaster.

### Fase 3: Rekomendasi & Packing Checklist Engine
- [ ] **Task 3.1 — Penyempurnaan Content-Based Filtering:**
  - Buat fungsi similarity (misal: **Cosine Similarity**) agar user bisa mencari: *"Tempat kemah yang mirip dengan Bukit Sekipan"*.
- [ ] **Task 3.2 — Modul Packing Checklist Dinamis:**
  - Lengkapi aturan checklist bawaan mandiri:
    - Ketinggian/Dingin $\rightarrow$ Baju hangat, sleeping bag thermal, kupluk, kaos kaki ekstra.
    - Dekat Air/Sungai $\rightarrow$ Sandal antiselip, flysheet penahan badai, dry bag.
    - Tanpa Listrik & Air $\rightarrow$ Powerbank kapasitas besar, jeriken air bersih.
    - Family Friendly $\rightarrow$ Obat-obatan P3K anak, matras tebal, lampu lentera meja.
- [ ] **Task 3.3 — Output Formatter:**
  - Sediakan fungsi untuk mengekspor checklist ke format teks/Markdown agar bisa langsung dicetak atau disalin ke HP.

---

## 🎒 PENDEKATAN 2: `02_gear_recommender`
> **Fokus:** Katalog Perlengkapan Outdoor, Analisis Spesifikasi Teknis/Material, dan Sistem Rekomendasi Pembelian/Bundling.

### Fase 1: Data Structuring & Normalisasi Spesifikasi
- [ ] **Task 1.1 — Normalisasi Atribut Teknis:**
  - Ekstrak bobot peralatan (dalam gram/kg) dari kolom `Material` dan `Ukuran`.
  - Ekstrak kapasitas tenda (1P, 2P, 4P) dan kapasitas tas (liter, misal: 35L, 45L, 60L).
  - Ekstrak rating suhu pada Sleeping Bag (misal: 1°C, 5–15°C, comfort vs limit).
- [ ] **Task 1.2 — Pembersihan Link Pembelian:**
  - Standarisasi kolom `Link` pembelian e-commerce (Shopee, Tokopedia, dll.).
  - Berikan flag ketersediaan link aktif/valid.

### Fase 2: Analisis Ekonomi & Perbandingan Material (EDA)
- [ ] **Task 2.1 — Trade-off Analysis (Material vs Harga):**
  - Bandingkan harga rata-rata tenda berbahan *Nylon 20D* (ultralight) vs *Polyester 210T* (standar).
  - Bandingkan sleeping bag bahan *Bulu Angsa (Down)* vs *Dacron Sintetis*.
- [ ] **Task 2.2 — Segmentasi Budget Calon Pembeli:**
  - Visualisasikan rentang harga per kategori gear menggunakan boxplot & violin plot.

### Fase 3: Rekomendasi Pembelian & Algoritma Optimasi (Knapsack)
- [ ] **Task 3.1 — Multi-Criteria Gear Recommender:**
  - Bangun fungsi pencarian berbasis multi-kriteria: Kategori, batas budget, prioritas bobot (ringan vs terjangkau).
- [ ] **Task 3.2 — Starter Pack Optimizer (Knapsack Problem):**
  - Terapkan optimasi kombinatorial sederhana (*0/1 Knapsack Problem*) menggunakan pustaka `scipy.optimize` atau greedy algorithm:
    - *Goal:* Memilih kombinasi 1 Tenda + 1 SB + 1 Matras + 1 Kompor dengan total harga $\le$ pagu budget dan skor kualitas/bobot maksimal.
- [ ] **Task 3.3 — Bundle Tiering:**
  - Rancang 3 paket bundling siap pakai:
    1. *Paket Mahasiswa / Hemat* (Target < Rp 1.000.000)
    2. *Paket Standar Nyaman* (Target Rp 1.000.000 – Rp 2.500.000)
    3. *Paket Ultralight Enthusiast* (Target > Rp 2.500.000)

---

## 🔗 PENDEKATAN 3: `03_integrated_approach`
> **Fokus:** Integrasi Holistik Destinasi + Kebutuhan Perlengkapan (End-to-End Smart Planner).

### Fase 1: Refactoring & Harmonisasi Logika
- [ ] **Task 1.1 — Perbaikan Pemisahan Beli vs Bawa:**
  - Perbarui fungsi perencana di notebook integrasi agar outputnya memisahkan secara tegas:
    - **A. Perlengkapan yang Harus Dibawa (Operational Checklist)**
    - **B. Opsi Rekomendasi Belanja / Sewa Gear (Katalog Opsional)** jika user belum memiliki perlengkapan tersebut.
- [ ] **Task 1.2 — Kalkulasi Total Estimasi Biaya Perjalanan:**
  - Estimasi Biaya Wisata = HTM Tiket Masuk + Parkir + Estimasi Konsumsi Logistik.
  - Biaya gear diposisikan sebagai biaya investasi awal opsional.

### Fase 2: Pembuatan Dashboard Interaktif (Streamlit / Gradio)
- [ ] **Task 2.1 — Setup Web App Sederhana (Streamlit):**
  - Buat file `app.py` di folder `03_integrated_approach/`.
  - Komponen antarmuka:
    - *Sidebar:* Pilihan Kabupaten/Kota, slider budget tiket, checkbox fasilitas wajib (listrik/toilet/air).
    - *Main Page:* Kartu rekomendasi destinasi kemah terbaik beserta foto/deskripsi dan tautan Google Maps.
    - *Tab 1:* Checklist perlengkapan yang wajib dibawa dari rumah.
    - *Tab 2:* Rekomendasi gear spesifik bagi yang butuh membeli alat baru.
- [ ] **Task 2.2 — Deploy Lokal & Dokumentasi Interaktif:**
  - Buat file `requirements.txt` untuk dependensi web app.
  - Tambahkan tangkapan layar antarmuka dashboard ke laporan akhir.

---

## 📅 Matriks Prioritas Eksekusi (Roadmap Belajar)

| Urutan | Modul | Task Utama | Skill yang Dipelajari |
| :---: | :--- | :--- | :--- |
| **1** | `01_camp_area` | Eksekusi Task 3.1 & 3.2 (Cosine Similarity & Checklist) | Content-based Recommender, Rule engines |
| **2** | `02_gear` | Eksekusi Task 3.2 (Starter Pack Knapsack Optimization) | Algoritma optimasi, constraint programming |
| **3** | `01_camp_area` | Eksekusi Task 2.1 (Silhouette Score & Hierarchical Clustering) | Validasi Unsupervised Learning |
| **4** | `03_integrated` | Eksekusi Task 2.1 (Membangun Web App Streamlit) | Fullstack Data Science & App Deployment |
