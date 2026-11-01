from pathlib import Path
import calendar
import math
import numpy as np
import pandas as pd

BASE_DIR = Path(r"C:\Users\Kagiso\WaterNetwork\CMIP6")
INPUT_DIR = BASE_DIR / "Future_Processed"
OUTPUT_DIR = INPUT_DIR / "ET0"
SCENARIOS = ("ssp245", "ssp585")
LATITUDE_DEG = 25.35
ELEVATION_M = 0.0
ALBEDO = 0.23
GSC = 0.0820
SIGMA = 4.903e-9


def calculate_month(row):
    year, month = int(row.Year), int(row.Month)
    days = calendar.monthrange(year, month)[1]
    doy = (pd.Timestamp(year, month, 1) + pd.Timedelta(days=days // 2)).dayofyear
    tmean = float(row.Tmean_C_Corrected)
    tmax_raw = float(row.Tmax_C_Raw)
    tmin_raw = float(row.Tmin_C_Raw)
    tmean_raw = float(row.Tmean_C_Raw)
    shift = tmean - tmean_raw
    tmax, tmin = tmax_raw + shift, tmin_raw + shift
    rh = float(row.RH_percent_Corrected)
    rs = float(row.Rs_MJ_m2_day_Corrected)
    u10 = float(row.Wind10m_ms_Corrected)
    u2 = u10 * 4.87 / math.log(67.8 * 10.0 - 5.42)
    pressure = 101.3 * ((293.0 - 0.0065 * ELEVATION_M) / 293.0) ** 5.26
    gamma = 0.000665 * pressure
    es = 0.6108 * math.exp(17.27 * tmean / (tmean + 237.3))
    ea = es * rh / 100.0
    delta = 4098.0 * es / (tmean + 237.3) ** 2
    phi = math.radians(LATITUDE_DEG)
    dr = 1.0 + 0.033 * math.cos(2.0 * math.pi * doy / 365.0)
    decl = 0.409 * math.sin(2.0 * math.pi * doy / 365.0 - 1.39)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(phi) * math.tan(decl))))
    ra = 24.0 * 60.0 / math.pi * GSC * dr * (
        ws * math.sin(phi) * math.sin(decl)
        + math.cos(phi) * math.cos(decl) * math.sin(ws)
    )
    rso = (0.75 + 2e-5 * ELEVATION_M) * ra
    rns = (1.0 - ALBEDO) * rs
    cloud_ratio = min(1.0, max(0.3, rs / rso)) if rso > 0 else 0.3
    # Match the historical ERA5-Land approach: monthly mean temperature
    # and monthly mean relative humidity in the FAO-56 radiation term.
    rnl = SIGMA * (tmean + 273.16) ** 4 * (
        0.34 - 0.14 * math.sqrt(max(ea, 0.0))
    ) * (1.35 * cloud_ratio - 0.35)
    rn = rns - rnl
    et0_day = (
        0.408 * delta * rn
        + gamma * (900.0 / (tmean + 273.0)) * u2 * (es - ea)
    ) / (delta + gamma * (1.0 + 0.34 * u2))
    if not np.isfinite(et0_day) or et0_day < 0:
        raise ValueError(f"Invalid ET0 for {year}-{month:02d}: {et0_day}")
    return {
        "Tmax_C_Corrected": tmax,
        "Tmin_C_Corrected": tmin,
        "Wind2m_ms": u2,
        "Pressure_kPa": pressure,
        "es_kPa": es,
        "ea_kPa": ea,
        "Delta_kPa_C": delta,
        "Gamma_kPa_C": gamma,
        "Ra_MJ_m2_day": ra,
        "Rso_MJ_m2_day": rso,
        "Rns_MJ_m2_day": rns,
        "Rnl_MJ_m2_day": rnl,
        "Rn_MJ_m2_day": rn,
        "ET0_mm_day": et0_day,
        "ET0_mm_month": et0_day * days,
        "Days_in_Month": days,
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined = []
    print("=" * 64)
    print("ACCESS-CM2 FUTURE MONTHLY FAO-56 ET0 | 2031-2070")
    print("=" * 64)
    for scenario in SCENARIOS:
        path = INPUT_DIR / f"ACCESS-CM2_{scenario}_Monthly_Corrected_2031_2070.xlsx"
        if not path.exists():
            # Older output scripts may have used a hyphen in the model name.
            path = INPUT_DIR / f"ACCESS-CM2_{scenario}_Monthly_Corrected_2031_2070.xlsx"
        if not path.exists():
            raise FileNotFoundError(path)
        frame = pd.read_excel(path, sheet_name="Monthly_2031_2070")
        required = ["Year", "Month", "Tmax_C_Raw", "Tmin_C_Raw",
                    "Tmean_C_Raw", "Tmean_C_Corrected", "RH_percent_Corrected",
                    "Rs_MJ_m2_day_Corrected", "Wind10m_ms_Corrected",
                    "Precipitation_mm_month_Corrected"]
        missing = [col for col in required if col not in frame.columns]
        if missing:
            raise ValueError(f"Missing columns in {path.name}: {missing}")
        if len(frame) != 480 or frame[required].isna().any().any():
            raise ValueError(f"Incomplete dataset: {path.name}")
        if frame.duplicated(["Year", "Month"]).any():
            raise ValueError(f"Duplicate year/month: {path.name}")
        frame = frame.sort_values(["Year", "Month"]).reset_index(drop=True)
        expected = [(y, m) for y in range(2031, 2071) for m in range(1, 13)]
        if list(zip(frame.Year, frame.Month)) != expected:
            raise ValueError(f"Missing or unexpected months: {path.name}")
        calculated = pd.DataFrame([calculate_month(row) for row in frame.itertuples(index=False)])
        result = pd.concat([frame, calculated], axis=1)
        if result[["ET0_mm_day", "ET0_mm_month"]].isna().any().any():
            raise ValueError(f"Missing ET0 values: {scenario}")
        out = OUTPUT_DIR / f"ACCESS-CM2_{scenario}_ET0_2031_2070.xlsx"
        with pd.ExcelWriter(out) as writer:
            result.to_excel(writer, sheet_name="Monthly_2031_2070", index=False)
            result[result.Year.between(2031, 2050)].to_excel(
                writer, sheet_name="Near_Term_2031_2050", index=False)
            result[result.Year.between(2051, 2070)].to_excel(
                writer, sheet_name="Mid_Century_2051_2070", index=False)
        combined.append(result)
        print(f"{scenario}: 480 months; mean annual ET0 = "
              f"{result.ET0_mm_month.sum() / 40:.1f} mm/year")
        print(f"Saved: {out}")
    csv = OUTPUT_DIR / "ACCESS-CM2_Future_ET0_2031_2070_Combined.csv"
    pd.concat(combined, ignore_index=True).to_csv(csv, index=False)
    print(f"Combined file: {csv}")
    print("Processing completed successfully.")


if __name__ == "__main__":
    main()
