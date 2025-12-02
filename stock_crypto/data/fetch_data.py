import yfinance as yf

# https://algotrading101.com/learn/yahoo-finance-api-guide/


def fetch_stock_data(ticker_symbol, period, interval):
    """
    This fetches the data from today to six months ago. Works best with single stocks.
    YF gives us a df with the ticker, close open high and low-prices as well as an index
    """

    # search for ticker in yahoo and get all the data connected to that ticker
    try:

        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period=period, interval=interval)

        return data[['Close', 'Open', 'High', 'Low']]

    except Exception as e:
        # fails if ticker is not existent and give me debugging options
        print(f"{e}")
        return None


def fetch_stock_data_set_dates(ticker_symbol, start, end):
    '''
    I mainly use it to fezch history with set dates for the historical heatmaps, so I can add Quarter start and end and get all the 
    important info for the quarter
    '''
    try:
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(start=start, end=end)

        return data

    except Exception as e:
        print(f"{e}")
        return None


def fetch_multiple_stocks_data(ticker_symbols, period, interval):
    """
    Fetch historical stock data for multiple ticker symbols. Ideal for creating heatmaps, 
    as we need a lot of tickers at once for the heatmap. 
    """
    # get data for multiple tickers, way way way faster than looping through them one by one
    tickers = yf.download(ticker_symbols, period=period, interval=interval,
                          group_by='ticker', threads=True, auto_adjust=True, progress=False)

    return tickers


def fetch_multiple_stocks_data_set_dates(ticker_symbols, start, end):
    """
    Fetch historical stock data for multiple ticker symbols within a date range.
    Idea is to use it for the database for quicker work, not implemented yet
    """
    tickers = yf.download(ticker_symbols, start=start, end=end,
                          group_by='ticker', threads=True, auto_adjust=True, progress=False)

    return tickers
