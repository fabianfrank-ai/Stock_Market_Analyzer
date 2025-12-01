# Verdict.py tries to use the sma, bollinger bands,ema and macd and rsi in order to create a verdict how the user should trade
# The verdict is based on the following rules:
# Out of the 5 indicators, if 3 or more indicate buy/sell, the verdict is buy/sell
# If only 1,2 indicator indicates buy/sell, the verdict is hold
# If none of the indicators indicate buy/sell, the verdict is hold
# Note: This is a very simple approach and should not be used for real trading decisions. It is just for educational purposes.
from indicators_verdict.ma_verdict import ma_verdict
from indicators_verdict.rsi_verdict import rsi_verdict
from indicators_verdict.macd_verdict import macd_verdict
from indicators_verdict.bollinger_verdict import bollinger_verdict


class Verdict:
    def __init__(self, data, sma_long, sma_short, ema_Long, ema_short, rsi, signal_line, macd_line, lower_band, upper_band):
        '''Initialize the Verdict class with necessary indicators.'''
        # Store the latest values of the indicators
        self.price = data['Close'].iloc[-1]

        self.sma_short = sma_short
        self.sma_long = sma_long
        self.buyer_score = 0

        # Calculate SMA verdict
        ma_verdict_sma = ma_verdict(
            self.price, self.sma_short, self.sma_long)
        self.buyer_score += ma_verdict_sma.buyer_score
        # Calculate EMA verdict
        ma_verdict_ema = ma_verdict(
            self.price, ema_short, ema_Long)
        self.buyer_score += ma_verdict_ema.buyer_score

        # Calculate RSI verdict
        rsi_verdict_instance = rsi_verdict(rsi)
        self.buyer_score += rsi_verdict_instance.buyer_score

        # Calculate MACD verdict
        macd_verdict_instance = macd_verdict(macd_line, signal_line)
        self.buyer_score += macd_verdict_instance.buyer_score

        # Calculate Bollinger Bands verdict
        bollinger_verdict_instance = bollinger_verdict(
            self.price, lower_band, upper_band, sma_long)
        self.buyer_score += bollinger_verdict_instance.buyer_score

        self.verdict = self.get_verdict()

    def get_verdict(self):
        '''Generate the final verdict based on the buyer score.'''
        if self.buyer_score >= 20:
            return "Strong Buy"
        elif self.buyer_score <= -20:
            return "Strong Sell"
        elif 12 <= self.buyer_score < 20:
            return "Buy"
        elif -20 < self.buyer_score <= -12:
            return "Sell"
        else:
            return "Hold"
