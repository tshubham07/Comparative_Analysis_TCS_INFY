import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
import plotly.express as px

# Set date range
start = dt.datetime(2020, 4, 1)
end = dt.datetime(2025, 4, 7)

# Sidebar
st.sidebar.title("📊 Stock Comparison Dashboard")
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
    df['Price Range'] = df['High'] - df['Low']
    df['Average Price'] = (df['High'] + df['Low']) / 2
    df['Volatility'] = df['Close'].rolling(window=20).std()
    return df

# Cache revenue data
@st.cache_data
def get_revenue_data(ticker, name):
    try:
        t = yf.Ticker(ticker)
        df = t.quarterly_financials
        if 'Total Revenue' in df.index:
            rev = df.loc['Total Revenue'].copy().T
            rev = rev.reset_index()
            rev.columns = ['Quarter', 'Revenue']
            rev['Quarter'] = pd.to_datetime(rev['Quarter']).dt.strftime('%Y-%m-%d')
            rev['Company'] = name
            return rev
    except:
        return pd.DataFrame()
    return pd.DataFrame()

# Load all data only once
stock_data = {}
revenue_data_all = pd.DataFrame()

for stock in selected_stocks:
    ticker = stock_map[stock]
    stock_data[stock] = load_data(ticker)
    revenue = get_revenue_data(ticker, stock)
    if not revenue.empty:
        revenue = revenue.sort_values(by='Quarter')
    revenue_data_all = pd.concat([revenue_data_all, revenue], ignore_index=True)

# Tabs for layout
tab1, tab2, tab3 = st.tabs(["📈 Stock Data", "💰 Revenue Overview", "📊 Growth Insights"])

# ------------------ TAB 1: Stock Price Info ------------------
with tab1:
    for stock in selected_stocks:
        df = stock_data[stock]

        st.header(f"📈 {stock} Stock Overview")

        st.subheader("Recent Stock Data")
        st.dataframe(df.tail()[['Open', 'High', 'Low', 'Close', 'Volume']])

        st.subheader(f"{stock} - 20-Day Rolling Volatility")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=df.index, y=df['Volatility'], name='20-Day Volatility', line=dict(color='orange')))
        fig_vol.update_layout(xaxis_title="Date", yaxis_title="Volatility")
        st.plotly_chart(fig_vol)

        st.markdown("""
        #### 🔍 Insight: Volatility
        - Measures how much the stock fluctuates over time.
        - Sharp spikes = market reactions or trading surges.
        """)

        st.subheader(f"{stock} - Daily Price Range (High - Low)")
        fig_range = go.Figure()
        fig_range.add_trace(go.Scatter(x=df.index, y=df['Price Range'], name='Price Range', line=dict(color='green')))
        fig_range.update_layout(xaxis_title="Date", yaxis_title="Range")
        st.plotly_chart(fig_range)

        st.markdown("""
        #### 🔍 Insight: Price Range
        - Indicates daily price movement scale.
        - High range = more intraday opportunities.
        """)

# ------------------ TAB 2: Revenue Line & Bar ------------------
with tab2:
    if not revenue_data_all.empty:
        st.header("💰 Company Revenue Comparison")

        # Line Chart
        fig_rev = px.line(
            revenue_data_all,
            x="Quarter",
            y="Revenue",
            color="Company",
            markers=True,
            title="Quarterly Revenue Comparison (TCS vs INFY)"
        )
        st.plotly_chart(fig_rev)

        st.markdown("""
        #### 🔍 Insight
        - TCS usually has higher absolute revenue.
        - Infosys may show faster relative growth over time.
        """)

        # Latest Quarter Bar Chart
        st.subheader("📊 Latest Quarter Revenue Snapshot")
        latest_quarter = revenue_data_all['Quarter'].max()
        latest_rev = revenue_data_all[revenue_data_all['Quarter'] == latest_quarter]

        fig_bar = px.bar(
            latest_rev,
            x='Company',
            y='Revenue',
            color='Company',
            title=f'Revenue in Latest Quarter ({latest_quarter})',
            text='Revenue'
        )
        st.plotly_chart(fig_bar)

        st.markdown("""
        #### 🔍 Insight
        - Useful for latest snapshot of company performance.
        """)

# ------------------ TAB 3: Growth Insights ------------------
# ------------------ TAB 3: Growth Insights ------------------
with tab3:
    if not revenue_data_all.empty:
        st.header("📊 Revenue Growth Insights")

        # Align quarters for both companies
        aligned_quarters = revenue_data_all.groupby("Company")["Quarter"].apply(set)
        common_quarters = set.intersection(*aligned_quarters.tolist())
        aligned_df = revenue_data_all[revenue_data_all["Quarter"].isin(common_quarters)]

        # Sort and normalize revenue for growth chart
        growth_df = aligned_df.copy()
        growth_df = growth_df.sort_values(by=["Company", "Quarter"])
        growth_df['Normalized Revenue'] = growth_df.groupby("Company")["Revenue"].transform(
            lambda x: (x / x.iloc[0]) * 100
        )

        # Normalized Revenue Growth Line Chart
        st.subheader("📈 Normalized Revenue Growth Over Time")
        fig_cum = px.line(
            growth_df,
            x='Quarter',
            y='Normalized Revenue',
            color='Company',
            markers=True,
            title='Normalized Revenue Growth (Base = First Quarter)'
        )
        st.plotly_chart(fig_cum)

        st.markdown("""
        #### 🔍 Insight
        - Shows percentage growth relative to the first available quarter.
        - A steeper line indicates faster revenue growth.
        """)

        # QoQ Growth Table
        st.subheader("📉 Quarter-on-Quarter Revenue Growth (%)")
        pivot_df = aligned_df.pivot(index="Quarter", columns="Company", values="Revenue")
        growth_rate = pivot_df.pct_change().dropna() * 100
        growth_rate = growth_rate.round(2)
        st.dataframe(growth_rate)

        st.markdown("""
        #### 🔍 Insight
        - Positive = growing, negative = declining revenue.
        - Helps spot significant growth jumps or revenue drops.
        - Missing data is filtered to ensure accurate alignment.
        """)


# Optional: Add download CSV
if not revenue_data_all.empty:
    csv = revenue_data_all.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Revenue CSV",
        data=csv,
        file_name='tcs_vs_infy_revenue.csv',
        mime='text/csv'
    )






