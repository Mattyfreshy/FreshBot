import yfinance as yf
import pandas as pd
import datetime as dt
import txt_dir as txt

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

def read_tickers(file) -> list:
    """ Read tickers from file and return list of tickers as strings """
    with open(file, 'r') as f:
        lst = []
        for line in f:
            if line.strip():
                lst.append(line.strip())
        return lst
    
def get_sma(stock: str, n=50):
    """ Calculate n_Day SMA (Default 50) """
    """ 
    Simple Moving Average:
        SMA = ( Sum ( Price, n ) ) / n    
        Where: n = Time Period in that respective unit (days, minutes, etc.)
    - Use 1m interval data for day trading.
    - Use 10m interval data for weekly trading.
    """
    # Get timeframe
    now = dt.datetime.now()
    n_days_ago = now - dt.timedelta(days=2)
    start_year = n_days_ago.year
    start_month = n_days_ago.month
    start_day = n_days_ago.day
    start = dt.datetime(start_year, start_month, start_day)

    # Get stock close data
    df = get_stock_data(stock,start,now,'1m')
    df_sum = sum(df['Close'][-n:])
    print(round(df_sum/n,2))

    return round(df_sum/n,2)

def get_rsi(df, delta_days=14):
    """ Calculate 14_Day RSI """
    now = dt.datetime.now()
    n_days_ago = now - dt.timedelta(days=delta_days)
    return

def get_MCAD(df):
    """ Calculate the MACD and Signal Line indicators """
    return

def get_stock_data(stock,start_date,end_date,interval):
        """ 
        Get stock close data from yahoo finance using yfinance.
        - Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo.
        - Intraday data cannot extend last 60 days.

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

""" Main """

def main():
    """ Testing Stage """
    ticker = read_tickers(txt.TICKERS_EQUITY)

    get_sma('AAPL',20)


    return    

if __name__ == '__main__':
    main()