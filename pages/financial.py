import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💵 Financial & Revenue Performance")

# Example placeholder dataset
data = {
    "Department": ["Sales", "Production", "Service"],
    "Net_Profit": [120000, 85000, 56000],
    "Month": ["June", "June", "June"]
}
df = pd.DataFrame(data)

# Bar chart
fig = px.bar(df, x="Department", y="Net_Profit", color="Department", title="Department Net Profit")
st.plotly_chart(fig, use_container_width=True)
