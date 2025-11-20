import streamlit as st
from data.fetch_data import fetch_stock_data
from core.indicators import sma,  bollinger_bands, rsi, price_change, ema, macd, moving_average_crossover, atr
from core.verdict import generate_verdict
from GUI.user_interface import sidebar, user_input, user_portfolio, tab_stock_chart, header, tab_init, tab_heatmap, tab_portfolio_calculator, tab_prediction, tab_network_graph, tab_short_term
from core.prediction import prediction
from core.portfolio import generate_portfolio


# create variables in session state so they don't get erased with each refresh
if 'bought_stocks' not in st.session_state:
    st.session_state.bought_stocks = None

if 'buy_in_price' not in st.session_state:
    st.session_state.buy_in_price = None

if 'amount_bought' not in st.session_state:
    st.session_state.amount_bought = None

if 'portfolio_df' not in st.session_state:
    st.session_state.portfolio_df = None

# get data from the user

# create Title and color theme for the web app
header()


# initialize tabs used
tab_init()

sidebar()

# use sliders function to get user input

period, stock, period_prediction, stock_prediction, predicted_time_frame, selected_indicators, timeframe_short, stock_short = user_input()

try:
    st.session_state.bought_stocks, st.session_state.buy_in_price, st.session_state.amount_bought = user_portfolio()
    st.session_state.buy_in_price = float(st.session_state.buy_in_price)
    st.session_state.amount_bought = float(st.session_state.amount_bought)
except Exception as e:
    pass


# use data from the user, do the math


# fetch the stock data
data = fetch_stock_data(stock, f'{period}y', '1d')
data_prediction_now = fetch_stock_data(
    stock_prediction, f'{period_prediction}y', '1d')
data_short_term = fetch_stock_data(stock_short, f'{timeframe_short}', '1m')

# handle errors in case the stock ticker is invalid
if data is None or data.empty:
    st.error("Error fetching data. please remind to only enter existing stocks")

try:
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
    verdict = generate_verdict(
        data, data_sma_30, data_sma_100, lower_band, upper_band, rsi)

    crossover_type_sma = moving_average_crossover(
        data, data_sma_30, data_sma_100)
    crossover_data_sma = crossover_type_sma.index

    crossover_type_ema = moving_average_crossover(data, ema_12, ema_26)
    crossover_data_ema = crossover_type_ema.index

    if st.session_state.bought_stocks and st.session_state.amount_bought and st.session_state.buy_in_price is not None:
        st.session_state.portfolio_df = generate_portfolio(
            st.session_state.bought_stocks, st.session_state.amount_bought, st.session_state.buy_in_price)


# calculate the price change percentage over the selected period
    price_change_data = price_change(data)


    atr_data = atr(data)

except Exception as e:
    print("Error")

try:
    data_pred_future = prediction(data_prediction_now, predicted_time_frame)
except Exception as e:
    data_pred_future = None


# give all the data to the UI
if data is not None and not data.empty:
    try:
        tab_stock_chart(stock, price_change_data, data, selected_indicators, data_sma_30, data_sma_100, crossover_data_sma, crossover_type_sma,
                        upper_band, lower_band, ema_12, ema_26, crossover_data_ema, crossover_type_ema, macd_line, signal_line, rsi,
                        verdict, atr_data)
        tab_prediction(data_pred_future, data_prediction_now,
                       predicted_time_frame)
    except Exception as e:
        print("Error in tab stock chart or prediction")


tab_short_term(data_short_term, stock_short)


tab_heatmap()


if st.session_state.portfolio_df is not None:
    tab_portfolio_calculator(st.session_state.portfolio_df)

tab_network_graph()
