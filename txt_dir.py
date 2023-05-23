import asyncio
import yfinance as yf
import pandas_datareader.data as web
import pandas as pd
import datetime as dt
import trading as td

""" Module for file paths of text files """

# Text file Directories/Filepaths
DIR = 'txt/'
TICKERS_EQUITY = DIR + 'tickersEquity.txt'
TICKERS_ETF = DIR + 'tickersETF.txt'
TRADES = DIR + 'trades.txt'

def main():
    print(TICKERS_EQUITY)
    return

if __name__ == '__main__':
    main()