import streamlit as st

from GUI.user_interface import GUI


# get data from the user

gui = GUI()


try:
    st.session_state.buy_in_price = float(st.session_state.buy_in_price)
    st.session_state.amount_bought = float(st.session_state.amount_bought)
except Exception as e:
    pass
