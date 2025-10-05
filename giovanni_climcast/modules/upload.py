import streamlit as st
import xarray as xr

def load_file():
    uploaded_file = st.file_uploader("📁 Upload NetCDF (.nc)", type=["nc"])
    if uploaded_file:
        st.write("📄 File name:", uploaded_file.name)
        st.write("📦 Size:", f"{uploaded_file.size / 1_000_000:.2f} MB")
        try:
            ds = xr.open_dataset(uploaded_file)
            st.success("✅ File loaded.")
            st.write("📌 Variables:", list(ds.data_vars))
            return ds
        except Exception as e:
            st.error(f"❌ Load failed: {e}")
    return None

def load_or_demo(demo_mode=False):
    if demo_mode:
        try:
            ds = xr.open_dataset("data/sample_precip.nc")
            st.success("🧪 Demo dataset loaded.")
            return ds
        except Exception as e:
            st.error(f"❌ Demo load failed: {e}")
    return load_file()
