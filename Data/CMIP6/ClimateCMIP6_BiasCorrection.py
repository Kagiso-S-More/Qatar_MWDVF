from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(r"C:\Users\Kagiso\WaterNetwork\CMIP6")

ERA5_FILE = (
    BASE_DIR / "ERA5_Land" /
    "ERA5_Land_Climate_1995_2025.xlsx"
)

CMIP6_FILE = (
    BASE_DIR /
    "ACCESS_CM2_Historical_Climate_1995_2014.xlsx"
)

OUTPUT_DIR = BASE_DIR / "Bias_Correction"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "ACCESS_CM2_Historical_Bias_Correction.xlsx"
)

BASELINE_START = 1995
BASELINE_END = 2014

PRECIP_MINIMUM = 0.1
PRECIP_MAX_FACTOR = 10.0

VARIABLES = {
    "Precipitation_mm_month": "multiplicative",
    "Tmean_C": "additive",
    "RH_percent": "additive",
    "Rs_MJ_m2_day": "multiplicative",
    "Wind10m_ms": "multiplicative"
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "figure.dpi": 150,
    "savefig.dpi": 300
})


def saturation_vapour_pressure(temperature):

    return 0.6108 * np.exp(
        17.27 * temperature /
        (temperature + 237.3)
    )


def load_data():

    print("Reading ERA5-Land dataset...")

    era = pd.read_excel(ERA5_FILE)

    print("Reading ACCESS-CM2 dataset...")

    cmip = pd.read_excel(CMIP6_FILE)

    required_era = [
        "Year", "Month", "Tmean_C", "Tdew_C",
        "Precipitation_mm_month",
        "Rs_MJ_m2_day", "Wind10m_ms"
    ]

    required_cmip = [
        "Year", "Month", "Tmean_C",
        "RH_percent", "Precipitation_mm_month",
        "Rs_MJ_m2_day", "Wind_ms"
    ]

    for column in required_era:
        if column not in era.columns:
            raise ValueError(
                f"Missing ERA5-Land column: {column}"
            )

    for column in required_cmip:
        if column not in cmip.columns:
            raise ValueError(
                f"Missing ACCESS-CM2 column: {column}"
            )

    era = era.loc[
        era["Year"].between(
            BASELINE_START, BASELINE_END
        )
    ].copy()

    cmip = cmip.loc[
        cmip["Year"].between(
            BASELINE_START, BASELINE_END
        )
    ].copy()

    era["RH_percent"] = (
        100 *
        saturation_vapour_pressure(
            era["Tdew_C"]
        ) /
        saturation_vapour_pressure(
            era["Tmean_C"]
        )
    ).clip(0, 100)

    cmip = cmip.rename(
        columns={"Wind_ms": "Wind10m_ms"}
    )

    columns = [
        "Year", "Month",
        "Precipitation_mm_month",
        "Tmean_C", "RH_percent",
        "Rs_MJ_m2_day", "Wind10m_ms"
    ]

    era = era[columns]
    cmip = cmip[columns]

    if era.duplicated(["Year", "Month"]).any():
        raise ValueError(
            "Duplicate ERA5-Land months detected."
        )

    if cmip.duplicated(["Year", "Month"]).any():
        raise ValueError(
            "Duplicate ACCESS-CM2 months detected."
        )

    merged = era.merge(
        cmip,
        on=["Year", "Month"],
        suffixes=("_ERA5", "_CMIP6"),
        validate="one_to_one"
    )

    merged = merged.sort_values(
        ["Year", "Month"]
    ).reset_index(drop=True)

    if len(merged) != 240:
        raise ValueError(
            f"Expected 240 months, found {len(merged)}."
        )

    if merged.isna().any().any():
        raise ValueError(
            "Missing values detected in baseline data."
        )

    merged["Date"] = pd.to_datetime(
        dict(
            year=merged["Year"],
            month=merged["Month"],
            day=1
        )
    )

    return merged


def evaluation_statistics(reference, simulation):

    reference = np.asarray(reference, dtype=float)
    simulation = np.asarray(simulation, dtype=float)

    difference = simulation - reference

    bias = np.mean(difference)
    mae = np.mean(np.abs(difference))
    rmse = np.sqrt(np.mean(difference ** 2))

    if (
        np.std(reference) > 0
        and np.std(simulation) > 0
    ):
        correlation = np.corrcoef(
            reference, simulation
        )[0, 1]
    else:
        correlation = np.nan

    return {
        "Bias": bias,
        "MAE": mae,
        "RMSE": rmse,
        "Correlation": correlation
    }



