# Proyek Analisis Data

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_folium import st_folium
import folium

# Custom CSS untuk tema warna dashboard
st.markdown(
    """
    <style>
    /* background utama dengan gradasi biru muda dan abu-abu */
    .reportview-container {
        background: linear-gradient(to right, #f0f4f8, #d9e2ec);
    }
    /* Ubah sidebar background */
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #f0f4f8, #d9e2ec);
    }
    /* metric card */
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True
)

# Load dataset 
df_combined = pd.read_csv("dashboard/combined_data.csv", parse_dates=["datetime"])

st.title("Dashboard Analisis Polusi Udara Beijing")

# Scorecard 
st.markdown("### Total Data dan Indikator Utama")
# SIDEBAR: Filter Data
st.sidebar.header("Filter Data")
# Filter rentang tanggal
start_date = st.sidebar.date_input("Mulai", value=pd.to_datetime("2013-03-01"))
end_date = st.sidebar.date_input("Selesai", value=pd.to_datetime("2017-02-28"))
# Filter stasiun dengan opsi "Semua"
station_option = st.sidebar.selectbox("Pilih Stasiun", ["Semua"] + list(df_combined["station"].unique()))

# Terapkan filter tanggal
df_filtered = df_combined[(df_combined["datetime"] >= pd.to_datetime(start_date)) & 
                          (df_combined["datetime"] <= pd.to_datetime(end_date))]
# Terapkan filter stasiun jika tidak memilih "Semua"
if station_option != "Semua":
    df_filtered = df_filtered[df_filtered["station"] == station_option]

# Tampilkan scorecard dengan metric
col1, col2, col3 = st.columns(3)
col1.metric("Total Data", df_filtered.shape[0])
col2.metric("Rata-rata PM2.5", f"{df_filtered['PM2.5'].mean():.2f} µg/m³")
col3.metric("Rata-rata PM10", f"{df_filtered['PM10'].mean():.2f} µg/m³")

# VISUALISASI 1: Perbandingan Tingkat Polusi dengan Bar Chart
st.header("Perbandingan Tingkat Polusi")
st.subheader("Rata-rata PM2.5 dan PM10 Berdasarkan Stasiun")
# Hitung rata-rata untuk masing-masing stasiun
avg_values = df_filtered.groupby("station")[["PM2.5", "PM10"]].mean().reset_index()

fig, ax = plt.subplots(figsize=(10,6))
width = 0.35  # lebar bar
x = range(len(avg_values))
ax.bar(x, avg_values["PM2.5"], width, label="PM2.5", color="#4a90e2")
ax.bar([p + width for p in x], avg_values["PM10"], width, label="PM10", color="#50e3c2")
ax.set_xticks([p + width/2 for p in x])
ax.set_xticklabels(avg_values["station"])
ax.set_title("Rata-rata Konsentrasi Polusi per Stasiun")
ax.set_xlabel("Stasiun")
ax.set_ylabel("Rata-rata Konsentrasi (µg/m³)")
ax.legend()
st.pyplot(fig)

# VISUALISASI 2: Tren Waktu PM2.5 dengan Line Chart
st.header("Tren Waktu PM2.5")
fig2, ax2 = plt.subplots(figsize=(12,5))
sns.lineplot(data=df_filtered, x="datetime", y="PM2.5", hue="station", ax=ax2, marker="o", palette="Set1")
ax2.set_title(f"Tren PM2.5 dari {start_date} sampai {end_date}")
ax2.set_xlabel("Waktu")
ax2.set_ylabel("PM2.5 (µg/m³)")
plt.xticks(rotation=45)
st.pyplot(fig2)

# VISUALISASI 3: Analisis Geospasial dengan Folium
st.header("Analisis Geospasial")
st.subheader("Peta Distribusi Polusi (PM2.5)")
# Buat peta dasar Folium (pusat di Beijing)
m = folium.Map(location=[39.9, 116.4], zoom_start=10)

# Koordinat untuk masing-masing stasiun (dimasukkan secara manual)
locations = {
    "Aotizhongxin": [39.982, 116.417],
    "Changping": [40.218, 116.231]
}

# Hitung rata-rata PM2.5 per stasiun berdasarkan data yang sudah difilter
avg_pm25 = df_filtered.groupby("station")["PM2.5"].mean()
# Tambahkan marker ke peta untuk setiap stasiun yang ada pada data yang difilter
for station, coords in locations.items():
    if station in avg_pm25.index:
        folium.CircleMarker(
            location=coords,
            radius=avg_pm25[station] / 10,  # Sesuaikan skala radius
            popup=f"{station}: {avg_pm25[station]:.2f} µg/m³",
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.6
        ).add_to(m)

# Tampilkan peta menggunakan st_folium
st_folium(m, width=700, height=500)
