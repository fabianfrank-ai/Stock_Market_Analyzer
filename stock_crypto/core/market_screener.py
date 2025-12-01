# this program will screen the maket to find eligible stocks to buy

import pandas as pd
import numpy as np
import urllib.request
from data.fetch_data import fetch_stock_data, fetch_stock_data_set_dates, fetch_multiple_stocks_data
from core.indicators import sma, bollinger_bands, rsi, ema, macd, atr
from core.verdict import Verdict


def get_tickers():

    # Get the list of S&P 500 companies from Wikipedia
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    tables = pd.read_html(html)

    # filter all the tickers from the table on wikipedia
    # note: the S&P 500 table is the second table on the page now because they changed it recently
    sp500_tickers = tables[1]['Symbol'].tolist()
    # wikipedia uses dots in some ticker symbols, but yfinance needs dashes (e.g. BF.B -> BF-B)
    sp500_tickers = [t.replace(".", "-") for t in sp500_tickers]

    # fetch data for all tickers at once to improve performance
    ticker_dataframe = fetch_multiple_stocks_data(
        sp500_tickers, period="6mo", interval='1d')
    dfs = {
        # create a dictionary of dataframes for each ticker
        ticker: ticker_dataframe[ticker] for ticker in sp500_tickers if ticker in ticker_dataframe.columns.get_level_values(0)
    }
    return dfs


def heatmap(start, end):
    """Generate a Dataframe of S&P 500 companies based on their gain/loss percentage over the last day."""

    ticker_data = []
    change_data = []
    verdict = []
    sma_data = []
    bollinger_data = []
    rsi_data = []
    ema_data = []
    macd_data = []
    atr_data = []

    dfs = get_tickers()

    # for every ticker in sp500(what is in the dataframe)
    for ticker in list(dfs.keys()):
        try:

            # fetch data, depending on whether start and end dates are provided (for database or not)
            if start is None and end is None:
                data = dfs[ticker]
                sma_percentage = (
                    sma(data, 30).iloc[-1] - sma(data, 100).iloc[-1]) / sma(data, 100).iloc[-1] * 100
                latest_close = data['Close'].iloc[-1]
                previous_close = data['Close'].iloc[-2]
                latest_change = (
                    (latest_close - previous_close) / previous_close) * 100
                latest_change = round(latest_change, 2)
            else:
                # use the provided dates to fetch data
                data = fetch_stock_data_set_dates(ticker, start=start, end=end)
                # calculate sma percentages based on shorter timeframes, due to the length of a quartal
                sma_percentage = (
                    sma(data, 20).iloc[-1] - sma(data, 50).iloc[-1]) / sma(data, 50).iloc[-1] * 100
                # calculate the change from the first to the last available data point, for more meaningful results
                latest_close = data['Close'].iloc[-1]
                previous_close = data['Close'].iloc[0]
                latest_change = (
                    (latest_close - previous_close) / previous_close) * 100
                latest_change = round(latest_change, 2)

            # check if data is valid
            if data is None or len(data) < 2:
                print(f"Not enough data for {ticker}")
                continue

            # append all the data to the respective lists
            ticker_data.append(ticker)
            change_data.append(latest_change)

            ema_percentage = (
                ema(data, 12).iloc[-1] - ema(data, 26).iloc[-1]) / ema(data, 26).iloc[-1] * 100
            ema_percentage = round(ema_percentage, 2)
            sma_percentage = round(sma_percentage, 2)

            macd_line, signal_line = macd(data)
            macd_difference = macd_line.iloc[-1] - signal_line.iloc[-1]
            macd_difference = round(macd_difference, 2)

            # calculate indicators for the ticker and append the relevant data to the respective lists
            sma_data.append(sma_percentage)
            lower_band, upper_band = bollinger_bands(data, 30)
            bollinger_percentage = (
                data['Close'].iloc[-1] - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])
            bollinger_percentage = round(bollinger_percentage, 2)
            rsi_value = rsi(data, 14).iloc[-1]
            rsi_value = round(rsi_value, 2)

            bollinger_data.append(bollinger_percentage)
            rsi_data.append(rsi_value)
            ema_data.append(ema_percentage)
            macd_data.append(macd_difference)

            # generate and append the verdict for the ticker
            verdict_signal = Verdict(data, sma(data, 100), sma(
                data, 30), ema(data, 26), ema(data, 12), rsi(data, 14), signal_line, macd_line)
            verdict.append(verdict_signal.verdict)

            atr_value = atr(data)
            atr_value = round(atr_value, 2)
            atr_data.append(atr_value)

            # create a dataframe from the lists
            df = pd.DataFrame({
                'Ticker': ticker_data,
                'Change': change_data,
                'SMA Diff': sma_data,
                'Bollinger %': bollinger_data,
                'RSI': rsi_data,
                'EMA Diff': ema_data,
                'MACD Diff': macd_data,
                'Verdict': verdict,
                'Risk': atr_data
            })

        # Print any errors and continue with the next ticker
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue


