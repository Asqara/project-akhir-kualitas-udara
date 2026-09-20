

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "main_data.csv.gz")

# --------------------------------------------------------------------------
# Konfigurasi halaman
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Kualitas Udara Beijing",
    page_icon="🌫️",
    layout="wide",
)

PM25_BINS = [-0.1, 12.0, 35.4, 55.4, 150.4, 250.4, np.inf]
PM25_LABELS = [
    "Baik (0-12)",
    "Sedang (12.1-35.4)",
    "Tidak Sehat bagi Sensitif (35.5-55.4)",
    "Tidak Sehat (55.5-150.4)",
    "Sangat Tidak Sehat (150.5-250.4)",
    "Berbahaya (>250.4)",
]
CATEGORY_COLORS = {
    "Baik (0-12)": "#4CAF50",
    "Sedang (12.1-35.4)": "#FFEB3B",
    "Tidak Sehat bagi Sensitif (35.5-55.4)": "#FF9800",
    "Tidak Sehat (55.5-150.4)": "#F44336",
    "Sangat Tidak Sehat (150.5-250.4)": "#9C27B0",
    "Berbahaya (>250.4)": "#7B1D1D",
}
STATION_COORDS = {
    "Aotizhongxin":  (39.982, 116.397),
    "Changping":     (40.217, 116.230),
    "Dingling":      (40.292, 116.220),
    "Dongsi":        (39.929, 116.417),
    "Guanyuan":      (39.929, 116.339),
    "Gucheng":       (39.914, 116.184),
    "Huairou":       (40.328, 116.628),
    "Nongzhanguan":  (39.937, 116.461),
    "Shunyi":        (40.127, 116.655),
    "Tiantan":       (39.886, 116.407),
    "Wanliu":        (39.987, 116.287),
    "Wanshouxigong": (39.878, 116.352),
}
CITY_CENTER = (39.9075, 116.3972)
POLLUTANTS = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["datetime"])
    if "pm25_category" not in df.columns:
        df["pm25_category"] = pd.cut(df["PM2.5"], bins=PM25_BINS, labels=PM25_LABELS)
    else:
        df["pm25_category"] = pd.Categorical(df["pm25_category"], categories=PM25_LABELS, ordered=True)
    return df


df = load_data()

# --------------------------------------------------------------------------
# Sidebar - Filter
# --------------------------------------------------------------------------
st.sidebar.title("🌫️ Filter Data")
st.sidebar.caption("Air Quality Dataset - Beijing (PRSA), Mar 2013 - Feb 2017")

