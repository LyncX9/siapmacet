# PROPOSAL & DOKUMENTASI TEKNIS: SiapMacet (Smart Traffic Monitoring System)

## 1. Ringkasan Eksekutif (Executive Summary)
**SiapMacet** adalah platform pemantauan dan prediksi kemacetan lalu lintas real-time yang dirancang untuk memberikan wawasan berbasis data spasial dan kecerdasan buatan (AI). Sistem ini menggabungkan data lalu lintas real-time dari TomTom API, pemetaan geospasial interaktif, dan algoritma Machine Learning untuk memprediksi tren kemacetan di masa depan.

Proyek ini bertujuan untuk menyediakan dashboard visual yang intuitif bagi pengambil keputusan dan publik untuk memahami pola lalu lintas kota secara makro maupun mikro.

---

## 2. Arsitektur Teknis (Technical Architecture)

### 2.1 Tech Stack
*   **Frontend**: Vue 3 (Vite), Tailwind CSS, Leaflet.js (Peta), Chart.js (Grafik).
*   **Backend**: Python FastAPI (High performance async framework).
*   **Database**: Supabase (PostgreSQL + PostGIS Extension untuk data spasial).
*   **External API**: TomTom Traffic API (Sumber data real-time).
*   **Machine Learning**: Scikit-learn, XGBoost (Traffic Prediction & Clustering).
*   **Infrastructure**: Render (Backend Hosting), Vercel (Frontend Hosting), Docker (Containerization).

### 2.2 Alur Data (Data Flow)
1.  **Ingestion**: `Scheduler` (Python) berjalan setiap 5 menit, mengambil data `speed` dan `travel_time` dari TomTom API berdasarkan koordinat ruas jalan (`roads`).
2.  **Storage**: Data disimpan ke PostgreSQL dengan ekstensi PostGIS untuk query spasial yang efisien.
3.  **Processing**:
    *   **Hourly Aggregation**: Menghitung rata-rata kecepatan per jam.
    *   **ML Clustering**: Mengelompokkan jalan berdasarkan pola kemacetan (misal: "Macet Pagi", "Stabil", "Macet Sore").
    *   **Forecasting**: Memprediksi kondisi 30 menit ke depan menggunakan XGBoost.
4.  **Presentation**: API menyajikan data GeoJSON ke Frontend untuk divisualisasikan sebagai layer warna pada peta (Hijau/Kuning/Merah).

---

## 3. Struktur Proyek & Direktori

```text
SiapMacet/
├── backend/                    # Python FastAPI Backend
│   ├── ml/                     # Modul Machine Learning
│   │   ├── forecast.py         # Logika forecasting (Phased Approach)
│   │   ├── clustering.py       # Algoritma K-Means untuk klasterisasi jalan
│   │   ├── prediction.py       # Inference engine XGBoost
│   │   └── train.py            # Script pelatihan model
│   ├── main.py                 # Entry point API (Endpoints)
│   ├── models.py               # Definisi Tabel Database (SQLAlchemy)
│   ├── scheduler.py            # Job pengambil data otomatis (Background Task)
│   ├── loader_geojson.py       # Script inisialisasi peta dasar (Seeding)
│   ├── db.py                   # Koneksi Database & Cache
│   ├── tomtom.py               # Wrapper untuk TomTom API
│   ├── requirements.txt        # Dependensi Python
│   └── Dockerfile              # Konfigurasi Container Backend
├── dashboard/                  # Vue 3 Frontend
│   ├── src/
│   │   ├── components/         # Komponen UI (Map, Charts, Sidebar)
│   │   │   ├── MapComponent.vue    # Visualisasi Peta Utama
│   │   │   ├── StatsCard.vue       # Kartu Statistik Ringkas
│   │   │   └── ...
│   │   ├── api.js              # Sentralisasi request ke Backend
│   │   └── App.vue             # Layout Utama
│   ├── vercel.json             # Konfigurasi deployment Frontend
│   └── index.html              # Entry point aplikasi web
└── data/                       # Data Mentah
    └── roads.geojson           # Data geometri ruas jalan (LineString)
```

---

## 4. Skema Database (Database Schema)

Menggunakan PostgreSQL dengan PostGIS.

### a. Tabel `roads`
Menyimpan data statis ruas jalan dan geometrinya.
*   `road_id` (PK): ID unik jalan (misal: `SBM_SKC_01`).
*   `road_name`: Nama jalan.
*   `city`: Kota/Wilayah.
*   `geom`: Geometri spasial (`LINESTRING`, SRID 4326).

### b. Tabel `traffic_history`
Menyimpan log data lalu lintas real-time (Time-series).
*   `id` (PK): Auto-increment.
*   `road_id`: Referensi ke tabel `roads`.
*   `speed`: Kecepatan saat ini (km/h).
*   `free_flow`: Kecepatan saat lancar (km/h).
*   `confidence`: Tingkat akurasi data API (0-1).
*   `created_at`: Stempel waktu data diambil.

### c. Tabel `road_clusters` (Hasil ML)
Menyimpan hasil analisis pola jalan.
*   `road_id`: Referensi ke `roads`.
*   `cluster_id`: ID Kelompok (0, 1, 2, ...).
*   `cluster_label`: Label manusia (contoh: "High Congestion Zone").

---

## 5. Fitur Utama & Keunggulan

### 5.1 Smart Caching & Resiliency
*   **Redis Caching**: Mengurangi beban database dengan menyimpan hasil query berat (snapshot traffic) selama 60 detik.
*   **API Key Rotation**: Sistem secara otomatis berputar menggunakan 10+ API Key TomTom untuk menghindari *Rate Limiting* (batas kuota harian).
*   **Fallback Mechanism**: Jika API TomTom mati, sistem tetap berjalan menampilkan data terakhir yang valid.

### 5.2 Phased Machine Learning Architecture
Sistem menggunakan pendekatan bertahap untuk akurasi prediksi:
*   **Phase 1 (Cold Start)**: Menggunakan *Estimation-Based Logic* (aturan statistik sederhana) ketika data historis belum cukup (< 7 hari).
*   **Phase 2 (AI Powered)**: Otomatis beralih ke *Supervised Learning (XGBoost)* setelah data terkumpul > 30 hari untuk prediksi presisi tinggi berdasarkan pola hari dan jam.

### 5.3 Interactive Dashboard
*   **Heatmap Layer**: Visualisasi area dengan kepadatan tinggi.
*   **Live Metrics**: Menampilkan "Average Speed" kota dan "Active Traffic Jams".
*   **Predictive Graph**: Grafik garis yang membandingkan kondisi "Saat Ini" vs "Prediksi 30 Menit ke Depan".

---

## 6. Strategi Deployment

Proyek ini dirancang Cloud-Native:
1.  **Backend (Render)**: Menggunakan Docker Container. Koneksi database menggunakan *Connection Pooling* untuk skalabilitas tinggi.
2.  **Frontend (Vercel)**: Static Site Generation (SSG/SPA) yang didistribusikan lewat CDN global.
3.  **Database (Supabase)**: Managed Service PostgreSQL yang dapat diakses secara *Secure Tunneling* dari backend.

---

**Dokumen ini dibuat untuk:**
*   Referensi pengembangan tim (Developers).
*   Context Injection untuk AI (LLM) agar memahami struktur kode.
*   Bahan dasar penyusunan Proposal Proyek / Tesis.
