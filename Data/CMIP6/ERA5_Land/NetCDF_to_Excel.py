import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path

FILES = [
    "data_stream-moda.nc",
    "cvl.area-subset.26.2.51.7.24.5.50.6.nc",
    "cvh.area-subset.26.2.51.7.24.5.50.6.nc",
    "slt.area-subset.26.2.51.7.24.5.50.6.nc",
]

OUT_XLSX = "ERA5_monthly_2009_2025_ALL_SELECTED.xlsx"

def open_fix(path):
    ds = xr.open_dataset(path, engine="netcdf4")

    # Standardize coord names if needed
    rename = {}
    if "lat" in ds.coords: rename["lat"] = "latitude"
    if "lon" in ds.coords: rename["lon"] = "longitude"
    if "valid_time" in ds.dims: rename["valid_time"] = "time"
    if "valid_time" in ds.coords: rename["valid_time"] = "time"
    if rename:
        ds = ds.rename(rename)

    return ds

# Open
datasets = [open_fix(Path(f)) for f in FILES]

# Align to a common lat/lon/time grid (prevents merge issues)
datasets = xr.align(*datasets, join="outer")

# Merge
ds = xr.merge(datasets, compat="override", join="outer")

print("\nVariables found:\n", list(ds.data_vars))
print("Dims:", ds.dims)

# Drop scalar “artifact” vars if present (these are not climate series)
drop_if_present = [v for v in ["cvl", "cvh", "slt"] if v in ds.data_vars]
if drop_if_present:
    ds = ds.drop_vars(drop_if_present)

# Spatial mean (one value per month)
spatial_dims = [d for d in ["latitude", "longitude"] if d in ds.dims]
ds_mean = ds.mean(dim=spatial_dims, skipna=True)

# Build monthly table
time = ds_mean["time"]
df = pd.DataFrame({
    "Year": time.dt.year.values,
    "Month": time.dt.month.values,
})

for var in ds_mean.data_vars:
    df[var] = ds_mean[var].values

# Add a readable Date column (optional, helps Excel)
df["Date"] = pd.to_datetime(dict(year=df["Year"], month=df["Month"], day=1))

# Metadata sheet
meta_rows = []
for var in ds.data_vars:
    meta_rows.append({
        "variable": var,
        "units": ds[var].attrs.get("units", ""),
        "long_name": ds[var].attrs.get("long_name", ds[var].attrs.get("standard_name", "")),
        "dims": str(ds[var].dims),
    })
meta = pd.DataFrame(meta_rows)

with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="monthly_area_mean", index=False)
    meta.to_excel(writer, sheet_name="metadata", index=False)

print(f"\n Saved: {OUT_XLSX}")
print("Columns in Excel:", list(df.columns))
