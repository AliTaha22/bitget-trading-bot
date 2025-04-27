from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
# API_PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")
