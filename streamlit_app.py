import streamlit as st
import requests
import pandas as pd
import time
import plotly.graph_objects as go # Tambahkan ini
import numpy as np # Untuk manipulasi data

# --- 1. KONFIGURASI AMAN ---
try:
    BLYNK_AUTH = st.secrets["BLYNK_AUTH"]
except KeyError:
    st.error("Token Blynk tidak ditemukan di secrets.toml!")
    st.stop()

PINS = {
    "Soil": "V0", "T_Soil": "V1", "T_Air": "V2", "H_Air": "V3",
    "Lux": "V4", "pH": "V5", "N": "V6", "P": "V7", "K": "V8", "Status": "V9"
}

st.set_page_config(page_title="Dashboard Irigasi Smart", layout="wide")
st.title("Monitoring & Prediksi Smart Irrigation")

# --- 2. FUNGSI AMBIL DATA ---
def get_blynk_data(pin):
    url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&{pin}"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            val = response.text
            try: return float(val)
            except: return val
        return 0
    except: return "N/A"

# --- 3. FUNGSI VISUALISASI LSTM ---
def plot_lstm_analysis():
    # Simulasi data (Ganti dengan hasil model.predict() kamu nanti)
    dates = pd.date_range(start='2024-01-01', periods=50, freq='H')
    actual = np.sin(np.linspace(0, 10, 50)) + np.random.normal(0, 0.1, 50)
    predicted = np.sin(np.linspace(0, 10, 50))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=actual, mode='lines', name='Data Historis', line=dict(color='royalblue')))
    fig.add_trace(go.Scatter(x=dates, y=predicted, mode='lines', name='Pola LSTM', line=dict(color='firebrick', dash='dot')))
    
    fig.update_layout(
        title="Analisis Pola Tren & Musiman (LSTM)",
        xaxis_title="Waktu",
        yaxis_title="Nilai Sensor",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 4. TAMPILAN DASHBOARD DENGAN TAB ---
tab1, tab2 = st.tabs(["Monitoring Real-time", "Analisis Pola LSTM"])

with tab1:
    placeholder = st.empty()

with tab2:
    st.subheader("Evaluasi Model Deep Learning")
    plot_lstm_analysis()
    st.write("Grafik di atas membandingkan data aktual lapangan dengan pola yang dipelajari oleh model LSTM.")

# --- 5. LOOP MONITORING (Hanya update Tab 1) ---
while True:
    with placeholder.container():
        data = {label: get_blynk_data(pin) for label, pin in PINS.items()}
        
        st.info(f"**Status Tanah:** {data['Status']}")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Kelembapan Tanah", f"{data['Soil']} %")
        col2.metric("Suhu Tanah", f"{data['T_Soil']} °C")
        col3.metric("Suhu Udara", f"{data['T_Air']} °C")
        col4.metric("pH Tanah", data['pH'])

        st.markdown("---")
        n_col, p_col, k_col, l_col = st.columns(4)
        n_col.metric("Nitrogen (N)", data['N'])
        p_col.metric("Fosfor (P)", data['P'])
        k_col.metric("Kalium (K)", data['K'])
        l_col.metric("Cahaya", f"{data['Lux']} Lux")

        waktu_wib = time.localtime(time.time() + 7*3600) 
        st.caption(f"Terakhir update: {time.strftime('%H:%M:%S', waktu_wib)}")
        
    time.sleep(5) # Naikkan ke 5 detik agar tidak membebani limit API Blynk