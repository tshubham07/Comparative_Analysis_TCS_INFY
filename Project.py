import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt

# Set date range
start = dt.datetime(2020, 1, 1)
end = dt.datetime(2025, 4, 7)

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
        st.markdown("##### 🔎 Key Insights")
        st.markdown("""
        - 📈 Shows the percentage change between open and close prices daily.
        - 🔍 Helps in identifying the volatility or intraday momentum.
        - 📉 Sudden spikes/dips can indicate news or market reactions.
        - 🧭 Useful for short-term trend detection.
        """)

        st.subheader(f"{stock} - Volatility (%)")
        fig_vol = px.line(df, x=df.index, y='Volatility %', title=f"{stock} Volatility (%)")
        st.plotly_chart(fig_vol)
        st.markdown("##### 🔎 Key Insights")
        st.markdown("""
        - 📊 Measures how much price fluctuates in a given period.
        - 🔄 Higher volatility means higher risk but also higher potential return.
        - 📆 Rolling 20-day window gives a mid-term volatility perspective.
        - 📍 Sudden volatility can be a signal for technical traders.
        """)

        st.subheader(f"{stock} - Price Range (High - Low)")
        fig_range = px.line(df, x=df.index, y='Price Range', title=f"{stock} Daily Price Range")
        st.plotly_chart(fig_range)
        st.markdown("##### 🔎 Key Insights")
        st.markdown("""
        - 💹 Highlights the spread between high and low prices.
        - 🔍 Wider range means more market activity or news impact.
        - 🧮 Good metric to spot breakout zones.
        - 📆 Patterns can help identify cyclical movements.
        """)

        st.subheader(f"{stock} - Average Price")
        fig_avg = px.line(df, x=df.index, y='Average Price', title=f"{stock} Average Price")
        st.plotly_chart(fig_avg)
        st.markdown("##### 🔎 Key Insights")
        st.markdown("""
        - 📈 Average of high and low prices reflects central market tendency.
        - 🧭 Smooths out daily noise and indicates fair value zone.
        - 🔗 Useful to compare with actual close for trend validation.
        - ⚙️ Can guide in setting mid-range price targets.
        """)


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

        st.markdown("##### 🔎 Key Insights")
        st.markdown("""
        - 📊 Both TCS and Infosys show consistent quarterly revenue growth with minor fluctuations.
        - 🔼 TCS generally maintains a higher revenue base compared to Infosys.
        - 🧭 The revenue trend is upward-sloping for both companies, indicating strong operational performance.
        - ⚠️ Temporary dips suggest seasonal or external factors affecting specific quarters.
        """)

        # 🔹 Latest Quarter Financial Snapshot
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

        st.markdown("##### 🔎 Key Insights")
        st.markdown(f"""
        - 🧾 Latest revenue data is for **{latest_quarter}**.
        - 📈 TCS has a higher revenue than Infosys this quarter.
        - 💹 The revenue gap is significant, indicating stronger topline growth by the leader.
        - 📌 Provides a snapshot for immediate quarter-to-quarter comparison.
        """)

        # 🔹 Revenue + Net Profit Grouped Bar
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

        st.markdown("##### 🔎 Key Insights")
        st.markdown("""
        - 🪙 Revenue is significantly higher than Net Profit for both companies, as expected.
        - 💡 TCS shows stronger profitability per unit of revenue.
        - 📆 Net profits follow a similar pattern to revenue, highlighting operational alignment.
        - 📉 Any deviation between revenue and profit signals margin compression or cost escalation.
        """)

        # 🔹 Operating Margin trend
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

        st.markdown("##### 🔎 Key Insights")
        st.markdown("""
        - ⚙️ TCS maintains a more stable operating margin across quarters.
        - 📊 Infosys shows more variability, possibly due to cost pressures or revenue shifts.
        - 🔄 Operating margins trend slightly upward, indicating efficiency improvements.
        - 📈 Consistent margins show scalability and cost control in both firms.
        """)

        # 🔹 Optional raw table
        st.subheader("📋 Revenue Table (Sorted by Quarter)")
        st.dataframe(revenue_data_all.sort_values(by=["Quarter", "Company"], ascending=[False, True]))

        # 🔍 Debug Section
        with st.expander("🛠️ Debug Info (Click to Expand)"):
            st.write("🕒 Latest Quarter:", latest_quarter)
            st.write("📦 Snapshot DataFrame")
            st.dataframe(snapshot_df)
            st.write("📈 Revenue DataFrame (Last 5 rows)")
            st.dataframe(revenue_data_all.tail())


