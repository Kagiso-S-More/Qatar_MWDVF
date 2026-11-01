from pathlib import Path
import calendar
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date

BASE_DIR = Path(r"C:\Users\Kagiso\WaterNetwork\CMIP6")
MODEL = "ACCESS-CM2"
SCENARIOS = ["ssp245", "ssp585"]
YEARS = range(2031, 2071)
VARIABLES = ["pr", "tasmax", "tasmin", "hurs", "rsds", "rlds", "sfcWind"]
PARAMETER_FILE = BASE_DIR / "ACCESS_CM2_Historical_Bias_Correction.xlsx"
OUTPUT_DIR = BASE_DIR / "Future_Processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CORRECTION_VARIABLES = {
    "Precipitation_mm_month": "Precipitation_mm_month",
    "Tmean_C": "Tmean_C",
    "RH_percent": "RH_percent",
    "Rs_MJ_m2_day": "Rs_MJ_m2_day",
    "Wind10m_ms": "Wind10m_ms",
}


def read_parameters():
    frame = pd.read_excel(PARAMETER_FILE, sheet_name="Correction_Parameters")
    parameters = {}
    for _, row in frame.iterrows():
        key = (str(row["Variable"]).strip(), int(row["Month"]))
        parameters[key] = (str(row["Method"]).strip().lower(), float(row["Correction"]))
    for name in CORRECTION_VARIABLES:
        for month in range(1, 13):
            if (name, month) not in parameters:
                raise ValueError(f"Missing correction parameter: {name}, month {month}")
    return parameters


def locate_file(scenario, variable, year):
    folder = BASE_DIR / MODEL / scenario / variable
    expected = folder / f"Qatar_{MODEL}_{scenario}_{variable}_{year}.nc"
    if expected.is_file():
        return expected
    candidates = sorted(folder.glob(f"*{variable}*{year}*.nc")) if folder.exists() else []
    if len(candidates) == 1:
        return candidates[0]
    raise FileNotFoundError(f"Expected file not found (or ambiguous): {expected}")


def read_daily(scenario, variable, year):
    path = locate_file(scenario, variable, year)
    with Dataset(str(path), "r") as ds:
        if variable not in ds.variables:
            raise ValueError(f"Variable {variable} missing from {path}")
        data = np.ma.filled(ds.variables[variable][:], np.nan).astype(float)
        dimensions = ds.variables[variable].dimensions
        if "time" not in dimensions:
            raise ValueError(f"No time dimension in {path}")
        axis = dimensions.index("time")
        data = np.moveaxis(data, axis, 0)
        times = ds.variables["time"]
        dates = num2date(times[:], units=times.units,
                         calendar=getattr(times, "calendar", "standard"),
                         only_use_cftime_datetimes=True)
        units = getattr(ds.variables[variable], "units", "")
        if data.ndim != 3:
            raise ValueError(f"Expected daily time/latitude/longitude grid: {path}")
        # Each downloaded subset uses the same spatial extent; take the
        # unweighted grid mean, matching the initial historical workflow.
        values = np.nanmean(data, axis=(1, 2))
        months = np.array([int(d.month) for d in dates])
        years = np.array([int(d.year) for d in dates])
        if np.any(years != year):
            raise ValueError(f"Unexpected year in {path}")
        if len(values) < 360 or not np.isfinite(values).all():
            raise ValueError(f"Incomplete/non-finite daily data: {path}")
        return values, months, units


def aggregate_variable(variable, values, months, units, year):
    monthly = {}
    for month in range(1, 13):
        selected = values[months == month]
        if selected.size != calendar.monthrange(year, month)[1]:
            raise ValueError(f"Missing daily values for {variable}, {year}-{month:02d}")
        if variable == "pr":
            # NEX-GDDP-CMIP6 precipitation flux: kg m-2 s-1 = mm/s
            monthly[month] = float(np.sum(selected * 86400.0))
        elif variable in ("tasmax", "tasmin"):
            monthly[month] = float(np.mean(selected) - 273.15)
        elif variable in ("rsds", "rlds"):
            # W m-2 -> MJ m-2 day-1
            monthly[month] = float(np.mean(selected) * 0.0864)
        else:
            monthly[month] = float(np.mean(selected))
    return monthly


