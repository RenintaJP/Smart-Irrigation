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

# --- 3. TAMPILAN DASHBOARD ---
st.title("Monitoring Smart Irrigation")
st.markdown("---")

placeholder = st.empty()

while True:
    with placeholder.container():
        # OPSI TURBO: Mengambil semua pin (V0 sampai V9) dalam SATU kali panggil
        all_pins = "V0,V1,V2,V3,V4,V5,V6,V7,V8,V9"
        url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&{all_pins}"
        
        try:
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                # Blynk akan mengembalikan data yang dipisahkan koma, misal: "42,27,27,80,365,7,10,12,15,Aman"
                raw_data = response.text.split(',')
                
                # Memasukkan data ke dalam dictionary (Pastikan urutan sesuai V0-V9)
                # raw_data[0] = V0, raw_data[1] = V1, dst.
                data = {
                    "Soil": raw_data[0], "T_Soil": raw_data[1], "T_Air": raw_data[2],
                    "H_Air": raw_data[3], "Lux": raw_data[4], "pH": raw_data[5],
                    "N": raw_data[6], "P": raw_data[7], "K": raw_data[8],
                    "Status": raw_data[9]
                }

                # --- Tampilan Atas: Status ---
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

                # --- Footer: Jam WIB (Fix Timezone) ---
                timezone_wib = datetime.timezone(datetime.timedelta(hours=7))
                waktu_sekarang = datetime.datetime.now(timezone_wib).strftime("%H:%M:%S")
                
                st.markdown("---")
                st.caption(f"Terakhir update (WIB): {waktu_sekarang} | Mode: Turbo Batch Sync")
            
            else:
                st.warning("Menunggu data dari Server Blynk...")

        except Exception as e:
            st.error(f"Koneksi terputus: {e}")

    # Karena sudah pakai Batch, jeda 1 detik sudah sangat aman dan cepat
    time.sleep(1)