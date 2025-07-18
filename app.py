import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
from streamlit.errors import StreamlitAPIException

# --- API CONFIG ---
BASE_URL = "https://api.centerpointconnect.io/centerpoint"
HEADERS = {
    "Authorization": st.secrets["centerpoint"]["api_key"],
    "Accept": "application/json"
}

@st.cache_data
def fetch_opportunities():
    url = f"{BASE_URL}/opportunities?include=accountManager,billedCompany,property"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return pd.json_normalize(res.json().get("data", []))
    except Exception as e:
        st.warning(f"Failed to fetch opportunities: {e}")
        return pd.DataFrame()

# --- Streamlit App Setup ---
st.set_page_config(page_title="\U0001F4CA Opportunity Management Dashboard", layout="wide")
st.title("\U0001F4CA Opportunity Management Dashboard")
st.markdown("Track service opportunities, performance trends, and pipeline insights from CenterPoint.")

with st.spinner("Loading opportunity data..."):
    df = fetch_opportunities()

if not df.empty:
    st.sidebar.header("\U0001F50E Filter Opportunities")

    # Basic cleanup & parsing
    df['Created Date'] = pd.to_datetime(df['attributes.createdAt'], errors='coerce')
    df['Closed Date'] = pd.to_datetime(df['attributes.closedAt'], errors='coerce')
    df['Status'] = df['attributes.displayStatus'].fillna("Unknown")
    df['Value'] = pd.to_numeric(df['attributes.price'], errors='coerce').fillna(0)
    df['Rep'] = df['attributes.accountManagerName'].fillna("Unassigned") if 'attributes.accountManagerName' in df.columns else "Unassigned"
    df['Client'] = df['attributes.billedCompanyName'].fillna("Unknown") if 'attributes.billedCompanyName' in df.columns else "Unknown"
    df['Opportunity ID'] = df['id']

    # Filters
    reps = df['Rep'].unique()
    clients = df['Client'].unique()
    min_date = df['Created Date'].dropna().min().date()
    max_date = df['Created Date'].dropna().max().date()

    selected_rep = st.sidebar.selectbox("Account Manager", options=["All"] + list(reps))
    selected_client = st.sidebar.selectbox("Client", options=["All"] + list(clients))
    status_filter = st.sidebar.multiselect("Status", options=df['Status'].unique())
    date_range = st.sidebar.date_input("Created Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    # Filter logic
    filtered = df.copy()
    if selected_rep != "All":
        filtered = filtered[filtered['Rep'] == selected_rep]
    if selected_client != "All":
        filtered = filtered[filtered['Client'] == selected_client]
    if status_filter:
        filtered = filtered[filtered['Status'].isin(status_filter)]
    if len(date_range) == 2:
        try:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            filtered = filtered[(filtered['Created Date'] >= start) & (filtered['Created Date'] <= end)]
        except Exception as e:
            st.warning("⚠️ Please select a valid date range within available data.")

    # KPI cards
    total_opps = filtered.shape[0]
    closed_opps = filtered[filtered['Status'].str.lower() == 'closed'].shape[0]
    open_opps = filtered[filtered['Status'].str.lower() != 'closed'].shape[0]
    win_rate = (closed_opps / total_opps) * 100 if total_opps > 0 else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Opportunities", total_opps)
    kpi2.metric("Open Opportunities", open_opps)
    kpi3.metric("Closed Opportunities", closed_opps)
    kpi4.metric("Win Rate", f"{win_rate:.2f}%")

    # Line chart - Opportunity trends over time
    trend = filtered.copy()
    trend['Month'] = trend['Created Date'].dt.to_period("M").astype(str)
    st.subheader("\U0001F4C8 Opportunity Trend (Monthly)")
    st.plotly_chart(px.line(trend.groupby(['Month', 'Status']).size().reset_index(name='Count'),
                            x='Month', y='Count', color='Status'), use_container_width=True)

    # Breakdown charts
    st.subheader("\U0001F4CA Opportunity Breakdown")
    breakdown1, breakdown2, breakdown3 = st.columns(3)

    with breakdown1:
        st.plotly_chart(px.bar(filtered['Rep'].value_counts().reset_index(), x='index', y='Rep',
                               labels={'index': 'Rep', 'Rep': 'Opportunities'}), use_container_width=True)
    with breakdown2:
        st.plotly_chart(px.pie(filtered, names='Client', title="By Client"), use_container_width=True)
    with breakdown3:
        st.plotly_chart(px.bar(filtered['attributes.opportunityType'].value_counts().reset_index(),
                               x='index', y='attributes.opportunityType',
                               labels={'index': 'Type', 'attributes.opportunityType': 'Count'}),
                        use_container_width=True)

    # Table
    st.subheader("\U0001F4CB Opportunity Table")
    st.dataframe(filtered[['Opportunity ID', 'Client', 'Rep', 'Status', 'Created Date', 'Value']]
                 .sort_values(by='Created Date', ascending=False), use_container_width=True)

else:
    st.error("No opportunity data available. Please check API credentials or connectivity.")
