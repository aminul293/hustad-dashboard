import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Centerpoint Service Dashboard",
    page_icon="📡",
    layout="wide",
)

# --- API Data Fetching and Cleaning ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def fetch_service_data(api_token):
    """
    Connects to the Centerpoint API, fetches service data, and returns a cleaned DataFrame.
    """
    api_url = "https://api.centerpoint.io/v1/services" # Example API URL
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raises an exception for 4XX/5XX errors
        data = response.json()

        # Extract relevant fields and flatten JSON if necessary
        # This part is based on the prompt's description of fields.
        # It may need adjustment for the actual API response structure.
        records = []
        for item in data.get('services', []): # Assuming data is {'services': [...]}
            records.append({
                'Ticket ID': item.get('ticketId'),
                'Description': item.get('description'),
                'Company': item.get('company', {}).get('name'),
                'Property': item.get('property', {}).get('name'),
                'Manager': item.get('manager', {}).get('fullName'),
                'Status': item.get('status'),
                'Type': item.get('type'),
                'Opened At': item.get('openedAt'),
                'Price': item.get('price'),
            })

        df = pd.DataFrame(records)

        # --- Data Cleaning and Type Conversion ---
        # Convert 'Opened At' to datetime, coercing errors to NaT (Not a Time)
        df['Opened At'] = pd.to_datetime(df['Opened At'], errors='coerce')

        # Clean up 'Price' column, converting to numeric
        if 'Price' in df.columns:
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)

        return df

    except requests.exceptions.RequestException as e:
        st.error(f"API Connection Error: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

# --- Main Application ---
st.title("📡 Centerpoint Service Dashboard")
st.markdown("Live service data from the Centerpoint API.")

# Use a placeholder for the API token for security
# In a real app, use st.secrets for this
API_TOKEN = "eyJvcmciOiI2NmJlMzEwMzFiMGJjMTAwMDEwM2RiN2MiLCJpZCI6IjE0NWQwN2E2MmRiMjQyNTM5NmQyOWU5NTBjY2VhMzk2IiwiaCI6Im11cm11cjEyOCJ9" 

# Fetch the data
with st.spinner("Fetching latest service data..."):
    df = fetch_service_data(API_TOKEN)

if not df.empty:
    # --- Sidebar for Filtering ---
    st.sidebar.header("Filter Options")

    # Set default date range: from the earliest date in data to the latest
    min_date = df['Opened At'].min().date()
    max_date = df['Opened At'].max().date()

    date_range = st.sidebar.date_input(
        "Filter by 'Opened At' date:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Ensure the date range is valid (start <= end)
    if len(date_range) == 2:
        start_date, end_date = date_range
        
        # --- 🛠️ FIX APPLIED HERE ---
        # Convert date_input's datetime.date objects to pandas datetime (Timestamp)
        # This ensures the comparison is between the same data types.
        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59) # Include the whole end day

        # Filter the DataFrame using the corrected Timestamps
        filtered_df = df[
            df['Opened At'].notna() &
            (df['Opened At'] >= start_ts) &
            (df['Opened At'] <= end_ts)
        ]

        # --- Display Filtered Data and Metrics ---
        st.header("Filtered Service Tickets")
        st.markdown(f"Displaying data from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**.")

        # Display metrics
        col1, col2 = st.columns(2)
        col1.metric("Total Tickets Found", f"{filtered_df.shape[0]}")
        col2.metric("Total Price (USD)", f"${filtered_df['Price'].sum():,.2f}")
        
        st.dataframe(
            filtered_df.sort_values(by="Opened At", ascending=False).style.format({"Price": "${:,.2f}"}),
            use_container_width=True
        )

        # Display dataset info
        with st.expander("View Dataset Details"):
            st.write("### Filtered Dataset Shape")
            st.write(f"Rows: {filtered_df.shape[0]}, Columns: {filtered_df.shape[1]}")
            st.write("### Column Information")
            st.write(filtered_df.info())

    else:
        st.warning("Please select a valid date range in the sidebar to view data.")

else:
    st.error("Could not fetch or process data from the API. Please check the token or API status.")