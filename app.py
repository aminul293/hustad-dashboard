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
    # --- 🛠️ FIX #1: Using the correct API URL ---
    api_url = "https://api.centerpointconnect.io/centerpoint/services"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # This structure assumes the API returns a list of services.
        # Adjust the .get('services', data) part if the JSON structure is different.
        records = []
        for item in data.get('services', data): # Fallback to 'data' if no 'services' key
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
        df['Opened At'] = pd.to_datetime(df['Opened At'], errors='coerce')
        if 'Price' in df.columns:
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)

        return df

    except requests.exceptions.RequestException as e:
        st.error(f"API Connection Error: {e}")
        return pd.DataFrame()
    except ValueError as e: # Catches JSON decoding errors
        st.error(f"Data Processing Error: Failed to decode JSON. The API may have returned an unexpected response. Details: {e}")
        return pd.DataFrame()


# --- Main Application ---
st.title("📡 Centerpoint Service Dashboard")
st.markdown("Live service data from the Centerpoint API.")

# --- 🛠️ FIX #2: Securely access the API token from st.secrets ---
# This assumes you have set a secret named 'api_token' in your Streamlit settings.
try:
    API_TOKEN = st.secrets["api_token"]
except (KeyError, FileNotFoundError):
    st.error("API token not found. Please set the 'api_token' in your Streamlit secrets.")
    st.stop()


# Fetch the data
with st.spinner("Fetching latest service data from Centerpoint API..."):
    df = fetch_service_data(API_TOKEN)

if not df.empty:
    st.sidebar.header("Filter Options")

    # Guard against NaT values before getting min/max
    valid_dates = df['Opened At'].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        date_range = st.sidebar.date_input(
            "Filter by 'Opened At' date:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        if len(date_range) == 2:
            start_date, end_date = date_range
            start_ts = pd.to_datetime(start_date)
            end_ts = pd.to_datetime(end_date).replace(hour=23, minute=59, second=59)

            filtered_df = df[
                df['Opened At'].notna() &
                (df['Opened At'] >= start_ts) &
                (df['Opened At'] <= end_ts)
            ]

            st.header("Filtered Service Tickets")
            st.markdown(f"Displaying data from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**.")

            col1, col2 = st.columns(2)
            col1.metric("Total Tickets Found", f"{filtered_df.shape[0]}")
            col2.metric("Total Price (USD)", f"${filtered_df['Price'].sum():,.2f}")
            
            st.dataframe(
                filtered_df.sort_values(by="Opened At", ascending=False).style.format({"Price": "${:,.2f}"}),
                use_container_width=True
            )
        else:
            st.warning("Please select a valid date range in the sidebar to view data.")
    else:
        st.warning("No valid dates found in the 'Opened At' column to create a filter.")

else:
    st.error("Could not fetch or process data from the API. Please check your API token, the API status, or your network connection.")