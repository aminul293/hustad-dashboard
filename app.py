import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Hustad Sales & Service Dashboard", layout="wide")

# Load CSV (local fallback sample)
@st.cache_data
def load_data():
    df = pd.read_csv("service-4-2025-07-09.csv")
    df.columns = df.columns.str.strip()  # clean column names
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    df['Sale Price'] = pd.to_numeric(df['Sale Price'], errors='coerce').fillna(0)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔎 Filter Data")
type_filter = st.sidebar.multiselect("Type", options=df['Type'].dropna().unique())
service_type_filter = st.sidebar.multiselect("Service Type", options=df['Service Type - Hustad'].dropna().unique())
stage_filter = st.sidebar.multiselect("Stage", options=df['Stage'].dropna().unique())
date_range = st.sidebar.date_input("Created Date Range", [])

# Apply filters
filtered_df = df.copy()

if type_filter:
    filtered_df = filtered_df[filtered_df['Type'].isin(type_filter)]

if service_type_filter:
    filtered_df = filtered_df[filtered_df['Service Type - Hustad'].isin(service_type_filter)]

if stage_filter:
    filtered_df = filtered_df[filtered_df['Stage'].isin(stage_filter)]

if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df['Created Date'] >= start) & (filtered_df['Created Date'] <= end)
    ]

# KPIs
st.title("🚀 Hustad Sales & Service Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(filtered_df))
col2.metric("Scheduled", filtered_df[filtered_df['Stage'] == 'Scheduled'].shape[0])
col3.metric("In Progress", filtered_df[filtered_df['Stage'] == 'In Progress'].shape[0])
col4.metric("Total Sale Value", f"${filtered_df['Sale Price'].sum():,.2f}")

# Charts
st.subheader("📊 Requests by Type")
type_counts = filtered_df['Type'].value_counts().reset_index()
type_counts.columns = ['Type', 'Count']
st.plotly_chart(px.bar(type_counts, x='Type', y='Count', title='Service Requests by Type'))

st.subheader("📌 Requests by Stage")
stage_counts = filtered_df['Stage'].value_counts().reset_index()
stage_counts.columns = ['Stage', 'Count']
st.plotly_chart(px.pie(stage_counts, names='Stage', values='Count', title='Stage Distribution'))

# Download
st.subheader("⬇️ Download Filtered CSV")
st.download_button("Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_service_data.csv")

# Raw Data View
with st.expander("📋 View Raw Data"):
    st.dataframe(filtered_df)
