import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_lstm_results(actual, predicted, dates):
    """
    Fungsi untuk menampilkan grafik interaktif antara data asli vs prediksi.
    """
    fig = go.Figure()

    # Menambahkan garis data asli (Actual)
    fig.add_trace(go.Scatter(
        x=dates, 
        y=actual, 
        mode='lines',
        name='Data Asli (Actual)',
        line=dict(color='royalblue', width=2)
    ))

    # Menambahkan garis hasil prediksi (Predicted)
    fig.add_trace(go.Scatter(
        x=dates, 
        y=predicted, 
        mode='lines',
        name='Prediksi LSTM',
        line=dict(color='firebrick', width=2, dash='dot')
    ))

    # Mengatur layout agar informatif
    fig.update_layout(
        title='Analisis Pola Musiman: Data Asli vs Prediksi LSTM',
        xaxis_title='Rentang Waktu',
        yaxis_title='Nilai',
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Simulasi Penggunaan di Streamlit ---
st.title("Monitoring Performa Model LSTM")

# Contoh data dummy (Ganti dengan data hasil model.predict() kamu)
dates = pd.date_range(start='2023-01-01', periods=100)
actual_data = np.sin(np.linspace(0, 10, 100)) + np.random.normal(0, 0.1, 100) # Pola musiman
predicted_data = np.sin(np.linspace(0, 10, 100)) # Pola prediksi yang mulus

plot_lstm_results(actual_data, predicted_data, dates)