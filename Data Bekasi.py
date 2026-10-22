
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="FiscalInsight | Data Fiskal",
    page_icon="🌸",
    layout="wide"
)

# =========================
# TEMA PINK PASTEL
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #FFF7FA;
}
[data-testid="stSidebar"] {
    background-color: #FCE8F0;
}
h1, h2, h3 {
    color: #A63D68;
}
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #F2C6D8;
    padding: 18px;
    border-radius: 15px;
}
.stButton > button {
    background-color: #E8A3BE;
    color: white;
    border-radius: 10px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Warna grafik pink pastel
WARNA = [
    "#D98EAD", "#EAB8CC", "#C87598",
    "#F2CEDC", "#B85C83", "#F5DCE6"
]

# =========================
# MEMBACA DATA
# =========================
@st.cache_data
def baca_data():
    return pd.read_csv("dataset_fiskal.csv", sep=None, engine="python")

try:
    data = baca_data()
except Exception as e:
    st.error("Dataset gagal dibaca. Pastikan dataset_fiskal.csv ada di GitHub.")
    st.stop()

# Periksa kolom
kolom_wajib = [
    "Kota", "Tahun", "PE",
    "bm_ekonomi", "bm_infrastruktur"
]

if not all(k in data.columns for k in kolom_wajib):
    st.error("Nama kolom dataset belum sesuai.")
    st.write("Kolom yang tersedia:", data.columns.tolist())
    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🌸 FiscalInsight")
st.sidebar.caption("Dashboard Analisis Data Fiskal")

halaman = st.sidebar.radio(
    "Navigasi",
    [
        "Beranda",
        "Perbandingan Kota",
        "Eksplorasi Data",
        "Analisis Mendalam"
    ]
)

st.sidebar.divider()

daftar_kota = sorted(data["Kota"].dropna().unique())

pilihan_kota = st.sidebar.multiselect(
    "Pilih kota",
    daftar_kota,
    default=["Kota Bekasi"] if "Kota Bekasi" in daftar_kota
    else daftar_kota[:1]
)

if not pilihan_kota:
    st.warning("Pilih minimal satu kota melalui sidebar.")
    st.stop()

df = data[data["Kota"].isin(pilihan_kota)].copy()

df["Tahun"] = pd.to_numeric(df["Tahun"], errors="coerce")
for kolom in ["PE", "bm_ekonomi", "bm_infrastruktur"]:
    df[kolom] = pd.to_numeric(df[kolom], errors="coerce")

df = df.dropna(
    subset=["Tahun", "PE", "bm_ekonomi", "bm_infrastruktur"]
)

if df.empty:
    st.warning("Tidak ada data valid untuk pilihan kota tersebut.")
    st.stop()

# =========================
# JUDUL
# =========================
st.title("🌸 Dashboard Analisis Data Fiskal")
st.write(
    "Eksplorasi belanja ekonomi, belanja infrastruktur, "
    "dan pertumbuhan ekonomi (PE)."
)

# =========================
# BERANDA
# =========================
if halaman == "Beranda":
    st.subheader("Ringkasan Data")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Jumlah Observasi", len(df))
    c2.metric("Rata-rata PE", f"{df['PE'].mean():.2f}")
    c3.metric(
        "Rata-rata Belanja Ekonomi",
        f"{df['bm_ekonomi'].mean():,.2f}"
    )
    c4.metric(
        "Rata-rata Belanja Infrastruktur",
        f"{df['bm_infrastruktur'].mean():,.2f}"
    )

    st.divider()

    kiri, kanan = st.columns(2)

    with kiri:
        st.subheader("Belanja Ekonomi dan PE")
        fig = px.scatter(
            df,
            x="bm_ekonomi",
            y="PE",
            color="Kota",
            hover_data=["Tahun"],
            trendline="ols" if len(df) >= 2 else None,
            color_discrete_sequence=WARNA,
            title="Hubungan Belanja Ekonomi dengan PE"
        )
        fig.update_layout(template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    with kanan:
        st.subheader("Belanja Infrastruktur dan PE")
        fig = px.scatter(
            df,
            x="bm_infrastruktur",
            y="PE",
            color="Kota",
            hover_data=["Tahun"],
            trendline="ols" if len(df) >= 2 else None,
            color_discrete_sequence=WARNA,
            title="Hubungan Belanja Infrastruktur dengan PE"
        )
        fig.update_layout(template="plotly_white", height=420)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Perkembangan PE per Tahun")
    fig = px.line(
        df.sort_values("Tahun"),
        x="Tahun",
        y="PE",
        color="Kota",
        markers=True,
        color_discrete_sequence=WARNA,
        title="Perubahan Pertumbuhan Ekonomi"
    )
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Data Fiskal")
    st.dataframe(df, use_container_width=True, hide_index=True)

# =========================
# PERBANDINGAN KOTA
# =========================
elif halaman == "Perbandingan Kota":
    st.subheader("Perbandingan Indikator Fiskal")

    indikator = st.selectbox(
        "Pilih indikator",
        ["PE", "bm_ekonomi", "bm_infrastruktur"]
    )

    ringkasan = (
        df.groupby("Kota", as_index=False)[indikator]
        .mean()
        .sort_values(indikator, ascending=False)
    )

    fig = px.bar(
        ringkasan,
        x="Kota",
        y=indikator,
        color="Kota",
        text_auto=".2f",
        color_discrete_sequence=WARNA,
        title=f"Perbandingan Rata-rata {indikator}"
    )
    fig.update_layout(template="plotly_white", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Peringkat Kota")
    st.dataframe(ringkasan, use_container_width=True, hide_index=True)

# =========================
# EKSPLORASI DATA
# =========================
elif halaman == "Eksplorasi Data":
    st.subheader("Eksplorasi Hubungan Variabel")

    x_var = st.selectbox(
        "Variabel sumbu X",
        ["bm_ekonomi", "bm_infrastruktur", "Tahun"]
    )

    y_var = st.selectbox(
        "Variabel sumbu Y",
        ["PE", "bm_ekonomi", "bm_infrastruktur"]
    )

    fig = px.scatter(
        df,
        x=x_var,
        y=y_var,
        color="Kota",
        hover_data=["Tahun"],
        color_discrete_sequence=WARNA,
        title=f"Hubungan {x_var} dan {y_var}"
    )
    fig.update_layout(template="plotly_white", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Statistik Deskriptif")
    st.dataframe(
        df[["PE", "bm_ekonomi", "bm_infrastruktur"]]
        .describe().T,
        use_container_width=True
    )

    st.download_button(
        "📥 Unduh Data CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="data_fiskal.csv",
        mime="text/csv"
    )

# =========================
# ANALISIS MENDALAM
# =========================
elif halaman == "Analisis Mendalam":
    st.subheader("Matriks Korelasi")

    angka = df[["PE", "bm_ekonomi", "bm_infrastruktur"]]

    if len(df) >= 2:
        korelasi = angka.corr()

        fig = px.imshow(
            korelasi,
            text_auto=".2f",
            color_continuous_scale=[
                "#F8E4EC", "#E8A3BE", "#A63D68"
            ],
            zmin=-1,
            zmax=1,
            title="Korelasi Antarvariabel"
        )
        fig.update_layout(template="plotly_white", height=450)
        st.plotly_chart(fig, use_container_width=True)

        st.write(
            "Korelasi menunjukkan arah dan kekuatan hubungan "
            "linear antarvariabel, tetapi tidak membuktikan "
            "hubungan sebab-akibat."
        )
    else:
        st.warning("Diperlukan minimal dua observasi untuk menghitung korelasi.")

    st.subheader("Statistik Ringkas")
    st.dataframe(angka.describe(), use_container_width=True)

st.sidebar.caption("FiscalInsight 🌷 | Dashboard Data Fiskal")
