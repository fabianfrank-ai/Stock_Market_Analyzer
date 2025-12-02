"""
Generates a verdict based on MACD behavior. Evaluates line positions,
momentum shifts, and crossover events to produce a signal.
"""


class macd_verdict:
    """
    Interprets MACD line dynamics to produce a market verdict.

    This class analyzes MACD and signal line positions, their direction
    of movement, and any crossover patterns to determine momentum strength
    and potential trend shifts.
    """

    def __init__(self, macd_line, signal_line):
        '''Initialize the MACD verdict class with necessary indicators.'''
        self.macd_line = macd_line
        self.signal_line = signal_line
        self.buyer_score = 0

        # Calculate MACD verdict
        self.buyer_score = self.calculate_verdict()
        self.buyer_score += self.movement_verdict()
        self.buyer_score += self.crossover_verdict()

    def calculate_verdict(self):
        '''
        Generate verdict based on MACD line and signal line

        Here we are looking at the relative position between macd line and signal line, giving off 2 points at most, 
        if macd line is above signal line
        '''
        buyer_score = 0

        # Determine verdict based on MACD line and signal line
        if self.macd_line.iloc[-1] > self.signal_line.iloc[-1]:
            buyer_score += 2
        elif self.macd_line.iloc[-1] < self.signal_line.iloc[-1]:
            buyer_score -= 2
        else:
            buyer_score += 0

        return buyer_score

    def movement_verdict(self):
        '''
        Generate verdict based on the movement of MACD and signal lines.
        Here we kinda look at momentum, that means, if the lines move upwards, a buy signal of one is given
        '''
        buyer_score = 0
        # Calculate the movements
        macd_movement = self.macd_line.iloc[-1] - self.macd_line.iloc[-2]
        signal_movement = self.signal_line.iloc[-1] - self.signal_line.iloc[-2]

        # Determine verdict based on the movements
        if macd_movement > 0:
            buyer_score += 1
        elif macd_movement < 0:
            buyer_score -= 1

        if signal_movement > 0:
            buyer_score += 1
        elif signal_movement < 0:
            buyer_score -= 1

        return buyer_score

    def crossover_verdict(self):
        '''
        Generate verdict based on MACD crossover events.
        If lines cross, we behave similarly than with ma crossings and give 5 signals
        '''
        buyer_score = 0
        # Check for recent crossover events
        if self.macd_line.iloc[-2] < self.signal_line.iloc[-2] and self.macd_line.iloc[-1] > self.signal_line.iloc[-1]:
            buyer_score += 5
        elif self.macd_line.iloc[-2] > self.signal_line.iloc[-2] and self.macd_line.iloc[-1] < self.signal_line.iloc[-1]:
            buyer_score -= 5

        return buyer_score
