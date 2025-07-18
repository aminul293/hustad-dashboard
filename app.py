# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="📊 Centerpoint Dashboard", layout="wide")
st.title("📊 Live Centerpoint Sales Dashboard")

with st.spinner("Fetching live data..."):
    df = fetch_service_data()

if df.empty:
    st.error("No data received from API.")
    st.stop()

# Filter
st.sidebar.header("Filters")
min_date, max_date = df["created_date"].min(), df["created_date"].max()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
rep_list = ["All"] + sorted(df["opportunity_manager"].dropna().unique().tolist())
selected_rep = st.sidebar.selectbox("Filter by Rep", rep_list)

filtered_df = df.copy()
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[filtered_df["created_date"].between(start, end)]

if selected_rep != "All":
    filtered_df = filtered_df[filtered_df["opportunity_manager"] == selected_rep]

# KPIs
st.subheader("📌 Summary Metrics")
col1, col2 = st.columns(2)
col1.metric("Closed Transactions", f"{filtered_df.shape[0]}")
col2.metric("Total Sales", f"${filtered_df['sale_price'].sum():,.0f}")

# Charts
st.subheader("🧑 Top Performing Reps")
top_reps = (
    filtered_df.groupby("opportunity_manager")["sale_price"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
fig1 = px.bar(top_reps, x="opportunity_manager", y="sale_price", title="Sales by Rep", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📅 Weekly Sales Trend")
trend = (
    filtered_df.set_index("created_date")
    .resample("W")["sale_price"]
    .sum()
    .reset_index()
)
fig2 = px.line(trend, x="created_date", y="sale_price", title="Weekly Sales")
st.plotly_chart(fig2, use_container_width=True)

# High Value
st.subheader("🏆 High-Value Transactions")
high_value = filtered_df[filtered_df["sale_price"] > 100000].sort_values(by="sale_price", ascending=False)
st.dataframe(high_value)

# Raw Table
st.markdown("### 📋 Full Data Table")
st.dataframe(filtered_df)

