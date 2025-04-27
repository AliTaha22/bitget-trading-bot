import asyncio
import threading
import logging
from exchange import exchange_ws
from indicators import calculate_indicators
from strategy import check_signal
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set the event loop to SelectorEventLoop for Windows compatibility
if __name__ == "__main__" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

symbol = 'BTC/USDT:USDT'
rsi_period = 14
ma_period = 20
bollinger_window = 20
bollinger_std_dev = 2
macd_fast = 12
macd_slow = 26
macd_signal = 9
atr_period = 14
risk_percentage = 0.02

in_position = False
position_type = None

# Enhanced validation to handle all numeric fields used in calculations
def validate_market_data(df):
    required_columns = ['open', 'high', 'low', 'close', 'volume']  # Add any other fields used in calculations
    for column in required_columns:
        if df[column].isnull().any() or not pd.api.types.is_numeric_dtype(df[column]):
            logging.error(f"Missing, invalid, or non-numeric data in column: {column}")
            return False
    return True

async def listen_to_market():
    try:
        logging.info("Starting market listener...")
        await exchange_ws.watch_ticker(symbol)
        while True:
            try:
                ticker = await exchange_ws.watch_ticker(symbol)
                logging.info(f"Received market data: {ticker}")
                df = pd.DataFrame([ticker], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'bid', 'ask'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                # Replace None values with 0 or a default value to avoid errors
                df.fillna(0, inplace=True)

                # Validate market data before proceeding
                if not validate_market_data(df):
                    continue

                df = calculate_indicators(df, rsi_period, ma_period, bollinger_window, bollinger_std_dev, macd_fast, macd_slow, macd_signal, atr_period)
                logging.info("Indicators calculated.")
                global in_position, position_type
                in_position, position_type = check_signal(df, symbol, risk_percentage, in_position, position_type)
                logging.info(f"Trade signal checked. In position: {in_position}, Position type: {position_type}")
            except Exception as e:
                logging.error(f"Error while processing market data: {e}")
    except asyncio.CancelledError:
        logging.info("Market listener task was cancelled.")
    except Exception as e:
        logging.error(f"Unexpected error in market listener: {e}")
    finally:
        try:
            await exchange_ws.close()
            logging.info("Exchange connection closed.")
        except Exception as e:
            logging.error(f"Error while closing exchange connection: {e}")

def run_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_to_market())

if __name__ == "__main__":
    threading.Thread(target=run_event_loop, daemon=True).start()
    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        logging.info("Program terminated.")