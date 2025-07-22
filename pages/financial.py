# pages/1_Financial.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Financial Dashboard", layout="wide")
st.title("💵 Financial & Revenue Performance")

# Sample DataFrame
data = {
    "Department": ["Sales", "Production", "Service", "Inspections"],
    "Net_Profit": [125000, 98000, 67000, 32000],
    "Cash_Projected": [180000, 150000, 90000, 50000],
    "Cash_Actual": [170000, 140000, 88000, 49000],
    "Month": ["June", "June", "June", "June"]
}
df = pd.DataFrame(data)

# P&L Summary Bar Chart
st.subheader("📊 Net Profit by Department")
fig1 = px.bar(df, x="Department", y="Net_Profit", color="Department", title="Department-wise Net Profit")
st.plotly_chart(fig1, use_container_width=True)

# Cash Flow Comparison Line Chart
st.subheader("💸 Cash Flow: Projected vs Actual")
fig2 = px.line(df, x="Department", y=["Cash_Projected", "Cash_Actual"], markers=True)
st.plotly_chart(fig2, use_container_width=True)
