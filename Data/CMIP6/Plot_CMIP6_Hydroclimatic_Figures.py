from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MaxNLocator

BASE_DIR = Path(r"C:\Users\Kagiso\WaterNetwork\CMIP6")
INPUT_FILE = BASE_DIR / "Future_Processed" / "CSI" / "ACCESS_CM2_Future_CSI_All_Scenarios.csv"
OUTPUT_DIR = BASE_DIR / "Future_Processed" / "Figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

print("Available columns:")
print(df.columns.tolist())

def find_column(data, candidates):
    for name in candidates:
        if name in data.columns:
            return name
    raise KeyError(f"Column not found. Expected one of: {candidates}")

scenario_col = find_column(df, ["Scenario", "scenario"])
year_col = find_column(df, ["Year", "year"])
precip_col = find_column(
    df,
    ["Precipitation_mm_month_BC", "Precipitation_mm_month_corrected",
     "Precipitation_mm_month_Corrected", "Precipitation_mm_month"]
)
et0_col = find_column(
    df,
    ["ET0_mm_month", "ET0_mm_month_BC", "ET0_monthly_mm"]
)
et0n_col = find_column(
    df,
    ["ET0_n", "ET0_normalized", "ET0_norm", "ET0_n_clipped"]
)
mpd_col = find_column(df, ["MPD", "MPD_clipped"])
spd_col = find_column(df, ["SPD3", "SPD_3", "SPD3_clipped"])
csi_col = find_column(df, ["CSI", "CSI_future"])

df[year_col] = pd.to_numeric(df[year_col], errors="coerce")

for col in [precip_col, et0_col, et0n_col, mpd_col, spd_col, csi_col]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

def standardize_scenario(value):
    s = str(value).lower().replace("-", "").replace("_", "").replace(".", "")
    if "245" in s:
        return "SSP2-4.5"
    if "585" in s:
        return "SSP5-8.5"
    return str(value)

df["Scenario_Label"] = df[scenario_col].apply(standardize_scenario)

scenarios = ["SSP2-4.5", "SSP5-8.5"]
colors = {
    "SSP2-4.5": "#2166AC",
    "SSP5-8.5": "#B2182B"
}

df = df[
    df["Scenario_Label"].isin(scenarios)
    & df[year_col].between(2031, 2070)
].copy()

annual = (
    df.groupby(["Scenario_Label", year_col], as_index=False)
    .agg(
        ET0=(et0_col, "sum"),
        Precipitation=(precip_col, "sum"),
        CSI=(csi_col, "mean")
    )
)

df["Period"] = np.where(
    df[year_col] <= 2050,
    "2031–2050",
    "2051–2070"
)

components = (
    df.groupby(["Scenario_Label", "Period"], as_index=False)
    .agg(
        ET0_n=(et0n_col, "mean"),
        MPD=(mpd_col, "mean"),
        SPD3=(spd_col, "mean"),
        CSI=(csi_col, "mean")
    )
)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 13,
    "axes.labelsize": 13,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "axes.linewidth": 1.0,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.size": 5,
    "ytick.major.size": 5,
    "xtick.minor.size": 3,
    "ytick.minor.size": 3,
    "savefig.dpi": 600,
    "pdf.fonttype": 42,
    "ps.fonttype": 42
})

fig, axes = plt.subplots(
    2, 2,
    figsize=(13.5, 9.5),
    constrained_layout=True
)

ax_a, ax_b = axes[0]
ax_c, ax_d = axes[1]

def style_axis(ax, minor_x=True, minor_y=True):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)

    ax.tick_params(
        axis="both",
        which="both",
        direction="in",
        top=True,
        right=True
    )

    if minor_x:
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    if minor_y:
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    ax.grid(False)

