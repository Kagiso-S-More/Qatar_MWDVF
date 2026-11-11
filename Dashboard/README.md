# Qatar MWDVF — Multipanel Dashboard V3

A single-screen Streamlit research dashboard using the supplied GIS, hydrochemical, hydraulic, climate, and Qatar GADM boundary datasets. All displayed values are derived from the packaged data.

## Start on Windows (Anaconda Prompt)

```bat
cd C:\Users\Kagiso\WaterNetwork\Qatar_MWDVF_Dashboard
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. **Do not run with Spyder `%runfile`**. If an older dashboard remains open, stop its server using Ctrl+C, replace the entire dashboard folder, then restart.

## Features

- One multipanel page: GIS choropleth, municipality rankings, hydrochemistry distribution, hydraulic scenario sensitivity, historical hydroclimate and future ACCESS-CM2 inputs
- Sidebar filters for municipalities, indicators, scenarios and sampling points
- Expandable tables and provenance/limitations section
- Annual future precipitation is **summed**, while other future variables use annual means

## Scientific scope

Groundwater samples are not measurements from municipal distribution pipes. Hydraulic scenarios are theoretical, and the app does not connect to live utility systems. Municipal values are recomputed by spatially joining sampling points to the supplied GADM boundaries. Future corrected meteorological inputs are displayed, not recalculated future CSI/ET0.
