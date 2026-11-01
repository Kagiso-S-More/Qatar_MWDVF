from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r'C:\Users\Kagiso\WaterNetwork\CMIP6')
ERA_FILE = ROOT / 'ERA5_Land' / 'ERA5_Land_Climate_1995_2025.xlsx'
FUTURE_DIR = ROOT / 'Future_Processed' / 'ET0'
OUTPUT_DIR = ROOT / 'Future_Processed' / 'CSI'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCENARIOS = ('ssp245', 'ssp585')
PERIODS = {'2031-2050': (2031, 2050), '2051-2070': (2051, 2070)}
WEIGHTS = {'ET0_n': 1 / 3, 'MPD': 1 / 3, 'SPD3': 1 / 3}


def load_months(path, sheet=0):
    if not path.exists():
        raise FileNotFoundError(f'Missing input file: {path}')
    df = pd.read_excel(path, sheet_name=sheet)
    needed = ['Year', 'Month', 'ET0_mm_month', 'Precipitation_mm_month']
    if 'Precipitation_mm_month' not in df and 'Precipitation_mm_month_Corrected' in df:
        df['Precipitation_mm_month'] = df['Precipitation_mm_month_Corrected']
    missing = [c for c in needed if c not in df]
    if missing:
        raise ValueError(f'{path.name}: missing columns {missing}; found {list(df.columns)}')
    df = df.copy()
    df['Year'] = pd.to_numeric(df['Year'], errors='raise').astype(int)
    df['Month'] = pd.to_numeric(df['Month'], errors='raise').astype(int)
    df = df.sort_values(['Year', 'Month']).reset_index(drop=True)
    if df.duplicated(['Year', 'Month']).any():
        raise ValueError(f'Duplicate months: {path.name}')
    if df[needed[2:]].isna().any().any() or not np.isfinite(df[needed[2:]].to_numpy(dtype=float)).all():
        raise ValueError(f'Missing or nonfinite climate values: {path.name}')
    if (df['Precipitation_mm_month'] < 0).any() or (df['ET0_mm_month'] < 0).any():
        raise ValueError(f'Negative precipitation or ET0: {path.name}')
    df['Date'] = pd.to_datetime(dict(year=df.Year, month=df.Month, day=1))
    return df


def check_timeline(df, start, end, name):
    expected = pd.date_range(f'{start}-01-01', f'{end}-12-01', freq='MS')
    if not pd.DatetimeIndex(df.Date).equals(expected):
        raise ValueError(f'{name}: incomplete or unexpected monthly timeline')


def empirical_dryness(value, reference):
    # Midrank empirical percentile, with reference extremes as anchors.
    reference = np.asarray(reference, dtype=float)
    n = len(reference)
    less = np.count_nonzero(reference < value)
    equal = np.count_nonzero(reference == value)
    percentile = (less + 0.5 * equal) / n
    return float(np.clip(1.0 - percentile, 0.0, 1.0))


