import streamlit as st
import requests
import time
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Irigasi Smart", layout="wide")

# --- 2. KONEKSI & AMBIL TOKEN ---
# Gunakan nilai manual jika di localhost agar tidak error secrets
BLYNK_AUTH = "BLcxBOK-Xa3y7hpoXhj5cjOTZbXS6OWw" 

try:
    # Inisialisasi koneksi Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    gsheets_ready = True
except Exception as e:
    st.warning(f"Koneksi Google Sheets belum aktif (Mode Monitoring Saja): {e}")
    gsheets_ready = False

# ... (kode title dll)

while True:
    with placeholder.container():
        url = f"https://sgp1.blynk.cloud/external/api/get?token={BLYNK_AUTH}&V0,V1,V2,V3,V4,V5,V6,V7,V8,V9"
        
        try:
            response = requests.get(url, timeout=5) # Naikkan timeout jadi 5
            
            if response.status_code == 200 and "," in response.text:
                raw_data = response.text.split(',')
                
                # --- (Proses data seperti biasa) ---
                # ... 
                
                # --- LOGIKA AUTO-SAVE (Hanya jalan jika gsheets_ready) ---
                current_time = time.time()
                if gsheets_ready and (current_time - st.session_state.last_save_time > 60):
                    try:
                        df_to_save = pd.DataFrame([data])
                        conn.create(data=df_to_save)
                        st.session_state.last_save_time = current_time
                        st.toast("Data masuk ke Google Sheets!", icon="💾")
                    except:
                        pass # Abaikan error save agar dashboard tidak berhenti
            else:
                st.warning("Data dari Blynk belum lengkap atau format salah...")

        except Exception as e:
            st.error(f"Gagal memanggil API Blynk: {e}")

    time.sleep(2)