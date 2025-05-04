import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from textblob import TextBlob

# Set date range
start = dt.datetime(2016, 1, 1)
end = dt.datetime(2023, 1, 1)

# Sidebar
st.sidebar.title("\U0001F4C8 Stock Comparison Dashboard")
selected_stocks = st.sidebar.multiselect(
    "Select companies:",
    options=["TCS", "INFY"],
    default=["TCS", "INFY"]
)

# Stock ticker map
stock_map = {
    "TCS": "TCS.NS",
    "INFY": "INFY.NS"
}

# Cache stock data
@st.cache_data
def load_data(ticker):
    df = yf.download(ticker, start=start, end=end)
    if not df.empty:
        df['Price Range'] = df['High'] - df['Low']
        df['Average Price'] = (df['High'] + df['Low']) / 2
        df['Volatility'] = df['Close'].rolling(window=20).std()
        df['Daily Return'] = (df['Close'] - df['Open']) / df['Open'] * 100
        df['Price Change'] = df['High'] - df['Low']
        df['Volatility %'] = (df['High'] - df['Low']) / df['Close'] * 100
    return df

# Cache revenue data
@st.cache_data
def get_revenue_data(ticker, name):
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_financials
        st.sidebar.write(f"Raw financials for {name}:")
        st.sidebar.write(df)
        if 'Total Revenue' in df.index:
            rev = df.loc['Total Revenue'].copy().T
            rev = rev.reset_index()
            rev.columns = ['Quarter', 'Revenue']
            rev['Quarter'] = pd.to_datetime(rev['Quarter']).dt.strftime('%Y-%m-%d')
            rev['Company'] = name
            rev['Net Profit'] = rev['Revenue'] * 0.20
            rev['Operating Margin'] = (rev['Net Profit'] / rev['Revenue']) * 100
            return rev
    except Exception as e:
        st.error(f"Failed to fetch revenue for {name}: {e}")
    return pd.DataFrame()

# Load all data only once
stock_data = {}
revenue_data_all = pd.DataFrame()

for stock in selected_stocks:
    ticker = stock_map[stock]
    st.sidebar.write(f"Loading stock data for {stock}...")
    df = load_data(ticker)
    if df.empty:
        st.sidebar.error(f"❌ No stock data for {stock}")
    else:
        stock_data[stock] = df

    st.sidebar.write(f"Loading revenue data for {stock}...")
    revenue = get_revenue_data(ticker, stock)
    if not revenue.empty:
        revenue = revenue.sort_values(by='Quarter')
        revenue_data_all = pd.concat([revenue_data_all, revenue], ignore_index=True)
    else:
        st.sidebar.warning(f"⚠️ No revenue data for {stock}")

# Debug Tab
st.sidebar.markdown("---")
if st.sidebar.checkbox("Show Debug Data"):
    st.subheader("\U0001F50E Debug Output")
    for stock in selected_stocks:
        st.write(f"**{stock} Stock Data (Last 5 rows):**")
        st.dataframe(stock_data.get(stock, pd.DataFrame()).tail())
    if not revenue_data_all.empty:
        st.write("**Revenue Data (Last 5 rows):**")
        st.dataframe(revenue_data_all.tail())

# Tabs for layout
tab1, tab2, tab3 = st.tabs(["\U0001F4C8 Stock Data", "\U0001F4B0 Revenue Overview", "\U0001F4CA Growth Insights"])

# TAB 1: Stock Price Info
with tab1:
    for stock in selected_stocks:
        df = stock_data.get(stock, pd.DataFrame())
        if df.empty:
            continue

        st.header(f"\U0001F4C8 {stock} Stock Overview")

        st.subheader("Recent Stock Data")
        st.dataframe(df.tail()[['Open', 'High', 'Low', 'Close', 'Volume']])

        st.subheader(f"{stock} - Daily Return (%)")
        fig_ret = px.line(df, x=df.index, y='Daily Return', title=f"{stock} Daily Return (%)")
        st.plotly_chart(fig_ret)

        st.subheader(f"{stock} - Volatility (%)")
        fig_vol = px.line(df, x=df.index, y='Volatility %', title=f"{stock} Volatility (%)")
        st.plotly_chart(fig_vol)

        st.subheader(f"{stock} - Price Range (High - Low)")
        fig_range = px.line(df, x=df.index, y='Price Range', title=f"{stock} Daily Price Range")
        st.plotly_chart(fig_range)

        st.subheader(f"{stock} - Average Price")
        fig_avg = px.line(df, x=df.index, y='Average Price', title=f"{stock} Average Price")
        st.plotly_chart(fig_avg)


