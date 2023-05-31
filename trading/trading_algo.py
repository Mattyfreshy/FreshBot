import datetime as dt
import txt_dir as txt
import math
import asyncio
import os

from dotenv import load_dotenv
from config import ALPACA_CONFIG

import matplotlib.pyplot as plt
import numpy as np

import plotly.graph_objects as go
import plotly.express as px

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
        self.sleeptime = 1
        self.tickers = self.read_tickers(txt.TICKERS_EQUITY)

    def marketStatus(self): 
        """ Returns True if market is open, False if market is closed """
        weekday = dt.date.today().weekday() <= 4
        time = dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
        return weekday and time

    def read_tickers(file) -> list:
        """ Read tickers from file and return list of tickers as strings """
        with open(file, 'r') as f:
            lst = []
            for line in f:
                if line.strip():
                    lst.append(line.strip())
            return lst
        
    def get_sma(self, stock: str, n=SMA_50):
        """ Calculate n_Day SMA (Default 50) """
        """ 
        Simple Moving Average:
            SMA = ( Sum ( Price, n ) ) / n    
            Where: n = Time Period in that respective unit (days, minutes, etc.)
        - Use 1m interval data for day trading.
        - Use 10m interval data for weekly trading.
        """
        # now = dt.datetime.now() # Current date
        # asset = 'AAPL'
        # historical_prices = self.get_historical_prices(
        #     asset=asset,
        #     length=100,
        #     timestep="day",
        # )

        # df = historical_prices.df
        # df_20 = df['close'][-n:]
        # # print(df['close'][-20:].reset_index())
        # sma_20 = ta.SMA(df_20, timeperiod=20)
        # # print(df.reset_index())
        # print(sma_20[0])

        return

    def get_rsi(self, df, delta_days=14):
        """ Calculate 14_Day RSI """
        now = dt.datetime.now()
        n_days_ago = now - dt.timedelta(days=delta_days)
        return

    def get_MCAD(self, df):
        """ Calculate the MACD and Signal Line indicators """
        return

    def on_trading_iteration(self):
        self.FreshStrategy()

    """ Main Trading Algorithm """

    def FreshStrategy(self):
        """ 
        Fresh trading algorithm:
            Uses sma(50), MACD, and RSI to determine buy/sell signals.
            Uses 1 minute interval data.
        ----------------------------------
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
        # Get stock data
        stocks = self.read_tickers(txt.TICKERS_EQUITY)

        market_open = self.marketStatus()
        while market_open:
            # Buy status variable
            buy = False

            
            # Algorithm
            if buy:
                # Stock already bought
                # Sell if conditions are met
                
                pass
            else:
                # Stock not bought
                # Buy if conditions are met

                pass


            # Delay between each iteration
            asyncio.sleep(60)    # n second delay
            # Get market status
            market_open = self.marketStatus()

        return

""" Main """

def main():
    trader = Trader()
    broker = Alpaca(ALPACA_CONFIG)
    strategy = FreshTrading(name='FreshStrategy', broker=broker)

    print(strategy.get_sma('AAPL'))

    """ Testing Stage """
    # backtesting_start = dt.datetime(2020, 1, 1)
    # backtesting_end = dt.datetime(2020, 12, 31)
    # strategy.backtest(
    #     YahooDataBacktesting,
    #     backtesting_start,
    #     backtesting_end,
    #     parameters= {
    #         "symbol": "SPY"
    #     },
    # )

    # trader.add_strategy(strategy)
    # trader.run_all()

    return    

if __name__ == '__main__':
    main()