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
with st.spinner("Fetching latest service data..."):
    df = fetch_service_data()

# --- Main App Logic ---
if not df.empty:
    st.sidebar.header("Filter Options")

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
        date_range = []

    # --- Filter DataFrame ---
    if len(date_range) == 2:
        # --- 🛠️ FIX APPLIED HERE ---
        # `date_range` gives naive dates. Convert them to timezone-naive Timestamps.
        start_ts = pd.to_datetime(date_range[0])
        end_ts = pd.to_datetime(date_range[1]).replace(hour=23, minute=59, second=59)

        # Create a temporary, timezone-naive version of the 'Opened At' column for comparison.
        # This handles both cases: where the original data is aware or naive.
        opened_at_for_comparison = df['Opened At']
        if pd.api.types.is_datetime64_any_dtype(opened_at_for_comparison) and opened_at_for_comparison.dt.tz is not None:
            opened_at_for_comparison = opened_at_for_comparison.dt.tz_convert(None)

        # Perform the filter using two naive datetime series, which is a valid comparison.
        mask = (
            df['Opened At'].notna() &
            (opened_at_for_comparison >= start_ts) &
            (opened_at_for_comparison <= end_ts)
        )
        filtered_df = df[mask]
        # --- END OF FIX ---
    else:
        filtered_df = df.copy()

    # --- Display Metrics and Data ---
    st.header("Filtered Service Tickets")
    
    if len(date_range) == 2:
        st.markdown(f"Displaying data from **{date_range[0].strftime('%Y-%m-%d')}** to **{date_range[1].strftime('%Y-%m-%d')}**.")

    col1, col2 = st.columns(2)
    col1.metric("Total Tickets Found", f"{filtered_df.shape[0]}")
    col2.metric("Total Price (USD)", f"${filtered_df['Price'].sum():,.2f}")

    st.dataframe(
        filtered_df.sort_values(by="Opened At", ascending=False).style.format({"Price": "${:,.2f}"}),
        use_container_width=True
    )

else:
    st.error("Failed to load data from Centerpoint API. Check the error message above and ensure your secrets are set correctly.")```

By replacing your `app.py` with this version, the date filtering will now work correctly regardless of timezones, and your dashboard should be fully operational.