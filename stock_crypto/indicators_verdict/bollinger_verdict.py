class bollinger_verdict:
    def __init__(self, price, lower_band, upper_band, sma_long):
        '''Initialize the Bollinger Bands verdict.'''
        self.price = price
        self.lower_band = lower_band
        self.upper_band = upper_band
        self.sma_long = sma_long
        self.buyer_score = self.calculate_buyer_score()

    def calculate_buyer_score(self):
        '''Calculate the buyer score based on Bollinger Bands.'''
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
