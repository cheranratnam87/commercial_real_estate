import folium
from fastkml import kml
from shapely.geometry import shape
import streamlit as st
from streamlit_folium import st_folium
import requests
import pandas as pd
import plotly.express as px

# Custom CSS to reduce padding and space between visuals
st.markdown("""
    <style>
    div.block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    .element-container { 
        margin-bottom: 0rem !important; 
        padding-bottom: 0rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
# Define the categorize_naics function here
def categorize_naics(label):
    # Convert label to lowercase for easier matching
    label = label.lower()
    
    # Define broader keyword lists for categorizing
    healthcare_keywords = ['health', 'dental', 'dentists', 'medical', 'hospital', 'clinic', 'nursing', 'chiropractors', 'optometrists', 'physicians', 'therapists', 'diagnostic']
    financial_keywords = ['finance', 'lending', 'credit', 'bank', 'insurance', 'investment', 'securities', 'brokerage', 'accountants','mortgage', 'tax','portfolio', 'intermediation']
    food_keywords = ['food', 'restaurant', 'eating', 'cafe', 'catering', 'bakery', 'beverage', 'snack', 'caterers']
    automotive_keywords = ['auto', 'car', 'vehicle', 'motor', 'automobile', 'garage', 'tire', 'parts']
    manufacturing_keywords = ['manufacturing', 'factory', 'production', 'assembly', 'printing']
    retail_keywords = ['retail', 'store', 'shop', 'outlet', 'mall', 'center', 'warehouse', 'home centers', 'supercenters', 'gasoline']
    construction_keywords = ['construction', 'building', 'contractor', 'remodeler', 'oil and gas']
    wholesale_keywords = ['wholesale', 'distributor', 'merchant']
    transportation_keywords = ['transportation', 'logistics', 'trucking', 'freight', 'warehousing']
    information_keywords = ['publishing', 'software', 'telecom', 'data processing', 'information', 'motion picture', 'sound recording']
    real_estate_keywords = ['real estate', 'leasing', 'property', 'lessors', 'rental', 'warehouses']
    education_keywords = ['school', 'education', 'tutoring', 'training', 'instruction']
    entertainment_keywords = ['arts', 'entertainment', 'recreation', 'sports', 'club', 'golf', 'independent artist', 'writers', 'performers']
    accommodation_keywords = ['hotel', 'motel', 'accommodation', 'lodging', 'caterers']
    repair_keywords = ['repair', 'maintenance', 'car wash', 'laundry', 'janitorial']
    personal_services_keywords = ['personal care', 'salon', 'barber', 'weight reducing', 'landscaping', 'photographic', 'veterinary']
    social_assistance_keywords = ['social assistance', 'family services', 'elderly', 'grantmaking', 'civic', 'professional organizations', 'religious']
    professional_services_keywords = ['legal', 'lawyer', 'accounting', 'consulting', 'design', 'scientific', 'technical', 'management', 'advertising', 'security', 'administrative', 'waste management', 'business support', 'employment', 'photography']
    
    # Match each label against keywords for categorization
    if any(keyword in label for keyword in healthcare_keywords):
        return 'Healthcare'
    elif any(keyword in label for keyword in financial_keywords):
        return 'Financial Services'
    elif any(keyword in label for keyword in food_keywords):
        return 'Food Services and Accommodation'
    elif any(keyword in label for keyword in automotive_keywords):
        return 'Automotive Services'
    elif any(keyword in label for keyword in manufacturing_keywords):
        return 'Manufacturing'
    elif any(keyword in label for keyword in retail_keywords):
        return 'Retail Trade'
    elif any(keyword in label for keyword in construction_keywords):
        return 'Construction'
    elif any(keyword in label for keyword in wholesale_keywords):
        return 'Wholesale Trade'
    elif any(keyword in label for keyword in transportation_keywords):
        return 'Transportation and Warehousing'
    elif any(keyword in label for keyword in information_keywords):
        return 'Information Technology and Media'
    elif any(keyword in label for keyword in real_estate_keywords):
        return 'Real Estate and Leasing'
    elif any(keyword in label for keyword in education_keywords):
        return 'Educational Services'
    elif any(keyword in label for keyword in entertainment_keywords):
        return 'Arts, Entertainment, and Recreation'
    elif any(keyword in label for keyword in accommodation_keywords):
        return 'Accommodation and Food Services'
    elif any(keyword in label for keyword in repair_keywords):
        return 'Repair and Maintenance'
    elif any(keyword in label for keyword in personal_services_keywords):
        return 'Personal and Laundry Services'
    elif any(keyword in label for keyword in social_assistance_keywords):
        return 'Social Assistance and Organizations'
    elif any(keyword in label for keyword in professional_services_keywords):
        return 'Professional, Scientific, and Technical Services'
    # 'Total for all sectors' should be categorized separately if needed
    elif 'total for all sectors' in label:
        return 'All Sectors'
    else:
        return 'Other'

# Streamlit title and description
st.title("Business and Healthcare Visualization Around 4901 Arroyo Trail, McKinney, Texas")
st.write("This dashboard visualizes businesses, healthcare facilities, and other locations around 4901 Arroyo Trail using categorized icons, along with NAICS categorization and demographic insights.")

### Map Visualization Section (First Visual) ###
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
    for category, info in category_icon_mapping.items():
        keywords = [keyword.lower() for keyword in info['keywords']]  # Ensure all keywords are lowercase
        icon = info['icon']
        # Check if any keyword matches the placemark name (case-insensitive)
        if any(keyword in placemark_name for keyword in keywords):
            icon_type = icon
            break

    # Add the marker with a corresponding icon
    folium.Marker(
        location=[geom.centroid.y, geom.centroid.x],
        popup=placemark.name,
        icon=folium.Icon(icon=icon_type, prefix='fa')  # 'fa' for Font Awesome icons
    ).add_to(map_visualization)

# Display the map in the Streamlit app using st_folium
st_folium(map_visualization, width=700, height=500)


### NAICS Categorization Section (Second Visual) ###
### NAICS Categorization Section (Second Visual) ###
### NAICS Categorization Section (Second Visual) ###
### NAICS Categorization Section (Second Visual) ###
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

naics_url = "https://raw.githubusercontent.com/cheranratnam87/commercial_real_estate/refs/heads/main/filtered_data.csv"
naics_data = load_data(naics_url)

# Show all categories including 'Other'
category_count = naics_data['NAICS2017_LABEL'].value_counts().reset_index()
category_count.columns = ['Category', 'Count']

# Create a horizontal bar chart of all categories including 'Other'
st.subheader("75070 zip Categorization of Businesses (Including All Categories)")
fig4 = px.bar(
    category_count,
    x='Count',
    y='Category',  # Swap x and y to make it horizontal
    labels={'Count': 'Number of Businesses', 'Category': 'Business Category'},
    title="Distribution of Businesses by Category (Including All Categories)",
    orientation='h'  # Set orientation to horizontal
)

# Display the plot
st.plotly_chart(fig4)



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
