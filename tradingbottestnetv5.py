import time
import pandas as pd
import streamlit as st
from kucoin.client import Market
import logging
import plotly.graph_objects as go
import talib as ta

# Initialize KuCoin Market client
market_client = Market(url='https://api.kucoin.com')

# Set up logging
logging.basicConfig(filename="trading_bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Simulated account balance
simulated_balances = {
    "USDT": 10000.0,  # Start with 10,000 USDT
    "BTC": 0.0
}

# Trading parameters (default values)
STOP_LOSS_PERCENTAGE = 0.02
TAKE_PROFIT_PERCENTAGE = 0.05
TRADE_SIZE = 0.01

st.title("Crypto Trading Bot - Streamlit Dashboard")

# User inputs for parameters
STOP_LOSS_PERCENTAGE = st.slider("Stop Loss Percentage", 0.0, 0.1, 0.02)
TAKE_PROFIT_PERCENTAGE = st.slider("Take Profit Percentage", 0.0, 0.1, 0.05)
TRADE_SIZE = st.number_input("Trade Size (in BTC)", min_value=0.001, value=TRADE_SIZE)

# Fetch the latest price from KuCoin API
def get_current_price(symbol="BTC-USDT"):
    try:
        ticker = market_client.get_ticker(symbol)
        return float(ticker['price']) if ticker else 0.0
    except Exception as e:
        st.error(f"Error fetching current price: {e}")
        logging.error(f"Error fetching current price: {e}")
        return 0.0

# Function to fetch market data
def get_kucoin_data(symbol="BTC-USDT", interval="15min"):
    try:
        klines = market_client.get_kline(symbol, interval)
        if not klines:
            return None

        df = pd.DataFrame(klines, columns=['Time', 'Open', 'Close', 'High', 'Low', 'Volume', 'Turnover'])
        df['Time'] = pd.to_datetime(df['Time'].astype(int), unit='s')
        df[['Open', 'Close', 'High', 'Low', 'Volume', 'Turnover']] = df[
            ['Open', 'Close', 'High', 'Low', 'Volume', 'Turnover']].astype(float)
        return df
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        logging.error(f"Error fetching market data: {e}")
        return None

# Signal generator
def signal_generator(df):
    if df is None or len(df) < 10:
        return 0

    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()

    if df['SMA_5'].iloc[-1] > df['SMA_10'].iloc[-1] and df['SMA_5'].iloc[-2] < df['SMA_10'].iloc[-2]:
        return 2  # Buy signal
    elif df['SMA_5'].iloc[-1] < df['SMA_10'].iloc[-1] and df['SMA_5'].iloc[-2] > df['SMA_10'].iloc[-2]:
        return 1  # Sell signal
    else:
        return 0

# Modify place_order to use the current price
def place_order(symbol="BTC-USDT", qty=TRADE_SIZE, signal=0):
    current_price = get_current_price(symbol)
    if signal == 2 and simulated_balances["USDT"] >= qty * current_price:
        simulated_balances["USDT"] -= qty * current_price
        simulated_balances["BTC"] += qty
        logging.info(f"Bought {qty} BTC at ${current_price:.2f}")
        return f"✅ Bought {qty} BTC at ${current_price:.2f}"
    elif signal == 1 and simulated_balances["BTC"] >= qty:
        simulated_balances["BTC"] -= qty
        simulated_balances["USDT"] += qty * current_price
        logging.info(f"Sold {qty} BTC at ${current_price:.2f}")
        return f"✅ Sold {qty} BTC at ${current_price:.2f}"
    return "❌ No trade executed."

# Risk management function
def risk_management(entry_price, current_price):
    # Calculate stop loss and take profit prices
    stop_loss_price = entry_price * (1 - STOP_LOSS_PERCENTAGE)
    take_profit_price = entry_price * (1 + TAKE_PROFIT_PERCENTAGE)
    if current_price <= stop_loss_price:
        return "Stop Loss Hit", stop_loss_price
    elif current_price >= take_profit_price:
        return "Take Profit Hit", take_profit_price
    return None, current_price

# Run trading bot in Streamlit
def trading_job():
    df = get_kucoin_data()
    signal = signal_generator(df)
    trade_message = place_order(symbol="BTC-USDT", qty=TRADE_SIZE, signal=signal)

    if signal != 0:
        # Apply risk management if a trade was executed
        status, adjusted_price = risk_management(0, get_current_price("BTC-USDT"))
        if status:
            trade_message = f"{status} at price ${adjusted_price:.2f}"

    return df, trade_message

# Function to plot candlestick chart using Plotly
def plot_candlestick(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df['Time'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Candlesticks"
    )])
    fig.update_layout(title="Candlestick Chart", xaxis_title="Time", yaxis_title="Price", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)

# Function to calculate RSI and plot
def plot_rsi(df):
    df['RSI'] = ta.RSI(df['Close'], timeperiod=14)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Time'], y=df['RSI'], mode='lines', name='RSI'))
    fig.update_layout(title="RSI (14)", xaxis_title="Time", yaxis_title="RSI", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)

# Function to calculate MACD and plot
def plot_macd(df):
    df['MACD'], df['MACD_signal'], _ = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Time'], y=df['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df['Time'], y=df['MACD_signal'], mode='lines', name='MACD Signal'))
    fig.update_layout(title="MACD", xaxis_title="Time", yaxis_title="MACD", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)

# Buttons to start trading
if st.button("Run Trading Bot"):
    df, trade_message = trading_job()
    if df is not None:
        st.write("### Latest Market Data")
        st.dataframe(df.tail(10))
        plot_candlestick(df)
        plot_rsi(df)
        plot_macd(df)
    st.write("### Trade Execution")
    st.success(trade_message)

# Display balances
st.write("### Simulated Account Balance")
st.json(simulated_balances)