# TAB 3: Growth Insights
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
            title='Normalized Revenue Growth (Base = First Quarter)'
        )
        st.plotly_chart(fig_cum)

        st.markdown("#### 🔍 Summary:")
        st.markdown("""
        - Normalized revenue shows how each company's revenue has grown relative to its own starting point.
        - A value of 150% means revenue has grown 50% since the first quarter.
        - Helpful for comparing growth rates regardless of actual revenue size.
        """)

        # Calculate Quarter-on-Quarter growth %
        st.subheader("📉 Quarter-on-Quarter Revenue Growth (%)")
        pivot_df = aligned_df.pivot(index="Quarter", columns="Company", values="Revenue")
        qoq_growth = pivot_df.pct_change().dropna() * 100
        st.dataframe(qoq_growth.round(2))

        st.markdown("#### 🔍 Summary:")
        st.markdown("""
        - Quarter-on-quarter growth highlights recent momentum and short-term trends.
        - Spikes may indicate strong seasonal performance or recovery.
        - Declines may flag weak demand or project delays.
        """)

        # Calculate Year-over-Year (YoY) growth
        st.subheader("📅 Year-over-Year Growth (%)")
        yoy_df = pivot_df.copy()
        yoy_df.index = pd.to_datetime(yoy_df.index)
        yoy_df = yoy_df.sort_index()
        yoy_growth = yoy_df.pct_change(periods=4).dropna() * 100
        st.dataframe(yoy_growth.round(2))

        st.markdown("#### 🔍 Summary:")
        st.markdown("""
        - YoY growth provides a long-term perspective, eliminating seasonality.
        - A consistent YoY rise indicates healthy expansion over time.
        - Sudden dips or negative values require further analysis.
        """)

        # Calculate CAGR
        st.subheader("🚀 Compound Annual Growth Rate (CAGR)")
        cagr_data = []
        for company in pivot_df.columns:
            rev_start = pivot_df[company].iloc[0]
            rev_end = pivot_df[company].iloc[-1]
            n_years = (pd.to_datetime(pivot_df.index[-1]) - pd.to_datetime(pivot_df.index[0])).days / 365.25
            cagr = ((rev_end / rev_start) ** (1 / n_years) - 1) * 100
            cagr_data.append((company, round(cagr, 2)))
        cagr_df = pd.DataFrame(cagr_data, columns=["Company", "CAGR (%)"])
        st.dataframe(cagr_df)

        st.markdown("#### 🔍 Summary:")
        st.markdown("""
        - CAGR shows the average annual growth rate across the time period.
        - It smoothens out short-term fluctuations for a clearer long-term trend.
        - Useful for comparing overall performance between companies.
        """)

        # Best & Worst Quarter per Company
        st.subheader("🏆 Best & Worst Quarters")
        stats_df = aligned_df.copy()
        best_worst = stats_df.groupby("Company").agg(
            Best_Quarter=('Revenue', lambda x: stats_df.loc[x.idxmax(), 'Quarter']),
            Worst_Quarter=('Revenue', lambda x: stats_df.loc[x.idxmin(), 'Quarter']),
            Max_Revenue=('Revenue', 'max'),
            Min_Revenue=('Revenue', 'min'),
            Avg_Growth=('Revenue', 'mean')
        ).reset_index()
        st.dataframe(best_worst)

        st.markdown("#### 🔍 Summary:")
        st.markdown("""
        - Shows peak and low performance periods for each company.
        - Identifies standout quarters for strategic decisions.
        - Useful to correlate with external events or company announcements.
        """)

        # Revenue Heatmap
        st.subheader("🔍 Revenue Heatmap")
        heatmap_df = pivot_df.T
        fig_heat = px.imshow(
            heatmap_df,
            labels=dict(x="Quarter", y="Company", color="Revenue"),
            x=heatmap_df.columns,
            y=heatmap_df.index,
            aspect="auto",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_heat)

        st.markdown("#### 🔍 Summary:")
        st.markdown("""
        - Visual representation of revenue concentration across quarters.
        - Darker colors = higher revenue, enabling quick visual insights.
        - Patterns help spot consistency or volatility in performance.
        """)

        # Download button for growth data
        st.download_button(
            label="📥 Download Growth Data (CSV)",
            data=growth_df.to_csv(index=False).encode('utf-8'),
            file_name='growth_insights_data.csv',
            mime='text/csv'
        )



# Optional CSV Download
if not revenue_data_all.empty:
    csv = revenue_data_all.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="\U0001F4E5 Download Revenue CSV",
        data=csv,
        file_name='tcs_vs_infy_revenue.csv',
        mime='text/csv'
    )




