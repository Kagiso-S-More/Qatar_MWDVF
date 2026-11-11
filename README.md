# Qatar Water Distribution Vulnerability Framework (WDVF)

**An Integrated GIS–AI Framework for Water Distribution Vulnerability Assessment Using Hydrochemical, Hydroclimatic and Hydraulic Indicators in Qatar**

## 1. Overview

This repository contains the research datasets, Python scripts, modelling outputs, climate projections, geospatial resources and interactive visualisation tools developed for the study:

**Integrated GIS–AI Assessment of Water Distribution Vulnerability Using Hydrochemical, Hydroclimatic and Hydraulic Indicators in Qatar**

The Water Distribution Vulnerability Framework (WDVF) integrates groundwater hydrochemistry, hydroclimatic stress, hydraulic susceptibility, geographic information systems (GIS) and artificial intelligence (AI) to assess spatial differences in water distribution vulnerability across Qatar.

The framework combines environmental indicators, hydraulic performance calculations, spatial vulnerability analysis and machine-learning classification to support water infrastructure assessment, risk identification and management prioritisation.

An interactive **Qatar Water Vulnerability Intelligence Dashboard** extends the analytical framework by presenting the principal research outputs through an integrated, GIS-enabled decision-support interface.

The repository supports scientific transparency, computational reproducibility, methodological verification and future applications in water-resource management, infrastructure planning and climate resilience.

**Repository:** https://github.com/Kagiso-S-More/Qatar_MWDVF

**Researcher:** Kagiso S. More

---

## 2. Research Objectives

The principal objectives of the WDVF are to:

1. Evaluate groundwater hydrochemical characteristics and derive indicators of hydrochemical vulnerability.
2. Quantify historical hydroclimatic stress using ERA5-Land climate data.
3. Assess future hydroclimatic conditions using CMIP6 climate projections under SSP2-4.5 and SSP5-8.5.
4. Evaluate hydraulic susceptibility using pipeline configurations, engineering parameters and hydrochemically informed risk indicators.
5. Integrate hydrochemical, hydroclimatic and hydraulic indicators through GIS-based spatial vulnerability analysis.
6. Apply machine-learning algorithms to classify integrated vulnerability and identify influential predictors.
7. Develop an interactive geospatial dashboard for visualising vulnerability patterns, comparing analytical indicators and supporting water infrastructure management.
8. Establish a transferable assessment framework applicable to Qatar and other water-stressed regions.

---

## 3. Study Area and Research Datasets

### 3.1 Study Area

The study focuses on Qatar, a hyper-arid country characterised by limited natural freshwater availability, high atmospheric evaporative demand and substantial reliance on engineered water infrastructure.

The WDVF evaluates the combined influence of hydrochemical conditions, climatic stress and hydraulic susceptibility on water distribution vulnerability.

Spatial analysis incorporates groundwater sampling locations and administrative boundaries to evaluate geographic variations in the integrated vulnerability indicators.

### 3.2 Groundwater and Hydrochemical Data

The hydrochemical assessment uses **201 groundwater observations collected in 2020**.

The analysis incorporates major-ion chemistry, hydrochemical indices, geochemical modelling outputs and spatially referenced groundwater characteristics.

Principal datasets include:

- `Geochemistry_Dataset.xlsx`
- `Hydrochemistry_Indicators.xlsx`
- `PHREEQC_Results.xlsx`
- `GIS_Indicators.xlsx`

Geochemical calculations and mineral saturation indices are supported by PHREEQC modelling.

The groundwater observations provide the hydrochemical baseline for the assessment and are distinct from measurements of treated water within operating distribution pipelines.

### 3.3 Historical Climate Data

Historical hydroclimatic conditions are evaluated using ERA5-Land climate data covering the broader 1995–2025 reference and analysis period.

The period 1995–2014 provides the historical reference for climate-model bias correction, while the dashboard presents monthly hydroclimatic indicators for 2009–2025.

Relevant datasets include:

- `ERA5-Land_Climate_Data.xlsx`
- `ETo_from_ERA5-Land.xlsx`
- `FAO56_ET0_Inputs_2009_2025_with_Rn.xlsx`
- `Hydroclimatic_Indicators.xlsx`

