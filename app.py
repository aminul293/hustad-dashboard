# centerpoint_api.py
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
    url = f"{BASE_URL}/services?include=billedCompany,property,accountManager"
    response = requests.get(url, headers=HEADERS)
    data = response.json()

    rows = []
    included_lookup = {}

    # Build lookup from included data
    for entry in data.get("included", []):
        included_lookup[(entry["type"], entry["id"])] = entry["attributes"].get("name")

    for item in data["data"]:
        attr = item["attributes"]
        rels = item.get("relationships", {})

        def get_name(rel_key):
            rel_data = rels.get(rel_key, {}).get("data")
            if rel_data:
                return included_lookup.get((rel_data["type"], rel_data["id"]), "Unknown")
            return "Unknown"

        rows.append({
            "Ticket ID": attr.get("name"),
            "Description": attr.get("description"),
            "Company": get_name("billedCompany"),
            "Property": get_name("property"),
            "Manager": get_name("accountManager"),
            "Status": attr.get("displayStatus"),
            "Type": attr.get("opportunityType"),
            "Opened At": attr.get("openedAt"),
            "Price": attr.get("price")
        })

    df = pd.DataFrame(rows)
    df["Opened At"] = pd.to_datetime(df["Opened At"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
    return df




import streamlit as st
from centerpoint_api import fetch_service_data

st.set_page_config(page_title="🛠 Service List", layout="wide")

st.title("📋 Service List from Centerpoint API")

df = fetch_service_data()

if df.empty:
    st.warning("No data available.")
else:
    st.dataframe(df, use_container_width=True)
