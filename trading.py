import asyncio
import yfinance as yf
import pandas_datareader.data as web
import pandas as pd
import datetime as dt

# Global variables
SOURCE = 'yahoo'
TODAY = dt.date.today()
NOW = dt.datetime.now()
WEEK_START = TODAY - dt.timedelta(days=TODAY.weekday())

# Read tickers from file and return list of tickers as strings
def read_tickers(file) -> list:
    with open(file, 'r') as f:
        return f.read().splitlines()

# Get quote of single stock
def get_quote(tick) -> str:
    stock = yf.Ticker(tick)
    return stock.info.get('symbol') + ": " + str(stock.info.get('currentPrice')) + " " + str(stock.info.get('currency'))

# Returns stock data of all tickers
def get_stock_quotes():
    ticks = []
    summary = []
    tickersEquity = read_tickers('tickersEquity.txt')
    tickersETF = read_tickers('tickersETF.txt')
    
    # Get stock data
    summary += ['__Equity:__\n']
    for ticker in tickersEquity:
        summary += [get_quote(ticker), '\n']


    summary += ['\n__ETF:__\n']
    for ticker in tickersETF:
        summary += [get_quote(ticker), '\n']
        
    # Return summary
    return ''.join(summary)
    

def main():
    return

    # Get stock data
    # df = web.DataReader(TICKERS[0], SOURCE, WEEK_START, TODAY)
    # df = web.DataReader('GE', 'yahoo', start='2019-09-10', end='2019-10-09')
    # print(df.head())
    
if __name__ == '__main__':
    main()