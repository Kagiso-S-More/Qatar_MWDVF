# Qatar Municipal Water Distribution Vulnerability Framework (MWDVF)

## 1. Overview

This repository contains the research datasets, Python scripts, modelling outputs, climate projections, and supporting documentation developed for the study:

**Integrated GIS–AI Assessment of Municipal Water Distribution Vulnerability Using Hydrochemical, Hydroclimatic and Hydraulic Indicators in Qatar**

The study develops an integrated framework for assessing municipal water distribution vulnerability in Qatar by combining groundwater hydrochemistry, hydroclimatic stress, hydraulic susceptibility, geographic information systems (GIS), and artificial intelligence (AI).

The repository supports research transparency, computational reproducibility, methodological verification, and future applications of integrated vulnerability assessment in water-resource management and infrastructure planning.

**Repository:** https://github.com/Kagiso-S-More/Qatar_MWDVF

**Researcher:** Kagiso S. More

---

## 2. Research Objectives

The study aims to:

1. Evaluate groundwater hydrochemical characteristics and derive hydrochemical vulnerability indicators.
2. Quantify historical hydroclimatic stress using ERA5-Land climate data.
3. Assess future hydroclimatic conditions using CMIP6 climate projections under SSP2-4.5 and SSP5-8.5.
4. Evaluate hydraulic susceptibility using theoretical pipeline configurations and hydrochemically informed risk indicators.
5. Integrate hydrochemical, hydroclimatic, and hydraulic indicators through GIS-based spatial analysis.
6. Apply machine-learning algorithms to classify vulnerability and identify influential predictors.
7. Develop an integrated municipal water distribution vulnerability assessment framework applicable to Qatar and other water-stressed regions.

---

## 3. Study Area and Research Datasets

### 3.1 Study Area

The study focuses on Qatar, a hyper-arid country characterized by limited natural freshwater availability, high atmospheric evaporative demand, and substantial reliance on engineered water infrastructure.

The framework evaluates environmental and hydraulic factors that may contribute to the vulnerability of municipal water distribution systems.

### 3.2 Groundwater and Hydrochemical Data

The hydrochemical assessment uses groundwater observations from 2020, comprising approximately 201 sampling locations.

The analysis incorporates major-ion chemistry, hydrochemical indices, geochemical modelling outputs, and spatially referenced groundwater characteristics.

Principal datasets include:

- `Geochemistry_Dataset.xlsx`
- `Hydrochemistry_Indicators.xlsx`
- `PHREEQC_Results.xlsx`
- `GIS_Indicators.xlsx`

Geochemical calculations and mineral saturation indices are supported by PHREEQC modelling.

### 3.3 Historical Climate Data

Historical hydroclimatic conditions are evaluated using ERA5-Land climate data covering 1995–2025.

The period 1995–2014 is used as the historical reference period for climate-model bias correction.

The analysis includes meteorological variables required for reference evapotranspiration and climate-stress calculations.

Relevant datasets include:

- `ERA5-Land_Climate_Data.xlsx`
- `ETo_from_ERA5-Land.xlsx`
- `FAO56_ET0_Inputs_2009_2025_with_Rn.xlsx`
- `Hydroclimatic_Indicators.xlsx`

### 3.4 Future Climate Projections

Future hydroclimatic conditions are assessed using the NASA NEX-GDDP-CMIP6 dataset.

The climate-projection configuration is:

| Parameter | Description |
|---|---|
| Climate model | ACCESS-CM2 |
| Ensemble member | r1i1p1f1 |
| Historical reference period | 1995–2014 |
| Future projection period | 2031–2070 |
| Near-term period | 2031–2050 |
| Mid-century period | 2051–2070 |
| Intermediate-emissions scenario | SSP2-4.5 |
| High-emissions scenario | SSP5-8.5 |

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

The future assessment uses one global climate model and should not be interpreted as a multi-model CMIP6 ensemble.

---

## 4. Methodological Framework

### 4.1 Hydrochemical Vulnerability Assessment

