# Verdict.py tries to use the sma, bollinger bands,ema and macd and rsi in order to create a verdict how the user should trade
# The verdict is based on the following rules:
# Out of the 5 indicators, if 3 or more indicate buy/sell, the verdict is buy/sell
# If only 1,2 indicator indicates buy/sell, the verdict is hold
# If none of the indicators indicate buy/sell, the verdict is hold
# Note: This is a very simple approach and should not be used for real trading decisions. It is just for educational purposes.
from indicators.ma_verdict import ma_verdict


class Verdict:
    def __init__(self, data, sma_long, sma_short):
        '''Initialize the Verdict class with necessary indicators.'''
        # Store the latest values of the indicators
        self.price = data['Close'].iloc[-1]

        self.sma_short = sma_short
        self.sma_long = sma_long
        self.buyer_score = 0
        print("Calculating MA verdict...")

        ma_verdict_sma = ma_verdict(
            self.price, self.sma_short, self.sma_long)
        self.buyer_score += ma_verdict_sma.buyer_score

        self.verdict = self.get_verdict()

    def get_verdict(self):
        '''Generate the final verdict based on the buyer score.'''
        if self.buyer_score >= 2:
            return "Buy"
        elif self.buyer_score <= -2:
            return "Sell"
        else:
            return "Hold"
