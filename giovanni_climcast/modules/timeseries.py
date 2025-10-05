# modules/timeseries.py

import streamlit as st
import matplotlib.pyplot as plt

def plot_timeseries(ds, var):
    st.subheader("📈 Time-Series Plot")

    if "time" not in ds[var].dims:
        st.warning(f"Variable '{var}' has no time dimension.")
        return

    mean_over_space = ds[var].mean(dim=["lat", "lon"])

    fig, ax = plt.subplots(figsize=(10, 4))
    mean_over_space.plot(ax=ax, color="green")
    ax.set_title(f"Time-Series of {var}")
    ax.set_xlabel("Time")
    ax.set_ylabel(var)
    st.pyplot(fig)
