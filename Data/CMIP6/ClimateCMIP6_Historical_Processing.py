from pathlib import Path
import calendar
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date

BASE_DIR = Path(r"C:\Users\Kagiso\WaterNetwork\CMIP6")

MODEL = "ACCESS-CM2"
EXPERIMENT = "historical"

INPUT_DIR = BASE_DIR / MODEL / EXPERIMENT

OUTPUT_FILE = (
    BASE_DIR /
    "ACCESS_CM2_Historical_Climate_1995_2014.xlsx"
)

VARIABLES = [
    "pr",
    "tasmax",
    "tasmin",
    "hurs",
    "rsds",
    "rlds",
    "sfcWind"
]

YEARS = range(1995, 2015)


def read_variable(variable, year):

    filename = (
        f"Qatar_{MODEL}_{EXPERIMENT}_"
        f"{variable}_{year}.nc"
    )

    filepath = INPUT_DIR / variable / filename

    if not filepath.exists():
        raise FileNotFoundError(filepath)

    with Dataset(str(filepath), "r") as ds:

        if variable not in ds.variables:
            raise ValueError(
                f"{variable} not found in {filepath.name}"
            )

        ncvar = ds.variables[variable]

        data = np.ma.filled(
            ncvar[:],
            np.nan
        ).astype(float)

        dimensions = list(ncvar.dimensions)

        if "time" not in dimensions:
            raise ValueError(
                f"Missing time dimension: {filepath.name}"
            )

        for dimension in dimensions[:]:

            if dimension not in [
                "time", "lat", "lon"
            ]:

                axis = dimensions.index(dimension)

                if data.shape[axis] != 1:
                    raise ValueError(
                        f"Unexpected dimension {dimension}"
                    )

                data = np.take(data, 0, axis=axis)
                dimensions.pop(axis)

        order = [
            dimensions.index("time"),
            dimensions.index("lat"),
            dimensions.index("lon")
        ]

        data = np.transpose(data, order)

        timevar = ds.variables["time"]

        dates = num2date(
            timevar[:],
            units=timevar.units,
            calendar=getattr(
                timevar, "calendar", "standard"
            )
        )

        dates = pd.to_datetime([
            f"{date.year:04d}-{date.month:02d}-{date.day:02d}"
            for date in dates
        ])

        units = getattr(ncvar, "units", "")

        latitude = np.asarray(
            ds.variables["lat"][:],
            dtype=float
        )

        longitude = np.asarray(
            ds.variables["lon"][:],
            dtype=float
        )

    if data.shape[0] != len(dates):
        raise ValueError(
            f"Time dimension mismatch: {filepath.name}"
        )

    return dates, data, units, latitude, longitude


def convert_units(variable, data, units):

    if variable == "pr":

        if units not in [
            "kg m-2 s-1",
            "kg m**-2 s**-1"
        ]:
            raise ValueError(
                f"Unexpected precipitation units: {units}"
            )

        return data * 86400.0

    if variable in ["tasmax", "tasmin"]:

        if units != "K":
            raise ValueError(
                f"Unexpected temperature units: {units}"
            )

        return data - 273.15

    if variable in ["rsds", "rlds"]:

        if units not in [
            "W m-2",
            "W m**-2"
        ]:
            raise ValueError(
                f"Unexpected radiation units: {units}"
            )

        return data * 0.0864

    if variable == "hurs":

        return data

    if variable == "sfcWind":

        return data

    raise ValueError(
        f"Unsupported variable: {variable}"
    )


