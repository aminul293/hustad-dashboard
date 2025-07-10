# In your main file named: app.py

import streamlit as st
import pandas as pd
from datetime import datetime
from centerpoint_api import fetch_service_data # <-- IMPORTANT: Import your function

# --- Page Configuration ---
st.set_page_config(
    page_title="Centerpoint Service Dashboard",
    page_icon="📡",
    layout="wide",
)

st.title("📡 Centerpoint Service Dashboard")
st.markdown("Live service data from the Centerpoint API.")

# --- Load Data ---
# Call the function from your centerpoint_api.py file.
# It handles tokens, errors, and data transformation internally.
with st.spinner("Fetching latest service data..."):
    df = fetch_service_data()

# --- Main App Logic ---
# The rest of the app now works with the clean DataFrame from your API module.
if not df.empty:
    st.sidebar.header("Filter Options")

    # The 'Opened At' column is already a datetime object from your API module.
    if not df['Opened At'].isnull().all():
        min_date = df['Opened At'].min().date()
        max_date = df['Opened At'].max().date()

        date_range = st.sidebar.date_input(
            "Filter by 'Opened At' date:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    else:
        date_range = [] # Disable filter if no valid dates

    # --- Filter DataFrame ---
    if len(date_range) == 2:
        start_ts = pd.to_datetime(date_range[0])
        end_ts = pd.to_datetime(date_range[1]).replace(hour=23, minute=59, second=59)

        # Filter the DataFrame using the datetime objects
        filtered_df = df[
            df['Opened At'].notna() &
            (df['Opened At'] >= start_ts) &
            (df['Opened At'] <= end_ts)
        ]
    else:
        filtered_df = df.copy()

    # --- Display Metrics and Data ---
    st.header("Filtered Service Tickets")
    
    if len(date_range) == 2:
        st.markdown(f"Displaying data from **{date_range[0].strftime('%Y-%m-%d')}** to **{date_range[1].strftime('%Y-%m-%d')}**.")

    col1, col2 = st.columns(2)
    col1.metric("Total Tickets Found", f"{filtered_df.shape[0]}")
    # The 'Price' column is already numeric from your API module.
    col2.metric("Total Price (USD)", f"${filtered_df['Price'].sum():,.2f}")

    st.dataframe(
        filtered_df.sort_values(by="Opened At", ascending=False).style.format({"Price": "${:,.2f}"}),
        use_container_width=True
    )

else:
    # This message appears if fetch_service_data returns an empty DataFrame
    st.error("Failed to load data from Centerpoint API. Check the error message above and ensure your secrets are set correctly.")