def main():
    historical = load_months(ERA_FILE, 'ERA5_1995_2025')
    check_timeline(historical, 1995, 2025, 'ERA5-Land')
    baseline = historical.loc[historical.Year.between(1995, 2014)].copy()
    check_timeline(baseline, 1995, 2014, 'ERA5 baseline')

    # Three-month totals are calculated before filtering to the baseline.
    historical['P3_mm'] = historical.Precipitation_mm_month.rolling(3, min_periods=3).sum()
    baseline_p3 = historical.loc[historical.Year.between(1995, 2014)].copy()

    # Fixed 1995-2014 min/max reference, separately for each calendar month.
    reference = baseline.groupby('Month').agg(
        ET0_min=('ET0_mm_month', 'min'), ET0_max=('ET0_mm_month', 'max'),
        P_min=('Precipitation_mm_month', 'min'), P_max=('Precipitation_mm_month', 'max')
    ).reset_index()
    for col in ('ET0', 'P'):
        if ((reference[f'{col}_max'] - reference[f'{col}_min']) <= 0).any():
            raise ValueError(f'Zero historical reference range for {col}')
    p3_lookup = {m: baseline_p3.loc[baseline_p3.Month.eq(m), 'P3_mm'].dropna().to_numpy(dtype=float)
                 for m in range(1, 13)}
    if any(len(v) < 15 for v in p3_lookup.values()):
        raise ValueError('Insufficient historical P3 values for calendar-month percentiles')

    def calculate_indices(frame):
        frame = frame.copy()
        # Rolling precipitation uses the immediately preceding two months.
        frame['P3_mm'] = frame.Precipitation_mm_month.rolling(3, min_periods=3).sum()
        frame = frame.merge(reference, on='Month', how='left', validate='many_to_one')
        frame['ET0_n_unclipped'] = (frame.ET0_mm_month - frame.ET0_min) / (frame.ET0_max - frame.ET0_min)
        frame['MPD_unclipped'] = (frame.P_max - frame.Precipitation_mm_month) / (frame.P_max - frame.P_min)
        frame['ET0_n'] = frame.ET0_n_unclipped.clip(0, 1)
        frame['MPD'] = frame.MPD_unclipped.clip(0, 1)
        frame['SPD3'] = [empirical_dryness(p, p3_lookup[int(m)]) if pd.notna(p) else np.nan
                         for p, m in zip(frame.P3_mm, frame.Month)]
        frame['CSI'] = sum(frame[key] * weight for key, weight in WEIGHTS.items())
        return frame

    # Historical reference includes 1995 Jan/Feb with undefined rolling 3-month total.
    hist_out = calculate_indices(historical)
    hist_baseline = hist_out.loc[hist_out.Year.between(1995, 2014)].copy()
    hist_baseline.to_excel(OUTPUT_DIR / 'ERA5_CSI_Reference_1995_2014.xlsx', index=False)
    reference.to_excel(OUTPUT_DIR / 'ERA5_Monthly_Normalization_Reference.xlsx', index=False)

    all_scenarios = []
    summary = []
    for scenario in SCENARIOS:
        path = FUTURE_DIR / f'ACCESS-CM2_{scenario}_ET0_2031_2070.xlsx'
        future = load_months(path)
        check_timeline(future, 2031, 2070, scenario)
        # Need November and December 2030 for true Jan/Feb 2031 P3.
        # The downloaded projections begin in 2031; exclude first two months from CSI.
        result = calculate_indices(future)
        result['Scenario'] = scenario
        result['Period'] = np.where(result.Year <= 2050, '2031-2050', '2051-2070')
        if result.loc[result.Date.ge('2031-03-01'), ['ET0_n', 'MPD', 'SPD3', 'CSI']].isna().any().any():
            raise ValueError(f'Unexpected missing CSI after February 2031: {scenario}')
        result.to_excel(OUTPUT_DIR / f'ACCESS-CM2_{scenario}_CSI_2031_2070.xlsx', index=False)
        all_scenarios.append(result)
        for label, (start, end) in PERIODS.items():
            sub = result.loc[result.Year.between(start, end)]
            summary.append({
                'Scenario': scenario, 'Period': label,
                'CSI_months': int(sub.CSI.notna().sum()),
                'ET0_mm_year': sub.ET0_mm_month.sum() / 20,
                'Precipitation_mm_year': sub.Precipitation_mm_month.sum() / 20,
                'Mean_ET0_n': sub.ET0_n.mean(), 'Mean_MPD': sub.MPD.mean(),
                'Mean_SPD3': sub.SPD3.mean(), 'Mean_CSI': sub.CSI.mean(),
                'ET0_above_reference_max_pct': 100 * (sub.ET0_n_unclipped > 1).mean(),
                'Precip_below_reference_min_pct': 100 * (sub.MPD_unclipped > 1).mean(),
            })
        print(f'{scenario}: {len(result)} months; valid CSI = {result.CSI.notna().sum()}')

    summary_df = pd.DataFrame(summary)
    summary_df.to_excel(OUTPUT_DIR / 'ACCESS_CM2_Future_CSI_Summary.xlsx', index=False)
    pd.concat(all_scenarios, ignore_index=True).to_csv(
        OUTPUT_DIR / 'ACCESS_CM2_Future_CSI_All_Scenarios.csv', index=False)
    print('\nPROJECTED HYDROCLIMATIC STRESS SUMMARY')
    print(summary_df.round(3).to_string(index=False))
    print('\nHistorical baseline CSI mean:', round(hist_baseline.CSI.mean(), 3))
    print('Note: January-February 2031 CSI undefined: 2030 precipitation unavailable.')
    print('Historical January-February 1995 CSI undefined: 1994 precipitation unavailable.')
    print('Output folder:', OUTPUT_DIR)


if __name__ == '__main__':
    main()
