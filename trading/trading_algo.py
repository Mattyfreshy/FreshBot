import datetime as dt
import txt_dir as txt
import asyncio
import os
import trading_yahoo as tdy

from dotenv import load_dotenv
from config import ALPACA_CONFIG

from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.entities import Asset, TradingFee
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
import talib as ta


# Load environment variables
load_dotenv()

# Initialize variables
alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')
SMA_20 = 20
SMA_50 = 50
SMA_200 = 200


class FreshTrading(Strategy):
    """ lumibot library strategy class """

    def initialize(self):
        self.sleeptime = 1  # minutes
        self.tickers = self.read_tickers(txt.TICKERS_EQUITY)

    def marketStatus(self): 
        """ Returns True if market is open, False if market is closed """
        weekday = dt.date.today().weekday() <= 4
        time = dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
        return weekday and time

    def read_tickers(self, file) -> list:
        """ Read tickers from file and return list of tickers as strings """
        with open(file, 'r') as f:
            lst = []
            for line in f:
                if line.strip():
                    lst.append(line.strip())
            return lst
        
    def get_sma(self, df, *, timeperiod=50):
        """ 
        Calculate n_Day SMA (Default 50)
            Simple Moving Average:
                SMA = ( Sum ( Price, n ) ) / n    
                Where: n = Time Period in that respective unit (days, minutes, etc.)
            - Use 1m interval data for day trading.
            - Use 10m interval data for weekly trading.
        
        Returns: float value
        """
        return ta.SMA(df['close'], timeperiod=timeperiod).tolist()[-1]

    def get_rsi(self, df, *, timeperiod=14):
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
        
        Returns: float value
        """
        return ta.RSI(df['close'], timeperiod=timeperiod).tolist()[-1]

    def get_macd(self, df, *, fastperiod=12, slowperiod=26, signalperiod=9):
        """ 
        Calculate the MACD and Signal Line indicators.
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
        macd, signal, hist = ta.MACD(df['close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
        return  (macd.tolist()[-1], signal.tolist()[-1], hist.tolist()[-1])
    
    def get_stock_data(self, asset, length, timestep):
        """ 
        Get historical prices for a given asset.
            asset: str
                Ticker symbol of asset
            length: int
                Number of days to get historical prices for
            timestep: str
                Time interval of historical prices
                - 'minute'
                - 'day'

        Returns: DataFrame
        """
        historical_prices = self.get_historical_prices(
            asset=asset,
            length=length,
            timestep=timestep,
        )

        df = historical_prices.df
        return df

    def on_trading_iteration(self):
        self.FreshStrategy()

    """ Main Trading Algorithm """

    def FreshStrategy(self):
        """ 
        Fresh trading algorithm:
            Uses sma(50), MACD, and RSI to determine buy/sell signals.
            - Uses 1 minute interval data for daily.
            - Uses 5 minute interval data for weekly.
        ----------------------------------
        Algorithm:
            Buy:
            - Stock price >= SMA(50)
            - MACD crosses above signal line
            - RSI < 65
            
            Sell:
            - Stock price <= SMA(20)
            - MACD crosses below signal line
            - RSI > 35
        """
        # Backtesting
        backtesting = True
        debug = False
        ticker = 'AAPL'

        # Get stock data
        # stocks = self.read_tickers(txt.TICKERS_EQUITY)

        if self.marketStatus() or backtesting:
            # Buy status variable
            has_position = self.get_position(ticker)

            # Get stock data
            df = self.get_stock_data(asset=ticker, length=100, timestep='day')

            # Technical indicators
            # current_price = df['close'].tolist()[-1]
            current_price = self.get_last_price(ticker)
            sma_20 = self.get_sma(df, timeperiod=20)
            sma_50 = self.get_sma(df, timeperiod=50)
            rsi = self.get_rsi(df)
            macd_tuple = self.get_macd(df)
            macd = macd_tuple[0]
            signal = macd_tuple[1]

            quantity = self.portfolio_value // current_price

            if debug:
                print(dt.datetime.now())
                print('Current Price: ', current_price)
                print('SMA_20: ', sma_20)
                print('SMA_50: ', sma_50)
                print('RSI: ', rsi)
                print('MACD: ', macd)
                print('Signal: ', signal)

            if has_position:
                if current_price <= sma_20 and macd < signal and rsi > 30:
                    order = self.create_order(ticker, quantity, 'sell')   
                    self.submit_order(order)                 
            else:
                if current_price >= sma_50 and macd > signal and rsi < 70:
                    order = self.create_order(ticker, quantity, 'buy')
                    self.submit_order(order)

        return

""" Main """

def main():
    trader = Trader()
    broker = Alpaca(ALPACA_CONFIG)
    strategy = FreshTrading(name='FreshStrategy', broker=broker)

    # df = strategy.get_stock_data(asset='AAPL', length=100, timestep='minute')
    # print(strategy.get_sma(df, timeperiod=20))

    """ Testing Stage """
    backtesting_start = dt.datetime(2020, 1, 1)
    backtesting_end = dt.datetime(2020, 12, 31)
    strategy.backtest(
        YahooDataBacktesting,
        backtesting_start,
        backtesting_end,
    )

    """ Run Strategy Live """
    # trader.add_strategy(strategy)
    # trader.run_all()

    return    

if __name__ == '__main__':
    main()