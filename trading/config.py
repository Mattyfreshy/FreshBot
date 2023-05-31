from dotenv import load_dotenv
import os

load_dotenv()

ALPACA_CONFIG = {
    # Put your own Alpaca key here:
    "API_KEY": os.getenv('ALPACA_API_KEY'),
    # Put your own Alpaca secret here:
    "API_SECRET": os.getenv('ALPACA_SECRET_KEY'),
    # If you want to go live, you must change this. It is currently set for paper trading
    "ENDPOINT": os.getenv('ALPACA_ENDPOINT'),
}