def calculate_parameters(data):

    records = []

    for variable, method in VARIABLES.items():

        for month in range(1, 13):

            subset = data.loc[
                data["Month"] == month
            ]

            observed = subset[
                f"{variable}_ERA5"
            ].mean()

            simulated = subset[
                f"{variable}_CMIP6"
            ].mean()

            if variable == "Precipitation_mm_month":

                adjustment = (
                    (observed + PRECIP_MINIMUM) /
                    (simulated + PRECIP_MINIMUM)
                )

                adjustment = min(
                    adjustment,
                    PRECIP_MAX_FACTOR
                )

            elif method == "additive":

                adjustment = observed - simulated

            else:

                if simulated <= 0:
                    raise ValueError(
                        f"Invalid denominator: "
                        f"{variable}, month {month}"
                    )

                adjustment = observed / simulated

            records.append({
                "Variable": variable,
                "Month": month,
                "Method": method,
                "ERA5_Mean": observed,
                "CMIP6_Mean": simulated,
                "Correction": adjustment
            })

    return pd.DataFrame(records)



def correct_historical(data, parameters):

    corrected = data.copy()

    for variable, method in VARIABLES.items():

        corrections = parameters.loc[
            parameters["Variable"] == variable,
            ["Month", "Correction"]
        ].set_index("Month")["Correction"]

        factors = corrected["Month"].map(
            corrections
        ).to_numpy(dtype=float)

        raw = corrected[
            f"{variable}_CMIP6"
        ].to_numpy(dtype=float)

        if method == "additive":

            values = raw + factors

        else:

            values = raw * factors

        if variable == "Precipitation_mm_month":

            values = np.maximum(values, 0)

            if np.isnan(values).any():
                raise ValueError(
                    "Precipitation correction undefined "
                    "for one or more months. "
                    "Inspect precipitation parameters."
                )

        elif variable == "RH_percent":

            values = np.clip(values, 0, 100)

        elif variable in [
            "Rs_MJ_m2_day", "Wind10m_ms"
        ]:

            values = np.maximum(values, 0)

        corrected[
            f"{variable}_Corrected"
        ] = values

    return corrected


def create_evaluation(data):

    records = []

    for variable in VARIABLES:

        reference = data[
            f"{variable}_ERA5"
        ].to_numpy()

        for label, column in [
            ("Raw", f"{variable}_CMIP6"),
            ("Corrected", f"{variable}_Corrected")
        ]:

            statistics = evaluation_statistics(
                reference,
                data[column].to_numpy()
            )

            records.append({
                "Variable": variable,
                "Dataset": label,
                **statistics
            })

    return pd.DataFrame(records)


def monthly_climatology(data):

    records = []

    for variable in VARIABLES:

        for month in range(1, 13):

            subset = data.loc[
                data["Month"] == month
            ]

            records.append({
                "Variable": variable,
                "Month": month,
                "ERA5": subset[
                    f"{variable}_ERA5"
                ].mean(),
                "Raw_CMIP6": subset[
                    f"{variable}_CMIP6"
                ].mean(),
                "Corrected_CMIP6": subset[
                    f"{variable}_Corrected"
                ].mean()
            })

    return pd.DataFrame(records)


def plot_climatology(climatology):

    labels = {
        "Precipitation_mm_month":
            "Precipitation (mm/month)",
        "Tmean_C":
            "Mean temperature (°C)",
        "RH_percent":
            "Relative humidity (%)",
        "Rs_MJ_m2_day":
            "Solar radiation (MJ/m²/day)",
        "Wind10m_ms":
            "Wind speed (m/s)"
    }

    fig, axes = plt.subplots(
        3, 2,
        figsize=(12, 12)
    )

    axes = axes.flatten()

    for index, variable in enumerate(VARIABLES):

        ax = axes[index]

        subset = climatology.loc[
            climatology["Variable"] == variable
        ]

        ax.plot(
            subset["Month"],
            subset["ERA5"],
            marker="o",
            linewidth=2,
            label="ERA5-Land"
        )

        ax.plot(
            subset["Month"],
            subset["Raw_CMIP6"],
            marker="s",
            linewidth=1.7,
            linestyle="--",
            label="ACCESS-CM2"
        )

        ax.plot(
            subset["Month"],
            subset["Corrected_CMIP6"],
            marker="^",
            linewidth=1.7,
            linestyle=":",
            label="Bias-corrected"
        )

        ax.set_xlabel("Month")
        ax.set_ylabel(labels[variable])
        ax.set_xticks(range(1, 13))
        ax.grid(alpha=0.25)

        ax.text(
            0.02, 0.96,
            f"({chr(97 + index)})",
            transform=ax.transAxes,
            va="top",
            fontweight="bold"
        )

    axes[-1].axis("off")

    handles, legend_labels = (
        axes[0].get_legend_handles_labels()
    )

    fig.legend(
        handles,
        legend_labels,
        loc="lower center",
        ncol=3,
        frameon=False
    )

    fig.suptitle(
        "Historical climate climatology (1995–2014)",
        fontsize=14
    )

    fig.tight_layout(
        rect=[0, 0.05, 1, 0.96]
    )

    fig.savefig(
        OUTPUT_DIR / "Fig1_Monthly_Climatology.png",
        bbox_inches="tight"
    )

    plt.close(fig)


