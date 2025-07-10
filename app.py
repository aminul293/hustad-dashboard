# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="📋 Service List from Centerpoint API", layout="wide")

# Load data
@st.cache_data
def load_data():
    return fetch_service_data()

df = load_data()

# Convert Opened At to datetime early
if "Opened At" in df.columns:
    df["Opened At"] = pd.to_datetime(df["Opened At"], errors="coerce")

# Display title and shape
st.title("📋 Service List from Centerpoint API")
st.success(f"✅ Fetched Data Shape: {df.shape}")

# Show columns
st.subheader("📋 Columns:")
st.code(df.columns.tolist())

# Date filter
date_range = st.date_input("📅 Filter by Opened Date Range", [])
filtered_df = df.copy()

if len(date_range) == 2 and "Opened At" in df.columns:
    start = pd.to_datetime(date_range[0])
    end = pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df["Opened At"] >= start) &
        (filtered_df["Opened At"] <= end)
    ]

# Select columns to display if they exist
columns_to_display = [
    "Ticket ID", "Description", "Company", "Property", "Manager", "Status",
    "Type", "Opened At", "Price"
]
missing = [col for col in columns_to_display if col not in df.columns]

if missing:
    st.warning("⚠️ Some expected columns are missing. Showing full raw table.")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.dataframe(filtered_df[columns_to_display].sort_values(by="Opened At", ascending=False), use_container_width=True)
