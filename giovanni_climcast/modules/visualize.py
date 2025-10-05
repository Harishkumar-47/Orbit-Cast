# modules/visualize.py

import streamlit as st
import matplotlib.pyplot as plt

def show_summary(stats, risk_level):
    st.subheader("📊 Summary Statistics")
    st.write(f"**Mean:** {stats['mean']}")
    st.write(f"**Standard Deviation:** {stats['std']}")
    st.write(f"**Max:** {stats['max']}")
    st.write(f"**Min:** {stats['min']}")
    st.write(f"**Exceedance Chance:** {stats['exceedance_chance']}%")
    st.write(f"**Risk Level:** {risk_level}")

def plot_map(ds, var):
    st.subheader("🗺️ Spatial Map")
    fig, ax = plt.subplots(figsize=(10, 5))
    ds[var].plot(ax=ax, cmap="viridis")
    st.pyplot(fig)
