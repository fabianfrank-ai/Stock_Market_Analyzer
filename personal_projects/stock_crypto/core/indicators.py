# chatgpt was used to suggest equations for suitable indicatiors
import pandas as pd

sma = pd.DataFrame()
crossings_data = []


def sma(data, window):
    """Calculate Simple Moving Average (SMA)"""

    # SMA = sum of closing prices over the window / window size (SMA30 and 100 are used, so window=100)
    # https://medium.com/analytics-vidhya/sma-short-moving-average-in-python-c656956a08f8
    sma = data['Close'].rolling(window=window).mean()

    return sma


def moving_average_crossover(data, short_ma, long_ma):
    """Calculate Moving Average Crossover Signals"""

    # empty DataFrame to store crossover signals
    crossings = pd.DataFrame()
    crossings_data = []

    # A golden cross occurs when a short-term moving average crosses above a long-term moving average, indicating a potential bullish trend.
    for i in range(1, len(data)):
        if i < len(data) - 1:

            if short_ma.iloc[i+1] > long_ma.iloc[i+1] and short_ma.iloc[i-1] <= long_ma.iloc[i-1]:
                crossings_data.append((data.index[i], 'Golden Cross'))

            elif short_ma.iloc[i+1] < long_ma.iloc[i+1] and short_ma.iloc[i-1] >= long_ma.iloc[i-1]:
                crossings_data.append((data.index[i], 'Death Cross'))

            else:
                continue

    if crossings_data:
        crossings = pd.DataFrame(crossings_data, columns=[
                                 'Date', 'Crossover Type']).set_index('Date')

    return crossings['Crossover Type']


def bollinger_bands(data, window):
    """Calculate Bollinger Bands"""

    # Bollinger Bands consist of a middle band (SMA), an upper band, and a lower band.
    # The upper band is typically 2 standard deviations above the SMA, and the lower band is 2 standard deviations below the SMA.
    # typically if the current market price is near/above the upper band, the asset is considered overbought
    # if the price is near/below the lower band, the asset is considered oversold
    sma = data['Close'].rolling(window=window).mean()
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.std.html
    std = data['Close'].rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)

    return lower_band, upper_band


def rsi(data, window):
    """Calculate Relative Strength Index (RSI)"""

    # RSI = 100 - (100 / (1 + RS))
    # RS = Average Gain / Average Loss over the specified window
    # Typically, an RSI above 70 indicates overbought conditions, while an RSI below 30 indicates oversold conditions.
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def price_change(data):
    """Calculate Price Change Percentage"""

    # Price Change Percentage = ((Current Price - Previous Price) / Previous Price) * 100
    price_change = (
        (data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100

    return price_change.round(2)


def ema(data, window):
    """Calculate Exponential Moving Average (EMA)"""

    # EMA gives more weight to recent prices, making it more responsive to new information.
    # EMA_today = (Price_today * (smoothing / (1 + window))) + (EMA_yesterday * (1 - (smoothing / (1 + window))))
    # A common smoothing factor is 2.
    ema = data['Close'].ewm(span=window, adjust=False).mean()
    return ema


def macd(data, short_window=12, long_window=26, signal_window=9):
    """Calculate Moving Average Convergence Divergence (MACD)"""

    # MACD = 12-day EMA - 26-day EMA
    # Signal Line = 9-day EMA of MACD
    ema_short = ema(data, short_window)
    ema_long = ema(data, long_window)
    macd_line = ema_short - ema_long
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    return macd_line, signal_line


def atr(data, window=14):
    """Average true range"""

    # Average true range is an indicator for market volatility and therefore risk

    true_ranges = pd.DataFrame()
    true_ranges['H-L'] = data['High'] - data['Low']
    true_ranges['H-PC'] = abs(data['High'] - data['Close'].shift(1))
    true_ranges['L-PC'] = abs(data['Low'] - data['Close'].shift(1))
    true_range = true_ranges.max(axis=1)

    atr = true_range.rolling(window=window).mean()

    # scale atr to be between 0 and 100 : easier to understand percentages
    atr_scaled = (atr / atr.max()) * 100

    return atr_scaled.iloc[-1]


# Further indicators can be added here in the future
