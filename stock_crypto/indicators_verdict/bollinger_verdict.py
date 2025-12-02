"""
Generates verdicts based on Bollinger Bands. Evaluates band touches,
volatility expansion or contraction, and price position within the bands.
"""


class bollinger_verdict:
    """
    Interprets Bollinger Band behavior to produce a market verdict.

    This class analyzes price movement relative to the upper, middle, 
    and lower bands, considers volatility changes, and evaluates signals 
    such as squeezes, breakouts, and overextension conditions.
    """

    def __init__(self, price, lower_band, upper_band, sma_long):
        '''Initialize the Bollinger Bands verdict.'''
        self.price = price
        self.lower_band = lower_band
        self.upper_band = upper_band
        self.sma_long = sma_long
        self.buyer_score = self.calculate_buyer_score()

    def calculate_buyer_score(self):
        '''
        Calculate the buyer score based on Bollinger Bands.

        We check for bullish/bearish conditions, as bollinger bands are treated differently there. If we are in a bullish market
        a high bb% (relative position of price between the two bands) could mean there is high momentum and the graph will
        break out.
        If we are in a bearish market a high bb% is considered a signal for overbought conditions and is treated differently here
        '''
        buyer_score = 0
        bollinger_percentage = (self.price - self.lower_band.iloc[-1]) / (
            self.upper_band.iloc[-1] - self.lower_band.iloc[-1]) * 100

        if self.price > self.sma_long.iloc[-1]:
            # Price is above long-term SMA -> Bullish context, Higher BB% could indicate breakout
            # if price is below momentum a high BB% could mean overbought
            if bollinger_percentage > 0.8:
                buyer_score += 3
            elif bollinger_percentage > 0.2:
                buyer_score += 1
            else:
                pass

        elif self.price < self.sma_long.iloc[-1]:
            # Price is below long-term SMA -> Bearish context, Lower BB% could indicate breakdown
            # if price is above momentum a low BB% could mean oversold
            if bollinger_percentage < 0.2:
                buyer_score -= 3
            elif bollinger_percentage < 0.8:
                buyer_score -= 1
            else:
                pass
        return buyer_score
