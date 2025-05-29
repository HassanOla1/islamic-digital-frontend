# frontend/app.py
import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
BACKEND_URL = os.getenv("BACKEND_API_URL", "https://economy-wvcc.onrender.com ")

# Set page config
st.set_page_config(page_title="Islamic Digital Economy and Digital Economy Dashboard", layout="wide")

def apply_custom_theme():
    st.markdown("""
    <style>
    /* === Light Theme === */
    .stMetric {
        background: linear-gradient(135deg, #0078D4, #FFD700);
        border-radius: 12px;
        padding: 20px;
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
        transition: transform 0.3s ease;
    }
    .stButton button:hover {
        transform: scale(1.05);
    }
    h1, h2 {
        background: linear-gradient(90deg, #004B87, #F4B400);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* === Dark Theme Auto (Optional) === */
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #121212;
            color: #e0e0e0;
        }
        .stMetric {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #f4f4f4;
        }
        .stTextInput input {
            background-color: #1e1e1e;
            border: 2px solid #f4b400;
            color: #ffffff;
        }
        .stButton button {
            background: linear-gradient(45deg, #1a1a2e, #f4b400);
            color: #fff;
        }
        h1, h2 {
            color: #f4b400;
        }
        section[data-testid="stSidebar"] {
            background-color: #1e1e1e;
            color: #ffffff;
            border-right: 1px solid #333;
        }
    }
    </style>
    """, unsafe_allow_html=True)

apply_custom_theme()

# Check backend health
def check_backend():
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(5)  # Wait before retrying
    return False

if not check_backend():
    st.error("⚠️ Backend service not available. Please check if the backend container is running.")
    st.stop()

# Sidebar
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

# Main content
st.title("📊 Islamic Digital Economy and Digital Economy Dashboard")
st.markdown("Explore trends in halal e-commerce, fintech, and digital economy metrics across Muslim-majority countries")