These datasets support the calculation and interpretation of reference evapotranspiration, precipitation-deficit indicators and composite hydroclimatic stress.

### 3.4 Future Climate Projections

Future hydroclimatic conditions are assessed using the NASA NEX-GDDP-CMIP6 dataset.

The climate-projection configuration is summarised below.

| Parameter | Description |
|---|---|
| Climate model | ACCESS-CM2 |
| Ensemble member | r1i1p1f1 |
| Historical reference period | 1995–2014 |
| Future projection period | 2031–2070 |
| Near-term period | 2031–2050 |
| Mid-century period | 2051–2070 |
| Intermediate-emissions pathway | SSP2-4.5 |
| High-emissions pathway | SSP5-8.5 |

Seven climate variables are incorporated:

| Variable | Description |
|---|---|
| `pr` | Precipitation |
| `tasmax` | Maximum near-surface air temperature |
| `tasmin` | Minimum near-surface air temperature |
| `hurs` | Near-surface relative humidity |
| `rsds` | Surface downwelling shortwave radiation |
| `rlds` | Surface downwelling longwave radiation |
| `sfcWind` | Near-surface wind speed |

Historical ACCESS-CM2 simulations are evaluated against ERA5-Land reference data, and bias-correction procedures are applied to future climate projections.

The future assessment uses a single global climate model rather than a multi-model CMIP6 ensemble.

---

## 4. Water Distribution Vulnerability Framework

The WDVF consists of interconnected hydrochemical, hydroclimatic, hydraulic, geospatial and machine-learning components.

### 4.1 Hydrochemical Vulnerability Assessment

Groundwater hydrochemical conditions are evaluated using derived indicators and PHREEQC geochemical modelling.

The principal hydrochemical indicators include:

- Sodium Adsorption Ratio (SAR)
- Kelly's Ratio (KR)
- Sodium Hazard Index (SHI)
- Mineral Saturation Potential (MSP)
- Total Dissolved Solids (TDS)

These indicators contribute to the composite **Hydrochemical Risk Index (HRI)**.

The HRI provides a normalised measure of relative hydrochemical susceptibility for integration with the other framework components.

### 4.2 Hydroclimatic Stress Assessment

Hydroclimatic assessment integrates historical meteorological conditions and future climate projections.

The principal analytical components include:

- Reference evapotranspiration (ET₀)
- Monthly Precipitation Deficit (MPD)
- Three-month Standardised Precipitation-Deficit Indicator (SPD₃)
- Composite Climate Stress Index (CSI)

The climate-processing workflow includes historical meteorological-data preparation, climate-model evaluation, bias correction, future climate processing, evapotranspiration calculations and hydroclimatic indicator development.

The resulting indicators support the assessment of atmospheric water demand, precipitation variability and hydroclimatic stress.

### 4.3 Hydraulic Vulnerability Assessment

Hydraulic vulnerability is evaluated using engineering parameters, established hydraulic relationships and hydrochemically informed indicators.

The framework incorporates:

- Hazen–Williams head-loss estimation
- Pipeline friction and hydraulic susceptibility
- Hydrochemically informed scaling and roughness assessment
- Pipeline Roughness and Scaling Index (PRSI)
- Hydraulic Vulnerability Index (HVI)
- Comparative evaluation of pipeline configurations and parameter sensitivity

The hydraulic calculations use specified pipeline characteristics, including length, diameter, flow and roughness-related coefficients.

Relevant datasets include:

- `Hydraulic_Indicators.xlsx`
- `Hydraulic_Pipeline_Scenarios.xlsx`

The hydraulic component provides calculated susceptibility indicators for comparative assessment. It is not derived from a calibrated operational distribution-network model.

### 4.4 GIS-Based Spatial Vulnerability Assessment

Spatial analysis integrates hydrochemical, hydroclimatic and hydraulic indicators to evaluate geographic differences in vulnerability.

The workflow incorporates:

- Spatial interpolation
- Administrative-area aggregation
- Spatial hotspot analysis
- Integrated vulnerability mapping
- Spatial Vulnerability Index (SVI)

