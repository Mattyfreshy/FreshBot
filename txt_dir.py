import os

""" Module for file paths of text files """

# Text file Directories/Filepaths
cwd = os.getcwd()
TXT_DIR = 'trading/txt/'
ML_DIR = 'trading/models/'
TICKERS_EQUITY = TXT_DIR + 'tickersEquity.txt'
TICKERS_ETF = TXT_DIR + 'tickersETF.txt'
TRADES = TXT_DIR + 'trades.txt'
AAPL_MODEL = ML_DIR + 'AAPL_model.joblib'

def main():
    return

if __name__ == '__main__':
    main()