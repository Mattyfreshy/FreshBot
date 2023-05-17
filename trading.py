import yfinance as yf
#import pandas_datareader.data as web
import pandas as pd
import datetime as dt

# Global variables
SOURCE = 'yahoo'
TICKERS = ['AAPL', 'META', 'TSLA', 'AMZN']
TODAY = dt.date.today()
NOW = dt.datetime.now()
WEEK_START = TODAY - dt.timedelta(days=TODAY.weekday())

# Get quote of single stock
def get_quote(tick):
    stock = yf.Ticker(tick)
    return stock.info['symbol'] + ": " + str(stock.info['currentPrice']) + " " + str(stock.info['currency'])

# Returns stock data of all tickers
def get_stock_quotes():
    ticks = []
    stock_infos = []
    summary = []
    
    # Get stock data
    for ticker in TICKERS:
        ticks.append(yf.Ticker(ticker))
    
    # Get stock info
    for stock in ticks:
        stock_infos.append(stock.info)

    # Create summary
    for tick in ticks:
        summary.append(tick.info['symbol'] + ": " + str(tick.info['currentPrice']) + " " + str(tick.info['currency']))
        summary.append("\n")
    
    # Add Spacer
    summary.append("------------------\n")

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