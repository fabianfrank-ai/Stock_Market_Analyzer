class bollinger_verdict:
    def __init__(self, price, lower_band, upper_band):
        '''Initialize the Bollinger Bands verdict.'''
        self.price = price
        self.lower_band = lower_band
        self.upper_band = upper_band
        self.buyer_score = self.calculate_buyer_score()

    def calculate_buyer_score(self):
        '''Calculate the buyer score based on Bollinger Bands.'''
        if self.price < self.lower_band:
            return 3  # Strong Buy
        elif self.price > self.upper_band:
            return -3  # Strong Sell
        else:
            return 0  # Hold
