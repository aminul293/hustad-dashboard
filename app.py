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
    res = requests.get(url, headers=HEADERS)
    data = res.json()

    included_lookup = {}
    for item in data.get("included", []):
        _type = item.get("type")
        _id = item.get("id")
        name = item.get("attributes", {}).get("name", "Unknown")
        included_lookup[(_type, _id)] = name

    rows = []
    for item in data.get("data", []):
        attr = item.get("attributes", {})
        rels = item.get("relationships", {})

        def resolve_name(rel_key):
            rel_data = rels.get(rel_key, {}).get("data")
            if rel_data:
                return included_lookup.get((rel_data["type"], rel_data["id"]), "Unknown")
            return "Unknown"

        rows.append({
            "Ticket ID": attr.get("name"),
            "Description": attr.get("description"),
            "Company": resolve_name("billedCompany"),
            "Property": resolve_name("property"),
            "Manager": resolve_name("accountManager"),
            "Status": attr.get("displayStatus", "Unknown"),
            "Type": attr.get("opportunityType", "Unknown"),
            "Opened At": attr.get("openedAt"),
            "Price": attr.get("price", 0)
        })

    df = pd.DataFrame(rows)
    df["Opened At"] = pd.to_datetime(df["Opened At"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)
    return df
