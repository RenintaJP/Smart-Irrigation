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
        # URL Batch API Blynk (SGP1 = Singapore Server agar cepat)
        all_pins = "V0,V1,V2,V3,V4,V5,V6,V7,V8,V9"
        url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&{all_pins}"
        
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200 and "," in response.text:
                raw_data = response.text.split(',')
                
                # Setup Waktu Indonesia Barat (WIB)
                tz_wib = datetime.timezone(datetime.timedelta(hours=7))
                now = datetime.datetime.now(tz_wib)
                waktu_skrg = now.strftime("%H:%M:%S")
                tgl_skrg = now.strftime("%Y-%m-%d")

                # Masukkan data ke dictionary
                data = {
                    "Tanggal": tgl_skrg,
                    "Waktu": waktu_skrg,
                    "Soil": raw_data[0], "T_Soil": raw_data[1], "T_Air": raw_data[2],
                    "H_Air": raw_data[3], "Lux": raw_data[4], "pH": raw_data[5],
                    "N": raw_data[6], "P": raw_data[7], "K": raw_data[8],
                    "Status": raw_data[9]
                }

                # --- BAGIAN VISUALISASI ---
                st.info(f"**Status Sistem Saat Ini:** {data['Status']}")

                # Baris 1: Sensor Lingkungan
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Kelembapan Tanah", f"{data['Soil']} %")
                col2.metric("Suhu Tanah", f"{data['T_Soil']} °C")
                col3.metric("Suhu Udara", f"{data['T_Air']} °C")
                col4.metric("pH Tanah", data['pH'])

                # Baris 2: NPK & Cahaya
                st.markdown("### Kandungan Nutrisi (NPK) & Intensitas Cahaya")
                n_col, p_col, k_col, l_col = st.columns(4)
                n_col.metric("Nitrogen (N)", f"{data['N']} mg/kg")
                p_col.metric("Fosfor (P)", f"{data['P']} mg/kg")
                k_col.metric("Kalium (K)", f"{data['K']} mg/kg")
                l_col.metric("Cahaya", f"{data['Lux']} Lux")

                # --- LOGIKA AUTO-SAVE KE GOOGLE SHEETS ---
                # Default: Simpan setiap 60 detik (1 menit)
                if gsheets_ready:
                    durasi_jeda = time.time() - st.session_state.last_save_time
                    if durasi_jeda > 60:
                        try:
                            df_baru = pd.DataFrame([data])
                            # Append data ke Google Sheets
                            conn.create(data=df_baru)
                            st.session_state.last_save_time = time.time()
                            st.toast("Data berhasil dicatat ke dataset!")
                        except Exception as err_save:
                            st.error(f"Gagal simpan ke Sheets: {err_save}")

                st.markdown("---")
                st.caption(f"Terakhir Sinkronisasi: {waktu_skrg} WIB | Interval Logging: 60 Detik")

            else:
                st.warning("⚠️ Data belum diterima dari Blynk. Pastikan alat sudah ON dan mengirim data V0-V9.")

        except Exception as e:
            st.error(f"⚠️ Gangguan Koneksi: {e}")

    # Jeda 2 detik sebelum ambil data lagi (biar server tidak overload)
    time.sleep(2)