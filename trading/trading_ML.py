import yfinance as yf
import pandas as pd
import datetime as dt
import txt_dir as txt
import numpy as np
import talib as ta
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

"""
Technical Indicators from yfinance:
    - Simple Moving Average (SMA)
    - Relative Strength Index (RSI)
    - Moving Average Convergence Divergence (MACD)
"""

# Pandas settings/fixes. (pandas_datareader fix)
yf.pdr_override()
pd.set_option('mode.chained_assignment', None)

""" Utility Functions """

def get_time_now_format(format):
    """ 
    Return time format depending on user preference
    - 12 hour (default) 
    - 24 hour 
    """
    if format == '12':
        return dt.datetime.now().strftime("%m-%d-%Y %I:%M:%S %p")
    elif format == '24':
        return dt.datetime.now().strftime("%H:%M:%S")
    else:
        return dt.datetime.now().strftime("%m-%d-%Y %I:%M:%S %p")
    
def marketStatus(): 
    """ Returns True if market is open, False if market is closed """
    weekday = dt.date.today().weekday() <= 4
    time = dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
    return weekday and time

def calculate_profit(txt):
    """ 
    Calculate profit from txt file
    Returns: profit
    """
    with open(txt, 'r') as f:
        profit = 0
        for line in f:
            if line.strip():
                line_split = line.split()
                if 'Buy' in line:
                    profit -= float(line_split[-1])
                elif 'Sell' in line:
                    profit += float(line_split[-1])
        return profit

""" Technical Indicator Functions """

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
    # df_sum = sum(df['Close'][-timeperiod:])
    # return df_sum/n
    return ta.SMA(df['Close'], timeperiod=timeperiod).tolist()[-1]

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
    return ta.RSI(df['Close'], timeperiod=timeperiod).tolist()[-1]

def get_macd(df, *, fastperiod=12, slowperiod=26, signalperiod=9):
    """ 
    Calculate the MACD and Signal Line indicators 
        MACD:
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
    macd, signal, hist = ta.MACD(df['Close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    return  (macd.tolist()[-1], signal.tolist()[-1], hist.tolist()[-1])

def get_stock_data(stock,interval):
        """ 
        Get stock close data from yahoo finance using yfinance.
        - Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo.
        - Intraday data cannot extend last 60 days.

        Returns pandas dataframe.
        """
        # Get timeframe
        now = dt.datetime.now()
        n_days_ago = now - dt.timedelta(days=5)
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

def train_model(ticker: str, interval: str):
    """ 
    Train model using stock data.
        - ticker must be valid in str format (e.g., 'AAPL')
        - Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo.
    Returns: trained model
    """
    df = get_stock_data(ticker, interval)

    # Technical indicators
    current_price = df['Close'].tolist()[-1]
    sma_20 = get_sma(df, timeperiod=20)
    sma_50 = get_sma(df, timeperiod=50)
    rsi = get_rsi(df)
    macd_tuple = get_macd(df)
    macd = macd_tuple[0]
    signal = macd_tuple[1]

    # Create labels indicating buy or sell based on a simple strategy (e.g., if tomorrow's close price > today's close price, label it as 1)
    df['Label'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)

    # Separate the features (SMA, RSI, MACD) and labels
    features = pd.DataFrame({'SMA_20': sma_20, 'SMA_50': sma_50, 'RSI': rsi, 'MACD': macd, 'Signal': signal}, index=df.index).fillna(0)  # Fill missing values with 0
    labels = df['Label']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    # Create and train the random forest classifier
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Predict labels for the test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print('Accuracy:', accuracy)

    # Save the trained model to a file
    time.sleep(1)
    joblib.dump(model, 'trading/models/AAPL_model.joblib')

    pass

""" Main """

def main():
    """ Testing Stage """
    
    train_model('AAPL', '15m')

    return    

if __name__ == '__main__':
    main()