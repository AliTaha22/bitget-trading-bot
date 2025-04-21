import ccxt
import pandas as pd
import ta
import time
from config import API_KEY, API_SECRET, API_PASSPHRASE

# === SETUP EXCHANGE ===
exchange = ccxt.bitget({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'password': API_PASSPHRASE,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'swap',  # USDT-Margined Futures
    }
})

symbol = 'BTC/USDT:USDT'
timeframe = '1m'
rsi_period = 14
overbought = 70
oversold = 30
quantity = 0.01  # change for your paper trades

# Paper trading state
in_position = False
position_type = None  # "long" or "short"

def fetch_data():
    candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_rsi(df):
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=rsi_period).rsi()
    return df

def check_signal(df):
    global in_position, position_type

    latest = df.iloc[-1]
    rsi = latest['rsi']
    price = latest['close']

    print(f"Price: {price} | RSI: {rsi:.2f}")

    if rsi is None:
        return

    if not in_position:
        if rsi < oversold:
            print("📈 RSI below 30 → BUY signal (paper)")
            in_position = True
            position_type = "long"
        elif rsi > overbought:
            print("📉 RSI above 70 → SHORT signal (paper)")
            in_position = True
            position_type = "short"
    else:
        if position_type == "long" and rsi > 50:
            print("🟢 Closing LONG position (paper)")
            in_position = False
            position_type = None
        elif position_type == "short" and rsi < 50:
            print("🔴 Closing SHORT position (paper)")
            in_position = False
            position_type = None

def run():
    df = fetch_data()
    df = calculate_rsi(df)
    check_signal(df)

if __name__ == "__main__":
    while True:
        run()
        time.sleep(10)  # run every 5 minutes