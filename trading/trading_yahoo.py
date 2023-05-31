import yfinance as yf
import pandas as pd
import datetime as dt
import txt_dir as txt
import asyncio

import talib as ta

"""
Technical Indicators from yfinance:
    - Simple Moving Average (SMA)
    - Relative Strength Index (RSI)
    - Moving Average Convergence Divergence (MACD)
"""

# Pandas settings/fixes. (pandas_datareader fix)
yf.pdr_override()
pd.set_option('mode.chained_assignment', None)


""" Technical Indicator Functions """

def marketStatus(self): 
    """ Returns True if market is open, False if market is closed """
    weekday = dt.date.today().weekday() <= 4
    time = dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
    return weekday and time

def read_tickers(file) -> list:
    """ 
    Read tickers from file and return list of tickers as strings 
    Returns: list of tickers as strings
    """
    with open(file, 'r') as f:
        lst = []
        for line in f:
            if line.strip():
                lst.append(line.strip())
        return lst
    
def get_sma(df, *, timeperiod=50):
    """ 
    Calculate n_Day SMA (Default 50)
        Simple Moving Average:
            SMA = ( Sum ( Price, n ) ) / n    
            Where: n = Time Period in that respective unit (days, minutes, etc.)
        - Use 1m interval data for day trading.
        - Use 10m interval data for weekly trading.
    
    Returns: SMA
    """
    # Get stock close data
    df_sum = sum(df['Close'][-timeperiod:])
    # return df_sum/n
    return ta.SMA(df['Close'], timeperiod=timeperiod)[-1:]

def get_rsi(df, *, timeperiod=14):
    """ 
    Calculate 14_Day RSI 
        RSI Step 1:
            RSI = 100 - (100 / (1 + RS))
            Where:
                RS = Average Gain / Average Loss
                Average Gain = Sum of Gains over the past 14 periods / 14
                Average Loss = Sum of Losses over the past 14 periods / 14
        RSI Step 2:
            Calculate Relative Strength (RS)
            RS = Average Gain / Average Loss
            Where:
                Average Gain = [(previous Average Gain) x 13 + current Gain] / 14
                Average Loss = [(previous Average Loss) x 13 + current Loss] / 14
    
    Returns: RSI
    """
    return ta.RSI(df['Close'], timeperiod=timeperiod)[-1:]

def get_MCAD(df, *, fastperiod=12, slowperiod=26, signalperiod=9):
    """ 
    Calculate the MACD and Signal Line indicators 
        MCAD:
            MACD = 12_Day EMA - 26_Day EMA
            Signal Line = 9_Day EMA of MACD
            Histogram = MACD - Signal Line
        EMA:
            EMA = (Price(t) x K) + (EMA(y) x (1-K))
            Where:
                t = today
                y = yesterday
                N = number of days in EMA
                K = 2 / (N+1)

    Returns: tuple(MACD, Signal Line, Histogram)
    """
    mcad, signal, hist = ta.MACD(df['Close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    return  (mcad[-1:], signal[-1:], hist[-1:])

def get_stock_data(stock,interval):
        """ 
        Get stock close data from yahoo finance using yfinance.
        - Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo.
        - Intraday data cannot extend last 60 days.

        Returns pandas dataframe.
        """
        # Get timeframe
        now = dt.datetime.now()
        n_days_ago = now - dt.timedelta(days=2)
        start_year = n_days_ago.year
        start_month = n_days_ago.month
        start_day = n_days_ago.day
        start = dt.datetime(start_year, start_month, start_day)

        df = yf.download(tickers=stock, start=start, end=now, interval=interval)
        df.reset_index(inplace=True) 

        # Re-parse datetime if interval is less than 1 day
        try:
            if interval[-1] == 'm':
                df["Datetime"] = pd.to_datetime(df["Datetime"]).dt.strftime('%m-%d-%Y %I:%M:%S %p')
        except:
            print("Error parsing datetime: Might be day's stock market is closed.")
            pass
      
        return df

""" Main """

def main():
    """ Testing Stage """
    ticker = read_tickers(txt.TICKERS_EQUITY)

    market_open = marketStatus()
    while market_open:
        df = get_stock_data(ticker[0],'1m')

        # Technical indicators
        sma_20 = get_sma(df, 20)
        sma_50 = get_sma(df, 50)
        rsi = get_rsi(df)
        mcad_tuple = get_MCAD(df)
        mcad = mcad_tuple[0]
        signal = mcad_tuple[1]

        print('SMA_20: ', sma_20)
        print('SMA_50: ', sma_50)
        print('RSI: ', rsi)
        print('MACD: ', mcad)
        print('Signal: ', signal)

        # Delay between each iteration
        asyncio.sleep(60)    # n second delay
        # Get market status
        market_open = marketStatus()

    return    

if __name__ == '__main__':
    main()