import streamlit as st
import pandas as pd
import plotly.express as px
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="Hustad Sales & Service Dashboard", layout="wide")

# Load data from API
df = fetch_service_data()

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

# Always ensure openedAt is datetime for safe filtering
filtered_df['openedAt'] = pd.to_datetime(filtered_df['openedAt'], errors='coerce')

if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[
        (filtered_df['openedAt'] >= start) & (filtered_df['openedAt'] <= end)
    ]

# KPIs
st.title("🚀 Hustad Sales & Service Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(filtered_df))
col2.metric("Backlog", filtered_df[filtered_df['displayStatus'] == 'Backlog'].shape[0])
col3.metric("In Progress", filtered_df[filtered_df['displayStatus'] == 'In Progress'].shape[0])
col4.metric("Total Quoted Amount", f"${filtered_df['price'].sum():,.2f}")

# Charts
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

st.subheader("📌 Requests by Status")
status_counts = filtered_df['displayStatus'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']
st.plotly_chart(px.pie(
    status_counts,
    names='Status',
    values='Count',
    title='Service Request Status Breakdown'
))

# Download filtered data
st.subheader("⬇️ Download Filtered CSV")
st.download_button("Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_requests.csv")