The resulting spatial outputs support identification of areas exhibiting relatively elevated environmental and hydraulic susceptibility.

Administrative boundaries are used to summarise and compare spatial vulnerability patterns.

### 4.5 Machine-Learning Vulnerability Classification

Machine-learning methods are used to classify integrated vulnerability and evaluate the contribution of hydrochemical, hydroclimatic and hydraulic predictors.

The modelling framework includes:

- Random Forest (RF)
- Gradient Boosting (GB)
- Extreme Gradient Boosting (XGBoost)

The repository contains separate primary and secondary modelling workflows.

Model evaluation incorporates classification-performance metrics, confusion matrices and feature-importance analysis.

The resulting classifications represent the framework's constructed vulnerability categories rather than independently observed pipeline failures.

### 4.6 Integrated Vulnerability Assessment

The WDVF integrates the principal analytical components into a structured assessment framework.

The integrated outputs support:

- Comparative vulnerability assessment
- Identification of influential environmental and hydraulic indicators
- Spatial differentiation of vulnerability
- Infrastructure susceptibility screening
- Management prioritisation
- Climate-informed water infrastructure planning

The framework is designed to accommodate updated monitoring observations, revised hydraulic parameters and additional climate information as these become available.

---

## 5. Qatar Water Vulnerability Intelligence Dashboard

The **Qatar Water Vulnerability Intelligence Dashboard** is an interactive Python-based application developed using Streamlit.

It consolidates the principal outputs of the WDVF into a unified geospatial and analytical interface, enabling interactive exploration of vulnerability patterns, hydrochemical characteristics, hydraulic performance and hydroclimatic conditions.

The dashboard is designed to support research interpretation, comparative analysis and water infrastructure decision-making.

### 5.1 Dashboard Components

The dashboard contains six integrated analytical panels.

| Panel | Analytical component | Function |
|---|---|---|
| 01 | Municipal Vulnerability Atlas | Interactive GIS visualisation of HRI, CSI, HVI and SVI |
| 02 | Municipality Performance Ranking | Comparative vulnerability indicators and spatial aggregation |
| 03 | Hydrochemical Risk Profile | Hydrochemical indicator distributions and comparisons |
| 04 | Hydraulic Performance Assessment | Head-loss calculations, pipeline configurations and hydraulic susceptibility |
| 05 | Hydroclimatic Conditions (2009–2025) | Historical climate-stress indicators and temporal variations |
| 06 | Climate Outlook (2031–2070) | ACCESS-CM2 meteorological projections under SSP2-4.5 and SSP5-8.5 |

The interface also includes interactive filters for spatial indicators, hydrochemical parameters, hydraulic performance metrics, historical climate variables, future meteorological projections and pipeline configurations.

Additional tables provide detailed indicator values, engineering parameters and supporting data provenance.

### 5.2 Dashboard Data Integration

The dashboard incorporates the following principal datasets:

- `GIS_Indicators.xlsx`
- `Hydrochemistry_Indicators.xlsx`
- `Hydraulic_Indicators.xlsx`
- `Hydraulic_Pipeline_Scenarios.xlsx`
- `Hydroclimatic_Indicators.xlsx`
- `ACCESS-CM2_ssp245_Monthly_Corrected_2031_2070.xlsx`
- `ACCESS-CM2_ssp585_Monthly_Corrected_2031_2070.xlsx`
- Qatar administrative boundary shapefiles

The dashboard reads the packaged datasets and generates interactive visualisations and aggregated indicator summaries.

The climate outlook displays bias-corrected meteorological projections. Future ET₀ and CSI are not recalculated within the dashboard interface.

### 5.3 Dashboard Installation and Execution

Clone the repository:

```bash
git clone https://github.com/Kagiso-S-More/Qatar_MWDVF.git
```

Navigate to the dashboard directory:

```bash
cd Qatar_MWDVF/Dashboard
```

Install the dashboard dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch the application:

```bash
python -m streamlit run app.py
```

The dashboard will be accessible locally at:

http://localhost:8501

The Streamlit server must remain active while the application is in use.