def plot_annual(ax, variable, ylabel, panel):
    for scenario in scenarios:
        subset = annual[
            annual["Scenario_Label"] == scenario
        ].sort_values(year_col)

        ax.plot(
            subset[year_col],
            subset[variable],
            color=colors[scenario],
            linewidth=1.65,
            marker="o",
            markersize=2.5,
            label=scenario
        )

    ax.axvline(
        2050.5,
        color="0.45",
        linestyle="--",
        linewidth=0.9
    )

    ax.set_xlim(2030, 2071)
    ax.set_xticks(np.arange(2035, 2071, 5))
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)

    ax.text(
        0.025, 0.965, f"({panel})",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=12,
        fontweight="bold"
    )

    style_axis(ax)
    ax.legend(
        loc="best",
        frameon=False,
        fontsize=9
    )

plot_annual(
    ax_a,
    "ET0",
    r"Annual ET$_0$ (mm year$^{-1}$)",
    "a"
)

plot_annual(
    ax_b,
    "Precipitation",
    r"Annual precipitation (mm year$^{-1}$)",
    "b"
)

plot_annual(
    ax_c,
    "CSI",
    "Annual mean CSI",
    "c"
)

ax_c.set_ylim(0, 1)

component_names = [
    r"ET$_{0,n}$",
    "MPD",
    r"SPD$_3$",
    "CSI"
]

component_cols = ["ET0_n", "MPD", "SPD3", "CSI"]

groups = [
    ("SSP2-4.5", "2031–2050"),
    ("SSP2-4.5", "2051–2070"),
    ("SSP5-8.5", "2031–2050"),
    ("SSP5-8.5", "2051–2070")
]

x = np.arange(len(component_cols))
width = 0.19

bar_styles = [
    (colors["SSP2-4.5"], "", 1.0),
    (colors["SSP2-4.5"], "//", 0.65),
    (colors["SSP5-8.5"], "", 1.0),
    (colors["SSP5-8.5"], "//", 0.65)
]

for i, (scenario, period) in enumerate(groups):
    subset = components[
        (components["Scenario_Label"] == scenario)
        & (components["Period"] == period)
    ]

    if subset.empty:
        raise ValueError(f"Missing data: {scenario}, {period}")

    values = subset.iloc[0][component_cols].to_numpy(dtype=float)

    color, hatch, alpha = bar_styles[i]
    offset = (i - 1.5) * width

    ax_d.bar(
        x + offset,
        values,
        width=width,
        color=color,
        alpha=alpha,
        hatch=hatch,
        edgecolor=color,
        linewidth=0.8,
        label=f"{scenario} ({period})"
    )

ax_d.set_xticks(x)
ax_d.set_xticklabels(component_names)
ax_d.set_ylabel("Mean normalized index")
ax_d.set_ylim(0, 1)
ax_d.set_xlim(-0.55, len(x) - 0.45)

ax_d.text(
    0.025, 0.965, "(d)",
    transform=ax_d.transAxes,
    ha="left",
    va="top",
    fontsize=12,
    fontweight="bold"
)

style_axis(ax_d, minor_x=False)
ax_d.legend(
    loc="upper right",
    fontsize=8,
    frameon=False,
    ncol=2,
    columnspacing=0.8,
    handlelength=1.4
)

fig.savefig(
    OUTPUT_DIR / "Figure_CMIP6_Hydroclimatic_2x2.png",
    dpi=400,
    bbox_inches="tight",
    facecolor="white"
)

fig.savefig(
    OUTPUT_DIR / "Figure_CMIP6_Hydroclimatic_2x2.tiff",
    dpi=400,
    bbox_inches="tight",
    facecolor="white"
)

fig.savefig(
    OUTPUT_DIR / "Figure_CMIP6_Hydroclimatic_2x2.pdf",
    bbox_inches="tight",
    facecolor="white"
)

plt.show()

print("\nFigure successfully generated.")
print(f"Output directory: {OUTPUT_DIR}")
print("\nMean hydroclimatic components:")
print(components.round(3).to_string(index=False))