Groundwater hydrochemical conditions are evaluated using derived indicators and PHREEQC geochemical modelling.

The hydrochemical framework incorporates parameters such as:

- Sodium adsorption ratio (SAR)
- Kelly's ratio (KR)
- Sodium hazard index (SHI)
- Mineral saturation potential (MSP)
- Total dissolved solids (TDS)

These indicators contribute to the composite Hydrochemical Risk Index (HRI).

### 4.2 Hydroclimatic Stress Assessment

Hydroclimatic assessment incorporates historical climate observations and future climate projections.

The principal analytical components include:

- Reference evapotranspiration (ET₀)
- Monthly precipitation deficit (MPD)
- Three-month standardized precipitation-deficit indicator (SPD₃)
- Composite Climate Stress Index (CSI)

The climate-processing workflow includes historical meteorological-data preparation, CMIP6 historical evaluation, bias correction, future climate processing, evapotranspiration calculations, and hydroclimatic indicator development.

### 4.3 Hydraulic Vulnerability Assessment

Hydraulic vulnerability is assessed using theoretical pipeline parameters and established hydraulic relationships.

The framework includes:

- Hazen–Williams head-loss estimation
- Pipeline friction and hydraulic susceptibility
- Hydrochemically informed scaling and roughness indicators
- Pipeline Roughness and Scaling Index (PRSI)
- Hydraulic Vulnerability Index (HVI)

The hydraulic assessment represents scenario-based susceptibility rather than direct measurements from a calibrated operational municipal water distribution network.

Relevant datasets include:

- `Hydraulic_Indicators.xlsx`
- `Hydraulic_Pipeline_Scenarios.xlsx`

### 4.4 GIS-Based Spatial Vulnerability Assessment

Spatial analysis integrates hydrochemical, hydroclimatic, and hydraulic indicators to evaluate geographic differences in vulnerability.

The workflow incorporates:

- Spatial interpolation
- Municipal-level aggregation
- Spatial hotspot analysis
- Integrated vulnerability mapping
- Spatial Vulnerability Index (SVI)

GIS-derived results support the identification of areas with relatively elevated environmental and hydraulic susceptibility.

### 4.5 Machine-Learning Vulnerability Classification

Machine-learning methods are used to classify vulnerability and evaluate the contribution of different hydrochemical, hydroclimatic, and hydraulic predictors.

The modelling framework considers:

- Random Forest (RF)
- Gradient Boosting (GB)
- Extreme Gradient Boosting (XGBoost)

The repository contains separate primary and secondary modelling workflows.

Model evaluation includes classification-performance metrics, confusion matrices, and feature-importance analysis.

### 4.6 Integrated Municipal Water Distribution Vulnerability Framework

The MWDVF integrates the principal vulnerability components into a structured assessment framework.

The resulting outputs are intended to support comparative vulnerability analysis, identification of influential risk factors, and research-based prioritization of municipal water infrastructure.

---

## 5. Repository Structure

The principal research files are organized under the `Data/` directory.

