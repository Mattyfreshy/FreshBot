import matplotlib.pyplot as plt
import numpy as np
import math
import asyncio
import yfinance as yf
import pandas_datareader.data as pdr
import pandas as pd
import datetime as dt
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

# Pandas settings/fixes. (pandas_datareader fix)
yf.pdr_override()
pd.set_option('mode.chained_assignment', None)

# Initialize variables
SMA_20 = 20
SMA_50 = 50
SMA_200 = 200

""" Utility Functions """

# Check if market is open
def marketStatus(): 
    weekday = dt.date.today().weekday() <= 4
    time = dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
    return weekday and time

# Read tickers from file and return list of tickers as strings
def read_tickers(file) -> list:
    with open(file, 'r') as f:
        lst = []
        for line in f:
            if line.strip():
                lst.append(line.strip())
        return lst
    
# Get RSI
def get_rsi(df, n=14):
    ## 14_Day RSI
    df['Up Move'] = np.nan
    df['Down Move'] = np.nan
    df['Average Up'] = np.nan
    df['Average Down'] = np.nan
    # Relative Strength
    df['RS'] = np.nan
    # Relative Strength Index
    df['RSI'] = np.nan
    ## Calculate Up Move & Down Move
    for x in range(1, len(df)):
        df['Up Move'][x] = 0
        df['Down Move'][x] = 0
        
        if df['Adj Close'][x] > df['Adj Close'][x-1]:
            df['Up Move'][x] = df['Adj Close'][x] - df['Adj Close'][x-1]
            
        if df['Adj Close'][x] < df['Adj Close'][x-1]:
            df['Down Move'][x] = abs(df['Adj Close'][x] - df['Adj Close'][x-1])  
            
    ## Calculate initial Average Up & Down, RS and RSI
    df['Average Up'][14] = df['Up Move'][1:15].mean()
    df['Average Down'][14] = df['Down Move'][1:15].mean()
    df['RS'][14] = df['Average Up'][14] / df['Average Down'][14]
    df['RSI'][14] = 100 - (100/(1+df['RS'][14]))
    ## Calculate rest of Average Up, Average Down, RS, RSI
    for x in range(15, len(df)):
        df['Average Up'][x] = (df['Average Up'][x-1]*13+df['Up Move'][x])/14
        df['Average Down'][x] = (df['Average Down'][x-1]*13+df['Down Move'][x])/14
        df['RS'][x] = df['Average Up'][x] / df['Average Down'][x]
        df['RSI'][x] = 100 - (100/(1+df['RS'][x]))

    ## Chart the stock price and RSI
    plt.style.use('classic')
    fig, axs = plt.subplots(2, sharex=True, figsize=(13,9))
    fig.suptitle('AAPL Stock Price (top) - 14 day RSI (bottom)')
    axs[0].plot(df['Adj Close'])
    axs[1].plot(df['RSI'])
    axs[0].grid()
    axs[1].grid()
    plt.ylim(0,100)
    plt.xlim(len(df.index)-10,len(df.index))
    plt.show()

# Get MACD
def get_MCAD(df):
    ## Calculate the MACD and Signal Line indicators
    ## Calculate the Short Term Exponential Moving Average
    ShortEMA = df.Close.ewm(span=12, adjust=False).mean() 
    ## Calculate the Long Term Exponential Moving Average
    LongEMA = df.Close.ewm(span=26, adjust=False).mean() 
    ## Calculate the Moving Average Convergence/Divergence (MACD)
    MACD = ShortEMA - LongEMA
    ## Calculate the signal line
    signal = MACD.ewm(span=9, adjust=False).mean()

    ## Plot the Chart
    plt.figure(figsize=(14,8))
    plt.style.use('classic')
    plt.plot(df.index, MACD, label='MACD', color = 'blue')
    plt.plot(df.index, signal, label='Signal Line', color='red')
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.show()

""" Main Trading Algorithm """

# Main trading algorithm
def freshbot_trading():
    """ Uses sma(50), MACD, and RSI to determine buy/sell signals """
    """ Uses 1 minute interval data """

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
    ticker = read_tickers(txt.TICKERS_EQUITY)
    # ticker = 'AAPL'
    # Last 3 years closing prices starting from Jan 2, 2018.
    
    now = dt.datetime.now()
    delta_days = 5
    n_days_ago = now - dt.timedelta(days=delta_days)

    start_year = n_days_ago.year
    start_month = n_days_ago.month
    start_day = n_days_ago.day
    start = dt.datetime(start_year, start_month, start_day)


    # Pandas DataReader
    df = pdr.get_data_yahoo(ticker, start=start, end=now)
    print(df.tail(20)['Close'])
    # get_rsi(df.tail(20))
    # get_MCAD(df.tail(100))

    return    

if __name__ == '__main__':
    main()