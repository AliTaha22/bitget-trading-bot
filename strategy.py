from exchange import exchange
from indicators import calculate_indicators
import numpy as np

def check_signal(df, symbol, risk_percentage, in_position, position_type):
    latest = df.iloc[-1]
    rsi = latest['rsi']
    price = latest['close']
    ma = latest['ma']
    bollinger_upper = latest['bollinger_upper']
    bollinger_lower = latest['bollinger_lower']
    macd = latest['macd']
    macd_signal = latest['macd_signal']
    atr = latest['atr']

    print(f"Price: {price} | RSI: {rsi:.2f} | MA: {ma:.2f} | Bollinger Upper: {bollinger_upper:.2f} | Bollinger Lower: {bollinger_lower:.2f} | MACD: {macd:.2f} | MACD Signal: {macd_signal:.2f} | ATR: {atr:.2f}")

    if rsi is None or np.isnan(ma) or np.isnan(bollinger_upper) or np.isnan(bollinger_lower) or np.isnan(macd) or np.isnan(macd_signal) or np.isnan(atr):
        return in_position, position_type

    account_balance = exchange.fetch_balance()['total']['USDT']
    position_size = (account_balance * risk_percentage) / atr

    if not in_position:
        if rsi < 30 and price < bollinger_lower and macd > macd_signal:
            print("📈 Strong BUY signal")
            exchange.create_market_buy_order(symbol, position_size)
            in_position = True
            position_type = "long"
        elif rsi > 70 and price > bollinger_upper and macd < macd_signal:
            print("📉 Strong SHORT signal")
            exchange.create_market_sell_order(symbol, position_size)
            in_position = True
            position_type = "short"
    else:
        if position_type == "long" and (rsi > 50 or price > ma):
            print("🟢 Closing LONG position")
            exchange.create_market_sell_order(symbol, position_size)
            in_position = False
            position_type = None
        elif position_type == "short" and (rsi < 50 or price < ma):
            print("🔴 Closing SHORT position")
            exchange.create_market_buy_order(symbol, position_size)
            in_position = False
            position_type = None

    return in_position, position_type