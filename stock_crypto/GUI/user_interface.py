# Wanted to change to a class with everything, don't like it yet, I need convincing


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
from core.indicators import sma,  bollinger_bands, rsi, price_change, ema, macd, moving_average_crossover, atr

from core.verdict import Verdict


class GUI:
    '''Class to handle all GUI related functions and code'''

    def __init__(self):
        '''Initialize the GUI class and set dark mode for plots'''

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
        # create variables in session state so they don't get erased with each refresh
        if 'bought_stocks' not in st.session_state:
            st.session_state.bought_stocks = None

        if 'buy_in_price' not in st.session_state:
            st.session_state.buy_in_price = None

        if 'amount_bought' not in st.session_state:
            st.session_state.amount_bought = None

        if 'portfolio_df' not in st.session_state:
            st.session_state.portfolio_df = None

        # ===============================================================================================
        #                            STRUCTURE CONFIGURATION
        # Here I ordered the tabs and stuff just in the most convenient way, for it to run automatically
        # once main.py accesses GUI()
        # ===============================================================================================
        self.tab_init()
        self.header()
        self.sidebar()
        self.user_input()
        self.prepare_data()
        self.calculate_data()
        self.user_portfolio()
        self.tab_stock_chart()
        self.tab_short_term()
        self.tab_heatmap()
        self.tab_prediction()
        self.tab_portfolio_calculator()
        self.tab_network_graph()


