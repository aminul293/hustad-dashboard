# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="🛠 Hustad Live Services Dashboard", layout="wide")

# Load and clean data
services_df = fetch_service_data()
services_df['openedAt'] = pd.to_datetime(services_df['openedAt'], errors='coerce')
services_df['opportunityType'] = services_df['opportunityType'].fillna("Unknown")
services_df['displayStatus'] = services_df['displayStatus'].fillna("Unknown")
services_df['domain'] = services_df['domain'].fillna("Unknown")
services_df['price'] = pd.to_numeric(services_df['price'], errors='coerce').fillna(0)

# KPIs
st.title("🛠 Service Requests Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(services_df))
col2.metric("Backlog", services_df[services_df['displayStatus'] == 'Backlog'].shape[0])
col3.metric("In Progress", services_df[services_df['displayStatus'] == 'In Progress'].shape[0])
col4.metric("Total Quoted", f"${services_df['price'].sum():,.2f}")

# Chart: Requests by Domain
domain_counts = services_df['domain'].value_counts().reset_index()
domain_counts.columns = ['Domain', 'Count']
if not domain_counts.empty:
    st.plotly_chart(px.bar(
        domain_counts, x='Domain', y='Count', title="Requests by Domain"
    ))
else:
    st.info("No data available for domain chart.")

# Chart: Opportunity Type
opptype_counts = services_df['opportunityType'].value_counts().reset_index()
opptype_counts.columns = ['Opportunity Type', 'Count']
if not opptype_counts.empty:
    st.plotly_chart(px.bar(
        opptype_counts, x='Opportunity Type', y='Count', title="Requests by Opportunity Type"
    ))

# Chart: Status Breakdown
status_counts = services_df['displayStatus'].value_counts().reset_index()
status_counts.columns = ['Status', 'Count']
if not status_counts.empty:
    st.plotly_chart(px.pie(
        status_counts, names='Status', values='Count', title='Status Breakdown'
    ))

# Data table
with st.expander("📋 View Raw Data"):
    st.dataframe(services_df.sort_values(by='openedAt', ascending=False), use_container_width=True)

# API status
st.sidebar.success("✅ Live API Connected: /services")