with tab2:
    if not revenue_data_all.empty:
        st.header("💰 Company Revenue Overview")

        # 🔹 Line chart for quarterly revenue
        st.subheader("📈 Quarterly Revenue Comparison")
        fig_rev = px.line(
            revenue_data_all,
            x="Quarter",
            y="Revenue",
            color="Company",
            markers=True,
            title="Quarterly Revenue Trend"
        )
        st.plotly_chart(fig_rev, use_container_width=True)

        st.subheader("📊 Latest Quarter Financial Snapshot")
        latest_quarter = revenue_data_all["Quarter"].max()
        snapshot_df = revenue_data_all[revenue_data_all["Quarter"] == latest_quarter]

        col1, col2, col3 = st.columns(3)

        # TCS Revenue Metric
        with col1:
            try:
                tcs_rev = snapshot_df[snapshot_df['Company'] == 'TCS']['Revenue'].values[0]
                st.metric("TCS Revenue", f"₹{tcs_rev:,.0f}")
            except:
                st.metric("TCS Revenue", "No Data")

        # INFY Revenue Metric
        with col2:
            try:
                infy_rev = snapshot_df[snapshot_df['Company'] == 'INFY']['Revenue'].values[0]
                st.metric("INFY Revenue", f"₹{infy_rev:,.0f}")
            except:
                st.metric("INFY Revenue", "No Data")

        # Revenue Gap
        with col3:
            try:
                if tcs_rev and infy_rev:
                    gap = tcs_rev - infy_rev
                    gap_label = "TCS - INFY" if gap > 0 else "INFY - TCS"
                    st.metric(f"Revenue Gap ({gap_label})", f"₹{abs(gap):,.0f}")
                else:
                    st.metric("Revenue Gap", "Insufficient Data")
            except:
                st.metric("Revenue Gap", "Error")

        # Revenue vs Net Profit Bar chart
        st.subheader("📊 Revenue and Net Profit Comparison")
        bar_data = revenue_data_all.copy()
        bar_data_melt = bar_data.melt(
            id_vars=["Quarter", "Company"],
            value_vars=["Revenue", "Net Profit"],
            var_name="Metric",
            value_name="Amount"
        )

        fig_bar = px.bar(
            bar_data_melt,
            x="Quarter",
            y="Amount",
            color="Metric",
            barmode="group",
            facet_col="Company",
            title="Revenue vs Net Profit per Quarter",
            labels={"Amount": "₹ Amount"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📉 Operating Margin (%)")
        fig_margin = px.line(
            revenue_data_all,
            x="Quarter",
            y="Operating Margin",
            color="Company",
            markers=True,
            title="Operating Margin Over Time"
        )
        st.plotly_chart(fig_margin, use_container_width=True)

# TAB 3: Growth Insights
with tab3:
    if not revenue_data_all.empty:
        st.header("📈 Revenue Growth Insights")

        # Align quarters for both companies
        aligned_quarters = revenue_data_all.groupby("Company")["Quarter"].apply(set)
        common_quarters = set.intersection(*aligned_quarters.tolist())
        aligned_df = revenue_data_all[revenue_data_all["Quarter"].isin(common_quarters)]

        # Normalize revenue
        growth_df = aligned_df.copy()
        growth_df = growth_df.sort_values(by=["Company", "Quarter"])
        growth_df['Normalized Revenue'] = growth_df.groupby("Company")["Revenue"].transform(
            lambda x: (x / x.iloc[0]) * 100
        )

        st.subheader("📊 Normalized Revenue Growth")
        fig_cum = px.line(
            growth_df,
            x='Quarter',
            y='Normalized Revenue',
            color='Company',
            markers=True,
            title='Normalized Revenue Growth (Base=100)'
        )
        st.plotly_chart(fig_cum)

       # Financial KPIs like CAGR and YoY growth
st.subheader("📉 CAGR & YoY Growth Analysis")

def calculate_cagr(start_value, end_value, years):
    if start_value == 0 or end_value == 0 or years <= 0:
        return np.nan  # return NaN if values are not valid for CAGR calculation
    return ((end_value / start_value) ** (1 / years) - 1) * 100

def calculate_yoy_growth(current_value, previous_value):
    if previous_value == 0:
        return np.nan  # return NaN if previous value is zero
    return ((current_value - previous_value) / previous_value) * 100

# Debugging: Check the structure of the data
st.write("Checking the available data for TCS and INFY:")
st.write(growth_df[growth_df['Company'] == 'TCS'])
st.write(growth_df[growth_df['Company'] == 'INFY'])

# Get the first and last revenue values for CAGR calculation
tcs_revenue = growth_df[growth_df['Company'] == 'TCS']['Revenue']
infy_revenue = growth_df[growth_df['Company'] == 'INFY']['Revenue']

# Debugging: Check the selected revenue data for both companies
st.write("TCS Revenue Data:")
st.write(tcs_revenue)

st.write("INFY Revenue Data:")
st.write(infy_revenue)

# Ensure there is enough data for the calculation
if len(tcs_revenue) >= 2 and len(infy_revenue) >= 2:
    cagr_tcs = calculate_cagr(
        tcs_revenue.iloc[0],  # First quarter revenue
        tcs_revenue.iloc[-1],  # Last quarter revenue
        len(tcs_revenue) / 4  # Number of years (assuming quarterly data)
    )

    cagr_infy = calculate_cagr(
        infy_revenue.iloc[0],
        infy_revenue.iloc[-1],
        len(infy_revenue) / 4
    )
else:
    cagr_tcs = cagr_infy = np.nan

# YoY Growth for most recent quarter
if len(tcs_revenue) > 4 and len(infy_revenue) > 4:  # Check if we have at least 5 quarters
    yoy_tcs = calculate_yoy_growth(
        tcs_revenue.iloc[-1],  # Most recent quarter revenue
        tcs_revenue.iloc[-5]   # Revenue from the same quarter last year
    )

    yoy_infy = calculate_yoy_growth(
        infy_revenue.iloc[-1],
        infy_revenue.iloc[-5]  # Same as TCS
    )
else:
    yoy_tcs = yoy_infy = np.nan

# Display KPIs
st.write(f"**CAGR for TCS:** {cagr_tcs:.2f}%") if not np.isnan(cagr_tcs) else st.write("**CAGR for TCS:** Insufficient Data")
st.write(f"**CAGR for INFY:** {cagr_infy:.2f}%") if not np.isnan(cagr_infy) else st.write("**CAGR for INFY:** Insufficient Data")
st.write(f"**YoY Growth for TCS:** {yoy_tcs:.2f}%") if not np.isnan(yoy_tcs) else st.write("**YoY Growth for TCS:** Insufficient Data")
st.write(f"**YoY Growth for INFY:** {yoy_infy:.2f}%") if not np.isnan(yoy_infy) else st.write("**YoY Growth for INFY:** Insufficient Data")