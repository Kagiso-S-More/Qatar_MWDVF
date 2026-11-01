# Qatar Municipal Water Distribution Vulnerability Framework (MWDVF)

Research data and analysis archive for an integrated GIS–AI assessment of hydrochemical, hydroclimatic, hydraulic and spatial vulnerability in Qatar.

> **Status:** Repository template. Data files and validated analysis code must be copied from the research computer. No source NetCDF files or analysis workbooks are included in this template.

## Study scope

- Groundwater observations: 2020, 201 locations.
- Historical climate: ERA5-Land, with 1995–2014 calibration/reference period and 2009–2025 study analysis.
- Climate projections: NASA NEX-GDDP-CMIP6, ACCESS-CM2, SSP2-4.5 and SSP5-8.5, 2031–2070.
- Climate variables: `pr`, `tasmax`, `tasmin`, `hurs`, `rsds`, `rlds`, `sfcWind`.
- Hydroclimatic outputs: ET₀, MPD, SPD₃ and CSI.
- Hydraulic and GIS–AI results: see workbooks and scripts under `Data/`.

## Repository structure

```text
Data/
├── CMIP6/
│   ├── ACCESS-CM2/
│   │   ├── historical/
│   │   ├── ssp245/
│   │   └── ssp585/
│   │       └── [each scenario has hurs, pr, rlds, rsds, sfcWind, tasmax, tasmin]
│   ├── Bias_Correction/
│   ├── ERA5_Land/
│   ├── Future_Processed/
│   │   ├── CSI/
│   │   ├── ET0/
│   │   └── Figures/
│   └── ClimateCMIP6*.py and Plot_CMIP6_Hydroclimatic_Figures.py
├── Primary Model/
├── Secondary Model/
├── Figures/
└── Documentation/
```

Other top-level workbooks in `Data/` should retain their existing names, including `Full_Dataset_2026_KM.xlsx`, `Hydraulic_Pipeline_Scenarios.xlsx`, `MWDVF_Sensitivity.xlsx`, `Climate_Data_Converted_2009_2025.xlsx`, and `FAO56_ET0_Inputs_2009_2025_with_Rn.xlsx`. Place all original processed climate workbooks and raw NetCDF files in their matching folders.

## Reproducibility

1. Copy the original Excel/CSV, NetCDF, figure and text log files into the corresponding folders.
2. Replace each Python placeholder with the validated script from the research computer.
3. Install dependencies with `pip install -r requirements.txt`. This is an indicative dependency list; pin exact tested versions for a final reproducible release.
4. Adjust hard-coded Windows paths in the original scripts to the local checkout or document their required input paths.
5. Document the processing order, calibration settings, data provenance, software versions, and any random seeds in `Data/Documentation/`.

**Suggested climate workflow:** historical download/processing → ERA5-Land comparison and bias correction → future monthly processing → ET₀ → CSI → figures. The other primary and secondary modelling workflows should be documented using the original scripts.

## Data provenance and attribution

- **NASA NEX-GDDP-CMIP6:** Thrasher, B. et al. (2022). NASA Global Daily Downscaled Projections, CMIP6. *Scientific Data* 9, 262. https://doi.org/10.1038/s41597-022-01393-4
- **ERA5-Land:** cite the exact Copernicus Climate Data Store dataset and version used in the analysis; retain downloaded metadata and applicable attribution.
- **Groundwater data:** Shomar and Sankaran (2024); include the complete bibliographic citation and original reuse terms before releasing redistributed data.

The archive should distinguish original third-party datasets from derived research products. Confirm NASA, Copernicus and other data-provider redistribution terms and acknowledge all sources. Remove private or identifying information before publishing.

## Storage

Raw `.nc` files are configured for **Git LFS** in `.gitattributes`. Install Git LFS and run `git lfs install` before adding files. GitHub enforces a 100 MiB limit per regular Git object; Git LFS storage and bandwidth quotas depend on the account. Verify the total size and quota before pushing. For very large raw collections, consider archiving raw data on Zenodo or another research repository and keeping download manifests/scripts on GitHub.

## Citation and licensing

Complete `CITATION.cff` after the manuscript/repository metadata are final. No blanket license is applied in this template: choose a license for original code and derived outputs only after checking the rights of all third-party data.

## Important interpretation

Hydraulic susceptibility is informed by available environmental data and model assumptions. Outputs should not be presented as directly measured utility-network operating conditions. Future climate results represent ACCESS-CM2 single-model projections, not a multi-model ensemble.
