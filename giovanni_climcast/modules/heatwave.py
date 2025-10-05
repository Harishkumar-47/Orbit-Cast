# modules/heatwave.py

import streamlit as st
import matplotlib.pyplot as plt

def show_heatwave_map(ds, var="T2M", anomaly_threshold=5.0, temp_threshold=35.0):
    st.subheader("🔥 Heatwave Risk Map")

    temp_data = ds[var]
    anomaly = temp_data - temp_data.mean(dim="time")
    heatwave_mask = (anomaly > anomaly_threshold) & (temp_data > temp_threshold)

    fig, ax = plt.subplots(figsize=(10, 5))
    heatwave_mask.mean(dim="time").plot(ax=ax, cmap="Reds")
    ax.set_title("Heatwave Risk Zones")
    st.pyplot(fig)
