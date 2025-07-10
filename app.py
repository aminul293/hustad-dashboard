# app.py
import streamlit as st
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="🛠 Service List Viewer", layout="wide")
st.title("📋 Service List from Centerpoint API")

df = fetch_service_data()

expected_cols = ["Ticket ID", "Description", "Company", "Property",
                 "Manager", "Status", "Type", "Opened At", "Price"]

if df.empty:
    st.warning("No data available from the API.")
else:
    st.write("✅ Loaded DataFrame with columns:")
    st.code(df.columns.tolist())

    if all(col in df.columns for col in expected_cols):
        st.dataframe(
            df[expected_cols].sort_values(by="Opened At", ascending=False),
            use_container_width=True
        )
    else:
        st.warning("⚠️ Some expected columns are missing. Showing full table.")
        st.dataframe(df, use_container_width=True)
