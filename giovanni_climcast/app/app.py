import streamlit as st
import xarray as xr
import pandas as pd
import folium
from streamlit_folium import st_folium

from modules import upload, variables, analyze, forecast, classifier, comfort

st.set_page_config(page_title="ClimaCast Dashboard", layout="wide")
st.title("🌍 ClimaCast: Climate Risk & Forecast Dashboard")

st.sidebar.header("🔧 Controls")
demo_mode = st.sidebar.checkbox("Use Demo Dataset")
ds = upload.load_or_demo(demo_mode)

if ds is not None:
    region = st.sidebar.selectbox("🌐 Region", variables.list_regions())
    bbox = variables.get_region_bbox(region)
    lat_min, lat_max, lon_min, lon_max = bbox
    ds_cropped = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

    var_label = st.sidebar.selectbox("📌 Variable", variables.list_vars(ds_cropped))
    var = variables.extract_var_name(var_label)

    if "time" in ds_cropped.dims:
        date_range = ds_cropped["time"].values
        start_date = st.sidebar.date_input("📅 Start Date", value=pd.to_datetime(str(date_range[0])))
        end_date = st.sidebar.date_input("📅 End Date", value=pd.to_datetime(str(date_range[-1])))
        ds_cropped = ds_cropped.sel(time=slice(start_date, end_date))
    else:
        st.sidebar.warning("⚠️ No time dimension found.")

    threshold = st.sidebar.slider("📊 Threshold Value", 0.0, 100.0, value=50.0)

    tabs = st.tabs([
        "🏁 Start", "📁 Upload", "🗺️ Map", "📊 Summary",
        "📈 Time-Series", "📈 Forecast", "📋 Conditions", "🗺️ Interactive", "📤 Export"
    ])

    with tabs[0]:
        st.markdown("Welcome to ClimaCast! Upload a dataset or use demo mode to explore climate risks.")

    with tabs[1]:
        st.write("✅ Dataset loaded.")
        st.write("Dimensions:", list(ds_cropped.dims))
        st.write("Variables:", list(ds_cropped.data_vars))

    with tabs[2]:
        st.subheader("🗺️ Spatial Map")
        variables.plot_map(ds_cropped, var_label)

    with tabs[3]:
        st.subheader("📊 Climate Summary for Users")
        user_stats = analyze.compute_user_friendly_stats(ds_cropped, var)
        for k, v in user_stats.items():
            st.write(f"🔹 **{k}**: {v}")
        comfort.display_comfort_index(ds_cropped, var)
        comfort.display_risk_meter(ds_cropped, var)

    with tabs[4]:
        st.subheader("📈 Time-Series Plot")
        variables.plot_timeseries(ds_cropped, var_label)

    with tabs[5]:
        st.subheader("📈 Forecast")
        if "time" in ds_cropped[var].dims:
            steps = st.slider("🔮 Months to Forecast", 1, 12, value=6)
            forecast_result = forecast.forecast_variable(ds_cropped, var, steps)
            if forecast_result is not None:
                original_ts = ds_cropped[var].mean(dim=["lat", "lon"]).to_series()
                forecast.plot_forecast(original_ts, forecast_result)
                labels = classifier.label_forecast(forecast_result, var_type=var)
                st.write("🔮 Forecasted Conditions:")
                st.write(labels)

                forecast_df = pd.DataFrame({
                    "Date": forecast_result.index,
                    "Forecast": forecast_result.values,
                    "Condition": labels
                })
                st.download_button("📥 Download Forecast CSV", forecast_df.to_csv(index=False), "forecast.csv")
        else:
            st.warning("⚠️ Selected variable has no time dimension.")

    with tabs[6]:
        st.subheader("📋 Condition Summary")
        classified_df, condition_summary = classifier.classify_conditions(ds_cropped, var)
        if classified_df is not None:
            st.dataframe(classified_df)
            st.json(condition_summary)
            st.download_button("📥 Download Condition Summary CSV", classified_df.to_csv(index=False), "conditions.csv")
        else:
            st.warning(condition_summary.get("Error", "Unknown error in classification."))

    with tabs[7]:
        st.subheader("🗺️ Interactive Map")
        m = folium.Map(location=[20, 78], zoom_start=4)
        m.add_child(folium.LatLngPopup())
        st.markdown("Click anywhere on the map to get weather insights.")
        map_data = st_folium(m, width=700, height=500)

        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            st.success(f"📍 You clicked: {lat:.2f}, {lon:.2f}")
            ds_point = ds.sel(lat=lat, lon=lon, method="nearest")
            st.write("🌡️ Temperature:", float(ds_point[var].values))
            comfort.display_comfort_index(ds_point, var)
            comfort.display_risk_meter(ds_point, var)

    with tabs[8]:
        st.subheader("📤 Export Options")
        st.write("Coming soon: Download filtered dataset and visualizations.")

else:
    st.warning("⚠️ No dataset loaded. Upload a file or enable demo mode.")