# ======================================================================================================
#                   DATA FETCHING AND CALCULATING
# Take input from the user via user_input(), like timeframes, stock tickers etc and get data from yfinance,
# afterwards take the data and calculate the indicators, been in Main before that but now it's here
# ======================================================================================================

    def prepare_data(self):
        '''Prepare the data from the user input'''
        # fetch the stock data
        self.data = fetch_stock_data(self.stock, f'{self.period}y', '1d')
        self.data_prediction_now = fetch_stock_data(
            self.stock_prediction, f'{self.period_prediction}y', '1d')
        self.data_short_term = fetch_stock_data(
            self.stock_short, f'{self.timeframe_short}', '1m')

    def calculate_data(self):
        '''Take the user input and cook something up, was in main before but it's here now'''
        if self.data is None or self.data.empty:
            st.error(
                "Error fetching data. please enter existing stocks")

        try:
            # create the smas, ema, macd and other indicators
            # explanations can be found in the notebooks on calculations
            self.data_sma_30 = sma(self.data, 30)
            self.data_sma_100 = sma(self.data, 100)

            self.ema_12 = ema(self.data, 12)
            self.ema_26 = ema(self.data, 26)

            self.macd_line, self.signal_line = macd(self.data)
            self.macd_histogram = self.macd_line - self.signal_line

            # create the bollinger bands and rsi
            self.lower_band, self.upper_band = bollinger_bands(self.data, 30)
            self.rsi_data = rsi(self.data, 14)

            # create a verdict for the data(buy/hold/sell)
            verdict = Verdict(
                self.data, self.data_sma_100, self.data_sma_30, self.ema_26, self.ema_12, self.rsi_data, self.signal_line, self.macd_line, self.lower_band, self.upper_band, atr(self.data))
            self.verdict = verdict.verdict

            self.crossover_type_sma = moving_average_crossover(
                self.data, self.data_sma_30, self.data_sma_100)
            self.crossover_data_sma = self.crossover_type_sma.index

            self.crossover_type_ema = moving_average_crossover(
                self.data, self.ema_12, self.ema_26)
            self.crossover_data_ema = self.crossover_type_ema.index

            if st.session_state.bought_stocks and st.session_state.amount_bought and st.session_state.buy_in_price is not None:
                st.session_state.portfolio_df = generate_portfolio(
                    st.session_state.bought_stocks, st.session_state.amount_bought, st.session_state.buy_in_price)

            # calculate the price change percentage over the selected period
            self.price_change_data = price_change(self.data)

            self.atr_data = atr(self.data)

        except Exception as e:
            print("Error")

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
        '''Initializes all the tabs used for the GUI for the User to switch between views and features'''

        # create tabs with streamlit
        self.tab1, self.tab2, self.tab3, self.tab4, self.tab5 = st.tabs(["Stock Prices 📈", "Heatmap 🟩🟨🟥",
                                                                         "Stock Prediction 💹", "Portfolio Calculator ➕", "Networking Graph 📊"])

 # ==============================================================================================================
 #                            HEADER
 # Give the User a brief introduction to what he's looking at
 # =============================================================================================================

    def header(self):
        '''Create a header for the entire web page and change color theme'''
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
        '''Create a sidebar with useful texts and information and some instructions'''

        # sidebar also defines some values like the indicators
        # not much code, just text here

        with st.sidebar:

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
        '''Create user interface for user to chose his own data'''
        # create sliders for user input(time range and selected stock)
        # was not sure whether to include this in user_interface but it's here now for tidiness

        with self.tab1:
            self.tab_long, self.tab_short = st.tabs(
                ["Long term prices", "Short term prices"])

            with self.tab_long:
                self.period = st.slider('Select Period', min_value=1, max_value=20, value=10,
                                        help='Select the number of years to fetch data for (1-20 years)')
                self.stock = st.text_input('Select Stock ticker (AMZN, MSFT, META)',
                                           help='Select the stock symbol to fetch data for', value='AMZN')
                self.options = ['SMA', 'Bollinger Bands', 'EMA', 'MACD', 'RSI']
                self.selected_indicators = st.multiselect(
                    'Select Indicators to Display', self.options, default=['SMA', 'Bollinger Bands', 'RSI'])

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
        ''' Use this to get the data from the user for the portfolio'''

        with self.tab4:
            col1, col2, col3 = st.columns(3)

            with col1:
                self.stock_buy = st.text_input("Enter Stock ticker")

            with col2:
                self.stock_amount = st.text_input(
                    "Enter the amount you bought")

            with col3:
                self.buy_in_price = st.text_input(" Enter Buy-in price")

            if self.stock_buy and self.buy_in_price and self.stock_amount:
                if st.button("Add"):
                    # only return data if input is valid, otherwise return an error
                    try:
                        float(self.stock_amount)
                        float(self.buy_in_price)
                        fetch_stock_data(self.stock_buy, '30d', '1d')
                    except Exception as e:
                        st.error("Uh oh! Please check your input!")

    def tab_stock_chart(self):
        """Use retreived data from main to create plots for the data and create heatmap if necessary"""

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

            # plot the data
            # check if the price change is positive or negative and change the background color accordingly
            if self.price_change_data > 0:

                # dark green background for positive price change
                ax.set_facecolor('#003f3f')
                ax.plot(
                    self.data.index, self.data['Close'], label=f'Close Price \u25B2 {price_change}%', color='white')

            else:

                # dark red background for negative price change
                ax.set_facecolor('#3f0000')
                ax.plot(
                    self.data.index, self.data['Close'], label=f'Close Price \u25BC {price_change}%', color='#ff4d4d')

            # plot the selected indicators, if any are selected
            if 'SMA' in self.selected_indicators:

                ax.plot(self.data_sma_100.index, self.data_sma_100,
                        label='100 Day SMA', color='#f000ff', linestyle='dashdot')
                ax.plot(self.data_sma_30.index, self.data_sma_30, label='30 Day SMA',
                        color="#ffc800", linestyle='dashdot')

                # check if user chose sma as indicator
                if self.crossover_data_sma is not None:

                    # extract date and crossover type
                    for date, ctype in zip(self.crossover_data_sma, self.crossover_type_sma):

                        # check if its golden or death cross and plot accordingly

                        if ctype == 'Golden Cross':
                            # there was some trouble with plotting the markers directly on the date, so I had to find the closest date in the data index
                            # very hacky but it works

                            closest_date = self.data.index.get_indexer(
                                [date], method='nearest')
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
                ax2.fill_between(self.rsi_data.index, self.rsi_data, 70, where=(
                    self.rsi_data >= 70), color='red', alpha=0.3)
                ax2.fill_between(self.rsi_data.index, self.rsi_data, 30, where=(
                    self.rsi_data <= 30), color='limegreen', alpha=0.3)
                ax2.set_ylabel('RSI')

            # add a title and legend
            ax.set_title(
                f'{self.stock} Stock Price between {self.data.index[0].date()} and {self.data.index[-1].date()}')
            ax.legend()
            ax2.legend()

        # Give the user feedback whether to buy,sell or hold a product
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

                # give user a feedback over the estimated risk of buying a stock, shown with a scaled ATR
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
        '''Creates a tab with the most recent data plotted'''
        try:
            self.today_data = self.data['Close'].iloc[-1]
            self.today_data = round(self.today_data, 2)
            self.beginning_data = self.data['Close'].iloc[0]
            self.beginning_data = round(self.beginning_data, 2)

            # basically same thing than the long term tab but short
            with self.tab_short:
                st.write(f"{self.stock} : {self.today_data}$")
                fig_short_term, (ax) = plt.subplots(figsize=(16, 8))

                # name the axes and add a grid
                ax.set_xlabel('Date')
                ax.set_ylabel('Price (USD)')
                ax.grid()
                # ax.set_title(f'{stock} Stock Price between {data.index[0].date()} and {data.index[-1].date()}')

                ax.plot(
                    self.data.index, self.data['Close'], label=f'Movement of {self.stock} in a short frame', color="#EA00FF")

                st.pyplot(fig_short_term)
        except Exception as e:
            st.error(f"Oops, something went wrong, try again: {e}")

    def tab_heatmap(self):
        '''Create a heatmap and display it as streamlit dataframe'''
        if 'heatmap_data' not in st.session_state:
            st.session_state.heatmap_data = None

        self.tab_quarters = []
        with self.tab2:
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
                # get pre calculated files from the folder and sort them
                for file in Path("stock_crypto/data_saved/heatmap_parquet").glob("*.parquet"):

                    self.tab_quarters.append(f'{file.stem}')

                self.tab_quarters.sort()
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
        '''Create a portfolio calculator for input given by the user'''

        with self.tab3:
            try:
                fig_prediction, ax = plt.subplots(figsize=(16, 8))

                ax.set_xlabel('Date')
                ax.set_ylabel('Price (USD)')
                ax.grid()
                print("YOOOO")

                ax.plot(
                    self.data.index, self.data['Close'], label="Stock price in the past", color='red', zorder=5)
                ax.plot(self.data_pred.index, self.data_pred['Close'],
                        label=f"Stock price prediction for the next {self.timeframe} days", color="#24FF07", linestyle="--")

                ax.legend()

                # take the most recent price in the prediction to indicate a potential price in the next n days
                target_price = self.data_pred['Close'].iloc[-1]
                target_price = round(target_price, 2)

                st.info(
                    f'The selected stock has the potential to reach {target_price} USD in the next {self.timeframe} days')

                st.pyplot(fig_prediction)
            except Exception as e:
                st.error("Something went wrong, did you check for correct input?")

    def tab_portfolio_calculator(self):
        """Plotting of the portfolio calculator based with the input by a user"""
        if st.session_state.portfolio_df is not None:
            portfolio_csv = st.session_state.portfolio_df.to_csv(
                index=False).encode('utf-8')

        with self.tab4:
            # visualize the dataframe and heatmap of the portfolio
            st.dataframe(st.session_state.portfolio_df.style.map(
                color_code, subset=['Change%']))
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
        '''Plot the networking graph'''
        network_quarter_options = []
        fig_network = None
        # just enable session state so it doesn't have to create all the data with each refresh
        if 'df_correlation' not in st.session_state:
            st.session_state.df_correlation = None

        # display the network input and output in tab 5
        with self.tab5:
            tab_current_adjustable, tab_historical_data = st.tabs(
                ["Show the current network", "Show historical networks"])
            st.write(
                "Creates a Network Graph showing correlations between market movements of S&P 500 companies in the past 6 months")

            # 2 tabs within a tab to distplay a current network and historical records of networks
            with tab_current_adjustable:
                threshold = st.slider("Threshold for the correlations", min_value=0.3, max_value=1.0, value=0.7,
                                      help="Bigger correlations usually mean companies are very connected. NOTE: Be aware that a low threshold might slow your PC!")

                # give user the choice between new data or pre calculated data
                if st.button("Create a new networking Graph"):

                    with st.spinner("This will take a while...Please wait"):
                        if st.session_state.df_correlation is None:
                            st.session_state.df_correlation = correlations(
                                None, None)

                        else:
                            pass

                        fig_network = plot_network(
                            st.session_state.df_correlation, threshold)

            with tab_historical_data:
                # create an option for every entry in the folder and create a select slider, then read json file
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
