import yfinance as yf
import pandas_datareader.data as web
import pandas as pd
import datetime as dt

# Data source
SOURCE = 'yahoo'

# Stock tickers
TICKERS = ['AAPL', 'TSLA']


def main():
    today = dt.date.today()
    now = dt.datetime.now()
    week_start = today - dt.timedelta(days=today.weekday())
    print(week_start)

    # Get stock data
    # df = web.DataReader(TICKERS[0], SOURCE, week_start, today)
    df = web.DataReader('GE', 'yahoo', start='2019-09-10', end='2019-10-09')
    print(df.head())
    
if __name__ == '__main__':
    main()