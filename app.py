# app.py

import streamlit as st

st.set_page_config(
    page_title="Hustad AI Workflow & Automation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Hustad AI Workflow & Automation Dashboard")

st.markdown("""
Welcome to the **Executive Dashboard**.

Use the sidebar to explore:
- Financials
- Sales Intelligence
- Labor Productivity
- Clients, Vendors, HR
- Trends, ROI, and more.
""")

# Optional overview KPIs
col1, col2, col3 = st.columns(3)
col1.metric("📈 Total Revenue", "$1.25M")
col2.metric("🧾 Open Invoices", "42")
col3.metric("✅ Avg. Client ROI", "19.6%")