def correct(value, name, month, parameters):
    method, factor = parameters[(name, month)]
    if not np.isfinite(factor):
        raise ValueError(f"Non-finite correction: {name}, {month}")
    if method == "additive":
        result = value + factor
    elif method == "multiplicative":
        result = value * factor
    else:
        raise ValueError(f"Unknown correction method: {method}")
    if name == "Precipitation_mm_month":
        result = max(0.0, result)
    elif name == "RH_percent":
        result = float(np.clip(result, 0.0, 100.0))
    elif name in ("Rs_MJ_m2_day", "Wind10m_ms"):
        result = max(0.0, result)
    return result


def process_year(scenario, year, parameters):
    series = {}
    for variable in VARIABLES:
        values, months, units = read_daily(scenario, variable, year)
        series[variable] = aggregate_variable(variable, values, months, units, year)
    rows = []
    for month in range(1, 13):
        tmax = series["tasmax"][month]
        tmin = series["tasmin"][month]
        tmean = (tmax + tmin) / 2.0
        raw = {
            "Precipitation_mm_month": series["pr"][month],
            "Tmean_C": tmean,
            "RH_percent": series["hurs"][month],
            "Rs_MJ_m2_day": series["rsds"][month],
            "Wind10m_ms": series["sfcWind"][month],
        }
        row = {
            "Scenario": scenario,
            "Year": year,
            "Month": month,
            "Date": pd.Timestamp(year, month, 1),
            "Tmax_C_Raw": tmax,
            "Tmin_C_Raw": tmin,
            "Rlds_MJ_m2_day_Raw": series["rlds"][month],
        }
        for name, value in raw.items():
            row[f"{name}_Raw"] = value
            row[f"{name}_Corrected"] = correct(value, name, month, parameters)
        rows.append(row)
    return rows


def main():
    parameters = read_parameters()
    print("=" * 65)
    print("ACCESS-CM2 FUTURE CLIMATE PROCESSING (2031-2070)")
    print("=" * 65)
    all_rows = []
    for scenario in SCENARIOS:
        scenario_rows = []
        print(f"\nProcessing {scenario.upper()}...")
        for year in YEARS:
            year_rows = process_year(scenario, year, parameters)
            scenario_rows.extend(year_rows)
            print(f"  {year}: 12 months processed")
        frame = pd.DataFrame(scenario_rows)
        if len(frame) != 480 or frame.isna().any().any():
            raise ValueError(f"Incomplete output for {scenario}")
        output = OUTPUT_DIR / f"{MODEL}_{scenario}_Monthly_Corrected_2031_2070.xlsx"
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            frame.to_excel(writer, sheet_name="Monthly_2031_2070", index=False)
            frame[frame.Year.between(2031, 2050)].to_excel(
                writer, sheet_name="Near_Term_2031_2050", index=False)
            frame[frame.Year.between(2051, 2070)].to_excel(
                writer, sheet_name="Mid_Century_2051_2070", index=False)
        all_rows.extend(scenario_rows)
        print(f"Saved: {output}")
    combined = pd.DataFrame(all_rows)
    combined_path = OUTPUT_DIR / "ACCESS_CM2_Future_Climate_2031_2070_Combined.csv"
    combined.to_csv(combined_path, index=False)
    print("\nPROCESSING SUMMARY")
    print(f"Scenarios: {', '.join(SCENARIOS)}")
    print(f"Total months: {len(combined)}")
    print(f"Missing values: {int(combined.isna().sum().sum())}")
    print(f"Combined CSV: {combined_path}")
    print("Processing completed successfully.")


if __name__ == "__main__":
    main()
