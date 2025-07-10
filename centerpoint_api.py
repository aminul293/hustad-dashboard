# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from centerpoint_api import (
    fetch_service_data,
    fetch_invoices,
    fetch_companies,
    fetch_properties,
    fetch_employees,
    fetch_opportunities
)

st.set_page_config(page_title="📡 Hustad Core Dashboard", layout="wide")

# Load data from API
services_df = fetch_service_data()
invoices_df = fetch_invoices()
companies_df = fetch_companies()
properties_df = fetch_properties()
employees_df = fetch_employees()
opportunities_df = fetch_opportunities()

# Clean & format service data
services_df['openedAt'] = pd.to_datetime(services_df['openedAt'], errors='coerce')
services_df['opportunityType'] = services_df['opportunityType'].fillna("Unknown")
services_df['displayStatus'] = services_df['displayStatus'].fillna("Unknown")
services_df['domain'] = services_df['domain'].fillna("Unknown")
services_df['price'] = pd.to_numeric(services_df['price'], errors='coerce').fillna(0)

# Tabs for sections
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🛠 Services", "🧾 Invoices", "🏢 Companies", "🏗 Properties", "👥 Employees", "📈 Opportunities"])

with tab1:
    st.title("🛠 Services Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests", len(services_df))
    col2.metric("Backlog", services_df[services_df['displayStatus'] == 'Backlog'].shape[0])
    col3.metric("In Progress", services_df[services_df['displayStatus'] == 'In Progress'].shape[0])
    col4.metric("Total Quoted", f"${services_df['price'].sum():,.2f}")

    # Safe domain count plot
    domain_counts = services_df['domain'].value_counts().reset_index()
    domain_counts.columns = ['Domain', 'Count']

    if not domain_counts.empty:
        st.plotly_chart(px.bar(
            domain_counts,
            x='Domain', y='Count', title="Requests by Domain"
        ))
    else:
        st.info("No data available to display domain chart.")

    # Status pie chart
    status_counts = services_df['displayStatus'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']

    if not status_counts.empty:
        st.plotly_chart(px.pie(
            status_counts,
            names='Status',
            values='Count',
            title='Status Breakdown'
        ))

    with st.expander("📋 View Service Records"):
        st.dataframe(services_df.sort_values(by='openedAt', ascending=False), use_container_width=True)

with tab2:
    st.title("🧾 Invoices")
    st.write(f"Total Invoices: {len(invoices_df)}")
    st.dataframe(invoices_df, use_container_width=True)

with tab3:
    st.title("🏢 Companies")
    st.write(f"Total Companies: {len(companies_df)}")
    st.dataframe(companies_df, use_container_width=True)

with tab4:
    st.title("🏗 Properties")
    st.write(f"Total Properties: {len(properties_df)}")
    st.dataframe(properties_df, use_container_width=True)

with tab5:
    st.title("👥 Employees")
    st.write(f"Total Employees: {len(employees_df)}")
    st.dataframe(employees_df, use_container_width=True)

with tab6:
    st.title("📈 Opportunities")
    st.write(f"Total Opportunities: {len(opportunities_df)}")
    st.dataframe(opportunities_df, use_container_width=True)

# API success
st.sidebar.success("✅ Live API Connected")
