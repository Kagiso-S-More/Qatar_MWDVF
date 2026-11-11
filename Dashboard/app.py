from pathlib import Path
import pandas as pd
import geopandas as gpd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Qatar Water Infrastructure | Vulnerability Intelligence', page_icon='💧', layout='wide', initial_sidebar_state='expanded')
BASE = Path(__file__).resolve().parent / 'data'

st.markdown('''<style>
.block-container {padding-top:1.15rem; padding-bottom:2rem; max-width: 1800px}
[data-testid="stMetric"] {background:#f0f5fa; border:1px solid #dce7f0; padding:14px; border-radius:12px}
[data-testid="stMetricLabel"] {font-size:0.84rem; color:#50677d}
section[data-testid="stSidebar"] {background:#f2f6fa}
h3 {padding-top:.4rem !important; color:#173d59}
div[data-testid="stPlotlyChart"] {border:1px solid #e3ebf1; border-radius:10px; overflow:hidden}
</style>''', unsafe_allow_html=True)

@st.cache_data(show_spinner='Loading vulnerability indicators…')
def load_data():
    gis = pd.read_excel(BASE / 'GIS_Indicators.xlsx')
    chem = pd.read_excel(BASE / 'Hydrochemistry_Indicators.xlsx')
    hyd = pd.read_excel(BASE / 'Hydraulic_Indicators.xlsx')
    scen = pd.read_excel(BASE / 'Hydraulic_Pipeline_Scenarios.xlsx', sheet_name='Scenario_Summary')
    climate = pd.read_excel(BASE / 'Hydroclimatic_Indicators.xlsx')
    future = {
        k: pd.read_excel(BASE / f'ACCESS-CM2_{k}_Monthly_Corrected_2031_2070.xlsx', sheet_name='Monthly_2031_2070')
        for k in ('ssp245', 'ssp585')
    }
    boundary = gpd.read_file(BASE / 'gadm41_QAT_shp/gadm41_QAT_1.shp').to_crs('EPSG:4326')
    return gis, chem, hyd, scen, climate, future, boundary

gis, chem, hyd, scen, climate, future, boundaries = load_data()
name_map = {'Ad Dawhah': 'Doha', 'Ar Rayyan': 'Al Rayyan', 'Al Wakrah': 'Al Wakra', 'Madinat ash Shamal': 'Al Shamal'}
boundaries['Municipality'] = boundaries['NAME_1'].replace(name_map)
points = gpd.GeoDataFrame(gis, geometry=gpd.points_from_xy(gis.Longitude, gis.Latitude), crs='EPSG:4326')
assigned = gpd.sjoin(points, boundaries[['Municipality', 'geometry']], how='left', predicate='within').drop(columns='index_right')
summary = (assigned.dropna(subset=['Municipality']).groupby('Municipality', as_index=False)
           .agg(n=('SVI', 'size'), HRI=('HRI', 'mean'), HVI=('HVI', 'mean'), SVI=('SVI', 'mean'), CSI=('CSI_2020', 'mean')))
summary['Coverage'] = summary['n'].map(lambda n: 'Insufficient (n=1)' if n == 1 else 'Observed')
merged = (assigned.merge(chem[['Sample_ID', 'SAR', 'KR', 'SHI', 'MSP', 'TDS_mg_L']], on='Sample_ID', how='left')
          .merge(hyd[['Sample_ID', 'PRSI', 'C_HA', 'hf']], on='Sample_ID', how='left'))
climate = climate.copy()
climate['Date'] = pd.to_datetime(dict(year=climate.Year, month=climate.Month, day=1))

st.sidebar.title('💧 Qatar Water Intelligence')
st.sidebar.caption('Municipal vulnerability assessment | Qatar')
all_municipalities = sorted(summary.Municipality.tolist())
selected = st.sidebar.multiselect('Municipalities', all_municipalities, default=all_municipalities)
map_metric = st.sidebar.selectbox('Spatial assessment metric', ['SVI', 'HRI', 'HVI', 'CSI'])
chem_metric = st.sidebar.selectbox('Hydrochemical indicator', ['HRI', 'SAR', 'KR', 'SHI', 'MSP', 'TDS_mg_L'])
hyd_metric = st.sidebar.selectbox('Hydraulic performance metric', ['Mean_hf_m', 'Mean_HVI', 'Mean_SVI', 'Class_changes'])
clim_metric = st.sidebar.selectbox('Historical climate indicator', ['CSI', 'ET0_mm/month', 'Precip_mm/month', 'MPD', 'SPD3'])
future_metric = st.sidebar.selectbox('Future meteorological input', ['Tmean_C_Corrected', 'Precipitation_mm_month_Corrected', 'RH_percent_Corrected', 'Rs_MJ_m2_day_Corrected', 'Wind10m_ms_Corrected'])
scenario_choices = ['All configurations'] + scen.Scenario.astype(str).tolist()
scenario_choice = st.sidebar.selectbox('Pipeline configuration', scenario_choices)
show_sites = st.sidebar.checkbox('Show sampling sites on map', value=False)