# return the dataframe
    return df


def heatmap_portfolio(portfolio):
    """Generate a Dataframe of Portfolio input based on their gain/loss percentage over the last day. And other indicators"""

    # create empty lists to store the data, lists are then used to create a dataframe at the end
    ticker_data = []
    change_data = []
    verdict = []
    sma_data = []
    bollinger_data = []
    rsi_data = []
    ema_data = []
    macd_data = []
    atr_data = []

    # filter all the tickers from the table on wikipedia
    portfolio = portfolio['Ticker'].to_list()

    # for every ticker in sp500
    for ticker in portfolio:
        try:

            # fetch data
            data = fetch_stock_data(ticker, "6mo", '1d')
            print(len(data))
            # check if data is valid
            if data is None or len(data) < 2:
                print(f"Not enough data for {ticker}")
                continue

            # calculate the percentage change from the previous close to the latest close
            latest_close = data['Close'].iloc[-1]
            previous_close = data['Close'].iloc[-2]
            latest_change = (
                (latest_close - previous_close) / previous_close) * 100

            # append all the data to the respective lists
            ticker_data.append(ticker)
            change_data.append(latest_change)

            ema_percentage = (
                ema(data, 12).iloc[-1] - ema(data, 26).iloc[-1]) / ema(data, 26).iloc[-1] * 100
            sma_percentage = (
                sma(data, 30).iloc[-1] - sma(data, 100).iloc[-1]) / sma(data, 100).iloc[-1] * 100

            macd_line, signal_line = macd(data)
            macd_difference = macd_line.iloc[-1] - signal_line.iloc[-1]

            # calculate indicators for the ticker and append the relevant data to the respective lists
            sma_data.append(sma_percentage)
            lower_band, upper_band = bollinger_bands(data, 30)
            bollinger_percentage = (
                data['Close'].iloc[-1] - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])

            bollinger_data.append(bollinger_percentage)
            rsi_data.append(rsi(data, 14).iloc[-1])
            ema_data.append(ema_percentage)
            macd_line, signal_line = macd(data)
            macd_data.append(macd_difference)

            # generate and append the verdict for the ticker
            verdict.append(Verdict(data, sma(data, 100), sma(
                data, 30), ema(data, 26), ema(data, 12), rsi(data, 14), signal_line, macd_line).verdict)

            atr_data.append(atr(data))

            # create a dataframe from the lists
            df = pd.DataFrame({
                'Ticker': ticker_data,
                'Change': change_data,
                'SMA Diff': sma_data,
                'Bollinger %': bollinger_data,
                'RSI': rsi_data,
                'EMA Diff': ema_data,
                'MACD Diff': macd_data,
                'Verdict': verdict,
                'Risk': atr_data
            })

        # Print any errors and continue with the next ticker
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue


# return the dataframe
    return df


def correlations(start, end):
    '''Calculates the correlations of the S&P 500 stock movements within the past 6 months'''

    dfs = get_tickers()

    data_dictionary = {}

    # for every ticker in sp500
    for ticker in list(dfs.keys()):
        try:

            # fetch data
            if start is None and end is None:
                data = dfs[ticker]
            else:
                data = fetch_stock_data_set_dates(ticker, start, end)

            changes = []

            # calculate the percentage change from the previous close to the latest close
            for i in range(len(data['Close']) - 1):
                latest_close = data['Close'].iloc[i + 1]
                previous_close = data['Close'].iloc[i]
                latest_change = (
                    (latest_close - previous_close) / previous_close) * 100

                changes.append(latest_change)

            if changes:
                data_dictionary[ticker] = changes

        # Print any errors and continue with the next ticker
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    if data_dictionary:
     # create dataframw ith NaN padding : with debugging for now

        try:
            df = pd.DataFrame(data_dictionary)
            print(f"DataFrame created with shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")

        except Exception as e:
            print(f"Error creating DataFrame with direct method: {e}")

            # Fallback if lengths do not allign
            max_length = max(len(v) for v in data_dictionary.values())
            print(f"Max length found: {max_length}")

            padded_dict = {}

            for ticker, changes in data_dictionary.items():
                current_length = len(changes)

                if current_length < max_length:

                    # fill with nAn

                    padded_changes = changes + \
                        [np.nan] * (max_length - current_length)
                    padded_dict[ticker] = padded_changes

                else:
                    padded_dict[ticker] = changes

            df = pd.DataFrame(padded_dict)
            print(f"DataFrame created with padding, shape: {df.shape}")

    df_correlation = df.corr()


# return the dataframe
    return df_correlation
