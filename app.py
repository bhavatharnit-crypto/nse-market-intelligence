
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta

st.set_page_config(page_title="NSE Market Intelligence", layout="wide")
st.title("NSE Market Intelligence")
st.subheader("AI-Powered Stock Analysis and Risk Assessment")
st.info("Educational analysis only. This app does not provide investment advice.")

stocks = {
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "SBI": "SBIN.NS"
}

with st.sidebar:
    st.header("Analysis Settings")
    company = st.selectbox("Select stock", list(stocks.keys()))
    end = date.today()
    start = st.date_input("Start date", end - timedelta(days=730))
    short = st.slider("Short moving average", 5, 50, 20)
    long = st.slider("Long moving average", 20, 200, 50)

if start >= end:
    st.error("Select a start date before the end date.")
    st.stop()

if short >= long:
    st.warning("Choose a short moving average smaller than the long moving average.")

@st.cache_data(ttl=900)
def get_data(symbol, start_date, end_date):
    data = yf.download(
        symbol,
        start=start_date,
        end=end_date + timedelta(days=1),
        auto_adjust=True,
        progress=False
    )
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    if data.empty or "Close" not in data.columns:
        return pd.DataFrame()
    return data[["Close"]].dropna()

with st.spinner("Loading historical stock data..."):
    df = get_data(stocks[company], start, end)

if df.empty:
    st.error("Unable to load stock data. Please try again later.")
    st.stop()

df["Return"] = df["Close"].pct_change()
df["Short MA"] = df["Close"].rolling(short).mean()
df["Long MA"] = df["Close"].rolling(long).mean()
df["Peak"] = df["Close"].cummax()
df["Drawdown"] = df["Close"] / df["Peak"] - 1

returns = df["Return"].dropna()
total_return = df["Close"].iloc[-1] / df["Close"].iloc[0] - 1
years = max((df.index[-1] - df.index[0]).days / 365.25, 1 / 365.25)
annual_return = (1 + total_return) ** (1 / years) - 1
volatility = returns.std() * np.sqrt(252)
max_drawdown = df["Drawdown"].min()
sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() else 0

st.caption(f"Data source: Yahoo Finance | {stocks[company]}")

a, b, c, d = st.columns(4)
a.metric("Total Return", f"{total_return:.2%}")
b.metric("Annualised Return", f"{annual_return:.2%}")
c.metric("Annualised Volatility", f"{volatility:.2%}")
d.metric("Maximum Drawdown", f"{max_drawdown:.2%}")

st.metric("Sharpe Ratio", f"{sharpe:.2f}")

tab1, tab2, tab3 = st.tabs(
    ["Price Analysis", "Risk Analysis", "Strategy Backtesting"]
)

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Stock Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Short MA"], name="Short MA"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Long MA"], name="Long MA"))
    fig.update_layout(title="Stock Price and Moving Averages",
                      xaxis_title="Date", yaxis_title="Price (INR)")
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Download Analysis CSV",
        df.to_csv().encode("utf-8"),
        "stock_analysis.csv",
        "text/csv"
    )

with tab2:
    st.subheader("Drawdown Analysis")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df.index, y=df["Drawdown"] * 100,
        fill="tozeroy", name="Drawdown"
    ))
    fig2.update_layout(yaxis_title="Drawdown (%)")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Daily Return Distribution")
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(x=returns * 100, nbinsx=40))
    fig3.update_layout(xaxis_title="Daily Return (%)")
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    bt = df[["Close", "Short MA", "Long MA"]].dropna().copy()
    bt["Signal"] = (bt["Short MA"] > bt["Long MA"]).astype(int)
    bt["Strategy Return"] = (
        bt["Signal"].shift(1).fillna(0) *
        bt["Close"].pct_change().fillna(0)
    )
    bt["Strategy"] = (1 + bt["Strategy Return"]).cumprod()
    bt["Buy and Hold"] = (
        1 + bt["Close"].pct_change().fillna(0)
    ).cumprod()

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=bt.index, y=bt["Strategy"], name="MA Strategy"
    ))
    fig4.add_trace(go.Scatter(
        x=bt.index, y=bt["Buy and Hold"], name="Buy and Hold"
    ))
    fig4.update_layout(
        title="Strategy Backtesting",
        xaxis_title="Date",
        yaxis_title="Growth of ₹1"
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.write(
        "Strategy return:",
        f"{(bt['Strategy'].iloc[-1] - 1):.2%}"
    )
    st.write(
        "Buy and hold return:",
        f"{(bt['Buy and Hold'].iloc[-1] - 1):.2%}"
    )

st.caption(
    "Historical data and illustrative strategy testing only. "
    "Backtest excludes transaction costs and taxes. "
    "Past performance does not guarantee future results."
)
