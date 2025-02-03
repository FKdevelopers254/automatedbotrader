import time
import pandas as pd
from kucoin.client import Market
import random

# Initialize KuCoin Market client (for fetching prices)
market_client = Market(url='https://api.kucoin.com')

# Simulated account balance
simulated_balances = {
    "USDT": 10000.0,  # Start with 10,000 USDT
    "BTC": 0.0
}

# Risk management parameters
STOP_LOSS_PERCENTAGE = 0.02  # 2% stop-loss
TAKE_PROFIT_PERCENTAGE = 0.05  # 5% take-profit
TRADE_SIZE = 0.01  # Amount of BTC to trade

def check_account_info():
    """Check simulated balance"""
    print("Simulated Account Balances:", simulated_balances)
    return simulated_balances.copy()

def get_kucoin_data(symbol="BTC-USDT", interval="15min"):
    """Fetch historical market data"""
    print("Fetching data from KuCoin...")
    try:
        klines = market_client.get_kline(symbol, interval)
        if not klines:
            print("No data retrieved!")
            return None

        df = pd.DataFrame(klines, columns=['Time', 'Open', 'Close', 'High', 'Low', 'Volume', 'Turnover'])
        df['Time'] = pd.to_datetime(df['Time'].astype(int), unit='s')
        df[['Open', 'Close', 'High', 'Low', 'Volume', 'Turnover']] = df[['Open', 'Close', 'High', 'Low', 'Volume', 'Turnover']].astype(float)

        print(df.tail())  # Print last few rows for debugging
        return df
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return None

def signal_generator(df):
    """Generate buy/sell signals based on moving averages"""
    if df is None or len(df) < 10:
        print("Not enough data to generate signals!")
        return 0

    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()

    # More sophisticated signal: Confirm the trend
    if df['SMA_5'].iloc[-1] > df['SMA_10'].iloc[-1] and df['SMA_5'].iloc[-2] < df['SMA_10'].iloc[-2]:
        print("🟢 Simulated Buy Signal (SMA Crossover confirmed)!")
        return 2  # Buy signal
    elif df['SMA_5'].iloc[-1] < df['SMA_10'].iloc[-1] and df['SMA_5'].iloc[-2] > df['SMA_10'].iloc[-2]:
        print("🔴 Simulated Sell Signal (SMA Crossover confirmed)!")
        return 1  # Sell signal
    else:
        print("⚪ No clear pattern detected.")
        return 0

def place_order(symbol="BTC-USDT", qty=TRADE_SIZE, signal=0):
    """Simulated buy or sell order"""
    base_currency, quote_currency = symbol.split("-")
    price = random.uniform(30000, 40000)  # Simulated BTC price

    # Setting a stop-loss and take-profit based on the entry price
    if signal == 2:  # Simulated Buy order
        cost = qty * price
        if simulated_balances["USDT"] >= cost:
            simulated_balances["USDT"] -= cost
            simulated_balances["BTC"] += qty
            stop_loss_price = price * (1 - STOP_LOSS_PERCENTAGE)
            take_profit_price = price * (1 + TAKE_PROFIT_PERCENTAGE)
            print(f"✅ Simulated Buy Order: {qty} BTC at ${price:.2f} each (Total: ${cost:.2f})")
            print(f"🚨 Stop-loss set at ${stop_loss_price:.2f}, Take-profit set at ${take_profit_price:.2f}")
        else:
            print(f"❌ Insufficient USDT balance to place a buy order.")

    elif signal == 1:  # Simulated Sell order
        if simulated_balances["BTC"] >= qty:
            revenue = qty * price
            simulated_balances["BTC"] -= qty
            simulated_balances["USDT"] += revenue
            print(f"✅ Simulated Sell Order: {qty} BTC at ${price:.2f} each (Total: ${revenue:.2f})")
        else:
            print(f"❌ Insufficient BTC balance to place a sell order.")

def trading_job():
    """Main trading bot function (Simulated)"""
    print("🚀 Running Simulated Trading Bot...")
    check_account_info()

    df = get_kucoin_data()
    signal = signal_generator(df)

    if signal in [1, 2]:
        place_order(symbol="BTC-USDT", qty=TRADE_SIZE, signal=signal)
    else:
        print("❌ No trade executed.")

# Continuous trading loop
while True:
    trading_job()
    time.sleep(4)  # Wait for 1 minute before executing the next trade
