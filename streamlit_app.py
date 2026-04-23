import streamlit as st
import requests
import time
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Irigasi Smart", layout="wide")

# --- 2. PENGATURAN KONEKSI ---
# Ganti TOKEN di bawah ini dengan Token Blynk kamu yang asli
BLYNK_AUTH = "BLcxBOK-Xa3y7hpoXhj5cjOTZbXS6OWw"

# Coba hubungkan ke Google Sheets
try:
    # Jika di localhost, pastikan URL gsheets sudah ada di .streamlit/secrets.toml
    # Jika belum ada, dashboard tetap jalan tapi tidak simpan data (Monitoring Only)
    conn = st.connection("gsheets", type=GSheetsConnection)
    gsheets_ready = True
except Exception as e:
    gsheets_ready = False

# --- 3. TAMPILAN DASHBOARD (UI STATIC) ---
st.title("Monitoring Smart Irrigation")
st.markdown(f"**Status Koneksi Google Sheets:** {'✅ Aktif' if gsheets_ready else '⚠️ Monitoring Saja (Belum Terkoneksi)'}")
st.markdown("---")

# Membuat wadah kosong (Placeholder) untuk data yang berubah-ubah
placeholder = st.empty()

# Variabel untuk mengatur interval simpan (dalam detik)
if 'last_save_time' not in st.session_state:
    st.session_state.last_save_time = time.time()

# --- 4. LOOPING PENGAMBILAN DATA ---
while True:
    with placeholder.container():
        # List pin yang mau diambil
        pins = ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9"]
        raw_values = []
        
        try:
            # Ambil data satu per satu secara cepat
            for pin in pins:
                url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&{pin}"
                res = requests.get(url, timeout=2)
                raw_values.append(res.text)
            
            # Jika semua data berhasil diambil
            if len(raw_values) == 10:
                # Setup Waktu WIB
                tz_wib = datetime.timezone(datetime.timedelta(hours=7))
                now = datetime.datetime.now(tz_wib)
                
                data = {
                    "Tanggal": now.strftime("%Y-%m-%d"),
                    "Waktu": now.strftime("%H:%M:%S"),
                    "Soil": raw_values[0], "T_Soil": raw_values[1], "T_Air": raw_values[2],
                    "H_Air": raw_values[3], "Lux": raw_values[4], "pH": raw_values[5],
                    "N": raw_values[6], "P": raw_values[7], "K": raw_values[8],
                    "Status": raw_values[9]
                }

                # --- BAGIAN VISUALISASI ---
                st.info(f"**Status Sistem:** {data['Status']}")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Kelembapan Tanah", f"{data['Soil']} %")
                c2.metric("Suhu Tanah", f"{data['T_Soil']} °C")
                c3.metric("Suhu Udara", f"{data['T_Air']} °C")
                c4.metric("pH Tanah", data['pH'])

                st.markdown("### Kandungan Nutrisi (NPK)")
                n_col, p_col, k_col, l_col = st.columns(4)
                n_col.metric("Nitrogen (N)", data['N'])
                p_col.metric("Fosfor (P)", data['P'])
                k_col.metric("Kalium (K)", data['K'])
                l_col.metric("Cahaya", f"{data['Lux']} Lux")

                # --- AUTO-SAVE GOOGLE SHEETS ---
                if gsheets_ready:
                    if time.time() - st.session_state.last_save_time > 10:
                        conn.create(data=pd.DataFrame([data]))
                        st.session_state.last_save_time = time.time()
                        st.toast("Data tersimpan ke Sheets")

                st.caption(f"Update: {data['Waktu']} WIB | Koneksi Stabil")
            
        except Exception as e:
            st.error(f"Gagal mengambil data: {e}")

    time.sleep(2)