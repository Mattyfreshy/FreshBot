import datetime as dt
import txt_dir as txt
import math
import asyncio

import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf
import pandas as pd
import pandas_datareader as pdr



""" Fresh Trading Algorithm Overview """
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

# Pandas settings/fixes. (pandas_datareader fix)
yf.pdr_override()
pd.set_option('mode.chained_assignment', None)

# Initialize variables
SMA_20 = 20
SMA_50 = 50
SMA_200 = 200

""" Utility Functions """

def marketStatus(): 
    """ Returns True if market is open, False if market is closed """
    weekday = dt.date.today().weekday() <= 4
    time = dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
    return weekday and time

def read_tickers(file) -> list:
    """ Read tickers from file and return list of tickers as strings """
    with open(file, 'r') as f:
        lst = []
        for line in f:
            if line.strip():
                lst.append(line.strip())
        return lst
    
def get_sma(stock: str, delta_days=SMA_50):
    """ Calculate n_Day SMA (Default 50) """
    """ 
    Simple Moving Average:
        SMA = ( Sum ( Price, n ) ) / n    
        Where: n = Time Period
    Uses 1m interval data for extreme accuracy.
    """
    now = dt.datetime.now() # Current date
    df_lst = [] # List of dataframes
    timedelta_lst = [now] # List of timedelta objects
    n_downloads = 8 # Number of downloads from yfinance

    for i in range(n_downloads):
        # Get timedelta object
        timedelta_lst.append(timedelta_lst[-1] - dt.timedelta(days=6))
    
    # for time in timedelta_lst:
    #     print(time) #* DEBUG

    # Get df's from yfinance
    for i in range(len(timedelta_lst)-1):
        week_ago = timedelta_lst[i+1]
        start_year = week_ago.year
        start_month = week_ago.month
        start_day = week_ago.day
        start = dt.datetime(start_year, start_month, start_day)
        print(start)    #* DEBUG
        df_temp = get_stock_data(stock,start,timedelta_lst[i],'1m')
        df_lst.append(df_temp)

    
    # n_weekdays_ago = now - dt.timedelta(days=delta_days)
    # start_year = n_weekdays_ago.year
    # start_month = n_weekdays_ago.month
    # start_day = n_weekdays_ago.day
    # start = dt.datetime(start_year, start_month, start_day)
    # print(start)    #* DEBUG

    # # Get stock close data
    # df = get_stock_data(stock,start,now,'1m')
    # print(df)   #* DEBUG
    # df = df[['Close']]

    # # Calculate SMA
    # sum = df.sum()
    # len = df.size
    # sma = sum / len
    # print(sma)  #* DEBUG

    return

def get_rsi(df, delta_days=14):
    """ Calculate 14_Day RSI """
    now = dt.datetime.now()
    n_days_ago = now - dt.timedelta(days=delta_days)
    return

def get_MCAD(df):
    """ Calculate the MACD and Signal Line indicators """
    return

# MIGHT BE TERMINATED DUE TO YFINANCE LIBRARY BEING UNRELIABLE
def get_stock_data(stock,start_date,end_date,interval):
        """ 
        Get stock close data from yahoo finance using yfinance:
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo.
            Intraday data cannot extend last 60 days.

        Returns pandas dataframe.
        """
        df = yf.download(tickers=stock, start=start_date, end=end_date, interval=interval)
        df.reset_index(inplace=True) 

        # Re-parse datetime if interval is less than 1 day
        try:
            if interval[-1] == 'm':
                df["Datetime"] = pd.to_datetime(df["Datetime"]).dt.strftime('%m-%d-%Y %I:%M:%S %p')
        except:
            print("Error parsing datetime: Might be day's stock market is closed.")
            pass
      
        return df

""" Main Trading Algorithm """

def freshbot_trading():
    """ 
    Fresh trading algorithm:
        Uses sma(50), MACD, and RSI to determine buy/sell signals.
        Uses 1 minute interval data.
    """
    # Get stock data
    stocks = read_tickers(txt.TICKERS_EQUITY)

    market_open = marketStatus()
    while market_open:



        # Delay between each iteration
        asyncio.sleep(60)    # n second delay
        # Get market status
        market_open = marketStatus()

    return

""" Main """

def main():
    """ Testing Stage """

    # ticker = read_tickers(txt.TICKERS_EQUITY)
    # # ticker = 'AAPL'
    # # Last 3 years closing prices starting from Jan 2, 2018.
    
    # now = dt.datetime.now()
    # delta_days = 3
    # n_days_ago = now - dt.timedelta(days=delta_days)

    # start_year = n_days_ago.year
    # start_month = n_days_ago.month
    # start_day = n_days_ago.day
    # start = dt.datetime(start_year, start_month, start_day)

    # # pandas_datareader
    # df = pdr.get_data_yahoo(ticker, start, now)

    # # yfinance
    # df = get_stock_data('AAPl',start,now,'1m')
    # print(df)

    get_sma('AAPL', delta_days=6)
    return    

if __name__ == '__main__':
    main()