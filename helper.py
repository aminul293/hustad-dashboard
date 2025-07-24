# utils/helpers.py

import requests

def fetch_ai_summary_from_n8n(webhook_url):
    try:
        response = requests.get(webhook_url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"❌ Failed to fetch from n8n: {e}"
