import requests
import pandas as pd
import streamlit as st

BASE_URL = "https://api.centerpointconnect.io/centerpoint"
HEADERS = {
    "Authorization": st.secrets["centerpoint"]["api_key"],
    "Accept": "application/json"
}

@st.cache_data
def fetch_service_data():
    res = requests.get(f"{BASE_URL}/services", headers=HEADERS)
    data = res.json().get("data", [])
    return pd.DataFrame([d["attributes"] for d in data])

@st.cache_data
def fetch_invoices():
    res = requests.get(f"{BASE_URL}/invoices", headers=HEADERS)
    data = res.json().get("data", [])
    return pd.DataFrame([d["attributes"] for d in data])

@st.cache_data
def fetch_companies():
    res = requests.get(f"{BASE_URL}/companies", headers=HEADERS)
    data = res.json().get("data", [])
    return pd.DataFrame([d["attributes"] for d in data])

@st.cache_data
def fetch_properties():
    res = requests.get(f"{BASE_URL}/properties", headers=HEADERS)
    data = res.json().get("data", [])
    return pd.DataFrame([d["attributes"] for d in data])

@st.cache_data
def fetch_employees():
    res = requests.get(f"{BASE_URL}/employees", headers=HEADERS)
    data = res.json().get("data", [])
    return pd.DataFrame([d["attributes"] for d in data])

@st.cache_data
def fetch_opportunities():
    res = requests.get(f"{BASE_URL}/opportunities", headers=HEADERS)
    data = res.json().get("data", [])
    return pd.DataFrame([d["attributes"] for d in data])