```text
Qatar_MWDVF/
│
├── README.md
├── CITATION.cff
├── requirements.txt
├── UPLOAD_GUIDE.md
├── .gitignore
├── .gitattributes
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
    │   │   │   └── [Seven climate-variable folders]
    │   │   │
    │   │   └── ssp585/
    │   │       └── [Seven climate-variable folders]
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
    ├── Documentation/
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

The folder tree summarizes the principal files and directories rather than providing an exhaustive inventory of every NetCDF file, Python script, figure, and supporting output.

---

## 6. Python Environment and Dependencies

### 6.1 Development Environment

The computational workflow uses **Python 3.13.9**, with the Anaconda Python distribution and Spyder integrated development environment (IDE) on Windows.

The Python environment supports scientific computing, climate-data processing, hydrochemical and hydraulic indicator calculations, machine-learning classification, and scientific visualization.

### 6.2 Recommended Python Library Versions

The following are recommended recent stable package versions for Python 3.13.9, rather than a verified record of the exact packages originally installed during every analysis.

| Python Library | Recommended Version | Application |
|---|---|---|
| NumPy | 2.5.4 | Numerical computations and array processing |
| pandas | 3.1.0 | Data manipulation and time-series analysis |
| SciPy | 1.18.1 | Scientific and statistical calculations |
| Matplotlib | 3.11.2 | Scientific plotting and visualization |
| scikit-learn | 1.9.1 | Machine learning, model evaluation, and validation |
| XGBoost | 3.4.1 | Extreme Gradient Boosting classification |
| netCDF4 | 1.7.5.1.post1 | Processing NetCDF climate datasets |
| openpyxl | 3.1.5 | Reading and writing Excel workbooks |

Other libraries imported by individual scripts may also be required.

### 6.3 Installing Python Dependencies

Create or activate a Python 3.13.9 environment before installing the packages.

The recommended packages can be installed using:

```bash
python -m pip install numpy==2.5.4 pandas==3.1.0 scipy==1.18.1 matplotlib==3.11.2 scikit-learn==1.9.1 xgboost==3.4.1 netCDF4==1.7.5.1.post1 openpyxl==3.1.5
```

Alternatively, use the repository's requirements file:

```bash
python -m pip install -r requirements.txt
```

The `requirements.txt` file should contain package versions consistent with the selected computational environment.

### 6.4 Recording the Computational Environment

For reproducibility, users can record their installed Python version and package dependencies using:

```bash
python --version
python -m pip freeze > environment_versions.txt
```

The resulting file provides a record of the installed packages for that computational environment.

The recommended dependency combination should be tested against the complete analysis workflow before being considered a fully validated environment.

---

## 7. Computational Reproducibility

The repository contains Python scripts and associated input datasets supporting the principal computational stages.

The recommended processing sequence is outlined below.

### Step 1: Prepare Groundwater and Hydraulic Datasets

Prepare the groundwater chemistry, hydrochemical indicators, PHREEQC results, theoretical hydraulic parameters, and GIS-related datasets.

### Step 2: Process Historical ERA5-Land Climate Data

Use the Python scripts within `Data/ERA5_Land/` to process the historical climate datasets and generate tabulated meteorological inputs.

### Step 3: Process Historical CMIP6 Simulations

Process ACCESS-CM2 historical climate simulations using the relevant scripts within `Data/CMIP6/`.

### Step 4: Perform Climate Bias Correction

Compare historical ACCESS-CM2 simulations against ERA5-Land reference data and derive the bias-correction parameters.

### Step 5: Process Future Climate Projections

Process the SSP2-4.5 and SSP5-8.5 climate projections for 2031–2070.

### Step 6: Calculate Future Hydroclimatic Indicators

Calculate reference evapotranspiration, precipitation-deficit indicators, and composite climate-stress metrics.

### Step 7: Conduct Spatial Vulnerability Analysis

Integrate the hydrochemical, hydroclimatic, and hydraulic indicators through GIS-based spatial analysis.

### Step 8: Execute Machine-Learning Models

Run the primary and secondary machine-learning scripts using their respective datasets.

### Step 9: Evaluate Model Performance

Evaluate classification performance, confusion matrices, feature importance, and sensitivity-analysis results.

### Step 10: Generate Research Figures and Tables

Use the processed datasets and modelling outputs to generate the figures, maps, and tables required for scientific interpretation.

**Important:** Some scripts use local Windows directory paths. These paths may need to be updated to match the user's computer before execution.

The processing stages are interdependent, and some scripts require outputs generated by preceding stages.

---

## 8. Research Outputs

The repository includes supporting materials for the following analytical components:

| Component | Principal Outputs |
|---|---|
| Hydrochemistry | Hydrochemical indicators, PHREEQC results, HRI |
| Hydroclimate | Historical and future climate indicators, CSI |
| Hydraulics | Pipeline scenarios, head-loss susceptibility, PRSI, HVI |
| GIS | Spatial indicators, vulnerability mapping, SVI |
| Machine learning | Classification results, performance metrics, confusion matrices |
| Sensitivity analysis | Integrated vulnerability sensitivity results |
| Climate projections | Historical and future ACCESS-CM2 datasets and processed outputs |

These materials support the scientific analysis and interpretation presented in the associated research manuscript.

---

## 9. Scientific Interpretation and Limitations

The results should be interpreted within the following methodological limitations:

1. **Climate-model uncertainty:** Future climate projections are based on ACCESS-CM2 rather than a multi-model CMIP6 ensemble.

2. **Bias-correction uncertainty:** Bias correction reduces selected systematic differences between historical simulations and reference data but does not eliminate future projection uncertainty.

3. **Spatial uncertainty:** Spatial interpolation, sampling distribution, and municipality-level aggregation may influence the resulting vulnerability patterns.

4. **Machine-learning uncertainty:** Classification performance depends on predictor selection, target-variable construction, training data, and validation procedures.

5. **Operational interpretation:** The framework is intended for comparative susceptibility assessment and research-based prioritization, not direct prediction of individual pipeline failures.

---

## 10. Data Sources and Acknowledgements

The research incorporates datasets and methodological information from the following sources.

### 10.1 NASA NEX-GDDP-CMIP6

Thrasher, B., et al. (2022). NASA Global Daily Downscaled Projections, CMIP6. *Scientific Data*, 9, 262.

https://doi.org/10.1038/s41597-022-01393-4

### 10.2 ERA5-Land

Copernicus Climate Change Service (C3S), Climate Data Store.

ERA5-Land reanalysis dataset.

https://cds.climate.copernicus.eu/

### 10.3 Groundwater Data

Groundwater observations are attributed to the original sources used in the study, including Shomar and Sankaran (2024).

Users should consult the associated manuscript and original publications for complete bibliographic information and applicable data-use conditions.

### 10.4 Software and Analytical Methods

The research incorporates Python scientific-computing libraries, PHREEQC geochemical modelling, and GIS-based spatial analysis.

The original developers, software documentation, and relevant scientific publications should be acknowledged where appropriate.

All third-party datasets remain subject to the access conditions and redistribution policies established by their respective providers.

---

## 11. Data Availability

The research datasets, Python scripts, modelling outputs, climate-processing materials, and supporting figures uploaded for the study are available through this GitHub repository:

https://github.com/Kagiso-S-More/Qatar_MWDVF

The repository includes processed research datasets and supporting source files associated with the hydrochemical, hydroclimatic, hydraulic, GIS, and machine-learning assessments.

The availability and reuse of individual third-party datasets remain subject to the terms established by their original providers.

---

## 12. Citation

Researchers using the framework, scripts, or derived datasets are requested to acknowledge this repository and cite the associated research publication when available.

**Repository title:** Qatar Municipal Water Distribution Vulnerability Framework (MWDVF)

**Author:** Kagiso S. More

**Repository URL:** https://github.com/Kagiso-S-More/Qatar_MWDVF

Citation metadata is provided in the `CITATION.cff` file.

Publication information and a permanent repository DOI may be added following manuscript publication and repository archiving.

---

## 13. Licensing and Reuse

No blanket open-source license is currently specified for this repository.

The absence of a license does not imply unrestricted permission to reproduce, modify, or redistribute the repository contents.

Original research code, processed datasets, and third-party source materials may be subject to different intellectual-property and reuse conditions.

Users should verify applicable permissions before redistributing source datasets or adapting research materials.

---

## 14. Contact

**Kagiso S. More**

Research areas: Hydrogeochemistry, Hydroclimatic Modelling, Water Infrastructure Vulnerability, GIS, and Machine Learning.

**GitHub:** https://github.com/Kagiso-S-More

**Research repository:** https://github.com/Kagiso-S-More/Qatar_MWDVF

For scientific enquiries, collaboration opportunities, or methodological questions, please contact the repository owner through GitHub.
