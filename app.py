# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="📋 Service List from Centerpoint API", layout="wide")

st.title("📋 Service List from Centerpoint API")

# Fetch data from API
df = fetch_service_data()

if df.empty:
    st.error("No data loaded from API.")
    st.stop()

# Inspect available columns
st.success(f"✅ Fetched Data Shape: {df.shape}")
with st.expander("📋 Columns:"):
    st.write(list(df.columns))

# Convert datetime for filtering
df["Opened At"] = pd.to_datetime(df["Opened At"], errors="coerce")

# Sidebar Filters
st.sidebar.header("🔎 Filter Data")

status_options = df["Status"].dropna().unique().tolist()
status = st.sidebar.multiselect("Status", status_options, default=status_options)

manager_options = df["Manager"].dropna().unique().tolist()
manager = st.sidebar.multiselect("Manager", manager_options)

company_options = df["Company"].dropna().unique().tolist()
company = st.sidebar.multiselect("Company", company_options)

min_date = df["Opened At"].min()
max_date = df["Opened At"].max()
date_range = st.sidebar.date_input("Opened At Range", [min_date, max_date])

# Apply filters
filtered_df = df.copy()
if status:
    filtered_df = filtered_df[filtered_df["Status"].isin(status)]
if manager:
    filtered_df = filtered_df[filtered_df["Manager"].isin(manager)]
if company:
    filtered_df = filtered_df[filtered_df["Company"].isin(company)]
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["Opened At"] >= pd.to_datetime(date_range[0])) &
        (filtered_df["Opened At"] <= pd.to_datetime(date_range[1]))
    ]

st.markdown("### 📊 Summary Visualizations")

# Chart: Requests by Status
if not filtered_df.empty:
    st.plotly_chart(
        px.bar(filtered_df["Status"].value_counts().reset_index(),
               x="index", y="Status",
               labels={"index": "Status", "Status": "Count"},
               title="Requests by Status")
    )

    # Chart: Requests over Time
    trend_df = filtered_df.groupby(filtered_df["Opened At"].dt.date).size().reset_index(name="Count")
    st.plotly_chart(
        px.line(trend_df, x="Opened At", y="Count", title="Requests Over Time")
    )
else:
    st.warning("No records match current filter.")

# Table output
st.markdown("### 📋 Filtered Service Records")
st.dataframe(filtered_df.sort_values(by="Opened At", ascending=False), use_container_width=True)

# Download button
st.download_button("📥 Download CSV", filtered_df.to_csv(index=False), file_name="filtered_service_data.csv")
