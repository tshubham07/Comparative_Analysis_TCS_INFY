# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from io import BytesIO

st.set_page_config(page_title="TCS vs Infosys - Simple Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    tcs = pd.read_csv("C:/Users/91797/Downloads/financial_performance_TCS.csv")
    infosys = pd.read_csv("C:/Users/91797/Downloads/financial_performance_Infosys.csv")
    tcs['Date'] = pd.to_datetime(tcs['Date'])
    infosys['Date'] = pd.to_datetime(infosys['Date'])
    tcs['Year'] = tcs['Date'].dt.year
    infosys['Year'] = infosys['Date'].dt.year
    return tcs, infosys

tcs, infosys = load_data()

# Title with emoji using markdown to avoid encoding issues
st.markdown("## 📊 Comparative Financial Performance Analysis of TCS and Infosys")

# Sidebar Content
st.sidebar.header("🔧 Dashboard Controls")
st.sidebar.markdown("""
This dashboard provides a comparative analysis of the financial performance of **TCS** and **Infosys**. 
You can explore various KPIs, revenue trends, financial ratios, and more.
""")

# Sidebar
option = st.sidebar.selectbox("Select Company", ["TCS", "Infosys", "Both"])

# Filtered data
if option == "TCS":
    data = tcs
elif option == "Infosys":
    data = infosys
else:
    tcs['Company'] = 'TCS'
    infosys['Company'] = 'Infosys'
    data = pd.concat([tcs, infosys])

# KPI Cards
st.subheader("📌 Key Performance Indicators")
if option != "Both":
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Revenue", f"{data['Revenue'].mean():,.2f}")
    col2.metric("Avg Net Profit", f"{data['Net_Profit'].mean():,.2f}")
    col3.metric("Avg Operating Margin", f"{data['Operating_Margin'].mean():.2f}%")
    col4.metric("Avg Volatility", f"{data['Volatility'].mean():.2f}")

# Revenue Trend
st.subheader("📈 Revenue Trend")
if option != "Both":
    st.line_chart(data.groupby('Year')['Revenue'].mean())
else:
    chart_data = data.groupby(['Year', 'Company'])['Revenue'].mean().unstack()
    st.line_chart(chart_data)

# Net Profit Trend
st.subheader("💰 Net Profit Trend")
if option != "Both":
    st.line_chart(data.groupby('Year')['Net_Profit'].mean())
else:
    profit_data = data.groupby(['Year', 'Company'])['Net_Profit'].mean().unstack()
    st.line_chart(profit_data)

# CAGR Comparison
st.subheader("📊 CAGR Comparison")
def calculate_cagr(start_value, end_value, periods):
    return ((end_value / start_value) ** (1 / periods) - 1) * 100

if option == "Both":
    start_year = data['Year'].min()
    end_year = data['Year'].max()
    tcs_cagr = calculate_cagr(
        tcs[tcs['Year'] == start_year]['Revenue'].mean(),
        tcs[tcs['Year'] == end_year]['Revenue'].mean(),
        end_year - start_year)
    info_cagr = calculate_cagr(
        infosys[infosys['Year'] == start_year]['Revenue'].mean(),
        infosys[infosys['Year'] == end_year]['Revenue'].mean(),
        end_year - start_year)
    st.table(pd.DataFrame({
        'Company': ['TCS', 'Infosys'],
        'CAGR (%)': [round(tcs_cagr, 2), round(info_cagr, 2)]
    }))

# Future Revenue Forecast
st.subheader("📅 Future Revenue Forecast (Estimated)")
def forecast(df):
    df = df.sort_values('Year')
    growth_rate = df.groupby('Year')['Revenue'].mean().pct_change().mean()
    last_year = df['Year'].max()
    last_value = df[df['Year'] == last_year]['Revenue'].mean()
    forecast_years = [last_year + i for i in range(1, 4)]
    forecast_values = [last_value * ((1 + growth_rate) ** i) for i in range(1, 4)]
    return pd.DataFrame({'Year': forecast_years, 'Forecast Revenue': forecast_values})

if option != "Both":
    forecast_df = forecast(data)
    st.line_chart(forecast_df.set_index('Year'))
else:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**TCS Forecast**")
        tcs_forecast = forecast(tcs)
        st.line_chart(tcs_forecast.set_index('Year'))
    with col2:
        st.markdown("**Infosys Forecast**")
        infosys_forecast = forecast(infosys)
        st.line_chart(infosys_forecast.set_index('Year'))

# Financial Ratios
st.subheader("📊 Financial Ratios Comparison")
def compute_ratios(df):
    df = df.copy()
    df['Operating Margin (%)'] = df['Operating_Margin']
    df['Net Profit Margin (%)'] = (df['Net_Profit'] / df['Revenue']) * 100
    return df[['Year', 'Operating Margin (%)', 'Net Profit Margin (%)']]

if option == "Both":
    tcs_ratios = compute_ratios(tcs).mean(numeric_only=True)
    infosys_ratios = compute_ratios(infosys).mean(numeric_only=True)
    ratio_df = pd.DataFrame({
        'Ratios': ['Operating Margin (%)', 'Net Profit Margin (%)'],
        'TCS': [tcs_ratios['Operating Margin (%)'], tcs_ratios['Net Profit Margin (%)']],
        'Infosys': [infosys_ratios['Operating Margin (%)'], infosys_ratios['Net Profit Margin (%)']]
    })
    st.bar_chart(ratio_df.set_index('Ratios'))

# Price-related Visuals
st.subheader("📉 Price Analysis")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Average Price Trend**")
    if option != "Both":
        avg_data = data.groupby('Year')['Average_price'].mean()
        st.line_chart(avg_data)
    else:
        avg_data = data.groupby(['Year', 'Company'])['Average_price'].mean().unstack()
        st.line_chart(avg_data)
with col2:
    st.markdown("**Volatility Trend**")
    if option != "Both":
        vol_data = data.groupby('Year')['Volatility'].mean()
        st.line_chart(vol_data)
    else:
        vol_data = data.groupby(['Year', 'Company'])['Volatility'].mean().unstack()
        st.line_chart(vol_data)

# Daily Return & Volume
st.subheader("📊 Daily Return & Volume Analysis")
col3, col4 = st.columns(2)
with col3:
    st.markdown("**Daily Return Trend**")
    if option != "Both":
        dr = data.groupby('Year')['daily_return'].mean()
        st.line_chart(dr)
    else:
        dr = data.groupby(['Year', 'Company'])['daily_return'].mean().unstack()
        st.line_chart(dr)
with col4:
    st.markdown("**Volume Trend**")
    if option != "Both":
        vol = data.groupby('Year')['Volume'].mean()
        st.line_chart(vol)
    else:
        vol = data.groupby(['Year', 'Company'])['Volume'].mean().unstack()
        st.line_chart(vol)

# Comparison Graphs
st.subheader("📊 Side-by-Side Financial Comparison")
if option == "Both":
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("**Grouped Bar: Revenue & Net Profit**")
        grouped_df = data.groupby(['Year', 'Company'])[['Revenue', 'Net_Profit']].mean().reset_index()
        fig1 = px.bar(grouped_df, x='Year', y='Revenue', color='Company', barmode='group', title="Revenue Comparison")
        st.plotly_chart(fig1, use_container_width=True)
        fig1.write_html("revenue_comparison.html")

    with col6:
        st.markdown("**Scatter: Revenue vs Net Profit**")
        scatter_df = data.groupby(['Year', 'Company'])[['Revenue', 'Net_Profit']].mean().reset_index()
        fig2 = px.scatter(scatter_df, x='Revenue', y='Net_Profit', color='Company', size='Revenue', hover_name='Year', title="Revenue vs Net Profit")
        st.plotly_chart(fig2, use_container_width=True)
        fig2.write_html("revenue_vs_profit.html")

# News Sentiment Placeholder
st.subheader("📰 News Sentiment Analysis (Coming Soon)")
st.info("News Sentiment Section will analyze TCS and Infosys mentions from financial news using sentiment scoring (positive, neutral, negative).")

# Export Insights
st.subheader("📝 Insights and Export")
if option == "Both":
    st.markdown("- TCS generally shows higher average revenue and net profit over the years.")
    st.markdown("- Infosys displays a more consistent volatility pattern.")
    st.markdown("- TCS has slightly better financial ratios on average.")
    st.markdown("- Volume trends indicate higher trading activity for Infosys in recent years.")

    if st.button("Export Insights to CSV"):
        insights = pd.DataFrame({
            'Key Insight': [
                'TCS shows higher average revenue and profit.',
                'Infosys shows more consistent volatility.',
                'TCS has better financial ratios.',
                'Infosys trading volume is increasing.'
            ]
        })
        insights.to_csv("TCS_vs_Infosys_Insights.csv", index=False)
        st.success("Insights exported as TCS_vs_Infosys_Insights.csv")


