# app.py

import streamlit as st
import pandas as pd
from centerpoint_api import fetch_service_data
from datetime import datetime

st.set_page_config(page_title="📡 Centerpoint Service Dashboard", layout="wide")

st.title("📡 Centerpoint Service Dashboard")
st.markdown("Live service data from the Centerpoint Production API.")

with st.spinner("Fetching data..."):
    df = fetch_service_data()

if not df.empty:
    st.sidebar.header("📅 Filter Options")

    if not df['Opened At'].isnull().all():
        min_date = df['Opened At'].min().date()
        max_date = df['Opened At'].max().date()
        date_range = st.sidebar.date_input(
            "Filter by 'Opened At':",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_range = []

    # Date filter logic
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]).replace(hour=23, minute=59)
        opened_at = df["Opened At"]
        if opened_at.dt.tz is not None:
            opened_at = opened_at.dt.tz_convert(None)
        filtered_df = df[(opened_at >= start) & (opened_at <= end)]
    else:
        filtered_df = df.copy()

    st.header("🧾 Filtered Service Tickets")

    if len(date_range) == 2:
        st.caption(f"Showing data from **{start.date()}** to **{end.date()}**")

    col1, col2 = st.columns(2)
    col1.metric("Tickets", f"{filtered_df.shape[0]}")
    col2.metric("Total Price (USD)", f"${filtered_df['Price'].sum():,.2f}")

    st.dataframe(
        filtered_df.sort_values(by="Opened At", ascending=False).style.format({"Price": "${:,.2f}"}),
        use_container_width=True
    )

else:
    st.error("❌ No data returned from the API.")
