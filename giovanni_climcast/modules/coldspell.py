# modules/storm.py

import streamlit as st
import matplotlib.pyplot as plt

def show_storm_map(ds, wind_var="WS2M", pressure_var="PS", wind_thresh=15, pressure_thresh=100000):
    st.subheader("🌪️ Storm Risk Map")

    wind = ds[wind_var]
    pressure = ds[pressure_var]

    storm_mask = (wind > wind_thresh) & (pressure < pressure_thresh)

    fig, ax = plt.subplots(figsize=(10, 5))
    storm_mask.mean(dim="time").plot(ax=ax, cmap="Blues")
    ax.set_title("Storm Risk Zones")
    st.pyplot(fig)
