import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import re

def list_regions():
    return [
        "Global", "India", "Europe", "North America", "Africa",
        "Australia", "South America", "East Asia", "Middle East"
    ]

def get_region_bbox(region):
    regions = {
        "Global": (-90, 90, -180, 180),
        "India": (8, 37, 68, 97),
        "Europe": (35, 70, -10, 40),
        "North America": (15, 70, -130, -60),
        "Africa": (-35, 37, -20, 55),
        "Australia": (-45, -10, 110, 155),
        "South America": (-55, 15, -80, -35),
        "East Asia": (5, 55, 100, 145),
        "Middle East": (10, 40, 35, 65)
    }
    return regions.get(region, (-90, 90, -180, 180))

def list_vars(ds):
    vars_with_units = []
    for var in ds.data_vars:
        unit = ds[var].attrs.get("units", "")
        icon = "🌧️" if "precip" in var.lower() else \
               "🌡️" if "temp" in var.lower() else \
               "💨" if "wind" in var.lower() else "📊"
        label = f"{icon} {var} ({unit})" if unit else f"{icon} {var}"
        vars_with_units.append(label)
    return vars_with_units

def extract_var_name(label):
    parts = label.split(" ")
    for part in parts:
        if "_" in part and not part.startswith("("):
            return part.strip()
    return label.strip()

def plot_map(ds, var_label):
    var = extract_var_name(var_label)
    try:
        data = ds[var].mean(dim="time") if "time" in ds[var].dims else ds[var]
        fig, ax = plt.subplots(figsize=(8, 4))
        data.plot(ax=ax, cmap="viridis")
        ax.set_title(f"Spatial Map: {var}")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"❌ Map plot failed: {e}")

def plot_timeseries(ds, var_label):
    var = extract_var_name(var_label)
    try:
        ts = ds[var].mean(dim=["lat", "lon"]).to_series()
        ts.index = pd.to_datetime(ts.index)
        st.line_chart(ts)
    except Exception as e:
        st.error(f"❌ Time-series plot failed: {e}")
