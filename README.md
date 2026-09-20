# Proyek Analisis Data: Air Quality Dataset (Beijing PRSA)

Proyek akhir kelas **Belajar Analisis Data dengan Python** (Dicoding) menggunakan
Air Quality Dataset — data kualitas udara per jam dari 12 stasiun pemantauan di
Beijing, Maret 2013 – Februari 2017.

## Struktur Folder

```
.
├── data/PRSA_Data_20130301-20170228/   # File Dataset
├── main.ipynb                      # Notebook analisis lengkap (Kriteria 1-3)
├── dashboard/
│   ├── dashboard.py                    # Aplikasi dashboard Streamlit (Kriteria 4)
│   └── main_data.csv.gz                # Dataset bersih hasil notebook, dipakai dashboard
├── requirements.txt
└── url.txt                             # Isi dengan link deployment Streamlit Cloud
```

## Menjalankan Notebook

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook notebook.ipynb
```

Jalankan seluruh sel (`Run All`) dari awal — notebook akan membaca file CSV mentah
di folder `data/`, melakukan data wrangling, EDA, visualisasi, hingga analisis lanjutan
(geospatial + manual grouping/binning).

## Menjalankan Dashboard Streamlit (Lokal)

```bash
cd dashboard
pip install -r ../requirements.txt
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di `http://localhost:8501`. Gunakan sidebar untuk
memfilter rentang tanggal, stasiun, dan polutan.

