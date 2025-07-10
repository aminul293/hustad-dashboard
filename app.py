# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="📋 Service List from Centerpoint API", layout="wide")

# Load data from API
df = fetch_service_data()

# Convert 'Opened At' column to datetime for filtering
if "Opened At" in df.columns:
    df["Opened At"] = pd.to_datetime(df["Opened At"], errors="coerce")

# Sidebar filters
st.sidebar.header("🔎 Filter Data")
date_range = st.sidebar.date_input("Opened Date Range", [])

filtered_df = df.copy()
if date_range and len(date_range) == 2:
    start = pd.to_datetime(date_range[0])
    end = pd.to_datetime(date_range[1])
    if "Opened At" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["Opened At"] >= start) & (filtered_df["Opened At"] <= end)
        ]

# Display API status
st.markdown("""
    ## 📋 Service List from Centerpoint API
    ✅ Fetched Data Shape: {0}
""".format(filtered_df.shape))

# Show columns
st.markdown("### 📋 Columns:")
st.code(list(filtered_df.columns))

# Show cleaned table
expected_columns = [
    "Ticket ID", "Description", "Company", "Property",
    "Manager", "Status", "Type", "Opened At", "Price"
]
if all(col in filtered_df.columns for col in expected_columns):
    st.dataframe(filtered_df[expected_columns].sort_values(by="Opened At", ascending=False))
else:
    st.warning("⚠️ Some expected columns are missing. Showing full raw table.")
    st.dataframe(filtered_df.sort_values(by=filtered_df.columns[0], ascending=False))