def process_year(year):

    daily_frames = []
    reference_dates = None
    reference_lat = None
    reference_lon = None

    for variable in VARIABLES:

        dates, data, units, lat, lon = read_variable(
            variable, year
        )

        if reference_dates is None:

            reference_dates = dates
            reference_lat = lat
            reference_lon = lon

        else:

            if not dates.equals(reference_dates):
                raise ValueError(
                    f"Date mismatch for {variable}, {year}"
                )

            if (
                not np.array_equal(lat, reference_lat)
                or not np.array_equal(lon, reference_lon)
            ):
                raise ValueError(
                    f"Grid mismatch for {variable}, {year}"
                )

        data = convert_units(
            variable, data, units
        )

        spatial_mean = np.nanmean(
            data, axis=(1, 2)
        )

        daily_frames.append(
            pd.DataFrame({
                "Date": dates,
                variable: spatial_mean
            })
        )

    daily = daily_frames[0]

    for frame in daily_frames[1:]:

        daily = daily.merge(
            frame,
            on="Date",
            validate="one_to_one"
        )

    daily["Year"] = daily["Date"].dt.year
    daily["Month"] = daily["Date"].dt.month

    monthly = daily.groupby(
        ["Year", "Month"],
        as_index=False
    ).agg({
        "pr": "sum",
        "tasmax": "mean",
        "tasmin": "mean",
        "hurs": "mean",
        "rsds": "mean",
        "rlds": "mean",
        "sfcWind": "mean"
    })

    monthly = monthly.rename(columns={
        "pr": "Precipitation_mm_month",
        "tasmax": "Tmax_C",
        "tasmin": "Tmin_C",
        "hurs": "RH_percent",
        "rsds": "Rs_MJ_m2_day",
        "rlds": "Rlds_MJ_m2_day",
        "sfcWind": "Wind_ms"
    })

    monthly["Tmean_C"] = (
        monthly["Tmax_C"]
        + monthly["Tmin_C"]
    ) / 2

    monthly["Date"] = pd.to_datetime(
        monthly[["Year", "Month"]].assign(
            Day=1
        ).rename(columns={"Day": "day"})
    )

    return monthly


def main():

    print("=" * 65)
    print("ACCESS-CM2 HISTORICAL CLIMATE PROCESSING")
    print("=" * 65)

    all_years = []

    for year in YEARS:

        print(f"Processing {year}...")

        monthly = process_year(year)

        if len(monthly) != 12:
            raise ValueError(
                f"Unexpected monthly count for {year}"
            )

        all_years.append(monthly)

    result = pd.concat(
        all_years,
        ignore_index=True
    )

    result = result.sort_values(
        "Date"
    ).reset_index(drop=True)

    expected_dates = pd.date_range(
        "1995-01-01",
        "2014-12-01",
        freq="MS"
    )

    if not pd.DatetimeIndex(
        result["Date"]
    ).equals(expected_dates):
        raise ValueError(
            "Missing or duplicate monthly records."
        )

    if result.isna().any().any():
        raise ValueError(
            "Missing values detected."
        )

    if (
        result["Precipitation_mm_month"] < 0
    ).any():
        raise ValueError(
            "Negative precipitation detected."
        )

    output_columns = [
        "Date",
        "Year",
        "Month",
        "Precipitation_mm_month",
        "Tmax_C",
        "Tmin_C",
        "Tmean_C",
        "RH_percent",
        "Rs_MJ_m2_day",
        "Rlds_MJ_m2_day",
        "Wind_ms"
    ]

    result = result[output_columns]

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:

        result.to_excel(
            writer,
            sheet_name="Historical_1995_2014",
            index=False
        )

    annual_precipitation = result.groupby(
        "Year"
    )["Precipitation_mm_month"].sum()

    print("\n" + "=" * 65)
    print("PROCESSING SUMMARY")
    print("=" * 65)

    print("First month:", result["Date"].min().date())
    print("Last month:", result["Date"].max().date())
    print("Total months:", len(result))
    print("Missing values:", int(result.isna().sum().sum()))

    print(
        "Mean annual precipitation (mm):",
        round(annual_precipitation.mean(), 2)
    )

    print(
        "Mean temperature (C):",
        round(result["Tmean_C"].mean(), 2)
    )

    print("\nOutput:", OUTPUT_FILE)
    print("Historical processing completed successfully.")


if __name__ == "__main__":
    main()
