import streamlit as st
import pandas as pd
import plotly.express as px
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="Hustad Sales & Service Dashboard", layout="wide")

# Load from API
df = fetch_service_data()

# Clean column values
df['opportunityType'] = df['opportunityType'].fillna("Unknown")
df['type'] = df['type'].fillna("Unknown")
df['domain'] = df['domain'].fillna("Unknown")
df['openedAt'] = pd.to_datetime(df['openedAt'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)

# Sidebar filters
st.sidebar.header("🔎 Filter Data")
rep = st.sidebar.multiselect("Opportunity Type", options=df['opportunityType'].dropna().unique())
status = st.sidebar.multiselect("Status", options=df['displayStatus'].dropna().unique())
domain = st.sidebar.multiselect("Domain", options=df['domain'].dropna().unique())
date_range = st.sidebar.date_input("Opened Date Range", [])

# Apply filters
filtered_df = df.copy()

if rep:
    filtered_df = filtered_df[filtered_df['opportunityType'].isin(rep)]

if status:
    filtered_df = filtered_df[filtered_df['displayStatus'].isin(status)]

if domain:
    filtered_df = filtered_df[filtered_df['domain'].isin(domain)]

if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df['openedAt'] >= start) & (filtered_df['openedAt'] <= end)
    ]

# KPI Summary
st.title("🚀 Hustad Sales & Service Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(filtered_df))
col2.metric("Backlog", filtered_df[filtered_df['displayStatus'] == 'Backlog'].shape[0])
col3.metric("In Progress", filtered_df[filtered_df['displayStatus'] == 'In Progress'].shape[0])
col4.metric("Total Quoted Amount", f"${filtered_df['price'].sum():,.2f}")

# Opportunity Type Chart
st.subheader("📊 Requests by Opportunity Type")
opptype_counts = filtered_df['opportunityType'].value_counts().reset_index()
opptype_counts.columns = ['Opportunity Type', 'Count']
st.plotly_chart(px.bar(
    opptype_counts,
    x='Opportunity Type',
    y='Count',
    labels={'Opportunity Type': 'Type', 'Count': 'Count'},
    title='Request Volume by Type'
))

# Status Chart
st.subheader("📌 Requests by Status")
status_counts = filtered_df['displayStatus'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']
st.plotly_chart(px.pie(
    status_counts,
    names='Status',
    values='Count',
    title='Service Request Status Breakdown'
))

# Domain Chart
st.subheader("🏷️ Requests by Domain")
domain_counts = filtered_df['domain'].value_counts().reset_index()
domain_counts.columns = ['Domain', 'Count']
st.plotly_chart(px.bar(
    domain_counts,
    x='Domain',
    y='Count',
    title='Requests by Domain'
))

# Download
st.subheader("⬇️ Download Filtered Data")
st.download_button("Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_requests.csv")

# Show Data Table
with st.expander("📋 View Data"):
    st.dataframe(filtered_df.sort_values(by='openedAt', ascending=False), use_container_width=True)

# API Status Badge
st.caption(f"✅ Connected to Centerpoint API · {len(df)} records loaded")
