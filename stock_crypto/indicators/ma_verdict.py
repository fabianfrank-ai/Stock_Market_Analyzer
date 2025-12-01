class ma_verdict:
    '''Generate verdict based on Moving Average indicators.'''

    def __init__(self, price, ma_short, ma_long):
        '''Initialize the ma_verdict class with necessary indicators.'''
        self.ma_short = ma_short
        self.ma_long = ma_long
        self.price = price

        print(self.price, self.ma_short.iloc[-1], self.ma_long.iloc[-1])

        buyer_score = 0
        buyer_score = self.difference_verdict()
        buyer_score += self.change_verdict()
        self.buyer_score = buyer_score

    def get_difference(self, price, ma):
        '''Calculate the percentage difference between two values.'''
        print("Calculating percentage difference...")
        return ((price - ma) / ma) * 100

    def difference_verdict(self):
        '''Generate verdict based on the difference between short and long moving averages.'''
        print("Calculating difference verdict...")

        buyer_score = 0
        # Calculate the percentage differences
        short_diff = self.get_difference(self.price, self.ma_long.iloc[-1])
        print(f"Short MA Difference: {short_diff}%")
        long_diff = self.get_difference(self.price, self.ma_short.iloc[-1])

        # Determine verdict based on the differences
        if short_diff > 4:
            buyer_score += 2
        elif 2 < short_diff <= 4:
            buyer_score += 1
        elif short_diff < -4:
            buyer_score -= 2
        elif -4 <= short_diff < -2:
            buyer_score -= 1
        else:
            buyer_score += 0

        # use 8 as threshold for long difference because long ma is less volatile
        if long_diff > 8:
            buyer_score += 2
        elif 4 < long_diff <= 8:
            buyer_score += 1
        elif long_diff < -8:
            buyer_score -= 2
        elif -8 <= long_diff < -4:
            buyer_score -= 1
        else:
            buyer_score += 0

        return buyer_score

    def change_verdict(self):
        '''Generate verdict based on the change in moving averages.'''
        buyer_score = 0
        # Calculate the changes in moving averages
        short_change = self.ma_short.iloc[-1] - self.ma_short.iloc[-2]
        long_change = self.ma_long.iloc[-1] - self.ma_long.iloc[-2]

        # Determine verdict based on the changes
        if short_change > 0:
            buyer_score += 1
        elif short_change < 0:
            buyer_score -= 1

        if long_change > 0:
            buyer_score += 1
        elif long_change < 0:
            buyer_score -= 1

        return buyer_score
