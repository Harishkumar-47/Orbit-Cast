import streamlit as st
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt

def forecast_variable(ds, var, steps=6):
    try:
        ts = ds[var].mean(dim=["lat", "lon"]).to_series()
        ts.index = pd.to_datetime(ts.index)
        model = SARIMAX(ts, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12))
        results = model.fit(disp=False)
        forecast = results.forecast(steps=steps)
        return forecast
    except Exception as e:
        st.error(f"Forecast failed: {e}")
        return None

def plot_forecast(original_ts, forecast_series):
    try:
        future_dates = pd.date_range(start=original_ts.index[-1], periods=len(forecast_series)+1, freq="MS")[1:]
        forecast_df = pd.Series(forecast_series.values, index=future_dates)

        fig, ax = plt.subplots(figsize=(10, 4))
        original_ts.plot(ax=ax, label="Historical", color="blue")
        forecast_df.plot(ax=ax, label="Forecast", color="orange")
        ax.set_title("Climate Forecast")
        ax.legend()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Plot failed: {e}")
