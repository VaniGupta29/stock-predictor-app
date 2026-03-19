import streamlit as st
import pickle
import pandas as pd
import yfinance as yf
import time
import plotly.graph_objects as go

# ------------------ Page Config ------------------
st.set_page_config(page_title="Stock Predictor Pro", page_icon="📈", layout="wide")

# ------------------ PREMIUM CSS ------------------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #e0f2fe, #f0f9ff, #f8fafc);
}

/* Main container */
.block-container {
    padding-top: 2rem;
}

/* Header */
h1 {
    text-align: center;
    color: #0369a1;
    font-weight: 700;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #e0f2fe;
}

/* Metric Cards (ICE BLUE STYLE) */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #ffffff, #e0f2fe);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #bae6fd;
    box-shadow: 0 4px 15px rgba(3, 105, 161, 0.1);
    transition: all 0.3s ease;
}

/* Hover effect */
[data-testid="stMetric"]:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 25px rgba(3, 105, 161, 0.2);
}

/* Metric value */
[data-testid="stMetricValue"] {
    color: #0284c7;
    font-weight: bold;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #0ea5e9, #38bdf8);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
    font-weight: 600;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #0284c7, #0ea5e9);
}

/* Radio buttons */
.stRadio > div {
    background: #e0f2fe;
    padding: 10px;
    border-radius: 10px;
}

/* Success */
.stAlert-success {
    background-color: #dbeafe;
    color: #1e40af;
}

/* Warning */
.stAlert-warning {
    background-color: #fef9c3;
}

/* Error */
.stAlert-error {
    background-color: #fee2e2;
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background: #bae6fd;
}

</style>
""", unsafe_allow_html=True)

# ------------------ Load Model ------------------
with open("Stock_Market_Predict.pkl", "rb") as file:
    model = pickle.load(file)

# ------------------ Header ------------------
st.markdown("""
<h1>📈 AI Stock Predictor Pro 🚀</h1>
<p style='text-align:center; color:gray;'>
Live Data • AI Prediction • Smart Trend • Dashboard
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ------------------ Sidebar ------------------
st.sidebar.header("📥 Input Section")

stock_list = [
    "AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "META",
    "RELIANCE.NS", "TCS.NS", "INFY.NS",
    "HDFCBANK.NS", "ICICIBANK.NS",
    "BTC-USD", "ETH-USD"
]

stock_symbol = st.sidebar.selectbox("🔥 Select Stock", stock_list)

refresh = st.sidebar.checkbox("🔄 Auto Refresh (5 sec)")
if refresh:
    time.sleep(5)
    st.rerun()

mode = st.radio("Select Mode", ["📊 Manual Input", "📡 Live Data"])

# ------------------ INPUT ------------------
if mode == "📊 Manual Input":
    open_val = float(st.sidebar.number_input("Open Price", value=1000.0))
    high_val = float(st.sidebar.number_input("High Price", value=1008.0))
    low_val = float(st.sidebar.number_input("Low Price", value=995.0))
    volume_val = float(st.sidebar.number_input("Volume", value=1000000.0))

else:
    ticker = yf.Ticker(stock_symbol)
    live_data = ticker.history(period="1d")

    if live_data.empty:
        st.error("❌ Invalid Symbol")
        st.stop()

    latest = live_data.iloc[-1]

    open_val = float(latest["Open"])
    high_val = float(latest["High"])
    low_val = float(latest["Low"])
    volume_val = float(latest["Volume"])

    st.success(f"✅ Live data loaded for {stock_symbol}")

# ------------------ Metrics ------------------
st.markdown("### 📊 Market Data")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Open", round(open_val, 2))
col2.metric("High", round(high_val, 2))
col3.metric("Low", round(low_val, 2))
col4.metric("Volume", int(volume_val))

st.markdown("---")

# ------------------ Prediction ------------------
if st.button("🚀 Predict Now"):

    input_data = pd.DataFrame([[open_val, high_val, low_val, volume_val]],
                              columns=["open", "high", "low", "volume"])

    result = model.predict(input_data)
    price = float(result[0])

    st.success(f"💰 Predicted Closing Price: {price:.2f}")

    if price > open_val:
        signal = "BUY 🟢"
        st.markdown("### 📈 Bullish Trend 🚀")
    else:
        signal = "SELL 🔴"
        st.markdown("### 📉 Bearish Trend ⚠️")

    st.subheader("💹 Trading Signal")
    st.write(f"👉 Recommendation: **{signal}**")

    change_percent = abs((price - open_val) / open_val) * 100
    st.subheader("📊 Confidence Level")
    st.progress(min(int(change_percent), 100))
    st.write(f"Confidence: {change_percent:.2f}%")

# ------------------ Chart + Smart Trend ------------------
if mode == "📡 Live Data":

    st.subheader("📉 Stock Chart + Smart Trend")

    ticker = yf.Ticker(stock_symbol)
    hist_data = ticker.history(period="6mo")

    if not hist_data.empty:
        hist_data.reset_index(inplace=True)

        for col in ["Open", "High", "Low", "Close"]:
            hist_data[col] = pd.to_numeric(hist_data[col], errors="coerce")

        hist_data.dropna(inplace=True)

        hist_data["MA20"] = hist_data["Close"].rolling(window=20).mean()
        hist_data["MA50"] = hist_data["Close"].rolling(window=50).mean()

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=hist_data["Date"],
            open=hist_data["Open"],
            high=hist_data["High"],
            low=hist_data["Low"],
            close=hist_data["Close"],
            name="Candles"
        ))

        fig.add_trace(go.Scatter(
            x=hist_data["Date"],
            y=hist_data["MA20"],
            name="MA 20"
        ))

        fig.add_trace(go.Scatter(
            x=hist_data["Date"],
            y=hist_data["MA50"],
            name="MA 50"
        ))

        fig.update_layout(
            template="plotly_dark",
            title=f"{stock_symbol} Chart",
            xaxis_rangeslider_visible=False,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("📊 Smart Market Trend")

        ma20 = hist_data["MA20"].iloc[-1]
        ma50 = hist_data["MA50"].iloc[-1]

        if pd.notna(ma20) and pd.notna(ma50):
            if ma20 > ma50:
                st.success("📈 STRONG BULLISH TREND 🚀")
            elif ma20 < ma50:
                st.error("📉 STRONG BEARISH TREND ⚠️")
            else:
                st.info("⚖️ SIDEWAYS MARKET")
        else:
            st.warning("⚠️ Not enough data")

    else:
        st.warning("⚠️ No chart data")

else:
    st.info("📊 Switch to Live Data mode to view chart")

# ------------------ Footer ------------------
st.markdown("---")
st.markdown("<p style='text-align:center;'>✨ Made with ❤️ using Streamlit</p>", unsafe_allow_html=True)