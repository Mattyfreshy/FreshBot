import asyncio
import yfinance as yf
import pandas_datareader.data as web
import pandas as pd
import datetime as dt
import trading.txt_dir as txt

""" 
Module of functions for obtaining stock data and returning them 
(For discord bot only)
"""

# Pandas settings/fixes. (pandas_datareader fix)
yf.pdr_override()
pd.set_option('mode.chained_assignment', None)

# Global variables
SOURCE = 'yahoo'
TODAY = dt.date.today()
NOW = dt.datetime.now()
WEEK_START = TODAY - dt.timedelta(days=TODAY.weekday())

# Read tickers from file and return list of tickers as strings
def read_tickers(file) -> list:
    with open(file, 'r') as f:
        lst = []
        for line in f:
            if line.strip():
                lst.append(line.strip())
        return lst

# Get quote of single stock
def get_quote(tick) -> str:
    stock = yf.Ticker(tick)
    return stock.info.get('symbol') + ": " + str(round(float(stock.info.get('currentPrice')), 2)) + " " + str(stock.info.get('currency'))

# Returns stock data of all tickers
def get_stock_quotes():
    ticks = []
    summary = []
    tickersEquity = read_tickers(txt.TICKERS_EQUITY)
    tickersETF = read_tickers(txt.TICKERS_ETF)
    
    # Get stock data
    if len(tickersEquity) > 0:
        summary += ['__Equity:__\n']
        for ticker in tickersEquity:
            summary += [get_quote(ticker), '\n']

    if len(tickersETF) > 0:
        summary += ['\n__ETF:__\n']
        for ticker in tickersETF:
            summary += [get_quote(ticker), '\n']
        
    # Return summary
    return ''.join(summary)
    

def main():
    print(get_stock_quotes())
    return

    # Get stock data
    # df = web.DataReader(TICKERS[0], SOURCE, WEEK_START, TODAY)
    # df = web.DataReader('GE', 'yahoo', start='2019-09-10', end='2019-10-09')
    # print(df.head())
    
if __name__ == '__main__':
    main()