
import pandas as pd
import requests
import streamlit as st

@st.cache_data
def fetch_service_data():
    try:
        headers = {
            "Authorization": st.secrets["centerpoint"]["api_key"],
            "Accept": "application/json"
        }

        url = "https://api.centerpointconnect.io/centerpoint/services"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            st.error(f"API Error: {response.status_code}")
            st.stop()

        json_data = response.json()
        data = json_data.get("data", [])

        # Flatten nested 'attributes' for each item in data
        records = [item["attributes"] for item in data if "attributes" in item]
        df = pd.DataFrame(records)

        # Attempt to convert dates and numeric fields
        for col in df.columns:
            if "date" in col.lower() or "at" in col.lower():
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df

    except Exception as e:
        st.error(f"Exception occurred: {e}")
        st.stop()
