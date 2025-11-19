import yfinance as yf
import pandas as pd


def fetch_stock_data(ticker_symbol, period, interval):
    """Fetch historical stock data for a given ticker symbol and period."""

    # search for ticker in yahoo and get all the data connected to that ticker
    try:

        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period=period, interval=interval)

        return data[['Close', 'Open', 'High', 'Low']]

    except Exception as e:
        print(f"{e}")
        return None


def fetch_stock_data_set_dates(ticker_symbol, start, end):

    try:

        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(start=start, end=end)

        return data

    except Exception as e:

        return None

def fetch_multiple_stocks_data(ticker_symbols, period, interval):
    """Fetch historical stock data for multiple ticker symbols."""

    tickers = yf.download(ticker_symbols, period=period, interval=interval, group_by='ticker', threads=True, auto_adjust=True, progress=False)
    
    return tickers