def plot_precipitation(data):

    annual = data.groupby("Year").agg({
        "Precipitation_mm_month_ERA5": "sum",
        "Precipitation_mm_month_CMIP6": "sum",
        "Precipitation_mm_month_Corrected": "sum"
    })

    fig, ax = plt.subplots(
        figsize=(11, 5)
    )

    ax.plot(
        annual.index,
        annual["Precipitation_mm_month_ERA5"],
        marker="o",
        label="ERA5-Land"
    )

    ax.plot(
        annual.index,
        annual["Precipitation_mm_month_CMIP6"],
        marker="s",
        linestyle="--",
        label="ACCESS-CM2"
    )

    ax.plot(
        annual.index,
        annual[
            "Precipitation_mm_month_Corrected"
        ],
        marker="^",
        linestyle=":",
        label="Bias-corrected"
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Annual precipitation (mm)")
    ax.set_title(
        "Historical annual precipitation (1995–2014)"
    )

    ax.grid(alpha=0.25)
    ax.legend(frameon=False)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "Fig2_Annual_Precipitation.png",
        bbox_inches="tight"
    )

    plt.close(fig)


def plot_temperature(data):

    annual = data.groupby("Year").agg({
        "Tmean_C_ERA5": "mean",
        "Tmean_C_CMIP6": "mean",
        "Tmean_C_Corrected": "mean"
    })

    fig, ax = plt.subplots(
        figsize=(11, 5)
    )

    ax.plot(
        annual.index,
        annual["Tmean_C_ERA5"],
        marker="o",
        label="ERA5-Land"
    )

    ax.plot(
        annual.index,
        annual["Tmean_C_CMIP6"],
        marker="s",
        linestyle="--",
        label="ACCESS-CM2"
    )

    ax.plot(
        annual.index,
        annual["Tmean_C_Corrected"],
        marker="^",
        linestyle=":",
        label="Bias-corrected"
    )

    ax.set_xlabel("Year")
    ax.set_ylabel("Mean air temperature (°C)")
    ax.set_title(
        "Historical annual mean temperature (1995–2014)"
    )

    ax.grid(alpha=0.25)
    ax.legend(frameon=False)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "Fig3_Annual_Temperature.png",
        bbox_inches="tight"
    )

    plt.close(fig)


def plot_model_bias(evaluation):

    raw = evaluation.loc[
        evaluation["Dataset"] == "Raw"
    ].set_index("Variable")

    corrected = evaluation.loc[
        evaluation["Dataset"] == "Corrected"
    ].set_index("Variable")

    variables = list(VARIABLES)

    raw_bias = raw.loc[
        variables, "Bias"
    ].to_numpy()

    corrected_bias = corrected.loc[
        variables, "Bias"
    ].to_numpy()

    labels = [
        "Precipitation",
        "Temperature",
        "Humidity",
        "Solar radiation",
        "Wind speed"
    ]

    x = np.arange(len(labels))

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    ax.bar(
        x - 0.2,
        raw_bias,
        width=0.4,
        label="Raw"
    )

    ax.bar(
        x + 0.2,
        corrected_bias,
        width=0.4,
        label="Corrected"
    )

    ax.axhline(
        0,
        color="black",
        linewidth=0.8
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(
        "Mean bias (variable-specific units)"
    )

    ax.set_title(
        "Historical mean bias before and after correction"
    )

    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / "Fig4_Model_Bias.png",
        bbox_inches="tight"
    )

    plt.close(fig)


def main():

    print("=" * 65)
    print("ACCESS-CM2 HISTORICAL EVALUATION")
    print("AND BIAS CORRECTION")
    print("=" * 65)

    data = load_data()

    print("\nCalculating monthly correction parameters...")

    parameters = calculate_parameters(data)

    print("Applying corrections...")

    corrected = correct_historical(
        data, parameters
    )

    print("Evaluating model performance...")

    evaluation = create_evaluation(corrected)

    climatology = monthly_climatology(corrected)

    print("Exporting Excel workbook...")

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:

        corrected.to_excel(
            writer,
            sheet_name="Historical_Comparison",
            index=False
        )

        parameters.to_excel(
            writer,
            sheet_name="Correction_Parameters",
            index=False
        )

        evaluation.to_excel(
            writer,
            sheet_name="Model_Evaluation",
            index=False
        )

        climatology.to_excel(
            writer,
            sheet_name="Monthly_Climatology",
            index=False
        )

    print("Generating figures...")

    plot_climatology(climatology)
    plot_precipitation(corrected)
    plot_temperature(corrected)
    plot_model_bias(evaluation)

    print("\n" + "=" * 65)
    print("PROCESSING SUMMARY")
    print("=" * 65)

    print(
        "Baseline:",
        BASELINE_START,
        "-",
        BASELINE_END
    )

    print("Total months:", len(corrected))

    print("\nMODEL EVALUATION:")
    print(
        evaluation.round(3).to_string(
            index=False
        )
    )

    print("\nOutput workbook:", OUTPUT_FILE)
    print("Output figures:", OUTPUT_DIR)

    print(
        "\nHistorical evaluation and "
        "bias correction completed successfully."
    )


if __name__ == "__main__":
    main()
