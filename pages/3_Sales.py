# pages/3_Sales.py

import streamlit as st
from utils.helpers import fetch_ai_summary_from_n8n

st.set_page_config(page_title="Sales Intelligence", layout="wide")
st.title("📈 Sales & Opportunity AI Summary")

# Your n8n webhook (returning the AI-generated report)
N8N_AI_URL = "https://n8n.hustad.ai/webhook/ai-report-live"

if st.button("🔄 Fetch Latest Summary"):
    result = fetch_ai_summary_from_n8n(N8N_AI_URL)
    st.text_area("📋 Daily Sales Summary", result, height=400)
