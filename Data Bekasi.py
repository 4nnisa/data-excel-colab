
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Judul aplikasi
st.title("Analisis Data Fiskal Kota Bekasi")
st.write("Aplikasi sederhana untuk analisis data fiskal.")

# Upload file CSV
file = st.file_uploader("Upload dataset CSV", type=["csv"])

if file is not None:
    df = pd.read_csv(file)

    # Memilih data Kota Bekasi
    if "Kota" in df.columns:
        df = df[df["Kota"] == "Kota Bekasi"]

    st.subheader("Data Fiskal")
    st.dataframe(df)

    # Statistik deskriptif
    st.subheader("Statistik Deskriptif")
    st.write(df.describe())

    # Grafik hubungan variabel
    if all(kolom in df.columns for kolom in
           ["bm_ekonomi", "PE"]):

        st.subheader("Grafik Belanja Ekonomi dan PE")

        fig, ax = plt.subplots()
        ax.scatter(df["bm_ekonomi"], df["PE"])
        ax.set_xlabel("Belanja Ekonomi")
        ax.set_ylabel("Pertumbuhan Ekonomi (PE)")
        ax.set_title("Hubungan Belanja Ekonomi dengan PE")

        st.pyplot(fig)

    else:
        st.warning("Kolom bm_ekonomi atau PE tidak ditemukan.")

else:
    st.info("Silakan upload file dataset CSV terlebih dahulu.")
