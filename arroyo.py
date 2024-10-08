import streamlit as st
import pandas as pd

# Load the data
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

# NAICS data URL
naics_url = "https://raw.githubusercontent.com/cheranratnam87/commercial_real_estate/refs/heads/main/filtered_data.csv"
naics_data = load_data(naics_url)

# Filters for Business Categories and Employment Sizes
selected_category = st.multiselect(
    'Select Business Categories',
    options=naics_data['NAICS2017_LABEL'].unique(),
    default=naics_data['NAICS2017_LABEL'].unique()
)

selected_emp_size = st.selectbox(
    'Select Employment Size Category',
    options=naics_data['EMPSZES_LABEL'].unique()
)

# Filter the data based on user selections
filtered_data = naics_data[
    (naics_data['NAICS2017_LABEL'].isin(selected_category)) &
    (naics_data['EMPSZES_LABEL'] == selected_emp_size)
]
import folium
from folium.plugins import MarkerCluster

# Create a folium map centered around McKinney, Texas
map_visualization = folium.Map(location=[33.1959, -96.6989], zoom_start=12)

# Add marker clusters to the map
marker_cluster = MarkerCluster().add_to(map_visualization)

# Add custom markers with tooltips and icons
for index, row in filtered_data.iterrows():
    tooltip = f"{row['NAICS2017_LABEL']} - {row['EMPSZES_LABEL']} Employees"
    icon_type = 'info-sign'  # Default icon

    # Customize icon based on category
    if 'Healthcare' in row['NAICS2017_LABEL']:
        icon_type = 'heartbeat'
    elif 'Retail' in row['NAICS2017_LABEL']:
        icon_type = 'shopping-cart'
    elif 'Construction' in row['NAICS2017_LABEL']:
        icon_type = 'wrench'

    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=row['NAICS2017_LABEL'],
        icon=folium.Icon(icon=icon_type, prefix='fa'),
        tooltip=tooltip
    ).add_to(marker_cluster)

# Display the map in Streamlit
st_data = st_folium(map_visualization, width=700, height=500)

import json
import requests

# Load the GeoJSON data (use the correct URL for the file)
geojson_url = "path_to_geojson_file.geojson"
geo_data = json.loads(requests.get(geojson_url).text)

# Create a choropleth map
folium.Choropleth(
    geo_data=geo_data,
    name="choropleth",
    data=filtered_data,
    columns=["ZIPCODE", "ESTAB"],  # You can change 'ESTAB' to 'PAYANN' for payroll
    key_on="feature.properties.ZIPCODE",  # Update based on the GeoJSON properties
    fill_color="YlGn",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Number of Establishments"
).add_to(map_visualization)

# Add layer control
folium.LayerControl().add_to(map_visualization)

# Display the updated map
st_folium(map_visualization, width=700, height=500)

# Bubble chart for payroll and number of employees
st.subheader("Bubble Chart for Number of Employees and Payroll")

fig = px.scatter(
    filtered_data,
    x='PAYANN',  # Annual payroll
    y='EMP',  # Number of employees
    size='ESTAB',  # Establishment count controls bubble size
    color='NAICS2017_LABEL',
    hover_name='NAICS2017_LABEL',
    size_max=60,
    title="Bubble Chart of Payroll vs Number of Employees"
)
st.plotly_chart(fig)

