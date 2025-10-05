import streamlit as st
import numpy as np

def compute_user_friendly_stats(ds, var):
    try:
        data = ds[var].values.flatten()
        data = data[~np.isnan(data)]

        stats = {}
        if "temp" in var.lower():
            stats["Average Temperature (°C)"] = round(float(np.mean(data)), 2)
            stats["Maximum Temperature (°C)"] = round(float(np.max(data)), 2)
        elif "wind" in var.lower():
            stats["Maximum Wind Speed (km/h)"] = round(float(np.max(data)), 2)
            stats["Average Wind Speed (km/h)"] = round(float(np.mean(data)), 2)
        elif "precip" in var.lower():
            stats["Total Rainfall (mm)"] = round(float(np.sum(data)), 2)
            stats["Average Daily Rainfall (mm)"] = round(float(np.mean(data)), 2)
        else:
            stats["Average Value"] = round(float(np.mean(data)), 2)
            stats["Maximum Value"] = round(float(np.max(data)), 2)

        stats["Data Points"] = int(len(data))
        return stats
    except Exception as e:
        st.error(f"Stats failed: {e}")
        return {}
