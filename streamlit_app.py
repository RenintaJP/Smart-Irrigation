import streamlit as st
import requests
import pandas as pd
import time

# --- 1. KONFIGURASI AMAN ---
try:
    BLYNK_AUTH = st.secrets["BLYNK_AUTH"]
except KeyError:
    st.error("Token Blynk tidak ditemukan di secrets.toml!")
    st.stop()

# Daftar Pin Lengkap (V0 - V9)
PINS = {
    "Soil": "V0",
    "T_Soil": "V1",
    "T_Air": "V2",
    "H_Air": "V3",
    "Lux": "V4",
    "pH": "V5",
    "N": "V6",
    "P": "V7",
    "K": "V8",
    "Status": "V9"
}

st.set_page_config(page_title="Dashboard Irigasi Smart", layout="wide")
st.title("Monitoring Smart Irrigation")

# --- 2. FUNGSI AMBIL DATA ---
def get_blynk_data(pin):
    url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&{pin}"
    try:
        response = requests.get(url, timeout=2) # Tambah timeout agar tidak freeze
        if response.status_code == 200:
            return response.text
        return "0"
    except:
        return "N/A"

# --- 3. TAMPILAN DASHBOARD ---
placeholder = st.empty()

# Gunakan Loop Streamlit yang lebih stabil
while True:
    with placeholder.container():
        # Ambil data satu per satu
        data = {label: get_blynk_data(pin) for label, pin in PINS.items()}
        
        # --- Baris Atas: Status Sistem ---
        st.info(f"💡 **Status Perangkat:** {data['Status']}")

        # --- Baris 1: Lingkungan Utama ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Kelembapan Tanah", f"{data['Soil']} %")
        col2.metric("Suhu Tanah", f"{data['T_Soil']} °C")
        col3.metric("Suhu Udara", f"{data['T_Air']} °C")
        col4.metric("pH Tanah", data['pH'])

        # --- Baris 2: NPK & Cahaya ---
        st.markdown("---")
        st.subheader("Nutrisi Tanah & Intensitas Cahaya")
        n_col, p_col, k_col, l_col = st.columns(4)
        n_col.metric("Nitrogen (N)", data['N'])
        p_col.metric("Fosfor (P)", data['P'])
        k_col.metric("Kalium (K)", data['K'])
        l_col.metric("Cahaya", f"{data['Lux']} Lux")

        # --- Footer ---
        st.caption(f"Terakhir update: {time.strftime('%H:%M:%S')}")
        
    time.sleep(5) # Jeda 5 detik sebelum ambil data lagi