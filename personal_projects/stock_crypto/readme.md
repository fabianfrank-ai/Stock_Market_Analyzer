## Stock market analyser : LIVE DEMO: (https://mainpy-ha8s7cwyirhspxlutcnpbv.streamlit.app)

# Overview

This project is an interactive stock tracker and analysis tool. It combines datafetching, financial indicators, simple portfolio management and network analysis in a single user-friendly interface.

# Main features:

- Ticker choice and datafetching (S&P500 or your own)
- Financial indicators (SMA, EMA, ATR, RSI, MACD, etc...)
- Interactive network with Plotly
- Heatmaps showing indicators of all S&P 500 tickers
- Portfolio Tracker
- (almost) real time stock prices
- a deterministic prediction tool
- an extensive verdict system for buy-signals

# How does it work?

- click on the link in the header
- you'll be redirected to the streamlit web page
- you might need to wake the app up first due to the nature of streamlit, this might take a minute or two
- feel free to explore any field that interests you 
- Note: loading time for creating new networks or heatmaps might be pretty long. Feel free to use historical data for quicker access

# Why is it useful?

- It shows historical data and recent data
- Multiple indicators for decisionmaking and analyzing
- User-friendly and easy to understand
- Many features which other websites hide behind a paywall
- Easy infrastructure allows for countless more additions

# Error-handling

- The program is developed in a way to prevent wrong user-input from crashing the app
- Entering wrong tickers or numbers will result in an error message
- The error message does not prevent the user from continuing his search for desired data
- Even though I think I prevented everything bugs might occur anyways. Please let me know if you find any and the problem will be resolved very quickly

# Future implementations:

- Performance optimization and reduce waiting times for plots or heatmaps
- Potential optimization to use C++ to accelerate certain calculations
- Replacing existing plots with interactive plots (matplotlib -> plotly)
