import streamlit as st
import pandas as pd
import plotly.express as px
from centerpoint_api import (
    fetch_service_data,
    fetch_invoices,
    fetch_companies,
    fetch_properties
)

st.set_page_config(page_title="Hustad Live Dashboard", layout="wide")

# Load all datasets
df_services = fetch_service_data()
df_invoices = fetch_invoices()
df_companies = fetch_companies()
df_properties = fetch_properties()

# Format key fields
df_services['openedAt'] = pd.to_datetime(df_services['openedAt'], errors='coerce')
df_services['opportunityType'] = df_services['opportunityType'].fillna("Unknown")
df_services['displayStatus'] = df_services['displayStatus'].fillna("Unknown")
df_services['domain'] = df_services['domain'].fillna("Unknown")
df_services['price'] = pd.to_numeric(df_services['price'], errors='coerce').fillna(0)

# Tabs layout
tab1, tab2, tab3, tab4 = st.tabs(["🛠️ Services", "🧾 Invoices", "🏢 Companies", "🏗️ Properties"])

with tab1:
    st.title("🛠️ Service Requests")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total", len(df_services))
    col2.metric("Backlog", df_services[df_services['displayStatus'] == 'Backlog'].shape[0])
    col3.metric("In Progress", df_services[df_services['displayStatus'] == 'In Progress'].shape[0])
    col4.metric("Quoted", f"${df_services['price'].sum():,.2f}")

    st.plotly_chart(px.bar(
        df_services['domain'].value_counts().reset_index().rename(columns={"index": "Domain", "domain": "Count"}),
        x='Domain', y='Count', title="Requests by Domain"
    ))

    st.subheader("📋 Full Service Data")
    st.dataframe(df_services)

with tab2:
    st.title("🧾 Invoices")
    st.write(f"Total Invoices: {len(df_invoices)}")
    st.dataframe(df_invoices)

with tab3:
    st.title("🏢 Companies")
    st.write(f"Total Companies: {len(df_companies)}")
    st.dataframe(df_companies)

with tab4:
    st.title("🏗️ Properties")
    st.write(f"Total Properties: {len(df_properties)}")
    st.dataframe(df_properties)

# API confirmation
st.sidebar.success(f"✅ Live API connected")
