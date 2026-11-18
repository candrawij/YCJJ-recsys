# 🏕️ YCJJ-RecSys: Smart Camping Recommender & Budget Optimizer (Jogja - Jateng)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Clustering-F7931E.svg)](https://scikit-learn.org/)

**YCJJ-RecSys (YuruCamp Jogja-Jateng Recommender System)** adalah sistem rekomendasi cerdas terpadu untuk destinasi tempat perkemahan di area Daerah Istimewa Yogyakarta dan Jawa Tengah, dilengkapi modul pemilihan perlengkapan luar ruang (*outdoor gear*) berbasis optimasi anggaran belanja (*0/1 Knapsack Problem*).

---

## 🌟 Fitur Utama

Sistem ini dirancang secara modular ke dalam **3 Pendekatan**:

### 1. 🏕️ Rekomendasi Tempat Kemah (`01_camp_area_recommender`)
- **Penyaringan Cerdas:** Filter berdasarkan 15 Kabupaten/Kota terstandarisasi, batas tiket masuk (HTM + Parkir), dan fasilitas wajib (toilet, listrik, air bersih, dll.).
- **Unsupervised K-Means Clustering ($k=3$):** Segmentasi destinasi ke dalam 3 persona terbukti via PCA:
  - 🟢 **Family & Fasilitas Lengkap** (Akses listrik, air, ramah keluarga).
  - 🔴 **Adventure & Wild** (Medan alami/menantang, minim fasilitas komersial).
  - 🔵 **Scenic & Pemandangan** (Panorama 360° pegunungan megah, hawa dingin).
- **Checklist Bawaan Mandiri (Packing List):** Daftar logis perlengkapan yang wajib disiapkan dari rumah berdasarkan kondisi fisik lokasi (baju hangat, dry bag, dll. — *tanpa membebankan biaya pembelian alat baru*).

### 2. 🎒 Rekomendasi Pembelian Gear Outdoor (`02_gear_recommender`)
- **Katalog Spesifikasi Material:** Kategorisasi teknologi bahan (*Ultralight Nylon 20D / Titanium / FP 800 Down* vs *Standard Polyester 210T / Fiber*).
- **Filter Kapasitas Tenda:** Pilihan kapasitas orang (1P, 2P, 4P).
- **Starter Pack Optimizer (Knapsack Problem):** Memilih secara optimal kombinasi 4 barang inti (**Tenda + Sleeping Bag + Matras + Kompor**) sesuai batas budget finansial pengguna dengan perhitungan sisa saldo presisi.

### 3. 🔗 Smart Camping Planner Terpadu (`03_integrated_approach`)
- **Perencanaan End-to-End:** Menggabungkan pencarian destinasi dengan status kepemilikan alat (*Sudah Punya* vs *Belum Punya*).
- **Transparansi Struktur Biaya:** Membedakan dengan tegas antara **Biaya Operasional Wisata** (tiket, parkir, estimasi makan) dan **Biaya Opsional Pengadaan Alat**.

---

## 📁 Struktur Direktori

```
YCJJ-recsys/
├── data/                                  # Database master terstandarisasi
│   ├── camp_area_cleaned.csv              # 56 spot kemah terverifikasi
│   ├── gear_equipment_cleaned.csv         # 49 item outdoor terstandarisasi
│   ├── Database Camp Area...csv           # Raw dataset
│   └── Database List Camp Equipment...csv # Raw dataset
│
├── 01_camp_area_recommender/              # Pendekatan 1: Destinasi Kemah
│   ├── camp_recommender.ipynb             # Notebook eksperimen & evaluasi K-Means
│   ├── app_camp.py                        # UI Streamlit mandiri
│   └── [Aset visualisasi EDA & PCA]
│
├── 02_gear_recommender/                   # Pendekatan 2: Pembelian Gear
│   ├── gear_recommender.ipynb             # Notebook analisis harga & Knapsack
│   ├── app_gear.py                        # UI Streamlit mandiri
│   └── [Aset visualisasi EDA gear]
│
├── 03_integrated_approach/                # Pendekatan 3: Perencanaan Terpadu
│   ├── main.ipynb                         # Notebook eksperimen integrasi
│   ├── app_integrated.py                  # UI Streamlit mandiri
│   └── LAPORAN_ANALISIS_YURUCAMP.md       # Laporan analisis historis
│
├── app.py                                 # 🚀 Hub Antarmuka Utama (3-in-1 UI)
├── PENJELASAN_DAN_INTERFACE.md            # Kajian teori ML & panduan antarmuka
├── TASKS.md                               # Roadmap pengembangan proyek
├── .gitignore                             # Git ignore file
└── README.md                              # Dokumentasi proyek
```

---

## 🚀 Panduan Menjalankan Aplikasi

### 1. Prasyarat Lingkungan
Pastikan Anda telah memasang Python 3.10+ dan pustaka pendukung:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn streamlit
```

### 2. Menjalankan Web App Streamlit
Jalankan hub utama antarmuka:
```bash
streamlit run app.py
```
Aplikasi web akan terbuka otomatis di peramban (*browser*) Anda pada alamat `http://localhost:8501`.

Anda dapat berpindah secara leluasa antara:
1. Rekomendasi Tempat Kemah
2. Rekomendasi Pembelian Gear
3. Smart Camping Planner Terpadu

---

## 🔬 Metodologi Data Science
- **Preprocessing & Cleaning:** Normalisasi harga string ke integer rupiah, eliminasi 28 baris hantu (*phantom rows*), dan standarisasi entitas 15 Kabupaten resmi.
- **Unsupervised Learning:** K-Means Clustering ($k=3$), dievaluasi dengan *Silhouette Score* (0.4652) dan *Davies-Bouldin Index* (1.5334).
- **Dimensionality Reduction:** Principal Component Analysis (PCA) 2D untuk visualisasi sebaran klaster.
- **Operations Research:** 0/1 Knapsack Problem / Heuristic Optimization untuk pemilihan paket belanja gear terbaik.
- **Expert System:** Knowledge-based rules untuk pemetaan kondisi medan ke checklist barang bawaan darurat.

---

## 👨‍💻 Kontributor
- **Candra Wijaya** ([@candrawij](https://github.com/candrawij))
