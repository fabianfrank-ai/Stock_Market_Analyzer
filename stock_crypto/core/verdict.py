"""
Defines the base verdict structure used across technical analysis components.
Provides shared logic, interfaces, and utilities for generating consistent
verdict outputs from various indicator-specific evaluators.
"""

from indicators_verdict.ma_verdict import ma_verdict
from indicators_verdict.rsi_verdict import rsi_verdict
from indicators_verdict.macd_verdict import macd_verdict
from indicators_verdict.bollinger_verdict import bollinger_verdict


class Verdict:
    '''
    This class takes all the indicator values and creates a verdict system and returns a simple string of 
    what the verdict should be. 

    Following indicators count into the verdict:
    SMA & EMA : at most 3 points through momentum and relative position to the actual price
    Crossovers : Death and Golden crosses can add or deduct 5 points, very strong signal
    RSI: At most 3 points
    MACD: 1 point for movements, 2 points for relative position and 5 points for crossovers
    Bollinger : Check if market is bullish or bearish and give 3 points accordingly
    ATR: If high volatility, adjust buyer score
    '''

    def __init__(self, data, sma_long, sma_short, ema_Long, ema_short, rsi, signal_line, macd_line, lower_band, upper_band, atr):
        '''Initialize the Verdict class with necessary indicators.'''
        # Store the latest values of the indicators
        self.price = data['Close'].iloc[-1]

        self.sma_short = sma_short
        self.sma_long = sma_long
        self.buyer_score = 0

        ma_verdict_sma = ma_verdict(
            self.price, self.sma_short, self.sma_long)
        self.buyer_score += ma_verdict_sma.buyer_score

        ma_verdict_ema = ma_verdict(
            self.price, ema_short, ema_Long)
        self.buyer_score += ma_verdict_ema.buyer_score

        rsi_verdict_instance = rsi_verdict(rsi)
        self.buyer_score += rsi_verdict_instance.buyer_score

        macd_verdict_instance = macd_verdict(macd_line, signal_line)
        self.buyer_score += macd_verdict_instance.buyer_score

        bollinger_verdict_instance = bollinger_verdict(
            self.price, lower_band, upper_band, sma_long)
        self.buyer_score += bollinger_verdict_instance.buyer_score

        if atr > 70:
            self.buyer_score *= 0.8
        elif atr < 30:
            self.buyer_score *= 1.2
        else:
            pass

        self.verdict = self.get_verdict()

    def get_verdict(self):
        '''Generate the final verdict based on the buyer score.'''
        if self.buyer_score >= 18:
            return "Strong Buy"
        elif self.buyer_score <= -18:
            return "Strong Sell"
        elif 10 <= self.buyer_score < 18:
            return "Buy"
        elif -18 < self.buyer_score <= -10:
            return "Sell"
        else:
            return "Hold"
