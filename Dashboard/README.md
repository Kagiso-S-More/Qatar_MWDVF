# Qatar | Water Vulnerability Intelligence

**An interactive, GIS-enabled dashboard for integrated water vulnerability assessment in Qatar.**

This Streamlit application brings together spatial vulnerability indicators, groundwater hydrochemistry, hydraulic performance calculations, historical hydroclimatic conditions, and climate projections in a single multipanel decision-support interface. Visualisations are generated from the datasets included in this directory.

## Dashboard capabilities

The interface presents six coordinated analytical panels:

| Panel | Analytical component | Output |
|---|---|---|
| 01 | Municipal vulnerability atlas | Interactive Qatar municipality map showing SVI, HRI, HVI or CSI, with optional groundwater sampling locations |
| 02 | Municipality performance ranking | Comparative municipal index values and observation coverage |
| 03 | Hydrochemical risk profile | Distributions of HRI, SAR, KR, SHI, MSP and TDS |
| 04 | Hydraulic performance assessment | Comparative head loss, HVI, SVI and classification changes across pipeline configurations and parameter settings |
| 05 | Hydroclimatic conditions (2009–2025) | Historical monthly CSI, ET₀, precipitation, MPD and SPD₃ |
| 06 | Climate outlook (2031–2070) | Bias-corrected ACCESS-CM2 meteorological projections under SSP2-4.5 and SSP5-8.5 |

Sidebar controls allow selection of municipalities, spatial and hydrochemical indicators, hydraulic metrics, pipeline configurations, historical climate indicators, and future meteorological variables. Expandable sections provide municipal indicator tables, pipeline configuration details, and data provenance.

## Repository structure

```text
Dashboard/
├── app.py
├── README.md
├── requirements.txt
└── data/
    ├── GIS_Indicators.xlsx
    ├── Hydrochemistry_Indicators.xlsx
    ├── Hydraulic_Indicators.xlsx
    ├── Hydraulic_Pipeline_Scenarios.xlsx
    ├── Hydroclimatic_Indicators.xlsx
    ├── ACCESS-CM2_ssp245_Monthly_Corrected_2031_2070.xlsx
    ├── ACCESS-CM2_ssp585_Monthly_Corrected_2031_2070.xlsx
    └── Qatar Boundary/
        ├── gadm41_QAT_0.*
        └── gadm41_QAT_1.*
```

The shapefile's `.shp`, `.shx`, `.dbf`, `.prj` and associated `.cpg` files must remain together. The application reads the municipality-level `gadm41_QAT_1.shp` layer.

## Installation and launch

**Requirements:** Python 3.12 or newer is recommended; package compatibility depends on the installed environment. Anaconda Prompt, Command Prompt, or another Python terminal can be used.

Clone the repository and enter the dashboard directory:

```bash
git clone https://github.com/Kagiso-S-More/Qatar_MWDVF.git
cd Qatar_MWDVF/Dashboard
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch the application:

```bash
python -m streamlit run app.py
```

Open **http://localhost:8501** if the browser does not open automatically. Keep the terminal running while using the dashboard; press `Ctrl+C` to stop it. Run with Streamlit rather than `python app.py` or Spyder's `%runfile`.

## Data and analytical interpretation

- **Groundwater and hydrochemistry:** The baseline comprises 201 groundwater observations from 2020 and their derived hydrochemical and integrated vulnerability indicators. These observations are distinct from measurements of treated water within distribution pipes.
- **Municipal aggregation:** Sampling locations are spatially assigned to the supplied GADM 4.1 municipality boundaries. Municipality means and counts are calculated from that spatial assignment. The supplied boundary layer contains seven municipality polygons; Al Shahaniya is not separately represented.
- **Hydraulic performance:** Head loss and associated indices are computed using the supplied pipeline configurations and engineering parameters. They are model outputs, not telemetry from an operating water distribution network. Index values can exceed the original baseline normalisation bounds when configurations are changed.
- **Historical climate:** The historical panel presents monthly hydroclimatic indicators from the provided ERA5-Land-derived dataset.
- **Climate outlook:** The future panel presents bias-corrected ACCESS-CM2 meteorological variables for 2031–2070. Monthly precipitation is summed to annual totals; other displayed variables are aggregated to annual means. Future ET₀ and CSI are not calculated within the dashboard.
- **Data updates:** The application reads the packaged source files. It is not connected to live utility telemetry or control systems.

Municipal comparisons should be interpreted alongside sampling coverage. The dashboard is intended for integrated screening, comparative assessment and research-informed prioritisation, not as a substitute for operational network verification.

## Reproducibility

The source workbooks, geospatial boundaries and application code are provided together so that the displayed results can be reproduced. The dashboard calculates municipal membership from the packaged shapefile rather than importing municipality rankings from the manuscript.

For repository-wide modelling methods, datasets and scripts, see the [Qatar MWDVF repository](https://github.com/Kagiso-S-More/Qatar_MWDVF).

## Citation

When referring to the dashboard, cite the accompanying research manuscript and the repository's citation information where available. No software DOI is claimed here.
