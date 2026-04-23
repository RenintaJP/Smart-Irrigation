import streamlit as st
import requests
import time
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Irigasi Smart", layout="wide")

# --- 2. KONEKSI & AMBIL TOKEN ---
try:
    BLYNK_AUTH = st.secrets["BLYNK_AUTH"]
    # Inisialisasi koneksi Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
except KeyError:
    st.error("Konfigurasi Secrets (BLYNK_AUTH) belum lengkap!")
    st.stop()

# --- 3. TAMPILAN DASHBOARD ---
st.title("Monitoring Smart Irrigation & Data Logging")
st.markdown("---")

placeholder = st.empty()

# Variabel session_state untuk mengatur waktu penyimpanan
if 'last_save_time' not in st.session_state:
    st.session_state.last_save_time = 0

while True:
    with placeholder.container():
        # OPSI TURBO: Batch Request V0-V9
        all_pins = "V0,V1,V2,V3,V4,V5,V6,V7,V8,V9"
        url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&{all_pins}"
        
        try:
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                raw_data = response.text.split(',')
                
                # Setup Waktu WIB
                timezone_wib = datetime.timezone(datetime.timedelta(hours=7))
                dt_now = datetime.datetime.now(timezone_wib)
                waktu_sekarang = dt_now.strftime("%H:%M:%S")
                tanggal_sekarang = dt_now.strftime("%Y-%m-%d")

                data = {
                    "Tanggal": tanggal_sekarang,
                    "Waktu": waktu_sekarang,
                    "Soil": raw_data[0], "T_Soil": raw_data[1], "T_Air": raw_data[2],
                    "H_Air": raw_data[3], "Lux": raw_data[4], "pH": raw_data[5],
                    "N": raw_data[6], "P": raw_data[7], "K": raw_data[8],
                    "Status": raw_data[9]
                }

                # --- Tampilan Visual (Metric) ---
                st.info(f"**Status Tanah:** {data['Status']}")

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Kelembapan Tanah", f"{data['Soil']} %")
                col2.metric("Suhu Tanah", f"{data['T_Soil']} °C")
                col3.metric("Suhu Udara", f"{data['T_Air']} °C")
                col4.metric("pH Tanah", data['pH'])

                st.markdown("### Kandungan Nutrisi & Cahaya")
                n_col, p_col, k_col, l_col = st.columns(4)
                n_col.metric("Nitrogen (N)", data['N'])
                p_col.metric("Fosfor (P)", data['P'])
                k_col.metric("Kalium (K)", data['K'])
                l_col.metric("Intensitas Cahaya", f"{data['Lux']} Lux")

                # --- FITUR AUTO-SAVE GOOGLE SHEETS ---
                # Interval simpan: Setiap 60 detik
                current_time = time.time()
                if current_time - st.session_state.last_save_time > 60:
                    try:
                        # Mengubah data terbaru menjadi DataFrame
                        df_to_save = pd.DataFrame([data])
                        
                        # Menambahkan data ke baris terakhir Google Sheets
                        conn.create(data=df_to_save)
                        
                        st.session_state.last_save_time = current_time
                        st.toast("Data otomatis tersimpan ke Google Sheets")
                    except Exception as gs_err:
                        st.error(f"Gagal simpan ke Sheets: {gs_err}")

                st.markdown("---")
                st.caption(f"Terakhir update (WIB): {waktu_sekarang} | Mode: Auto-Logging Aktif (60s)")
            
            else:
                st.warning("Menunggu data dari Server Blynk...")

        except Exception as e:
            st.error(f"Koneksi terputus: {e}")

    time.sleep(1)