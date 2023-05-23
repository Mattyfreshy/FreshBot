import asyncio
import yfinance as yf
import pandas_datareader.data as web
import pandas as pd
import datetime as dt
import trading as td
import txt_dir as txt


""" Fresh Trading Algorithm """
"""
Algorithm:
    Buy:
    - Stock price >= SMA(50)
    - MACD crosses above signal line and MACD < 0
    - RSI < 65
    
    Sell:
    - Stock price <= SMA(20)
    - MACD crosses below signal line and MACD > 0
    - RSI > 35
"""

# Main trading algorithm
def freshbot_trading():
    """ Uses sma(50), MACD, and RSI to determine buy/sell signals """
    """ Uses 1 minute interval data """
    market_open = marketStatus()
    while market_open:
        # Get stock data
        equities = td.read_tickers(txt.TICKERS_EQUITY)
        testing_equity = 'AAPL'



        # Delay between each iteration
        asyncio.sleep(60)    # n second delay
        market_open = marketStatus()

    return

""" Utility Functions """

# Check if market is open
def marketStatus(): 
    weekday = dt.date.today().weekday() <= 4
    time = dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
    return weekday and time

""" Main """

def main():
    return    

if __name__ == '__main__':
    main()