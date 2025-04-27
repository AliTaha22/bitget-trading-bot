import pandas as pd
import pandas_ta as ta  # Replace talib with pandas-ta
import logging

# Initialize a global DataFrame to store historical data
historical_data = pd.DataFrame()

def calculate_indicators(df, rsi_period, ma_period, bollinger_window, bollinger_std_dev, macd_fast, macd_slow, macd_signal, atr_period):
    global historical_data

    # Append new data to historical data
    historical_data = pd.concat([historical_data, df]).drop_duplicates(subset=['timestamp']).reset_index(drop=True)

    # Ensure the DataFrame has enough rows for calculations
    required_rows = max(rsi_period, ma_period, bollinger_window, macd_slow, atr_period) + 1
    if len(historical_data) < required_rows:
        logging.error(f"Not enough data to calculate indicators. DataFrame length: {len(historical_data)}, required: {required_rows}")
        return historical_data  # Return the DataFrame as-is without calculations

    # Moving Average
    historical_data['ma'] = historical_data['close'].rolling(window=ma_period).mean()

    # Bollinger Bands
    historical_data['bollinger_upper'] = historical_data['ma'] + (historical_data['close'].rolling(window=bollinger_window).std() * bollinger_std_dev)
    historical_data['bollinger_lower'] = historical_data['ma'] - (historical_data['close'].rolling(window=bollinger_window).std() * bollinger_std_dev)

    # RSI Calculation
    rsi = historical_data.ta.rsi(length=rsi_period)
    if isinstance(rsi, pd.Series):
        historical_data['rsi'] = rsi
    else:
        logging.error("RSI calculation failed.")

    # MACD Calculation
    macd = historical_data.ta.macd(fast=macd_fast, slow=macd_slow, signal=macd_signal)
    if isinstance(macd, pd.DataFrame):
        try:
            historical_data['macd'] = macd.iloc[:, 0]  # MACD line
            historical_data['macd_signal'] = macd.iloc[:, 1]  # Signal line
        except IndexError:
            logging.error("MACD calculation did not return expected columns.")
    else:
        logging.error("MACD calculation failed.")

    # ATR Calculation
    atr = historical_data.ta.atr(length=atr_period)
    if isinstance(atr, pd.Series):
        historical_data['atr'] = atr
    else:
        logging.error("ATR calculation failed or did not return a Series.")

    return historical_data