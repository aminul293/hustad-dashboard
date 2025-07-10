
import openai
import streamlit as st

openai.api_key = st.secrets["openai"]["api_key"]

def generate_followup_email(client, property_name, issue, rep_name):
    prompt = f"Write a professional follow-up email to {client} regarding the service at {property_name}. The issue is: {issue}. The sales rep is {rep_name}."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

def generate_weekly_summary(df):
    total = len(df)
    scheduled = df[df['Stage'] == 'Scheduled'].shape[0]
    in_progress = df[df['Stage'] == 'In Progress'].shape[0]
    value = df['Sale Price'].sum()
    return f"This week, you have {total} requests, with {scheduled} scheduled, {in_progress} in progress, and a total estimated value of ${value:,.2f}."
