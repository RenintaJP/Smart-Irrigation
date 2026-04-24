import streamlit as st
import requests
import time
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Smart Irrigation", 
    layout="wide", 
)

# --- 2. AMBIL DATA PRIVAT DARI SECRETS ---
try:
    BLYNK_AUTH = st.secrets["BLYNK_AUTH"]
except Exception as e:
    st.error("Konfigurasi Secrets (Token Blynk) belum diatur!")
    st.stop()

# --- 3. PENGATURAN KONEKSI ---
try:
    # Memastikan koneksi menggunakan Service Account dari secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    gsheets_ready = True
except Exception as e:
    st.sidebar.warning(f"GSheets Connection Error: {e}")
    gsheets_ready = False

# --- 4. UI STATIC ---
st.title("Smart Irrigation Monitoring")
status_color = "" if gsheets_ready else ""
st.markdown(f"**Status Google Sheets:** {status_color} {'Terhubung' if gsheets_ready else 'Mode Monitoring (Offline)'}")
st.markdown("---")

# Placeholder untuk update konten secara dinamis
placeholder = st.empty()

# Simpan waktu terakhir sinkronisasi di session state
if 'last_save_time' not in st.session_state:
    st.session_state.last_save_time = time.time()

# --- 5. FUNGSI HELPER ---
def get_sensor_data():
    """Mengambil data dari 10 Virtual Pin Blynk secara berurutan"""
    pins = ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9"]
    raw_values = []
    
    try:
        for pin in pins:
            url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&{pin}"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                raw_values.append(res.text)
            else:
                raw_values.append("0") 
        
        tz_wib = datetime.timezone(datetime.timedelta(hours=7))
        now = datetime.datetime.now(tz_wib)
        
        return {
            "Tanggal": now.strftime("%Y-%m-%d"),
            "Waktu": now.strftime("%H:%M:%S"),
            "Soil": raw_values[0], "T_Soil": raw_values[1], "T_Air": raw_values[2],
            "H_Air": raw_values[3], "Lux": raw_values[4], "pH": raw_values[5],
            "N": raw_values[6], "P": raw_values[7], "K": raw_values[8],
            "Status": raw_values[9]
        }
    except Exception as e:
        return None

# --- 6. MAIN LOOP (REAL-TIME UPDATE) ---
while True:
    current_data = get_sensor_data()
    
    if current_data:
        with placeholder.container():
            # Tampilan Status Tanah
            st.info(f"**Status Tanah:** {current_data['Status']}")
            
            # Baris 1: Sensor Tanah & Udara
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Kelembapan Tanah", f"{current_data['Soil']} %")
            m2.metric("Suhu Tanah", f"{current_data['T_Soil']} °C")
            m3.metric("Suhu Udara", f"{current_data['T_Air']} °C")
            m4.metric("Kelembapan Udara", f"{current_data['H_Air']} %")

            # Baris 2: NPK & Cahaya
            st.markdown("### Nutrisi & Lingkungan")
            n1, n2, n3, n4 = st.columns(4)
            n1.metric("Nitrogen (N)", f"{current_data['N']} mg/kg")
            n2.metric("Fosfor (P)", f"{current_data['P']} mg/kg")
            n3.metric("Kalium (K)", f"{current_data['K']} mg/kg")
            n4.metric("Intensitas Cahaya", f"{current_data['Lux']} Lux")
            
            st.metric("pH Tanah", current_data['pH'])

            # --- LOGIKA JAM UPDATE (VISUAL) ---
            timezone_wib = datetime.timezone(datetime.timedelta(hours=7))
            jam_update = datetime.datetime.now(timezone_wib).strftime("%H:%M:%S")
            
            st.markdown("---")
            st.caption(f"**Terakhir Update:** {jam_update} WIB | Mode: Turbo Batch Sync")

            # --- AUTO-SAVE (LOGGING KE GOOGLE SHEETS) ---
            if gsheets_ready:
                waktu_sekarang_detik = time.time()
                selisih = waktu_sekarang_detik - st.session_state.last_save_time

                # Interval simpan setiap 60 detik
                if selisih >= 60:
                    try:
                        # Ambil data lama, gabung dengan data baru, lalu timpa ulang (Append simulation)
                        df_old = conn.read(worksheet="Sheet1", ttl=0)
                        df_new = pd.DataFrame([current_data])
                        df_final = pd.concat([df_old, df_new], ignore_index=True)
                        
                        conn.update(worksheet="Sheet1", data=df_final)
                        
                        # Reset timer
                        st.session_state.last_save_time = waktu_sekarang_detik
                        st.toast(f"Data Berhasil Masuk Sheets")
                    except Exception as e:
                        st.error(f"Gagal simpan data: {e}")

    # Delay pengambilan data dari Blynk (2 detik)
    time.sleep(2)