**Dashboard source code and documentation:**

[Dashboard directory](https://github.com/Kagiso-S-More/Qatar_MWDVF/tree/main/Dashboard)

[Dashboard README](https://github.com/Kagiso-S-More/Qatar_MWDVF/blob/main/Dashboard/README.md)

### 5.4 Application Scope

The dashboard provides an integrated research and decision-support environment based on the available datasets and modelling outputs.

Hydrochemical information originates from groundwater observations, hydraulic performance indicators are calculated using the specified engineering parameters, and future climate conditions are derived from bias-corrected ACCESS-CM2 projections.

The application supports interactive vulnerability assessment and data exploration. It does not currently receive continuous operational telemetry from water distribution infrastructure.

---

## 6. Repository Structure

The repository separates the interactive dashboard from the principal research datasets, modelling scripts and analytical outputs.

```text
Qatar_MWDVF/
│
├── README.md
├── CITATION.cff
├── requirements.txt
├── .gitignore
├── .gitattributes
│
├── Dashboard/
│   ├── app.py
│   ├── README.md
│   ├── requirements.txt
│   │
│   └── data/
│       ├── GIS_Indicators.xlsx
│       ├── Hydrochemistry_Indicators.xlsx
│       ├── Hydraulic_Indicators.xlsx
│       ├── Hydraulic_Pipeline_Scenarios.xlsx
│       ├── Hydroclimatic_Indicators.xlsx
│       ├── ACCESS-CM2_ssp245_Monthly_Corrected_2031_2070.xlsx
│       ├── ACCESS-CM2_ssp585_Monthly_Corrected_2031_2070.xlsx
│       │
│       └── Qatar Boundary/
│           ├── gadm41_QAT_0.*
│           └── gadm41_QAT_1.*
│
└── Data/
    │
    ├── CMIP6/
    │   ├── ACCESS-CM2/
    │   │   ├── historical/
    │   │   │   ├── hurs/
    │   │   │   ├── pr/
    │   │   │   ├── rlds/
    │   │   │   ├── rsds/
    │   │   │   ├── sfcWind/
    │   │   │   ├── tasmax/
    │   │   │   └── tasmin/
    │   │   │
    │   │   ├── ssp245/
    │   │   └── ssp585/
    │   │
    │   ├── Bias_Correction/
    │   ├── ERA5_Land/
    │   ├── Future_Processed/
    │   └── Climate processing Python scripts
    │
    ├── ERA5_Land/
    │   ├── ERA5_Land_Processing.py
    │   ├── NetCDF_to_Excel.py
    │   └── Climate datasets
    │
    ├── Primary Model/
    │   ├── Primary_Model.py
    │   ├── Primary_ML_Dataset.xlsx
    │   └── Primary_ML_Results.xlsx
    │
    ├── Secondary Model/
    │   ├── Secondary_Model.py
    │   ├── Secondary_ML_Dataset.xlsx
    │   └── Secondary_ML_Results.xlsx
    │
    ├── ML_Final_Outputs/
    │   ├── Model_Performance.png
    │   ├── Feature_Importance.png
    │   ├── RF_Confusion_Matrix.png
    │   └── Supporting results workbooks
    │
    ├── Figures/
    │
    ├── ERA5-Land_Climate_Data.xlsx
    ├── ETo_from_ERA5-Land.xlsx
    ├── FAO56_ET0_Inputs_2009_2025_with_Rn.xlsx
    ├── Geochemistry_Dataset.xlsx
    ├── Hydrochemistry_Indicators.xlsx
    ├── Hydroclimatic_Indicators.xlsx
    ├── Hydraulic_Indicators.xlsx
    ├── Hydraulic_Pipeline_Scenarios.xlsx
    ├── GIS_Indicators.xlsx
    ├── PHREEQC_Results.xlsx
    └── MWDVF_Sensitivity.xlsx
```

The directory structure summarises the principal files and folders rather than providing an exhaustive inventory of every climate file, Python script, figure and supporting output.

---

## 7. Python Environment and Dependencies

### 7.1 Development Environment

The principal computational workflow was developed using **Python 3.13.9**, with the Anaconda Python distribution and Spyder integrated development environment on Windows.

The workflow supports scientific computing, climate-data processing, geochemical and hydraulic calculations, machine-learning classification and scientific visualisation.

The Streamlit dashboard operates as a separate Python application and is launched through a terminal.

### 7.2 Dependency Management

The repository contains two requirements files:

| File | Purpose |
|---|---|
| `requirements.txt` | Principal scientific and modelling workflow |
| `Dashboard/requirements.txt` | Streamlit dashboard and visualisation dependencies |

Install the principal research dependencies using:

```bash
python -m pip install -r requirements.txt
```

For the dashboard:

```bash
python -m pip install -r Dashboard/requirements.txt
```

The dependencies required for individual scripts may differ according to their analytical functions.

### 7.3 Recording the Computational Environment

For reproducibility, users can record their installed Python version and package dependencies using:

```bash
python --version
python -m pip freeze > environment_versions.txt
```

The resulting file provides a record of the installed packages for that computational environment.

---

## 8. Computational Reproducibility

The repository provides Python scripts and associated datasets supporting the principal computational stages of the WDVF.

The recommended processing sequence is outlined below.

**Step 1: Groundwater and Hydrochemical Data Preparation**

Prepare groundwater chemistry datasets, hydrochemical indicators, PHREEQC outputs and spatially referenced observations.

**Step 2: Historical ERA5-Land Climate Processing**

Process historical meteorological datasets using the scripts within `Data/ERA5_Land/`.

**Step 3: Historical CMIP6 Processing**

Process ACCESS-CM2 historical climate simulations using the relevant scripts within `Data/CMIP6/`.

**Step 4: Climate Bias Correction**

Evaluate historical ACCESS-CM2 simulations against ERA5-Land reference data and apply the selected bias-correction procedures.

**Step 5: Future Climate Projection Processing**

Process SSP2-4.5 and SSP5-8.5 projections for 2031–2070.

**Step 6: Hydroclimatic Indicator Development**

Calculate reference evapotranspiration, precipitation-deficit indicators and composite climate-stress metrics.

**Step 7: Hydraulic Vulnerability Assessment**

Calculate hydraulic head loss, roughness and scaling indicators, and hydraulic vulnerability indices using the supplied engineering parameters.

**Step 8: GIS-Based Spatial Vulnerability Assessment**

Integrate hydrochemical, hydroclimatic and hydraulic indicators through spatial interpolation, aggregation and vulnerability mapping.

**Step 9: Machine-Learning Classification**

Execute the primary and secondary machine-learning workflows using their respective datasets.

**Step 10: Model Evaluation and Sensitivity Analysis**

Evaluate classification performance, feature importance, confusion matrices and sensitivity-analysis results.

**Step 11: Interactive Dashboard Visualisation**

Launch the Streamlit dashboard to explore the integrated spatial, hydrochemical, hydraulic and climate outputs.

**Important:** Some research scripts contain local Windows directory paths and may require adjustment before execution on another computer. Processing stages may also depend on outputs generated during preceding steps.

---

## 9. Research Outputs

The repository includes supporting materials for the following analytical components.

| Component | Principal outputs |
|---|---|
| Hydrochemistry | SAR, KR, SHI, MSP, TDS, PHREEQC results and HRI |
| Hydroclimate | Historical hydroclimatic indicators, climate projections and CSI |
| Hydraulics | Pipeline configurations, head-loss calculations, PRSI and HVI |
| GIS | Spatial indicators, vulnerability maps and SVI |
| Machine learning | Classification outputs, performance metrics, confusion matrices and feature importance |
| Sensitivity analysis | Hydraulic parameter sensitivity and integrated vulnerability responses |
| Climate projections | ACCESS-CM2 historical and future climate datasets and processed outputs |
| Interactive dashboard | Integrated GIS maps, vulnerability rankings, indicator comparisons, hydraulic assessments and climate visualisations |

These outputs support the scientific interpretation and practical application of the WDVF.

---

## 10. Scientific Interpretation and Limitations

The WDVF should be interpreted within the following methodological considerations.

1. **Hydrochemical data:** Groundwater observations represent the hydrochemical baseline and should not be interpreted as direct measurements of treated water within operating distribution pipelines.

2. **Hydraulic assessment:** Hydraulic indicators are derived from the supplied pipeline configurations and engineering parameters rather than a calibrated operational distribution-network model.

3. **Climate-model uncertainty:** Future climate projections are based on ACCESS-CM2 and do not represent a multi-model CMIP6 ensemble.

4. **Bias-correction uncertainty:** Bias correction reduces selected systematic differences between historical simulations and reference data but does not eliminate future projection uncertainty.

5. **Spatial uncertainty:** Sampling distribution, spatial interpolation and administrative-area aggregation may influence vulnerability patterns and rankings.

6. **Machine-learning interpretation:** Classification performance depends on predictor selection, constructed vulnerability classes, training data and validation procedures.

7. **Dashboard interpretation:** The dashboard visualises calculated research indicators and climate projections. It is not connected to live water distribution telemetry or utility control systems.

The framework is intended for comparative vulnerability assessment, infrastructure susceptibility screening and research-informed prioritisation rather than direct prediction of individual pipeline failures.

---

## 11. Data Sources and Acknowledgements

### 11.1 NASA NEX-GDDP-CMIP6

Thrasher, B., et al. (2022). NASA Global Daily Downscaled Projections, CMIP6. *Scientific Data*, 9, 262.

https://doi.org/10.1038/s41597-022-01393-4

### 11.2 ERA5-Land

Copernicus Climate Change Service (C3S), Climate Data Store.

ERA5-Land reanalysis dataset.

https://cds.climate.copernicus.eu/

### 11.3 Groundwater Data

Groundwater observations are attributed to the original sources used in the study, including Shomar and Sankaran (2024).

Users should consult the associated manuscript and original publications for complete bibliographic information and applicable data-use conditions.

### 11.4 Software and Analytical Methods

The research incorporates Python scientific-computing libraries, PHREEQC geochemical modelling, GIS-based spatial analysis, machine-learning methods and Streamlit interactive visualisation.

Original software developers, documentation and relevant scientific publications should be acknowledged where appropriate.

Third-party datasets remain subject to the access conditions and redistribution policies established by their respective providers.

---

## 12. Data and Code Availability

The research datasets, Python scripts, modelling outputs, climate-processing materials, geospatial resources and interactive dashboard are available through the GitHub repository:

**https://github.com/Kagiso-S-More/Qatar_MWDVF**

The repository provides supporting materials associated with the hydrochemical, hydroclimatic, hydraulic, GIS and machine-learning components of the WDVF.

The interactive dashboard is available under:

**https://github.com/Kagiso-S-More/Qatar_MWDVF/tree/main/Dashboard**

The availability and reuse of individual third-party datasets remain subject to their original licensing and access conditions.

---

## 13. Citation

Researchers using the framework, scripts, dashboard or derived datasets are requested to acknowledge the repository and cite the associated research publication when available.

**Repository title:** Qatar Water Distribution Vulnerability Framework (WDVF)

**Author:** Kagiso S. More

**Repository URL:** https://github.com/Kagiso-S-More/Qatar_MWDVF

Citation metadata is provided in `CITATION.cff`.

Publication information and a permanent repository DOI may be added following manuscript publication and repository archiving.

---

## 14. Licensing and Reuse

No blanket open-source licence is currently specified for this repository.

The absence of a licence does not imply unrestricted permission to reproduce, modify or redistribute repository contents.

Original research code, processed datasets and third-party source materials may be subject to different intellectual-property and reuse conditions.

Users should verify applicable permissions before redistributing source datasets or adapting research materials.

---

## 15. Contact

**Kagiso S. More**

Research areas: Hydrogeochemistry, Hydroclimatic Modelling, Water Infrastructure Vulnerability, GIS and Machine Learning.

**GitHub:** https://github.com/Kagiso-S-More

**Research repository:** https://github.com/Kagiso-S-More/Qatar_MWDVF

For scientific enquiries, collaboration opportunities or methodological questions, please contact the repository owner through GitHub.
