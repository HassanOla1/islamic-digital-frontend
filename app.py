# frontend/app.py
import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import time  

# Set page config
st.set_page_config(page_title="Islamic Digital Economy Dashboard", layout="wide")

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")

def apply_custom_theme():
    st.markdown("""
<style>
    .stMetric {
        background: linear-gradient(135deg, #0078D4, #228B22);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 120, 212, 0.2);
        color: white;
    }
    .stTextInput input {
        border-radius: 10px;
        border: 2px solid #0078D4;
        transition: all 0.3s ease;
    }
    .stTextInput input:focus {
        border-color: #FFD700;
        box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.3);
    }
    .stButton button {
        background: linear-gradient(45deg, #0078D4, #FFD700);
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0, 120, 212, 0.4);
    }
</style>
""", unsafe_allow_html=True)

apply_custom_theme()

def check_backend():
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                return True
            time.sleep(5)  # ✅ Wait before retrying
        except:
            if i < max_retries - 1:
                time.sleep(5)  # ✅ Wait before retrying
            continue
    return False

# Sidebar filters
st.sidebar.image("https://via.placeholder.com/200x100?text=Islamic+Economy+Dashboard ")
st.sidebar.markdown("## 🌍 Filters")

# Country selector
try:
    response = requests.get(f"{BACKEND_URL}/query/halal_ecommerce")
    countries = list(set(row["country"] for row in response.json())) if response.status_code == 200 else ["Malaysia", "Indonesia", "Saudi Arabia"]
except:
    countries = ["Malaysia", "Indonesia", "Saudi Arabia"]

selected_countries = st.sidebar.multiselect("Select Countries", options=countries, default=countries)
selected_year = st.sidebar.slider("Select Year", min_value=2015, max_value=2025, value=2020)

# Main dashboard
st.title("📊 Islamic Digital Economy Dashboard")
st.markdown("Explore trends in halal e-commerce, fintech, and digital economy metrics")

# Tabs
selected = option_menu(
    menu_title=None,
    options=["Halal E-commerce", "ICT & Fintech", "Data Explorer"],
    icons=["shop", "graph-up-arrow", "table"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

# Tab: Halal E-commerce
if selected == "Halal E-commerce":
    st.header("🛒 Halal E-commerce Growth")
    
    # Revenue comparison
    rev_response = requests.get(
        f"{BACKEND_URL}/aggregation/halal_ecommerce",
        params={"metric": "revenue_usd", "group_by": "country"}
    )
    
    if rev_response.status_code == 200:
        rev_data = rev_response.json()
        rev_df = pd.DataFrame(rev_data if isinstance(rev_data, list) else [rev_data])
        if not rev_df.empty:
            fig = px.bar(
                rev_df, 
                x="country", 
                y="total", 
                title="Total Revenue by Country",
                color="country",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig, use_container_width=True)

    # Growth rate trends
    trend_response = requests.get(
        f"{BACKEND_URL}/query/halal_ecommerce",
        params={"countries": selected_countries}
    )

    if trend_response.status_code == 200:
        trend_data = trend_response.json()
        trend_df = pd.DataFrame(trend_data if isinstance(trend_data, list) else [trend_data])
        if not trend_df.empty:
            trend_fig = px.line(
                trend_df[trend_df["country"].isin(selected_countries)],
                x="year", 
                y="growth_rate", 
                color="country",
                title="Growth Rate Trends",
                markers=True
            )
            st.plotly_chart(trend_fig, use_container_width=True)

# Tab: ICT & Fintech
elif selected == "ICT & Fintech":
    col1, col2 = st.columns(2)
    with col1:
        ict_response = requests.get(f"{BACKEND_URL}/aggregation/ict_services", params={"metric": "gross_output", "group_by": "country"})
        if ict_response.status_code == 200:
            ict_data = ict_response.json()
            ict_df = pd.DataFrame(ict_data if isinstance(ict_data, list) else [ict_data])
            if not ict_df.empty:
                ict_fig = px.area(ict_df, x="country", y="total", title="Gross Output by Country")
                st.plotly_chart(ict_fig, use_container_width=True)

    with col2:
        penetration_response = requests.get(f"{BACKEND_URL}/query/internet_penetration")
        if penetration_response.status_code == 200:
            penetration_data = penetration_response.json()
            penetration_df = pd.DataFrame(penetration_data if isinstance(penetration_data, dict) else penetration_data)
            if not penetration_df.empty:
                penetration_df["internet_penetration"] = penetration_df["internet_penetration"].str.replace("%", "").astype(float)
                penetration_fig = px.bar(
                    penetration_df, 
                    x="country", 
                    y="internet_penetration", 
                    title="Internet Penetration Rate",
                    range_y=[0, 100]
                )
                st.plotly_chart(penetration_fig, use_container_width=True)

# Tab: Data Explorer
elif selected == "Data Explorer":
    st.header("🔍 Data Explorer")
    tables = ["halal_ecommerce", "ict_services", "islamic_fintech", "household_ict"]
    selected_table = st.selectbox("Select Dataset", tables)
    if st.button("Load Data"):
        response = requests.get(f"{BACKEND_URL}/query/{selected_table}")
        df = pd.DataFrame(response.json() if response.status_code == 200 else [])
        st.dataframe(df)

# Summary Metrics
st.markdown("## 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    response = requests.get(f"{BACKEND_URL}/summary/halal_ecommerce")
    data = response.json() if response.status_code == 200 else {"count": 0, "avg_growth_rate": 0}
    st.metric("Total Halal Revenue", f"${data.get('count', 0) * 1_000_000:,.0f} USD")

with col2:
    response = requests.get(f"{BACKEND_URL}/summary/islamic_fintech")
    data = response.json() if response.status_code == 200 else {"count": 0}
    st.metric("Total Fintech Transactions", f"${data.get('count', 0) * 1_000_000:,.0f} USD")

with col3:
    response = requests.get(f"{BACKEND_URL}/summary/ict_services")
    data = response.json() if response.status_code == 200 else {"count": 0}
    st.metric("Total ICT Output", f"${data.get('count', 0) * 1_000_000:,.0f} USD")

with col4:
    response = requests.get(f"{BACKEND_URL}/summary/household_ict")
    data = response.json() if response.status_code == 200 else {"avg_growth_rate": 75.4}
    st.metric("Average Internet Usage", f"{data.get('avg_growth_rate', 75.4):.1f}%")

# Download Reports
st.sidebar.markdown("## 📥 Download Reports")
all_tables = ["halal_ecommerce", "ict_services", "islamic_fintech", "household_ict"]
selected_report = st.sidebar.selectbox("Select Report", all_tables)
if st.sidebar.button("Generate Report"):
    response = requests.get(f"{BACKEND_URL}/download/{selected_report}")
    st.sidebar.download_button(
        label="Download CSV",
        data=response.content,
        file_name=f"{selected_report}.csv",
        mime="text/csv"
    )