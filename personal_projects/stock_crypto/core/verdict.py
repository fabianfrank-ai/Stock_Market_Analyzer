#Verdict.py tries to use the sma, bollinger bands,ema and macd and rsi in order to create a verdict how the user should trade
#The verdict is based on the following rules:
#Out of the 5 indicators, if 3 or more indicate buy/sell, the verdict is buy/sell
#If only 1,2 indicator indicates buy/sell, the verdict is hold
#If none of the indicators indicate buy/sell, the verdict is hold
#Note: This is a very simple approach and should not be used for real trading decisions. It is just for educational purposes.

import pandas as pd
from core.indicators import ema, macd

def generate_verdict(data,short_sma,long_sma,lower_band,upper_band,rsi):
    
    """Generate a trading verdict based on multiple technical indicators."""
  
    # at the beginning of the function, set the signals to 0, as there is no data yet
    buy_signals = 0
    sell_signals = 0


    # SMA signal
    # as market prices may vary, we will use the percantage difference between long and short SMA
    sma_diff=(short_sma - long_sma) / long_sma * 100



   # use 2 as threshold to decide whether the difference between sma differences is noteworthy enough
   # NEW : stronger signals for bigger differences - for ALL indicators

    if sma_diff.iloc[-1] > 2 and sma_diff.iloc[-1] < 8: 
        buy_signals += 1
    elif sma_diff.iloc[-1] < -2:
        sell_signals += 1
    elif sma_diff.iloc[-1] >= 10 :
        buy_signals += 3
    elif sma_diff.iloc[-1] <= -10 :
        sell_signals += 3

    else:
        pass  # No signal from SMA

 

    # Bollinger Bands signal
    bollinger_percentage=(data['Close'].iloc[-1] - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])

    if bollinger_percentage < 0.2 :
        sell_signals += 3
    elif bollinger_percentage >= 0.2 and bollinger_percentage <= 0.4:
        sell_signals += 1
    elif bollinger_percentage >= 0.4 and bollinger_percentage <= 0.6 :
        buy_signals += 1
    elif bollinger_percentage > 0.8:
        buy_signals += 3



    # RSI signal
    if rsi.iloc[-1] > 80:  
        sell_signals += 3
    elif rsi.iloc[-1] > 60 and rsi.iloc[-1] <= 80:
        sell_signals += 1
    elif rsi.iloc[-1] >= 20 and rsi.iloc[-1] <= 40:
        buy_signals += 1
    elif rsi.iloc[-1] < 20:  
        buy_signals += 3
    else:
        pass  
    # No signal from RSI




    # EMA signal
    ema_short=ema(data, 12)
    ema_long=ema(data, 26)

    ema_percentage=(ema_short - ema_long) / ema_long * 100

    if ema_percentage.iloc[-1] > 2 and ema_percentage.iloc[-1] < 8:
        buy_signals += 1
    elif ema_percentage.iloc[-1] < -2:
        sell_signals += 1
    elif ema_percentage.iloc[-1] >= 10 :
        buy_signals += 3
    elif ema_percentage.iloc[-1] <= -10 :
        sell_signals += 3
    else:
        pass
     # No signal from EMA


    # MACD signal
    macd_line, signal_line=macd(data)

    macd_difference= macd_line - signal_line
    macd_scale= (macd_difference / signal_line) * 100

    if macd_scale.iloc[-1] > 2 and macd_scale.iloc[-1] < 9:
        buy_signals += 1
    elif macd_scale.iloc[-1] < -2 and macd_scale.iloc[-1] > -9:
        sell_signals += 1
    elif macd_scale.iloc[-1] >= 10 :
        buy_signals += 3
    elif macd_scale.iloc[-1] <= -10 :
        sell_signals += 3
    else:
        pass
     
    # No signal from MACD
     

    # return verdict
    if buy_signals >= 6 and buy_signals < 11:
        return "Buy"
    if buy_signals >=12:
        return "Strong Buy"
    elif sell_signals >=6 and sell_signals < 11:
        return "Sell"
    elif sell_signals >= 12:
        return "Strong Sell"
    else:
        return "Hold"
    

