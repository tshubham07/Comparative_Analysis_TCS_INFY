import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression

# Set page config
st.set_page_config(page_title="TCS vs Infosys Dashboard", layout="wide")

# Sidebar controls
st.sidebar.title("🔍 Dashboard Controls")

company_choice = st.sidebar.radio(
    "Select Company View:",
    ("Both", "TCS", "Infosys"),
    index=0
)

show_sections = st.sidebar.multiselect(
    "Select Sections to Display",
    ["Revenue Trends", "YoY Growth", "CAGR", "Volatility", "Forecast", "Financial Ratios", "Sentiment Analysis"],
    default=["Revenue Trends", "YoY Growth", "CAGR", "Volatility", "Forecast", "Financial Ratios", "Sentiment Analysis"]
)

# Title and Summary
st.title("📊 Comparative Revenue Performance Analysis of TCS and Infosys")

st.markdown("""
### 📘 Executive Summary

This dashboard presents a comparative revenue performance analysis of **TCS** and **Infosys** from 2016 to 2023, with forecasts through 2026.

- TCS leads in absolute revenue, while Infosys shows a slightly higher CAGR.
- Both companies exhibit consistent growth with some volatility.
- TCS has stronger profitability metrics.
- Sentiment remains largely positive for both companies.
""")


# Data
years = list(range(2016, 2024))
tcs_revenue = [108.78, 117.97, 128.49, 139.72, 152.56, 167.31, 183.65, 198.45]
infosys_revenue = [68.48, 70.52, 80.24, 88.22, 94.96, 105.08, 121.64, 135.15]

df_rev = pd.DataFrame({"Year": years, "TCS": tcs_revenue, "Infosys": infosys_revenue})
df_growth = df_rev.copy()
df_growth["TCS YoY (%)"] = df_growth["TCS"].pct_change() * 100
df_growth["Infosys YoY (%)"] = df_growth["Infosys"].pct_change() * 100

# Revenue Trends
if "Revenue Trends" in show_sections:
    st.subheader("1. 📁 Revenue Trends Over Time")
    st.markdown("""
- TCS consistently leads in revenue from 2016 to 2023.
- Both companies show a clear upward trend.
- Revenue growth is steady and predictable.
- No negative revenue dips in the observed period.
""")
    y_columns = {"Both": ["TCS", "Infosys"], "TCS": ["TCS"], "Infosys": ["Infosys"]}[company_choice]
    fig = px.line(df_rev, x="Year", y=y_columns, markers=True, title="Annual Revenue (\u20b9K Cr)",
                  color_discrete_map={"TCS": "#1f77b4", "Infosys": "#ff7f0e"})
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

# YoY Growth
if "YoY Growth" in show_sections:
    st.subheader("2. 📊 YoY Growth Comparison")
    st.markdown("""
- Shows yearly momentum of revenue changes.
- Positive but fluctuating growth for both.
- Peaks may indicate exceptional performance.
- Drops hint at market or internal slowdowns.
""")
    y_columns = {"Both": ["TCS YoY (%)", "Infosys YoY (%)"], "TCS": ["TCS YoY (%)"], "Infosys": ["Infosys YoY (%)"]}[company_choice]
    fig = px.bar(df_growth.dropna(), x="Year", y=y_columns, barmode="group", title="YoY Growth (%)",
                 color_discrete_map={"TCS YoY (%)": "#1f77b4", "Infosys YoY (%)": "#ff7f0e"})
    st.plotly_chart(fig, use_container_width=True)

# CAGR
if "CAGR" in show_sections:
    st.subheader("3. 📈 CAGR Comparison")
    st.markdown("""
- Reflects long-term growth efficiency.
- Infosys has slightly higher CAGR.
- Indicates Infosys' agility despite smaller base.
- Both companies sustain 10%+ growth.
""")
    def calculate_cagr(start, end, periods):
        return ((end/start) ** (1/periods) - 1) * 100
    data = []
    if company_choice in ["Both", "TCS"]:
        data.append(["TCS", round(calculate_cagr(tcs_revenue[0], tcs_revenue[-1], len(years)-1), 2)])
    if company_choice in ["Both", "Infosys"]:
        data.append(["Infosys", round(calculate_cagr(infosys_revenue[0], infosys_revenue[-1], len(years)-1), 2)])
    cagr_df = pd.DataFrame(data, columns=["Company", "CAGR (%)"])
    fig = px.bar(cagr_df, x="Company", y="CAGR (%)", color="Company", title="CAGR Comparison",
                 color_discrete_map={"TCS": "#1f77b4", "Infosys": "#ff7f0e"})
    st.plotly_chart(fig, use_container_width=True)

