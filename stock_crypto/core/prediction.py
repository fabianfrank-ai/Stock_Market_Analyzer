"""
Handles generation of predictive signals based on processed market data.
Implements logic for estimating future movements, aggregating indicator
verdicts, and producing a consolidated prediction output.
"""

from core.indicators import Indicators
import pandas as pd


class Prediction:
    '''
    This class contains the prediction logic, it needs data, calculate the indicators, scales them, adds weights and
    adds it to the current price
    '''

    def __init__(self, data, timeframe):
        self.data = data
        self.timeframe = timeframe

        self.prediction()

    def retreive_data(self):
        '''
        It takes the data, calculates the indicators, scales them and creates a trend score, 
        indicating price movement for the day after
        '''
        indicators = Indicators(self.data)
        # I explained the idea in the notebook in notebooks/

        sma_short = indicators.sma(30)
        sma_long = indicators.sma(100)
        ema_short = indicators.ema(12)
        ema_long = indicators.ema(26)
        rsi_14 = indicators.rsi(14)
        lower_band, upper_band = indicators.bollinger_bands(30)
        macd_line, signal_line = indicators.macd()

        sma_short, sma_long = sma_short.align(sma_long, join='inner')
        sma_diff = (sma_short - sma_long) / sma_long

        ema_short, ema_long = ema_short.align(ema_long, join='inner')
        ema_diff = (ema_short - ema_long) / ema_long

        # if a desired indicator is good, it's score is 1, otherwise -1

        if rsi_14.iloc[-1] > 70:
            rsi_score = 1

        elif rsi_14.iloc[-1] < 30:
            rsi_score = -1

        else:
            rsi_score = 0

        bollinger_percentage = (self.data['Close'].iloc[-1] - lower_band.iloc[-1]
                                ) / (upper_band.iloc[-1] - lower_band.iloc[-1])

        if bollinger_percentage < 0.2:
            bb_score = -1

        elif bollinger_percentage > 0.5:
            bb_score = 1

        else:
            bb_score = 0

        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            macd_score = 1

        elif macd_line.iloc[-1] < signal_line.iloc[-1]:
            macd_score = -1

        else:
            macd_score = 0

        # weights are chosen of personal opinion, might change later
        self.trend_score = sma_diff.iloc[-1] * 0.25 + ema_diff.iloc[-1] * \
            0.25 + rsi_score * 0.2 + bb_score * 0.2 + macd_score * 0.2

    def prediction(self):
        '''Create a rough estimate of how the future price might develop'''
        # copy data to avoid modifying original dataframe
        self.data_pred = self.data.copy()

        std = self.data_pred['Close'].rolling(window=30).std()
        std_val = min(std.iloc[-1], 10)

        # predict the first 100 days for simplicity and as placeholder

        for i in range(self.timeframe):

            self.retreive_data()

            next_close = self.data_pred['Close'].iloc[-1] + \
                self.trend_score * std_val * 0.1

            next_date = pd.bdate_range(
                start=self.data_pred.index[-1], periods=2)[1]

            # Create a new row as a DataFrame
            new_row = pd.DataFrame({'Close': [next_close]},  index=[next_date])

            # Concatenate the new row
            # https://pandas.pydata.org/docs/reference/api/pandas.concat.html
            self.data_pred = pd.concat([self.data_pred, new_row])
