import streamlit as st
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="🛠 Service List Viewer", layout="wide")
st.title("📋 Service List from Centerpoint API")

# Show loading spinner while data loads
with st.spinner("🔄 Loading data from API..."):
    df = fetch_service_data()

# Show what was loaded
st.write("✅ Fetched Data Shape:", df.shape)
st.write("📋 Columns:", df.columns.tolist())

# Define expected display columns
expected_cols = ["Ticket ID", "Description", "Company", "Property",
                 "Manager", "Status", "Type", "Opened At", "Price"]

if df.empty:
    st.warning("⚠️ No data returned from API.")
else:
    if all(col in df.columns for col in expected_cols):
        st.dataframe(
            df[expected_cols].sort_values(by="Opened At", ascending=False),
            use_container_width=True
        )
    else:
        st.warning("⚠️ Some expected columns are missing. Showing full raw table.")
        st.dataframe(df, use_container_width=True)
