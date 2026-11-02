# Proyek Analisis Data: E-Commerce Public Dataset

Dashboard interaktif dan notebook analisis data untuk eksplorasi performa penjualan, kepuasan pengiriman, segmentasi RFM, dan demografi pelanggan pada E-Commerce Public Dataset.

- **Nama:** Daniel Julian Caesar
- **Email:** ds009b6y0409@student.devacademy.id
- **ID Dicoding:** ds009b6y0409

---

## Struktur Direktori

```
submission
├── dashboard
│   ├── main_data.csv
│   └── dashboard.py
├── data
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

---

## Cara Menjalankan Dashboard

### 1. Buat dan Aktifkan Virtual Environment (Opsional tapi Direkomendasikan)

Menggunakan `venv`:
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Atau menggunakan `conda`:
```bash
conda create --name main-ds python=3.11 -y
conda activate main-ds
```

### 2. Pasang Semua Dependensi

```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi Streamlit

Buka terminal di root direktori submission atau di dalam folder `dashboard`, lalu jalankan:

```bash
streamlit run dashboard/dashboard.py
```

Atau jika berada di dalam direktori `dashboard`:
```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan otomatis terbuka di browser pada alamat default `http://localhost:8501`.

---

## Cara Deploy ke Streamlit Cloud

1. Buat repositori baru di GitHub (misal: `dicoding-ecommerce-dashboard`).
2. Push isi folder `submission` (atau file `dashboard/dashboard.py`, `dashboard/main_data.csv`, `requirements.txt`) ke GitHub.
3. Buka [Streamlit Community Cloud](https://share.streamlit.io/) dan login menggunakan akun GitHub Anda.
4. Klik **New app**, pilih repositori yang baru Anda buat, tentukan branch (`main`), dan arahkan Main file path ke `dashboard/dashboard.py` (atau `dashboard.py` tergantung root repo).
5. Klik **Deploy!**
6. Salin tautan publik dashboard yang dihasilkan dan masukkan ke dalam berkas `url.txt`.
