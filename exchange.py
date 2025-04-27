import ccxt
from config import API_KEY, API_SECRET

# Initialize Binance Testnet Exchange
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    },
    'urls': {
        'api': {
            'public': 'https://testnet.binancefuture.com/fapi/v1',
            'private': 'https://testnet.binancefuture.com/fapi/v1',
        }
    }
})

# WebSocket-based real-time data handling
from ccxt.pro import binance as binance_pro

# Initialize WebSocket client
exchange_ws = ccxt.pro.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',
    }
})

# Activate testnet mode
exchange_ws.set_sandbox_mode(True)