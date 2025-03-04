import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
import os
import json
from google.cloud import bigquery
from google.oauth2 import service_account

# Check if the secret is available in the environment variables (Streamlit Cloud loads them automatically)
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if creds_json:
    # Parse the JSON credentials from the environment variable
    service_account_info = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    client = bigquery.Client(credentials=credentials, project=service_account_info["homework1-452207"])
else:
    # Fallback for local development if credentials file exists locally
    client = bigquery.Client(project="homework1-452207")

@st.cache(ttl=600)
def load_data(query):
    return client.query(query).to_dataframe()

query = """
SELECT *
FROM `homework1-452207.san_jose_data.san_jose_data_fire_incident`
"""
df = load_data(query)

st.title("San Jose Fire Incident Dashboard")
st.write("Explore the fire incident data with interactive filters and visualizations.")

incident_types = df['Final_Incident_Type'].unique()
selected_type = st.selectbox("Select an Incident Type", incident_types)
filtered_df = df[df['Final_Incident_Type'] == selected_type]

st.subheader("Filtered Data")
st.dataframe(filtered_df.head())

station_counts = filtered_df.groupby('Station').size().reset_index(name='count')
fig_bar = px.bar(station_counts, x='Station', y='count',
                 title="Incident Counts by Station")
st.plotly_chart(fig_bar)

filtered_df['Date_Time_Of_Event'] = pd.to_datetime(filtered_df['Date_Time_Of_Event'], errors='coerce')
filtered_df['day'] = filtered_df['Date_Time_Of_Event'].dt.date
daily_counts = filtered_df.groupby('day').size().reset_index(name='count')
fig_line = px.line(daily_counts, x='day', y='count', markers=True,
                   title="Daily Incident Trends")
st.plotly_chart(fig_line)

query1 = """
SELECT *
FROM `homework1-452207.san_jose_data.top_10_streets`
"""
df1 = load_data(query1)

if 'lat' in df1.columns and 'lon' in df1.columns:
    fig_map = px.scatter_mapbox(
        df1,
        lat="lat",
        lon="lon",
        hover_name="Street_Name",
        hover_data=["incident_count"],
        color="incident_count",
        size="incident_count",
        size_max=25,
        color_continuous_scale="Viridis",
        zoom=10,
        height=700,
        title="Incident Locations in San Jose"
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map)
else:
    st.write("No geocoded data available for map view.")


st.write("This dashboard pulls data from BigQuery and updates interactively based on your selections.")
