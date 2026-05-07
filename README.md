# Proyek Analisis Data: E-Commerce Public Dataset

Proyek akhir kelas *Belajar Analisis Data dengan Python* — Dicoding.
Repositori ini berisi notebook analisis data dan dashboard interaktif berbasis **Streamlit** atas **Olist Brazilian E-Commerce Public Dataset** (periode September 2016 – Oktober 2018).

---

## 📂 Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv          # Data hasil cleaning & merging untuk dashboard
│   └── dashboard.py           # Aplikasi Streamlit
├── data/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb             # Notebook lengkap (analisis end-to-end)
├── README.md                  # Berkas ini
├── requirements.txt           # Daftar library
└── url.txt                    # Tautan dashboard yang sudah di-deploy
```

---

## 🛠️ Setup Environment

### Menggunakan Anaconda

```bash
conda create --name proyek-analisis-data python=3.10
conda activate proyek-analisis-data
pip install -r requirements.txt
```

### Menggunakan Pipenv / Virtualenv (alternatif)

```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
python -m venv venv
# Linux / Mac
source venv/bin/activate
# Windows
# venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🚀 Menjalankan Aplikasi

### 1. Notebook Analisis

Buka `notebook.ipynb` di Jupyter Notebook / Jupyter Lab / Google Colab:

```bash
jupyter notebook notebook.ipynb
```

Notebook akan memandu Anda melalui:
1. **Pertanyaan Bisnis** (SMART Question)
2. **Data Wrangling** — *Gathering, Assessing, Cleaning Data*
3. **Exploratory Data Analysis (EDA)**
4. **Visualization & Explanatory Analysis**
5. **Analisis Lanjutan** — *RFM Analysis, Geospatial Analysis, Manual Clustering (Binning)*
6. **Conclusion & Recommendation**

### 2. Dashboard Streamlit (Local)

Dari direktori utama project:

```bash
cd dashboard
streamlit run dashboard.py
```

Aplikasi akan otomatis terbuka di browser pada `http://localhost:8501`.

### 3. Dashboard Online

Tautan dashboard yang sudah dideploy ke **Streamlit Community Cloud** ada di berkas [`url.txt`](url.txt).

---

## 📌 Pertanyaan Bisnis yang Dijawab

1. Bagaimana **tren jumlah pesanan dan total revenue bulanan** di Olist selama periode September 2016 – Agustus 2018, dan **kategori produk apa** yang berkontribusi paling besar terhadap revenue?
2. **State (negara bagian) di Brazil mana** yang memberikan kontribusi revenue tertinggi pada periode 2016–2018, dan bagaimana **segmentasi pelanggan berdasarkan analisis RFM (Recency, Frequency, Monetary)** untuk mengidentifikasi pelanggan bernilai tinggi?

---

## 🔬 Teknik Analisis Lanjutan yang Diterapkan

| Teknik                      | Tujuan                                                                |
| --------------------------- | --------------------------------------------------------------------- |
| **RFM Analysis**            | Segmentasi pelanggan menjadi *Champions, Loyal, Potential, At Risk*.  |
| **Geospatial Analysis**     | Visualisasi distribusi revenue per state Brazil dengan peta scatter.  |
| **Manual Clustering (Binning)** | Pengelompokan pelanggan ke dalam tier *Bronze – Platinum* berbasis kuartil monetary. |

Catatan: Sesuai ketentuan, ketiga teknik di atas **tidak menggunakan algoritma machine learning** — murni berbasis aturan bisnis, kuartil, dan agregasi.

---

## 📦 Dataset

Dataset yang digunakan adalah **Olist Brazilian E-Commerce Public Dataset** yang disediakan oleh program Dicoding, berisi sekitar **100.000 pesanan** e-commerce yang dilakukan di marketplace Olist antara 2016–2018.

Sumber: <https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>

---

## 👤 Author

- **Nama:** [Rizky Ramdhani]
- **Email:** [kikidewadota11@gmail.com]
- **ID Dicoding:** [kiki_dewadota11ghcw]
