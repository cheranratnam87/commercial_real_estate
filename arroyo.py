import folium
from fastkml import kml
from shapely.geometry import shape
import streamlit as st
from streamlit_folium import st_folium
import requests

# URL to your KML file
kml_url = "https://raw.githubusercontent.com/cheranratnam87/commercial_real_estate/refs/heads/main/4901%20Arroyo%20Trail%20Comps.kml?token=GHSAT0AAAAAACXBZ732CQNPEJFILZWKNDZ2ZYEWMWQ"

# Streamlit title and description
st.title("Business and Healthcare Visualization Around 4901 Arroyo Trail, McKinney, Texas")
st.write("This map visualizes businesses, healthcare facilities, and other locations around 4901 Arroyo Trail using categorized icons.")

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
