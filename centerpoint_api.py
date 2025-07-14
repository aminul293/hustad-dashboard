# centerpoint_api.py

import requests
import pandas as pd
import streamlit as st

BASE_URL = "https://api.centerpointconnect.io/centerpoint"
HEADERS = {
    "Authorization": st.secrets["centerpoint"]["eyJvcmciOiI2NmJlMzEwMzFiMGJjMTAwMDEwM2RiN2MiLCJpZCI6IjE0NWQwN2E2MmRiMjQyNTM5NmQyOWU5NTBjY2VhMzk2IiwiaCI6Im11cm11cjEyOCJ9"],  # Make sure this is the actual token, not the hash
    "Accept": "application/json"
}

@st.cache_data
def fetch_service_data():
    url = f"{BASE_URL}/services?include=billedCompany,property,accountManager&sort=-openedAt"

    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except Exception as e:
        st.error(f"❌ API error: {e}")
        return pd.DataFrame()

    data = res.json()

    # Create lookup from included section
    included_lookup = {}
    for item in data.get("included", []):
        _type = item.get("type")
        _id = item.get("id")
        name = item.get("attributes", {}).get("name", "Unknown")
        included_lookup[(_type, _id)] = name

    def resolve(rel, rel_type):
        if isinstance(rel, dict) and "data" in rel:
            rel_data = rel["data"]
            if isinstance(rel_data, dict):
                _id = rel_data.get("id")
                return included_lookup.get((rel_type, _id), "Unknown") if _id else "Unknown"
        return "Unknown"

    records = []
    for item in data.get("data", []):
        attr = item.get("attributes", {})
        rels = item.get("relationships", {})

        records.append({
            "Ticket ID": attr.get("name"),
            "Description": attr.get("description"),
            "Company": resolve(rels.get("billedCompany"), "companies"),
            "Property": resolve(rels.get("property"), "properties"),
            "Manager": resolve(rels.get("accountManager"), "employees"),
            "Status": attr.get("displayStatus", "Unknown"),
            "Type": attr.get("opportunityType", "Unknown"),
            "Opened At": attr.get("openedAt"),
            "Price": attr.get("price", 0)
        })

    df = pd.DataFrame(records)
    df["Opened At"] = pd.to_datetime(df["Opened At"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
    return df

