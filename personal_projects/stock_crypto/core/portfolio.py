import streamlit as st # need streamlit for session_state
from data.fetch_data import fetch_stock_data
import pandas as pd

sst = st.session_state

# create empty lists to insert into dataframe - not very pretty but it works
ticker_list = []
amount_list = []
buy_in_list = []
current_price_list = []
change_list = []
invested_overall_list = []
value_now_list = []
overall_profit_list = []


# create a session_state of the portfolio, so refreshing will not erase all data (sst used to reduce effort)
if 'portfolio_dataframe' not in sst:
    sst.portfolio_dataframe = pd.DataFrame (columns = ["Ticker", "Amount", "Buy-In", "Current Price", "Change%", 
                                                        "Invested overall", "Value Now", "Overall profit"])


def generate_portfolio(ticker, amount, buy_in):
        ''' Creates a dataframe with the user input for the portfolio '''


        # check if there is an entry for the ticker, pass if there is
        if ticker not in ticker_list:


            # get the most recent price as list (for the index) and as float (as output)
            current_price_index = fetch_stock_data(ticker, '1d')


            # calculate indicators and round if necessary
            # then insert into a list for the datafframe

            current_price = float(current_price_index['Close'].iloc[-1])
            current_price = round(current_price, 2)


            price_change = ((current_price - buy_in) / buy_in ) * 100
            price_change = round(price_change,2)


            overall_bought = amount * buy_in
            overall_bought = round(overall_bought, 2)


            value_now = current_price * amount
            value_now = round(value_now, 2)


            profit_per_stock = value_now - overall_bought
            profit_per_stock = round(profit_per_stock, 2)



            ticker_list.append(ticker)
            amount_list.append(amount)
            buy_in_list.append(buy_in)
            value_now_list.append(value_now)
            invested_overall_list.append(overall_bought)
            change_list.append(price_change)
            current_price_list.append(current_price)


            overall_profit_list.append(profit_per_stock)
            # create a dataframe that does'nt get deleted
            sst.portfolio_dataframe = pd.DataFrame ({'Ticker' : ticker_list,
                                                        'Amount' : amount_list,
                                                        'Buy-In' : buy_in_list,
                                                        'Current Price' : current_price_list,
                                                        'Change%' : change_list,
                                                        'Invested overall': invested_overall_list,
                                                        'Value Now' : value_now_list, 
                                                        'Overall profit' : overall_profit_list})
        else:
            pass

        return sst.portfolio_dataframe



