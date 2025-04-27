# import ccxt
# import pandas as pd
# import ta
# import time
# import numpy as np
# import talib
# import threading
# import asyncio
# from config import API_KEY, API_SECRET

# # === SETUP EXCHANGE ===
# # exchange = ccxt.bitget({
# #     'apiKey': API_KEY,
# #     'secret': API_SECRET,
# #     'password': API_PASSPHRASE,
# #     'enableRateLimit': True,
# #     'options': {
# #         'defaultType': 'swap',  # USDT-Margined Futures
# #     }
# # })

# exchange = ccxt.binance({
#     'apiKey': API_KEY,
#     'secret': API_SECRET,
#     'enableRateLimit': True,
#     'options': {
#         'defaultType': 'future',  # Use futures for leverage trading
#     },
#     'urls': {
#         'api': {
#             'public': 'https://testnet.binancefuture.com/fapi/v1',
#             'private': 'https://testnet.binancefuture.com/fapi/v1',
#         }
#     }
# })

# # WebSocket-based real-time data handling
# from ccxt.pro import binance as binance_pro

# # Initialize WebSocket client
# exchange_ws = binance_pro({
#     'apiKey': API_KEY,
#     'secret': API_SECRET,
#     'enableRateLimit': True,
#     'options': {
#         'defaultType': 'future',
#     },
#     'urls': {
#         'api': {
#             'public': 'wss://stream.binancefuture.com/ws',
#             'private': 'wss://stream.binancefuture.com/ws',
#         }
#     }
# })

# symbol = 'BTC/USDT:USDT'
# timeframe = '1m'

# # Adjusted values for better strategy tuning
# rsi_period = 14  # Standard RSI period
# oversold = 30  # RSI below 30 indicates oversold
# overbought = 70  # RSI above 70 indicates overbought
# quantity = 0.001  # Adjusted for smaller trade size
# ma_period = 20  # Moving Average period
# bollinger_window = 20  # Bollinger Bands window
# bollinger_std_dev = 2  # Standard deviation for Bollinger Bands

# # Add MACD and ATR for advanced strategy
# macd_fast = 12
# macd_slow = 26
# macd_signal = 9
# atr_period = 14
# risk_percentage = 0.02  # Risk 2% of account balance per trade

# # Updated check_signal to include Bollinger Bands, Moving Average, MACD, and ATR
# def check_signal(df):
#     global in_position, position_type

#     latest = df.iloc[-1]
#     rsi = latest['rsi']
#     price = latest['close']
#     ma = latest['ma']
#     bollinger_upper = latest['bollinger_upper']
#     bollinger_lower = latest['bollinger_lower']
#     macd = latest['macd']
#     macd_signal = latest['macd_signal']
#     atr = latest['atr']

#     print(f"Price: {price} | RSI: {rsi:.2f} | MA: {ma:.2f} | Bollinger Upper: {bollinger_upper:.2f} | Bollinger Lower: {bollinger_lower:.2f} | MACD: {macd:.2f} | MACD Signal: {macd_signal:.2f} | ATR: {atr:.2f}")

#     if rsi is None or np.isnan(ma) or np.isnan(bollinger_upper) or np.isnan(bollinger_lower) or np.isnan(macd) or np.isnan(macd_signal) or np.isnan(atr):
#         return

#     account_balance = exchange.fetch_balance()['total']['USDT']
#     position_size = (account_balance * risk_percentage) / atr

#     if not in_position:
#         if rsi < oversold and price < bollinger_lower and macd > macd_signal:
#             print("📈 Strong BUY signal")
#             exchange.create_market_buy_order(symbol, position_size)
#             in_position = True
#             position_type = "long"
#         elif rsi > overbought and price > bollinger_upper and macd < macd_signal:
#             print("📉 Strong SHORT signal")
#             exchange.create_market_sell_order(symbol, position_size)
#             in_position = True
#             position_type = "short"
#     else:
#         if position_type == "long" and (rsi > 50 or price > ma):
#             print("🟢 Closing LONG position")
#             exchange.create_market_sell_order(symbol, position_size)
#             in_position = False
#             position_type = None
#         elif position_type == "short" and (rsi < 50 or price < ma):
#             print("🔴 Closing SHORT position")
#             exchange.create_market_buy_order(symbol, position_size)
#             in_position = False
#             position_type = None

# def handle_realtime_data():
#     async def listen_to_market():
#         await exchange_ws.watch_ticker(symbol)
#         while True:
#             ticker = await exchange_ws.watch_ticker(symbol)
#             df = pd.DataFrame([ticker], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#             df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#             df['ma'] = df['close'].rolling(window=ma_period).mean()
#             df['bollinger_upper'] = df['ma'] + (df['close'].rolling(window=bollinger_window).std() * bollinger_std_dev)
#             df['bollinger_lower'] = df['ma'] - (df['close'].rolling(window=bollinger_window).std() * bollinger_std_dev)
#             df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=rsi_period).rsi()
#             df['macd'], df['macd_signal'], _ = talib.MACD(df['close'], fastperiod=macd_fast, slowperiod=macd_slow, signalperiod=macd_signal)
#             df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=atr_period)
#             check_signal(df)

#     # Run the WebSocket listener in a separate thread
#     threading.Thread(target=lambda: asyncio.run(listen_to_market()), daemon=True).start()

# # Replace the main loop with WebSocket-based execution
# if __name__ == "__main__":
#     handle_realtime_data()
#     while True:
#         time.sleep(1)  # Keep the main thread alive