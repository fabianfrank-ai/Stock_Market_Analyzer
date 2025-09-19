# this program will screen the maket to find eligible stocks to buy 

import pandas as pd
import urllib.request
from data.fetch_data import fetch_stock_data
from core.indicators import sma, bollinger_bands, rsi, ema, macd , atr
from core.verdict import generate_verdict


def market_screener():
   """Screen the market for potential buy opportunities in S&P 500 companies."""

   
   # Get the list of S&P 500 companies from Wikipedia
   url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
   req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
   html = urllib.request.urlopen(req).read()
   tables = pd.read_html(html)


   # filter all the tickers from the table on wikipedia
   sp500_tickers = tables[0]['Symbol'].tolist()


   # for every ticker in sp500
   for ticker in sp500_tickers:


      # try, in order to prevent false tickers in eg wikipedia or conversion errors
      try:

         # fetch data, create smas, bollinger bands and rsi for every ticker
         data = fetch_stock_data(ticker, "5mo")
         sma_30 = sma(data, 30)
         sma_100 = sma(data, 100)
         lower_band, upper_band = bollinger_bands(data, 30)
         rsi_14 = rsi(data, 14)


         # create a verdict for the ticker 
         verdict = generate_verdict(data, sma_30, sma_100, lower_band, upper_band, rsi_14)


         # save the tickers with a buy verdict 
         if verdict == "Strong Buy" :
            return ticker, verdict
         else:
            pass  # No action for "Sell" or "Hold"



      except Exception as e:
         print(f"Error processing {ticker}: {e}")
         continue






# I'm sure there is a better way to do this, but for now it works, open to suggestions

def heatmap():
   """Generate a Dataframe of S&P 500 companies based on their gain/loss percentage over the last day."""


   # Get the list of S&P 500 companies from Wikipedia
   url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
   req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
   html = urllib.request.urlopen(req).read()
   tables = pd.read_html(html)
   

   # create empty lists to store the data, lists are then used to create a dataframe at the end
   ticker_data = []
   change_data = []
   verdict=[]
   sma_data = []
   bollinger_data = []
   rsi_data = []
   ema_data = []
   macd_data = []
   atr_data = []


   # filter all the tickers from the table on wikipedia
   sp500_tickers = tables[0]['Symbol'].tolist()


   # for every ticker in sp500
   for ticker in sp500_tickers:
      try:
         
         # fetch data
         data = fetch_stock_data(ticker, "6mo")

         
         # check if data is valid
         if data is None or len(data) < 2:
            print(f"Not enough data for {ticker}")
            continue


         # calculate the percentage change from the previous close to the latest close
         latest_close = data['Close'].iloc[-1]
         previous_close = data['Close'].iloc[-2]
         latest_change = ((latest_close - previous_close) / previous_close) * 100


         # append all the data to the respective lists
         ticker_data.append(ticker)
         change_data.append(latest_change)

         ema_percentage=(ema(data,12).iloc[-1] - ema(data,26).iloc[-1]) / ema(data,26).iloc[-1] * 100
         sma_percentage=(sma(data,30).iloc[-1] - sma(data,100).iloc[-1]) / sma(data,100).iloc[-1] * 100

         macd_line, signal_line = macd(data)
         macd_difference= macd_line.iloc[-1] - signal_line.iloc[-1]



         # calculate indicators for the ticker and append the relevant data to the respective lists
         sma_data.append(sma_percentage)
         lower_band, upper_band = bollinger_bands(data,30)
         bollinger_percentage=(data['Close'].iloc[-1] - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])

         bollinger_data.append(bollinger_percentage)
         rsi_data.append(rsi(data,14).iloc[-1])
         ema_data.append(ema_percentage)
         macd_line, signal_line = macd(data)
         macd_data.append(macd_difference)


         # generate and append the verdict for the ticker
         verdict.append(generate_verdict(data, sma(data,30), sma(data,100), *bollinger_bands(data,30), rsi(data,14)))


         atr_data.append(atr(data))


         # create a dataframe from the lists
         df=pd.DataFrame({
         'Ticker': ticker_data,
         'Change': change_data,
         'SMA Diff': sma_data,
         'Bollinger %': bollinger_data,
         'RSI': rsi_data,
         'EMA Diff': ema_data,
         'MACD Diff': macd_data,
         'Verdict': verdict,
         'Risk': atr_data
          })
        

   
      
      # Print any errors and continue with the next ticker
      except Exception as e:
         print(f"Error processing {ticker}: {e}")
         continue


# return the dataframe
   return df

