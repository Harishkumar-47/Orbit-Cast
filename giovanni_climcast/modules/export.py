# modules/export.py

import streamlit as st
import json

def generate_summary(region, var, stats, risk_level):
    return {
        "region": region,
        "variable": var,
        "mean": stats["mean"],
        "std_dev": stats["std"],
        "max": stats["max"],
        "min": stats["min"],
        "exceedance_chance": stats["exceedance_chance"],
        "risk_level": risk_level
    }

def export_json(summary):
    st.subheader("📤 Export Summary")
    json_str = json.dumps(summary, indent=2)
    st.download_button("Download Summary as JSON", data=json_str, file_name="climacast_summary.json", mime="application/json")