filtered = summary[summary.Municipality.isin(selected)].copy()
site_data = merged[merged.Municipality.isin(selected)].copy()
scenario_data = scen if scenario_choice == 'All configurations' else scen[scen.Scenario.astype(str) == scenario_choice]

st.title('Qatar | Water Vulnerability Intelligence')
st.caption('Integrated geospatial, hydrochemical, hydraulic and climate analytics  •  Qatar  •  Groundwater baseline: 2020')

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric('Groundwater observations', len(site_data))
k2.metric('Municipalities in view', len(filtered))
k3.metric('Mean vulnerability index', f'{site_data.SVI.mean():.3f}' if not site_data.empty else '—')
k4.metric('Climate stress index · 2020', f'{gis.CSI_2020.mean():.3f}')
k5.metric('Pipeline configurations', len(scenario_data))

left, right = st.columns([1.22, 1], gap='large')
with left:
    st.subheader('01  |  Municipal vulnerability atlas')
    # Explicit feature IDs prevent ambiguity between GeoJSON properties and dataframe indexes.
    geo = boundaries.merge(filtered[['Municipality', 'n', map_metric]], on='Municipality', how='left')
    geo = geo.reset_index(drop=True)
    geo['map_id'] = geo.index.astype(str)
    geojson = geo.__geo_interface__
    fig_map = px.choropleth_map(
        geo, geojson=geojson, locations='map_id', featureidkey='properties.map_id',
        color=map_metric, hover_name='Municipality', hover_data={'n': True, map_metric: ':.3f', 'map_id': False},
        color_continuous_scale='YlOrRd', center={'lat': 25.35, 'lon': 51.2}, zoom=7.3,
        map_style='carto-positron', opacity=.70)
    if show_sites and not site_data.empty:
        fig_map.add_trace(go.Scattermap(lat=site_data.Latitude, lon=site_data.Longitude, mode='markers',
                                       marker={'size':5, 'color':'#1d4ed8'}, name='Groundwater sites',
                                       hovertext=site_data.Sample_ID.astype(str), hoverinfo='text'))
    fig_map.update_layout(height=420, margin=dict(l=0, r=0, t=0, b=0),
                          coloraxis_colorbar=dict(title=map_metric, thickness=12, len=.75))
    st.plotly_chart(fig_map, width='stretch', key='spatial_map')
    st.caption('Municipal index values aggregated from georeferenced observations; areas without data remain unclassified.')
with right:
    st.subheader('02  |  Municipality performance ranking')
    if filtered.empty:
        st.info('Select at least one municipality in the sidebar.')
    else:
        ranking = filtered.sort_values(map_metric, ascending=True)
        fig_rank = px.bar(ranking, x=map_metric, y='Municipality', orientation='h',
                          color=map_metric, color_continuous_scale='YlOrRd',
                          hover_data=['n', 'Coverage'])
        fig_rank.update_layout(height=420, margin=dict(l=5, r=5, t=10, b=5),
                               coloraxis_showscale=False, yaxis_title=None)
        st.plotly_chart(fig_rank, width='stretch', key='municipality_ranking')
        st.caption('Municipality comparisons include the number of observations to support coverage-aware interpretation.')

left, right = st.columns(2, gap='large')
with left:
    st.subheader('03  |  Hydrochemical risk profile')
    if site_data.empty:
        st.info('No sampling sites in selected municipalities.')
    else:
        fig_chem = px.histogram(site_data, x=chem_metric, nbins=25, color_discrete_sequence=['#157b9e'])
        fig_chem.update_layout(height=285, margin=dict(l=5, r=5, t=10, b=5), yaxis_title='Observations')
        st.plotly_chart(fig_chem, width='stretch', key='hydrochemistry')
        st.caption('Hydrochemical indices derived from the groundwater quality dataset (2020).')