# Tabs
selected = option_menu(
    menu_title=None,
    options=["Halal E-commerce", "ICT & Fintech", "AI Insights", "Data Explorer"],
    icons=["shop", "graph-up-arrow", "robot", "table"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

# Tab 1: Halal E-commerce
if selected == "Halal E-commerce":
    st.header("🛒 Halal E-commerce Growth")
    
    # Revenue comparison
    rev_response = requests.get(
        f"{BACKEND_URL}/aggregation/halal_ecommerce",
        params={"metric": "revenue_usd", "group_by": "country"}
    )
    
    if rev_response.status_code == 200:
        rev_data = rev_response.json()
        rev_df = pd.DataFrame([rev_data] if isinstance(rev_data, dict) else rev_data)
        
        if not rev_df.empty:
            fig = px.bar(
                rev_df, 
                x="country", 
                y="total", 
                title="Total Revenue by Country",
                color="country",
                animation_frame="country",
                range_y=[0, rev_df["total"].max() * 1.2],
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig, use_container_width=True)

    # Growth rate trend
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
            trend_fig.update_layout(
                template="plotly_white",
                height=500,
                transition_duration=500
            )
            st.plotly_chart(trend_fig, use_container_width=True)

# Tab 2: ICT & Fintech
elif selected == "ICT & Fintech":
    col1, col2 = st.columns(2)
    
    with col1:
        # ICT Services
        ict_response = requests.get(f"{BACKEND_URL}/aggregation/ict_services", 
                                  params={"metric": "gross_output", "group_by": "country"})
        ict_data = ict_response.json()
        ict_df = pd.DataFrame([ict_data] if isinstance(ict_data, dict) else ict_data)
        
        if not ict_df.empty:
            ict_fig = px.area(ict_df, x="country", y="total", 
                            title="Gross Output by Country", 
                            color="country",
                            color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(ict_fig, use_container_width=True)

    with col2:
        # Internet Penetration
        penetration_response = requests.get(f"{BACKEND_URL}/query/internet_penetration")
        penetration_data = penetration_response.json()
        penetration_df = pd.DataFrame([penetration_data] if isinstance(penetration_data, dict) else penetration_data)
        
        if not penetration_df.empty:
            penetration_df["internet_penetration"] = penetration_df["internet_penetration"].str.replace("%", "").astype(float)
            penetration_fig = px.bar(
                penetration_df, 
                x="country", 
                y="internet_penetration", 
                title="Internet Penetration Rate",
                color="country",
                range_y=[0, 100],
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            st.plotly_chart(penetration_fig, use_container_width=True)

    # Fintech metrics
    fintech_response = requests.get(f"{BACKEND_URL}/query/islamic_fintech")
    fintech_data = fintech_response.json()
    fintech_df = pd.DataFrame([fintech_data] if isinstance(fintech_data, dict) else fintech_data)
    
    if not fintech_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            users_fig = px.pie(
                fintech_df, 
                values="active_users", 
                names="country", 
                title="Active Fintech Users Distribution",
                color_discrete_sequence=px.colors.sequential.Sunset
            )
            st.plotly_chart(users_fig, use_container_width=True)
        
        with col2:
            volume_fig = px.bar(
                fintech_df, 
                x="country", 
                y="transaction_volume_usd",
                title="Transaction Volume by Country",
                color="country",
                color_discrete_sequence=px.colors.sequential.Turbo
            )
            st.plotly_chart(volume_fig, use_container_width=True)

# Tab 3: AI Insights
elif selected == "AI Insights":
    st.header("🤖 AI-Powered Analysis")
    user_query = st.text_input("Ask a question about the data")
    
    if st.button("Get AI Analysis"):
        ai_response = requests.post(f"{BACKEND_URL}/ai_query", 
                                  json={"question": user_query})
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            st.markdown("### 🤖 AI Analysis")
            st.markdown(ai_data["answer"])
            
            if "result" in ai_data:
                ai_df = pd.DataFrame(ai_data["result"])
                st.markdown("### 📊 Query Results")
                st.dataframe(ai_df)
        else:
            st.error(f"AI Query Failed: {ai_response.text}")

# Tab 4: Data Explorer
elif selected == "Data Explorer":
    st.header("🔍 Data Explorer")
    tables = [
        "halal_ecommerce", "e_commerce", "ict_services", 
        "islamic_fintech", "household_ict"
    ]
    selected_table = st.selectbox("Select Dataset", tables)
    
    if st.button("Load Data"):
        response = requests.get(f"{BACKEND_URL}/query/{selected_table}")
        df = pd.DataFrame(response.json() if response.status_code == 200 else [])
        st.dataframe(df)
        
        if st.checkbox("Show Summary Statistics") and not df.empty:
            st.write(df.describe())

# Summary Metrics
st.markdown("## 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    response = requests.get(f"{BACKEND_URL}/summary/halal_ecommerce")
    data = response.json() if response.status_code == 200 else {"count": 0, "avg_growth_rate": 0}
    st.metric("Total Halal Revenue", f"${data.get('count', 0) * 1000000:,.0f} USD")

with col2:
    response = requests.get(f"{BACKEND_URL}/summary/islamic_fintech")
    data = response.json() if response.status_code == 200 else {"count": 0}
    st.metric("Total Fintech Transactions", f"${data.get('count', 0) * 1000000:,.0f} USD")

with col3:
    response = requests.get(f"{BACKEND_URL}/summary/ict_services")
    data = response.json() if response.status_code == 200 else {"count": 0}
    st.metric("Total ICT Output", f"${data.get('count', 0) * 1000000:,.0f} USD")

with col4:
    response = requests.get(f"{BACKEND_URL}/summary/household_ict")
    data = response.json() if response.status_code == 200 else {"avg_growth_rate": 75.4}
    st.metric("Average Internet Usage", f"{data.get('avg_growth_rate', 75.4):.1f}%")

# Downloadable Reports
st.sidebar.markdown("## 📥 Download Reports")
all_tables = [
    "halal_ecommerce", "e_commerce", "ict_services", 
    "islamic_fintech", "household_ict"
]
selected_report = st.sidebar.selectbox("Select Report", all_tables)

if st.sidebar.button("Generate Report"):
    response = requests.get(f"{BACKEND_URL}/download/{selected_report}")
    st.sidebar.download_button(
        label="Download CSV",
        data=response.content,
        file_name=f"{selected_report}.csv",
        mime="text/csv"
    )

# Country Profile Tool
st.markdown("## 🌏 Country Profile Tool")
country_profile = st.selectbox("Select Country for Detailed Analysis", countries)

if country_profile:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {country_profile} - Halal E-commerce")
        response = requests.get(
            "{BACKEND_URL}/query/halal_ecommerce",
            params={"countries": [country_profile]}
        )
        df = pd.DataFrame(response.json() if response.status_code == 200 else [])
        st.dataframe(df)
    
    with col2:
        st.markdown(f"### {country_profile} - Fintech")
        fintech_response = requests.get(
            "{BACKEND_URL}/query/islamic_fintech",
            params={"countries": [country_profile]}
        )
        fintech_df = pd.DataFrame(fintech_response.json() if fintech_response.status_code == 200 else [])
        st.dataframe(fintech_df)
        
     # 🌐 Country-wise Total Comparison Across Sectors
st.markdown("## 🌐 Country-wise Total Comparison Across Sectors")

# List of metrics and endpoints
metrics = {
    "Halal E-commerce": "halal_ecommerce",
    "Islamic Fintech": "islamic_fintech",
    "ICT Services": "ict_services"
}

# Data structure to hold totals
country_totals = {}

# Iterate over each metric
for label, endpoint in metrics.items():
    try:
        response = requests.get(f"{BACKEND_URL}/aggregation/{endpoint}", params={"metric": "count", "group_by": "country"})
        data = response.json()
        df = pd.DataFrame(data if isinstance(data, list) else [data])
        
        for _, row in df.iterrows():
            country = row["country"]
            total = row["total"] * 1_000_000  # Convert to USD
            if country not in country_totals:
                country_totals[country] = {}
            country_totals[country][label] = total
    except:
        continue

# Create DataFrame
comparison_df = pd.DataFrame.from_dict(country_totals, orient="index").fillna(0).reset_index().rename(columns={"index": "Country"})

# Melt for stacked bar chart
melted_df = comparison_df.melt(id_vars="Country", var_name="Sector", value_name="Total (USD)")

# Plot
compare_fig = px.bar(
    melted_df,
    x="Country",
    y="Total (USD)",
    color="Sector",
    title="Total Digital Economy Metrics by Country and Sector",
    barmode="group",
    text_auto='.2s',
    color_discrete_sequence=px.colors.qualitative.Pastel
)

st.plotly_chart(compare_fig, use_container_width=True)
