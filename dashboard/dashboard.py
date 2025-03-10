import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_folium import st_folium
import folium

# Load dataset df_combined dari file CSV
df_combined = pd.read_csv("dashboard/combined_data.csv", parse_dates=["datetime"])
df_combined.head()

st.title("Dashboard Analisis Polusi Udara Beijing")

st.header("Perbandingan Tingkat Polusi")
st.subheader("Distribusi PM2.5 dan PM10 antara Aotizhongxin dan Changping")

fig1, ax1 = plt.subplots(figsize=(10,6))
sns.boxplot(x='station', y='PM2.5', data=df_combined, palette='Set2', ax=ax1)
ax1.set_title("Distribusi PM2.5")
ax1.set_xlabel("Stasiun")
ax1.set_ylabel("PM2.5 (µg/m³)")
st.pyplot(fig1)

fig2, ax2 = plt.subplots(figsize=(10,6))
sns.boxplot(x='station', y='PM10', data=df_combined, palette='Set2', ax=ax2)
ax2.set_title("Distribusi PM10")
ax2.set_xlabel("Stasiun")
ax2.set_ylabel("PM10 (µg/m³)")
st.pyplot(fig2)

st.header("Tren Waktu PM2.5")
fig3, ax3 = plt.subplots(figsize=(12,5))
sns.lineplot(data=df_combined, x="datetime", y="PM2.5", hue="station", ax=ax3)
ax3.set_title("Tren PM2.5 pada Waktu Tertentu")
plt.xticks(rotation=45)
st.pyplot(fig3)

st.header("Analisis Geospasial")
st.subheader("Peta Distribusi Polusi (PM2.5)")

# Buat peta dasar Folium, misalnya dengan pusat di Beijing
m = folium.Map(location=[39.9, 116.4], zoom_start=10)

# Misalnya, kita ingin menampilkan marker yang menunjukkan rata-rata PM2.5 per stasiun
locations = {
    "Aotizhongxin": [39.982, 116.417],
    "Changping": [40.218, 116.231]
}

avg_pm25 = df_combined.groupby("station")["PM2.5"].mean()

for station, coords in locations.items():
    folium.CircleMarker(
        location=coords,
        radius=avg_pm25[station] / 10,  # Sesuaikan skala radius
        popup=f"{station}: {avg_pm25[station]:.2f} µg/m³",
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.6
    ).add_to(m)

# Tampilkan peta di dashboard dengan st_folium
st_folium(m, width=700, height=500)

st.sidebar.header("Filter Data")

# Misalnya, filter berdasarkan stasiun
station_option = st.sidebar.selectbox("Pilih Stasiun", df_combined["station"].unique())
df_filtered = df_combined[df_combined["station"] == station_option]

st.sidebar.write("Jumlah data:", df_filtered.shape[0])

# Tampilkan diagram berdasarkan pilihan
st.subheader(f"Data Polusi untuk Stasiun: {station_option}")
fig4, ax4 = plt.subplots(figsize=(10,6))
sns.boxplot(x='station', y='PM2.5', data=df_filtered, palette='Set2', ax=ax4)
ax4.set_title(f"Distribusi PM2.5 di {station_option}")
st.pyplot(fig4)

st.sidebar.header("Filter Waktu")
start_date = st.sidebar.date_input("Mulai", value=pd.to_datetime("2013-03-01"))
end_date = st.sidebar.date_input("Selesai", value=pd.to_datetime("2017-02-28"))

df_filtered_time = df_combined[(df_combined["datetime"] >= pd.to_datetime(start_date)) & 
                               (df_combined["datetime"] <= pd.to_datetime(end_date))]
st.write("Jumlah data setelah filter waktu:", df_filtered_time.shape[0])
