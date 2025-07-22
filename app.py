import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Hustad AI Workflow Dashboard", layout="wide")

with st.sidebar:
    selected = option_menu(
        menu_title="Hustad Dashboards",
        options=[
            "Overview", "Financial", "ROI & Profitability", "Sales Intelligence",
            "Labor Efficiency", "Vendors", "Client Accounts", "Trends",
            "HR & Workforce", "Production", "Project Management"
        ],
        icons=["house", "bar-chart-line", "graph-up", "clipboard-data",
               "people", "truck", "person-lines-fill", "activity",
               "person-workspace", "gear", "building"],
        default_index=0,
    )

st.title("📊 Hustad AI Workflow & Automation Dashboard")

if selected == "Overview":
    st.header("📌 Executive Overview")
    st.markdown("Welcome to the Hustad Executive Dashboard. Use the sidebar to explore each department.")
    # KPIs snapshot
    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Revenue", "$1.2M")
    col2.metric("Open Opportunities", "124")
    col3.metric("Avg ROI / Client", "18.4%")

elif selected == "Financial":
    st.switch_page("pages/1_Financial.py")

elif selected == "ROI & Profitability":
    st.switch_page("pages/2_ROI.py")

elif selected == "Sales Intelligence":
    st.switch_page("pages/3_Sales.py")

elif selected == "Labor Efficiency":
    st.switch_page("pages/4_Labor.py")

elif selected == "Vendors":
    st.switch_page("pages/5_Vendors.py")

elif selected == "Client Accounts":
    st.switch_page("pages/6_Clients.py")

elif selected == "Trends":
    st.switch_page("pages/7_Trend_Analysis.py")

elif selected == "HR & Workforce":
    st.switch_page("pages/8_HR.py")

elif selected == "Production":
    st.switch_page("pages/9_Production.py")

elif selected == "Project Management":
    st.switch_page("pages/10_Project_Management.py")
