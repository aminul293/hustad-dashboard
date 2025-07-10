# app.py
import streamlit as st
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="🛠 Service List Viewer", layout="wide")
st.title("📋 Service List from Centerpoint API")

df = fetch_service_data()

if df.empty:
    st.warning("No data available from the API.")
else:
    st.dataframe(
        df[[
            "Ticket ID", "Description", "Company", "Property",
            "Manager", "Status", "Type", "Opened At", "Price"
        ]].sort_values(by="Opened At", ascending=False),
        use_container_width=True
    )
