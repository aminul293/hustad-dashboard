
import pandas as pd
import requests
import streamlit as st

@st.cache_data
def fetch_service_data():
    try:
        headers = {"x-api-key": st.secrets["centerpoint"]["api_key"]}
        url = "https://api.centerpointconnect.io/service/records"  # Example endpoint
        resp = requests.get(url, headers=headers)
        data = resp.json()
        df = pd.DataFrame(data)
        df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
        df['Sale Price'] = pd.to_numeric(df['Sale Price'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.warning("Using fallback CSV due to API error.")
        df = pd.read_csv("service-4-2025-07-09.csv")
        df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
        df['Sale Price'] = pd.to_numeric(df['Sale Price'], errors='coerce').fillna(0)
        return df
