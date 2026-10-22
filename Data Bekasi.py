
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Judul aplikasi
st.title("Analisis Data Fiskal Kota Bekasi")
st.write("Analisis data belanja dan pertumbuhan ekonomi.")

# Membaca dataset
try:
    df = pd.read_csv("dataset_fiskal.csv")

    # Filter Kota Bekasi
    if "Kota" in df.columns:
        df = df[df["Kota"] == "Kota Bekasi"]

    st.subheader("Data Fiskal")
    st.dataframe(df)

    # Statistik deskriptif
    st.subheader("Statistik Deskriptif")
    st.write(df.describe())

    # Grafik
    if "bm_ekonomi" in df.columns and "PE" in df.columns:
        fig, ax = plt.subplots()
        ax.scatter(df["bm_ekonomi"], df["PE"])
        ax.set_xlabel("Belanja Ekonomi")
        ax.set_ylabel("Pertumbuhan Ekonomi")
        ax.set_title("Belanja Ekonomi dan PE")

        st.pyplot(fig)
    else:
        st.warning("Kolom bm_ekonomi atau PE tidak ditemukan.")

except FileNotFoundError:
    st.error("File dataset_fiskal.csv tidak ditemukan di repository GitHub.")
    
