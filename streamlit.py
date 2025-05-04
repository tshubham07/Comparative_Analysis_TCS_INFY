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

# Cache data loading
@st.cache_data
def load_data(ticker):
    df = yf.download(ticker, start=start, end=end)
    df['Price Range'] = df['High'] - df['Low']
    df['Average Price'] = (df['High'] + df['Low']) / 2
    df['Volatility'] = df['Close'].rolling(window=20).std()
    return df

# Get revenue data
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
    except Exception as e:
        st.warning(f"⚠️ Revenue data not available for {name}")
        return pd.DataFrame()
    return pd.DataFrame()

# Store all revenue data
all_revenue = pd.DataFrame()

# Display stock info
for stock in selected_stocks:
    st.header(f"📈 {stock} Stock Overview")
    df = load_data(stock_map[stock])
    
    st.subheader("Recent Stock Data")
    st.dataframe(df.tail()[['Open', 'High', 'Low', 'Close', 'Volume']])

    # Volatility chart
    st.subheader(f"{stock} - 20-Day Rolling Volatility")
    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(x=df.index, y=df['Volatility'], name='20-Day Volatility', line=dict(color='orange')))
    fig_vol.update_layout(xaxis_title="Date", yaxis_title="Volatility")
    st.plotly_chart(fig_vol)

    # Volatility insight
    st.markdown(f"""
    #### 🔍 Insight: Volatility
    - {stock}'s volatility shows how much the stock fluctuates over time.
    - If the line is relatively flat, it indicates **stable price movement**.
    - Sharp spikes may suggest **market reactions or trading volume surges**.
    """)

    # Price range chart
    st.subheader(f"{stock} - Daily Price Range (High - Low)")
    fig_range = go.Figure()
    fig_range.add_trace(go.Scatter(x=df.index, y=df['Price Range'], name='Price Range', line=dict(color='green')))
    fig_range.update_layout(xaxis_title="Date", yaxis_title="Range")
    st.plotly_chart(fig_range)

    # Price range insight
    st.markdown(f"""
    #### 🔍 Insight: Price Range
    - The **daily price range** gives an idea of how much the stock moves during a single day.
    - Higher ranges might mean **more short-term trading opportunities**.
    - Consistent low ranges suggest **less intraday volatility**.
    """)

    # Append revenue data
    revenue_data = get_revenue_data(stock_map[stock], stock)
    all_revenue = pd.concat([all_revenue, revenue_data], ignore_index=True)

# Revenue visualization
if not all_revenue.empty:
    st.header("💰 Company Revenue Comparison")
    fig_rev = px.line(
        all_revenue,
        x="Quarter",
        y="Revenue",
        color="Company",
        markers=True,
        title="Quarterly Revenue Comparison (TCS vs INFY)"
    )
    st.plotly_chart(fig_rev)

    # Revenue insights
    st.markdown("""
    #### 🔍 Insight: Revenue Comparison
    - TCS generally has higher quarterly revenue compared to Infosys, reflecting a **larger scale** of operations.
    - However, a **steeper upward trend** in Infosys revenue could indicate **faster growth**.
    - Watching quarterly revenue trends helps assess **business performance and expansion**.
    """)
else:
    st.warning("No revenue data available to display.")







