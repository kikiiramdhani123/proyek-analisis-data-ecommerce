# Proyek Analisis Data: E-Commerce Public Dataset

Proyek akhir kelas **Belajar Analisis Data dengan Python** (Dicoding). Analisis memakai data marketplace Olist (Brasil) pada pesanan berstatus *delivered* periode **Januari 2017 – Agustus 2018**.

## Pertanyaan Bisnis
1. Bagaimana tren jumlah pesanan dan revenue bulanan, kapan puncaknya, dan berapa pertumbuhan MoM pada bulan puncak?
2. Kategori produk apa yang masuk 10 besar dan 10 terbawah berdasarkan revenue, dan berapa kontribusi 10 teratas?
3. Berapa selisih rata-rata review score antara pesanan terlambat dan tepat waktu, dan state mana yang paling sering terlambat?
4. *(Analisis lanjutan)* Segmentasi pelanggan dengan RFM Analysis.

## Struktur Direktori
```
submission
├───dashboard
│   ├───dashboard.py        # aplikasi Streamlit
│   └───main_data.csv       # data bersih hasil notebook
├───data                    # dataset mentah yang digunakan
│   ├───customers_dataset.csv
│   ├───order_items_dataset.csv
│   ├───order_payments_dataset.csv
│   ├───order_reviews_dataset.csv
│   ├───orders_dataset.csv
│   ├───product_category_name_translation.csv
│   └───products_dataset.csv
├───notebook.ipynb
├───README.md
└───requirements.txt
```

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```
atau dengan `venv`:
```
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Notebook
```
jupyter notebook notebook.ipynb
```
Jalankan dari folder `submission` agar path `data/` dan `dashboard/` terbaca. Notebook juga menghasilkan ulang `dashboard/main_data.csv`.

## Menjalankan Dashboard Streamlit
```
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`. Gunakan filter **rentang tanggal** dan **state pelanggan** di sidebar untuk mengeksplorasi data.
