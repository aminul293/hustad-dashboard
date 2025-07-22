import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💵 Financial & Revenue Performance")

# Load sample data
df = pd.read_csv("data/sales_pipline.csv")

# Filters
year = st.selectbox("Select Year", df['Year'].unique())
filtered = df[df['Year'] == year]

# Charts
st.subheader("Department-Level P&L Summary")
fig = px.bar(filtered, x="Department", y="Net_Profit", color="Department", barmode="group")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Cash Flow: Projected vs Actual")
fig2 = px.line(filtered, x="Month", y=["Cash_Projected", "Cash_Actual"], markers=True)
st.plotly_chart(fig2, use_container_width=True)
