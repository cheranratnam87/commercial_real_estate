import folium
from fastkml import kml
from shapely.geometry import shape
import streamlit as st
from streamlit_folium import st_folium
import requests
import pandas as pd
import plotly.express as px

# Custom CSS to reduce padding and space
st.markdown("""
    <style>
    div.block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit title and description
st.title("Business and Healthcare Visualization Around 4901 Arroyo Trail, McKinney, Texas")
st.write("This dashboard visualizes businesses, healthcare facilities, and other locations around 4901 Arroyo Trail using categorized icons, along with NAICS categorization and demographic insights.")

### NAICS Categorization Section (First Visual) ###
@st.cache
def load_data(url):
    return pd.read_csv(url)

naics_url = "https://raw.githubusercontent.com/cheranratnam87/commercial_real_estate/refs/heads/main/filtered_data.csv"
naics_data = load_data(naics_url)

# Show all categories including 'Other'
category_count = naics_data['NAICS2017_LABEL'].value_counts().reset_index()
category_count.columns = ['Category', 'Count']

# Button to show "Other" listings
show_other_listings = st.button("Show listings under 'Other'")

if show_other_listings:
    st.subheader("Businesses Listed Under 'Other'")
    other_listings = naics_data[naics_data['NAICS2017_LABEL'] == 'Other']
    st.dataframe(other_listings)

# Create a bar chart of categories including "Other"
st.subheader("NAICS Categorization of Businesses (Including 'Other')")
fig4 = px.bar(
    category_count,
    x='Category',
    y='Count',
    labels={'Count': 'Number of Businesses', 'Category': 'Business Category'},
    title="Distribution of Businesses by Category (Including 'Other')"
)
st.plotly_chart(fig4)

### Map Visualization Section (Second Visual) ###
# URL to your KML file
kml_url = "https://raw.githubusercontent.com/cheranratnam87/commercial_real_estate/refs/heads/main/4901%20Arroyo%20Trail%20Comps.kml"

# Fetch the KML file content from the URL
response = requests.get(kml_url)
doc = response.content

# Parse the KML file
k = kml.KML()
k.from_string(doc)

# A function to recursively extract all placemarks
def extract_placemarks(features):
    placemarks = []
    for feature in features:
        if hasattr(feature, 'geometry') and feature.geometry is not None:
            placemarks.append(feature)
        elif hasattr(feature, 'features'):
            placemarks.extend(extract_placemarks(feature.features()))
    return placemarks

# Extract all placemarks
placemarks = extract_placemarks(k.features())

# Ensure there is at least one placemark to center the map
if placemarks:
    first_geom = shape(placemarks[0].geometry)
    map_center = [first_geom.centroid.y, first_geom.centroid.x]
else:
    # If no placemarks, set a default center
    map_center = [33.152685, -96.7242727]  # Centering around Arroyo Trail

# Create a folium map centered around the first coordinate
map_visualization = folium.Map(location=map_center, zoom_start=15)

# Define a mapping of keywords to category and icon
category_icon_mapping = {
    'kids': {
        'keywords': ['day care', 'learning', 'child', 'crème learning', 'kids', 'preschool', 'kindercare', 'montessori', 'school', 'academy', 'education', 'college', 'university', 'guidepost montessori at craig ranch', 'kiddie kollege'],
        'icon': 'child'
    },
    'medical': {
        'keywords': ['medical', 'primary care', 'medicine', 'clinic', 'wellness', 'health', 'doctor', 'pharmacy', 'family medicine', 'healthcare', 'physician', 'dentist', 'dental', 'urgent care', 'mental health', 'therapy', 'orthopedic', 'dermatology', 'pediatrics', 'optical', 'hospital', 'baylor scott & white', 'village medical', 'passion health'],
        'icon': 'heartbeat'
    },
    'office': {
        'keywords': ['office', 'corporate', 'workspace', 'business center'],
        'icon': 'building'
    },
    'grocery/retail': {
        'keywords': ['grocery', 'supermarket', 'retail'],
        'icon': 'shopping-cart'
    },
    'community': {
        'keywords': ['community', 'master-planned community', 'neighborhood'],
        'icon': 'home'
    },
    'construction': {
        'keywords': ['construction', 'development', 'cell tower', 'potential new construction'],
        'icon': 'wrench'
    },
}

# Add placemarks to the map with categorized icons
for placemark in placemarks:
    geom = shape(placemark.geometry)
    placemark_name = placemark.name.lower()

    # Check for the main location: "4901 Arroyo Trail"
    if "4901 arroyo trail" in placemark_name:
        folium.Marker(
            location=[geom.centroid.y, geom.centroid.x],
            popup=placemark.name,
            icon=folium.Icon(icon='usd', prefix='fa', color='red')  # Sale sign icon with 'usd' symbol and red color
        ).add_to(map_visualization)
        continue

    # Default icon if no category matches
    icon_type = 'info-sign'

    # Determine the category and icon based on keywords
    categorized = False
    for category, info in category_icon_mapping.items():
        keywords = [keyword.lower() for keyword in info['keywords']]  # Ensure all keywords are lowercase
        icon = info['icon']
        # Check if any keyword matches the placemark name (case-insensitive)
        if any(keyword in placemark_name for keyword in keywords):
            icon_type = icon
            categorized = True
            break

    # Add the marker with a corresponding icon
    folium.Marker(
        location=[geom.centroid.y, geom.centroid.x],
        popup=placemark.name,
        icon=folium.Icon(icon=icon_type, prefix='fa')  # 'fa' for Font Awesome icons
    ).add_to(map_visualization)

# Display the map in the Streamlit app using st_folium
st_folium(map_visualization, width=700, height=500)

### Demographic Data Section (Third Visual) ###
# Creating the demographic DataFrame
data = {
    "Radius": ["1 Mile", "3 Mile", "5 Mile"],
    "2024 Population": [17525, 137712, 349375],
    "2029 Projected Population": [21613, 169353, 426989],
    "Growth 2024-2029 (%)": [23.33, 22.98, 22.22],
    "Median Age": [36.8, 37.1, 38.3],
    "Average Age": [35.4, 35.4, 36.7],
    "Average Household Income ($)": [139537, 160307, 156846],
    "Median Household Income ($)": [110234, 130858, 130229],
    "Median Home Value ($)": [421909, 474010, 442683],
    "Households 2024": [6232, 45995, 118665],
    "Households 2029": [7711, 56666, 145322],
    "Household Growth 2024-2029 (%)": [23.73, 23.2, 22.46],
    "Owner Occupied (%)": [59.56, 67.86, 67.45],
    "Renter Occupied (%)": [40.44, 32.14, 32.55]
}

# Convert to DataFrame
demographic_df = pd.DataFrame(data)

# Display the DataFrame as a table in Streamlit
st.subheader("Demographic Data (2024-2029)")
st.dataframe(demographic_df)

# Create an interactive line plot for Population Growth
st.subheader("Projected Population Growth (2024-2029)")
fig1 = px.line(
    demographic_df,
    x="Radius",
    y=["2024 Population", "2029 Projected Population"],
    labels={"value": "Population", "variable": "Year"},
    title="Projected Population Growth in Different Radii"
)
fig1.update_layout(legend_title_text="Population")
st.plotly_chart(fig1)

# Create an interactive bar plot for Household Growth
st.subheader("Household Growth (2024-2029)")
fig2 = px.bar(
    demographic_df,
    x="Radius",
    y=["Households 2024", "Households 2029"],
    barmode="group",
    labels={"value": "Households", "variable": "Year"},
    title="Household Growth in Different Radii"
)
fig2.update_layout(legend_title_text="Households")
st.plotly_chart(fig2)

# Create an interactive bar plot for Median and Average Household Income
st.subheader("Household Income Levels (2024)")
fig3 = px.bar(
    demographic_df,
    x="Radius",
    y=["Median Household Income ($)", "Average Household Income ($)"],
    barmode="group",
    labels={"value": "Income ($)", "variable": "Income Type"},
    title="Household Income Levels in Different Radii"
)
fig3.update_layout(legend_title_text="Income Type")
st.plotly_chart(fig3)
