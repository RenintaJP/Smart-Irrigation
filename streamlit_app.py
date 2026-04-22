import streamlit as st
import requests
import time
import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Irigasi Smart", layout="wide")

# --- 2. AMBIL TOKEN DARI SECRETS ---
try:
    BLYNK_AUTH = st.secrets["BLYNK_AUTH"]
except KeyError:
    st.error("Token Blynk tidak ditemukan! Pastikan sudah setting di Advanced Settings Streamlit Cloud.")
    st.stop()

# Daftar Pin Sesuai ESP32 (V0 - V9)
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

# --- 3. FUNGSI AMBIL DATA (LEBIH AKURAT) ---
def get_blynk_data(pin):
    # Menggunakan server SGP1 karena kita di Indonesia
    url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&{pin}"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            val = response.text
            # Coba ubah ke angka agar presisi, jika gagal (seperti Status) biarkan teks
            try:
                if "." in val:
                    return float(val)
                return int(val)
            except:
                return val
        return 0
    except:
        return "N/A"

# --- 4. TAMPILAN DASHBOARD ---
st.title("Monitoring Smart Irrigation")
st.markdown("---")

placeholder = st.empty()

while True:
    with placeholder.container():
        # Ambil semua data sekaligus ke dalam dictionary
        data = {label: get_blynk_data(pin) for label, pin in PINS.items()}
        
        # --- Baris Atas: Status Sistem ---
        st.info(f"**Status Tanah:** {data['Status']}")

        # --- Baris 1: Sensor Utama ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Kelembapan Tanah", f"{data['Soil']} %")
        col2.metric("Suhu Tanah", f"{data['T_Soil']} °C")
        col3.metric("Suhu Udara", f"{data['T_Air']} °C")
        col4.metric("pH Tanah", data['pH'])

        # --- Baris 2: Nutrisi NPK & Cahaya ---
        st.markdown("### Kandungan Nutrisi & Cahaya")
        n_col, p_col, k_col, l_col = st.columns(4)
        n_col.metric("Nitrogen (N)", data['N'])
        p_col.metric("Fosfor (P)", data['P'])
        k_col.metric("Kalium (K)", data['K'])
        l_col.metric("Intensitas Cahaya", f"{data['Lux']} Lux")

        # --- Footer: Jam WIB ---
        # Membuat zona waktu UTC+7 secara eksplisit
        timezone_wib = datetime.timezone(datetime.timedelta(hours=7))
        sekarang = datetime.datetime.now(timezone_wib)
        waktu_sekarang = sekarang.strftime("%H:%M:%S")

        st.markdown("---")
        st.caption(f"Terakhir update (WIB): {waktu_sekarang}")

        # Refresh setiap 3 detik agar lebih sinkron dengan Blynk
        time.sleep(3)