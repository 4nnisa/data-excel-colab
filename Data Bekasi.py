
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

st.set_page_config(
    page_title="Analisis Fiskal Bekasi",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Aplikasi Analisis Regresi Data Fiskal")
st.write("Analisis PE, belanja modal ekonomi, dan infrastruktur.")

# ---------- Membaca dataset ----------
FILE = "dataset_fiskal_97_hipoFull (1).csv"

uploaded = st.sidebar.file_uploader(
    "Upload dataset CSV (opsional)",
    type=["csv"]
)

@st.cache_data
def baca_data(file):
    return pd.read_csv(file)

try:
    if uploaded is not None:
        df = baca_data(uploaded)
    else:
        df = baca_data(FILE)

    kolom_wajib = [
        "Kota", "Tahun", "PE",
        "bm_ekonomi", "bm_infrastruktur"
    ]

    if not all(k in df.columns for k in kolom_wajib):
        st.error("Dataset tidak memiliki semua kolom yang diperlukan.")
        st.stop()

    # ---------- Sidebar ----------
    st.sidebar.header("⚙️ Pengaturan")

    daftar_kota = sorted(df["Kota"].dropna().unique())
    default_kota = (
        daftar_kota.index("Kota Bekasi")
        if "Kota Bekasi" in daftar_kota else 0
    )

    kota = st.sidebar.selectbox(
        "Pilih Kota",
        daftar_kota,
        index=default_kota
    )

    d = df[df["Kota"] == kota].copy()
    d = d.dropna(
        subset=["Tahun", "PE", "bm_ekonomi", "bm_infrastruktur"]
    )
    d = d.sort_values("Tahun").reset_index(drop=True)

    if len(d) < 4:
        st.warning("Data lengkap terlalu sedikit untuk regresi.")
        st.stop()

    # ---------- Model regresi ----------
    y = d["PE"].to_numpy(dtype=float)
    x1 = d["bm_ekonomi"].to_numpy(dtype=float)
    x2 = d["bm_infrastruktur"].to_numpy(dtype=float)

    model1 = LinearRegression().fit(x1.reshape(-1, 1), y)
    model2 = LinearRegression().fit(x2.reshape(-1, 1), y)

    X = d[["bm_ekonomi", "bm_infrastruktur"]]
    model3 = LinearRegression().fit(X, y)

    pred1 = model1.predict(x1.reshape(-1, 1))
    pred2 = model2.predict(x2.reshape(-1, 1))
    pred3 = model3.predict(X)

    r2_1 = r2_score(y, pred1)
    r2_2 = r2_score(y, pred2)
    r2_3 = r2_score(y, pred3)
    rmse = np.sqrt(mean_squared_error(y, pred3))

    # ---------- Ringkasan ----------
    st.subheader(f"Ringkasan Data: {kota}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jumlah Observasi", len(d))
    c2.metric("R² Regresi 3D", f"{r2_3:.4f}")
    c3.metric("RMSE", f"{rmse:.4f}")
    c4.metric(
        "Periode",
        f"{int(d['Tahun'].min())}–{int(d['Tahun'].max())}"
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Data",
        "📊 Statistik",
        "📈 Regresi",
        "🔮 Prediksi"
    ])

    # ---------- Tab Data ----------
    with tab1:
        st.subheader("Pratinjau Data")
        st.dataframe(
            d[["Tahun", "PE", "bm_ekonomi", "bm_infrastruktur"]],
            use_container_width=True
        )

        st.download_button(
            "⬇️ Unduh Data",
            d.to_csv(index=False).encode("utf-8"),
            file_name="data_fiskal.csv",
            mime="text/csv"
        )

    # ---------- Tab Statistik ----------
    with tab2:
        st.subheader("Statistik Deskriptif")
        st.dataframe(
            d[["PE", "bm_ekonomi", "bm_infrastruktur"]]
            .describe().T,
            use_container_width=True
        )

        st.subheader("Matriks Korelasi")
        corr = d[
            ["PE", "bm_ekonomi", "bm_infrastruktur"]
        ].corr()

        fig_corr = px.imshow(
            corr,
            text_auto=".3f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Korelasi Antarvariabel"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # ---------- Tab Regresi ----------
    with tab3:
        st.subheader("Hasil Regresi")

        hasil_model = pd.DataFrame({
            "Model": [
                "PE vs bm_ekonomi",
                "PE vs bm_infrastruktur",
                "PE vs kedua variabel"
            ],
            "R²": [r2_1, r2_2, r2_3]
        })
        st.dataframe(hasil_model, use_container_width=True)

        st.markdown("**Persamaan Regresi 3D**")
        st.latex(
            rf"\widehat{{PE}} = {model3.intercept_:.4f}"
            rf" + ({model3.coef_[0]:.4f})X_1"
            rf" + ({model3.coef_[1]:.4f})X_2"
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=d["Tahun"], y=y,
            mode="lines+markers",
            name="PE Aktual"
        ))
        fig.add_trace(go.Scatter(
            x=d["Tahun"], y=pred3,
            mode="lines+markers",
            name="PE Prediksi"
        ))
        fig.update_layout(
            title="PE Aktual vs Prediksi",
            xaxis_title="Tahun",
            yaxis_title="PE"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Grafik hubungan dua variabel bebas dengan PE
        fig2 = px.scatter(
            d,
            x="bm_ekonomi",
            y="PE",
            color="bm_infrastruktur",
            hover_data=["Tahun"],
            title="PE dan Belanja Modal Ekonomi"
        )
        st.plotly_chart(fig2, use_container_width=True)

        residual = y - pred3
        fig3 = px.scatter(
            x=pred3,
            y=residual,
            labels={
                "x": "PE Prediksi",
                "y": "Residual"
            },
            title="Plot Residual Regresi 3D"
        )
        fig3.add_hline(y=0, line_dash="dash")
        st.plotly_chart(fig3, use_container_width=True)

    # ---------- Tab Prediksi ----------
    with tab4:
        st.subheader("Coba Prediksi PE")

        nilai1 = st.number_input(
            "Nilai bm_ekonomi",
            value=float(x1.mean())
        )
        nilai2 = st.number_input(
            "Nilai bm_infrastruktur",
            value=float(x2.mean())
        )

        hasil = model3.predict(
            pd.DataFrame({
                "bm_ekonomi": [nilai1],
                "bm_infrastruktur": [nilai2]
            })
        )[0]

        st.success(f"Prediksi PE = {hasil:.4f}")

        hasil_df = d[
            ["Tahun", "PE", "bm_ekonomi", "bm_infrastruktur"]
        ].copy()
        hasil_df["Prediksi_PE"] = pred3
        hasil_df["Residual"] = y - pred3

        st.download_button(
            "⬇️ Unduh Hasil Regresi CSV",
            hasil_df.to_csv(index=False).encode("utf-8"),
            file_name="hasil_regresi_bekasi.csv",
            mime="text/csv"
        )

except FileNotFoundError:
    st.error(
        "Dataset tidak ditemukan. Upload file CSV ke repository "
        "yang sama dengan app.py, atau gunakan fitur upload."
    )
except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
