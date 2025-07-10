import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="📋 Service List from Centerpoint API", layout="wide")

# Load data from API
df = fetch_service_data()

# Rename columns for display if they exist
column_renames = {
    "name": "Ticket ID",
    "description": "Description",
    "Company": "Company",
    "Property": "Property",
    "Manager": "Manager",
    "displayStatus": "Status",
    "type": "Type",
    "openedAt": "Opened At",
    "price": "Price"
}
df.rename(columns=column_renames, inplace=True)

# Ensure 'Opened At' is in datetime format if it exists
if 'Opened At' in df.columns:
    df['Opened At'] = pd.to_datetime(df['Opened At'], errors='coerce')

# Sidebar filter for date range
date_range = st.sidebar.date_input("📅 Opened Date Range", [])

# Filter by date if applicable
filtered_df = df.copy()
if 'Opened At' in df.columns and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask = filtered_df['Opened At'].notna()
    filtered_df = filtered_df[mask & (filtered_df['Opened At'] >= start) & (filtered_df['Opened At'] <= end)]

# Display title and summary
st.title("📋 Service List from Centerpoint API")
st.success(f"✅ Fetched Data Shape: {filtered_df.shape}")

# Show column names
st.subheader("📋 Columns:")
st.code(list(filtered_df.columns))

# Display table
st.dataframe(filtered_df.sort_values(by='Opened At', ascending=False) if 'Opened At' in filtered_df.columns else filtered_df, use_container_width=True)
