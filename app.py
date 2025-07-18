import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
from streamlit.errors import StreamlitAPIException  # Added to fix exception handling

# --- API CONFIG ---
BASE_URL = "https://api.centerpointconnect.io/centerpoint"
HEADERS = {
    "Authorization": st.secrets["centerpoint"]["api_key"],
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
            "Created Date": attr.get("createdAt"),
            "Price": attr.get("price", 0)
        })

    df = pd.DataFrame(records)
    df["Opened At"] = pd.to_datetime(df["Opened At"], errors="coerce")
    df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0)

    return df

# --- Streamlit App Setup ---
st.set_page_config(page_title="📡 Centerpoint Service Dashboard", layout="wide")
st.title("📡 Centerpoint Service Dashboard")
st.markdown("Live service data from the Centerpoint API.")

with st.spinner("Fetching latest service data..."):
    df = fetch_service_data()

if not df.empty:
    st.sidebar.header("Filter Options")

    if not df['Created Date'].isnull().all():
        min_date = df['Created Date'].min().date()
        max_data_date = df['Created Date'].max().date()
        today = datetime.today().date()
        max_display_date = max(today + timedelta(days=7), max_data_date)

        try:
            date_range = st.sidebar.date_input(
                "Filter by 'Created Date':",
                value=(max_data_date - timedelta(days=7), max_data_date),
                min_value=min_date,
                max_value=max_display_date
            )
        except StreamlitAPIException:
            st.sidebar.error("⚠️ Please select a date within the valid range.")
            date_range = []
    else:
        date_range = []

    if len(date_range) == 2:
        start_ts = pd.to_datetime(date_range[0])
        end_ts = pd.to_datetime(date_range[1]).replace(hour=23, minute=59, second=59)

        created_for_comparison = df["Created Date"]
        if pd.api.types.is_datetime64_any_dtype(created_for_comparison) and created_for_comparison.dt.tz is not None:
            created_for_comparison = created_for_comparison.dt.tz_convert(None)

        mask = (
            df["Created Date"].notna() &
            (created_for_comparison >= start_ts) &
            (created_for_comparison <= end_ts)
        )
        filtered_df = df[mask]

        if filtered_df.empty:
            st.warning("⚠️ No data found for the selected date range.")
    else:
        filtered_df = df.copy()

    st.header("Filtered Service Tickets")

    if len(date_range) == 2:
        st.markdown(f"Displaying data from **{date_range[0].strftime('%Y-%m-%d')}** to **{date_range[1].strftime('%Y-%m-%d')}**.")

    col1, col2 = st.columns(2)
    col1.metric("Total Tickets Found", f"{filtered_df.shape[0]}")
    col2.metric("Total Price (USD)", f"${filtered_df['Price'].sum():,.2f}")

    st.dataframe(
        filtered_df.sort_values(by="Created Date", ascending=False).style.format({"Price": "${:,.2f}"}),
        use_container_width=True
    )
else:
    st.error("Failed to load data from Centerpoint API. Check the error message above and ensure your secrets are set correctly.")
