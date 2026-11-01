from pathlib import Path
import calendar
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date

DATA_DIR = Path(r"C:\Users\Kagiso\WaterNetwork\CMIP6\ERA5_Land")

OLD_FILE = DATA_DIR / "f10386e8a0e92e89f74a59d6ef1b1547.nc"
NEW_FILE = DATA_DIR / "data_stream-moda.nc"

OUTPUT_FILE = DATA_DIR / "ERA5_Land_Climate_1995_2025.xlsx"

VARIABLES = [
    "t2m", "d2m", "u10", "v10",
    "sp", "ssrd", "tp"
]

LATITUDE_DEG = 25.35
ELEVATION_M = 0.0
ALBEDO = 0.23

GSC = 0.0820
SIGMA = 4.903e-9


def read_netcdf(filepath):

    if not filepath.exists():
        raise FileNotFoundError(filepath)

    with Dataset(str(filepath), "r") as ds:

        time_name = (
            "valid_time"
            if "valid_time" in ds.variables
            else "time"
        )

        time_var = ds.variables[time_name]

        dates = num2date(
            time_var[:],
            units=time_var.units,
            calendar=getattr(
                time_var, "calendar", "standard"
            )
        )

        dates = pd.to_datetime([
            f"{d.year:04d}-{d.month:02d}-01"
            for d in dates
        ])

        lat = np.asarray(
            ds.variables["latitude"][:],
            dtype=float
        )

        lon = np.asarray(
            ds.variables["longitude"][:],
            dtype=float
        )

        result = pd.DataFrame({"Date": dates})

        for variable in VARIABLES:

            if variable not in ds.variables:
                raise ValueError(
                    f"Missing {variable} in {filepath.name}"
                )

            ncvar = ds.variables[variable]

            data = np.ma.filled(
                ncvar[:], np.nan
            ).astype(float)

            dims = list(ncvar.dimensions)

            for extra_dim in ["number", "expver"]:

                if extra_dim in dims:

                    axis = dims.index(extra_dim)

                    if data.shape[axis] == 1:
                        data = np.take(data, 0, axis=axis)
                    else:
                        data = np.nanmean(data, axis=axis)

                    dims.pop(axis)

            expected = {
                time_name, "latitude", "longitude"
            }

            if set(dims) != expected:
                raise ValueError(
                    f"Unexpected dimensions: {dims}"
                )

            order = [
                dims.index(time_name),
                dims.index("latitude"),
                dims.index("longitude")
            ]

            data = np.transpose(data, order)

            result[variable] = np.nanmean(
                data, axis=(1, 2)
            )

    return result, lat, lon


def saturation_vapour_pressure(temp):

    return 0.6108 * np.exp(
        17.27 * temp / (temp + 237.3)
    )


def extraterrestrial_radiation(latitude, doy):

    phi = np.radians(latitude)

    dr = 1 + 0.033 * np.cos(
        2 * np.pi * doy / 365
    )

    delta = 0.409 * np.sin(
        2 * np.pi * doy / 365 - 1.39
    )

    omega = np.arccos(
        np.clip(
            -np.tan(phi) * np.tan(delta),
            -1, 1
        )
    )

    ra = (
        (24 * 60 / np.pi)
        * GSC
        * dr
        * (
            omega * np.sin(phi) * np.sin(delta)
            + np.cos(phi)
            * np.cos(delta)
            * np.sin(omega)
        )
    )

    return ra


def process_climate(df):

    df = df.copy()

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month

    df["Days_in_Month"] = [
        calendar.monthrange(int(y), int(m))[1]
        for y, m in zip(df["Year"], df["Month"])
    ]

    df["DOY"] = (
        df["Date"]
        + pd.to_timedelta(
            (df["Days_in_Month"] - 1) / 2,
            unit="D"
        )
    ).dt.dayofyear

    df["Tmean_C"] = df["t2m"] - 273.15
    df["Tdew_C"] = df["d2m"] - 273.15

    df["Wind10m_ms"] = np.sqrt(
        df["u10"] ** 2 + df["v10"] ** 2
    )

    df["Wind2m_ms"] = (
        df["Wind10m_ms"]
        * 4.87 / np.log(67.8 * 10 - 5.42)
    )

    df["Pressure_kPa"] = df["sp"] / 1000

    df["Precipitation_mm_month"] = (
        df["tp"] * 1000
        * df["Days_in_Month"]
    )

    df["Rs_MJ_m2_day"] = (
        df["ssrd"] / 1_000_000
    )

    df["es_kPa"] = saturation_vapour_pressure(
        df["Tmean_C"]
    )

    df["ea_kPa"] = saturation_vapour_pressure(
        df["Tdew_C"]
    )

    df["VPD_kPa"] = (
        df["es_kPa"] - df["ea_kPa"]
    ).clip(lower=0)

    df["Delta_kPa_C"] = (
        4098 * df["es_kPa"]
        / (df["Tmean_C"] + 237.3) ** 2
    )

    df["Gamma_kPa_C"] = (
        0.000665 * df["Pressure_kPa"]
    )

    df["Ra_MJ_m2_day"] = extraterrestrial_radiation(
        LATITUDE_DEG,
        df["DOY"].to_numpy()
    )

    df["Rso_MJ_m2_day"] = (
        0.75 + 2e-5 * ELEVATION_M
    ) * df["Ra_MJ_m2_day"]

    df["Rns_MJ_m2_day"] = (
        (1 - ALBEDO) * df["Rs_MJ_m2_day"]
    )

    cloud_ratio = (
        df["Rs_MJ_m2_day"]
        / df["Rso_MJ_m2_day"]
    ).clip(lower=0.3, upper=1.0)

    df["Rnl_MJ_m2_day"] = (
        SIGMA
        * (df["Tmean_C"] + 273.15) ** 4
        * (
            0.34 - 0.14
            * np.sqrt(df["ea_kPa"].clip(lower=0))
        )
        * (1.35 * cloud_ratio - 0.35)
    )

    df["Rn_MJ_m2_day"] = (
        df["Rns_MJ_m2_day"]
        - df["Rnl_MJ_m2_day"]
    )

    numerator = (
        0.408
        * df["Delta_kPa_C"]
        * df["Rn_MJ_m2_day"]
        + df["Gamma_kPa_C"]
        * (
            900 / (df["Tmean_C"] + 273.15)
        )
        * df["Wind2m_ms"]
        * df["VPD_kPa"]
    )

    denominator = (
        df["Delta_kPa_C"]
        + df["Gamma_kPa_C"]
        * (
            1 + 0.34 * df["Wind2m_ms"]
        )
    )

    df["ET0_mm_day"] = (
        numerator / denominator
    ).clip(lower=0)

    df["ET0_mm_month"] = (
        df["ET0_mm_day"]
        * df["Days_in_Month"]
    )

    df["MPD_mm_month"] = (
        df["ET0_mm_month"]
        - df["Precipitation_mm_month"]
    )

    df["P3_mm"] = (
        df["Precipitation_mm_month"]
        .rolling(window=3, min_periods=3)
        .sum()
    )

    return df