# Volatility
if "Volatility" in show_sections:
    st.subheader("4. 📉 Revenue Volatility")
    st.markdown("""
- Standard deviation measures fluctuations.
- Infosys shows slightly more variability.
- TCS's stability may indicate mature operations.
- Useful to assess risk profiles.
""")
    data = []
    if company_choice in ["Both", "TCS"]:
        data.append(["TCS", np.std(tcs_revenue)])
    if company_choice in ["Both", "Infosys"]:
        data.append(["Infosys", np.std(infosys_revenue)])
    volatility_df = pd.DataFrame(data, columns=["Company", "Revenue SD"])
    fig = px.bar(volatility_df, x="Company", y="Revenue SD", color="Company",
                 title="Revenue Standard Deviation",
                 color_discrete_map={"TCS": "#1f77b4", "Infosys": "#ff7f0e"})
    st.plotly_chart(fig, use_container_width=True)

# Forecast
if "Forecast" in show_sections:
    st.subheader("5. 🤔 Revenue Forecast (2024–2026)")
    st.markdown("""
- Forecast based on linear regression.
- Predicts continued revenue increase.
- TCS likely to maintain lead.
- Useful for investment or strategy decisions.
""")
    X = np.array(years).reshape(-1, 1)
    future_years = np.array([2024, 2025, 2026]).reshape(-1, 1)
    forecast_data = {"Year": years + list(future_years.flatten())}
    if company_choice in ["Both", "TCS"]:
        model_tcs = LinearRegression().fit(X, tcs_revenue)
        forecast_data["TCS"] = tcs_revenue + list(model_tcs.predict(future_years))
    if company_choice in ["Both", "Infosys"]:
        model_infosys = LinearRegression().fit(X, infosys_revenue)
        forecast_data["Infosys"] = infosys_revenue + list(model_infosys.predict(future_years))
    df_forecast = pd.DataFrame(forecast_data)
    y_columns = [col for col in ["TCS", "Infosys"] if col in df_forecast.columns]
    fig = px.line(df_forecast, x="Year", y=y_columns, markers=True,
                  title="Revenue Forecast (2024–2026)",
                  color_discrete_map={"TCS": "#1f77b4", "Infosys": "#ff7f0e"})
    fig.update_traces(line=dict(width=3))
    st.plotly_chart(fig, use_container_width=True)

# Financial Ratios
if "Financial Ratios" in show_sections:
    st.subheader("6. 📄 Financial Ratios Comparison")
    st.markdown("""
- TCS leads in profitability and efficiency.
- Net profit and ROE are significantly stronger.
- Operating margin shows better cost control.
- Ratios show business quality over raw numbers.
""")
    ratios = {
        "Metric": ["Net Profit Margin", "Operating Margin", "ROE"],
        "TCS": [23.6, 26.0, 38.0],
        "Infosys": [20.7, 24.5, 31.2]
    }
    ratios_df = pd.DataFrame(ratios)
    if company_choice != "Both":
        ratios_df = ratios_df[["Metric", company_choice]]
    melted = ratios_df.melt(id_vars="Metric", var_name="Company", value_name="Value")
    fig = px.bar(melted, x="Metric", y="Value", color="Company", barmode="group",
                 title="Financial Efficiency Metrics",
                 color_discrete_map={"TCS": "#1f77b4", "Infosys": "#ff7f0e"})
    st.plotly_chart(fig, use_container_width=True)

# Sentiment Analysis
if "Sentiment Analysis" in show_sections:
    st.subheader("7. 😊 News Sentiment Analysis")
    st.markdown("""
- Sentiment shows public/media perception.
- Positive news dominates for both firms.
- Reflects stable reputation and trust.
- Negative sentiment is very low.
""")
    sentiment_df = pd.DataFrame({
        "Company": ["TCS", "Infosys"],
        "Positive": [65, 50],
        "Neutral": [30, 35],
        "Negative": [5, 15]
    }).set_index("Company")
    if company_choice != "Both":
        sentiment_df = sentiment_df.loc[[company_choice]]
    fig = px.bar(sentiment_df, barmode="stack", title="News Sentiment Overview",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
