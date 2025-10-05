import numpy as np
import pandas as pd

def classify_conditions(ds, var):
    if "time" not in ds[var].dims:
        return None, {"Error": "Selected variable has no time dimension."}

    data = ds[var].mean(dim=["lat", "lon"]).to_series()
    data.index = pd.to_datetime(data.index)
    labels = []

    for value in data:
        if "temp" in var.lower():
            labels.append("Very Hot" if value > 35 else "Very Cold" if value < 5 else "Normal")
        elif "precip" in var.lower():
            labels.append("Very Wet" if value > 50 else "Normal")
        elif "wind" in var.lower():
            labels.append("Very Windy" if value > 60 else "Normal")
        elif "humidity" in var.lower():
            labels.append("Very Uncomfortable" if value > 70 else "Normal")
        else:
            labels.append("Normal")

    df = pd.DataFrame({
        "Date": data.index,
        "Value": data.values,
        "Condition": labels
    })

    summary = df["Condition"].value_counts(normalize=True).to_dict()
    summary = {k: f"{v*100:.2f}%" for k, v in summary.items()}
    return df, summary

def label_forecast(forecast_series, var_type="temp"):
    labels = []
    for value in forecast_series:
        if var_type == "temp":
            labels.append("Very Hot" if value > 35 else "Very Cold" if value < 5 else "Normal")
        elif var_type == "precip":
            labels.append("Very Wet" if value > 50 else "Normal")
        elif var_type == "wind":
            labels.append("Very Windy" if value > 60 else "Normal")
        elif var_type == "humidity":
            labels.append("Very Uncomfortable" if value > 70 else "Normal")
        else:
            labels.append("Normal")
    return labels

