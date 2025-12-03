"""
Implements the graphical user interface for the application. Handles user
interaction, event processing, and the coordination of displayed data and
controls.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import plotly.io as pio

from core.prediction import prediction
from core.market_screener import heatmap, heatmap_portfolio, correlations
from core.portfolio import generate_portfolio
from GUI.colour_coding import color_code, verdict_color, rsi_color, ema_color, macd_color, sma_color, bollinger_color, atr_color
from core.network_graphing import plot_network
from data.fetch_data import fetch_stock_data
from core.indicators import Indicators

from core.verdict import Verdict


class GUI:
    '''
    Creates a GUI with data provided from the other functions

    This module creates a streamlit GUI, fetches data in accordance with user input and uses them to calculate and displays it to the user
    I tried working on error handling and I am sure there might be ways to break the code, but as far as I have checked I already iradicated every  
    possibility and it should run well and user-friendly.

    The GUI consists of 5 Tabs, each having their own special plots, dataframes or similar.

    Author: Fabian Frank
    Date: 2nd of December 2025
    '''

    def __init__(self):
        '''
        Initialises the GUI class, sets the colour theme for matplotlib and ploty, initialises session state, so user input won't get deleted,
        and gives the project structure, by arranging the functions of each area. It also plays an important role in error handling by detecting mainly missing
        values and giving user feedback that something might've gone wrong.'''

        # =============================================================================================
        #                           CONFIGURATION
        # Turn everything to dark mode for it to be more pleasant on the eyes
        # =============================================================================================

        # set dark mode for plotly
        pio.templates.default = "plotly_dark"
        # change the style of the plot to dark mode (Hex colors used from ChatGPT, (I don't like the default dark mode by matplotlib)
        plt.rcParams.update({
            "figure.facecolor": "#2e2e2e",
            "axes.facecolor":   "#2e2e2e",
            "axes.edgecolor":   "#cccccc",
            "axes.labelcolor":  "#ffffff",
            "xtick.color":      "#dddddd",
            "ytick.color":      "#dddddd",
            "grid.color":       "#555555",
            "text.color":       "#ffffff",
            "figure.edgecolor": "#2e2e2e"
        })
        # ==============================================================================================
        #                           SESSION STATE INITIALISATION
        # Streamlit loves to reset values with every reset and session state basically just prevents that
        # ==============================================================================================
        # create variables in session state so they don't get erased with each refres

        if 'portfolio_df' not in st.session_state:
            st.session_state.portfolio_df = None

        if 'df_correlation' not in st.session_state:
            st.session_state.df_correlation = None

        if 'heatmap_data' not in st.session_state:
            st.session_state.heatmap_data = None

        # ===============================================================================================
        #                            STRUCTURE CONFIGURATION
        # Here I ordered the tabs and stuff just in the most convenient way, for it to run automatically
        # once main.py accesses GUI()
        # Functions can be commented out if you want to fix a bug or single out a problem
        # It creates the widgets and stuff according to their corresponding functions in their respective
        # tabs
        # ===============================================================================================
        self.header()
        self.tab_init()
        with st.sidebar:
            self.sidebar()
        self.user_input()
        self.prepare_data()
        self.calculate_data()

        # basic error handling for the Portfolio to make sure the code won't break with certain values
        # return an error message if something fishy happens here and prevent portfolio from being created
        with self.tab4:
            try:
                self.user_portfolio()
            except Exception as e:
                st.error("Oops, did you check that the information is correct?")
            if st.session_state.portfolio_df is not None:
                self.tab_portfolio_calculator()

        # again, basic error handling, give user an error message if he entered bullshit into the text input
        if self.data is not None and not self.data.empty:
            self.tab_stock_chart()
        else:
            with self.tab_long:
                st.error("Did you make sure you entered correct values?")
        self.tab_short_term()

        with self.tab2:
            self.tab_heatmap()

        with self.tab3:
            self.tab_prediction()

        with self.tab5:
            self.tab_network_graph()


# ======================================================================================================
#                   DATA FETCHING AND CALCULATING
# Take input from the user via user_input(), like timeframes, stock tickers etc and get data from yfinance,
# afterwards take the data and calculate the indicators, been in Main before that but now it's here
# ======================================================================================================


    def prepare_data(self):
        '''
        Prepare the data from the user input. Here we fetch data 
        '''
        # here we fetch 3 different data because user can use 3 different inputs, so for each case we need
        # a different dataset/frame
        self.data = fetch_stock_data(self.stock, f'{self.period}y', '1d')
        self.data_prediction_now = fetch_stock_data(
            self.stock_prediction, f'{self.period_prediction}y', '1d')
        self.data_short_term = fetch_stock_data(
            self.stock_short, f'{self.timeframe_short}', '1m')

    def calculate_data(self):
        '''
        Take the user input and cook something up, was in main before but it's here now.
        It uses defs and classes from different files and uses data from yfinance to calculate indicators, which will later be used for visualization. 
        also some error handling, if, let's say something goes wrong, I get feedback on the terminal as to where the mistake happens.

        If you are interested in indicators, you can have a look at the indicators_guide notebook in notebooks/ , there I explain what the code does and what the indicators show, but for 
        here we just use the functionality and the result, I don't think I need to explain them further 
        '''
        try:
            indicators = Indicators(self.data)

            self.data_sma_30 = indicators.sma(30)
            self.data_sma_100 = indicators.sma(100)

            self.ema_12 = indicators.ema(12)
            self.ema_26 = indicators.ema(26)

            self.macd_line, self.signal_line = indicators.macd()
            self.macd_histogram = self.macd_line - self.signal_line

            self.lower_band, self.upper_band = indicators.bollinger_bands()
            self.rsi_data = indicators.rsi()
            self.atr_data = indicators.atr()

            verdict = Verdict(
                self.data, self.data_sma_100, self.data_sma_30, self.ema_26, self.ema_12, self.rsi_data, self.signal_line, self.macd_line, self.lower_band, self.upper_band, self.atr_data)
            self.verdict = verdict

            self.crossover_type_sma = indicators.moving_average_crossover(
                self.data_sma_30, self.data_sma_100)

            self.crossover_data_sma = self.crossover_type_sma.index

            self.crossover_type_ema = indicators.moving_average_crossover(
                self.ema_12, self.ema_26)
            self.crossover_data_ema = self.crossover_type_ema.index

            self.price_change_data = indicators.price_change()

        except Exception as e:
            # if something goes wrong, here is the error message for debugging, so I know what's going on
            print(f"Error,{e}")

        # also some basic error handling, in case input is weird or something
        try:
            self.data_pred_future = prediction(
                self.data_prediction_now, self.predicted_time_frame)
        except Exception as e:
            self.data_pred_future = None

# ==============================================================================================================|
#                            Visualization                                                                      |
# Everything from now on are GUI elements (mainly) for visualization , take the values we just calculated and   |
# turn them into plots, dataframes etc                                                                          |
# ==============================================================================================================|

    def tab_init(self):
        '''
        Initializes all the tabs used for the GUI for the User to switch between views and features.
        Creates 5 tabs via streamlit (they will later get sub-tabs, in a future update I might move the code to here, but for now we just initialize the main tabs). 
        Each tab has their own respective funtion and output (both numbers and plots)
        '''

        # create tabs with streamlit
        self.tab1, self.tab2, self.tab3, self.tab4, self.tab5 = st.tabs(["Stock Prices 📈", "Heatmap 🟩🟨🟥",
                                                                         "Stock Prediction 💹", "Portfolio Calculator ➕", "Networking Graph 📊"])

 # ==============================================================================================================
 #                            HEADER
 # Give the User a brief introduction to what he's looking at
 # =============================================================================================================

    def header(self):
        '''Create a header for the entire web page '''

        # Streamlit app layout with title and description
        st.title('Stock Price Viewer')
        st.write(
            'This app fetches and displays historical stock price data using yfinance and Streamlit.')

# ================================================================================================================
#                             Sidebar
# If the user has any questions about what he's looking at he can also get more information from here and also
# some more information on the app in general
# ================================================================================================================

    def sidebar(self):
        '''
        Here we create a sidebar via streamlit, there are not real data or functionalities, It's basically just information about the project, some indicators and 
        also have instructions for the user, for them to look at what they could do (IF it wasn't clear - I think the website is pretty intuitive)
        I noticed some things are depreciated, as the project has changed a lot, I will try to make time to rework it a bit.
        '''

        with st.sidebar.expander('About this app'):

            st.write('This app was created by Fabian Frank. It uses yfinance to fetch stock data and Streamlit for the web interface. You can view stock prices along with technical indicators like Simple Moving Averages (SMA) and Bollinger Bands.')
            st.write(
                'Feel free to explore and modify the code for your own projects!')
            st.write('DISCLAIMER: This app is for educational purposes only and should not be used for real trading decisions. Always do your own research and consult with a financial advisor before making investment decisions.')

        with st.sidebar.expander('SMA? Bollinger Bands? RSI? MACD? EMA?'):

            st.write('Simple Moving Averages (SMA) smooth out price data to identify trends. The 30-day SMA reacts faster to price changes than the 100-day SMA.')
            st.write('Bollinger Bands consist of a middle band (SMA), an upper band, and a lower band. Prices near the upper band may indicate overbought conditions, while prices near the lower band may indicate oversold conditions.')
            st.write('Relative Strength Index (RSI) measures the speed and change of price movements. An RSI above 70 indicates overbought conditions, while an RSI below 30 indicates oversold conditions.')
            st.write(
                'Exponential Moving Average (EMA) gives more weight to recent prices, making it more responsive to new information.')
            st.write('Moving Average Convergence Divergence (MACD) is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price.')
            st.write(
                'These indicators help traders make informed decisions about buying or selling stocks.')

        with st.sidebar.expander('Instructions'):

            st.write(
                '1. Select the stock ticker symbol (e.g., AMZN, MSFT, META) in the input box.')
            st.write('2. Use the slider to choose the period (in years) for which you want to fetch historical data. Note: indicatiors like SMA and Bollinger Bands are more visiblie with smaller periods')
            st.write(
                '3. The app will display the stock price along with the 30-day and 100-day SMAs and Bollinger Bands on the chart.')
            st.write(
                '4. You can select additional technical indicators to display on the chart from the sidebar.')
            st.write(
                '5. The verdict (Buy, Hold, Sell) is generated based on multiple technical indicators and displayed above the chart.')
            st.write(
                '6. You can also run the Signal Searcher to scan the S&P 500 for potential buy opportunities.')
            st.write(
                '7. Click the "Show S&P 500 Heatmap" button to generate a heatmap of S&P 500 companies based on their daily gain/loss percentage.')

        with st.sidebar.expander('What are Stock Tickers and where can I find them ?'):

            st.write('You can find stock ticker symbols on financial websites like Yahoo Finance, Google Finance, or your brokerage platform. Common examples include AAPL for Apple, MSFT for Microsoft, and AMZN for Amazon.')

        with st.sidebar.expander('How does the verdict work?'):

            st.write(
                'The new verdict system still uses the five main indicators: SMA, Bollinger Bands, RSI, EMA and MACD.')
            st.write('However, the strength of the signals has been increased. Now, if an indicator shows a very strong buy/sell signal (e.g., RSI > 80 or < 20), it counts as 3 buy/sell signals instead of just 1. This way, the verdict is more responsive to significant market movements.')
            st.write('If 9 or more buy/sell signals are generated, the verdict will be "Strong Buy" or "Strong Sell". If 3-8 buy/sell signals are generated, the verdict will be "Buy" or "Sell". If only 1-2 buy/sell signals are generated, the verdict will be "Hold". If no buy/sell signals are generated, the verdict will also be "Hold".')
        with st.sidebar.expander('How does the prediction work?'):

            st.write(
                'The prediction uses all of the indicators of the most recent data and calculates how the price could evolve based on them')
            st.write(
                'Indicators are scaled and added together to form a weight which will be applied to the data')
            st.write('Since stocks are not purely statistical, the prediction is very likely to fail, however, a broad understanding of future developments can be made')

        with st.sidebar.expander("What is a networking graph and what does it display?"):
            st.write(
                "A networking graph displays the correlations between price movements of the S&P 500 Stocks")
            st.write(
                "If stocks have a high correlation (e.g. 0.8+) most of their trends allign. Meaning: they tend to react to the market in a similar way")
            st.write(
                "Typically you'll find certain industries in clusters, as banks, tech, energy or healthcare are often closely intertwined")
            st.write("If you create a networking graph you'll probably see bank and loan organisations in the center with the most connections, due to the nature of their business")

        with st.sidebar.expander('Future Improvements'):

            st.write(
                '- Add more technical indicators like Volume, Stochastic Oscillator, etc.')
            st.write('- Implement user authentication for saving preferences.')
            st.write('- Allow users to save and compare multiple stocks.')
            st.write(
                '- Integrate real-time data updates for live stock prices.')
            st.write(
                '- Add educational resources about stock trading and technical analysis.')


# ======================================================================================================================================
#                               USER INPUT
# Here the user can just enter his preferred values in everything he wants and get further opportunities to analyze it to his liking
# ======================================================================================================================================


    def user_input(self):
        '''
        Create user interface for user to chose his own data, for mainly stock plots, predictions, long- and short term plots
        As I try to make it useful tool, It's important to add some interactivity with data, as it makes it easier to analyze.
        This basically decides over the structure of the data that's being displayed, from stock timeframes to indicators, we make
        use of streamlit widgets and safe the user input as variables for the class to access them 
        '''
        with self.tab1:
            self.tab_long, self.tab_short = st.tabs(
                ["Long term prices", "Short term prices"])

            with self.tab_long:

                self.period = st.slider('Select Period', min_value=1, max_value=20, value=10,
                                        help='Select the number of years to fetch data for (1-20 years)')

                self.stock = st.text_input('Select Stock ticker (AMZN, MSFT, META)',
                                           help='Select the stock symbol to fetch data for', value='AMZN')

                options = ['SMA', 'Bollinger Bands', 'EMA', 'MACD', 'RSI']
                self.selected_indicators = st.multiselect(
                    'Select Indicators to Display', options, default=['SMA', 'Bollinger Bands', 'RSI'])

            with self.tab_short:

                self.stock_short = st.text_input('Select Stock ticker (AMZN, MSFT, META)',
                                                 help='Select the stock symbol uto fetch data for', value='AMZN', key="Input box for short term analysis")

                self.options_pills = (
                    ["1d", "2d", "3d", "4d", "5d", "6d", '7d'])
                self.timeframe_short = st.pills(
                    label="Choose the timeframe you want to see", options=self.options_pills, default="7d")

        with self.tab3:
            self.period_prediction = st.slider('Select Period', min_value=1, max_value=20, value=10,
                                               help=' Select the number of years to fetch data for (1-20 years)', key="Slider Tab 3")

            self.predicted_time_frame = st.slider('Select the timeframe you want to predict', min_value=5, max_value=120,
                                                  value=60, help='Decides the length of the prediction. NOTE: Larger timeframes might be unrealistic')

            self.stock_prediction = st.text_input('Select Stock ticker (AMZN, MSFT, META)',
                                                  help='Select the stock symbol to fetch data for', value='AMZN', key="Input tab 3")

    def user_portfolio(self):
        '''
        This is also for getting data from the user, however due to the difference of structure, it is a different approach
        It creates 3 text inputs where the user can input anything he want. Afterwards we check and if all inputs are filled out, a add button appears, which adds the data and creates
        a dataframe.
        There is also error-handling, in case of user input being false, we chack if the user entered numbers and valid tickers and return an error if the user messed up
        '''

        col1, col2, col3 = st.columns(3)

        with col1:
            self.stock_buy = st.text_input("Enter Stock ticker")

        with col2:
            self.stock_amount = st.text_input(
                "Enter the amount you bought")

        with col3:
            self.buy_in_price = st.text_input(" Enter Buy-in price")

        # error handling again: check if all inputs are filled out and afterwards if the input is correct: Are there valid tickers
        # and numbers in fields where numbers are necessary
        if self.stock_buy and self.buy_in_price and self.stock_amount:
            if st.button("Add"):
                # only create dataframe if input is valid, otherwise return an error
                try:
                    self.stock_amount = float(self.stock_amount)
                    self.buy_in_price = float(self.buy_in_price)
                    fetch_stock_data(self.stock_buy, '30d', '1d')

                    # create datafrane from the input
                    st.session_state.portfolio_df = generate_portfolio(
                        self.stock_buy, self.stock_amount, self.buy_in_price)

                except Exception as e:
                    st.error("Uh oh! Please check your input!")

# =======================================================================================================================================
#                   DATA VISUALIZATION
# Take the calculated values and data based on user input and display them to the user in respective tabs
# =======================================================================================================================================

    def tab_stock_chart(self):
        """
        In tab_long we create two seperate plots for data visualization of long term stocks
        First plot will show the data graph, movement, price change and indicators like the SMA, EMA, Bollinger,
        plot two will consist of MACD and RSI, as values of those are relative and won't be displayed well in the main plot.
        We take advantage of matplotlib for visualisation here.
        """

        with self.tab_long:

            fig_long_term, (ax, ax2) = plt.subplots(
                2, 1, figsize=(16, 20), sharex=True)
            fig_long_term.tight_layout(pad=5.0)

            # name the axes and add a grid
            ax.set_xlabel('Date')
            ax.set_ylabel('Price (USD)')
            ax.grid()
            ax2.grid()
            ax2.set_ylabel('RSI')

            if self.price_change_data > 0:

                # dark green background for positive price change
                ax.set_facecolor('#003f3f')
                ax.plot(
                    self.data.index, self.data['Close'], label=f'Close Price \u25B2 {self.price_change_data}%', color='white')

            else:

                # dark red background for negative price change
                ax.set_facecolor('#3f0000')
                ax.plot(
                    self.data.index, self.data['Close'], label=f'Close Price \u25BC {self.price_change_data}%', color='#ff4d4d')

            if 'SMA' in self.selected_indicators:

                ax.plot(self.data_sma_100.index, self.data_sma_100,
                        label='100 Day SMA', color='#f000ff', linestyle='dashdot')
                ax.plot(self.data_sma_30.index, self.data_sma_30, label='30 Day SMA',
                        color="#ffc800", linestyle='dashdot')

                if self.crossover_data_sma is not None:

                    # extract date and crossover type
                    for date, ctype in zip(self.crossover_data_sma, self.crossover_type_sma):

                        # check if its golden or death cross and plot accordingly

                        if ctype == 'Golden Cross':
                            # there was some trouble with plotting the markers directly on the date, so I had to find the closest date in the data index
                            # very hacky but it works
                            # asked Claude for advice because I have never encountered that before

                            closest_date = self.data.index.get_indexer(
                                [date], method='nearest')

                            # plot a golden arrow up, to indicate a golden cross
                            ax.plot(self.data.index[closest_date][0], self.data.loc[self.data.index[closest_date][0], 'Close'],
                                    marker='^', color='gold', markersize=15, zorder=5)

                        elif ctype == 'Death Cross':

                            closest_date = self.data.index.get_indexer(
                                [date], method='nearest')
                            ax.plot(self.data.index[closest_date][0], self.data.loc[self.data.index[closest_date][0], 'Close'],
                                    marker='v', color='black', markersize=15, zorder=5)

            if 'Bollinger Bands' in self.selected_indicators:

                ax.plot(self.upper_band.index, self.upper_band,
                        label='Upper Bollinger Band', color='limegreen', linestyle='--')

                ax.plot(self.lower_band.index, self.lower_band,
                        label='Lower Bollinger Band', color='red', linestyle='--')

            if 'EMA' in self.selected_indicators:

                ax.plot(self.ema_12.index, self.ema_12, label='12 Day EMA',
                        color="#99f5ff", linestyle='dotted')
                ax.plot(self.ema_26.index, self.ema_26, label='26 Day EMA',
                        color='#ff00ff', linestyle='dotted')

                if self.crossover_data_ema is not None:

                    for date, ctype in zip(self.crossover_data_ema, self.crossover_type_ema):

                        if ctype == 'Golden Cross':
                            closest_date = self.data.index.get_indexer(
                                [date], method='nearest')
                            ax.plot(self.data.index[closest_date][0], self.data.loc[self.data.index[closest_date][0], 'Close'],
                                    marker='^', color='cyan', markersize=15)

                        elif ctype == 'Death Cross':

                            closest_date = self.data.index.get_indexer(
                                [date], method='nearest')
                            ax.plot(self.data.index[closest_date][0], self.data.loc[self.data.index[closest_date][0], 'Close'],
                                    marker='v', color='magenta', markersize=15)

            if 'MACD' in self.selected_indicators:

                ax2.plot(self.macd_line.index, self.macd_line,
                         label='MACD Line', color='#00ff00')

                ax2.plot(self.signal_line.index, self.signal_line,
                         label='Signal Line', color='#ff0000')

                ax2.bar(self.macd_histogram.index, self.macd_histogram,
                        label='MACD Histogram', color="#d400ff", alpha=0.5)

                ax2.axhline(0, color='grey', linestyle='--')
                ax2.set_ylabel('MACD')

            if 'RSI' in self.selected_indicators:

                ax2.plot(self.rsi_data.index, self.rsi_data,
                         label='14 Day RSI', color='#ffa500')

                ax2.axhline(70, color='red', linestyle='--')
                ax2.axhline(30, color='limegreen', linestyle='--')

                # it fills in everything above 70 in red -> overbought
                ax2.fill_between(self.rsi_data.index, self.rsi_data, 70, where=(
                    self.rsi_data >= 70), color='red', alpha=0.3)
                # it fills in everythint below 30 in green -> oversold
                ax2.fill_between(self.rsi_data.index, self.rsi_data, 30, where=(
                    self.rsi_data <= 30), color='limegreen', alpha=0.3)

                ax2.set_ylabel('RSI')

            ax.set_title(
                f'{self.stock} Stock Price between {self.data.index[0].date()} and {self.data.index[-1].date()}')
            ax.legend()
            ax2.legend()

            if self.verdict == "Buy":
                st.success(
                    f'Verdict: {self.verdict}. According to the indicators, it might be a good time to buy {self.stock}. Look at the sidebar for an explanation!')
            elif self.verdict == "Strong Buy":
                st.success(
                    f'Verdict: {self.verdict}. According to the indicators, it might be a very good time to buy {self.stock}. Look at the sidebar for an explanation!')
            elif self.verdict == "Strong Sell":
                st.error(
                    f'Verdict: {self.verdict}. According to the indicators, it might be a very good time to sell {self.stock}.')
            elif self.verdict == "Sell":
                st.error(
                    f'Verdict: {self.verdict}. According to the indicators, it might be a good time to sell {self.stock}.')
            else:
                st.warning(
                    f'Verdict: {self.verdict}. According to the indicators, it might be best to hold {self.stock} for now.')

            if self.atr_data is not None:

                if self.atr_data > 70:

                    st.error(
                        f'Risk (ATR): {self.atr_data:.2f}%. The stock seems highly volatile. Investing in it could be a huge rist.')

                elif self.atr_data > 40 and self.atr_data <= 70:

                    st.warning(
                        f'Risk (ATR): {self.atr_data:.2f}%. The stock seems volatile. Investing in it could be a risk.')

                elif self.atr_data > 20 and self.atr_data <= 40:

                    st.info(
                        f'Risk (ATR): {self.atr_data:.2f}%. The stock seems somewhat volatile. Investing in it could be a moderate risk.')

                else:
                    st.success(
                        f'Risk (ATR): {self.atr_data:.2f}%. The stock seems not very volatile. Investing in it should be relatively safe.')

            st.pyplot(fig_long_term)

    def tab_short_term(self):
        '''
        Takes data for short term data (<7d) and display it to the user, also give him a current price of the stock 
        This all happens in the second tab within tab 1(Sounds weird, I know), so it's seperated from the rest. If it cannot be plotted for whatever reason, there is also error handling here. We
        also use the data saved in the class for this occasion, for convenience
        '''
        # error handling, check if everything is alright and say no if it's not alright
        try:
            today_data = self.data_short_term['Close'].iloc[-1]
            today_data = round(today_data, 2)

            with self.tab_short:

                st.write(f"{self.stock} : {today_data}$")
                fig_short_term, (ax) = plt.subplots(figsize=(16, 8))

                ax.set_xlabel('Date')
                ax.set_ylabel('Price (USD)')
                ax.grid()

                ax.plot(
                    self.data_short_term.index, self.data_short_term['Close'], label=f'Movement of {self.stock} in a short frame', color="#EA00FF")

                st.pyplot(fig_short_term)
        except Exception as e:
            st.error(f"Oops, something went wrong, try again: {e}")

    def tab_heatmap(self):
        '''
        Take all the data we have collected so far and create a heatmap of indicators and verdict within the past 6 months and display them as streamlit dataframe. 
        We also give the user the opportunity to create a historical heatmap of one of the quarters we have saved in data_daved as parquet file.
        If creation was successful we also offer the opportunity to download the heatmap as csv data, in case he wants it
        '''

        self.tab_quarters = []

        col1, col2 = st.columns(2)
        with col1:
            # only create heatmap if it's not been created yet....
            if st.button("Create Heatmap"):

                # create a dataframe(pandas) with the heatmap function initialized in the data folder
                with st.spinner('Generating heatmap... This may take a moment.'):
                    # input none none to not interfere with historical data
                    st.session_state.heatmap_data = heatmap(None, None)

                st.write('S&P 500 Daily Change Percentage:')

        # ... or choose from a historical option
        with col2:
            # get pre calculated files from the folder and sort them,
            for file in Path("stock_crypto/data_saved/heatmap_parquet").glob("*.parquet"):

                self.tab_quarters.append(f'{file.stem}')

            self.tab_quarters.sort()

            # sorted Heatmaps can be chosen, they are in chronological order, so it fits in a select slicer
            self.quarter_choice = st.select_slider(
                label="Select a quarter to display the heatmap from", options=self.tab_quarters)

            if st.button("Go"):
                st.session_state.heatmap_data = pd.read_parquet(
                    f'stock_crypto/data_saved/heatmap_parquet/{self.quarter_choice}.parquet').copy()

        if st.session_state.heatmap_data is not None:
            st.dataframe(st.session_state.heatmap_data.style
                         .map(color_code, subset=['Change'])
                         .map(verdict_color, subset=['Verdict'])
                         .map(sma_color, subset=['SMA Diff'])
                         .map(rsi_color, subset=['RSI'])
                         .map(bollinger_color, subset=['Bollinger %'])
                         .map(ema_color, subset=['EMA Diff'])
                         .map(macd_color, subset=['MACD Diff'])
                         .map(atr_color, subset=['Risk']))

            heatmap_csv = st.session_state.heatmap_data.to_csv(
                index=False).encode('utf-8')
            st.download_button(label="Export Heatmap as CSV",
                               data=heatmap_csv, file_name="Heatmap.csv", mime="text/csv")

            st.info(
                "Note: Historical data uses SMA20 and SMA50 for calculations instead of SMA30 and SMA100 to better fit the shorter timeframes")

    def tab_prediction(self):
        '''
        Use the predicition system from predition and display it as plot. Also give the user
        the opportunity to adjust timeframes to look at it from different perspectives. This all 
        happens in the dedicated prediction tab and works basically the same as the other plot tabs in tab 1
        '''

        with self.tab3:
            # error handling, in case the graph cannot be plotted
            try:
                fig_prediction, ax = plt.subplots(figsize=(16, 8))

                ax.set_xlabel('Date')
                ax.set_ylabel('Price (USD)')
                ax.grid()

                # plot first the historical data from previous days as red and then put the prediction beneath it, hacky but works best that way
                ax.plot(
                    self.data_prediction_now.index, self.data_prediction_now['Close'], label="Stock price in the past", color='red', zorder=5)
                ax.plot(self.data_pred_future.index, self.data_pred_future['Close'],
                        label=f"Stock price prediction for the next {self.predicted_time_frame} days", color="#24FF07", linestyle="--")

                ax.legend()

                target_price = self.data_pred_future['Close'].iloc[-1]
                target_price = round(target_price, 2)

                st.info(
                    f'The selected stock has the potential to reach {target_price} USD in the next {self.predicted_time_frame} days')

                st.pyplot(fig_prediction)
            except Exception as e:
                st.error("Something went wrong, did you check for correct input?")

    def tab_portfolio_calculator(self):
        """
        Get the dataframe created earlier and display it as portfolio table basically
        Also use the data collected for the portfolio and create a heatmap similarly to the other heatmap to give the user further insight into how the state
        of his portfolio is looking like.
        Again, we offer download buttons as csv file if desired
        """

        # visualize the dataframe and heatmap of the portfolio
        # use some of the colours initialized in colour coding for the change
        st.dataframe(st.session_state.portfolio_df.style.map(
            color_code, subset=['Change%']))
        portfolio_csv = st.session_state.portfolio_df.to_csv(
            index=False).encode('utf-8')

        st.download_button(label="Download your portfolio as csv",
                           data=portfolio_csv, file_name="Portfolio.csv", mime="text/csv")

        heatmap_portf = heatmap_portfolio(st.session_state.portfolio_df)
        heatmap_portf_csv = heatmap_portf.to_csv(
            index=False).encode('utf-8')

        st.dataframe(heatmap_portf.style
                     .map(color_code, subset=['Change'])
                     .map(verdict_color, subset=['Verdict'])
                     .map(sma_color, subset=['SMA Diff'])
                     .map(rsi_color, subset=['RSI'])
                     .map(bollinger_color, subset=['Bollinger %'])
                     .map(ema_color, subset=['EMA Diff'])
                     .map(macd_color, subset=['MACD Diff'])
                     .map(atr_color, subset=['Risk']))

        st.download_button(label="Download your heatmap as csv", data=heatmap_portf_csv,
                           file_name='Portfolio heatmap.csv', mime="text/csv")

        st.info("Note that you can only add one stock of each kind")

    def tab_network_graph(self):
        '''
        Plot the networking graph, unlike the other plots we do not use motplotlib but plotly instead, to make it interactable and cooler looking
        Here we also offer the option for historical and recent options.

        For that we take the parquet files to read them and display them in the second tab. We basically just use the correlations and plot them, 
        further infomration can be found in notebooks and code from other functions 
        '''
        network_quarter_options = []
        fig_network = None

        with self.tab5:

            tab_current_adjustable, tab_historical_data = st.tabs(
                ["Show the current network", "Show historical networks"])

            st.write(
                "Creates a Network Graph showing correlations between market movements of S&P 500 companies in the past 6 months")

            with tab_current_adjustable:
                # user input for the threshold, for better analysis and interactivity
                threshold = st.slider("Threshold for the correlations", min_value=0.3, max_value=1.0, value=0.7,
                                      help="Bigger correlations usually mean companies are very connected. NOTE: Be aware that a low threshold might slow your PC!")

                # give user the choice between new data or pre calculated data
                if st.button("Create a new networking Graph"):

                    with st.spinner("This will take a while...Please wait"):

                        # create the correlations for the network, explanation is in correlations
                        st.session_state.df_correlation = correlations(
                            None, None)

                        # plot the network with the calculated correlations and given threshold
                        fig_network = plot_network(
                            st.session_state.df_correlation, threshold)

            with tab_historical_data:
                # create an option for every entry in the folder and create a select slider, then read parquet and sort
                for file in Path("stock_crypto/data_saved/correlation_parquet").glob("*.parquet"):

                    network_quarter_options.append(f'{file.stem}')

                network_quarter_options.sort()
                network_quarter_choice = st.select_slider(
                    label="Select a quarter to display the network graph from", options=network_quarter_options)

                threshold = st.slider("Threshold for the correlations", min_value=0.3, max_value=1.0, value=0.7,
                                      help="Bigger correlations usually mean companies are very connected. NOTE: Be aware that a low threshold might slow your PC!", key="Network threshold slider")

                if st.button("Go", key="Network go button"):
                    st.session_state.df_correlation = pd.read_parquet(
                        f'stock_crypto/data_saved/correlation_parquet/{network_quarter_choice}.parquet').copy()
                    fig_network = plot_network(
                        st.session_state.df_correlation, threshold)

            if fig_network is not None:
                st.plotly_chart(fig_network)

# ===============================================================================================================
#                   Future additions and tabs can be added here
# ===============================================================================================================
