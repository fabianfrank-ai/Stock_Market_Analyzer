import streamlit as st
from data.fetch_data import fetch_stock_data
from core.indicators import sma,  bollinger_bands, rsi, price_change, ema, macd , moving_average_crossover, atr
from core.verdict import generate_verdict
from GUI.user_interface import sidebar, sliders, tab_stock_chart, header, tab_init, tab_heatmap, tab_portfolio_calculator
from core.prediction import prediction

# create Title and color theme for the web app
header()


# initialize tabs used
tab_init()

# use sidebar function in user_interface to keep main.py clean
selected_indicators = sidebar()


# use sliders function to get period and stock

period, stock =sliders()


# fetch the stock data
data = fetch_stock_data(stock, f'{period}y')
data_1_y = fetch_stock_data(stock, '1y')


# handle errors in case the stock ticker is invalid
if data is None or data.empty:
    st.error('Error fetching data. Please check the stock ticker symbol and try again.')
    st.stop()

# create the smas, ema, macd and other indicators
data_sma_30 = sma(data, 30) 
data_sma_100 = sma(data, 100)


ema_12 = ema(data, 12)
ema_26 = ema(data, 26)


macd_line, signal_line = macd(data)


# create the bollinger bands and rsi
lower_band, upper_band = bollinger_bands(data, 30)
rsi = rsi(data, 14)



# create a verdict for the data(buy/hold/sell)
verdict = generate_verdict(data, data_sma_30, data_sma_100, lower_band, upper_band, rsi)

crossover_type_sma = moving_average_crossover(data, data_sma_30, data_sma_100)
crossover_data_sma = crossover_type_sma.index 

crossover_type_ema = moving_average_crossover(data, ema_12, ema_26)
crossover_data_ema = crossover_type_ema.index



# calculate the price change percentage over the selected period
price_change = price_change(data)


atr = atr(data)

data_pred = prediction(data_1_y)

tab_stock_chart(stock, price_change, data, selected_indicators, data_sma_30, data_sma_100, crossover_data_sma, crossover_type_sma,
                    upper_band, lower_band, ema_12, ema_26, crossover_data_ema, crossover_type_ema, macd_line, signal_line, rsi,
                      verdict, atr)

tab_heatmap()

tab_portfolio_calculator(data_pred, data)

