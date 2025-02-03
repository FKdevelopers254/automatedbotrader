import time
import random
import pandas as pd
import streamlit as st
from kucoin.client import Market

# Initialize KuCoin Market client
market_client = Market(url='https://api.kucoin.com')

# Simulated account balance
simulated_balances = {
    "USDT": 10000.0,  # Start with 10,000 USDT
    "BTC": 0.0
}

# Trading parameters
STOP_LOSS_PERCENTAGE = 0.02
TAKE_PROFIT_PERCENTAGE = 0.05
TRADE_SIZE = 0.01

st.title("Crypto Trading Bot - Streamlit Dashboard")

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

# Function to simulate orders with stop loss and take profit
def place_order(symbol="BTC-USDT", qty=TRADE_SIZE, signal=0):
    price = random.uniform(30000, 40000)  # Simulated BTC price
    if signal == 2 and simulated_balances["USDT"] >= qty * price:
        simulated_balances["USDT"] -= qty * price
        simulated_balances["BTC"] += qty
        return f"✅ Bought {qty} BTC at ${price:.2f}"
    elif signal == 1 and simulated_balances["BTC"] >= qty:
        simulated_balances["BTC"] -= qty
        simulated_balances["USDT"] += qty * price
        return f"✅ Sold {qty} BTC at ${price:.2f}"
    return "❌ No trade executed."

# Run trading bot in Streamlit
def trading_job():
    df = get_kucoin_data()
    signal = signal_generator(df)
    trade_message = place_order(signal=signal)
    return df, trade_message

# Continuous trading loop with error handling
def continuous_trading():
    while True:
        df, trade_message = trading_job()
        if df is not None:
            st.write("### Latest Market Data")
            st.dataframe(df.tail(10))
        st.write("### Trade Execution")
        st.success(trade_message)
        time.sleep(60)  # Run every 60 seconds

# Buttons to start trading
if st.button("Run Trading Bot"):
    df, trade_message = trading_job()
    if df is not None:
        st.write("### Latest Market Data")
        st.dataframe(df.tail(10))
    st.write("### Trade Execution")
    st.success(trade_message)

if st.button("Start Continuous Trading"):
    continuous_trading()

# Display balances
st.write("### Simulated Account Balance")
st.json(simulated_balances)

# Display price chart
df = get_kucoin_data()
if df is not None:
    st.write("### Price Movement Chart")
    st.line_chart(df[['Time', 'Close']].set_index('Time'))
