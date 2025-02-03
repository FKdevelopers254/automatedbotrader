import time
import pandas as pd
from kucoin.client import Trade, Market, User
from config import API_KEY, SECRET_KEY, API_PASSPHRASE

# Initialize KuCoin clients
market_client = Market(url='https://api.kucoin.com')
trade_client = Trade(key=API_KEY, secret=SECRET_KEY, passphrase=API_PASSPHRASE)
user_client = User(key=API_KEY, secret=SECRET_KEY, passphrase=API_PASSPHRASE)


def check_account_info():
    """Check available balance"""
    try:
        balances = user_client.get_account_list()
        available_balances = {bal['currency']: float(bal['available']) for bal in balances['data']}
        print("Account Balances:", available_balances)
        return available_balances
    except Exception as e:
        print(f"Error fetching account info: {e}")
        return {}


def get_kucoin_data(symbol="BTC-USDT", interval="5min"):
    """Fetch historical market data"""
    print("Fetching data from KuCoin...")
    try:
        klines = market_client.get_kline(symbol, interval)
        if not klines:
            print("No data retrieved!")
            return None

        # Ensure correct column order
        df = pd.DataFrame(klines, columns=['Time', 'Open', 'Close', 'High', 'Low', 'Volume', 'Turnover'])

        # Convert data types
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

    if df['SMA_5'].iloc[-1] > df['SMA_10'].iloc[-1]:
        print("🟢 Buy Signal (SMA Crossover)!")
        return 2
    elif df['SMA_5'].iloc[-1] < df['SMA_10'].iloc[-1]:
        print("🔴 Sell Signal (SMA Crossover)!")
        return 1
    else:
        print("⚪ No clear pattern detected.")
        return 0


def place_order(symbol="BTC-USDT", qty=0.01, signal=0, balances=None):
    """Place buy or sell order with balance check"""
    try:
        if balances is None:
            balances = check_account_info()

        base_currency, quote_currency = symbol.split("-")

        if signal == 2:  # Buy order
            if quote_currency not in balances or balances[quote_currency] < qty * 1000:
                print(f"❌ Insufficient {quote_currency} balance to place a buy order.")
                return
            print("Placing Buy Order...")
            order = trade_client.create_market_order(symbol, 'buy', 'market', size=qty)
            print("✅ Buy Order Placed:", order)

        elif signal == 1:  # Sell order
            if base_currency not in balances or balances[base_currency] < qty:
                print(f"❌ Insufficient {base_currency} balance to place a sell order.")
                return
            print("Placing Sell Order...")
            order = trade_client.create_market_order(symbol, 'sell', 'market', size=qty)
            print("✅ Sell Order Placed:", order)

    except Exception as e:
        print(f"Error placing order: {e}")


def trading_job():
    """Main trading bot function"""
    print("🚀 Running Trading Bot on KuCoin...")
    balances = check_account_info()

    df = get_kucoin_data()
    signal = signal_generator(df)

    if signal in [1, 2]:
        place_order(symbol="BTC-USDT", qty=0.01, signal=signal, balances=balances)
    else:
        print("❌ No trade executed.")


# Run trading bot
trading_job()