def main():

    print("=" * 65)
    print("ERA5-LAND CLIMATE PROCESSING: 1995-2025")
    print("=" * 65)

    print("\nReading 1995-2008...")
    old, lat_old, lon_old = read_netcdf(OLD_FILE)

    print("Reading 2009-2025...")
    new, lat_new, lon_new = read_netcdf(NEW_FILE)

    if (
        lat_old.shape != lat_new.shape
        or lon_old.shape != lon_new.shape
        or not np.allclose(lat_old, lat_new)
        or not np.allclose(lon_old, lon_new)
    ):
        raise ValueError("Spatial grids do not match.")

    old = old[
        old["Date"].between(
            "1995-01-01", "2008-12-01"
        )
    ]

    new = new[
        new["Date"].between(
            "2009-01-01", "2025-12-01"
        )
    ]

    combined = pd.concat(
        [old, new], ignore_index=True
    ).sort_values("Date").reset_index(drop=True)

    expected_dates = pd.date_range(
        "1995-01-01", "2025-12-01",
        freq="MS"
    )

    if not pd.DatetimeIndex(
        combined["Date"]
    ).equals(expected_dates):
        raise ValueError(
            "Missing, duplicated or unexpected months."
        )

    if combined[VARIABLES].isna().any().any():
        raise ValueError(
            "Missing meteorological data detected."
        )

    print("\nCalculating FAO-56 ET0...")

    combined = process_climate(combined)

    baseline = combined[
        combined["Year"].between(1995, 2014)
    ].copy()

    metadata = pd.DataFrame([
        ["Source", "ERA5-Land monthly averaged reanalysis"],
        ["Full period", "1995-2025"],
        ["Bias correction reference", "1995-2014"],
        ["Spatial method", "Unweighted grid mean"],
        ["ET0 method", "FAO-56 Penman-Monteith"],
        ["Radiation", "Estimated FAO-56 net radiation"],
        ["Latitude", LATITUDE_DEG],
        ["Elevation_m", ELEVATION_M],
        ["Precipitation", "Monthly mean daily accumulation x days"],
        ["Wind", "Magnitude of spatial-mean 10 m vector"],
    ], columns=["Property", "Value"])

    with pd.ExcelWriter(
        OUTPUT_FILE, engine="openpyxl"
    ) as writer:

        combined.to_excel(
            writer,
            sheet_name="ERA5_1995_2025",
            index=False
        )

        baseline.to_excel(
            writer,
            sheet_name="Baseline_1995_2014",
            index=False
        )

        metadata.to_excel(
            writer,
            sheet_name="Metadata",
            index=False
        )

    print("\n" + "=" * 65)
    print("PROCESSING SUMMARY")
    print("=" * 65)

    print("First month:", combined["Date"].min().date())
    print("Last month:", combined["Date"].max().date())
    print("Total months:", len(combined))
    print("Baseline months:", len(baseline))
    print("Missing input values:",
          int(combined[VARIABLES].isna().sum().sum()))

    print(
        "Mean annual precipitation (mm):",
        round(
            combined.groupby("Year")[
                "Precipitation_mm_month"
            ].sum().mean(), 2
        )
    )

    print(
        "Mean annual ET0 (mm):",
        round(
            combined.groupby("Year")[
                "ET0_mm_month"
            ].sum().mean(), 2
        )
    )

    print(
        "Mean air temperature (C):",
        round(combined["Tmean_C"].mean(), 2)
    )

    print("\nOutput:", OUTPUT_FILE)
    print("Processing completed successfully.")


if __name__ == "__main__":
    main()
