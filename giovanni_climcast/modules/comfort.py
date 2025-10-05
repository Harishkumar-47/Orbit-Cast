import streamlit as st
import numpy as np
import plotly.graph_objects as go

def compute_comfort_index(temp, humidity):
    return temp - 0.55 * (1 - humidity / 100) * (temp - 14.5)

def display_comfort_index(ds, var):
    if "temp" in var.lower() and "humidity" in ds.data_vars:
        temp = ds[var].mean(dim=["lat", "lon"]).values.flatten()
        humidity = ds["humidity"].mean(dim=["lat", "lon"]).values.flatten()
        comfort_scores = compute_comfort_index(temp, humidity)
        avg_score = np.mean(comfort_scores)
        st.metric("🧘 Comfort Index", f"{avg_score:.2f}")

def display_risk_meter(ds, var):
    if "time" not in ds[var].dims:
        return

    data = ds[var].mean(dim=["lat", "lon"]).to_series()
    hot_days = sum(data > 35)
    wet_days = sum(data > 50) if "precip" in var.lower() else 0
    windy_days = sum(data > 60) if "wind" in var.lower() else 0
    risk_score = hot_days * 2 + wet_days * 1.5 + windy_days * 1.5

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={'text': "Weather Risk Level"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "red" if risk_score > 70 else "orange" if risk_score > 40 else "green"}
        }
    ))
    st.plotly_chart(fig)