min_date, max_date = df["datetime"].min().date(), df["datetime"].max().date()
date_range = st.sidebar.date_input(
    "Rentang tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

all_stations = sorted(df["station"].unique())
selected_stations = st.sidebar.multiselect(
    "Stasiun pemantauan", options=all_stations, default=all_stations
)

selected_pollutant = st.sidebar.selectbox("Polutan utama", options=POLLUTANTS, index=0)

if not selected_stations:
    st.warning("Pilih minimal satu stasiun pada sidebar untuk menampilkan data.")
    st.stop()

mask = (
    (df["datetime"].dt.date >= start_date)
    & (df["datetime"].dt.date <= end_date)
    & (df["station"].isin(selected_stations))
)
filtered_df = df.loc[mask].copy()

if filtered_df.empty:
    st.warning("Tidak ada data pada rentang filter yang dipilih.")
    st.stop()

# --------------------------------------------------------------------------
# Header & KPI
# --------------------------------------------------------------------------
st.title("Dashboard Analisis Kualitas Udara Beijing 🌫️")
st.markdown(
    "Dashboard interaktif untuk mengeksplorasi tren, pola waktu, dan sebaran spasial "
    "polusi udara dari **Air Quality Dataset (PRSA)** — data per jam dari 12 stasiun "
    "pemantauan di Beijing, Maret 2013 – Februari 2017."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric(f"Rata-rata {selected_pollutant}", f"{filtered_df[selected_pollutant].mean():,.1f}")
col2.metric(f"Maksimum {selected_pollutant}", f"{filtered_df[selected_pollutant].max():,.1f}")
pct_unhealthy = (filtered_df["PM2.5"] > 55.4).mean() * 100
col3.metric("% Jam PM2.5 Tidak Sehat (>55.4)", f"{pct_unhealthy:,.1f}%")
col4.metric("Jumlah Observasi", f"{len(filtered_df):,}")

st.divider()

# --------------------------------------------------------------------------
# Pertanyaan 1: Tren bulanan & stasiun paling tercemar
# --------------------------------------------------------------------------
st.header("1. Tren & Perbandingan Antar Stasiun")
tab1, tab2 = st.tabs(["Tren Bulanan", "Rata-rata per Stasiun"])

with tab1:
    monthly = filtered_df.set_index("datetime")[selected_pollutant].resample("ME").mean()
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(monthly.index, monthly.values, color="#D64545", linewidth=2)
    ax.set_title(f"Tren Rata-rata Bulanan {selected_pollutant}")
    ax.set_xlabel("Periode")
    ax.set_ylabel(f"Rata-rata {selected_pollutant}")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b-%y"))
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close(fig)

with tab2:
    station_mean = (
        filtered_df.groupby("station")[selected_pollutant].mean().sort_values(ascending=False)
    )
    top3 = station_mean.head(3).index.tolist()
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#D64545" if s in top3 else "#9CB4CC" for s in station_mean.index]
    sns.barplot(x=station_mean.values, y=station_mean.index, hue=station_mean.index,
                palette=colors, legend=False, ax=ax)
    ax.set_xlabel(f"Rata-rata {selected_pollutant}")
    ax.set_ylabel("Stasiun")
    ax.set_title(f"Rata-rata {selected_pollutant} per Stasiun (Merah = 3 Tertinggi)")
    st.pyplot(fig)
    plt.close(fig)
    st.caption(f"3 stasiun dengan rata-rata {selected_pollutant} tertinggi pada filter saat ini: **{', '.join(top3)}**")

st.divider()

# --------------------------------------------------------------------------
# Pertanyaan 2: Pola diurnal per musim
# --------------------------------------------------------------------------
st.header("2. Pola Diurnal PM2.5: Musim Dingin vs Musim Panas")

focus_station = st.selectbox("Pilih stasiun untuk analisis pola per jam", options=selected_stations)
station_df = filtered_df[filtered_df["station"] == focus_station]
season_df = station_df[station_df["season"].isin(["Dingin (DJF)", "Panas (JJA)"])]

colA, colB = st.columns(2)

with colA:
    if season_df.empty:
        st.info("Tidak ada data musim Dingin/Panas pada rentang filter saat ini.")
    else:
        hourly = season_df.groupby(["season", "hour"])["PM2.5"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.lineplot(data=hourly, x="hour", y="PM2.5", hue="season", marker="o",
                     palette={"Dingin (DJF)": "#D64545", "Panas (JJA)": "#4E8098"}, ax=ax)
        ax.axhline(55.4, color="black", linestyle="--", linewidth=1, label="Ambang Tidak Sehat")
        ax.set_title(f"Pola Diurnal PM2.5 - {focus_station}")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata PM2.5")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)

with colB:
    if season_df.empty:
        st.info("Tidak ada data musim Dingin/Panas pada rentang filter saat ini.")
    else:
        pct = (
            season_df.assign(is_unhealthy=lambda x: x["PM2.5"] > 55.4)
            .groupby(["season", "hour"])["is_unhealthy"].mean().mul(100).reset_index()
        )
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.lineplot(data=pct, x="hour", y="is_unhealthy", hue="season", marker="o",
                     palette={"Dingin (DJF)": "#D64545", "Panas (JJA)": "#4E8098"}, ax=ax)
        ax.set_title(f"% Jam PM2.5 > 55.4 µg/m³ - {focus_station}")
        ax.set_xlabel("Jam")
        ax.set_ylabel("% Kejadian Tidak Sehat")
        st.pyplot(fig)
        plt.close(fig)

st.divider()

# --------------------------------------------------------------------------
# Kategori kualitas udara (binning dinamis)
# --------------------------------------------------------------------------
st.header("3. Distribusi Kategori Kualitas Udara")

# Buat kategori berdasarkan polutan yang dipilih
if selected_pollutant == "PM2.5":
    pollutant_bins = [-0.1, 12.0, 35.4, 55.4, 150.4, 250.4, np.inf]
    pollutant_labels = [
        "Baik (0-12)",
        "Sedang (12.1-35.4)",
        "Tidak Sehat bagi Sensitif (35.5-55.4)",
        "Tidak Sehat (55.5-150.4)",
        "Sangat Tidak Sehat (150.5-250.4)",
        "Berbahaya (>250.4)",
    ]

elif selected_pollutant == "PM10":
    pollutant_bins = [-0.1, 54, 154, 254, 354, 424, np.inf]
    pollutant_labels = [
        "Baik (0-54)",
        "Sedang (55-154)",
        "Tidak Sehat bagi Sensitif (155-254)",
        "Tidak Sehat (255-354)",
        "Sangat Tidak Sehat (355-424)",
        "Berbahaya (>424)",
    ]

else:
    # Untuk polutan lain gunakan quantile agar tetap dinamis
    quantiles = filtered_df[selected_pollutant].quantile(
        [0, .2, .4, .6, .8, 1]
    ).values

    pollutant_bins = sorted(list(set(quantiles)))

    pollutant_labels = [
        "Sangat Rendah",
        "Rendah",
        "Sedang",
        "Tinggi",
        "Sangat Tinggi"
    ]


# Tambahkan kategori sementara
category_col = f"{selected_pollutant}_category"

filtered_df[category_col] = pd.cut(
    filtered_df[selected_pollutant],
    bins=pollutant_bins,
    labels=pollutant_labels[:len(pollutant_bins)-1],
    include_lowest=True
)


category_counts = (
    filtered_df[category_col]
    .value_counts()
    .reindex(pollutant_labels)
    .fillna(0)
)


fig, ax = plt.subplots(figsize=(10, 4.5))

sns.barplot(
    x=category_counts.values,
    y=category_counts.index,
    hue=category_counts.index,
    palette="viridis",
    legend=False,
    ax=ax
)

ax.set_title(
    f"Distribusi Kategori {selected_pollutant}"
)

ax.set_xlabel("Jumlah Observasi (jam)")
ax.set_ylabel("Kategori")


for i, value in enumerate(category_counts.values):
    ax.text(
        value,
        i,
        f" {int(value):,}",
        va="center"
    )


st.pyplot(fig)
plt.close(fig)

st.caption(
    "Sumber breakpoint kategori: US EPA AQI PM2.5 24-hour breakpoints "
    "(https://www.airnow.gov/aqi/aqi-basics/) \n"
    "Sumber Data: Air Quality Dataset - PRSA, Beijing, Mar 2013 - Feb 2017."
    "(https://drive.google.com/file/d/1RhU3gJlkteaAQfyn9XOVAz7a5o1-etgr/view)"
)

st.divider()

