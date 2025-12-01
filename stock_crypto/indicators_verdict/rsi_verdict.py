class rsi_verdict:
    def __init__(self, rsi_value):
        '''Initialize the RSI verdict class with the RSI value.'''
        self.rsi_value = rsi_value.iloc[-1]
        self.buyer_score = self.calculate_verdict()

    def calculate_verdict(self):
        '''Calculate the buyer score based on RSI value.'''
        if self.rsi_value > 70:
            return -3
        elif 50 < self.rsi_value <= 70:
            return -1
        elif 30 <= self.rsi_value <= 50:
            return 1
        elif self.rsi_value < 30:
            return 3
