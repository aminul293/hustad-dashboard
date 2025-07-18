# centerpoint_api.py

import requests
import pandas as pd
import streamlit as st

BASE_URL = "https://api.centerpointconnect.io/centerpoint"
HEADERS = {
    "Authorization": st.secrets["centerpoint"]["api_key"],
    "Accept": "application/json"
}

@st.cache_data(ttl=300)
def fetch_service_data():
    url = f"{BASE_URL}/services?include=billedCompany,property,accountManager&sort=-openedAt"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        return pd.DataFrame()

    data = res.json()
    included_lookup = {
        (item["type"], item["id"]): item.get("attributes", {}).get("name", "Unknown")
        for item in data.get("included", [])
    }

    def resolve(rel, rel_type):
        if isinstance(rel, dict) and "data" in rel:
            _id = rel["data"].get("id")
            return included_lookup.get((rel_type, _id), "Unknown")
        return "Unknown"

    records = []
    for item in data.get("data", []):
        attr = item.get("attributes", {})
        rels = item.get("relationships", {})
        records.append({
            "ticket_id": attr.get("name"),
            "description": attr.get("description"),
            "company": resolve(rels.get("billedCompany"), "companies"),
            "property": resolve(rels.get("property"), "properties"),
            "opportunity_manager": resolve(rels.get("accountManager"), "employees"),
            "state": attr.get("displayStatus"),
            "created_date": attr.get("openedAt"),
            "type": attr.get("opportunityType", "Unknown"),
            "sale_price": attr.get("price", 0)
        })

    df = pd.DataFrame(records)
    df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
    df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce").fillna(0)
    return df
