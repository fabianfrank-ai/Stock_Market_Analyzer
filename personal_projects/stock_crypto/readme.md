## Stock market analyser : LIVE DEMO: (https://mainpy-ha8s7cwyirhspxlutcnpbv.streamlit.app)

# How does it work?
It fetches data from yfinance(yahoo finance), uses simple indication techniques like sma, rsi and bollinger bands. The user can see all 5 indicators in a chart on a web app, created with streamlit. The user can search for stocks with tickers and manually change the desired length of the development. The user can also see the rsi line in a seperate axis. Not only can the user use those indications with explanations given by the program, the program also creates a verdict over the state of a desired stock(buy,sell,hold) based on the 5 indicators.

The project is still under construction and still lacks finetuning, this is only a broad framework.

## Explanation 

The project is devided into 3 folders and the main.py file:

The main file is used as the main framework and used as a bridge between the Streamlit interface as well as the data fetched and used for calculations.

The data folder is integral in order to fetch data from the web via yfinance and return it to the other projects. It also contains a database function for SQLite3, which is not used as of now but might be in the future.

The core folder contains the core functionalities and juggling with data. The fetched data get's processed and is used for calculations for indicators or even a verdict of the next 100 days.

As the project thrives to be user-friendly there is also a seperate GUI folder for the Streamlit GUI. It was previously cramped in the main file but the seperate just keeps the code readable and somewhat tidy. Most of it is just plotting and writing so nothing too complex there

The data_saved data is a database consisting of html, csv and parquet files. As of now they do not get used, however changes are staged in order to be able to browse quickly through selected historical data. The conversion machine has been specifically added to this and it will be extended in the future to guarantee the best possible analytic capabilities.


## Future ideas: 

- I really like the Idea of animating historical records
- More features in the portfolio tab
- quicker refresh speeds

