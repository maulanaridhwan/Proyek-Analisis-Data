# proyek analisis data

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_folium import st_folium
import folium

#  CSS untuk tema dashboard
st.markdown(
    """
    <style>
    /* Background utama dengan gradasi biru muda dan abu-abu */
    .reportview-container {
        background: linear-gradient(to right, #f0f4f8, #d9e2ec);
    }
    /* Sidebar background */
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #f0f4f8, #d9e2ec);
    }
    /* Scorecard: latar putih, teks biru muda */
    .stMetric {
        background-color: #ffffff !important;
        border: 1px solid #d9e2ec;
        border-radius: 10px;
        padding: 10px;
    }
    .stMetric * {
        color: #187bcd !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# Load dataset 
df_combined = pd.read_csv("dashboard/combined_data.csv", parse_dates=["datetime"])

st.title("Dashboard Analisis Polusi Udara Beijing")

# SIDEBAR: Filter Data
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input("Mulai", value=pd.to_datetime("2013-03-01"))
end_date = st.sidebar.date_input("Selesai", value=pd.to_datetime("2017-02-28"))
station_option = st.sidebar.selectbox("Pilih Stasiun", ["Semua"] + list(df_combined["station"].unique()))

# Terapkan filter tanggal
df_filtered = df_combined[(df_combined["datetime"] >= pd.to_datetime(start_date)) & 
                          (df_combined["datetime"] <= pd.to_datetime(end_date))]
# Terapkan filter stasiun jika tidak memilih "Semua"
if station_option != "Semua":
    df_filtered = df_filtered[df_filtered["station"] == station_option]

# Scorecard 
col1, col2, col3 = st.columns(3)
col1.metric("Total Data", df_filtered.shape[0])
col2.metric("Rata-rata PM2.5", f"{df_filtered['PM2.5'].mean():.2f} µg/m³")
col3.metric("Rata-rata PM10", f"{df_filtered['PM10'].mean():.2f} µg/m³")

# VISUALISASI: Bar Chart Perbandingan Rata-rata Polusi (Pertanyaan 1)
st.header("Perbandingan Tingkat Polusi")
st.subheader("Rata-rata PM2.5 dan PM10 Berdasarkan Stasiun")
avg_values = df_filtered.groupby("station")[["PM2.5", "PM10"]].mean().reset_index()

fig1, ax1 = plt.subplots(figsize=(10,6))
width = 0.35
x = range(len(avg_values))
ax1.bar(x, avg_values["PM2.5"], width, label="PM2.5", color="#4a90e2")
ax1.bar([p + width for p in x], avg_values["PM10"], width, label="PM10", color="#50e3c2")
ax1.set_xticks([p + width/2 for p in x])
ax1.set_xticklabels(avg_values["station"])
ax1.set_title("Rata-rata Konsentrasi Polusi per Stasiun")
ax1.set_xlabel("Stasiun")
ax1.set_ylabel("Rata-rata Konsentrasi (µg/m³)")
ax1.legend()
st.pyplot(fig1)

# VISUALISASI: Tren Waktu PM2.5 dengan Line Chart
st.header("Tren Waktu PM2.5")
fig2, ax2 = plt.subplots(figsize=(12,5))
sns.lineplot(data=df_filtered, x="datetime", y="PM2.5", hue="station", ax=ax2, marker="o", palette="Set1")
ax2.set_title(f"Tren PM2.5 dari {start_date} sampai {end_date}")
ax2.set_xlabel("Waktu")
ax2.set_ylabel("PM2.5 (µg/m³)")
plt.xticks(rotation=45)
st.pyplot(fig2)

# VISUALISASI: Scatter Plot Hubungan Kondisi Cuaca dengan Polusi (Pertanyaan 2)
st.header("Pengaruh Kondisi Cuaca terhadap Polusi")

# Scatter Plot: Kecepatan Angin vs PM2.5
st.subheader("Hubungan antara Kecepatan Angin (WSPM) dan PM2.5")
fig2, ax2 = plt.subplots(figsize=(10,6))
sns.scatterplot(data=df_filtered, x="WSPM", y="PM2.5", hue="station", palette="Set1", alpha=0.6, ax=ax2)
ax2.set_title("Hubungan Kecepatan Angin dengan PM2.5")
ax2.set_xlabel("Kecepatan Angin (m/s)")
ax2.set_ylabel("PM2.5 (µg/m³)")
st.pyplot(fig2)

# Scatter Plot: Suhu vs PM2.5
st.subheader("Hubungan antara Suhu (TEMP) dan PM2.5")
fig3, ax3 = plt.subplots(figsize=(10,6))
sns.scatterplot(data=df_filtered, x="TEMP", y="PM2.5", hue="station", palette="Set2", alpha=0.6, ax=ax3)
ax3.set_title("Hubungan Suhu dengan PM2.5")
ax3.set_xlabel("Suhu (°C)")
ax3.set_ylabel("PM2.5 (µg/m³)")
st.pyplot(fig3)

# VISUALISASI 3: Analisis Geospasial dengan Folium
st.header("Analisis Geospasial")
st.subheader("Peta Distribusi Polusi (PM2.5)")
m = folium.Map(location=[39.9, 116.4], zoom_start=10)
locations = {
    "Aotizhongxin": [39.982, 116.417],
    "Changping": [40.218, 116.231]
}
avg_pm25 = df_filtered.groupby("station")["PM2.5"].mean()
for station, coords in locations.items():
    if station in avg_pm25.index:
        folium.CircleMarker(
            location=coords,
            radius=avg_pm25[station] / 10,
            popup=f"{station}: {avg_pm25[station]:.2f} µg/m³",
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.6
        ).add_to(m)
st_folium(m, width=700, height=500)
