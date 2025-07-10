
import streamlit as st
import pandas as pd
import plotly.express as px
from centerpoint_api import fetch_service_data
from ai_agents import generate_followup_email, generate_weekly_summary

st.set_page_config(page_title="Hustad Sales & Service Dashboard", layout="wide")

# Load data from API or fallback CSV
df = fetch_service_data()

# Sidebar filters
st.sidebar.header("🔎 Filter Data")
rep = st.sidebar.multiselect("Sales Rep", options=df['Opportunity Manager'].dropna().unique())
stage = st.sidebar.multiselect("Stage", options=df['Stage'].dropna().unique())
stype = st.sidebar.multiselect("Service Type", options=df['Service Type - Hustad'].dropna().unique())
date_range = st.sidebar.date_input("Created Date Range", [])

# Apply filters
filtered_df = df.copy()
if rep:
    filtered_df = filtered_df[filtered_df['Opportunity Manager'].isin(rep)]
if stage:
    filtered_df = filtered_df[filtered_df['Stage'].isin(stage)]
if stype:
    filtered_df = filtered_df[filtered_df['Service Type - Hustad'].isin(stype)]
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Created Date'] >= pd.to_datetime(date_range[0])) &
        (filtered_df['Created Date'] <= pd.to_datetime(date_range[1]))
    ]

# KPIs
st.title("🚀 Hustad Sales & Service Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(filtered_df))
col2.metric("Scheduled", filtered_df[filtered_df['Stage'] == 'Scheduled'].shape[0])
col3.metric("In Progress", filtered_df[filtered_df['Stage'] == 'In Progress'].shape[0])
col4.metric("Total Sale Value", f"${filtered_df['Sale Price'].sum():,.2f}")

# Charts
st.subheader("📊 Requests by Type")
st.plotly_chart(px.bar(filtered_df['Type'].value_counts().reset_index(), x='index', y='Type', labels={'index': 'Type', 'Type': 'Count'}))

st.subheader("🧑‍💼 By Sales Rep")
st.plotly_chart(px.bar(filtered_df['Opportunity Manager'].value_counts().reset_index(), x='index', y='Opportunity Manager', labels={'index': 'Rep', 'Opportunity Manager': 'Count'}))

# Download filtered data
st.subheader("⬇️ Download CSV")
st.download_button("Download Filtered Data", data=filtered_df.to_csv(index=False), file_name="filtered_requests.csv")

# AI Tools
st.header("🤖 AI-Powered Tools")

tab1, tab2 = st.tabs(["📩 Follow-Up Generator", "📋 Weekly Sales Summary"])

with tab1:
    st.subheader("Generate Follow-Up Email")
    sample = filtered_df[filtered_df['Type'] == 'Scope'].sample(1) if not filtered_df.empty else pd.DataFrame()
    if not sample.empty:
        desc = sample.iloc[0]['Description']
        company = sample.iloc[0]['Company']
        prop = sample.iloc[0]['Property']
        rep = sample.iloc[0]['Opportunity Manager']
        if st.button("Generate Email"):
            email = generate_followup_email(company, prop, desc, rep)
            st.success(email)
    else:
        st.info("No 'Scope' records found.")

with tab2:
    st.subheader("Weekly AI Summary")
    if st.button("Generate Summary"):
        summary = generate_weekly_summary(filtered_df)
        st.info(summary)
