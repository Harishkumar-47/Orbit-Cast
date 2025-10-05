# validator.py

import xarray as xr

def validate_nc_file(path):
    print(f"🔍 Validating: {path}")
    try:
        ds = xr.open_dataset(path)
    except Exception as e:
        print(f"❌ Failed to open file: {e}")
        return

    print("\n✅ Variables found:")
    for var in ds.data_vars:
        dims = ds[var].dims
        shape = ds[var].shape
        print(f" - {var}: dims={dims}, shape={shape}")

    print("\n📐 Dimensions:")
    for dim in ds.dims:
        print(f" - {dim}: size={ds.dims[dim]}")

    print("\n🕒 Time Axis Check:")
    if "time" in ds.dims:
        print("✅ 'time' dimension is present.")
        print(f" - Time range: {str(ds['time'].values[0])} to {str(ds['time'].values[-1])}")
    else:
        print("⚠️ No 'time' dimension found. Time-series plots will not work.")

    print("\n📊 Sample Data Preview:")
    for var in list(ds.data_vars)[:3]:  # Preview first 3 variables
        print(f"\n🔸 {var} sample:")
        print(ds[var].values[0] if "time" in ds[var].dims else ds[var].values)

# Example usage
validate_nc_file("data/wind_speed_2010_2025.nc")