with right:
    st.subheader('04  |  Hydraulic performance assessment')
    fig_hyd = px.bar(scenario_data, x='Scenario', y=hyd_metric, color='Alpha',
                     hover_data=['Pipe configuration', 'L_m', 'D_mm', 'Q_m3s'])
    fig_hyd.update_layout(height=285, margin=dict(l=5, r=5, t=10, b=5))
    st.plotly_chart(fig_hyd, width='stretch', key='hydraulic_scenarios')
    st.caption('Hydraulic performance calculated for the supplied pipeline configurations and engineering parameters.')

left, right = st.columns(2, gap='large')
with left:
    st.subheader('05  |  Hydroclimatic conditions · 2009–2025')
    fig_clim = px.line(climate, x='Date', y=clim_metric, color_discrete_sequence=['#147d94'])
    fig_clim.update_layout(height=285, margin=dict(l=5, r=5, t=10, b=5), xaxis_title=None)
    st.plotly_chart(fig_clim, width='stretch', key='historical_climate')
    st.caption('Monthly hydroclimatic indicators derived from the historical ERA5-Land dataset.')
with right:
    st.subheader('06  |  Climate outlook · 2031–2070')
    frames = []
    for key, df in future.items():
        part = df.copy()
        part['Scenario'] = 'SSP2-4.5' if key == 'ssp245' else 'SSP5-8.5'
        part['Date'] = pd.to_datetime(part['Date'])
        frames.append(part)
    future_plot = pd.concat(frames, ignore_index=True)
    # Annual aggregation keeps the 40-year comparison readable on a compact screen.
    future_plot['Year_plot'] = future_plot['Date'].dt.year
    aggregation = 'sum' if future_metric == 'Precipitation_mm_month_Corrected' else 'mean'
    annual = future_plot.groupby(['Year_plot', 'Scenario'], as_index=False)[future_metric].agg(aggregation)
    fig_future = px.line(annual, x='Year_plot', y=future_metric, color='Scenario',
                         color_discrete_map={'SSP2-4.5':'#2563eb', 'SSP5-8.5':'#e76f51'})
    fig_future.update_layout(height=285, margin=dict(l=5, r=5, t=10, b=5), xaxis_title='Year', legend_title=None)
    st.plotly_chart(fig_future, width='stretch', key='future_climate')
    st.caption(('Annual precipitation totals' if future_metric == 'Precipitation_mm_month_Corrected' else 'Annual means') + ' from bias-corrected ACCESS-CM2 meteorological projections.')

with st.expander('Municipal indicator register', expanded=False):
    st.dataframe(filtered.sort_values('SVI', ascending=False).round(3), hide_index=True, width='stretch')
with st.expander('Pipeline configuration details', expanded=False):
    st.dataframe(scenario_data.round(3), hide_index=True, width='stretch')
with st.expander('Methodology, data provenance and interpretation', expanded=False):
    st.markdown('''
**Data provenance and interpretation**

- **Hydrochemical baseline:** Groundwater chemistry and derived indicators are based on the supplied 2020 observations. These are not in-pipe drinking-water measurements.
- **Hydraulic assessment:** Head-loss and related indices are calculated from the supplied pipeline configurations and engineering input parameters; they are not measurements from an operating distribution network.
- **Climate outlook:** ACCESS-CM2 outputs represent bias-corrected meteorological projections. Future ET₀ and CSI are not calculated in this interface.
- **Geospatial coverage:** Municipality attribution uses the supplied GADM 4.1 boundaries (seven administrative polygons). Al Shahaniya is not represented separately.
- **Coverage and index interpretation:** Sample counts are displayed alongside municipal summaries. Locations with limited observations should not be assigned confident comparative priorities. Hydraulic indices may exceed the original baseline normalization bounds.
- **Update frequency:** Results are refreshed when source files are updated; the application is not connected to operational telemetry or utility control systems.

All charts are generated directly from the supplied data files, without substituting manuscript-derived values.
''')
    st.markdown('**Included Excel data sources**')
    for file in sorted(BASE.glob('*.xlsx')):
        st.markdown(f'- `{file.name}`')

st.divider()
st.caption('Qatar Municipal Water Vulnerability Intelligence  |  Integrated environmental and hydraulic assessment  |  Data provenance and methods available above')
